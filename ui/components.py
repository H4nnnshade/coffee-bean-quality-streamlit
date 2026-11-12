"""Streamlit UI components for coffee bean quality classification (Compact Luxury Product Design)."""

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

# Class styling dictionaries for modern luxury UI
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
    "defect": "Biji cacat fisik, berlubang akibat serangga, hitam, atau pecah",
    "longberry": "Biji varietas khusus berkarakter fisik memanjang dan pipih",
    "peaberry": "Biji tunggal (lanang) berbentuk bulat utuh tanpa belahan",
    "premium": "Biji mutu tertinggi, utuh simetris, dan seragam tanpa cacat",
}

# Vector SVG Icons (Lucide / Feather Standard Specifications, 14-18px)
ICONS = {
    "cpu": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>""",
    "database": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>""",
    "zap": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "target": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
    "shield_check": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>""",
    "upload_cloud": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>""",
    "search": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>""",
    "sparkle": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>""",
    "mobilenet": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>""",
    "shufflenet": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>""",
    "efficientnet": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>""",
    "defect": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E11D48" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>""",
    "longberry": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="12" rx="5" ry="9" transform="rotate(-30 12 12)"/><path d="M12 4c-1 3-1 13 0 16"/></svg>""",
    "peaberry": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/></svg>""",
    "premium": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>""",
}


def _clean_html(raw: str) -> str:
    """Strip leading/trailing whitespace from each line to prevent Markdown code-block interpretation."""
    return "".join(line.strip() for line in raw.splitlines())


def render_kpi_metrics_bar() -> None:
    """Render top compact 4-stat KPI overview strip with vector SVG icons and refined gradient styling."""
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            _clean_html(f"""
            <div style="
                background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 14px;
                box-shadow: 0 1px 2px rgba(15,23,42,0.02);
            ">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em;">Engine Pipeline</span>
                    <div style="width: 24px; height: 24px; border-radius: 6px; background: #ECFDF5; color: #059669; display: flex; align-items: center; justify-content: center;">
                        {ICONS["cpu"]}
                    </div>
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">3 Models Active</div>
                <div style="font-size: 0.72rem; color: #64748B; margin-top: 1px;">Penultimate Pooling Ready</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            _clean_html(f"""
            <div style="
                background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 14px;
                box-shadow: 0 1px 2px rgba(15,23,42,0.02);
            ">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em;">Skenario Riset</span>
                    <div style="width: 24px; height: 24px; border-radius: 6px; background: #FFFBEB; color: #D97706; display: flex; align-items: center; justify-content: center;">
                        {ICONS["database"]}
                    </div>
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">60:20:20 Split</div>
                <div style="font-size: 0.72rem; color: #64748B; margin-top: 1px;">Train : Val : Test Stratified</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            _clean_html(f"""
            <div style="
                background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 14px;
                box-shadow: 0 1px 2px rgba(15,23,42,0.02);
            ">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em;">Latensi Tercepat</span>
                    <div style="width: 24px; height: 24px; border-radius: 6px; background: #EFF6FF; color: #2563EB; display: flex; align-items: center; justify-content: center;">
                        {ICONS["zap"]}
                    </div>
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; font-family: 'JetBrains Mono', monospace;">~20.7 ms</div>
                <div style="font-size: 0.72rem; color: #64748B; margin-top: 1px;">ShuffleNetV2 Backbone</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            _clean_html(f"""
            <div style="
                background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 14px;
                box-shadow: 0 1px 2px rgba(15,23,42,0.02);
            ">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em;">Target Mutu</span>
                    <div style="width: 24px; height: 24px; border-radius: 6px; background: #F8FAFC; color: #0F172A; display: flex; align-items: center; justify-content: center; border: 1px solid #E2E8F0;">
                        {ICONS["target"]}
                    </div>
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">4 Kelas Kopi</div>
                <div style="font-size: 0.72rem; color: #64748B; margin-top: 1px;">Peaberry • Premium • Longberry • Defect</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)


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


def render_image_metadata(image: Image.Image) -> None:
    """Render comprehensive image metadata and tensor normalization card on the left column below uploader."""
    aspect_ratio = f"{image.width / image.height:.2f}:1" if image.height > 0 else "N/A"
    total_pixels = f"{image.width * image.height:,} px"

    metadata_html = f"""
    <div style="
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 10px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02), 0 3px 8px -2px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="color: #92400E; display: flex; align-items: center;">{ICONS["database"]}</div>
                <span style="font-size: 0.74rem; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em;">
                    Spesifikasi Citra & Tensor
                </span>
            </div>
            <span style="
                background: #ECFDF5;
                color: #059669;
                font-size: 0.66rem;
                font-weight: 700;
                padding: 2px 8px;
                border-radius: 9999px;
                border: 1px solid #A7F3D0;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            ">
                <span style="width: 5px; height: 5px; border-radius: 50%; background: #059669; display: inline-block;"></span>
                Valid RGB
            </span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 7px; padding: 7px 10px;">
                <span style="font-size: 0.65rem; color: #64748B; font-weight: 600; text-transform: uppercase; display: block;">Dimensi Asli</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 700; color: #0F172A;">
                    {image.width} × {image.height} px
                </span>
            </div>
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 7px; padding: 7px 10px;">
                <span style="font-size: 0.65rem; color: #64748B; font-weight: 600; text-transform: uppercase; display: block;">Tensor CNN</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 700; color: #92400E;">
                    1 × 3 × 224 × 224
                </span>
            </div>
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 7px; padding: 7px 10px;">
                <span style="font-size: 0.65rem; color: #64748B; font-weight: 600; text-transform: uppercase; display: block;">Kanal Warna</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 700; color: #0F172A;">
                    RGB (24-bit)
                </span>
            </div>
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 7px; padding: 7px 10px;">
                <span style="font-size: 0.65rem; color: #64748B; font-weight: 600; text-transform: uppercase; display: block;">Rasio Aspek</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 700; color: #0F172A;">
                    {aspect_ratio} ({total_pixels})
                </span>
            </div>
        </div>

        <div style="
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #F1F5F9;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.68rem;
            color: #64748B;
        ">
            <span>Normalisasi: ImageNet Mean & Std</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #475569;">Float32 Tensor</span>
        </div>
    </div>
    """
    st.markdown(_clean_html(metadata_html), unsafe_allow_html=True)


def render_image_preview(image: Image.Image) -> None:
    """Render image preview inside a clean framed inspector canvas."""
    preview_header = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="color: #92400E; display: flex; align-items: center;">{ICONS["search"]}</div>
            <h4 style="margin: 0; font-size: 0.88rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">
                Pratinjau Citra Resolusi Tinggi
            </h4>
        </div>
        <span style="
            background: #EFF6FF;
            color: #1D4ED8;
            font-size: 0.68rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 9999px;
            border: 1px solid #BFDBFE;
        ">
            Display Ready
        </span>
    </div>
    """
    st.markdown(_clean_html(preview_header), unsafe_allow_html=True)
    st.image(image, width="stretch")


def render_probability_chart(probabilities: list) -> None:
    """Render horizontal bar chart for class probabilities using Altair with modern compact product styling."""
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
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6, height=18)
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
                    titleFontSize=10,
                ),
            ),
            y=alt.Y(
                "Kelas:N",
                sort=alt.EncodingSortField(field="Probabilitas", order="descending"),
                title=None,
                axis=alt.Axis(
                    labelColor="#0F172A",
                    labelFontWeight=700,
                    labelFontSize=11,
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
            dx=6,
            fontSize=10.5,
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
        .properties(height=140)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, width="stretch")


def render_prediction_badge(display_name: str, confidence: float, class_key: str) -> None:
    """Render prominent prediction card with XSS sanitization (CWE-79) in modern compact luxury product design."""
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
        border-left: 4px solid {color};
        padding: 14px 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02), 0 3px 8px rgba(15, 23, 42, 0.03);
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
            <span style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; color: {color}; font-weight: 800; display: flex; align-items: center; gap: 5px;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background-color: {color}; display: inline-block;"></span>
                Prediksi Mutu Utama
            </span>
            <span style="background-color: {color}15; color: {color}; font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace;">
                SVM-RBF
            </span>
        </div>
        <div style="display: flex; align-items: baseline; justify-content: space-between; gap: 10px; flex-wrap: wrap;">
            <h2 style="margin: 1px 0 2px 0; color: #0F172A; font-size: 1.55rem; font-weight: 800; letter-spacing: -0.03em;">
                {safe_name}
            </h2>
            <div style="text-align: right;">
                <span style="font-size: 0.68rem; color: #64748B; font-weight: 600; display: block; text-transform: uppercase;">
                    Confidence
                </span>
                <span style="font-size: 1.20rem; font-weight: 800; color: {color}; font-family: 'JetBrains Mono', monospace;">
                    {confidence * 100:.2f}%
                </span>
            </div>
        </div>
        <p style="margin: 2px 0 0 0; font-size: 0.76rem; color: #64748B; line-height: 1.35;">
            {desc}
        </p>
    </div>
    """
    st.markdown(_clean_html(badge_html), unsafe_allow_html=True)


def render_model_result_card(result: Any) -> None:
    """Render single model inference result card with vector SVG architecture icons."""
    model_name = html.escape(str(getattr(result, "model_name", "Model")))
    pred_class = getattr(result, "predicted_class", "unknown")
    disp_name = getattr(result, "display_name", pred_class)
    conf = float(getattr(result, "confidence", 0.0))
    probs = getattr(result, "probabilities", [])
    lat = float(getattr(result, "inference_time_ms", 0.0))

    # Architecture tags & vector icons
    if "MobileNet" in model_name:
        arch_pill = "1024-d Penultimate"
        svg_icon = ICONS["mobilenet"]
    elif "ShuffleNet" in model_name:
        arch_pill = "1024-d Penultimate"
        svg_icon = ICONS["shufflenet"]
    else:
        arch_pill = "1280-d Penultimate"
        svg_icon = ICONS["efficientnet"]

    model_header_html = f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 2px 8px 2px;
        margin-bottom: 2px;
    ">
        <div style="display: flex; align-items: center; gap: 7px;">
            <div style="color: #78350F; display: flex; align-items: center;">{svg_icon}</div>
            <span style="font-weight: 800; color: #0F172A; font-size: 0.92rem; letter-spacing: -0.01em;">
                {model_name}
            </span>
        </div>
        <span style="font-size: 0.68rem; color: #64748B; font-weight: 600; background: #F1F5F9; border: 1px solid #E2E8F0; padding: 2px 8px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace;">
            {arch_pill}
        </span>
    </div>
    """
    st.markdown(_clean_html(model_header_html), unsafe_allow_html=True)

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
            first_disp = html.escape(str(getattr(results[0], "display_name", preds[0].capitalize())))
            avg_conf = sum(getattr(r, "confidence", 0.0) for r in results) / len(results) * 100
            consensus_html = f"""
            <div style="
                background: linear-gradient(135deg, #ECFDF5 0%, #FFFFFF 100%);
                border: 1px solid #A7F3D0;
                border-left: 4px solid #059669;
                padding: 12px 16px;
                border-radius: 10px;
                margin-bottom: 14px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 10px;
                box-shadow: 0 1px 2px rgba(15,23,42,0.02);
            ">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 30px; height: 30px; border-radius: 8px; background: #D1FAE5; color: #047857; display: flex; align-items: center; justify-content: center;">
                        {ICONS["shield_check"]}
                    </div>
                    <div>
                        <span style="font-size: 0.90rem; font-weight: 800; color: #064E3B; display: block;">
                            Konsensus 100% Sepakat: Seluruh arsitektur (3/3) mengonfirmasi mutu <u>{first_disp}</u>
                        </span>
                        <span style="font-size: 0.74rem; color: #047857;">
                            Kesesuaian representasi fitur terkonfirmasi solid pada MobileNetV3, ShuffleNetV2, dan EfficientNet-B0.
                        </span>
                    </div>
                </div>
                <span style="font-size: 0.78rem; font-weight: 800; color: #047857; background: #FFFFFF; padding: 4px 10px; border-radius: 6px; border: 1px solid #A7F3D0; font-family: 'JetBrains Mono', monospace;">
                    Avg Confidence: {avg_conf:.2f}%
                </span>
            </div>
            """
            st.markdown(_clean_html(consensus_html), unsafe_allow_html=True)
        else:
            partial_html = f"""
            <div style="
                background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
                border: 1px solid #FDE68A;
                border-left: 4px solid #D97706;
                padding: 12px 16px;
                border-radius: 10px;
                margin-bottom: 14px;
                display: flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 1px 2px rgba(15,23,42,0.02);
            ">
                <div style="width: 30px; height: 30px; border-radius: 8px; background: #FEF3C7; color: #B45309; display: flex; align-items: center; justify-content: center;">
                    {ICONS["target"]}
                </div>
                <div>
                    <span style="font-size: 0.90rem; font-weight: 800; color: #78350F; display: block;">
                        Konsensus Bervariasi Antar Arsitektur
                    </span>
                    <span style="font-size: 0.74rem; color: #92400E;">
                        Terdapat divergensi representasi fitur antar model. Periksa distribusi probabilitas individual di bawah.
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
        width="stretch",
    )


def render_visual_dictionary_deck() -> None:
    """Render comprehensive 4-card deck for coffee bean quality classes with vector SVG badges."""
    st.markdown("### Kamus Visual Mutu Biji Kopi Arabika (Dataset USK)")
    st.markdown(
        "Karakteristik fisik, cacat morfologi, dan acuan mutu standar ekspor pada skenario riset 60:20:20:"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            _clean_html(f"""
            <div style="background: #FFFFFF; border: 1px solid #FFE4E6; border-top: 3px solid #E11D48; border-radius: 10px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        {ICONS["defect"]}
                        <span style="font-size: 0.95rem; font-weight: 800; color: #BE123C;">Defect</span>
                    </div>
                    <span style="font-size: 0.65rem; background: #FFF1F2; color: #E11D48; font-weight: 700; padding: 2px 5px; border-radius: 4px;">Tolak Ekspor</span>
                </div>
                <p style="font-size: 0.76rem; color: #475569; line-height: 1.35; margin-bottom: 10px;">
                    Biji mengalami cacat fisik berat seperti lubang hama penggerek buah kopi (PBKo), pecah, hitam (black bean), berjamur, atau keriput.
                </p>
                <div style="background: #F8FAFC; border-radius: 6px; padding: 6px 8px; font-size: 0.70rem; color: #64748B;">
                    <b>Ciri Kunci:</b> Diskolorasi gelap, lubang berdiameter &lt;1mm, tekstur rapuh.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            _clean_html(f"""
            <div style="background: #FFFFFF; border: 1px solid #FEF3C7; border-top: 3px solid #D97706; border-radius: 10px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        {ICONS["longberry"]}
                        <span style="font-size: 0.95rem; font-weight: 800; color: #B45309;">Longberry</span>
                    </div>
                    <span style="font-size: 0.65rem; background: #FFFBEB; color: #D97706; font-weight: 700; padding: 2px 5px; border-radius: 4px;">Spesialitas</span>
                </div>
                <p style="font-size: 0.76rem; color: #475569; line-height: 1.35; margin-bottom: 10px;">
                    Varietas Arabika khusus dengan bentuk biji khas yang memanjang dan pipih melengkung. Populer di dataran tinggi Gayo dan Aceh.
                </p>
                <div style="background: #F8FAFC; border-radius: 6px; padding: 6px 8px; font-size: 0.70rem; color: #64748B;">
                    <b>Ciri Kunci:</b> Rasio panjang-terhadap-lebar tinggi, ujung meruncing.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            _clean_html(f"""
            <div style="background: #FFFFFF; border: 1px solid #DBEAFE; border-top: 3px solid #2563EB; border-radius: 10px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        {ICONS["peaberry"]}
                        <span style="font-size: 0.95rem; font-weight: 800; color: #1D4ED8;">Peaberry</span>
                    </div>
                    <span style="font-size: 0.65rem; background: #EFF6FF; color: #2563EB; font-weight: 700; padding: 2px 5px; border-radius: 4px;">Kopi Lanang</span>
                </div>
                <p style="font-size: 0.76rem; color: #475569; line-height: 1.35; margin-bottom: 10px;">
                    Biji tunggal bulat utuh tanpa belahan tengah. Terjadi karena pembuahan tunggal alami dalam ceri kopi (hanya 5–10% dari total panen).
                </p>
                <div style="background: #F8FAFC; border-radius: 6px; padding: 6px 8px; font-size: 0.70rem; color: #64748B;">
                    <b>Ciri Kunci:</b> Bentuk oval bulat seperti kacang polong, celah tengah dangkal.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            _clean_html(f"""
            <div style="background: #FFFFFF; border: 1px solid #D1FAE5; border-top: 3px solid #059669; border-radius: 10px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        {ICONS["premium"]}
                        <span style="font-size: 0.95rem; font-weight: 800; color: #047857;">Premium</span>
                    </div>
                    <span style="font-size: 0.65rem; background: #ECFDF5; color: #059669; font-weight: 700; padding: 2px 5px; border-radius: 4px;">Grade 1 Utama</span>
                </div>
                <p style="font-size: 0.76rem; color: #475569; line-height: 1.35; margin-bottom: 10px;">
                    Biji mutu pertama dengan bentuk fisik simetris, belahan tengah rapi, densitas padat seragam, dan bersih dari segala cacat primer maupun sekunder.
                </p>
                <div style="background: #F8FAFC; border-radius: 6px; padding: 6px 8px; font-size: 0.70rem; color: #64748B;">
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
    """Render view when waiting for user to upload image with vector SVG steps."""
    st.info(
        "**Siap Melakukan Inferensi.** Silakan unggah citra biji kopi melalui area uploader di atas "
        "untuk memulai evaluasi mutu otomatis multi-model CNN-SVM.",
        icon="✨",
    )

    steps_html = f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 10px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02);
    ">
        <h4 style="margin: 0 0 12px 0; font-size: 0.90rem; font-weight: 800; color: #0F172A;">
            Alur Kerja Pipeline Klasifikasi Mutu Kopi:
        </h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px;">
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 12px; border-radius: 8px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #92400E; text-transform: uppercase;">Langkah 1</span>
                    <div style="color: #92400E;">{ICONS["upload_cloud"]}</div>
                </div>
                <h5 style="margin: 2px 0 2px 0; font-size: 0.82rem; font-weight: 700; color: #0F172A;">Unggah Citra</h5>
                <p style="margin: 0; font-size: 0.72rem; color: #64748B; line-height: 1.35;">Upload foto biji kopi (JPG/PNG/WEBP). Resolusi otomatis dinormalisasi.</p>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 12px; border-radius: 8px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #2563EB; text-transform: uppercase;">Langkah 2</span>
                    <div style="color: #2563EB;">{ICONS["cpu"]}</div>
                </div>
                <h5 style="margin: 2px 0 2px 0; font-size: 0.82rem; font-weight: 700; color: #0F172A;">Ekstraksi Fitur</h5>
                <p style="margin: 0; font-size: 0.72rem; color: #64748B; line-height: 1.35;">Ekstraksi representasi penultimate layer 1024-d/1280-d via PyTorch CNN.</p>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 12px; border-radius: 8px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #059669; text-transform: uppercase;">Langkah 3</span>
                    <div style="color: #059669;">{ICONS["target"]}</div>
                </div>
                <h5 style="margin: 2px 0 2px 0; font-size: 0.82rem; font-weight: 700; color: #0F172A;">Evaluasi SVM</h5>
                <p style="margin: 0; font-size: 0.72rem; color: #64748B; line-height: 1.35;">Klasifikasi margin RBF dan kalkulasi distribusi Softmax multi-kelas.</p>
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
