
from analytics.data_loader import (
    get_connection,
    create_analytics_views
)

from analytics.date_analysis import create_date_view



# ==========================================================
# 1. BUILD DYNAMIC FILTER CONDITIONS
# ==========================================================

def build_filters(filters=None):

    if filters is None:
        filters = {}

    conditions = []
    params = []

    # Allowed filter columns
    filter_columns = {
        "source": "source",
        "utility": "utility",
        "installation_type": "installation_type",
        "division_name": "division_name",
        "vendor_type": "vendor_type",
        "vendor_manager": "vendor_manager"
    }

    # Apply case-insensitive filtering
    for key, column in filter_columns.items():

        value = filters.get(key)

        if value is not None and str(value).strip() not in ("", "All", "ALL"):

            if key == "vendor_manager":
                # Selecting a vendor-manager label matches every value
                # containing that text, regardless of letter case.
                conditions.append(
                    f"LOWER(TRIM(CAST({column} AS VARCHAR))) LIKE '%' || LOWER(TRIM(?)) || '%'"
                )
            else:
                conditions.append(
                    f"LOWER(TRIM(CAST({column} AS VARCHAR))) = LOWER(TRIM(?))"
                )

            params.append(str(value).strip())

    # Date filters
    # Support both date_start/date_end and start_date/end_date
    start_date = (
        filters.get("date_start")
        or filters.get("start_date")
    )

    end_date = (
        filters.get("date_end")
        or filters.get("end_date")
    )

    if start_date:

        conditions.append(
            "CAST(event_timestamp AS DATE) >= CAST(? AS DATE)"
        )

        params.append(str(start_date))

    if end_date:

        conditions.append(
            "CAST(event_timestamp AS DATE) <= CAST(? AS DATE)"
        )

        params.append(str(end_date))

    # Build WHERE clause
    where_clause = ""

    if conditions:

        where_clause = "WHERE " + " AND ".join(conditions)

    return where_clause, params




# ==========================================================
# 2. FILTER OPTIONS FOR DASHBOARD
#    REMOVE CASE-INSENSITIVE DUPLICATES
# ==========================================================

def get_filter_options(con):

    columns = [
        "source",
        "utility",
        "installation_type",
        "division_name",
        "vendor_type",
        "vendor_manager"
    ]

    options = {}

    for column in columns:

        query = f"""
            SELECT value
            FROM (
                SELECT
                    TRIM(CAST({column} AS VARCHAR)) AS value,

                    ROW_NUMBER() OVER (
                        PARTITION BY
                            LOWER(TRIM(CAST({column} AS VARCHAR)))

                        ORDER BY
                            CASE
                                WHEN TRIM(CAST({column} AS VARCHAR))
                                     = UPPER(TRIM(CAST({column} AS VARCHAR)))
                                THEN 2

                                WHEN TRIM(CAST({column} AS VARCHAR))
                                     = LOWER(TRIM(CAST({column} AS VARCHAR)))
                                THEN 1

                                ELSE 0
                            END,

                            TRIM(CAST({column} AS VARCHAR))
                    ) AS rn

                FROM dated_records

                WHERE
                    {column} IS NOT NULL
                    AND TRIM(CAST({column} AS VARCHAR)) <> ''
            )

            WHERE rn = 1

            ORDER BY LOWER(value), value
        """

        values = con.execute(query).fetchall()

        options[column] = [
            row[0] for row in values
        ]

    # Installation date range
    date_range = con.execute("""
        SELECT
            MIN(CAST(event_timestamp AS DATE)),
            MAX(CAST(event_timestamp AS DATE))
        FROM dated_records
    """).fetchone()

    options["date_range"] = {
        "start": date_range[0],
        "end": date_range[1]
    }

    return options



# ==========================================================
# 3. OVERALL KPI SUMMARY
# ==========================================================

def get_dashboard_kpis(con, where_clause, params):

    query = f"""
        SELECT

            COUNT(*) AS total_records,

            COUNT(*) FILTER (
                WHERE installation_type = 'MI'
            ) AS mi_records,

            COUNT(*) FILTER (
                WHERE installation_type = 'NMI'
            ) AS nmi_records,

            COUNT(*) FILTER (
                WHERE source = 'NB'
            ) AS nb_records,

            COUNT(*) FILTER (
                WHERE source = 'SB'
            ) AS sb_records,

            COUNT(*) FILTER (
                WHERE source = 'NMI'
            ) AS nmi_source_records

        FROM dated_records

        {where_clause}
    """

    return con.execute(query, params).fetchdf()


