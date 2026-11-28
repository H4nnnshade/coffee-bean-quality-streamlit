"""Unit tests for UI components, state handling, and security sanitization."""

import pathlib
import re
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from PIL import Image

from ui.components import (
    render_prediction_badge,
    render_probability_chart,
    render_compact_probability_rows,
    render_comparison_card,
    render_model_result_card,
    render_comparison_section,
    render_image_metadata,
    render_image_preview,
    render_idle_state,
    render_loading_state,
    render_empty_state,
    render_error_state,
    render_kpi_metrics_bar,
    render_export_buttons,
    _set_split_from_button,
    CLASS_COLORS,
    CLASS_LIGHT_BG,
)
from core.schemas import ComparisonResult, PerModelResult
from ui.layout import render_header


class DummyProbability:
    def __init__(self, label: str, display_name: str, score: float):
        self.label = label
        self.display_name = display_name
        self.score = score


class DummyInferenceResult:
    def __init__(
        self,
        model_name: str,
        predicted_class: str,
        display_name: str,
        confidence: float,
        probabilities: list,
        inference_time_ms: float,
    ):
        self.model_name = model_name
        self.predicted_class = predicted_class
        self.display_name = display_name
        self.confidence = confidence
        self.probabilities = probabilities
        self.inference_time_ms = inference_time_ms


