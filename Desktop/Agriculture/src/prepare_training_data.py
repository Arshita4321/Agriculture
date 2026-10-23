from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed" / "agri_training_data"


def main():
    spark = (
        SparkSession.builder
        .appName("AgricultureFeatureJoin")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    try:
        crop_path = RAW / "crop_yield.csv"
        soil_path = RAW / "state_soil_data.csv"
        weather_path = RAW / "state_weather_data_1997_2020.csv"

        for path in [crop_path, soil_path, weather_path]:
            if not path.exists():
                raise FileNotFoundError(f"Missing file: {path}")

        crops = (
            spark.read.option("header", True)
            .option("inferSchema", True)
            .csv(str(crop_path))
        )
        soil = (
            spark.read.option("header", True)
            .option("inferSchema", True)
            .csv(str(soil_path))
        )
        weather = (
            spark.read.option("header", True)
            .option("inferSchema", True)
            .csv(str(weather_path))
        )

        crops = (
            crops.withColumn("state_key", F.lower(F.trim(F.col("state"))))
            .withColumn("year", F.col("year").cast("int"))
        )
        soil = soil.withColumn(
            "state_key", F.lower(F.trim(F.col("state")))
        )
        weather = (
            weather.withColumn(
                "state_key", F.lower(F.trim(F.col("state")))
            )
            .withColumn("year", F.col("year").cast("int"))
        )

        soil_duplicates = (
            soil.groupBy("state_key")
            .count()
            .filter(F.col("count") > 1)
            .count()
        )
        weather_duplicates = (
            weather.groupBy("state_key", "year")
            .count()
            .filter(F.col("count") > 1)
            .count()
        )

        if soil_duplicates:
            raise ValueError(
                f"Soil data has {soil_duplicates} duplicate state keys."
            )
        if weather_duplicates:
            raise ValueError(
                f"Weather data has {weather_duplicates} duplicate state/year keys."
            )

        soil = soil.select(
            "state_key",
            F.col("N").cast("double").alias("soil_N"),
            F.col("P").cast("double").alias("soil_P"),
            F.col("K").cast("double").alias("soil_K"),
            F.col("pH").cast("double").alias("soil_pH"),
        )

        weather = weather.select(
            "state_key",
            "year",
            F.col("avg_temp_c").cast("double"),
            F.col("total_rainfall_mm").cast("double"),
            F.col("avg_humidity_percent").cast("double"),
        )

        original_count = crops.count()

        enriched = (
            crops.join(soil, on="state_key", how="left")
            .join(weather, on=["state_key", "year"], how="left")
            .drop("state_key")
        )

        enriched_count = enriched.count()

        print("\nOriginal crop rows:", original_count)
        print("Enriched rows:", enriched_count)

        print("\nMissing soil/weather matches:")
        enriched.select(
            F.sum(
                F.col("soil_N").isNull().cast("int")
            ).alias("missing_soil"),
            F.sum(
                F.col("avg_temp_c").isNull().cast("int")
            ).alias("missing_weather"),
        ).show()

        print("\nEnriched dataset schema:")
        enriched.printSchema()

        print("\nExample enriched records:")
        enriched.select(
            "crop", "state", "year", "yield",
            "soil_N", "soil_P", "soil_K", "soil_pH",
            "avg_temp_c", "total_rainfall_mm",
            "avg_humidity_percent",
        ).show(10, truncate=False)

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        enriched.write.mode("overwrite").parquet(str(OUTPUT))

        print("\nEnriched dataset saved to:", OUTPUT)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()