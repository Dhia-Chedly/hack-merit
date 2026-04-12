"""Generate synthetic site visits and reservations from lead-level data."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

try:
    from .config import (
        CHANNEL_ASSUMPTIONS,
        CITY_CONFIGS,
        CONVERSION_ASSUMPTIONS,
        PROJECT_QUALITY_TIERS,
        RANDOM_SEED,
        RAW_DIR,
    )
except ImportError:  # pragma: no cover - local execution fallback
    from config import (  # type: ignore
        CHANNEL_ASSUMPTIONS,
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
    return pd.read_csv(path, parse_dates=["lead_date"])


def generate_visits(
    leads_df: pd.DataFrame | None = None,
    projects_df: pd.DataFrame | None = None,
    output_path: Path | None = None,
    seed: int = RANDOM_SEED + 3,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    leads = leads_df.copy() if leads_df is not None else _load_leads()
    projects = projects_df.copy() if projects_df is not None else _load_projects()

    project_lookup = projects.set_index("project_id").to_dict(orient="index")

    visit_rows: list[dict[str, object]] = []
    visit_counter = 1

    base_visit_probability = float(CONVERSION_ASSUMPTIONS["base_visit_probability"])
    base_reservation_probability = float(CONVERSION_ASSUMPTIONS["base_reservation_probability"])

    for lead in leads.itertuples(index=False):
        project = project_lookup.get(lead.project_id)
        if project is None:
            continue

        city_cfg = CITY_CONFIGS[str(project["city"])]
        tier_cfg = PROJECT_QUALITY_TIERS[str(project["quality_tier"])]
        channel_cfg = CHANNEL_ASSUMPTIONS[str(lead.channel)]

        budget_ratio = float(lead.budget_tnd) / max(float(project["avg_price"]), 1.0)
        price_penalty = max(0.0, 1.0 - budget_ratio)

        lead_score_factor = 0.55 + (float(lead.lead_score) / 100.0)
        visit_probability = (
            base_visit_probability
            * lead_score_factor
            * float(channel_cfg["visit_intent_multiplier"])
            * float(city_cfg["conversion_index"])
            * float(tier_cfg["conversion_multiplier"])
            * max(0.42, 1.0 - (price_penalty * 0.65))
        )
        if int(lead.is_qualified) == 0:
            visit_probability *= 0.52
        visit_probability = float(np.clip(visit_probability, 0.02, 0.88))

        has_visit = bool(rng.random() < visit_probability)
        if not has_visit:
            continue

        visit_date = pd.Timestamp(lead.lead_date) + pd.Timedelta(days=int(rng.integers(1, 30)))

        reservation_probability = (
            base_reservation_probability
            * (0.50 + (float(lead.lead_score) / 100.0))
            * float(city_cfg["conversion_index"])
            * float(tier_cfg["conversion_multiplier"])
            * max(0.46, 1.0 - (price_penalty * 0.80))
        )
        if int(lead.is_qualified) == 0:
            reservation_probability *= 0.58
        reservation_probability = float(np.clip(reservation_probability, 0.01, 0.92))

        is_reservation = bool(rng.random() < reservation_probability)
        reservation_date = (
            visit_date + pd.Timedelta(days=int(rng.integers(0, 10))) if is_reservation else pd.NaT
        )

        visit_rows.append(
            {
                "visit_id": f"V{visit_counter:07d}",
                "lead_id": lead.lead_id,
                "project_id": lead.project_id,
                "visit_date": visit_date.normalize(),
                "is_reservation": int(is_reservation),
                "reservation_date": reservation_date.normalize() if is_reservation else pd.NaT,
            }
        )
        visit_counter += 1

    visits_df = pd.DataFrame(visit_rows)
    visits_df = visits_df.sort_values(by=["visit_date", "project_id", "visit_id"])
    visits_df = visits_df.reset_index(drop=True)

    save_path = output_path or (RAW_DIR / "visits.csv")
    visits_df.to_csv(save_path, index=False)

    print(f"[generate_visits] Wrote {len(visits_df):,} rows -> {save_path}")
    return visits_df


def main() -> None:
    generate_visits()


if __name__ == "__main__":
    main()
