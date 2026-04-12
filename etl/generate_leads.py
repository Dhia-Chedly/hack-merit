"""Generate synthetic lead-level records from campaign output."""

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
        city_mid_price,
    )
except ImportError:  # pragma: no cover - local execution fallback
    from config import (  # type: ignore
        CHANNEL_ASSUMPTIONS,
        CITY_CONFIGS,
        CONVERSION_ASSUMPTIONS,
        PROJECT_QUALITY_TIERS,
        RANDOM_SEED,
        RAW_DIR,
        city_mid_price,
    )


def _load_projects(projects_path: Path | None = None) -> pd.DataFrame:
    path = projects_path or (RAW_DIR / "projects.csv")
    return pd.read_csv(path, parse_dates=["launch_date"])


def _load_campaigns(campaigns_path: Path | None = None) -> pd.DataFrame:
    path = campaigns_path or (RAW_DIR / "campaigns.csv")
    return pd.read_csv(path, parse_dates=["campaign_date"])


def _purchase_horizon(channel: str, rng: np.random.Generator) -> int:
    channel_windows = {
        "Google Search": (16, 95),
        "Meta Ads": (35, 170),
        "Property Portals": (18, 120),
        "Referral": (14, 90),
    }
    low, high = channel_windows.get(channel, (21, 150))
    return int(rng.integers(low, high + 1))


def generate_leads(
    projects_df: pd.DataFrame | None = None,
    campaigns_df: pd.DataFrame | None = None,
    output_path: Path | None = None,
    seed: int = RANDOM_SEED + 2,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    projects = projects_df.copy() if projects_df is not None else _load_projects()
    campaigns = campaigns_df.copy() if campaigns_df is not None else _load_campaigns()

    project_lookup = projects.set_index("project_id").to_dict(orient="index")
    qualified_threshold = float(CONVERSION_ASSUMPTIONS["qualified_score_threshold"])
    price_penalty_strength = float(CONVERSION_ASSUMPTIONS["price_penalty_strength"])

    lead_rows: list[dict[str, object]] = []
    lead_counter = 1

    for campaign in campaigns.itertuples(index=False):
        project = project_lookup.get(campaign.project_id)
        if project is None:
            continue

        city = str(project["city"])
        channel_cfg = CHANNEL_ASSUMPTIONS[str(campaign.channel)]
        city_cfg = CITY_CONFIGS[city]
        tier_cfg = PROJECT_QUALITY_TIERS[str(project["quality_tier"])]

        city_price_mid = city_mid_price(city)
        avg_price = float(project["avg_price"])
        price_pressure = max(0.0, (avg_price - city_price_mid) / city_price_mid)

        leads_to_create = int(max(0, campaign.attributed_leads))
        for _ in range(leads_to_create):
            lead_date = pd.Timestamp(campaign.campaign_date) + pd.Timedelta(
                days=int(rng.integers(0, 7))
            )

            base_score = 53.0
            base_score += (float(channel_cfg["quality_multiplier"]) - 1.0) * 28.0
            base_score += (float(tier_cfg["lead_quality_multiplier"]) - 1.0) * 24.0
            base_score += (float(city_cfg["conversion_index"]) - 0.9) * 22.0
            base_score -= price_pressure * (100.0 * price_penalty_strength)
            base_score += rng.normal(0.0, 10.5)
            lead_score = float(np.clip(base_score, 1.0, 99.0))

            qualification_lift = (lead_score - qualified_threshold) / 15.0
            qualified_probability = 1.0 / (1.0 + np.exp(-qualification_lift))
            qualified_probability = float(np.clip(qualified_probability, 0.03, 0.97))
            is_qualified = bool(rng.random() < qualified_probability)

            budget_multiplier = float(rng.normal(loc=0.90 + (lead_score / 1000), scale=0.16))
            budget_multiplier = float(np.clip(budget_multiplier, 0.52, 1.35))
            budget_tnd = float(max(60000.0, avg_price * budget_multiplier))

            horizon_days = _purchase_horizon(str(campaign.channel), rng)
            if not is_qualified:
                horizon_days = min(365, horizon_days + int(rng.integers(10, 65)))

            lead_rows.append(
                {
                    "lead_id": f"L{lead_counter:07d}",
                    "campaign_id": campaign.campaign_id,
                    "project_id": campaign.project_id,
                    "lead_date": lead_date.normalize(),
                    "channel": campaign.channel,
                    "city": city,
                    "neighborhood": project["neighborhood"],
                    "property_type": project["property_type"],
                    "lead_score": round(lead_score, 2),
                    "is_qualified": int(is_qualified),
                    "budget_tnd": round(budget_tnd, 2),
                    "expected_purchase_days": int(horizon_days),
                }
            )
            lead_counter += 1

    leads_df = pd.DataFrame(lead_rows)
    leads_df = leads_df.sort_values(by=["lead_date", "project_id", "lead_id"])
    leads_df = leads_df.reset_index(drop=True)

    save_path = output_path or (RAW_DIR / "leads.csv")
    leads_df.to_csv(save_path, index=False)

    print(f"[generate_leads] Wrote {len(leads_df):,} rows -> {save_path}")
    return leads_df


def main() -> None:
    generate_leads()


if __name__ == "__main__":
    main()
