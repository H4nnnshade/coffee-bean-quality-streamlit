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
        # Search calls to mock_markdown for escaped payload
        html_calls = [c[0][0] for c in mock_markdown.call_args_list if c[0]]
        full_rendered = " ".join(str(h) for h in html_calls)
        self.assertNotIn("<img src=x", full_rendered)
        self.assertIn("&lt;img src=x", full_rendered)

    @patch("streamlit.altair_chart")
    def test_render_probability_chart(self, mock_altair_chart):
        render_probability_chart(self.dummy_probs)
        mock_altair_chart.assert_called_once()

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
    def test_render_header_centered_between_logos(self, mock_markdown):
        """Verify header renders centered website title flanked by dual brand logos."""
        render_header()
        mock_markdown.assert_called_once()
        html_arg = mock_markdown.call_args[0][0]
        self.assertIn("Arabica Vision AI", html_arg)
        self.assertIn("v2.5 • Studio", html_arg)
        # Check dual logos exist (each logo contains coffee_brand_grad gradient definition and fill)
        self.assertEqual(html_arg.count("coffee_brand_grad"), 4)
        self.assertIn("text-align: center", html_arg)


if __name__ == "__main__":
    unittest.main()
