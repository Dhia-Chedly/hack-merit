"""Project risk scoring utilities for an interpretable MVP layer.

This module combines marketing efficiency and forecast momentum signals into a
single project-level risk score. The scoring is intentionally transparent:
weighted normalized components that can be explained in a demo.
"""

from collections.abc import Iterable

import pandas as pd

from src.forecasting import forecast_projects
from src.kpis import project_marketing_breakdown

RISK_REQUIRED_COLUMNS = [
    "project_name",
    "city",
    "neighborhood",
    "property_type",
    "ad_spend",
    "leads",
    "qualified_leads",
    "visits",
    "reservations",
    "sales",
    "unsold_inventory",
]

RISK_OUTPUT_COLUMNS = [
    "project_name",
    "city",
    "neighborhood",
    "property_type",
    "current_leads",
    "current_sales",
    "unsold_inventory",
    "projected_sales",
    "projected_demand_score",
    "qualified_lead_rate",
    "cost_per_qualified_lead",
    "lead_to_visit_rate",
    "visit_to_reservation_rate",
    "risk_score",
    "risk_level",
    "top_risk_drivers",
]

CITY_RISK_COLUMNS = [
    "city",
    "project_count",
    "average_risk_score",
    "high_risk_projects",
    "medium_risk_projects",
    "low_risk_projects",
    "high_risk_share",
    "total_unsold_inventory",
    "total_projected_sales",
    "average_projected_demand_score",
]

RISK_SCORING_ASSUMPTIONS = [
    (
        "Risk score is a weighted normalized blend of lead quality, funnel conversion, "
        "inventory pressure, and forecast weakness signals."
    ),
    (
        "Each component is scaled from low-to-high risk so drivers are directly comparable "
        "across projects."
    ),
    (
        "Risk levels use fixed business thresholds (Low < 40, Medium 40-66.9, High >= 67) "
        "for straightforward interpretation in demos."
    ),
]

# Weighted risk components.
# Higher values mean higher risk after normalization.
RISK_COMPONENTS = {
    "low_qualified_lead_rate": {
        "source_column": "qualified_lead_rate",
        "invert": True,
        "weight": 0.17,
        "label": "Low qualified lead rate",
    },
    "high_cost_per_qualified_lead": {
        "source_column": "cost_per_qualified_lead",
        "invert": False,
        "weight": 0.17,
        "label": "High cost per qualified lead",
    },
    "weak_lead_to_visit_rate": {
        "source_column": "lead_to_visit_rate",
        "invert": True,
        "weight": 0.10,
        "label": "Weak lead to visit rate",
    },
    "weak_visit_to_reservation_rate": {
        "source_column": "visit_to_reservation_rate",
        "invert": True,
        "weight": 0.10,
        "label": "Weak visit to reservation rate",
    },
    "low_current_sales": {
        "source_column": "current_sales",
        "invert": True,
        "weight": 0.10,
        "label": "Low current sales",
    },
    "high_unsold_inventory": {
        "source_column": "unsold_inventory",
        "invert": False,
        "weight": 0.14,
        "label": "High unsold inventory",
    },
    "weak_projected_sales": {
        "source_column": "projected_sales",
        "invert": True,
        "weight": 0.12,
        "label": "Weak projected sales",
    },
    "weak_projected_demand_score": {
        "source_column": "projected_demand_score",
        "invert": True,
        "weight": 0.10,
        "label": "Weak projected demand score",
    },
}


def _validate_dataframe(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    if df is None:
        raise ValueError("Input DataFrame is None.")
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns for risk scoring: {missing_text}")


def _safe_divide(numerator: float | int, denominator: float | int) -> float:
    denominator_value = float(denominator)
    if denominator_value == 0:
        return 0.0
    return float(numerator) / denominator_value


def _normalize_series(series: pd.Series, *, invert: bool = False) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0.0)
    min_value = float(values.min()) if len(values) else 0.0
    max_value = float(values.max()) if len(values) else 0.0

    if max_value - min_value == 0:
        normalized = pd.Series(0.5, index=values.index, dtype="float64")
    else:
        normalized = (values - min_value) / (max_value - min_value)

    return 1 - normalized if invert else normalized


def _assign_risk_level(score: float) -> str:
    if score >= 67:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def _top_risk_driver_text(row: pd.Series, contribution_map: dict[str, str]) -> str:
    ranked = sorted(
        contribution_map.items(),
        key=lambda item: float(row[item[0]]),
        reverse=True,
    )
    top_labels = [label for _, label in ranked[:3]]
    return ", ".join(top_labels)


def risk_scoring_assumptions() -> list[str]:
    return RISK_SCORING_ASSUMPTIONS.copy()


def _empty_project_risk() -> pd.DataFrame:
    return pd.DataFrame(columns=RISK_OUTPUT_COLUMNS)


