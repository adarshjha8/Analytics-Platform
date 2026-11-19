from analytics.data_loader import get_connection, create_analytics_views


# ==========================================================
# 1. CREATE A STANDARDIZED DATE VIEW
# ==========================================================

def create_date_view(con):
    """Create dated_records and retain the standardized worker ID."""

    con.execute("""
        CREATE OR REPLACE TEMP VIEW dated_records AS
        SELECT
            source,
            installation_type,
            utility,
            division_name,
            ci_meter_status,
            vendor_manager,
            vendor_type,
            consumer_id,
            field_worker_id,

            CASE
                WHEN installation_type = 'MI' THEN mi_updated_at
                WHEN installation_type = 'NMI' THEN completion_date
            END AS raw_event_date,

            TRY_STRPTIME(
                NULLIF(
                    TRIM(CAST(
                        CASE
                            WHEN installation_type = 'MI' THEN mi_updated_at
                            WHEN installation_type = 'NMI' THEN completion_date
                        END AS VARCHAR
                    )),
                    ''
                ),
                '%m/%d/%Y'
            ) AS event_timestamp
        FROM all_installations
    """)


# ==========================================================
# 2. DATE QUALITY REPORT
# ==========================================================

def get_date_quality(con):
    query = """
        SELECT
            source,
            installation_type,
            COUNT(*) AS total_records,
            COUNT(*) FILTER (WHERE event_timestamp IS NOT NULL) AS valid_dates,
            COUNT(*) FILTER (
                WHERE raw_event_date IS NULL
                   OR TRIM(CAST(raw_event_date AS VARCHAR)) = ''
            ) AS missing_dates,
            COUNT(*) FILTER (
                WHERE raw_event_date IS NOT NULL
                  AND TRIM(CAST(raw_event_date AS VARCHAR)) <> ''
                  AND event_timestamp IS NULL
            ) AS invalid_dates,
            MIN(CAST(event_timestamp AS DATE)) AS first_date,
            MAX(CAST(event_timestamp AS DATE)) AS last_date
        FROM dated_records
        GROUP BY source, installation_type
        ORDER BY source
    """
    return con.execute(query).fetchdf()


# ==========================================================
# 3. DAILY EVENT ANALYSIS
# ==========================================================

def get_daily_installations(con):
    query = """
        SELECT
            source,
            installation_type,
            utility,
            CAST(event_timestamp AS DATE) AS event_date,
            COUNT(*) AS total_records
        FROM dated_records
        WHERE event_timestamp IS NOT NULL
        GROUP BY source, installation_type, utility,
                 CAST(event_timestamp AS DATE)
        ORDER BY event_date DESC, source
    """
    return con.execute(query).fetchdf()


# ==========================================================
# 4. MONTHLY EVENT ANALYSIS
# ==========================================================

def get_monthly_installations(con):
    query = """
        SELECT
            source,
            installation_type,
            utility,
            DATE_TRUNC('month', event_timestamp)::DATE AS month,
            COUNT(*) AS total_records
        FROM dated_records
        WHERE event_timestamp IS NOT NULL
        GROUP BY source, installation_type, utility,
                 DATE_TRUNC('month', event_timestamp)
        ORDER BY month DESC, source
    """
    return con.execute(query).fetchdf()


# ==========================================================
# 5. DAILY DIVISION ANALYSIS
# ==========================================================

def get_daily_division_summary(con):
    query = """
        SELECT
            source,
            installation_type,
            utility,
            division_name,
            CAST(event_timestamp AS DATE) AS event_date,
            COUNT(*) AS total_records
        FROM dated_records
        WHERE event_timestamp IS NOT NULL
        GROUP BY source, installation_type, utility, division_name,
                 CAST(event_timestamp AS DATE)
        ORDER BY event_date DESC, total_records DESC
    """
    return con.execute(query).fetchdf()


# ==========================================================
# 6. MONTHLY VENDOR ANALYSIS
# ==========================================================

def get_monthly_vendor_summary(con):
    query = """
        SELECT
            source,
            installation_type,
            utility,
            vendor_manager,
            vendor_type,
            DATE_TRUNC('month', event_timestamp)::DATE AS month,
            COUNT(*) AS total_records
        FROM dated_records
        WHERE event_timestamp IS NOT NULL
        GROUP BY source, installation_type, utility, vendor_manager,
                 vendor_type, DATE_TRUNC('month', event_timestamp)
        ORDER BY month DESC, total_records DESC
    """
    return con.execute(query).fetchdf()


# ==========================================================
# 7. DAILY COMBINED SUMMARY
# ==========================================================

def get_daily_total_summary(con):
    query = """
        SELECT
            CAST(event_timestamp AS DATE) AS event_date,
            COUNT(*) FILTER (WHERE installation_type = 'MI') AS mi_records,
            COUNT(*) FILTER (WHERE installation_type = 'NMI') AS nmi_completion_date_records,
            COUNT(*) AS total_event_records
        FROM dated_records
        WHERE event_timestamp IS NOT NULL
        GROUP BY CAST(event_timestamp AS DATE)
        ORDER BY event_date DESC
    """
    return con.execute(query).fetchdf()


# ==========================================================
# 8. INVALID DATE EXAMPLES
# ==========================================================

def get_invalid_date_samples(con, limit=20):
    query = """
        SELECT
            source,
            installation_type,
            raw_event_date,
            division_name,
            consumer_id
        FROM dated_records
        WHERE raw_event_date IS NOT NULL
          AND TRIM(CAST(raw_event_date AS VARCHAR)) <> ''
          AND event_timestamp IS NULL
        LIMIT ?
    """
    return con.execute(query, [limit]).fetchdf()


# ==========================================================
# 9. RUN COMPLETE DATE ANALYSIS
# ==========================================================

def run_date_analysis():
    con = get_connection()
    try:
        print("\nConnecting to Parquet files...")
        create_analytics_views(con)
        print("Creating standardized date view...")
        create_date_view(con)
        print("Date view created successfully.")

        return {
            "date_quality": get_date_quality(con),
            "daily": get_daily_installations(con),
            "monthly": get_monthly_installations(con),
            "daily_division": get_daily_division_summary(con),
            "monthly_vendor": get_monthly_vendor_summary(con),
            "daily_total": get_daily_total_summary(con)
        }
    finally:
        con.close()
