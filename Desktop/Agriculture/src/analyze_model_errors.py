
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "data" / "processed" / "test_predictions_enriched.csv"
OUT = ROOT / "data" / "processed"

df = pd.read_csv(FILE)

df["error"] = df["predicted_yield"] - df["actual_yield"]
df["absolute_error"] = df["error"].abs()

# Calculate percentage error only where actual yield is nonzero
valid = df["actual_yield"].abs() > 1e-9
df["percentage_error"] = np.nan
df.loc[valid, "percentage_error"] = (
    df.loc[valid, "absolute_error"]
    / df.loc[valid, "actual_yield"].abs()
) * 100

# Summarize performance for each crop
summary = df.groupby("crop").agg(
    records=("actual_yield", "size"),
    actual_mean=("actual_yield", "mean"),
    predicted_mean=("predicted_yield", "mean"),
    MAE=("absolute_error", "mean"),
    RMSE=("error", lambda x: np.sqrt(np.mean(x**2))),
    mean_percentage_error=("percentage_error", "mean"),
    within_20_percent=("percentage_error",
                       lambda x: (x <= 20).mean() * 100)
).reset_index()

summary = summary.sort_values("MAE", ascending=False)

summary.to_csv(
    OUT / "crop_model_error_analysis.csv",
    index=False
)

print("\n===== WORST 15 CROPS BY MAE =====")
print(summary.head(15).round(3).to_string(index=False))

print("\nSaved report:")
print(OUT / "crop_model_error_analysis.csv")

