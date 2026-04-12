from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

PROJECT_SOURCE = Literal["legacy", "curated"]

LEGACY_PROJECTS_PATH = Path("data/projects.csv")
CURATED_PROJECT_METRICS_PATH = Path("data/curated/project_metrics.csv")

REQUIRED_COLUMNS = [
    "project_name",
    "city",
    "neighborhood",
    "latitude",
    "longitude",
    "property_type",
    "ad_spend",
    "leads",
    "qualified_leads",
    "visits",
    "reservations",
    "sales",
    "unsold_inventory",
    "avg_price",
]

NUMERIC_COLUMNS = [
    "latitude",
    "longitude",
    "ad_spend",
    "leads",
    "qualified_leads",
    "visits",
    "reservations",
    "sales",
    "unsold_inventory",
    "avg_price",
]

TEXT_COLUMNS = ["project_name", "city", "neighborhood", "property_type"]

CURATED_REQUIRED_COLUMNS = [
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


def _read_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    try:
        if parse_dates:
            return pd.read_csv(path, parse_dates=parse_dates)
        return pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Dataset file '{path}' is empty.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Dataset file '{path}' has invalid CSV format.") from exc
    except OSError as exc:
        raise RuntimeError(f"Unable to read dataset file '{path}': {exc}") from exc


def _validate_project_dataframe(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    if df.empty:
        raise ValueError(f"{dataset_name} contains no project rows.")

    df = df.copy()
    df.columns = [str(column).strip() for column in df.columns]

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"{dataset_name} is missing required columns: {missing_text}")

    for column in TEXT_COLUMNS:
        if df[column].isna().any() or df[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"{dataset_name} column '{column}' contains empty values.")

    for column in NUMERIC_COLUMNS:
        converted_values = pd.to_numeric(df[column], errors="coerce")
        if converted_values.isna().any():
            raise ValueError(f"{dataset_name} column '{column}' contains non-numeric values.")
        df[column] = converted_values

    ordered_columns = REQUIRED_COLUMNS + [
        column for column in df.columns if column not in REQUIRED_COLUMNS
    ]
    return df[ordered_columns].copy()


def _load_legacy_projects(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Legacy dataset not found at '{path}'. Expected file: data/projects.csv"
        )
    legacy_df = _read_csv(path)
    return _validate_project_dataframe(legacy_df, dataset_name=f"Legacy dataset '{path}'")


def _load_curated_projects(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Curated dataset not found at '{path}'. Expected file: data/curated/project_metrics.csv"
        )

    curated_df = _read_csv(path, parse_dates=["launch_date"])
    if curated_df.empty:
        raise ValueError(f"Curated dataset '{path}' contains no project rows.")

    curated_df = curated_df.copy()
    curated_df.columns = [str(column).strip() for column in curated_df.columns]

    missing_columns = [
        column for column in CURATED_REQUIRED_COLUMNS if column not in curated_df.columns
    ]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(
            f"Curated dataset '{path}' is missing required columns: {missing_text}"
        )

    if "neighborhood" not in curated_df.columns:
        curated_df["neighborhood"] = "Unknown"

    if "unsold_inventory" not in curated_df.columns:
        if "total_units" not in curated_df.columns:
            raise ValueError(
                "Curated project metrics must include either 'unsold_inventory' or 'total_units'."
            )
        total_units = pd.to_numeric(curated_df["total_units"], errors="coerce").fillna(0.0)
        sales = pd.to_numeric(curated_df["sales"], errors="coerce").fillna(0.0)
        curated_df["unsold_inventory"] = (total_units - sales).clip(lower=0.0)

    curated_df = curated_df.rename(columns={"spend": "ad_spend", "total_leads": "leads"})

    return _validate_project_dataframe(
        curated_df, dataset_name=f"Curated dataset '{path}'"
    )


def resolve_projects_source(
    source: str = "auto",
    *,
    legacy_path: str | Path = LEGACY_PROJECTS_PATH,
    curated_project_metrics_path: str | Path = CURATED_PROJECT_METRICS_PATH,
) -> tuple[PROJECT_SOURCE, Path]:
    source_normalized = source.strip().lower()
    if source_normalized not in {"auto", "legacy", "curated"}:
        raise ValueError("source must be one of: 'auto', 'legacy', 'curated'.")

    legacy = Path(legacy_path)
    curated = Path(curated_project_metrics_path)

    if source_normalized == "legacy":
        if not legacy.exists():
            raise FileNotFoundError(
                f"Legacy dataset not found at '{legacy}'. Expected file: data/projects.csv"
            )
        return "legacy", legacy

    if source_normalized == "curated":
        if not curated.exists():
            raise FileNotFoundError(
                f"Curated dataset not found at '{curated}'. Expected file: data/curated/project_metrics.csv"
            )
        return "curated", curated

    if curated.exists():
        return "curated", curated
    if legacy.exists():
        return "legacy", legacy

    raise FileNotFoundError(
        "No dataset found. Expected one of: "
        f"'{curated}' (curated) or '{legacy}' (legacy)."
    )


def load_projects_data_with_metadata(
    *,
    source: str = "auto",
    legacy_path: str | Path = LEGACY_PROJECTS_PATH,
    curated_project_metrics_path: str | Path = CURATED_PROJECT_METRICS_PATH,
) -> tuple[pd.DataFrame, PROJECT_SOURCE, Path]:
    resolved_source, resolved_path = resolve_projects_source(
        source,
        legacy_path=legacy_path,
        curated_project_metrics_path=curated_project_metrics_path,
    )
    if resolved_source == "curated":
        dataset = _load_curated_projects(resolved_path)
    else:
        dataset = _load_legacy_projects(resolved_path)

    return dataset, resolved_source, resolved_path


def load_projects_data(
    file_path: str | Path = LEGACY_PROJECTS_PATH,
    *,
    source: str = "auto",
    curated_project_metrics_path: str | Path = CURATED_PROJECT_METRICS_PATH,
) -> pd.DataFrame:
    dataset, _, _ = load_projects_data_with_metadata(
        source=source,
        legacy_path=file_path,
        curated_project_metrics_path=curated_project_metrics_path,
    )
    return dataset

