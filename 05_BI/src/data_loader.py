from __future__ import annotations

from pathlib import Path
import pandas as pd

# The BI layer only reads from the explicitly transformed Gold table
BI_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "project_metrics.csv"

REQUIRED_COLUMNS = [
    "project_name",
    "city",
    "property_type",
    "latitude",
    "longitude",
    "spend",
    "total_leads",
    "qualified_leads",
    "visits",
    "reservations",
    "sales",
    "avg_price",
]

def load_projects_data() -> pd.DataFrame:
    """Loads the curated BI layer dataset."""
    if not BI_DATA_PATH.exists():
        raise FileNotFoundError(
            f"BI dataset not found at '{BI_DATA_PATH}'. Please run the ELT pipeline first."
        )

    try:
        df = pd.read_csv(BI_DATA_PATH, parse_dates=["launch_date"])
    except Exception as exc:
        raise ValueError(f"Failed to read BI dataset: {exc}") from exc

    if df.empty:
        raise ValueError("BI dataset contains no rows.")

    df.columns = [str(column).strip() for column in df.columns]

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"BI dataset is missing required columns: {', '.join(missing_columns)}")

    # Ensure required derived metrics exist
    if "neighborhood" not in df.columns:
        df["neighborhood"] = "Unknown"

    if "unsold_inventory" not in df.columns:
        if "total_units" not in df.columns:
            raise ValueError("Dataset must include 'unsold_inventory' or 'total_units'.")
        
        total_units = pd.to_numeric(df["total_units"], errors="coerce").fillna(0.0)
        sales = pd.to_numeric(df["sales"], errors="coerce").fillna(0.0)
        df["unsold_inventory"] = (total_units - sales).clip(lower=0.0)

    # Standardize column mappings that the dashboard expects
    df = df.rename(columns={"spend": "ad_spend", "total_leads": "leads"})

    # Validate numeric types
    numeric_columns = ["latitude", "longitude", "ad_spend", "leads", "qualified_leads", "visits", "reservations", "sales", "unsold_inventory", "avg_price"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def load_projects_data_with_metadata() -> tuple[pd.DataFrame, str, Path]:
    df = load_projects_data()
    return df, "Bi-Lakehouse", BI_DATA_PATH

