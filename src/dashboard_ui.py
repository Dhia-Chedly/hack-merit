from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable

import plotly.graph_objects as go
import streamlit as st


_DASHBOARD_CSS = """
<style>
:root {
    --bg-main: #050d1f;
    --bg-card: #0d1d3a;
    --bg-card-soft: #132b52;
    --bg-sidebar: #040b1a;
    --text-main: #f2f8ff;
    --text-muted: #afc5e8;
    --text-soft: #8fa9d3;
    --accent: #5eb8ff;
    --accent-2: #63f5d8;
    --panel-border: rgba(132, 184, 255, 0.3);
    --panel-shadow: 0 12px 30px rgba(3, 11, 28, 0.58);
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: radial-gradient(1400px 580px at 14% -8%, #103161 0%, var(--bg-main) 56%);
    color: var(--text-main);
    font-family: "Space Grotesk", "IBM Plex Sans", "Segoe UI", sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08162f 0%, var(--bg-sidebar) 100%);
    border-right: 1px solid rgba(123, 176, 255, 0.3);
    box-shadow: 10px 0 26px rgba(3, 9, 24, 0.4);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.55rem;
}

[data-testid="stSidebar"] * {
    color: var(--text-main);
}

[data-testid="stSidebarNav"] {
    padding-top: 0.25rem;
    margin-bottom: 0.55rem;
}

[data-testid="stSidebarNav"]::before {
    content: "Navigation";
    display: block;
    margin: 0.1rem 0.2rem 0.38rem 0.2rem;
    color: var(--text-soft);
    font-size: 0.7rem;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    font-weight: 650;
}

[data-testid="stSidebarNav"] a {
    border-radius: 10px;
    margin: 0.1rem 0;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    transition: background 120ms ease, border-color 120ms ease;
    border: 1px solid rgba(0, 0, 0, 0);
}

[data-testid="stSidebarNav"] a:hover {
    background: rgba(98, 171, 255, 0.18);
    border-color: rgba(112, 178, 255, 0.3);
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(89, 162, 248, 0.28);
    border: 1px solid rgba(108, 177, 255, 0.46);
}

.block-container {
    padding-top: 0.95rem !important;
    padding-bottom: 2rem !important;
    max-width: 1480px;
}

h1, h2, h3, h4 {
    color: var(--text-main) !important;
    letter-spacing: 0.006em;
    line-height: 1.24;
}

p, li, label, .stCaption, small, .stMarkdown, .stText {
    color: #d9e8ff;
    line-height: 1.45;
}

.dashboard-hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(140deg, rgba(17, 40, 78, 0.92), rgba(8, 20, 43, 0.96));
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    box-shadow: var(--panel-shadow);
    padding: 1.12rem 1.25rem 1.06rem 1.25rem;
    margin-bottom: 0.72rem;
}

.dashboard-hero::after {
    content: "";
    position: absolute;
    right: -55px;
    top: -55px;
    width: 210px;
    height: 210px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(86, 176, 255, 0.28) 0%, rgba(86, 176, 255, 0) 68%);
    pointer-events: none;
}

.dashboard-hero-title {
    font-size: 1.52rem;
    font-weight: 720;
    line-height: 1.25;
    margin-bottom: 0.22rem;
}

.dashboard-hero-subtitle {
    color: var(--text-muted);
    font-size: 0.92rem;
    max-width: 980px;
}

.source-chip {
    display: inline-block;
    margin-top: 0.25rem;
    font-size: 0.75rem;
    color: #c7dbfb;
    background: rgba(58, 122, 206, 0.22);
    border: 1px solid rgba(101, 164, 240, 0.48);
    border-radius: 999px;
    padding: 0.2rem 0.66rem;
}

.kpi-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(165deg, rgba(21, 44, 82, 0.95) 0%, rgba(12, 30, 58, 0.98) 100%);
    border: 1px solid rgba(128, 178, 255, 0.34);
    border-radius: 14px;
    box-shadow: 0 9px 24px rgba(7, 17, 40, 0.5);
    padding: 0.76rem 0.92rem 0.74rem 0.92rem;
    min-height: 108px;
    transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
}

.kpi-card::before {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 2px;
    background: linear-gradient(90deg, rgba(92, 180, 255, 0.96), rgba(99, 245, 216, 0.9));
}

.kpi-card:hover {
    border-color: rgba(145, 198, 255, 0.52);
    box-shadow: 0 12px 27px rgba(12, 34, 70, 0.58);
    transform: translateY(-1.5px);
}

.kpi-label {
    color: var(--text-muted);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.38rem;
    font-weight: 650;
}

.kpi-value {
    color: #ffffff;
    font-size: 1.74rem;
    font-weight: 760;
    line-height: 1.1;
    margin-bottom: 0.22rem;
}

.kpi-subtext {
    color: #a9c8f3;
    font-size: 0.79rem;
    min-height: 1.05rem;
}

.kpi-delta {
    display: inline-block;
    margin-right: 0.34rem;
    font-size: 0.74rem;
    color: #85eecf;
    font-weight: 700;
    letter-spacing: 0.01em;
}

[data-testid="column"] > div {
    padding-bottom: 0.18rem;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--panel-border) !important;
    border-radius: 14px !important;
    background: linear-gradient(180deg, rgba(11, 27, 54, 0.94), rgba(7, 18, 39, 0.97));
    box-shadow: var(--panel-shadow);
    padding: 0.42rem 0.58rem 0.46rem 0.58rem;
    margin-bottom: 0.86rem;
}

.panel-header {
    margin-bottom: 0.58rem;
    padding-left: 0.04rem;
    padding-right: 0.04rem;
}

.panel-title {
    font-size: 1.02rem;
    font-weight: 690;
    color: #ecf5ff;
}

.panel-subtitle {
    color: var(--text-muted);
    font-size: 0.8rem;
    margin-top: 0.14rem;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(128, 177, 246, 0.3);
    border-radius: 12px;
    overflow: hidden;
    background: rgba(8, 20, 42, 0.68);
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    background-color: #0b1d3b !important;
    border-color: rgba(122, 173, 250, 0.42) !important;
    border-radius: 10px !important;
    min-height: 2.36rem;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

[data-baseweb="select"] > div:hover,
[data-baseweb="input"] > div:hover {
    border-color: rgba(135, 190, 255, 0.6) !important;
}

[data-baseweb="tag"] {
    background: rgba(87, 145, 236, 0.29) !important;
    border: 1px solid rgba(122, 184, 255, 0.46) !important;
    color: #e8f3ff !important;
}

[data-testid="stSidebar"] label {
    color: #bfd4f6 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 650;
}

.sidebar-block {
    border: 1px solid rgba(120, 174, 252, 0.28);
    border-radius: 12px;
    background: rgba(16, 37, 73, 0.62);
    padding: 0.64rem 0.72rem;
    margin-bottom: 0.58rem;
}

.sidebar-title {
    font-size: 0.8rem;
    font-weight: 680;
    margin-bottom: 0.14rem;
    letter-spacing: 0.02em;
}

.sidebar-caption {
    color: var(--text-soft);
    font-size: 0.74rem;
    line-height: 1.36;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(121, 174, 250, 0.28) !important;
    border-radius: 12px;
    background: rgba(11, 26, 52, 0.66);
}

.stDivider {
    opacity: 0.2;
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
        cols = st.columns(columns)
        for idx in range(columns):
            with cols[idx]:
                if idx >= len(row_cards):
                    st.empty()
                    continue
                card = row_cards[idx]
                label = card.get("label", "")
                value = card.get("value", "")
                subtext = card.get("subtext", "")
                delta = card.get("delta", "")
                st.markdown(
                    (
                        "<div class='kpi-card'>"
                        f"<div class='kpi-label'>{label}</div>"
                        f"<div class='kpi-value'>{value}</div>"
                        "<div class='kpi-subtext'>"
                        f"{f'<span class=\"kpi-delta\">{delta}</span>' if delta else ''}"
                        f"{subtext}"
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
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=["#5db8ff", "#65f4d8", "#8f7dff", "#ffb156", "#ff6d90"],
        font=dict(color="#edf6ff", family="Space Grotesk, IBM Plex Sans, Segoe UI, sans-serif"),
        title_font=dict(size=15, color="#edf6ff", family="Space Grotesk, IBM Plex Sans, Segoe UI, sans-serif"),
        margin=dict(l=8, r=8, t=44, b=14),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(121, 170, 252, 0.18)",
            borderwidth=0.8,
            font=dict(color="#d7e8ff"),
        ),
        hoverlabel=dict(
            bgcolor="rgba(9, 24, 48, 0.96)",
            bordercolor="rgba(122, 179, 255, 0.42)",
            font=dict(color="#ebf5ff"),
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(165, 199, 247, 0.2)",
        zeroline=False,
        tickfont=dict(color="#d7e8ff"),
        title_font=dict(color="#d7e8ff"),
    )
    fig.update_yaxes(
        gridcolor="rgba(165, 199, 247, 0.2)",
        zeroline=False,
        tickfont=dict(color="#d7e8ff"),
        title_font=dict(color="#d7e8ff"),
    )
    if height is not None:
        fig.update_layout(height=height)
    return fig
