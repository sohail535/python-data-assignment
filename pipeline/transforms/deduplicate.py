# Implement deduplication: keep the row with the most recent last_updated per product_id.
from typing import Iterable, List
from pipeline.models import Product

def deduplicate_keep_latest(products: Iterable[Product]) -> List[Product]:
    pass  # TODO
