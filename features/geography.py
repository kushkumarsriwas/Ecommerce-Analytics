import pandas as pd
BRAZIL_STATE_COORDINATES = {
    "AC": (-8.77, -70.55), "AL": (-9.71, -35.73),
    "AP": (1.41, -51.77), "AM": (-3.47, -65.10),
    "BA": (-12.96, -38.51), "CE": (-5.20, -39.53),
    "DF": (-15.83, -47.86), "ES": (-19.19, -40.34),
    "GO": (-15.98, -49.86), "MA": (-5.42, -45.44),
    "MT": (-12.64, -55.42), "MS": (-20.51, -54.54),
    "MG": (-18.10, -44.38), "PA": (-3.79, -52.48),
    "PB": (-7.28, -36.72), "PR": (-24.89, -51.55),
    "PE": (-8.38, -37.86), "PI": (-7.72, -42.72),
    "RJ": (-22.25, -42.66), "RN": (-5.81, -36.59),
    "RS": (-30.17, -53.50), "RO": (-10.83, -63.34),
    "RR": (1.99, -61.33), "SC": (-27.45, -50.95),
    "SP": (-22.19, -48.79), "SE": (-10.57, -37.45),
    "TO": (-9.46, -48.26),
}
def prepare_state_map(customers, orders=None):
    """Prepare state-level data with coordinates for interactive maps."""
    df = customers.copy()
    if "customer_state" not in df.columns:
        raise ValueError(
            "Customers dataframe must contain customer_state."
        )
    state_data = (
        df.groupby("customer_state")
        .agg(
            customers=("customer_id", "nunique")
        )
        .reset_index()
    )
    if orders is not None:
        order_df = orders.copy()
        if "customer_id" in order_df.columns and "payment_value" in order_df.columns:
            revenue = (
                order_df.groupby("customer_id")["payment_value"]
                .sum()
                .reset_index(name="revenue")
            )
            state_revenue = (
                df[["customer_id", "customer_state"]]
                .drop_duplicates("customer_id")
                .merge(revenue, on="customer_id", how="left")
                .groupby("customer_state")["revenue"]
                .sum()
                .reset_index()
            )
            state_data = state_data.merge(
                state_revenue,
                on="customer_state",
                how="left",
            )
    state_data["revenue"] = state_data.get(
        "revenue",
        pd.Series(0, index=state_data.index),
    ).fillna(0)
    state_data["latitude"] = state_data["customer_state"].map(
        lambda x: BRAZIL_STATE_COORDINATES.get(str(x).upper(), (None, None))[0]
    )
    state_data["longitude"] = state_data["customer_state"].map(
        lambda x: BRAZIL_STATE_COORDINATES.get(str(x).upper(), (None, None))[1]
    )
    return state_data.dropna(
        subset=["latitude", "longitude"]
    )
