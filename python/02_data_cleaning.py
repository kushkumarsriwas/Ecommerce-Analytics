import pandas as pd
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data"
CLEAN = RAW / "cleaned"
CLEAN.mkdir(exist_ok=True)
files = [
    "olist_customers_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv"
]
for file in files:
    df = pd.read_csv(RAW / file)
    # Remove completely duplicated rows
    df = df.drop_duplicates()
    # Convert date columns
    for col in df.columns:
        if "date" in col or "timestamp" in col:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    # Product data
    if file == "olist_products_dataset.csv":
        df["product_category_name"] = df["product_category_name"].fillna("unknown")
    # Review text is optional
    if file == "olist_order_reviews_dataset.csv":
        df["review_comment_title"] = df["review_comment_title"].fillna("")
        df["review_comment_message"] = df["review_comment_message"].fillna("")
    # Keep missing order dates because they can legitimately represent
    # orders that were not completed/delivered.
    output = CLEAN / file
    df.to_csv(output, index=False)
    print(f"{file}: {len(df):,} rows -> cleaned")
print("\nCleaning completed successfully.")
