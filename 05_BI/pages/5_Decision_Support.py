import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard_ui import (
    apply_dashboard_theme,
    dashboard_panel,
    render_kpi_cards,
    render_page_hero,
    render_sidebar_block,
    render_source_chip,
    style_plotly_figure,
)
from src.data_loader import load_projects_data_with_metadata
from src.decision_support import (
    DECISION_ACTIONS,
    calculate_project_recommendations,
    decision_action_breakdown,
    decision_city_breakdown,
    decision_overview_metrics,
    decision_summary_insights,
    decision_support_assumptions,
)
from src.presentation import format_number, full_page_title, sorted_options


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("Decision Support"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()


def source_display_name(source: str) -> str:
    return "Curated project metrics" if source == "curated" else "Legacy projects dataset"


def load_decision_data() -> tuple[pd.DataFrame, str, str] | None:
    try:
        projects_df, source, source_path = load_projects_data_with_metadata()
        decision_df = calculate_project_recommendations(projects_df)
        return decision_df, source, str(source_path)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to load decision support data: {error}")
        st.info(
            "Please verify `data/curated/project_metrics.csv` or `data/projects.csv` and decision support modules."
        )
        return None


def render_header() -> None:
    render_page_hero(
        "Decision Support",
        "Convert performance, forecast, and risk signals into clear project-level actions with explainable reasoning and priority scoring.",
    )


def render_sidebar_filters(
    df: pd.DataFrame,
) -> tuple[list[str], list[str], list[str], list[str]]:
    render_sidebar_block(
        "Decision Controls",
        "Refine recommendations by city, asset type, action type, and risk level.",
    )

    city_options = sorted_options(df, "city")
    property_type_options = sorted_options(df, "property_type")
    action_options = [
        action for action in DECISION_ACTIONS if action in df["recommended_action"].unique()
    ]
    risk_options = [level for level in ["High", "Medium", "Low"] if level in df["risk_level"].unique()]

    selected_cities = st.sidebar.multiselect("Cities", options=city_options, default=city_options)
    selected_property_types = st.sidebar.multiselect(
        "Property Types",
        options=property_type_options,
        default=property_type_options,
    )
    selected_actions = st.sidebar.multiselect(
        "Recommended Actions",
        options=action_options,
        default=action_options,
    )
    selected_risk_levels = st.sidebar.multiselect(
        "Risk Levels",
        options=risk_options,
        default=risk_options,
    )
    return selected_cities, selected_property_types, selected_actions, selected_risk_levels


def apply_filters(
    df: pd.DataFrame,
    selected_cities: list[str],
    selected_property_types: list[str],
    selected_actions: list[str],
    selected_risk_levels: list[str],
) -> pd.DataFrame:
    filtered_df = df[df["city"].isin(selected_cities)]
    filtered_df = filtered_df[filtered_df["property_type"].isin(selected_property_types)]
    filtered_df = filtered_df[filtered_df["recommended_action"].isin(selected_actions)]
    filtered_df = filtered_df[filtered_df["risk_level"].isin(selected_risk_levels)]
    return filtered_df.copy()


def render_assumptions() -> None:
    with st.expander("Recommendation Methodology", expanded=False):
        for assumption in decision_support_assumptions():
            st.markdown(f"- {assumption}")


def render_summary_metrics(metrics: dict[str, float | int]) -> None:
    cards = [
        {
            "label": "Projects in Scope",
            "value": format_number(metrics["project_count"]),
            "subtext": "Filtered portfolio under decision analysis",
        },
        {
            "label": "High-Priority Opportunities",
            "value": format_number(metrics["high_priority_opportunities"]),
            "subtext": "Projects suited for growth investment",
        },
        {
            "label": "Projects Needing Intervention",
            "value": format_number(metrics["projects_needing_intervention"]),
            "subtext": "Assets requiring corrective action",
        },
        {
            "label": "Urgent Interventions",
            "value": format_number(metrics["urgent_interventions"]),
            "subtext": "Interventions with high urgency score",
        },
        {
            "label": "Average Priority Score",
            "value": f"{float(metrics['average_priority_score']):.1f}",
            "delta": format_number(metrics["urgent_interventions"]),
            "subtext": "Urgent interventions",
        },
    ]
    render_kpi_cards(cards, columns=5)


def render_summary(insights: dict[str, object]) -> None:
    top_opportunity = insights.get("top_opportunity_project")
    at_risk_project = insights.get("most_at_risk_project")
    most_common_action = insights.get("most_common_action")
    observations = insights.get("observations", [])

    if isinstance(top_opportunity, dict):
        st.markdown(
            "- Top opportunity project: "
            f"**{top_opportunity['project_name']} ({top_opportunity['city']})** with action "
            f"**{top_opportunity['recommended_action']}**, priority **{top_opportunity['priority_score']:.1f}**, "
            f"and projected demand score **{top_opportunity['projected_demand_score']:.1f}**."
        )
    if isinstance(at_risk_project, dict):
        st.markdown(
            "- Most at-risk project needing action: "
            f"**{at_risk_project['project_name']} ({at_risk_project['city']})** with risk "
            f"**{at_risk_project['risk_level']} ({at_risk_project['risk_score']:.1f})** and recommended action "
            f"**{at_risk_project['recommended_action']}**."
        )
    if isinstance(most_common_action, str):
        st.markdown(f"- Most common recommended action: **{most_common_action}**.")
    if isinstance(observations, list):
        for observation in observations[:2]:
            st.markdown(f"- {observation}")


def render_charts(action_df: pd.DataFrame, city_df: pd.DataFrame, project_df: pd.DataFrame) -> None:
    col_actions, col_priority = st.columns(2)

    with col_actions:
        action_fig = px.bar(
            action_df.sort_values("project_count", ascending=True),
            x="project_count",
            y="recommended_action",
            orientation="h",
            text="project_count",
            labels={"project_count": "Projects", "recommended_action": "Recommended Action"},
            title="Action Distribution",
            color="average_priority_score",
            color_continuous_scale="Blues",
        )
        style_plotly_figure(action_fig, height=370)
        st.plotly_chart(action_fig, use_container_width=True)

    with col_priority:
        top_projects = project_df.nlargest(min(10, len(project_df)), "priority_score").copy()
        priority_fig = px.bar(
            top_projects.sort_values("priority_score", ascending=True),
            x="priority_score",
            y="project_name",
            orientation="h",
            color="recommended_action",
            labels={"priority_score": "Priority Score", "project_name": "Project"},
            hover_data={
                "city": True,
                "risk_level": True,
                "projected_demand_score": ":.1f",
                "projected_sales": ":,.0f",
            },
            title="Top Priority Projects",
            text="priority_score",
        )
        priority_fig.update_traces(texttemplate="%{x:.1f}", textposition="outside")
        style_plotly_figure(priority_fig, height=370)
        st.plotly_chart(priority_fig, use_container_width=True)

    city_fig = px.bar(
        city_df.sort_values("high_priority_projects", ascending=False),
        x="city",
        y="high_priority_projects",
        color="top_recommended_action",
        labels={
            "city": "City",
            "high_priority_projects": "High Priority Projects",
            "top_recommended_action": "Top Action",
        },
        title="High-Priority Projects by City",
        hover_data={
            "average_priority_score": ":.1f",
            "projects_needing_intervention": True,
            "high_risk_projects": True,
            "top_action_share": ":.1%",
        },
    )
    style_plotly_figure(city_fig, height=370)
    st.plotly_chart(city_fig, use_container_width=True)


def render_recommendation_charts(df: pd.DataFrame) -> None:
    col_priority, col_action = st.columns(2)

    with col_priority:
        priority_fig = px.scatter(
            df,
            x="projected_demand_score",
            y="priority_score",
            size="unsold_inventory",
            color="recommended_action",
            symbol="risk_level",
            hover_name="project_name",
            hover_data={
                "city": True,
                "projected_sales": ":,.0f",
                "confidence_level": True,
            },
            labels={
                "projected_demand_score": "Projected Demand Score",
                "priority_score": "Priority Score",
                "unsold_inventory": "Unsold Inventory",
                "recommended_action": "Recommended Action",
                "risk_level": "Risk Level",
            },
            title="Priority vs Demand by Project",
        )
        style_plotly_figure(priority_fig, height=380)
        st.plotly_chart(priority_fig, use_container_width=True)

    with col_action:
        action_flow = px.sunburst(
            df,
            path=[px.Constant("Portfolio"), "city", "recommended_action"],
            values="priority_score",
            color="risk_score",
            color_continuous_scale="Plasma",
            hover_data={
                "projected_sales": ":,.0f",
                "unsold_inventory": ":,.0f",
            },
            title="Action Distribution by City and Priority Weight",
        )
        style_plotly_figure(action_flow, height=380)
        st.plotly_chart(action_flow, use_container_width=True)


def render_city_breakdown_charts(city_df: pd.DataFrame) -> None:
    col_volume, col_focus = st.columns(2)

    with col_volume:
        city_metric_df = city_df.melt(
            id_vars="city",
            value_vars=[
                "high_priority_projects",
                "projects_needing_intervention",
                "high_risk_projects",
            ],
            var_name="metric",
            value_name="metric_value",
        )
        city_metric_df["metric"] = city_metric_df["metric"].replace(
            {
                "high_priority_projects": "High Priority Projects",
                "projects_needing_intervention": "Projects Needing Intervention",
                "high_risk_projects": "High-Risk Projects",
            }
        )
        city_fig = px.bar(
            city_metric_df,
            x="city",
            y="metric_value",
            color="metric",
            barmode="group",
            labels={"city": "City", "metric_value": "Projects", "metric": "Metric"},
            title="City Action Volume by Strategic Metric",
        )
        style_plotly_figure(city_fig, height=350)
        st.plotly_chart(city_fig, use_container_width=True)

    with col_focus:
        focus_fig = px.scatter(
            city_df,
            x="top_action_share",
            y="average_priority_score",
            size="project_count",
            color="top_recommended_action",
            hover_name="city",
            hover_data={
                "high_priority_projects": True,
                "projects_needing_intervention": True,
            },
            labels={
                "top_action_share": "Top Action Share",
                "average_priority_score": "Average Priority Score",
                "project_count": "Projects",
                "top_recommended_action": "Top Recommended Action",
            },
            title="City Focus Map: Action Concentration vs Priority",
        )
        focus_fig.update_xaxes(tickformat=".0%")
        style_plotly_figure(focus_fig, height=350)
        st.plotly_chart(focus_fig, use_container_width=True)


def main() -> None:
    configure_page()
    render_header()

    load_result = load_decision_data()
    if load_result is None:
        return
    decision_df, data_source, source_path = load_result

    selected_cities, selected_property_types, selected_actions, selected_risk_levels = (
        render_sidebar_filters(decision_df)
    )
    filtered_df = apply_filters(
        decision_df,
        selected_cities,
        selected_property_types,
        selected_actions,
        selected_risk_levels,
    )
    if filtered_df.empty:
        st.warning("No projects match the selected filters. Adjust the filters and try again.")
        return

    action_df = decision_action_breakdown(filtered_df)
    city_df = decision_city_breakdown(filtered_df)
    metrics = decision_overview_metrics(filtered_df)
    insights = decision_summary_insights(filtered_df)

    render_source_chip(
        f"Source: {source_display_name(data_source)} | {len(filtered_df):,} rows | {source_path}"
    )

    with dashboard_panel("Decision KPI Overview", "Action urgency and opportunity concentration at a glance."):
        render_summary_metrics(metrics)

    with dashboard_panel("Recommendation Methodology", "Transparent rule-based logic used to generate actions."):
        render_assumptions()

    with dashboard_panel("Strategic Decision Summary", "Top opportunities, intervention priorities, and portfolio signals."):
        render_summary(insights)

    with dashboard_panel("Recommendation Analytics", "Action mix, top priority projects, and city opportunity concentration."):
        render_charts(action_df, city_df, filtered_df)

    with dashboard_panel(
        "Recommendation Signals",
        "Project-level recommendation dynamics replacing static ranked tables.",
    ):
        render_recommendation_charts(filtered_df)

    with dashboard_panel(
        "City Decision Breakdown",
        "City-level action concentration and strategic workload visuals.",
    ):
        render_city_breakdown_charts(city_df)


if __name__ == "__main__":
    main()
