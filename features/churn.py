import pandas as pd
import numpy as np
def calculate_churn_risk(rfm):
    """Score customers by inactivity and purchasing behavior."""
    df = rfm.copy()
    if "Recency" not in df.columns:
        raise ValueError("RFM dataframe must contain Recency.")
    if "Frequency" not in df.columns:
        raise ValueError("RFM dataframe must contain Frequency.")
    if "Monetary" not in df.columns:
        raise ValueError("RFM dataframe must contain Monetary.")
    recency_score = np.clip(
        df["Recency"] / max(df["Recency"].quantile(0.95), 1),
        0,
        1,
    )
    frequency_score = 1 - np.clip(
        df["Frequency"]
        / max(df["Frequency"].quantile(0.95), 1),
        0,
        1,
    )
    monetary_score = 1 - np.clip(
        df["Monetary"]
        / max(df["Monetary"].quantile(0.95), 1),
        0,
        1,
    )
    df["Churn_Risk_Score"] = (
        0.50 * recency_score
        + 0.30 * frequency_score
        + 0.20 * monetary_score
    ) * 100
    df["Risk_Level"] = pd.cut(
        df["Churn_Risk_Score"],
        bins=[-1, 30, 60, 100],
        labels=[
            "Low Risk",
            "Medium Risk",
            "High Risk",
        ],
    )
    return df.sort_values(
        "Churn_Risk_Score",
        ascending=False,
    )
