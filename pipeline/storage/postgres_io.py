# Implement Postgres upsert for Silver and Gold tables.
from typing import Iterable, Dict, Any
from pipeline.models import Product

def init_schema():
    pass  # TODO

def upsert_products(products: Iterable[Product]) -> int:
    pass  # TODO

def upsert_gold(rows: Iterable[Dict[str, Any]]) -> int:
    pass  # TODO
