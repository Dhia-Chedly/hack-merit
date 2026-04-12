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
from src.kpis import (
    calculate_marketing_kpis,
    city_marketing_breakdown,
    marketing_summary_insights,
    project_marketing_breakdown,
    property_type_marketing_breakdown,
)
from src.presentation import (
    format_currency,
    format_number,
    format_percentage,
    full_page_title,
    sorted_options,
)


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("Marketing Intelligence"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()


def source_display_name(source: str) -> str:
    return "Curated project metrics" if source == "curated" else "Legacy projects dataset"


def load_marketing_data() -> tuple[pd.DataFrame, str, str] | None:
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
    render_sidebar_block("Marketing Controls", "Filter analysis by city and property type.")

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
        "Marketing Intelligence",
        "Evaluate acquisition quality and funnel efficiency to reveal where spend is producing stronger qualified demand.",
    )


def render_summary_metrics(metrics: dict[str, float | int], project_count: int) -> None:
    cards = [
        {"label": "Projects in Scope", "value": format_number(project_count), "subtext": "Filtered project portfolio"},
        {
            "label": "Total Ad Spend",
            "value": format_currency(metrics["total_ad_spend"]),
            "subtext": "Aggregate paid investment",
        },
        {"label": "Total Leads", "value": format_number(metrics["total_leads"]), "subtext": "Acquisition volume"},
        {
            "label": "Qualified Leads",
            "value": format_number(metrics["total_qualified_leads"]),
            "delta": format_percentage(metrics["qualified_lead_rate"]),
            "subtext": "Lead qualification rate",
        },
        {
            "label": "Cost per Lead",
            "value": format_currency(metrics["cost_per_lead"]),
            "subtext": "Spend efficiency at top funnel",
        },
        {
            "label": "Cost per Qualified Lead",
            "value": format_currency(metrics["cost_per_qualified_lead"]),
            "subtext": "Quality-adjusted acquisition cost",
        },
        {
            "label": "Lead to Visit Rate",
            "value": format_percentage(metrics["lead_to_visit_rate"]),
            "delta": format_percentage(metrics["visit_to_reservation_rate"]),
            "subtext": "Visit-to-reservation rate",
        },
        {
            "label": "Reservation to Sale Rate",
            "value": format_percentage(metrics["reservation_to_sale_rate"]),
            "subtext": "Closing effectiveness",
        },
    ]
    render_kpi_cards(cards, columns=4)


def render_business_summary(insights: dict[str, object]) -> None:
    strongest_city = insights.get("strongest_city")
    weakest_city = insights.get("weakest_city")
    strongest_project = insights.get("strongest_project")
    weakest_project = insights.get("weakest_project")
    observations = insights.get("observations", [])

    if isinstance(strongest_city, dict):
        st.markdown(
            "- Strongest city for qualified demand: "
            f"**{strongest_city['city']}** with qualified lead rate "
            f"**{format_percentage(strongest_city['qualified_lead_rate'])}** and cost per qualified lead "
            f"**{format_currency(strongest_city['cost_per_qualified_lead'])}**."
        )
    if isinstance(weakest_city, dict):
        st.markdown(
            "- Weakest city for lead quality efficiency: "
            f"**{weakest_city['city']}** with qualified lead rate "
            f"**{format_percentage(weakest_city['qualified_lead_rate'])}** and cost per qualified lead "
            f"**{format_currency(weakest_city['cost_per_qualified_lead'])}**."
        )
    if isinstance(strongest_project, dict):
        st.markdown(
            "- Strongest project signal: "
            f"**{strongest_project['project_name']} ({strongest_project['city']})** "
            f"with performance band **{strongest_project['marketing_performance']}**."
        )
    if isinstance(weakest_project, dict):
        st.markdown(
            "- Weakest project signal: "
            f"**{weakest_project['project_name']} ({weakest_project['city']})** "
            f"with performance band **{weakest_project['marketing_performance']}**."
        )
    if isinstance(observations, list):
        for observation in observations[:3]:
            st.markdown(f"- {observation}")


