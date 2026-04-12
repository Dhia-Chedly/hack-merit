import pandas as pd
import plotly.express as px
import pydeck as pdk
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
from src.presentation import (
    format_currency,
    format_number,
    full_page_title,
    sorted_options,
)

MAP_CENTER_LAT = 34.2
MAP_CENTER_LON = 9.4
MAP_INITIAL_ZOOM = 5.8
MAP_HEIGHT = 540
MAP_STYLE_DARK = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("Map Explorer"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()


def source_display_name(source: str) -> str:
    return "Curated project metrics" if source == "curated" else "Legacy projects dataset"


def load_map_data() -> tuple[pd.DataFrame, str, str] | None:
    try:
        projects_df, source, source_path = load_projects_data_with_metadata()
        return projects_df, source, str(source_path)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to load project dataset: {error}")
        st.info(
            "Please verify `data/curated/project_metrics.csv` or `data/projects.csv` and try again."
        )
        return None


def add_decision_data(df: pd.DataFrame) -> pd.DataFrame | None:
    try:
        decision_df = calculate_project_recommendations(df)
    except ValueError as error:
        st.error(f"Unable to compute decision signals for the map view: {error}")
        return None

    join_keys = ["project_name", "city", "neighborhood", "property_type"]
    merge_columns = join_keys + [
        "risk_score",
        "risk_level",
        "top_risk_drivers",
        "recommended_action",
        "confidence_level",
        "priority_score",
    ]
    return df.merge(decision_df[merge_columns], on=join_keys, how="left")


def render_header() -> None:
    render_page_hero(
        "Map Explorer",
        "Explore project concentration and commercial signals across Tunisia. Marker size reflects lead volume, while tooltips combine performance, risk, and recommended action.",
    )


def render_sidebar_filters(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    render_sidebar_block("Map Controls", "Refine the geospatial view by market and asset type.")

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


def render_map_summary(filtered_df: pd.DataFrame) -> None:
    cards = [
        {"label": "Projects Displayed", "value": format_number(len(filtered_df)), "subtext": "Visible projects on the map"},
        {"label": "Total Leads", "value": format_number(filtered_df["leads"].sum()), "subtext": "Demand volume in current map scope"},
        {"label": "Total Sales", "value": format_number(filtered_df["sales"].sum()), "subtext": "Completed transactions in scope"},
        {
            "label": "Unsold Inventory",
            "value": format_number(filtered_df["unsold_inventory"].sum()),
            "subtext": f"Average price: {format_currency(filtered_df['avg_price'].mean())}",
        },
    ]
    render_kpi_cards(cards, columns=4)


def prepare_map_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    map_df = df.copy()

    map_df["marker_radius"] = (
        map_df["leads"].clip(lower=1).pow(0.5).mul(250).clip(lower=2500, upper=12000)
    )

    map_df["leads_display"] = map_df["leads"].map(lambda value: f"{int(value):,}")
    map_df["qualified_leads_display"] = map_df["qualified_leads"].map(
        lambda value: f"{int(value):,}"
    )
    map_df["visits_display"] = map_df["visits"].map(lambda value: f"{int(value):,}")
    map_df["reservations_display"] = map_df["reservations"].map(lambda value: f"{int(value):,}")
    map_df["sales_display"] = map_df["sales"].map(lambda value: f"{int(value):,}")
    map_df["unsold_inventory_display"] = map_df["unsold_inventory"].map(
        lambda value: f"{int(value):,}"
    )
    map_df["avg_price_display"] = map_df["avg_price"].map(lambda value: format_currency(value))
    map_df["risk_score_display"] = map_df["risk_score"].map(
        lambda value: f"{float(value):.1f}" if pd.notna(value) else "N/A"
    )
    map_df["risk_level_display"] = map_df["risk_level"].fillna("N/A")
    map_df["top_risk_drivers_display"] = map_df["top_risk_drivers"].fillna("N/A")
    map_df["recommended_action_display"] = map_df["recommended_action"].fillna("N/A")
    map_df["confidence_display"] = map_df["confidence_level"].fillna("N/A")
    map_df["priority_score_display"] = map_df["priority_score"].map(
        lambda value: f"{float(value):.1f}" if pd.notna(value) else "N/A"
    )

    return map_df


def build_map(map_df: pd.DataFrame) -> pdk.Deck:
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_radius="marker_radius",
        get_fill_color=[43, 151, 255, 185],
        get_line_color=[223, 241, 255, 180],
        line_width_min_pixels=1,
        pickable=True,
        stroked=True,
        radius_min_pixels=4,
        radius_max_pixels=30,
    )

    view_state = pdk.ViewState(
        latitude=MAP_CENTER_LAT,
        longitude=MAP_CENTER_LON,
        zoom=MAP_INITIAL_ZOOM,
        pitch=0,
        bearing=0,
    )

    tooltip = {
        "html": """
        <b>{project_name}</b><br/>
        City: {city}<br/>
        Neighborhood: {neighborhood}<br/>
        Property Type: {property_type}<br/>
        Leads: {leads_display}<br/>
        Qualified Leads: {qualified_leads_display}<br/>
        Visits: {visits_display}<br/>
        Reservations: {reservations_display}<br/>
        Sales: {sales_display}<br/>
        Unsold Inventory: {unsold_inventory_display}<br/>
        Avg Price: {avg_price_display}<br/>
        Risk Score: {risk_score_display}<br/>
        Risk Level: {risk_level_display}<br/>
        Top Risk Drivers: {top_risk_drivers_display}<br/>
        Recommended Action: {recommended_action_display}<br/>
        Confidence: {confidence_display}<br/>
        Priority Score: {priority_score_display}
        """,
        "style": {
            "backgroundColor": "#08172f",
            "color": "#e7f2ff",
            "fontSize": "12px",
        },
    }

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=MAP_STYLE_DARK,
        map_provider="carto",
    )


