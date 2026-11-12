"""Streamlit UI layout and shell structure."""

import streamlit as st


def setup_page_config() -> None:
    """Set global Streamlit page configuration."""
    st.set_page_config(
        page_title="Klasifikasi Mutu Biji Kopi | Hybrid CNN-SVM",
        page_icon="☕",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_header() -> None:
    """Render page title and subheader with system metadata."""
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                <span style="font-size: 2.2rem;">☕</span>
                <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #111827;">
                    Sistem Klasifikasi Mutu Biji Kopi
                </h1>
            </div>
            <p style="margin: 4px 0 0 0; font-size: 1.05rem; color: #4B5563;">
                Inferensi mutu 4 kelas (Defect, Longberry, Peaberry, Premium) berbasis 
                <b>Transfer Learning Penultimate Layer + SVM (RBF)</b>.
            </p>
            <div style="display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;">
                <span style="background-color: #EEF2FF; color: #4338CA; padding: 4px 10px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;">
                    Skenario 60:20:20
                </span>
                <span style="background-color: #ECFDF5; color: #047857; padding: 4px 10px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;">
                    Backbone: MobileNetV3 | ShuffleNetV2 | EfficientNet-B0
                </span>
                <span style="background-color: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;">
                    Classifier: SVM One-vs-Rest (RBF)
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")


def render_sidebar() -> str:
    """Render sidebar with mode selection and technical references."""
    with st.sidebar:
        st.header("⚙️ Konfigurasi Model")
        model_mode = st.radio(
            "Pilih Mode Inferensi:",
            options=[
                "Perbandingan Semua Model (3 Model)",
                "MobileNetV3-Small (Cepat & Ringan)",
                "ShuffleNetV2 (Optimal Mobile)",
                "EfficientNet-B0 (Representasi Tinggi)",
            ],
            index=0,
            help="Pilih apakah ingin menjalankan inferensi pada satu model spesifik atau membandingkan ketiganya secara paralel.",
        )

        st.markdown("---")
        st.subheader("📖 Definisi Kelas Mutu Kopi")
        st.markdown(
            """
            - **Defect**: Biji cacat fisik, berlubang karena serangga, pecah, hitam, atau berjamur.
            - **Longberry**: Biji kopi varietas khusus dengan karakteristik bentuk memanjang pipih.
            - **Peaberry**: Biji kopi tunggal (*lanang*) berbentuk bulat utuh tanpa belahan.
            - **Premium**: Biji kopi utuh berkualitas tinggi, simetris, tanpa cacat fisik.
            """
        )

        st.markdown("---")
        st.subheader("🔬 Spesifikasi Arsitektur")
        st.markdown(
            """
            | Parameter | Keterangan |
            |---|---|
            | **Input Tensor** | 224 x 224 px RGB |
            | **Ekstraksi Fitur** | Penultimate Pooling Layer |
            | **MobileNetV3 Dim** | 1024 float |
            | **ShuffleNetV2 Dim** | 1024 float |
            | **EfficientNet-B0 Dim** | 1280 float |
            | **Normalisasi Skor** | Softmax Numerik Stabil |
            """
        )

        st.markdown("---")
        st.caption("Klasifikasi Mutu Kopi v1.0 | Riset Skripsi Skenario 60:20:20")

    return model_mode


def render_footer() -> None:
    """Render page footer."""
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #6B7280; font-size: 0.85rem; padding: 16px 0;">
            Aplikasi Klasifikasi Mutu Biji Kopi &copy; 2026. Dikembangkan dengan Streamlit, PyTorch, dan Scikit-Learn.
        </div>
        """,
        unsafe_allow_html=True,
    )
