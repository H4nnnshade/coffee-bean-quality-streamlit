"""Negative and boundary value testing for coffee classification app."""

import io
import unittest
from unittest.mock import MagicMock
from PIL import Image
import numpy as np

from core.constants import MAX_FILE_SIZE_MB, MAX_IMAGE_PIXELS
from services.predictor import predict_single_model
from ui.components import render_uploader


class TestNegativeAndBoundaryScenarios(unittest.TestCase):
    """Negative testing suite: corrupted payloads, boundaries, DoS prevention."""

    def test_corrupted_file_upload(self):
        """Simulate uploaded file with random corrupted bytes."""
        mock_file = io.BytesIO(b"NOT_A_VALID_IMAGE_HEADER_1234567890\x00\xff")
        mock_file.name = "corrupt.jpg"
        mock_file.size = len(mock_file.getvalue())

        # Test render_uploader with corrupt file
        import streamlit as st
        original_uploader = st.file_uploader
        st.file_uploader = MagicMock(return_value=mock_file)
        try:
            res = render_uploader()
            self.assertIsNone(res)
        finally:
            st.file_uploader = original_uploader

    def test_zero_byte_file_upload(self):
        """Simulate 0-byte uploaded file."""
        mock_file = io.BytesIO(b"")
        mock_file.name = "empty.png"
        mock_file.size = 0

        import streamlit as st
        original_uploader = st.file_uploader
        st.file_uploader = MagicMock(return_value=mock_file)
        try:
            res = render_uploader()
            self.assertIsNone(res)
        finally:
            st.file_uploader = original_uploader

    def test_oversized_file_upload(self):
        """Simulate file exceeding MAX_FILE_SIZE_MB limit."""
        mock_file = io.BytesIO(b"fake data")
        mock_file.name = "huge.jpg"
        mock_file.size = (MAX_FILE_SIZE_MB + 1) * 1024 * 1024  # > 10 MB

        import streamlit as st
        original_uploader = st.file_uploader
        st.file_uploader = MagicMock(return_value=mock_file)
        try:
            res = render_uploader()
            self.assertIsNone(res)
        finally:
            st.file_uploader = original_uploader

    def test_extreme_dimension_decompression_bomb(self):
        """Simulate image dimensions exceeding MAX_IMAGE_PIXELS."""
        # Create a mock image report with 5000 x 5000 (> 16MP)
        img_bytes = io.BytesIO()
        # Save a 100x100 real image first
        img = Image.new("RGB", (100, 100), color=(128, 128, 128))
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        img_bytes.name = "bomb.png"
        img_bytes.size = len(img_bytes.getvalue())

        import streamlit as st
        original_uploader = st.file_uploader
        original_open = Image.open

        mock_oversize_img = MagicMock()
        mock_oversize_img.format = "PNG"
        mock_oversize_img.width = 5000
        mock_oversize_img.height = 5000

        st.file_uploader = MagicMock(return_value=img_bytes)
        Image.open = MagicMock(return_value=mock_oversize_img)
        try:
            res = render_uploader()
            self.assertIsNone(res)
        finally:
            st.file_uploader = original_uploader
            Image.open = original_open

    def test_boundary_1x1_pixel_image_inference(self):
        """Boundary test: 1x1 px minimal image through entire inference pipeline."""
        tiny_img = Image.new("RGB", (1, 1), color=(200, 100, 50))
        res = predict_single_model(tiny_img, "MobileNetV3-Small")
        self.assertIsNotNone(res)
        self.assertIn(res.predicted_class, ["defect", "longberry", "peaberry", "premium"])
        self.assertAlmostEqual(sum(p.score for p in res.probabilities), 1.0, places=4)

    def test_boundary_extreme_aspect_ratio_image_inference(self):
        """Boundary test: extreme aspect ratio 1x1000 px image through inference."""
        extreme_img = Image.new("RGB", (1, 1000), color=(50, 120, 200))
        res = predict_single_model(extreme_img, "ShuffleNetV2")
        self.assertIsNotNone(res)
        self.assertIn(res.predicted_class, ["defect", "longberry", "peaberry", "premium"])

    def test_invalid_model_key_exception(self):
        """Verify requesting non-existent model raises ValueError."""
        img = Image.new("RGB", (64, 64), color=(100, 100, 100))
        with self.assertRaises(ValueError):
            predict_single_model(img, "NonExistentModel-V99")


if __name__ == "__main__":
    unittest.main()
