"""Generate synthetic real-estate projects for Tunisia."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

try:
    from .config import (
        CITY_CONFIGS,
        DATE_RANGE,
        PROJECT_COUNTS_BY_CITY,
        PROJECT_QUALITY_TIERS,
        PROPERTY_TYPES,
        QUALITY_TIER_WEIGHTS,
        RANDOM_SEED,
        RAW_DIR,
        ensure_data_directories,
    )
except ImportError:  # pragma: no cover - local execution fallback
    from config import (  # type: ignore
        CITY_CONFIGS,
        DATE_RANGE,
        PROJECT_COUNTS_BY_CITY,
        PROJECT_QUALITY_TIERS,
        PROPERTY_TYPES,
        QUALITY_TIER_WEIGHTS,
        RANDOM_SEED,
        RAW_DIR,
        ensure_data_directories,
    )


PROJECT_NAME_SUFFIXES = [
    "Residences",
    "Gardens",
    "Heights",
    "Park",
    "Living",
    "Terraces",
    "Homes",
    "Suites",
    "Vista",
]


def _weighted_choice(rng: np.random.Generator, weights: dict[str, float]) -> str:
    keys = list(weights.keys())
    probs = np.array(list(weights.values()), dtype="float64")
    probs = probs / probs.sum()
    return str(rng.choice(keys, p=probs))


def _build_project_name(neighborhood: str, property_type: str, suffix: str) -> str:
    type_token = {
        "Apartment": "Urban",
        "Studio": "Compact",
        "Villa": "Signature",
        "Office": "Business",
    }.get(property_type, "Prime")
    return f"{neighborhood} {type_token} {suffix}"


def generate_projects(
    output_path: Path | None = None,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    ensure_data_directories()
    rng = np.random.default_rng(seed)

    launch_start = pd.Timestamp(DATE_RANGE["start"])
    launch_end = launch_start + pd.Timedelta(days=160)

    rows: list[dict[str, object]] = []
    project_counter = 1

    for city, city_project_count in PROJECT_COUNTS_BY_CITY.items():
        city_config = CITY_CONFIGS[city]
        city_price_low, city_price_high = city_config["price_range"]

        for _ in range(city_project_count):
            neighborhood_info = city_config["neighborhoods"][
                int(rng.integers(0, len(city_config["neighborhoods"])))
            ]
            property_type = _weighted_choice(rng, city_config["property_mix"])
            quality_tier = _weighted_choice(rng, QUALITY_TIER_WEIGHTS)

            property_cfg = PROPERTY_TYPES[property_type]
            tier_cfg = PROJECT_QUALITY_TIERS[quality_tier]

            base_city_price = rng.uniform(city_price_low, city_price_high)
            price_noise = rng.normal(loc=1.0, scale=0.07)
            avg_price = (
                base_city_price
                * float(property_cfg["price_multiplier"])
                * float(tier_cfg["lead_quality_multiplier"])
                * price_noise
            )
            avg_price = max(90000.0, round(avg_price / 1000) * 1000)

            units_low, units_high = property_cfg["unit_range"]
            unit_adjustment = 0.92 + (city_config["demand_index"] - 1.0) * 0.60
            total_units = int(
                round(rng.integers(units_low, units_high + 1) * unit_adjustment)
            )
            total_units = int(max(24, total_units))

            latitude = float(neighborhood_info["lat"] + rng.normal(0.0, 0.0042))
            longitude = float(neighborhood_info["lon"] + rng.normal(0.0, 0.0048))

            project_id = f"P{project_counter:04d}"
            project_counter += 1

            suffix = PROJECT_NAME_SUFFIXES[int(rng.integers(0, len(PROJECT_NAME_SUFFIXES)))]
            project_name = _build_project_name(
                neighborhood=str(neighborhood_info["name"]),
                property_type=property_type,
                suffix=suffix,
            )

            launch_date = launch_start + pd.Timedelta(
                days=int(rng.integers(0, (launch_end - launch_start).days + 1))
            )

            rows.append(
                {
                    "project_id": project_id,
                    "project_name": project_name,
                    "city": city,
                    "neighborhood": neighborhood_info["name"],
                    "latitude": round(latitude, 6),
                    "longitude": round(longitude, 6),
                    "property_type": property_type,
                    "quality_tier": quality_tier,
                    "total_units": total_units,
                    "avg_price": int(avg_price),
                    "launch_date": launch_date.normalize(),
                }
            )

    projects_df = pd.DataFrame(rows).sort_values(
        by=["city", "project_name", "project_id"]
    )
    projects_df = projects_df.reset_index(drop=True)

    save_path = output_path or (RAW_DIR / "projects.csv")
    projects_df.to_csv(save_path, index=False)

    print(f"[generate_projects] Wrote {len(projects_df):,} rows -> {save_path}")
    return projects_df


def main() -> None:
    generate_projects()


if __name__ == "__main__":
    main()
