from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, FloatType, BooleanType, TimestampType

def create_product_schema():
    return StructType([
        StructField("product_id", StringType(), False),
        StructField("name", StringType(), False),
        StructField("category", StringType(), False),
        StructField("price", FloatType(), False),
        StructField("currency", StringType(), False),
        StructField("rating", FloatType(), False),
        StructField("in_stock", BooleanType(), False),
        StructField("last_updated", TimestampType(), False),
        StructField("source", StringType(), True),
        StructField("ingested_at", TimestampType(), True)
    ])

def normalize_dataframe(df):
    """Apply normalization rules to the dataframe."""
    return df.withColumn("category", F.lower(F.col("category"))) \
             .withColumn("currency", F.upper(F.col("currency"))) \
             .withColumn("rating", F.least(F.greatest(F.col("rating"), F.lit(0.0)), F.lit(5.0))) \
             .withColumn("price", F.round(F.col("price"), 2))

def run(input_dir: str, output_dir: str):
    """
    Process Bronze JSONL files to create Silver Parquet.
    
    Args:
        input_dir: Directory containing Bronze JSONL files
        output_dir: Directory to write Silver Parquet
    """
    spark = SparkSession.builder \
        .appName("Bronze to Silver") \
        .getOrCreate()
    
    try:
        # Read all Bronze JSONL files
        schema = create_product_schema()
        df = spark.read.json(f"{input_dir}/*.jsonl", schema=schema)
        
        # Normalize fields
        df = normalize_dataframe(df)
        
        # Deduplicate by product_id, keeping newest last_updated
        window_spec = Window.partitionBy("product_id").orderBy(F.col("last_updated").desc())
        df = df.withColumn("row_num", F.row_number().over(window_spec)) \
             .filter(F.col("row_num") == 1) \
             .drop("row_num")
        
        # Write to Parquet
        df.write \
          .mode("overwrite") \
          .partitionBy("category") \
          .parquet(output_dir)
        
    finally:
        spark.stop()
