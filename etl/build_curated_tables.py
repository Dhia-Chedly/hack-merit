"""Build curated analytics-ready tables from processed ETL outputs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

try:
    from .config import CURATED_DIR, PROCESSED_DIR, campaign_dates, ensure_data_directories
except ImportError:  # pragma: no cover - local execution fallback
    from config import CURATED_DIR, PROCESSED_DIR, campaign_dates, ensure_data_directories  # type: ignore


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
    if values.empty:
        return values
    min_value = float(values.min())
    max_value = float(values.max())
    if max_value - min_value == 0:
        return pd.Series(0.5, index=values.index, dtype="float64")
    return (values - min_value) / (max_value - min_value)


def load_processed_tables(processed_dir: Path = PROCESSED_DIR) -> dict[str, pd.DataFrame]:
    tables = {
        "projects": pd.read_csv(processed_dir / "projects.csv", parse_dates=["launch_date"]),
        "campaigns": pd.read_csv(processed_dir / "campaigns.csv", parse_dates=["campaign_date"]),
        "leads": pd.read_csv(processed_dir / "leads.csv", parse_dates=["lead_date"]),
        "visits": pd.read_csv(
            processed_dir / "visits.csv", parse_dates=["visit_date", "reservation_date"]
        ),
        "sales": pd.read_csv(processed_dir / "sales.csv", parse_dates=["sale_date"]),
    }
    return tables


def build_project_metrics(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    projects = tables["projects"].copy()
    campaigns = tables["campaigns"].copy()
    leads = tables["leads"].copy()
    visits = tables["visits"].copy()
    sales = tables["sales"].copy()

    spend_df = (
        campaigns.groupby("project_id", as_index=False)
        .agg(
            spend=("spend", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
        )
        .copy()
    )

    leads_df = (
        leads.groupby("project_id", as_index=False)
        .agg(
            total_leads=("lead_id", "count"),
            qualified_leads=("is_qualified", "sum"),
        )
        .copy()
    )

    visits_df = (
        visits.groupby("project_id", as_index=False)
        .agg(
            visits=("visit_id", "count"),
            reservations=("is_reservation", "sum"),
        )
        .copy()
    )

    sales_df = (
        sales.groupby("project_id", as_index=False)
        .agg(
            sales=("sale_id", "count"),
            revenue=("sale_price", "sum"),
            avg_sale_price=("sale_price", "mean"),
        )
        .copy()
    )

    project_metrics = (
        projects.merge(spend_df, on="project_id", how="left")
        .merge(leads_df, on="project_id", how="left")
        .merge(visits_df, on="project_id", how="left")
        .merge(sales_df, on="project_id", how="left")
    )

    fill_zero_cols = [
        "spend",
        "impressions",
        "clicks",
        "total_leads",
        "qualified_leads",
        "visits",
        "reservations",
        "sales",
        "revenue",
    ]
    for column in fill_zero_cols:
        project_metrics[column] = pd.to_numeric(project_metrics[column], errors="coerce").fillna(0)

    project_metrics["avg_sale_price"] = pd.to_numeric(
        project_metrics["avg_sale_price"], errors="coerce"
    ).fillna(project_metrics["avg_price"])

    project_metrics["qualified_lead_rate"] = _safe_divide_series(
        project_metrics["qualified_leads"], project_metrics["total_leads"]
    )
    project_metrics["lead_to_visit_rate"] = _safe_divide_series(
        project_metrics["visits"], project_metrics["total_leads"]
    )
    project_metrics["visit_to_reservation_rate"] = _safe_divide_series(
        project_metrics["reservations"], project_metrics["visits"]
    )
    project_metrics["reservation_to_sale_rate"] = _safe_divide_series(
        project_metrics["sales"], project_metrics["reservations"]
    )

    project_metrics["cpl"] = _safe_divide_series(
        project_metrics["spend"], project_metrics["total_leads"]
    )
    project_metrics["cpql"] = _safe_divide_series(
        project_metrics["spend"], project_metrics["qualified_leads"]
    )

    project_metrics["unsold_inventory"] = (
        project_metrics["total_units"] - project_metrics["sales"]
    ).clip(lower=0)
    project_metrics["sell_through_rate"] = _safe_divide_series(
        project_metrics["sales"], project_metrics["total_units"]
    )

    ordered_columns = [
        "project_id",
        "project_name",
        "city",
        "neighborhood",
        "latitude",
        "longitude",
        "property_type",
        "quality_tier",
        "launch_date",
        "total_units",
        "avg_price",
        "total_leads",
        "qualified_leads",
        "qualified_lead_rate",
        "visits",
        "reservations",
        "sales",
        "spend",
        "cpl",
        "cpql",
        "lead_to_visit_rate",
        "visit_to_reservation_rate",
        "reservation_to_sale_rate",
        "revenue",
        "avg_sale_price",
        "unsold_inventory",
        "sell_through_rate",
    ]

    project_metrics = project_metrics[ordered_columns].copy()
    project_metrics = project_metrics.sort_values(by=["city", "project_name"]).reset_index(drop=True)

    return project_metrics


def build_city_metrics(project_metrics: pd.DataFrame) -> pd.DataFrame:
    city_metrics = (
        project_metrics.groupby("city", as_index=False)
        .agg(
            project_count=("project_id", "count"),
            total_units=("total_units", "sum"),
            unsold_inventory=("unsold_inventory", "sum"),
            spend=("spend", "sum"),
            total_leads=("total_leads", "sum"),
            qualified_leads=("qualified_leads", "sum"),
            visits=("visits", "sum"),
            reservations=("reservations", "sum"),
            sales=("sales", "sum"),
            revenue=("revenue", "sum"),
            avg_price=("avg_price", "mean"),
        )
        .copy()
    )

    city_metrics["qualified_lead_rate"] = _safe_divide_series(
        city_metrics["qualified_leads"], city_metrics["total_leads"]
    )
    city_metrics["lead_to_visit_rate"] = _safe_divide_series(
        city_metrics["visits"], city_metrics["total_leads"]
    )
    city_metrics["visit_to_reservation_rate"] = _safe_divide_series(
        city_metrics["reservations"], city_metrics["visits"]
    )
    city_metrics["reservation_to_sale_rate"] = _safe_divide_series(
        city_metrics["sales"], city_metrics["reservations"]
    )
    city_metrics["cpl"] = _safe_divide_series(city_metrics["spend"], city_metrics["total_leads"])
    city_metrics["cpql"] = _safe_divide_series(
        city_metrics["spend"], city_metrics["qualified_leads"]
    )
    city_metrics["sell_through_rate"] = _safe_divide_series(
        city_metrics["sales"], city_metrics["total_units"]
    )

    city_metrics = city_metrics.sort_values(by="sales", ascending=False).reset_index(drop=True)
    return city_metrics


def _weekly_period_start(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values, errors="coerce").dt.to_period("W-SUN").dt.start_time


def build_project_timeseries(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    projects = tables["projects"].copy()
    campaigns = tables["campaigns"].copy()
    leads = tables["leads"].copy()
    visits = tables["visits"].copy()
    sales = tables["sales"].copy()

    weekly_periods = pd.DatetimeIndex(campaign_dates())
    base = projects[["project_id", "project_name", "city", "property_type", "total_units"]].copy()
    base = base.assign(key=1).merge(
        pd.DataFrame({"period_start": weekly_periods, "key": 1}), on="key", how="inner"
    )
    base = base.drop(columns=["key"])

    campaign_weekly = campaigns.copy()
    campaign_weekly["period_start"] = _weekly_period_start(campaign_weekly["campaign_date"])
    campaign_weekly = (
        campaign_weekly.groupby(["project_id", "period_start"], as_index=False)
        .agg(
            spend=("spend", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            attributed_leads=("attributed_leads", "sum"),
        )
        .copy()
    )

    leads_weekly = leads.copy()
    leads_weekly["period_start"] = _weekly_period_start(leads_weekly["lead_date"])
    leads_weekly = (
        leads_weekly.groupby(["project_id", "period_start"], as_index=False)
        .agg(leads=("lead_id", "count"), qualified_leads=("is_qualified", "sum"))
        .copy()
    )

    visits_weekly = visits.copy()
    visits_weekly["period_start"] = _weekly_period_start(visits_weekly["visit_date"])
    visits_weekly = (
        visits_weekly.groupby(["project_id", "period_start"], as_index=False)
        .agg(visits=("visit_id", "count"), reservations=("is_reservation", "sum"))
        .copy()
    )

    sales_weekly = sales.copy()
    if sales_weekly.empty:
        sales_weekly = pd.DataFrame(columns=["project_id", "period_start", "sales", "revenue"])
    else:
        sales_weekly["period_start"] = _weekly_period_start(sales_weekly["sale_date"])
        sales_weekly = (
            sales_weekly.groupby(["project_id", "period_start"], as_index=False)
            .agg(sales=("sale_id", "count"), revenue=("sale_price", "sum"))
            .copy()
        )

    ts = (
        base.merge(campaign_weekly, on=["project_id", "period_start"], how="left")
        .merge(leads_weekly, on=["project_id", "period_start"], how="left")
        .merge(visits_weekly, on=["project_id", "period_start"], how="left")
        .merge(sales_weekly, on=["project_id", "period_start"], how="left")
    )

    fill_zero_cols = [
        "spend",
        "impressions",
        "clicks",
        "attributed_leads",
        "leads",
        "qualified_leads",
        "visits",
        "reservations",
        "sales",
        "revenue",
    ]
    for column in fill_zero_cols:
        ts[column] = pd.to_numeric(ts[column], errors="coerce").fillna(0)

    ts["cpl"] = _safe_divide_series(ts["spend"], ts["leads"])
    ts["cpql"] = _safe_divide_series(ts["spend"], ts["qualified_leads"])
    ts["qualified_lead_rate"] = _safe_divide_series(ts["qualified_leads"], ts["leads"])
    ts["lead_to_visit_rate"] = _safe_divide_series(ts["visits"], ts["leads"])
    ts["visit_to_reservation_rate"] = _safe_divide_series(ts["reservations"], ts["visits"])
    ts["reservation_to_sale_rate"] = _safe_divide_series(ts["sales"], ts["reservations"])

    ts = ts.sort_values(by=["project_id", "period_start"]).reset_index(drop=True)
    ts["cumulative_sales"] = ts.groupby("project_id")["sales"].cumsum()
    ts["unsold_inventory"] = (ts["total_units"] - ts["cumulative_sales"]).clip(lower=0)

    return ts


def build_forecast_base(
    project_metrics: pd.DataFrame,
    project_timeseries: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for project_id, group in project_timeseries.groupby("project_id"):
        g = group.sort_values("period_start").reset_index(drop=True)
        if g.empty:
            continue

        last_4 = g.tail(4)
        prev_4 = g.iloc[-8:-4] if len(g) >= 8 else g.iloc[:-4]

        leads_last_4 = float(last_4["leads"].sum())
        leads_prev_4 = float(prev_4["leads"].sum()) if not prev_4.empty else 0.0
        sales_last_4 = float(last_4["sales"].sum())
        sales_prev_4 = float(prev_4["sales"].sum()) if not prev_4.empty else 0.0

        qualified_last_4 = float(last_4["qualified_leads"].sum())
        visits_last_4 = float(last_4["visits"].sum())
        reservations_last_4 = float(last_4["reservations"].sum())
        spend_last_4 = float(last_4["spend"].sum())

        row = {
            "project_id": project_id,
            "city": str(g.iloc[-1]["city"]),
            "property_type": str(g.iloc[-1]["property_type"]),
            "latest_period": pd.Timestamp(g.iloc[-1]["period_start"]),
            "leads_last_4w": leads_last_4,
            "leads_prev_4w": leads_prev_4,
            "sales_last_4w": sales_last_4,
            "sales_prev_4w": sales_prev_4,
            "spend_last_4w": spend_last_4,
            "qualified_lead_rate_last_4w": _safe_divide(qualified_last_4, leads_last_4),
            "lead_to_visit_rate_last_4w": _safe_divide(visits_last_4, leads_last_4),
            "visit_to_reservation_rate_last_4w": _safe_divide(reservations_last_4, visits_last_4),
            "reservation_to_sale_rate_last_4w": _safe_divide(sales_last_4, reservations_last_4),
            "leads_growth_4w": _safe_divide(leads_last_4 - leads_prev_4, max(leads_prev_4, 1.0)),
            "sales_growth_4w": _safe_divide(sales_last_4 - sales_prev_4, max(sales_prev_4, 1.0)),
            "current_unsold_inventory": float(g.iloc[-1]["unsold_inventory"]),
            "current_total_units": float(g.iloc[-1]["total_units"]),
        }
        rows.append(row)

    forecast_base = pd.DataFrame(rows)

    if forecast_base.empty:
        return forecast_base

    forecast_base = forecast_base.merge(
        project_metrics[
            [
                "project_id",
                "project_name",
                "quality_tier",
                "avg_price",
                "total_units",
                "unsold_inventory",
            ]
        ],
        on="project_id",
        how="left",
    )

    forecast_base["inventory_pressure"] = _safe_divide_series(
        forecast_base["current_unsold_inventory"], forecast_base["current_total_units"]
    )

    volume_component = _normalize_series(forecast_base["leads_last_4w"])
    quality_component = forecast_base["qualified_lead_rate_last_4w"].clip(lower=0, upper=1)
    visit_component = forecast_base["lead_to_visit_rate_last_4w"].clip(lower=0, upper=1)
    reservation_component = forecast_base["visit_to_reservation_rate_last_4w"].clip(lower=0, upper=1)
    growth_component = ((forecast_base["sales_growth_4w"].clip(-1, 1) + 1) / 2).clip(0, 1)
    inventory_component = (1 - forecast_base["inventory_pressure"].clip(0, 1)).clip(0, 1)

    forecast_base["demand_momentum_score"] = (
        100
        * (
            0.24 * volume_component
            + 0.21 * quality_component
            + 0.17 * visit_component
            + 0.15 * reservation_component
            + 0.13 * growth_component
            + 0.10 * inventory_component
        )
    ).round(1)

    score_factor = forecast_base["demand_momentum_score"] / 100
    forecast_base["projected_leads_baseline"] = (
        forecast_base["leads_last_4w"] * (1 + 0.35 * (score_factor - 0.5))
    ).clip(lower=0)
    forecast_base["projected_sales_baseline"] = (
        forecast_base["sales_last_4w"] * (1 + 0.45 * (score_factor - 0.5))
    ).clip(lower=0)

    forecast_base["projected_leads_baseline"] = forecast_base["projected_leads_baseline"].round(0)
    forecast_base["projected_sales_baseline"] = forecast_base["projected_sales_baseline"].round(0)

    ordered_columns = [
        "project_id",
        "project_name",
        "city",
        "property_type",
        "quality_tier",
        "avg_price",
        "latest_period",
        "leads_last_4w",
        "leads_prev_4w",
        "leads_growth_4w",
        "sales_last_4w",
        "sales_prev_4w",
        "sales_growth_4w",
        "spend_last_4w",
        "qualified_lead_rate_last_4w",
        "lead_to_visit_rate_last_4w",
        "visit_to_reservation_rate_last_4w",
        "reservation_to_sale_rate_last_4w",
        "current_unsold_inventory",
        "inventory_pressure",
        "demand_momentum_score",
        "projected_leads_baseline",
        "projected_sales_baseline",
    ]

    forecast_base = forecast_base[ordered_columns].sort_values(
        by=["demand_momentum_score", "projected_sales_baseline"], ascending=[False, False]
    )
    forecast_base = forecast_base.reset_index(drop=True)

    return forecast_base


def build_risk_base(project_metrics: pd.DataFrame, forecast_base: pd.DataFrame) -> pd.DataFrame:
    risk_base = project_metrics.merge(
        forecast_base[
            [
                "project_id",
                "demand_momentum_score",
                "projected_sales_baseline",
                "sales_growth_4w",
                "leads_growth_4w",
                "inventory_pressure",
            ]
        ],
        on="project_id",
        how="left",
    )

    risk_base["demand_momentum_score"] = risk_base["demand_momentum_score"].fillna(50.0)
    risk_base["projected_sales_baseline"] = risk_base["projected_sales_baseline"].fillna(0)
    risk_base["sales_growth_4w"] = risk_base["sales_growth_4w"].fillna(0)
    risk_base["leads_growth_4w"] = risk_base["leads_growth_4w"].fillna(0)
    risk_base["inventory_pressure"] = risk_base["inventory_pressure"].fillna(
        _safe_divide_series(risk_base["unsold_inventory"], risk_base["total_units"])
    )

    cpql_norm = _normalize_series(risk_base["cpql"])
    weak_quality = 1 - risk_base["qualified_lead_rate"].clip(0, 1)
    weak_lead_to_visit = 1 - risk_base["lead_to_visit_rate"].clip(0, 1)
    weak_visit_to_res = 1 - risk_base["visit_to_reservation_rate"].clip(0, 1)
    weak_sale_close = 1 - risk_base["reservation_to_sale_rate"].clip(0, 1)
    weak_forecast = 1 - (risk_base["demand_momentum_score"].clip(0, 100) / 100)

    risk_base["risk_pressure_proxy"] = (
        100
        * (
            0.19 * weak_quality
            + 0.19 * cpql_norm
            + 0.14 * weak_lead_to_visit
            + 0.14 * weak_visit_to_res
            + 0.10 * weak_sale_close
            + 0.14 * risk_base["inventory_pressure"].clip(0, 1)
            + 0.10 * weak_forecast
        )
    ).round(1)

    ordered_columns = [
        "project_id",
        "project_name",
        "city",
        "property_type",
        "quality_tier",
        "avg_price",
        "spend",
        "total_leads",
        "qualified_leads",
        "qualified_lead_rate",
        "cpl",
        "cpql",
        "lead_to_visit_rate",
        "visit_to_reservation_rate",
        "reservation_to_sale_rate",
        "sales",
        "unsold_inventory",
        "total_units",
        "inventory_pressure",
        "demand_momentum_score",
        "projected_sales_baseline",
        "sales_growth_4w",
        "leads_growth_4w",
        "risk_pressure_proxy",
    ]

    risk_base = risk_base[ordered_columns].sort_values(
        by=["risk_pressure_proxy", "unsold_inventory"], ascending=[False, False]
    )
    risk_base = risk_base.reset_index(drop=True)

    return risk_base


def _save_curated_table(df: pd.DataFrame, curated_dir: Path, file_name: str) -> None:
    output_path = curated_dir / file_name
    df.to_csv(output_path, index=False)
    print(f"[build_curated_tables] Saved {file_name}: {len(df):,} rows -> {output_path}")


def build_curated_tables(processed_dir: Path = PROCESSED_DIR, curated_dir: Path = CURATED_DIR) -> dict[str, pd.DataFrame]:
    ensure_data_directories()

    print("[build_curated_tables] Loading processed tables...")
    tables = load_processed_tables(processed_dir=processed_dir)

    project_metrics = build_project_metrics(tables)
    city_metrics = build_city_metrics(project_metrics)
    project_timeseries = build_project_timeseries(tables)
    forecast_base = build_forecast_base(project_metrics, project_timeseries)
    risk_base = build_risk_base(project_metrics, forecast_base)

    curated_tables = {
        "project_metrics": project_metrics,
        "city_metrics": city_metrics,
        "project_timeseries": project_timeseries,
        "forecast_base": forecast_base,
        "risk_base": risk_base,
    }

    print("[build_curated_tables] Writing curated tables...")
    _save_curated_table(project_metrics, curated_dir, "project_metrics.csv")
    _save_curated_table(city_metrics, curated_dir, "city_metrics.csv")
    _save_curated_table(project_timeseries, curated_dir, "project_timeseries.csv")
    _save_curated_table(forecast_base, curated_dir, "forecast_base.csv")
    _save_curated_table(risk_base, curated_dir, "risk_base.csv")

    return curated_tables


def main() -> None:
    build_curated_tables()


if __name__ == "__main__":
    main()
