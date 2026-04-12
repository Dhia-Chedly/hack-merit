import pandas as pd
import streamlit as st

from src.data_loader import load_projects_data_with_metadata
from src.decision_support import calculate_project_recommendations
from src.kpis import calculate_kpis
from src.presentation import (
    APP_NAME,
    format_currency,
    format_number,
    format_percentage,
    full_page_title,
)
from src.risk import calculate_project_risk


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("Overview"),
        layout="wide",
    )


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


def render_home() -> None:
    st.title(APP_NAME)
    st.markdown(
        """
        A Tunisia-focused decision intelligence MVP for real-estate teams.
        The platform combines **marketing performance**, **forecast momentum**, **risk signals**,
        and **recommended actions** to support faster commercial decisions.
        """
    )
    st.caption(
        "Use the left navigation to move from portfolio overview to map exploration, marketing analysis, forecasting, risk analysis, and decision support."
    )


def render_kpi_section(projects_df: pd.DataFrame) -> None:
    try:
        kpi_values = calculate_kpis(projects_df)
    except ValueError as error:
        st.error(f"Unable to calculate KPIs: {error}")
        return

    st.subheader("Portfolio KPI Snapshot")
    top_row = st.columns(4)
    bottom_row = st.columns(3)

    top_row[0].metric("Total Leads", format_number(kpi_values["total_leads"]))
    top_row[1].metric("Qualified Leads", format_number(kpi_values["total_qualified_leads"]))
    top_row[2].metric("Qualified Lead Rate", format_percentage(kpi_values["qualified_lead_rate"]))
    top_row[3].metric("Total Sales", format_number(kpi_values["total_sales"]))

    bottom_row[0].metric("Unsold Inventory", format_number(kpi_values["total_unsold_inventory"]))
    bottom_row[1].metric("Average Price", format_currency(kpi_values["average_property_price"]))
    bottom_row[2].metric(
        "Visit to Reservation Rate",
        format_percentage(kpi_values["visit_to_reservation_rate"]),
    )


def render_platform_summary(projects_df: pd.DataFrame) -> None:
    st.subheader("Platform Summary")
    city_count = int(projects_df["city"].nunique())
    property_type_count = int(projects_df["property_type"].nunique())
    top_city_by_leads = (
        projects_df.groupby("city", as_index=False)["leads"].sum().sort_values("leads", ascending=False)
    )
    top_city_name = "N/A" if top_city_by_leads.empty else str(top_city_by_leads.iloc[0]["city"])

    col_1, col_2, col_3 = st.columns(3)
    col_1.metric("Projects in Portfolio", format_number(len(projects_df)))
    col_2.metric("Cities Covered", format_number(city_count))
    col_3.metric("Property Types", format_number(property_type_count))

    st.caption(f"Highest lead concentration currently appears in **{top_city_name}**.")


def _prepare_home_decision_tables(projects_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    decision_df = calculate_project_recommendations(projects_df)
    risk_df = calculate_project_risk(projects_df)

    top_recommendations = decision_df[
        [
            "project_name",
            "city",
            "recommended_action",
            "priority_score",
            "confidence_level",
        ]
    ].copy()
    top_recommendations = top_recommendations.sort_values(
        by=["priority_score", "project_name"], ascending=[False, True]
    ).head(3)

    top_risks = risk_df[
        [
            "project_name",
            "city",
            "risk_level",
            "risk_score",
            "top_risk_drivers",
        ]
    ].copy()
    top_risks = top_risks.sort_values(by=["risk_score", "project_name"], ascending=[False, True]).head(3)

    top_recommendations["priority_score"] = top_recommendations["priority_score"].map(
        lambda value: f"{float(value):.1f}"
    )
    top_risks["risk_score"] = top_risks["risk_score"].map(lambda value: f"{float(value):.1f}")

    return (
        top_recommendations.rename(
            columns={
                "project_name": "Project",
                "city": "City",
                "recommended_action": "Recommended Action",
                "priority_score": "Priority Score",
                "confidence_level": "Confidence",
            }
        ),
        top_risks.rename(
            columns={
                "project_name": "Project",
                "city": "City",
                "risk_level": "Risk Level",
                "risk_score": "Risk Score",
                "top_risk_drivers": "Top Risk Drivers",
            }
        ),
    )


def render_home_highlights(projects_df: pd.DataFrame) -> None:
    st.subheader("Immediate Signals")
    st.caption("A quick shortlist to anchor the demo narrative before diving into detailed pages.")

    try:
        recommendations_table, risks_table = _prepare_home_decision_tables(projects_df)
    except ValueError as error:
        st.warning(f"Decision and risk highlights are unavailable: {error}")
        return

    col_reco, col_risk = st.columns(2)
    with col_reco:
        st.markdown("**Top 3 Recommended Actions**")
        st.dataframe(recommendations_table, use_container_width=True, hide_index=True, height=180)

    with col_risk:
        st.markdown("**Top 3 Risk Alerts**")
        st.dataframe(risks_table, use_container_width=True, hide_index=True, height=180)


def render_data_preview(projects_df: pd.DataFrame, data_source: str, source_path: str) -> None:
    st.subheader("Data Coverage Preview")
    st.caption(
        f"Rows loaded: **{len(projects_df):,}** | Source: **{source_display_name(data_source)}** (`{source_path}`)"
    )

    preview_columns = [
        "project_name",
        "city",
        "neighborhood",
        "property_type",
        "leads",
        "qualified_leads",
        "sales",
        "unsold_inventory",
        "avg_price",
    ]
    preview_df = projects_df[preview_columns].copy().head(10)
    preview_df["leads"] = preview_df["leads"].map(format_number)
    preview_df["qualified_leads"] = preview_df["qualified_leads"].map(format_number)
    preview_df["sales"] = preview_df["sales"].map(format_number)
    preview_df["unsold_inventory"] = preview_df["unsold_inventory"].map(format_number)
    preview_df["avg_price"] = preview_df["avg_price"].map(format_currency)

    st.dataframe(
        preview_df.rename(
            columns={
                "project_name": "Project",
                "city": "City",
                "neighborhood": "Neighborhood",
                "property_type": "Property Type",
                "leads": "Leads",
                "qualified_leads": "Qualified Leads",
                "sales": "Sales",
                "unsold_inventory": "Unsold Inventory",
                "avg_price": "Average Price",
            }
        ),
        use_container_width=True,
        hide_index=True,
        height=320,
    )


def main() -> None:
    configure_page()
    render_home()

    load_result = load_dashboard_data()
    if load_result is None:
        return
    projects_df, data_source, source_path = load_result

    render_kpi_section(projects_df)
    st.divider()
    render_platform_summary(projects_df)
    st.divider()
    render_home_highlights(projects_df)
    st.divider()
    render_data_preview(projects_df, data_source, source_path)


if __name__ == "__main__":
    main()
