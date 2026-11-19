
from analytics.data_loader import (
    get_connection,
    create_analytics_views
)


def get_summary_kpis(con):

    query = """
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
            ) AS sb_records

        FROM all_installations
    """

    return con.execute(query).fetchdf()


def get_source_distribution(con):

    query = """
        SELECT
            source,
            installation_type,
            COUNT(*) AS total_records,

            ROUND(
                COUNT(*) * 100.0 /
                SUM(COUNT(*)) OVER (),
                2
            ) AS percentage

        FROM all_installations

        GROUP BY source, installation_type

        ORDER BY source
    """

    return con.execute(query).fetchdf()


def get_division_summary(con):

    query = """
        SELECT
            source,
            installation_type,
            division_name,
            COUNT(*) AS total_records

        FROM all_installations

        GROUP BY
            source,
            installation_type,
            division_name

        ORDER BY total_records DESC
    """

    return con.execute(query).fetchdf()


def get_vendor_summary(con):

    query = """
        SELECT
            source,
            vendor_manager,
            vendor_type,
            COUNT(*) AS total_records

        FROM all_installations

        GROUP BY
            source,
            vendor_manager,
            vendor_type

        ORDER BY total_records DESC
    """

    return con.execute(query).fetchdf()


def get_utility_summary(con):

    query = """
        SELECT
            source,
            utility,
            COUNT(*) AS total_records

        FROM all_installations

        GROUP BY source, utility

        ORDER BY total_records DESC
    """

    return con.execute(query).fetchdf()


def run_all_kpis():

    con = get_connection()

    try:

        create_analytics_views(con)

        results = {
            "summary": get_summary_kpis(con),
            "source": get_source_distribution(con),
            "division": get_division_summary(con),
            "vendor": get_vendor_summary(con),
            "utility": get_utility_summary(con)
        }

        return results

    finally:
        con.close()
