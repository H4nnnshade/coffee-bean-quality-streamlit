"""Integration test validating end-to-end inference across all 3 models."""

import unittest
from pathlib import Path
from PIL import Image
import numpy as np

from core.constants import CLASS_NAMES, MODEL_KEYS
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
        """Verify multi-model comparison execution."""
        results = predict_all_models(self.test_image)
        self.assertEqual(len(results), len(MODEL_KEYS))
        names = [r.model_name for r in results]
        self.assertEqual(names, MODEL_KEYS)

        for r in results:
            total_prob = sum(p.score for p in r.probabilities)
            self.assertAlmostEqual(total_prob, 1.0, places=4)


if __name__ == "__main__":
    unittest.main()
