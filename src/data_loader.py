from pathlib import Path

import pandas as pd

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


def load_projects_data(file_path: str | Path = "data/projects.csv") -> pd.DataFrame:
    dataset_path = Path(file_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{dataset_path}'. Expected file: data/projects.csv"
        )

    try:
        df = pd.read_csv(dataset_path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Dataset file '{dataset_path}' is empty.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Dataset file '{dataset_path}' has invalid CSV format.") from exc
    except OSError as exc:
        raise RuntimeError(f"Unable to read dataset file '{dataset_path}': {exc}") from exc

    if df.empty:
        raise ValueError(f"Dataset file '{dataset_path}' contains no project rows.")

    df.columns = [str(column).strip() for column in df.columns]
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"Dataset is missing required columns: {missing_text}")

    for column in TEXT_COLUMNS:
        if df[column].isna().any() or df[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Column '{column}' contains empty values.")

    for column in NUMERIC_COLUMNS:
        converted_values = pd.to_numeric(df[column], errors="coerce")
        if converted_values.isna().any():
            raise ValueError(f"Column '{column}' contains non-numeric values.")
        df[column] = converted_values

    ordered_columns = REQUIRED_COLUMNS + [
        column for column in df.columns if column not in REQUIRED_COLUMNS
    ]
    return df[ordered_columns].copy()
