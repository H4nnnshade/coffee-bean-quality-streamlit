"""Streamlit UI components for coffee bean quality classification."""

from typing import Any, List, Optional
import html
import logging
import pandas as pd
import altair as alt
import streamlit as st
from PIL import Image

# Import constants & schemas from core
try:
    from core.constants import (
        ALLOWED_EXTENSIONS,
        CLASS_COLORS,
        MAX_FILE_SIZE_MB,
        MAX_IMAGE_PIXELS,
    )
    from core.schemas import ModelInferenceOutput
except ImportError:
    ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
    MAX_FILE_SIZE_MB = 10
    MAX_IMAGE_PIXELS = 4096 * 4096
    CLASS_COLORS = {
        "defect": "#DC2626",
        "longberry": "#D97706",
        "peaberry": "#2563EB",
        "premium": "#059669",
    }
    ModelInferenceOutput = Any  # type: ignore

# Security Guard: Prevent decompression bomb DoS attacks (CWE-400)
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


def render_uploader() -> Optional[Image.Image]:
    """Render drag-and-drop file uploader with security validation."""
    uploaded_file = st.file_uploader(
        "Unggah Citra Biji Kopi",
        type=ALLOWED_EXTENSIONS,
        help=f"Mendukung format JPG, JPEG, PNG, WEBP (Maksimal {MAX_FILE_SIZE_MB} MB)",
        key="coffee_image_uploader",
    )

    if uploaded_file is None:
        return None

    # 1. Zero-bloat size check (avoids duplicating byte buffer into RAM)
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if getattr(uploaded_file, "size", 0) > max_bytes:
        st.error(
            f"Ukuran file melebihi batas maksimal {MAX_FILE_SIZE_MB} MB. "
            "Silakan unggah citra yang lebih kecil."
        )
        return None

    try:
        # Pass file-like object directly into PIL without full buffer duplication
        image = Image.open(uploaded_file)

        # 2. Magic bytes format validation
        img_format = (image.format or "").lower()
        if img_format not in ["jpeg", "jpg", "png", "webp"]:
            st.error("Format berkas tidak valid atau rusak. Hanya menerima JPG, PNG, atau WEBP.")
            return None

        # 3. Resolution ceiling validation (prevents massive memory expansion on convert)
        pixel_count = image.width * image.height
        if pixel_count > MAX_IMAGE_PIXELS:
            st.error("Dimensi citra terlalu besar (maksimal resolusi 4096 x 4096 px).")
            return None

        return image.convert("RGB")

    except Image.DecompressionBombError:
        logging.error("Decompression bomb rejected during upload.", exc_info=True)
        st.error("Citra ditolak: Terdeteksi risiko dekompresi berbahaya (Decompression Bomb).")
        return None
    except Exception as exc:
        logging.error(f"Image read error: {exc}", exc_info=True)
        st.error("Gagal membaca berkas citra. Pastikan berkas adalah gambar valid dan tidak rusak.")
        return None


def render_image_preview(image: Image.Image) -> None:
    """Render image preview inside a clean container."""
    st.subheader("Citra Biji Kopi")
    st.image(
        image,
        caption=f"Resolusi: {image.width}x{image.height} px | Format: RGB",
        use_container_width=True,
    )


def render_probability_chart(probabilities: list) -> None:
    """Render horizontal bar chart for class probabilities using Altair."""
    data = []
    for item in probabilities:
        if isinstance(item, dict):
            label = str(item.get("label", ""))
            disp = str(item.get("display_name", label))
            score = float(item.get("score", 0.0))
        else:
            label = str(getattr(item, "label", ""))
            disp = str(getattr(item, "display_name", label))
            score = float(getattr(item, "score", 0.0))
        data.append({
            "Kelas": disp,
            "Probabilitas": score * 100,
            "LabelKey": label.lower(),
        })

    df = pd.DataFrame(data)

    color_scale = alt.Scale(
        domain=list(CLASS_COLORS.keys()),
        range=list(CLASS_COLORS.values()),
    )

    bars = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            x=alt.X(
                "Probabilitas:Q",
                scale=alt.Scale(domain=[0, 100]),
                title="Probabilitas (%)",
                axis=alt.Axis(format=".1f"),
            ),
            y=alt.Y(
                "Kelas:N",
                sort=alt.EncodingSortField(field="Probabilitas", order="descending"),
                title=None,
            ),
            color=alt.Color("LabelKey:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("Kelas:N"),
                alt.Tooltip("Probabilitas:Q", format=".2f", title="Probabilitas (%)"),
            ],
        )
    )

    text = (
        alt.Chart(df)
        .mark_text(
            align="left",
            baseline="middle",
            dx=5,
            fontSize=12,
            fontWeight="bold",
        )
        .encode(
            x=alt.X("Probabilitas:Q"),
            y=alt.Y("Kelas:N", sort=alt.EncodingSortField(field="Probabilitas", order="descending")),
            text=alt.Text("Probabilitas:Q", format=".1f"),
        )
    )

    chart = (bars + text).properties(height=200).configure_view(strokeWidth=0)
    st.altair_chart(chart, use_container_width=True)


