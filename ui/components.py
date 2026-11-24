"""Streamlit UI components — Warm Light + Dark Accent design."""

from typing import Any, List, Optional
import html
import logging
import inspect
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
        "peaberry": "#7C3AED",
        "premium": "#059669",
    }
    ModelInferenceOutput = Any  # type: ignore

# Security Guard: Prevent decompression bomb DoS attacks (CWE-400)
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

# Class styling — light tinted backgrounds on white cards
CLASS_LIGHT_BG = {
    "defect": "#FFF1F2",
    "longberry": "#FFFBEB",
    "peaberry": "#F5F3FF",
    "premium": "#ECFDF5",
}
CLASS_LIGHT_BORDER = {
    "defect": "#FECDD3",
    "longberry": "#FDE68A",
    "peaberry": "#DDD6FE",
    "premium": "#A7F3D0",
}
CLASS_DESCRIPTIONS = {
    "defect": "Biji cacat fisik, berlubang akibat serangga, hitam, atau pecah",
    "longberry": "Biji varietas khusus berkarakter fisik memanjang dan pipih",
    "peaberry": "Biji tunggal (lanang) berbentuk bulat utuh tanpa belahan",
    "premium": "Biji mutu tertinggi, utuh simetris, dan seragam tanpa cacat",
}

# Vector SVG Icons (Lucide / Feather, 14-18px)
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
    "defect": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>""",
    "longberry": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="12" rx="5" ry="9" transform="rotate(-30 12 12)"/><path d="M12 4c-1 3-1 13 0 16"/></svg>""",
    "peaberry": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/></svg>""",
    "premium": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>""",
}


def _clean_html(raw: str) -> str:
    """Strip leading/trailing whitespace from each line to prevent Markdown code-block interpretation."""
    return "".join(line.strip() for line in raw.splitlines())


