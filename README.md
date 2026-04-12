# Tunisia Real-Estate Demand Intelligence (Streamlit MVP)

## Product Overview
Tunisia Real-Estate Demand Intelligence is a hackathon-ready MVP that helps commercial teams:
- understand marketing efficiency and lead quality
- explore project performance geographically
- estimate near-term demand and sales momentum
- identify underperforming projects through transparent risk scoring
- translate analytics into clear project-level actions

The app is built as a modular Streamlit product with reusable business logic in `src/`, UI pages in `pages/`, and a layered ETL pipeline in `etl/`.

## Core Features
- Executive overview homepage with KPI snapshot and immediate signals
- Interactive Tunisia map with project tooltips, filters, and decision context
- Marketing intelligence page for acquisition and conversion performance
- Forecasting page with explainable projected demand and sales
- Risk analysis page with project and city risk breakdowns
- Decision support page with ranked recommended actions and priority scoring

## Data Layers
- `data/raw/`: synthetic operational tables (projects, campaigns, leads, visits, sales)
- `data/processed/`: cleaned and validated tables with enforced business rules
- `data/curated/`: analytics-ready tables for dashboarding, forecasting, and risk inputs

## Project Structure
```text
.
├── app.py
├── data/
│   ├── raw/
│   ├── processed/
│   ├── curated/
│   └── projects.csv
├── etl/
│   ├── config.py
│   ├── generate_projects.py
│   ├── generate_campaigns.py
│   ├── generate_leads.py
│   ├── generate_visits.py
│   ├── generate_sales.py
│   ├── clean_raw_data.py
│   ├── build_curated_tables.py
│   └── run_pipeline.py
├── pages/
│   ├── 1_Map.py
│   ├── 2_Marketing_Intelligence.py
│   ├── 3_Forecasting.py
│   ├── 4_Risk_Analysis.py
│   └── 5_Decision_Support.py
├── src/
│   ├── data_loader.py
│   ├── kpis.py
│   ├── forecasting.py
│   ├── risk.py
│   ├── decision_support.py
│   └── presentation.py
├── requirements.txt
└── README.md
```

## Setup
1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

## Run the Streamlit App
```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.
The app auto-selects `data/curated/project_metrics.csv` when available and falls back to `data/projects.csv`.

## Run the ETL Pipeline
From the project root:

```bash
python etl/run_pipeline.py
```

This executes:
1. Raw synthetic generation
2. Cleaning and validation
3. Curated table construction

## ETL Script Guide
- `etl/config.py`: reusable assumptions for Tunisian city profiles, neighborhood geographies, channel behavior, conversion rules, quality tiers, and date range.
- `etl/generate_projects.py`: creates project master data with realistic city/property pricing patterns.
- `etl/generate_campaigns.py`: generates channel-level spend/impressions/clicks/leads with business relationships.
- `etl/generate_leads.py`: creates lead-level records tied to campaign performance and lead quality dynamics.
- `etl/generate_visits.py`: simulates visit and reservation behavior from lead quality, intent, and price pressure.
- `etl/generate_sales.py`: simulates transactions and sale prices from reservation pipeline strength.
- `etl/clean_raw_data.py`: standardizes types/dates, validates IDs and joins, enforces funnel constraints, and writes processed tables.
- `etl/build_curated_tables.py`: builds analytics-ready tables:
  - `project_metrics.csv`
  - `city_metrics.csv`
  - `project_timeseries.csv`
  - `forecast_base.csv`
  - `risk_base.csv`
- `etl/run_pipeline.py`: orchestrates the full ETL flow with clear progress logs and row counts.

## Notes
- The synthetic generation is deterministic and relationship-driven (not independent random columns).
- Forecasting, risk, and recommendations in the app remain transparent and explainable for demo storytelling.
- The ETL and app structure are designed for extension in future phases.
