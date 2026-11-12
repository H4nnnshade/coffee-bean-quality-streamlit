"""Streamlit UI layout, modern light design system, and shell structure."""

import streamlit as st


def _clean_html(raw: str) -> str:
    """Strip leading/trailing whitespace from each line to prevent Markdown code-block interpretation."""
    return "".join(line.strip() for line in raw.splitlines())


def setup_page_config() -> None:
    """Set global Streamlit page configuration and inject modern light design tokens."""
    st.set_page_config(
        page_title="Klasifikasi Mutu Biji Kopi | Hybrid CNN-SVM",
        page_icon="☕",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject modern light theme CSS stylesheet
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
        background-color: #F8FAFC;
    }

    header[data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.85);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #E2E8F0;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.02);
    }

    .coffee-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .coffee-card:hover {
        box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.06), 0 4px 8px -2px rgba(0, 0, 0, 0.03);
        border-color: #CBD5E1;
    }

    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 16px;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    section[data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 24px 16px !important;
        transition: border-color 0.2s ease, background-color 0.2s ease;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #B45309 !important;
        background-color: #FFFBEB !important;
    }

    .stAltairChart {
        background-color: transparent !important;
    }

    hr {
        margin: 20px 0 !important;
        border-color: #E2E8F0 !important;
    }
    </style>
    """
    st.markdown(_clean_html(css), unsafe_allow_html=True)


def render_header() -> None:
    """Render modern light hero header with system metadata and badges."""
    header_html = """
    <div style="margin-bottom: 24px; padding: 4px 0;">
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
            <div style="
                width: 52px;
                height: 52px;
                border-radius: 14px;
                background: linear-gradient(135deg, #B45309 0%, #78350F 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.8rem;
                box-shadow: 0 4px 12px rgba(180, 83, 9, 0.25);
            ">
                ☕
            </div>
            <div>
                <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">
                    Klasifikasi Mutu Biji Kopi
                </h1>
                <p style="margin: 2px 0 0 0; font-size: 0.98rem; color: #64748B; font-weight: 500;">
                    Sistem Inferensi Mutu Arabika Berbasis <b>Transfer Learning Penultimate Layer + SVM (RBF)</b>
                </p>
            </div>
        </div>
        
        <div style="display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; align-items: center;">
            <span class="pill-badge" style="background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background-color: #B45309; display: inline-block;"></span>
                Skenario Riset 60:20:20
            </span>
            <span class="pill-badge" style="background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background-color: #2563EB; display: inline-block;"></span>
                3 Backbone CNN: MobileNetV3 | ShuffleNetV2 | EfficientNet-B0
            </span>
            <span class="pill-badge" style="background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background-color: #059669; display: inline-block;"></span>
                Classifier: SVM One-vs-Rest (RBF)
            </span>
        </div>
    </div>
    """
    st.markdown(_clean_html(header_html), unsafe_allow_html=True)
    st.markdown("---")


def render_sidebar() -> str:
    """Render sidebar with mode selection and technical references in light aesthetic."""
    with st.sidebar:
        title_html = """
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
            <span style="font-size: 1.4rem;">⚙️</span>
            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #0F172A;">
                Pengaturan Model
            </h3>
        </div>
        """
        st.markdown(_clean_html(title_html), unsafe_allow_html=True)

        model_mode = st.radio(
            "Pilih Mode Inferensi:",
            options=[
                "Perbandingan Semua Model (3 Model)",
                "MobileNetV3-Small (Cepat & Ringan)",
                "ShuffleNetV2 (Optimal Mobile)",
                "EfficientNet-B0 (Representasi Tinggi)",
            ],
            index=0,
            help="Pilih apakah ingin mengevaluasi 3 arsitektur sekaligus secara komparatif atau menjalankan inferensi tunggal.",
        )

        st.markdown("---")
        kamus_title_html = """
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span style="font-size: 1.2rem;">📖</span>
            <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #0F172A;">
                Kamus Mutu Kopi
            </h4>
        </div>
        """
        st.markdown(_clean_html(kamus_title_html), unsafe_allow_html=True)

        kamus_cards_html = """
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="background: #FFF1F2; border: 1px solid #FFE4E6; padding: 10px 12px; border-radius: 8px;">
                <span style="color: #BE123C; font-weight: 700; font-size: 0.85rem;">🔴 Defect</span>
                <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #4C0519; line-height: 1.3;">
                    Biji cacat fisik, berlubang karena serangga, pecah, hitam, atau berjamur.
                </p>
            </div>
            <div style="background: #FFFBEB; border: 1px solid #FEF3C7; padding: 10px 12px; border-radius: 8px;">
                <span style="color: #B45309; font-weight: 700; font-size: 0.85rem;">🟡 Longberry</span>
                <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #78350F; line-height: 1.3;">
                    Biji varietas khusus berkarakter bentuk memanjang dan pipih.
                </p>
            </div>
            <div style="background: #EFF6FF; border: 1px solid #DBEAFE; padding: 10px 12px; border-radius: 8px;">
                <span style="color: #1D4ED8; font-weight: 700; font-size: 0.85rem;">🔵 Peaberry</span>
                <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #1E3A8A; line-height: 1.3;">
                    Biji tunggal (lanang) berbentuk bulat utuh tanpa belahan.
                </p>
            </div>
            <div style="background: #ECFDF5; border: 1px solid #D1FAE5; padding: 10px 12px; border-radius: 8px;">
                <span style="color: #047857; font-weight: 700; font-size: 0.85rem;">🟢 Premium</span>
                <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #064E3B; line-height: 1.3;">
                    Biji utuh berkualitas tinggi, simetris, seragam, tanpa cacat fisik.
                </p>
            </div>
        </div>
        """
        st.markdown(_clean_html(kamus_cards_html), unsafe_allow_html=True)

        st.markdown("---")
        param_title_html = """
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="font-size: 1.2rem;">🔬</span>
            <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #0F172A;">
                Parameter Teknis
            </h4>
        </div>
        """
        st.markdown(_clean_html(param_title_html), unsafe_allow_html=True)

        st.markdown(
            """
            | Parameter | Konfigurasi |
            |---|---|
            | **Input Tensor** | 224 x 224 px RGB |
            | **Feature Layer** | Penultimate Pooling |
            | **MobileNetV3 Dim** | 1024 float |
            | **ShuffleNetV2 Dim** | 1024 float |
            | **EfficientNet-B0 Dim** | 1280 float |
            | **Decision Function** | Softmax Numerik Stabil |
            """
        )

        st.markdown("---")
        st.caption("Klasifikasi Mutu Kopi Arabika • Skenario 60:20:20 • Streamlit Light Edition")

    return model_mode


def render_footer() -> None:
    """Render modern clean footer."""
    st.markdown("---")
    footer_html = """
    <div style="
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        padding: 20px 0 10px 0;
        display: flex;
        flex-direction: column;
        gap: 4px;
        align-items: center;
    ">
        <span style="font-weight: 600; color: #334155;">
            Aplikasi Web Klasifikasi Mutu Biji Kopi Arabika &copy; 2026
        </span>
        <span style="font-size: 0.78rem; color: #94A3B8;">
            Dibangun dengan Streamlit • PyTorch • Scikit-Learn • Altair Visualization
        </span>
    </div>
    """
    st.markdown(_clean_html(footer_html), unsafe_allow_html=True)
