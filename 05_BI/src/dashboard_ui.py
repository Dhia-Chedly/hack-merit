from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable

import plotly.graph_objects as go
import streamlit as st


_DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-main: #e8efea;
    --bg-card: #ffffff;
    --bg-sidebar: #2b2d31;
    --text-primary: #1a1d23;
    --text-secondary: #5a5f6b;
    --text-muted: #8b919d;
    --accent: #e87461;
    --accent-dark: #2b2d31;
    --border: #d4dbd6;
    --border-light: #e2e8e4;
    --card-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* ── Reset animations globally ── */
*, *::before, *::after {
    transition: none !important;
    animation: none !important;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: var(--bg-main) !important;
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

[data-testid="stHeader"] {
    display: none !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: none;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.65rem;
}

[data-testid="stSidebar"],
[data-testid="stSidebar"] * {
    color: #e4e5e7;
}

[data-testid="stSidebarNav"] {
    padding-top: 0.25rem;
    margin-bottom: 0.5rem;
}

[data-testid="stSidebarNav"]::before {
    content: "Navigation";
    display: block;
    margin: 0.1rem 0.2rem 0.4rem 0.2rem;
    color: #9b9da2;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 600;
}

[data-testid="stSidebarNav"] a {
    border-radius: 6px;
    margin: 0.08rem 0;
    padding-top: 0.22rem;
    padding-bottom: 0.22rem;
    border: none !important;
}

[data-testid="stSidebarNav"] a:hover {
    background: rgba(255, 255, 255, 0.08) !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(232, 116, 97, 0.18) !important;
    border: none !important;
}

/* ── Main content area ── */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1480px;
}

h1, h2, h3, h4 {
    color: var(--text-primary) !important;
    letter-spacing: -0.01em;
    line-height: 1.25;
    font-weight: 700;
}

p, li, label, .stCaption, small, .stMarkdown, .stText {
    color: var(--text-secondary);
    line-height: 1.5;
}

/* ── Page hero ── */
.dashboard-hero {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.25rem 0.9rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: var(--card-shadow);
}

.dashboard-hero-title {
    font-size: 1.35rem;
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 0.2rem;
    color: var(--text-primary);
}

.dashboard-hero-subtitle {
    color: var(--text-secondary);
    font-size: 0.85rem;
    max-width: 900px;
}

/* ── Source chip ── */
.source-chip {
    display: inline-block;
    margin-top: 0.2rem;
    margin-bottom: 0.5rem;
    font-size: 0.7rem;
    color: var(--text-muted);
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.18rem 0.55rem;
}

/* ── KPI cards (responsive) ── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    box-shadow: var(--card-shadow);
    padding: 0;
    min-height: 0;
    overflow: hidden;
    margin-bottom: 0.4rem;
}

.kpi-card-header {
    background: var(--accent-dark);
    padding: 0.35rem 0.6rem;
    min-height: 2rem;
    display: flex;
    align-items: center;
}

.kpi-label {
    color: #e4e5e7;
    font-size: 0.58rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    line-height: 1.3;
}

.kpi-body {
    padding: 0.5rem 0.75rem 0.6rem 0.75rem;
}

.kpi-value {
    color: var(--text-primary);
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 0.12rem;
    white-space: nowrap;
}

.kpi-subtext {
    color: var(--text-muted);
    font-size: 0.68rem;
    line-height: 1.3;
}

.kpi-delta {
    display: inline-block;
    margin-right: 0.25rem;
    font-size: 0.68rem;
    color: var(--accent);
    font-weight: 600;
}

/* ── Column padding ── */
[data-testid="column"] > div {
    padding-bottom: 0.1rem;
}

