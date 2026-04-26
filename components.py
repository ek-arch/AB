"""
Visibility Monitor — design system helpers for Streamlit.

Usage:
    import streamlit as st
    from components import inject_css, page_header, stat_saturation, \
        stat_top30, stat_knowledge_graph, results_list, ResultRow

    st.set_page_config(page_title="Visibility Monitor", layout="wide")
    inject_css()
    # ... build the page using helpers below.
"""

from __future__ import annotations
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable, Literal, Optional

import streamlit as st

# --------------------------------------------------------------------- #
# CSS injection
# --------------------------------------------------------------------- #

_CSS_PATH = Path(__file__).parent / "styles.css"


def inject_css() -> None:
    """Inject styles.css once per session. Call right after set_page_config."""
    if st.session_state.get("_vm_css_injected"):
        return
    css = _CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    st.session_state["_vm_css_injected"] = True


def _html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


# --------------------------------------------------------------------- #
# Page header (eyebrow + title + lede)
# --------------------------------------------------------------------- #

def page_header(
    section_num: str,
    title: str,
    lede: Optional[str] = None,
    *,
    eyebrow: str = "Section",
    meta: Optional[str] = "Updated 2 min ago",
    query: Optional[str] = None,
) -> None:
    """Render the standard page header.

    `lede` may contain a literal token "{q}"; if `query` is provided it is
    rendered as a highlighted query pill.
    """
    parts = [
        '<div class="vm-eyebrow">',
        f'  <span class="vm-badge-num">{escape(section_num)}</span>',
        f'  <span>{escape(eyebrow)}</span>',
    ]
    if meta:
        parts += ['  <span class="vm-dot">·</span>', f'  <span>{escape(meta)}</span>']
    parts += ['</div>', f'<h1 class="vm-h1">{escape(title)}</h1>']

    if lede:
        body = escape(lede)
        if query and "{q}" in lede:
            body = escape(lede).replace(
                "{q}", f'<span class="vm-q">"{escape(query)}"</span>'
            )
        # let **bold** survive
        import re
        body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
        parts.append(f'<p class="vm-lede">{body}</p>')

    _html("\n".join(parts))


# --------------------------------------------------------------------- #
# Sidebar status chip
# --------------------------------------------------------------------- #

def sidebar_status(label: str = "API connected") -> None:
    _html(
        f'<div class="vm-status"><span class="vm-pulse"></span>{escape(label)}</div>'
    )


# --------------------------------------------------------------------- #
# Stat cards
# --------------------------------------------------------------------- #

def _stat_open(priority: bool = False) -> str:
    cls = "vm-stat vm-stat--priority" if priority else "vm-stat"
    return f'<div class="{cls}">'


def stat_saturation(num: int, total: int = 10, label: str = "Page 1 saturation",
                    owned: int = 0, earned: int = 0, strong_label: str = "STRONG") -> str:
    segs = "".join(
        f'<span class="vm-bar__seg{" vm-bar__seg--on" if i < num else ""}"></span>'
        for i in range(total)
    )
    return (
        f'{_stat_open()}'
        f'<div class="vm-stat__label">{escape(label)}</div>'
        f'<div class="vm-stat__big">'
        f'  <span class="vm-stat__num">{num}</span>'
        f'  <span class="vm-stat__den">/{total}</span>'
        f'  <span class="vm-tag vm-tag--strong" style="margin-left:8px;">{escape(strong_label)}</span>'
        f'</div>'
        f'<div class="vm-bar">{segs}</div>'
        f'<div class="vm-stat__caption">'
        f'<strong>{owned} owned</strong>'
        f'<span style="color:var(--vm-faint);margin:0 6px;">·</span>'
        f'{earned} earned</div>'
        f'</div>'
    )


