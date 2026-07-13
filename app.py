"""
Digital Junior Analyst — Streamlit Application
Premium dark-mode financial intelligence interface.
"""
import os
import time
import json
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Digital Junior Analyst",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# THEME STATE
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "report_result" not in st.session_state:
    st.session_state.report_result = None
if "store_ready" not in st.session_state:
    st.session_state.store_ready = False
if "uploaded_docs_info" not in st.session_state:
    st.session_state.uploaded_docs_info = []
if "demo_loaded" not in st.session_state:
    st.session_state.demo_loaded = False

IS_DARK = st.session_state.theme == "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# ---------------------------------------------------------------------------
# DESIGN SYSTEM CSS  (Zinc/shadcn inspired — matching existing project)
# ---------------------------------------------------------------------------
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {{
    --bg:          {"#09090b" if IS_DARK else "#ffffff"};
    --bg-subtle:   {"#0c0c0f" if IS_DARK else "#f9fafb"};
    --card:        {"#0f0f12" if IS_DARK else "#ffffff"};
    --card-hover:  {"#17171c" if IS_DARK else "#f4f4f5"};
    --border:      {"#1e1e24" if IS_DARK else "#e4e4e7"};
    --border-sub:  {"#16161a" if IS_DARK else "#f0f0f2"};
    --text:        {"#fafafa" if IS_DARK else "#09090b"};
    --text-muted:  #71717a;
    --text-dim:    {"#52525b" if IS_DARK else "#a1a1aa"};
    --accent:      #2563eb;
    --accent-glow: {"rgba(37,99,235,0.15)" if IS_DARK else "rgba(37,99,235,0.08)"};
    --green:       {"#22c55e" if IS_DARK else "#16a34a"};
    --green-bg:    {"rgba(34,197,94,0.10)" if IS_DARK else "rgba(22,163,74,0.07)"};
    --amber:       {"#f59e0b" if IS_DARK else "#d97706"};
    --amber-bg:    {"rgba(245,158,11,0.10)" if IS_DARK else "rgba(217,119,6,0.07)"};
    --red:         {"#ef4444" if IS_DARK else "#dc2626"};
    --red-bg:      {"rgba(239,68,68,0.10)" if IS_DARK else "rgba(220,38,38,0.07)"};
    --purple:      {"#a78bfa" if IS_DARK else "#7c3aed"};
    --purple-bg:   {"rgba(167,139,250,0.10)" if IS_DARK else "rgba(124,58,237,0.07)"};
    --shadow:      {"none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.06)"};
    --radius:      10px;
}}

/* ---- hide streamlit chrome ---- */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton {{
    display: none !important;
}}

/* ---- global ---- */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
.main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}
.block-container {{
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1380px !important;
}}
[data-testid="stHorizontalBlock"] {{ gap: 1.25rem !important; }}

/* ---- sidebar ---- */
[data-testid="stSidebar"] {{
    background: var(--bg-subtle) !important;
    border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] .block-container {{
    padding: 1.5rem 1.25rem 2rem !important;
}}

/* ---- tabs ---- */
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    border: 1px solid transparent !important;
    border-radius: 7px !important;
    transition: all 0.2s ease !important;
}}
button[data-baseweb="tab"]:hover {{ color: var(--text) !important; background: var(--card-hover) !important; }}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--text) !important;
    background: var(--card) !important;
    border-color: var(--border) !important;
}}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{ display: none !important; }}
[data-baseweb="tab-list"] {{
    gap: 6px !important;
    background: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    margin-bottom: 1.5rem !important;
}}

/* ---- cards ---- */
.card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}}
.card-accent {{
    border-left: 3px solid var(--accent);
    background: var(--accent-glow);
}}
.card-green  {{ border-left: 3px solid var(--green); background: var(--green-bg); }}
.card-amber  {{ border-left: 3px solid var(--amber); background: var(--amber-bg); }}
.card-red    {{ border-left: 3px solid var(--red);   background: var(--red-bg); }}
.card-purple {{ border-left: 3px solid var(--purple); background: var(--purple-bg); }}

