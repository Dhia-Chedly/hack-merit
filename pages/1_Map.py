import pandas as pd
import pydeck as pdk
import streamlit as st

from src.data_loader import load_projects_data
from src.risk import calculate_project_risk

MAP_CENTER_LAT = 34.2
MAP_CENTER_LON = 9.4
MAP_INITIAL_ZOOM = 5.8
MAP_HEIGHT = 560


def load_map_data() -> pd.DataFrame | None:
    try:
        return load_projects_data()
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to load project dataset: {error}")
        st.info("Please verify `data/projects.csv` and try again.")
        return None


def add_risk_data(df: pd.DataFrame) -> pd.DataFrame | None:
    try:
        risk_df = calculate_project_risk(df)
    except ValueError as error:
        st.error(f"Unable to compute risk signals for map view: {error}")
        return None

    join_keys = ["project_name", "city", "neighborhood", "property_type"]
    merge_columns = join_keys + ["risk_score", "risk_level", "top_risk_drivers"]
    return df.merge(risk_df[merge_columns], on=join_keys, how="left")


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


def prepare_map_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    map_df = df.copy()

    # Size markers by leads so high-demand projects stand out clearly on the map.
    map_df["marker_radius"] = (
        map_df["leads"].clip(lower=1).pow(0.5).mul(250).clip(lower=2500, upper=12000)
    )

    map_df["leads_display"] = map_df["leads"].map(lambda value: f"{int(value):,}")
    map_df["qualified_leads_display"] = map_df["qualified_leads"].map(
        lambda value: f"{int(value):,}"
    )
    map_df["visits_display"] = map_df["visits"].map(lambda value: f"{int(value):,}")
    map_df["reservations_display"] = map_df["reservations"].map(
        lambda value: f"{int(value):,}"
    )
    map_df["sales_display"] = map_df["sales"].map(lambda value: f"{int(value):,}")
    map_df["unsold_inventory_display"] = map_df["unsold_inventory"].map(
        lambda value: f"{int(value):,}"
    )
    map_df["avg_price_display"] = map_df["avg_price"].map(
        lambda value: f"TND {float(value):,.0f}"
    )
    map_df["risk_score_display"] = map_df["risk_score"].map(
        lambda value: f"{float(value):.1f}" if pd.notna(value) else "N/A"
    )
    map_df["risk_level_display"] = map_df["risk_level"].fillna("N/A")
    map_df["top_risk_drivers_display"] = map_df["top_risk_drivers"].fillna("N/A")

    return map_df


def build_map(map_df: pd.DataFrame) -> pdk.Deck:
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_radius="marker_radius",
        get_fill_color=[15, 98, 254, 180],
        get_line_color=[255, 255, 255, 180],
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
        Top Risk Drivers: {top_risk_drivers_display}
        """,
        "style": {
            "backgroundColor": "white",
            "color": "#1f2937",
            "fontSize": "12px",
        },
    }

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light",
        map_provider="carto",
    )


def render_filtered_table(df: pd.DataFrame) -> None:
    st.subheader("Filtered Project List")
    table_df = (
        df[
            [
                "project_name",
                "city",
                "neighborhood",
                "property_type",
                "leads",
                "sales",
                "unsold_inventory",
                "avg_price",
                "risk_score",
                "risk_level",
            ]
        ]
        .sort_values(by=["city", "project_name"])
        .reset_index(drop=True)
    )

    table_df["leads"] = table_df["leads"].map(lambda value: f"{int(value):,}")
    table_df["sales"] = table_df["sales"].map(lambda value: f"{int(value):,}")
    table_df["unsold_inventory"] = table_df["unsold_inventory"].map(
        lambda value: f"{int(value):,}"
    )
    table_df["avg_price"] = table_df["avg_price"].map(
        lambda value: f"TND {float(value):,.0f}"
    )
    table_df["risk_score"] = table_df["risk_score"].map(
        lambda value: f"{float(value):.1f}" if pd.notna(value) else "N/A"
    )

    st.dataframe(
        table_df.rename(
            columns={
                "project_name": "Project",
                "city": "City",
                "neighborhood": "Neighborhood",
                "property_type": "Property Type",
                "leads": "Leads",
                "sales": "Sales",
                "unsold_inventory": "Unsold Inventory",
                "avg_price": "Avg Price",
                "risk_score": "Risk Score",
                "risk_level": "Risk Level",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    st.title("Project Map Explorer")
    st.markdown(
        """
        Explore project distribution across Tunisia and filter by city and property type.
        Marker size is based on **leads**, helping you quickly spot high-demand projects.
        """
    )

    projects_df = load_map_data()
    if projects_df is None:
        return

    projects_with_risk_df = add_risk_data(projects_df)
    if projects_with_risk_df is None:
        return

    selected_cities, selected_property_types = render_sidebar_filters(projects_with_risk_df)
    filtered_df = apply_filters(projects_with_risk_df, selected_cities, selected_property_types)

    if filtered_df.empty:
        st.warning(
            "No projects match the selected filters. Adjust city or property type selections."
        )
        st.subheader("Filtered Project List")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        return

    st.caption(f"Projects shown on map: {len(filtered_df):,}")

    map_df = prepare_map_dataframe(filtered_df)
    st.pydeck_chart(build_map(map_df), use_container_width=True, height=MAP_HEIGHT)

    render_filtered_table(filtered_df)


if __name__ == "__main__":
    main()
