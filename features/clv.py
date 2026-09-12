import pandas as pd
import numpy as np
def calculate_clv(orders):
    """Estimate customer lifetime value from historical purchasing behavior."""
    df = orders.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce"
    )
    df = df.dropna(
        subset=[
            "customer_id",
            "order_purchase_timestamp"
        ]
    )
    if "payment_value" in df.columns:
        revenue_column = "payment_value"
    elif "price" in df.columns:
        revenue_column = "price"
    else:
        raise ValueError(
            "Orders dataframe must contain payment_value or price."
        )
    customer = (
        df.groupby("customer_id")
        .agg(
            total_revenue=(revenue_column, "sum"),
            total_orders=("order_id", "nunique"),
            first_purchase=(
                "order_purchase_timestamp",
                "min"
            ),
            last_purchase=(
                "order_purchase_timestamp",
                "max"
            ),
        )
        .reset_index()
    )
    customer["customer_lifetime_days"] = (
        customer["last_purchase"]
        - customer["first_purchase"]
    ).dt.days
    customer["customer_lifetime_years"] = (
        customer["customer_lifetime_days"] / 365
    )
    customer["average_order_value"] = (
        customer["total_revenue"]
        / customer["total_orders"]
    )
    customer["purchase_frequency"] = np.where(
        customer["customer_lifetime_years"] > 0,
        customer["total_orders"]
        / customer["customer_lifetime_years"],
        customer["total_orders"]
    )
    customer["estimated_annual_value"] = (
        customer["average_order_value"]
        * customer["purchase_frequency"]
    )
    customer["estimated_clv"] = (
        customer["estimated_annual_value"]
        * np.maximum(
            customer["customer_lifetime_years"],
            1
        )
    )
    return customer.sort_values(
        "estimated_clv",
        ascending=False
    )