/* ---- kpi ---- */
.kpi-label {{
    font-size: 0.72rem; font-weight: 500; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.05em;
}}
.kpi-value {{
    font-size: 2rem; font-weight: 700; color: var(--text);
    letter-spacing: -0.04em; margin: 0.2rem 0 0.3rem;
}}
.kpi-sub {{ font-size: 0.75rem; color: var(--text-dim); }}

/* ---- badges ---- */
.badge {{
    display: inline-block; padding: 2px 9px; border-radius: 6px;
    font-size: 0.70rem; font-weight: 600;
}}
.badge-critical {{ color: var(--red);    background: var(--red-bg); }}
.badge-high     {{ color: var(--amber);  background: var(--amber-bg); }}
.badge-medium   {{ color: var(--accent); background: var(--accent-glow); }}
.badge-low      {{ color: var(--green);  background: var(--green-bg); }}
.badge-purple   {{ color: var(--purple); background: var(--purple-bg); }}

/* ---- report output ---- */
.report-output {{
    background: var(--bg-subtle);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.75rem 2rem;
    font-size: 0.9rem;
    line-height: 1.75;
    color: var(--text);
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
    max-height: 70vh;
    overflow-y: auto;
}}

/* ---- source citation card ---- */
.source-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 0.8rem;
}}
.source-title {{
    font-weight: 600; color: var(--text); font-size: 0.82rem; margin-bottom: 0.35rem;
}}
.source-chunk {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.73rem;
    color: var(--text-muted); line-height: 1.55;
    background: var(--bg-subtle); border-radius: 5px;
    padding: 0.6rem 0.8rem; margin-top: 0.4rem; overflow: hidden;
    display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical;
}}

/* ---- thinking steps ---- */
.step-card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
    font-size: 0.8rem; font-family: 'JetBrains Mono', monospace;
    color: var(--text-dim);
}}
.step-action {{ color: var(--accent); font-weight: 600; }}
.step-obs {{ color: var(--green); }}

/* ---- buttons ---- */
div.stButton > button {{
    background: var(--card) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    padding: 0.45rem 1rem !important; transition: all 0.2s ease !important;
}}
div.stButton > button:hover {{
    border-color: var(--accent) !important;
    background: var(--card-hover) !important;
    color: var(--text) !important;
}}
div.stButton > button[kind="primary"] {{
    background: var(--accent) !important; color: #fff !important;
    border-color: var(--accent) !important;
}}
div.stButton > button[kind="primary"]:hover {{
    background: #1d4ed8 !important; border-color: #1d4ed8 !important;
}}

/* ---- text area ---- */
[data-testid="stTextArea"] textarea {{
    background: var(--card) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important;
}}
[data-testid="stTextArea"] textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}}

/* ---- select / file upload ---- */
[data-testid="stSelectbox"] > div {{ background: var(--card) !important; border-color: var(--border) !important; }}
[data-testid="stFileUploader"] {{ background: var(--card) !important; border-color: var(--border) !important; border-radius: 8px !important; }}

/* ---- spinner ---- */
.stSpinner > div {{ border-top-color: var(--accent) !important; }}

/* ---- dividers ---- */
hr {{ border-color: var(--border) !important; margin: 1.5rem 0 !important; }}

/* ---- scrollbar ---- */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--text-dim); }}

/* ---- pulse animation ---- */
@keyframes pulse-dot {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%        {{ opacity: 0.4; transform: scale(0.85); }}
}}
.live-dot {{
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    background: var(--green); animation: pulse-dot 1.4s ease-in-out infinite;
    margin-right: 6px; vertical-align: middle;
}}

