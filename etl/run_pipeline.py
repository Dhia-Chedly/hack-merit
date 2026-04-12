"""Run the full synthetic ETL pipeline: raw generation -> cleaning -> curated tables."""

from __future__ import annotations

import time

try:
    from .build_curated_tables import build_curated_tables
    from .clean_raw_data import clean_raw_data
    from .config import CURATED_DIR, PROCESSED_DIR, RAW_DIR, ensure_data_directories
    from .generate_campaigns import generate_campaigns
    from .generate_leads import generate_leads
    from .generate_projects import generate_projects
    from .generate_sales import generate_sales
    from .generate_visits import generate_visits
except ImportError:  # pragma: no cover - local execution fallback
    from build_curated_tables import build_curated_tables  # type: ignore
    from clean_raw_data import clean_raw_data  # type: ignore
    from config import CURATED_DIR, PROCESSED_DIR, RAW_DIR, ensure_data_directories  # type: ignore
    from generate_campaigns import generate_campaigns  # type: ignore
    from generate_leads import generate_leads  # type: ignore
    from generate_projects import generate_projects  # type: ignore
    from generate_sales import generate_sales  # type: ignore
    from generate_visits import generate_visits  # type: ignore


def _log(message: str) -> None:
    print(f"[run_pipeline] {message}")


def run_pipeline() -> None:
    start = time.time()
    ensure_data_directories()

    _log("Starting ETL pipeline for Tunisia real-estate intelligence...")
    _log(f"Raw layer path: {RAW_DIR}")
    _log(f"Processed layer path: {PROCESSED_DIR}")
    _log(f"Curated layer path: {CURATED_DIR}")

    _log("Step 1/3: Generating raw tables")
    projects_df = generate_projects()
    campaigns_df = generate_campaigns(projects_df=projects_df)
    leads_df = generate_leads(projects_df=projects_df, campaigns_df=campaigns_df)
    visits_df = generate_visits(leads_df=leads_df, projects_df=projects_df)
    sales_df = generate_sales(
        visits_df=visits_df,
        leads_df=leads_df,
        projects_df=projects_df,
    )

    _log(
        "Raw row counts -> "
        f"projects={len(projects_df):,}, "
        f"campaigns={len(campaigns_df):,}, "
        f"leads={len(leads_df):,}, "
        f"visits={len(visits_df):,}, "
        f"sales={len(sales_df):,}"
    )

    _log("Step 2/3: Cleaning and validating raw tables")
    processed_tables = clean_raw_data()
    _log(
        "Processed row counts -> "
        + ", ".join(f"{name}={len(df):,}" for name, df in processed_tables.items())
    )

    _log("Step 3/3: Building curated analytics tables")
    curated_tables = build_curated_tables()
    _log(
        "Curated row counts -> "
        + ", ".join(f"{name}={len(df):,}" for name, df in curated_tables.items())
    )

    elapsed = time.time() - start
    _log(f"Pipeline completed successfully in {elapsed:.1f}s")


def main() -> None:
    run_pipeline()


if __name__ == "__main__":
    main()
