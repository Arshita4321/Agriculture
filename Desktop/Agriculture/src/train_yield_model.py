

from pathlib import Path
import json
import shutil

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    StringIndexer,
    OneHotEncoder,
    VectorAssembler
)
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

ROOT = Path(__file__).resolve().parents[1]

# Read the joined dataset, not the original crop CSV
DATA_DIR = ROOT / "data" / "processed" / "agri_training_data"

# Keep the enriched model separate from the original model
MODEL_DIR = ROOT / "models" / "yield_random_forest_enriched"
OUTPUT_DIR = ROOT / "data" / "processed"

PREDICTIONS_DIR = OUTPUT_DIR / "test_predictions_enriched_parts"
PREDICTIONS_CSV = OUTPUT_DIR / "test_predictions_enriched.csv"
METRICS_FILE = OUTPUT_DIR / "model_metrics_enriched.json"


def main():
    spark = (
        SparkSession.builder
        .appName("AgriculturalYieldModelEnriched")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    predictions = None

    try:
        if not DATA_DIR.exists():
            raise FileNotFoundError(
                f"Joined dataset not found: {DATA_DIR}. "
                "Run src/prepare_training_data.py first."
            )

        # 1. Load joined Parquet dataset
        df = spark.read.parquet(str(DATA_DIR))

        features_required = [
            "crop", "year", "season", "state",
            "fertilizer", "pesticide",
            "soil_N", "soil_P", "soil_K", "soil_pH",
            "avg_temp_c", "total_rainfall_mm",
            "avg_humidity_percent", "yield"
        ]

        missing = [
            c for c in features_required if c not in df.columns
        ]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        numeric_columns = [
            "year", "fertilizer", "pesticide",
            "soil_N", "soil_P", "soil_K", "soil_pH",
            "avg_temp_c", "total_rainfall_mm",
            "avg_humidity_percent", "yield"
        ]

        for col_name in numeric_columns:
            df = df.withColumn(
                col_name, F.col(col_name).cast("double")
            )

        df = (
            df.dropna(subset=features_required)
            .dropDuplicates()
            .filter(
                (F.col("year") > 0) & (F.col("yield") >= 0)
            )
        )

        total_rows = df.count()
        if total_rows < 20:
            raise ValueError("Too few valid records for model training.")

        print("\nJoined dataset rows used:", total_rows)

        # 2. Chronological split: older years train, newer years test
        years = [
            row["year"]
            for row in (
                df.select("year")
                .distinct()
                .orderBy("year")
                .collect()
            )
        ]

        if len(years) < 2:
            raise ValueError("At least two distinct years are required.")

        split_index = max(1, int(len(years) * 0.8))
        split_index = min(split_index, len(years) - 1)
        cutoff_year = years[split_index]

        train = df.filter(F.col("year") < cutoff_year)
        test = df.filter(F.col("year") >= cutoff_year)

        train_count = train.count()
        test_count = test.count()

        if train_count == 0 or test_count == 0:
            raise ValueError("Chronological split produced an empty set.")

        print("Training rows:", train_count)
        print("Testing rows:", test_count)
        print("Test years start at:", cutoff_year)

        # 3. Encode categorical columns
        categorical = ["crop", "season", "state"]

        indexers = [
            StringIndexer(
                inputCol=c,
                outputCol=f"{c}_index",
                handleInvalid="keep"
            )
            for c in categorical
        ]

        encoder = OneHotEncoder(
            inputCols=[f"{c}_index" for c in categorical],
            outputCols=[f"{c}_encoded" for c in categorical],
            handleInvalid="keep"
        )

        # 4. Include crop, soil, and weather information
        numeric_features = [
            "year",
            "fertilizer",
            "pesticide",
            "soil_N",
            "soil_P",
            "soil_K",
            "soil_pH",
            "avg_temp_c",
            "total_rainfall_mm",
            "avg_humidity_percent"
        ]

        assembler = VectorAssembler(
            inputCols=numeric_features + [
                "crop_encoded",
                "season_encoded",
                "state_encoded"
            ],
            outputCol="features",
            handleInvalid="error"
        )

        forest = RandomForestRegressor(
            labelCol="yield",
            featuresCol="features",
            predictionCol="prediction",
            numTrees=100,
            maxDepth=8,
            seed=42
        )

        pipeline = Pipeline(
            stages=indexers + [encoder, assembler, forest]
        )

        # 5. Train the enriched model
        print("\nTraining enriched Random Forest model...")
        model = pipeline.fit(train)

        # 6. Evaluate on later years not used for training
        predictions = model.transform(test).cache()
        predictions.count()

        def evaluate(metric):
            evaluator = RegressionEvaluator(
                labelCol="yield",
                predictionCol="prediction",
                metricName=metric
            )
            return float(evaluator.evaluate(predictions))

        metrics = {
            "model": "Random Forest Regression (Spark MLlib)",
            "features": numeric_features + categorical,
            "target": "yield",
            "split_method": "Chronological by year",
            "test_start_year": float(cutoff_year),
            "training_rows": int(train_count),
            "testing_rows": int(test_count),
            "mae": evaluate("mae"),
            "mse": evaluate("mse"),
            "rmse": evaluate("rmse"),
            "r2": evaluate("r2"),
            "interpretation": (
                "Held-out chronological regression metrics. "
                "R2 is not classification accuracy. "
                "Compare against the original model and a baseline."
            )
        }

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)

        # 7. Save enriched model
        model.write().overwrite().save(str(MODEL_DIR))

        # 8. Save metrics
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        # 9. Save predictions for charts and error analysis
        result = predictions.select(
            F.col("year").cast("int").alias("year"),
            "crop",
            "state",
            "season",
            F.col("yield").alias("actual_yield"),
            F.col("prediction").alias("predicted_yield")
        ).withColumn(
            "error",
            F.col("predicted_yield") - F.col("actual_yield")
        ).withColumn(
            "absolute_error",
            F.abs(F.col("error"))
        ).orderBy("year", "crop")

        result.coalesce(1).write.mode("overwrite").option(
            "header", True
        ).csv(str(PREDICTIONS_DIR))

        part_files = list(PREDICTIONS_DIR.glob("part-*.csv"))
        if not part_files:
            raise RuntimeError("Spark did not produce a predictions CSV.")

        shutil.copy2(part_files[0], PREDICTIONS_CSV)

        print("\n========== ENRICHED MODEL EVALUATION ==========")
        for key, value in metrics.items():
            print(f"{key}: {value}")

        print("\nSaved enriched model:", MODEL_DIR)
        print("Saved metrics:", METRICS_FILE)
        print("Saved predictions:", PREDICTIONS_CSV)

    finally:
        if predictions is not None:
            predictions.unpersist()
        spark.stop()


if __name__ == "__main__":
    main()