/* ---- hero gradient text ---- */
.hero-title {{
    font-size: 1.6rem; font-weight: 700; letter-spacing: -0.03em;
    background: {"linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%)" if IS_DARK else "linear-gradient(135deg, #1e293b 0%, #475569 100%)"};
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; display: inline-block;
}}
.hero-sub {{ font-size: 0.8rem; color: var(--text-dim); margin-top: 0.15rem; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# UTILITY HELPERS
# ---------------------------------------------------------------------------

def kpi_card(label: str, value: str, sub: str = "", color: str = "accent"):
    color_map = {"accent": "var(--accent)", "green": "var(--green)",
                 "amber": "var(--amber)", "red": "var(--red)"}
    c = color_map.get(color, "var(--accent)")
    st.markdown(
        f'<div class="card" style="border-left:3px solid {c};">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value" style="color:{c};">{value}</div>'
        f'<div class="kpi-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def severity_badge(level: str) -> str:
    cls = {"critical": "badge-critical", "high": "badge-high",
           "medium": "badge-medium", "low": "badge-low"}.get(level.lower(), "badge-medium")
    return f'<span class="badge {cls}">{level.upper()}</span>'


def render_source_card(src: dict, idx: int):
    st.markdown(
        f'<div class="source-card">'
        f'<div class="source-title">📄 {src["title"]}</div>'
        f'<div style="font-size:0.72rem;color:var(--text-muted);margin-bottom:4px;">'
        f'  File: {src["source"]}  ·  Score: {src["score"]:.4f}</div>'
        f'<div class="source-chunk">{src["chunk"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", size=11,
              color="#a1a1aa" if IS_DARK else "#71717a"),
    margin=dict(l=0, r=0, t=20, b=0),
)


# ---------------------------------------------------------------------------
# RAG / AGENT INITIALIZATION (cached resource)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_vector_store():
    """Create a singleton VectorStoreManager (cached across reruns)."""
    from rag_pipeline import VectorStoreManager
    return VectorStoreManager()


def load_demo_data(store, api_key: str):
    """Load demo docs into the store (idempotent)."""
    if st.session_state.demo_loaded:
        return
    from rag_pipeline import load_demo_documents
    with st.spinner("📚 Loading demo financial documents into knowledge base..."):
        docs = load_demo_documents()
        store.build(docs, api_key=api_key)
    st.session_state.demo_loaded = True
    st.session_state.store_ready = True
    st.session_state.uploaded_docs_info = [
        {"title": "ACME Corp — Q3 2024 Earnings Report", "source": "ACME_Q3_2024_Earnings.pdf", "chunks": 8},
        {"title": "Regulatory Compliance Risk Memo", "source": "Regulatory_Compliance_Memo_2024.pdf", "chunks": 7},
        {"title": "Global Equity Portfolio Risk Assessment", "source": "Portfolio_Risk_Assessment_Oct2024.pdf", "chunks": 9},
        {"title": "Macro Risk Outlook Q4 2024", "source": "Macro_Risk_Outlook_Q4_2024.pdf", "chunks": 6},
    ]


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------

with st.sidebar:
    # Brand
    st.markdown(
        '<div style="margin-bottom:1.5rem;">'
        '<div style="font-size:1.1rem;font-weight:700;color:var(--text);letter-spacing:-0.02em;">💼 Digital Junior Analyst</div>'
        '<div style="font-size:0.72rem;color:var(--text-dim);margin-top:2px;">Tier 1 Intelligence. Instant.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # API Key
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("🔑 Gemini API Key", type="password",
                                placeholder="AIza...")
    else:
        st.markdown(
            '<div class="card card-green" style="font-size:0.78rem;padding:0.6rem 0.9rem;">'
            '<span class="live-dot"></span> API key loaded from .env</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Knowledge Base section
    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.6rem;">Knowledge Base</div>', unsafe_allow_html=True)

    demo_col, _ = st.columns([2, 1])
    with demo_col:
        load_demo_btn = st.button("📚 Load Demo Data", use_container_width=True)

    st.markdown('<div style="font-size:0.72rem;color:var(--text-dim);margin:0.5rem 0 0.8rem;">Or upload your own documents:</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "txt", "csv"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    # Show loaded docs
    if st.session_state.uploaded_docs_info:
        st.markdown('<div style="font-size:0.72rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;margin:0.8rem 0 0.4rem;">Loaded Documents</div>', unsafe_allow_html=True)
        for doc in st.session_state.uploaded_docs_info:
            st.markdown(
                f'<div style="font-size:0.75rem;padding:0.4rem 0;border-bottom:1px solid var(--border-sub);">'
                f'<div style="color:var(--text);font-weight:500;">{doc["title"][:40]}{"..." if len(doc["title"])>40 else ""}</div>'
                f'<div style="color:var(--text-dim);">{doc["chunks"]} chunks indexed</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Settings
    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.6rem;">Settings</div>', unsafe_allow_html=True)
    use_agent = st.toggle("🤖 ReAct Agent Mode", value=True,
                          help="When ON: multi-step reasoning agent. When OFF: single RAG call (faster).")
    num_sources = st.slider("Sources to retrieve", min_value=3, max_value=10, value=5)

    st.markdown("---")
    theme_label = "☀️ Light Mode" if IS_DARK else "🌙 Dark Mode"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

    st.markdown(
        '<div style="font-size:0.68rem;color:var(--text-dim);margin-top:1.5rem;text-align:center;">'
        'Powered by Gemini 3.1 Flash-Lite + LangChain RAG<br>© 2024 Digital Junior Analyst</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# INITIALIZE STORE
# ---------------------------------------------------------------------------
store = get_vector_store()

# Handle demo load button
if load_demo_btn and api_key:
    st.session_state.demo_loaded = False  # force reload
    load_demo_data(store, api_key)
    st.rerun()
elif load_demo_btn and not api_key:
    st.sidebar.error("Please provide a Gemini API key first.")

# Handle file uploads
if uploaded_files and api_key:
    from rag_pipeline import ingest_pdf, ingest_csv, ingest_text
    all_docs = []
    new_doc_info = list(st.session_state.uploaded_docs_info)
    existing_sources = {d["source"] for d in new_doc_info}

    for f in uploaded_files:
        if f.name in existing_sources:
            continue
        file_bytes = f.read()
        if f.name.endswith(".pdf"):
            docs = ingest_pdf(file_bytes, f.name)
        elif f.name.endswith(".csv"):
            docs = ingest_csv(file_bytes, f.name)
        else:
            docs = ingest_text(file_bytes.decode("utf-8", errors="ignore"), f.name, f.name)
        all_docs.extend(docs)
        new_doc_info.append({"title": f.name, "source": f.name, "chunks": len(docs)})

    if all_docs:
        with st.spinner(f"Indexing {len(uploaded_files)} document(s)..."):
            # Combine with any existing docs
            if st.session_state.demo_loaded:
                from rag_pipeline import load_demo_documents
                existing = load_demo_documents()
                all_docs = existing + all_docs
            store.build(all_docs, api_key=api_key)
        st.session_state.uploaded_docs_info = new_doc_info
        st.session_state.store_ready = True
        st.rerun()

# Auto-load demo if API key present and nothing loaded yet
if api_key and not st.session_state.store_ready and not st.session_state.demo_loaded:
    load_demo_data(store, api_key)


# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
h_left, h_right = st.columns([7, 2])
with h_left:
    st.markdown(
        '<div style="margin-bottom:1.75rem;">'
        '<span class="hero-title">◆ Digital Junior Analyst</span>'
        '<div class="hero-sub">Instant Synthesized Risk Intelligence · Powered by Agentic RAG · Gemini 3.1 Flash-Lite</div>'
        '</div>',
        unsafe_allow_html=True,
    )
with h_right:
    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
    status_color = "var(--green)" if st.session_state.store_ready else "var(--amber)"
    status_label = f"{'✓ Knowledge Base Ready' if st.session_state.store_ready else '⚡ Load Demo Data'}"
    st.markdown(
        f'<div class="card" style="text-align:center;padding:0.7rem;border-color:{status_color};">'
        f'<div style="font-size:0.75rem;font-weight:600;color:{status_color};">{status_label}</div>'
        f'<div style="font-size:0.68rem;color:var(--text-dim);">'
        f'{len(st.session_state.uploaded_docs_info)} doc(s) indexed</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# QUICK-FIRE EXAMPLE QUERIES
# ---------------------------------------------------------------------------
EXAMPLE_QUERIES = [
    "Summarize the key risks facing ACME Corp based on the Q3 2024 earnings report",
    "What are the most critical compliance violations identified and their financial exposure?",
    "Analyze the portfolio concentration risk and provide rebalancing recommendations",
    "What is ACME Corp's leverage ratio and is it at risk of a covenant breach?",
    "Generate a complete macro risk report for Q4 2024 including scenario probabilities",
]

if "query_text" not in st.session_state:
    st.session_state.query_text = ""

# ---------------------------------------------------------------------------
# MAIN TABS
# ---------------------------------------------------------------------------
tab_report, tab_sources, tab_risk_matrix, tab_agent_log = st.tabs([
    "⚡ Instant Report",
    "📄 Source Documents",
    "📊 Risk Matrix",
    "🔬 Agent Reasoning Log",
])

# ===========================================================================
# TAB 1: INSTANT REPORT
# ===========================================================================
with tab_report:

    # Example query pills
    st.markdown(
        '<div style="font-size:0.72rem;color:var(--text-muted);margin-bottom:0.5rem;font-weight:500;text-transform:uppercase;letter-spacing:0.04em;">Quick Start Examples</div>',
        unsafe_allow_html=True,
    )
    ex_cols = st.columns(len(EXAMPLE_QUERIES))
    for i, (col, query) in enumerate(zip(ex_cols, EXAMPLE_QUERIES)):
        with col:
            short = query[:38] + "…"
            if st.button(short, key=f"ex_{i}", use_container_width=True):
                st.session_state.query_text = query

    st.markdown('<div style="height:0.75rem;"></div>', unsafe_allow_html=True)

    # Query input
    user_query = st.text_area(
        "Analyst Query",
        value=st.session_state.query_text,
        placeholder="Ask your analyst: 'Generate a risk report on ACME Corp's liquidity position...' or 'What are the top 3 regulatory risks?'",
        height=110,
        label_visibility="collapsed",
        key="main_query_input",
    )

    btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 4])
    with btn_col1:
        generate_btn = st.button("⚡ Generate Risk Report", type="primary", use_container_width=True)
    with btn_col2:
        clear_btn = st.button("✕ Clear", use_container_width=True)

    if clear_btn:
        st.session_state.report_result = None
        st.session_state.query_text = ""
        st.rerun()

    st.markdown("---")

    # GENERATE REPORT
    if generate_btn and user_query.strip():
        if not api_key:
            st.error("🔑 Please provide a Gemini API key in the sidebar.")
        elif not st.session_state.store_ready:
            st.warning("📚 Please load the demo data or upload documents first (sidebar → Load Demo Data).")
        else:
            # Status placeholder
            status_ph = st.empty()
            progress_ph = st.empty()

            steps_taken = []
            def status_callback(msg: str):
                status_ph.markdown(
                    f'<div class="card card-accent" style="font-size:0.82rem;padding:0.75rem 1rem;">'
                    f'<span class="live-dot"></span>{msg}</div>',
                    unsafe_allow_html=True,
                )
                steps_taken.append(msg)

            from analyst_agent import run_analyst
            try:
                result = run_analyst(
                    query=user_query,
                    api_key=api_key,
                    store=store,
                    use_agent=use_agent,
                    status_callback=status_callback,
                )
                status_ph.empty()
                st.session_state.report_result = result
                st.session_state.report_result["query"] = user_query
                st.rerun()
            except Exception as e:
                status_ph.empty()
                st.error(f"Error generating report: {e}")

    elif generate_btn:
        st.warning("Please enter a query before generating a report.")

    # DISPLAY REPORT
    if st.session_state.report_result:
        result = st.session_state.report_result
        report_text = result.get("report", "")
        method = result.get("method", "direct")
        query_used = result.get("query", "")
        sources = result.get("sources", [])

        # Meta bar
        method_label = {"agent": "🤖 ReAct Agent", "direct": "⚡ RAG Direct",
                        "direct_fallback": "⚡ RAG Fallback"}.get(method, method)
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">'
            f'<div style="font-size:0.85rem;font-weight:600;color:var(--text);">📋 Risk Report</div>'
            f'<div style="display:flex;gap:0.5rem;align-items:center;">'
            f'<span class="badge badge-purple">{method_label}</span>'
            f'<span style="font-size:0.72rem;color:var(--text-muted);">{len(sources)} sources cited</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        # Query echo
        st.markdown(
            f'<div style="font-size:0.78rem;color:var(--text-dim);margin-bottom:0.75rem;">'
            f'Query: <em>{query_used[:120]}{"..." if len(query_used)>120 else ""}</em></div>',
            unsafe_allow_html=True,
        )

        # Report body
        st.markdown(
            f'<div class="report-output">{report_text}</div>',
            unsafe_allow_html=True,
        )

        # Download button
        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
        dl_col, _, _ = st.columns([1, 1, 3])
        with dl_col:
            st.download_button(
                "⬇️ Download Report",
                data=f"DIGITAL JUNIOR ANALYST — RISK REPORT\n{'='*60}\nQuery: {query_used}\nMethod: {method_label}\n{'='*60}\n\n{report_text}",
                file_name="risk_report.txt",
                mime="text/plain",
                use_container_width=True,
            )


# ===========================================================================
# TAB 2: SOURCE DOCUMENTS
# ===========================================================================
with tab_sources:
    if not st.session_state.uploaded_docs_info:
        st.markdown(
            '<div class="card card-amber" style="text-align:center;padding:2rem;">'
            '<div style="font-size:1.5rem;margin-bottom:0.5rem;">📚</div>'
            '<div style="font-weight:600;margin-bottom:0.25rem;">No documents loaded</div>'
            '<div style="font-size:0.82rem;color:var(--text-muted);">Click "Load Demo Data" in the sidebar to get started, or upload your own PDFs/CSVs.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:1rem;">'
            f'{len(st.session_state.uploaded_docs_info)} document(s) indexed in the knowledge base</div>',
            unsafe_allow_html=True,
        )

        for doc in st.session_state.uploaded_docs_info:
            total_chunks = doc.get("chunks", 0)
            st.markdown(
                f'<div class="card">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                f'<div>'
                f'<div style="font-weight:600;font-size:0.9rem;margin-bottom:0.25rem;">📄 {doc["title"]}</div>'
                f'<div style="font-size:0.75rem;color:var(--text-muted);">File: {doc["source"]}</div>'
                f'</div>'
                f'<span class="badge badge-purple">{total_chunks} chunks</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Source citations from last report
        if st.session_state.report_result and st.session_state.report_result.get("sources"):
            st.markdown("---")
            st.markdown(
                '<div style="font-size:0.85rem;font-weight:600;margin-bottom:0.75rem;">🔎 Citations from Last Report</div>',
                unsafe_allow_html=True,
            )
            for i, src in enumerate(st.session_state.report_result["sources"], 1):
                render_source_card(src, i)


# ===========================================================================
# TAB 3: RISK MATRIX
# ===========================================================================
with tab_risk_matrix:
    if not st.session_state.report_result:
        st.markdown(
            '<div class="card card-accent" style="text-align:center;padding:2.5rem;">'
            '<div style="font-size:1.5rem;margin-bottom:0.5rem;">📊</div>'
            '<div style="font-weight:600;margin-bottom:0.25rem;">No report generated yet</div>'
            '<div style="font-size:0.82rem;color:var(--text-muted);">Generate a risk report in the "Instant Report" tab first.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        report_text = st.session_state.report_result.get("report", "")

        # Parse severity mentions from report text
        import re

        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for key in severity_counts:
            severity_counts[key] = len(re.findall(key, report_text, re.IGNORECASE))

        # KPIs
        kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
        with kpi_c1:
            kpi_card("Critical Risks", str(severity_counts["Critical"]), "Immediate action required", "red")
        with kpi_c2:
            kpi_card("High Risks", str(severity_counts["High"]), "Elevated monitoring", "amber")
        with kpi_c3:
            kpi_card("Medium Risks", str(severity_counts["Medium"]), "Track and manage", "accent")
        with kpi_c4:
            kpi_card("Low Risks", str(severity_counts["Low"]), "Standard oversight", "green")

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

        # Severity Distribution Chart
        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown('<div class="card"><div style="font-weight:600;font-size:0.85rem;margin-bottom:0.75rem;">Risk Severity Distribution</div>', unsafe_allow_html=True)
            colors_map = {"Critical": "#ef4444", "High": "#f59e0b", "Medium": "#2563eb", "Low": "#22c55e"}
            non_zero = {k: v for k, v in severity_counts.items() if v > 0}
            if non_zero:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(non_zero.keys()),
                    values=list(non_zero.values()),
                    marker_colors=[colors_map[k] for k in non_zero.keys()],
                    hole=0.52,
                    textfont_size=11,
                    hovertemplate="%{label}: %{value} mentions<extra></extra>",
                )])
                fig_pie.update_layout(
                    **PLOT_LAYOUT,
                    height=260,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0.5, xanchor="center"),
                    annotations=[dict(text=f"<b>{sum(non_zero.values())}</b><br>risks", x=0.5, y=0.5,
                                      font_size=14, font_color="#fafafa" if IS_DARK else "#09090b",
                                      showarrow=False)]
                )
                st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        with ch2:
            st.markdown('<div class="card"><div style="font-weight:600;font-size:0.85rem;margin-bottom:0.75rem;">Risk Heat Map (Likelihood vs Impact)</div>', unsafe_allow_html=True)

            # Build a synthetic heat map from common risk types found in report
            risk_keywords = {
                "Liquidity": (4, 5), "Leverage": (3, 5), "Regulatory": (3, 4),
                "Market": (4, 3), "Operational": (3, 3), "Currency": (2, 3),
                "Credit": (3, 4), "Geopolitical": (2, 5), "Concentration": (4, 4),
            }

            found_risks = [(k, v) for k, v in risk_keywords.items()
                           if k.lower() in report_text.lower()][:8]

            if found_risks:
                risk_names = [r[0] for r in found_risks]
                likelihoods = [r[1][0] for r in found_risks]
                impacts = [r[1][1] for r in found_risks]
                risk_scores = [l * i for l, i in zip(likelihoods, impacts)]
                max_score = max(risk_scores)
                bubble_sizes = [max(20, (s / max_score) * 50) for s in risk_scores]
                text_labels = [f"{n}<br>Score: {s}" for n, s in zip(risk_names, risk_scores)]
                dot_colors = [
                    "#ef4444" if s >= 16 else "#f59e0b" if s >= 9 else "#2563eb" if s >= 4 else "#22c55e"
                    for s in risk_scores
                ]

                fig_heat = go.Figure(data=[go.Scatter(
                    x=likelihoods, y=impacts,
                    mode="markers+text",
                    text=risk_names,
                    textposition="top center",
                    marker=dict(
                        size=bubble_sizes,
                        color=dot_colors,
                        opacity=0.85,
                        line=dict(width=1, color="rgba(255,255,255,0.2)"),
                    ),
                    hovertemplate="<b>%{text}</b><br>Likelihood: %{x}/5<br>Impact: %{y}/5<extra></extra>",
                )])
                fig_heat.update_layout(
                    **PLOT_LAYOUT,
                    height=260,
                    xaxis=dict(title="Likelihood (1-5)", range=[0, 5.5], dtick=1,
                               gridcolor="rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.05)",
                               tickfont=dict(size=10, color="#71717a")),
                    yaxis=dict(title="Impact (1-5)", range=[0, 5.5], dtick=1,
                               gridcolor="rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.05)",
                               tickfont=dict(size=10, color="#71717a")),
                )
                st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        # Source breakdown bar chart
        if st.session_state.report_result.get("sources"):
            sources = st.session_state.report_result["sources"]
            src_df = pd.DataFrame(sources)
            if "title" in src_df.columns and "score" in src_df.columns:
                st.markdown('<div class="card"><div style="font-weight:600;font-size:0.85rem;margin-bottom:0.75rem;">Source Relevance Scores</div>', unsafe_allow_html=True)
                # Shorter labels
                src_df["short_title"] = src_df["title"].apply(lambda x: x[:35] + "…" if len(x) > 35 else x)
                # Lower score = more similar in FAISS (L2 distance)
                src_df["relevance"] = 1 / (1 + src_df["score"])
                src_df = src_df.sort_values("relevance", ascending=True)

                fig_src = go.Figure(go.Bar(
                    x=src_df["relevance"].round(4),
                    y=src_df["short_title"],
                    orientation="h",
                    marker_color="#2563eb",
                    text=src_df["relevance"].round(3).astype(str),
                    textposition="outside",
                ))
                fig_src.update_layout(**PLOT_LAYOUT, height=max(200, len(src_df) * 40))
                st.plotly_chart(fig_src, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)


# ===========================================================================
# TAB 4: AGENT REASONING LOG
# ===========================================================================
with tab_agent_log:
    if not st.session_state.report_result:
        st.markdown(
            '<div class="card card-accent" style="text-align:center;padding:2.5rem;">'
            '<div style="font-size:1.5rem;margin-bottom:0.5rem;">🔬</div>'
            '<div style="font-weight:600;margin-bottom:0.25rem;">No reasoning trace yet</div>'
            '<div style="font-size:0.82rem;color:var(--text-muted);">Generate a report with ReAct Agent Mode enabled to see the agent\'s reasoning steps.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        method = st.session_state.report_result.get("method", "direct")
        steps = st.session_state.report_result.get("intermediate_steps", [])

        meta_label = {"agent": "🤖 ReAct Agent", "direct": "⚡ RAG Direct",
                      "direct_fallback": "⚡ RAG Fallback"}.get(method, method)
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">'
            f'<span class="badge badge-purple">{meta_label}</span>'
            f'<span style="font-size:0.78rem;color:var(--text-muted);">{len(steps)} reasoning step(s) logged</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if not steps:
            st.markdown(
                '<div class="card card-amber" style="font-size:0.82rem;">'
                '⚠️ No intermediate steps captured. This happens in direct RAG mode or when the agent returns a single-step response.</div>',
                unsafe_allow_html=True,
            )
        else:
            for i, (action, observation) in enumerate(steps, 1):
                tool_name = getattr(action, "tool", str(action))
                tool_input = getattr(action, "tool_input", "")
                obs_text = str(observation)[:600] + ("..." if len(str(observation)) > 600 else "")

                st.markdown(
                    f'<div class="step-card">'
                    f'<div><span class="step-action">Step {i} → {tool_name}</span></div>'
                    f'<div style="margin-top:4px;color:var(--text-dim);font-size:0.72rem;">Input: {str(tool_input)[:200]}</div>'
                    f'<div style="margin-top:6px;" class="step-obs">Observation: {obs_text}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