def calculate_project_risk(df: pd.DataFrame) -> pd.DataFrame:
    _validate_dataframe(df, RISK_REQUIRED_COLUMNS)

    if df.empty:
        return _empty_project_risk()

    marketing_df = project_marketing_breakdown(df)
    forecast_df = forecast_projects(df)

    join_keys = ["project_name", "city", "neighborhood", "property_type"]
    merge_marketing_cols = join_keys + [
        "qualified_lead_rate",
        "cost_per_qualified_lead",
        "lead_to_visit_rate",
        "visit_to_reservation_rate",
    ]
    merge_forecast_cols = join_keys + [
        "current_leads",
        "current_sales",
        "unsold_inventory",
        "projected_sales",
        "projected_demand_score",
    ]

    risk_df = forecast_df[merge_forecast_cols].merge(
        marketing_df[merge_marketing_cols],
        on=join_keys,
        how="left",
    )

    contribution_column_labels: dict[str, str] = {}
    risk_score_components = pd.Series(0.0, index=risk_df.index, dtype="float64")

    for component_name, config in RISK_COMPONENTS.items():
        source_column = config["source_column"]
        weight = float(config["weight"])
        normalized_component = _normalize_series(
            risk_df[source_column], invert=bool(config["invert"])
        )

        contribution_column = f"{component_name}_contribution"
        risk_df[contribution_column] = normalized_component * weight
        contribution_column_labels[contribution_column] = str(config["label"])
        risk_score_components += risk_df[contribution_column]

    risk_df["risk_score"] = (risk_score_components * 100).round(1).clip(0, 100)
    risk_df["risk_level"] = risk_df["risk_score"].map(_assign_risk_level)
    risk_df["top_risk_drivers"] = risk_df.apply(
        lambda row: _top_risk_driver_text(row, contribution_column_labels), axis=1
    )

    output_df = risk_df[RISK_OUTPUT_COLUMNS].copy()
    return output_df.sort_values("risk_score", ascending=False).reset_index(drop=True)


def risk_overview_metrics(project_risk_df: pd.DataFrame) -> dict[str, float | int]:
    _validate_dataframe(project_risk_df, RISK_OUTPUT_COLUMNS)

    if project_risk_df.empty:
        return {
            "project_count": 0,
            "high_risk_projects": 0,
            "medium_risk_projects": 0,
            "low_risk_projects": 0,
            "average_risk_score": 0.0,
            "high_risk_share": 0.0,
        }

    project_count = int(len(project_risk_df))
    high_risk_projects = int((project_risk_df["risk_level"] == "High").sum())
    medium_risk_projects = int((project_risk_df["risk_level"] == "Medium").sum())
    low_risk_projects = int((project_risk_df["risk_level"] == "Low").sum())

    return {
        "project_count": project_count,
        "high_risk_projects": high_risk_projects,
        "medium_risk_projects": medium_risk_projects,
        "low_risk_projects": low_risk_projects,
        "average_risk_score": float(project_risk_df["risk_score"].mean()),
        "high_risk_share": _safe_divide(high_risk_projects, project_count),
    }


def risk_city_breakdown(project_risk_df: pd.DataFrame) -> pd.DataFrame:
    _validate_dataframe(project_risk_df, RISK_OUTPUT_COLUMNS)

    if project_risk_df.empty:
        return pd.DataFrame(columns=CITY_RISK_COLUMNS)

    city_df = (
        project_risk_df.groupby("city", as_index=False)
        .agg(
            project_count=("project_name", "count"),
            average_risk_score=("risk_score", "mean"),
            high_risk_projects=("risk_level", lambda values: int((values == "High").sum())),
            medium_risk_projects=(
                "risk_level",
                lambda values: int((values == "Medium").sum()),
            ),
            low_risk_projects=("risk_level", lambda values: int((values == "Low").sum())),
            total_unsold_inventory=("unsold_inventory", "sum"),
            total_projected_sales=("projected_sales", "sum"),
            average_projected_demand_score=("projected_demand_score", "mean"),
        )
        .copy()
    )

    city_df["average_risk_score"] = city_df["average_risk_score"].round(1)
    city_df["average_projected_demand_score"] = city_df["average_projected_demand_score"].round(1)
    city_df["high_risk_share"] = city_df.apply(
        lambda row: _safe_divide(row["high_risk_projects"], row["project_count"]), axis=1
    )

    return city_df[CITY_RISK_COLUMNS].sort_values(
        by=["average_risk_score", "high_risk_share"],
        ascending=[False, False],
    ).reset_index(drop=True)


def risk_summary_insights(
    project_risk_df: pd.DataFrame, city_risk_df: pd.DataFrame
) -> dict[str, object]:
    _validate_dataframe(project_risk_df, RISK_OUTPUT_COLUMNS)
    _validate_dataframe(city_risk_df, CITY_RISK_COLUMNS)

    if project_risk_df.empty or city_risk_df.empty:
        return {
            "highest_risk_city": None,
            "highest_risk_project": None,
            "most_common_risk_drivers": [],
            "observations": [
                "No projects match the selected filters, so risk insights are unavailable."
            ],
        }

    highest_risk_city = city_risk_df.sort_values(
        by=["average_risk_score", "high_risk_share"],
        ascending=[False, False],
    ).iloc[0]
    highest_risk_project = project_risk_df.sort_values(
        by=["risk_score", "unsold_inventory"],
        ascending=[False, False],
    ).iloc[0]

    driver_counts = (
        project_risk_df["top_risk_drivers"]
        .dropna()
        .str.split(", ")
        .explode()
        .value_counts()
    )
    common_drivers = driver_counts.head(3).index.tolist()

    metrics = risk_overview_metrics(project_risk_df)
    observations = [
        (
            f"{metrics['high_risk_projects']:,.0f} out of {metrics['project_count']:,.0f} "
            f"projects are high risk ({metrics['high_risk_share']:.1%})."
        ),
        (
            f"{highest_risk_city['city']} shows the highest average risk score "
            f"({highest_risk_city['average_risk_score']:.1f}) with "
            f"{highest_risk_city['high_risk_projects']} high-risk projects."
        ),
    ]

    return {
        "highest_risk_city": highest_risk_city.to_dict(),
        "highest_risk_project": highest_risk_project.to_dict(),
        "most_common_risk_drivers": common_drivers,
        "observations": observations,
    }
