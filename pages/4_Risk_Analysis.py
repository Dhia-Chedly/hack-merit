import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_projects_data_with_metadata
from src.presentation import (
    format_number,
    format_percentage,
    full_page_title,
    sorted_options,
)
from src.risk import (
    calculate_project_risk,
    risk_city_breakdown,
    risk_overview_metrics,
    risk_scoring_assumptions,
    risk_summary_insights,
)


def configure_page() -> None:
    st.set_page_config(page_title=full_page_title("Risk Analysis"), layout="wide")


def source_display_name(source: str) -> str:
    return "Curated project metrics" if source == "curated" else "Legacy projects dataset"


def load_risk_data() -> tuple[pd.DataFrame, str, str] | None:
    try:
        projects_df, source, source_path = load_projects_data_with_metadata()
        risk_df = calculate_project_risk(projects_df)
        return risk_df, source, str(source_path)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to load risk analysis data: {error}")
        st.info(
            "Please verify `data/curated/project_metrics.csv` or `data/projects.csv` and supporting calculation modules."
        )
        return None


def render_sidebar_filters(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    st.sidebar.header("Filters")

    city_options = sorted_options(df, "city")
    property_type_options = sorted_options(df, "property_type")
    risk_level_options = [level for level in ["High", "Medium", "Low"] if level in df["risk_level"].unique()]

    selected_cities = st.sidebar.multiselect("Cities", options=city_options, default=city_options)
    selected_property_types = st.sidebar.multiselect(
        "Property Types",
        options=property_type_options,
        default=property_type_options,
    )
    selected_risk_levels = st.sidebar.multiselect(
        "Risk Levels",
        options=risk_level_options,
        default=risk_level_options,
    )
    return selected_cities, selected_property_types, selected_risk_levels


def apply_filters(
    df: pd.DataFrame,
    selected_cities: list[str],
    selected_property_types: list[str],
    selected_risk_levels: list[str],
) -> pd.DataFrame:
    filtered_df = df[df["city"].isin(selected_cities)]
    filtered_df = filtered_df[filtered_df["property_type"].isin(selected_property_types)]
    filtered_df = filtered_df[filtered_df["risk_level"].isin(selected_risk_levels)]
    return filtered_df.copy()


def render_header() -> None:
    st.title("Risk Analysis")
    st.markdown(
        """
        Identify projects and cities with elevated commercial risk using a transparent score
        based on lead quality, conversion efficiency, inventory pressure, and forecast weakness.
        """
    )


def render_assumptions() -> None:
    with st.expander("Risk Scoring Methodology", expanded=False):
        for assumption in risk_scoring_assumptions():
            st.markdown(f"- {assumption}")


def render_summary_metrics(metrics: dict[str, float | int]) -> None:
    st.subheader("Risk Overview")
    columns = st.columns(5)

    columns[0].metric("Projects in Scope", format_number(metrics["project_count"]))
    columns[1].metric("High-Risk Projects", format_number(metrics["high_risk_projects"]))
    columns[2].metric("Medium-Risk Projects", format_number(metrics["medium_risk_projects"]))
    columns[3].metric("Low-Risk Projects", format_number(metrics["low_risk_projects"]))
    columns[4].metric("Average Risk Score", f"{float(metrics['average_risk_score']):.1f}")
    st.caption(f"High-risk share: {format_percentage(metrics['high_risk_share'])}")


def render_summary(insights: dict[str, object]) -> None:
    st.subheader("Strategic Summary")

    highest_risk_city = insights.get("highest_risk_city")
    highest_risk_project = insights.get("highest_risk_project")
    common_drivers = insights.get("most_common_risk_drivers", [])
    observations = insights.get("observations", [])

    if isinstance(highest_risk_city, dict):
        st.markdown(
            "- Highest-risk city: "
            f"**{highest_risk_city['city']}** with average risk score "
            f"**{highest_risk_city['average_risk_score']:.1f}** and high-risk share "
            f"**{format_percentage(highest_risk_city['high_risk_share'])}**."
        )
    if isinstance(highest_risk_project, dict):
        st.markdown(
            "- Highest-risk project: "
            f"**{highest_risk_project['project_name']} ({highest_risk_project['city']})** "
            f"with risk score **{highest_risk_project['risk_score']:.1f}**."
        )
    if isinstance(common_drivers, list) and common_drivers:
        st.markdown(f"- Most common risk drivers: **{', '.join(common_drivers[:3])}**.")
    if isinstance(observations, list):
        for observation in observations[:2]:
            st.markdown(f"- {observation}")


def render_risk_charts(project_df: pd.DataFrame, city_df: pd.DataFrame) -> None:
    st.subheader("Risk Hotspots")
    col_projects, col_cities = st.columns(2)

    with col_projects:
        top_projects = project_df.nlargest(min(10, len(project_df)), "risk_score").sort_values(
            "risk_score", ascending=True
        )
        fig_projects = px.bar(
            top_projects,
            x="risk_score",
            y="project_name",
            orientation="h",
            color="risk_level",
            color_discrete_map={"High": "#d62728", "Medium": "#ff7f0e", "Low": "#2ca02c"},
            labels={"risk_score": "Risk Score", "project_name": "Project", "risk_level": "Risk Level"},
            title="Highest-Risk Projects",
            hover_data={
                "city": True,
                "projected_sales": ":,.0f",
                "unsold_inventory": ":,.0f",
                "projected_demand_score": ":.1f",
            },
            text="risk_score",
        )
        fig_projects.update_traces(texttemplate="%{x:.1f}", textposition="outside")
        fig_projects.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=420)
        st.plotly_chart(fig_projects, use_container_width=True)

    with col_cities:
        fig_cities = px.bar(
            city_df.sort_values("average_risk_score", ascending=True),
            x="average_risk_score",
            y="city",
            orientation="h",
            color="high_risk_share",
            color_continuous_scale="OrRd",
            labels={
                "average_risk_score": "Average Risk Score",
                "city": "City",
                "high_risk_share": "High-Risk Share",
            },
            title="City Risk Exposure",
            hover_data={
                "high_risk_projects": True,
                "project_count": True,
                "average_projected_demand_score": ":.1f",
            },
            text="average_risk_score",
        )
        fig_cities.update_traces(texttemplate="%{x:.1f}", textposition="outside")
        fig_cities.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=420)
        st.plotly_chart(fig_cities, use_container_width=True)


