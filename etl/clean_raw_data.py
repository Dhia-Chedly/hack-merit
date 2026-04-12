"""Clean, validate, and enforce business rules on synthetic raw tables."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

try:
    from .config import PROCESSED_DIR, RAW_DIR, ensure_data_directories
except ImportError:  # pragma: no cover - local execution fallback
    from config import PROCESSED_DIR, RAW_DIR, ensure_data_directories  # type: ignore


PRIMARY_KEYS = {
    "projects": "project_id",
    "campaigns": "campaign_id",
    "leads": "lead_id",
    "visits": "visit_id",
    "sales": "sale_id",
}

RAW_FILES = {
    "projects": "projects.csv",
    "campaigns": "campaigns.csv",
    "leads": "leads.csv",
    "visits": "visits.csv",
    "sales": "sales.csv",
}


def _record_issue(
    issues: list[dict[str, Any]],
    table: str,
    check: str,
    affected_rows: int,
    action: str,
) -> None:
    issues.append(
        {
            "table": table,
            "check": check,
            "affected_rows": int(affected_rows),
            "action": action,
        }
    )


def _read_table(path: Path, date_columns: list[str] | None = None) -> pd.DataFrame:
    if date_columns:
        return pd.read_csv(path, parse_dates=date_columns)
    return pd.read_csv(path)


def load_raw_tables(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    tables = {
        "projects": _read_table(raw_dir / RAW_FILES["projects"], date_columns=["launch_date"]),
        "campaigns": _read_table(
            raw_dir / RAW_FILES["campaigns"], date_columns=["campaign_date"]
        ),
        "leads": _read_table(raw_dir / RAW_FILES["leads"], date_columns=["lead_date"]),
        "visits": _read_table(
            raw_dir / RAW_FILES["visits"], date_columns=["visit_date", "reservation_date"]
        ),
        "sales": _read_table(raw_dir / RAW_FILES["sales"], date_columns=["sale_date"]),
    }
    return tables


def _deduplicate_primary_key(
    table_name: str,
    df: pd.DataFrame,
    issues: list[dict[str, Any]],
) -> pd.DataFrame:
    primary_key = PRIMARY_KEYS[table_name]
    duplicate_count = int(df[primary_key].duplicated().sum())
    if duplicate_count:
        _record_issue(
            issues,
            table_name,
            f"duplicate {primary_key}",
            duplicate_count,
            "kept first occurrence",
        )
        df = df.drop_duplicates(subset=[primary_key], keep="first")
    return df


def _to_datetime(df: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_datetime(df[column], errors="coerce")


def _to_numeric(df: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    values = pd.to_numeric(df[column], errors="coerce")
    return values.fillna(default)


def _clean_projects(projects: pd.DataFrame, issues: list[dict[str, Any]]) -> pd.DataFrame:
    projects = projects.copy()
    projects.columns = [str(col).strip() for col in projects.columns]

    projects = _deduplicate_primary_key("projects", projects, issues)

    projects["launch_date"] = _to_datetime(projects, "launch_date")
    missing_launch = int(projects["launch_date"].isna().sum())
    if missing_launch:
        fallback_date = pd.Timestamp("2025-01-01")
        projects.loc[projects["launch_date"].isna(), "launch_date"] = fallback_date
        _record_issue(issues, "projects", "invalid launch_date", missing_launch, "filled default date")

    projects["latitude"] = pd.to_numeric(projects["latitude"], errors="coerce")
    projects["longitude"] = pd.to_numeric(projects["longitude"], errors="coerce")
    projects["avg_price"] = _to_numeric(projects, "avg_price")
    projects["total_units"] = _to_numeric(projects, "total_units")

    missing_geo = int(projects[["latitude", "longitude"]].isna().any(axis=1).sum())
    if missing_geo:
        projects = projects.dropna(subset=["latitude", "longitude"])
        _record_issue(issues, "projects", "missing latitude/longitude", missing_geo, "dropped")

    invalid_units = int((projects["total_units"] <= 0).sum())
    if invalid_units:
        projects = projects[projects["total_units"] > 0]
        _record_issue(issues, "projects", "non-positive total_units", invalid_units, "dropped")

    invalid_prices = int((projects["avg_price"] <= 0).sum())
    if invalid_prices:
        projects = projects[projects["avg_price"] > 0]
        _record_issue(issues, "projects", "non-positive avg_price", invalid_prices, "dropped")

    projects["total_units"] = projects["total_units"].round().astype("int64")
    projects["avg_price"] = projects["avg_price"].round(2)
    projects["latitude"] = projects["latitude"].round(6)
    projects["longitude"] = projects["longitude"].round(6)

    return projects.reset_index(drop=True)


def _clean_campaigns(
    campaigns: pd.DataFrame,
    projects: pd.DataFrame,
    issues: list[dict[str, Any]],
) -> pd.DataFrame:
    campaigns = campaigns.copy()
    campaigns.columns = [str(col).strip() for col in campaigns.columns]

    campaigns = _deduplicate_primary_key("campaigns", campaigns, issues)

    campaigns["campaign_date"] = _to_datetime(campaigns, "campaign_date")
    invalid_dates = int(campaigns["campaign_date"].isna().sum())
    if invalid_dates:
        campaigns = campaigns[campaigns["campaign_date"].notna()]
        _record_issue(issues, "campaigns", "invalid campaign_date", invalid_dates, "dropped")

    valid_projects = set(projects["project_id"])
    invalid_project_ids = int((~campaigns["project_id"].isin(valid_projects)).sum())
    if invalid_project_ids:
        campaigns = campaigns[campaigns["project_id"].isin(valid_projects)]
        _record_issue(
            issues,
            "campaigns",
            "project_id not found in projects",
            invalid_project_ids,
            "dropped",
        )

    for column in ["spend", "impressions", "clicks", "attributed_leads"]:
        campaigns[column] = _to_numeric(campaigns, column)

    negative_spend = int((campaigns["spend"] < 0).sum())
    if negative_spend:
        campaigns.loc[campaigns["spend"] < 0, "spend"] = 0.0
        _record_issue(issues, "campaigns", "negative spend", negative_spend, "clipped to 0")

    for column in ["impressions", "clicks", "attributed_leads"]:
        negatives = int((campaigns[column] < 0).sum())
        if negatives:
            campaigns.loc[campaigns[column] < 0, column] = 0
            _record_issue(issues, "campaigns", f"negative {column}", negatives, "clipped to 0")

    # Plausibility constraints within the marketing funnel.
    clicks_gt_impr = int((campaigns["clicks"] > campaigns["impressions"]).sum())
    if clicks_gt_impr:
        campaigns.loc[campaigns["clicks"] > campaigns["impressions"], "impressions"] = campaigns[
            "clicks"
        ]
        _record_issue(
            issues,
            "campaigns",
            "clicks > impressions",
            clicks_gt_impr,
            "set impressions equal to clicks",
        )

    leads_gt_clicks = int((campaigns["attributed_leads"] > campaigns["clicks"]).sum())
    if leads_gt_clicks:
        campaigns.loc[campaigns["attributed_leads"] > campaigns["clicks"], "attributed_leads"] = campaigns[
            "clicks"
        ]
        _record_issue(
            issues,
            "campaigns",
            "attributed_leads > clicks",
            leads_gt_clicks,
            "clipped to clicks",
        )

    campaigns["spend"] = campaigns["spend"].round(2)
    campaigns["impressions"] = campaigns["impressions"].round().astype("int64")
    campaigns["clicks"] = campaigns["clicks"].round().astype("int64")
    campaigns["attributed_leads"] = campaigns["attributed_leads"].round().astype("int64")

    return campaigns.reset_index(drop=True)


def _clean_leads(
    leads: pd.DataFrame,
    campaigns: pd.DataFrame,
    projects: pd.DataFrame,
    issues: list[dict[str, Any]],
) -> pd.DataFrame:
    leads = leads.copy()
    leads.columns = [str(col).strip() for col in leads.columns]

    leads = _deduplicate_primary_key("leads", leads, issues)

    leads["lead_date"] = _to_datetime(leads, "lead_date")
    invalid_dates = int(leads["lead_date"].isna().sum())
    if invalid_dates:
        leads = leads[leads["lead_date"].notna()]
        _record_issue(issues, "leads", "invalid lead_date", invalid_dates, "dropped")

    valid_campaigns = set(campaigns["campaign_id"])
    invalid_campaign_ids = int((~leads["campaign_id"].isin(valid_campaigns)).sum())
    if invalid_campaign_ids:
        leads = leads[leads["campaign_id"].isin(valid_campaigns)]
        _record_issue(
            issues,
            "leads",
            "campaign_id not found in campaigns",
            invalid_campaign_ids,
            "dropped",
        )

    valid_projects = set(projects["project_id"])
    invalid_project_ids = int((~leads["project_id"].isin(valid_projects)).sum())
    if invalid_project_ids:
        leads = leads[leads["project_id"].isin(valid_projects)]
        _record_issue(issues, "leads", "project_id not found in projects", invalid_project_ids, "dropped")

    # Enforce campaign-to-project consistency.
    campaign_project = campaigns[["campaign_id", "project_id"]].drop_duplicates()
    leads = leads.merge(
        campaign_project,
        on="campaign_id",
        how="left",
        suffixes=("", "_campaign"),
    )
    mismatch = leads["project_id"] != leads["project_id_campaign"]
    mismatch_count = int(mismatch.sum())
    if mismatch_count:
        leads = leads[~mismatch]
        _record_issue(
            issues,
            "leads",
            "lead project_id does not match campaign project_id",
            mismatch_count,
            "dropped",
        )
    leads = leads.drop(columns=["project_id_campaign"])

    for column in ["lead_score", "budget_tnd", "expected_purchase_days", "is_qualified"]:
        leads[column] = _to_numeric(leads, column)

    leads["lead_score"] = leads["lead_score"].clip(lower=0, upper=100).round(2)

    negative_budget = int((leads["budget_tnd"] <= 0).sum())
    if negative_budget:
        project_price = projects.set_index("project_id")["avg_price"].to_dict()
        leads.loc[leads["budget_tnd"] <= 0, "budget_tnd"] = leads.loc[
            leads["budget_tnd"] <= 0, "project_id"
        ].map(project_price) * 0.75
        _record_issue(
            issues,
            "leads",
            "non-positive budget_tnd",
            negative_budget,
            "replaced with 75% of project avg_price",
        )

    leads["expected_purchase_days"] = leads["expected_purchase_days"].clip(lower=1, upper=365)
    leads["is_qualified"] = (leads["is_qualified"] >= 1).astype("int64")
    leads["budget_tnd"] = leads["budget_tnd"].round(2)
    leads["expected_purchase_days"] = leads["expected_purchase_days"].round().astype("int64")

    return leads.reset_index(drop=True)


def _clean_visits(
    visits: pd.DataFrame,
    leads: pd.DataFrame,
    projects: pd.DataFrame,
    issues: list[dict[str, Any]],
) -> pd.DataFrame:
    visits = visits.copy()
    visits.columns = [str(col).strip() for col in visits.columns]

    visits = _deduplicate_primary_key("visits", visits, issues)

    visits["visit_date"] = _to_datetime(visits, "visit_date")
    visits["reservation_date"] = _to_datetime(visits, "reservation_date")

    invalid_visit_dates = int(visits["visit_date"].isna().sum())
    if invalid_visit_dates:
        visits = visits[visits["visit_date"].notna()]
        _record_issue(issues, "visits", "invalid visit_date", invalid_visit_dates, "dropped")

    valid_leads = set(leads["lead_id"])
    invalid_lead_ids = int((~visits["lead_id"].isin(valid_leads)).sum())
    if invalid_lead_ids:
        visits = visits[visits["lead_id"].isin(valid_leads)]
        _record_issue(issues, "visits", "lead_id not found in leads", invalid_lead_ids, "dropped")

    lead_project = leads[["lead_id", "project_id", "lead_date"]].rename(
        columns={"project_id": "lead_project_id"}
    )
    visits = visits.merge(lead_project, on="lead_id", how="left")

    mismatch = visits["project_id"] != visits["lead_project_id"]
    mismatch_count = int(mismatch.sum())
    if mismatch_count:
        visits = visits[~mismatch]
        _record_issue(
            issues,
            "visits",
            "visit project_id does not match lead project_id",
            mismatch_count,
            "dropped",
        )

    visits["is_reservation"] = (_to_numeric(visits, "is_reservation") >= 1).astype("int64")

    # Ensure visit date happens after lead date.
    before_lead = visits["visit_date"] < visits["lead_date"]
    before_lead_count = int(before_lead.sum())
    if before_lead_count:
        visits.loc[before_lead, "visit_date"] = visits.loc[before_lead, "lead_date"] + pd.Timedelta(
            days=1
        )
        _record_issue(
            issues,
            "visits",
            "visit_date before lead_date",
            before_lead_count,
            "shifted to lead_date + 1 day",
        )

    missing_res_date = (visits["is_reservation"] == 1) & (visits["reservation_date"].isna())
    missing_res_count = int(missing_res_date.sum())
    if missing_res_count:
        visits.loc[missing_res_date, "reservation_date"] = visits.loc[
            missing_res_date, "visit_date"
        ] + pd.Timedelta(days=2)
        _record_issue(
            issues,
            "visits",
            "reservation flag without reservation_date",
            missing_res_count,
            "filled visit_date + 2 days",
        )

    visits.loc[visits["is_reservation"] == 0, "reservation_date"] = pd.NaT

    before_visit = (
        (visits["is_reservation"] == 1)
        & visits["reservation_date"].notna()
        & (visits["reservation_date"] < visits["visit_date"])
    )
    before_visit_count = int(before_visit.sum())
    if before_visit_count:
        visits.loc[before_visit, "reservation_date"] = visits.loc[before_visit, "visit_date"]
        _record_issue(
            issues,
            "visits",
            "reservation_date before visit_date",
            before_visit_count,
            "set equal to visit_date",
        )

    visits = visits.drop(columns=["lead_project_id"])
    visits = visits.drop(columns=["lead_date"])

    valid_projects = set(projects["project_id"])
    invalid_projects = int((~visits["project_id"].isin(valid_projects)).sum())
    if invalid_projects:
        visits = visits[visits["project_id"].isin(valid_projects)]
        _record_issue(issues, "visits", "project_id not found in projects", invalid_projects, "dropped")

    return visits.reset_index(drop=True)


def _clean_sales(
    sales: pd.DataFrame,
    visits: pd.DataFrame,
    leads: pd.DataFrame,
    projects: pd.DataFrame,
    issues: list[dict[str, Any]],
) -> pd.DataFrame:
    sales = sales.copy()
    sales.columns = [str(col).strip() for col in sales.columns]

    if sales.empty:
        return sales

    sales = _deduplicate_primary_key("sales", sales, issues)

    sales["sale_date"] = _to_datetime(sales, "sale_date")
    invalid_dates = int(sales["sale_date"].isna().sum())
    if invalid_dates:
        sales = sales[sales["sale_date"].notna()]
        _record_issue(issues, "sales", "invalid sale_date", invalid_dates, "dropped")

    valid_visits = set(visits["visit_id"])
    invalid_visit_ids = int((~sales["visit_id"].isin(valid_visits)).sum())
    if invalid_visit_ids:
        sales = sales[sales["visit_id"].isin(valid_visits)]
        _record_issue(issues, "sales", "visit_id not found in visits", invalid_visit_ids, "dropped")

    valid_leads = set(leads["lead_id"])
    invalid_leads = int((~sales["lead_id"].isin(valid_leads)).sum())
    if invalid_leads:
        sales = sales[sales["lead_id"].isin(valid_leads)]
        _record_issue(issues, "sales", "lead_id not found in leads", invalid_leads, "dropped")

    valid_projects = set(projects["project_id"])
    invalid_projects = int((~sales["project_id"].isin(valid_projects)).sum())
    if invalid_projects:
        sales = sales[sales["project_id"].isin(valid_projects)]
        _record_issue(issues, "sales", "project_id not found in projects", invalid_projects, "dropped")

    visit_refs = visits[["visit_id", "lead_id", "project_id", "reservation_date"]].copy()
    visit_refs = visit_refs.rename(
        columns={
            "lead_id": "visit_lead_id",
            "project_id": "visit_project_id",
        }
    )
    sales = sales.merge(visit_refs, on="visit_id", how="left")

    mismatch = (sales["lead_id"] != sales["visit_lead_id"]) | (
        sales["project_id"] != sales["visit_project_id"]
    )
    mismatch_count = int(mismatch.sum())
    if mismatch_count:
        sales = sales[~mismatch]
        _record_issue(
            issues,
            "sales",
            "sale references inconsistent with visit lead/project",
            mismatch_count,
            "dropped",
        )

    sales["sale_price"] = _to_numeric(sales, "sale_price")
    sales["discount_rate"] = _to_numeric(sales, "discount_rate")

    bad_price = int((sales["sale_price"] <= 0).sum())
    if bad_price:
        project_price = projects.set_index("project_id")["avg_price"].to_dict()
        sales.loc[sales["sale_price"] <= 0, "sale_price"] = sales.loc[
            sales["sale_price"] <= 0, "project_id"
        ].map(project_price) * 0.90
        _record_issue(issues, "sales", "non-positive sale_price", bad_price, "replaced with 90% of avg_price")

    sales["discount_rate"] = sales["discount_rate"].clip(lower=0.0, upper=0.40)

    bad_date_order = (
        sales["reservation_date"].notna() & (sales["sale_date"] < sales["reservation_date"])
    )
    bad_date_count = int(bad_date_order.sum())
    if bad_date_count:
        sales.loc[bad_date_order, "sale_date"] = sales.loc[bad_date_order, "reservation_date"] + pd.Timedelta(
            days=1
        )
        _record_issue(
            issues,
            "sales",
            "sale_date before reservation_date",
            bad_date_count,
            "shifted to reservation_date + 1 day",
        )

    sales = sales.drop(columns=["visit_lead_id", "visit_project_id", "reservation_date"])
    sales["sale_price"] = sales["sale_price"].round(2)

    return sales.reset_index(drop=True)


def _enforce_funnel_rules(
    projects: pd.DataFrame,
    campaigns: pd.DataFrame,
    leads: pd.DataFrame,
    visits: pd.DataFrame,
    sales: pd.DataFrame,
    issues: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    # qualified_leads <= leads check (project-level)
    lead_counts = (
        leads.groupby("project_id", as_index=False)
        .agg(leads=("lead_id", "count"), qualified_leads=("is_qualified", "sum"))
        .copy()
    )
    invalid_qualified = lead_counts[lead_counts["qualified_leads"] > lead_counts["leads"]]
    if not invalid_qualified.empty:
        _record_issue(
            issues,
            "leads",
            "qualified_leads > leads",
            int(len(invalid_qualified)),
            "flagged for investigation",
        )

    # visits should not exceed plausible upstream volume (leads).
    visit_counts = visits.groupby("project_id", as_index=False).agg(visits=("visit_id", "count"))
    plausibility_df = visit_counts.merge(lead_counts[["project_id", "leads"]], on="project_id", how="left")
    plausibility_df["leads"] = plausibility_df["leads"].fillna(0)
    over_visit_projects = plausibility_df[plausibility_df["visits"] > plausibility_df["leads"]]
    if not over_visit_projects.empty:
        dropped_rows = 0
        for row in over_visit_projects.itertuples(index=False):
            extra = int(row.visits - row.leads)
            if extra <= 0:
                continue
            candidate_idx = (
                visits[visits["project_id"] == row.project_id]
                .sort_values(by=["visit_date", "visit_id"], ascending=False)
                .head(extra)
                .index
            )
            dropped_rows += int(len(candidate_idx))
            visits = visits.drop(index=candidate_idx)
        _record_issue(
            issues,
            "visits",
            "visits exceed leads",
            dropped_rows,
            "dropped latest excess visits",
        )

    # reservations <= visits (project-level)
    reservation_counts = (
        visits.groupby("project_id", as_index=False)
        .agg(visits=("visit_id", "count"), reservations=("is_reservation", "sum"))
        .copy()
    )
    invalid_reservations = reservation_counts[
        reservation_counts["reservations"] > reservation_counts["visits"]
    ]
    if not invalid_reservations.empty:
        _record_issue(
            issues,
            "visits",
            "reservations > visits",
            int(len(invalid_reservations)),
            "flagged for investigation",
        )

    # sales <= reservations and sales <= total_units.
    reservation_lookup = (
        visits[visits["is_reservation"] == 1]
        .groupby("project_id", as_index=False)
        .agg(reservations=("visit_id", "count"))
    )
    sales_lookup = sales.groupby("project_id", as_index=False).agg(sales=("sale_id", "count"))
    sales_check = sales_lookup.merge(reservation_lookup, on="project_id", how="left")
    sales_check["reservations"] = sales_check["reservations"].fillna(0)

    too_many_sales = sales_check[sales_check["sales"] > sales_check["reservations"]]
    if not too_many_sales.empty:
        dropped_sales = 0
        for row in too_many_sales.itertuples(index=False):
            extra = int(row.sales - row.reservations)
            candidate_idx = (
                sales[sales["project_id"] == row.project_id]
                .sort_values(by=["sale_date", "sale_id"], ascending=False)
                .head(extra)
                .index
            )
            dropped_sales += int(len(candidate_idx))
            sales = sales.drop(index=candidate_idx)
        _record_issue(
            issues,
            "sales",
            "sales > reservations",
            dropped_sales,
            "dropped latest excess sales",
        )

    total_units_lookup = projects.set_index("project_id")["total_units"].to_dict()
    sales_counts = sales.groupby("project_id", as_index=False).agg(sales=("sale_id", "count"))
    sales_counts["total_units"] = sales_counts["project_id"].map(total_units_lookup).fillna(0)
    inventory_violations = sales_counts[sales_counts["sales"] > sales_counts["total_units"]]
    if not inventory_violations.empty:
        dropped_sales = 0
        for row in inventory_violations.itertuples(index=False):
            extra = int(row.sales - row.total_units)
            candidate_idx = (
                sales[sales["project_id"] == row.project_id]
                .sort_values(by=["sale_date", "sale_id"], ascending=False)
                .head(extra)
                .index
            )
            dropped_sales += int(len(candidate_idx))
            sales = sales.drop(index=candidate_idx)
        _record_issue(
            issues,
            "sales",
            "sales exceed total_units (unsold inventory < 0)",
            dropped_sales,
            "dropped latest excess sales",
        )

    # Rebuild sales IDs if rows were removed.
    sales = sales.sort_values(by=["sale_date", "project_id", "visit_id"]).reset_index(drop=True)
    if not sales.empty:
        sales["sale_id"] = [f"S{i:07d}" for i in range(1, len(sales) + 1)]

    # Ensure no duplicate IDs after reshaping.
    sales = _deduplicate_primary_key("sales", sales, issues)

    # Keep only visits that still exist after sales trims for referential integrity.
    valid_visit_ids = set(visits["visit_id"])
    sales = sales[sales["visit_id"].isin(valid_visit_ids)].reset_index(drop=True)

    return visits.reset_index(drop=True), sales.reset_index(drop=True)


def _save_processed_tables(tables: dict[str, pd.DataFrame], processed_dir: Path) -> None:
    for table_name, df in tables.items():
        output_path = processed_dir / f"{table_name}.csv"
        df.to_csv(output_path, index=False)
        print(f"[clean_raw_data] Saved {table_name}: {len(df):,} rows -> {output_path}")


def clean_raw_data(
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
) -> dict[str, pd.DataFrame]:
    ensure_data_directories()

    print("[clean_raw_data] Loading raw tables...")
    raw_tables = load_raw_tables(raw_dir=raw_dir)
    issues: list[dict[str, Any]] = []

    projects = _clean_projects(raw_tables["projects"], issues)
    campaigns = _clean_campaigns(raw_tables["campaigns"], projects, issues)
    leads = _clean_leads(raw_tables["leads"], campaigns, projects, issues)
    visits = _clean_visits(raw_tables["visits"], leads, projects, issues)
    sales = _clean_sales(raw_tables["sales"], visits, leads, projects, issues)

    visits, sales = _enforce_funnel_rules(projects, campaigns, leads, visits, sales, issues)

    processed_tables = {
        "projects": projects,
        "campaigns": campaigns,
        "leads": leads,
        "visits": visits,
        "sales": sales,
    }

    print("[clean_raw_data] Writing processed tables...")
    _save_processed_tables(processed_tables, processed_dir)

    issues_df = pd.DataFrame(issues)
    issues_path = processed_dir / "validation_issues.csv"
    issues_df.to_csv(issues_path, index=False)
    print(
        f"[clean_raw_data] Validation checks recorded: {len(issues_df):,} rows -> {issues_path}"
    )

    # Validation summary required by the project brief.
    lead_check = (
        leads.groupby("project_id", as_index=False)
        .agg(leads=("lead_id", "count"), qualified_leads=("is_qualified", "sum"))
        .assign(is_valid=lambda d: d["qualified_leads"] <= d["leads"])
    )
    reservation_check = (
        visits.groupby("project_id", as_index=False)
        .agg(visits=("visit_id", "count"), reservations=("is_reservation", "sum"))
        .assign(is_valid=lambda d: d["reservations"] <= d["visits"])
    )
    sales_check = (
        sales.groupby("project_id", as_index=False)
        .agg(sales=("sale_id", "count"))
        .merge(
            visits[visits["is_reservation"] == 1]
            .groupby("project_id", as_index=False)
            .agg(reservations=("visit_id", "count")),
            on="project_id",
            how="left",
        )
        .fillna({"reservations": 0})
        .assign(is_valid=lambda d: d["sales"] <= d["reservations"])
    )

    print(
        "[clean_raw_data] Checks: "
        f"qualified<=leads valid={lead_check['is_valid'].all()} | "
        f"reservations<=visits valid={reservation_check['is_valid'].all()} | "
        f"sales<=reservations valid={sales_check['is_valid'].all()}"
    )

    return processed_tables


def main() -> None:
    clean_raw_data()


if __name__ == "__main__":
    main()
