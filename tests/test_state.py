"""Unit tests for ui/state.py: resolve_result_state (S5 / PRD D11)."""

import unittest

from core.schemas import PerModelResult
from ui.state import resolve_result_state


class TestResolveResultState(unittest.TestCase):
    def test_all_models_ok(self):
        models = [
            PerModelResult("MobileNetV3-Small", "ok", "premium", 0.9, {}, None, 50.0),
            PerModelResult("ShuffleNetV2", "ok", "premium", 0.8, {}, None, 30.0),
            PerModelResult("EfficientNet-B0", "ok", "premium", 0.85, {}, None, 100.0),
        ]
        self.assertEqual(resolve_result_state(models), "ok")

    def test_partial_success_degraded(self):
        models = [
            PerModelResult("MobileNetV3-Small", "ok", "premium", 0.9, {}, None, 50.0),
            PerModelResult("ShuffleNetV2", "failed", None, None, None, "ARTIFACT_MISSING", None),
            PerModelResult("EfficientNet-B0", "ok", "premium", 0.85, {}, None, 100.0),
        ]
        self.assertEqual(resolve_result_state(models), "partial")

    def test_all_failed_artifact_missing_gives_empty(self):
        models = [
            PerModelResult("MobileNetV3-Small", "failed", None, None, None, "ARTIFACT_MISSING", None),
            PerModelResult("ShuffleNetV2", "failed", None, None, None, "ARTIFACT_MISSING", None),
            PerModelResult("EfficientNet-B0", "failed", None, None, None, "ARTIFACT_MISSING", None),
        ]
        self.assertEqual(resolve_result_state(models), "empty")

    def test_all_failed_with_integrity_error_gives_error(self):
        models = [
            PerModelResult("MobileNetV3-Small", "failed", None, None, None, "ARTIFACT_MISSING", None),
            PerModelResult("ShuffleNetV2", "failed", None, None, None, "ARTIFACT_INTEGRITY", None),
            PerModelResult("EfficientNet-B0", "failed", None, None, None, "ARTIFACT_MISSING", None),
        ]
        self.assertEqual(resolve_result_state(models), "error")

    def test_all_failed_with_inference_or_invalid_request_gives_error(self):
        models = [
            PerModelResult("MobileNetV3-Small", "failed", None, None, None, "INFERENCE_ERROR", None),
            PerModelResult("ShuffleNetV2", "failed", None, None, None, "INVALID_REQUEST", None),
            PerModelResult("EfficientNet-B0", "failed", None, None, None, "INFERENCE_ERROR", None),
        ]
        self.assertEqual(resolve_result_state(models), "error")

    def test_empty_models_list_gives_error(self):
        self.assertEqual(resolve_result_state([]), "error")


if __name__ == "__main__":
    unittest.main()