def render_filtered_project_charts(df: pd.DataFrame) -> None:
    col_demand, col_risk = st.columns(2)

    with col_demand:
        top_demand_projects = df.nlargest(min(12, len(df)), "leads")
        demand_fig = px.bar(
            top_demand_projects.sort_values("leads", ascending=True),
            x="leads",
            y="project_name",
            orientation="h",
            color="city",
            text="leads",
            labels={"leads": "Leads", "project_name": "Project", "city": "City"},
            hover_data={
                "property_type": True,
                "sales": ":,.0f",
                "unsold_inventory": ":,.0f",
                "recommended_action": True,
            },
            title="Top Projects by Lead Volume",
        )
        demand_fig.update_traces(texttemplate="%{x:,.0f}", textposition="outside")
        style_plotly_figure(demand_fig, height=360)
        st.plotly_chart(demand_fig, use_container_width=True)

    with col_risk:
        risk_fig = px.scatter(
            df,
            x="sales",
            y="unsold_inventory",
            size="avg_price",
            color="recommended_action",
            symbol="risk_level",
            hover_name="project_name",
            hover_data={
                "city": True,
                "property_type": True,
                "leads": ":,.0f",
                "risk_score": ":.1f",
                "priority_score": ":.1f",
            },
            labels={
                "sales": "Sales",
                "unsold_inventory": "Unsold Inventory",
                "avg_price": "Average Price",
                "recommended_action": "Recommended Action",
                "risk_level": "Risk Level",
            },
            title="Sales vs Inventory with Risk and Action Context",
        )
        style_plotly_figure(risk_fig, height=360)
        st.plotly_chart(risk_fig, use_container_width=True)


def main() -> None:
    configure_page()
    render_header()

    load_result = load_map_data()
    if load_result is None:
        return
    projects_df, data_source, source_path = load_result

    projects_with_decision_df = add_decision_data(projects_df)
    if projects_with_decision_df is None:
        return

    selected_cities, selected_property_types = render_sidebar_filters(projects_with_decision_df)
    filtered_df = apply_filters(projects_with_decision_df, selected_cities, selected_property_types)

    if filtered_df.empty:
        st.warning("No projects match the selected filters. Adjust city or property type selections.")
        return

    render_source_chip(
        f"Source: {source_display_name(data_source)} | {len(filtered_df):,} rows | {source_path}"
    )

    with dashboard_panel("Map KPI Snapshot", "Key metrics for the filtered geospatial scope."):
        render_map_summary(filtered_df)

    with dashboard_panel("Interactive Project Map", "Hover markers to inspect project-level funnel and risk signals."):
        map_df = prepare_map_dataframe(filtered_df)
        st.pydeck_chart(build_map(map_df), use_container_width=True, height=MAP_HEIGHT)

    with dashboard_panel(
        "Filtered Project Signals",
        "Visual comparison of demand leaders and inventory pressure for visible projects.",
    ):
        render_filtered_project_charts(filtered_df)


if __name__ == "__main__":
    main()
