"""API FastAPI exposant les KPI Gold du Lakehouse."""

from pathlib import Path

import duckdb
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

GOLD_DIR = Path(__file__).resolve().parent.parent / "data" / "gold"
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="GlobalTrade Lakehouse API", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def _read_parquet(filename: str) -> list[dict]:
    path = GOLD_DIR / filename
    con = duckdb.connect()
    df = con.execute(f"SELECT * FROM '{path}'").fetchdf()
    con.close()
    # Convert timestamps to strings for JSON serialization
    for col in df.select_dtypes(include=["datetime64", "datetimetz"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d")
    return df.to_dict(orient="records")


@app.get("/")
def index():
    """Sert l'interface web."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/kpi/summary")
def kpi_summary():
    """KPI global : total commandes, clients, CA, panier moyen."""
    return _read_parquet("kpi_summary.parquet")


@app.get("/api/kpi/revenue-by-country")
def kpi_revenue_by_country():
    """CA ventilé par pays."""
    return _read_parquet("kpi_revenue_by_country.parquet")


@app.get("/api/kpi/sales-by-category")
def kpi_sales_by_category():
    """Ventes par catégorie de produit."""
    return _read_parquet("kpi_sales_by_category.parquet")


@app.get("/api/kpi/monthly-trend")
def kpi_monthly_trend():
    """Tendance mensuelle du chiffre d'affaires."""
    return _read_parquet("kpi_monthly_trend.parquet")
