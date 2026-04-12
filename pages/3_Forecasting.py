import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_projects_data
from src.forecasting import (
    forecast_assumptions,
    forecast_city_summary,
    forecast_overview_metrics,
    forecast_projects,
    forecast_summary_insights,
)


def configure_page() -> None:
    st.set_page_config(
        page_title="Forecasting | Tunisia Real-Estate",
        layout="wide",
    )


def load_forecasting_data() -> pd.DataFrame | None:
    try:
        return load_projects_data()
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to load project dataset: {error}")
        st.info("Please verify `data/projects.csv` and try again.")
        return None


def render_sidebar_filters(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    st.sidebar.header("Filters")

    city_options = sorted(df["city"].dropna().unique().tolist())
    property_type_options = sorted(df["property_type"].dropna().unique().tolist())

    selected_cities = st.sidebar.multiselect(
        "City",
        options=city_options,
        default=city_options,
    )
    selected_property_types = st.sidebar.multiselect(
        "Property Type",
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


def format_number(value: float | int) -> str:
    return f"{float(value):,.0f}"


def format_percentage(value: float | int) -> str:
    return f"{float(value):.1%}"


def format_score(value: float | int) -> str:
    return f"{float(value):.1f}/100"


def render_header() -> None:
    st.title("Forecasting Layer")
    st.markdown(
        """
        This page estimates what is likely to happen next for project demand and sales
        using transparent, explainable forecasting heuristics built for an MVP demo.
        """
    )


def render_assumptions() -> None:
    with st.expander("Forecasting Methodology and Assumptions", expanded=False):
        for assumption in forecast_assumptions():
            st.markdown(f"- {assumption}")


def render_overview_metrics(metrics: dict[str, float | int]) -> None:
    st.subheader("Forecast KPI Overview")
    columns = st.columns(5)

    columns[0].metric("Projects in Forecast", format_number(metrics["project_count"]))
    columns[1].metric(
        "Projected Leads",
        format_number(metrics["projected_leads"]),
        delta=f"{format_percentage(metrics['lead_growth_rate'])} vs current",
    )
    columns[2].metric(
        "Projected Sales",
        format_number(metrics["projected_sales"]),
        delta=f"{format_percentage(metrics['sales_growth_rate'])} vs current",
    )
    columns[3].metric(
        "Avg Projected Demand Score",
        format_score(metrics["average_projected_demand_score"]),
    )
    columns[4].metric(
        "High Opportunity Projects", format_number(metrics["high_opportunity_projects"])
    )


def render_city_charts(city_df: pd.DataFrame) -> None:
    st.subheader("Projected Performance by City")
    col_demand, col_sales = st.columns(2)

    with col_demand:
        demand_fig = px.bar(
            city_df.sort_values("projected_demand_score", ascending=True),
            x="projected_demand_score",
            y="city",
            orientation="h",
            text="projected_demand_score",
            labels={
                "projected_demand_score": "Projected Demand Score",
                "city": "City",
            },
            title="Projected Demand Score by City",
        )
        demand_fig.update_traces(texttemplate="%{x:.1f}", textposition="outside")
        demand_fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=380)
        st.plotly_chart(demand_fig, use_container_width=True)

    with col_sales:
        sales_compare = city_df[["city", "current_sales", "projected_sales"]].melt(
            id_vars="city",
            value_vars=["current_sales", "projected_sales"],
            var_name="series",
            value_name="sales",
        )
        sales_compare["series"] = sales_compare["series"].replace(
            {
                "current_sales": "Current Sales",
                "projected_sales": "Projected Sales",
            }
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
        sales_fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=380)
        st.plotly_chart(sales_fig, use_container_width=True)


def render_project_charts(project_df: pd.DataFrame) -> None:
    st.subheader("Top Opportunity Projects")
    top_projects = project_df.nlargest(min(10, len(project_df)), "projected_demand_score")

    chart_df = top_projects.sort_values("projected_demand_score", ascending=True)
    project_fig = px.bar(
        chart_df,
        x="projected_demand_score",
        y="project_name",
        orientation="h",
        color="projected_sales_growth_rate",
        color_continuous_scale="Blues",
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
    project_fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=420)
    st.plotly_chart(project_fig, use_container_width=True)


def render_project_forecast_table(project_df: pd.DataFrame) -> None:
    st.subheader("Project-Level Forecast Table")

    display_df = project_df[
        [
            "project_name",
            "city",
            "projected_leads",
            "projected_sales",
            "projected_demand_score",
            "current_sales",
            "unsold_inventory",
            "projected_sales_growth_rate",
        ]
    ].copy()

    display_df["projected_leads"] = display_df["projected_leads"].map(format_number)
    display_df["projected_sales"] = display_df["projected_sales"].map(format_number)
    display_df["projected_demand_score"] = display_df["projected_demand_score"].map(
        lambda value: f"{float(value):.1f}"
    )
    display_df["current_sales"] = display_df["current_sales"].map(format_number)
    display_df["unsold_inventory"] = display_df["unsold_inventory"].map(format_number)
    display_df["projected_sales_growth_rate"] = display_df["projected_sales_growth_rate"].map(
        format_percentage
    )

    st.dataframe(
        display_df.rename(
            columns={
                "project_name": "Project",
                "city": "City",
                "projected_leads": "Projected Leads",
                "projected_sales": "Projected Sales",
                "projected_demand_score": "Projected Demand Score",
                "current_sales": "Current Sales",
                "unsold_inventory": "Unsold Inventory",
                "projected_sales_growth_rate": "Projected Sales Growth",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_city_forecast_table(city_df: pd.DataFrame) -> None:
    st.subheader("City Forecast Summary")
    display_df = city_df.copy()

    for column in [
        "project_count",
        "current_leads",
        "projected_leads",
        "current_sales",
        "projected_sales",
        "unsold_inventory",
    ]:
        display_df[column] = display_df[column].map(format_number)

    display_df["projected_demand_score"] = display_df["projected_demand_score"].map(
        lambda value: f"{float(value):.1f}"
    )
    display_df["projected_lead_growth_rate"] = display_df["projected_lead_growth_rate"].map(
        format_percentage
    )
    display_df["projected_sales_growth_rate"] = display_df["projected_sales_growth_rate"].map(
        format_percentage
    )

    st.dataframe(
        display_df.rename(
            columns={
                "city": "City",
                "project_count": "Projects",
                "current_leads": "Current Leads",
                "projected_leads": "Projected Leads",
                "current_sales": "Current Sales",
                "projected_sales": "Projected Sales",
                "unsold_inventory": "Unsold Inventory",
                "projected_demand_score": "Projected Demand Score",
                "projected_lead_growth_rate": "Projected Lead Growth",
                "projected_sales_growth_rate": "Projected Sales Growth",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_summary(insights: dict[str, object]) -> None:
    st.subheader("Forecast Summary")

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


def main() -> None:
    configure_page()
    render_header()
    render_assumptions()

    projects_df = load_forecasting_data()
    if projects_df is None:
        return

    selected_cities, selected_property_types = render_sidebar_filters(projects_df)
    filtered_df = apply_filters(projects_df, selected_cities, selected_property_types)

    if filtered_df.empty:
        st.warning(
            "No projects match the selected filters. Adjust city or property type selections."
        )
        return

    try:
        project_forecast_df = forecast_projects(filtered_df)
        city_summary_df = forecast_city_summary(project_forecast_df)
        overview_metrics = forecast_overview_metrics(project_forecast_df)
        insights = forecast_summary_insights(project_forecast_df, city_summary_df)
    except ValueError as error:
        st.error(f"Unable to compute forecasts: {error}")
        return

    st.caption(f"Projects included in forecast: {len(project_forecast_df):,}")
    render_overview_metrics(overview_metrics)
    st.divider()
    render_summary(insights)
    st.divider()
    render_city_charts(city_summary_df)
    st.divider()
    render_project_charts(project_forecast_df)
    st.divider()
    render_project_forecast_table(project_forecast_df)
    st.divider()
    render_city_forecast_table(city_summary_df)


if __name__ == "__main__":
    main()