/* ── Panels / bordered containers ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    background: var(--bg-card) !important;
    box-shadow: var(--card-shadow);
    padding: 0.5rem 0.75rem;
    margin-bottom: 0.75rem;
}

.panel-header {
    margin-bottom: 0.5rem;
}

.panel-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.panel-subtitle {
    color: var(--text-muted);
    font-size: 0.75rem;
    margin-top: 0.08rem;
}

/* ── Data frames ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    background: var(--bg-card);
}

/* ── Form inputs (sidebar) ── */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div {
    background-color: #383a3f !important;
    border-color: #4a4c52 !important;
    border-radius: 6px !important;
    min-height: 2.2rem;
    color: #e4e5e7 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
[data-testid="stSidebar"] [data-baseweb="input"] > div:hover {
    border-color: #5a5c62 !important;
}

[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: rgba(232, 116, 97, 0.22) !important;
    border: 1px solid rgba(232, 116, 97, 0.35) !important;
    color: #e4e5e7 !important;
    border-radius: 4px !important;
    font-size: 0.68rem !important;
}

/* ── Main area inputs ── */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    border-radius: 6px !important;
    border-color: var(--border) !important;
}

/* ── Sidebar labels ── */
[data-testid="stSidebar"] label {
    color: #c0c2c7 !important;
    font-size: 0.66rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}

.sidebar-block {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.05);
    padding: 0.55rem 0.65rem;
    margin-bottom: 0.5rem;
}

.sidebar-title {
    font-size: 0.76rem;
    font-weight: 600;
    margin-bottom: 0.1rem;
    color: #e4e5e7;
}

.sidebar-caption {
    color: #9b9da2;
    font-size: 0.68rem;
    line-height: 1.35;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 6px;
    background: var(--bg-card);
}

/* ── Divider ── */
.stDivider {
    opacity: 0.3;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--accent-dark) !important;
    color: #e4e5e7 !important;
    border: none !important;
    border-radius: 6px !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 0.45rem 0.8rem !important;
    white-space: nowrap !important;
    overflow: hidden;
    text-overflow: ellipsis;
}

.stButton > button:hover {
    background: #3d3f44 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 2px solid transparent;
    padding: 0.45rem 0.9rem;
}

.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Chat styling ── */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-light);
    border-radius: 6px;
}

/* ── Slider ── */
[data-testid="stSidebar"] .stSlider > div > div > div {
    color: #e4e5e7 !important;
}

/* ── Tooltip override for PyDeck ── */
.deck-tooltip {
    background-color: var(--accent-dark) !important;
    color: #e4e5e7 !important;
    font-size: 12px !important;
    border-radius: 6px !important;
    border: none !important;
}

/* ── Responsive: ensure plotly titles don't show "undefined" ── */
/* This is handled in style_plotly_figure by explicitly setting title */

/* ── Responsive breakpoints ── */
@media (max-width: 1200px) {
    .kpi-value {
        font-size: 1.3rem;
    }
    .kpi-label {
        font-size: 0.55rem;
    }
    .kpi-subtext {
        font-size: 0.62rem;
    }
    .panel-title {
        font-size: 0.8rem;
    }
}

@media (max-width: 900px) {
    .kpi-value {
        font-size: 1.15rem;
    }
    .kpi-label {
        font-size: 0.52rem;
        letter-spacing: 0.06em;
    }
    .kpi-subtext, .kpi-delta {
        font-size: 0.58rem;
    }
    .kpi-body {
        padding: 0.35rem 0.55rem 0.4rem 0.55rem;
    }
    .kpi-card-header {
        padding: 0.3rem 0.55rem;
    }
    .dashboard-hero-title {
        font-size: 1.1rem;
    }
    .dashboard-hero-subtitle {
        font-size: 0.78rem;
    }
    .panel-title {
        font-size: 0.75rem;
    }
    .panel-subtitle {
        font-size: 0.68rem;
    }
}