# ==========================================================
# 4. LATEST INSTALLATION DATE KPIs
# ==========================================================

def get_latest_date_kpis(con, where_clause, params):

    query = f"""
        WITH filtered_records AS (

            SELECT *
            FROM dated_records
            {where_clause}

        ),

        latest_date AS (

            SELECT MAX(CAST(event_timestamp AS DATE)) AS latest_date
            FROM filtered_records

        )

        SELECT

            latest_date.latest_date,

            COUNT(*) FILTER (
                WHERE CAST(filtered_records.event_timestamp AS DATE) = latest_date.latest_date
                  AND filtered_records.installation_type = 'MI'
            ) AS mi_records,

            COUNT(*) FILTER (
                WHERE CAST(filtered_records.event_timestamp AS DATE) = latest_date.latest_date
                  AND filtered_records.installation_type = 'NMI'
            ) AS nmi_records

        FROM latest_date
        LEFT JOIN filtered_records ON TRUE
        GROUP BY latest_date.latest_date
    """

    return con.execute(query, params).fetchdf()


# ==========================================================
# 4. CURRENT MONTH INSTALLATION INSIGHTS
# ==========================================================

def get_current_month_kpis(con, where_clause, params):

    query = f"""
        SELECT
            DATE_TRUNC('month', CURRENT_DATE)::DATE AS month_start,
            COUNT(*) AS total_records,
            COUNT(*) FILTER (
                WHERE installation_type = 'MI'
            ) AS mi_records,
            COUNT(*) FILTER (
                WHERE installation_type = 'NMI'
            ) AS nmi_records
        FROM dated_records
        {where_clause}
        { 'AND' if where_clause else 'WHERE' }
            event_timestamp >= DATE_TRUNC('month', CURRENT_DATE)
            AND event_timestamp < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
    """

    return con.execute(query, params).fetchdf()


# ==========================================================
# 4. DAILY TREND
# ==========================================================

def get_daily_trend(con, where_clause, params):

    query = f"""
        SELECT

            CAST(event_timestamp AS DATE) AS event_date,

            COUNT(*) FILTER (
                WHERE installation_type = 'MI'
            ) AS mi_records,

            COUNT(*) FILTER (
                WHERE installation_type = 'NMI'
            ) AS nmi_records,

            COUNT(*) AS total_records

        FROM dated_records

        {where_clause}

        GROUP BY CAST(event_timestamp AS DATE)

        ORDER BY event_date
    """

    return con.execute(query, params).fetchdf()


# ==========================================================
# 5. MONTHLY TREND
# ==========================================================

def get_monthly_trend(con, where_clause, params):

    query = f"""
        WITH filtered_records AS (

            SELECT *
            FROM dated_records
            {where_clause}

        ),

        latest_month AS (

            SELECT
                DATE_TRUNC('month', MAX(event_timestamp)) AS max_month
            FROM filtered_records

        )

        SELECT

            DATE_TRUNC(
                'month',
                filtered_records.event_timestamp
            )::DATE AS month,

            COUNT(*) FILTER (
                WHERE filtered_records.installation_type = 'MI'
            ) AS mi_records,

            COUNT(*) FILTER (
                WHERE filtered_records.installation_type = 'NMI'
            ) AS nmi_records,

            COUNT(*) AS total_records

        FROM filtered_records
        CROSS JOIN latest_month

        WHERE DATE_TRUNC(
            'month',
            filtered_records.event_timestamp
        ) >= latest_month.max_month - INTERVAL '4 months'

        GROUP BY DATE_TRUNC(
            'month',
            filtered_records.event_timestamp
        )

        ORDER BY month
    """

    return con.execute(query, params).fetchdf()


# ==========================================================
# 6. DIVISION ANALYSIS
# ==========================================================

def get_division_analysis(con, where_clause, params):

    query = f"""
        SELECT

            utility,
            MIN(TRIM(division_name)) AS division_name,

            COUNT(*) FILTER (
                WHERE installation_type = 'MI'
            ) AS mi_records,

            COUNT(*) FILTER (
                WHERE installation_type = 'NMI'
            ) AS nmi_records,

            COUNT(*) AS total_records,

            COUNT(DISTINCT CASE
                WHEN field_worker_id IS NOT NULL
                 AND TRIM(CAST(field_worker_id AS VARCHAR)) <> ''
                THEN LOWER(TRIM(CAST(field_worker_id AS VARCHAR)))
            END) AS manpower

        FROM dated_records

        {where_clause}

        GROUP BY
            utility,
            LOWER(TRIM(division_name))

        ORDER BY
            utility,
            division_name
    """

    return con.execute(query, params).fetchdf()


