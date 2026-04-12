import streamlit as st

from src.dashboard_ui import (
    apply_dashboard_theme,
    dashboard_panel,
    render_kpi_cards,
    render_page_hero,
    render_sidebar_block,
    render_source_chip,
)
from src.data_loader import load_projects_data_with_metadata
from src.gemini_client import GEMINI_MODEL_NAME
from src.insights_engine import (
    build_dashboard_context,
    generate_focus_brief,
    generate_structured_insights,
)
from src.presentation import format_currency, format_number, format_percentage, full_page_title


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("AI Insights"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()


def source_display_name(source: str) -> str:
    return "Curated project metrics" if source == "curated" else "Legacy projects dataset"


@st.cache_data(show_spinner=False)
def load_ai_context(top_n: int) -> tuple[dict, str, str, int]:
    """Load dataset and build compact context once per filter depth."""
    projects_df, source, source_path = load_projects_data_with_metadata()
    context = build_dashboard_context(
        projects_df,
        top_n=top_n,
        source_label=source_display_name(source),
        source_path=str(source_path),
    )
    return context, source, str(source_path), int(len(projects_df))


def render_header() -> None:
    render_page_hero(
        "AI Insights",
        "Generate concise executive intelligence from the current dashboard context using Gemini.",
    )


def render_sidebar() -> int:
    render_sidebar_block(
        "AI Insight Controls",
        "Choose how much ranked context to include in prompts. Higher values increase detail and token usage.",
    )
    return int(st.sidebar.slider("Context Depth", min_value=4, max_value=10, value=6, step=1))


def render_context_snapshot(context: dict, project_count: int) -> None:
    kpis = context.get("headline_kpis", {})

    cards = [
        {
            "label": "Projects in Context",
            "value": format_number(project_count),
            "subtext": "Current portfolio scope",
        },
        {
            "label": "Total Leads",
            "value": format_number(kpis.get("total_leads", 0)),
            "subtext": "Demand volume in prompt context",
        },
        {
            "label": "Qualified Lead Rate",
            "value": format_percentage(kpis.get("qualified_lead_rate", 0.0)),
            "subtext": "Lead quality baseline",
        },
        {
            "label": "Cost per Qualified Lead",
            "value": format_currency(kpis.get("cost_per_qualified_lead", 0.0)),
            "subtext": "Acquisition efficiency anchor",
        },
        {
            "label": "Total Sales",
            "value": format_number(kpis.get("total_sales", 0)),
            "subtext": "Current portfolio closes",
        },
    ]
    render_kpi_cards(cards, columns=5)


def _render_structured_output(payload: dict[str, list[str]]) -> None:
    col_insights, col_risks, col_actions = st.columns(3)

    with col_insights:
        st.markdown("**3 Key Insights**")
        for item in payload.get("key_insights", []):
            st.markdown(f"- {item}")

    with col_risks:
        st.markdown("**2 Main Risks**")
        for item in payload.get("main_risks", []):
            st.markdown(f"- {item}")

    with col_actions:
        st.markdown("**2 Recommended Actions**")
        for item in payload.get("recommended_actions", []):
            st.markdown(f"- {item}")


def _handle_ai_error(error: Exception) -> None:
    st.error(f"AI generation failed: {error}")
    st.info("Set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) and ensure `google-genai` is installed.")


def main() -> None:
    configure_page()
    render_header()

    top_n = render_sidebar()

    try:
        context, source, source_path, project_count = load_ai_context(top_n)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to prepare AI context: {error}")
        return

    render_source_chip(
        (
            f"Source: {source_display_name(source)} | {project_count:,} rows | "
            f"Model: {GEMINI_MODEL_NAME} | {source_path}"
        )
    )

    with dashboard_panel("Context Snapshot", "Compact data summary used for AI insight generation."):
        render_context_snapshot(context, project_count)

    col_exec, col_risk, col_city = st.columns(3)
    with col_exec:
        run_executive = st.button("Generate Executive Summary", use_container_width=True)
    with col_risk:
        run_risks = st.button("Explain Top Risks", use_container_width=True)
    with col_city:
        run_city = st.button("Summarize City Performance", use_container_width=True)

    if "ai_executive_output" not in st.session_state:
        st.session_state.ai_executive_output = None
    if "ai_risk_brief" not in st.session_state:
        st.session_state.ai_risk_brief = None
    if "ai_city_brief" not in st.session_state:
        st.session_state.ai_city_brief = None

    if run_executive:
        try:
            with st.spinner("Generating executive summary..."):
                st.session_state.ai_executive_output = generate_structured_insights(
                    context,
                    focus="Executive summary with portfolio highlights, critical risks, and immediate actions.",
                )
        except (RuntimeError, ValueError) as error:
            _handle_ai_error(error)

    if run_risks:
        try:
            with st.spinner("Explaining top risks..."):
                st.session_state.ai_risk_brief = generate_focus_brief(
                    context,
                    topic="Explain the top commercial risks and why they matter now.",
                )
        except (RuntimeError, ValueError) as error:
            _handle_ai_error(error)

    if run_city:
        try:
            with st.spinner("Summarizing city performance..."):
                st.session_state.ai_city_brief = generate_focus_brief(
                    context,
                    topic="Summarize city performance differences for demand, conversion, and risk exposure.",
                )
        except (RuntimeError, ValueError) as error:
            _handle_ai_error(error)

    with dashboard_panel("Executive Insight Output", "3 insights, 2 risks, and 2 action recommendations."):
        if st.session_state.ai_executive_output:
            _render_structured_output(st.session_state.ai_executive_output)
        else:
            st.caption("Click `Generate Executive Summary` to produce AI insights.")

    with dashboard_panel("Top Risk Explanation", "Focused narrative on the strongest portfolio risk signals."):
        if st.session_state.ai_risk_brief:
            st.markdown(st.session_state.ai_risk_brief)
        else:
            st.caption("Click `Explain Top Risks` for a risk-focused AI brief.")

    with dashboard_panel("City Performance Summary", "Focused narrative comparing city-level performance."):
        if st.session_state.ai_city_brief:
            st.markdown(st.session_state.ai_city_brief)
        else:
            st.caption("Click `Summarize City Performance` for a city-level AI brief.")


if __name__ == "__main__":
    main()
