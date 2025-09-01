import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from prefect import flow, task # type: ignore
import logging
from json import JSONEncoder
import pyarrow.parquet as pq
from pipeline.io.parsers import parse_json, parse_csv, parse_xml, parse_parquet
from pipeline.io.api_client import fetch_all_products
from pipeline.io.scraper import scrape_dynamic_products
from pipeline.quality.validation import validate
from pipeline.storage.postgres_io import upsert_products, upsert_gold
from pipeline.spark_jobs import bronze_to_silver, build_gold as build_gold_job
from pipeline.models import ProductSilver, CategoryPriceSummaryGold

logger = logging.getLogger(__name__)

# Get service URLs from environment variables or use defaults for local development
API_BASE_URL = os.getenv('API_BASE_URL', 'http://mock_api:5000')
WEBSITE_URL = os.getenv('WEBSITE_URL', 'http://mock_website:80')


class DateTimeEncoder(JSONEncoder):
    def default(self, o: object):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

@task
def extract_files():
    """Extract data from files and write to Bronze layer."""
    bronze_dir = Path("data/bronze")
    bronze_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse each format
    products = []
    products.extend(parse_json("data/raw/products.json"))
    products.extend(parse_csv("data/raw/products.csv"))
    products.extend(parse_xml("data/raw/products.xml"))
    
    # Write to Bronze JSONL
    output_path = bronze_dir / "files.jsonl"
    with output_path.open('w') as f:
        for product in products:
            product_dict = {
                'product_id': product.product_id,
                'name': product.name,
                'category': product.category,
                'price': product.price,
                'currency': product.currency,
                'rating': product.rating,
                'in_stock': product.in_stock,
                'last_updated': product.last_updated,
                'source': product.source,
                'ingested_at': product.ingested_at
            }
            f.write(json.dumps(product_dict, cls=DateTimeEncoder) + '\n')
    
    return len(products)

@task
def extract_api():
    """Extract data from API and write to Bronze layer."""
    bronze_dir = Path("data/bronze")
    bronze_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch API data using service URL from environment
    base_url = f"{API_BASE_URL}/api/products"
    logger.info(f"Fetching products from API: {base_url}")
    products = asyncio.run(fetch_all_products(base_url=base_url))
    logger.info(f"Fetched {len(products)} products from API")
    
    # Write to Bronze JSONL
    output_path = bronze_dir / "api.jsonl"
    with output_path.open('w') as f:
        for product in products:
            f.write(json.dumps(product, cls=DateTimeEncoder) + '\n')
    
    return len(products)

@task
def extract_web():
    """Extract data from web scraping and write to Bronze layer."""
    bronze_dir = Path("data/bronze")
    bronze_dir.mkdir(parents=True, exist_ok=True)
    
    # Scrape products using service URL from environment
    products = scrape_dynamic_products(f"{WEBSITE_URL}")  # The index page is already set to products.html
    
    # Write to Bronze JSONL
    output_path = bronze_dir / "web.jsonl"
    with output_path.open('w') as f:
        for product in products:
            f.write(json.dumps(product, cls=DateTimeEncoder) + '\n')
    
    return len(products)

@task
def spark_bronze_to_silver():
    """Transform Bronze to Silver using Spark."""
    bronze_to_silver.run(
        input_dir="data/bronze",
        output_dir="data/silver/products_silver.parquet"
    )

@task
def validate_silver():
    """Validate Silver data and write rejected records."""
    # Read Silver Parquet using the parser
    products = parse_parquet("data/silver/products_silver.parquet")
    
    # Validate
    valid_products, rejected_products = validate(products)
    
    # Write rejected records
    if rejected_products:
        output_path = Path("data/silver/rejected.jsonl")
        with output_path.open('w') as f:
            for product in rejected_products:
                f.write(json.dumps(product.__dict__, cls=DateTimeEncoder) + '\n')
    
    # Replace Product with ProductSilver for Silver-related tasks
    valid_products = [
        ProductSilver(
            product_id=product.product_id,
            name=product.name,
            category=product.category,
            price=product.price,
            currency=product.currency,
            rating=product.rating,
            in_stock=product.in_stock,
            last_updated=product.last_updated,
            source=product.source,
            ingested_at=product.ingested_at
        )
        for product in valid_products
    ]
    
    return len(valid_products), len(rejected_products)

@task
def load_silver_to_db():
    """Load valid Silver data to Postgres."""
    try:
        # Read validated Silver products
        products = parse_parquet("data/silver/products_silver.parquet")
        valid_products, _ = validate(products)
        
        # Upsert to database
        return upsert_products(valid_products)
    except Exception as e:
        logger.error(f"Failed to load to database: {e}")
        return 0

@task
def build_gold():
    """Build Gold aggregates and load to both Parquet and Postgres."""
    # Run Spark job to build Gold
    build_gold_job.run(
        silver_dir="data/silver/products_silver.parquet",
        gold_dir="data/gold/category_price_summary.parquet"
    )
    
    try:
        # Read gold data directly using pyarrow
        table = pq.read_table("data/gold/category_price_summary.parquet")
        df = table.to_pandas()
        
        # Convert to list of dicts for database insert
        gold_data = df.to_dict('records')
        return upsert_gold(gold_data)
    except Exception as e:
        logger.error(f"Failed to load Gold to database: {e}")
        return 0

@flow(name="Product Data Pipeline")
def pipeline():
    """Main pipeline flow."""
    # Extract phase (parallel)
    files_count = extract_files()
    api_count = extract_api()
    web_count = extract_web()
    
    logger.info(f"Extracted {files_count} products from files")
    logger.info(f"Extracted {api_count} products from API")
    logger.info(f"Extracted {web_count} products from web")
    
    # Transform phase
    spark_bronze_to_silver()
    valid_count, rejected_count = validate_silver()
    logger.info(f"Validated {valid_count} products, rejected {rejected_count}")
    
    # Load phase
    loaded_count = load_silver_to_db()
    logger.info(f"Loaded {loaded_count} products to database")
    
    # Build Gold
    categories_count = build_gold()
    logger.info(f"Built Gold summaries for {categories_count} categories")

if __name__ == "__main__":
    pipeline()
