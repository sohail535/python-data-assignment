import json
import csv
import xml.etree.ElementTree as ET
import pyarrow.parquet as pq

from datetime import datetime
from pathlib import Path
from typing import List, Union
from pipeline.models import ProductSilver

def parse_json(path: Union[str, Path]) -> List[ProductSilver]:
    path = Path(path)
    with path.open('r') as f:
        data = json.load(f)
    products: List[ProductSilver] = []
    for item in data:
        product = ProductSilver(
            product_id=item.get('product_id', ''),
            name=item.get('name', ''),
            category=item.get('category', '').lower(),
            price=float(item['price']) if item.get('price') else 0.0,
            currency=item.get('currency', '').upper(),
            rating=float(item['rating']) if item.get('rating') else 0.0,
            in_stock=item.get('in_stock', False),
            source='files',
            last_updated=datetime.fromisoformat(item['last_updated']) if item.get('last_updated') else datetime.now(),
            ingested_at=datetime.now()
        )
        products.append(product)
    return products

def parse_csv(path: Union[str, Path]) -> List[ProductSilver]:
    path = Path(path)
    products: List[ProductSilver] = []
    with path.open('r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['product_id'] = row['product_id']
            row['name'] = row['name']
            row['category'] = row['category']
            row['price'] = float(row['price'])
            row['currency'] = row['currency']
            row['rating'] = float(row['rating'])
            row['in_stock'] = row['in_stock'] == 'true'
            row['source'] = 'files'
            row['last_updated'] = datetime.fromisoformat(row['last_updated'])
            row['ingested_at'] = datetime.now()
            products.append(ProductSilver(**row))
    return products

def parse_xml(path: Union[str, Path]) -> List[ProductSilver]:
    path = Path(path)
    tree = ET.parse(path)
    root = tree.getroot()
    products: List[ProductSilver] = []

    for product_elem in root.findall('.//product'):
        product = ProductSilver(
            product_id=str(product_elem.findtext('product_id', default='')),
            name=str(product_elem.findtext('name', default='')),
            category=str(product_elem.findtext('category', default='')).lower(),
            price=float(product_elem.findtext('price', default='0.0') or 0.0),
            currency=str(product_elem.findtext('currency', default='')).upper(),
            rating=float(product_elem.findtext('rating', default='0.0') or 0.0),
            in_stock=(product_elem.findtext('in_stock', default='false').lower() == 'true'),
            last_updated=(datetime.fromisoformat(product_elem.findtext('last_updated', default='')) if product_elem.findtext('last_updated') else datetime.now()),
            source='files',
            ingested_at=datetime.now()
        )
        products.append(product)

    return products

def parse_parquet(path: Union[str, Path]) -> List[ProductSilver]:
    path = Path(path)
    table = pq.read_table(path)
    df = table.to_pandas()
    products: List[ProductSilver] = []

    for _, row in df.iterrows():
        product = ProductSilver(
            product_id=str(row.get('product_id', '')),
            name=str(row.get('name', '')),
            category=str(row.get('category', '')).lower(),
            price=float(row.get('price', 0.0) or 0.0),
            currency=str(row.get('currency', '')).upper(),
            rating=float(row.get('rating', 0.0) or 0.0),
            in_stock=bool(row.get('in_stock', False)),
            source=str(row.get('source', '')),
            last_updated=row.get('last_updated', datetime.now()),
            ingested_at=datetime.now()
        )
        products.append(product)

    return products
