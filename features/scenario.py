import pandas as pd
import numpy as np
def run_revenue_scenario(
    orders,
    revenue_change=0.0,
    order_change=0.0,
    aov_change=0.0,
):
    """Simulate revenue under configurable business assumptions."""
    df = orders.copy()
    if "payment_value" not in df.columns:
        raise ValueError(
            "Orders dataframe must contain payment_value."
        )
    baseline_revenue = df["payment_value"].sum()
    baseline_orders = df["order_id"].nunique()
    baseline_aov = (
        baseline_revenue / baseline_orders
        if baseline_orders > 0
        else 0
    )
    projected_orders = (
        baseline_orders * (1 + order_change)
    )
    projected_aov = (
        baseline_aov * (1 + aov_change)
    )
    projected_revenue = (
        baseline_revenue * (1 + revenue_change)
    )
    projected_revenue_from_orders_aov = (
        projected_orders * projected_aov
    )
    return pd.DataFrame(
        {
            "Metric": [
                "Orders",
                "Average Order Value",
                "Revenue",
            ],
            "Baseline": [
                baseline_orders,
                baseline_aov,
                baseline_revenue,
            ],
            "Projected": [
                projected_orders,
                projected_aov,
                projected_revenue_from_orders_aov,
            ],
        }
    )
