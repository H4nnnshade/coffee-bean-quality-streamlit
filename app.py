"""Main application entry point for Coffee Bean Quality Classification Web App."""

import logging
import streamlit as st

from ui.layout import (
    setup_page_config,
    render_header,
    render_footer,
)
from ui.components import (
    render_uploader,
    render_image_metadata,
    render_image_preview,
    render_model_result_card,
    render_primary_quality_result,
    render_comparison_section,
    render_visual_dictionary_deck,
    render_architecture_specs_tab,
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

# 2. Compact brand header and task introduction
render_header()
st.markdown(
    """<div class='lab-intro'>
    <h1>Analisis mutu biji kopi</h1>
    <p>Unggah citra Arabika untuk meninjau mutu, probabilitas model, dan karakter visual dalam satu ruang kerja.</p>
    </div>""",
    unsafe_allow_html=True,
)

# Main inspection workspace. Uploaded image validation and inference calls stay unchanged.
st.markdown("## Periksa sampel")
col_input, col_meta = st.columns([0.88, 1.12], gap="large")

with col_input:
    image = render_uploader()
    if image is not None:
        render_image_metadata(image)

with col_meta:
    if image is not None:
        render_image_preview(image)
    else:
        st.markdown(
            "<div class='preview-empty'><strong>Pratinjau citra belum tersedia</strong><span>Unggah citra untuk melihat sampel.</span></div>",
            unsafe_allow_html=True,
        )

# 5. Primary quality result and supporting analysis. Inference branches remain unchanged.
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
            # Primary panel and supporting analysis consume actual inference outputs.
            render_primary_quality_result(results)
            with st.expander("Probabilitas & perbandingan model", expanded=True):
                render_comparison_section(results)

    except Exception as exc:
        logging.error(f"Inference pipeline execution error: {exc}", exc_info=True)
        render_error_state("Gagal memproses klasifikasi citra. Silakan coba kembali atau periksa masukan.")

# Secondary analyses and reference material retain existing result contracts.
with st.expander("Analisis model tunggal", expanded=False):
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
                render_model_result_card(res)
        except Exception as exc:
            logging.error(f"Single model execution error: {exc}", exc_info=True)
            render_error_state("Gagal memproses model tunggal.")

with st.expander("Kamus mutu kopi Arabika", expanded=False):
    render_visual_dictionary_deck()

with st.expander("Spesifikasi riset & arsitektur", expanded=False):
    render_architecture_specs_tab()

# 6. Minimalist Luxury Product Footer
render_footer()
