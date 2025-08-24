CREATE TABLE IF NOT EXISTS products_silver (
    product_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC NOT NULL,
    currency TEXT NOT NULL,
    rating NUMERIC NOT NULL,
    in_stock BOOLEAN NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    source TEXT
);

CREATE TABLE IF NOT EXISTS category_price_summary_gold (
    category TEXT PRIMARY KEY,
    avg_price NUMERIC NOT NULL,
    avg_rating NUMERIC NOT NULL,
    item_count INTEGER NOT NULL,
    last_refresh_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
