"""Lightweight, explainable forecasting utilities for the MVP.

This module is intentionally heuristic-driven because the current dataset is
cross-sectional (project snapshots) rather than true time series.

Forecast assumptions:
1. Projects with stronger funnel quality (qualified lead rate and conversion)
   should see better near-term momentum.
2. Higher inventory absorption (sales vs. unsold inventory) indicates healthier
   demand and supports stronger projections.
3. Forecasts blend current performance and normalized relative strength to avoid
   unstable jumps in a hackathon demo setting.
"""

from collections.abc import Iterable

import pandas as pd

FORECAST_REQUIRED_COLUMNS = [
    "project_name",
    "city",
    "neighborhood",
    "property_type",
    "leads",
    "qualified_leads",
    "visits",
    "reservations",
    "sales",
    "unsold_inventory",
]

PROJECT_FORECAST_COLUMNS = [
    "project_name",
    "city",
    "neighborhood",
    "property_type",
    "current_leads",
    "current_sales",
    "unsold_inventory",
    "projected_leads",
    "projected_sales",
    "projected_demand_score",
    "projected_lead_growth_rate",
    "projected_sales_growth_rate",
    "qualified_lead_rate",
    "lead_to_visit_rate",
    "visit_to_reservation_rate",
    "reservation_to_sale_rate",
]

CITY_FORECAST_COLUMNS = [
    "city",
    "project_count",
    "current_leads",
    "projected_leads",
    "current_sales",
    "projected_sales",
    "unsold_inventory",
    "projected_demand_score",
    "projected_lead_growth_rate",
    "projected_sales_growth_rate",
]

FORECAST_ASSUMPTIONS = [
    (
        "Demand score uses a weighted blend of current lead volume, qualified lead rate, "
        "funnel conversion, and inventory absorption."
    ),
    (
        "Projected leads adjust current leads with a bounded momentum factor based on "
        "demand score, quality rate, visit engagement, and inventory absorption."
    ),
    (
        "Projected sales blend current sales with a pipeline estimate and apply a "
        "light inventory cap to keep projections realistic."
    ),
]


