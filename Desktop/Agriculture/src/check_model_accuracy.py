
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "data" / "processed" / "test_predictions_enriched.csv"

df = pd.read_csv(FILE)

actual = df["actual_yield"]
predicted = df["predicted_yield"]

# Avoid division by zero for percentage errors
valid = actual.abs() > 1e-9
percentage_error = (
    (predicted[valid] - actual[valid]).abs()
    / actual[valid].abs()
) * 100

within_10 = (percentage_error <= 10).mean() * 100
within_20 = (percentage_error <= 20).mean() * 100

print("\n===== MODEL PERFORMANCE =====")
print(f"Test records: {len(df)}")
print(f"R2 score: {1 - ((actual - predicted) ** 2).sum() / ((actual - actual.mean()) ** 2).sum():.4f}")
print(f"Predictions within 10% error: {within_10:.2f}%")
print(f"Predictions within 20% error: {within_20:.2f}%")
print(f"Records used for percentage error: {valid.sum()}")
print(f"Records with zero actual yield: {(~valid).sum()}")
