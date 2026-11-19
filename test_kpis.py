
from analytics.kpi_engine import run_all_kpis


def main():

    print("\n" + "=" * 60)
    print("INSTALLATION INTELLIGENCE - KPI REPORT")
    print("=" * 60)

    results = run_all_kpis()

    print("\n1. OVERALL KPI SUMMARY")
    print(results["summary"].to_string(index=False))

    print("\n2. SOURCE DISTRIBUTION")
    print(results["source"].to_string(index=False))

    print("\n3. TOP 20 DIVISIONS")
    print(
        results["division"]
        .head(20)
        .to_string(index=False)
    )

    print("\n4. TOP 20 VENDORS")
    print(
        results["vendor"]
        .head(20)
        .to_string(index=False)
    )

    print("\n5. UTILITY SUMMARY")
    print(results["utility"].to_string(index=False))

    print("\n" + "=" * 60)
    print("KPI ENGINE EXECUTED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
