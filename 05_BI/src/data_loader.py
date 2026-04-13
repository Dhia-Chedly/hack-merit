from __future__ import annotations

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_CANDIDATES: dict[str, Path] = {
    "curated": PROJECT_ROOT / "data" / "curated" / "project_metrics.csv",
    "bi_layer": PROJECT_ROOT / "05_BI" / "data" / "project_metrics.csv",
}

SOURCE_DISPLAY_NAMES: dict[str, str] = {
    "curated": "Curated project metrics",
    "bi_layer": "BI layer project metrics",
}

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


def source_display_name(source: str) -> str:
    return SOURCE_DISPLAY_NAMES.get(source, source)


def _resolve_dataset_path() -> tuple[str, Path]:
    """Resolve dataset path from known locations.

    Preference:
    1. Most recently updated candidate file.
    2. If timestamps tie, favor curated.
    """
    existing_sources: list[tuple[str, Path, float]] = []
    for source, path in DATASET_CANDIDATES.items():
        if path.exists():
            existing_sources.append((source, path, path.stat().st_mtime))

    if not existing_sources:
        expected_paths = "\n".join([f"- {path}" for path in DATASET_CANDIDATES.values()])
        raise FileNotFoundError(
            "BI dataset not found. Expected one of:\n"
            f"{expected_paths}\n"
            "Run the ingestion and transform scripts from project root first."
        )

    existing_sources.sort(
        key=lambda item: (item[2], item[0] == "curated"),
        reverse=True,
    )
    source, path, _ = existing_sources[0]
    return source, path


def load_projects_data(*, dataset_path: Path | None = None) -> pd.DataFrame:
    """Loads the curated BI layer dataset."""
    if dataset_path is None:
        _, dataset_path = _resolve_dataset_path()

    try:
        df = pd.read_csv(dataset_path)
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

    if "launch_date" in df.columns:
        df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")

    # Validate numeric types
    numeric_columns = ["latitude", "longitude", "ad_spend", "leads", "qualified_leads", "visits", "reservations", "sales", "unsold_inventory", "avg_price"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_projects_data_with_metadata() -> tuple[pd.DataFrame, str, Path]:
    source, dataset_path = _resolve_dataset_path()
    df = load_projects_data(dataset_path=dataset_path)
    return df, source, dataset_path
