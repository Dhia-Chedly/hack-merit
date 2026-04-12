import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_projects_data
from src.kpis import (
    calculate_marketing_kpis,
    city_marketing_breakdown,
    marketing_summary_insights,
    project_marketing_breakdown,
    property_type_marketing_breakdown,
)


def configure_page() -> None:
    st.set_page_config(
        page_title="Marketing Intelligence | Tunisia Real-Estate",
        layout="wide",
    )


def load_marketing_data() -> pd.DataFrame | None:
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


def format_currency(value: float | int) -> str:
    return f"TND {float(value):,.0f}"


def format_percentage(value: float | int) -> str:
    return f"{float(value):.1%}"


def render_header() -> None:
    st.title("Marketing Intelligence")
    st.markdown(
        """
        This layer tracks **acquisition quality** and **conversion efficiency** to show where
        marketing spend is producing stronger buyer demand across Tunisia.
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
    row_2[1].metric(
        "Cost per Qualified Lead", format_currency(metrics["cost_per_qualified_lead"])
    )
    row_2[2].metric("Qualified Lead Rate", format_percentage(metrics["qualified_lead_rate"]))

    row_3[0].metric("Lead to Visit Rate", format_percentage(metrics["lead_to_visit_rate"]))
    row_3[1].metric(
        "Visit to Reservation Rate",
        format_percentage(metrics["visit_to_reservation_rate"]),
    )
    row_3[2].metric(
        "Reservation to Sale Rate",
        format_percentage(metrics["reservation_to_sale_rate"]),
    )


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
    selected_columns = [group_column] + context_columns + metric_columns
    table_df = df[selected_columns].copy()

    table_df["ad_spend"] = table_df["ad_spend"].map(format_currency)
    table_df["leads"] = table_df["leads"].map(format_number)
    table_df["qualified_leads"] = table_df["qualified_leads"].map(format_number)
    table_df["qualified_lead_rate"] = table_df["qualified_lead_rate"].map(format_percentage)
    table_df["cost_per_lead"] = table_df["cost_per_lead"].map(format_currency)
    table_df["cost_per_qualified_lead"] = table_df["cost_per_qualified_lead"].map(
        format_currency
    )
    table_df["lead_to_visit_rate"] = table_df["lead_to_visit_rate"].map(format_percentage)
    table_df["visit_to_reservation_rate"] = table_df["visit_to_reservation_rate"].map(
        format_percentage
    )
    table_df["reservation_to_sale_rate"] = table_df["reservation_to_sale_rate"].map(
        format_percentage
    )

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


def _render_quality_bar_charts(city_df: pd.DataFrame, project_df: pd.DataFrame) -> None:
    st.subheader("Lead Quality Ranking")

    city_top = city_df.nlargest(min(5, len(city_df)), "qualified_lead_rate").copy()
    city_bottom = city_df.nsmallest(min(5, len(city_df)), "qualified_lead_rate").copy()

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

    project_top = project_df.nlargest(min(8, len(project_df)), "qualified_lead_rate").copy()
    project_bottom = project_df.nsmallest(min(8, len(project_df)), "qualified_lead_rate").copy()

    col_project_top, col_project_bottom = st.columns(2)
    with col_project_top:
        fig_project_top = px.bar(
            project_top.sort_values("qualified_lead_rate"),
            x="qualified_lead_rate",
            y="project_name",
            orientation="h",
            title="Top Projects by Qualified Lead Rate",
            labels={
                "qualified_lead_rate": "Qualified Lead Rate",
                "project_name": "Project",
            },
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
            labels={
                "qualified_lead_rate": "Qualified Lead Rate",
                "project_name": "Project",
            },
            text="qualified_lead_rate",
        )
        fig_project_bottom.update_traces(texttemplate="%{x:.1%}", textposition="outside")
        fig_project_bottom.update_xaxes(tickformat=".0%")
        fig_project_bottom.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=380)
        st.plotly_chart(fig_project_bottom, use_container_width=True)


def render_city_and_type_breakdowns(city_df: pd.DataFrame, property_type_df: pd.DataFrame) -> None:
    st.subheader("Breakdowns by City and Property Type")
    col_city, col_type = st.columns(2)

    with col_city:
        st.markdown("**City Performance**")
        st.dataframe(
            _format_breakdown_table(city_df, "city"),
            use_container_width=True,
            hide_index=True,
        )

    with col_type:
        st.markdown("**Property Type Performance**")
        st.dataframe(
            _format_breakdown_table(property_type_df, "property_type"),
            use_container_width=True,
            hide_index=True,
        )


def render_project_ranking(project_df: pd.DataFrame) -> None:
    st.subheader("Project Ranking by Marketing Performance")

    ranking_table = _format_breakdown_table(project_df, "project_name")
    ranking_table = ranking_table[
        [
            "Project",
            "City",
            "Property Type",
            "Leads",
            "Qualified Lead Rate",
            "Cost per Qualified Lead",
            "Lead to Visit Rate",
            "Visit to Reservation Rate",
            "Reservation to Sale Rate",
            "Marketing Performance",
        ]
    ]
    st.dataframe(ranking_table, use_container_width=True, hide_index=True)

    st.markdown("**Cost Efficiency Extremes (Cost per Qualified Lead)**")
    best_cpql = project_df.nsmallest(min(5, len(project_df)), "cost_per_qualified_lead")
    worst_cpql = project_df.nlargest(min(5, len(project_df)), "cost_per_qualified_lead")
    col_best, col_worst = st.columns(2)

    with col_best:
        st.markdown("Lowest Cost per Qualified Lead")
        st.dataframe(
            _format_breakdown_table(best_cpql, "project_name")[
                ["Project", "City", "Qualified Lead Rate", "Cost per Qualified Lead", "Leads"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    with col_worst:
        st.markdown("Highest Cost per Qualified Lead")
        st.dataframe(
            _format_breakdown_table(worst_cpql, "project_name")[
                ["Project", "City", "Qualified Lead Rate", "Cost per Qualified Lead", "Leads"]
            ],
            use_container_width=True,
            hide_index=True,
        )


def render_quality_vs_conversion_chart(project_df: pd.DataFrame) -> None:
    st.subheader("Lead Quality vs Conversion Performance")
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
        title="Projects with higher lead quality and higher close conversion trend toward the top-right",
    )
    comparison_fig.update_xaxes(tickformat=".0%")
    comparison_fig.update_yaxes(tickformat=".0%")
    comparison_fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=460)
    st.plotly_chart(comparison_fig, use_container_width=True)


def render_business_summary(insights: dict[str, object]) -> None:
    st.subheader("Business Summary")
    strongest_city = insights.get("strongest_city")
    weakest_city = insights.get("weakest_city")
    strongest_project = insights.get("strongest_project")
    weakest_project = insights.get("weakest_project")
    observations = insights.get("observations", [])

    if isinstance(strongest_city, dict):
        st.markdown(
            "- Strongest city: "
            f"**{strongest_city['city']}** with a qualified lead rate of "
            f"**{format_percentage(strongest_city['qualified_lead_rate'])}** and "
            f"cost per qualified lead of **{format_currency(strongest_city['cost_per_qualified_lead'])}**."
        )

    if isinstance(weakest_city, dict):
        st.markdown(
            "- Weakest city: "
            f"**{weakest_city['city']}** with a qualified lead rate of "
            f"**{format_percentage(weakest_city['qualified_lead_rate'])}** and "
            f"cost per qualified lead of **{format_currency(weakest_city['cost_per_qualified_lead'])}**."
        )

    if isinstance(strongest_project, dict):
        st.markdown(
            "- Strongest project signal: "
            f"**{strongest_project['project_name']} ({strongest_project['city']})** marked as "
            f"**{strongest_project['marketing_performance']}**, with qualified lead rate "
            f"**{format_percentage(strongest_project['qualified_lead_rate'])}**."
        )

    if isinstance(weakest_project, dict):
        st.markdown(
            "- Weakest project signal: "
            f"**{weakest_project['project_name']} ({weakest_project['city']})** marked as "
            f"**{weakest_project['marketing_performance']}**, with qualified lead rate "
            f"**{format_percentage(weakest_project['qualified_lead_rate'])}**."
        )

    if isinstance(observations, list):
        for observation in observations[:2]:
            st.markdown(f"- {observation}")


def main() -> None:
    configure_page()
    render_header()

    projects_df = load_marketing_data()
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
        marketing_metrics = calculate_marketing_kpis(filtered_df)
        project_df = project_marketing_breakdown(filtered_df)
        city_df = city_marketing_breakdown(filtered_df)
        property_type_df = property_type_marketing_breakdown(filtered_df)
        insights = marketing_summary_insights(filtered_df)
    except ValueError as error:
        st.error(f"Unable to compute marketing intelligence metrics: {error}")
        return

    st.caption(f"Projects included in analysis: {len(filtered_df):,}")
    render_summary_metrics(marketing_metrics, project_count=len(filtered_df))
    st.divider()
    render_business_summary(insights)
    st.divider()
    _render_quality_bar_charts(city_df, project_df)
    st.divider()
    render_quality_vs_conversion_chart(project_df)
    st.divider()
    render_project_ranking(project_df)
    st.divider()
    render_city_and_type_breakdowns(city_df, property_type_df)


if __name__ == "__main__":
    main()
