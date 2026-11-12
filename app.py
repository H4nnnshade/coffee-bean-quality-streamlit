"""Main application entry point for Coffee Bean Quality Classification Web App."""

import logging
import streamlit as st

from ui.layout import (
    setup_page_config,
    render_header,
    render_footer,
)
from ui.components import (
    render_kpi_metrics_bar,
    render_uploader,
    render_image_metadata,
    render_image_preview,
    render_model_result_card,
    render_comparison_section,
    render_visual_dictionary_deck,
    render_idle_state,
    render_error_state,
)

# Configure internal server logging (safe from exposing internal path to UI)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# 1. Page Configuration
setup_page_config()

# 2. Header
render_header()

# 3. Top Executive KPI Bar
render_kpi_metrics_bar()

# 4. Primary Knowledge Hub: Standar Mutu Biji Kopi di Awal (Obsidian Dark Deck)
render_visual_dictionary_deck()

# 5. Core Testing & Inspection Space (Dashboard Area)
col_input, col_meta = st.columns([1, 1], gap="medium")

with col_input:
    image = render_uploader()
    if image is not None:
        render_image_metadata(image)

with col_meta:
    if image is not None:
        render_image_preview(image)
    else:
        st.markdown(
            """
            <div style="
                background: #F8FAFC;
                border: 1.5px dashed #CBD5E1;
                border-radius: 12px;
                padding: 24px 14px;
                text-align: center;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            ">
                <div style="color: #94A3B8; margin-bottom: 6px;">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
                </div>
                <span style="font-size: 0.85rem; font-weight: 700; color: #334155; margin-bottom: 3px;">
                    Pratinjau Citra Belum Tersedia
                </span>
                <span style="font-size: 0.72rem; color: #94A3B8; max-width: 280px; line-height: 1.4;">
                    Pilih atau jatuhkan berkas foto biji kopi pada zona drop di sebelah kiri untuk inspeksi dimensi dan ekstraksi fitur CNN.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# 6. Core Analytics Workspace (Pristine Compact Tabs)
tab_multi, tab_single = st.tabs([
    "Evaluasi Komparasi Multi-Model (Side-by-Side)",
    "Analisis Model Tunggal & Probabilitas",
])

with tab_multi:
    if image is None:
        render_idle_state()
    else:
        try:
            with st.spinner("Mengekstraksi representasi fitur 3 CNN & menjalankan inferensi SVM..."):
                try:
                    from services.predictor import predict_all_models
                except ImportError:
                    logging.error("Backend services missing", exc_info=True)
                    st.warning(
                        "Layanan backend inferensi sedang disiapkan oleh tim backend (@padolo). "
                        "Silakan pastikan modul `services.predictor` telah siap."
                    )
                    st.stop()

                results = predict_all_models(image)
                render_comparison_section(results)

        except Exception as exc:
            logging.error(f"Inference pipeline execution error: {exc}", exc_info=True)
            render_error_state("Gagal memproses klasifikasi citra. Silakan coba kembali atau periksa masukan.")

with tab_single:
    st.markdown("#### Pilih Arsitektur Backbone untuk Analisis Mendalam")
    selected_backbone = st.radio(
        "Arsitektur:",
        ["MobileNetV3-Small", "ShuffleNetV2", "EfficientNet-B0"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if image is None:
        st.info("Silakan unggah citra biji kopi di atas untuk mengevaluasi arsitektur ini secara mendalam.")
    else:
        try:
            with st.spinner(f"Menjalankan inferensi pada {selected_backbone}..."):
                from services.predictor import predict_single_model
                res = predict_single_model(image, selected_backbone)
                render_model_result_card(res, show_chart=True)
        except Exception as exc:
            logging.error(f"Single model execution error: {exc}", exc_info=True)
            render_error_state("Gagal memproses model tunggal.")

# 7. Minimalist Luxury Product Footer
render_footer()
