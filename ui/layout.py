"""Streamlit UI layout, modern product design system, and compact shell structure."""

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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', ui-monospace, Menlo, Monaco, monospace;
        --bg-main: #F8FAFC;
        --bg-surface: #FFFFFF;
        --border-subtle: #E2E8F0;
        --border-medium: #CBD5E1;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-tertiary: #94A3B8;
        --brand-amber: #92400E;
        --brand-amber-dark: #451A03;
        --brand-gold: #D97706;
        --brand-gold-subtle: rgba(217, 119, 6, 0.08);
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

    /* Compact root container padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1320px !important;
    }

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

    /* Tabs Styling - Linear / Vercel Compact Pill Navigation */
    div[data-testid="stTabs"] {
        margin-top: 6px;
    }
    div[data-testid="stTabs"] [role="tablist"] {
        gap: 6px;
        background: #F1F5F9;
        padding: 4px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    div[data-testid="stTabs"] [data-testid="stTab"] {
        font-family: var(--font-sans);
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        border-radius: 7px;
        padding: 6px 14px;
        border: none;
        background: transparent;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
        height: auto;
    }
    div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08), 0 2px 6px rgba(15, 23, 42, 0.04) !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Metric Cards - Multi-layered Depth & Compact Density */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 12px 14px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 2px 8px -1px rgba(15, 23, 42, 0.03);
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1);
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
        border-color: #92400E !important;
        background-color: #FFFDF9 !important;
        box-shadow: 0 0 0 3px rgba(146, 64, 14, 0.08), 0 4px 12px rgba(146, 64, 14, 0.04) !important;
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

    /* Monospace formatting */
    code, pre {
        font-family: var(--font-mono) !important;
    }

    /* Table & Chart Container */
    .stAltairChart {
        background-color: transparent !important;
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
    """Render executive hero header with centered website title flanked symmetrically by brand logos."""
    header_html = f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02), 0 4px 12px -2px rgba(15, 23, 42, 0.03);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #78350F 0%, #D97706 50%, #B45309 100%);
        "></div>
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap;">
            <!-- Left Brand Logo -->
            <div style="
                width: 44px;
                height: 44px;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                filter: drop-shadow(0 3px 8px rgba(120, 53, 15, 0.20));
            ">
                {SVG_ICONS["logo"]}
            </div>

            <!-- Centered Website Name, Status, and Subtitle -->
            <div style="flex: 1; min-width: 280px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
                    <h1 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">
                        Arabica Vision AI
                    </h1>
                    <span style="
                        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
                        color: #92400E;
                        font-size: 0.68rem;
                        font-weight: 700;
                        padding: 2px 8px;
                        border-radius: 9999px;
                        border: 1px solid #FDE68A;
                        font-family: 'JetBrains Mono', monospace;
                    ">
                        v2.5 • Studio
                    </span>
                    <div style="
                        display: inline-flex;
                        align-items: center;
                        gap: 5px;
                        background: #F0FDF4;
                        border: 1px solid #BBF7D0;
                        padding: 2px 8px;
                        border-radius: 9999px;
                    ">
                        <span style="
                            width: 6.5px;
                            height: 6.5px;
                            border-radius: 50%;
                            background-color: #10B981;
                            display: inline-block;
                            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
                        "></span>
                        <span style="font-size: 0.70rem; font-weight: 700; color: #166534; letter-spacing: 0.02em;">
                            Online • 3 Backbones
                        </span>
                    </div>
                    <div style="
                        background: #FFFBEB;
                        border: 1px solid #FDE68A;
                        color: #92400E;
                        font-size: 0.70rem;
                        font-weight: 700;
                        padding: 2px 8px;
                        border-radius: 9999px;
                        font-family: 'JetBrains Mono', monospace;
                    ">
                        Split 60:20:20
                    </div>
                </div>
                <p style="margin: 0; font-size: 0.82rem; color: #64748B; font-weight: 500;">
                    Klasifikasi Cerdas 4 Mutu Kopi • Penultimate CNN Feature Extraction + Support Vector Machine RBF
                </p>
            </div>

            <!-- Right Brand Logo -->
            <div style="
                width: 44px;
                height: 44px;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                filter: drop-shadow(0 3px 8px rgba(120, 53, 15, 0.20));
            ">
                {SVG_ICONS["logo"]}
            </div>
        </div>

        <div style="
            display: flex;
            gap: 8px;
            margin-top: 12px;
            padding-top: 10px;
            border-top: 1px solid #F1F5F9;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
        ">
            <span style="background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; padding: 3px 8px; border-radius: 6px; font-size: 0.70rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
                {SVG_ICONS["cpu"]} MobileNetV3 • ShuffleNetV2 • EfficientNet-B0
            </span>
            <span style="background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; padding: 3px 8px; border-radius: 6px; font-size: 0.70rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
                {SVG_ICONS["target"]} One-vs-Rest SVM (RBF + Numerically Stable Softmax)
            </span>
            <span style="background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; padding: 3px 8px; border-radius: 6px; font-size: 0.70rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
                {SVG_ICONS["shield_check"]} Defense-in-Depth: CWE-400 (16 MP) • CWE-79 Sanitized
            </span>
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
