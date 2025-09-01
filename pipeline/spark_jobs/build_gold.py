from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from datetime import datetime

def run(silver_dir: str, gold_dir: str):
    """
    Build Gold layer aggregations from Silver data.
    
    Args:
        silver_dir: Directory containing Silver Parquet files
        gold_dir: Directory to write Gold Parquet
    """
    spark = SparkSession.builder \
        .appName("Build Gold") \
        .getOrCreate()
    
    try:
        # Read Silver data
        df = spark.read.parquet(silver_dir)
        
        # Compute category-level aggregations
        now = datetime.now()
        gold_df = df.groupBy("category") \
            .agg(
                F.avg("price").alias("avg_price"),
                F.avg("rating").alias("avg_rating"),
                F.count("*").alias("item_count")
            ) \
            .withColumn("last_refresh_ts", F.lit(now))
        
        # Round averages to 2 decimal places
        gold_df = gold_df \
            .withColumn("avg_price", F.round("avg_price", 2)) \
            .withColumn("avg_rating", F.round("avg_rating", 1))
        
        # Write Gold Parquet
        gold_df.write \
            .mode("overwrite") \
            .parquet(gold_dir)
        
    finally:
        spark.stop()