def render_quality_bar_charts(city_df: pd.DataFrame, project_df: pd.DataFrame) -> None:
    top_n_city = min(5, len(city_df))
    top_n_project = min(8, len(project_df))

    city_top = city_df.nlargest(top_n_city, "qualified_lead_rate").copy()
    city_bottom = city_df.nsmallest(top_n_city, "qualified_lead_rate").copy()

    col_city_top, col_city_bottom = st.columns(2)
    with col_city_top:
        fig_city_top = px.bar(
            city_top.sort_values("qualified_lead_rate"),
            x="qualified_lead_rate",
            y="city",
            orientation="h",
            title="Top Cities by Qualified Lead Rate",
            labels={"qualified_lead_rate": "Qualified Lead Rate", "city": "City"},
            text="qualified_lead_rate",
        )
        fig_city_top.update_traces(texttemplate="%{x:.1%}", textposition="outside")
        fig_city_top.update_xaxes(tickformat=".0%")
        style_plotly_figure(fig_city_top, height=360)
        st.plotly_chart(fig_city_top, use_container_width=True)

    with col_city_bottom:
        fig_city_bottom = px.bar(
            city_bottom.sort_values("qualified_lead_rate"),
            x="qualified_lead_rate",
            y="city",
            orientation="h",
            title="Lowest Cities by Qualified Lead Rate",
            labels={"qualified_lead_rate": "Qualified Lead Rate", "city": "City"},
            text="qualified_lead_rate",
        )
        fig_city_bottom.update_traces(texttemplate="%{x:.1%}", textposition="outside")
        fig_city_bottom.update_xaxes(tickformat=".0%")
        style_plotly_figure(fig_city_bottom, height=360)
        st.plotly_chart(fig_city_bottom, use_container_width=True)

    project_top = project_df.nlargest(top_n_project, "qualified_lead_rate").copy()
    project_bottom = project_df.nsmallest(top_n_project, "qualified_lead_rate").copy()
    col_project_top, col_project_bottom = st.columns(2)

    with col_project_top:
        fig_project_top = px.bar(
            project_top.sort_values("qualified_lead_rate"),
            x="qualified_lead_rate",
            y="project_name",
            orientation="h",
            title="Top Projects by Qualified Lead Rate",
            labels={"qualified_lead_rate": "Qualified Lead Rate", "project_name": "Project"},
            text="qualified_lead_rate",
        )
        fig_project_top.update_traces(texttemplate="%{x:.1%}", textposition="outside")
        fig_project_top.update_xaxes(tickformat=".0%")
        style_plotly_figure(fig_project_top, height=360)
        st.plotly_chart(fig_project_top, use_container_width=True)

    with col_project_bottom:
        fig_project_bottom = px.bar(
            project_bottom.sort_values("qualified_lead_rate"),
            x="qualified_lead_rate",
            y="project_name",
            orientation="h",
            title="Lowest Projects by Qualified Lead Rate",
            labels={"qualified_lead_rate": "Qualified Lead Rate", "project_name": "Project"},
            text="qualified_lead_rate",
        )
        fig_project_bottom.update_traces(texttemplate="%{x:.1%}", textposition="outside")
        fig_project_bottom.update_xaxes(tickformat=".0%")
        style_plotly_figure(fig_project_bottom, height=360)
        st.plotly_chart(fig_project_bottom, use_container_width=True)


def render_quality_vs_conversion_chart(project_df: pd.DataFrame) -> None:
    comparison_fig = px.scatter(
        project_df,
        x="qualified_lead_rate",
        y="reservation_to_sale_rate",
        size="leads",
        color="city",
        hover_name="project_name",
        hover_data={
            "property_type": True,
            "cost_per_qualified_lead": ":.0f",
            "lead_to_visit_rate": ":.1%",
            "visit_to_reservation_rate": ":.1%",
            "qualified_lead_rate": ":.1%",
            "reservation_to_sale_rate": ":.1%",
        },
        labels={
            "qualified_lead_rate": "Qualified Lead Rate",
            "reservation_to_sale_rate": "Reservation to Sale Rate",
        },
        title="Projects closer to the top-right combine stronger lead quality and close conversion",
    )
    comparison_fig.update_xaxes(tickformat=".0%")
    comparison_fig.update_yaxes(tickformat=".0%")
    style_plotly_figure(comparison_fig, height=420)
    st.plotly_chart(comparison_fig, use_container_width=True)


