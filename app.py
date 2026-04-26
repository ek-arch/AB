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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  --bg: #FFFFFF;
  --surface: #FFFFFF;
  --surface-2: #F4F4F4;
  --border: #D4D4D4;
  --border-bright: #9C9C9C;
  --text: #0A0A0A;
  --text-dim: #1F1F1F;
  --muted: #525252;
  --accent: #15402F;
  --accent-light: #1F5C44;
  --good: #176638;
  --warn: #8C4500;
  --bad: #931F19;
  --info: #1A3F66;
}

html, body, [class*="css"], .stApp, .main, .block-container {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
  color: var(--text) !important;
  font-size: 16px;
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
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
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
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
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
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
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
  font-family: 'Inter', sans-serif;
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

/* ===== Sidebar navigation ===== */
.nav-links { display: flex; flex-direction: column; gap: 4px; margin-top: 8px; }
.nav-link {
  display: block;
  padding: 10px 14px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text) !important;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none !important;
  transition: all 0.12s;
}
.nav-link:hover {
  background: var(--surface-2);
  border-color: var(--accent);
  color: var(--accent) !important;
}
.nav-link-step { font-weight: 600; }
.nav-link-sub {
  font-size: 13px;
  padding: 8px 14px 8px 28px;
  font-weight: 500;
}
.nav-sublabel {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--muted);
  margin: 14px 0 6px;
  font-weight: 600;
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

# Drop-in design system (deep-navy theme). Loaded AFTER CUSTOM_CSS so its base
# overrides (typography, buttons, sidebar surface) win the cascade.
try:
    from components import inject_css as _inject_design_css
    _inject_design_css()
except Exception:
    pass

# ============================================================
# CONSTANTS
# ============================================================
CONFIG_FILE = Path("config.json")
SNAPSHOTS_FILE = Path("snapshots.json")
TASKS_FILE = Path("tasks.json")

