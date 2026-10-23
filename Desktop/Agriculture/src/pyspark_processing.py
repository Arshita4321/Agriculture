
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Find the main project folder
ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "raw" / "crop_yield.csv"
OUTPUT_DIR = ROOT / "data" / "processed" / "crop_yield_parquet"
YEARLY_OUTPUT = ROOT / "data" / "processed" / "yearly_yield_summary"
CROP_OUTPUT = ROOT / "data" / "processed" / "crop_yield_summary"


def main():
    # Start Spark locally using all available CPU cores
    spark = (
        SparkSession.builder
        .appName("AgriculturalRiskIntelligence")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    try:
        # STEP 1: Check whether the dataset exists
        if not INPUT_FILE.exists():
            raise FileNotFoundError(
                f"Dataset not found: {INPUT_FILE}\n"
                "Place crop_yield.csv inside data/raw/"
            )

        # STEP 2: Load the dataset using PySpark
        df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(INPUT_FILE))
        )

        print("\n========== ORIGINAL DATA ==========")
        df.show(5, truncate=False)
        df.printSchema()

        # STEP 3: Remove duplicate rows
        df = df.dropDuplicates()

        # STEP 4: Convert numeric columns to appropriate types
        numeric_columns = [
            "year",
            "area",
            "production",
            "fertilizer",
            "pesticide",
            "yield"
        ]

        for column in numeric_columns:
            if column in df.columns:
                df = df.withColumn(
                    column,
                    F.col(column).cast("double")
                )

        # STEP 5: Remove rows missing essential information
        required_columns = [
            "crop", "year", "season", "state", "yield"
        ]

        df = df.dropna(subset=required_columns)

        # Remove invalid year and yield values
        df = df.filter(
            (F.col("year") > 0) &
            (F.col("yield") >= 0)
        )

        print("\n========== CLEANED DATA ==========")
        df.show(10, truncate=False)

        print("Total cleaned records:", df.count())

        # STEP 6: Save cleaned data as Parquet
        (
            df.write
            .mode("overwrite")
            .parquet(str(OUTPUT_DIR))
        )

        print("\nCleaned dataset saved successfully.")

        # STEP 7: Perform analysis using Spark SQL
        df.createOrReplaceTempView("crop_yields")

        yearly_summary = spark.sql("""
            SELECT
                CAST(year AS INT) AS year,
                COUNT(*) AS record_count,
                ROUND(AVG(yield), 3) AS average_yield
            FROM crop_yields
            GROUP BY year
            ORDER BY year
        """)

        print("\n========== YEARLY YIELD ANALYSIS ==========")
        yearly_summary.show(20, truncate=False)

        (
            yearly_summary.write
            .mode("overwrite")
            .parquet(str(YEARLY_OUTPUT))
        )

        # STEP 8: Analyze average yield for each crop
        crop_summary = (
            df.groupBy("crop")
            .agg(
                F.count("*").alias("record_count"),
                F.round(
                    F.avg("yield"), 3
                ).alias("average_yield")
            )
            .orderBy(F.desc("average_yield"))
        )

        print("\n========== CROP-WISE ANALYSIS ==========")
        crop_summary.show(20, truncate=False)

        (
            crop_summary.write
            .mode("overwrite")
            .parquet(str(CROP_OUTPUT))
        )

        # STEP 9: Analyze yield by state
        state_summary = (
            df.groupBy("state")
            .agg(
                F.count("*").alias("record_count"),
                F.round(
                    F.avg("yield"), 3
                ).alias("average_yield")
            )
            .orderBy(F.desc("average_yield"))
        )

        print("\n========== STATE-WISE ANALYSIS ==========")
        state_summary.show(20, truncate=False)

        print("\n========== PROCESS COMPLETED ==========")
        print("Cleaned data:", OUTPUT_DIR)
        print("Yearly summary:", YEARLY_OUTPUT)
        print("Crop summary:", CROP_OUTPUT)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
