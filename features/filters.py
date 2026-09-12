import pandas as pd
import streamlit as st
def apply_global_filters(
    df,
    date_column=None,
    state_column=None,
    category_column=None,
    status_column=None,
    payment_column=None,
):
    """Apply reusable Streamlit sidebar filters to a dataframe."""
    filtered = df.copy()
    if date_column and date_column in filtered.columns:
        filtered[date_column] = pd.to_datetime(filtered[date_column], errors="coerce")
        min_date = filtered[date_column].min()
        max_date = filtered[date_column].max()
        if pd.notna(min_date) and pd.notna(max_date):
            date_range = st.sidebar.date_input(
                "Date Range",
                value=(min_date.date(), max_date.date()),
                min_value=min_date.date(),
                max_value=max_date.date(),
                key=f"filter_date_{date_column}",
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
                filtered = filtered[
                    (filtered[date_column].dt.date >= start_date)
                    & (filtered[date_column].dt.date <= end_date)
                ]
    filter_map = [
        (state_column, "State", "filter_state"),
        (category_column, "Category", "filter_category"),
        (status_column, "Order Status", "filter_status"),
        (payment_column, "Payment Type", "filter_payment"),
    ]
    for column, label, key in filter_map:
        if column and column in filtered.columns:
            values = sorted(filtered[column].dropna().astype(str).unique())
            selected = st.sidebar.multiselect(
                label,
                values,
                default=[],
                key=key,
            )
            if selected:
                filtered = filtered[
                    filtered[column].astype(str).isin(selected)
                ]
    return filtered