def _validate_dataframe(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    if df is None:
        raise ValueError("Input DataFrame is None.")
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(
            f"Missing required columns for forecasting calculations: {missing_text}"
        )


def _safe_divide(numerator: float | int, denominator: float | int) -> float:
    denominator_value = float(denominator)
    if denominator_value == 0:
        return 0.0
    return float(numerator) / denominator_value


def _safe_divide_series(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    numerator_values = pd.to_numeric(numerator, errors="coerce").fillna(0.0)
    denominator_values = pd.to_numeric(denominator, errors="coerce").fillna(0.0)

    output = pd.Series(0.0, index=numerator_values.index, dtype="float64")
    valid = denominator_values != 0
    output.loc[valid] = numerator_values.loc[valid] / denominator_values.loc[valid]
    return output


def _normalize_series(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0.0)
    min_value = float(values.min()) if len(values) else 0.0
    max_value = float(values.max()) if len(values) else 0.0

    if max_value - min_value == 0:
        return pd.Series(0.5, index=values.index, dtype="float64")

    return (values - min_value) / (max_value - min_value)


def forecast_assumptions() -> list[str]:
    return FORECAST_ASSUMPTIONS.copy()


def _empty_project_forecast() -> pd.DataFrame:
    return pd.DataFrame(columns=PROJECT_FORECAST_COLUMNS)


def forecast_projects(df: pd.DataFrame) -> pd.DataFrame:
    _validate_dataframe(df, FORECAST_REQUIRED_COLUMNS)

    if df.empty:
        return _empty_project_forecast()

    work_df = df.copy()
    for column in [
        "leads",
        "qualified_leads",
        "visits",
        "reservations",
        "sales",
        "unsold_inventory",
    ]:
        work_df[column] = pd.to_numeric(work_df[column], errors="coerce").fillna(0.0)

    work_df["qualified_lead_rate"] = _safe_divide_series(
        work_df["qualified_leads"], work_df["leads"]
    )
    work_df["lead_to_visit_rate"] = _safe_divide_series(work_df["visits"], work_df["leads"])
    work_df["visit_to_reservation_rate"] = _safe_divide_series(
        work_df["reservations"], work_df["visits"]
    )
    work_df["reservation_to_sale_rate"] = _safe_divide_series(
        work_df["sales"], work_df["reservations"]
    )
    work_df["inventory_absorption_rate"] = _safe_divide_series(
        work_df["sales"], work_df["sales"] + work_df["unsold_inventory"]
    )

    work_df["projected_demand_score"] = (
        0.30 * _normalize_series(work_df["leads"])
        + 0.20 * work_df["qualified_lead_rate"]
        + 0.15 * work_df["lead_to_visit_rate"]
        + 0.15 * work_df["visit_to_reservation_rate"]
        + 0.20 * work_df["inventory_absorption_rate"]
    ).clip(0, 1) * 100

    overall_qualified_rate = _safe_divide(
        work_df["qualified_leads"].sum(), work_df["leads"].sum()
    )
    overall_visit_rate = _safe_divide(work_df["visits"].sum(), work_df["leads"].sum())
    mean_absorption = float(work_df["inventory_absorption_rate"].mean())

    base_momentum = (work_df["projected_demand_score"] / 100 - 0.5) * 0.35
    quality_adjustment = (work_df["qualified_lead_rate"] - overall_qualified_rate) * 0.40
    engagement_adjustment = (work_df["lead_to_visit_rate"] - overall_visit_rate) * 0.25
    inventory_adjustment = (work_df["inventory_absorption_rate"] - mean_absorption) * 0.20
    work_df["projected_lead_growth_rate"] = (
        base_momentum
        + quality_adjustment
        + engagement_adjustment
        + inventory_adjustment
    ).clip(-0.25, 0.35)

    work_df["projected_leads"] = (
        work_df["leads"] * (1 + work_df["projected_lead_growth_rate"])
    ).round().clip(lower=0)

    current_sale_rate = _safe_divide_series(work_df["sales"], work_df["leads"])
    demand_multiplier = (0.80 + (work_df["projected_demand_score"] / 100) * 0.60).clip(
        0.70, 1.40
    )
    projected_pipeline_sales = work_df["projected_leads"] * current_sale_rate * demand_multiplier
    blended_projected_sales = 0.55 * work_df["sales"] + 0.45 * projected_pipeline_sales

    inventory_cap = (work_df["sales"] + (work_df["unsold_inventory"] * 0.75)).clip(lower=0)
    work_df["projected_sales"] = (
        blended_projected_sales.clip(lower=0).where(
            blended_projected_sales <= inventory_cap, inventory_cap
        )
    ).round()

    work_df["projected_sales_growth_rate"] = _safe_divide_series(
        work_df["projected_sales"] - work_df["sales"], work_df["sales"]
    ).clip(-0.40, 0.60)

    output_df = pd.DataFrame(
        {
            "project_name": work_df["project_name"],
            "city": work_df["city"],
            "neighborhood": work_df["neighborhood"],
            "property_type": work_df["property_type"],
            "current_leads": work_df["leads"].round().astype("int64"),
            "current_sales": work_df["sales"].round().astype("int64"),
            "unsold_inventory": work_df["unsold_inventory"].round().astype("int64"),
            "projected_leads": work_df["projected_leads"].round().astype("int64"),
            "projected_sales": work_df["projected_sales"].round().astype("int64"),
            "projected_demand_score": work_df["projected_demand_score"].round(1),
            "projected_lead_growth_rate": work_df["projected_lead_growth_rate"],
            "projected_sales_growth_rate": work_df["projected_sales_growth_rate"],
            "qualified_lead_rate": work_df["qualified_lead_rate"],
            "lead_to_visit_rate": work_df["lead_to_visit_rate"],
            "visit_to_reservation_rate": work_df["visit_to_reservation_rate"],
            "reservation_to_sale_rate": work_df["reservation_to_sale_rate"],
        }
    )

    return output_df.sort_values(
        by=["projected_demand_score", "projected_sales", "projected_leads"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def forecast_city_summary(project_forecast_df: pd.DataFrame) -> pd.DataFrame:
    _validate_dataframe(project_forecast_df, PROJECT_FORECAST_COLUMNS)

    if project_forecast_df.empty:
        return pd.DataFrame(columns=CITY_FORECAST_COLUMNS)

    grouped_df = (
        project_forecast_df.groupby("city", as_index=False)
        .agg(
            project_count=("project_name", "count"),
            current_leads=("current_leads", "sum"),
            projected_leads=("projected_leads", "sum"),
            current_sales=("current_sales", "sum"),
            projected_sales=("projected_sales", "sum"),
            unsold_inventory=("unsold_inventory", "sum"),
            projected_demand_score=("projected_demand_score", "mean"),
        )
        .copy()
    )

    grouped_df["projected_lead_growth_rate"] = _safe_divide_series(
        grouped_df["projected_leads"] - grouped_df["current_leads"], grouped_df["current_leads"]
    )
    grouped_df["projected_sales_growth_rate"] = _safe_divide_series(
        grouped_df["projected_sales"] - grouped_df["current_sales"], grouped_df["current_sales"]
    )
    grouped_df["projected_demand_score"] = grouped_df["projected_demand_score"].round(1)

    return grouped_df.sort_values(
        by=["projected_demand_score", "projected_sales"],
        ascending=[False, False],
    ).reset_index(drop=True)


def forecast_overview_metrics(project_forecast_df: pd.DataFrame) -> dict[str, float | int]:
    _validate_dataframe(project_forecast_df, PROJECT_FORECAST_COLUMNS)

    if project_forecast_df.empty:
        return {
            "project_count": 0,
            "current_leads": 0,
            "projected_leads": 0,
            "current_sales": 0,
            "projected_sales": 0,
            "lead_growth_rate": 0.0,
            "sales_growth_rate": 0.0,
            "average_projected_demand_score": 0.0,
            "high_opportunity_projects": 0,
        }

    current_leads = int(project_forecast_df["current_leads"].sum())
    projected_leads = int(project_forecast_df["projected_leads"].sum())
    current_sales = int(project_forecast_df["current_sales"].sum())
    projected_sales = int(project_forecast_df["projected_sales"].sum())

    return {
        "project_count": int(len(project_forecast_df)),
        "current_leads": current_leads,
        "projected_leads": projected_leads,
        "current_sales": current_sales,
        "projected_sales": projected_sales,
        "lead_growth_rate": _safe_divide(projected_leads - current_leads, current_leads),
        "sales_growth_rate": _safe_divide(projected_sales - current_sales, current_sales),
        "average_projected_demand_score": float(
            project_forecast_df["projected_demand_score"].mean()
        ),
        "high_opportunity_projects": int(
            (project_forecast_df["projected_demand_score"] >= 65).sum()
        ),
    }


def forecast_summary_insights(
    project_forecast_df: pd.DataFrame, city_summary_df: pd.DataFrame
) -> dict[str, object]:
    _validate_dataframe(project_forecast_df, PROJECT_FORECAST_COLUMNS)
    _validate_dataframe(city_summary_df, CITY_FORECAST_COLUMNS)

    if project_forecast_df.empty or city_summary_df.empty:
        return {
            "strongest_city": None,
            "strongest_project": None,
            "slowdown_cities": [],
            "slowdown_projects": [],
            "observations": [
                "No projects match the selected filters, so no forecasting summary is available."
            ],
        }

    strongest_city = city_summary_df.sort_values(
        by=["projected_demand_score", "projected_sales_growth_rate"],
        ascending=[False, False],
    ).iloc[0]
    strongest_project = project_forecast_df.sort_values(
        by=["projected_demand_score", "projected_sales_growth_rate"],
        ascending=[False, False],
    ).iloc[0]

    slowdown_cities_df = city_summary_df[
        (city_summary_df["projected_demand_score"] < city_summary_df["projected_demand_score"].median())
        | (city_summary_df["projected_sales_growth_rate"] < 0)
    ].sort_values(
        by=["projected_demand_score", "projected_sales_growth_rate"],
        ascending=[True, True],
    )
    slowdown_projects_df = project_forecast_df[
        (project_forecast_df["projected_demand_score"] < project_forecast_df["projected_demand_score"].quantile(0.35))
        | (project_forecast_df["projected_sales_growth_rate"] < 0)
    ].sort_values(
        by=["projected_demand_score", "projected_sales_growth_rate"],
        ascending=[True, True],
    )

    overview = forecast_overview_metrics(project_forecast_df)
    observations = [
        (
            "Overall forecast indicates leads moving from "
            f"{overview['current_leads']:,.0f} to {overview['projected_leads']:,.0f} "
            f"({overview['lead_growth_rate']:.1%})."
        ),
        (
            "Sales outlook shifts from "
            f"{overview['current_sales']:,.0f} to {overview['projected_sales']:,.0f} "
            f"({overview['sales_growth_rate']:.1%}) under the current funnel assumptions."
        ),
    ]

    return {
        "strongest_city": strongest_city.to_dict(),
        "strongest_project": strongest_project.to_dict(),
        "slowdown_cities": slowdown_cities_df.head(2).to_dict(orient="records"),
        "slowdown_projects": slowdown_projects_df.head(2).to_dict(orient="records"),
        "observations": observations,
    }

