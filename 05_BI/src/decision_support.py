"""Rule-based decision support utilities for the MVP.

This module transforms performance, forecast, and risk signals into concrete
project-level actions. Logic is intentionally transparent and deterministic so
it can be explained easily in a hackathon demo.
"""

from collections.abc import Iterable

import pandas as pd

from src.risk import RISK_OUTPUT_COLUMNS, calculate_project_risk

DECISION_REQUIRED_COLUMNS = [
    "project_name",
    "city",
    "neighborhood",
    "property_type",
    "ad_spend",
    "leads",
    "qualified_leads",
    "visits",
    "reservations",
    "sales",
    "unsold_inventory",
]

DECISION_ACTIONS = [
    "Increase Marketing",
    "Reduce Marketing",
    "Improve Targeting",
    "Review Pricing",
    "Delay Promotion",
    "Prioritize Sales Follow-up",
    "Monitor Closely",
]

INTERVENTION_ACTIONS = {
    "Reduce Marketing",
    "Improve Targeting",
    "Review Pricing",
    "Delay Promotion",
    "Prioritize Sales Follow-up",
}

DECISION_OUTPUT_COLUMNS = [
    "project_name",
    "city",
    "neighborhood",
    "property_type",
    "recommended_action",
    "recommendation_reason",
    "expected_impact",
    "confidence_level",
    "priority_score",
    "risk_score",
    "risk_level",
    "projected_demand_score",
    "projected_sales",
    "unsold_inventory",
    "current_sales",
    "current_leads",
    "qualified_lead_rate",
    "lead_to_visit_rate",
    "visit_to_reservation_rate",
    "cost_per_qualified_lead",
    "top_risk_drivers",
]

CITY_DECISION_COLUMNS = [
    "city",
    "project_count",
    "average_priority_score",
    "high_priority_projects",
    "projects_needing_intervention",
    "high_risk_projects",
    "top_recommended_action",
    "top_action_share",
]

DECISION_ASSUMPTIONS = [
    (
        "Recommendations are generated with transparent business rules using "
        "risk, demand outlook, conversion quality, and inventory pressure."
    ),
    (
        "Priority score reflects action urgency or upside potential on a 0-100 "
        "scale using weighted rule factors."
    ),
    (
        "Confidence level indicates how strongly project metrics match the "
        "selected action conditions (High / Medium / Low)."
    ),
]

ACTION_IMPACT_TEXT = {
    "Increase Marketing": "Expected to accelerate qualified pipeline and near-term sales momentum.",
    "Reduce Marketing": "Expected to reduce inefficient spend and preserve budget for stronger assets.",
    "Improve Targeting": "Expected to increase lead quality and reduce acquisition waste.",
    "Review Pricing": "Expected to improve inventory absorption and reservation momentum.",
    "Delay Promotion": "Expected to limit budget burn while demand and risk conditions stabilize.",
    "Prioritize Sales Follow-up": "Expected to improve visit-to-reservation and close conversion performance.",
    "Monitor Closely": "Expected to maintain performance while waiting for a clearer signal.",
}


