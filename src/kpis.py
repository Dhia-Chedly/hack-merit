from collections.abc import Iterable

import pandas as pd

KPI_REQUIRED_COLUMNS = [
    "leads",
    "qualified_leads",
    "sales",
    "unsold_inventory",
    "avg_price",
    "visits",
    "reservations",
]


def _validate_dataframe(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    if df is None:
        raise ValueError("Input DataFrame is None.")

    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns for KPI calculation: {missing_text}")


def _get_numeric_series(df: pd.DataFrame, column_name: str) -> pd.Series:
    _validate_dataframe(df, [column_name])

    if df.empty:
        return pd.Series(dtype="float64")

    return pd.to_numeric(df[column_name], errors="coerce").fillna(0.0)


def total_leads(df: pd.DataFrame) -> int:
    return int(_get_numeric_series(df, "leads").sum())


def total_qualified_leads(df: pd.DataFrame) -> int:
    return int(_get_numeric_series(df, "qualified_leads").sum())


def qualified_lead_rate(df: pd.DataFrame) -> float:
    leads = total_leads(df)
    if leads == 0:
        return 0.0
    return total_qualified_leads(df) / leads


def total_sales(df: pd.DataFrame) -> int:
    return int(_get_numeric_series(df, "sales").sum())


def total_unsold_inventory(df: pd.DataFrame) -> int:
    return int(_get_numeric_series(df, "unsold_inventory").sum())


def average_property_price(df: pd.DataFrame) -> float:
    prices = _get_numeric_series(df, "avg_price")
    if prices.empty:
        return 0.0
    return float(prices.mean())


def visit_to_reservation_rate(df: pd.DataFrame) -> float:
    visits = int(_get_numeric_series(df, "visits").sum())
    if visits == 0:
        return 0.0

    reservations = int(_get_numeric_series(df, "reservations").sum())
    return reservations / visits


def calculate_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    _validate_dataframe(df, KPI_REQUIRED_COLUMNS)

    return {
        "total_leads": total_leads(df),
        "total_qualified_leads": total_qualified_leads(df),
        "qualified_lead_rate": qualified_lead_rate(df),
        "total_sales": total_sales(df),
        "total_unsold_inventory": total_unsold_inventory(df),
        "average_property_price": average_property_price(df),
        "visit_to_reservation_rate": visit_to_reservation_rate(df),
    }
