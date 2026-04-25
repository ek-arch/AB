"""
Visibility Monitor — Andrii Bruiaka
SerpAPI-powered SERP/GEO audit dashboard

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import json
import time
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Visibility Monitor",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# THEME / CSS
# ============================================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,800;1,9..144,400&family=JetBrains+Mono:wght@300;400;500;700&display=swap');

:root {
  --bg: #FAF7F0;
  --surface: #FFFFFF;
  --surface-2: #EDE6D2;
  --border: #C9C2B0;
  --border-bright: #9E957F;
  --text: #15130F;
  --text-dim: #2A2722;
  --muted: #555049;
  --accent: #1A4234;
  --accent-light: #2D6B54;
  --good: #2C5F3F;
  --warn: #8C4500;
  --bad: #862A21;
  --info: #1F436B;
}

html, body, [class*="css"], .stApp, .main, .block-container {
  font-family: 'JetBrains Mono', monospace !important;
  color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* Display fonts */
h1, h2, h3, h4, .display-serif {
  font-family: 'Fraunces', serif !important;
  letter-spacing: -0.01em;
  color: var(--text);
}

/* Brand mark in sidebar */
.brand-mark {
  font-family: 'Fraunces', serif;
  font-size: 26px;
  font-style: normal;
  font-weight: 400;
  letter-spacing: -0.02em;
  color: var(--text);
  line-height: 1.1;
  margin-bottom: 4px;
}
.brand-mark::first-letter { color: var(--accent); }

.brand-tag {
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--muted);
  margin-bottom: 20px;
}

/* Sidebar background */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] > div {
  padding-top: 16px;
}

/* Status pill */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-dim);
  margin-bottom: 16px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--bad);
}
.status-pill.live .status-dot {
  background: var(--accent);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* Section labels */
.section-label {
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--muted);
  margin: 18px 0 8px;
  font-weight: 500;
}

.task-group-label {
  font-family: 'Fraunces', serif;
  font-style: normal;
  font-size: 15px;
  color: var(--accent);
  margin: 16px 0 6px;
}

/* Streamlit button overrides */
.stButton > button {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 15px !important;
  border-radius: 0 !important;
  border: 1px solid var(--border) !important;
  background: var(--surface) !important;
  color: var(--text) !important;
  text-align: left !important;
  padding: 8px 12px !important;
  height: auto !important;
  transition: all 0.15s !important;
  font-weight: 400 !important;
}

.stButton > button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  background: var(--surface-2) !important;
}

/* Primary button (Run Audit) */
.stButton > button[kind="primary"] {
  background: var(--accent) !important;
  color: var(--bg) !important;
  border: none !important;
  padding: 12px !important;
  font-weight: 600 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  text-align: center !important;
}

.stButton > button[kind="primary"]:hover {
  background: var(--accent-light) !important;
}

/* Text inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 14px !important;
  border-radius: 0 !important;
  border-color: var(--border) !important;
  background: var(--surface) !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: none !important;
}

label {
  font-size: 14px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.15em !important;
  color: var(--muted) !important;
}

/* Expanders */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 15px !important;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-dim) !important;
  border-radius: 0 !important;
}

[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: 0 !important;
  background: transparent !important;
}

/* === MAIN PANEL CONTENT === */

/* Welcome state */
.welcome-card {
  text-align: center;
  padding: 80px 40px;
  max-width: 600px;
  margin: 60px auto;
}

.welcome-title {
  font-family: 'Fraunces', serif;
  font-style: normal;
  font-weight: 500;
  font-size: 48px;
  color: var(--text-dim);
  letter-spacing: -0.02em;
  margin-bottom: 16px;
}

.welcome-body {
  font-size: 15px;
  color: var(--muted);
  line-height: 1.7;
  margin-bottom: 32px;
}

.welcome-hint {
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--accent);
}

/* Result query header */
.query-display {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border);
}

.query-text {
  font-family: 'Fraunces', serif;
  font-style: normal;
  font-size: 36px;
  font-weight: 400;
  color: var(--text);
  letter-spacing: -0.01em;
  margin-bottom: 12px;
  line-height: 1.2;
}

.query-text::before { content: '"'; color: var(--accent); margin-right: 4px; }
.query-text::after { content: '"'; color: var(--accent); margin-left: 4px; }

.query-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
}

.query-meta strong { color: var(--text); font-weight: 500; }
.query-meta .accent { color: var(--accent); font-weight: 600; }

/* Saturation card */
.saturation-card {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 28px 32px;
  margin-bottom: 32px;
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 40px;
  align-items: center;
}

.saturation-number {
  font-family: 'Fraunces', serif;
  font-size: 80px;
  font-weight: 500;
  color: var(--accent);
  line-height: 0.95;
  letter-spacing: -0.04em;
}

.saturation-number span {
  color: var(--muted);
  font-size: 36px;
}

.saturation-label {
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--muted);
  margin-top: 12px;
}

.saturation-bar {
  display: flex;
  height: 8px;
  background: var(--border);
  margin-bottom: 20px;
  overflow: hidden;
}

.bar-owned { background: var(--accent); }
.bar-earned { background: var(--info); }
.bar-neutral { background: var(--border-bright); }
.bar-negative { background: var(--bad); }

.legend-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.legend-cell { display: flex; flex-direction: column; gap: 4px; }

.legend-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
}

.legend-dot { width: 8px; height: 8px; }
.legend-count {
  font-family: 'Fraunces', serif;
  font-size: 26px;
  color: var(--text);
  font-weight: 400;
  line-height: 1;
}

/* Knowledge graph card */
.kg-card {
  background: var(--surface);
  border-left: 3px solid var(--accent);
  padding: 20px 24px;
  margin-bottom: 32px;
  position: relative;
}
.kg-card::before {
  content: 'KNOWLEDGE GRAPH';
  position: absolute;
  top: 12px;
  right: 16px;
  font-size: 15px;
  letter-spacing: 0.22em;
  color: var(--accent);
}
.kg-title { font-family: 'Fraunces', serif; font-size: 24px; margin-bottom: 4px; }
.kg-type { font-size: 16px; text-transform: uppercase; letter-spacing: 0.15em; color: var(--muted); margin-bottom: 12px; }
.kg-desc { font-size: 16px; color: var(--text-dim); line-height: 1.6; }

.no-kg {
  background: var(--surface);
  border: 1px dashed var(--border-bright);
  padding: 14px 20px;
  margin-bottom: 32px;
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
}
.no-kg::before { content: '⚠ '; color: var(--warn); }

/* Section title */
.section-title {
  font-family: 'Fraunces', serif;
  font-style: normal;
  font-size: 22px;
  color: var(--text);
  margin: 32px 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.section-title small {
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  font-style: normal;
}

/* Result list item */
.result-row {
  display: grid;
  grid-template-columns: 36px 1fr 100px;
  gap: 18px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}

.result-pos {
  font-family: 'Fraunces', serif;
  font-size: 24px;
  color: var(--muted);
  font-weight: 500;
  line-height: 1;
}

.result-body { min-width: 0; }
.result-title {
  font-size: 15px;
  color: var(--text);
  margin-bottom: 4px;
  font-weight: 500;
}
.result-link {
  font-size: 15px;
  margin-bottom: 6px;
  word-break: break-all;
}
.result-link a {
  color: var(--info);
  text-decoration: none;
}
.result-link a:hover { color: var(--accent); }
.result-snippet {
  font-size: 15px;
  color: var(--muted);
  line-height: 1.6;
}

.tag {
  align-self: start;
  text-align: center;
  padding: 4px 10px;
  font-size: 15px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  border: 1px solid;
  white-space: nowrap;
  height: fit-content;
}
.tag.owned { color: var(--accent); border-color: var(--accent); background: rgba(31, 78, 61, 0.06); }
.tag.earned { color: var(--info); border-color: var(--info); background: rgba(45, 90, 140, 0.06); }
.tag.neutral { color: var(--muted); border-color: var(--border-bright); }
.tag.negative { color: var(--bad); border-color: var(--bad); background: rgba(168, 54, 42, 0.06); }

/* Related searches */
.related-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.pill {
  padding: 6px 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  font-size: 15px;
  color: var(--text-dim);
}

/* Block container width */
.main .block-container {
  padding-top: 2rem;
  padding-bottom: 4rem;
  max-width: 1200px;
}

/* Hide Streamlit deploy button etc */
[data-testid="stToolbar"] { display: none; }

/* High-contrast overrides for readability */
.stApp p, .stApp li, .stMarkdown p, .stMarkdown li { color: var(--text) !important; line-height: 1.6; }
.stCaption, [data-testid="stCaptionContainer"], .stMarkdown small { color: var(--text-dim) !important; font-size: 14px !important; }
.stMarkdown strong, .stMarkdown b { color: var(--text) !important; font-weight: 700 !important; }
/* Restore primary button white text (broad rules above must not touch buttons) */
.stButton > button[kind="primary"], .stButton > button[kind="primary"] * {
  color: var(--bg) !important;
}

/* Lock the sidebar permanently open — no collapse, no toggle */
section[data-testid="stSidebar"] {
  transform: translateX(0) !important;
  visibility: visible !important;
  min-width: 320px !important;
  width: 320px !important;
  max-width: 320px !important;
  margin-left: 0 !important;
}
section[data-testid="stSidebar"][aria-expanded="false"] {
  transform: translateX(0) !important;
  margin-left: 0 !important;
}

/* Hide every collapse / expand control across Streamlit versions */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseControl"],
[data-testid="stSidebarHeader"] button,
section[data-testid="stSidebar"] button[kind="header"],
section[data-testid="stSidebar"] [data-testid="baseButton-headerNoPadding"],
section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"] {
  display: none !important;
}

/* ===== Step structure ===== */
.step-block { margin: 56px 0 8px; padding-top: 32px; border-top: 2px solid var(--border); }
.step-block.first { border-top: none; padding-top: 8px; margin-top: 16px; }
.step-header { display: flex; align-items: baseline; gap: 18px; margin-bottom: 4px; }
.step-num {
  font-family: 'Fraunces', serif;
  font-size: 60px;
  font-weight: 500;
  color: var(--accent);
  line-height: 1;
  letter-spacing: -0.04em;
}
.step-title {
  font-family: 'Fraunces', serif;
  font-style: normal;
  font-size: 38px;
  font-weight: 400;
  color: var(--text);
  letter-spacing: -0.01em;
}
.step-subtitle {
  font-size: 16px;
  color: var(--muted);
  margin: 4px 0 24px 78px;
  line-height: 1.5;
}

/* Category subsection within Step 3 */
.category-header {
  margin: 36px 0 4px;
  padding: 16px 0 0;
  border-top: 1px dashed var(--border);
}
.category-header:first-of-type { border-top: none; padding-top: 8px; }
.category-title {
  font-family: 'Fraunces', serif;
  font-style: normal;
  font-size: 24px;
  color: var(--text);
  margin-bottom: 2px;
}
.category-subtitle {
  font-size: 15px;
  color: var(--muted);
  margin-bottom: 18px;
  line-height: 1.5;
}

.task-topic {
  font-style: normal;
  color: var(--accent);
  font-size: 16px;
  margin: 6px 0;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
CONFIG_FILE = Path("config.json")
SNAPSHOTS_FILE = Path("snapshots.json")
TASKS_FILE = Path("tasks.json")

DEFAULT_OWNED = [
    "bruiaka.com",
    "andrewbruiaka.substack.com",
    "andrewbruiaka",
    "andriibruiaka",
    "andrii-bruiaka",
    "onicore.io",
    "nonbank.io",
]

DEFAULT_EARNED = [
    "finextra.com",
    "thefintechtimes.com",
    "sifted.eu",
    "bankingdive.com",
    "fintechfilter.com",
    "hackernoon.com",
    "medium.com",
    "dev.to",
    "substack.com",
    "coindesk.com",
    "cointelegraph.com",
    "decrypt.co",
    "theblock.co",
    "crunchbase.com",
    "producthunt.com",
    "f6s.com",
    "clarity.fm",
    "stackoverflow.com",
    "hashnode.com",
    "allmylinks.com",
    "coinmarketcap.com",
    "d-themes.com",
    "linkedin.com",
]

TASKS = [
    # Core Identity
    {"id": "core_g", "group": "Core Identity", "label": "andrii bruiaka", "engine": "google", "query": "andrii bruiaka"},
    {"id": "core_b", "group": "Core Identity", "label": "andrii bruiaka", "engine": "bing", "query": "andrii bruiaka"},
    {"id": "core_alt", "group": "Core Identity", "label": "andrew bruiaka", "engine": "google", "query": "andrew bruiaka"},
    {"id": "core_quoted", "group": "Core Identity", "label": '"andrii bruiaka"', "engine": "google", "query": '"andrii bruiaka"'},
    # Brand Surface
    {"id": "brand_dom", "group": "Brand Surface", "label": "bruiaka.com", "engine": "google", "query": "bruiaka.com"},
    {"id": "brand_sub", "group": "Brand Surface", "label": "andrii bruiaka substack", "engine": "google", "query": "andrii bruiaka substack"},
    {"id": "brand_li", "group": "Brand Surface", "label": "andrii bruiaka linkedin", "engine": "google", "query": "andrii bruiaka linkedin"},
    # Companies
    {"id": "co_oni", "group": "Companies", "label": "onicore", "engine": "google", "query": "onicore fintech"},
    {"id": "co_nb", "group": "Companies", "label": "nonbank.io", "engine": "google", "query": "nonbank.io"},
    {"id": "co_kolo", "group": "Companies", "label": "kolo wallet", "engine": "google", "query": "kolo crypto wallet"},
    # Topic Authority
    {"id": "tp_fin", "group": "Topic Authority", "label": "andrii bruiaka fintech", "engine": "google", "query": "andrii bruiaka fintech"},
    {"id": "tp_crypto", "group": "Topic Authority", "label": "andrii bruiaka crypto UX", "engine": "google", "query": "andrii bruiaka crypto UX"},
    {"id": "tp_pk", "group": "Topic Authority", "label": "andrii bruiaka passkey", "engine": "google", "query": "andrii bruiaka passkey"},
    {"id": "tp_emb", "group": "Topic Authority", "label": "andrii bruiaka embedded finance", "engine": "google", "query": "andrii bruiaka embedded finance"},
]

# ============================================================
# PERSISTENCE
# ============================================================
def load_config():
    """Load config from disk, with secrets fallback for cloud deploys."""
    config = {
        "api_key": "",
        "perplexity_key": "",
        "owned_domains": DEFAULT_OWNED.copy(),
        "earned_domains": DEFAULT_EARNED.copy(),
        "negatives": [],
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                stored = json.load(f)
                config.update(stored)
        except Exception:
            pass
    # Cloud secret takes precedence if set
    try:
        if not config["api_key"] and "serpapi_key" in st.secrets:
            config["api_key"] = st.secrets["serpapi_key"]
    except Exception:
        pass
    try:
        if not config["perplexity_key"] and "perplexity_key" in st.secrets:
            config["perplexity_key"] = st.secrets["perplexity_key"]
    except Exception:
        pass
    return config


def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        st.error(f"Could not save config: {e}")


def load_snapshots():
    if SNAPSHOTS_FILE.exists():
        try:
            with open(SNAPSHOTS_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def load_tasks():
    if TASKS_FILE.exists():
        try:
            return json.loads(TASKS_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_tasks(tasks):
    try:
        TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    except Exception:
        pass


def save_snapshot(task_id, data):
    snapshots = load_snapshots()
    if task_id not in snapshots:
        snapshots[task_id] = []
    snapshots[task_id].insert(
        0,
        {
            "timestamp": datetime.now().isoformat(),
            "organic_count": len(data.get("organic_results") or []),
            "has_kg": bool(data.get("knowledge_graph")),
        },
    )
    snapshots[task_id] = snapshots[task_id][:10]
    try:
        with open(SNAPSHOTS_FILE, "w") as f:
            json.dump(snapshots, f, indent=2)
    except Exception:
        pass


# ============================================================
# SERPAPI
# ============================================================
def call_serpapi(query, engine, api_key, timeout=30, start=0):
    params = {"q": query, "engine": engine, "api_key": api_key, "num": 10, "start": start}
    if engine == "google":
        params["gl"] = "us"
        params["hl"] = "en"
    resp = requests.get("https://serpapi.com/search.json", params=params, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def call_serpapi_multipage(query, engine, api_key, pages=3, timeout=30):
    """Fetch N pages of SERP results and merge organic_results."""
    merged = None
    all_organic = []
    for page in range(pages):
        data = call_serpapi(query, engine, api_key, timeout=timeout, start=page * 10)
        organic = data.get("organic_results") or []
        all_organic.extend(organic)
        if merged is None:
            merged = data
        if not organic:
            break
    if merged is None:
        return {}
    merged["organic_results"] = all_organic
    return merged


# ============================================================
# PERPLEXITY (LLM visibility probe)
# ============================================================
PERPLEXITY_PROBE = "Who is Andrii Bruiaka? What does he do, what companies has he founded, and where can I read his work?"


def call_perplexity(query, api_key, timeout=45):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": query}],
    }
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        json=payload,
        headers=headers,
        timeout=timeout,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.json()


def parse_perplexity(data):
    """Extract answer + citations from Perplexity response."""
    msg = (data.get("choices") or [{}])[0].get("message") or {}
    answer = msg.get("content", "")
    citations = data.get("citations") or data.get("search_results") or []
    citation_urls = []
    for c in citations:
        if isinstance(c, str):
            citation_urls.append(c)
        elif isinstance(c, dict):
            citation_urls.append(c.get("url") or c.get("link") or "")
    citation_urls = [u for u in citation_urls if u]
    return answer, citation_urls


# ============================================================
# CLASSIFICATION
# ============================================================
def result_key(result):
    return ((result.get("link") or "").lower()) + "|" + (result.get("title") or "")


def classify(result, config):
    url = (result.get("link") or "").lower()
    if result_key(result) in (config.get("negatives") or []):
        return "negative"
    for d in config["owned_domains"]:
        if d and d.lower() in url:
            return "owned"
    for d in config["earned_domains"]:
        if d and d.lower() in url:
            return "earned"
    return "neutral"


# ============================================================
# ACTION PLAN — categorized tasks
# ============================================================
ACTION_CATEGORIES = [
    {
        "id": "press",
        "title": "Articles & press placements",
        "subtitle": "Each one is a page-1 SERP slot owned by a high-trust outlet, plus citation fodder for LLMs. Pitch concrete angles, not bios.",
        "tasks": [
            {
                "label": "Finextra — bylined column or founder profile",
                "priority": 1,
                "topic": "\"How small fintechs rebuild infrastructure without 50-person engineering teams\" — drawn from Onicore",
                "why": "Tier-1 fintech outlet. Always ranks page-1 for founder names.",
                "action": "Email pitch to editor@finextra.com (or LinkedIn-DM the relevant editor). 200 words, 3 angle options, 1 concrete data point from Onicore.",
                "domains": ["finextra.com"],
            },
            {
                "label": "Sifted — founder profile",
                "priority": 1,
                "topic": "\"Eastern-European founders quietly rebuilding the EU fintech stack\" (you as one of 3-4)",
                "why": "Read by EU VCs and journalists. Profile pieces rank for the name.",
                "action": "Pitch news desk via tips@sifted.eu. Reference recent Sifted coverage to show fit.",
                "domains": ["sifted.eu"],
            },
            {
                "label": "The Fintech Times — guest contributor",
                "priority": 1,
                "topic": "\"Embedded finance is dead — long live infrastructure-as-a-service\" POV piece",
                "why": "Easier to land than Finextra/Sifted, ranks well for founder name.",
                "action": "Submit at thefintechtimes.com/contribute or email editor@thefintechtimes.com. They take strong opinion pieces.",
                "domains": ["thefintechtimes.com"],
            },
            {
                "label": "Banking Dive — interview or quote",
                "priority": 2,
                "topic": "Compliance / fraud prevention angle — quoteable on operational fintech infrastructure",
                "why": "Tier-1 in US banking media. Quotes ride the name in search.",
                "action": "Pitch yourself as a source on Help a B2B Writer / Featured. Or DM Banking Dive reporters on LinkedIn.",
                "domains": ["bankingdive.com"],
            },
            {
                "label": "Coindesk or Decrypt — bylined",
                "priority": 2,
                "topic": "\"Why crypto UX still fails: passkeys, recovery, and the seed-phrase problem\" — drawn from Kolo wallet work",
                "why": "Crypto-native outlets index quickly and feed LLMs. Builds the crypto-UX angle of the brand.",
                "action": "Pitch contribute@coindesk.com or contributors@decrypt.co with full draft + author bio.",
                "domains": ["coindesk.com", "decrypt.co"],
            },
            {
                "label": "HackerNoon — contributor profile + 2 articles",
                "priority": 3,
                "topic": "Technical post-mortems of building Onicore / Kolo. Long-form, code-light.",
                "why": "Lowest bar of all tier-2 outlets. Author page itself ranks for the name.",
                "action": "Sign up at hackernoon.com/contribute. Publish 2 pieces back-to-back so author page has weight.",
                "domains": ["hackernoon.com"],
            },
            {
                "label": "Podcast — Fintech Insider (11:FS)",
                "priority": 1,
                "topic": "\"Building fintech infrastructure outside the big-bank stack\"",
                "why": "Industry-defining podcast. Episode show notes rank page-1 for guest names.",
                "action": "Pitch via 11fs.com/podcast/contact. Reference 2 recent episodes you'd extend on.",
                "domains": ["11fs.com"],
            },
            {
                "label": "Podcast — This Week in Fintech",
                "priority": 2,
                "topic": "Founder spotlight or panel on embedded finance",
                "why": "Weekly cadence + active newsletter audience.",
                "action": "Email nik@thisweekinfintech.com with a 1-paragraph pitch.",
                "domains": ["thisweekinfintech.com"],
            },
            {
                "label": "TechCrunch / Forbes coverage",
                "priority": 1,
                "topic": "Onicore funding announcement, partnership, or product launch (news hook required)",
                "why": "Single biggest entity-recognition trigger for Google. Once you have one, KG often follows.",
                "action": "Don't pitch a profile cold — wait for a news hook (raise, partnership, customer milestone), then pitch via warm intro.",
                "domains": ["techcrunch.com", "forbes.com"],
            },
        ],
    },
    {
        "id": "profiles",
        "title": "Profile sites — claim or register",
        "subtitle": "Each profile = a SERP slot you control with your own copy. Most rank for the name within days. Free.",
        "tasks": [
            {
                "label": "Wikidata entry",
                "priority": 1,
                "why": "Lower bar than Wikipedia. Feeds Google Knowledge Graph + read as authoritative by ChatGPT/Perplexity/Claude.",
                "action": "Create at wikidata.org/wiki/Special:NewItem. Need ≥2 third-party reliable sources to cite (use any tier-1 press once landed).",
                "domains": ["wikidata.org"],
            },
            {
                "label": "Crunchbase person page",
                "priority": 1,
                "why": "Always ranks for founder names. Drives entity recognition. Links to founded companies.",
                "action": "Sign up at crunchbase.com → create person → link Onicore, Nonbank.io, Kolo. Add headshot + bio + LinkedIn.",
                "domains": ["crunchbase.com"],
            },
            {
                "label": "AngelList / Wellfound founder profile",
                "priority": 2,
                "why": "Founder-focused, ranks well for the name + 'founder' qualifier.",
                "action": "Sign up at wellfound.com → mark as founder → link companies.",
                "domains": ["wellfound.com", "angel.co"],
            },
            {
                "label": "F6S profile",
                "priority": 2,
                "why": "Startup-ecosystem directory, indexes fast.",
                "action": "Create at f6s.com → list all ventures + investments + advisor roles.",
                "domains": ["f6s.com"],
            },
            {
                "label": "GitHub profile",
                "priority": 2,
                "why": "Easy 10-min win. Ranks for technical founder names. Read by LLMs.",
                "action": "github.com/andriibruiaka — bio, link to bruiaka.com, pin 3 repos (even if just docs/specs).",
                "domains": ["github.com"],
            },
            {
                "label": "Speakerhub profile",
                "priority": 2,
                "why": "Pulls inbound podcast and conference invitations — feeds the press category.",
                "action": "Sign up at speakerhub.com → list 3 talk topics matching the brand pillars (fintech infra, embedded finance, crypto UX).",
                "domains": ["speakerhub.com"],
            },
            {
                "label": "Hashnode author profile",
                "priority": 3,
                "why": "Indexes fast, ranks well for technical author names.",
                "action": "hashnode.com → claim @andriibruiaka or similar. Cross-post 1 article.",
                "domains": ["hashnode.com"],
            },
            {
                "label": "Dev.to author profile",
                "priority": 3,
                "why": "Same as Hashnode — author page ranks.",
                "action": "dev.to/andriibruiaka. Cross-post the same article (with canonical link to Substack).",
                "domains": ["dev.to"],
            },
            {
                "label": "Medium author profile",
                "priority": 3,
                "why": "medium.com/@<name> ranks page-1 for many founder names.",
                "action": "Set vanity URL to @andriibruiaka. Cross-post 1 cornerstone article.",
                "domains": ["medium.com"],
            },
            {
                "label": "AllMyLinks profile",
                "priority": 3,
                "why": "Aggregator that ranks for the name. Acts as a meta-bio when nothing else exists.",
                "action": "allmylinks.com/andriibruiaka — link every other profile here. 5-min setup.",
                "domains": ["allmylinks.com"],
            },
            {
                "label": "X / Twitter — verified handle, complete bio",
                "priority": 2,
                "why": "Profile cards appear in some Google name searches and feed Grok/ChatGPT.",
                "action": "Confirm @ matches the brand. Bio with link to bruiaka.com. Verified ($8/mo) helps for entity recognition.",
                "domains": ["twitter.com", "x.com"],
            },
            {
                "label": "Reddit — earn karma, one organic mention",
                "priority": 3,
                "why": "LLMs (especially ChatGPT) rely heavily on Reddit. One thread can move AI answers.",
                "action": "Build account karma by commenting in r/fintech, r/startups for 4 weeks. Then post a Show & Tell or AMA tied to a launch.",
                "domains": ["reddit.com"],
            },
        ],
    },
    {
        "id": "owned",
        "title": "Owned web properties",
        "subtitle": "Sites you fully control. Add Person schema markup for entity recognition; cross-link aggressively.",
        "tasks": [
            {
                "label": "bruiaka.com — Person schema.org markup",
                "priority": 1,
                "why": "Tells Google explicitly 'this site is the person Andrii Bruiaka.' Single biggest on-page Knowledge Graph signal.",
                "action": "Add JSON-LD Person schema to homepage with name, jobTitle, worksFor (Onicore), sameAs (LinkedIn, Substack, Crunchbase, Wikidata once live).",
                "domains": [],
            },
            {
                "label": "andriibruiaka.com — confirm ownership + add to owned list",
                "priority": 1,
                "why": "Perplexity already cites it. Make sure it's officially owned and matches brand.",
                "action": "Add 'andriibruiaka.com' to Settings → Owned Domains in this dashboard. Add Person schema mirroring bruiaka.com.",
                "domains": ["andriibruiaka.com"],
            },
            {
                "label": "Cornerstone Substack post: \"Andrii Bruiaka — what I work on\"",
                "priority": 1,
                "topic": "Bio-style post with name in title, URL slug, and H1. Links to bruiaka.com and all owned profiles.",
                "why": "Substack ranks fast and acts as a canonical bio answering 'who is...' queries.",
                "action": "Title: \"Andrii Bruiaka: building fintech infrastructure\". URL slug: /p/andrii-bruiaka. Internal-link to all profile URLs.",
                "domains": ["substack.com"],
            },
            {
                "label": "Substack — author/about page with structured data",
                "priority": 2,
                "why": "About page is what LLMs hit for bio queries. Make it crawlable and entity-tagged.",
                "action": "Substack 'About' → name in H1, professional bio (3 paragraphs), links to all founded companies + profiles.",
                "domains": ["substack.com"],
            },
            {
                "label": "Onicore.io — founder bio page linking back",
                "priority": 2,
                "why": "Reciprocal linking from company → founder strengthens the entity graph.",
                "action": "/about page: dedicated bio block with name as H2, photo, link to bruiaka.com and LinkedIn.",
                "domains": ["onicore.io", "onicore.ie"],
            },
            {
                "label": "Nonbank.io — founder bio page linking back",
                "priority": 2,
                "why": "Same as Onicore — reciprocal entity signal.",
                "action": "/about or /team — name as H2, link out to bruiaka.com.",
                "domains": ["nonbank.io"],
            },
        ],
    },
    {
        "id": "content",
        "title": "Content cadence",
        "subtitle": "Recurring rhythm. Treat each as a standing task — re-mark 'done' monthly.",
        "tasks": [
            {
                "label": "Monthly Substack post (cornerstone)",
                "priority": 1,
                "topic": "Pillars: fintech infrastructure · embedded finance · crypto UX · passkeys / auth",
                "why": "1 post/month at 1500+ words is the bare minimum for Substack ranking.",
                "action": "Calendar 4 topics ahead. Each post: name in author + 1 mention in body + link to /about.",
                "domains": ["substack.com"],
            },
            {
                "label": "Monthly Medium cross-post",
                "priority": 2,
                "why": "Reach + author-page weight. Cross-post with canonical link back to Substack.",
                "action": "After each Substack post, cross-post on Medium with rel=canonical to original.",
                "domains": ["medium.com"],
            },
            {
                "label": "Bi-weekly LinkedIn long-form",
                "priority": 2,
                "why": "LinkedIn long-form posts surface in Google for the name.",
                "action": "1 long-form (1000+ words) every 2 weeks. Reuse Substack content trimmed.",
                "domains": ["linkedin.com"],
            },
            {
                "label": "Monthly podcast pitch (1 outbound)",
                "priority": 1,
                "why": "Forces a steady press cadence. Even 1 in 5 lands = 2-3 episodes/year, which moves both SERP and KG.",
                "action": "Pick a podcast from the press category each month. Send pitch by 5th of month.",
                "domains": [],
            },
            {
                "label": "Monthly tier-1 outlet pitch",
                "priority": 1,
                "why": "Same logic as podcast: keep the funnel alive.",
                "action": "Rotate Finextra → Sifted → Fintech Times → Banking Dive. One pitch every 4 weeks.",
                "domains": [],
            },
            {
                "label": "Quarterly Wikidata refresh",
                "priority": 3,
                "why": "Every new tier-1 press piece = a new sitelink to add as evidence.",
                "action": "Once per quarter, add new press citations to the Wikidata entity. Keep statements current.",
                "domains": ["wikidata.org"],
            },
        ],
    },
]


def auto_check_task(task, urls_blob, citations_blob):
    """A task auto-marks 'done' if any of its check domains appears in SERP or Perplexity citations."""
    domains = task.get("domains") or []
    if not domains:
        return False
    haystack = urls_blob + " " + citations_blob
    return any(d.lower() in haystack for d in domains if d)


# ============================================================
# SESSION STATE
# ============================================================
if "config" not in st.session_state:
    st.session_state.config = load_config()
if "results" not in st.session_state:
    st.session_state.results = {}
if "task_status" not in st.session_state:
    st.session_state.task_status = {}
if "active_task_id" not in st.session_state:
    st.session_state.active_task_id = None
if "custom_tasks" not in st.session_state:
    st.session_state.custom_tasks = []
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Strategy"
if "perplexity_result" not in st.session_state:
    st.session_state.perplexity_result = None
if "perplexity_status" not in st.session_state:
    st.session_state.perplexity_status = "idle"

all_tasks = TASKS + st.session_state.custom_tasks


def get_task(task_id):
    for t in all_tasks:
        if t["id"] == task_id:
            return t
    return None


def run_perplexity():
    key = st.session_state.config.get("perplexity_key")
    if not key:
        st.session_state.perplexity_status = "error"
        st.session_state.perplexity_result = {"error": "No Perplexity key configured"}
        return
    try:
        st.session_state.perplexity_status = "running"
        data = call_perplexity(PERPLEXITY_PROBE, key)
        st.session_state.perplexity_result = data
        st.session_state.perplexity_status = "ok"
    except Exception as e:
        st.session_state.perplexity_status = "error"
        st.session_state.perplexity_result = {"error": str(e)}


def run_single(task):
    """Synchronously call SerpAPI and store results."""
    try:
        st.session_state.task_status[task["id"]] = "running"
        data = call_serpapi(task["query"], task["engine"], st.session_state.config["api_key"])
        st.session_state.results[task["id"]] = data
        st.session_state.task_status[task["id"]] = "ok"
        save_snapshot(task["id"], data)
        return True, None
    except Exception as e:
        st.session_state.task_status[task["id"]] = "error"
        st.session_state.results[task["id"]] = {"error": str(e)}
        return False, str(e)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="brand-mark">Visibility Monitor</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-tag">SERP / GEO Audit · A. Bruiaka</div>', unsafe_allow_html=True)

    has_key = bool(st.session_state.config.get("api_key"))
    pill_class = "live" if has_key else ""
    pill_text = "API Connected" if has_key else "No API Key"
    st.markdown(
        f'<div class="status-pill {pill_class}"><span class="status-dot"></span>{pill_text}</div>',
        unsafe_allow_html=True,
    )

    st.session_state.view_mode = st.radio(
        "View",
        ["Strategy", "Raw queries"],
        index=0 if st.session_state.view_mode == "Strategy" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )

    # Settings expander
    with st.expander("⚙ Settings", expanded=not has_key):
        api_input = st.text_input(
            "SerpAPI Key",
            value=st.session_state.config.get("api_key", ""),
            type="password",
            help="Get one at serpapi.com/dashboard. Free tier = 100 searches/month.",
        )
        pplx_input = st.text_input(
            "Perplexity Key (optional)",
            value=st.session_state.config.get("perplexity_key", ""),
            type="password",
            help="Get one at perplexity.ai/settings/api. Used for the LLM visibility check.",
        )
        owned_input = st.text_area(
            "Owned Domains (one per line)",
            value="\n".join(st.session_state.config["owned_domains"]),
            height=140,
            help="Substring match — 'linkedin.com/in/andrii' = that profile only",
        )
        earned_input = st.text_area(
            "Earned Media Domains (one per line)",
            value="\n".join(st.session_state.config["earned_domains"]),
            height=140,
            help="Target outlets you've published on or want to",
        )
        if st.button("Save Settings", use_container_width=True):
            st.session_state.config["api_key"] = api_input.strip()
            st.session_state.config["perplexity_key"] = pplx_input.strip()
            st.session_state.config["owned_domains"] = [
                l.strip() for l in owned_input.split("\n") if l.strip()
            ]
            st.session_state.config["earned_domains"] = [
                l.strip() for l in earned_input.split("\n") if l.strip()
            ]
            save_config(st.session_state.config)
            st.success("Saved")
            time.sleep(0.5)
            st.rerun()

    st.markdown('<div class="section-label">Audit Battery</div>', unsafe_allow_html=True)

    # Run all
    if st.button(
        "▶ RUN FULL AUDIT",
        use_container_width=True,
        disabled=not has_key,
        type="primary",
    ):
        progress_bar = st.progress(0)
        status_text = st.empty()
        for i, task in enumerate(TASKS):
            status_text.markdown(f'<div style="font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:0.1em">Running: {task["label"]}</div>', unsafe_allow_html=True)
            run_single(task)
            progress_bar.progress((i + 1) / len(TASKS))
            time.sleep(0.25)
        status_text.empty()
        progress_bar.empty()
        st.success("Audit complete")
        time.sleep(0.5)
        st.rerun()

    # Custom query
    with st.expander("+ Custom Query"):
        custom_q = st.text_input("Query", key="custom_q_input")
        custom_engine = st.selectbox("Engine", ["google", "bing", "duckduckgo"], key="custom_eng_input")
        if st.button("Run", key="run_custom", disabled=not has_key, use_container_width=True):
            if custom_q.strip():
                cid = f"custom_{len(st.session_state.custom_tasks) + 1}_{int(time.time())}"
                ctask = {
                    "id": cid,
                    "group": "Custom",
                    "label": custom_q.strip()[:40],
                    "engine": custom_engine,
                    "query": custom_q.strip(),
                }
                st.session_state.custom_tasks.append(ctask)
                st.session_state.active_task_id = cid
                run_single(ctask)
                st.rerun()

    # Task list
    groups = {}
    for t in all_tasks:
        groups.setdefault(t["group"], []).append(t)

    status_icons = {"idle": "○", "running": "◐", "ok": "●", "error": "✕"}

    for group_name, tasks in groups.items():
        st.markdown(f'<div class="task-group-label">{group_name}</div>', unsafe_allow_html=True)
        for task in tasks:
            status = st.session_state.task_status.get(task["id"], "idle")
            icon = status_icons[status]

            # Compute saturation if we have a result
            sat_label = ""
            if task["id"] in st.session_state.results:
                result = st.session_state.results[task["id"]]
                if "error" not in result:
                    organic = (result.get("organic_results") or [])[:20]
                    aligned = sum(
                        1 for r in organic if classify(r, st.session_state.config) in ("owned", "earned")
                    )
                    sat_label = f"  {aligned}/{len(organic)}"

            label_text = f"{icon}  {task['label'][:28]}{sat_label}"
            if st.button(label_text, key=f"task_{task['id']}", use_container_width=True):
                st.session_state.active_task_id = task["id"]
                if task["id"] not in st.session_state.results and has_key:
                    run_single(task)
                st.rerun()


# ============================================================
# MAIN PANEL
# ============================================================
def render_strategy():
    has_serp = bool(st.session_state.config.get("api_key"))
    has_pplx = bool(st.session_state.config.get("perplexity_key"))
    primary_task = next((t for t in TASKS if t["id"] == "core_g"), None)

    # Header
    st.markdown(
        """
        <div class="query-display">
          <div class="query-text">andrii bruiaka</div>
          <div class="query-meta">
            <span>Goal · <strong>OWN PAGE 1 WITH POSITIVE CONTENT</strong></span>
            <span>Engine · <strong>GOOGLE + LLMs</strong></span>
            <span class="accent">3 steps · measure · then act</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not has_serp:
        st.warning("Add SerpAPI key in Settings to begin.")
        return

    serp_result = st.session_state.results.get(primary_task["id"]) if primary_task else None
    pplx_result = st.session_state.perplexity_result

    # ============================================================
    # STEP 1 — Google
    # ============================================================
    st.markdown(
        '<div class="step-block first">'
        '<div class="step-header"><div class="step-num">01</div><div class="step-title">Google search</div></div>'
        '<div class="step-subtitle">What do pages 1-3 (top 30) look like for "andrii bruiaka"? Each row is a SERP slot you either own, earn, or need to displace. Page 1 is what almost everyone sees; pages 2-3 are still in reach for someone digging.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("▶ Refresh Google name search (3 pages, top 30)", use_container_width=True, type="primary"):
        try:
            st.session_state.task_status[primary_task["id"]] = "running"
            data = call_serpapi_multipage(
                primary_task["query"],
                primary_task["engine"],
                st.session_state.config["api_key"],
                pages=3,
            )
            st.session_state.results[primary_task["id"]] = data
            st.session_state.task_status[primary_task["id"]] = "ok"
            save_snapshot(primary_task["id"], data)
        except Exception as e:
            st.session_state.task_status[primary_task["id"]] = "error"
            st.session_state.results[primary_task["id"]] = {"error": str(e)}
        st.rerun()

    if not serp_result:
        st.info("Click 'Refresh Google name search' above to load page 1-3 data (top 30).")
        return
    if "error" in serp_result:
        st.error(serp_result["error"])
        return

    organic = (serp_result.get("organic_results") or [])[:30]
    counts = {"owned": 0, "earned": 0, "neutral": 0, "negative": 0}
    for r in organic:
        counts[classify(r, st.session_state.config)] += 1
    aligned = counts["owned"] + counts["earned"]
    total = len(organic) or 1
    kg_present = bool(serp_result.get("knowledge_graph"))

    # Page 1 specifically (first 10) — that's what most users see
    page1 = organic[:10]
    page1_counts = {"owned": 0, "earned": 0, "neutral": 0, "negative": 0}
    for r in page1:
        page1_counts[classify(r, st.session_state.config)] += 1
    page1_aligned = page1_counts["owned"] + page1_counts["earned"]
    page1_total = len(page1) or 1

    google_status = (
        ("strong", "var(--good)") if page1_aligned >= 7
        else ("moderate", "var(--warn)") if page1_aligned >= 4
        else ("weak", "var(--bad)")
    )
    kg_status = ("present", "var(--good)") if kg_present else ("missing", "var(--bad)")

    st.markdown(
        f"""
        <div class="saturation-card" style="grid-template-columns: 1fr 1fr 1fr; gap: 24px;">
          <div>
            <div class="saturation-label">Page 1 saturation</div>
            <div class="saturation-number" style="color: {google_status[1]};">{page1_aligned}<span>/{page1_total}</span></div>
            <div class="saturation-label" style="color: {google_status[1]};">{google_status[0]} — {page1_counts['owned']} owned · {page1_counts['earned']} earned</div>
          </div>
          <div>
            <div class="saturation-label">Top 30 (3 pages)</div>
            <div class="saturation-number" style="color: var(--accent);">{aligned}<span>/{total}</span></div>
            <div class="saturation-label">{counts['owned']} owned · {counts['earned']} earned · {counts['neutral']} neutral · {counts['negative']} negative</div>
          </div>
          <div>
            <div class="saturation-label">Knowledge Graph (entity card)</div>
            <div class="saturation-number" style="font-size: 42px; color: {kg_status[1]};">{kg_status[0]}</div>
            <div class="saturation-label">Biggest signal Google built an entity</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(f"All results · {len(organic)} ranked across 3 pages", expanded=True):
        for i, r in enumerate(organic):
            cls = classify(r, st.session_state.config)
            title = escape_html(r.get("title") or "Untitled")
            link = r.get("link") or ""
            displayed = escape_html(r.get("displayed_link") or link)
            snippet = escape_html((r.get("snippet") or "")[:160])
            st.markdown(
                f"""
                <div class="result-row">
                  <div class="result-pos">{i+1:02d}</div>
                  <div class="result-body">
                    <div class="result-title">{title}</div>
                    <div class="result-link"><a href="{escape_html(link)}" target="_blank" rel="noopener">{displayed}</a></div>
                    {f'<div class="result-snippet">{snippet}</div>' if snippet else ''}
                  </div>
                  <div class="tag {cls}">{cls}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ============================================================
    # STEP 2 — LLM
    # ============================================================
    st.markdown(
        '<div class="step-block">'
        '<div class="step-header"><div class="step-num">02</div><div class="step-title">LLM visibility</div></div>'
        '<div class="step-subtitle">Does the AI search layer know who this is? What does it say, and which sources does it cite?</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if has_pplx:
        if st.button("▶ Refresh Perplexity probe", use_container_width=True):
            run_perplexity()
            st.rerun()
    else:
        st.caption("Add Perplexity key in Settings (or Streamlit Secrets) to enable LLM probe.")

    pplx_mentioned = False
    pplx_owned_cited = 0
    pplx_answer = ""
    pplx_citations = []
    if pplx_result and "error" not in pplx_result:
        pplx_answer, pplx_citations = parse_perplexity(pplx_result)
        pplx_mentioned = "bruiaka" in pplx_answer.lower()
        owned = st.session_state.config.get("owned_domains", [])
        for url in pplx_citations:
            ul = url.lower()
            if any(d.lower() in ul for d in owned if d):
                pplx_owned_cited += 1

    if pplx_result is None:
        pplx_status = ("not run", "var(--muted)")
    elif "error" in (pplx_result or {}):
        pplx_status = ("error", "var(--bad)")
    elif pplx_mentioned:
        pplx_status = (
            f"mentioned · {pplx_owned_cited} owned cited",
            "var(--good)" if pplx_owned_cited else "var(--warn)",
        )
    else:
        pplx_status = ("not mentioned", "var(--bad)")

    st.markdown(
        f"""
        <div class="saturation-card" style="grid-template-columns: 1fr 1fr; gap: 32px;">
          <div>
            <div class="saturation-label">Perplexity (sonar)</div>
            <div class="saturation-number" style="font-size: 36px; color: {pplx_status[1]};">{pplx_status[0]}</div>
            <div class="saturation-label">probe: "Who is Andrii Bruiaka?"</div>
          </div>
          <div>
            <div class="saturation-label">ChatGPT · Claude · Gemini</div>
            <div class="saturation-number" style="font-size: 28px; color: var(--muted);">not yet wired</div>
            <div class="saturation-label">add OpenAI / Anthropic / Google keys to extend</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if pplx_result and "error" not in pplx_result:
        with st.expander(f"What Perplexity says · {len(pplx_citations)} citations", expanded=True):
            st.markdown(
                f'<div class="kg-card"><div class="kg-desc">{escape_html(pplx_answer)}</div></div>',
                unsafe_allow_html=True,
            )
            if pplx_citations:
                st.markdown("**Citations**")
                for i, url in enumerate(pplx_citations, 1):
                    is_owned = any(
                        d.lower() in url.lower()
                        for d in st.session_state.config.get("owned_domains", [])
                        if d
                    )
                    tag = " · **OWNED**" if is_owned else ""
                    st.markdown(f"{i}. [{url}]({url}){tag}")
    elif pplx_result and "error" in pplx_result:
        st.error(f"Perplexity: {pplx_result['error']}")

    # ============================================================
    # STEP 3 — Action plan
    # ============================================================
    st.markdown(
        '<div class="step-block">'
        '<div class="step-header"><div class="step-num">03</div><div class="step-title">Action plan</div></div>'
        '<div class="step-subtitle">Concrete tasks grouped by category. Mark status, paste the proof URL when each is published. Auto-detection flags items already showing on page 1 or in Perplexity citations.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    serp_urls = " ".join((r.get("link") or "").lower() for r in organic)
    citation_urls = " ".join((c or "").lower() for c in pplx_citations)

    tasks_state = load_tasks()
    status_options = ["todo", "in progress", "done"]
    priority_label = {1: "P1", 2: "P2", 3: "P3"}
    priority_color = {1: "var(--bad)", 2: "var(--warn)", 3: "var(--muted)"}
    status_order = {"todo": 0, "in progress": 1, "done": 2}

    total_counts = {"todo": 0, "in progress": 0, "done": 0}
    changed = False

    for category in ACTION_CATEGORIES:
        st.markdown(
            f"""
            <div class="category-header">
              <div class="category-title">{escape_html(category['title'])}</div>
              <div class="category-subtitle">{escape_html(category['subtitle'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        items = []
        for t in category["tasks"]:
            label = t["label"]
            saved = tasks_state.get(label, {})
            auto_done = auto_check_task(t, serp_urls, citation_urls)
            default_status = "done" if auto_done else "todo"
            items.append({
                **t,
                "status": saved.get("status", default_status),
                "url": saved.get("url", ""),
                "notes": saved.get("notes", ""),
                "auto_present": auto_done,
            })

        items.sort(key=lambda i: (status_order[i["status"]], i["priority"]))

        for it in items:
            total_counts[it["status"]] += 1
            label = it["label"]
            with st.container(border=True):
                head_cols = st.columns([1, 5, 2])
                with head_cols[0]:
                    st.markdown(
                        f'<div style="font-size:13px; color:{priority_color[it["priority"]]}; text-transform:uppercase; letter-spacing:0.12em; font-weight:600; padding-top:6px;">{priority_label[it["priority"]]}</div>',
                        unsafe_allow_html=True,
                    )
                with head_cols[1]:
                    st.markdown(f"**{escape_html(label)}**")
                with head_cols[2]:
                    new_status = st.selectbox(
                        "Status",
                        status_options,
                        index=status_options.index(it["status"]),
                        key=f"status_{category['id']}_{label}",
                        label_visibility="collapsed",
                    )

                if it.get("topic"):
                    st.markdown(
                        f'<div class="task-topic">↳ Topic: {escape_html(it["topic"])}</div>',
                        unsafe_allow_html=True,
                    )
                st.caption(f"**Why:** {it['why']}")
                st.caption(f"**Action:** {it['action']}")

                link_cols = st.columns([3, 2])
                with link_cols[0]:
                    new_url = st.text_input(
                        "Proof URL",
                        value=it["url"],
                        placeholder="https://... (the published article, profile, etc.)",
                        key=f"url_{category['id']}_{label}",
                        label_visibility="collapsed",
                    )
                with link_cols[1]:
                    new_notes = st.text_input(
                        "Notes",
                        value=it["notes"],
                        placeholder="notes (optional)",
                        key=f"notes_{category['id']}_{label}",
                        label_visibility="collapsed",
                    )

                if (
                    new_status != it["status"]
                    or new_url != it["url"]
                    or new_notes != it["notes"]
                ):
                    tasks_state[label] = {
                        "status": new_status,
                        "url": new_url,
                        "notes": new_notes,
                    }
                    changed = True

                if new_url and new_status == "done":
                    st.markdown(
                        f'<div style="font-size:13px;"><a href="{escape_html(new_url)}" target="_blank">↗ {escape_html(new_url)}</a></div>',
                        unsafe_allow_html=True,
                    )

                if it["auto_present"] and new_status != "done":
                    st.caption("⚐ Auto-detected on page 1 / Perplexity citations — consider marking as done.")

    st.markdown(
        f'<div class="section-title">Plan summary <small>{total_counts["todo"]} todo · {total_counts["in progress"]} doing · {total_counts["done"]} done</small></div>',
        unsafe_allow_html=True,
    )

    if changed:
        save_tasks(tasks_state)
        st.rerun()


def render_welcome():
    st.markdown(
        """
        <div class="welcome-card">
          <div class="welcome-title">Pick a task to begin</div>
          <div class="welcome-body">
            Each task runs a SerpAPI query and classifies the top results as
            <strong style="color: var(--accent)">owned</strong>,
            <strong style="color: var(--info)">earned</strong>,
            <strong style="color: var(--text-dim)">neutral</strong>, or
            <strong style="color: var(--bad)">negative</strong>.
            The saturation score tells you how much of the SERP you control.
          </div>
          <div class="welcome-hint">"""
        + ("↳ Click a task in the sidebar" if st.session_state.config.get("api_key") else "↳ Add SerpAPI key in Settings to start")
        + """</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def escape_html(s):
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_task_result(task):
    result = st.session_state.results.get(task["id"])
    status = st.session_state.task_status.get(task["id"], "idle")

    if status == "running":
        st.markdown(
            f"""
            <div class="query-display">
              <div class="query-text">{escape_html(task['query'])}</div>
              <div class="query-meta">
                <span>Engine · <strong>{task['engine'].upper()}</strong></span>
                <span class="accent">◐ Querying SerpAPI…</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if not result:
        st.markdown(
            f"""
            <div class="query-display">
              <div class="query-text">{escape_html(task['query'])}</div>
            </div>
            <div class="no-kg">No data yet — click run</div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.config.get("api_key"):
            if st.button("▶ Run query", key=f"run_inline_{task['id']}"):
                run_single(task)
                st.rerun()
        return

    if "error" in result:
        st.markdown(
            f"""
            <div class="query-display">
              <div class="query-text">{escape_html(task['query'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.error(f"Error: {result['error']}")
        if st.button("▶ Retry", key=f"retry_{task['id']}"):
            run_single(task)
            st.rerun()
        return

    organic = (result.get("organic_results") or [])[:20]
    counts = {"owned": 0, "earned": 0, "neutral": 0, "negative": 0}
    for r in organic:
        counts[classify(r, st.session_state.config)] += 1

    total = len(organic) or 1
    aligned = counts["owned"] + counts["earned"]
    aligned_pct = int(aligned / total * 100)

    # Header
    st.markdown(
        f"""
        <div class="query-display">
          <div class="query-text">{escape_html(task['query'])}</div>
          <div class="query-meta">
            <span>Engine · <strong>{task['engine'].upper()}</strong></span>
            <span>Results · <strong>{len(organic)}</strong></span>
            <span>Top {total} saturation · <span class="accent">{aligned_pct}%</span></span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Saturation card
    bar_segments = []
    for cls in ["owned", "earned", "neutral", "negative"]:
        if counts[cls]:
            pct = counts[cls] / total * 100
            bar_segments.append(f'<div class="bar-{cls}" style="width: {pct}%"></div>')

    st.markdown(
        f"""
        <div class="saturation-card">
          <div>
            <div class="saturation-number">{aligned}<span>/{total}</span></div>
            <div class="saturation-label">Aligned in top {total}</div>
          </div>
          <div>
            <div class="saturation-bar">{''.join(bar_segments)}</div>
            <div class="legend-grid">
              <div class="legend-cell"><div class="legend-label"><div class="legend-dot bar-owned"></div>Owned</div><div class="legend-count">{counts['owned']}</div></div>
              <div class="legend-cell"><div class="legend-label"><div class="legend-dot bar-earned"></div>Earned</div><div class="legend-count">{counts['earned']}</div></div>
              <div class="legend-cell"><div class="legend-label"><div class="legend-dot bar-neutral"></div>Neutral</div><div class="legend-count">{counts['neutral']}</div></div>
              <div class="legend-cell"><div class="legend-label"><div class="legend-dot bar-negative"></div>Negative</div><div class="legend-count">{counts['negative']}</div></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Knowledge Graph
    kg = result.get("knowledge_graph")
    if kg:
        st.markdown(
            f"""
            <div class="kg-card">
              <div class="kg-title">{escape_html(kg.get('title', ''))}</div>
              {f'<div class="kg-type">{escape_html(kg.get("type", ""))}</div>' if kg.get('type') else ''}
              {f'<div class="kg-desc">{escape_html(kg.get("description", ""))}</div>' if kg.get('description') else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="no-kg">No Knowledge Graph for this query — entity not yet established</div>',
            unsafe_allow_html=True,
        )

    # Organic results
    st.markdown(
        f'<div class="section-title">Top Results <small>{len(organic)} ranked</small></div>',
        unsafe_allow_html=True,
    )

    for i, r in enumerate(organic):
        cls = classify(r, st.session_state.config)
        title = escape_html(r.get("title") or "Untitled")
        link = r.get("link") or ""
        displayed = escape_html(r.get("displayed_link") or link)
        snippet = escape_html(r.get("snippet") or "")
        st.markdown(
            f"""
            <div class="result-row">
              <div class="result-pos">{i+1:02d}</div>
              <div class="result-body">
                <div class="result-title">{title}</div>
                <div class="result-link"><a href="{escape_html(link)}" target="_blank" rel="noopener">{displayed}</a></div>
                {f'<div class="result-snippet">{snippet}</div>' if snippet else ''}
              </div>
              <div class="tag {cls}">{cls}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Negative tagging UI
    if organic:
        with st.expander("Mark results as negative"):
            options = [f"{i+1}. {r.get('title', '')[:80]}" for i, r in enumerate(organic)]
            current_negatives = st.session_state.config.get("negatives", [])
            current_indices = [
                i for i, r in enumerate(organic) if result_key(r) in current_negatives
            ]
            selected = st.multiselect(
                "Select results to mark as negative",
                options=list(range(len(organic))),
                default=current_indices,
                format_func=lambda i: f"{i+1}. {organic[i].get('title', '')[:60]}",
                key=f"negs_{task['id']}",
            )
            if st.button("Update", key=f"upd_negs_{task['id']}"):
                neg_set = set(st.session_state.config.get("negatives", []))
                # Remove old negatives from this task's results
                for r in organic:
                    neg_set.discard(result_key(r))
                # Add new
                for i in selected:
                    neg_set.add(result_key(organic[i]))
                st.session_state.config["negatives"] = list(neg_set)
                save_config(st.session_state.config)
                st.rerun()

    # People also ask
    paa = result.get("related_questions") or []
    if paa:
        st.markdown(
            f'<div class="section-title">People Also Ask <small>{len(paa)}</small></div>',
            unsafe_allow_html=True,
        )
        for q in paa[:6]:
            snippet = escape_html(q.get("snippet", "") or "")
            st.markdown(
                f"""
                <div class="result-row" style="grid-template-columns: 36px 1fr;">
                  <div class="result-pos">?</div>
                  <div class="result-body">
                    <div class="result-title">{escape_html(q.get('question', ''))}</div>
                    {f'<div class="result-snippet">{snippet}</div>' if snippet else ''}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Related searches
    related = result.get("related_searches") or []
    if related:
        st.markdown(
            f'<div class="section-title">Related Searches <small>{len(related)}</small></div>',
            unsafe_allow_html=True,
        )
        pills = "".join(
            f'<div class="pill">{escape_html(rs.get("query", "") if isinstance(rs, dict) else rs)}</div>'
            for rs in related
        )
        st.markdown(f'<div class="related-pills">{pills}</div>', unsafe_allow_html=True)


# Render
if st.session_state.view_mode == "Strategy":
    render_strategy()
else:
    if st.session_state.active_task_id is None:
        render_welcome()
    else:
        task = get_task(st.session_state.active_task_id)
        if task:
            render_task_result(task)
        else:
            st.session_state.active_task_id = None
            render_welcome()
