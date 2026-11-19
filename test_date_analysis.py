
from analytics.date_analysis import (
    run_date_analysis,
    get_connection,
    create_analytics_views,
    create_date_view,
    get_invalid_date_samples
)


def print_report(title, dataframe, limit=None):

    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)

    if dataframe.empty:
        print("No records found.")
        return

    if limit is not None:
        dataframe = dataframe.head(limit)

    print(dataframe.to_string(index=False))


def main():

    print("\n" + "=" * 65)
    print("INSTALLATION INTELLIGENCE - DATE ANALYSIS")
    print("=" * 65)

    results = run_date_analysis()

    print_report(
        "1. DATE QUALITY REPORT",
        results["date_quality"]
    )

    print_report(
        "2. DAILY EVENT ANALYSIS",
        results["daily"],
        20
    )

    print_report(
        "3. MONTHLY EVENT ANALYSIS",
        results["monthly"],
        30
    )

    print_report(
        "4. DAILY DIVISION ANALYSIS",
        results["daily_division"],
        20
    )

    print_report(
        "5. MONTHLY VENDOR ANALYSIS",
        results["monthly_vendor"],
        20
    )

    print_report(
        "6. DAILY COMBINED SUMMARY",
        results["daily_total"],
        20
    )

    con = get_connection()

    try:

        create_analytics_views(con)
        create_date_view(con)

        invalid = get_invalid_date_samples(con)

        print_report(
            "7. INVALID DATE EXAMPLES",
            invalid
        )

    finally:
        con.close()

    print("\n" + "=" * 65)
    print("DATE ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()
