from typing import Iterable, List, Tuple
from pipeline.models import ProductSilver

def validate(products: Iterable[ProductSilver]) -> Tuple[List[ProductSilver], List[ProductSilver]]:
    """
    Validate products according to business rules:
    - Required fields are present
    - Price is >= 0
    - Rating is between 0 and 5
    
    Returns a tuple of (valid_products, rejected_products)
    """
    valid_products: List[ProductSilver] = []
    rejected_products: List[ProductSilver] = []
    
    for product in products:
        is_valid = True
        
        # Check required fields
        required_fields = [
            getattr(product, 'product_id', ''),
            getattr(product, 'name', ''),
            getattr(product, 'category', ''),
            getattr(product, 'currency', '')
        ]
        
        if not all(bool(field) and bool(str(field).strip()) for field in required_fields):
            is_valid = False
            
        # Check price >= 0
        try:
            price = float(getattr(product, 'price', 0))
            if price < 0:
                is_valid = False
        except (TypeError, ValueError):
            is_valid = False
            
        # Check rating between 0 and 5
        try:
            rating = float(getattr(product, 'rating', 0))
            if not (0 <= rating <= 5):
                is_valid = False
        except (TypeError, ValueError):
            is_valid = False
            
        if is_valid:
            valid_products.append(product)
        else:
            rejected_products.append(product)
    
    return valid_products, rejected_products
