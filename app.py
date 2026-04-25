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
  --surface-2: #F4EFE2;
  --border: #E5DFD0;
  --border-bright: #C9C2B0;
  --text: #1F1D1A;
  --text-dim: #4A453B;
  --muted: #8A8474;
  --accent: #1F4E3D;
  --accent-light: #2D6B54;
  --good: #3B7A52;
  --warn: #B85C00;
  --bad: #A8362A;
  --info: #2D5A8C;
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
  font-style: italic;
  font-weight: 400;
  letter-spacing: -0.02em;
  color: var(--text);
  line-height: 1.1;
  margin-bottom: 4px;
}
.brand-mark::first-letter { color: var(--accent); }

.brand-tag {
  font-size: 9px;
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
  font-size: 10px;
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
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--muted);
  margin: 18px 0 8px;
  font-weight: 500;
}

.task-group-label {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 13px;
  color: var(--accent);
  margin: 16px 0 6px;
}

/* Streamlit button overrides */
.stButton > button {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 11px !important;
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
  font-size: 12px !important;
  border-radius: 0 !important;
  border-color: var(--border) !important;
  background: var(--surface) !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: none !important;
}

label {
  font-size: 10px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.15em !important;
  color: var(--muted) !important;
}

/* Expanders */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 11px !important;
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
  font-style: italic;
  font-weight: 300;
  font-size: 48px;
  color: var(--text-dim);
  letter-spacing: -0.02em;
  margin-bottom: 16px;
}

.welcome-body {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.7;
  margin-bottom: 32px;
}

.welcome-hint {
  font-size: 10px;
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
  font-style: italic;
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
  font-size: 10px;
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
  font-weight: 300;
  color: var(--accent);
  line-height: 0.95;
  letter-spacing: -0.04em;
}

.saturation-number span {
  color: var(--muted);
  font-size: 36px;
}

.saturation-label {
  font-size: 9px;
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
  font-size: 9px;
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
  font-size: 8px;
  letter-spacing: 0.22em;
  color: var(--accent);
}
.kg-title { font-family: 'Fraunces', serif; font-size: 24px; margin-bottom: 4px; }
.kg-type { font-size: 10px; text-transform: uppercase; letter-spacing: 0.15em; color: var(--muted); margin-bottom: 12px; }
.kg-desc { font-size: 12px; color: var(--text-dim); line-height: 1.6; }

.no-kg {
  background: var(--surface);
  border: 1px dashed var(--border-bright);
  padding: 14px 20px;
  margin-bottom: 32px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
}
.no-kg::before { content: '⚠ '; color: var(--warn); }

/* Section title */
.section-title {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 22px;
  color: var(--text);
  margin: 32px 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.section-title small {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
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
  font-weight: 300;
  line-height: 1;
}

.result-body { min-width: 0; }
.result-title {
  font-size: 13px;
  color: var(--text);
  margin-bottom: 4px;
  font-weight: 500;
}
.result-link {
  font-size: 11px;
  margin-bottom: 6px;
  word-break: break-all;
}
.result-link a {
  color: var(--info);
  text-decoration: none;
}
.result-link a:hover { color: var(--accent); }
.result-snippet {
  font-size: 11px;
  color: var(--muted);
  line-height: 1.6;
}

.tag {
  align-self: start;
  text-align: center;
  padding: 4px 10px;
  font-size: 9px;
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
  font-size: 11px;
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
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
CONFIG_FILE = Path("config.json")
SNAPSHOTS_FILE = Path("snapshots.json")

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
def call_serpapi(query, engine, api_key, timeout=30):
    params = {"q": query, "engine": engine, "api_key": api_key, "num": 20}
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

all_tasks = TASKS + st.session_state.custom_tasks


def get_task(task_id):
    for t in all_tasks:
        if t["id"] == task_id:
            return t
    return None


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

    # Settings expander
    with st.expander("⚙ Settings", expanded=not has_key):
        api_input = st.text_input(
            "SerpAPI Key",
            value=st.session_state.config.get("api_key", ""),
            type="password",
            help="Get one at serpapi.com/dashboard. Free tier = 100 searches/month.",
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
            status_text.markdown(f'<div style="font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:0.1em">Running: {task["label"]}</div>', unsafe_allow_html=True)
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
                    organic = (result.get("organic_results") or [])[:10]
                    aligned = sum(
                        1 for r in organic if classify(r, st.session_state.config) in ("owned", "earned")
                    )
                    sat_label = f"  {aligned}/10"

            label_text = f"{icon}  {task['label'][:28]}{sat_label}"
            if st.button(label_text, key=f"task_{task['id']}", use_container_width=True):
                st.session_state.active_task_id = task["id"]
                if task["id"] not in st.session_state.results and has_key:
                    run_single(task)
                st.rerun()


# ============================================================
# MAIN PANEL
# ============================================================
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
if st.session_state.active_task_id is None:
    render_welcome()
else:
    task = get_task(st.session_state.active_task_id)
    if task:
        render_task_result(task)
    else:
        st.session_state.active_task_id = None
        render_welcome()
