from pathlib import Path
import pandas as pd

file_path = Path("data/raw/ludhiana_weather.csv")

if not file_path.exists():
    raise FileNotFoundError(f"Dataset not found: {file_path}")

# Find the actual CSV header because NASA files may
# contain metadata before the data table.
with open(file_path, "r", encoding="utf-8-sig") as f:
    lines = f.readlines()

header_index = next(
    (
        i for i, line in enumerate(lines)
        if line.strip().startswith("YEAR,MO,DY,")
    ),
    None,
)

if header_index is None:
    raise ValueError(
        "Could not find the YEAR,MO,DY header. "
        "Inspect the first 15 lines of the downloaded CSV."
    )

df = pd.read_csv(file_path, skiprows=header_index)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst five records:")
print(df.head())

print("\nDataset dimensions:")
print(df.shape)

print("\nMissing values:")
print(df.isna().sum())