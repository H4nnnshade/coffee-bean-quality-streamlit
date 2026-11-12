"""Data schemas and domain contracts for prediction outputs."""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ClassProbability:
    """Individual class probability output."""
    label: str           # defect, longberry, peaberry, premium
    display_name: str    # Defect, Longberry, Peaberry, Premium
    score: float         # 0.0 - 1.0 (confidence score)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "display_name": self.display_name,
            "score": self.score,
        }


@dataclass(frozen=True)
class ModelInferenceOutput:
    """Output contract for single model inference."""
    model_name: str
    predicted_class: str
    display_name: str
    confidence: float
    probabilities: List[ClassProbability]
    inference_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "predicted_class": self.predicted_class,
            "display_name": self.display_name,
            "confidence": self.confidence,
            "probabilities": [p.to_dict() for p in self.probabilities],
            "inference_time_ms": self.inference_time_ms,
        }
