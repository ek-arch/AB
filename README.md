# Visibility Monitor — Andrii Bruiaka

A SerpAPI-powered Streamlit dashboard for monitoring SERP saturation and AI visibility for the personal brand "Andrii Bruiaka".

## What it does

- Runs 14 pre-configured SerpAPI queries (core identity, brand surface, companies, topic authority) on Google + Bing
- Classifies each result as **owned**, **earned**, **neutral**, or **negative** against your domain lists
- Computes a saturation score per query — what % of the top results you control
- Detects whether Google has a Knowledge Graph entry for the entity (key signal for AI search optimization)
- Saves snapshots over time so you can track drift
- Lets you tag negative results manually for ongoing reputation tracking

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. On first run, click **Settings** in the sidebar and paste your SerpAPI key. It's saved to `config.json` in the project folder.

## Deploy free to Streamlit Community Cloud

1. Push this folder to a public or private GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub
3. New app → pick the repo → main file `app.py`
4. In **Advanced settings → Secrets**, add:
   ```
   serpapi_key = "your_serpapi_key_here"
   ```
5. Deploy. The key loads from `st.secrets` automatically; you don't need to enter it in the UI.

## Files

- `app.py` — main Streamlit application
- `requirements.txt` — Python dependencies (streamlit, requests)
- `.streamlit/config.toml` — light editorial theme settings
- `config.json` — created on first save; stores API key and domain lists locally
- `snapshots.json` — created on first audit run; stores last 10 snapshots per task

> **Don't commit `config.json`** to a public repo — it contains your API key. Add it to `.gitignore`.

## SerpAPI usage

- Free tier: 100 searches/month → ~7 full audits (14 queries each)
- Developer plan ($75/mo): 5,000 searches → run weekly with room to spare
- Each task in the audit = 1 SerpAPI call

## Customization

Everything is editable in **Settings**:
- **SerpAPI key** — change at any time
- **Owned domains** — bruiaka.com, social profiles, company sites. Substring match against the result URL.
- **Earned domains** — target outlets (Finextra, The Fintech Times, Banking Dive, etc.)

To add or remove tasks, edit the `TASKS` list near the top of `app.py`.

## Roadmap suggestions (not built yet)

- Diff view between snapshots (which results moved up/down)
- Export to CSV/JSON
- Slack/email alerts on saturation drops
- Cross-engine comparison view (same query side-by-side on Google vs Bing vs DuckDuckGo)
- Direct querying of ChatGPT/Perplexity/Gemini APIs for entity Q&A drift