def render_project_ranking_table(project_df: pd.DataFrame) -> None:
    st.subheader("Project Risk Ranking")
    table_df = project_df[
        [
            "project_name",
            "city",
            "property_type",
            "risk_level",
            "risk_score",
            "top_risk_drivers",
            "current_sales",
            "projected_sales",
            "unsold_inventory",
            "projected_demand_score",
        ]
    ].copy()

    table_df["risk_score"] = table_df["risk_score"].map(lambda value: f"{float(value):.1f}")
    table_df["current_sales"] = table_df["current_sales"].map(format_number)
    table_df["projected_sales"] = table_df["projected_sales"].map(format_number)
    table_df["unsold_inventory"] = table_df["unsold_inventory"].map(format_number)
    table_df["projected_demand_score"] = table_df["projected_demand_score"].map(
        lambda value: f"{float(value):.1f}"
    )

    st.dataframe(
        table_df.rename(
            columns={
                "project_name": "Project",
                "city": "City",
                "property_type": "Property Type",
                "risk_level": "Risk Level",
                "risk_score": "Risk Score",
                "top_risk_drivers": "Top Risk Drivers",
                "current_sales": "Current Sales",
                "projected_sales": "Projected Sales",
                "unsold_inventory": "Unsold Inventory",
                "projected_demand_score": "Projected Demand Score",
            }
        ),
        use_container_width=True,
        hide_index=True,
        height=380,
    )


def render_city_breakdown_table(city_df: pd.DataFrame) -> None:
    st.subheader("City Risk Breakdown")
    table_df = city_df.copy()
    for column in [
        "project_count",
        "high_risk_projects",
        "medium_risk_projects",
        "low_risk_projects",
        "total_unsold_inventory",
        "total_projected_sales",
    ]:
        table_df[column] = table_df[column].map(format_number)
    table_df["average_risk_score"] = table_df["average_risk_score"].map(
        lambda value: f"{float(value):.1f}"
    )
    table_df["high_risk_share"] = table_df["high_risk_share"].map(format_percentage)
    table_df["average_projected_demand_score"] = table_df["average_projected_demand_score"].map(
        lambda value: f"{float(value):.1f}"
    )

    st.dataframe(
        table_df.rename(
            columns={
                "city": "City",
                "project_count": "Projects",
                "average_risk_score": "Average Risk Score",
                "high_risk_projects": "High-Risk Projects",
                "medium_risk_projects": "Medium-Risk Projects",
                "low_risk_projects": "Low-Risk Projects",
                "high_risk_share": "High-Risk Share",
                "total_unsold_inventory": "Total Unsold Inventory",
                "total_projected_sales": "Total Projected Sales",
                "average_projected_demand_score": "Average Projected Demand Score",
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

    load_result = load_risk_data()
    if load_result is None:
        return
    project_risk_df, data_source, source_path = load_result

    selected_cities, selected_property_types, selected_risk_levels = render_sidebar_filters(
        project_risk_df
    )
    filtered_risk_df = apply_filters(
        project_risk_df,
        selected_cities,
        selected_property_types,
        selected_risk_levels,
    )
    if filtered_risk_df.empty:
        st.warning("No projects match the selected filters. Adjust the filters and try again.")
        return

    city_risk_df = risk_city_breakdown(filtered_risk_df)
    overview_metrics = risk_overview_metrics(filtered_risk_df)
    insights = risk_summary_insights(filtered_risk_df, city_risk_df)

    st.caption(
        f"Projects included in risk analysis: {len(filtered_risk_df):,} | Source: {source_display_name(data_source)} (`{source_path}`)"
    )
    render_summary_metrics(overview_metrics)
    st.divider()
    render_summary(insights)
    st.divider()
    render_risk_charts(filtered_risk_df, city_risk_df)
    st.divider()
    render_project_ranking_table(filtered_risk_df)
    st.divider()
    render_city_breakdown_table(city_risk_df)


if __name__ == "__main__":
    main()