def stat_top30(num: int, total: int = 28, label: str = "Top 30 · 3 pages",
               owned: int = 0, earned: int = 0, neutral: int = 0, negative: int = 0) -> str:
    def pct(x: int) -> str:
        return f"{(x / total * 100):.4f}%"
    return (
        f'{_stat_open()}'
        f'<div class="vm-stat__label">{escape(label)}</div>'
        f'<div class="vm-stat__big">'
        f'  <span class="vm-stat__num">{num}</span>'
        f'  <span class="vm-stat__den">/{total}</span>'
        f'</div>'
        f'<div class="vm-stacked">'
        f'  <div class="vm-stacked__seg vm-stacked__seg--owned"    style="width:{pct(owned)}"></div>'
        f'  <div class="vm-stacked__seg vm-stacked__seg--earned"   style="width:{pct(earned)}"></div>'
        f'  <div class="vm-stacked__seg vm-stacked__seg--neutral"  style="width:{pct(neutral)}"></div>'
        f'  <div class="vm-stacked__seg vm-stacked__seg--negative" style="width:{pct(negative)}"></div>'
        f'</div>'
        f'<div class="vm-legend">'
        f'  <span class="vm-legend__item"><span class="vm-legend__sw vm-legend__sw--owned"></span>{owned} owned</span>'
        f'  <span class="vm-legend__item"><span class="vm-legend__sw vm-legend__sw--earned"></span>{earned} earned</span>'
        f'  <span class="vm-legend__item"><span class="vm-legend__sw vm-legend__sw--neutral"></span>{neutral} neutral</span>'
        f'  <span class="vm-legend__item"><span class="vm-legend__sw vm-legend__sw--negative"></span>{negative} negative</span>'
        f'</div>'
        f'</div>'
    )


def stat_knowledge_graph(state: str = "Missing", priority: bool = True,
                         label: str = "Knowledge graph",
                         description: str = (
                             "The strongest signal Google has built an entity card "
                             "for the name. Currently absent — biggest single lever."
                         )) -> str:
    pri_tag = '<span class="vm-tag vm-tag--priority">PRIORITY</span>' if priority else ""
    return (
        f'{_stat_open(priority=priority)}'
        f'<div class="vm-stat__label">{escape(label)}{pri_tag}</div>'
        f'<div class="vm-stat__missing">{escape(state)}</div>'
        f'<div class="vm-stat__desc">{escape(description)}</div>'
        f'</div>'
    )


def stats_row(*cards: str) -> None:
    """Render stat cards side-by-side. Pass HTML strings produced by stat_* helpers."""
    _html('<div class="vm-stats">' + "".join(cards) + "</div>")


# --------------------------------------------------------------------- #
# Results list
# --------------------------------------------------------------------- #

Status = Literal["owned", "earned", "neutral", "negative"]


@dataclass
class ResultRow:
    n: str
    title: str
    url: str
    snippet: str
    status: Status = "neutral"


_PILL_LABELS = {
    "owned": "Owned",
    "earned": "Earned",
    "neutral": "Neutral",
    "negative": "Negative",
}


def status_pill(status: Status) -> str:
    return f'<span class="vm-pill vm-pill--{status}">{_PILL_LABELS[status]}</span>'


def results_header(title: str = "All results", visible: int = 0,
                   hidden: int = 0, pages: int = 3,
                   active_filter: str = "All",
                   filters: Iterable[str] = ("All", "Owned", "Earned", "Neutral", "Negative")) -> None:
    chips = "".join(
        f'<button class="vm-chip{" vm-chip--active" if f == active_filter else ""}">{escape(f)}</button>'
        for f in filters
    )
    _html(
        f'<div class="vm-results-head">'
        f'  <div>'
        f'    <span class="vm-results-head__title">{escape(title)}</span>'
        f'    <span class="vm-results-head__count">{visible} visible · {hidden} hidden · {pages} pages</span>'
        f'  </div>'
        f'  <div class="vm-filters">{chips}</div>'
        f'</div>'
    )


def results_list(rows: Iterable[ResultRow]) -> None:
    items = []
    for r in rows:
        row_cls = "vm-row vm-row--negative" if r.status == "negative" else "vm-row"
        num_cls = f"vm-row__num vm-row__num--{r.status}" if r.status in ("owned", "earned", "negative") else "vm-row__num"
        items.append(
            f'<div class="{row_cls}">'
            f'  <div class="{num_cls}">{escape(r.n)}</div>'
            f'  <div>'
            f'    <div class="vm-row__title">{escape(r.title)}</div>'
            f'    <a class="vm-row__url" href="{escape(r.url)}" target="_blank" rel="noopener">{escape(r.url)}</a>'
            f'    <div class="vm-row__snippet">{escape(r.snippet)}</div>'
            f'  </div>'
            f'  <div style="padding-top:4px;">{status_pill(r.status)}</div>'
            f'  <div></div>'  # hide button slot — wire up via st.button below the row if needed
            f'</div>'
        )
    _html('<div class="vm-results">' + "".join(items) + "</div>")
