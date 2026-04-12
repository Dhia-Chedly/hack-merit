"""AI insights engine for compact, prompt-driven dashboard analysis.

This module builds a compact business context from dashboard data and sends
that context to Gemini for concise executive insight generation.

Design goals:
- Keep token usage efficient by summarizing data instead of sending full tables.
- Keep outputs explainable and business-friendly.
- Enforce prompt constraints so model responses stay grounded in provided data.
"""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from src.decision_support import calculate_project_recommendations
from src.forecasting import forecast_city_summary, forecast_projects
from src.gemini_client import generate_text
from src.kpis import (
    calculate_kpis,
    calculate_marketing_kpis,
    city_marketing_breakdown,
)
from src.risk import calculate_project_risk, risk_city_breakdown


def _to_python_number(value: Any) -> Any:
    """Convert pandas/numpy numeric values into plain Python scalars."""
    if pd.isna(value):
        return None
    if isinstance(value, (int, bool)):
        return int(value)
    if isinstance(value, float):
        return round(value, 4)
    return value


def _records(df: pd.DataFrame, columns: list[str], *, top_n: int, sort_by: str | None) -> list[dict[str, Any]]:
    """Create compact serializable records for prompt context."""
    if df.empty:
        return []

    work_df = df.copy()
    if sort_by and sort_by in work_df.columns:
        work_df = work_df.sort_values(sort_by, ascending=False)

    work_df = work_df.head(top_n)
    output: list[dict[str, Any]] = []
    for _, row in work_df.iterrows():
        output.append({column: _to_python_number(row[column]) for column in columns if column in row})
    return output


def context_to_json(context: dict[str, Any]) -> str:
    """Serialize context to JSON for Gemini prompts."""
    return json.dumps(context, ensure_ascii=False, separators=(",", ":"), default=str)


def build_dashboard_context(
    projects_df: pd.DataFrame,
    *,
    top_n: int = 6,
    source_label: str | None = None,
    source_path: str | None = None,
) -> dict[str, Any]:
    """Build compact dashboard context for AI prompts.

    The context intentionally includes only high-signal slices:
    headline KPIs, city summary, top projects, top risks, forecast leaders,
    and recommendation leaders.
    """
    if projects_df is None or not isinstance(projects_df, pd.DataFrame):
        raise ValueError("projects_df must be a pandas DataFrame.")
    if projects_df.empty:
        raise ValueError("projects_df is empty. AI context cannot be built.")

    base_kpis = calculate_kpis(projects_df)
    marketing_kpis = calculate_marketing_kpis(projects_df)

    city_marketing_df = city_marketing_breakdown(projects_df)
    project_forecast_df = forecast_projects(projects_df)
    city_forecast_df = forecast_city_summary(project_forecast_df)
    risk_df = calculate_project_risk(projects_df)
    city_risk_df = risk_city_breakdown(risk_df)
    decision_df = calculate_project_recommendations(projects_df)

    city_summary_df = city_marketing_df[
        [
            "city",
            "leads",
            "qualified_lead_rate",
            "cost_per_qualified_lead",
            "reservation_to_sale_rate",
            "marketing_performance",
        ]
    ].merge(
        city_forecast_df[
            [
                "city",
                "projected_demand_score",
                "projected_sales_growth_rate",
            ]
        ],
        on="city",
        how="left",
    )
    city_summary_df = city_summary_df.merge(
        city_risk_df[["city", "average_risk_score", "high_risk_share"]],
        on="city",
        how="left",
    )

    join_keys = ["project_name", "city", "neighborhood", "property_type"]
    project_summary_df = projects_df[
        join_keys + ["leads", "qualified_leads", "sales", "unsold_inventory", "avg_price"]
    ].merge(
        decision_df[join_keys + ["recommended_action", "priority_score", "confidence_level"]],
        on=join_keys,
        how="left",
    )

    context: dict[str, Any] = {
        "scope": {
            "projects": int(len(projects_df)),
            "cities": int(projects_df["city"].nunique()),
            "property_types": int(projects_df["property_type"].nunique()),
            "data_source": source_label,
            "source_path": source_path,
        },
        "headline_kpis": {
            "total_leads": int(base_kpis["total_leads"]),
            "total_qualified_leads": int(base_kpis["total_qualified_leads"]),
            "qualified_lead_rate": _to_python_number(base_kpis["qualified_lead_rate"]),
            "total_sales": int(base_kpis["total_sales"]),
            "total_unsold_inventory": int(base_kpis["total_unsold_inventory"]),
            "average_property_price": _to_python_number(base_kpis["average_property_price"]),
            "visit_to_reservation_rate": _to_python_number(base_kpis["visit_to_reservation_rate"]),
            "total_ad_spend": _to_python_number(marketing_kpis["total_ad_spend"]),
            "cost_per_lead": _to_python_number(marketing_kpis["cost_per_lead"]),
            "cost_per_qualified_lead": _to_python_number(marketing_kpis["cost_per_qualified_lead"]),
            "reservation_to_sale_rate": _to_python_number(marketing_kpis["reservation_to_sale_rate"]),
        },
        "city_summary": _records(
            city_summary_df,
            [
                "city",
                "leads",
                "qualified_lead_rate",
                "cost_per_qualified_lead",
                "reservation_to_sale_rate",
                "marketing_performance",
                "projected_demand_score",
                "projected_sales_growth_rate",
                "average_risk_score",
                "high_risk_share",
            ],
            top_n=top_n,
            sort_by="leads",
        ),
        "top_projects": _records(
            project_summary_df,
            [
                "project_name",
                "city",
                "property_type",
                "leads",
                "qualified_leads",
                "sales",
                "unsold_inventory",
                "avg_price",
                "recommended_action",
                "priority_score",
                "confidence_level",
            ],
            top_n=top_n,
            sort_by="leads",
        ),
        "top_risks": _records(
            risk_df,
            [
                "project_name",
                "city",
                "risk_score",
                "risk_level",
                "top_risk_drivers",
                "unsold_inventory",
                "projected_sales",
                "projected_demand_score",
            ],
            top_n=top_n,
            sort_by="risk_score",
        ),
        "top_forecast_signals": _records(
            project_forecast_df,
            [
                "project_name",
                "city",
                "projected_demand_score",
                "projected_sales",
                "projected_sales_growth_rate",
                "projected_leads",
                "unsold_inventory",
            ],
            top_n=top_n,
            sort_by="projected_demand_score",
        ),
        "top_recommendations": _records(
            decision_df,
            [
                "project_name",
                "city",
                "recommended_action",
                "priority_score",
                "confidence_level",
                "risk_level",
                "projected_demand_score",
                "projected_sales",
                "unsold_inventory",
            ],
            top_n=top_n,
            sort_by="priority_score",
        ),
    }

    return context


