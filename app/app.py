import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ---------------- CONFIG ----------------

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "cleaned"

st.set_page_config(
    page_title="E-Commerce Business Intelligence",
    page_icon="🛒",
    layout="wide"
)


# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():

    # Orders
    orders = pd.read_csv(
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

    # Order Items
    items = pd.read_csv(
        DATA / "olist_order_items_dataset.csv",
        usecols=[
            "order_id",
            "product_id",
            "price"
        ]
    )

    # Customers
    customers = pd.read_csv(
        DATA / "olist_customers_dataset.csv",
        usecols=[
            "customer_id",
            "customer_unique_id",
            "customer_state"
        ]
    )

    # Products
    products = pd.read_csv(
        DATA / "olist_products_dataset.csv",
        usecols=[
            "product_id",
            "product_category_name"
        ]
    )

    # Payments
    payments = pd.read_csv(
        DATA / "olist_order_payments_dataset.csv",
        usecols=[
            "order_id",
            "payment_type",
            "payment_value"
        ]
    )

    # Reviews
    reviews = pd.read_csv(
        DATA / "olist_order_reviews_dataset.csv",
        usecols=[
            "order_id",
            "review_score"
        ]
    )

    # Sellers
    sellers = pd.read_csv(
        DATA / "olist_sellers_dataset.csv"
    )

    # Category Translation
    translation = pd.read_csv(
        DATA / "product_category_name_translation.csv"
    )

    # Translate product categories
    products = products.merge(
        translation,
        on="product_category_name",
        how="left"
    )

    products["category"] = products[
        "product_category_name_english"
    ].fillna(
        products["product_category_name"]
    ).fillna("Unknown")

    # Create sales dataframe
    sales = (
        orders
        .merge(
            customers,
            on="customer_id",
            how="left"
        )
        .merge(
            items,
            on="order_id",
            how="inner"
        )
        .merge(
            products[["product_id", "category"]],
            on="product_id",
            how="left"
        )
    )

    return (
        orders,
        items,
        customers,
        products,
        payments,
        reviews,
        sellers,
        sales
    )


orders, items, customers, products, payments, reviews, sellers, sales = load_data()


# ---------------- SIDEBAR ----------------

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
        "Payments & Reviews"
    ]
)


# ---------------- EXECUTIVE DASHBOARD ----------------

if page == "Executive Dashboard":

    st.title("E-Commerce Business Intelligence")

    st.caption(
        "Brazilian E-Commerce Analytics | Olist Public Dataset"
    )

    total_orders = orders["order_id"].nunique()

    total_customers = sales["customer_unique_id"].nunique()

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

    monthly = (
        sales.assign(
            month=sales[
                "order_purchase_timestamp"
            ].dt.to_period("M").astype(str)
        )
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

    repeat = (
        orders
        .merge(
            customers,
            on="customer_id"
        )
        .groupby(
            "customer_unique_id"
        )["order_id"]
        .nunique()
    )

    repeat_rate = (
        repeat.gt(1).mean() * 100
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


# ---------------- SALES ANALYTICS ----------------

elif page == "Sales Analytics":

    st.title("Sales Analytics")

    monthly = (
        sales.assign(
            month=sales[
                "order_purchase_timestamp"
            ].dt.to_period("M").astype(str)
        )
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

    category = (
        sales
        .groupby("category")
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


# ---------------- CUSTOMER ANALYTICS ----------------

elif page == "Customer Analytics":

    st.title("Customer Analytics")

    customer_orders = (
        orders
        .merge(
            customers,
            on="customer_id"
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

    one_time_count = (
        customer_orders["customer_type"]
        == "One-time"
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


# ---------------- PRODUCT ANALYTICS ----------------

elif page == "Product Analytics":

    st.title("Product Analytics")

    category = (
        sales
        .groupby("category")
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
        sales
        .groupby(
            ["product_id", "category"]
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


# ---------------- GEOGRAPHIC ANALYTICS ----------------

elif page == "Geographic Analytics":

    st.title("Geographic Analytics")

    state = (
        sales
        .groupby("customer_state")
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


# ---------------- OPERATIONS ANALYTICS ----------------

elif page == "Operations Analytics":

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
        delivered
        .merge(
            customers,
            on="customer_id"
        )
        .groupby(
            "customer_state"
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


# ---------------- PAYMENTS & REVIEWS ----------------

elif page == "Payments & Reviews":

    st.title("Payments & Customer Reviews")

    payment = (
        payments
        .groupby("payment_type")
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


# ---------------- FOOTER ----------------

st.sidebar.divider()

st.sidebar.caption(
    "Built with Python  |  Pandas  |  Plotly  |  Streamlit"
)