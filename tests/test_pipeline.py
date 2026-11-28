"""Integration test validating end-to-end inference across all 3 models."""

import unittest
from pathlib import Path
from PIL import Image
import numpy as np

from core.constants import (
    ALLOWED_SPLITS,
    CLASS_NAMES,
    MAX_PARALLEL_WORKERS,
    MODEL_KEYS,
)
from services import predictor
from services.predictor import predict_all_models, predict_single_model

SAMPLE_IMAGE_DIR = Path(
    "/Users/agusfarhan/Ngampuscoyy/Skripsi/Dataset/USK-Coffee/USK-Coffee-Datasets"
)


class TestInferencePipeline(unittest.TestCase):
    """End-to-end integration tests for CNN-SVM classification pipeline."""

    @classmethod
    def setUpClass(cls):
        # Look for real dataset sample first, fallback to synthetic bean-like image
        peaberry_sample = SAMPLE_IMAGE_DIR / "peaberry" / "0.jpg"
        if peaberry_sample.exists():
            cls.test_image = Image.open(peaberry_sample).convert("RGB")
            cls.is_real_sample = True
        else:
            # Synthetic RGB image with size 256x256
            arr = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
            cls.test_image = Image.fromarray(arr, "RGB")
            cls.is_real_sample = False

    def test_single_model_mobilenet(self):
        """Verify MobileNetV3-Small single inference."""
        res = predict_single_model(self.test_image, "MobileNetV3-Small")
        self.assertEqual(res.model_name, "MobileNetV3-Small")
        self.assertIn(res.predicted_class, CLASS_NAMES)
        self.assertGreater(res.confidence, 0.25)
        self.assertEqual(len(res.probabilities), len(CLASS_NAMES))
        self.assertGreater(res.inference_time_ms, 0.0)

    def test_single_model_shufflenet(self):
        """Verify ShuffleNetV2 single inference."""
        res = predict_single_model(self.test_image, "ShuffleNetV2")
        self.assertEqual(res.model_name, "ShuffleNetV2")
        self.assertIn(res.predicted_class, CLASS_NAMES)
        self.assertGreater(res.confidence, 0.25)
        self.assertEqual(len(res.probabilities), len(CLASS_NAMES))
        self.assertGreater(res.inference_time_ms, 0.0)

    def test_single_model_efficientnet(self):
        """Verify EfficientNet-B0 single inference."""
        res = predict_single_model(self.test_image, "EfficientNet-B0")
        self.assertEqual(res.model_name, "EfficientNet-B0")
        self.assertIn(res.predicted_class, CLASS_NAMES)
        self.assertGreater(res.confidence, 0.25)
        self.assertEqual(len(res.probabilities), len(CLASS_NAMES))
        self.assertGreater(res.inference_time_ms, 0.0)

    def test_predict_all_models(self):
        """Verify multi-model comparison execution returning ComparisonResult."""
        comp_res = predict_all_models(self.test_image)
        self.assertEqual(len(comp_res.models), len(MODEL_KEYS))
        names = [r.model_key for r in comp_res.models]
        self.assertEqual(names, MODEL_KEYS)
        self.assertFalse(comp_res.degraded)
        self.assertEqual(comp_res.failed_count, 0)
        self.assertGreater(comp_res.total_time_ms, 0.0)

        for r in comp_res.models:
            self.assertEqual(r.status, "ok")
            self.assertIn(r.predicted_class, CLASS_NAMES)
            self.assertIsNotNone(r.confidence)
            self.assertGreater(r.confidence, 0.25)
            self.assertIsNotNone(r.probabilities)
            total_prob = sum(r.probabilities.values())
            self.assertAlmostEqual(total_prob, 1.0, places=4)
            self.assertIsInstance(r.needs_review, bool)

    def test_predict_all_models_multi_split(self):
        """Verify inference execution across all allowed split scenarios."""
        for split in ALLOWED_SPLITS:
            comp_res = predict_all_models(self.test_image, split=split)
            self.assertEqual(comp_res.split_ratio, split)
            self.assertEqual(len(comp_res.models), len(MODEL_KEYS))
            for r in comp_res.models:
                self.assertEqual(r.status, "ok")
                self.assertIn(r.predicted_class, CLASS_NAMES)
                self.assertIsNotNone(r.confidence)
                self.assertGreater(r.confidence, 0.25)
                self.assertIsNotNone(r.probabilities)
                total_prob = sum(r.probabilities.values())
                self.assertAlmostEqual(total_prob, 1.0, places=4)

    def test_predict_all_models_isolated_failure(self):
        """Assert single model failure does not abort run, marks failed, and maintains ordering."""
        from unittest.mock import patch
        from core.exceptions import ChecksumMismatchError

        # Mock ShuffleNetV2 feature extractor retrieval to simulate artifact failure
        original_get_extractor = predictor.get_feature_extractor

        def mock_get_extractor(name, split="60-20-20"):
            if name == "ShuffleNetV2":
                raise ChecksumMismatchError("Mocked hash failure for testing")
            return original_get_extractor(name, split=split)

        with patch("services.predictor.get_feature_extractor", side_effect=mock_get_extractor):
            comp_res = predict_all_models(self.test_image)

        self.assertEqual(len(comp_res.models), len(MODEL_KEYS))
        self.assertEqual([m.model_key for m in comp_res.models], MODEL_KEYS)
        self.assertTrue(comp_res.degraded)
        self.assertEqual(comp_res.failed_count, 1)

        m0, m1, m2 = comp_res.models
        self.assertEqual(m0.status, "ok")
        self.assertEqual(m1.model_key, "ShuffleNetV2")
        self.assertEqual(m1.status, "failed")
        self.assertEqual(m1.error_code, "ARTIFACT_INTEGRITY")
        self.assertIsNone(m1.predicted_class)
        self.assertEqual(m2.status, "ok")


    def test_predict_all_models_parallel_fanout(self):
        """S4: all MODEL_KEYS workers must run concurrently and keep ordering.

        A barrier of size MAX_PARALLEL_WORKERS can only be released if all three
        model tasks are in flight at the same time. A sequential loop breaks the
        barrier -> every model is mapped to a failed result -> test fails.
        """
        import threading
        from unittest.mock import patch

        barrier = threading.Barrier(MAX_PARALLEL_WORKERS, timeout=10)
        original_one = predictor._predict_one_model

        def concurrent_one(image, model_key, split="60-20-20"):
            barrier.wait()
            return original_one(image, model_key, split=split)

        with patch("services.predictor._predict_one_model", side_effect=concurrent_one):
            comp_res = predict_all_models(self.test_image)

        self.assertEqual([m.model_key for m in comp_res.models], MODEL_KEYS)
        self.assertEqual(comp_res.failed_count, 0)
        self.assertFalse(comp_res.degraded)
        self.assertLessEqual(MAX_PARALLEL_WORKERS, 3)


if __name__ == "__main__":
    unittest.main()