def _extract_json_payload(raw_text: str) -> dict[str, Any]:
    """Parse JSON robustly from a model response that may include wrappers."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Gemini returned non-JSON output.")
        return json.loads(cleaned[start : end + 1])


def _normalize_items(values: Any, *, target_count: int, fallback: str) -> list[str]:
    """Ensure fixed-length bullet outputs for consistent UI rendering."""
    if not isinstance(values, list):
        values = []

    normalized: list[str] = []
    for value in values:
        text = str(value).strip()
        if text:
            normalized.append(text)
        if len(normalized) == target_count:
            break

    while len(normalized) < target_count:
        normalized.append(fallback)

    return normalized


def _build_insight_prompt(context: dict[str, Any], *, focus: str) -> str:
    """Construct strict prompt for executive insight generation."""
    return f"""
You are a BI analyst for a Tunisia real-estate demand intelligence platform.

Task focus: {focus}

Rules:
1. Use only the provided data context.
2. Do not invent numbers or projects.
3. If context is insufficient, explicitly say what is missing.
4. Keep language concise, business-friendly, and practical.
5. Output must be valid JSON only (no markdown).

Return this exact schema:
{{
  "key_insights": ["...", "...", "..."],
  "main_risks": ["...", "..."],
  "recommended_actions": ["...", "..."]
}}

Data context (JSON):
{context_to_json(context)}
""".strip()


def generate_structured_insights(
    context: dict[str, Any],
    *,
    focus: str = "Executive overview",
) -> dict[str, list[str]]:
    """Generate structured insights with fixed output counts.

    Returns:
        {
            "key_insights": [3 items],
            "main_risks": [2 items],
            "recommended_actions": [2 items],
        }
    """
    prompt = _build_insight_prompt(context, focus=focus)
    raw_output = generate_text(prompt)

    parsed = _extract_json_payload(raw_output)
    return {
        "key_insights": _normalize_items(
            parsed.get("key_insights"),
            target_count=3,
            fallback="Insufficient context for a reliable additional insight.",
        ),
        "main_risks": _normalize_items(
            parsed.get("main_risks"),
            target_count=2,
            fallback="Insufficient context for a reliable additional risk statement.",
        ),
        "recommended_actions": _normalize_items(
            parsed.get("recommended_actions"),
            target_count=2,
            fallback="Insufficient context for a reliable additional action recommendation.",
        ),
    }


def generate_focus_brief(context: dict[str, Any], *, topic: str) -> str:
    """Generate a concise topic-specific narrative from compact dashboard context."""
    prompt = f"""
You are a BI analyst for a Tunisia real-estate demand intelligence platform.

Topic: {topic}

Rules:
- Use only the provided data context.
- Never invent numbers or entities.
- If context is insufficient, state the limitation clearly.
- Provide 4 concise bullet points in plain business language.
- Start each line with '- '.

Data context (JSON):
{context_to_json(context)}
""".strip()

    return generate_text(prompt)
