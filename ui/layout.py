"""Streamlit UI layout, modern product design system (Figma & Linear inspired), and shell structure."""

import streamlit as st


def _clean_html(raw: str) -> str:
    """Strip leading/trailing whitespace from each line to prevent Markdown code-block interpretation."""
    return "".join(line.strip() for line in raw.splitlines())


def setup_page_config() -> None:
    """Set global Streamlit page configuration and inject modern product design tokens."""
    st.set_page_config(
        page_title="Coffee Bean Quality AI | Multi-Model CNN-SVM",
        page_icon="☕",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject modern product design system CSS (Figma / Linear / Framer inspired)
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', ui-monospace, Menlo, Monaco, monospace;
        --bg-main: #F8FAFC;
        --bg-card: #FFFFFF;
        --border-subtle: #E2E8F0;
        --border-hover: #CBD5E1;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-muted: #94A3B8;
        --accent-amber: #B45309;
        --accent-amber-light: #FFFBEB;
    }

    html, body, [class*="css"] {
        font-family: var(--font-sans);
        color: var(--text-primary);
        background-color: var(--bg-main);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* App Header Bar - Translucent Frosted Glass */
    header[data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
    }

    /* Sidebar - Figma/Linear Inspector Style */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid var(--border-subtle);
        box-shadow: 1px 0 8px rgba(15, 23, 42, 0.02);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Product Card Surface with Subtle Ring Elevation */
    .product-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03), 0 4px 12px -2px rgba(15, 23, 42, 0.04);
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .product-card:hover {
        border-color: var(--border-hover);
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.04), 0 12px 24px -4px rgba(15, 23, 42, 0.06);
    }

    /* Modern Metric Widget */
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.02);
    }
    div[data-testid="stMetricLabel"] {
        font-family: var(--font-sans) !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: var(--text-primary) !important;
    }

    /* Interactive Upload Dropzone */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 14px !important;
        padding: 28px 20px !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #0F172A !important;
        background-color: #F8FAFC !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
    }

    /* Pill Badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    /* Code / Monospace Styling */
    code, pre {
        font-family: var(--font-mono) !important;
    }

    /* Altair Chart Container Clean Background */
    .stAltairChart {
        background-color: transparent !important;
    }

    /* Clean Dividers */
    hr {
        margin: 24px 0 !important;
        border: none !important;
        border-top: 1px solid #E2E8F0 !important;
    }

    /* Custom Radio styling in sidebar */
    div[data-testid="stRadio"] > label {
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        color: #334155 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    </style>
    """
    st.markdown(_clean_html(css), unsafe_allow_html=True)


def render_header() -> None:
    """Render modern product hero header with system status and architectural badges."""
    header_html = """
    <div style="margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid #E2E8F0;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="
                    width: 56px;
                    height: 56px;
                    border-radius: 16px;
                    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.85rem;
                    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.15), inset 0 1px 1px rgba(255, 255, 255, 0.2);
                ">
                    ☕
                </div>
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2px;">
                        <h1 style="margin: 0; font-size: 2.15rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">
                            Coffee Bean Quality AI
                        </h1>
                        <span style="
                            background-color: #F1F5F9;
                            color: #475569;
                            font-size: 0.72rem;
                            font-weight: 700;
                            padding: 3px 9px;
                            border-radius: 6px;
                            border: 1px solid #E2E8F0;
                            font-family: 'JetBrains Mono', monospace;
                        ">
                            v2.4 • Pro
                        </span>
                    </div>
                    <p style="margin: 0; font-size: 0.95rem; color: #64748B; font-weight: 500;">
                        Sistem Klasifikasi Cerdas Mutu Arabika • Transfer Learning Penultimate Layer + Multi-Model SVM (RBF)
                    </p>
                </div>
            </div>
            
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                padding: 6px 14px;
                border-radius: 9999px;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
            ">
                <span style="
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background-color: #10B981;
                    display: inline-block;
                    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
                "></span>
                <span style="font-size: 0.8rem; font-weight: 700; color: #0F172A; letter-spacing: 0.02em;">
                    Engine Status: Online
                </span>
                <span style="color: #CBD5E1;">|</span>
                <span style="font-size: 0.78rem; font-weight: 500; color: #64748B; font-family: 'JetBrains Mono', monospace;">
                    3/3 Backbones Loaded
                </span>
            </div>
        </div>

        <div style="display: flex; gap: 8px; margin-top: 16px; flex-wrap: wrap; align-items: center;">
            <span class="badge-pill" style="background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #B45309;"></span>
                Skenario Riset 60:20:20 (Stratified Split)
            </span>
            <span class="badge-pill" style="background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #2563EB;"></span>
                Backbones: MobileNetV3-Small • ShuffleNetV2 • EfficientNet-B0
            </span>
            <span class="badge-pill" style="background-color: #F1F5F9; color: #334155; border: 1px solid #E2E8F0;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #64748B;"></span>
                Classifier: One-vs-Rest SVM (RBF Kernel + Softmax Calibrated)
            </span>
            <span class="badge-pill" style="background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #059669;"></span>
                Security: Decompression Bomb Guard (Max 16 MP)
            </span>
        </div>
    </div>
    """
    st.markdown(_clean_html(header_html), unsafe_allow_html=True)


def render_sidebar() -> str:
    """Render sidebar with mode selection and technical references in modern inspector aesthetic."""
    with st.sidebar:
        title_html = """
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
                font-size: 1rem;
            ">
                ⚡
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.1rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">
                    Inspector & Controls
                </h3>
                <span style="font-size: 0.75rem; color: #64748B; font-weight: 500;">
                    Konfigurasi Pipeline Inferensi
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
        kamus_title_html = """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.1rem;">🏷️</span>
                <h4 style="margin: 0; font-size: 0.95rem; font-weight: 700; color: #0F172A;">
                    Kamus Mutu Arabika
                </h4>
            </div>
            <span style="font-size: 0.72rem; color: #64748B; font-family: 'JetBrains Mono', monospace;">
                4 Kelas
            </span>
        </div>
        """
        st.markdown(_clean_html(kamus_title_html), unsafe_allow_html=True)

        kamus_cards_html = """
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="background: #FFFFFF; border: 1px solid #FFE4E6; border-left: 4px solid #E11D48; padding: 12px 14px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="color: #BE123C; font-weight: 800; font-size: 0.85rem;">🔴 Defect</span>
                    <span style="font-size: 0.68rem; background: #FFF1F2; color: #E11D48; font-weight: 700; padding: 2px 6px; border-radius: 4px;">Cacat Fisik</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 0.78rem; color: #64748B; line-height: 1.35;">
                    Biji berlubang (hama bubuk), pecah, hitam, berjamur, atau keriput.
                </p>
            </div>
            <div style="background: #FFFFFF; border: 1px solid #FEF3C7; border-left: 4px solid #D97706; padding: 12px 14px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="color: #B45309; font-weight: 800; font-size: 0.85rem;">🟡 Longberry</span>
                    <span style="font-size: 0.68rem; background: #FFFBEB; color: #D97706; font-weight: 700; padding: 2px 6px; border-radius: 4px;">Varietas Khusus</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 0.78rem; color: #64748B; line-height: 1.35;">
                    Biji berbentuk fisik memanjang dan pipih berkarakter aroma khas.
                </p>
            </div>
            <div style="background: #FFFFFF; border: 1px solid #DBEAFE; border-left: 4px solid #2563EB; padding: 12px 14px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="color: #1D4ED8; font-weight: 800; font-size: 0.85rem;">🔵 Peaberry</span>
                    <span style="font-size: 0.68rem; background: #EFF6FF; color: #2563EB; font-weight: 700; padding: 2px 6px; border-radius: 4px;">Biji Lanang</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 0.78rem; color: #64748B; line-height: 1.35;">
                    Biji tunggal berbentuk bulat tanpa belahan akibat anomali alami (5–10% panen).
                </p>
            </div>
            <div style="background: #FFFFFF; border: 1px solid #D1FAE5; border-left: 4px solid #059669; padding: 12px 14px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="color: #047857; font-weight: 800; font-size: 0.85rem;">🟢 Premium</span>
                    <span style="font-size: 0.68rem; background: #ECFDF5; color: #059669; font-weight: 700; padding: 2px 6px; border-radius: 4px;">Mutu Pertama</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 0.78rem; color: #64748B; line-height: 1.35;">
                    Biji utuh simetris, seragam, ukuran ideal tanpa cacat fisik sedikitpun.
                </p>
            </div>
        </div>
        """
        st.markdown(_clean_html(kamus_cards_html), unsafe_allow_html=True)

        st.markdown("---")
        param_title_html = """
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="font-size: 1.1rem;">⚙️</span>
            <h4 style="margin: 0; font-size: 0.95rem; font-weight: 700; color: #0F172A;">
                Spesifikasi Arsitektur
            </h4>
        </div>
        """
        st.markdown(_clean_html(param_title_html), unsafe_allow_html=True)

        st.markdown(
            """
            | Parameter | Konfigurasi |
            |---|---|
            | **Tensor Resolusi** | `224 × 224 × 3 RGB` |
            | **Feature Layer** | Penultimate Pooling |
            | **MobileNetV3 Dim** | `1024-d float32` |
            | **ShuffleNetV2 Dim** | `1024-d float32` |
            | **EfficientNet Dim** | `1280-d float32` |
            | **Classifier Model** | SVM RBF (OvR) |
            | **Probabilitas** | Softmax Stabil |
            """
        )

        st.markdown("---")
        footer_badge = """
        <div style="
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
        ">
            <span style="font-size: 0.72rem; color: #64748B; font-weight: 600; display: block;">
                USK Coffee Quality Research Dataset
            </span>
            <span style="font-size: 0.7rem; color: #94A3B8; font-family: 'JetBrains Mono', monospace;">
                Transfer Learning • Scenario 60:20:20
            </span>
        </div>
        """
        st.markdown(_clean_html(footer_badge), unsafe_allow_html=True)

    return model_mode


def render_footer() -> None:
    """Render modern product footer."""
    st.markdown("---")
    footer_html = """
    <div style="
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        padding: 24px 0 16px 0;
        display: flex;
        flex-direction: column;
        gap: 6px;
        align-items: center;
    ">
        <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #0F172A;">
            <span>☕ Coffee Bean Quality AI</span>
            <span style="color: #CBD5E1;">•</span>
            <span style="font-weight: 500; color: #64748B;">Multi-Backbone Transfer Learning Engine</span>
        </div>
        <span style="font-size: 0.78rem; color: #94A3B8; font-family: 'JetBrains Mono', monospace;">
            Streamlit • PyTorch • Scikit-Learn • Altair • Built with Clean Architecture
        </span>
    </div>
    """
    st.markdown(_clean_html(footer_html), unsafe_allow_html=True)
