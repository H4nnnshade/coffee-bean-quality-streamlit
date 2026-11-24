"""Streamlit UI layout — Warm Light + Dark Accent design system."""

import streamlit as st


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
    "arrow_right": """<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>""",
}


def setup_page_config() -> None:
    """Set global Streamlit page configuration and inject Warm Light + Dark Accent design tokens."""
    st.set_page_config(
        page_title="Arabica Vision AI | Multi-Model CNN-SVM Studio",
        page_icon="☕",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Warm Light + Dark Accent design system
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', ui-monospace, Menlo, Monaco, monospace;

        /* Light base palette */
        --bg-main: #FAF7F4;
        --bg-surface: #FFFFFF;
        --bg-muted: #F5F0EB;
        --border-subtle: #EDE8E3;
        --border-medium: #D6CFC8;
        --text-primary: #1A1210;
        --text-secondary: #5C4F45;
        --text-tertiary: #9C8E84;

        /* Dark accent surfaces */
        --dark-surface: #1C1109;
        --dark-surface-2: #2A1A0E;
        --dark-border: rgba(255,255,255,0.10);
        --dark-text: #F5EDE3;
        --dark-text-muted: #A8906E;

        /* Brand */
        --brand-amber: #92400E;
        --brand-gold: #D97706;
        --brand-gold-light: #FDE68A;
        --brand-emerald: #059669;
        --brand-rose: #DC2626;
        --brand-violet: #7C3AED;
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
        padding-bottom: 2.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1340px !important;
    }

    /* Responsive brand header */
    @media (max-width: 600px) {
        .brand-title { font-size: 1.1rem !important; }
        .brand-version { font-size: 0.60rem !important; padding: 2px 6px !important; }
        .brand-identity-row { gap: 8px !important; }
        .brand-tagline { margin-left: 0 !important; }
    }

    /* Streamlit App Shell Header */
    header[data-testid="stHeader"] {
        background-color: rgba(250, 247, 244, 0.90);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-bottom: 1px solid #EDE8E3;
        height: 2.75rem;
    }

    /* Streamlit Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #FAF7F4 100%);
        border-right: 1px solid #EDE8E3;
        box-shadow: 2px 0 12px rgba(26,18,9,0.04);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Tabs — pill navigation */
    div[data-testid="stTabs"] { margin-top: 8px; }
    div[data-testid="stTabs"] [role="tablist"] {
        gap: 4px;
        background: #EDE8E3;
        padding: 4px;
        border-radius: 10px;
        border: 1px solid #D6CFC8;
    }
    div[data-testid="stTabs"] [data-testid="stTab"] {
        font-family: var(--font-sans);
        font-size: 0.83rem;
        font-weight: 600;
        color: #7A6A5A;
        border-radius: 7px;
        padding: 6px 16px;
        border: none;
        background: transparent;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
        height: auto;
    }
    div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
        background: #FFFFFF !important;
        color: #1A1210 !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 4px rgba(26,18,9,0.10), 0 2px 8px rgba(26,18,9,0.05) !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }

    /* Metric Cards — light surface */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #EDE8E3;
        border-radius: 12px;
        padding: 13px 15px;
        box-shadow: 0 1px 3px rgba(26,18,9,0.04), 0 2px 8px -2px rgba(26,18,9,0.03);
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px -4px rgba(26,18,9,0.10), 0 2px 6px -2px rgba(26,18,9,0.06);
    }
    div[data-testid="stMetricLabel"] {
        font-family: var(--font-sans) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #9C8E84 !important;
        margin-bottom: 2px !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: #1A1210 !important;
    }

    /* File Upload Dropzone */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important;
        border: 1.5px dashed #D6CFC8 !important;
        border-radius: 14px !important;
        padding: 20px 18px !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 1px 3px rgba(26,18,9,0.03) !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #D97706 !important;
        background-color: #FFFDF9 !important;
        box-shadow: 0 0 0 3px rgba(217,119,6,0.09), 0 4px 14px rgba(217,119,6,0.06) !important;
    }

    /* Image Preview */
    div[data-testid="stImage"] img {
        border-radius: 12px !important;
        border: 1px solid #EDE8E3 !important;
        box-shadow: 0 2px 8px rgba(26,18,9,0.06), 0 1px 3px rgba(26,18,9,0.04) !important;
        transition: box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-testid="stImage"] img:hover {
        box-shadow: 0 6px 20px rgba(26,18,9,0.10) !important;
    }

    /* Monospace */
    code, pre { font-family: var(--font-mono) !important; }

    /* Chart + table */
    .stAltairChart { background-color: transparent !important; }
    hr {
        margin: 18px 0 !important;
        border: none !important;
        border-top: 1px solid #EDE8E3 !important;
    }

    /* Dataframe polish */
    div[data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #EDE8E3 !important;
    }
    </style>
    """
    st.markdown(_clean_html(css), unsafe_allow_html=True)


def render_header() -> None:
    """Render branded dashboard header — light card with dark accent stripe."""
    header_html = f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #EDE8E3;
        border-radius: 16px;
        padding: 22px clamp(14px,4vw,28px);
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(26,18,9,0.04), 0 8px 24px -8px rgba(26,18,9,0.08);
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
    ">
      <!-- Amber gradient top bar -->
      <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#78350F 0%,#D97706 50%,#B45309 100%);border-radius:16px 16px 0 0;"></div>

      <!-- Brand row -->
      <div class="brand-identity-row" style="display:flex;align-items:center;gap:14px;flex-wrap:nowrap;min-width:0;">
        <!-- Logo -->
        <div style="width:48px;height:48px;flex:0 0 48px;border-radius:12px;display:flex;align-items:center;justify-content:center;filter:drop-shadow(0 3px 10px rgba(120,53,15,0.25));">
          {SVG_ICONS["logo"]}
        </div>

        <!-- Title block -->
        <div style="display:flex;flex-direction:column;gap:3px;min-width:0;flex:1;">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            <h1 class="brand-title" style="margin:0;font-size:1.75rem;line-height:1.15;font-weight:800;color:#1A1210;letter-spacing:-.03em;white-space:nowrap;">Arabica Vision AI</h1>
            <span class="brand-version" style="background:#1C1109;color:#D97706;font-size:.68rem;font-weight:700;padding:3px 9px;border-radius:9999px;font-family:'JetBrains Mono',monospace;white-space:nowrap;letter-spacing:.02em;">v2.5 · Studio</span>
          </div>
          <p class="brand-tagline" style="margin:0;font-size:.82rem;color:#7A6A5A;font-weight:500;line-height:1.4;">
            Analisis mutu biji kopi Arabika · Evaluasi multi-model CNN–SVM
          </p>
        </div>

        <!-- Right status pill (desktop only) -->
        <div style="flex-shrink:0;display:flex;align-items:center;gap:6px;background:#F5F0EB;border:1px solid #D6CFC8;border-radius:9999px;padding:5px 12px;">
          <span style="width:7px;height:7px;border-radius:50%;background:#059669;display:inline-block;flex-shrink:0;"></span>
          <span style="font-size:.72rem;font-weight:700;color:#374151;white-space:nowrap;">Pipeline Aktif</span>
        </div>
      </div>

      <!-- Bottom breadcrumb bar -->
      <div style="display:flex;align-items:center;gap:6px;margin-top:14px;padding-top:12px;border-top:1px solid #F0EBE5;flex-wrap:wrap;">
        <span style="font-size:.72rem;color:#9C8E84;">{SVG_ICONS["coffee"]}</span>
        <span style="font-size:.72rem;color:#9C8E84;font-weight:600;">Unggah Citra</span>
        <span style="color:#D6CFC8;">{SVG_ICONS["arrow_right"]}</span>
        <span style="font-size:.72rem;color:#9C8E84;font-weight:600;">Inspeksi Metadata</span>
        <span style="color:#D6CFC8;">{SVG_ICONS["arrow_right"]}</span>
        <span style="font-size:.72rem;color:#9C8E84;font-weight:600;">Klasifikasi CNN–SVM</span>
        <span style="color:#D6CFC8;">{SVG_ICONS["arrow_right"]}</span>
        <span style="font-size:.72rem;color:#9C8E84;font-weight:600;">Komparasi Arsitektur</span>
      </div>
    </div>
    """
    st.markdown(_clean_html(header_html), unsafe_allow_html=True)


