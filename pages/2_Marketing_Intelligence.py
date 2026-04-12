import pandas as pd
import plotly.express as px
import streamlit as st

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
    st.set_page_config(page_title=full_page_title("Marketing Intelligence"), layout="wide")


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
    st.title("Marketing Intelligence")
    st.markdown(
        """
        Evaluate acquisition quality and funnel efficiency to understand where marketing spend
        is producing stronger qualified demand across cities and projects.
        """
    )


def render_summary_metrics(metrics: dict[str, float | int], project_count: int) -> None:
    st.subheader("Marketing KPI Overview")
    row_1 = st.columns(4)
    row_2 = st.columns(3)
    row_3 = st.columns(3)

    row_1[0].metric("Projects in Scope", format_number(project_count))
    row_1[1].metric("Total Ad Spend", format_currency(metrics["total_ad_spend"]))
    row_1[2].metric("Total Leads", format_number(metrics["total_leads"]))
    row_1[3].metric("Qualified Leads", format_number(metrics["total_qualified_leads"]))

    row_2[0].metric("Cost per Lead", format_currency(metrics["cost_per_lead"]))
    row_2[1].metric("Cost per Qualified Lead", format_currency(metrics["cost_per_qualified_lead"]))
    row_2[2].metric("Qualified Lead Rate", format_percentage(metrics["qualified_lead_rate"]))

    row_3[0].metric("Lead to Visit Rate", format_percentage(metrics["lead_to_visit_rate"]))
    row_3[1].metric("Visit to Reservation Rate", format_percentage(metrics["visit_to_reservation_rate"]))
    row_3[2].metric("Reservation to Sale Rate", format_percentage(metrics["reservation_to_sale_rate"]))


def _format_breakdown_table(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    context_columns = [
        column
        for column in ["city", "neighborhood", "property_type"]
        if column in df.columns and column != group_column
    ]
    metric_columns = [
        "ad_spend",
        "leads",
        "qualified_leads",
        "qualified_lead_rate",
        "cost_per_lead",
        "cost_per_qualified_lead",
        "lead_to_visit_rate",
        "visit_to_reservation_rate",
        "reservation_to_sale_rate",
        "marketing_performance",
    ]
    selected_columns = [column for column in [group_column] + context_columns + metric_columns if column in df.columns]
    table_df = df[selected_columns].copy()

    for column in ["ad_spend", "cost_per_lead", "cost_per_qualified_lead"]:
        if column in table_df.columns:
            table_df[column] = table_df[column].map(format_currency)
    for column in ["leads", "qualified_leads"]:
        if column in table_df.columns:
            table_df[column] = table_df[column].map(format_number)
    for column in [
        "qualified_lead_rate",
        "lead_to_visit_rate",
        "visit_to_reservation_rate",
        "reservation_to_sale_rate",
    ]:
        if column in table_df.columns:
            table_df[column] = table_df[column].map(format_percentage)

    renamed_columns = {
        "project_name": "Project",
        "city": "City",
        "neighborhood": "Neighborhood",
        "property_type": "Property Type",
        "ad_spend": "Ad Spend",
        "leads": "Leads",
        "qualified_leads": "Qualified Leads",
        "qualified_lead_rate": "Qualified Lead Rate",
        "cost_per_lead": "Cost per Lead",
        "cost_per_qualified_lead": "Cost per Qualified Lead",
        "lead_to_visit_rate": "Lead to Visit Rate",
        "visit_to_reservation_rate": "Visit to Reservation Rate",
        "reservation_to_sale_rate": "Reservation to Sale Rate",
        "marketing_performance": "Marketing Performance",
    }
    return table_df.rename(columns=renamed_columns)


def render_business_summary(insights: dict[str, object]) -> None:
    st.subheader("Strategic Summary")
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
        for observation in observations[:2]:
            st.markdown(f"- {observation}")


def render_quality_bar_charts(city_df: pd.DataFrame, project_df: pd.DataFrame) -> None:
    st.subheader("Lead Quality Rankings")
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
        fig_city_top.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=340)
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
        fig_city_bottom.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=340)
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
        fig_project_top.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=380)
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
        fig_project_bottom.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=380)
        st.plotly_chart(fig_project_bottom, use_container_width=True)


def render_quality_vs_conversion_chart(project_df: pd.DataFrame) -> None:
    st.subheader("Lead Quality vs Close Conversion")
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
        title="Projects closer to the top-right combine stronger lead quality and closing conversion",
    )
    comparison_fig.update_xaxes(tickformat=".0%")
    comparison_fig.update_yaxes(tickformat=".0%")
    comparison_fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=460)
    st.plotly_chart(comparison_fig, use_container_width=True)


def render_project_ranking(project_df: pd.DataFrame) -> None:
    st.subheader("Project Marketing Ranking")
    ranking_table = _format_breakdown_table(project_df, "project_name")
    desired_columns = [
        "Project",
        "City",
        "Property Type",
        "Leads",
        "Qualified Leads",
        "Qualified Lead Rate",
        "Cost per Qualified Lead",
        "Lead to Visit Rate",
        "Visit to Reservation Rate",
        "Reservation to Sale Rate",
        "Marketing Performance",
    ]
    available_columns = [column for column in desired_columns if column in ranking_table.columns]
    st.dataframe(
        ranking_table[available_columns],
        use_container_width=True,
        hide_index=True,
        height=380,
    )

    st.markdown("**Cost Efficiency Extremes (Cost per Qualified Lead)**")
    best_cpql = project_df.nsmallest(min(5, len(project_df)), "cost_per_qualified_lead")
    worst_cpql = project_df.nlargest(min(5, len(project_df)), "cost_per_qualified_lead")
    col_best, col_worst = st.columns(2)

    compact_columns = ["Project", "City", "Qualified Lead Rate", "Cost per Qualified Lead", "Leads"]
    with col_best:
        st.markdown("Lowest Cost per Qualified Lead")
        st.dataframe(
            _format_breakdown_table(best_cpql, "project_name")[compact_columns],
            use_container_width=True,
            hide_index=True,
            height=210,
        )
    with col_worst:
        st.markdown("Highest Cost per Qualified Lead")
        st.dataframe(
            _format_breakdown_table(worst_cpql, "project_name")[compact_columns],
            use_container_width=True,
            hide_index=True,
            height=210,
        )


def render_city_and_type_breakdowns(city_df: pd.DataFrame, property_type_df: pd.DataFrame) -> None:
    st.subheader("Breakdown Tables")
    col_city, col_type = st.columns(2)
    with col_city:
        st.markdown("**City Performance**")
        st.dataframe(
            _format_breakdown_table(city_df, "city"),
            use_container_width=True,
            hide_index=True,
            height=320,
        )
    with col_type:
        st.markdown("**Property Type Performance**")
        st.dataframe(
            _format_breakdown_table(property_type_df, "property_type"),
            use_container_width=True,
            hide_index=True,
            height=320,
        )


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

    st.caption(
        f"Projects included in analysis: {len(filtered_df):,} | Source: {source_display_name(data_source)} (`{source_path}`)"
    )
    render_summary_metrics(marketing_metrics, project_count=len(filtered_df))
    st.divider()
    render_business_summary(insights)
    st.divider()
    render_quality_bar_charts(city_df, project_df)
    st.divider()
    render_quality_vs_conversion_chart(project_df)
    st.divider()
    render_project_ranking(project_df)
    st.divider()
    render_city_and_type_breakdowns(city_df, property_type_df)


if __name__ == "__main__":
    main()
