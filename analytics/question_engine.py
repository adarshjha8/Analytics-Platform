
import re
import duckdb
import pandas as pd


# --------------------------------------------------
# QUESTION ENGINE - INSTALLATION INTELLIGENCE
# --------------------------------------------------

def clean_question(question):
    """Normalize the user's question."""
    return re.sub(r"\s+", " ", question.strip().lower())


def detect_metric(question):
    """Identify which installation metric the user wants."""

    if "nmi" in question:
        return "NMI"

    if re.search(r"\bmi\b", question):
        return "MI"

    if "nbpdcl" in question:
        return "NBPDCL"

    if "sbpdcl" in question:
        return "SBPDCL"

    if re.search(r"\bnb\b", question):
        return "NB"

    if re.search(r"\bsb\b", question):
        return "SB"

    return "TOTAL"


def detect_grouping(question):
    """Identify the grouping dimension."""

    if "division" in question:
        return "division_name"

    if "vendor manager" in question:
        return "vendor_manager"

    if "vendor type" in question:
        return "vendor_type"

    if "vendor" in question:
        return "vendor_manager"

    if "utility" in question:
        return "utility"

    if "month" in question or "monthly" in question:
        return "month"

    if "day" in question or "daily" in question:
        return "day"

    return None


def detect_top_n(question):
    """Extract a requested top/bottom N."""

    match = re.search(r"\btop\s+(\d+)\b", question)

    if match:
        return int(match.group(1)), "DESC"

    match = re.search(r"\bbottom\s+(\d+)\b", question)

    if match:
        return int(match.group(1)), "ASC"

    return None, "DESC"


def detect_installation_filter(question):
    """Extract simple installation type filters."""

    if "nmi" in question:
        return "NMI"

    if re.search(r"\bmi\b", question):
        return "MI"

    return None


def detect_utility_filter(question):
    """Extract utility filter."""

    if "nbpdcl" in question:
        return "NBPDCL"

    if "sbpdcl" in question:
        return "SBPDCL"

    return None


def detect_source_filter(question):
    """Extract source filter."""

    if re.search(r"\bnb\b", question):
        return "NB"

    if re.search(r"\bsb\b", question):
        return "SB"

    return None


def build_question_query(question):
    """
    Convert supported questions into safe SQL.

    Only predefined columns and SQL expressions are used.
    """

    question = clean_question(question)

    metric = detect_metric(question)
    grouping = detect_grouping(question)
    top_n, sort_order = detect_top_n(question)

    conditions = []
    params = []

    # Installation type
    installation_type = detect_installation_filter(question)

    if installation_type:
        conditions.append("installation_type = ?")
        params.append(installation_type)

    # Utility
    utility = detect_utility_filter(question)

    if utility:
        conditions.append(
            "LOWER(TRIM(utility)) = LOWER(?)"
        )
        params.append(utility)

    # Source
    source = detect_source_filter(question)

    if source:
        conditions.append("source = ?")
        params.append(source)

    # Metric expression
    metric_expressions = {
        "TOTAL": "COUNT(*)",
        "MI": "SUM(CASE WHEN installation_type = 'MI' THEN 1 ELSE 0 END)",
        "NMI": "SUM(CASE WHEN installation_type = 'NMI' THEN 1 ELSE 0 END)",
        "NB": "SUM(CASE WHEN source = 'NB' THEN 1 ELSE 0 END)",
        "SB": "SUM(CASE WHEN source = 'SB' THEN 1 ELSE 0 END)",
        "NBPDCL": "SUM(CASE WHEN LOWER(TRIM(utility)) = 'nbpdcl' THEN 1 ELSE 0 END)",
        "SBPDCL": "SUM(CASE WHEN LOWER(TRIM(utility)) = 'sbpdcl' THEN 1 ELSE 0 END)"
    }

    metric_expression = metric_expressions[metric]

    # Grouping expression
    grouping_expressions = {
        "division_name": "division_name",
        "vendor_manager": "vendor_manager",
        "vendor_type": "vendor_type",
        "utility": "utility",
        "month": "DATE_TRUNC('month', event_timestamp)",
        "day": "CAST(event_timestamp AS DATE)"
    }

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    if grouping:
        group_expression = grouping_expressions[grouping]

        query = f"""
            SELECT
                {group_expression} AS category,
                {metric_expression} AS installation_count
            FROM all_installations
            {where_clause}
            GROUP BY {group_expression}
            ORDER BY installation_count {sort_order}
        """

        if top_n:
            query += f" LIMIT {top_n}"

    else:
        query = f"""
            SELECT
                {metric_expression} AS installation_count
            FROM all_installations
            {where_clause}
        """

    return query, params, metric, grouping


def answer_question(con, question):
    """Execute a supported question and return its result."""

    if not question or not question.strip():
        return {
            "status": "error",
            "message": "Please enter a question."
        }

    try:
        query, params, metric, grouping = build_question_query(
            question
        )

        result = con.execute(query, params).fetchdf()

        if result.empty:
            return {
                "status": "success",
                "message": "No matching records found.",
                "data": [],
                "metric": metric,
                "grouping": grouping
            }

        return {
            "status": "success",
            "message": "Question answered successfully.",
            "data": result.to_dict(orient="records"),
            "metric": metric,
            "grouping": grouping
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }
