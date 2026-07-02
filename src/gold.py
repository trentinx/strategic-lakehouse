"""Couche Gold : agrégation des KPI métier via DuckDB."""

from pathlib import Path

import duckdb

SILVER_DIR = Path(__file__).resolve().parent.parent / "data" / "silver"
GOLD_DIR = Path(__file__).resolve().parent.parent / "data" / "gold"


def build_kpis() -> None:
    """Construit les tables Gold à partir des données Silver avec DuckDB."""
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()

    sales = str(SILVER_DIR / "sales.parquet")
    customers = str(SILVER_DIR / "customers.parquet")
    products = str(SILVER_DIR / "products.parquet")

    # KPI 1 : Chiffre d'affaires par pays
    con.execute(f"""
        COPY (
            SELECT c.country,
                   COUNT(DISTINCT s.order_number) AS nb_orders,
                   SUM(s.sales) AS total_revenue,
                   ROUND(AVG(s.sales), 2) AS avg_order_value
            FROM '{sales}' s
            JOIN '{customers}' c ON s.customer_key = c.customer_key
            GROUP BY c.country
            ORDER BY total_revenue DESC
        ) TO '{GOLD_DIR}/kpi_revenue_by_country.parquet' (FORMAT PARQUET)
    """)
    print("[GOLD] kpi_revenue_by_country.parquet")

    # KPI 2 : Ventes par catégorie produit
    con.execute(f"""
        COPY (
            SELECT p.category,
                   p.sub_category,
                   SUM(s.quantity) AS total_quantity,
                   SUM(s.sales) AS total_revenue
            FROM '{sales}' s
            JOIN '{products}' p ON s.product_key = p.product_key
            GROUP BY p.category, p.sub_category
            ORDER BY total_revenue DESC
        ) TO '{GOLD_DIR}/kpi_sales_by_category.parquet' (FORMAT PARQUET)
    """)
    print("[GOLD] kpi_sales_by_category.parquet")

    # KPI 3 : Tendance mensuelle du CA
    con.execute(f"""
        COPY (
            SELECT DATE_TRUNC('month', s.order_date) AS month,
                   COUNT(DISTINCT s.order_number) AS nb_orders,
                   SUM(s.sales) AS total_revenue
            FROM '{sales}' s
            GROUP BY month
            ORDER BY month
        ) TO '{GOLD_DIR}/kpi_monthly_trend.parquet' (FORMAT PARQUET)
    """)
    print("[GOLD] kpi_monthly_trend.parquet")

    # KPI 4 : Résumé global
    result = con.execute(f"""
        SELECT COUNT(DISTINCT s.order_number) AS total_orders,
               COUNT(DISTINCT s.customer_key) AS total_customers,
               SUM(s.sales) AS total_revenue,
               ROUND(AVG(s.sales), 2) AS avg_order_value
        FROM '{sales}' s
    """).fetchdf()
    result.to_parquet(GOLD_DIR / "kpi_summary.parquet", index=False)
    print("[GOLD] kpi_summary.parquet")

    con.close()


if __name__ == "__main__":
    build_kpis()
