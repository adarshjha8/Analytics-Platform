
from analytics.data_loader import (
    get_connection,
    create_analytics_views
)


def main():

    con = get_connection()

    try:

        print("\nCreating analytical views...")

        create_analytics_views(con)

        print("Views created successfully!")

        # Total records
        print("\n1. TOTAL RECORDS")

        result = con.execute("""
            SELECT
                source,
                installation_type,
                COUNT(*) AS total_records

            FROM all_installations

            GROUP BY source, installation_type

            ORDER BY source
        """).fetchdf()

        print(result.to_string(index=False))

        # MI and NMI counts
        print("\n2. INSTALLATION TYPE SUMMARY")

        result = con.execute("""
            SELECT
                installation_type,
                COUNT(*) AS total_records

            FROM all_installations

            GROUP BY installation_type
        """).fetchdf()

        print(result.to_string(index=False))

        # Division-wise records
        print("\n3. DIVISION-WISE SUMMARY")

        result = con.execute("""
            SELECT
                source,
                division_name,
                COUNT(*) AS total_records

            FROM all_installations

            GROUP BY source, division_name

            ORDER BY source, total_records DESC
            LIMIT 30
        """).fetchdf()

        print(result.to_string(index=False))

        print("\nAnalytics layer test completed!")

    finally:
        con.close()


if __name__ == "__main__":
    main()
