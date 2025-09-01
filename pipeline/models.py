from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProductSilver(Base):
    __tablename__ = 'products_silver'

    product_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False) #type: ignore
    currency = Column(String(3), nullable=False)
    rating = Column(Float, nullable=False) #type: ignore
    in_stock = Column(Boolean, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    source = Column(String)
    ingested_at = Column(DateTime)

class CategoryPriceSummaryGold(Base):
    __tablename__ = 'category_price_summary_gold'

    category = Column(String, primary_key=True)
    avg_price = Column(Float, nullable=False) #type: ignore
    avg_rating = Column(Float, nullable=False) #type: ignore
    item_count = Column(Integer, nullable=False)
    last_refresh_ts = Column(DateTime, nullable=False)

@dataclass
class Product:
    product_id: str
    name: str
    category: str
    price: float
    currency: str
    rating: float
    in_stock: bool
    last_updated: datetime
    source: Optional[str] = None
    ingested_at: Optional[datetime] = None
    avg_price: Optional[float] = None
    avg_rating: Optional[float] = None
    item_count: Optional[int] = None
    last_refresh_ts: Optional[datetime] = None

    def normalize(self):
        """Normalize the product data according to business rules."""
        self.category = self.category.lower()
        self.currency = self.currency.upper()
        self.rating = max(0, min(5, self.rating))  # Clamp between 0 and 5
        self.price = round(self.price, 2)
        return self

    def validate(self) -> bool:
        """Validate the product data."""
        return all([
            self.product_id,
            self.name,
            self.category,
            self.price >= 0,
            0 <= self.rating <= 5,
        ])