def render_sidebar() -> str:
    """Render sidebar with mode selection and technical references."""
    with st.sidebar:
        title_html = f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
            <div style="width:30px;height:30px;border-radius:8px;background:linear-gradient(135deg,#78350F 0%,#451A03 100%);color:#FDE68A;display:flex;align-items:center;justify-content:center;">
                {SVG_ICONS["sparkle"]}
            </div>
            <div>
                <h3 style="margin:0;font-size:.95rem;font-weight:800;color:#1A1210;letter-spacing:-.02em;">Inspector Studio</h3>
                <span style="font-size:.70rem;color:#9C8E84;font-weight:500;">Kontrol Evaluasi Inferensi</span>
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
        <div style="background:#1C1109;border:1px solid rgba(255,255,255,0.10);padding:13px;border-radius:11px;box-shadow:0 2px 8px rgba(0,0,0,0.25);">
            <span style="font-size:.68rem;color:#A8906E;font-weight:700;text-transform:uppercase;letter-spacing:.05em;display:flex;align-items:center;gap:5px;margin-bottom:7px;">
                {SVG_ICONS["database"]} Dataset USK-Coffee
            </span>
            <div style="font-size:.84rem;font-weight:700;color:#F5EDE3;margin-bottom:3px;">Arabika Gayo &amp; Aceh</div>
            <div style="font-size:.73rem;color:#A8906E;line-height:1.4;">Defect · Longberry · Peaberry · Premium</div>
        </div>
        """
        st.markdown(_clean_html(spec_badge), unsafe_allow_html=True)

    return model_mode


def render_footer() -> None:
    """Render footer — dark accent strip."""
    st.markdown("---")
    footer_html = f"""
    <div style="background:#1C1109;border-radius:12px;padding:14px 20px;margin-top:4px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:22px;height:22px;flex-shrink:0;display:inline-flex;align-items:center;justify-content:center;">{SVG_ICONS["logo"]}</div>
            <span style="font-size:.82rem;font-weight:700;color:#F5EDE3;">Arabica Vision AI Studio</span>
            <span style="color:rgba(255,255,255,0.15);">·</span>
            <span style="font-size:.78rem;font-weight:400;color:#A8906E;">Multi-Backbone Transfer Learning Engine</span>
        </div>
        <span style="font-size:.70rem;color:#6B5A44;font-family:'JetBrains Mono',monospace;">
            PyTorch 2.0 · Scikit-Learn · Streamlit · Altair
        </span>
    </div>
    """
    st.markdown(_clean_html(footer_html), unsafe_allow_html=True)
