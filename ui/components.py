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


def render_kpi_metrics_bar() -> None:
    """Render top minimalist 4-stat KPI overview strip (Linear/Vercel style)."""
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            _clean_html("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.03);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Engine Status</span>
                    <span style="width: 7px; height: 7px; border-radius: 50%; background-color: #10B981; display: inline-block;"></span>
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">3 Models Active</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">Penultimate Pooling Ready</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            _clean_html("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.03);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Skenario Riset</span>
                    <span style="font-size: 0.75rem;">📊</span>
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">60:20:20 Split</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">Train : Val : Test Stratified</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            _clean_html("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.03);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Latensi Tercepat</span>
                    <span style="font-size: 0.75rem;">⚡</span>
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; font-family: 'JetBrains Mono', monospace;">~20.7 ms</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">ShuffleNetV2 Backbone</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            _clean_html("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.03);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Target Mutu</span>
                    <span style="font-size: 0.75rem;">🏷️</span>
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">4 Kelas Kopi</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">Peaberry • Premium • Longberry • Defect</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


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
            <span style="font-size: 1.05rem;">🔍</span>
            <h4 style="margin: 0; font-size: 1.02rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">
                Inspeksi Citra Aktif
            </h4>
        </div>
        <span style="
            background: #EFF6FF;
            color: #1D4ED8;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 9999px;
            border: 1px solid #BFDBFE;
        ">
            Input Valid
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
        gap: 6px;
        flex-wrap: wrap;
        margin-top: 8px;
        margin-bottom: 8px;
    ">
        <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 4px 8px; border-radius: 6px; font-size: 0.74rem; font-weight: 600; color: #334155; font-family: 'JetBrains Mono', monospace;">
            📐 {image.width} × {image.height} px
        </span>
        <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 4px 8px; border-radius: 6px; font-size: 0.74rem; font-weight: 600; color: #334155; font-family: 'JetBrains Mono', monospace;">
            🎨 RGB 24-bit
        </span>
        <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 4px 8px; border-radius: 6px; font-size: 0.74rem; font-weight: 600; color: #334155; font-family: 'JetBrains Mono', monospace;">
            ⚡ 224 × 224 Norm
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
        padding: 18px 20px;
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
            <h2 style="margin: 2px 0 4px 0; color: #0F172A; font-size: 2rem; font-weight: 800; letter-spacing: -0.03em;">
                {safe_name}
            </h2>
            <div style="text-align: right;">
                <span style="font-size: 0.75rem; color: #64748B; font-weight: 600; display: block; text-transform: uppercase;">
                    Confidence
                </span>
                <span style="font-size: 1.4rem; font-weight: 800; color: {color}; font-family: 'JetBrains Mono', monospace;">
                    {confidence * 100:.2f}%
                </span>
            </div>
        </div>
        <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #64748B; line-height: 1.35;">
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
    # 1. Consensus Analysis Banner
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
                padding: 14px 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 10px;
                box-shadow: 0 1px 3px rgba(15,23,42,0.02);
            ">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.35rem;">🎯</span>
                    <div>
                        <span style="font-size: 0.95rem; font-weight: 800; color: #064E3B; display: block;">
                            Konsensus 100% Sepakat: Seluruh arsitektur (3/3) mengonfirmasi mutu <u>{first_disp}</u>
                        </span>
                        <span style="font-size: 0.78rem; color: #047857;">
                            Kesesuaian fitur terkonfirmasi solid pada MobileNetV3, ShuffleNetV2, dan EfficientNet-B0.
                        </span>
                    </div>
                </div>
                <span style="font-size: 0.85rem; font-weight: 800; color: #047857; background: #FFFFFF; padding: 4px 12px; border-radius: 8px; border: 1px solid #A7F3D0; font-family: 'JetBrains Mono', monospace;">
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
                padding: 14px 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 12px;
            ">
                <span style="font-size: 1.35rem;">⚖️</span>
                <div>
                    <span style="font-size: 0.95rem; font-weight: 800; color: #78350F; display: block;">
                        Konsensus Bervariasi Antar Arsitektur
                    </span>
                    <span style="font-size: 0.78rem; color: #92400E;">
                        Terdapat perbedaan representasi fitur antar model. Periksa distribusi probabilitas individual di bawah.
                    </span>
                </div>
            </div>
            """
            st.markdown(_clean_html(partial_html), unsafe_allow_html=True)

    # 2. Side-by-side columns (Contract for test)
    cols = st.columns(len(results))
    for idx, (col, r) in enumerate(zip(cols, results)):
        with col:
            render_model_result_card(r)

    st.markdown("---")

    # 3. Summary comparison table (Contract for test)
    st.markdown("#### Matriks Komparasi Kinerja Arsitektur")
    table_data = []
    for r in results:
        table_data.append({
            "Arsitektur Backbone": getattr(r, "model_name", ""),
            "Prediksi Mutu": getattr(r, "display_name", ""),
            "Tingkat Keyakinan": f"{getattr(r, 'confidence', 0.0) * 100:.2f}%",
            "Latensi Inferensi": f"{getattr(r, 'inference_time_ms', 0.0):.1f} ms",
        })

    st.dataframe(
        pd.DataFrame(table_data),
        hide_index=True,
        use_container_width=True,
    )


def render_visual_dictionary_deck() -> None:
    """Render comprehensive 4-card deck for coffee bean quality classes."""
    st.markdown("### Kamus Visual Mutu Biji Kopi Arabika (Dataset USK)")
    st.markdown(
        "Karakteristik fisik, cacat morfologi, dan acuan penentuan mutu pada skenario riset 60:20:20:"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            _clean_html("""
            <div style="background: #FFFFFF; border: 1px solid #FFE4E6; border-top: 4px solid #E11D48; border-radius: 12px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.15rem; font-weight: 800; color: #BE123C;">🔴 Defect</span>
                    <span style="font-size: 0.68rem; background: #FFF1F2; color: #E11D48; font-weight: 700; padding: 2px 6px; border-radius: 4px;">Tolak Ekspor</span>
                </div>
                <p style="font-size: 0.8rem; color: #475569; line-height: 1.4; margin-bottom: 12px;">
                    Biji mengalami cacat fisik berat seperti lubang hama penggerek buah kopi (PBKo), pecah, hitam (black bean), berjamur, atau keriput.
                </p>
                <div style="background: #F8FAFC; border-radius: 8px; padding: 8px 10px; font-size: 0.74rem; color: #64748B;">
                    <b>Ciri Kunci:</b> Diskolorasi gelap, lubang berdiameter &lt;1mm, tekstur rapuh.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            _clean_html("""
            <div style="background: #FFFFFF; border: 1px solid #FEF3C7; border-top: 4px solid #D97706; border-radius: 12px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.15rem; font-weight: 800; color: #B45309;">🟡 Longberry</span>
                    <span style="font-size: 0.68rem; background: #FFFBEB; color: #D97706; font-weight: 700; padding: 2px 6px; border-radius: 4px;">Spesialitas</span>
                </div>
                <p style="font-size: 0.8rem; color: #475569; line-height: 1.4; margin-bottom: 12px;">
                    Varietas Arabika khusus dengan bentuk biji khas yang memanjang dan pipih melengkung. Populer di dataran tinggi Gayo dan Aceh.
                </p>
                <div style="background: #F8FAFC; border-radius: 8px; padding: 8px 10px; font-size: 0.74rem; color: #64748B;">
                    <b>Ciri Kunci:</b> Rasio panjang-terhadap-lebar tinggi, ujung meruncing.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            _clean_html("""
            <div style="background: #FFFFFF; border: 1px solid #DBEAFE; border-top: 4px solid #2563EB; border-radius: 12px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.15rem; font-weight: 800; color: #1D4ED8;">🔵 Peaberry</span>
                    <span style="font-size: 0.68rem; background: #EFF6FF; color: #2563EB; font-weight: 700; padding: 2px 6px; border-radius: 4px;">Kopi Lanang</span>
                </div>
                <p style="font-size: 0.8rem; color: #475569; line-height: 1.4; margin-bottom: 12px;">
                    Biji tunggal bulat utuh tanpa belahan tengah. Terjadi karena pembuahan tunggal alami dalam ceri kopi (hanya 5–10% dari total panen).
                </p>
                <div style="background: #F8FAFC; border-radius: 8px; padding: 8px 10px; font-size: 0.74rem; color: #64748B;">
                    <b>Ciri Kunci:</b> Bentuk oval bulat seperti kacang polong, celah tengah dangkal.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            _clean_html("""
            <div style="background: #FFFFFF; border: 1px solid #D1FAE5; border-top: 4px solid #059669; border-radius: 12px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.15rem; font-weight: 800; color: #047857;">🟢 Premium</span>
                    <span style="font-size: 0.68rem; background: #ECFDF5; color: #059669; font-weight: 700; padding: 2px 6px; border-radius: 4px;">Grade 1 Utama</span>
                </div>
                <p style="font-size: 0.8rem; color: #475569; line-height: 1.4; margin-bottom: 12px;">
                    Biji kualitas pertama dengan bentuk fisik simetris, belahan tengah rapi, densitas padat seragam, dan bersih dari segala cacat primer maupun sekunder.
                </p>
                <div style="background: #F8FAFC; border-radius: 8px; padding: 8px 10px; font-size: 0.74rem; color: #64748B;">
                    <b>Ciri Kunci:</b> Permukaan mulus, warna hijau kebiruan segar, ukuran seragam.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )


def render_architecture_specs_tab() -> None:
    """Render technical architecture specifications and thesis methodology details."""
    st.markdown("### Spesifikasi Teknis & Metodologi Riset Skenario 60:20:20")
    st.markdown(
        "Rincian konfigurasi transfer learning penultimate layer dan implementasi classifier SVM:"
    )

    col_spec1, col_spec2 = st.columns(2)

    with col_spec1:
        st.markdown(
            """
            #### 1. Pembagian Dataset (Stratified 60:20:20)
            - **Data Latih (Training)**: `60%` sampel per kelas mutu, digunakan untuk melatih penyesuaian bobot CNN & fitting SVM hyperplane.
            - **Data Validasi (Validation)**: `20%` sampel per kelas mutu, digunakan untuk evaluasi tuning hyperparameter C dan Gamma RBF.
            - **Data Uji (Testing)**: `20%` sampel per kelas mutu independen, digunakan untuk benchmarking akurasi generalisasi akhir.
            - **Total Dataset**: Citra biji kopi Arabika dari repositori riset USK-Coffee.
            """
        )

        st.markdown(
            """
            #### 2. Ekstraksi Representasi Penultimate Layer
            - Menghapus lapisan klasifikasi akhir (*classifier head*) pada ketiga arsitektur CNN dan menggantinya dengan `nn.Identity()`.
            - Representasi vektor fitur diambil langsung pasca *Global Average Pooling*:
              - **MobileNetV3-Small**: Vektor fitur `1024-dimensi`
              - **ShuffleNetV2**: Vektor fitur `1024-dimensi`
              - **EfficientNet-B0**: Vektor fitur `1280-dimensi`
            """
        )

    with col_spec2:
        st.markdown(
            """
            #### 3. Support Vector Machine (SVM) Pipeline
            - **Kernel**: Radial Basis Function (RBF) non-linear.
            - **Strategi Multi-Kelas**: One-vs-Rest (OvR).
            - **Preprocessing**: `StandardScaler` terintegrasi di dalam scikit-learn pipeline untuk normalisasi zero-mean unit-variance.
            - **Estimasi Probabilitas**: Normalisasi eksponensial stabil (*Numerically Stable Softmax*) pada jarak margin `decision_function`:
            """
        )
        st.latex(r"\sigma(z)_i = \frac{e^{z_i - \max(z)}}{\sum_{j=1}^K e^{z_j - \max(z)}}")

        st.markdown(
            """
            #### 4. Standar Keamanan & Keandalan Runtime
            - **CWE-400 Decompression Bomb**: Pembatas `MAX_IMAGE_PIXELS = 16,777,216` px (16 MP).
            - **CWE-79 XSS Prevention**: Sanitasi teks dinamis badge via `html.escape()`.
            - **CWE-209 Info Exposure**: Error logging internal tanpa membocorkan trace path sistem.
            """
        )


# State handlers
def render_idle_state() -> None:
    """Render view when waiting for user to upload image (Figma/Linear onboarding style)."""
    st.info(
        "**Siap Melakukan Inferensi.** Silakan unggah citra biji kopi melalui area uploader di atas "
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
