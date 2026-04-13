import streamlit as st

from src.chatbot import answer_question_from_context
from src.dashboard_ui import (
    apply_dashboard_theme,
    dashboard_panel,
    render_page_hero,
    render_sidebar_block,
    render_source_chip,
)
from src.data_loader import load_projects_data_with_metadata
from src.gemini_client import GEMINI_MODEL_NAME
from src.insights_engine import build_dashboard_context
from src.presentation import full_page_title


def configure_page() -> None:
    st.set_page_config(
        page_title=full_page_title("AI Chatbot"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()


def source_display_name(source: str) -> str:
    return "Curated project metrics" if source == "curated" else "Legacy projects dataset"


@st.cache_data(show_spinner=False)
def load_chat_context(top_n: int) -> tuple[dict, str, str, int]:
    """Build compact context once for the chatbot."""
    projects_df, source, source_path = load_projects_data_with_metadata()
    context = build_dashboard_context(
        projects_df,
        top_n=top_n,
        source_label=source_display_name(source),
        source_path=str(source_path),
    )
    return context, source, str(source_path), int(len(projects_df))


def initialize_chat_state() -> None:
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = [
            {
                "role": "assistant",
                "content": (
                    "I can answer questions about leads, city performance, forecasting, risk, "
                    "and recommendations using the current dashboard context."
                ),
            }
        ]


def render_header() -> None:
    render_page_hero(
        "AI Chatbot",
        "Ask practical questions about the portfolio. Responses are grounded in compact dashboard context only.",
    )


def render_sidebar() -> int:
    render_sidebar_block(
        "Chatbot Controls",
        "Tune context depth and reset conversation when starting a new scenario.",
    )
    context_depth = int(st.sidebar.slider("Context Depth", min_value=4, max_value=10, value=6, step=1))
    if st.sidebar.button("Clear Chat", use_container_width=True):
        st.session_state.ai_chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Chat reset. Ask any question about projects, cities, risks, forecasts, "
                    "or recommended actions."
                ),
            }
        ]
    return context_depth


def _render_chat_history() -> None:
    for message in st.session_state.ai_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _handle_chat_error(error: Exception) -> None:
    message = str(error)
    message_lower = message.lower()
    with st.chat_message("assistant"):
        st.error(f"I could not generate a response: {message}")
        if "quota exceeded" in message_lower or "resource_exhausted" in message_lower:
            st.caption(
                "Gemini quota is exhausted for this project. Wait for reset or use a key/project with available quota."
            )
            return
        if "api key" in message_lower or "missing" in message_lower:
            st.caption(
                "Set a valid `GEMINI_API_KEY`/`GOOGLE_API_KEY` for a Gemini-enabled project."
            )
            return
        st.caption("Verify `google-genai` installation and Gemini project permissions/billing.")


def main() -> None:
    configure_page()
    render_header()
    initialize_chat_state()

    context_depth = render_sidebar()
    try:
        context, source, source_path, project_count = load_chat_context(context_depth)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to prepare chatbot context: {error}")
        return

    render_source_chip(
        (
            f"Source: {source_display_name(source)} | {project_count:,} rows | "
            f"Model: {GEMINI_MODEL_NAME} | {source_path}"
        )
    )

    with dashboard_panel(
        "Suggested Questions",
        "Try focused prompts like: 'Which city has the strongest demand signal?', 'Which projects are high risk?', or 'Where should we increase marketing?'.",
    ):
        _render_chat_history()

    user_question = st.chat_input("Ask about projects, cities, forecasts, risks, or recommended actions...")
    if not user_question:
        return

    st.session_state.ai_chat_history.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing dashboard context..."):
                answer = answer_question_from_context(
                    user_question=user_question,
                    context=context,
                    chat_history=st.session_state.ai_chat_history[:-1],
                )
            st.markdown(answer)
    except (RuntimeError, ValueError) as error:
        _handle_chat_error(error)
        return

    st.session_state.ai_chat_history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
