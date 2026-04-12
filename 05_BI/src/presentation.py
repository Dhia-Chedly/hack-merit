"""Shared presentation helpers for Streamlit pages."""

from __future__ import annotations

import math

import pandas as pd

APP_NAME = "Tunisia Real-Estate Demand Intelligence"


def full_page_title(page_name: str) -> str:
    return f"{page_name} | {APP_NAME}"


def sorted_options(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    return sorted(df[column].dropna().astype(str).unique().tolist())


def _to_float(value: float | int | str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(converted) or math.isinf(converted):
        return default
    return converted


def format_number(value: float | int | str | None) -> str:
    return f"{_to_float(value):,.0f}"


def format_percentage(value: float | int | str | None, *, digits: int = 1) -> str:
    return f"{_to_float(value):.{digits}%}"


def format_currency(
    value: float | int | str | None, *, currency: str = "TND", digits: int = 0
) -> str:
    return f"{currency} {_to_float(value):,.{digits}f}"


def format_score(value: float | int | str | None, *, digits: int = 1, scale: int = 100) -> str:
    return f"{_to_float(value):.{digits}f}/{scale}"
