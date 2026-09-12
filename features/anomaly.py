import pandas as pd
from sklearn.ensemble import IsolationForest
def detect_revenue_anomalies(orders, contamination=0.05):
    """Detect unusual daily revenue patterns."""
    df = orders.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce",
    )
    if "payment_value" not in df.columns:
        raise ValueError(
            "Orders dataframe must contain payment_value."
        )
    daily = (
        df.dropna(
            subset=[
                "order_purchase_timestamp",
                "payment_value",
            ]
        )
        .assign(
            date=lambda x: x["order_purchase_timestamp"].dt.date
        )
        .groupby("date", as_index=False)
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique"),
        )
    )
    if len(daily) < 10:
        raise ValueError(
            "At least 10 days of data are required."
        )
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
    )
    daily["anomaly"] = model.fit_predict(
        daily[["revenue", "orders"]]
    )
    daily["anomaly_label"] = daily["anomaly"].map(
        {
            1: "Normal",
            -1: "Anomaly",
        }
    )
    return daily.sort_values("date")