def render_kpi_metrics_bar() -> None:
    """Render top 4-stat KPI strip — dark accent cards for high contrast."""
    _CARDS = [
        {
            "label": "Engine Pipeline",
            "value": "3 Models",
            "sub": "Penultimate Pooling Ready",
            "icon": ICONS["cpu"],
            "icon_color": "#10B981",
            "icon_bg": "rgba(16,185,129,0.15)",
            "accent": "#10B981",
        },
        {
            "label": "Skenario Riset",
            "value": "60:20:20",
            "sub": "Train · Val · Test Stratified",
            "icon": ICONS["database"],
            "icon_color": "#D97706",
            "icon_bg": "rgba(217,119,6,0.15)",
            "accent": "#D97706",
        },
        {
            "label": "Kelas Mutu",
            "value": "4 Kategori",
            "sub": "Defect · Long · Pea · Prem",
            "icon": ICONS["target"],
            "icon_color": "#A78BFA",
            "icon_bg": "rgba(167,139,250,0.15)",
            "accent": "#A78BFA",
        },
        {
            "label": "Protokol Uji",
            "value": "DoD Strict",
            "sub": "CWE-400 & CWE-79 Shield",
            "icon": ICONS["zap"],
            "icon_color": "#FB923C",
            "icon_bg": "rgba(251,146,60,0.15)",
            "accent": "#FB923C",
        },
    ]

    cols = st.columns(4)
    for col, card in zip(cols, _CARDS):
        with col:
            st.markdown(
                _clean_html(f"""
                <div style="
                    background: linear-gradient(145deg, #1C1109 0%, #2A1A0E 100%);
                    border: 1px solid rgba(255,255,255,0.09);
                    border-top: 2px solid {card['accent']};
                    border-radius: 13px;
                    padding: 14px 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.30), 0 1px 3px rgba(0,0,0,0.20);
                    transition: transform 0.18s cubic-bezier(0.16,1,0.3,1), box-shadow 0.18s;
                ">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                        <span style="font-size:.67rem;font-weight:700;color:#A8906E;text-transform:uppercase;letter-spacing:.07em;">{card['label']}</span>
                        <div style="width:26px;height:26px;border-radius:7px;background:{card['icon_bg']};color:{card['icon_color']};display:flex;align-items:center;justify-content:center;">
                            {card['icon']}
                        </div>
                    </div>
                    <div style="font-size:1.18rem;font-weight:800;color:#F5EDE3;letter-spacing:-.025em;font-family:'JetBrains Mono',monospace;">{card['value']}</div>
                    <div style="font-size:.71rem;color:#6B5A44;margin-top:2px;">{card['sub']}</div>
                </div>
                """),
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)


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

    # 1. Zero-bloat size check
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if getattr(uploaded_file, "size", 0) > max_bytes:
        st.error(
            f"Ukuran file melebihi batas maksimal {MAX_FILE_SIZE_MB} MB. "
            "Silakan unggah citra yang lebih kecil."
        )
        return None

    try:
        image = Image.open(uploaded_file)

        # 2. Magic bytes format validation
        img_format = (image.format or "").lower()
        if img_format not in ["jpeg", "jpg", "png", "webp"]:
            st.error("Format berkas tidak valid atau rusak. Hanya menerima JPG, PNG, atau WEBP.")
            return None

        # 3. Resolution ceiling validation
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
    """Render image metadata card — dark accent surface."""
    aspect_ratio = f"{image.width / image.height:.2f}:1" if image.height > 0 else "N/A"
    total_pixels = f"{image.width * image.height:,} px"

    metadata_html = f"""
    <div style="
        background: linear-gradient(145deg, #1C1109 0%, #2A1A0E 100%);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 13px;
        padding: 14px 16px;
        margin-top: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.28), 0 1px 3px rgba(0,0,0,0.18);
    ">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
            <div style="display:flex;align-items:center;gap:7px;">
                <div style="color:#D97706;display:flex;align-items:center;">{ICONS["database"]}</div>
                <span style="font-size:.74rem;font-weight:800;color:#F5EDE3;text-transform:uppercase;letter-spacing:.05em;">Spesifikasi Citra &amp; Tensor</span>
            </div>
            <span style="background:rgba(16,185,129,0.15);color:#10B981;font-size:.65rem;font-weight:700;padding:2px 9px;border-radius:9999px;border:1px solid rgba(16,185,129,0.25);display:inline-flex;align-items:center;gap:4px;">
                <span style="width:5px;height:5px;border-radius:50%;background:#10B981;display:inline-block;"></span>
                Valid RGB
            </span>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:8px 10px;">
                <span style="font-size:.64rem;color:#6B5A44;font-weight:600;text-transform:uppercase;display:block;margin-bottom:2px;">Dimensi Asli</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:.83rem;font-weight:700;color:#F5EDE3;">{image.width} × {image.height} px</span>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:8px 10px;">
                <span style="font-size:.64rem;color:#6B5A44;font-weight:600;text-transform:uppercase;display:block;margin-bottom:2px;">Tensor CNN</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:.83rem;font-weight:700;color:#D97706;">1 × 3 × 224 × 224</span>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:8px 10px;">
                <span style="font-size:.64rem;color:#6B5A44;font-weight:600;text-transform:uppercase;display:block;margin-bottom:2px;">Kanal Warna</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:.83rem;font-weight:700;color:#F5EDE3;">RGB (24-bit)</span>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:8px 10px;">
                <span style="font-size:.64rem;color:#6B5A44;font-weight:600;text-transform:uppercase;display:block;margin-bottom:2px;">Rasio Aspek</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:.83rem;font-weight:700;color:#F5EDE3;">{aspect_ratio}</span>
            </div>
        </div>

        <div style="margin-top:9px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.07);display:flex;align-items:center;justify-content:space-between;font-size:.68rem;color:#6B5A44;">
            <span>Normalisasi: ImageNet Mean &amp; Std</span>
            <span style="font-family:'JetBrains Mono',monospace;font-weight:600;color:#A8906E;">Float32 · {total_pixels}</span>
        </div>
    </div>
    """
    st.markdown(_clean_html(metadata_html), unsafe_allow_html=True)


