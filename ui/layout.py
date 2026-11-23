"""Streamlit UI layout, modern product design system, and compact shell structure."""

import streamlit as st


_COFFEE_CONTRAST_PAIRS = (
    ("primary button default", "#FFFFFF", "#8E4A25", 6.56),
    ("primary button hover", "#FFFFFF", "#733B1D", 6.56),
    ("small text on cream", "#6A5D51", "#F3ECDF", 5.34),
    ("result heading", "#FFF6EB", "#34251D", 4.5),
    ("result detail", "#F1DDC9", "#34251D", 4.5),
    ("result label", "#E4A879", "#34251D", 4.5),
    ("disabled button", "#6A5D51", "#E8D9C7", 4.5),
)


def _clean_html(raw: str) -> str:
    """Strip leading/trailing whitespace from each line to prevent Markdown code-block interpretation."""
    return "".join(line.strip() for line in raw.splitlines())


# Vector SVG Icons (Lucide / Feather Standard Specifications, 14-20px)
SVG_ICONS = {
    "logo": """<svg width="100%" height="100%" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="32" height="32" rx="8" fill="url(#coffee_brand_grad)" />
        <path d="M16 6C10.477 6 6 10.477 6 16C6 21.523 10.477 26 16 26C21.523 26 26 21.523 26 16C26 10.477 21.523 6 16 6Z" fill="#78350F" fill-opacity="0.3"/>
        <path d="M16 8C13 12 13 20 16 24C19 20 19 12 16 8Z" stroke="#FDE68A" stroke-width="2" stroke-linecap="round"/>
        <circle cx="11.5" cy="13.5" r="1.5" fill="#FFFFFF"/>
        <circle cx="20.5" cy="18.5" r="1.5" fill="#FDE68A"/>
        <defs>
            <linearGradient id="coffee_brand_grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                <stop stop-color="#78350F" />
                <stop offset="1" stop-color="#451A03" />
            </linearGradient>
        </defs>
    </svg>""",
    "cpu": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>""",
    "database": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>""",
    "zap": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "target": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
    "shield_check": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>""",
    "sparkle": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>""",
    "coffee": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>""",
    "activity": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>""",
}


