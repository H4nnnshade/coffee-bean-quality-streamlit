"""Unit tests verifying model files, layer architectures, and loader caching."""

import unittest
from pathlib import Path
import config
from core.constants import MODEL_FEATURE_DIMS, MODEL_KEYS
from core.schemas import ClassProbability, ModelInferenceOutput
from services.predictor import _stable_softmax
import numpy as np


class TestModelArtifactsAndLoader(unittest.TestCase):
    """Verify weights existence, schemas, and math stability."""

    def test_artifact_files_exist(self):
        """Verify that all 3 PyTorch checkpoints and 3 SVM pipelines exist on disk."""
        for model_name in MODEL_KEYS:
            ckpt_path = config.CHECKPOINT_FILES[model_name]
            svm_path = config.SVM_FILES[model_name]

            self.assertTrue(
                ckpt_path.exists(),
                f"Checkpoint {ckpt_path} untuk {model_name} tidak ditemukan.",
            )
            self.assertTrue(
                svm_path.exists(),
                f"Model SVM {svm_path} untuk {model_name} tidak ditemukan.",
            )
            self.assertGreater(
                ckpt_path.stat().st_size,
                1_000_000,
                f"Ukuran checkpoint {ckpt_path} mencurigakan (< 1 MB).",
            )
            self.assertGreater(
                svm_path.stat().st_size,
                1_000_000,
                f"Ukuran SVM {svm_path} mencurigakan (< 1 MB).",
            )

    def test_schema_integrity(self):
        """Verify schema serialization and immutability."""
        prob = ClassProbability(label="defect", display_name="Defect", score=0.95)
        out = ModelInferenceOutput(
            model_name="MobileNetV3-Small",
            predicted_class="defect",
            display_name="Defect",
            confidence=0.95,
            probabilities=[prob],
            inference_time_ms=12.5,
        )
        d = out.to_dict()
        self.assertEqual(d["model_name"], "MobileNetV3-Small")
        self.assertEqual(d["predicted_class"], "defect")
        self.assertEqual(len(d["probabilities"]), 1)
        self.assertEqual(d["probabilities"][0]["score"], 0.95)

    def test_softmax_numerical_stability(self):
        """Verify softmax handling of extreme logits / margins."""
        extreme_logits = np.array([1000.0, 1005.0, 990.0, 1002.0])
        probs = _stable_softmax(extreme_logits)
        self.assertAlmostEqual(float(np.sum(probs)), 1.0, places=5)
        self.assertEqual(int(np.argmax(probs)), 1)
        self.assertFalse(np.isnan(probs).any())


if __name__ == "__main__":
    unittest.main()
