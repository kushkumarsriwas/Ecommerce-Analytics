import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from features import (
    calculate_rfm,
    build_cohort_analysis,
    calculate_clv,
    calculate_churn_risk,
    calculate_product_pareto,
    calculate_market_basket,
    forecast_revenue,
    detect_revenue_anomalies,
    prepare_state_map,
    run_revenue_scenario,
    profile_dataframe,
    dataset_summary,
    generate_kpi_summary,
)


# =========================================================
# CONFIG
# =========================================================

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "cleaned"

st.set_page_config(
    page_title="E-Commerce Business Intelligence",
    page_icon="??",
    layout="wide"
)


# =========================================================
# DATA LOADERS
# =========================================================

@st.cache_data
def load_orders():

    return pd.read_csv(
        DATA / "olist_orders_dataset.csv",
        usecols=[
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ],
        parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    )


@st.cache_data
def load_items():

    return pd.read_csv(
        DATA / "olist_order_items_dataset.csv",
        usecols=[
            "order_id",
            "product_id",
            "price"
        ]
    )


@st.cache_data
def load_customers():

    customers = pd.read_csv(
        DATA / "olist_customers_dataset.csv",
        usecols=[
            "customer_id",
            "customer_unique_id",
            "customer_state"
        ]
    )

    customers["customer_state"] = (
        customers["customer_state"].astype("category")
    )

    return customers


@st.cache_data
def load_products():

    products = pd.read_csv(
        DATA / "olist_products_dataset.csv",
        usecols=[
            "product_id",
            "product_category_name"
        ]
    )

    translation = pd.read_csv(
        DATA / "product_category_name_translation.csv",
        usecols=[
            "product_category_name",
            "product_category_name_english"
        ]
    )

    products = products.merge(
        translation,
        on="product_category_name",
        how="left"
    )

    products["category"] = (
        products["product_category_name_english"]
        .fillna(products["product_category_name"])
        .fillna("Unknown")
    )

    products["category"] = (
        products["category"].astype("category")
    )

    return products[
        ["product_id", "category"]
    ]


@st.cache_data
def load_payments():

    return pd.read_csv(
        DATA / "olist_order_payments_dataset.csv",
        usecols=[
            "order_id",
            "payment_type",
            "payment_value"
        ]
    )


@st.cache_data
def load_reviews():

    return pd.read_csv(
        DATA / "olist_order_reviews_dataset.csv",
        usecols=[
            "order_id",
            "review_score"
        ]
    )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Dashboard Navigation")

page = st.sidebar.radio(
    "Select Analysis",
    [
        "Executive Dashboard",
        "Sales Analytics",
        "Customer Analytics",
        "Product Analytics",
        "Geographic Analytics",
        "Operations Analytics",
        "Payments & Reviews", "Advanced Analytics"
    ]
)


# =========================================================
# EXECUTIVE DASHBOARD
# =========================================================