# ==========================================================
# 7. VENDOR ANALYSIS
# ==========================================================

def get_vendor_analysis(con, where_clause, params):

    query = f"""
        SELECT

            source,
            installation_type,
            utility,
            vendor_manager,
            vendor_type,

            COUNT(*) AS total_records

        FROM dated_records

        {where_clause}

        GROUP BY
            source,
            installation_type,
            utility,
            vendor_manager,
            vendor_type

        ORDER BY total_records DESC
    """

    return con.execute(query, params).fetchdf()


# ==========================================================
# 8. UTILITY ANALYSIS
# ==========================================================

def get_utility_analysis(con, where_clause, params):

    query = f"""
        SELECT

            utility,
            installation_type,

            COUNT(*) AS total_records

        FROM dated_records

        {where_clause}

        GROUP BY
            utility,
            installation_type

        ORDER BY total_records DESC
    """

    return con.execute(query, params).fetchdf()


# ==========================================================
# 9. SOURCE DISTRIBUTION
# ==========================================================

def get_source_analysis(con, where_clause, params):

    query = f"""
        SELECT

            source,
            installation_type,

            COUNT(*) AS total_records,

            ROUND(
                COUNT(*) * 100.0 /
                NULLIF(SUM(COUNT(*)) OVER (), 0),
                2
            ) AS percentage

        FROM dated_records

        {where_clause}

        GROUP BY
            source,
            installation_type

        ORDER BY source
    """

    return con.execute(query, params).fetchdf()


# ==========================================================
# 10. FIELD WORKER PRODUCTIVITY
# ==========================================================

def get_field_worker_productivity(con, where_clause, params):
    """Return one row per worker, combining MI and NMI counts.

    data_loader.py standardizes NB/SB mi_updated_by and NMI updated_by
    into dated_records.field_worker_id.
    """

    query = f"""
        WITH filtered_records AS (
            SELECT
                LOWER(TRIM(CAST(field_worker_id AS VARCHAR))) AS worker_key,
                TRIM(CAST(field_worker_id AS VARCHAR)) AS field_worker_id,
                UPPER(TRIM(CAST(installation_type AS VARCHAR))) AS installation_type
            FROM dated_records
            {where_clause}
        ),
        valid_records AS (
            SELECT worker_key, field_worker_id, installation_type
            FROM filtered_records
            WHERE worker_key IS NOT NULL
              AND worker_key <> ''
        )
        SELECT
            MIN(field_worker_id) AS field_worker_id,
            COUNT(*) FILTER (WHERE installation_type = 'MI') AS "MI",
            COUNT(*) FILTER (WHERE installation_type = 'NMI') AS "NMI",
            COUNT(*) AS "MI + NMI"
        FROM valid_records
        GROUP BY worker_key
        ORDER BY "MI + NMI" DESC, field_worker_id
    """

    result = con.execute(query, params).fetchdf()

    if not result.empty:
        for column in ["MI", "NMI", "MI + NMI"]:
            result[column] = result[column].fillna(0).astype(int)

    return result[["field_worker_id", "MI", "NMI", "MI + NMI"]]


# ==========================================================
# 10. MAIN DASHBOARD ENGINE
# ==========================================================

def get_dashboard_data(filters=None):

    con = get_connection()

    try:

        # Create views over original Parquet files
        create_analytics_views(con)

        # Create standardized installation date view
        create_date_view(con)

        # Get available filter options
        filter_options = get_filter_options(con)

        # Prepare selected filters
        where_clause, params = build_filters(filters)

        # Calculate dashboard results
        results = {

            "kpis": get_dashboard_kpis(
                con, where_clause, params
            ),

            "daily_trend": get_daily_trend(
                con, where_clause, params
            ),

            "latest_date_kpis": get_latest_date_kpis(
                con, where_clause, params
            ),

            "current_month_kpis": get_current_month_kpis(
                con, where_clause, params
            ),

            "monthly_trend": get_monthly_trend(
                con, where_clause, params
            ),

            "division": get_division_analysis(
                con, where_clause, params
            ),

            "vendor": get_vendor_analysis(
                con, where_clause, params
            ),

            "utility": get_utility_analysis(
                con, where_clause, params
            ),

            "source": get_source_analysis(
                con, where_clause, params
            ),

            "field_worker_productivity": get_field_worker_productivity(
                con, where_clause, params
            ),

            "filter_options": filter_options

        }

        return results

    finally:
        con.close()
