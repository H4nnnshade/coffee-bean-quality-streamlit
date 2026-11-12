"""Streamlit UI layout, modern product design system, and shell structure."""

import streamlit as st


def _clean_html(raw: str) -> str:
    """Strip leading/trailing whitespace from each line to prevent Markdown code-block interpretation."""
    return "".join(line.strip() for line in raw.splitlines())


# Vector SVG Icons (Lucide / Feather Standard Specifications)
SVG_ICONS = {
    "logo": """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="32" height="32" rx="9" fill="url(#logo_grad)" />
        <path d="M16 6C10.477 6 6 10.477 6 16C6 21.523 10.477 26 16 26C21.523 26 26 21.523 26 16C26 10.477 21.523 6 16 6Z" fill="#78350F" fill-opacity="0.25"/>
        <path d="M16 8C13 12 13 20 16 24C19 20 19 12 16 8Z" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
        <circle cx="11" cy="13" r="1.5" fill="#FFFFFF"/>
        <circle cx="21" cy="19" r="1.5" fill="#FDE68A"/>
        <defs>
            <linearGradient id="logo_grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                <stop stop-color="#92400E" />
                <stop offset="1" stop-color="#451A03" />
            </linearGradient>
        </defs>
    </svg>""",
    "cpu": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>""",
    "database": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>""",
    "zap": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "target": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
    "shield_check": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>""",
    "sparkle": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>""",
}


def setup_page_config() -> None:
    """Set global Streamlit page configuration and inject modern luxury product design tokens."""
    st.set_page_config(
        page_title="Arabica Vision AI | Multi-Model CNN-SVM Studio",
        page_icon="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/coffee.svg",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject ultra-refined design system CSS (Linear, Resend, Stripe inspired)
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

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
        --brand-gold: #B45309;
        --brand-gold-glow: rgba(180, 83, 9, 0.12);
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

    /* Streamlit App Shell Header */
    header[data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(226, 232, 240, 0.85);
    }

    /* Streamlit Sidebar Polish */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
        border-right: 1px solid var(--border-subtle);
        box-shadow: 1px 0 12px rgba(15, 23, 42, 0.02);
    }

    /* Tabs Styling - Linear/Vercel Pill Navigation */
    div[data-testid="stTabs"] {
        margin-top: 10px;
    }
    div[data-testid="stTabs"] [role="tablist"] {
        gap: 8px;
        background: #F1F5F9;
        padding: 5px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
    div[data-testid="stTabs"] [data-testid="stTab"] {
        font-family: var(--font-sans);
        font-size: 0.86rem;
        font-weight: 600;
        color: #64748B;
        border-radius: 8px;
        padding: 8px 18px;
        border: none;
        background: transparent;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.06), 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Metric Cards - Multi-layered Depth */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02), 0 4px 10px -2px rgba(15, 23, 42, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.06);
    }
    div[data-testid="stMetricLabel"] {
        font-family: var(--font-sans) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #64748B !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em;
        color: var(--text-primary) !important;
    }

    /* Modern Dropzone */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important;
        border: 1.5px dashed #CBD5E1 !important;
        border-radius: 14px !important;
        padding: 30px 24px !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02) !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #3B82F6 !important;
        background-color: #F8FAFC !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
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
        margin: 24px 0 !important;
        border: none !important;
        border-top: 1px solid #E2E8F0 !important;
    }
    </style>
    """
    st.markdown(_clean_html(css), unsafe_allow_html=True)


def render_header() -> None:
    """Render executive hero header with custom SVG geometric logo and status indicators."""
    header_html = f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02), 0 6px 18px -4px rgba(15, 23, 42, 0.03);
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="
                    width: 52px;
                    height: 52px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 14px rgba(146, 64, 14, 0.18);
                    border-radius: 14px;
                ">
                    {SVG_ICONS["logo"]}
                </div>
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 3px;">
                        <h1 style="margin: 0; font-size: 1.85rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">
                            Arabica Vision AI
                        </h1>
                        <span style="
                            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
                            color: #334155;
                            font-size: 0.72rem;
                            font-weight: 700;
                            padding: 3px 10px;
                            border-radius: 9999px;
                            border: 1px solid #E2E8F0;
                            font-family: 'JetBrains Mono', monospace;
                        ">
                            v2.5 • Enterprise
                        </span>
                    </div>
                    <p style="margin: 0; font-size: 0.92rem; color: #64748B; font-weight: 500;">
                        Sistem Klasifikasi Cerdas Mutu Kopi • Penultimate Transfer Learning + Multi-Model SVM-RBF
                    </p>
                </div>
            </div>

            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    background: #F0FDF4;
                    border: 1px solid #BBF7D0;
                    padding: 6px 14px;
                    border-radius: 9999px;
                ">
                    <span style="
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        background-color: #10B981;
                        display: inline-block;
                        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25);
                    "></span>
                    <span style="font-size: 0.78rem; font-weight: 700; color: #166534; letter-spacing: 0.02em;">
                        Online • 3/3 Backbones
                    </span>
                </div>
                <div style="
                    background: #FFFBEB;
                    border: 1px solid #FDE68A;
                    color: #92400E;
                    font-size: 0.78rem;
                    font-weight: 700;
                    padding: 6px 14px;
                    border-radius: 9999px;
                    font-family: 'JetBrains Mono', monospace;
                ">
                    Split 60:20:20
                </div>
            </div>
        </div>

        <div style="
            display: flex;
            gap: 8px;
            margin-top: 16px;
            padding-top: 14px;
            border-top: 1px solid #F1F5F9;
            flex-wrap: wrap;
            align-items: center;
        ">
            <span style="background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 6px; font-size: 0.73rem; font-weight: 600; display: inline-flex; align-items: center; gap: 5px;">
                {SVG_ICONS["cpu"]} MobileNetV3 • ShuffleNetV2 • EfficientNet-B0
            </span>
            <span style="background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 6px; font-size: 0.73rem; font-weight: 600; display: inline-flex; align-items: center; gap: 5px;">
                {SVG_ICONS["target"]} One-vs-Rest SVM (RBF + Softmax Stabil)
            </span>
            <span style="background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 6px; font-size: 0.73rem; font-weight: 600; display: inline-flex; align-items: center; gap: 5px;">
                {SVG_ICONS["shield_check"]} Guardrails: CWE-400 (Max 16 MP) • CWE-79 Sanitized
            </span>
        </div>
    </div>
    """
    st.markdown(_clean_html(header_html), unsafe_allow_html=True)


