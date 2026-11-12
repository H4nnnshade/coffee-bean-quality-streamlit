"""Streamlit UI components for coffee bean quality classification (Modern Product Design System)."""

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
        "defect": "#E11D48",
        "longberry": "#D97706",
        "peaberry": "#2563EB",
        "premium": "#059669",
    }
    ModelInferenceOutput = Any  # type: ignore

# Security Guard: Prevent decompression bomb DoS attacks (CWE-400)
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

# Class styling dictionaries for modern product UI
CLASS_LIGHT_BG = {
    "defect": "#FFF1F2",
    "longberry": "#FFFBEB",
    "peaberry": "#EFF6FF",
    "premium": "#ECFDF5",
}
CLASS_LIGHT_BORDER = {
    "defect": "#FECDD3",
    "longberry": "#FDE68A",
    "peaberry": "#BFDBFE",
    "premium": "#A7F3D0",
}
CLASS_DESCRIPTIONS = {
    "defect": "Biji cacat fisik, berlubang karena serangga, hitam, atau pecah",
    "longberry": "Biji varietas khusus berkarakter fisik memanjang dan pipih",
    "peaberry": "Biji tunggal (lanang) berbentuk bulat utuh tanpa belahan",
    "premium": "Biji kualitas tertinggi, utuh simetris, dan seragam tanpa cacat",
}


def _clean_html(raw: str) -> str:
    """Strip leading/trailing whitespace from each line to prevent Markdown code-block interpretation."""
    return "".join(line.strip() for line in raw.splitlines())


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
    """Render image preview inside an inspector media card with metadata chips."""
    preview_header = """
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.1rem;">🔍</span>
            <h3 style="margin: 0; font-size: 1.1rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">
                Inspeksi Citra Biji Kopi
            </h3>
        </div>
        <span style="
            background: #F1F5F9;
            color: #475569;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 9999px;
            border: 1px solid #E2E8F0;
        ">
            Active Sample
        </span>
    </div>
    """
    st.markdown(_clean_html(preview_header), unsafe_allow_html=True)

    st.image(
        image,
        use_container_width=True,
    )

    metadata_html = f"""
    <div style="
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 10px;
        margin-bottom: 16px;
    ">
        <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 8px; font-size: 0.76rem; font-weight: 600; color: #334155; font-family: 'JetBrains Mono', monospace;">
            📐 {image.width} × {image.height} px
        </span>
        <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 8px; font-size: 0.76rem; font-weight: 600; color: #334155; font-family: 'JetBrains Mono', monospace;">
            🎨 RGB 24-bit
        </span>
        <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 8px; font-size: 0.76rem; font-weight: 600; color: #334155; font-family: 'JetBrains Mono', monospace;">
            ⚡ Crop: 224 × 224 PyTorch
        </span>
    </div>
    """
    st.markdown(_clean_html(metadata_html), unsafe_allow_html=True)


def render_probability_chart(probabilities: list) -> None:
    """Render horizontal bar chart for class probabilities using Altair with modern product styling."""
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
        .mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8, height=24)
        .encode(
            x=alt.X(
                "Probabilitas:Q",
                scale=alt.Scale(domain=[0, 100]),
                title="Skor Probabilitas (%)",
                axis=alt.Axis(
                    format=".1f",
                    gridColor="#F1F5F9",
                    labelColor="#64748B",
                    titleColor="#475569",
                    tickColor="#CBD5E1",
                    titleFontWeight=600,
                    titleFontSize=11,
                ),
            ),
            y=alt.Y(
                "Kelas:N",
                sort=alt.EncodingSortField(field="Probabilitas", order="descending"),
                title=None,
                axis=alt.Axis(
                    labelColor="#0F172A",
                    labelFontWeight=700,
                    labelFontSize=12,
                    tickSize=0,
                ),
            ),
            color=alt.Color("LabelKey:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("Kelas:N", title="Mutu Kopi"),
                alt.Tooltip("Probabilitas:Q", format=".2f", title="Probabilitas (%)"),
            ],
        )
    )

    text = (
        alt.Chart(df)
        .mark_text(
            align="left",
            baseline="middle",
            dx=8,
            fontSize=11.5,
            fontWeight=700,
            font="Plus Jakarta Sans",
            color="#1E293B",
        )
        .encode(
            x=alt.X("Probabilitas:Q"),
            y=alt.Y("Kelas:N", sort=alt.EncodingSortField(field="Probabilitas", order="descending")),
            text=alt.Text("Probabilitas:Q", format=".1f"),
        )
    )

    chart = (
        (bars + text)
        .properties(height=180)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, use_container_width=True)