def render_prediction_badge(display_name: str, confidence: float, class_key: str) -> None:
    """Render prominent prediction card with XSS sanitization (CWE-79)."""
    safe_name = html.escape(str(display_name))
    color = CLASS_COLORS.get(class_key.lower(), "#2563EB")
    st.markdown(
        f"""
        <div style="
            background-color: {color}15;
            border-left: 6px solid {color};
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 16px;
        ">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: {color}; font-weight: 700;">
                Prediksi Mutu Utama
            </span>
            <h2 style="margin: 4px 0 6px 0; color: {color}; font-size: 2rem; font-weight: 800;">
                {safe_name}
            </h2>
            <span style="font-size: 1.05rem; font-weight: 600; color: #374151;">
                Tingkat Keyakinan: <b>{confidence * 100:.2f}%</b>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_model_result_card(result: Any) -> None:
    """Render single model inference result card."""
    model_name = getattr(result, "model_name", "Model")
    pred_class = getattr(result, "predicted_class", "unknown")
    disp_name = getattr(result, "display_name", pred_class)
    conf = float(getattr(result, "confidence", 0.0))
    probs = getattr(result, "probabilities", [])
    lat = float(getattr(result, "inference_time_ms", 0.0))

    with st.container():
        st.markdown(f"### {model_name}")
        render_prediction_badge(disp_name, conf, pred_class)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Confidence", f"{conf * 100:.2f}%")
        with col2:
            st.metric("Latensi Inferensi", f"{lat:.1f} ms")

        st.caption("Distribusi Probabilitas Kelas:")
        render_probability_chart(probs)


def render_comparison_section(results: List[Any]) -> None:
    """Render side-by-side comparison for multiple models."""
    st.markdown("## Perbandingan Hasil Antar Model")
    st.markdown(
        "Evaluasi konsistensi prediksi inferensi pada 3 arsitektur CNN Backbone yang berbeda:"
    )

    # 1. Summary comparison table
    table_data = []
    for r in results:
        table_data.append({
            "Arsitektur Model": getattr(r, "model_name", ""),
            "Prediksi Mutu": getattr(r, "display_name", ""),
            "Confidence": f"{getattr(r, 'confidence', 0.0) * 100:.2f}%",
            "Latensi (ms)": f"{getattr(r, 'inference_time_ms', 0.0):.1f} ms",
        })

    st.dataframe(
        pd.DataFrame(table_data),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("---")

    # 2. Side-by-side 3 columns
    cols = st.columns(len(results))
    for idx, (col, r) in enumerate(zip(cols, results)):
        with col:
            render_model_result_card(r)


# State handlers
def render_idle_state() -> None:
    """Render view when waiting for user to upload image."""
    st.info(
        "**Siap Menganalisis.** Silakan unggah foto biji kopi melalui panel uploader di sebelah kiri "
        "untuk memulai klasifikasi mutu otomatis berbasis CNN-SVM.",
        icon="ℹ️",
    )
    with st.expander("Panduan Pengambilan Citra Biji Kopi Optimal", expanded=True):
        st.markdown(
            """
            - **Pencahayaan Cukup**: Hindari bayangan tajam yang menutupi permukaan biji.
            - **Latar Belakang Netral**: Gunakan alas berwarna putih atau gelap polos untuk kontras maksimal.
            - **Jarak Fokus Presisi**: Pastikan tekstur permukaan biji terlihat jelas (tidak buram/blur).
            - **Satu Biji Per Foto**: Untuk akurasi klasifikasi tertinggi, posisikan 1 biji kopi di tengah frame.
            """
        )


def render_loading_state() -> Any:
    """Context manager / element for loading state."""
    return st.spinner("Memproses ekstraksi fitur CNN dan klasifikasi SVM...")


def render_empty_state() -> None:
    """Render view when file uploaded is empty or reset."""
    st.warning("Belum ada citra biji kopi yang diunggah. Silakan pilih berkas citra terlebih dahulu.")


def render_error_state(error_message: str) -> None:
    """Render user-friendly error box without exposing internal stack trace (CWE-209)."""
    st.error(f"Terjadi kendala: {error_message}")
    st.button("Muat Ulang Halaman", on_click=lambda: st.rerun())
