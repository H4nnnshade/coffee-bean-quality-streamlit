"""Unit tests for UI components, state handling, and security sanitization."""

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from PIL import Image

from ui.components import (
    render_prediction_badge,
    render_probability_chart,
    render_model_result_card,
    render_comparison_section,
    render_image_metadata,
    render_image_preview,
    render_idle_state,
    render_empty_state,
    render_error_state,
)
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

    @patch("streamlit.warning")
    def test_render_empty_state(self, mock_warning):
        render_empty_state()
        mock_warning.assert_called_once()

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


if __name__ == "__main__":
    unittest.main()
