from typing import Iterable, List
from pipeline.models import Product

def normalize(products: Iterable[Product]) -> List[Product]:
    """
    Normalize product fields according to business rules:
    - Convert category to lowercase
    - Convert currency to uppercase
    - Clamp rating between 0 and 5
    - Round price to 2 decimal places
    """
    return [product.normalize() for product in products]
