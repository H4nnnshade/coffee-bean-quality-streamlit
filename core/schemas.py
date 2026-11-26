"""Data schemas and domain contracts for prediction outputs."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.constants import REVIEW_THRESHOLD


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
    split_ratio: str = "60-20-20"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "predicted_class": self.predicted_class,
            "display_name": self.display_name,
            "confidence": self.confidence,
            "probabilities": [p.to_dict() for p in self.probabilities],
            "inference_time_ms": self.inference_time_ms,
            "split_ratio": self.split_ratio,
        }


@dataclass(frozen=True)
class PerModelResult:
    """
    Contract for individual model in a comparison run.
    Failed models are represented with status='failed' rather than omitted.
    """
    model_key: str                     # Exactly one of MODEL_KEYS
    status: str                        # "ok" | "failed"
    predicted_class: Optional[str]     # None when failed
    confidence: Optional[float]        # softmax over margin
    probabilities: Optional[Dict[str, float]]
    error_code: Optional[str]          # ARTIFACT_MISSING, ARTIFACT_INTEGRITY, INVALID_REQUEST, INFERENCE_ERROR
    latency_ms: Optional[float]

    @property
    def needs_review(self) -> bool:
        """Computed property: True if status is ok and confidence is strictly below threshold."""
        return self.status == "ok" and self.confidence is not None and self.confidence < REVIEW_THRESHOLD

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_key": self.model_key,
            "status": self.status,
            "predicted_class": self.predicted_class,
            "confidence": self.confidence,
            "probabilities": self.probabilities,
            "error_code": self.error_code,
            "latency_ms": self.latency_ms,
            "needs_review": self.needs_review,
        }


@dataclass(frozen=True)
class ComparisonResult:
    """
    Contract for aggregated multi-model inference across a scenario.
    Maintains strictly ordered, positional results for each model in MODEL_KEYS.
    """
    split_ratio: str
    models: List[PerModelResult]       # Length strictly == len(MODEL_KEYS), order == MODEL_KEYS
    degraded: bool                     # True if 1 <= failed_count < len(MODEL_KEYS)
    failed_count: int
    total_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "split_ratio": self.split_ratio,
            "models": [m.to_dict() for m in self.models],
            "degraded": self.degraded,
            "failed_count": self.failed_count,
            "total_time_ms": self.total_time_ms,
        }
