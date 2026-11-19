
import duckdb

from config.settings import PARQUET_FILES


DATE_COLUMNS = {
    "NB": "mi_updated_at",
    "SB": "mi_updated_at",
    "NMI": "completion_date"
}

con = duckdb.connect(database=":memory:")

try:

    for source, file_path in PARQUET_FILES.items():

        column = DATE_COLUMNS[source]

        print("\n" + "=" * 65)
        print("SOURCE:", source)
        print("FILE:", file_path)
        print("=" * 65)

        if not file_path.exists():
            print("FILE NOT FOUND")
            continue

        query = f"""
            SELECT
                CAST("{column}" AS VARCHAR) AS raw_date,
                LENGTH(CAST("{column}" AS VARCHAR)) AS date_length,

                TRY_STRPTIME(
                    TRIM(CAST("{column}" AS VARCHAR)),
                    '%m/%d/%Y'
                ) AS format_1,

                TRY_STRPTIME(
                    TRIM(CAST("{column}" AS VARCHAR)),
                    '%Y-%m-%d'
                ) AS format_2,

                TRY_CAST(
                    TRIM(CAST("{column}" AS VARCHAR))
                    AS TIMESTAMP
                ) AS format_3

            FROM read_parquet(?)

            WHERE "{column}" IS NOT NULL

            LIMIT 10
        """

        result = con.execute(
            query,
            [str(file_path)]
        ).fetchall()

        print("RAW DATE | LENGTH | MM/DD/YYYY | YYYY-MM-DD | TRY CAST")

        for row in result:
            print(row)

        print("\nDistinct date examples:")

        distinct_query = f"""
            SELECT DISTINCT
                CAST("{column}" AS VARCHAR)
            FROM read_parquet(?)
            WHERE "{column}" IS NOT NULL
            LIMIT 15
        """

        distinct = con.execute(
            distinct_query,
            [str(file_path)]
        ).fetchall()

        for item in distinct:
            print(repr(item[0]))

finally:
    con.close()

print("\nDATE DIAGNOSTICS COMPLETED")
