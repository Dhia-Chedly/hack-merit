import pandas as pd
import plotly.express as px
import streamlit as st

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
    st.set_page_config(page_title=full_page_title("Forecasting"), layout="wide")


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
    st.sidebar.header("Filters")

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
    st.title("Forecasting")
    st.markdown(
        """
        Estimate near-term demand and sales momentum using explainable MVP heuristics.
        This view helps teams anticipate where performance is likely to accelerate or slow down.
        """
    )


def render_assumptions() -> None:
    with st.expander("Forecast Methodology", expanded=False):
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
        "Average Projected Demand",
        format_score(metrics["average_projected_demand_score"]),
    )
    columns[4].metric("High Opportunity Projects", format_number(metrics["high_opportunity_projects"]))


def render_risk_snapshot(project_risk_df: pd.DataFrame) -> None:
    st.markdown("**Risk Snapshot (from Current + Forecast Signals)**")
    risk_metrics = risk_overview_metrics(project_risk_df)
    col_1, col_2, col_3 = st.columns(3)
    col_1.metric("High-Risk Projects", format_number(risk_metrics["high_risk_projects"]))
    col_2.metric("Average Risk Score", f"{float(risk_metrics['average_risk_score']):.1f}")
    col_3.metric("High-Risk Share", format_percentage(risk_metrics["high_risk_share"]))


def render_summary(insights: dict[str, object]) -> None:
    st.subheader("Strategic Summary")

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
    st.subheader("City Outlook")
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
        sales_fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=380)
        st.plotly_chart(sales_fig, use_container_width=True)


def render_project_chart(project_df: pd.DataFrame) -> None:
    st.subheader("Top Opportunity Projects")
    top_projects = project_df.nlargest(min(10, len(project_df)), "projected_demand_score")

    project_fig = px.bar(
        top_projects.sort_values("projected_demand_score", ascending=True),
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
    st.subheader("Project Forecast Table")

    display_df = project_df[
        [
            "project_name",
            "city",
            "projected_leads",
            "projected_sales",
            "projected_demand_score",
            "projected_sales_growth_rate",
            "current_sales",
            "unsold_inventory",
            "risk_level",
            "risk_score",
            "top_risk_drivers",
        ]
    ].copy()

    display_df["projected_leads"] = display_df["projected_leads"].map(format_number)
    display_df["projected_sales"] = display_df["projected_sales"].map(format_number)
    display_df["projected_demand_score"] = display_df["projected_demand_score"].map(
        lambda value: f"{float(value):.1f}"
    )
    display_df["projected_sales_growth_rate"] = display_df["projected_sales_growth_rate"].map(
        format_percentage
    )
    display_df["current_sales"] = display_df["current_sales"].map(format_number)
    display_df["unsold_inventory"] = display_df["unsold_inventory"].map(format_number)
    display_df["risk_score"] = display_df["risk_score"].map(
        lambda value: f"{float(value):.1f}" if pd.notna(value) else "N/A"
    )
    display_df["top_risk_drivers"] = display_df["top_risk_drivers"].fillna("N/A")

    st.dataframe(
        display_df.rename(
            columns={
                "project_name": "Project",
                "city": "City",
                "projected_leads": "Projected Leads",
                "projected_sales": "Projected Sales",
                "projected_demand_score": "Projected Demand Score",
                "projected_sales_growth_rate": "Projected Sales Growth",
                "current_sales": "Current Sales",
                "unsold_inventory": "Unsold Inventory",
                "risk_level": "Risk Level",
                "risk_score": "Risk Score",
                "top_risk_drivers": "Top Risk Drivers",
            }
        ),
        use_container_width=True,
        hide_index=True,
        height=390,
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
        height=320,
    )


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

    st.caption(
        f"Projects included in forecast: {len(project_forecast_df):,} | Source: {source_display_name(data_source)} (`{source_path}`)"
    )
    render_overview_metrics(overview_metrics)
    render_risk_snapshot(project_risk_df)
    st.divider()
    render_summary(insights)
    st.divider()
    render_city_charts(city_summary_df)
    st.divider()
    render_project_chart(project_forecast_df)
    st.divider()
    render_project_forecast_table(project_forecast_df)
    st.divider()
    render_city_forecast_table(city_summary_df)


if __name__ == "__main__":
    main()
