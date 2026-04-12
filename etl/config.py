"""Shared configuration for the Tunisia real-estate ETL pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RANDOM_SEED = 20260412

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CURATED_DIR = DATA_DIR / "curated"

DATE_RANGE = {
    "start": "2025-01-01",
    "end": "2025-12-31",
    "frequency": "D",
}

PROJECT_COUNTS_BY_CITY = {
    "Tunis": 10,
    "Ariana": 7,
    "La Marsa": 5,
    "Sousse": 6,
    "Nabeul": 5,
    "Hammamet": 4,
    "Sfax": 8,
}

CITY_CONFIGS = {
    "Tunis": {
        "neighborhoods": [
            {"name": "Lac 1", "lat": 36.8370, "lon": 10.2468},
            {"name": "Lac 2", "lat": 36.8478, "lon": 10.2724},
            {"name": "El Menzah", "lat": 36.8245, "lon": 10.1671},
            {"name": "Mutuelleville", "lat": 36.8158, "lon": 10.1644},
            {"name": "Centre Urbain Nord", "lat": 36.8442, "lon": 10.1889},
        ],
        "price_range": (250000, 520000),
        "demand_index": 1.25,
        "conversion_index": 0.92,
        "marketing_efficiency": 1.00,
        "seasonal_profile": "stable",
        "property_mix": {
            "Apartment": 0.58,
            "Studio": 0.20,
            "Villa": 0.12,
            "Office": 0.10,
        },
    },
    "Ariana": {
        "neighborhoods": [
            {"name": "Ennasr", "lat": 36.8617, "lon": 10.1550},
            {"name": "Menzah 6", "lat": 36.8521, "lon": 10.1660},
            {"name": "Mnihla", "lat": 36.8353, "lon": 10.0788},
            {"name": "Raoued", "lat": 36.8907, "lon": 10.2332},
        ],
        "price_range": (170000, 360000),
        "demand_index": 1.05,
        "conversion_index": 0.95,
        "marketing_efficiency": 0.93,
        "seasonal_profile": "stable",
        "property_mix": {
            "Apartment": 0.62,
            "Studio": 0.15,
            "Villa": 0.13,
            "Office": 0.10,
        },
    },
    "La Marsa": {
        "neighborhoods": [
            {"name": "Marsa Plage", "lat": 36.8862, "lon": 10.3236},
            {"name": "Sidi Daoud", "lat": 36.8720, "lon": 10.2966},
            {"name": "Gammarth", "lat": 36.9189, "lon": 10.2831},
            {"name": "Cite Les Pins", "lat": 36.8877, "lon": 10.3149},
        ],
        "price_range": (420000, 980000),
        "demand_index": 0.82,
        "conversion_index": 0.74,
        "marketing_efficiency": 0.90,
        "seasonal_profile": "stable",
        "property_mix": {
            "Apartment": 0.45,
            "Studio": 0.05,
            "Villa": 0.40,
            "Office": 0.10,
        },
    },
    "Sousse": {
        "neighborhoods": [
            {"name": "Khezama", "lat": 35.8408, "lon": 10.6257},
            {"name": "Sahloul", "lat": 35.8324, "lon": 10.5907},
            {"name": "Khzema Est", "lat": 35.8482, "lon": 10.6381},
            {"name": "Hammam Sousse", "lat": 35.8617, "lon": 10.6035},
        ],
        "price_range": (180000, 390000),
        "demand_index": 1.12,
        "conversion_index": 1.03,
        "marketing_efficiency": 1.02,
        "seasonal_profile": "coastal_medium",
        "property_mix": {
            "Apartment": 0.55,
            "Studio": 0.12,
            "Villa": 0.25,
            "Office": 0.08,
        },
    },
    "Nabeul": {
        "neighborhoods": [
            {"name": "Cite El Wafa", "lat": 36.4585, "lon": 10.7353},
            {"name": "Corniche", "lat": 36.4541, "lon": 10.7366},
            {"name": "Mrezga", "lat": 36.4444, "lon": 10.7332},
            {"name": "Dar Chaabane", "lat": 36.4692, "lon": 10.6960},
        ],
        "price_range": (165000, 420000),
        "demand_index": 0.98,
        "conversion_index": 0.89,
        "marketing_efficiency": 0.96,
        "seasonal_profile": "coastal_high",
        "property_mix": {
            "Apartment": 0.42,
            "Studio": 0.08,
            "Villa": 0.42,
            "Office": 0.08,
        },
    },
    "Hammamet": {
        "neighborhoods": [
            {"name": "Yasmine Hammamet", "lat": 36.3667, "lon": 10.5333},
            {"name": "Mrezga Sud", "lat": 36.4005, "lon": 10.6202},
            {"name": "Centre Hammamet", "lat": 36.4000, "lon": 10.6167},
            {"name": "Bir Bouregba", "lat": 36.4364, "lon": 10.5725},
        ],
        "price_range": (200000, 460000),
        "demand_index": 0.95,
        "conversion_index": 0.85,
        "marketing_efficiency": 0.94,
        "seasonal_profile": "coastal_high",
        "property_mix": {
            "Apartment": 0.36,
            "Studio": 0.06,
            "Villa": 0.50,
            "Office": 0.08,
        },
    },
    "Sfax": {
        "neighborhoods": [
            {"name": "Sakiet Ezzit", "lat": 34.8022, "lon": 10.7282},
            {"name": "El Ain", "lat": 34.7511, "lon": 10.6982},
            {"name": "Centre Ville", "lat": 34.7406, "lon": 10.7603},
            {"name": "Route Gremda", "lat": 34.7697, "lon": 10.6949},
        ],
        "price_range": (120000, 300000),
        "demand_index": 0.90,
        "conversion_index": 0.82,
        "marketing_efficiency": 0.78,
        "seasonal_profile": "stable",
        "property_mix": {
            "Apartment": 0.60,
            "Studio": 0.10,
            "Villa": 0.22,
            "Office": 0.08,
        },
    },
}

PROPERTY_TYPES = {
    "Apartment": {"price_multiplier": 1.00, "unit_range": (90, 250)},
    "Studio": {"price_multiplier": 0.72, "unit_range": (70, 200)},
    "Villa": {"price_multiplier": 1.45, "unit_range": (35, 110)},
    "Office": {"price_multiplier": 1.12, "unit_range": (45, 140)},
}

CHANNEL_ASSUMPTIONS = {
    "Google Search": {
        "volume_multiplier": 0.82,
        "quality_multiplier": 1.24,
        "visit_intent_multiplier": 1.10,
        "cpc_range": (1.80, 3.20),
        "ctr_range": (0.040, 0.080),
        "lead_rate_range": (0.10, 0.17),
        "active_probability": 0.86,
    },
    "Meta Ads": {
        "volume_multiplier": 1.36,
        "quality_multiplier": 0.84,
        "visit_intent_multiplier": 0.84,
        "cpc_range": (0.70, 1.45),
        "ctr_range": (0.015, 0.030),
        "lead_rate_range": (0.08, 0.13),
        "active_probability": 0.90,
    },
    "Property Portals": {
        "volume_multiplier": 0.98,
        "quality_multiplier": 1.08,
        "visit_intent_multiplier": 1.24,
        "cpc_range": (1.05, 2.05),
        "ctr_range": (0.020, 0.050),
        "lead_rate_range": (0.09, 0.16),
        "active_probability": 0.84,
    },
    "Referral": {
        "volume_multiplier": 0.44,
        "quality_multiplier": 1.16,
        "visit_intent_multiplier": 1.36,
        "cpc_range": (0.40, 0.90),
        "ctr_range": (0.030, 0.060),
        "lead_rate_range": (0.12, 0.21),
        "active_probability": 0.55,
    },
}

PROJECT_QUALITY_TIERS = {
    "strong": {
        "spend_multiplier": 1.24,
        "lead_quality_multiplier": 1.20,
        "conversion_multiplier": 1.16,
    },
    "average": {
        "spend_multiplier": 1.00,
        "lead_quality_multiplier": 1.00,
        "conversion_multiplier": 1.00,
    },
    "weak": {
        "spend_multiplier": 0.78,
        "lead_quality_multiplier": 0.82,
        "conversion_multiplier": 0.78,
    },
}

QUALITY_TIER_WEIGHTS = {
    "strong": 0.30,
    "average": 0.48,
    "weak": 0.22,
}

CONVERSION_ASSUMPTIONS = {
    "base_visit_probability": 0.33,
    "base_reservation_probability": 0.40,
    "base_sale_probability": 0.56,
    "qualified_score_threshold": 62.0,
    "price_penalty_strength": 0.24,
}


def ensure_data_directories() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, CURATED_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def generation_dates() -> pd.DatetimeIndex:
    return pd.date_range(
        DATE_RANGE["start"],
        DATE_RANGE["end"],
        freq=DATE_RANGE["frequency"],
    )


def campaign_dates() -> pd.DatetimeIndex:
    # Weekly campaign periods give enough trend signal while keeping data size practical.
    return pd.date_range(DATE_RANGE["start"], DATE_RANGE["end"], freq="W-MON")


def city_mid_price(city: str) -> float:
    low, high = CITY_CONFIGS[city]["price_range"]
    return (float(low) + float(high)) / 2.0


def seasonal_multiplier(city: str, current_date: pd.Timestamp) -> float:
    profile = CITY_CONFIGS[city]["seasonal_profile"]
    month = int(current_date.month)

    if profile == "stable":
        return 1.00
    if profile == "coastal_medium":
        if month in [6, 7, 8]:
            return 1.18
        if month in [11, 12, 1, 2]:
            return 0.90
        return 1.00
    if profile == "coastal_high":
        if month in [6, 7, 8, 9]:
            return 1.30
        if month in [11, 12, 1, 2]:
            return 0.78
        return 0.98
    return 1.00
