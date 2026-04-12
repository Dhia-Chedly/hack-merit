"""Generate synthetic sales transactions from reservations."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

try:
    from .config import (
        CITY_CONFIGS,
        CONVERSION_ASSUMPTIONS,
        PROJECT_QUALITY_TIERS,
        RANDOM_SEED,
        RAW_DIR,
    )
except ImportError:  # pragma: no cover - local execution fallback
    from config import (  # type: ignore
        CITY_CONFIGS,
        CONVERSION_ASSUMPTIONS,
        PROJECT_QUALITY_TIERS,
        RANDOM_SEED,
        RAW_DIR,
    )


def _load_projects(projects_path: Path | None = None) -> pd.DataFrame:
    path = projects_path or (RAW_DIR / "projects.csv")
    return pd.read_csv(path)


def _load_leads(leads_path: Path | None = None) -> pd.DataFrame:
    path = leads_path or (RAW_DIR / "leads.csv")
    return pd.read_csv(path)


def _load_visits(visits_path: Path | None = None) -> pd.DataFrame:
    path = visits_path or (RAW_DIR / "visits.csv")
    return pd.read_csv(path, parse_dates=["visit_date", "reservation_date"])


def generate_sales(
    visits_df: pd.DataFrame | None = None,
    leads_df: pd.DataFrame | None = None,
    projects_df: pd.DataFrame | None = None,
    output_path: Path | None = None,
    seed: int = RANDOM_SEED + 4,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    visits = visits_df.copy() if visits_df is not None else _load_visits()
    leads = leads_df.copy() if leads_df is not None else _load_leads()
    projects = projects_df.copy() if projects_df is not None else _load_projects()

    leads_lookup = leads.set_index("lead_id").to_dict(orient="index")
    project_lookup = projects.set_index("project_id").to_dict(orient="index")

    reservations = visits[visits["is_reservation"] == 1].copy()

    base_sale_probability = float(CONVERSION_ASSUMPTIONS["base_sale_probability"])
    sale_rows: list[dict[str, object]] = []

    for reservation in reservations.itertuples(index=False):
        lead = leads_lookup.get(reservation.lead_id)
        project = project_lookup.get(reservation.project_id)
        if lead is None or project is None:
            continue

        city_cfg = CITY_CONFIGS[str(project["city"])]
        tier_cfg = PROJECT_QUALITY_TIERS[str(project["quality_tier"])]

        budget_ratio = float(lead["budget_tnd"]) / max(float(project["avg_price"]), 1.0)
        price_penalty = max(0.0, 1.0 - budget_ratio)

        score_factor = 0.55 + (float(lead["lead_score"]) / 100.0)
        sale_probability = (
            base_sale_probability
            * score_factor
            * float(city_cfg["conversion_index"])
            * float(tier_cfg["conversion_multiplier"])
            * max(0.42, 1.0 - (price_penalty * 0.85))
        )
        if int(lead["is_qualified"]) == 0:
            sale_probability *= 0.58
        sale_probability = float(np.clip(sale_probability, 0.02, 0.95))

        if rng.random() >= sale_probability:
            continue

        reservation_date = pd.Timestamp(reservation.reservation_date)
        delay_low, delay_high = 3, 42
        if str(project["city"]) == "La Marsa":
            delay_low, delay_high = 8, 60

        sale_date = reservation_date + pd.Timedelta(days=int(rng.integers(delay_low, delay_high + 1)))

        discount_rate = 0.035 + (price_penalty * 0.10) + rng.uniform(-0.01, 0.04)
        discount_rate = float(np.clip(discount_rate, 0.0, 0.20))

        sale_price = float(project["avg_price"]) * (1.0 - discount_rate) * rng.uniform(0.96, 1.04)
        sale_price = max(70000.0, round(sale_price, 2))

        sale_rows.append(
            {
                "visit_id": reservation.visit_id,
                "lead_id": reservation.lead_id,
                "project_id": reservation.project_id,
                "sale_date": sale_date.normalize(),
                "sale_price": sale_price,
                "discount_rate": round(discount_rate, 4),
            }
        )

    sales_df = pd.DataFrame(sale_rows)
    if sales_df.empty:
        sales_df = pd.DataFrame(
            columns=[
                "sale_id",
                "visit_id",
                "lead_id",
                "project_id",
                "sale_date",
                "sale_price",
                "discount_rate",
            ]
        )
    else:
        sales_df = sales_df.sort_values(by=["project_id", "sale_date", "visit_id"])

        capped_rows: list[pd.DataFrame] = []
        total_units_lookup = projects.set_index("project_id")["total_units"].to_dict()
        for project_id, group in sales_df.groupby("project_id", sort=False):
            allowed_units = int(total_units_lookup.get(project_id, len(group)))
            capped_rows.append(group.head(allowed_units))

        sales_df = pd.concat(capped_rows, ignore_index=True)
        sales_df = sales_df.sort_values(by=["sale_date", "project_id", "visit_id"])
        sales_df = sales_df.reset_index(drop=True)
        sales_df.insert(0, "sale_id", [f"S{i:07d}" for i in range(1, len(sales_df) + 1)])

    save_path = output_path or (RAW_DIR / "sales.csv")
    sales_df.to_csv(save_path, index=False)

    print(f"[generate_sales] Wrote {len(sales_df):,} rows -> {save_path}")
    return sales_df


def main() -> None:
    generate_sales()


if __name__ == "__main__":
    main()
