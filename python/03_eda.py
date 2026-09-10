import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "cleaned"
orders = pd.read_csv(DATA / "olist_orders_dataset.csv", parse_dates=[
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
])
items = pd.read_csv(DATA / "olist_order_items_dataset.csv")
customers = pd.read_csv(DATA / "olist_customers_dataset.csv")
products = pd.read_csv(DATA / "olist_products_dataset.csv")
reviews = pd.read_csv(DATA / "olist_order_reviews_dataset.csv")
# Revenue by month
sales = orders.merge(items, on="order_id")
monthly = (
    sales.assign(month=sales["order_purchase_timestamp"].dt.to_period("M"))
    .groupby("month")
    .agg(
        revenue=("price", "sum"),
        orders=("order_id", "nunique")
    )
    .reset_index()
)
monthly["month"] = monthly["month"].astype(str)
print("\nMONTHLY SALES")
print(monthly.to_string(index=False))
# Customer analysis
customer_orders = (
    orders.merge(customers, on="customer_id")
    .groupby("customer_unique_id")["order_id"]
    .nunique()
)
print("\nCUSTOMER TYPE")
print(
    customer_orders
    .value_counts()
    .rename_axis("orders")
    .reset_index(name="customers")
)
# Review analysis
print("\nREVIEW SCORES")
print(reviews["review_score"].value_counts().sort_index())
# Delivery analysis
delivered = orders.dropna(subset=["order_delivered_customer_date"]).copy()
delivered["delivery_days"] = (
    delivered["order_delivered_customer_date"]
    - delivered["order_purchase_timestamp"]
).dt.total_seconds() / 86400
delivered["late"] = (
    delivered["order_delivered_customer_date"]
    > delivered["order_estimated_delivery_date"]
)
print("\nDELIVERY ANALYSIS")
print(f"Average delivery days: {delivered['delivery_days'].mean():.2f}")
print(f"Late delivery rate: {delivered['late'].mean() * 100:.2f}%")
# Basic statistics
print("\nREVENUE STATISTICS")
print(sales["price"].describe())
# Save monthly analysis
OUTPUT = BASE / "data" / "monthly_sales.csv"
monthly.to_csv(OUTPUT, index=False)
print(f"\nSaved: {OUTPUT}")
print("\nEDA completed successfully.")
