"""Export utilities for inference results (CSV and JSON) (S6 / PRD §9)."""

import csv
import io
import json
from typing import Any, Dict

from core.schemas import ComparisonResult, PerModelResult


def export_comparison_to_csv(comp_result: ComparisonResult) -> str:
    """
    Export ComparisonResult to CSV format.
    Required columns: model_key, status, predicted_class, confidence, needs_review, error_code, split_ratio.
    Failed models maintain a row with status='failed'.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "model_key",
        "status",
        "predicted_class",
        "confidence",
        "needs_review",
        "error_code",
        "split_ratio",
    ])

    for m in comp_result.models:
        conf_str = f"{m.confidence:.4f}" if m.confidence is not None else ""
        writer.writerow([
            m.model_key,
            m.status,
            m.predicted_class or "",
            conf_str,
            str(m.needs_review),
            m.error_code or "",
            comp_result.split_ratio,
        ])

    return output.getvalue()


def export_comparison_to_json(comp_result: ComparisonResult) -> str:
    """
    Export full ComparisonResult to formatted JSON string.
    Contains no PII, no host paths.
    """
    data = comp_result.to_dict()
    return json.dumps(data, indent=2)
