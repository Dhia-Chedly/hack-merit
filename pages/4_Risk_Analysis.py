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
from src.presentation import format_number, format_percentage, full_page_title, sorted_options
from src.risk import (
    calculate_project_risk,
    risk_city_breakdown,
    risk_overview_metrics,
    risk_scoring_assumptions,
    risk_summary_insights,
)


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("Risk Analysis"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()


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


def render_header() -> None:
    render_page_hero(
        "Risk Analysis",
        "Identify underperforming projects and market exposure using an interpretable score combining lead quality, conversion efficiency, inventory pressure, and forecast weakness.",
    )


def render_sidebar_filters(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    render_sidebar_block("Risk Controls", "Adjust city, asset type, and risk segment focus.")

    city_options = sorted_options(df, "city")
    property_type_options = sorted_options(df, "property_type")
    risk_level_options = [
        level for level in ["High", "Medium", "Low"] if level in df["risk_level"].unique()
    ]

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


def render_assumptions() -> None:
    with st.expander("Risk Scoring Methodology", expanded=False):
        for assumption in risk_scoring_assumptions():
            st.markdown(f"- {assumption}")


def render_summary_metrics(metrics: dict[str, float | int]) -> None:
    cards = [
        {
            "label": "Projects in Scope",
            "value": format_number(metrics["project_count"]),
            "subtext": "Projects included after sidebar filters",
        },
        {
            "label": "High-Risk Projects",
            "value": format_number(metrics["high_risk_projects"]),
            "delta": format_percentage(metrics["high_risk_share"]),
            "subtext": "Share of portfolio",
        },
        {
            "label": "Medium-Risk Projects",
            "value": format_number(metrics["medium_risk_projects"]),
            "subtext": "Projects needing active monitoring",
        },
        {
            "label": "Low-Risk Projects",
            "value": format_number(metrics["low_risk_projects"]),
            "subtext": "Projects with healthier commercial profile",
        },
        {
            "label": "Average Risk Score",
            "value": f"{float(metrics['average_risk_score']):.1f}",
            "subtext": "Portfolio risk intensity score (0-100)",
        },
    ]
    render_kpi_cards(cards, columns=5)


def render_summary(insights: dict[str, object]) -> None:
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
            color_discrete_map={"High": "#ff5a6f", "Medium": "#ffb347", "Low": "#32c7a1"},
            labels={"risk_score": "Risk Score", "project_name": "Project", "risk_level": "Risk Level"},
            hover_data={
                "city": True,
                "projected_sales": ":,.0f",
                "unsold_inventory": ":,.0f",
                "projected_demand_score": ":.1f",
            },
            text="risk_score",
            title="Highest-Risk Projects",
        )
        fig_projects.update_traces(texttemplate="%{x:.1f}", textposition="outside")
        style_plotly_figure(fig_projects, height=380)
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
            hover_data={
                "high_risk_projects": True,
                "project_count": True,
                "average_projected_demand_score": ":.1f",
            },
            text="average_risk_score",
            title="City Risk Exposure",
        )
        fig_cities.update_traces(texttemplate="%{x:.1f}", textposition="outside")
        style_plotly_figure(fig_cities, height=380)
        st.plotly_chart(fig_cities, use_container_width=True)


def render_project_risk_patterns(project_df: pd.DataFrame) -> None:
    col_scatter, col_box = st.columns(2)

    with col_scatter:
        risk_scatter = px.scatter(
            project_df,
            x="projected_demand_score",
            y="risk_score",
            size="unsold_inventory",
            color="risk_level",
            hover_name="project_name",
            hover_data={
                "city": True,
                "projected_sales": ":,.0f",
                "current_sales": ":,.0f",
                "top_risk_drivers": True,
            },
            labels={
                "projected_demand_score": "Projected Demand Score",
                "risk_score": "Risk Score",
                "unsold_inventory": "Unsold Inventory",
                "risk_level": "Risk Level",
            },
            title="Project Risk vs Forecast Demand",
        )
        risk_scatter.update_yaxes(range=[0, 100])
        style_plotly_figure(risk_scatter, height=380)
        st.plotly_chart(risk_scatter, use_container_width=True)

    with col_box:
        inventory_box = px.box(
            project_df,
            x="risk_level",
            y="unsold_inventory",
            color="risk_level",
            points="all",
            category_orders={"risk_level": ["Low", "Medium", "High"]},
            labels={"risk_level": "Risk Level", "unsold_inventory": "Unsold Inventory"},
            title="Inventory Pressure by Risk Level",
        )
        style_plotly_figure(inventory_box, height=380)
        st.plotly_chart(inventory_box, use_container_width=True)


def render_city_breakdown_charts(city_df: pd.DataFrame) -> None:
    col_stack, col_mix = st.columns(2)

    with col_stack:
        risk_mix = city_df.melt(
            id_vars="city",
            value_vars=["high_risk_projects", "medium_risk_projects", "low_risk_projects"],
            var_name="risk_bucket",
            value_name="project_count",
        )
        risk_mix["risk_bucket"] = risk_mix["risk_bucket"].replace(
            {
                "high_risk_projects": "High Risk",
                "medium_risk_projects": "Medium Risk",
                "low_risk_projects": "Low Risk",
            }
        )
        risk_mix_fig = px.bar(
            risk_mix,
            x="city",
            y="project_count",
            color="risk_bucket",
            barmode="stack",
            labels={"city": "City", "project_count": "Projects", "risk_bucket": "Risk Segment"},
            title="Risk Segment Mix by City",
        )
        style_plotly_figure(risk_mix_fig, height=350)
        st.plotly_chart(risk_mix_fig, use_container_width=True)

    with col_mix:
        risk_treemap = px.treemap(
            city_df,
            path=[px.Constant("Cities"), "city"],
            values="project_count",
            color="average_risk_score",
            color_continuous_scale="OrRd",
            hover_data={
                "high_risk_share": ":.1%",
                "total_unsold_inventory": ":,.0f",
                "average_projected_demand_score": ":.1f",
            },
            title="City Risk Concentration and Exposure",
        )
        style_plotly_figure(risk_treemap, height=350)
        st.plotly_chart(risk_treemap, use_container_width=True)


def main() -> None:
    configure_page()
    render_header()

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

    render_source_chip(
        f"Source: {source_display_name(data_source)} | {len(filtered_risk_df):,} rows | {source_path}"
    )

    with dashboard_panel("Risk KPI Overview", "Portfolio-level exposure and segment count distribution."):
        render_summary_metrics(overview_metrics)

    with dashboard_panel("Risk Scoring Methodology", "Transparent assumptions behind the risk score."):
        render_assumptions()

    with dashboard_panel("Strategic Risk Summary", "Top risk hotspots and notable portfolio observations."):
        render_summary(insights)

    with dashboard_panel("Risk Hotspots", "Highest-risk projects and city-level exposure profile."):
        render_risk_charts(filtered_risk_df, city_risk_df)

    with dashboard_panel(
        "Project Risk Patterns",
        "Visual project risk diagnostics replacing static ranking tables.",
    ):
        render_project_risk_patterns(filtered_risk_df)

    with dashboard_panel(
        "City Risk Breakdown",
        "City-level risk segment mix and concentration visuals.",
    ):
        render_city_breakdown_charts(city_risk_df)


if __name__ == "__main__":
    main()
