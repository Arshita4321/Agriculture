
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "data" / "eda_reports"
CHART_DIR = REPORT_DIR / "charts"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)


def main():
    files = list(RAW_DIR.glob("*.csv"))

    if not files:
        print("No CSV files found in:", RAW_DIR)
        return

    overview = []
    missing_reports = []
    numeric_reports = []

    for file in files:
        print("\n" + "=" * 65)
        print("FILE:", file.name)

        try:
            # Skip comment lines, if any. NASA files may need
            # special header handling and will be reviewed separately.
            df = pd.read_csv(file, comment="#", on_bad_lines="warn")
        except Exception as exc:
            print("Could not parse this CSV:", exc)
            print("It may contain metadata before its column header.")
            continue

        print("Rows:", len(df))
        print("Columns:", df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head().to_string(index=False))
        print("\nData types:")
        print(df.dtypes.to_string())

        duplicates = int(df.duplicated().sum())
        print("\nExact duplicate rows:", duplicates)

        overview.append({
            "file": file.name,
            "rows": len(df),
            "columns": len(df.columns),
            "duplicates": duplicates
        })

        missing = df.isna().sum()
        missing_pct = (missing / max(len(df), 1) * 100).round(2)

        print("\nMissing values:")
        print(pd.DataFrame({
            "missing_count": missing,
            "missing_percent": missing_pct
        }).to_string())

        for col in df.columns:
            missing_reports.append({
                "file": file.name,
                "column": col,
                "missing_count": int(missing[col]),
                "missing_percent": float(missing_pct[col])
            })

        # Convert columns only if most non-empty values are numeric.
        for col in df.columns:
            if df[col].dtype == "object":
                converted = pd.to_numeric(df[col], errors="coerce")
                nonempty = df[col].notna().sum()

                if nonempty and converted.notna().sum() / nonempty >= 0.9:
                    df[col] = converted

        numeric = df.select_dtypes(include="number")

        if not numeric.empty:
            print("\nNumeric statistics:")
            print(numeric.describe().round(3).to_string())

            stats = numeric.describe().T
            stats.insert(0, "file", file.name)
            numeric_reports.append(stats.reset_index(names="column"))

            # Histograms for numeric columns
            for col in numeric.columns:
                values = numeric[col].dropna()

                if len(values) > 1 and values.nunique() > 1:
                    plt.figure(figsize=(8, 4))
                    plt.hist(values, bins=30, edgecolor="black")
                    plt.title(f"{file.stem}: {col} distribution")
                    plt.xlabel(col)
                    plt.ylabel("Frequency")
                    plt.tight_layout()
                    plt.savefig(
                        CHART_DIR / f"{file.stem}_{col}_hist.png"
                    )
                    plt.close()

            # Correlation matrix
            if len(numeric.columns) >= 2:
                corr = numeric.corr()
                fig, ax = plt.subplots(figsize=(9, 7))
                image = ax.imshow(corr, vmin=-1, vmax=1, aspect="auto")
                ax.set_xticks(range(len(corr.columns)))
                ax.set_yticks(range(len(corr.columns)))
                ax.set_xticklabels(corr.columns, rotation=90)
                ax.set_yticklabels(corr.columns)
                fig.colorbar(image, ax=ax, label="Correlation")
                ax.set_title(f"{file.stem}: correlation")
                fig.tight_layout()
                fig.savefig(CHART_DIR / f"{file.stem}_correlation.png")
                plt.close(fig)

    if overview:
        pd.DataFrame(overview).to_csv(
            REPORT_DIR / "dataset_overview.csv", index=False
        )

    if missing_reports:
        pd.DataFrame(missing_reports).to_csv(
            REPORT_DIR / "missing_values.csv", index=False
        )

    if numeric_reports:
        pd.concat(numeric_reports, ignore_index=True).to_csv(
            REPORT_DIR / "numeric_statistics.csv", index=False
        )

    print("\nEDA COMPLETED")
    print("Reports saved to:", REPORT_DIR)
    print("Charts saved to:", CHART_DIR)


if __name__ == "__main__":
    main()