if page == "Executive Dashboard":

    orders = load_orders()
    items = load_items()
    customers = load_customers()

    st.title("E-Commerce Business Intelligence")

    st.caption(
        "Brazilian E-Commerce Analytics | Olist Public Dataset"
    )

    total_orders = orders["order_id"].nunique()

    total_customers = customers["customer_unique_id"].nunique()

    revenue = items["price"].sum()

    aov = revenue / total_orders

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Orders",
        f"{total_orders:,}"
    )

    c2.metric(
        "Unique Customers",
        f"{total_customers:,}"
    )

    c3.metric(
        "Revenue",
        f"R$ {revenue:,.2f}"
    )

    c4.metric(
        "Average Order Value",
        f"R$ {aov:,.2f}"
    )

    st.divider()

    # Monthly revenue
    monthly = (
        orders[
            [
                "order_id",
                "order_purchase_timestamp"
            ]
        ]
        .merge(
            items[
                [
                    "order_id",
                    "price"
                ]
            ],
            on="order_id",
            how="inner"
        )
    )

    monthly["month"] = (
        monthly[
            "order_purchase_timestamp"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        monthly
        .groupby("month")
        .agg(
            Revenue=("price", "sum"),
            Orders=("order_id", "nunique")
        )
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.line(
            monthly,
            x="month",
            y="Revenue",
            markers=True,
            title="Monthly Revenue"
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Revenue"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.bar(
            monthly,
            x="month",
            y="Orders",
            title="Monthly Orders"
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Orders"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    del monthly

    # Delivery
    delivered = orders.dropna(
        subset=[
            "order_delivered_customer_date"
        ]
    ).copy()

    late_rate = (
        (
            delivered[
                "order_delivered_customer_date"
            ]
            >
            delivered[
                "order_estimated_delivery_date"
            ]
        ).mean()
        * 100
    )

    # Repeat customers
    customer_order_count = (
        orders[
            [
                "customer_id",
                "order_id"
            ]
        ]
        .merge(
            customers[
                [
                    "customer_id",
                    "customer_unique_id"
                ]
            ],
            on="customer_id",
            how="left"
        )
        .groupby(
            "customer_unique_id"
        )["order_id"]
        .nunique()
    )

    repeat_rate = (
        customer_order_count.gt(1).mean()
        * 100
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Delivered Orders",
        f"{len(delivered):,}"
    )

    c2.metric(
        "Late Delivery Rate",
        f"{late_rate:.2f}%"
    )

    c3.metric(
        "Repeat Customer Rate",
        f"{repeat_rate:.2f}%"
    )


# =========================================================
# SALES ANALYTICS
# =========================================================

elif page == "Sales Analytics":

    orders = load_orders()
    items = load_items()
    products = load_products()

    st.title("Sales Analytics")

    # Create only the required sales dataframe
    sales = (
        orders[
            [
                "order_id",
                "order_purchase_timestamp"
            ]
        ]
        .merge(
            items,
            on="order_id",
            how="inner"
        )
    )

    sales["month"] = (
        sales[
            "order_purchase_timestamp"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        sales
        .groupby("month")
        .agg(
            Revenue=("price", "sum"),
            Orders=("order_id", "nunique")
        )
        .reset_index()
    )

    fig = px.line(
        monthly,
        x="month",
        y="Revenue",
        markers=True,
        title="Revenue Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            monthly,
            x="month",
            y="Orders",
            title="Orders Over Time"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        monthly["AOV"] = (
            monthly["Revenue"]
            /
            monthly["Orders"]
        )

        fig = px.line(
            monthly,
            x="month",
            y="AOV",
            markers=True,
            title="Monthly Average Order Value"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("Top Product Categories")

    category_sales = (
        items[
            [
                "order_id",
                "product_id",
                "price"
            ]
        ]
        .merge(
            products,
            on="product_id",
            how="left"
        )
    )

    category = (
        category_sales
        .groupby("category", observed=True)
        .agg(
            Revenue=("price", "sum"),
            Orders=("order_id", "nunique"),
            Units=("product_id", "count")
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    fig = px.bar(
        category.head(15),
        x="Revenue",
        y="category",
        orientation="h",
        title="Top 15 Categories by Revenue"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# CUSTOMER ANALYTICS
# =========================================================

elif page == "Customer Analytics":

    orders = load_orders()
    customers = load_customers()

    st.title("Customer Analytics")

    customer_orders = (
        orders[
            [
                "order_id",
                "customer_id"
            ]
        ]
        .merge(
            customers[
                [
                    "customer_id",
                    "customer_unique_id"
                ]
            ],
            on="customer_id",
            how="inner"
        )
        .groupby(
            "customer_unique_id"
        )
        .agg(
            orders=("order_id", "nunique")
        )
        .reset_index()
    )

    customer_orders["customer_type"] = (
        customer_orders["orders"]
        .apply(
            lambda x:
            "Repeat" if x > 1
            else "One-time"
        )
    )

    repeat_count = (
        customer_orders["customer_type"]
        == "Repeat"
    ).sum()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Customers",
        f"{len(customer_orders):,}"
    )

    c2.metric(
        "Repeat Customers",
        f"{repeat_count:,}"
    )

    c3.metric(
        "Repeat Rate",
        f"{repeat_count / len(customer_orders) * 100:.2f}%"
    )

    distribution = (
        customer_orders[
            "customer_type"
        ]
        .value_counts()
        .reset_index()
    )

    distribution.columns = [
        "Customer Type",
        "Customers"
    ]

    fig = px.pie(
        distribution,
        names="Customer Type",
        values="Customers",
        title="One-time vs Repeat Customers"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Customer Order Frequency")

    frequency = (
        customer_orders["orders"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    frequency.columns = [
        "Orders",
        "Customers"
    ]

    fig = px.bar(
        frequency,
        x="Orders",
        y="Customers",
        title="Orders per Customer"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# PRODUCT ANALYTICS
# =========================================================

elif page == "Product Analytics":

    items = load_items()
    products = load_products()

    st.title("Product Analytics")

    category_data = (
        items
        .merge(
            products,
            on="product_id",
            how="left"
        )
    )

    category = (
        category_data
        .groupby("category", observed=True)
        .agg(
            Revenue=("price", "sum"),
            Units=("product_id", "count"),
            Orders=("order_id", "nunique")
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    st.subheader("Category Performance")

    st.dataframe(
        category.style.format(
            {
                "Revenue": "R$ {:,.2f}",
                "Units": "{:,.0f}",
                "Orders": "{:,.0f}"
            }
        ),
        use_container_width=True
    )

    fig = px.bar(
        category.head(15),
        x="Revenue",
        y="category",
        orientation="h",
        title="Top 15 Categories"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Top Products by Revenue")

    top_products = (
        category_data
        .groupby(
            [
                "product_id",
                "category"
            ],
            observed=True
        )
        .agg(
            Revenue=("price", "sum"),
            Units=("product_id", "count")
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        top_products.style.format(
            {
                "Revenue": "R$ {:,.2f}",
                "Units": "{:,.0f}"
            }
        ),
        use_container_width=True
    )


# =========================================================
# GEOGRAPHIC ANALYTICS
# =========================================================

elif page == "Geographic Analytics":

    orders = load_orders()
    items = load_items()
    customers = load_customers()

    st.title("Geographic Analytics")

    sales = (
        orders[
            [
                "order_id",
                "customer_id"
            ]
        ]
        .merge(
            customers[
                [
                    "customer_id",
                    "customer_unique_id",
                    "customer_state"
                ]
            ],
            on="customer_id",
            how="left"
        )
        .merge(
            items[
                [
                    "order_id",
                    "price"
                ]
            ],
            on="order_id",
            how="inner"
        )
    )

    state = (
        sales
        .groupby("customer_state", observed=True)
        .agg(
            Revenue=("price", "sum"),
            Orders=("order_id", "nunique"),
            Customers=(
                "customer_unique_id",
                "nunique"
            )
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    fig = px.bar(
        state.head(15),
        x="customer_state",
        y="Revenue",
        title="Revenue by Customer State"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("State Performance")

    st.dataframe(
        state.style.format(
            {
                "Revenue": "R$ {:,.2f}",
                "Orders": "{:,.0f}",
                "Customers": "{:,.0f}"
            }
        ),
        use_container_width=True
    )


# =========================================================
# OPERATIONS ANALYTICS
# =========================================================

elif page == "Operations Analytics":

    orders = load_orders()
    customers = load_customers()

    st.title("Operations & Delivery Analytics")

    delivered = orders.dropna(
        subset=[
            "order_delivered_customer_date"
        ]
    ).copy()

    delivered["delivery_days"] = (
        delivered[
            "order_delivered_customer_date"
        ]
        -
        delivered[
            "order_purchase_timestamp"
        ]
    ).dt.total_seconds() / 86400

    delivered["late"] = (
        delivered[
            "order_delivered_customer_date"
        ]
        >
        delivered[
            "order_estimated_delivery_date"
        ]
    )

    avg_delivery = (
        delivered["delivery_days"].mean()
    )

    late_rate = (
        delivered["late"].mean() * 100
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Delivered Orders",
        f"{len(delivered):,}"
    )

    c2.metric(
        "Average Delivery",
        f"{avg_delivery:.2f} days"
    )

    c3.metric(
        "Late Delivery Rate",
        f"{late_rate:.2f}%"
    )

    delivery_state = (
        delivered[
            [
                "customer_id",
                "delivery_days"
            ]
        ]
        .merge(
            customers[
                [
                    "customer_id",
                    "customer_state"
                ]
            ],
            on="customer_id",
            how="left"
        )
        .groupby(
            "customer_state",
            observed=True
        )["delivery_days"]
        .mean()
        .reset_index()
        .sort_values(
            "delivery_days"
        )
    )

    fig = px.bar(
        delivery_state,
        x="customer_state",
        y="delivery_days",
        title="Average Delivery Time by State"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    status = (
        orders["order_status"]
        .value_counts()
        .reset_index()
    )

    status.columns = [
        "Order Status",
        "Orders"
    ]

    fig = px.pie(
        status,
        names="Order Status",
        values="Orders",
        title="Order Status Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# PAYMENTS & REVIEWS
# =========================================================

elif page == "Advanced Analytics":
    payments = load_payments()
    orders = load_orders()
    items = load_items()
    products = load_products()
    orders = orders.merge(payments.groupby("order_id", as_index=False)["payment_value"].sum(), on="order_id", how="left")
    orders = load_orders()
    items = load_items()
    products = load_products()
    st.title("?? Advanced Analytics")
    st.subheader("Customer Intelligence")
    orders = orders.merge(payments.groupby("order_id", as_index=False)["payment_value"].sum(), on="order_id", how="left")

    @st.cache_data
    def cached_rfm(df):
        return calculate_rfm(df)

    rfm = cached_rfm(orders)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Customers", f"{len(rfm):,}")
    c2.metric("Champions", f"{(rfm["Segment"] == "Champions").sum():,}")
    c3.metric("At Risk", f"{rfm["Segment"].isin(["At Risk", "At Risk High Value"]).sum():,}")
    c4.metric("Lost Customers", f"{(rfm["Segment"] == "Lost Customers").sum():,}")
    st.plotly_chart(
        px.bar(
            rfm["Segment"].value_counts().reset_index(),
            x="Segment",
            y="count",
            title="Customer Segments",
        ),
        use_container_width=True,
    )
    st.subheader("Customer RFM Analysis")
    st.dataframe(
        rfm.sort_values("Monetary", ascending=False),
        use_container_width=True,
    )
    st.subheader("Revenue Forecast")
    periods = st.slider(
        "Forecast months",
        min_value=3,
        max_value=12,
        value=6,
    )
    if st.button("Generate Revenue Forecast"):
        with st.spinner("Building forecast..."):
            monthly, forecast = forecast_revenue(
                orders,
                periods=periods,
            )
        fig = px.line(
            forecast,
            x="ds",
            y="yhat",
            title="Revenue Forecast",
        )
        fig.add_scatter(
            x=forecast["ds"],
            y=forecast["yhat_upper"],
            mode="lines",
            name="Upper Bound",
        )
        fig.add_scatter(
            x=forecast["ds"],
            y=forecast["yhat_lower"],
            mode="lines",
            name="Lower Bound",
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
        )
        st.download_button(
            "Download Forecast CSV",
            forecast.to_csv(index=False),
            "revenue_forecast.csv",
            "text/csv",
        )
    st.subheader("Revenue Anomaly Detection")
    if st.button("Detect Revenue Anomalies"):
        anomalies = detect_revenue_anomalies(orders)
        st.metric(
            "Anomalous Days",
            f"{(anomalies["anomaly_label"] == "Anomaly").sum():,}",
        )
        st.plotly_chart(
            px.scatter(
                anomalies,
                x="date",
                y="revenue",
                color="anomaly_label",
                size="orders",
                title="Daily Revenue Anomalies",
            ),
            use_container_width=True,
        )
        st.dataframe(
            anomalies[
                anomalies["anomaly_label"] == "Anomaly"
            ],
            use_container_width=True,
        )
    st.subheader("Product Pareto Analysis")
    @st.cache_data
    def cached_pareto(items_df, products_df):
        return calculate_product_pareto(items_df, products_df)

    pareto = cached_pareto(
        items,
        products,
    )
    st.plotly_chart(
        px.line(
            pareto.head(100),
            x=pareto.head(100).index,
            y="cumulative_revenue_share",
            title="Cumulative Revenue Contribution",
        ),
        use_container_width=True,
    )
    st.dataframe(
        pareto.head(100),
        use_container_width=True,
    )
    st.subheader("Customer Cohort Retention")
    @st.cache_data
    def cached_cohort(df):
        return build_cohort_analysis(df)

    retention, retention_rate = cached_cohort(orders)
    st.dataframe(
        retention_rate.round(1),
        use_container_width=True,
    )
    st.subheader("What-If Revenue Scenario")
    revenue_change = st.slider(
        "Revenue adjustment",
        -50,
        100,
        0,
        format="%d%%",
    ) / 100
    order_change = st.slider(
        "Order volume adjustment",
        -50,
        100,
        0,
        format="%d%%",
    ) / 100
    aov_change = st.slider(
        "AOV adjustment",
        -50,
        100,
        0,
        format="%d%%",
    ) / 100
    scenario = run_revenue_scenario(
        orders,
        revenue_change=revenue_change,
        order_change=order_change,
        aov_change=aov_change,
    )
    st.dataframe(
        scenario,
        use_container_width=True,
    )
    st.subheader("Data Quality")
    quality = dataset_summary(orders)
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows", f'{quality["rows"]:,}')
    q2.metric("Columns", f'{quality["columns"]:,}')
    q3.metric("Duplicate Rows", f'{quality["duplicate_rows"]:,}')
    q4.metric("Missing %", f'{quality["missing_percentage"]:.2f}%')
    st.dataframe(
        profile_dataframe(orders),
        use_container_width=True,
    )
elif page == "Payments & Reviews":

    payments = load_payments()
    reviews = load_reviews()

    st.title("Payments & Customer Reviews")

    payment = (
        payments
        .groupby("payment_type", observed=True)
        .agg(
            Orders=("order_id", "nunique"),
            Payment_Value=(
                "payment_value",
                "sum"
            ),
            Average_Payment=(
                "payment_value",
                "mean"
            )
        )
        .reset_index()
        .sort_values(
            "Payment_Value",
            ascending=False
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            payment,
            x="payment_type",
            y="Payment_Value",
            title="Payment Value by Method"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.pie(
            payment,
            names="payment_type",
            values="Orders",
            title="Orders by Payment Method"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("Payment Details")

    st.dataframe(
        payment.style.format(
            {
                "Payment_Value": "R$ {:,.2f}",
                "Average_Payment": "R$ {:,.2f}",
                "Orders": "{:,.0f}"
            }
        ),
        use_container_width=True
    )

    st.subheader("Review Scores")

    review_counts = (
        reviews["review_score"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    review_counts.columns = [
        "Review Score",
        "Reviews"
    ]

    fig = px.bar(
        review_counts,
        x="Review Score",
        y="Reviews",
        title="Customer Review Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# FOOTER
# =========================================================

st.sidebar.divider()

st.sidebar.caption(
    "Built with Python  |  Pandas  |  Plotly  |  Streamlit"
)










