
from analytics.dashboard_engine import get_dashboard_data


def display(title, dataframe, limit=15):

    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)

    if dataframe.empty:
        print("No records found.")
    else:
        print(dataframe.head(limit).to_string(index=False))


def main():

    print("\n")
    print("=" * 65)
    print("INSTALLATION INTELLIGENCE - DASHBOARD ENGINE")
    print("=" * 65)

    # ------------------------------------------------------
    # TEST 1: COMPLETE DATASET
    # ------------------------------------------------------

    print("\nTEST 1: ALL DATA")

    results = get_dashboard_data()

    display(
        "1. DASHBOARD KPI CARDS",
        results["kpis"]
    )

    display(
        "2. DAILY TREND",
        results["daily_trend"]
    )

    display(
        "3. MONTHLY TREND",
        results["monthly_trend"]
    )

    display(
        "4. DIVISION ANALYSIS",
        results["division"]
    )

    display(
        "5. VENDOR ANALYSIS",
        results["vendor"]
    )

    display(
        "6. UTILITY ANALYSIS",
        results["utility"]
    )

    display(
        "7. SOURCE DISTRIBUTION",
        results["source"]
    )

    print("\n8. AVAILABLE DASHBOARD FILTERS")

    for key, value in results["filter_options"].items():
        print(key, ":", value)

    # ------------------------------------------------------
    # TEST 2: SELECTED FILTERS
    # ------------------------------------------------------

    print("\n" + "=" * 65)
    print("TEST 2: NBPDCL - NB - MI")
    print("=" * 65)

    selected_filters = {

        "source": "NB",

        "utility": "NBPDCL",

        "installation_type": "MI",

        "start_date": "2026-11-01",

        "end_date": "2026-11-11"

    }

    filtered_results = get_dashboard_data(
        selected_filters
    )

    display(
        "FILTERED KPI SUMMARY",
        filtered_results["kpis"]
    )

    display(
        "FILTERED DAILY TREND",
        filtered_results["daily_trend"]
    )

    display(
        "FILTERED DIVISION ANALYSIS",
        filtered_results["division"]
    )

    print("\n" + "=" * 65)
    print("DASHBOARD ENGINE TEST COMPLETED")
    print("=" * 65)


if __name__ == "__main__":
    main()
