import pandas as pd
def calculate_product_pareto(items, products=None):
    """Calculate product/category revenue contribution and cumulative share."""
    df = items.copy()
    if "price" not in df.columns:
        raise ValueError("Items dataframe must contain price.")
    if "product_id" in df.columns:
        result = (
            df.groupby("product_id")
            .agg(
                revenue=("price", "sum"),
                units_sold=("product_id", "size"),
            )
            .reset_index()
            .sort_values("revenue", ascending=False)
        )
    else:
        raise ValueError("Items dataframe must contain product_id.")
    total_revenue = result["revenue"].sum()
    if total_revenue > 0:
        result["revenue_share"] = (
            result["revenue"] / total_revenue * 100
        )
        result["cumulative_revenue_share"] = (
            result["revenue_share"].cumsum()
        )
    else:
        result["revenue_share"] = 0
        result["cumulative_revenue_share"] = 0
    result["pareto_group"] = result[
        "cumulative_revenue_share"
    ].apply(
        lambda x: "Top 80% Revenue"
        if x <= 80
        else "Remaining 20%"
    )
    if products is not None and "product_id" in products.columns:
        product_cols = [
            c for c in [
                "product_id",
                "product_category_name",
            ]
            if c in products.columns
        ]
        if product_cols:
            result = result.merge(
                products[product_cols].drop_duplicates("product_id"),
                on="product_id",
                how="left",
            )
    return result
