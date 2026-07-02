"""Couche Silver : nettoyage, typage et dédoublonnage des données Bronze."""

from pathlib import Path

import pandas as pd

BRONZE_DIR = Path(__file__).resolve().parent.parent / "data" / "bronze"
SILVER_DIR = Path(__file__).resolve().parent.parent / "data" / "silver"


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie la table des ventes."""
    df = df.drop_duplicates(subset=["order_number", "product_key"])
    df = df.dropna(subset=["sales", "quantity", "price"])

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["shipping_date"] = pd.to_datetime(df["shipping_date"], errors="coerce")
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype("Int64")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    df = df.dropna(subset=["order_date"])
    return df


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie la table des clients."""
    df = df.drop_duplicates(subset=["customer_key"])
    df = df.dropna(subset=["first_name", "last_name", "country"])

    # Nettoyage des \r parasites sur toutes les colonnes texte
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.replace("\r", "", regex=False).str.strip()

    df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
    df["first_name"] = df["first_name"].str.title()
    df["last_name"] = df["last_name"].str.title()
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie la table des produits."""
    df = df.drop_duplicates(subset=["product_key"])
    df = df.dropna(subset=["product_name", "category"])

    # Nettoyage des \r parasites sur toutes les colonnes texte
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.replace("\r", "", regex=False).str.strip()

    df["cost"] = pd.to_numeric(df["cost"], errors="coerce").fillna(0)
    return df


def transform_all(bronze: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Applique les transformations Silver sur toutes les tables."""
    silver = {
        "sales": clean_sales(bronze["sales"]),
        "customers": clean_customers(bronze["customers"]),
        "products": clean_products(bronze["products"]),
    }

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in silver.items():
        df.to_parquet(SILVER_DIR / f"{name}.parquet", index=False)
        print(f"[SILVER] {name}: {len(df)} lignes (nettoyé + dédoublonné)")

    return silver