def render_project_ranking(project_df: pd.DataFrame) -> None:
    col_efficiency, col_extremes = st.columns(2)

    with col_efficiency:
        efficiency_fig = px.scatter(
            project_df,
            x="cost_per_qualified_lead",
            y="qualified_lead_rate",
            size="leads",
            color="marketing_performance",
            hover_name="project_name",
            hover_data={
                "city": True,
                "property_type": True,
                "lead_to_visit_rate": ":.1%",
                "visit_to_reservation_rate": ":.1%",
                "reservation_to_sale_rate": ":.1%",
            },
            labels={
                "cost_per_qualified_lead": "Cost per Qualified Lead",
                "qualified_lead_rate": "Qualified Lead Rate",
                "marketing_performance": "Performance Band",
                "leads": "Leads",
            },
            title="Lead Quality vs Cost Efficiency by Project",
        )
        efficiency_fig.update_yaxes(tickformat=".0%")
        style_plotly_figure(efficiency_fig, height=390)
        st.plotly_chart(efficiency_fig, use_container_width=True)

    best_cpql = project_df.nsmallest(min(5, len(project_df)), "cost_per_qualified_lead")
    worst_cpql = project_df.nlargest(min(5, len(project_df)), "cost_per_qualified_lead")
    cpql_extremes = pd.concat(
        [
            best_cpql.assign(efficiency_band="Most Efficient"),
            worst_cpql.assign(efficiency_band="Needs Attention"),
        ],
        ignore_index=True,
    ).drop_duplicates(subset=["project_name"])
    with col_extremes:
        extreme_fig = px.bar(
            cpql_extremes.sort_values("cost_per_qualified_lead", ascending=True),
            x="cost_per_qualified_lead",
            y="project_name",
            orientation="h",
            color="efficiency_band",
            text="cost_per_qualified_lead",
            hover_data={
                "city": True,
                "qualified_lead_rate": ":.1%",
                "leads": ":,.0f",
            },
            labels={
                "cost_per_qualified_lead": "Cost per Qualified Lead",
                "project_name": "Project",
                "efficiency_band": "Efficiency Band",
            },
            title="Cost per Qualified Lead Extremes",
        )
        extreme_fig.update_traces(texttemplate="TND %{x:,.0f}", textposition="outside")
        style_plotly_figure(extreme_fig, height=390)
        st.plotly_chart(extreme_fig, use_container_width=True)


def render_city_and_type_breakdowns(city_df: pd.DataFrame, property_type_df: pd.DataFrame) -> None:
    col_city, col_type = st.columns(2)
    with col_city:
        city_fig = px.treemap(
            city_df,
            path=[px.Constant("Cities"), "city"],
            values="leads",
            color="qualified_lead_rate",
            color_continuous_scale="Tealgrn",
            hover_data={
                "cost_per_qualified_lead": ":,.0f",
                "lead_to_visit_rate": ":.1%",
                "reservation_to_sale_rate": ":.1%",
            },
            title="City Demand and Lead-Quality Mix",
        )
        style_plotly_figure(city_fig, height=380)
        st.plotly_chart(city_fig, use_container_width=True)

    with col_type:
        type_fig = px.sunburst(
            property_type_df,
            path=[px.Constant("Property Types"), "property_type", "marketing_performance"],
            values="leads",
            color="reservation_to_sale_rate",
            color_continuous_scale="Blues",
            hover_data={
                "cost_per_qualified_lead": ":,.0f",
                "qualified_lead_rate": ":.1%",
            },
            title="Property Type Conversion Profile",
        )
        style_plotly_figure(type_fig, height=380)
        st.plotly_chart(type_fig, use_container_width=True)


def main() -> None:
    configure_page()
    render_header()

    load_result = load_marketing_data()
    if load_result is None:
        return
    projects_df, data_source, source_path = load_result

    selected_cities, selected_property_types = render_sidebar_filters(projects_df)
    filtered_df = apply_filters(projects_df, selected_cities, selected_property_types)
    if filtered_df.empty:
        st.warning("No projects match the selected filters. Adjust the filters and try again.")
        return

    try:
        marketing_metrics = calculate_marketing_kpis(filtered_df)
        project_df = project_marketing_breakdown(filtered_df)
        city_df = city_marketing_breakdown(filtered_df)
        property_type_df = property_type_marketing_breakdown(filtered_df)
        insights = marketing_summary_insights(filtered_df)
    except ValueError as error:
        st.error(f"Unable to compute marketing intelligence metrics: {error}")
        return

    render_source_chip(
        f"Source: {source_display_name(data_source)} | {len(filtered_df):,} rows | {source_path}"
    )

    with dashboard_panel("Marketing KPI Overview", "Acquisition quality and conversion efficiency at a glance."):
        render_summary_metrics(marketing_metrics, project_count=len(filtered_df))

    with dashboard_panel("Strategic Marketing Summary", "Narrative highlights to support fast decision-making."):
        render_business_summary(insights)

    with dashboard_panel("Lead Quality Rankings", "Best and weakest performers by city and project lead quality."):
        render_quality_bar_charts(city_df, project_df)

    with dashboard_panel("Lead Quality vs Close Conversion", "Quality and closing conversion relationship by project."):
        render_quality_vs_conversion_chart(project_df)

    with dashboard_panel("Project Marketing Ranking", "Detailed project-level ranking and cost-efficiency extremes."):
        render_project_ranking(project_df)

    with dashboard_panel("Breakdowns by City and Property Type", "Aggregated views for market and product-mix analysis."):
        render_city_and_type_breakdowns(city_df, property_type_df)


if __name__ == "__main__":
    main()
