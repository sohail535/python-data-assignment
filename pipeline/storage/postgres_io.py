import os
from typing import Iterable, Dict, Any
import psycopg2
from psycopg2.extras import execute_values
from pipeline.models import Product
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection from environment variables."""
    try:
        return psycopg2.connect(
            dbname=os.environ.get('POSTGRES_DB', 'products'),
            user=os.environ.get('POSTGRES_USER', 'postgres'),
            password=os.environ.get('POSTGRES_PASSWORD', 'postgres'),
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            port=os.environ.get('POSTGRES_PORT', '5432')
        )
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def upsert_products(products: Iterable[Product]) -> int:
    """
    Upsert products into the silver table.
    Returns the number of products upserted.
    """
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        with conn.cursor() as cur:
            # Convert products to tuples for bulk insert
            values = [(
                p.product_id,
                p.name,
                p.category,
                p.price,
                p.currency,
                p.rating,
                p.in_stock,
                p.last_updated,
                p.source,
                p.ingested_at
            ) for p in products]
            
            # Perform upsert
            execute_values(cur, """
                INSERT INTO products_silver (
                    product_id, name, category, price, currency,
                    rating, in_stock, last_updated, source, ingested_at
                ) VALUES %s
                ON CONFLICT (product_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    price = EXCLUDED.price,
                    currency = EXCLUDED.currency,
                    rating = EXCLUDED.rating,
                    in_stock = EXCLUDED.in_stock,
                    last_updated = EXCLUDED.last_updated,
                    source = EXCLUDED.source,
                    ingested_at = EXCLUDED.ingested_at;
            """, values)
            
            conn.commit()
            return len(values)
    except psycopg2.Error as e:
        logger.error(f"Failed to upsert products: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def upsert_gold(rows: Iterable[Dict[str, Any]]) -> int:
    """
    Upsert category summaries into the gold table.
    Returns the number of categories upserted.
    """
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        with conn.cursor() as cur:
            values = [(
                r['category'],
                r['avg_price'],
                r['avg_rating'],
                r['item_count'],
                r['last_refresh_ts']
            ) for r in rows]
            
            execute_values(cur, """
                INSERT INTO category_price_summary_gold (
                    category, avg_price, avg_rating, item_count, last_refresh_ts
                ) VALUES %s
                ON CONFLICT (category) DO UPDATE SET
                    avg_price = EXCLUDED.avg_price,
                    avg_rating = EXCLUDED.avg_rating,
                    item_count = EXCLUDED.item_count,
                    last_refresh_ts = EXCLUDED.last_refresh_ts;
            """, values)
            
            conn.commit()
            return len(values)
    except psycopg2.Error as e:
        logger.error(f"Failed to upsert gold records: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()
