import streamlit as st
import pandas as pd

from src.data_loader import load_projects_data
from src.kpis import calculate_kpis


def configure_page() -> None:
    st.set_page_config(
        page_title="Tunisia Real-Estate Demand Intelligence",
        layout="wide",
    )


def render_home() -> None:
    st.title("Tunisia Real-Estate Demand Intelligence")
    st.markdown(
        """
        A real-estate demand intelligence platform for Tunisia.
        This executive overview highlights core demand and sales performance
        across active projects in the dataset.
        """
    )


def format_number(value: int | float) -> str:
    return f"{value:,.0f}"


def format_percentage(value: float) -> str:
    return f"{value:.1%}"


def format_price(value: float) -> str:
    return f"TND {value:,.0f}"


def load_dashboard_data() -> pd.DataFrame | None:
    try:
        return load_projects_data()
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to load project dataset: {error}")
        st.info("Please verify `data/projects.csv` and try again.")
        return None


def render_kpi_section(projects_df: pd.DataFrame) -> None:
    try:
        kpi_values = calculate_kpis(projects_df)
    except ValueError as error:
        st.error(f"Unable to calculate KPIs: {error}")
        return

    st.subheader("Executive KPI Overview")
    top_row = st.columns(4)
    bottom_row = st.columns(3)

    top_row[0].metric("Total Leads", format_number(kpi_values["total_leads"]))
    top_row[1].metric(
        "Qualified Leads", format_number(kpi_values["total_qualified_leads"])
    )
    top_row[2].metric(
        "Qualified Lead Rate", format_percentage(kpi_values["qualified_lead_rate"])
    )
    top_row[3].metric("Total Sales", format_number(kpi_values["total_sales"]))

    bottom_row[0].metric(
        "Unsold Inventory", format_number(kpi_values["total_unsold_inventory"])
    )
    bottom_row[1].metric(
        "Average Price", format_price(kpi_values["average_property_price"])
    )
    bottom_row[2].metric(
        "Visit to Reservation Rate",
        format_percentage(kpi_values["visit_to_reservation_rate"]),
    )


def render_data_preview(projects_df: pd.DataFrame) -> None:
    st.subheader("Dataset Preview")
    st.write(f"Projects loaded: **{len(projects_df):,}**")
    st.dataframe(projects_df.head(10), use_container_width=True, hide_index=True)
    st.caption("Showing the first 10 rows from `data/projects.csv`.")


def main() -> None:
    configure_page()
    render_home()
    projects_df = load_dashboard_data()
    if projects_df is None:
        return

    render_kpi_section(projects_df)
    st.divider()
    render_data_preview(projects_df)


if __name__ == "__main__":
    main()