def render_prediction_badge(display_name: str, confidence: float, class_key: str) -> None:
    """Render prominent prediction card with XSS sanitization (CWE-79) in modern product design."""
    safe_name = html.escape(str(display_name))
    clean_key = class_key.lower()
    color = CLASS_COLORS.get(clean_key, "#2563EB")
    bg_color = CLASS_LIGHT_BG.get(clean_key, "#F8FAFC")
    border_color = CLASS_LIGHT_BORDER.get(clean_key, "#E2E8F0")
    desc = CLASS_DESCRIPTIONS.get(clean_key, "Klasifikasi hasil evaluasi inferensi CNN-SVM")

    badge_html = f"""
    <div style="
        background: linear-gradient(135deg, {bg_color} 0%, #FFFFFF 100%);
        border: 1px solid {border_color};
        border-left: 6px solid {color};
        padding: 20px 22px;
        border-radius: 14px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03), 0 4px 12px rgba(15, 23, 42, 0.02);
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: {color}; font-weight: 800; display: flex; align-items: center; gap: 6px;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background-color: {color}; display: inline-block;"></span>
                Prediksi Mutu Utama
            </span>
            <span style="background-color: {color}15; color: {color}; font-size: 0.72rem; font-weight: 700; padding: 2px 10px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace;">
                SVM-RBF
            </span>
        </div>
        <div style="display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap;">
            <h2 style="margin: 2px 0 4px 0; color: #0F172A; font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em;">
                {safe_name}
            </h2>
            <div style="text-align: right;">
                <span style="font-size: 0.78rem; color: #64748B; font-weight: 600; display: block; text-transform: uppercase;">
                    Confidence
                </span>
                <span style="font-size: 1.45rem; font-weight: 800; color: {color}; font-family: 'JetBrains Mono', monospace;">
                    {confidence * 100:.2f}%
                </span>
            </div>
        </div>
        <p style="margin: 6px 0 0 0; font-size: 0.82rem; color: #64748B; line-height: 1.4;">
            {desc}
        </p>
    </div>
    """
    st.markdown(_clean_html(badge_html), unsafe_allow_html=True)


def render_model_result_card(result: Any) -> None:
    """Render single model inference result card in modern product design."""
    model_name = getattr(result, "model_name", "Model")
    pred_class = getattr(result, "predicted_class", "unknown")
    disp_name = getattr(result, "display_name", pred_class)
    conf = float(getattr(result, "confidence", 0.0))
    probs = getattr(result, "probabilities", [])
    lat = float(getattr(result, "inference_time_ms", 0.0))

    # Architecture tags
    if "MobileNet" in model_name:
        arch_pill = "1024-d Penultimate"
        icon = "⚡"
    elif "ShuffleNet" in model_name:
        arch_pill = "1024-d Penultimate"
        icon = "🚀"
    else:
        arch_pill = "1280-d Penultimate"
        icon = "🧠"

    card_header = f"""
    <div style="
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px 12px 0 0;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: -1px;
    ">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.15rem;">{icon}</span>
            <span style="font-weight: 800; color: #0F172A; font-size: 0.95rem;">
                {model_name}
            </span>
        </div>
        <span style="font-size: 0.7rem; color: #64748B; font-weight: 600; background: #FFFFFF; border: 1px solid #CBD5E1; padding: 2px 8px; border-radius: 6px; font-family: 'JetBrains Mono', monospace;">
            {arch_pill}
        </span>
    </div>
    """
    st.markdown(_clean_html(card_header), unsafe_allow_html=True)

    with st.container():
        render_prediction_badge(disp_name, conf, pred_class)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Confidence", f"{conf * 100:.2f}%")
        with col2:
            st.metric("Latensi Inferensi", f"{lat:.1f} ms")

        st.caption("Distribusi Probabilitas Kelas:")
        render_probability_chart(probs)


def render_comparison_section(results: List[Any]) -> None:
    """Render side-by-side comparison for multiple models with consensus intelligence."""
    # 1. Section Header
    header_html = """
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <div>
            <h2 style="margin: 0; font-size: 1.5rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">
                Evaluasi Multi-Model (Side-by-Side)
            </h2>
            <p style="margin: 2px 0 0 0; font-size: 0.9rem; color: #64748B;">
                Perbandingan representasi fitur 3 arsitektur CNN Backbone & ketahanan klasifikasi SVM
            </p>
        </div>
    </div>
    """
    st.markdown(_clean_html(header_html), unsafe_allow_html=True)

    # 2. Consensus Analysis Banner
    if results:
        preds = [getattr(r, "predicted_class", "").lower() for r in results]
        all_equal = len(set(preds)) == 1
        if all_equal and len(preds) > 1:
            first_disp = getattr(results[0], "display_name", preds[0].capitalize())
            avg_conf = sum(getattr(r, "confidence", 0.0) for r in results) / len(results) * 100
            consensus_html = f"""
            <div style="
                background: #ECFDF5;
                border: 1px solid #A7F3D0;
                border-left: 5px solid #059669;
                padding: 12px 18px;
                border-radius: 10px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 8px;
            ">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.25rem;">🎯</span>
                    <span style="font-size: 0.88rem; font-weight: 700; color: #064E3B;">
                        Konsensus 100% Sepakat: Seluruh arsitektur (3/3) mengonfirmasi mutu <u>{first_disp}</u>.
                    </span>
                </div>
                <span style="font-size: 0.78rem; font-weight: 700; color: #047857; font-family: 'JetBrains Mono', monospace;">
                    Avg Confidence: {avg_conf:.2f}%
                </span>
            </div>
            """
            st.markdown(_clean_html(consensus_html), unsafe_allow_html=True)
        else:
            partial_html = """
            <div style="
                background: #FFFBEB;
                border: 1px solid #FDE68A;
                border-left: 5px solid #D97706;
                padding: 12px 18px;
                border-radius: 10px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <span style="font-size: 1.25rem;">⚖️</span>
                <span style="font-size: 0.88rem; font-weight: 700; color: #78350F;">
                    Konsensus Bervariasi: Terdeteksi perbedaan prediksi antar arsitektur. Periksa distribusi probabilitas.
                </span>
            </div>
            """
            st.markdown(_clean_html(partial_html), unsafe_allow_html=True)

    # 3. Summary comparison table (Contract for test)
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

    # 4. Side-by-side columns (Contract for test)
    cols = st.columns(len(results))
    for idx, (col, r) in enumerate(zip(cols, results)):
        with col:
            render_model_result_card(r)


