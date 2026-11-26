"""Unit tests for services/export.py (S6)."""

import csv
import io
import json
import unittest

from core.schemas import ComparisonResult, PerModelResult
from services.export import export_comparison_to_csv, export_comparison_to_json


class TestExportComparison(unittest.TestCase):
    def setUp(self):
        self.comp_result = ComparisonResult(
            split_ratio="60-20-20",
            models=[
                PerModelResult(
                    model_key="MobileNetV3-Small",
                    status="ok",
                    predicted_class="premium",
                    confidence=0.9250,
                    probabilities={"premium": 0.925, "defect": 0.025, "longberry": 0.025, "peaberry": 0.025},
                    error_code=None,
                    latency_ms=45.2,
                ),
                PerModelResult(
                    model_key="ShuffleNetV2",
                    status="ok",
                    predicted_class="peaberry",
                    confidence=0.5200,  # below 0.55 threshold -> needs_review=True
                    probabilities={"premium": 0.10, "defect": 0.10, "longberry": 0.28, "peaberry": 0.52},
                    error_code=None,
                    latency_ms=22.1,
                ),
                PerModelResult(
                    model_key="EfficientNet-B0",
                    status="failed",
                    predicted_class=None,
                    confidence=None,
                    probabilities=None,
                    error_code="ARTIFACT_INTEGRITY",
                    latency_ms=None,
                ),
            ],
            degraded=True,
            failed_count=1,
            total_time_ms=75.3,
        )

    def test_export_comparison_to_csv_columns_and_rows(self):
        csv_str = export_comparison_to_csv(self.comp_result)
        reader = csv.DictReader(io.StringIO(csv_str))

        expected_columns = [
            "model_key",
            "status",
            "predicted_class",
            "confidence",
            "needs_review",
            "error_code",
            "split_ratio",
        ]
        self.assertEqual(reader.fieldnames, expected_columns)

        rows = list(reader)
        self.assertEqual(len(rows), 3)

        # Row 1: ok, premium, no review
        self.assertEqual(rows[0]["model_key"], "MobileNetV3-Small")
        self.assertEqual(rows[0]["status"], "ok")
        self.assertEqual(rows[0]["predicted_class"], "premium")
        self.assertEqual(rows[0]["confidence"], "0.9250")
        self.assertEqual(rows[0]["needs_review"], "False")
        self.assertEqual(rows[0]["error_code"], "")
        self.assertEqual(rows[0]["split_ratio"], "60-20-20")

        # Row 2: ok, peaberry, confidence 0.52 < 0.55 -> needs_review True
        self.assertEqual(rows[1]["model_key"], "ShuffleNetV2")
        self.assertEqual(rows[1]["status"], "ok")
        self.assertEqual(rows[1]["predicted_class"], "peaberry")
        self.assertEqual(rows[1]["confidence"], "0.5200")
        self.assertEqual(rows[1]["needs_review"], "True")
        self.assertEqual(rows[1]["error_code"], "")
        self.assertEqual(rows[1]["split_ratio"], "60-20-20")

        # Row 3: failed model
        self.assertEqual(rows[2]["model_key"], "EfficientNet-B0")
        self.assertEqual(rows[2]["status"], "failed")
        self.assertEqual(rows[2]["predicted_class"], "")
        self.assertEqual(rows[2]["confidence"], "")
        self.assertEqual(rows[2]["needs_review"], "False")
        self.assertEqual(rows[2]["error_code"], "ARTIFACT_INTEGRITY")
        self.assertEqual(rows[2]["split_ratio"], "60-20-20")

    def test_export_comparison_to_json(self):
        json_str = export_comparison_to_json(self.comp_result)
        data = json.loads(json_str)

        self.assertEqual(data["split_ratio"], "60-20-20")
        self.assertTrue(data["degraded"])
        self.assertEqual(data["failed_count"], 1)
        self.assertEqual(data["total_time_ms"], 75.3)
        self.assertEqual(len(data["models"]), 3)

        # Check no host path in json
        self.assertNotIn("/Users/", json_str)
        self.assertNotIn("/home/", json_str)


if __name__ == "__main__":
    unittest.main()