DEFAULT_OWNED = [
    "bruiaka.com",
    "andriibruiaka.com",
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

# Single primary search powering the Strategy view. Not shown in the sidebar list.
PRIMARY_TASK = {
    "id": "core_g",
    "group": "_primary",
    "label": "andrii bruiaka",
    "engine": "google",
    "query": "andrii bruiaka",
}

TASKS = [PRIMARY_TASK]

# ============================================================
# PERSISTENCE
# ============================================================
def load_config():
    """Load config from disk, with secrets fallback for cloud deploys."""
    config = {
        "api_key": "",
        "perplexity_key": "",
        "openai_key": "",
        "owned_domains": DEFAULT_OWNED.copy(),
        "earned_domains": DEFAULT_EARNED.copy(),
        "negative_domains": ["fintelegram.com"],
        "negatives": [],
        "irrelevant": [],
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
    try:
        if not config["openai_key"] and "openai_key" in st.secrets:
            config["openai_key"] = st.secrets["openai_key"]
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


def empty_tasks_doc():
    return {"states": {}, "hidden": [], "custom": {}}


def load_tasks():
    """Return {states, hidden, custom}. Migrate legacy flat dict if needed."""
    if not TASKS_FILE.exists():
        return empty_tasks_doc()
    try:
        data = json.loads(TASKS_FILE.read_text())
    except Exception:
        return empty_tasks_doc()
    if isinstance(data, dict) and "states" in data:
        data.setdefault("hidden", [])
        data.setdefault("custom", {})
        return data
    # Legacy flat schema: {label: {status, url, notes}} → migrate
    return {"states": data if isinstance(data, dict) else {}, "hidden": [], "custom": {}}


def _github_token():
    """Read GitHub PAT from Streamlit secrets. Returns None if not configured."""
    try:
        return st.secrets.get("github_token") or st.secrets.get("GITHUB_TOKEN")
    except Exception:
        return None


def push_tasks_to_github(doc, repo="ek-arch/AB", path="tasks.json", branch="main"):
    """Best-effort: commit tasks.json to GitHub via the contents API.
    Silently no-ops if no token is configured (e.g. local dev).
    Returns (ok: bool, message: str) so the caller can show feedback.
    """
    import base64
    token = _github_token()
    if not token:
        return False, "no token (saved locally only)"
    try:
        api = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        # Get current sha (required for updates; omit for first create)
        get = requests.get(api, headers=headers, params={"ref": branch}, timeout=10)
        sha = get.json().get("sha") if get.status_code == 200 else None

        body = json.dumps(doc, indent=2)
        payload = {
            "message": f"app: update tasks.json ({datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')})",
            "content": base64.b64encode(body.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha

        put = requests.put(api, headers=headers, json=payload, timeout=15)
        if put.status_code in (200, 201):
            return True, "synced to github"
        return False, f"github HTTP {put.status_code}: {put.text[:120]}"
    except Exception as e:
        return False, f"github error: {e}"


def save_tasks(doc):
    # Always write locally first (so the running session sees the change)
    try:
        TASKS_FILE.write_text(json.dumps(doc, indent=2))
    except Exception:
        pass
    # Then attempt to mirror to GitHub for cross-deploy persistence
    push_tasks_to_github(doc)


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


OPENAI_PROBE = PERPLEXITY_PROBE


def call_openai(query, api_key, timeout=60):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-search-preview",
        "web_search_options": {},
        "messages": [{"role": "user", "content": query}],
    }
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=timeout,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.json()


def parse_openai(data):
    """Extract answer + citation URLs from OpenAI web-search response."""
    msg = (data.get("choices") or [{}])[0].get("message") or {}
    answer = msg.get("content", "") or ""
    urls = []
    for ann in (msg.get("annotations") or []):
        if ann.get("type") == "url_citation":
            url = (ann.get("url_citation") or {}).get("url")
            if url:
                urls.append(url)
    # Dedupe preserving order
    seen = set()
    citation_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            citation_urls.append(u)
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
    for d in (config.get("negative_domains") or []):
        if d and d.lower() in url:
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
        "subtitle": "Each placement = a page-1 SERP slot on a high-trust domain plus citation fodder for LLMs. Realistic friction noted in each action.",
        "tasks": [
            {
                "label": "Finextra Member Blog — self-publish under your profile",
                "priority": 1,
                "effort": 2,
                "default_status": "in progress",
                "topic": "\"How small fintechs rebuild infrastructure without 50-person engineering teams\" — Onicore POV",
                "why": "Finextra has no public editor inbox for cold pitches. The realistic path that ranks page-1 for founder names is the free Member Blog: your own author profile + posts on finextra.com/blogposts.",
                "action": "Account already registered (rep management). Next: complete profile (headshot, company, bio, links), publish first post via Member Blog. Author page goes live at finextra.com/blogs/<slug>.",
                "domains": ["finextra.com"],
            },
            {
                "label": "The Fintech Times — guest contributor",
                "priority": 2,
                "effort": 3,
                "topic": "\"Embedded finance is dead — long live infrastructure-as-a-service\" POV piece",
                "why": "Takes guest contributions but most slots come through their PR partnership program (paid) or existing relationships. Cold submissions go to a slow queue.",
                "action": "Two-track: (a) submit via thefintechtimes.com/submit-an-article-or-news-story with a finished draft (4-8 week response window, ~30% accept rate); (b) pitch via LinkedIn DM to a named TFT editor — find recent bylines, reference one. Don't expect a cold-email reply from a generic inbox.",
                "domains": ["thefintechtimes.com"],
            },
            {
                "label": "Sifted — founder profile or quote",
                "priority": 2,
                "effort": 4,
                "topic": "Eastern-European founders rebuilding EU fintech infra (panel piece, you as one of 3-4)",
                "why": "Sifted essentially does not run unsolicited founder profiles. Realistic entry is being a quoted source on a story they're already writing, or a news hook (raise, partnership, regulatory move) plus a warm intro.",
                "action": "(a) Set up alerts on a few Sifted reporters covering fintech infra (Amy O'Brien, Tom Matsuda) and reply to their X/LinkedIn posts with substantive takes. (b) When you have a news hook, pitch via warm intro from an existing Sifted source (other founder, VC). (c) Set up a Featured.com / Qwoted profile to be source-able.",
                "domains": ["sifted.eu"],
            },
            {
                "label": "Banking Dive / Payments Dive — get quoted as a source",
                "priority": 2,
                "effort": 2,
                "default_status": "in progress",
                "topic": "Compliance / fraud-prevention angle — operational fintech infra commentary",
                "why": "Banking Dive doesn't take guest pieces and rarely profiles individuals. Reliable path is being a named source in their own reporting.",
                "action": "Per rep management — 'unique article for review' draft is in progress. Also sign up on Featured.com, Qwoted, Help a B2B Writer (free) and answer 2-3 prompts/week tagged compliance/fintech.",
                "domains": ["bankingdive.com", "paymentsdive.com"],
            },
            {
                "label": "Crypto press — Decrypt / Cointelegraph / The Block",
                "priority": 2,
                "effort": 3,
                "topic": "\"Why crypto UX still fails: passkeys, recovery, and the seed-phrase problem\" — Kolo wallet POV",
                "why": "Coindesk's contributor program was wound down post-restructuring; cold pitches there are unproductive. Decrypt/Cointelegraph still take guest posts but mostly via paid placement or via PR firms. Editorial coverage requires news.",
                "action": "Two paths: (a) bylined sponsored content via PR agency (Wachsman, MarketAcross — $$$ but reliably indexes for the name); (b) earned: pitch a reporter (Decrypt's Mat Di Salvo, CT's Helen Partz) only with hard data — not opinions. Lead with a chart or a number from Kolo.",
                "domains": ["decrypt.co", "cointelegraph.com", "theblock.co"],
            },
            {
                "label": "HackerNoon — contributor + 2 articles",
                "priority": 3,
                "effort": 2,
                "default_status": "in progress",
                "topic": "Technical post-mortems of building Onicore / Kolo. Long-form, code-light.",
                "why": "Sign-up is open but every submission goes through editorial review (1-3 weeks, ~50% accept rate). Author page ranks for the name once you have 2+ posts.",
                "action": "Per rep management — first article queued. Submit second piece within 30 days so the author page has weight (rotate from crypto.news, biweekly cadence).",
                "domains": ["hackernoon.com"],
            },
            {
                "label": "Substack-syndicated newsletters — be the guest writer",
                "priority": 2,
                "effort": 2,
                "topic": "Guest essays on Fintech Brainfood (Simon Taylor), Net Interest, Popular Fintech",
                "why": "Faster than tier-1 press. Each newsletter has 10K-50K fintech readers + the post lives on a substack.com URL that ranks for the name.",
                "action": "DM the writer with a 3-bullet pitch + 1 paragraph teaser. Reference one of their recent issues. Conversion rate ~30% if the angle is sharp.",
                "domains": ["substack.com"],
            },
            {
                "label": "Podcast — Fintech Insider (11:FS)",
                "priority": 2,
                "effort": 4,
                "topic": "\"Building fintech infrastructure outside the big-bank stack\"",
                "why": "Highly relationship-driven booking. Cold form-fills via 11fs.com rarely convert. Realistic path is via a current/former 11:FS person or an existing guest who can intro.",
                "action": "Map your 2nd-degree LinkedIn connections to 11:FS staff (David Brear, Jason Bates, Simon Taylor) and ask one for an intro to the booking producer. Bring a sharp angle they haven't covered, not a generic founder pitch.",
                "domains": ["11fs.com"],
            },
            {
                "label": "Podcast — This Week in Fintech",
                "priority": 2,
                "effort": 3,
                "topic": "Founder spotlight or panel on embedded finance",
                "why": "TWIF is primarily a newsletter; the podcast slots are limited and booked by Nik Milanović personally. Cold email works better than for 11:FS but still <20% reply rate.",
                "action": "Email Nik with a 1-paragraph pitch + 1 specific TWIF newsletter issue you'd extend on. Subscribing + commenting in the TWIF community Slack ahead of pitching helps. Don't pitch for a generic founder spot — pitch for a panel he's already running.",
                "domains": ["thisweekinfintech.com"],
            },
            {
                "label": "TechCrunch / Forbes coverage",
                "priority": 1,
                "effort": 5,
                "topic": "Onicore funding announcement, partnership, or product launch — news hook required",
                "why": "Single biggest entity-recognition trigger for Google. Once you have one, KG entry often follows.",
                "action": "Don't pitch a profile cold (won't work). Wait for a news hook (raise, named-customer milestone, regulatory first). Engage a tier-1 PR firm 6 weeks out, or get a warm intro from a portfolio-company founder. Forbes Council membership ($1.7K/yr) is a paid shortcut to forbes.com author page.",
                "domains": ["techcrunch.com", "forbes.com"],
            },
        ],
    },
    {
        "id": "profiles",
        "title": "Profile sites — claim or register",
        "subtitle": "Each profile = a SERP slot you control with your own copy. Most rank for the name within days. Most are free.",
        "tasks": [
            {
                "label": "Crunchbase person page",
                "priority": 1,
                "effort": 1,
                "default_status": "done",
                "why": "Always ranks for founder names. Drives entity recognition. Links to founded companies.",
                "action": "✅ Already registered (rep management). Verify it links Onicore + Nonbank.io + Kolo, headshot + bio + LinkedIn are current; refresh quarterly.",
                "domains": ["crunchbase.com"],
            },
            {
                "label": "GitHub profile",
                "priority": 2,
                "effort": 1,
                "why": "10-min win. Ranks for technical founder names. Read by LLMs.",
                "action": "github.com/andriibruiaka — fill bio, link bruiaka.com, pin 3 repos (even if just docs/specs). Not in rep management; treat as still todo.",
                "domains": ["github.com"],
            },
            {
                "label": "AllMyLinks profile",
                "priority": 3,
                "effort": 1,
                "default_status": "done",
                "why": "Aggregator that ranks for the name. Acts as a meta-bio when nothing else exists yet.",
                "action": "✅ Already registered (rep management). Verify allmylinks.com/andriibruiaka links every active profile and is current.",
                "domains": ["allmylinks.com"],
            },
            {
                "label": "Hashnode author profile + 1 cross-post",
                "priority": 3,
                "effort": 1,
                "default_status": "done",
                "why": "Indexes fast, ranks well for technical author names.",
                "action": "✅ Profile registered (rep management — biweekly article cadence). Verify @andriibruiaka and that latest Substack post is cross-posted.",
                "domains": ["hashnode.com"],
            },
            {
                "label": "Dev.to author profile + 1 cross-post",
                "priority": 3,
                "effort": 1,
                "default_status": "done",
                "why": "Same as Hashnode — author page ranks.",
                "action": "✅ Profile registered (rep management — biweekly article cadence). 'Fintech and Web3 are merging' published at dev.to/andriibruiaka.",
                "domains": ["dev.to"],
            },
            {
                "label": "Medium author profile + 1 cross-post",
                "priority": 3,
                "effort": 1,
                "default_status": "done",
                "why": "medium.com/@<name> ranks page-1 for many founder names.",
                "action": "✅ Profile registered, monthly article updates per rep management. Confirm vanity URL @andriibruiaka and current canonical-back to Substack.",
                "domains": ["medium.com"],
            },
            {
                "label": "F6S profile",
                "priority": 3,
                "effort": 1,
                "default_status": "done",
                "why": "Startup-ecosystem directory, indexes fast for founder names.",
                "action": "✅ Already registered (rep management). Verify all ventures + advisor + investor sections are populated.",
                "domains": ["f6s.com"],
            },
            {
                "label": "X / Twitter — verified handle, complete bio",
                "priority": 2,
                "effort": 1,
                "default_status": "in progress",
                "why": "Profile cards appear in some Google name searches and feed Grok/ChatGPT.",
                "action": "Handle exists. Verify bio = name + role + company + link to bruiaka.com. Verified ($8/mo) noticeably helps entity recognition — turn on if not already.",
                "domains": ["twitter.com", "x.com"],
            },
            {
                "label": "AngelList / Wellfound founder profile",
                "priority": 2,
                "effort": 2,
                "why": "Founder-focused, ranks well for the name + 'founder' qualifier.",
                "action": "wellfound.com → mark as founder → link companies + add 200-word bio. (5-min create, but wellfound profiles take 1-2 days to start ranking.)",
                "domains": ["wellfound.com", "angel.co"],
            },
            {
                "label": "Speakerhub profile",
                "priority": 2,
                "effort": 2,
                "why": "Pulls inbound podcast and conference invitations — feeds the press category.",
                "action": "speakerhub.com → list 3 talk topics matching brand pillars (fintech infra, embedded finance, crypto UX). Inbound conversion takes 4-8 weeks.",
                "domains": ["speakerhub.com"],
            },
            {
                "label": "Reddit — earn karma, one organic mention",
                "priority": 3,
                "effort": 5,
                "default_status": "in progress",
                "why": "LLMs (especially ChatGPT) lean heavily on Reddit. One thread can move AI answers.",
                "action": "Account purchased per rep management ('set up/buy reddit acc, weekly comments'). Continue: 4 weeks of karma in r/fintech / r/startups / r/CryptoCurrency, then a Show & Tell or AMA tied to a launch.",
                "domains": ["reddit.com"],
            },
            {
                "label": "Wikidata entry",
                "priority": 1,
                "effort": 4,
                "why": "Lower bar than Wikipedia. Feeds Google Knowledge Graph + read as authoritative by ChatGPT/Perplexity/Claude.",
                "action": "Realistic prerequisite: 2+ tier-1 third-party sources (Finextra/TFT/TC/Forbes). Without them the entry gets nominated for deletion within 30 days. Sequence: land press first → then create at wikidata.org/wiki/Special:NewItem with full statements (occupation, employer, founder of, sameAs).",
                "domains": ["wikidata.org"],
            },
        ],
    },
    {
        "id": "owned",
        "title": "Owned web properties",
        "subtitle": "Sites you fully control. Add Person schema for entity recognition; cross-link aggressively.",
        "tasks": [
            {
                "label": "andriibruiaka.com — confirm ownership + add to Owned Domains",
                "priority": 1,
                "effort": 1,
                "default_status": "done",
                "why": "Perplexity already cites it. Make sure it's officially owned and counted in this dashboard's saturation score.",
                "action": "✅ Added to DEFAULT_OWNED (and substring 'andriibruiaka' was already matching). Saturation now counts it as owned.",
                "domains": ["andriibruiaka.com"],
            },
            {
                "label": "Substack 'About' page polish",
                "priority": 2,
                "effort": 2,
                "default_status": "in progress",
                "why": "About page is what LLMs hit for bio queries. Make it crawlable and entity-tagged.",
                "action": "Substack registered (rep management — 4 articles already published incl. 'From seed phrases to Face ID', 'Why 80% of crypto users still avoid self-custody', 'What 2025 taught us about crypto adoption'). Verify About page: name in H1, 3-paragraph bio, links to all founded companies.",
                "domains": ["substack.com"],
            },
            {
                "label": "Cornerstone Substack post: bio-style canonical",
                "priority": 1,
                "effort": 3,
                "topic": "\"Andrii Bruiaka — what I work on\" — name in title, URL slug, H1, plus links to bruiaka.com and every owned profile",
                "why": "Substack ranks fast and acts as a canonical bio answering 'who is...' queries. Articles published so far are topical — still missing the explicit bio-canonical post.",
                "action": "Write a dedicated bio post (separate from the topic articles already on Substack). Title: \"Andrii Bruiaka: building fintech infrastructure\". URL slug /p/andrii-bruiaka. Internal-link every profile URL. ~3 hours.",
                "domains": ["substack.com"],
            },
            {
                "label": "bruiaka.com — Person schema.org JSON-LD",
                "priority": 1,
                "effort": 3,
                "why": "Tells Google explicitly 'this site is the person Andrii Bruiaka.' Single biggest on-page Knowledge Graph signal.",
                "action": "Add JSON-LD <script type=\"application/ld+json\"> in <head> with @type:Person, name, jobTitle, worksFor (Onicore), sameAs array (LinkedIn, Substack, Crunchbase, Wikidata once live). Half-day if you have CMS access; longer if you have to brief a webflow dev.",
                "domains": [],
            },
            {
                "label": "Onicore.io — founder bio block on /about",
                "priority": 2,
                "effort": 3,
                "why": "Reciprocal linking from company → founder strengthens the entity graph.",
                "action": "Brief web team: dedicated bio block on /about (or /team) with name as H2, photo, 2-paragraph bio, link to bruiaka.com + LinkedIn. Half-day including review cycle.",
                "domains": ["onicore.io", "onicore.ie"],
            },
            {
                "label": "Nonbank.io — founder bio on /about or /team",
                "priority": 2,
                "effort": 3,
                "why": "Same as Onicore — reciprocal entity signal.",
                "action": "Brief web team: name as H2, photo, link out to bruiaka.com + LinkedIn. Half-day.",
                "domains": ["nonbank.io"],
            },
        ],
    },
    {
        "id": "content",
        "title": "Content cadence",
        "subtitle": "Recurring rhythm. Treat each as a standing task — re-mark monthly.",
        "tasks": [
            {
                "label": "Quarterly Wikidata refresh",
                "priority": 3,
                "effort": 2,
                "why": "Every new tier-1 press piece = a new sitelink to add as evidence. Keeps the entry from being challenged.",
                "action": "Once per quarter, add new press citations as 'reference URL' on existing statements. Update job/company if changed. ~30 min per quarter.",
                "domains": ["wikidata.org"],
            },
            {
                "label": "Monthly Medium cross-post",
                "priority": 2,
                "effort": 2,
                "why": "Reach + author-page weight. Cross-post with canonical link back to Substack.",
                "action": "After each Substack post, paste into Medium → Story Settings → 'Import a story' or set canonical. ~20 min.",
                "domains": ["medium.com"],
            },
            {
                "label": "Monthly tier-1 outlet pitch (1 outbound)",
                "priority": 1,
                "effort": 3,
                "why": "Keeps the press funnel alive. Even 1 in 5 lands = 2-3 placements/year, which moves SERP and KG.",
                "action": "Rotate Finextra Member Blog → TFT → crypto press → Featured/Qwoted prompts. One pitch every 4 weeks. 2-3 hours per pitch including research.",
                "domains": [],
            },
            {
                "label": "Monthly podcast pitch (1 outbound)",
                "priority": 1,
                "effort": 3,
                "why": "Forces a steady press cadence. Even 1 in 5 lands = 2-3 episodes/year, which moves both SERP and KG.",
                "action": "Pick 1 podcast/month from the press category. Spend 2 hours: listen to 1 recent episode, write a pitch that explicitly extends it.",
                "domains": [],
            },
            {
                "label": "Bi-weekly LinkedIn long-form",
                "priority": 2,
                "effort": 4,
                "why": "LinkedIn long-form posts surface in Google for the name + drive inbound DMs from journalists.",
                "action": "1 long-form (1000+ words) every 2 weeks. Cheapest source: trim a Substack post. ~3 hours each.",
                "domains": ["linkedin.com"],
            },
            {
                "label": "Monthly Substack post (cornerstone, 1500+ words)",
                "priority": 1,
                "effort": 5,
                "topic": "Pillars: fintech infrastructure · embedded finance · crypto UX · passkeys / auth",
                "why": "1 post/month at 1500+ words is the bare minimum for Substack to rank consistently.",
                "action": "Calendar 4 topics ahead. Each post: name in author byline, 1 mention in body, link to /about. Realistic effort: 1 day per post including drafting + edit.",
                "domains": ["substack.com"],
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
if "openai_result" not in st.session_state:
    st.session_state.openai_result = None
if "openai_status" not in st.session_state:
    st.session_state.openai_status = "idle"

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


def run_openai():
    key = st.session_state.config.get("openai_key")
    if not key:
        st.session_state.openai_status = "error"
        st.session_state.openai_result = {"error": "No OpenAI key configured"}
        return
    try:
        st.session_state.openai_status = "running"
        data = call_openai(OPENAI_PROBE, key)
        st.session_state.openai_result = data
        st.session_state.openai_status = "ok"
    except Exception as e:
        st.session_state.openai_status = "error"
        st.session_state.openai_result = {"error": str(e)}


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
        pplx_input = st.text_input(
            "Perplexity Key (optional)",
            value=st.session_state.config.get("perplexity_key", ""),
            type="password",
            help="Get one at perplexity.ai/settings/api. Used for the LLM visibility check.",
        )
        openai_input = st.text_input(
            "OpenAI Key (optional)",
            value=st.session_state.config.get("openai_key", ""),
            type="password",
            help="Get one at platform.openai.com/api-keys. Used for the ChatGPT (web search) visibility check.",
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
        negative_input = st.text_area(
            "Negative Domains (one per line)",
            value="\n".join(st.session_state.config.get("negative_domains", [])),
            height=100,
            help="Domains where any result auto-classifies as negative (e.g. watchdog/hit-piece sites)",
        )
        if st.button("Save Settings", use_container_width=True):
            st.session_state.config["api_key"] = api_input.strip()
            st.session_state.config["perplexity_key"] = pplx_input.strip()
            st.session_state.config["openai_key"] = openai_input.strip()
            st.session_state.config["owned_domains"] = [
                l.strip() for l in owned_input.split("\n") if l.strip()
            ]
            st.session_state.config["earned_domains"] = [
                l.strip() for l in earned_input.split("\n") if l.strip()
            ]
            st.session_state.config["negative_domains"] = [
                l.strip() for l in negative_input.split("\n") if l.strip()
            ]
            save_config(st.session_state.config)
            st.success("Saved")
            time.sleep(0.5)
            st.rerun()

    # Navigation — switches main panel between views
    if "view_radio" not in st.session_state:
        st.session_state.view_radio = "Overview"

    st.markdown('<div class="section-label">Navigation</div>', unsafe_allow_html=True)
    st.radio(
        "View",
        ["Overview", "01 · Google search", "02 · LLM visibility", "03 · Action plan", "04 · Content plan"],
        label_visibility="collapsed",
        key="view_radio",
    )

    st.markdown(
        """
        <div class="nav-links" style="display:none;">
          <a href="#step-1-google" class="nav-link nav-link-step">01 · Google search</a>
          <a href="#step-2-llm" class="nav-link nav-link-step">02 · LLM visibility</a>
          <a href="#step-3-action" class="nav-link nav-link-step">03 · Action plan</a>
          <div class="nav-sublabel">Action plan categories</div>
          <a href="#cat-press" class="nav-link nav-link-sub">Articles &amp; press</a>
          <a href="#cat-profiles" class="nav-link nav-link-sub">Profile sites</a>
          <a href="#cat-owned" class="nav-link nav-link-sub">Owned web properties</a>
          <a href="#cat-content" class="nav-link nav-link-sub">Content cadence</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CONTENT PLAN — concrete editorial calendar
# Each item = an article/podcast/post with title, outlet, keywords, thesis.
# Status persists in tasks.json under the same `states` dict keyed by title.
# ============================================================
CONTENT_PILLARS = [
    {"id": "crypto-ux",  "title": "Crypto usability, wallets & ownership"},
    {"id": "infra",      "title": "Fintech infrastructure & APIs"},
    {"id": "compliance", "title": "Compliance, RegTech & anti-fraud"},
    {"id": "ai",         "title": "Fintech + AI"},
    {"id": "banking",    "title": "Digital banking & cross-border"},
    {"id": "investment", "title": "Fintech investment & ecosystems"},
    {"id": "tech",       "title": "Engineering & build stories"},
]

CONTENT_PLAN = [
    # ============ Crypto UX (already publishing here) ============
    {
        "title": "From seed phrases to Face ID: the human side of crypto UX",
        "pillar": "crypto-ux",
        "outlets": ["Substack", "Finextra", "TFT", "Medium", "LinkedIn"],
        "keywords": ["passkeys", "crypto UX", "self-custody", "Face ID", "WebAuthn"],
        "thesis": "Passwords are the weakest link in fintech. Passkeys bridge UX + security: biometric login with cryptographic safety. The future of crypto onboarding looks like Apple Pay.",
        "default_status": "done",
        "default_url": "https://open.substack.com/pub/andrewbruiaka/p/from-seed-phrases-to-face-id",
    },
    {
        "title": "Why 80% of crypto users still avoid self-custody — and how to fix it",
        "pillar": "crypto-ux",
        "outlets": ["CoinMarketCap", "LinkedIn", "Substack"],
        "keywords": ["self-custody", "non-custodial wallets", "exchange dependence", "Chainalysis 2024"],
        "thesis": "Most crypto sits on exchanges, not wallets. Better UX, simple recovery, and passkey tech can close the gap between security and usability. Freedom is meaningless if it's too hard to use.",
        "default_status": "done",
        "default_url": "https://andrewbruiaka.substack.com/p/why-80-of-crypto-users-still-avoid",
    },
    {
        "title": "What 2025 taught us about crypto adoption",
        "pillar": "crypto-ux",
        "outlets": ["Substack", "LinkedIn"],
        "keywords": ["crypto adoption", "user retention", "regulation", "Statista 1B forecast"],
        "thesis": "500M+ crypto users now, but most stick to exchanges. UX and trust are the new growth engines. Markets with stronger compliance saw the highest retention. Forecast: 1B users by 2027 — but only if UX keeps improving.",
        "default_status": "done",
        "default_url": "https://andrewbruiaka.substack.com/p/what-2025-taught-me-about-crypto",
    },
    {
        "title": "The wallet is becoming the new home screen of finance",
        "pillar": "crypto-ux",
        "outlets": ["Finextra Member Blog", "TFT", "Stack Overflow blog", "fintechfilter.com"],
        "keywords": ["super-apps", "Revolut", "PayPal", "Cash App", "Gen Z finance", "mobile wallets"],
        "thesis": "Most fintech users open a wallet app more often than a bank's website. Super-apps blend payments + crypto + credit. For the next generation, the wallet IS the bank — 68% of Gen Z manage finances through mobile wallets (Statista 2025).",
        "default_status": "in progress",
    },
    {
        "title": "Fintech and Web3 are merging into one ecosystem",
        "pillar": "crypto-ux",
        "outlets": ["dev.to", "LinkedIn", "Medium"],
        "keywords": ["fintech web3 convergence", "stablecoins", "digital identity", "unified finance"],
        "thesis": "The border between banks, wallets, and crypto is fading. A single app could soon manage fiat, tokens, stablecoins, and digital IDs. It isn't crypto vs. banks — it's unifying the experience around users.",
        "default_status": "done",
        "default_url": "https://dev.to/andriibruiaka/fintech-and-web3-are-merging-into-one-ecosystem-2aml",
    },
    {
        "title": "Crypto cashback isn't a gimmick: rebuilding loyalty programs on-chain",
        "pillar": "crypto-ux",
        "outlets": ["Decrypt", "Cointelegraph", "Finextra", "Substack"],
        "keywords": ["BTC cashback", "loyalty programs", "rewards on-chain", "crypto cards", "Kolo"],
        "thesis": "Visa/Mastercard cashback hasn't moved in 20 years. Crypto cashback is the first real reset: programmatic rewards, instant settlement, denominated in an appreciating asset. Kolo case study: 50K active wallets, $250M tx volume in 7 months.",
        "default_status": "todo",
    },

    # ============ Fintech infrastructure & APIs ============
    {
        "title": "How embedded finance reshapes how money moves (B2B2C)",
        "pillar": "infra",
        "outlets": ["Finextra", "TFT", "fintechfilter.com"],
        "keywords": ["embedded finance", "B2B2C", "API-first banking", "NonBank.io"],
        "thesis": "Embedded finance drives B2B transformation. Any business can now offer financial features through APIs. By 2030 most fintech revenue will come from financialized non-bank platforms, not banks. NonBank.io shows the operating model.",
        "default_status": "in progress",
    },
    {
        "title": "Will payment APIs replace traditional banks?",
        "pillar": "infra",
        "outlets": ["Finextra", "Sifted", "dev.to"],
        "keywords": ["payment APIs", "real-time payments", "legacy banking rails", "modern infrastructure"],
        "thesis": "Legacy bank rails are too slow for a real-time economy. Speed and transparency are the new standards. Modern APIs enable instant, borderless payments. Banks become rails, not relationships.",
        "default_status": "todo",
    },
    {
        "title": "Building trust in open banking systems",
        "pillar": "infra",
        "outlets": ["Finextra", "TFT", "Medium", "LinkedIn"],
        "keywords": ["open banking", "API-first", "data trust", "auditability", "OniCore"],
        "thesis": "Open banking only works when users trust data connections. API-first design creates transparency and control. Security and auditability built into the system, not bolted on. OniCore proves trust can be engineered.",
        "default_status": "todo",
    },

    # ============ Compliance / RegTech ============
    {
        "title": "Smart compliance as a fintech's secret weapon",
        "pillar": "compliance",
        "outlets": ["Finextra", "Banking Dive", "fintechfilter.com"],
        "keywords": ["RegTech", "behavioural risk models", "proactive compliance", "AML automation"],
        "thesis": "Behavioural models allow proactive risk detection instead of reactive screening. Compliance can be a value driver, not just a cost. Old compliance tools slow down fintech growth — modern ones unlock it.",
        "default_status": "in progress",
    },
    {
        "title": "Can data outsmart fraud? The new financial security playbook",
        "pillar": "compliance",
        "outlets": ["Finextra", "TFT", "Banking Dive"],
        "keywords": ["AI fraud detection", "real-time risk", "ML in compliance", "risk engines"],
        "thesis": "Fraud detection must evolve with data, not rules. AI predicts fraud before it happens. Risk engines integrated into APIs keep systems safer. Real-time analytics change how fintech fights crime.",
        "default_status": "todo",
    },

    # ============ Fintech + AI ============
    {
        "title": "Predictive fintech platforms will think ahead of you",
        "pillar": "ai",
        "outlets": ["Sifted", "TFT", "fintechfilter.com"],
        "keywords": ["predictive analytics", "proactive UX", "churn reduction", "AI in fintech"],
        "thesis": "Predictive analytics anticipate user needs. Fintech must move from react to proact. Data helps reduce churn and increase customer LTV. The product feels like it's reading your mind because it's reading your patterns.",
        "default_status": "todo",
    },

    # ============ Banking / Wallets / Cross-border ============
    {
        "title": "The rise of non-banks: API-first beats bureaucracy",
        "pillar": "banking",
        "outlets": ["Finextra", "Sifted"],
        "keywords": ["non-banks", "challenger banks", "API-first", "NonBank.io"],
        "thesis": "Banks are losing ground to API-first fintech platforms. NonBank.io shows how technology beats bureaucracy. The bank licence isn't the moat anymore — the operating model is.",
        "default_status": "in progress",
    },
    {
        "title": "Re-inventing digital wallets for Web3",
        "pillar": "banking",
        "outlets": ["Finextra", "TFT"],
        "keywords": ["Web3 wallets", "multi-currency", "non-custodial UX", "fiat-crypto bridge"],
        "thesis": "Web3 wallets give users full control and ownership. Multi-currency design solves cross-border friction. Crypto and fiat can coexist in one system. UX and security remain the main challenges.",
        "default_status": "todo",
    },
    {
        "title": "Why cross-border payments still don't work",
        "pillar": "banking",
        "outlets": ["Finextra", "Sifted"],
        "keywords": ["SWIFT alternative", "stablecoin payments", "remittances", "cross-border"],
        "thesis": "Networks like SWIFT are too slow and costly. Fintech can rebuild payments using APIs and stablecoins. NonBank.io offers a new global model — programmable money rails, not letter-of-credit relationships.",
        "default_status": "todo",
    },

    # ============ Investment & ecosystems ============
    {
        "title": "The smart money is moving into fintech infrastructure",
        "pillar": "investment",
        "outlets": ["Sifted", "TFT"],
        "keywords": ["fintech VC", "B2B infra", "platform investing", "infrastructure moat"],
        "thesis": "The future of fintech investment is in B2B infrastructure. Platforms outlast apps and hype cycles. Product-led growth creates lasting value. Infrastructure is the new competitive moat.",
        "default_status": "todo",
    },
    {
        "title": "Why fintech needs builders, not speculators",
        "pillar": "investment",
        "outlets": ["Sifted", "HackerNoon"],
        "keywords": ["fintech founders", "long-term R&D", "anti-hype", "engineering culture"],
        "thesis": "The industry has been overrun by hype investors. True value comes from founders who build, not flip. Innovation depends on long-term R&D focus.",
        "default_status": "in progress",
    },
    {
        "title": "From code to capital: VCs should think like engineers",
        "pillar": "investment",
        "outlets": ["HackerNoon", "Sifted"],
        "keywords": ["technical founders", "engineering-led VC", "infrastructure investing"],
        "thesis": "Investing in software is investing in infrastructure. Tech-driven founders manage capital smarter. VCs must think like engineers, not bankers. 'Builders funding builders' is the next wave.",
        "default_status": "todo",
    },

    # ============ Tech / Engineering stories ============
    {
        "title": "What we learned building a scalable fintech platform from scratch",
        "pillar": "tech",
        "outlets": ["HackerNoon", "Medium", "Substack"],
        "keywords": ["fintech architecture", "scaling", "security at scale", "OniCore engineering"],
        "thesis": "Scaling fintech is more about systems than size. Security must evolve with scale. Good architecture builds user trust before any UI does.",
        "default_status": "in progress",
    },
    {
        "title": "From prototype to platform: building payment software that lasts",
        "pillar": "tech",
        "outlets": ["HackerNoon", "Medium", "Substack"],
        "keywords": ["MVP to platform", "long-term design", "product engineering", "developer culture"],
        "thesis": "Many fintech MVPs fail because they don't scale. Long-term design beats short-term speed. NonBank.io shows how to build for growth. Developer culture defines product success.",
        "default_status": "todo",
    },
]


# ============================================================
# DASHBOARD — at-a-glance summary above the detailed steps
# ============================================================
EFFORT_LABELS = {1: "5–30 min", 2: "<2 h", 3: "½ day", 4: "multi-day", 5: "ongoing/weeks"}

# Last-known snapshot shown when no live audit has been run yet.
# Update these when reality changes meaningfully.
DASHBOARD_BASELINE = {
    "page1_aligned": 7,           # owned + earned in top 10
    "page1_total": 10,
    "kg_present": False,           # is there a Google Knowledge Graph entity card?
    "negatives": 3,                # negative URLs in top 30
    "llm_owned_cited": 1,          # how many of your owned domains are cited in LLM answers
    "snapshot_label": "snapshot · April 2026",
}


def _resolve_status(task, saved, auto_done):
    """Resolve the effective status for a task.

    Precedence:
    1) If user has truly interacted (proof URL or notes set) → respect saved status.
    2) Else if task defines default_status → use it (overrides any stale saved 'todo').
    3) Else if auto_done → 'done'.
    4) Else fall back to saved status (for legacy interactions without url/notes), then 'todo'.
    """
    has_interaction = bool(saved.get("url")) or bool(saved.get("notes"))
    if has_interaction:
        return saved.get("status", "todo")
    if task.get("default_status"):
        return task["default_status"]
    if auto_done:
        return "done"
    return saved.get("status", "todo")


def render_dashboard(serp_result, pplx_result, openai_result, config):
    """Top-of-page dashboard: 'Now' KPIs + 'Activity' task summary."""

    # ---- Compute Now KPIs from current state ----
    page1_aligned = page1_total = 0
    kg_present = False
    negatives = 0
    audit_run = False
    if serp_result and "error" not in serp_result:
        audit_run = True
        raw = (serp_result.get("organic_results") or [])[:30]
        irr = set(config.get("irrelevant", []))
        organic = [r for r in raw if result_key(r) not in irr]
        page1 = organic[:10]
        for r in page1:
            cls = classify(r, config)
            if cls in ("owned", "earned"):
                page1_aligned += 1
        page1_total = len(page1) or 10
        for r in organic:
            if classify(r, config) == "negative":
                negatives += 1
        kg_present = bool(serp_result.get("knowledge_graph"))

    # Count how many of your owned domains are cited by LLMs (the real GEO signal)
    owned_list = [d for d in (config.get("owned_domains") or []) if d]
    llm_owned_cited = 0
    llm_runs = 0
    for result, parser in [(pplx_result, parse_perplexity), (openai_result, parse_openai)]:
        if not result or "error" in result:
            continue
        llm_runs += 1
        _, citations = parser(result)
        for url in citations:
            ul = (url or "").lower()
            if any(d.lower() in ul for d in owned_list):
                llm_owned_cited += 1

    # ---- Compute Activity from task store ----
    doc = load_tasks()
    states = doc["states"]
    hidden = set(doc["hidden"])
    custom = doc["custom"]

    counts = {"todo": 0, "in progress": 0, "done": 0}
    quick_wins = []  # (effort, priority, label, cat_id)
    serp_urls = ""
    citation_urls = ""
    if serp_result and "error" not in serp_result:
        serp_urls = " ".join((r.get("link") or "").lower() for r in (serp_result.get("organic_results") or []))
    if pplx_result and "error" not in pplx_result:
        _, c = parse_perplexity(pplx_result)
        citation_urls += " " + " ".join((u or "").lower() for u in c)
    if openai_result and "error" not in openai_result:
        _, c = parse_openai(openai_result)
        citation_urls += " " + " ".join((u or "").lower() for u in c)

    for cat in ACTION_CATEGORIES:
        for t in cat["tasks"]:
            if t["label"] in hidden:
                continue
            saved = states.get(t["label"], {})
            auto_done = auto_check_task(t, serp_urls, citation_urls)
            status = _resolve_status(t, saved, auto_done)
            counts[status] += 1
            if status != "done":
                quick_wins.append(
                    (t.get("effort", 3), t.get("priority", 2), t["label"], cat["id"])
                )
        for c in custom.get(cat["id"], []):
            saved = states.get(c["label"], {})
            status = _resolve_status(c, saved, False)
            counts[status] += 1
            if status != "done":
                quick_wins.append(
                    (c.get("effort", 3), c.get("priority", 2), c["label"], cat["id"])
                )

    quick_wins.sort()  # by effort ascending, then priority
    quick_wins = quick_wins[:5]

    total_tasks = sum(counts.values()) or 1
    done_pct = round(100 * counts["done"] / total_tasks)

    # ---- Status helpers ----
    def kpi_color(state):
        return {"good": "var(--vm-green)", "warn": "#8c4500", "bad": "var(--vm-bad)", "muted": "var(--vm-muted)"}[state]

    # If nothing's been run yet, fall back to the saved snapshot
    is_live = audit_run
    if not audit_run:
        page1_aligned = DASHBOARD_BASELINE["page1_aligned"]
        page1_total = DASHBOARD_BASELINE["page1_total"]
        kg_present = DASHBOARD_BASELINE["kg_present"]
        negatives = DASHBOARD_BASELINE["negatives"]
    if llm_runs == 0:
        llm_owned_cited = DASHBOARD_BASELINE["llm_owned_cited"]

    # Page 1 saturation: owned/earned share of top 10
    if page1_aligned >= 7:
        page1_state, page1_text = "good", "strong control"
    elif page1_aligned >= 4:
        page1_state, page1_text = "warn", "moderate"
    else:
        page1_state, page1_text = "bad", "weak"
    page1_caption = "How many of Google's first 10 results you own or earn"

    # Knowledge graph
    kg_state, kg_text = ("good", "present") if kg_present else ("bad", "missing")
    kg_caption = "Google's entity card — biggest single AI-search signal"

    # LLM source citations: how many of your owned domains AI tools cite
    if llm_owned_cited >= 2:
        llm_state, llm_text, llm_sub = "good", str(llm_owned_cited), "your sources are being cited"
    elif llm_owned_cited == 1:
        llm_state, llm_text, llm_sub = "warn", "1", "only one source cited — broaden footprint"
    else:
        llm_state, llm_text, llm_sub = "bad", "0", "AI tools cite outside sources, not yours"

    # Negative results
    if negatives == 0:
        neg_state, neg_text, neg_sub = "good", "0", "clean top 30"
    elif negatives <= 2:
        neg_state, neg_text, neg_sub = "warn", str(negatives), "watch — limited blast"
    else:
        neg_state, neg_text, neg_sub = "bad", str(negatives), "needs displacement work"

    # ---- Render: NOW row ----
    freshness = "live · just refreshed" if is_live else f"{DASHBOARD_BASELINE['snapshot_label']} · run audits to refresh"
    st.markdown(
        f"""
        <div style="display:flex; align-items:baseline; gap:12px; margin: 4px 0 12px;">
          <div style="font-size:11px; letter-spacing:0.14em; text-transform:uppercase; color:var(--vm-muted); font-weight:600;">Now</div>
          <div style="font-size:11px; color:var(--vm-faint);">{escape_html(freshness)}</div>
          <div style="height:1px; background:var(--vm-line); flex:1;"></div>
        </div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-bottom:24px;">
          <div style="border:1px solid var(--vm-line); border-radius:10px; padding:14px 16px; background:#fff;">
            <div style="font-size:10.5px; letter-spacing:0.1em; text-transform:uppercase; color:var(--vm-muted); margin-bottom:4px;">Page 1 control</div>
            <div style="font-size:28px; font-weight:600; color:{kpi_color(page1_state)}; line-height:1; letter-spacing:-0.02em;">
              {page1_aligned}<span style="font-size:16px; color:var(--vm-faint); font-weight:500;">/{page1_total}</span>
            </div>
            <div style="font-size:12px; color:{kpi_color(page1_state)}; margin-top:6px; font-weight:500;">{page1_text}</div>
            <div style="font-size:11px; color:var(--vm-muted); margin-top:4px; line-height:1.35;">{page1_caption}</div>
          </div>
          <div style="border:1px solid var(--vm-line); border-radius:10px; padding:14px 16px; background:#fff;">
            <div style="font-size:10.5px; letter-spacing:0.1em; text-transform:uppercase; color:var(--vm-muted); margin-bottom:4px;">Knowledge graph</div>
            <div style="font-size:24px; font-weight:600; color:{kpi_color(kg_state)}; line-height:1.05; letter-spacing:-0.02em;">{kg_text}</div>
            <div style="font-size:11px; color:var(--vm-muted); margin-top:6px; line-height:1.35;">{kg_caption}</div>
          </div>
          <div style="border:1px solid var(--vm-line); border-radius:10px; padding:14px 16px; background:#fff;">
            <div style="font-size:10.5px; letter-spacing:0.1em; text-transform:uppercase; color:var(--vm-muted); margin-bottom:4px;">AI source citations</div>
            <div style="font-size:28px; font-weight:600; color:{kpi_color(llm_state)}; line-height:1; letter-spacing:-0.02em;">{llm_text}</div>
            <div style="font-size:12px; color:{kpi_color(llm_state)}; margin-top:6px; font-weight:500;">{llm_sub}</div>
            <div style="font-size:11px; color:var(--vm-muted); margin-top:4px; line-height:1.35;">Owned URLs cited by ChatGPT / Perplexity when explaining who you are</div>
          </div>
          <div style="border:1px solid var(--vm-line); border-radius:10px; padding:14px 16px; background:#fff;">
            <div style="font-size:10.5px; letter-spacing:0.1em; text-transform:uppercase; color:var(--vm-muted); margin-bottom:4px;">Negative results</div>
            <div style="font-size:28px; font-weight:600; color:{kpi_color(neg_state)}; line-height:1; letter-spacing:-0.02em;">{neg_text}</div>
            <div style="font-size:12px; color:{kpi_color(neg_state)}; margin-top:6px; font-weight:500;">{neg_sub}</div>
            <div style="font-size:11px; color:var(--vm-muted); margin-top:4px; line-height:1.35;">Hit pieces or unflattering pages in top 30</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Render: ACTIVITY row ----
    quick_html = ""
    if quick_wins:
        rows = []
        for eff, prio, label, cat_id in quick_wins:
            rows.append(
                f'<a href="#cat-{cat_id}" style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid var(--vm-line); text-decoration:none; color:var(--vm-ink);">'
                f'<span style="font-size:13px; font-weight:500;">{escape_html(label)}</span>'
                f'<span style="font-size:11px; color:var(--vm-muted); margin-left:12px; white-space:nowrap;">{EFFORT_LABELS[eff]} · P{prio}</span>'
                f'</a>'
            )
        quick_html = "".join(rows)
    else:
        quick_html = '<div style="font-size:13px; color:var(--vm-muted); padding:8px 0;">All open tasks complete 🎉</div>'

    st.markdown(
        f"""
        <div style="display:flex; align-items:baseline; gap:12px; margin: 4px 0 12px;">
          <div style="font-size:11px; letter-spacing:0.14em; text-transform:uppercase; color:var(--vm-muted); font-weight:600;">Activity</div>
          <div style="height:1px; background:var(--vm-line); flex:1;"></div>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 2fr; gap:10px; margin-bottom:32px;">
          <div style="border:1px solid var(--vm-line); border-radius:10px; padding:16px 18px; background:#fff;">
            <div style="font-size:10.5px; letter-spacing:0.1em; text-transform:uppercase; color:var(--vm-muted); margin-bottom:8px;">Action plan progress</div>
            <div style="font-size:36px; font-weight:600; color:var(--vm-blue); line-height:1; letter-spacing:-0.025em;">
              {done_pct}<span style="font-size:18px; color:var(--vm-faint); font-weight:500;">%</span>
            </div>
            <div style="display:flex; gap:14px; margin-top:14px; font-size:12px;">
              <div><span style="font-weight:600; color:var(--vm-ink);">{counts['done']}</span> <span style="color:var(--vm-muted);">done</span></div>
              <div><span style="font-weight:600; color:var(--vm-ink);">{counts['in progress']}</span> <span style="color:var(--vm-muted);">doing</span></div>
              <div><span style="font-weight:600; color:var(--vm-ink);">{counts['todo']}</span> <span style="color:var(--vm-muted);">todo</span></div>
            </div>
          </div>
          <div style="border:1px solid var(--vm-line); border-radius:10px; padding:16px 18px; background:#fff;">
            <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
              <div style="font-size:10.5px; letter-spacing:0.1em; text-transform:uppercase; color:var(--vm-muted); font-weight:600;">Quickest wins</div>
              <div style="font-size:11px; color:var(--vm-faint);">sorted by effort ↑</div>
            </div>
            {quick_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Real Streamlit buttons for navigation (anchor links can't switch views)
    def _switch_view(v):
        st.session_state.view_radio = v

    nav_cols = st.columns([1, 1, 1, 1, 3])
    with nav_cols[0]:
        st.button(
            "→ Action plan",
            key="dash_to_actions",
            use_container_width=True,
            on_click=_switch_view,
            args=("03 · Action plan",),
        )
    with nav_cols[1]:
        st.button(
            "→ Google search",
            key="dash_to_google",
            use_container_width=True,
            on_click=_switch_view,
            args=("01 · Google search",),
        )
    with nav_cols[2]:
        st.button(
            "→ LLM probes",
            key="dash_to_llm",
            use_container_width=True,
            on_click=_switch_view,
            args=("02 · LLM visibility",),
        )
    with nav_cols[3]:
        st.button(
            "→ Content plan",
            key="dash_to_content",
            use_container_width=True,
            on_click=_switch_view,
            args=("04 · Content plan",),
        )


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
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not has_serp:
        st.warning("Add SerpAPI key in Settings to begin.")
        return

    serp_result = st.session_state.results.get(primary_task["id"]) if primary_task else None
    pplx_result = st.session_state.perplexity_result
    openai_result = st.session_state.openai_result

    view = st.session_state.get("view_radio", "Overview")

    # ============================================================
    # OVERVIEW VIEW — dashboard only, then return
    # ============================================================
    if view == "Overview":
        render_dashboard(
            serp_result=serp_result,
            pplx_result=pplx_result,
            openai_result=openai_result,
            config=st.session_state.config,
        )
        return

    # ============================================================
    # Dispatch to the correct step renderer.
    # Each step is implemented as a standalone function (defined below
    # render_strategy) so navigation is a clean view-switch.
    # ============================================================
    if view == "01 · Google search":
        render_step1(primary_task, serp_result, st.session_state.config)
        return
    if view == "02 · LLM visibility":
        render_step2(pplx_result, openai_result, has_pplx, st.session_state.config)
        return
    if view == "04 · Content plan":
        render_content_plan(st.session_state.config)
        return
    # Default: action plan (view "03 · Action plan")
    render_step3(serp_result, pplx_result, openai_result, st.session_state.config)


def render_step1(primary_task, serp_result, config):
    """Step 1 — Google search SERP audit."""
    st.markdown(
        '<a id="step-1-google"></a>'
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

    raw_organic = (serp_result.get("organic_results") or [])[:30]
    irrelevant_set = set(st.session_state.config.get("irrelevant", []))
    # Filter out results the user marked as not-relevant (wrong person, etc.)
    organic = [r for r in raw_organic if result_key(r) not in irrelevant_set]
    hidden_count = len(raw_organic) - len(organic)

    counts = {"owned": 0, "earned": 0, "neutral": 0, "negative": 0}
    for r in organic:
        counts[classify(r, st.session_state.config)] += 1
    aligned = counts["owned"] + counts["earned"]
    total = len(organic) or 1
    kg_present = bool(serp_result.get("knowledge_graph"))

    # Page 1 specifically (first 10 of the visible results) — that's what most users see
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

    expander_title = f"All results · {len(organic)} visible"
    if hidden_count:
        expander_title += f" ({hidden_count} hidden as not relevant)"
    expander_title += " across 3 pages"

    with st.expander(expander_title, expanded=True):
        for i, r in enumerate(organic):
            cls = classify(r, st.session_state.config)
            title = escape_html(r.get("title") or "Untitled")
            link = r.get("link") or ""
            displayed = escape_html(link or r.get("displayed_link") or "")
            full_snippet = r.get("snippet") or ""
            snippet = escape_html(full_snippet)

            row_cols = st.columns([0.5, 7, 1.2, 1], vertical_alignment="center")
            with row_cols[0]:
                st.markdown(
                    f'<div style="font-family: \'Fraunces\', serif; font-size: 28px; font-weight: 500; color: var(--muted); padding-top: 8px;">{i+1:02d}</div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                st.markdown(
                    f"""
                    <div style="padding: 6px 0;">
                      <div style="font-size: 18px; font-weight: 600; line-height: 1.3; margin-bottom: 6px;">
                        <a href="{escape_html(link)}" target="_blank" rel="noopener" style="color: var(--text); text-decoration: none;">{title}</a>
                      </div>
                      <div style="font-size: 14px; margin-bottom: 8px;">
                        <a href="{escape_html(link)}" target="_blank" rel="noopener" style="color: var(--info); text-decoration: none; word-break: break-all;">{displayed}</a>
                      </div>
                      {f'<div style="font-size: 16px; color: var(--text-dim); line-height: 1.55;">{snippet}</div>' if snippet else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with row_cols[2]:
                st.markdown(
                    f'<div class="tag {cls}">{cls}</div>',
                    unsafe_allow_html=True,
                )
            with row_cols[3]:
                if st.button("✕ hide", key=f"hide_{i}_{result_key(r)[:60]}", help="Mark as not relevant (wrong person, etc.) — hides from breakdown and saturation count"):
                    irr = list(st.session_state.config.get("irrelevant", []))
                    rk = result_key(r)
                    if rk not in irr:
                        irr.append(rk)
                    st.session_state.config["irrelevant"] = irr
                    save_config(st.session_state.config)
                    st.rerun()

    if hidden_count:
        with st.expander(f"Hidden as not relevant ({hidden_count}) — restore"):
            irr = list(st.session_state.config.get("irrelevant", []))
            for r in raw_organic:
                rk = result_key(r)
                if rk not in irrelevant_set:
                    continue
                cols = st.columns([7, 1])
                with cols[0]:
                    title = r.get("title") or "Untitled"
                    link = r.get("link") or ""
                    st.markdown(f"**{title}**  \n[{link}]({link})")
                with cols[1]:
                    if st.button("Restore", key=f"restore_irr_{rk[:60]}"):
                        irr = [k for k in irr if k != rk]
                        st.session_state.config["irrelevant"] = irr
                        save_config(st.session_state.config)
                        st.rerun()


def render_step2(pplx_result, openai_result, has_pplx, config):
    """Step 2 — LLM visibility (Perplexity + ChatGPT probes)."""
    st.markdown(
        '<a id="step-2-llm"></a>'
        '<div class="step-block first">'
        '<div class="step-header"><div class="step-num">02</div><div class="step-title">LLM visibility</div></div>'
        '<div class="step-subtitle">Does the AI search layer know who this is? What does it say, and which sources does it cite?</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    has_openai = bool(st.session_state.config.get("openai_key"))
    openai_result = st.session_state.openai_result

    btn_cols = st.columns(2)
    with btn_cols[0]:
        if has_pplx:
            if st.button("▶ Refresh Perplexity probe", use_container_width=True):
                run_perplexity()
                st.rerun()
        else:
            st.caption("Add Perplexity key in Settings to enable.")
    with btn_cols[1]:
        if has_openai:
            if st.button("▶ Refresh ChatGPT probe", use_container_width=True):
                run_openai()
                st.rerun()
        else:
            st.caption("Add OpenAI key in Settings to enable.")

    owned = st.session_state.config.get("owned_domains", [])

    pplx_mentioned = False
    pplx_owned_cited = 0
    pplx_answer = ""
    pplx_citations = []
    if pplx_result and "error" not in pplx_result:
        pplx_answer, pplx_citations = parse_perplexity(pplx_result)
        pplx_mentioned = "bruiaka" in pplx_answer.lower()
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

    openai_mentioned = False
    openai_owned_cited = 0
    openai_answer = ""
    openai_citations = []
    if openai_result and "error" not in openai_result:
        openai_answer, openai_citations = parse_openai(openai_result)
        openai_mentioned = "bruiaka" in openai_answer.lower()
        for url in openai_citations:
            ul = url.lower()
            if any(d.lower() in ul for d in owned if d):
                openai_owned_cited += 1

    if openai_result is None:
        openai_status = ("not run", "var(--muted)")
    elif "error" in (openai_result or {}):
        openai_status = ("error", "var(--bad)")
    elif openai_mentioned:
        openai_status = (
            f"mentioned · {openai_owned_cited} owned cited",
            "var(--good)" if openai_owned_cited else "var(--warn)",
        )
    else:
        openai_status = ("not mentioned", "var(--bad)")

    st.markdown(
        f"""
        <div class="saturation-card" style="grid-template-columns: 1fr 1fr; gap: 32px;">
          <div>
            <div class="saturation-label">Perplexity (sonar)</div>
            <div class="saturation-number" style="font-size: 36px; color: {pplx_status[1]};">{pplx_status[0]}</div>
            <div class="saturation-label">probe: "Who is Andrii Bruiaka?"</div>
          </div>
          <div>
            <div class="saturation-label">ChatGPT (gpt-4o-search-preview)</div>
            <div class="saturation-number" style="font-size: 36px; color: {openai_status[1]};">{openai_status[0]}</div>
            <div class="saturation-label">probe: "Who is Andrii Bruiaka?"</div>
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
                        d.lower() in url.lower() for d in owned if d
                    )
                    tag = " · **OWNED**" if is_owned else ""
                    st.markdown(f"{i}. [{url}]({url}){tag}")
    elif pplx_result and "error" in pplx_result:
        st.error(f"Perplexity: {pplx_result['error']}")

    if openai_result and "error" not in openai_result:
        with st.expander(f"What ChatGPT says · {len(openai_citations)} citations", expanded=True):
            st.markdown(
                f'<div class="kg-card"><div class="kg-desc">{escape_html(openai_answer)}</div></div>',
                unsafe_allow_html=True,
            )
            if openai_citations:
                st.markdown("**Citations**")
                for i, url in enumerate(openai_citations, 1):
                    is_owned = any(
                        d.lower() in url.lower() for d in owned if d
                    )
                    tag = " · **OWNED**" if is_owned else ""
                    st.markdown(f"{i}. [{url}]({url}){tag}")
    elif openai_result and "error" in openai_result:
        st.error(f"ChatGPT: {openai_result['error']}")


def render_content_plan(config):
    """Step 04 — Editorial / content calendar."""
    st.markdown(
        '<a id="step-4-content"></a>'
        '<div class="step-block first">'
        '<div class="step-header"><div class="step-num">04</div><div class="step-title">Content plan</div></div>'
        '<div class="step-subtitle">Editorial pipeline grouped by brand pillar. Each item is a concrete piece — title, target outlets, SEO keywords, and a 1-line thesis. Mark status, paste the published URL when it lands.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    doc = load_tasks()
    states = doc["states"]
    hidden = set(doc["hidden"])
    custom = doc["custom"]
    changed = False

    status_options = ["todo", "in progress", "done"]
    status_color = {"todo": "var(--vm-muted)", "in progress": "#8c4500", "done": "var(--vm-green)"}
    status_order = {"todo": 0, "in progress": 1, "done": 2}

    pillar_options = ["All pillars"] + [p["title"] for p in CONTENT_PILLARS]
    selected_pillar = st.radio(
        "Filter by pillar",
        pillar_options,
        horizontal=True,
        key="content_pillar_filter",
        label_visibility="collapsed",
    )

    sort_choice = st.radio(
        "Order by",
        ["Status (todo first)", "Pillar"],
        horizontal=True,
        key="content_sort_mode",
        label_visibility="collapsed",
    )

    counts = {"todo": 0, "in progress": 0, "done": 0}

    for pillar in CONTENT_PILLARS:
        if selected_pillar != "All pillars" and selected_pillar != pillar["title"]:
            continue

        items = [c for c in CONTENT_PLAN if c["pillar"] == pillar["id"] and c["title"] not in hidden]
        custom_pillar = custom.get(f"content::{pillar['id']}", [])
        items.extend([{**c, "_custom": True} for c in custom_pillar])

        if not items:
            continue

        # Resolve status for each item
        for it in items:
            saved = states.get(it["title"], {})
            it["_status"] = _resolve_status(it, saved, False)
            it["_url"] = saved.get("url", "") or it.get("default_url", "")
            it["_notes"] = saved.get("notes", "")
            counts[it["_status"]] += 1

        if sort_choice.startswith("Status"):
            items.sort(key=lambda i: status_order[i["_status"]])

        # Render pillar header
        st.markdown(
            f'<div class="category-header"><div class="category-title">{escape_html(pillar["title"])}</div></div>',
            unsafe_allow_html=True,
        )

        # Add-content form (above the list)
        with st.expander(f"+ Add piece to '{pillar['title']}'"):
            with st.form(key=f"add_content_{pillar['id']}", clear_on_submit=True):
                new_title = st.text_input("Title *", key=f"ct_title_{pillar['id']}")
                new_outlets = st.text_input("Target outlets (comma-separated)", key=f"ct_outlets_{pillar['id']}")
                new_keywords = st.text_input("Keywords (comma-separated)", key=f"ct_kw_{pillar['id']}")
                new_thesis = st.text_area("Thesis (1-2 lines)", key=f"ct_thesis_{pillar['id']}", height=70)
                if st.form_submit_button("Add piece"):
                    if new_title.strip():
                        custom.setdefault(f"content::{pillar['id']}", []).append({
                            "title": new_title.strip(),
                            "pillar": pillar["id"],
                            "outlets": [o.strip() for o in new_outlets.split(",") if o.strip()],
                            "keywords": [k.strip() for k in new_keywords.split(",") if k.strip()],
                            "thesis": new_thesis.strip(),
                        })
                        save_tasks({"states": states, "hidden": list(hidden), "custom": custom})
                        st.rerun()

        for it in items:
            with st.container(border=True):
                head = st.columns([6, 2, 1])
                with head[0]:
                    st.markdown(f"**{escape_html(it['title'])}**")
                with head[1]:
                    new_status = st.selectbox(
                        "status",
                        status_options,
                        index=status_options.index(it["_status"]),
                        key=f"cstatus_{it['title']}",
                        label_visibility="collapsed",
                    )
                with head[2]:
                    if st.button("✕", key=f"cdel_{it['title']}", help="Hide this piece"):
                        if it.get("_custom"):
                            custom[f"content::{pillar['id']}"] = [
                                c for c in custom.get(f"content::{pillar['id']}", []) if c["title"] != it["title"]
                            ]
                        else:
                            hidden.add(it["title"])
                        states.pop(it["title"], None)
                        save_tasks({"states": states, "hidden": list(hidden), "custom": custom})
                        st.rerun()

                outlets = " · ".join(it.get("outlets", []))
                if outlets:
                    st.markdown(
                        f'<div style="font-size:12px; color:var(--vm-muted); margin-top:2px;">↳ Outlets: <span style="color:var(--vm-ink);">{escape_html(outlets)}</span></div>',
                        unsafe_allow_html=True,
                    )
                kws = ", ".join(it.get("keywords", []))
                if kws:
                    st.markdown(
                        f'<div style="font-size:12px; color:var(--vm-muted); margin-top:2px;">↳ Keywords: <span style="color:var(--vm-ink);">{escape_html(kws)}</span></div>',
                        unsafe_allow_html=True,
                    )
                if it.get("thesis"):
                    st.caption(f"**Thesis:** {it['thesis']}")

                link_cols = st.columns([3, 2])
                with link_cols[0]:
                    new_url = st.text_input(
                        "Published URL",
                        value=it["_url"],
                        placeholder="https://... (paste once published)",
                        key=f"curl_{it['title']}",
                        label_visibility="collapsed",
                    )
                with link_cols[1]:
                    new_notes = st.text_input(
                        "Notes",
                        value=it["_notes"],
                        placeholder="notes",
                        key=f"cnotes_{it['title']}",
                        label_visibility="collapsed",
                    )

                if (
                    new_status != it["_status"]
                    or new_url != it["_url"]
                    or new_notes != it["_notes"]
                ):
                    states[it["title"]] = {
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

    st.markdown(
        f'<div class="section-title">Content pipeline <small>{counts["todo"]} todo · {counts["in progress"]} drafting · {counts["done"]} published</small></div>',
        unsafe_allow_html=True,
    )

    if changed:
        save_tasks({"states": states, "hidden": list(hidden), "custom": custom})
        st.rerun()


def render_step3(serp_result, pplx_result, openai_result, config):
    """Step 3 — Action plan (tasks with status, effort, sort)."""
    # Compute citation/serp blobs for auto-check
    organic = []
    if serp_result and "error" not in serp_result:
        raw = (serp_result.get("organic_results") or [])[:30]
        irr = set(config.get("irrelevant", []))
        organic = [r for r in raw if result_key(r) not in irr]

    pplx_citations = []
    openai_citations = []
    if pplx_result and "error" not in pplx_result:
        _, pplx_citations = parse_perplexity(pplx_result)
    if openai_result and "error" not in openai_result:
        _, openai_citations = parse_openai(openai_result)
    all_citations = pplx_citations + openai_citations

    st.markdown(
        '<a id="step-3-action"></a>'
        '<div class="step-block first">'
        '<div class="step-header"><div class="step-num">03</div><div class="step-title">Action plan</div></div>'
        '<div class="step-subtitle">Concrete tasks grouped by category. Mark status, paste the proof URL when each is published. Auto-detection flags items already showing on page 1 or in Perplexity citations.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    serp_urls = " ".join((r.get("link") or "").lower() for r in organic)
    citation_urls = " ".join((c or "").lower() for c in all_citations)

    doc = load_tasks()
    states = doc["states"]
    hidden = set(doc["hidden"])
    custom = doc["custom"]

    status_options = ["todo", "in progress", "done"]
    priority_label = {1: "P1", 2: "P2", 3: "P3"}
    priority_color = {1: "var(--bad)", 2: "var(--warn)", 3: "var(--muted)"}
    status_order = {"todo": 0, "in progress": 1, "done": 2}
    effort_label = {1: "5–30 min", 2: "<2 h", 3: "½ day", 4: "multi-day", 5: "ongoing/weeks"}
    effort_dot = {1: "●", 2: "●●", 3: "●●●", 4: "●●●●", 5: "●●●●●"}

    # Sub-navigation: filter by category
    cat_options = ["All categories"] + [c["title"] for c in ACTION_CATEGORIES]
    selected_cat = st.radio(
        "Filter by category",
        cat_options,
        horizontal=True,
        key="action_cat_filter",
        label_visibility="collapsed",
    )

    sort_mode = st.radio(
        "Order tasks by",
        ["Status + priority (default)", "Quickest wins first (effort ↑)"],
        horizontal=True,
        key="action_sort_mode",
        label_visibility="collapsed",
    )

    total_counts = {"todo": 0, "in progress": 0, "done": 0}
    changed = False

    def render_task(it, cat_id, is_custom):
        nonlocal changed
        label = it["label"]
        eff = it.get("effort", 3)
        with st.container(border=True):
            head_cols = st.columns([1, 4, 2, 1])
            with head_cols[0]:
                st.markdown(
                    f'<div style="font-size:13px; color:{priority_color[it["priority"]]}; text-transform:uppercase; letter-spacing:0.12em; font-weight:600; padding-top:6px;">{priority_label[it["priority"]]}</div>'
                    f'<div style="font-size:11px; color:var(--muted); letter-spacing:0.08em; padding-top:2px;" title="Effort: {effort_label.get(eff, "?")}">{effort_dot.get(eff, "●●●")} {effort_label.get(eff, "")}</div>',
                    unsafe_allow_html=True,
                )
            with head_cols[1]:
                st.markdown(f"**{escape_html(label)}**")
            with head_cols[2]:
                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(it["status"]),
                    key=f"status_{cat_id}_{label}",
                    label_visibility="collapsed",
                )
            with head_cols[3]:
                if st.button("✕", key=f"del_{cat_id}_{label}", help="Remove this task"):
                    if is_custom:
                        custom[cat_id] = [
                            c for c in custom.get(cat_id, []) if c["label"] != label
                        ]
                    else:
                        if label not in hidden:
                            hidden.add(label)
                    states.pop(label, None)
                    save_tasks({"states": states, "hidden": list(hidden), "custom": custom})
                    st.rerun()

            if it.get("topic"):
                st.markdown(
                    f'<div class="task-topic">↳ Topic: {escape_html(it["topic"])}</div>',
                    unsafe_allow_html=True,
                )
            if it.get("why"):
                st.caption(f"**Why:** {it['why']}")
            if it.get("action"):
                st.caption(f"**Action:** {it['action']}")

            link_cols = st.columns([3, 2])
            with link_cols[0]:
                new_url = st.text_input(
                    "Proof URL",
                    value=it["url"],
                    placeholder="https://... (the published article, profile, etc.)",
                    key=f"url_{cat_id}_{label}",
                    label_visibility="collapsed",
                )
            with link_cols[1]:
                new_notes = st.text_input(
                    "Notes",
                    value=it["notes"],
                    placeholder="notes (optional)",
                    key=f"notes_{cat_id}_{label}",
                    label_visibility="collapsed",
                )

            if (
                new_status != it["status"]
                or new_url != it["url"]
                or new_notes != it["notes"]
            ):
                states[label] = {
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

            if it.get("auto_present") and new_status != "done":
                st.caption("⚐ Auto-detected on page 1 / Perplexity citations — consider marking as done.")

    for category in ACTION_CATEGORIES:
        cat_id = category["id"]

        # Skip categories that don't match the sub-nav filter
        if selected_cat != "All categories" and selected_cat != category["title"]:
            continue

        st.markdown(
            f"""
            <a id="cat-{escape_html(cat_id)}"></a>
            <div class="category-header">
              <div class="category-title">{escape_html(category['title'])}</div>
              <div class="category-subtitle">{escape_html(category['subtitle'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Build items: built-in (not hidden) + custom
        items = []
        for t in category["tasks"]:
            if t["label"] in hidden:
                continue
            saved = states.get(t["label"], {})
            auto_done = auto_check_task(t, serp_urls, citation_urls)
            items.append({
                **t,
                "status": _resolve_status(t, saved, auto_done),
                "url": saved.get("url", ""),
                "notes": saved.get("notes", ""),
                "auto_present": auto_done,
                "_custom": False,
            })
        for c in custom.get(cat_id, []):
            saved = states.get(c["label"], {})
            items.append({
                **c,
                "status": _resolve_status(c, saved, False),
                "url": saved.get("url", ""),
                "notes": saved.get("notes", ""),
                "auto_present": False,
                "_custom": True,
            })

        if sort_mode.startswith("Quickest"):
            # Effort-first so quick wins visibly float to top regardless of status
            items.sort(key=lambda i: (i.get("effort", 3), status_order[i["status"]], i["priority"]))
        else:
            items.sort(key=lambda i: (status_order[i["status"]], i["priority"], i.get("effort", 3)))

        # + Add task form (rendered ABOVE the task list per user preference)
        with st.expander(f"+ Add task to '{category['title']}'"):
            with st.form(key=f"add_form_{cat_id}", clear_on_submit=True):
                new_label = st.text_input("Task name *", key=f"new_label_{cat_id}")
                col_p, col_e, col_t = st.columns([1, 1, 3])
                with col_p:
                    new_priority = st.selectbox("Priority", [1, 2, 3], key=f"new_prio_{cat_id}")
                with col_e:
                    new_effort = st.selectbox(
                        "Effort",
                        [1, 2, 3, 4, 5],
                        index=2,
                        format_func=lambda v: f"{v} · {effort_label[v]}",
                        key=f"new_effort_{cat_id}",
                    )
                with col_t:
                    new_topic = st.text_input("Topic / angle (optional)", key=f"new_topic_{cat_id}")
                new_why = st.text_area("Why it matters (optional)", key=f"new_why_{cat_id}", height=70)
                new_action = st.text_area("Concrete action (optional)", key=f"new_action_{cat_id}", height=70)
                submitted = st.form_submit_button("Add task")
                if submitted and new_label.strip():
                    custom.setdefault(cat_id, []).append({
                        "label": new_label.strip(),
                        "priority": new_priority,
                        "effort": new_effort,
                        "topic": new_topic.strip(),
                        "why": new_why.strip(),
                        "action": new_action.strip(),
                        "domains": [],
                    })
                    save_tasks({"states": states, "hidden": list(hidden), "custom": custom})
                    st.rerun()

        for it in items:
            total_counts[it["status"]] += 1
            render_task(it, cat_id, it["_custom"])

    st.markdown(
        f'<div class="section-title">Plan summary <small>{total_counts["todo"]} todo · {total_counts["in progress"]} doing · {total_counts["done"]} done</small></div>',
        unsafe_allow_html=True,
    )

    # Restore hidden tasks (in case user wants something back)
    if hidden:
        with st.expander(f"Hidden built-in tasks ({len(hidden)}) — restore"):
            for label in sorted(hidden):
                cols = st.columns([5, 1])
                with cols[0]:
                    st.write(label)
                with cols[1]:
                    if st.button("Restore", key=f"restore_{label}"):
                        hidden.discard(label)
                        save_tasks({"states": states, "hidden": list(hidden), "custom": custom})
                        st.rerun()

    if changed:
        save_tasks({"states": states, "hidden": list(hidden), "custom": custom})
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
render_strategy()