def _validate_dataframe(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    if df is None:
        raise ValueError("Input DataFrame is None.")
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns for decision support: {missing_text}")


def _safe_divide(numerator: float | int, denominator: float | int) -> float:
    denominator_value = float(denominator)
    if denominator_value == 0:
        return 0.0
    return float(numerator) / denominator_value


def _normalize_series(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0.0)
    min_value = float(values.min()) if len(values) else 0.0
    max_value = float(values.max()) if len(values) else 0.0

    if max_value - min_value == 0:
        return pd.Series(0.5, index=values.index, dtype="float64")
    return (values - min_value) / (max_value - min_value)


def _confidence_from_strength(match_count: int, priority_score: float) -> str:
    if match_count >= 3 and priority_score >= 70:
        return "High"
    if match_count >= 2 or priority_score >= 58:
        return "Medium"
    return "Low"


def decision_support_assumptions() -> list[str]:
    return DECISION_ASSUMPTIONS.copy()


def _empty_decision_df() -> pd.DataFrame:
    return pd.DataFrame(columns=DECISION_OUTPUT_COLUMNS)


def _threshold_map(df: pd.DataFrame) -> dict[str, float]:
    return {
        "high_demand": float(df["projected_demand_score"].quantile(0.65)),
        "very_low_demand": float(df["projected_demand_score"].quantile(0.30)),
        "low_demand": float(df["projected_demand_score"].quantile(0.35)),
        "strong_leads": float(df["current_leads"].quantile(0.65)),
        "strong_visit_volume": float(df["current_visits"].quantile(0.50)),
        "high_inventory": float(df["unsold_inventory"].quantile(0.75)),
        "high_cpql": float(df["cost_per_qualified_lead"].quantile(0.70)),
        "low_projected_sales": float(df["projected_sales"].quantile(0.35)),
        "weak_qualified_rate": float(df["qualified_lead_rate"].quantile(0.35)),
        "healthy_qualified_rate": float(df["qualified_lead_rate"].quantile(0.50)),
        "strong_lead_to_visit": float(df["lead_to_visit_rate"].quantile(0.60)),
        "weak_visit_to_reservation": float(df["visit_to_reservation_rate"].quantile(0.50)),
    }


def _priority_score(row: pd.Series, action: str) -> float:
    risk_n = float(row["risk_score"]) / 100
    demand_n = float(row["projected_demand_score"]) / 100
    inventory_n = float(row["inventory_norm"])
    cpql_n = float(row["cpql_norm"])
    projected_sales_n = float(row["projected_sales_norm"])
    qualified_n = float(row["qualified_lead_rate"])
    lead_to_visit_n = float(row["lead_to_visit_rate"])
    visit_to_res_n = float(row["visit_to_reservation_rate"])

    if action == "Increase Marketing":
        score = 52 + 26 * demand_n + 14 * projected_sales_n + 8 * (1 - risk_n)
    elif action == "Delay Promotion":
        score = 56 + 24 * risk_n + 14 * (1 - demand_n) + 8 * inventory_n
    elif action == "Review Pricing":
        score = 52 + 18 * inventory_n + 16 * (1 - visit_to_res_n) + 14 * risk_n
    elif action == "Improve Targeting":
        score = 50 + 22 * (1 - qualified_n) + 14 * cpql_n + 10 * risk_n
    elif action == "Prioritize Sales Follow-up":
        score = 50 + 20 * lead_to_visit_n + 16 * (1 - visit_to_res_n) + 10 * risk_n
    elif action == "Reduce Marketing":
        score = 48 + 18 * cpql_n + 18 * (1 - demand_n) + 12 * risk_n
    else:  # Monitor Closely
        score = 42 + 12 * risk_n + 8 * inventory_n

    return round(min(100.0, max(30.0, score)), 1)


def _recommend_for_row(row: pd.Series, thresholds: dict[str, float]) -> dict[str, str | float]:
    high_risk = str(row["risk_level"]) == "High"
    medium_risk = str(row["risk_level"]) == "Medium"
    low_risk = str(row["risk_level"]) == "Low"

    high_demand = float(row["projected_demand_score"]) >= thresholds["high_demand"]
    very_low_demand = float(row["projected_demand_score"]) <= thresholds["very_low_demand"]
    low_demand = float(row["projected_demand_score"]) <= thresholds["low_demand"]
    strong_leads = float(row["current_leads"]) >= thresholds["strong_leads"]
    strong_visit_volume = float(row["current_visits"]) >= thresholds["strong_visit_volume"]
    high_inventory = float(row["unsold_inventory"]) >= thresholds["high_inventory"]
    high_cpql = float(row["cost_per_qualified_lead"]) >= thresholds["high_cpql"]
    low_projected_sales = float(row["projected_sales"]) <= thresholds["low_projected_sales"]
    weak_qualified_rate = (
        float(row["qualified_lead_rate"]) <= thresholds["weak_qualified_rate"]
    )
    healthy_qualified_rate = (
        float(row["qualified_lead_rate"]) >= thresholds["healthy_qualified_rate"]
    )
    strong_lead_to_visit = (
        float(row["lead_to_visit_rate"]) >= thresholds["strong_lead_to_visit"]
    )
    weak_visit_to_reservation = (
        float(row["visit_to_reservation_rate"]) <= thresholds["weak_visit_to_reservation"]
    )

    action = "Monitor Closely"
    reason = "Signals are mixed; maintain current plan while tracking changes closely."
    match_count = 1

    # Rule ordering prioritizes budget protection and inventory risk first.
    if high_risk and very_low_demand and high_inventory:
        action = "Delay Promotion"
        reason = (
            "Demand outlook is weak while risk and inventory exposure are high, "
            "so additional promotion is likely inefficient."
        )
        match_count = sum([high_risk, very_low_demand, high_inventory])
    elif high_inventory and weak_visit_to_reservation and low_projected_sales:
        action = "Review Pricing"
        reason = (
            "Inventory remains elevated and downstream conversion is weak, "
            "indicating pricing/offer structure may be limiting take-up."
        )
        match_count = sum([high_inventory, weak_visit_to_reservation, low_projected_sales])
    elif strong_visit_volume and weak_visit_to_reservation:
        action = "Prioritize Sales Follow-up"
        reason = (
            "Visit volume is healthy but reservation conversion is lagging, "
            "so sales follow-up discipline should be prioritized."
        )
        match_count = sum([strong_visit_volume, weak_visit_to_reservation])
    elif (strong_leads or high_cpql) and weak_qualified_rate:
        action = "Improve Targeting"
        reason = (
            "Lead volume is present but qualification quality is weak, "
            "suggesting audience targeting and channel mix should be refined."
        )
        match_count = sum([strong_leads or high_cpql, weak_qualified_rate])
    elif strong_lead_to_visit and weak_visit_to_reservation:
        action = "Prioritize Sales Follow-up"
        reason = (
            "Traffic reaches visits but fails to convert well into reservations, "
            "indicating follow-up quality and sales process need attention."
        )
        match_count = sum([strong_lead_to_visit, weak_visit_to_reservation])
    elif high_demand and low_risk and healthy_qualified_rate:
        action = "Increase Marketing"
        reason = (
            "Demand projection is strong with controlled risk and healthy lead quality, "
            "supporting additional growth investment."
        )
        match_count = sum([high_demand, low_risk, healthy_qualified_rate])
    elif high_cpql and low_demand and (high_risk or medium_risk):
        action = "Reduce Marketing"
        reason = (
            "Acquisition is expensive while demand outlook is soft under elevated risk, "
            "so spend should be tightened until efficiency improves."
        )
        match_count = sum([high_cpql, low_demand, high_risk or medium_risk])

    priority = _priority_score(row, action)
    confidence = _confidence_from_strength(match_count=int(match_count), priority_score=priority)

    return {
        "recommended_action": action,
        "recommendation_reason": reason,
        "expected_impact": ACTION_IMPACT_TEXT[action],
        "confidence_level": confidence,
        "priority_score": priority,
    }


def calculate_project_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """Generate project-level recommendation actions from performance + risk context."""
    _validate_dataframe(df, DECISION_REQUIRED_COLUMNS)

    if df.empty:
        return _empty_decision_df()

    risk_df = calculate_project_risk(df)
    _validate_dataframe(risk_df, RISK_OUTPUT_COLUMNS)
    if risk_df.empty:
        return _empty_decision_df()

    work_df = risk_df.copy()
    join_keys = ["project_name", "city", "neighborhood", "property_type"]
    visits_df = df[join_keys + ["visits"]].copy()
    visits_df = visits_df.rename(columns={"visits": "current_visits"})
    work_df = work_df.merge(visits_df, on=join_keys, how="left")

    for column in [
        "risk_score",
        "projected_demand_score",
        "projected_sales",
        "unsold_inventory",
        "current_sales",
        "current_leads",
        "current_visits",
        "qualified_lead_rate",
        "lead_to_visit_rate",
        "visit_to_reservation_rate",
        "cost_per_qualified_lead",
    ]:
        work_df[column] = pd.to_numeric(work_df[column], errors="coerce").fillna(0.0)

    work_df["inventory_norm"] = _normalize_series(work_df["unsold_inventory"])
    work_df["cpql_norm"] = _normalize_series(work_df["cost_per_qualified_lead"])
    work_df["projected_sales_norm"] = _normalize_series(work_df["projected_sales"])

    thresholds = _threshold_map(work_df)
    recommendation_df = work_df.apply(
        lambda row: pd.Series(_recommend_for_row(row, thresholds)), axis=1
    )
    output_df = pd.concat([work_df, recommendation_df], axis=1)

    return output_df[DECISION_OUTPUT_COLUMNS].sort_values(
        by=["priority_score", "risk_score", "projected_demand_score"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def decision_overview_metrics(decision_df: pd.DataFrame) -> dict[str, float | int]:
    _validate_dataframe(decision_df, DECISION_OUTPUT_COLUMNS)

    if decision_df.empty:
        return {
            "project_count": 0,
            "high_priority_opportunities": 0,
            "projects_needing_intervention": 0,
            "urgent_interventions": 0,
            "average_priority_score": 0.0,
            "high_risk_projects": 0,
        }

    high_priority_opportunities = int(
        (
            (decision_df["recommended_action"] == "Increase Marketing")
            & (pd.to_numeric(decision_df["priority_score"], errors="coerce") >= 70)
        ).sum()
    )
    projects_needing_intervention = int(
        decision_df["recommended_action"].isin(INTERVENTION_ACTIONS).sum()
    )
    urgent_interventions = int(
        (
            decision_df["recommended_action"].isin(INTERVENTION_ACTIONS)
            & (pd.to_numeric(decision_df["priority_score"], errors="coerce") >= 70)
        ).sum()
    )

    return {
        "project_count": int(len(decision_df)),
        "high_priority_opportunities": high_priority_opportunities,
        "projects_needing_intervention": projects_needing_intervention,
        "urgent_interventions": urgent_interventions,
        "average_priority_score": float(
            pd.to_numeric(decision_df["priority_score"], errors="coerce").fillna(0).mean()
        ),
        "high_risk_projects": int((decision_df["risk_level"] == "High").sum()),
    }


def decision_action_breakdown(decision_df: pd.DataFrame) -> pd.DataFrame:
    _validate_dataframe(decision_df, DECISION_OUTPUT_COLUMNS)
    if decision_df.empty:
        return pd.DataFrame(columns=["recommended_action", "project_count", "average_priority_score"])

    breakdown_df = (
        decision_df.groupby("recommended_action", as_index=False)
        .agg(
            project_count=("project_name", "count"),
            average_priority_score=("priority_score", "mean"),
        )
        .copy()
    )
    breakdown_df["average_priority_score"] = breakdown_df["average_priority_score"].round(1)

    action_order = {action: idx for idx, action in enumerate(DECISION_ACTIONS)}
    breakdown_df["action_order"] = breakdown_df["recommended_action"].map(action_order).fillna(99)
    return breakdown_df.sort_values(
        by=["project_count", "average_priority_score", "action_order"],
        ascending=[False, False, True],
    ).drop(columns=["action_order"]).reset_index(drop=True)


def decision_city_breakdown(decision_df: pd.DataFrame) -> pd.DataFrame:
    _validate_dataframe(decision_df, DECISION_OUTPUT_COLUMNS)
    if decision_df.empty:
        return pd.DataFrame(columns=CITY_DECISION_COLUMNS)

    city_df = (
        decision_df.groupby("city", as_index=False)
        .agg(
            project_count=("project_name", "count"),
            average_priority_score=("priority_score", "mean"),
            high_priority_projects=("priority_score", lambda values: int((values >= 70).sum())),
            projects_needing_intervention=(
                "recommended_action",
                lambda values: int(pd.Series(values).isin(INTERVENTION_ACTIONS).sum()),
            ),
            high_risk_projects=("risk_level", lambda values: int((values == "High").sum())),
        )
        .copy()
    )
    city_df["average_priority_score"] = city_df["average_priority_score"].round(1)

    city_action_counts = (
        decision_df.groupby(["city", "recommended_action"]).size().reset_index(name="action_count")
    )
    city_action_counts = city_action_counts.sort_values(
        by=["city", "action_count"], ascending=[True, False]
    )
    top_actions_df = city_action_counts.groupby("city", as_index=False).first()
    top_actions_df = top_actions_df.rename(
        columns={"recommended_action": "top_recommended_action"}
    )

    city_df = city_df.merge(top_actions_df[["city", "top_recommended_action", "action_count"]], on="city")
    city_df["top_action_share"] = city_df.apply(
        lambda row: _safe_divide(row["action_count"], row["project_count"]), axis=1
    )
    city_df = city_df.drop(columns=["action_count"])

    return city_df[CITY_DECISION_COLUMNS].sort_values(
        by=["high_priority_projects", "average_priority_score"],
        ascending=[False, False],
    ).reset_index(drop=True)


def decision_summary_insights(decision_df: pd.DataFrame) -> dict[str, object]:
    _validate_dataframe(decision_df, DECISION_OUTPUT_COLUMNS)

    if decision_df.empty:
        return {
            "top_opportunity_project": None,
            "most_at_risk_project": None,
            "most_common_action": None,
            "observations": [
                "No projects match the selected filters, so decision insights are unavailable."
            ],
        }

    opportunity_df = decision_df[
        (decision_df["recommended_action"] == "Increase Marketing")
        & (decision_df["risk_level"] != "High")
    ].sort_values(by=["priority_score", "projected_demand_score"], ascending=[False, False])
    if opportunity_df.empty:
        opportunity_df = decision_df.sort_values(
            by=["projected_demand_score", "priority_score"], ascending=[False, False]
        )

    at_risk_df = decision_df[
        decision_df["recommended_action"].isin(INTERVENTION_ACTIONS)
    ].sort_values(by=["risk_score", "priority_score"], ascending=[False, False])
    if at_risk_df.empty:
        at_risk_df = decision_df.sort_values(
            by=["risk_score", "priority_score"], ascending=[False, False]
        )

    top_opportunity = opportunity_df.iloc[0]
    most_at_risk = at_risk_df.iloc[0]
    most_common_action = str(decision_df["recommended_action"].value_counts().idxmax())

    metrics = decision_overview_metrics(decision_df)
    observations = [
        (
            f"{metrics['projects_needing_intervention']:,.0f} projects require intervention actions, "
            f"with {metrics['urgent_interventions']:,.0f} flagged as urgent."
        ),
        (
            f"The dominant action is '{most_common_action}', indicating a portfolio-wide "
            "need for consistent operational focus."
        ),
    ]

    return {
        "top_opportunity_project": top_opportunity.to_dict(),
        "most_at_risk_project": most_at_risk.to_dict(),
        "most_common_action": most_common_action,
        "observations": observations,
    }
