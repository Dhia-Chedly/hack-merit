# Tunisia Real-Estate Demand Intelligence (Streamlit MVP)

## Product Overview
Tunisia Real-Estate Demand Intelligence is a hackathon-ready MVP that helps commercial teams:
- understand marketing efficiency and lead quality
- explore project performance geographically
- estimate near-term demand and sales momentum
- identify underperforming projects through transparent risk scoring
- translate analytics into clear project-level actions

## Repository Architecture
This repository uses a root-level Streamlit entrypoint that delegates to the BI application under `05_BI/`.

- Root launch entrypoints:
  - `app.py` (Streamlit app launcher)
  - `pages/*.py` (multipage launch wrappers)
  - `run_pipeline.py` (pipeline orchestrator)
- BI application code:
  - `05_BI/app.py`
  - `05_BI/pages/`
  - `05_BI/src/`
- Data pipeline scripts:
  - `02_Ingestion/ingest_to_raw.py`
  - `04_Transform/transform_pipeline.py`

## Data Layers
- `01_Source/projects.csv`: source dataset used for ingestion
- `03_Storage_Raw/lakehouse.duckdb`: raw lakehouse store
- `data/curated/project_metrics.csv`: canonical curated metrics table for dashboard use
- `05_BI/data/project_metrics.csv`: mirrored BI-layer copy for backward compatibility

The transform step writes both curated outputs so either path stays up to date.

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

3. Configure Gemini API key (required for AI pages).

```bash
export GEMINI_API_KEY="your_api_key_here"
```

`GOOGLE_API_KEY` is also supported.
A project-root `.env` file is auto-read as a fallback.

## Run From Project Root
### 1) Build/refresh data pipeline
```bash
python3 run_pipeline.py
```

This runs:
1. `02_Ingestion/ingest_to_raw.py`
2. `04_Transform/transform_pipeline.py`

### 2) Launch Streamlit
```bash
streamlit run app.py
```

This works directly from the repository root.

## AI Features (Gemini)
The app includes two Gemini-powered pages:
- `6_AI_Insights.py`: structured executive summary (3 insights, 2 risks, 2 actions)
- `7_AI_Chatbot.py`: contextual Q&A grounded in dashboard context only

### Gemini Integration Notes
- SDK: `google-genai`
- API key sources: `GEMINI_API_KEY` or `GOOGLE_API_KEY` (or `.env`)
- Model configuration lives in `05_BI/src/gemini_client.py` (`GEMINI_MODEL_NAME`)

## Notes
- Forecasting, risk, and recommendations are intentionally transparent and explainable for demo use.
- The architecture now supports running everything from the root without moving existing BI modules.