@media (max-width: 640px) {
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .kpi-value {
        font-size: 1rem;
    }
    .dashboard-hero {
        padding: 0.7rem 0.9rem;
    }
}
</style>
"""


def apply_dashboard_theme() -> None:
    st.markdown(_DASHBOARD_CSS, unsafe_allow_html=True)


def render_page_hero(title: str, subtitle: str) -> None:
    st.markdown(
        (
            "<div class='dashboard-hero'>"
            f"<div class='dashboard-hero-title'>{title}</div>"
            f"<div class='dashboard-hero-subtitle'>{subtitle}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_source_chip(label: str) -> None:
    st.markdown(f"<span class='source-chip'>{label}</span>", unsafe_allow_html=True)


def render_sidebar_block(title: str, caption: str | None = None) -> None:
    caption_html = f"<div class='sidebar-caption'>{caption}</div>" if caption else ""
    st.sidebar.markdown(
        (
            "<div class='sidebar-block'>"
            f"<div class='sidebar-title'>{title}</div>"
            f"{caption_html}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_kpi_cards(cards: Iterable[dict[str, str]], columns: int = 4) -> None:
    card_list = list(cards)
    if not card_list:
        return

    row_start = 0
    while row_start < len(card_list):
        row_cards = card_list[row_start : row_start + columns]
        cols = st.columns(len(row_cards))
        for idx, col in enumerate(cols):
            with col:
                card = row_cards[idx]
                label = card.get("label", "")
                value = card.get("value", "")
                subtext = card.get("subtext", "")
                delta = card.get("delta", "")
                st.markdown(
                    (
                        "<div class='kpi-card'>"
                        f"<div class='kpi-card-header'><div class='kpi-label'>{label}</div></div>"
                        "<div class='kpi-body'>"
                        f"<div class='kpi-value'>{value}</div>"
                        "<div class='kpi-subtext'>"
                        f"{f'<span class=\"kpi-delta\">{delta}</span>' if delta else ''}"
                        f"{subtext}"
                        "</div>"
                        "</div>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
        row_start += columns


@contextmanager
def dashboard_panel(title: str, subtitle: str | None = None):
    try:
        container = st.container(border=True)
    except TypeError:
        container = st.container()

    with container:
        subtitle_html = f"<div class='panel-subtitle'>{subtitle}</div>" if subtitle else ""
        st.markdown(
            (
                "<div class='panel-header'>"
                f"<div class='panel-title'>{title}</div>"
                f"{subtitle_html}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        yield


def style_plotly_figure(fig: go.Figure, *, height: int | None = None) -> go.Figure:
    # Preserve the existing title text, but style it properly.
    current_title = fig.layout.title
    title_text = ""
    if current_title and hasattr(current_title, "text") and current_title.text:
        title_text = current_title.text

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=["#2b2d31", "#e87461", "#7bb8a0", "#5a8fcb", "#d4a556", "#9370b8"],
        font=dict(
            color="#1a1d23",
            family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            size=11,
        ),
        title=dict(
            text=title_text,
            font=dict(
                size=13,
                color="#1a1d23",
                family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            ),
            x=0,
            xanchor="left",
            y=0.98,
            yanchor="top",
        ),
        margin=dict(l=10, r=10, t=40 if title_text else 20, b=80),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="#d4dbd6",
            borderwidth=0.5,
            font=dict(color="#5a5f6b", size=10),
            orientation="h",
            yanchor="top",
            y=-0.35,
            xanchor="center",
            x=0.5,
        ),
        hoverlabel=dict(
            bgcolor="#2b2d31",
            bordercolor="#4a4c52",
            font=dict(color="#e4e5e7", size=11),
        ),
    )
    fig.update_xaxes(
        gridcolor="#e2e8e4",
        zeroline=False,
        tickfont=dict(color="#5a5f6b", size=10),
        title_font=dict(color="#5a5f6b", size=11),
        showline=True,
        linecolor="#d4dbd6",
        linewidth=1,
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor="#e2e8e4",
        zeroline=False,
        tickfont=dict(color="#5a5f6b", size=10),
        title_font=dict(color="#5a5f6b", size=11),
        showline=True,
        linecolor="#d4dbd6",
        linewidth=1,
        automargin=True,
    )
    if height is not None:
        fig.update_layout(height=height)
    return fig
