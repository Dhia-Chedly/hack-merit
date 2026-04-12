# Tunisia Real-Estate Demand Intelligence (Streamlit MVP)

## Product Overview
Tunisia Real-Estate Demand Intelligence is a hackathon-ready MVP that helps commercial teams:
- understand marketing efficiency and lead quality
- explore project performance geographically
- estimate near-term demand and sales momentum
- identify underperforming projects through transparent risk scoring
- translate analytics into clear project-level actions

The app is built as a modular Streamlit product with reusable business logic in `src/` and presentation pages in `pages/`.

## Core Features
- Executive overview homepage with KPI snapshot and immediate signals
- Interactive Tunisia map with project tooltips, filters, and decision context
- Marketing intelligence page for acquisition and conversion performance
- Forecasting page with explainable projected demand and sales
- Risk analysis page with project and city risk breakdowns
- Decision support page with ranked recommended actions and priority scoring

## Project Structure
```text
.
├── app.py
├── data/
│   └── projects.csv
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

## Data and Logic
- Dataset: `data/projects.csv`
- Scope: mock project-level data for Tunisian cities (for demo use)
- Data validation: required columns and numeric checks in `src/data_loader.py`
- KPI and marketing metrics: `src/kpis.py`
- Forecasting (explainable heuristic layer): `src/forecasting.py`
- Risk scoring (weighted normalized components): `src/risk.py`
- Decision support (rule-based recommendations): `src/decision_support.py`

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

## Run the App
```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Page Guide
- `Overview` (`app.py`): landing dashboard with portfolio KPIs, quick recommendations, and top risk alerts.
- `Map`: geospatial view of projects with city and property filters plus rich project tooltips.
- `Marketing Intelligence`: lead quality, conversion efficiency, and cost-efficiency comparisons.
- `Forecasting`: projected demand/sales metrics and city/project forecast summaries.
- `Risk Analysis`: risk score rankings, city risk exposure, and driver-level interpretation.
- `Decision Support`: prioritized action recommendations with confidence, rationale, and expected impact.

## Notes
- This MVP is intentionally transparent and explainable for demo storytelling.
- Forecasting, risk, and recommendations are rule/heuristic based (not heavy ML pipelines).
- The structure is designed for easy extension in future phases.
