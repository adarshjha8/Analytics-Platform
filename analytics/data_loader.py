
import duckdb
import re

from config.settings import PARQUET_FILES


def get_connection():
    """Create an in-memory DuckDB connection."""
    return duckdb.connect(database=":memory:")


def sql_path(path):
    """Safely format a file path as a SQL string literal."""
    return "'" + str(path).replace("'", "''") + "'"


def _circle_column_expression(con, file_path):
    """Detect a circle column or return NULL if unavailable."""
    path = sql_path(file_path)

    schema = con.execute(
        f"DESCRIBE SELECT * FROM read_parquet({path})"
    ).fetchall()

    candidates = {
        re.sub(r"[^a-z0-9]", "", str(row[0]).lower()): str(row[0])
        for row in schema
    }

    for candidate in ("circle", "circlename", "circle_name"):
        normalized = re.sub(r"[^a-z0-9]", "", candidate.lower())

        if normalized in candidates:
            actual_name = candidates[normalized]
            quoted_name = '"' + actual_name.replace('"', '""') + '"'
            return f"CAST({quoted_name} AS VARCHAR)"

    return "NULL::VARCHAR"


def create_analytics_views(con):
    """Create analytical views over NB, SB and NMI Parquet files."""

    for source, file_path in PARQUET_FILES.items():
        if not file_path.exists():
            raise FileNotFoundError(
                f"{source} Parquet file not found: {file_path}"
            )

    # NB and SB: MI datasets
    for source in ["NB", "SB"]:
        path = sql_path(PARQUET_FILES[source])
        circle_expression = _circle_column_expression(
            con, PARQUET_FILES[source]
        )

        con.execute(f"""
            CREATE OR REPLACE VIEW {source.lower()}_data AS
            SELECT
                '{source}' AS source,
                'MI' AS installation_type,
                "Utility" AS utility,
                utility_id,
                division_id,
                "Division Name" AS division_name,
                {circle_expression} AS circle_name,
                sub_division_id,
                NULL::VARCHAR AS section,
                consumer_id,
                installation_number,
                "Load" AS load,
                "Load Category" AS load_category,
                vendor_manager,
                "Vendor Type" AS vendor_type,
                cat_code,
                CAST(mi_updated_by AS VARCHAR) AS field_worker_id,
                mi_updated_at,
                last_updated_at,
                NULL::VARCHAR AS completion_date,
                ci_meter_status,
                NULL::VARCHAR AS verification_status,
                mi_meter_number AS meter_number,
                NULL::VARCHAR AS origin_id
            FROM read_parquet({path})
        """)

    # NMI dataset
    nmi_path = sql_path(PARQUET_FILES["NMI"])
    nmi_circle_expression = _circle_column_expression(
        con, PARQUET_FILES["NMI"]
    )

    con.execute(f"""
        CREATE OR REPLACE VIEW nmi_data AS
        SELECT
            'NMI' AS source,
            'NMI' AS installation_type,
            "Utility" AS utility,
            utility_id,
            NULL::VARCHAR AS division_id,
            "Division Name" AS division_name,
            {nmi_circle_expression} AS circle_name,
            sub_division_id,
            section,
            consumer_id,
            installation_number,
            NULL::VARCHAR AS load,
            NULL::VARCHAR AS load_category,
            vendor_manager,
            "Vendor Type" AS vendor_type,
            NULL::VARCHAR AS cat_code,
            CAST(updated_by AS VARCHAR) AS field_worker_id,
            NULL::VARCHAR AS mi_updated_at,
            NULL::VARCHAR AS last_updated_at,
            completion_date,
            NULL::VARCHAR AS ci_meter_status,
            verification_status,
            NULL::VARCHAR AS meter_number,
            NULL::VARCHAR AS origin_id
        FROM read_parquet({nmi_path})
    """)

    # Combined MI dataset
    con.execute("""
        CREATE OR REPLACE VIEW mi_data AS
        SELECT * FROM nb_data
        UNION ALL
        SELECT * FROM sb_data
    """)

    # Combined MI + NMI dataset
    con.execute("""
        CREATE OR REPLACE VIEW all_installations AS
        SELECT * FROM mi_data
        UNION ALL
        SELECT * FROM nmi_data
    """)


def check_parquet_files():
    results = {}
    con = get_connection()

    try:
        for source, file_path in PARQUET_FILES.items():
            if not file_path.exists():
                results[source] = {
                    "status": "Missing",
                    "rows": 0
                }
                continue

            total_rows = con.execute(
                "SELECT COUNT(*) FROM read_parquet(?)",
                [str(file_path)]
            ).fetchone()[0]

            results[source] = {
                "status": "Connected",
                "rows": total_rows
            }

    finally:
        con.close()

    return results