class TestUIComponents(unittest.TestCase):
    def setUp(self):
        self.dummy_probs = [
            DummyProbability("defect", "Defect", 0.05),
            DummyProbability("longberry", "Longberry", 0.10),
            DummyProbability("peaberry", "Peaberry", 0.80),
            DummyProbability("premium", "Premium", 0.05),
        ]
        self.dummy_result = DummyInferenceResult(
            model_name="MobileNetV3-Small",
            predicted_class="peaberry",
            display_name="Peaberry",
            confidence=0.80,
            probabilities=self.dummy_probs,
            inference_time_ms=42.5,
        )

    @patch("streamlit.markdown")
    def test_render_prediction_badge(self, mock_markdown):
        render_prediction_badge("Peaberry", 0.80, "peaberry")
        mock_markdown.assert_called_once()
        call_arg = mock_markdown.call_args[0][0]
        self.assertIn("Peaberry", call_arg)
        self.assertIn("80.00%", call_arg)

    @patch("streamlit.markdown")
    def test_render_prediction_badge_xss_sanitization(self, mock_markdown):
        """Verify HTML injection payload is escaped (CWE-79)."""
        malicious_input = "<script>alert('xss')</script>"
        render_prediction_badge(malicious_input, 0.50, "defect")
        call_arg = mock_markdown.call_args[0][0]
        self.assertNotIn("<script>", call_arg)
        self.assertIn("&lt;script&gt;", call_arg)

    @patch("streamlit.dataframe")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_render_comparison_section_xss_sanitization(
        self, mock_markdown, mock_cols, mock_dataframe
    ):
        """Verify consensus banner escapes injected display_name."""
        mock_cols.side_effect = lambda spec, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else spec)
        ]
        malicious_name = "<img src=x onerror=alert(1)>"
        results = [
            DummyInferenceResult("MobileNet", "peaberry", malicious_name, 0.9, self.dummy_probs, 20.0),
            DummyInferenceResult("ShuffleNet", "peaberry", malicious_name, 0.9, self.dummy_probs, 20.0),
        ]
        render_comparison_section(results)
        html_calls = [c[0][0] for c in mock_markdown.call_args_list if c[0]]
        full_rendered = " ".join(str(h) for h in html_calls)
        self.assertNotIn("<img src=x", full_rendered)
        self.assertIn("&lt;img src=x", full_rendered)

    @patch("streamlit.altair_chart")
    def test_render_probability_chart(self, mock_altair_chart):
        render_probability_chart(self.dummy_probs)
        mock_altair_chart.assert_called_once()

        chart = mock_altair_chart.call_args.args[0]
        spec = chart.to_dict()
        self.assertEqual(spec["layer"][0]["encoding"]["x"]["scale"]["domain"], [0, 122])
        self.assertEqual(spec["layer"][1]["encoding"]["text"]["field"], "LabelDiagram")
        self.assertEqual(spec["layer"][1]["encoding"]["text"]["type"], "nominal")
        self.assertFalse(spec["layer"][0]["encoding"]["y"]["axis"]["labels"])
        self.assertFalse(spec["layer"][1]["encoding"]["y"]["axis"]["labels"])
        self.assertEqual(spec["layer"][1]["mark"]["dx"], 8)
        self.assertEqual(spec["layer"][1]["encoding"]["x"]["scale"]["domain"], [0, 122])
        self.assertEqual(spec["layer"][0]["encoding"]["x"]["title"], "Skor Probabilitas (%)")
        self.assertEqual(spec["layer"][0]["encoding"]["x"]["axis"]["values"], [0, 25, 50, 75, 100])
        self.assertEqual(spec["layer"][0]["encoding"]["x"]["axis"]["gridColor"], "#F1F5F9")
        self.assertEqual(spec["layer"][0]["encoding"]["x"]["axis"]["format"], ".0f")

        source = spec["datasets"][next(iter(spec["datasets"]))]
        percentages = [row["Persen"] for row in source]
        self.assertEqual(percentages, ["5.0%", "10.0%", "80.0%", "5.0%"])
        labels = [row["LabelDiagram"] for row in source]
        self.assertEqual(labels, [
            "Defect · 5.0%", "Longberry · 10.0%", "Peaberry · 80.0%", "Premium · 5.0%",
        ])
        self.assertEqual(spec["layer"][1]["encoding"]["y"], spec["layer"][0]["encoding"]["y"])

    @patch("streamlit.altair_chart")
    def test_render_probability_chart_uses_legacy_width_api_when_needed(self, mock_chart):
        render_probability_chart(self.dummy_probs)
        mock_chart.assert_called_once()
        self.assertEqual(mock_chart.call_args.kwargs, {"use_container_width": True})

    @patch("streamlit.altair_chart")
    def test_render_probability_chart_uses_stretch_width_when_supported(self, mock_chart):
        supported_signature = MagicMock(parameters={"width": object()})
        with patch("ui.components.inspect.signature", return_value=supported_signature):
            render_probability_chart(self.dummy_probs)
        self.assertEqual(mock_chart.call_args.kwargs, {"width": "stretch"})

    @patch("streamlit.metric")
    @patch("streamlit.markdown")
    @patch("streamlit.caption")
    @patch("ui.components.render_probability_chart")
    def test_render_model_result_card(
        self, mock_chart, mock_caption, mock_markdown, mock_metric
    ):
        render_model_result_card(self.dummy_result)
        self.assertTrue(mock_metric.called)
        self.assertTrue(mock_chart.called)

    @patch("streamlit.dataframe")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_render_comparison_section(
        self, mock_markdown, mock_cols, mock_dataframe
    ):
        mock_cols.side_effect = lambda spec, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else spec)
        ]
        results = [
            self.dummy_result,
            DummyInferenceResult("ShuffleNetV2", "peaberry", "Peaberry", 0.78, self.dummy_probs, 38.2),
            DummyInferenceResult("EfficientNet-B0", "peaberry", "Peaberry", 0.85, self.dummy_probs, 55.1),
        ]
        render_comparison_section(results)
        self.assertTrue(mock_dataframe.called)

    @patch("streamlit.info")
    @patch("streamlit.expander")
    def test_render_idle_state(self, mock_expander, mock_info):
        render_idle_state()
        mock_info.assert_called_once()

    @patch("streamlit.spinner")
    def test_render_loading_state(self, mock_spinner):
        render_loading_state()
        mock_spinner.assert_called_once()

    @patch("streamlit.button")
    @patch("streamlit.warning")
    def test_render_empty_state(self, mock_warning, mock_button):
        render_empty_state("60-20-20", "70-15-15")
        mock_warning.assert_called_once()
        self.assertIn("60-20-20", mock_warning.call_args[0][0])
        mock_button.assert_called_once()
        self.assertIn("70-15-15", mock_button.call_args[0][0])
        self.assertEqual(mock_button.call_args[1].get("on_click"), _set_split_from_button)
        self.assertEqual(mock_button.call_args[1].get("args"), ("70-15-15",))

    def test_empty_state_button_changes_split(self):
        """Verify callback setter changes split without StreamlitAPIException (D6/T6)."""
        mock_session = {}
        _set_split_from_button("70-15-15", mock_session)
        self.assertEqual(mock_session["kpi_split_selector"], "70-15-15")

    @patch("streamlit.download_button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_render_export_buttons(self, mock_markdown, mock_cols, mock_download):
        """Verify export buttons render CSV and JSON download buttons."""
        mock_cols.return_value = [MagicMock(), MagicMock()]
        comp = ComparisonResult(
            split_ratio="60-20-20",
            models=[],
            degraded=False,
            failed_count=0,
            total_time_ms=10.0,
        )
        render_export_buttons(comp)
        self.assertEqual(mock_download.call_count, 2)

    @patch("streamlit.markdown")
    def test_render_image_metadata(self, mock_markdown):
        """Verify image metadata card displays dimension, channel, and tensor information."""
        img = Image.new("RGB", (320, 240))
        render_image_metadata(img)
        mock_markdown.assert_called_once()
        html_arg = mock_markdown.call_args[0][0]
        self.assertIn("320 × 240 px", html_arg)
        self.assertIn("1 × 3 × 224 × 224", html_arg)
        self.assertIn("RGB (24-bit)", html_arg)

    @patch("streamlit.image")
    @patch("streamlit.markdown")
    def test_render_image_preview(self, mock_markdown, mock_image):
        """Verify image preview header and display call."""
        img = Image.new("RGB", (320, 240))
        render_image_preview(img)
        mock_markdown.assert_called_once()
        mock_image.assert_called_once_with(img, width="stretch")

    @patch("streamlit.error")
    @patch("streamlit.button")
    def test_render_error_state(self, mock_button, mock_error):
        render_error_state("Failed inference message")
        mock_error.assert_called_once()
        self.assertIn("Failed inference message", mock_error.call_args[0][0])

    @patch("streamlit.markdown")
    def test_render_header_has_single_logo_and_dashboard_hierarchy(self, mock_markdown):
        """Assert header identity, alignment, responsive wrapping, and truthful content."""
        render_header()
        mock_markdown.assert_called_once()
        html_arg = mock_markdown.call_args[0][0]
        self.assertEqual(html_arg.count("<svg "), 2)
        self.assertEqual(html_arg.count("Arabica Vision AI"), 1)
        self.assertIn("align-items:center;gap:6px;", html_arg)
        self.assertEqual(html_arg.count("<div "), html_arg.count("</div>"))
        self.assertIn("<h1 class=\"brand-title\" style=\"white-space:nowrap;margin:0", html_arg)
        self.assertIn("justify-content:center;", html_arg)
        self.assertEqual(html_arg.count("Studio Unggah Inspeksi"), 1)
        self.assertEqual(html_arg.count("coffee_brand_grad"), 2)
        self.assertIn("v2.5 • Studio", html_arg)
        self.assertIn("Alur analisis: unggah citra · periksa metadata · tinjau hasil klasifikasi", html_arg)
        self.assertIn("display:flex;align-items:center;gap:12px;flex-wrap:nowrap;", html_arg)
        self.assertNotIn("align-self:flex-start", html_arg)
        self.assertIn("width:46px;height:46px;flex:0 0 46px", html_arg)
        identity_row = html_arg.split("class=\"brand-identity-row\"", 1)[1]
        self.assertIn("<h1 class=\"brand-title\"", identity_row)
        self.assertIn("class=\"brand-version\"", identity_row)
        self.assertIn("width:46px;height:46px;flex:0 0 46px", identity_row)
        self.assertIn("gap:12px;flex-wrap:nowrap;min-width:0;", identity_row)
        self.assertIn("gap:8px;flex-wrap:nowrap;min-width:0;min-height:46px;", identity_row)
        self.assertIn("Studio Unggah Inspeksi Citra", html_arg)
        self.assertIn("Analisis mutu biji kopi Arabika", html_arg)
        self.assertIn("margin:8px 0 0 58px", html_arg)
        self.assertIn("margin:4px 0 0 58px", html_arg)
        self.assertIn("class=\"brand-identity-row\"", html_arg)
        self.assertIn("white-space:nowrap", html_arg)
        title_line = html_arg.split("<h1", 1)[1].split("</h1>", 1)[0]
        self.assertIn("margin:0", title_line)
        self.assertNotIn("transform:", title_line)
        self.assertNotIn("translateY", title_line)
        self.assertNotIn("padding-top", title_line)
        self.assertNotIn("margin-top", title_line)
        self.assertIn("line-height:1.2", title_line)
        self.assertIn("min-width:0;", identity_row)
        self.assertIn("align-items:center", html_arg)
        self.assertIn("flex-wrap:wrap", html_arg)
        self.assertNotIn("transform:", html_arg)
        self.assertNotIn("translateY", html_arg)
        self.assertNotIn("padding-top", html_arg.split("<h1", 1)[1].split("</h1>", 1)[0])
        self.assertNotIn("Studio Unggah & Inspeksi Citra", html_arg)
        self.assertNotIn("3 arsitektur model", html_arg)
        self.assertNotIn("arsitektur model", html_arg)
        self.assertNotIn("Split 60:20:20", html_arg)
        self.assertNotIn("ready", html_arg.lower())
        self.assertNotIn("online", html_arg.lower())

    @patch("streamlit.markdown")
    def test_render_header_has_aligned_identity_and_context_icons(self, mock_markdown):
        render_header()
        html_arg = mock_markdown.call_args[0][0]
        self.assertEqual(html_arg.count("<svg "), 2)
        self.assertEqual(html_arg.count("coffee_brand_grad"), 2)
        self.assertIn("Studio Unggah Inspeksi Citra", html_arg)
        self.assertIn("align-items:center;gap:6px;", html_arg)

    @patch("streamlit.radio")
    @patch("streamlit.popover")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_render_kpi_metrics_bar_dynamic_split(self, mock_markdown, mock_cols, mock_popover, mock_radio):
        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_popover.return_value.__enter__.return_value = MagicMock()
        mock_radio.side_effect = lambda *args, **kwargs: kwargs.get("options", ["60-20-20"])[kwargs.get("index", 0)]

        # Test default split
        chosen = render_kpi_metrics_bar()
        self.assertEqual(chosen, "60-20-20")
        # WCAG 4.1.2: popover trigger must carry a non-empty accessible name
        mock_popover.assert_called_with(
            "Pilih skenario split", help="Klik untuk memilih skenario rasio dataset"
        )
        self.assertEqual(mock_radio.call_args[1]["index"], 0)

        # Check card content rendered exact title, icon, and split text
        calls = [c[0][0] for c in mock_markdown.call_args_list if c[0]]
        full_text = " ".join(str(c) for c in calls)
        self.assertIn("Skenario Riset", full_text)
        self.assertIn("60:20:20 Split", full_text)
        self.assertIn("Train • Val • Test Stratified", full_text)

        # Test custom split
        mock_popover.reset_mock()
        mock_radio.reset_mock()
        mock_markdown.reset_mock()
        chosen = render_kpi_metrics_bar(selected_split="70-15-15")
        self.assertEqual(chosen, "70-15-15")
        self.assertEqual(mock_radio.call_args[1]["index"], 1)

        calls = [c[0][0] for c in mock_markdown.call_args_list if c[0]]
        full_text = " ".join(str(c) for c in calls)
        self.assertIn("70:15:15 Split", full_text)

        # Verify format_func renders cleanly
        format_func = mock_radio.call_args[1]["format_func"]
        self.assertEqual(format_func("70-15-15"), "70:15:15 Split")
        self.assertEqual(format_func("80-10-10"), "80:10:10 Split")

    @patch("streamlit.radio")
    @patch("streamlit.popover")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_render_kpi_metrics_bar_themed_colors(self, mock_markdown, mock_cols, mock_popover, mock_radio):
        """Verify the 4 KPI cards use the high-dynamic-range crypto gradients (ARCHITECTURE.md §19)."""
        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_popover.return_value.__enter__.return_value = MagicMock()
        render_kpi_metrics_bar()

        calls = [c[0][0] for c in mock_markdown.call_args_list if c[0]]
        full_text = " ".join(str(c) for c in calls)

        # Keempat kartu memakai arah 115deg sesuai §19.
        self.assertNotIn("linear-gradient(135deg, #", full_text)

        # Card 1 - Mint/Teal to Electric Blue
        self.assertIn("linear-gradient(115deg, #008572 0%, #0071EF 100%)", full_text)
        self.assertIn("rgba(0, 133, 114, 0.40)", full_text)

        # Card 2 - Violet to Neon Magenta/Pink
        self.assertIn("linear-gradient(115deg, #7047EB 0%, #E50B6A 100%)", full_text)
        self.assertIn("rgba(112, 71, 235, 0.40)", full_text)

        # Card 3 - Warm Amber/Peach to Coral/Rose
        self.assertIn("linear-gradient(115deg, #BC5A00 0%, #EC002B 100%)", full_text)
        self.assertIn("rgba(188, 90, 0, 0.40)", full_text)

        # Card 4 - Royal Indigo to Periwinkle Lavender
        self.assertIn("linear-gradient(115deg, #4E36E2 0%, #7B55FF 100%)", full_text)
        self.assertIn("rgba(78, 54, 226, 0.40)", full_text)

        # Shared typography & border tokens (text-shadow enhancement §19.2)
        self.assertIn("rgba(255, 255, 255, 0.20)", full_text)
        self.assertIn("text-shadow: 0 1px 3px rgba(0, 0, 0, 0.45)", full_text)
        self.assertIn("#FFFFFF", full_text)
        self.assertIn("background: rgba(255, 255, 255, 0.22)", full_text)

        # §19.1 poin 4: label/subtitle WAJIB solid #FFFFFF, bukan alpha.
        # Tanpa assertNotIn ini, regresi ke rgba(0.88/0.90) lolos diam-diam.
        self.assertNotIn("rgba(255, 255, 255, 0.88)", full_text)
        self.assertNotIn("rgba(255, 255, 255, 0.90)", full_text)


class TestRenderComparisonCard(unittest.TestCase):
    """Unit tests for render_comparison_card (ARCHITECTURE.md §13 Opsi A)."""

    def setUp(self):
        self.dummy_probs = [
            DummyProbability("defect", "Defect", 0.05),
            DummyProbability("peaberry", "Peaberry", 0.80),
            DummyProbability("premium", "Premium", 0.15),
        ]
        self.dummy_result = DummyInferenceResult(
            model_name="MobileNetV3-Small",
            predicted_class="peaberry",
            display_name="Peaberry",
            confidence=0.80,
            probabilities=self.dummy_probs,
            inference_time_ms=42.5,
        )

    @patch("streamlit.metric")
    @patch("streamlit.markdown")
    @patch("streamlit.caption")
    @patch("ui.components.render_compact_probability_rows")
    @patch("ui.components.render_probability_chart")
    def test_comparison_card_uses_compact_not_altair(
        self, mock_altair, mock_compact, mock_caption, mock_markdown, mock_metric
    ):
        """render_comparison_card must call render_compact_probability_rows, not render_probability_chart."""
        render_comparison_card(self.dummy_result)
        self.assertTrue(mock_compact.called, "render_compact_probability_rows must be called")
        self.assertFalse(mock_altair.called, "render_probability_chart must NOT be called")

    @patch("streamlit.metric")
    @patch("streamlit.markdown")
    @patch("streamlit.caption")
    @patch("ui.components.render_compact_probability_rows")
    def test_comparison_card_calls_metric(
        self, mock_compact, mock_caption, mock_markdown, mock_metric
    ):
        """render_comparison_card must render confidence and latency metrics."""
        render_comparison_card(self.dummy_result)
        self.assertTrue(mock_metric.called)


class TestRenderCompactProbabilityRows(unittest.TestCase):
    """Unit tests for render_compact_probability_rows (ARCHITECTURE.md §13.6)."""

    def setUp(self):
        self.dummy_probs = [
            {"label": "defect", "display_name": "Defect", "score": 0.05},
            {"label": "longberry", "display_name": "Longberry", "score": 0.10},
            {"label": "peaberry", "display_name": "Peaberry", "score": 0.80},
            {"label": "premium", "display_name": "Premium", "score": 0.05},
        ]

    @patch("streamlit.markdown")
    def test_sort_descending(self, mock_markdown):
        """Rows sorted descending by score (Peaberry 80% first)."""
        render_compact_probability_rows(self.dummy_probs)
        rendered = mock_markdown.call_args[0][0]
        idx_pea = rendered.index("Peaberry")
        idx_long = rendered.index("Longberry")
        idx_def = rendered.index("Defect")
        self.assertLess(idx_pea, idx_long)
        self.assertLess(idx_long, idx_def)

    @patch("streamlit.markdown")
    def test_display_name_xss_escaped(self, mock_markdown):
        """HTML injection in display_name must be escaped (CWE-79)."""
        probs = [{"label": "defect", "display_name": "<script>alert(1)</script>", "score": 0.5}]
        render_compact_probability_rows(probs)
        rendered = mock_markdown.call_args[0][0]
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    @patch("streamlit.markdown")
    def test_display_name_none_falls_back_to_label(self, mock_markdown):
        """display_name=None must not render 'None'; fall back to label."""
        probs = [{"label": "peaberry", "display_name": None, "score": 0.9}]
        render_compact_probability_rows(probs)
        rendered = mock_markdown.call_args[0][0]
        self.assertNotIn(">None<", rendered)
        self.assertIn("peaberry", rendered)

    @patch("streamlit.markdown")
    def test_unknown_class_uses_fallback_color(self, mock_markdown):
        """Unrecognised class label must fall back to the brand violet, not KeyError."""
        probs = [{"label": "exotic_new_class", "display_name": "Exotic", "score": 0.7}]
        render_compact_probability_rows(probs)
        rendered = mock_markdown.call_args[0][0]
        self.assertIn("#4E36E2", rendered)

    @patch("streamlit.markdown")
    def test_score_nan_renders_zero_width(self, mock_markdown):
        """NaN score must clamp to 0% bar width, not crash or inject 'nan%'."""
        import math
        probs = [{"label": "defect", "display_name": "Defect", "score": math.nan}]
        render_compact_probability_rows(probs)
        rendered = mock_markdown.call_args[0][0]
        self.assertIn("width:0.00%", rendered)
        self.assertNotIn("nan", rendered.lower())

    @patch("streamlit.markdown")
    def test_score_above_one_clamps_to_100_percent(self, mock_markdown):
        """score=1.5 must clamp to 100% bar width, not 150%."""
        probs = [{"label": "premium", "display_name": "Premium", "score": 1.5}]
        render_compact_probability_rows(probs)
        rendered = mock_markdown.call_args[0][0]
        self.assertIn("width:100.00%", rendered)
        self.assertNotIn("150", rendered)

    @patch("streamlit.markdown")
    def test_label_key_absent_from_markup(self, mock_markdown):
        """label_key (raw label string) must not appear as HTML attr or class."""
        probs = [{"label": "peaberry", "display_name": "Peaberry", "score": 0.9}]
        render_compact_probability_rows(probs)
        rendered = mock_markdown.call_args[0][0]
        self.assertNotIn('class="row-peaberry"', rendered)
        self.assertNotIn('data-key="peaberry"', rendered)


class TestClassChipContrast(unittest.TestCase):
    """Regresi kontras chip kelas (ARCHITECTURE.md §19.4, WCAG AA SC 1.4.3)."""

    def _ratio(self, fg: str, bg: str) -> float:
        def _lin(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        def _rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

        def _lum(h):
            r, g, b = _rgb(h)
            return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

        hi, lo = sorted((_lum(fg), _lum(bg)), reverse=True)
        return (hi + 0.05) / (lo + 0.05)

    def test_all_class_chips_meet_wcag_aa(self):
        """Setiap pasangan CLASS_COLORS vs CLASS_LIGHT_BG wajib >= 4.5:1."""
        for key, fg in CLASS_COLORS.items():
            bg = CLASS_LIGHT_BG[key]
            with self.subTest(cls=key):
                self.assertGreaterEqual(
                    self._ratio(fg, bg), 4.5,
                    f"{key}: {fg} on {bg} gagal WCAG AA",
                )

    def test_class_chip_tokens_are_locked(self):
        """Token §19.4 dikunci: regresi ke hex kontras-rendah harus gagal."""
        self.assertEqual(CLASS_COLORS["defect"], "#BE123C")
        self.assertEqual(CLASS_COLORS["longberry"], "#B45309")
        self.assertEqual(CLASS_COLORS["premium"], "#047857")
        self.assertEqual(CLASS_COLORS["peaberry"], "#2563EB")
        # Hex lama yang gagal AA tidak boleh kembali.
        for stale in ("#E11D48", "#D97706", "#059669"):
            self.assertNotIn(stale, CLASS_COLORS.values())



class TestNoStaleHexTextColor(unittest.TestCase):
    """Tripwire sumber: hex kontras-rendah tidak boleh dipakai sebagai `color:`
    (ARCHITECTURE.md 19.4 / 19.6, WCAG AA SC 1.4.3)."""

    SOURCE = pathlib.Path(__file__).resolve().parents[1] / "ui" / "components.py"

    # Deklarasi non-text (ambang SC 1.4.11 = 3:1) dibuang sebelum pemeriksaan.
    _NON_TEXT = re.compile(r"(?:border[a-z-]*|background|box-shadow|fill|stroke)\s*:\s*[^;\"\']*")

    def _text_only(self, src: str) -> str:
        return self._NON_TEXT.sub("", src)

    def test_no_stale_hex_as_text_color(self):
        """Nol sisa #E11D48 / #059669 / #DC2626 / #D97706 sebagai warna teks."""
        text_only = self._text_only(self.SOURCE.read_text(encoding="utf-8"))
        for stale in ("#E11D48", "#059669", "#DC2626", "#D97706"):
            self.assertNotIn(stale, text_only, f"{stale} masih dipakai sebagai warna teks")

    def test_tripwire_has_teeth(self):
        """Injeksi palsu `color: #059669` wajib tertangkap; non-text wajib lolos."""
        poisoned = self._text_only('<div style="font-size:0.66rem;color: #059669;">x</div>')
        self.assertIn("#059669", poisoned)
        allowed = self._text_only('<div style="border-left: 4px solid #059669; background:#ECFDF5;"></div>')
        self.assertNotIn("#059669", allowed)


class TestSlate500OnSlate100Pill(unittest.TestCase):
    """Teks di atas `#F1F5F9` wajib `#475569` (ARCHITECTURE.md §19.8, §19.4).

    `#64748B` di atas `#F1F5F9` hanya 4.34:1 -> FAIL WCAG AA SC 1.4.3.
    Cakupan wajib tiga berkas: `ui/components.py`, `ui/layout.py`, `app.py`.
    Tripwire file-scoped = hijau palsu; dua situs nyata (tab bar + pill header)
    tinggal di berkas yang tidak pernah dibaca test lama.
    """

    ROOT = pathlib.Path(__file__).resolve().parents[1]
    SOURCES = ("ui/components.py", "ui/layout.py", "app.py")
    TAG = re.compile(r"<span[^>]*>")
    RULE = re.compile(r"([^{}]*)\{([^{}]*)\}")

    def _slate100_tags(self, src: str):
        """Tag `<span>` yang mengecat dirinya sendiri dengan `#F1F5F9`."""
        out = []
        for m in self.TAG.finditer(src):
            tag = m.group(0)
            if re.search(r"background\s*:\s*#F1F5F9", tag, re.IGNORECASE):
                out.append(tag)
        return out

    def test_no_slate500_on_slate100_pill(self):
        """Semua berkas: tag `#F1F5F9` tidak boleh ber-`color: #64748B`."""
        checked_by_file = {}
        for rel in self.SOURCES:
            src = (self.ROOT / rel).read_text(encoding="utf-8")
            hits = self._slate100_tags(src)
            checked_by_file[rel] = len(hits)
            for tag in hits:
                self.assertNotIn(
                    "#64748B", tag,
                    f"{rel}: teks di atas #F1F5F9 wajib #475569 (6.92:1), bukan #64748B (4.34:1)",
                )
        # Guard per berkas: markup berubah -> tripwire tidak boleh hijau diam-diam.
        self.assertGreaterEqual(checked_by_file["ui/components.py"], 2,
                                "tripwire kehilangan target pill di ui/components.py")
        self.assertGreaterEqual(checked_by_file["app.py"], 1,
                                "tripwire kehilangan target pill di app.py")

    def test_tabbar_slate100_uses_slate700(self):
        """Tab bar: tablist `#F1F5F9` -> tab tidak terpilih wajib `#475569`."""
        src = (self.ROOT / "ui" / "layout.py").read_text(encoding="utf-8")
        rules = [(sel, body) for sel, body in self.RULE.findall(src)]
        tablist = [(s, b) for s, b in rules if 'role="tablist"' in s]
        self.assertEqual(len(tablist), 1, "tripwire kehilangan target [role=tablist]")
        self.assertIn("#F1F5F9", tablist[0][1].upper(),
                      "tablist wajib tetap #F1F5F9 (background tidak dipatch)")
        tabs = [(s, b) for s, b in rules if 'data-testid="stTab"' in s]
        self.assertTrue(tabs, "tripwire kehilangan target [data-testid=stTab]")
        checked = 0
        for sel, body in tabs:
            m = re.search(r"color\s*:\s*(#[0-9A-Fa-f]{6})", body)
            if m:
                checked += 1
                self.assertNotEqual(
                    m.group(1).upper(), "#64748B",
                    "label tab di atas #F1F5F9 wajib #475569 (6.92:1), bukan #64748B (4.34:1)",
                )
        self.assertGreaterEqual(checked, 1, "tripwire kehilangan deklarasi color tab")

    def test_tripwire_has_teeth(self):
        """Tag pill palsu ber-`#64748B` wajib tertangkap oleh pola yang dipakai."""
        poisoned = '<span style="font-size:0.68rem;color:#64748B;background:#F1F5F9;">x</span>'
        tags = self._slate100_tags(poisoned)
        self.assertEqual(len(tags), 1)
        self.assertIn("#64748B", tags[0])


class TestUploaderHeaderNoChrome(unittest.TestCase):
    """Tripwire inline-style: `.upload-studio-header` dilarang punya chrome.

    ARCHITECTURE.md 20.11 (dikunci, bentuk final). Scope = atribut `style`
    milik `<div class="upload-studio-header">` di `app.py` saja.
    Bentuk region-slice gugur (3 FP di span badge), substring `"position:"`
    gugur (mem-ban `position: static` yang diwajibkan 20.9 poin 5).
    """

    ROOT = pathlib.Path(__file__).resolve().parents[1]
    BANNED = ("background", "border", "border-radius", "box-shadow",
              "position: absolute", "position: fixed")

    def _style_block(self, src: str) -> str:
        anchor = src.index('class="upload-studio-header"')
        start = src.index('style="', anchor)
        return src[start:src.index('">', start)]

    def test_uploader_header_has_no_chrome(self):
        src = (self.ROOT / "app.py").read_text(encoding="utf-8")
        block = self._style_block(src)
        # Tiga guard: slice terpotong / menelan markup anak / tidak terambil.
        self.assertLess(len(block), 400, "slice style header terpotong")
        self.assertNotIn("<div", block.lower(), "slice menelan markup anak")
        self.assertIn("display: flex", block.lower(), "blok style header tidak terambil")
        # CSS case-insensitive (20.11.1): nama properti + `position:` dinormalkan
        # ke huruf kecil sebelum diperiksa, kalau tidak `BACKGROUND:` lolos.
        low = block.lower()
        for prop in self.BANNED:
            self.assertNotIn(prop, low,
                             f".upload-studio-header dilarang {prop} (20.9 poin 2)")

    def test_tripwire_has_teeth(self):
        """Enam injeksi chrome wajib tertangkap; `position: static` wajib lolos."""
        src = (self.ROOT / "app.py").read_text(encoding="utf-8")
        good = self._style_block(src)
        self.assertEqual([p for p in self.BANNED if p in good], [])
        for inject in ("background: #FFFFFF;", "border: 1px solid #E2E8F0;",
                       "border-radius: 12px;", "box-shadow: 0 1px 3px rgba(0,0,0,.1);",
                       "position: absolute;", "position: fixed;",
                       # Varian kapital (20.11.1): CSS tidak peduli huruf.
                       "BACKGROUND: #FFFFFF;", "Border: 1px solid #E2E8F0;",
                       "BORDER-RADIUS: 12px;", "BOX-SHADOW: 0 1px 3px rgba(0,0,0,.1);",
                       "POSITION: ABSOLUTE;", "Position: Fixed;"):
            poisoned = good.replace("display: flex;", "display: flex;" + inject)
            self.assertNotEqual(poisoned, good)
            hits = [p for p in self.BANNED if p in poisoned.lower()]
            self.assertTrue(hits, f"injeksi {inject!r} tidak tertangkap")
        for safe in ("position: static;", "POSITION: STATIC;"):
            static_ok = good.replace("display: flex;", "display: flex; " + safe)
            self.assertNotEqual(static_ok, good)
            self.assertEqual([p for p in self.BANNED if p in static_ok.lower()], [],
                             f"{safe} sah (20.9 poin 5)")


class TestNoImportantChromeOverride(unittest.TestCase):
    """Tripwire stylesheet: rule yang menyebut `.upload-studio-header` di blok
    `<style>` dilarang me-force properti geometri/chrome dengan `!important`.

    ARCHITECTURE.md 20.12. Cakupan tiga berkas (`app.py`, `ui/layout.py`,
    `ui/components.py`) karena ketiganya memasang `unsafe_allow_html=True`.
    Ekstraksi `<style>` wajib lebih dulu: regex rule atas source Python mentah
    mencocokkan brace docstring/dict (`SEL: ...`, `BODY: selected_split`).
    Batas: perlu, tidak cukup (lihat 20.13 pintu keempat).
    """

    ROOT = pathlib.Path(__file__).resolve().parents[1]
    SOURCES = ("app.py", "ui/layout.py", "ui/components.py")
    STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
    RULE = re.compile(r"([^{}]*upload-studio-header[^{}]*)\{([^{}]*)\}", re.S)
    GEOM_PROPS = ("padding", "margin", "background", "border", "border-radius",
                  "box-shadow")
    # 20.12.1: `!important`, nama properti, dan nilai `position` case-insensitive
    # per spec CSS. Tanpa re.I, `PADDING: 14px !IMPORTANT` lolos utuh.
    POS = re.compile(r"\bposition\s*:\s*(?:absolute|fixed)\b[^;]*!important", re.I)

    def _scan(self, src: str):
        """Kembalikan (n_blocks, n_rules, hits) untuk satu berkas."""
        hits, rules = [], 0
        blocks = self.STYLE_BLOCK.findall(src)
        for block in blocks:
            for m in self.RULE.finditer(block):
                rules += 1
                selector, body = m.group(1).strip(), m.group(2)
                for prop in self.GEOM_PROPS:
                    if re.search(rf"\b{prop}[^;]*!important", body, re.I):
                        hits.append((selector, prop))
                        break
                if self.POS.search(body):
                    hits.append((selector, "position:absolute|fixed"))
        return len(blocks), rules, hits

    # Guard per-berkas (20.12.1): agregat `>= 1` menyembunyikan kerusakan, karena
    # `ui/layout.py` sendirian sudah memenuhi ambang saat berkas lain nol blok.
    EXPECTED_BLOCKS = {"app.py": 0, "ui/layout.py": 1, "ui/components.py": 0}

    def test_no_important_chrome_override_for_uploader_header(self):
        seen = {}
        report = []
        for path in self.SOURCES:
            src = (self.ROOT / path).read_text(encoding="utf-8")
            blocks, rules, hits = self._scan(src)
            seen[path] = blocks
            report.append(f"{path}: blocks={blocks} rules={rules} hits={len(hits)}")
            for selector, prop in hits:
                self.fail(f"{path}: {selector} dilarang me-force {prop} !important "
                          f"(20.9 poin 2/5)")
        for path, expected in self.EXPECTED_BLOCKS.items():
            self.assertEqual(
                seen[path], expected,
                f"{path}: blok <style> terbaca {seen[path]}, harusnya {expected} - "
                f"ekstraksi rusak, semua pemeriksaan berkas ini lolos buta")
        print("[20.12] " + " | ".join(report))

    def test_tripwire_has_teeth(self):
        """Injeksi rule ke blok `<style>` nyata wajib tertangkap; versi
        tanpa `!important` wajib lolos (kosmetik, nol efek geometri)."""
        src = (self.ROOT / "ui/layout.py").read_text(encoding="utf-8")
        blocks, rules, hits = self._scan(src)
        self.assertGreaterEqual(blocks, 1)
        self.assertEqual(hits, [], "baseline ui/layout.py sudah memuat chrome !important")
        inject = (".upload-studio-header { padding: 14px 18px !important; "
                  "margin-bottom: 14px !important; }")
        poisoned = src.replace("</style>", inject + "</style>", 1)
        self.assertNotEqual(poisoned, src)
        blocks2, rules2, hits2 = self._scan(poisoned)
        self.assertEqual(blocks2, blocks)
        self.assertEqual(rules2, rules + 1, "rule injeksi tidak terbaca")
        self.assertTrue(hits2, "injeksi !important tidak tertangkap")
        for upper in (".upload-studio-header { PADDING: 14px !IMPORTANT; }",
                      ".upload-studio-header { Padding: 14px !Important; }",
                      ".upload-studio-header { MARGIN-BOTTOM: 14px !IMPORTANT; }",
                      ".upload-studio-header { POSITION: FIXED !IMPORTANT; }"):
            poisoned_upper = src.replace("</style>", upper + "</style>", 1)
            self.assertNotEqual(poisoned_upper, src)
            hits_upper = self._scan(poisoned_upper)[2]
            self.assertTrue(hits_upper, f"injeksi kapital {upper!r} tidak tertangkap")
        cos = src.replace("</style>", ".upload-studio-header { background: #FFF; }</style>", 1)
        self.assertEqual(self._scan(cos)[2], [], "background tanpa !important harus lolos")
        for safe_pos in ("position: static !important;", "POSITION: STATIC !IMPORTANT;"):
            static_important = src.replace(
                "</style>",
                f".upload-studio-header {{ {safe_pos} }}</style>", 1)
            self.assertEqual(self._scan(static_important)[2], [],
                             f"{safe_pos} sah (20.9 poin 5)")


if __name__ == "__main__":
    unittest.main()
