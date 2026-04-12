from collections.abc import Iterable

import pandas as pd

CORE_KPI_REQUIRED_COLUMNS = [
    "leads",
    "qualified_leads",
    "sales",
    "unsold_inventory",
    "avg_price",
    "visits",
    "reservations",
]

MARKETING_METRIC_REQUIRED_COLUMNS = [
    "ad_spend",
    "leads",
    "qualified_leads",
    "visits",
    "reservations",
    "sales",
]

MARKETING_GROUP_REQUIRED_COLUMNS = [
    "project_name",
    "city",
    "neighborhood",
    "property_type",
]

MARKETING_AGGREGATION_COLUMNS = [
    "ad_spend",
    "leads",
    "qualified_leads",
    "visits",
    "reservations",
    "sales",
]

MARKETING_OUTPUT_COLUMNS = [
    "cost_per_lead",
    "cost_per_qualified_lead",
    "qualified_lead_rate",
    "lead_to_visit_rate",
    "visit_to_reservation_rate",
    "reservation_to_sale_rate",
    "marketing_efficiency_score",
    "marketing_performance",
]


def _validate_dataframe(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    if df is None:
        raise ValueError("Input DataFrame is None.")

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns for KPI calculation: {missing_text}")


def _get_numeric_series(df: pd.DataFrame, column_name: str) -> pd.Series:
    _validate_dataframe(df, [column_name])

    if df.empty:
        return pd.Series(dtype="float64")

    return pd.to_numeric(df[column_name], errors="coerce").fillna(0.0)


def _safe_divide(numerator: float | int, denominator: float | int) -> float:
    numerator_value = float(numerator)
    denominator_value = float(denominator)
    if denominator_value == 0:
        return 0.0
    return numerator_value / denominator_value


def _safe_divide_series(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    numerator_values = pd.to_numeric(numerator, errors="coerce").fillna(0.0)
    denominator_values = pd.to_numeric(denominator, errors="coerce").fillna(0.0)

    result = pd.Series(0.0, index=numerator_values.index, dtype="float64")
    valid_denominator = denominator_values != 0
    result.loc[valid_denominator] = (
        numerator_values.loc[valid_denominator] / denominator_values.loc[valid_denominator]
    )
    return result


def total_leads(df: pd.DataFrame) -> int:
    return int(_get_numeric_series(df, "leads").sum())


def total_qualified_leads(df: pd.DataFrame) -> int:
    return int(_get_numeric_series(df, "qualified_leads").sum())


def qualified_lead_rate(df: pd.DataFrame) -> float:
    leads = total_leads(df)
    if leads == 0:
        return 0.0
    return _safe_divide(total_qualified_leads(df), leads)


def total_sales(df: pd.DataFrame) -> int:
    return int(_get_numeric_series(df, "sales").sum())


def total_unsold_inventory(df: pd.DataFrame) -> int:
    return int(_get_numeric_series(df, "unsold_inventory").sum())


def average_property_price(df: pd.DataFrame) -> float:
    prices = _get_numeric_series(df, "avg_price")
    if prices.empty:
        return 0.0
    return float(prices.mean())


def total_ad_spend(df: pd.DataFrame) -> float:
    return float(_get_numeric_series(df, "ad_spend").sum())


def cost_per_lead(df: pd.DataFrame) -> float:
    return _safe_divide(total_ad_spend(df), total_leads(df))


def cost_per_qualified_lead(df: pd.DataFrame) -> float:
    return _safe_divide(total_ad_spend(df), total_qualified_leads(df))


def lead_to_visit_rate(df: pd.DataFrame) -> float:
    return _safe_divide(_get_numeric_series(df, "visits").sum(), total_leads(df))


def visit_to_reservation_rate(df: pd.DataFrame) -> float:
    visits = int(_get_numeric_series(df, "visits").sum())
    if visits == 0:
        return 0.0

    reservations = int(_get_numeric_series(df, "reservations").sum())
    return _safe_divide(reservations, visits)


def reservation_to_sale_rate(df: pd.DataFrame) -> float:
    reservations = int(_get_numeric_series(df, "reservations").sum())
    if reservations == 0:
        return 0.0

    return _safe_divide(total_sales(df), reservations)


def calculate_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    _validate_dataframe(df, CORE_KPI_REQUIRED_COLUMNS)

    return {
        "total_leads": total_leads(df),
        "total_qualified_leads": total_qualified_leads(df),
        "qualified_lead_rate": qualified_lead_rate(df),
        "total_sales": total_sales(df),
        "total_unsold_inventory": total_unsold_inventory(df),
        "average_property_price": average_property_price(df),
        "visit_to_reservation_rate": visit_to_reservation_rate(df),
    }


def calculate_marketing_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    _validate_dataframe(df, MARKETING_METRIC_REQUIRED_COLUMNS)

    return {
        "total_ad_spend": total_ad_spend(df),
        "total_leads": total_leads(df),
        "total_qualified_leads": total_qualified_leads(df),
        "cost_per_lead": cost_per_lead(df),
        "cost_per_qualified_lead": cost_per_qualified_lead(df),
        "qualified_lead_rate": qualified_lead_rate(df),
        "lead_to_visit_rate": lead_to_visit_rate(df),
        "visit_to_reservation_rate": visit_to_reservation_rate(df),
        "reservation_to_sale_rate": reservation_to_sale_rate(df),
    }


def _empty_marketing_breakdown(group_by: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=group_by + MARKETING_AGGREGATION_COLUMNS + MARKETING_OUTPUT_COLUMNS)


def _add_marketing_performance_band(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    scores = df["marketing_efficiency_score"]
    df = df.copy()
    df["marketing_performance"] = "Average"

    if scores.nunique() <= 1:
        return df

    strong_threshold = float(scores.quantile(0.67))
    weak_threshold = float(scores.quantile(0.33))
    df.loc[scores >= strong_threshold, "marketing_performance"] = "Strong"
    df.loc[scores <= weak_threshold, "marketing_performance"] = "Weak"
    return df


def _aggregate_marketing_breakdown(df: pd.DataFrame, group_by: list[str]) -> pd.DataFrame:
    required_columns = MARKETING_METRIC_REQUIRED_COLUMNS + group_by
    _validate_dataframe(df, required_columns)

    if df.empty:
        return _empty_marketing_breakdown(group_by)

    grouped = (
        df.groupby(group_by, dropna=False, as_index=False)[MARKETING_AGGREGATION_COLUMNS]
        .sum()
        .copy()
    )

    grouped["cost_per_lead"] = _safe_divide_series(grouped["ad_spend"], grouped["leads"])
    grouped["cost_per_qualified_lead"] = _safe_divide_series(
        grouped["ad_spend"], grouped["qualified_leads"]
    )
    grouped["qualified_lead_rate"] = _safe_divide_series(
        grouped["qualified_leads"], grouped["leads"]
    )
    grouped["lead_to_visit_rate"] = _safe_divide_series(grouped["visits"], grouped["leads"])
    grouped["visit_to_reservation_rate"] = _safe_divide_series(
        grouped["reservations"], grouped["visits"]
    )
    grouped["reservation_to_sale_rate"] = _safe_divide_series(
        grouped["sales"], grouped["reservations"]
    )

    grouped["marketing_efficiency_score"] = (
        grouped["qualified_lead_rate"] * 0.45
        + grouped["lead_to_visit_rate"] * 0.2
        + grouped["visit_to_reservation_rate"] * 0.2
        + grouped["reservation_to_sale_rate"] * 0.15
    )
    grouped = _add_marketing_performance_band(grouped)

    return grouped[group_by + MARKETING_AGGREGATION_COLUMNS + MARKETING_OUTPUT_COLUMNS]


def project_marketing_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    breakdown_df = _aggregate_marketing_breakdown(
        df, ["project_name", "city", "neighborhood", "property_type"]
    )
    if breakdown_df.empty:
        return breakdown_df

    return breakdown_df.sort_values(
        by=[
            "marketing_efficiency_score",
            "qualified_lead_rate",
            "cost_per_qualified_lead",
        ],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def city_marketing_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    breakdown_df = _aggregate_marketing_breakdown(df, ["city"])
    if breakdown_df.empty:
        return breakdown_df

    return breakdown_df.sort_values(
        by=["qualified_lead_rate", "cost_per_qualified_lead"],
        ascending=[False, True],
    ).reset_index(drop=True)


def property_type_marketing_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    breakdown_df = _aggregate_marketing_breakdown(df, ["property_type"])
    if breakdown_df.empty:
        return breakdown_df

    return breakdown_df.sort_values(
        by=["qualified_lead_rate", "cost_per_qualified_lead"],
        ascending=[False, True],
    ).reset_index(drop=True)


def marketing_summary_insights(df: pd.DataFrame) -> dict[str, object]:
    _validate_dataframe(df, MARKETING_METRIC_REQUIRED_COLUMNS + MARKETING_GROUP_REQUIRED_COLUMNS)

    if df.empty:
        return {
            "strongest_city": None,
            "weakest_city": None,
            "strongest_project": None,
            "weakest_project": None,
            "observations": [
                "No data is available for the selected filters, so no marketing summary can be generated."
            ],
        }

    city_df = city_marketing_breakdown(df)
    project_df = project_marketing_breakdown(df)

    strongest_city = city_df.sort_values(
        by=["qualified_lead_rate", "cost_per_qualified_lead"],
        ascending=[False, True],
    ).iloc[0]
    weakest_city = city_df.sort_values(
        by=["qualified_lead_rate", "cost_per_qualified_lead"],
        ascending=[True, False],
    ).iloc[0]

    strongest_project = project_df.sort_values(
        by=["marketing_efficiency_score", "cost_per_qualified_lead"],
        ascending=[False, True],
    ).iloc[0]
    weakest_project = project_df.sort_values(
        by=["marketing_efficiency_score", "cost_per_qualified_lead"],
        ascending=[True, False],
    ).iloc[0]

    lead_threshold = float(project_df["leads"].quantile(0.75))
    conversion_median = float(project_df["reservation_to_sale_rate"].median())
    high_lead_low_conversion = project_df[
        (project_df["leads"] >= lead_threshold)
        & (project_df["reservation_to_sale_rate"] <= conversion_median)
    ]

    best_cpql_city = city_df.sort_values("cost_per_qualified_lead", ascending=True).iloc[0]
    worst_cpql_city = city_df.sort_values("cost_per_qualified_lead", ascending=False).iloc[0]

    observations: list[str] = [
        (
            "Lead quality differs materially by city: "
            f"{strongest_city['city']} converts {strongest_city['qualified_lead_rate']:.1%} "
            "of leads into qualified demand, while "
            f"{weakest_city['city']} converts {weakest_city['qualified_lead_rate']:.1%}."
        ),
        (
            "Spend efficiency spread is notable: "
            f"{best_cpql_city['city']} has the lowest cost per qualified lead "
            f"(TND {best_cpql_city['cost_per_qualified_lead']:,.0f}) versus "
            f"{worst_cpql_city['city']} at TND {worst_cpql_city['cost_per_qualified_lead']:,.0f}."
        ),
    ]

    if not high_lead_low_conversion.empty:
        highlighted_project = high_lead_low_conversion.sort_values(
            by=["leads", "reservation_to_sale_rate"],
            ascending=[False, True],
        ).iloc[0]
        observations.append(
            (
                f"{highlighted_project['project_name']} draws strong traffic "
                f"({highlighted_project['leads']:,.0f} leads) but closes only "
                f"{highlighted_project['reservation_to_sale_rate']:.1%} of reservations into sales."
            )
        )

    return {
        "strongest_city": strongest_city.to_dict(),
        "weakest_city": weakest_city.to_dict(),
        "strongest_project": strongest_project.to_dict(),
        "weakest_project": weakest_project.to_dict(),
        "observations": observations,
    }
