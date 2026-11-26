"""Unit tests for 12-factor configuration and path traversal containment defenses (CWE-22)."""

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from config import (
    BASE_DIR,
    CHECKPOINT_DIR,
    DEFAULT_MODEL_DIR,
    MODEL_BASE_DIR,
    SVM_DIR,
    get_checkpoint_path,
    get_svm_path,
)
from core.exceptions import ArtifactContainmentError


class TestConfigContainment(unittest.TestCase):
    """Test suite ensuring strict path confinement within the allowed model directory."""

    def test_default_model_dir_is_in_repo_and_resolved(self):
        """Assert default model directory points to resolved in-repo models/ dir."""
        expected = (BASE_DIR / "models").resolve()
        self.assertEqual(DEFAULT_MODEL_DIR, expected)
        self.assertTrue(CHECKPOINT_DIR.is_relative_to(MODEL_BASE_DIR))
        self.assertTrue(SVM_DIR.is_relative_to(MODEL_BASE_DIR))

    def test_valid_paths_resolve_without_containment_error(self):
        """Assert legitimate model and split resolution stays within checkpoint/svm dirs."""
        ckpt = get_checkpoint_path("MobileNetV3-Small", "60-20-20")
        svm = get_svm_path("MobileNetV3-Small", "60-20-20")

        self.assertTrue(ckpt.is_relative_to(CHECKPOINT_DIR))
        self.assertTrue(svm.is_relative_to(SVM_DIR))
        self.assertTrue(str(ckpt).endswith("MobileNetV3-Small_60-20-20.pt"))
        self.assertTrue(str(svm).endswith("MobileNetV3-Small_60-20-20_svm.joblib"))

    def test_path_traversal_in_model_name_raises_containment_error(self):
        """Assert path climb attempts in model_name trigger ArtifactContainmentError."""
        with self.assertRaises(ArtifactContainmentError):
            get_checkpoint_path("../../etc/passwd", "60-20-20")

        with self.assertRaises(ArtifactContainmentError):
            get_svm_path("../../../shadow", "60-20-20")

    def test_path_traversal_in_split_slug_raises_containment_error(self):
        """Assert directory traversal in split_slug triggers ArtifactContainmentError."""
        with self.assertRaises(ArtifactContainmentError):
            get_checkpoint_path("MobileNetV3-Small", "../../../etc/hosts")

        with self.assertRaises(ArtifactContainmentError):
            get_svm_path("ShuffleNetV2", "../../../../../secret")


if __name__ == "__main__":
    unittest.main()
