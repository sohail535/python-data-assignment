from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import os, json

app = FastAPI(title="Assignment Mock API")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "products.json")
with open(DATA_PATH, "r") as f:
    DATA: List[Dict[str, Any]] = json.load(f)

REQ_COUNT = 0
RATE_LIMIT_EVERY_N = int(os.getenv("RATE_LIMIT_EVERY_N","7"))

@app.get("/health")
def health():
    return {"status": "ok", "count": REQ_COUNT}

@app.get("/products")
def products(page: int = 1, size: int = 10):
    global REQ_COUNT
    REQ_COUNT += 1
    if RATE_LIMIT_EVERY_N > 0 and REQ_COUNT % RATE_LIMIT_EVERY_N == 0:
        headers = {"Retry-After": "2"}
        raise HTTPException(status_code=429, detail="Rate limit exceeded", headers=headers)
    start = (page-1) * size
    end = start + size
    slice_ = DATA[start:end]
    return {"page": page, "size": size, "total": len(DATA), "items": slice_}
