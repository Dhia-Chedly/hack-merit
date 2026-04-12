"""Generate synthetic marketing campaigns linked to projects and city dynamics."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

try:
    from .config import (
        CHANNEL_ASSUMPTIONS,
        CITY_CONFIGS,
        PROJECT_QUALITY_TIERS,
        RANDOM_SEED,
        RAW_DIR,
        campaign_dates,
        city_mid_price,
        seasonal_multiplier,
    )
except ImportError:  # pragma: no cover - local execution fallback
    from config import (  # type: ignore
        CHANNEL_ASSUMPTIONS,
        CITY_CONFIGS,
        PROJECT_QUALITY_TIERS,
        RANDOM_SEED,
        RAW_DIR,
        campaign_dates,
        city_mid_price,
        seasonal_multiplier,
    )


def _load_projects(projects_path: Path | None = None) -> pd.DataFrame:
    path = projects_path or (RAW_DIR / "projects.csv")
    return pd.read_csv(path, parse_dates=["launch_date"])


def generate_campaigns(
    projects_df: pd.DataFrame | None = None,
    output_path: Path | None = None,
    seed: int = RANDOM_SEED + 1,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    projects = projects_df.copy() if projects_df is not None else _load_projects()

    periods = campaign_dates()
    campaign_rows: list[dict[str, object]] = []
    campaign_counter = 1

    for project in projects.itertuples(index=False):
        city_cfg = CITY_CONFIGS[project.city]
        tier_cfg = PROJECT_QUALITY_TIERS[str(project.quality_tier)]
        city_price_mid = city_mid_price(project.city)
        price_pressure = max(0.0, (float(project.avg_price) - city_price_mid) / city_price_mid)

        for period_start in periods:
            if pd.Timestamp(period_start) < pd.Timestamp(project.launch_date):
                continue

            seasonal = seasonal_multiplier(project.city, pd.Timestamp(period_start))

            for channel_name, channel_cfg in CHANNEL_ASSUMPTIONS.items():
                if rng.random() > float(channel_cfg["active_probability"]):
                    continue

                channel_volume = float(channel_cfg["volume_multiplier"])
                city_demand = float(city_cfg["demand_index"])
                spend_multiplier = float(tier_cfg["spend_multiplier"])

                property_volume_factor = {
                    "Apartment": 1.08,
                    "Studio": 1.12,
                    "Villa": 0.82,
                    "Office": 0.74,
                }.get(str(project.property_type), 1.00)

                spend_mean = (
                    420.0
                    * city_demand
                    * spend_multiplier
                    * seasonal
                    * channel_volume
                    * property_volume_factor
                )
                spend = rng.normal(loc=spend_mean, scale=spend_mean * 0.22)
                spend = float(np.clip(spend, 120.0, 3400.0))

                cpc_low, cpc_high = channel_cfg["cpc_range"]
                cpc = float(rng.uniform(cpc_low, cpc_high)) / max(
                    float(city_cfg["marketing_efficiency"]), 0.65
                )

                ctr_low, ctr_high = channel_cfg["ctr_range"]
                ctr = float(rng.uniform(ctr_low, ctr_high)) * float(
                    city_cfg["marketing_efficiency"]
                )
                ctr = float(np.clip(ctr, 0.008, 0.12))

                clicks = int(max(0, round((spend / cpc) * rng.uniform(0.86, 1.14))))
                impressions = int(max(clicks, round(clicks / max(ctr, 0.001))))

                lead_rate_low, lead_rate_high = channel_cfg["lead_rate_range"]
                lead_rate = float(rng.uniform(lead_rate_low, lead_rate_high))
                lead_rate *= float(tier_cfg["lead_quality_multiplier"])
                lead_rate *= float(city_cfg["marketing_efficiency"])
                lead_rate *= max(0.58, 1.0 - (price_pressure * 0.30))
                lead_rate *= rng.uniform(0.86, 1.12)
                lead_rate = float(np.clip(lead_rate, 0.02, 0.22))

                # Scale raw click->lead output to keep campaign realism without
                # creating excessively large lead-level tables for demo loops.
                attributed_leads = int(max(0, round(clicks * lead_rate * 0.20)))
                attributed_leads = min(attributed_leads, clicks)

                campaign_rows.append(
                    {
                        "campaign_id": f"C{campaign_counter:06d}",
                        "project_id": project.project_id,
                        "campaign_date": pd.Timestamp(period_start).normalize(),
                        "channel": channel_name,
                        "spend": round(spend, 2),
                        "impressions": impressions,
                        "clicks": clicks,
                        "attributed_leads": attributed_leads,
                    }
                )
                campaign_counter += 1

    campaigns_df = pd.DataFrame(campaign_rows)
    campaigns_df = campaigns_df.sort_values(by=["campaign_date", "project_id", "channel"])
    campaigns_df = campaigns_df.reset_index(drop=True)

    save_path = output_path or (RAW_DIR / "campaigns.csv")
    campaigns_df.to_csv(save_path, index=False)

    print(f"[generate_campaigns] Wrote {len(campaigns_df):,} rows -> {save_path}")
    return campaigns_df


def main() -> None:
    generate_campaigns()


if __name__ == "__main__":
    main()
