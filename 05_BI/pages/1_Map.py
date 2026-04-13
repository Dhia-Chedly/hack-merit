import pandas as pd
import pydeck as pdk
import streamlit as st

from src.dashboard_ui import (
    apply_dashboard_theme,
    dashboard_panel,
    render_page_hero,
    render_sidebar_block,
    render_source_chip,
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
MAP_HEIGHT = 640
MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"


_MAP_LAYOUT_CSS = """
<style>
.block-container {
    max-width: 100vw !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

.map-shell-panel {
    background: #ffffff;
    border: 1px solid #d4dbd6;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    padding: 0.9rem;
    min-height: 640px;
}

.map-mini-panel {
    background: #f8faf8;
    border: 1px solid #e2e8e4;
    border-radius: 8px;
    padding: 0.72rem;
    margin-bottom: 0.65rem;
}

.map-overline {
    color: #8b919d;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.16rem;
}

.map-panel-title {
    color: #1a1d23;
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 0.35rem;
}

.map-panel-copy {
    color: #5a5f6b;
    font-size: 0.78rem;
    line-height: 1.45;
}

.map-hero-strip {
    background: linear-gradient(135deg, #e87461, #b85548, #2b2d31);
    border-radius: 8px;
    color: white;
    padding: 0.9rem;
    margin-bottom: 0.75rem;
}

.map-hero-value {
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1;
    margin-top: 0.25rem;
}

.map-kpi-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.55rem;
    margin-top: 0.65rem;
}

.map-kpi-tile {
    border: 1px solid #e2e8e4;
    border-radius: 8px;
    padding: 0.62rem;
    background: #ffffff;
}

.map-kpi-label {
    color: #8b919d;
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.map-kpi-value {
    color: #1a1d23;
    font-size: 1.2rem;
    font-weight: 800;
    margin-top: 0.14rem;
}

.map-legend-dot {
    display: inline-block;
    width: 0.65rem;
    height: 0.65rem;
    border-radius: 999px;
    margin-right: 0.45rem;
    vertical-align: middle;
}
</style>
"""


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("Map Explorer"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()
    st.markdown(_MAP_LAYOUT_CSS, unsafe_allow_html=True)


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
        "Map Command Center",
        "Explore project concentration, commercial pressure, and recommended actions in a map-first workspace.",
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


def _metric_tile(label: str, value: str) -> str:
    return (
        "<div class='map-kpi-tile'>"
        f"<div class='map-kpi-label'>{label}</div>"
        f"<div class='map-kpi-value'>{value}</div>"
        "</div>"
    )


def render_left_intelligence_panel(filtered_df: pd.DataFrame) -> None:
    total_leads = int(filtered_df["leads"].sum())
    total_qualified = int(filtered_df["qualified_leads"].sum())
    qualified_rate = total_qualified / total_leads if total_leads else 0
    avg_price = float(filtered_df["avg_price"].mean()) if not filtered_df.empty else 0
    top_city = (
        filtered_df.groupby("city")["leads"].sum().sort_values(ascending=False).index[0]
        if not filtered_df.empty
        else "N/A"
    )

    html = (
        "<div class='map-shell-panel'>"
        "<div class='map-hero-strip'>"
        "<div class='map-overline' style='color: rgba(255,255,255,0.76);'>Active lens</div>"
        "<div style='font-size: 1.05rem; font-weight: 800;'>Project Demand Atlas</div>"
        "<div class='map-panel-copy' style='color: rgba(255,255,255,0.86); margin-top: 0.4rem;'>"
        "Lead volume, inventory pressure, and decision signals are combined for the selected market scope."
        "</div>"
        f"<div class='map-hero-value'>{format_number(len(filtered_df))}</div>"
        "<div style='font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;'>Projects tracked</div>"
        "</div>"
        "<div class='map-mini-panel'>"
        "<div class='map-overline'>Portfolio story</div>"
        f"<div class='map-panel-title'>{top_city} leads the current map view</div>"
        f"<div class='map-panel-copy'>The selected scope contains {format_number(total_leads)} leads with a qualified lead rate of {qualified_rate:.1%}.</div>"
        "</div>"
        "<div class='map-kpi-grid'>"
        f"{_metric_tile('Qualified Leads', format_number(total_qualified))}"
        f"{_metric_tile('Sales', format_number(filtered_df['sales'].sum()))}"
        f"{_metric_tile('Unsold Units', format_number(filtered_df['unsold_inventory'].sum()))}"
        f"{_metric_tile('Avg Price', format_currency(avg_price))}"
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_map_legend(filtered_df: pd.DataFrame) -> None:
    max_leads = int(filtered_df["leads"].max()) if not filtered_df.empty else 0
    high_risk_count = int((filtered_df["risk_level"] == "High").sum()) if "risk_level" in filtered_df else 0
    st.markdown(
        (
            "<div class='map-mini-panel' style='min-height: auto;'>"
            "<div class='map-overline'>Map legend</div>"
            "<div class='map-panel-copy'>"
            "<span class='map-legend-dot' style='background:#e87461;'></span>Marker size follows lead volume"
            "</div>"
            "<div class='map-panel-copy'>"
            "<span class='map-legend-dot' style='background:#2ec4d6;'></span>Marker color reflects risk score"
            "</div>"
            f"<div class='map-panel-copy' style='margin-top:0.35rem;'>Peak marker: {format_number(max_leads)} leads</div>"
            f"<div class='map-panel-copy'>High-risk projects in view: {format_number(high_risk_count)}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_right_insight_panel(filtered_df: pd.DataFrame) -> None:
    project_names = filtered_df["project_name"].sort_values().tolist()
    selected_project = st.selectbox("Selected Project", options=project_names)
    project = filtered_df[filtered_df["project_name"] == selected_project].iloc[0]

    demand_level = "Accelerate" if float(project["priority_score"]) >= 70 else "Calibrate"
    if str(project["risk_level"]) == "High":
        demand_level = "Mitigate"

    risk_score = f"{float(project['risk_score']):.1f}"
    priority_score = f"{float(project['priority_score']):.1f}"

    st.markdown(
        (
            "<div class='map-shell-panel'>"
            "<div class='map-overline'>Selected project</div>"
            f"<div class='map-panel-title'>{project['project_name']}</div>"
            f"<div class='map-panel-copy'>{project['city']} . {project['neighborhood']} . {project['property_type']}</div>"
            "<div class='map-hero-strip' style='margin-top:0.85rem;'>"
            "<div class='map-overline' style='color: rgba(255,255,255,0.76);'>Decision stance</div>"
            f"<div class='map-hero-value'>{demand_level}</div>"
            f"<div class='map-panel-copy' style='color: rgba(255,255,255,0.86);'>Recommended action: {project['recommended_action']}</div>"
            "</div>"
            "<div class='map-kpi-grid'>"
            f"{_metric_tile('Risk Score', risk_score)}"
            f"{_metric_tile('Priority', priority_score)}"
            f"{_metric_tile('Leads', format_number(project['leads']))}"
            f"{_metric_tile('Sales', format_number(project['sales']))}"
            "</div>"
            "<div class='map-mini-panel' style='margin-top:0.8rem;'>"
            "<div class='map-overline'>Risk drivers</div>"
            f"<div class='map-panel-copy'>{project['top_risk_drivers']}</div>"
            "</div>"
            "<div class='map-mini-panel'>"
            "<div class='map-overline'>Commercial input</div>"
            f"<div class='map-panel-copy'>Unsold inventory: {format_number(project['unsold_inventory'])}</div>"
            f"<div class='map-panel-copy'>Average price: {format_currency(project['avg_price'])}</div>"
            f"<div class='map-panel-copy'>Confidence: {project['confidence_level']}</div>"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def prepare_map_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    map_df = df.copy()

    numeric_columns = [
        "latitude",
        "longitude",
        "leads",
        "qualified_leads",
        "visits",
        "reservations",
        "sales",
        "unsold_inventory",
        "avg_price",
        "risk_score",
        "priority_score",
    ]
    for column in numeric_columns:
        if column in map_df.columns:
            map_df[column] = pd.to_numeric(map_df[column], errors="coerce")

    text_columns = [
        "project_name",
        "city",
        "neighborhood",
        "property_type",
        "risk_level",
        "top_risk_drivers",
        "recommended_action",
        "confidence_level",
    ]
    for column in text_columns:
        if column in map_df.columns:
            map_df[column] = map_df[column].fillna("N/A")

    map_df = map_df.dropna(subset=["latitude", "longitude"])

    # Precompute marker colors from risk score to avoid DeckGL expression parser issues.
    risk = map_df["risk_score"].fillna(50).clip(lower=0, upper=100)
    map_df["marker_red"] = (52 + risk * 1.95).clip(lower=52, upper=245).round().astype(int)
    map_df["marker_green"] = (225 - risk * 1.72).clip(lower=52, upper=225).round().astype(int)
    map_df["marker_blue"] = (235 - risk * 2.0).clip(lower=36, upper=235).round().astype(int)
    map_df["marker_alpha"] = 242

    # Pixel-sized marker scale is more readable than meter-sized points at country zoom.
    max_leads = float(map_df["leads"].max()) if not map_df.empty else 1.0
    max_leads = max(max_leads, 1.0)
    lead_ratio = (map_df["leads"].fillna(0) / max_leads).clip(lower=0, upper=1)
    map_df["marker_px"] = (8 + lead_ratio.pow(0.5) * 18).round(2)
    map_df["glow_px"] = (map_df["marker_px"] * 1.95 + 4).round(2)

    return map_df


def build_pydeck_map(map_df: pd.DataFrame) -> pdk.Deck:
    glow_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_radius="glow_px",
        radius_units="pixels",
        get_fill_color=[86, 230, 209, 62],
        pickable=False,
        stroked=False,
    )

    marker_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_radius="marker_px",
        radius_units="pixels",
        radius_min_pixels=8,
        radius_max_pixels=30,
        get_fill_color=["marker_red", "marker_green", "marker_blue", "marker_alpha"],
        get_line_color=[246, 249, 255, 235],
        line_width_min_pixels=2,
        pickable=True,
        stroked=True,
    )

    view_state = pdk.ViewState(
        latitude=MAP_CENTER_LAT,
        longitude=MAP_CENTER_LON,
        zoom=MAP_INITIAL_ZOOM,
        pitch=18,
        bearing=0,
    )

    tooltip = {
        "html": """
        <b>{project_name}</b><br/>
        {city} . {neighborhood} . {property_type}<br/><br/>
        Leads: {leads}<br/>
        Qualified Leads: {qualified_leads}<br/>
        Visits: {visits}<br/>
        Reservations: {reservations}<br/>
        Sales: {sales}<br/>
        Unsold Inventory: {unsold_inventory}<br/>
        Avg Price: {avg_price}<br/>
        Risk Level: {risk_level}<br/>
        Action: {recommended_action}
        """,
        "style": {"backgroundColor": "#0f172a", "color": "#e2e8f0", "fontSize": "12px"},
    }

    return pdk.Deck(
        layers=[glow_layer, marker_layer],
        initial_view_state=view_state,
        map_style=MAP_STYLE,
        map_provider="carto",
        tooltip=tooltip,
    )


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

    left_panel, map_panel, right_panel = st.columns([0.27, 0.46, 0.27], gap="small")

    with left_panel:
        render_left_intelligence_panel(filtered_df)

    with map_panel:
        with dashboard_panel("Live Project Map", "Hover markers to inspect demand, risk, and action signals."):
            map_df = prepare_map_dataframe(filtered_df)
            st.pydeck_chart(build_pydeck_map(map_df), use_container_width=True, height=MAP_HEIGHT)
        render_map_legend(filtered_df)

    with right_panel:
        render_right_insight_panel(filtered_df)


if __name__ == "__main__":
    main()