# State handlers
def render_idle_state() -> None:
    """Render view when waiting for user to upload image (Figma/Linear onboarding style)."""
    st.info(
        "**Siap Melakukan Inferensi.** Silakan unggah citra biji kopi melalui area uploader di sebelah kiri "
        "untuk memulai evaluasi mutu otomatis multi-model CNN-SVM.",
        icon="✨",
    )

    steps_html = """
    <div style="
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 12px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
    ">
        <h4 style="margin: 0 0 14px 0; font-size: 0.98rem; font-weight: 800; color: #0F172A;">
            Alur Kerja Pipeline Klasifikasi Mutu Kopi:
        </h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px;">
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 14px; border-radius: 10px;">
                <span style="font-size: 0.72rem; font-weight: 700; color: #B45309; text-transform: uppercase;">Langkah 1</span>
                <h5 style="margin: 4px 0 2px 0; font-size: 0.88rem; font-weight: 700; color: #0F172A;">Unggah Citra</h5>
                <p style="margin: 0; font-size: 0.76rem; color: #64748B;">Upload foto biji kopi (JPG/PNG/WEBP). Resolusi otomatis dinormalisasi.</p>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 14px; border-radius: 10px;">
                <span style="font-size: 0.72rem; font-weight: 700; color: #2563EB; text-transform: uppercase;">Langkah 2</span>
                <h5 style="margin: 4px 0 2px 0; font-size: 0.88rem; font-weight: 700; color: #0F172A;">Ekstraksi Fitur</h5>
                <p style="margin: 0; font-size: 0.76rem; color: #64748B;">Ekstraksi representasi penultimate layer 1024-d/1280-d via PyTorch CNN.</p>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 14px; border-radius: 10px;">
                <span style="font-size: 0.72rem; font-weight: 700; color: #059669; text-transform: uppercase;">Langkah 3</span>
                <h5 style="margin: 4px 0 2px 0; font-size: 0.88rem; font-weight: 700; color: #0F172A;">Evaluasi SVM</h5>
                <p style="margin: 0; font-size: 0.76rem; color: #64748B;">Klasifikasi margin RBF dan kalkulasi distribusi Softmax multi-kelas.</p>
            </div>
        </div>
    </div>
    """
    st.markdown(_clean_html(steps_html), unsafe_allow_html=True)

    with st.expander("Tips Pengambilan Citra Biji Kopi untuk Akurasi Maksimal", expanded=False):
        st.markdown(
            """
            - **Pencahayaan Cukup**: Hindari bayangan tajam yang menutupi kontur permukaan biji.
            - **Latar Belakang Netral**: Gunakan alas berwarna putih atau gelap polos untuk kontras maksimal.
            - **Jarak Fokus Presisi**: Pastikan tekstur permukaan biji terlihat jelas (tidak buram/blur).
            - **Satu Biji Per Foto**: Untuk akurasi klasifikasi tertinggi, posisikan 1 biji kopi di tengah frame.
            """
        )


def render_loading_state() -> Any:
    """Context manager / element for loading state."""
    return st.spinner("Mengekstraksi representasi fitur & mengeksekusi inferensi multi-model SVM...")


def render_empty_state() -> None:
    """Render view when file uploaded is empty or reset."""
    st.warning("Belum ada citra biji kopi yang diunggah. Silakan pilih berkas citra terlebih dahulu.")


def render_error_state(error_message: str) -> None:
    """Render user-friendly error box without exposing internal stack trace (CWE-209)."""
    st.error(f"Terjadi kendala: {error_message}")
    st.button("Muat Ulang Halaman", on_click=lambda: st.rerun())
