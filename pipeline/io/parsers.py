# Implement multi-format parsers that return a list of Product objects.
# Functions are intentionally left as stubs.
from pathlib import Path
from typing import List
from pipeline.models import Product

def parse_json(path: str | Path) -> List[Product]:
    pass  # TODO

def parse_csv(path: str | Path) -> List[Product]:
    pass  # TODO

def parse_xml(path: str | Path) -> List[Product]:
    pass  # TODO

def parse_parquet(path: str | Path) -> List[Product]:
    pass  # TODO
