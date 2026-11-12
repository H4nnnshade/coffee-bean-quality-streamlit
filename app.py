"""Main application entry point for Coffee Bean Quality Classification Web App."""

import logging
import streamlit as st

from ui.layout import (
    setup_page_config,
    render_header,
    render_sidebar,
    render_footer,
)
from ui.components import (
    render_uploader,
    render_image_preview,
    render_model_result_card,
    render_comparison_section,
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

# 2. Header & Navigation
render_header()
selected_mode = render_sidebar()

# 3. Main Workspace Layout
col_upload, col_result = st.columns([1, 1.3], gap="large")

with col_upload:
    image = render_uploader()
    if image is not None:
        render_image_preview(image)

with col_result:
    if image is None:
        # State: Idle
        render_idle_state()
    else:
        # State: Loading & Prediction
        try:
            with st.spinner("Mengekstraksi representasi fitur & menjalankan inferensi SVM..."):
                try:
                    from services.predictor import (
                        predict_all_models,
                        predict_single_model,
                    )
                except ImportError as ie:
                    logging.error("Backend services missing", exc_info=True)
                    st.warning(
                        "Layanan backend inferensi sedang disiapkan oleh tim backend (@padolo). "
                        "Silakan pastikan modul `services.predictor` telah siap."
                    )
                    st.stop()

                if "Perbandingan Semua Model" in selected_mode:
                    results = predict_all_models(image)
                    render_comparison_section(results)
                else:
                    if "MobileNetV3" in selected_mode:
                        model_key = "MobileNetV3-Small"
                    elif "ShuffleNetV2" in selected_mode:
                        model_key = "ShuffleNetV2"
                    else:
                        model_key = "EfficientNet-B0"

                    result = predict_single_model(image, model_key)
                    st.markdown("## Hasil Klasifikasi")
                    render_model_result_card(result)

        except Exception as exc:
            # Internal log with full traceback (CWE-209 protection)
            logging.error(f"Inference pipeline execution error: {exc}", exc_info=True)
            render_error_state("Gagal memproses klasifikasi citra. Silakan coba kembali atau periksa masukan.")

# 4. Footer
render_footer()
