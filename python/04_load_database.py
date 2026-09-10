import os
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
BASE = Path(__file__).resolve().parent.parent
CLEAN = BASE / "data" / "cleaned"
engine = create_engine(
    os.getenv("DATABASE_URL")
)
tables = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "category_translation"
}
for file, table in tables.items():
    print(f"Loading {file}...")
    df = pd.read_csv(CLEAN / file)
    df.to_sql(table, engine, if_exists="append", index=False, method="multi")
    print(f"Loaded {len(df):,} rows into {table}")
print("\nAll data loaded successfully.")