def render_image_preview(image: Image.Image) -> None:
    """Render image preview inside a clean framed inspector canvas."""
    preview_header = f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <div style="display:flex;align-items:center;gap:7px;">
            <div style="color:#D97706;display:flex;align-items:center;">{ICONS["search"]}</div>
            <h4 style="margin:0;font-size:.88rem;font-weight:800;color:#1A1210;letter-spacing:-.02em;">Pratinjau Citra</h4>
        </div>
        <span style="background:#1C1109;color:#D97706;font-size:.67rem;font-weight:700;padding:3px 9px;border-radius:9999px;border:1px solid rgba(217,119,6,0.25);font-family:'JetBrains Mono',monospace;">
            Display Ready
        </span>
    </div>
    """
    st.markdown(_clean_html(preview_header), unsafe_allow_html=True)
    st.image(image, width="stretch")


def render_probability_chart(probabilities: list) -> None:
    """Render horizontal probability bar chart via Altair."""
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
            "LabelDiagram": f"{disp} · {score * 100:.1f}%",
            "LabelKey": label.lower(),
        })

    df = pd.DataFrame(data)

    color_scale = alt.Scale(
        domain=list(CLASS_COLORS.keys()),
        range=list(CLASS_COLORS.values()),
    )
    y_scale = alt.Scale(paddingInner=0.42, paddingOuter=0.22)
    chart_scale = alt.Scale(domain=[0, 122], nice=False)

    no_axis = alt.Axis(labels=False, ticks=False, domain=False, title=None)

    base = alt.Chart(df).encode(
        y=alt.Y("Kelas:N", scale=y_scale,
                sort=alt.EncodingSortField(field="Probabilitas", order="descending"),
                title=None, axis=no_axis)
    )

    bars = base.mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5, height=15).encode(
        x=alt.X("Probabilitas:Q", scale=chart_scale,
                title="Probabilitas (%)",
                axis=alt.Axis(values=[0, 25, 50, 75, 100], format=".0f",
                              gridColor="#F0EBE5", labelColor="#9C8E84",
                              titleColor="#7A6A5A", tickColor="#D6CFC8",
                              titleFont="Plus Jakarta Sans", titleFontWeight=600,
                              titleFontSize=10)),
        color=alt.Color("LabelKey:N", scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip("Kelas:N", title="Mutu Kopi"),
            alt.Tooltip("Probabilitas:Q", format=".2f", title="Probabilitas (%)"),
        ],
    )

    text_labels = base.mark_text(
        align="left", baseline="middle", dx=8,
        fontSize=10.5, fontWeight=700, font="JetBrains Mono", color="#374151",
    ).encode(
        x=alt.X("Probabilitas:Q", scale=chart_scale),
        text=alt.Text("LabelDiagram:N"),
    )

    chart = (bars + text_labels).properties(height=148).configure_view(strokeWidth=0)

    chart_parameters = inspect.signature(st.altair_chart).parameters
    if "width" in chart_parameters:
        st.altair_chart(chart, width="stretch")
    else:
        st.altair_chart(chart, use_container_width=True)


def render_prediction_badge(display_name: str, confidence: float, class_key: str) -> None:
    """Render prominent prediction badge — light tinted card with colored left border (CWE-79 safe)."""
    safe_name = html.escape(str(display_name))
    clean_key = class_key.lower()
    color = CLASS_COLORS.get(clean_key, "#7C3AED")
    bg_color = CLASS_LIGHT_BG.get(clean_key, "#F8FAFC")
    border_color = CLASS_LIGHT_BORDER.get(clean_key, "#E2E8F0")
    desc = CLASS_DESCRIPTIONS.get(clean_key, "Klasifikasi hasil evaluasi inferensi CNN-SVM")

    badge_html = f"""
    <div style="
        background: linear-gradient(135deg, {bg_color} 0%, #FFFFFF 100%);
        border: 1px solid {border_color};
        border-left: 4px solid {color};
        padding: 15px 17px;
        border-radius: 13px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(26,18,9,0.05), 0 2px 10px -2px rgba(26,18,9,0.04);
    ">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px;">
            <span style="font-size:.67rem;text-transform:uppercase;letter-spacing:.07em;color:{color};font-weight:800;display:flex;align-items:center;gap:5px;">
                <span style="width:6px;height:6px;border-radius:50%;background:{color};display:inline-block;"></span>
                Prediksi Mutu Utama
            </span>
            <span style="background:{color}18;color:{color};font-size:.67rem;font-weight:700;padding:2px 8px;border-radius:9999px;font-family:'JetBrains Mono',monospace;">
                SVM-RBF
            </span>
        </div>
        <div style="display:flex;align-items:baseline;justify-content:space-between;gap:10px;flex-wrap:wrap;">
            <h2 style="margin:1px 0 2px 0;color:#1A1210;font-size:1.60rem;font-weight:800;letter-spacing:-.03em;">{safe_name}</h2>
            <div style="text-align:right;">
                <span style="font-size:.67rem;color:#9C8E84;font-weight:600;display:block;text-transform:uppercase;letter-spacing:.04em;">Confidence</span>
                <span style="font-size:1.25rem;font-weight:800;color:{color};font-family:'JetBrains Mono',monospace;">{confidence * 100:.2f}%</span>
            </div>
        </div>
        <p style="margin:3px 0 0 0;font-size:.77rem;color:#5C4F45;line-height:1.4;">{desc}</p>
    </div>
    """
    st.markdown(_clean_html(badge_html), unsafe_allow_html=True)


def render_model_result_card(result: Any) -> None:
    """Render single model inference result card — dark header + light body."""
    model_name = html.escape(str(getattr(result, "model_name", "Model")))
    pred_class = getattr(result, "predicted_class", "unknown")
    disp_name = getattr(result, "display_name", pred_class)
    conf = float(getattr(result, "confidence", 0.0))
    probs = getattr(result, "probabilities", [])
    lat = float(getattr(result, "inference_time_ms", 0.0))

    if "MobileNet" in model_name:
        arch_pill = "1024-d Penultimate"
        svg_icon = ICONS["mobilenet"]
    elif "ShuffleNet" in model_name:
        arch_pill = "1024-d Penultimate"
        svg_icon = ICONS["shufflenet"]
    else:
        arch_pill = "1280-d Penultimate"
        svg_icon = ICONS["efficientnet"]

    # Dark accent model header card
    model_header_html = f"""
    <div style="
        background: linear-gradient(135deg, #1C1109 0%, #2A1A0E 100%);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 11px;
        padding: 10px 14px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    ">
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="color:#D97706;display:flex;align-items:center;">{svg_icon}</div>
            <span style="font-weight:800;color:#F5EDE3;font-size:.93rem;letter-spacing:-.01em;">{model_name}</span>
        </div>
        <span style="font-size:.67rem;color:#A8906E;font-weight:600;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.09);padding:2px 8px;border-radius:9999px;font-family:'JetBrains Mono',monospace;">
            {arch_pill}
        </span>
    </div>
    """
    st.markdown(_clean_html(model_header_html), unsafe_allow_html=True)

    with st.container():
        render_prediction_badge(disp_name, conf, pred_class)
        st.metric("Latensi Inferensi", f"{lat:.1f} ms")
        st.caption("Distribusi Probabilitas Kelas:")
        render_probability_chart(probs)


def render_comparison_section(results: List[Any]) -> None:
    """Render side-by-side comparison for multiple models with consensus intelligence."""
    # 1. Consensus banner
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
                padding: 13px 17px;
                border-radius: 13px;
                margin-bottom: 14px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 10px;
                box-shadow: 0 1px 4px rgba(26,18,9,0.05), 0 2px 10px -2px rgba(26,18,9,0.04);
            ">
                <div style="display:flex;align-items:center;gap:11px;">
                    <div style="width:32px;height:32px;border-radius:9px;background:#D1FAE5;color:#047857;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                        {ICONS["shield_check"]}
                    </div>
                    <div>
                        <span style="font-size:.90rem;font-weight:800;color:#064E3B;display:block;">
                            Konsensus 100%: Seluruh arsitektur (3/3) mengonfirmasi mutu <u>{first_disp}</u>
                        </span>
                        <span style="font-size:.74rem;color:#047857;">
                            Kesesuaian representasi fitur solid pada MobileNetV3, ShuffleNetV2, EfficientNet-B0.
                        </span>
                    </div>
                </div>
                <span style="font-size:.78rem;font-weight:800;color:#047857;background:#1C1109;padding:5px 11px;border-radius:7px;border:1px solid rgba(5,150,105,0.25);font-family:'JetBrains Mono',monospace;">
                    Avg {avg_conf:.2f}%
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
                padding: 13px 17px;
                border-radius: 13px;
                margin-bottom: 14px;
                display: flex;
                align-items: center;
                gap: 11px;
                box-shadow: 0 1px 4px rgba(26,18,9,0.05), 0 2px 10px -2px rgba(26,18,9,0.04);
            ">
                <div style="width:32px;height:32px;border-radius:9px;background:#FEF3C7;color:#B45309;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                    {ICONS["target"]}
                </div>
                <div>
                    <span style="font-size:.90rem;font-weight:800;color:#78350F;display:block;">Konsensus Bervariasi Antar Arsitektur</span>
                    <span style="font-size:.74rem;color:#92400E;">Terdapat divergensi representasi fitur antar model. Periksa distribusi probabilitas individual di bawah.</span>
                </div>
            </div>
            """
            st.markdown(_clean_html(partial_html), unsafe_allow_html=True)

    # 2. Side-by-side columns
    cols = st.columns(len(results))
    for col, r in zip(cols, results):
        with col:
            render_model_result_card(r)

    st.markdown("---")

    # 3. Summary comparison table
    st.markdown("#### Matriks Komparasi Kinerja Arsitektur")
    table_data = []
    for r in results:
        table_data.append({
            "Arsitektur Backbone": getattr(r, "model_name", ""),
            "Prediksi Mutu": getattr(r, "display_name", ""),
            "Tingkat Keyakinan": f"{getattr(r, 'confidence', 0.0) * 100:.2f}%",
            "Latensi Inferensi": f"{getattr(r, 'inference_time_ms', 0.0):.1f} ms",
        })

    st.dataframe(pd.DataFrame(table_data), hide_index=True, width="stretch")


def render_visual_dictionary_deck() -> None:
    """Render 4-card deck for coffee bean quality classes — dark surface cards."""
    st.markdown("### Kamus Visual Mutu Biji Kopi Arabika (Dataset USK)")
    st.markdown(
        "Karakteristik fisik, cacat morfologi, dan acuan mutu standar ekspor pada skenario riset 60:20:20:"
    )

    _CLASSES = [
        {
            "key": "defect",
            "title": "Defect",
            "color": "#DC2626",
            "bg": "rgba(220,38,38,0.09)",
            "border": "rgba(220,38,38,0.22)",
            "top_border": "#DC2626",
            "badge": "Tolak Ekspor",
            "badge_bg": "rgba(220,38,38,0.12)",
            "icon": "defect",
            "desc": "Biji mengalami cacat fisik berat seperti lubang hama PBKo, pecah, hitam (black bean), berjamur, atau keriput.",
            "hint": "Diskolorasi gelap, lubang &lt;1mm, tekstur rapuh.",
        },
        {
            "key": "longberry",
            "title": "Longberry",
            "color": "#D97706",
            "bg": "rgba(217,119,6,0.09)",
            "border": "rgba(217,119,6,0.22)",
            "top_border": "#D97706",
            "badge": "Spesialitas",
            "badge_bg": "rgba(217,119,6,0.12)",
            "icon": "longberry",
            "desc": "Varietas Arabika khusus dengan bentuk biji khas memanjang dan pipih melengkung. Populer di dataran tinggi Gayo.",
            "hint": "Rasio panjang-lebar tinggi, ujung meruncing.",
        },
        {
            "key": "peaberry",
            "title": "Peaberry",
            "color": "#7C3AED",
            "bg": "rgba(124,58,237,0.09)",
            "border": "rgba(124,58,237,0.22)",
            "top_border": "#7C3AED",
            "badge": "Kopi Lanang",
            "badge_bg": "rgba(124,58,237,0.12)",
            "icon": "peaberry",
            "desc": "Biji tunggal bulat utuh tanpa belahan tengah. Terjadi karena pembuahan tunggal alami (hanya 5–10% panen).",
            "hint": "Bentuk oval bulat, celah tengah dangkal.",
        },
        {
            "key": "premium",
            "title": "Premium",
            "color": "#059669",
            "bg": "rgba(5,150,105,0.09)",
            "border": "rgba(5,150,105,0.22)",
            "top_border": "#059669",
            "badge": "Grade 1",
            "badge_bg": "rgba(5,150,105,0.12)",
            "icon": "premium",
            "desc": "Biji mutu pertama: simetris, belahan tengah rapi, densitas padat seragam, bersih dari segala cacat.",
            "hint": "Permukaan mulus, hijau kebiruan segar, ukuran seragam.",
        },
    ]

    cols = st.columns(4)
    for col, cls in zip(cols, _CLASSES):
        with col:
            st.markdown(
                _clean_html(f"""
                <div style="
                    background: #1C1109;
                    border: 1px solid {cls['border']};
                    border-top: 3px solid {cls['top_border']};
                    border-radius: 13px;
                    padding: 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.28), 0 1px 3px rgba(0,0,0,0.18);
                    height: 100%;
                ">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:6px;">
                            {ICONS[cls['icon']]}
                            <span style="font-size:.96rem;font-weight:800;color:{cls['color']};">{cls['title']}</span>
                        </div>
                        <span style="font-size:.64rem;background:{cls['badge_bg']};color:{cls['color']};font-weight:700;padding:2px 7px;border-radius:5px;">{cls['badge']}</span>
                    </div>
                    <p style="font-size:.77rem;color:#A8906E;line-height:1.4;margin-bottom:10px;">{cls['desc']}</p>
                    <div style="background:rgba(255,255,255,0.05);border-radius:7px;padding:7px 9px;font-size:.70rem;color:#6B5A44;">
                        <b style="color:#8A7560;">Ciri Kunci:</b> {cls['hint']}
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
            - **Data Latih (Training)**: `60%` sampel per kelas, digunakan untuk melatih bobot CNN & fitting SVM hyperplane.
            - **Data Validasi**: `20%` sampel, digunakan untuk tuning hyperparameter C dan Gamma RBF.
            - **Data Uji (Testing)**: `20%` sampel independen untuk benchmarking akurasi generalisasi akhir.
            - **Total Dataset**: Citra biji kopi Arabika dari repositori riset USK-Coffee.
            """
        )

        st.markdown(
            """
            #### 2. Ekstraksi Representasi Penultimate Layer
            - Menghapus lapisan klasifikasi akhir (*classifier head*) pada ketiga CNN dan menggantinya dengan `nn.Identity()`.
            - Vektor fitur diambil pasca *Global Average Pooling*:
              - **MobileNetV3-Small**: `1024-dimensi`
              - **ShuffleNetV2**: `1024-dimensi`
              - **EfficientNet-B0**: `1280-dimensi`
            """
        )

    with col_spec2:
        st.markdown(
            """
            #### 3. Support Vector Machine (SVM) Pipeline
            - **Kernel**: Radial Basis Function (RBF) non-linear.
            - **Strategi Multi-Kelas**: One-vs-Rest (OvR).
            - **Preprocessing**: `StandardScaler` terintegrasi (zero-mean unit-variance).
            - **Estimasi Probabilitas**: Numerically Stable Softmax pada `decision_function`:
            """
        )
        st.latex(r"\sigma(z)_i = \frac{e^{z_i - \max(z)}}{\sum_{j=1}^K e^{z_j - \max(z)}}")

        st.markdown(
            """
            #### 4. Standar Keamanan & Keandalan Runtime
            - **CWE-400**: `MAX_IMAGE_PIXELS = 16,777,216` px — cegah Decompression Bomb.
            - **CWE-79**: Sanitasi teks dinamis via `html.escape()`.
            - **CWE-209**: Error logging internal tanpa membocorkan trace path sistem ke client.
            """
        )


# ── State handlers ──────────────────────────────────────────────────────────

def render_idle_state() -> None:
    """Render idle/welcome state — custom card tanpa st.info() default."""
    idle_html = f"""
    <div style="
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
        border: 1px solid #FDE68A;
        border-left: 4px solid #D97706;
        border-radius: 13px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(26,18,9,0.05), 0 2px 10px -2px rgba(26,18,9,0.04);
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="width:36px;height:36px;border-radius:9px;background:#FEF3C7;color:#D97706;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:1.3rem;">✨</div>
        <div>
            <span style="font-size:.90rem;font-weight:800;color:#78350F;display:block;">Siap Melakukan Inferensi</span>
            <span style="font-size:.78rem;color:#92400E;">Unggah citra biji kopi melalui area uploader di atas untuk memulai evaluasi mutu otomatis multi-model CNN-SVM.</span>
        </div>
    </div>
    """
    st.markdown(_clean_html(idle_html), unsafe_allow_html=True)

    steps_html = f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #EDE8E3;
        border-radius: 13px;
        padding: 18px 20px;
        margin-top: 4px;
        box-shadow: 0 1px 4px rgba(26,18,9,0.04), 0 2px 10px -2px rgba(26,18,9,0.03);
    ">
        <h4 style="margin:0 0 13px 0;font-size:.90rem;font-weight:800;color:#1A1210;">Alur Kerja Pipeline Klasifikasi Mutu Kopi:</h4>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;">
            <div style="background:#1C1109;border:1px solid rgba(255,255,255,0.09);padding:12px 13px;border-radius:9px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px;">
                    <span style="font-size:.67rem;font-weight:700;color:#D97706;text-transform:uppercase;letter-spacing:.06em;">Langkah 1</span>
                    <div style="color:#D97706;">{ICONS["upload_cloud"]}</div>
                </div>
                <h5 style="margin:0 0 3px 0;font-size:.83rem;font-weight:700;color:#F5EDE3;">Unggah Citra</h5>
                <p style="margin:0;font-size:.73rem;color:#A8906E;line-height:1.35;">Upload foto biji kopi (JPG/PNG/WEBP). Resolusi otomatis dinormalisasi.</p>
            </div>
            <div style="background:#1C1109;border:1px solid rgba(255,255,255,0.09);padding:12px 13px;border-radius:9px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px;">
                    <span style="font-size:.67rem;font-weight:700;color:#A78BFA;text-transform:uppercase;letter-spacing:.06em;">Langkah 2</span>
                    <div style="color:#A78BFA;">{ICONS["cpu"]}</div>
                </div>
                <h5 style="margin:0 0 3px 0;font-size:.83rem;font-weight:700;color:#F5EDE3;">Ekstraksi Fitur</h5>
                <p style="margin:0;font-size:.73rem;color:#A8906E;line-height:1.35;">Ekstraksi representasi penultimate layer 1024-d/1280-d via PyTorch CNN.</p>
            </div>
            <div style="background:#1C1109;border:1px solid rgba(255,255,255,0.09);padding:12px 13px;border-radius:9px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px;">
                    <span style="font-size:.67rem;font-weight:700;color:#10B981;text-transform:uppercase;letter-spacing:.06em;">Langkah 3</span>
                    <div style="color:#10B981;">{ICONS["target"]}</div>
                </div>
                <h5 style="margin:0 0 3px 0;font-size:.83rem;font-weight:700;color:#F5EDE3;">Evaluasi SVM</h5>
                <p style="margin:0;font-size:.73rem;color:#A8906E;line-height:1.35;">Klasifikasi margin RBF dan kalkulasi distribusi Softmax multi-kelas.</p>
            </div>
        </div>
    </div>
    """
    st.markdown(_clean_html(steps_html), unsafe_allow_html=True)


def render_loading_state() -> Any:
    """Context manager for loading state."""
    return st.spinner("Mengekstraksi representasi fitur & mengeksekusi inferensi multi-model SVM...")


def render_empty_state() -> None:
    """Render empty state."""
    st.warning("Belum ada citra biji kopi yang diunggah. Silakan pilih berkas citra terlebih dahulu.")


def render_error_state(error_message: str) -> None:
    """Render user-friendly error box without exposing internal stack trace (CWE-209)."""
    st.error(f"Terjadi kendala: {error_message}")
    st.button("Muat Ulang Halaman", on_click=lambda: st.rerun())
