"""Couche Bronze : ingestion brute des fichiers CSV dans le lakehouse."""

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
BRONZE_DIR = Path(__file__).resolve().parent.parent / "data" / "bronze"


def ingest_csv(filename: str) -> pd.DataFrame:
    """Charge un CSV brut et le stocke tel quel en Parquet (couche Bronze)."""
    source = RAW_DIR / filename
    try:
        df = pd.read_csv(source, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(source, encoding="latin-1")

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    parquet_name = Path(filename).stem + ".parquet"
    df.to_parquet(BRONZE_DIR / parquet_name, index=False)

    print(f"[BRONZE] {filename} -> {parquet_name}  ({len(df)} lignes)")
    return df


def ingest_all() -> dict[str, pd.DataFrame]:
    """Ingère les 3 fichiers principaux des silos GlobalTrade."""
    return {
        "sales": ingest_csv("g_fact_sales.csv"),
        "customers": ingest_csv("g_dim_customers.csv"),
        "products": ingest_csv("g_dim_products.csv"),
    }


if __name__ == "__main__":
    ingest_all()
