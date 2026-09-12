import pandas as pd
import numpy as np
def generate_kpi_summary(orders):
    """Generate executive KPIs and period-over-period changes."""
    df = orders.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce",
    )
    df = df.dropna(subset=["order_purchase_timestamp"])
    if "payment_value" not in df.columns:
        raise ValueError("Orders dataframe must contain payment_value.")
    df["month"] = df["order_purchase_timestamp"].dt.to_period("M")
    monthly = (
        df.groupby("month")
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
        .reset_index()
    )
    monthly["aov"] = np.where(
        monthly["orders"] > 0,
        monthly["revenue"] / monthly["orders"],
        0,
    )
    monthly["revenue_growth"] = monthly["revenue"].pct_change() * 100
    monthly["orders_growth"] = monthly["orders"].pct_change() * 100
    monthly["customer_growth"] = monthly["customers"].pct_change() * 100
    monthly["aov_growth"] = monthly["aov"].pct_change() * 100
    return monthly