def setup_page_config() -> None:
    """Set global Streamlit page configuration and inject modern luxury product design tokens."""
    st.set_page_config(
        page_title="Arabica Vision AI | Multi-Model CNN-SVM Studio",
        page_icon="☕",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Ultra-refined design system CSS (Linear, Stripe, Apple HIG, Vercel inspired)
    css = """
    <style>
    :root {
        --font-sans: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --font-mono: ui-monospace, "SFMono-Regular", Menlo, Monaco, Consolas, monospace;
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-6: 24px;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --shadow-card: 0 1px 3px rgba(15, 23, 42, 0.04), 0 6px 18px -8px rgba(15, 23, 42, 0.12);
        --motion-fast: 160ms cubic-bezier(0.2, 0.8, 0.2, 1);
        --bg-main: #F3ECDF;
        --bg-surface: #FFFAF1;
        --bg-disabled: #E8D9C7;
        --border-subtle: #D9CBBB;
        --border-medium: #B9A893;
        --text-primary: #292018;
        --text-secondary: #6A5D51;
        --text-tertiary: #6A5D51;
        --brand-amber: #8E4A25;
        --brand-amber-dark: #34251D;
        --brand-gold: #8F4B26;
        --brand-gold-subtle: rgba(143, 75, 38, 0.08);
        --brand-indigo: #2563EB;
        --brand-emerald: #059669;
    }

    html, body, [class*="css"] {
        font-family: var(--font-sans);
        color: var(--text-primary);
        background-color: var(--bg-main);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1320px !important;
    }

    /* Respect reduced-motion preference; keep all states usable. */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            scroll-behavior: auto !important;
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    @media (max-width: 600px) {
        .block-container {
            padding-left: var(--space-3) !important;
            padding-right: var(--space-3) !important;
        }
        .brand-title { font-size: 1.2rem !important; }
        .brand-version { font-size: 0.6rem !important; padding: 3px 6px !important; }
        .brand-identity-row { gap: var(--space-2) !important; }
    }

    body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main .block-container { background: var(--bg-main) !important; color: var(--text-primary) !important; }
    [data-testid="stVerticalBlockBorderWrapper"] > div { background: var(--bg-surface) !important; border-color: var(--border-subtle) !important; }
    ::selection { background: #E8C5AA; color: #292018; }
    .block-container > div { min-width: 0; }
    .lab-intro { padding: 12px 0 18px; max-width: 68ch; }
    .lab-intro h1 { margin: 0 0 8px; color: var(--text-primary); font: 500 clamp(2rem, 4vw, 3.25rem)/1.05 Georgia, "Times New Roman", serif; letter-spacing: -0.035em; }
    .lab-intro p { margin: 0; color: var(--text-secondary); font-size: 1rem; }
    .stButton > button[kind="primary"] { background: #8E4A25 !important; color: #FFFFFF !important; border-color: #8E4A25 !important; }
    .stButton > button[kind="primary"]:hover { background: #733B1D !important; border-color: #733B1D !important; }
    .stButton > button:disabled, .stButton > button[disabled] { color: #6A5D51 !important; background: #E8D9C7 !important; border-color: #B9A893 !important; opacity: 1 !important; }
    .quality-result { display:flex; align-items:center; justify-content:space-between; gap:20px; margin:18px 0; padding:24px 28px; border-radius:14px; background:#34251D; color:#FFF6EB; }
    .quality-result-label { margin:0 0 6px; color:#E4A879; font-size:.8rem; font-weight:700; }
    .quality-result h2 { margin:0; color:#FFF6EB; font:500 clamp(1.7rem,3vw,2.5rem)/1.1 Georgia,"Times New Roman",serif; }
    .quality-result-detail { margin:7px 0 0; color:#F1DDC9; font-size:.9rem; }
    .quality-result-count { padding:8px 12px; border:1px solid #B18B6E; border-radius:8px; color:#FFF6EB; white-space:nowrap; }
    .preview-empty { min-height:216px; display:grid; align-content:center; justify-items:center; gap:8px; padding:20px; text-align:center; border:1px dashed #B9A893; border-radius:var(--radius-md); background:rgba(255,250,241,.72); color:var(--text-primary); }
    .preview-empty span { color:var(--text-secondary); font-size:.9rem; }
    .lab-intro, .preview-empty, .quality-result, .stExpander { min-width:0; }
    .stButton > button[kind="primary"]:focus-visible { outline:3px solid #34251D !important; outline-offset:3px !important; box-shadow:0 0 0 5px #E8C5AA !important; }
    .stButton > button:disabled:focus-visible { outline-color:#6A5D51 !important; }
    @media(max-width:700px) {
        .block-container { padding-left:12px !important; padding-right:12px !important; }
        .lab-intro { padding:8px 0 14px; }
        .lab-intro p { font-size:.92rem; }
        .quality-result { padding:18px; gap:12px; }
        .quality-result-count { font-size:.8rem; }
    }
    @media(prefers-reduced-motion: reduce) { *,*::before,*::after { transform:none !important; } }
        .stExpander { border-color:var(--border-subtle) !important; border-radius:var(--radius-md) !important; }
    .quality-card, div[data-testid="stMetric"] { border-radius:var(--radius-sm) !important; }

    /* Streamlit App Shell Header */
    header[data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
        height: 2.75rem;
    }

    /* Streamlit Sidebar Polish */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
        border-right: 1px solid var(--border-subtle);
        box-shadow: 1px 0 10px rgba(15, 23, 42, 0.02);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Keyboard focus remains visible across native Streamlit controls. */
    :where(button, a, input, [role="tab"], [role="button"]):focus-visible {
        outline: 3px solid rgba(146, 64, 14, 0.55) !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 4px rgba(217, 119, 6, 0.12) !important;
    }

    /* Tabs: compact pill navigation, horizontally scrollable on narrow screens. */
    div[data-testid="stTabs"] {
        margin-top: var(--space-2);
    }
    div[data-testid="stTabs"] [role="tablist"] {
        gap: var(--space-1);
        background: #F1F5F9;
        padding: var(--space-1);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
        overflow-x: auto;
        scrollbar-width: thin;
    }
    div[data-testid="stTabs"] [data-testid="stTab"] {
        font-family: var(--font-sans);
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        border-radius: var(--radius-sm);
        padding: 6px 14px;
        border: none;
        background: transparent;
        transition: background-color var(--motion-fast), color var(--motion-fast), box-shadow var(--motion-fast);
        height: auto;
        flex: 0 0 auto;
        white-space: nowrap;
    }
    div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
        background: #FFFFFF !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08), 0 2px 6px rgba(15, 23, 42, 0.04) !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Native inputs, buttons and status widgets use one consistent surface system. */
    div[data-testid="stFileUploader"], div[data-testid="stSelectbox"], div[data-testid="stTextInput"] {
        min-width: 0;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stTextInput"] input {
        border-color: var(--border-medium) !important;
        border-radius: var(--radius-sm) !important;
        background: var(--bg-surface) !important;
        transition: border-color var(--motion-fast), box-shadow var(--motion-fast) !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--brand-amber) !important;
        box-shadow: 0 0 0 3px rgba(146, 64, 14, 0.12) !important;
    }
    .stButton > button, [data-testid="stDownloadButton"] > button {
        border-radius: var(--radius-sm) !important;
        font-weight: 650 !important;
        transition: background-color var(--motion-fast), border-color var(--motion-fast), box-shadow var(--motion-fast), transform var(--motion-fast) !important;
    }
    .stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-card) !important;
    }

    /* Metric Cards - Multi-layered Depth & Compact Density */
    div[data-testid="stMetric"] {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: var(--space-3) var(--space-4);
        box-shadow: var(--shadow-card);
        transition: transform var(--motion-fast), box-shadow var(--motion-fast);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 14px -2px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stMetricLabel"] {
        font-family: var(--font-sans) !important;
        font-size: 0.70rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B !important;
        margin-bottom: 2px !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: var(--text-primary) !important;
    }

    /* Modern Dropzone Compact */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important;
        border: 1.5px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 18px 16px !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02) !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #8F4B26 !important;
        background-color: #FFFDF9 !important;
        box-shadow: 0 0 0 3px rgba(143, 75, 38, 0.12), 0 4px 12px rgba(143, 75, 38, 0.08) !important;
    }

    /* Image Preview Frame Polish */
    div[data-testid="stImage"] img {
        border-radius: 10px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 2px 8px -1px rgba(15, 23, 42, 0.03) !important;
        transition: box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-testid="stImage"] img:hover {
        box-shadow: 0 4px 14px -2px rgba(15, 23, 42, 0.08) !important;
    }

    /* Shared state cards for idle/loading/empty/error flows. */
    .state-card {
        padding: var(--space-4) var(--space-6);
        margin: var(--space-3) 0;
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        background: linear-gradient(145deg, var(--bg-surface), var(--bg-main));
        box-shadow: var(--shadow-card);
    }
    .state-card h3, .state-card p { margin: var(--space-1) 0; }
    .state-card .state-kicker {
        color: var(--brand-amber);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .state-loading { border-left: 4px solid var(--brand-amber); }
    .state-error { border-left: 4px solid #B42318; background: #FFF7F6; }
    .state-empty { border-style: dashed; }
    .upload-section-heading {
        display: flex;
        align-items: baseline;
        flex-wrap: wrap;
        gap: var(--space-2);
        margin: 0 0 var(--space-2);
    }
    .upload-section-heading > span {
        color: var(--brand-amber);
        font: 700 0.7rem var(--font-mono);
    }
    .upload-section-heading > strong { color: var(--text-primary); }
    .upload-section-heading > small { margin-left: auto; }
    .quality-card {
        min-height: 100%;
        padding: var(--space-4);
        border: 1px solid var(--border-subtle);
        border-top: 3px solid var(--quality-accent, var(--brand-amber));
        border-radius: var(--radius-md);
        background: linear-gradient(150deg, var(--quality-tint, #FFFFFF), var(--bg-surface) 62%);
        box-shadow: var(--shadow-card);
        transition: transform var(--motion-fast), box-shadow var(--motion-fast);
    }
    .quality-card:hover { transform: translateY(-2px); }
    .spec-section {
        padding: var(--space-4);
        margin-bottom: var(--space-3);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        background: var(--bg-surface);
        box-shadow: var(--shadow-card);
    }
    .comparison-banner {
        padding: var(--space-3) var(--space-4);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        background: linear-gradient(135deg, #FFF8EB, #FFFFFF);
        box-shadow: var(--shadow-card);
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
            transform: none !important;
        }
        div[data-testid="stMetric"]:hover,
        .stButton > button:hover,
        [data-testid="stDownloadButton"] > button:hover,
        .quality-card:hover {
            transform: none !important;
        }
    }

    /* Unified visual treatment for alerts, tables, charts, expanders and previews. */
    div[data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-subtle) !important;
        box-shadow: var(--shadow-card) !important;
    }
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        border-radius: var(--radius-md) !important;
        overflow: hidden;
        border: 1px solid var(--border-subtle) !important;
        background: var(--bg-surface) !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        background: var(--bg-surface) !important;
    }
    div[data-testid="stImage"] img {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-subtle) !important;
        box-shadow: var(--shadow-card) !important;
    }
    div[data-testid="stSpinner"] > div { color: var(--brand-amber) !important; }
    .stCaption, small { color: var(--text-secondary); }

    /* Monospace formatting */
    code, pre {
        font-family: var(--font-mono) !important;
    }

    /* Table & Chart Container */
    .stAltairChart {
        background-color: transparent !important;
        border-radius: var(--radius-md);
    }
    hr {
        margin: 16px 0 !important;
        border: none !important;
        border-top: 1px solid #E2E8F0 !important;
    }
    </style>
    """
    st.markdown(_clean_html(css), unsafe_allow_html=True)


def render_header() -> None:
    """Render branded dashboard header with aligned identity and workspace context."""
    header_html = f"""
    <div style="background:linear-gradient(135deg,#FFFFFF 0%,#FFFCF7 100%);border:1px solid #E2E8F0;border-radius:14px;padding:20px clamp(12px,4vw,24px);margin-bottom:14px;box-shadow:0 1px 3px rgba(15,23,42,.03),0 6px 18px -8px rgba(15,23,42,.12);position:relative;overflow:hidden;box-sizing:border-box;min-width:0;">
      <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#78350F,#D97706,#B45309);"></div>
      <div class="brand-identity-row" style="display:flex;align-items:center;gap:12px;flex-wrap:nowrap;min-width:0;">
        <div style="width:46px;height:46px;flex:0 0 46px;display:flex;align-items:center;justify-content:center;filter:drop-shadow(0 3px 8px rgba(120,53,15,.2));">
          {SVG_ICONS["logo"]}
        </div>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:nowrap;min-width:0;min-height:46px;">
          <h1 class="brand-title" style="white-space:nowrap;margin:0;font-size:1.7rem;line-height:1.2;font-weight:800;color:#0F172A;letter-spacing:-.03em;">Arabica Vision AI</h1>
          <span class="brand-version" style="white-space:nowrap;background:#FFFBEB;color:#92400E;font-size:.68rem;font-weight:700;padding:3px 7px;border-radius:9999px;border:1px solid #FDE68A;font-family:'JetBrains Mono',monospace;">v2.5 • Studio</span>
        </div>
      </div>
      <p style="display:flex;align-items:center;gap:6px;margin:8px 0 0 58px;font-size:.72rem;line-height:1.3;color:#92400E;font-weight:700;"><span aria-hidden="true" style="width:15px;height:15px;display:inline-flex;flex:0 0 15px;align-items:center;justify-content:center;">{SVG_ICONS["coffee"]}</span><span>Studio Unggah Inspeksi Citra</span></p>
      <p style="margin:4px 0 0 58px;font-size:.84rem;line-height:1.4;color:#64748B;font-weight:500;">Analisis mutu biji kopi Arabika dengan evaluasi CNN–SVM</p>
      <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:16px 0 0;padding-top:13px;border-top:1px solid #F1F5F9;">
        <span style="font-size:.76rem;color:#64748B;line-height:1.5;">Alur analisis: unggah citra · periksa metadata · tinjau hasil klasifikasi</span>
      </div>
    </div>
    """
    st.markdown(_clean_html(header_html), unsafe_allow_html=True)


def render_sidebar() -> str:
    """Render sidebar with mode selection and technical references in modern inspector aesthetic."""
    with st.sidebar:
        title_html = f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <div style="
                width: 28px;
                height: 28px;
                border-radius: 7px;
                background: linear-gradient(135deg, #78350F 0%, #451A03 100%);
                color: #FFFFFF;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                {SVG_ICONS["sparkle"]}
            </div>
            <div>
                <h3 style="margin: 0; font-size: 0.95rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">
                    Inspector Studio
                </h3>
                <span style="font-size: 0.70rem; color: #64748B; font-weight: 500;">
                    Kontrol Evaluasi Inferensi
                </span>
            </div>
        </div>
        """
        st.markdown(_clean_html(title_html), unsafe_allow_html=True)

        model_mode = st.radio(
            "Pilih Mode Evaluasi:",
            options=[
                "Perbandingan Semua Model (3 Model)",
                "MobileNetV3-Small (Cepat & Ringan)",
                "ShuffleNetV2 (Optimal Mobile)",
                "EfficientNet-B0 (Representasi Tinggi)",
            ],
            index=0,
            help="Mode perbandingan mengeksekusi 3 model secara serentak untuk mengukur konsensus prediksi dan latensi.",
        )

        st.markdown("---")
        spec_badge = f"""
        <div style="
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            padding: 12px;
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02);
        ">
            <span style="font-size: 0.68rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 5px; margin-bottom: 6px;">
                {SVG_ICONS["database"]} Dataset USK-Coffee
            </span>
            <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                Arabika Gayo & Aceh
            </div>
            <div style="font-size: 0.72rem; color: #64748B; line-height: 1.35;">
                Defect • Longberry • Peaberry • Premium
            </div>
        </div>
        """
        st.markdown(_clean_html(spec_badge), unsafe_allow_html=True)

    return model_mode


def render_footer() -> None:
    """Render modern compact luxury product footer."""
    st.markdown("---")
    footer_html = f"""
    <div style="
        text-align: center;
        color: #64748B;
        font-size: 0.80rem;
        padding: 16px 0 12px 0;
        display: flex;
        flex-direction: column;
        gap: 6px;
        align-items: center;
    ">
        <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #0F172A;">
            <div style="width: 20px; height: 20px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center;">{SVG_ICONS["logo"]}</div>
            <span>Arabica Vision AI Studio</span>
            <span style="color: #CBD5E1;">•</span>
            <span style="font-weight: 500; color: #64748B;">Multi-Backbone Transfer Learning Engine</span>
        </div>
        <span style="font-size: 0.72rem; color: #94A3B8; font-family: 'JetBrains Mono', monospace;">
            PyTorch 2.0 • Scikit-Learn • Streamlit • Altair Graphics • Zero Memory Leak
        </span>
    </div>
    """
    st.markdown(_clean_html(footer_html), unsafe_allow_html=True)
