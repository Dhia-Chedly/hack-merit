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
from src.forecasting import (
    forecast_assumptions,
    forecast_city_summary,
    forecast_overview_metrics,
    forecast_projects,
    forecast_summary_insights,
)
from src.presentation import (
    format_number,
    format_percentage,
    format_score,
    full_page_title,
    sorted_options,
)
from src.risk import calculate_project_risk, risk_overview_metrics


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("Forecasting"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()


def source_display_name(source: str) -> str:
    return "Curated project metrics" if source == "curated" else "Legacy projects dataset"


def load_forecasting_data() -> tuple[pd.DataFrame, str, str] | None:
    try:
        projects_df, source, source_path = load_projects_data_with_metadata()
        return projects_df, source, str(source_path)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to load project dataset: {error}")
        st.info(
            "Please verify `data/curated/project_metrics.csv` or `data/projects.csv` and try again."
        )
        return None


def render_sidebar_filters(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    render_sidebar_block("Forecast Controls", "Adjust scope for city and property type.")
    city_options = sorted_options(df, "city")
    property_type_options = sorted_options(df, "property_type")

    selected_cities = st.sidebar.multiselect("Cities", options=city_options, default=city_options)
    selected_property_types = st.sidebar.multiselect(
        "Property Types",
        options=property_type_options,
        default=property_type_options,
    )
    return selected_cities, selected_property_types


def apply_filters(
    df: pd.DataFrame, selected_cities: list[str], selected_property_types: list[str]
) -> pd.DataFrame:
    filtered_df = df[df["city"].isin(selected_cities)]
    filtered_df = filtered_df[filtered_df["property_type"].isin(selected_property_types)]
    return filtered_df.copy()


def render_header() -> None:
    render_page_hero(
        "Forecasting",
        "Estimate near-term demand and sales momentum using explainable heuristics aligned with a demo-ready predictive layer.",
    )


def render_assumptions() -> None:
    with st.expander("Forecast Methodology", expanded=False):
        for assumption in forecast_assumptions():
            st.markdown(f"- {assumption}")


def render_overview_metrics(metrics: dict[str, float | int]) -> None:
    cards = [
        {
            "label": "Projects in Forecast",
            "value": format_number(metrics["project_count"]),
            "subtext": "Forecast scope after filters",
        },
        {
            "label": "Projected Leads",
            "value": format_number(metrics["projected_leads"]),
            "delta": format_percentage(metrics["lead_growth_rate"]),
            "subtext": "Growth vs current leads",
        },
        {
            "label": "Projected Sales",
            "value": format_number(metrics["projected_sales"]),
            "delta": format_percentage(metrics["sales_growth_rate"]),
            "subtext": "Growth vs current sales",
        },
        {
            "label": "Average Demand Score",
            "value": format_score(metrics["average_projected_demand_score"]),
            "subtext": "Portfolio-level demand outlook",
        },
        {
            "label": "High Opportunity Projects",
            "value": format_number(metrics["high_opportunity_projects"]),
            "subtext": "Projects with strong momentum signal",
        },
    ]
    render_kpi_cards(cards, columns=5)


def render_risk_snapshot(project_risk_df: pd.DataFrame) -> None:
    risk_metrics = risk_overview_metrics(project_risk_df)
    cards = [
        {
            "label": "High-Risk Projects",
            "value": format_number(risk_metrics["high_risk_projects"]),
            "subtext": "Current risk layer perspective",
        },
        {
            "label": "Average Risk Score",
            "value": f"{float(risk_metrics['average_risk_score']):.1f}",
            "delta": format_percentage(risk_metrics["high_risk_share"]),
            "subtext": "High-risk project share",
        },
    ]
    render_kpi_cards(cards, columns=2)


def render_summary(insights: dict[str, object]) -> None:
    strongest_city = insights.get("strongest_city")
    strongest_project = insights.get("strongest_project")
    slowdown_cities = insights.get("slowdown_cities", [])
    slowdown_projects = insights.get("slowdown_projects", [])
    observations = insights.get("observations", [])

    if isinstance(strongest_city, dict):
        st.markdown(
            "- Strongest forecasted city: "
            f"**{strongest_city['city']}** with projected demand score "
            f"**{strongest_city['projected_demand_score']:.1f}** and projected sales growth "
            f"of **{format_percentage(strongest_city['projected_sales_growth_rate'])}**."
        )
    if isinstance(strongest_project, dict):
        st.markdown(
            "- Strongest forecasted project: "
            f"**{strongest_project['project_name']} ({strongest_project['city']})** with projected "
            f"demand score **{strongest_project['projected_demand_score']:.1f}** and projected sales "
            f"of **{format_number(strongest_project['projected_sales'])}**."
        )
    if isinstance(slowdown_cities, list) and slowdown_cities:
        city_notes = ", ".join(
            [
                (
                    f"{entry['city']} ({entry['projected_demand_score']:.1f} score, "
                    f"{format_percentage(entry['projected_sales_growth_rate'])} sales growth)"
                )
                for entry in slowdown_cities[:2]
            ]
        )
        st.markdown(f"- Cities that may slow down: {city_notes}.")
    if isinstance(slowdown_projects, list) and slowdown_projects:
        project_notes = ", ".join(
            [
                (
                    f"{entry['project_name']} ({entry['city']}, "
                    f"{entry['projected_demand_score']:.1f} score)"
                )
                for entry in slowdown_projects[:2]
            ]
        )
        st.markdown(f"- Projects that may slow down: {project_notes}.")
    if isinstance(observations, list):
        for observation in observations[:2]:
            st.markdown(f"- {observation}")


def render_city_charts(city_df: pd.DataFrame) -> None:
    col_demand, col_sales = st.columns(2)

    with col_demand:
        demand_fig = px.bar(
            city_df.sort_values("projected_demand_score", ascending=True),
            x="projected_demand_score",
            y="city",
            orientation="h",
            text="projected_demand_score",
            labels={"projected_demand_score": "Projected Demand Score", "city": "City"},
            title="Projected Demand Score by City",
        )
        demand_fig.update_traces(texttemplate="%{x:.1f}", textposition="outside")
        style_plotly_figure(demand_fig, height=360)
        st.plotly_chart(demand_fig, use_container_width=True)

    with col_sales:
        sales_compare = city_df[["city", "current_sales", "projected_sales"]].melt(
            id_vars="city",
            value_vars=["current_sales", "projected_sales"],
            var_name="series",
            value_name="sales",
        )
        sales_compare["series"] = sales_compare["series"].replace(
            {"current_sales": "Current Sales", "projected_sales": "Projected Sales"}
        )
        sales_fig = px.bar(
            sales_compare,
            x="city",
            y="sales",
            color="series",
            barmode="group",
            labels={"city": "City", "sales": "Sales", "series": "Series"},
            title="Current vs Projected Sales by City",
        )
        style_plotly_figure(sales_fig, height=360)
        st.plotly_chart(sales_fig, use_container_width=True)


def render_project_chart(project_df: pd.DataFrame) -> None:
    top_projects = project_df.nlargest(min(10, len(project_df)), "projected_demand_score")
    project_fig = px.bar(
        top_projects.sort_values("projected_demand_score", ascending=True),
        x="projected_demand_score",
        y="project_name",
        orientation="h",
        color="projected_sales_growth_rate",
        color_continuous_scale="Tealgrn",
        text="projected_demand_score",
        hover_data={
            "city": True,
            "projected_leads": ":,.0f",
            "projected_sales": ":,.0f",
            "projected_sales_growth_rate": ":.1%",
        },
        labels={
            "projected_demand_score": "Projected Demand Score",
            "project_name": "Project",
            "projected_sales_growth_rate": "Projected Sales Growth",
        },
        title="Top Projects by Projected Demand Score",
    )
    project_fig.update_traces(texttemplate="%{x:.1f}", textposition="outside")
    style_plotly_figure(project_fig, height=390)
    st.plotly_chart(project_fig, use_container_width=True)


def render_project_forecast_charts(project_df: pd.DataFrame) -> None:
    col_comparison, col_heatmap = st.columns(2)

    with col_comparison:
        comparison_fig = px.scatter(
            project_df,
            x="current_sales",
            y="projected_sales",
            size="projected_demand_score",
            color="risk_level",
            hover_name="project_name",
            hover_data={
                "city": True,
                "projected_leads": ":,.0f",
                "projected_sales_growth_rate": ":.1%",
                "unsold_inventory": ":,.0f",
            },
            labels={
                "current_sales": "Current Sales",
                "projected_sales": "Projected Sales",
                "projected_demand_score": "Projected Demand Score",
                "risk_level": "Risk Level",
            },
            title="Current vs Projected Sales by Project",
        )
        max_axis_value = float(
            max(
                pd.to_numeric(project_df["current_sales"], errors="coerce").fillna(0).max(),
                pd.to_numeric(project_df["projected_sales"], errors="coerce").fillna(0).max(),
            )
        )
        comparison_fig.add_shape(
            type="line",
            x0=0,
            y0=0,
            x1=max_axis_value,
            y1=max_axis_value,
            line={"color": "rgba(160, 196, 255, 0.55)", "dash": "dash"},
        )
        style_plotly_figure(comparison_fig, height=380)
        st.plotly_chart(comparison_fig, use_container_width=True)

    with col_heatmap:
        top_projects = project_df.nlargest(min(12, len(project_df)), "projected_demand_score").copy()
        heatmap_input = top_projects.set_index("project_name")[
            [
                "projected_leads",
                "projected_sales",
                "projected_sales_growth_rate",
                "projected_demand_score",
                "risk_score",
            ]
        ].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        heatmap_normalized = (
            (heatmap_input - heatmap_input.min()) / (heatmap_input.max() - heatmap_input.min())
        ).fillna(0.0)
        heatmap_fig = px.imshow(
            heatmap_normalized,
            labels={"x": "Forecast Metric", "y": "Project", "color": "Relative Intensity"},
            color_continuous_scale="Blues",
            aspect="auto",
            title="Forecast Signal Heatmap (Top Projects)",
        )
        style_plotly_figure(heatmap_fig, height=380)
        st.plotly_chart(heatmap_fig, use_container_width=True)


def render_city_growth_charts(city_df: pd.DataFrame) -> None:
    col_growth, col_outlook = st.columns(2)

    with col_growth:
        growth_df = city_df.melt(
            id_vars="city",
            value_vars=["projected_lead_growth_rate", "projected_sales_growth_rate"],
            var_name="growth_metric",
            value_name="growth_rate",
        )
        growth_df["growth_metric"] = growth_df["growth_metric"].replace(
            {
                "projected_lead_growth_rate": "Projected Lead Growth",
                "projected_sales_growth_rate": "Projected Sales Growth",
            }
        )
        growth_fig = px.bar(
            growth_df,
            x="city",
            y="growth_rate",
            color="growth_metric",
            barmode="group",
            labels={"city": "City", "growth_rate": "Growth Rate", "growth_metric": "Metric"},
            title="Projected Growth Rates by City",
        )
        growth_fig.update_yaxes(tickformat=".0%")
        style_plotly_figure(growth_fig, height=350)
        st.plotly_chart(growth_fig, use_container_width=True)

    with col_outlook:
        outlook_fig = px.scatter_polar(
            city_df,
            r="projected_demand_score",
            theta="city",
            color="projected_sales_growth_rate",
            color_continuous_scale="Tealgrn",
            size="projected_sales",
            hover_data={
                "project_count": True,
                "unsold_inventory": ":,.0f",
            },
            labels={
                "projected_demand_score": "Projected Demand Score",
                "projected_sales_growth_rate": "Projected Sales Growth",
                "projected_sales": "Projected Sales",
            },
            title="City Outlook Wheel (Demand, Growth, Sales)",
        )
        style_plotly_figure(outlook_fig, height=350)
        st.plotly_chart(outlook_fig, use_container_width=True)


def main() -> None:
    configure_page()
    render_header()
    render_assumptions()

    load_result = load_forecasting_data()
    if load_result is None:
        return
    projects_df, data_source, source_path = load_result

    selected_cities, selected_property_types = render_sidebar_filters(projects_df)
    filtered_df = apply_filters(projects_df, selected_cities, selected_property_types)
    if filtered_df.empty:
        st.warning("No projects match the selected filters. Adjust the filters and try again.")
        return

    try:
        project_forecast_df = forecast_projects(filtered_df)
        project_risk_df = calculate_project_risk(filtered_df)
        join_keys = ["project_name", "city", "neighborhood", "property_type"]
        project_forecast_df = project_forecast_df.merge(
            project_risk_df[join_keys + ["risk_score", "risk_level", "top_risk_drivers"]],
            on=join_keys,
            how="left",
        )
        city_summary_df = forecast_city_summary(project_forecast_df)
        overview_metrics = forecast_overview_metrics(project_forecast_df)
        insights = forecast_summary_insights(project_forecast_df, city_summary_df)
    except ValueError as error:
        st.error(f"Unable to compute forecasts: {error}")
        return

    render_source_chip(
        f"Source: {source_display_name(data_source)} | {len(project_forecast_df):,} rows | {source_path}"
    )

    with dashboard_panel("Forecast KPI Overview", "Executive signals for projected demand and projected sales."):
        render_overview_metrics(overview_metrics)

    with dashboard_panel("Risk Snapshot", "Risk context derived from current and projected portfolio behavior."):
        render_risk_snapshot(project_risk_df)

    with dashboard_panel("Forecast Strategic Summary", "Concise narrative for strongest and slowing opportunities."):
        render_summary(insights)

    with dashboard_panel("City Forecast Outlook", "City-level momentum and current vs projected sales comparisons."):
        render_city_charts(city_summary_df)

    with dashboard_panel("Top Opportunity Projects", "Highest forecasted demand projects ranked by projected momentum."):
        render_project_chart(project_forecast_df)

    with dashboard_panel(
        "Project Forecast Dynamics",
        "Visual project comparison replacing static forecast tables.",
    ):
        render_project_forecast_charts(project_forecast_df)

    with dashboard_panel(
        "City Forecast Growth Patterns",
        "City-level growth and outlook visuals for market planning.",
    ):
        render_city_growth_charts(city_summary_df)


if __name__ == "__main__":
    main()
