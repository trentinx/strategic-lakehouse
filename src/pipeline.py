"""Pipeline complet : Bronze -> Silver -> Gold."""

from src.bronze import ingest_all
from src.silver import transform_all
from src.gold import build_kpis


def run() -> None:
    print("=" * 50)
    print("  Pipeline Lakehouse - GlobalTrade Solutions")
    print("=" * 50)

    print("\n--- Couche Bronze (ingestion brute) ---")
    bronze = ingest_all()

    print("\n--- Couche Silver (nettoyage + typage + dédoublonnage) ---")
    transform_all(bronze)

    print("\n--- Couche Gold (agrégation KPI) ---")
    build_kpis()

    print("\n Pipeline terminé avec succès.")


if __name__ == "__main__":
    run()
