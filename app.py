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
from src.decision_support import calculate_project_recommendations
from src.kpis import calculate_kpis
from src.presentation import (
    APP_NAME,
    format_currency,
    format_number,
    format_percentage,
    full_page_title,
    sorted_options,
)
from src.risk import calculate_project_risk


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("Overview"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()


def source_display_name(source: str) -> str:
    return "Curated project metrics" if source == "curated" else "Legacy projects dataset"


def load_dashboard_data() -> tuple[pd.DataFrame, str, str] | None:
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
    render_sidebar_block("Dashboard Controls", "Filter the portfolio scope for this overview.")
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


def render_home() -> None:
    render_page_hero(
        APP_NAME,
        "A premium BI-style command center for Tunisia real-estate demand, conversion performance, risk exposure, and action prioritization.",
    )
    st.caption(
        "Use the left navigation to move across Map, Marketing Intelligence, Forecasting, Risk Analysis, and Decision Support."
    )


def render_kpi_section(projects_df: pd.DataFrame) -> None:
    try:
        kpi_values = calculate_kpis(projects_df)
    except ValueError as error:
        st.error(f"Unable to calculate KPIs: {error}")
        return

    cards = [
        {
            "label": "Total Leads",
            "value": format_number(kpi_values["total_leads"]),
            "subtext": "Top-of-funnel demand captured",
        },
        {
            "label": "Qualified Leads",
            "value": format_number(kpi_values["total_qualified_leads"]),
            "delta": format_percentage(kpi_values["qualified_lead_rate"]),
            "subtext": "Lead qualification rate",
        },
        {
            "label": "Total Sales",
            "value": format_number(kpi_values["total_sales"]),
            "delta": format_percentage(kpi_values["visit_to_reservation_rate"]),
            "subtext": "Visit-to-reservation conversion",
        },
        {
            "label": "Unsold Inventory",
            "value": format_number(kpi_values["total_unsold_inventory"]),
            "delta": format_currency(kpi_values["average_property_price"]),
            "subtext": "Average property price",
        },
    ]
    render_kpi_cards(cards, columns=4)


def render_portfolio_snapshot(projects_df: pd.DataFrame) -> None:
    city_count = int(projects_df["city"].nunique())
    property_type_count = int(projects_df["property_type"].nunique())
    top_city_by_leads = (
        projects_df.groupby("city", as_index=False)["leads"].sum().sort_values("leads", ascending=False)
    )
    top_city_name = "N/A" if top_city_by_leads.empty else str(top_city_by_leads.iloc[0]["city"])

    cards = [
        {
            "label": "Projects in Scope",
            "value": format_number(len(projects_df)),
            "subtext": "Active projects included in current filter context",
        },
        {
            "label": "Cities Covered",
            "value": format_number(city_count),
            "subtext": f"Highest lead concentration: {top_city_name}",
        },
        {
            "label": "Property Types",
            "value": format_number(property_type_count),
            "subtext": "Segment spread across asset types",
        },
    ]
    render_kpi_cards(cards, columns=3)


def render_overview_charts(projects_df: pd.DataFrame) -> None:
    by_city = (
        projects_df.groupby("city", as_index=False)
        .agg(
            leads=("leads", "sum"),
            sales=("sales", "sum"),
            unsold_inventory=("unsold_inventory", "sum"),
        )
        .sort_values("leads", ascending=False)
    )

    by_type = (
        projects_df.groupby("property_type", as_index=False)
        .agg(
            leads=("leads", "sum"),
            sales=("sales", "sum"),
            avg_price=("avg_price", "mean"),
        )
        .sort_values("leads", ascending=False)
    )

    col_1, col_2 = st.columns(2)
    with col_1:
        with dashboard_panel(
            "Demand & Sales by City",
            "City-level funnel output for quick market prioritization.",
        ):
            chart_df = by_city.melt(
                id_vars="city",
                value_vars=["leads", "sales"],
                var_name="metric",
                value_name="value",
            )
            chart_df["metric"] = chart_df["metric"].replace(
                {"leads": "Leads", "sales": "Sales"}
            )
            fig = px.bar(
                chart_df,
                x="city",
                y="value",
                color="metric",
                barmode="group",
                labels={"city": "City", "value": "Volume", "metric": "Metric"},
            )
            style_plotly_figure(fig, height=360)
            st.plotly_chart(fig, use_container_width=True)

    with col_2:
        with dashboard_panel(
            "Inventory Pressure by City",
            "Compares completed sales with remaining unsold inventory.",
        ):
            chart_df = by_city.melt(
                id_vars="city",
                value_vars=["sales", "unsold_inventory"],
                var_name="metric",
                value_name="value",
            )
            chart_df["metric"] = chart_df["metric"].replace(
                {"sales": "Sales", "unsold_inventory": "Unsold Inventory"}
            )
            fig = px.bar(
                chart_df,
                x="city",
                y="value",
                color="metric",
                barmode="group",
                labels={"city": "City", "value": "Units", "metric": "Metric"},
            )
            style_plotly_figure(fig, height=360)
            st.plotly_chart(fig, use_container_width=True)

    with dashboard_panel(
        "Demand Mix by Property Type",
        "Segment-level signal combining lead volume, sales, and average pricing.",
    ):
        fig = px.scatter(
            by_type,
            x="leads",
            y="sales",
            size="avg_price",
            color="property_type",
            text="property_type",
            labels={
                "leads": "Leads",
                "sales": "Sales",
                "avg_price": "Average Price",
                "property_type": "Property Type",
            },
        )
        fig.update_traces(textposition="top center")
        style_plotly_figure(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)


def _prepare_home_highlight_data(projects_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    decision_df = calculate_project_recommendations(projects_df)
    risk_df = calculate_project_risk(projects_df)
    return decision_df.copy(), risk_df.copy()


def render_home_highlights(projects_df: pd.DataFrame) -> None:
    try:
        decision_df, risk_df = _prepare_home_highlight_data(projects_df)
    except ValueError as error:
        st.warning(f"Decision and risk highlights are unavailable: {error}")
        return

    col_reco, col_risk = st.columns(2)
    with col_reco:
        with dashboard_panel(
            "Top Recommended Actions",
            "Highest-priority opportunities and interventions across projects.",
        ):
            top_recommendations = decision_df.nlargest(min(10, len(decision_df)), "priority_score")
            reco_fig = px.bar(
                top_recommendations.sort_values("priority_score", ascending=True),
                x="priority_score",
                y="project_name",
                orientation="h",
                color="recommended_action",
                text="priority_score",
                hover_data={
                    "city": True,
                    "confidence_level": True,
                    "risk_level": True,
                    "projected_demand_score": ":.1f",
                },
                labels={
                    "priority_score": "Priority Score",
                    "project_name": "Project",
                    "recommended_action": "Recommended Action",
                },
                title="Top Priority Actions by Project",
            )
            reco_fig.update_traces(texttemplate="%{x:.1f}", textposition="outside")
            style_plotly_figure(reco_fig, height=360)
            st.plotly_chart(reco_fig, use_container_width=True)

    with col_risk:
        with dashboard_panel(
            "Top Risk Alerts",
            "Projects currently presenting the strongest commercial risk signal.",
        ):
            top_risks = risk_df.nlargest(min(14, len(risk_df)), "risk_score")
            risk_fig = px.scatter(
                top_risks,
                x="unsold_inventory",
                y="risk_score",
                size="projected_sales",
                color="risk_level",
                hover_name="project_name",
                hover_data={
                    "city": True,
                    "projected_demand_score": ":.1f",
                    "top_risk_drivers": True,
                },
                labels={
                    "unsold_inventory": "Unsold Inventory",
                    "risk_score": "Risk Score",
                    "risk_level": "Risk Level",
                    "projected_sales": "Projected Sales",
                },
                title="Risk Score vs Inventory Pressure",
            )
            risk_fig.update_yaxes(range=[0, 100])
            style_plotly_figure(risk_fig, height=360)
            st.plotly_chart(risk_fig, use_container_width=True)


def render_portfolio_story_charts(projects_df: pd.DataFrame) -> None:
    composition_df = projects_df.copy()

    col_mix, col_distribution = st.columns(2)
    with col_mix:
        mix_fig = px.treemap(
            composition_df,
            path=[px.Constant("Tunisia"), "city", "property_type"],
            values="leads",
            color="avg_price",
            color_continuous_scale="Blues",
            hover_data={
                "sales": ":,.0f",
                "qualified_leads": ":,.0f",
                "unsold_inventory": ":,.0f",
            },
            title="Demand Composition by City and Property Type",
        )
        style_plotly_figure(mix_fig, height=390)
        st.plotly_chart(mix_fig, use_container_width=True)

    with col_distribution:
        price_fig = px.box(
            composition_df,
            x="city",
            y="avg_price",
            color="property_type",
            points="all",
            labels={"city": "City", "avg_price": "Average Price", "property_type": "Property Type"},
            title="Price Distribution by City and Property Type",
        )
        style_plotly_figure(price_fig, height=390)
        st.plotly_chart(price_fig, use_container_width=True)


def render_data_preview(projects_df: pd.DataFrame) -> None:
    with dashboard_panel(
        "Portfolio Composition and Pricing",
        "Visual portfolio mix replacing static tabular preview.",
    ):
        render_portfolio_story_charts(projects_df)


def main() -> None:
    configure_page()
    render_home()

    load_result = load_dashboard_data()
    if load_result is None:
        return
    projects_df, data_source, source_path = load_result

    selected_cities, selected_property_types = render_sidebar_filters(projects_df)
    filtered_df = apply_filters(projects_df, selected_cities, selected_property_types)
    if filtered_df.empty:
        st.warning("No projects match the selected filters. Adjust the filters and try again.")
        return

    render_source_chip(
        f"Source: {source_display_name(data_source)} | {len(filtered_df):,} rows | {source_path}"
    )

    with dashboard_panel("Portfolio KPI Snapshot", "High-level performance indicators for executive review."):
        render_kpi_section(filtered_df)

    with dashboard_panel("Portfolio Breadth", "Coverage and market distribution of the current filtered scope."):
        render_portfolio_snapshot(filtered_df)

    render_overview_charts(filtered_df)
    render_home_highlights(filtered_df)
    render_data_preview(filtered_df)


if __name__ == "__main__":
    main()
