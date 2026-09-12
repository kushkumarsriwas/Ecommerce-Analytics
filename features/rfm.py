import pandas as pd
import numpy as np
def calculate_rfm(orders):
    """Calculate Recency, Frequency and Monetary value per customer."""
    df = orders.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce"
    )
    df = df.dropna(
        subset=[
            "customer_id",
            "order_purchase_timestamp",
        ]
    )
    reference_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = (
        df.groupby("customer_id")
        .agg(
            Recency=(
                "order_purchase_timestamp",
                lambda x: (reference_date - x.max()).days,
            ),
            Frequency=("order_id", "nunique"),
        )
        .reset_index()
    )
    if "payment_value" in df.columns:
        monetary = (
            df.groupby("customer_id")["payment_value"]
            .sum()
            .reset_index(name="Monetary")
        )
        rfm = rfm.merge(monetary, on="customer_id", how="left")
    else:
        rfm["Monetary"] = 0.0
    rfm["R_Score"] = pd.qcut(
        rfm["Recency"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1],
    ).astype(int)
    rfm["F_Score"] = pd.qcut(
        rfm["Frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)
    rfm["M_Score"] = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)
    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(str)
        + rfm["F_Score"].astype(str)
        + rfm["M_Score"].astype(str)
    )
    def segment(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 4 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2:
            return "New Customers"
        elif r <= 2 and f >= 4:
            return "At Risk High Value"
        elif r <= 2 and f >= 2:
            return "At Risk"
        elif r <= 2:
            return "Lost Customers"
        else:
            return "Potential Loyalists"
    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm
