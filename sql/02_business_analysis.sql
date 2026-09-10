-- ============================================================
-- E-COMMERCE BUSINESS ANALYSIS
-- ============================================================
-- 1. Total orders, customers and order value
SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS total_customers,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS average_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id;
-- 2. Monthly revenue trend
SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY 1
ORDER BY 1;
-- 3. Revenue by product category
SELECT
    COALESCE(ct.product_category_name_english,
             p.product_category_name,
             'Unknown') AS category,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(DISTINCT oi.order_id) AS orders
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
GROUP BY 1
ORDER BY revenue DESC;
-- 4. Top 10 products by revenue
SELECT
    oi.product_id,
    COALESCE(ct.product_category_name_english,
             p.product_category_name,
             'Unknown') AS category,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(*) AS units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
GROUP BY oi.product_id, category
ORDER BY revenue DESC
LIMIT 10;
-- 5. Revenue by customer state
SELECT
    c.customer_state,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY revenue DESC;
-- 6. Order status distribution
SELECT
    order_status,
    COUNT(*) AS orders,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM orders
GROUP BY order_status
ORDER BY orders DESC;
-- 7. Payment method analysis
SELECT
    payment_type,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(payment_value), 2) AS payment_value,
    ROUND(AVG(payment_value), 2) AS average_payment
FROM order_payments
GROUP BY payment_type
ORDER BY payment_value DESC;
-- 8. Review score analysis
SELECT
    review_score,
    COUNT(*) AS reviews,
    ROUND(AVG(review_score) OVER (), 2) AS overall_average_score
FROM order_reviews
GROUP BY review_score
ORDER BY review_score;
-- 9. Delivery performance
SELECT
    COUNT(*) FILTER (
        WHERE order_delivered_customer_date IS NOT NULL
    ) AS delivered_orders,
    COUNT(*) FILTER (
        WHERE order_delivered_customer_date >
              order_estimated_delivery_date
    ) AS late_orders,
    ROUND(
        COUNT(*) FILTER (
            WHERE order_delivered_customer_date >
                  order_estimated_delivery_date
        ) * 100.0 /
        NULLIF(
            COUNT(*) FILTER (
                WHERE order_delivered_customer_date IS NOT NULL
            ), 0
        ),
        2
    ) AS late_delivery_percentage
FROM orders;
-- 10. Customer repeat-purchase analysis
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
)
SELECT
    CASE
        WHEN order_count = 1 THEN 'One-time'
        ELSE 'Repeat'
    END AS customer_type,
    COUNT(*) AS customers
FROM customer_orders
GROUP BY 1
ORDER BY customers DESC;
-- 11. Top sellers by revenue
SELECT
    oi.seller_id,
    s.seller_state,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(DISTINCT oi.order_id) AS orders
FROM order_items oi
JOIN sellers s ON oi.seller_id = s.seller_id
GROUP BY oi.seller_id, s.seller_state
ORDER BY revenue DESC
LIMIT 10;
-- 12. Monthly revenue with previous month comparison
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
        SUM(oi.price) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        LAG(revenue) OVER (ORDER BY month),
        2
    ) AS previous_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month))
        * 100.0
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
        2
    ) AS month_over_month_growth
FROM monthly_revenue
ORDER BY month;
-- 13. Category revenue ranking
WITH category_revenue AS (
    SELECT
        COALESCE(ct.product_category_name_english,
                 p.product_category_name,
                 'Unknown') AS category,
        SUM(oi.price) AS revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN category_translation ct
        ON p.product_category_name = ct.product_category_name
    GROUP BY 1
)
SELECT
    category,
    ROUND(revenue, 2) AS revenue,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM category_revenue
ORDER BY revenue_rank;
-- 14. Average delivery time by customer state
SELECT
    c.customer_state,
    ROUND(
        AVG(
            EXTRACT(
                EPOCH FROM (
                    o.order_delivered_customer_date
                    - o.order_purchase_timestamp
                )
            ) / 86400
        ),
        2
    ) AS avg_delivery_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_days;
-- 15. Customers with highest lifetime revenue
SELECT
    c.customer_unique_id,
    ROUND(SUM(oi.price), 2) AS lifetime_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_unique_id
ORDER BY lifetime_revenue DESC
LIMIT 20;
