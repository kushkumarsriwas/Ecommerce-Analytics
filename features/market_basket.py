import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
def calculate_market_basket(items, min_support=0.01, min_confidence=0.2):
    """Find frequently purchased product combinations and association rules."""
    df = items.copy()
    required = {"order_id", "product_id"}
    if not required.issubset(df.columns):
        raise ValueError(
            "Items dataframe must contain order_id and product_id."
        )
    basket = (
        df.assign(value=1)
        .pivot_table(
            index="order_id",
            columns="product_id",
            values="value",
            aggfunc="max",
            fill_value=0,
        )
    )
    frequent_itemsets = apriori(
        basket.astype(bool),
        min_support=min_support,
        use_colnames=True,
    )
    if frequent_itemsets.empty:
        return frequent_itemsets, pd.DataFrame()
    rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=min_confidence,
    )
    return frequent_itemsets, rules.sort_values(
        ["lift", "confidence"],
        ascending=False,
    )
