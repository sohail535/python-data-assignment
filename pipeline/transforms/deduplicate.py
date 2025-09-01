from typing import Iterable, List, Dict
from pipeline.models import Product

def deduplicate_keep_latest(products: Iterable[Product]) -> List[Product]:
    """
    Deduplicate products by product_id, keeping the version with the most recent last_updated timestamp.
    """
    product_map: Dict[str, Product] = {}
    
    for product in products:
        if (product.product_id not in product_map or 
            product.last_updated > product_map[product.product_id].last_updated):
            product_map[product.product_id] = product
    
    return list(product_map.values())