def render_sidebar() -> str:
    """Render sidebar with mode selection and technical references in modern inspector aesthetic."""
    with st.sidebar:
        title_html = f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
            <div style="
                width: 32px;
                height: 32px;
                border-radius: 8px;
                background-color: #0F172A;
                color: #FFFFFF;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                {SVG_ICONS["sparkle"]}
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">
                    Inspector Studio
                </h3>
                <span style="font-size: 0.74rem; color: #64748B; font-weight: 500;">
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
            padding: 14px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02);
        ">
            <span style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                {SVG_ICONS["database"]} Dataset USK-Coffee
            </span>
            <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                Arabika Gayo & Aceh
            </div>
            <div style="font-size: 0.74rem; color: #64748B; line-height: 1.4;">
                Defect • Longberry • Peaberry • Premium
            </div>
        </div>
        """
        st.markdown(_clean_html(spec_badge), unsafe_allow_html=True)

    return model_mode


def render_footer() -> None:
    """Render modern luxury product footer."""
    st.markdown("---")
    footer_html = f"""
    <div style="
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        padding: 24px 0 20px 0;
        display: flex;
        flex-direction: column;
        gap: 8px;
        align-items: center;
    ">
        <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #0F172A;">
            <div style="width: 20px; height: 20px;">{SVG_ICONS["logo"]}</div>
            <span>Arabica Vision AI Studio</span>
            <span style="color: #CBD5E1;">•</span>
            <span style="font-weight: 500; color: #64748B;">Multi-Backbone Transfer Learning Engine</span>
        </div>
        <span style="font-size: 0.76rem; color: #94A3B8; font-family: 'JetBrains Mono', monospace;">
            PyTorch 2.0 • Scikit-Learn • Streamlit • Altair Graphics • Zero Memory Leak
        </span>
    </div>
    """
    st.markdown(_clean_html(footer_html), unsafe_allow_html=True)
