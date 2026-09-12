import pandas as pd
from prophet import Prophet
def forecast_revenue(orders, periods=6):
    """Forecast monthly revenue using Prophet."""
    df = orders.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce",
    )
    if "payment_value" not in df.columns:
        raise ValueError(
            "Orders dataframe must contain payment_value."
        )
    monthly = (
        df.dropna(
            subset=[
                "order_purchase_timestamp",
                "payment_value",
            ]
        )
        .assign(
            ds=lambda x: x["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
        )
        .groupby("ds", as_index=False)["payment_value"]
        .sum()
        .rename(columns={"payment_value": "y"})
    )
    if len(monthly) < 3:
        raise ValueError(
            "At least 3 months of historical data are required."
        )
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
    )
    model.fit(monthly)
    future = model.make_future_dataframe(
        periods=periods,
        freq="MS",
    )
    forecast = model.predict(future)
    return monthly, forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper",
        ]
    ]
