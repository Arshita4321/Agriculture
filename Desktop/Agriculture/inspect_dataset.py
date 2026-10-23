
from pathlib import Path
import pandas as pd

folder = Path("data/raw")

for file in sorted(folder.glob("*.csv")):
    print("\n" + "=" * 60)
    print("FILE:", file.name)

    try:
        if file.name == "ludhiana_weather.csv":
            lines = file.read_text(
                encoding="utf-8-sig"
            ).splitlines()

            header = next(
                (
                    i for i, line in enumerate(lines)
                    if line.strip().startswith("YEAR,MO,DY,")
                ),
                None,
            )

            if header is None:
                print("NASA table header not found.")
                print("\n".join(lines[:15]))
                continue

            df = pd.read_csv(file, skiprows=header, nrows=1000)
        else:
            df = pd.read_csv(file, nrows=1000)

        print("Columns:", df.columns.tolist())
        print("\nFirst five rows:")
        print(df.head().to_string(index=False))
        print("\nData types:")
        print(df.dtypes)
        print("\nMissing values in inspected rows:")
        print(df.isna().sum())

    except Exception as e:
        print("Could not inspect this file:", e)
