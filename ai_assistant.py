import json
import os
import re

from google import genai

from analytics.data_loader import get_connection, create_analytics_views
from analytics.date_analysis import create_date_view


MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

SCHEMA_DESCRIPTION = """
You are a data analyst for an installation analytics platform.
You may query ONLY the DuckDB view `ai_records`, with these columns:
- source: NB, SB, NMI
- installation_type: MI or NMI
- utility
- division_name
- ci_meter_status (populated for NB/SB MI records; NULL for NMI)
- vendor_manager
- vendor_type
- consumer_id
- field_worker_id
- raw_event_date
- event_timestamp (timestamp parsed from MI mi_updated_at or NMI completion_date)

Rules:
- Return one simple DuckDB SELECT statement (no CTEs) and nothing else.
- Use only ai_records. Do not use any other table, view, file, path, URL, or extension.
- Never use INSERT, UPDATE, DELETE, CREATE, DROP, COPY, ATTACH, DETACH, PRAGMA, CALL, EXPORT, IMPORT, INSTALL, LOAD, or filesystem/network functions.
- Use event_timestamp for date analysis and exclude NULL event_timestamp when analyzing dates.
- MI and NMI are installation_type values. source identifies NB, SB, or NMI.
- Use COUNT(*) for record counts. Use COUNT(DISTINCT field_worker_id) for unique manpower.
- For top-N questions, order by the requested metric descending.
- Prefer clear aliases. Keep results concise.
- Do not invent columns.
"""

FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|COPY|ATTACH|DETACH|PRAGMA|CALL|"
    r"EXPORT|IMPORT|INSTALL|LOAD|REPLACE|TRUNCATE|MERGE|VACUUM|SET|RESET|"
    r"READ_CSV|READ_PARQUET|READ_JSON|GLOB|HTTPFS|PARQUET_SCAN|CSV_SCAN|"
    r"WRITE_PARQUET|WRITE_CSV|NEXTVAL|SEQUENCE)\b",
    re.IGNORECASE,
)


def _get_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to Windows environment variables "
            "and restart VS Code/terminal."
        )
    return genai.Client(api_key=key)


def _generate_sql(question, filters):
    client = _get_client()
    prompt = f"""
{SCHEMA_DESCRIPTION}

Current dashboard filters (apply these where relevant):
{json.dumps(filters or {{}}, default=str, ensure_ascii=False)}

User question:
{question}

Return one SQL SELECT statement only. Do not wrap it in markdown fences.
"""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    sql = (response.text or "").strip()
    sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql, flags=re.IGNORECASE).strip()
    return sql


def validate_sql(sql):
    """Allow a single read-only SELECT against ai_records only."""
    if not sql:
        raise ValueError("Gemini did not return a SQL query.")

    cleaned = sql.strip()
    if ";" in cleaned.rstrip(";"):
        raise ValueError("Only one SQL statement is allowed.")
    cleaned = cleaned.rstrip(";").strip()

    if not re.match(r"^(SELECT|WITH)\b", cleaned, flags=re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    if FORBIDDEN.search(cleaned):
        raise ValueError("The generated query contains a restricted SQL operation.")

    # No comments or quoted identifiers that could conceal extra SQL.
    if "--" in cleaned or "/*" in cleaned or "*/" in cleaned:
        raise ValueError("SQL comments are not allowed.")

    # Require the sole permitted source to be referenced.
    if not re.search(r"\bai_records\b", cleaned, flags=re.IGNORECASE):
        raise ValueError("Query must use the approved ai_records view.")

    # Block references to other tables/views, table functions, and external access.
    if re.search(r"\b(FROM|JOIN)\s+(?!ai_records\b|\()([A-Za-z_][A-Za-z0-9_.]*)",
                 cleaned, flags=re.IGNORECASE):
        raise ValueError("Query may reference only ai_records.")

    if re.search(r"\b(read_|query|pragma_|http|sqlite|postgres|mysql)\w*\s*\(",
                 cleaned, flags=re.IGNORECASE):
        raise ValueError("External or system functions are not allowed.")

    return cleaned


def run_read_only_query(sql, filters=None, max_rows=200):
    """Create filtered, Parquet-backed views and execute a validated read-only query."""
    con = get_connection()
    try:
        create_analytics_views(con)
        create_date_view(con)

        allowed_filters = {
            "utility": "utility",
            "installation_type": "installation_type",
            "division_name": "division_name",
            "ci_meter_status": "ci_meter_status",
            "vendor_type": "vendor_type",
            "vendor_manager": "vendor_manager",
        }
        conditions = []
        for key, column in allowed_filters.items():
            value = (filters or {}).get(key)
            if value is not None and str(value).strip() not in ("", "All", "ALL"):
                escaped = str(value).strip().replace("'", "''")
                conditions.append(
                    f"LOWER(TRIM(CAST({column} AS VARCHAR))) = LOWER('{escaped}')"
                )

        for key, operator in (("start_date", ">="), ("end_date", "<=")):
            value = (filters or {}).get(key)
            if value:
                escaped = str(value).replace("'", "''")
                conditions.append(
                    f"CAST(event_timestamp AS DATE) {operator} CAST('{escaped}' AS DATE)"
                )

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        con.execute(f"CREATE OR REPLACE TEMP VIEW ai_records AS SELECT * FROM dated_records {where}")

        # Validation occurs before this function; wrapping caps returned rows.
        query = f"SELECT * FROM ({sql}) AS ai_result LIMIT {int(max_rows)}"
        return con.execute(query).fetchdf()
    finally:
        con.close()


def _summarize(question, sql, dataframe):
    client = _get_client()
    preview = dataframe.head(50).to_dict(orient="records")
    prompt = f"""
You are an analytics assistant. Answer the user's question using ONLY the query
result below. Do not claim information not present in the result. If the result
is empty, say no matching records were found. Mention the metric and relevant
grouping clearly. Be concise.

Question: {question}
SQL executed:
{sql}
Result rows (up to 50):
{json.dumps(preview, default=str, ensure_ascii=False)}
"""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return (response.text or "").strip()


def ask_data_question(question, filters=None):
    """Generate safe SQL, query Parquet-backed DuckDB views, and explain results."""
    question = (question or "").strip()
    if not question:
        raise ValueError("Please enter a question.")

    sql = validate_sql(_generate_sql(question, filters))
    result = run_read_only_query(sql, filters=filters)
    answer = _summarize(question, sql, result) if not result.empty else (
        "No matching records were found for that question and the available data."
    )
    return {"answer": answer, "sql": sql, "data": result}
