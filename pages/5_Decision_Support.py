import pandas as pd
import plotly.express as px
import streamlit as st

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
from src.presentation import (
    format_number,
    format_percentage,
    full_page_title,
    sorted_options,
)


def configure_page() -> None:
    st.set_page_config(page_title=full_page_title("Decision Support"), layout="wide")


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


def render_sidebar_filters(
    df: pd.DataFrame,
) -> tuple[list[str], list[str], list[str], list[str]]:
    st.sidebar.header("Filters")

    city_options = sorted_options(df, "city")
    property_type_options = sorted_options(df, "property_type")
    action_options = [action for action in DECISION_ACTIONS if action in df["recommended_action"].unique()]
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


def render_header() -> None:
    st.title("Decision Support")
    st.markdown(
        """
        Translate current performance, forecast momentum, and risk exposure into clear
        action priorities for each project.
        """
    )


def render_assumptions() -> None:
    with st.expander("Recommendation Methodology", expanded=False):
        for assumption in decision_support_assumptions():
            st.markdown(f"- {assumption}")


def render_summary_metrics(metrics: dict[str, float | int]) -> None:
    st.subheader("Decision Overview")
    columns = st.columns(5)
    columns[0].metric("Projects in Scope", format_number(metrics["project_count"]))
    columns[1].metric("High-Priority Opportunities", format_number(metrics["high_priority_opportunities"]))
    columns[2].metric(
        "Projects Needing Intervention",
        format_number(metrics["projects_needing_intervention"]),
    )
    columns[3].metric("Urgent Interventions", format_number(metrics["urgent_interventions"]))
    columns[4].metric("Average Priority Score", f"{float(metrics['average_priority_score']):.1f}")


def render_summary(insights: dict[str, object]) -> None:
    st.subheader("Strategic Summary")
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
    st.subheader("Recommendation Analytics")
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
        action_fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=390)
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
        priority_fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=390)
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
    city_fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=390)
    st.plotly_chart(city_fig, use_container_width=True)


def render_recommendation_table(df: pd.DataFrame) -> None:
    st.subheader("Ranked Recommendations")
    table_df = df[
        [
            "project_name",
            "city",
            "recommended_action",
            "recommendation_reason",
            "expected_impact",
            "confidence_level",
            "priority_score",
            "risk_level",
            "projected_demand_score",
            "projected_sales",
            "unsold_inventory",
        ]
    ].copy()

    table_df["priority_score"] = table_df["priority_score"].map(lambda value: f"{float(value):.1f}")
    table_df["projected_demand_score"] = table_df["projected_demand_score"].map(
        lambda value: f"{float(value):.1f}"
    )
    table_df["projected_sales"] = table_df["projected_sales"].map(format_number)
    table_df["unsold_inventory"] = table_df["unsold_inventory"].map(format_number)

    st.dataframe(
        table_df.rename(
            columns={
                "project_name": "Project",
                "city": "City",
                "recommended_action": "Recommended Action",
                "recommendation_reason": "Reason",
                "expected_impact": "Expected Impact",
                "confidence_level": "Confidence",
                "priority_score": "Priority Score",
                "risk_level": "Risk Level",
                "projected_demand_score": "Projected Demand Score",
                "projected_sales": "Projected Sales",
                "unsold_inventory": "Unsold Inventory",
            }
        ),
        use_container_width=True,
        hide_index=True,
        height=390,
    )


def render_city_breakdown_table(city_df: pd.DataFrame) -> None:
    st.subheader("City Decision Breakdown")
    table_df = city_df.copy()
    for column in [
        "project_count",
        "high_priority_projects",
        "projects_needing_intervention",
        "high_risk_projects",
    ]:
        table_df[column] = table_df[column].map(format_number)
    table_df["average_priority_score"] = table_df["average_priority_score"].map(
        lambda value: f"{float(value):.1f}"
    )
    table_df["top_action_share"] = table_df["top_action_share"].map(format_percentage)

    st.dataframe(
        table_df.rename(
            columns={
                "city": "City",
                "project_count": "Projects",
                "average_priority_score": "Average Priority Score",
                "high_priority_projects": "High Priority Projects",
                "projects_needing_intervention": "Projects Needing Intervention",
                "high_risk_projects": "High-Risk Projects",
                "top_recommended_action": "Top Recommended Action",
                "top_action_share": "Top Action Share",
            }
        ),
        use_container_width=True,
        hide_index=True,
        height=320,
    )


def main() -> None:
    configure_page()
    render_header()
    render_assumptions()

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

    st.caption(
        f"Projects included in decision support: {len(filtered_df):,} | Source: {source_display_name(data_source)} (`{source_path}`)"
    )
    render_summary_metrics(metrics)
    st.divider()
    render_summary(insights)
    st.divider()
    render_charts(action_df, city_df, filtered_df)
    st.divider()
    render_recommendation_table(filtered_df)
    st.divider()
    render_city_breakdown_table(city_df)


if __name__ == "__main__":
    main()
