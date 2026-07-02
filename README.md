# Strategic Lakehouse — POC GlobalTrade Solutions

POC minimal d'architecture Lakehouse (Bronze / Silver / Gold) pour la société fictive GlobalTrade Solutions.

## Prérequis

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets)

## Installation

```bash
git clone <url-du-repo>
cd strategic-lakehouse
uv venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
uv sync
```

## Données

Télécharger le dataset Kaggle [Cleaned Retail Customer Dataset](https://www.kaggle.com/datasets/rizwanbinakbar/cleaned-retail-customer-dataset-sql-based-etl) et extraire les CSV dans `data/raw/` :

```
data/raw/
├── g_fact_sales.csv
├── g_dim_customers.csv
└── g_dim_products.csv
```

## Lancement

### 1. Exécuter le pipeline (Bronze → Silver → Gold)

```bash
python -m src.pipeline
```

Cela génère les fichiers Parquet dans `data/bronze/`, `data/silver/` et `data/gold/`.

### 2. Lancer l'API et le dashboard

```bash
uvicorn src.api:app --reload
```

Puis ouvrir [http://localhost:8000](http://localhost:8000) pour le dashboard.

## Endpoints API

| Endpoint | Description |
|---|---|
| `GET /api/kpi/summary` | KPI globaux (commandes, clients, CA, panier moyen) |
| `GET /api/kpi/revenue-by-country` | CA par pays |
| `GET /api/kpi/sales-by-category` | Ventes par catégorie produit |
| `GET /api/kpi/monthly-trend` | Tendance mensuelle du CA |

## Architecture

```
data/
├── raw/       ← CSV bruts (source Kaggle)
├── bronze/    ← Parquet brut (copie fidèle)
├── silver/    ← Parquet nettoyé, typé, dédoublonné
└── gold/      ← Parquet agrégé (KPI)

src/
├── bronze.py   ← Ingestion CSV → Parquet
├── silver.py   ← Nettoyage, typage, dédoublonnage
├── gold.py     ← Agrégation KPI via DuckDB
├── pipeline.py ← Orchestration Bronze → Silver → Gold
└── api.py      ← API FastAPI + interface web

static/
└── index.html  ← Dashboard accessible (WCAG)
```

## Accessibilité

L'interface respecte les normes RGAA / WCAG 2.1 AA :
- Balises HTML sémantiques (`<header>`, `<main>`, `<footer>`, `<h1>`, `<h2>`)
- Contrastes conformes (ratio > 4.5:1 sur tous les textes)
- Navigation clavier avec skip link
- Zones `aria-live="polite"` pour le rafraîchissement des KPI
- Attributs `role` et `aria-label` sur les régions
