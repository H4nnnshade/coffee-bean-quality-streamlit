"""Tests for artifact integrity, SHA-256 verification, and fail-closed security guards."""

import io
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import joblib
import torch

import config
from core.constants import DEFAULT_SPLIT, MODEL_KEYS
from core.exceptions import ChecksumMismatchError, ModelArtifactNotFoundError
from services.model_loader import (
    load_feature_extractor,
    load_manifest,
    load_svm_classifier,
    verify_and_buffer_artifact,
)


class TestArtifactIntegrity(unittest.TestCase):
    """Test suite ensuring strict artifact verification before any deserialization."""

    def setUp(self):
        load_manifest.cache_clear()
        if hasattr(load_feature_extractor, "clear"):
            load_feature_extractor.clear()
        if hasattr(load_svm_classifier, "clear"):
            load_svm_classifier.clear()

    def tearDown(self):
        load_manifest.cache_clear()
        if hasattr(load_feature_extractor, "clear"):
            load_feature_extractor.clear()
        if hasattr(load_svm_classifier, "clear"):
            load_svm_classifier.clear()

    def test_manifest_contains_exactly_18_entries(self):
        """Assert manifest has exactly 18 entries, relative paths, no duplicates."""
        manifest = load_manifest()
        self.assertEqual(len(manifest), 18)
        for rel_path, digest in manifest.items():
            self.assertFalse(rel_path.startswith("/"))
            self.assertTrue(rel_path.startswith("models/"))
            self.assertEqual(len(digest), 64)
            self.assertNotEqual(rel_path, "models/MANIFEST.sha256")

    def test_git_tracked_artifacts_match_manifest_exactly(self):
        """Assert git-tracked model artifacts set matches manifest exactly (no orphaned models)."""
        res = subprocess.run(
            ["git", "ls-files", "models"],
            cwd=str(config.BASE_DIR),
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        tracked = {
            line.strip()
            for line in res.stdout.splitlines()
            if line.strip() and not line.strip().endswith("MANIFEST.sha256")
        }
        manifest = set(load_manifest().keys())
        self.assertEqual(tracked, manifest, "Git tracked models and manifest must match exactly")

    def test_tampered_artifact_fails_before_joblib_unpickle(self):
        """
        Event-order test: Ensure tamper raises ChecksumMismatchError
        and joblib.load is NEVER invoked (tripwire assertion).
        """
        # Ensure manifest is already cached before patching file open
        load_manifest()

        svm_path = config.get_svm_path("MobileNetV3-Small", DEFAULT_SPLIT)
        real_bytes = svm_path.read_bytes()

        # Flip 1 byte in the content
        tampered_bytes = bytearray(real_bytes)
        tampered_bytes[0] ^= 0xFF

        def tripwire_load(*args, **kwargs):
            self.fail("SECURITY VIOLATION: joblib.load() called on tampered artifact buffer!")

        with patch("services.model_loader.open", create=True) as mock_builtin_open:
            pass

        # Use patch on builtins.open directly
        real_builtin_open = open

        def selective_builtin_open(file, *args, **kwargs):
            if str(Path(file).resolve()) == str(svm_path.resolve()):
                return io.BytesIO(tampered_bytes)
            return real_builtin_open(file, *args, **kwargs)

        with patch("builtins.open", side_effect=selective_builtin_open):
            with patch("joblib.load", side_effect=tripwire_load):
                with self.assertRaises(ChecksumMismatchError):
                    load_svm_classifier("MobileNetV3-Small", DEFAULT_SPLIT)

    def test_tampered_artifact_fails_before_torch_load(self):
        """
        Event-order test: Ensure checkpoint tamper raises ChecksumMismatchError
        and torch.load is NEVER invoked (tripwire assertion).
        """
        # Ensure manifest is already cached before patching file open
        load_manifest()

        ckpt_path = config.get_checkpoint_path("MobileNetV3-Small", DEFAULT_SPLIT)
        real_bytes = ckpt_path.read_bytes()

        tampered_bytes = bytearray(real_bytes)
        tampered_bytes[0] ^= 0xFF

        def tripwire_torch(*args, **kwargs):
            self.fail("SECURITY VIOLATION: torch.load() called on tampered checkpoint buffer!")

        real_builtin_open = open

        def selective_builtin_open(file, *args, **kwargs):
            if str(Path(file).resolve()) == str(ckpt_path.resolve()):
                return io.BytesIO(tampered_bytes)
            return real_builtin_open(file, *args, **kwargs)

        with patch("builtins.open", side_effect=selective_builtin_open):
            with patch("torch.load", side_effect=tripwire_torch):
                with self.assertRaises(ChecksumMismatchError):
                    load_feature_extractor("MobileNetV3-Small", DEFAULT_SPLIT)

    def test_missing_manifest_fails_closed(self):
        """Assert loader refuses to load when manifest is missing."""
        with patch("services.model_loader._get_manifest_path") as mock_get_manifest:
            mock_get_manifest.return_value = config.BASE_DIR / "models" / "NON_EXISTENT_MANIFEST.sha256"
            with self.assertRaises(ChecksumMismatchError):
                load_manifest()

    def test_unlisted_artifact_rejected(self):
        """Assert unlisted artifact path is rejected by manifest guard."""
        fake_path = config.BASE_DIR / "models" / "checkpoint" / "GhostModel_60-20-20.pt"
        with patch.object(Path, "is_file", return_value=True):
            with self.assertRaises(ChecksumMismatchError):
                verify_and_buffer_artifact(fake_path)

    def test_legitimate_artifacts_verify_and_load_cleanly(self):
        """Assert genuine registered artifacts pass checksum and load with weights_only=True."""
        model = load_feature_extractor("MobileNetV3-Small", DEFAULT_SPLIT)
        self.assertIsNotNone(model)
        svm = load_svm_classifier("MobileNetV3-Small", DEFAULT_SPLIT)
        self.assertIsNotNone(svm)


if __name__ == "__main__":
    unittest.main()
