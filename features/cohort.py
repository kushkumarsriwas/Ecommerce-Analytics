import pandas as pd
import numpy as np
def build_cohort_analysis(orders):
    """Build monthly customer cohorts and retention matrix."""
    df = orders.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce"
    )
    df = df.dropna(
        subset=["customer_id", "order_purchase_timestamp"]
    )
    df["order_month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
    )
    first_purchase = (
        df.groupby("customer_id")["order_month"]
        .min()
        .rename("cohort_month")
    )
    df = df.join(first_purchase, on="customer_id")
    df["cohort_index"] = (
        (df["order_month"].dt.year - df["cohort_month"].dt.year) * 12
        + (df["order_month"].dt.month - df["cohort_month"].dt.month)
        + 1
    )
    cohort_data = (
        df.groupby(["cohort_month", "cohort_index"])["customer_id"]
        .nunique()
        .reset_index()
    )
    retention = cohort_data.pivot(
        index="cohort_month",
        columns="cohort_index",
        values="customer_id",
    )
    cohort_sizes = retention.iloc[:, 0]
    retention_rate = retention.divide(
        cohort_sizes,
        axis=0
    ) * 100
    return retention, retention_rate
