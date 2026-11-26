"""Inference service executing CNN feature extraction and SVM decision function."""

import logging
import os
import time
from typing import Dict, List, Optional, Union
import numpy as np
from PIL import Image

from core.constants import (
    ALLOWED_SPLITS,
    CLASS_DISPLAY,
    CLASS_NAMES,
    DEFAULT_SPLIT,
    MODEL_KEYS,
)
from core.exceptions import (
    ArtifactContainmentError,
    ChecksumMismatchError,
    ModelArtifactNotFoundError,
)
from core.schemas import (
    ClassProbability,
    ComparisonResult,
    ModelInferenceOutput,
    PerModelResult,
)
from services.feature_extractor import extract_features
from services.model_loader import get_feature_extractor, get_svm_classifier


def _stable_softmax(decision_values: np.ndarray) -> np.ndarray:
    """
    Numerically stable softmax applied to continuous SVM decision margin values.
    σ(z)_i = exp(z_i - max(z)) / sum(exp(z_j - max(z)))
    """
    z = np.asarray(decision_values, dtype=np.float64)
    if z.ndim > 1:
        z = np.ravel(z)
    shift_z = z - np.max(z)
    exp_z = np.exp(shift_z)
    sum_exp = np.sum(exp_z)
    if sum_exp == 0 or np.isnan(sum_exp):
        return np.ones_like(z) / len(z)
    return exp_z / sum_exp


def predict_single_model(
    image: Image.Image,
    model_name: str,
    split: str = DEFAULT_SPLIT,
) -> ModelInferenceOutput:
    """
    Execute full inference pipeline (Feature Extraction + SVM Classification)
    for a single CNN-SVM model combination under a specified split scenario.
    """
    # Defense-in-depth: validate PIL image instance and bounds
    from services.input_gate import validate_pil_image
    image = validate_pil_image(image)

    if model_name not in MODEL_KEYS:
        raise ValueError(
            f"Model '{model_name}' tidak valid. Pilihan yang tersedia: {MODEL_KEYS}"
        )

    # 1. Retrieve cached model instances for selected split
    extractor = get_feature_extractor(model_name, split=split)
    svm_classifier = get_svm_classifier(model_name, split=split)

    # 2. Measure inference duration (feature extraction + classification)
    start_time = time.perf_counter()

    features = extract_features(image, extractor)

    # 3. Decision function margin & calibrated probabilities
    decision_margins = svm_classifier.decision_function(features)
    probabilities = _stable_softmax(decision_margins)

    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000.0

    # 4. Determine winning class
    pred_idx = int(np.argmax(probabilities))
    predicted_class = CLASS_NAMES[pred_idx]
    display_name = CLASS_DISPLAY[pred_idx]
    confidence = float(probabilities[pred_idx])

    # 5. Format class probability distribution
    prob_list: List[ClassProbability] = [
        ClassProbability(
            label=CLASS_NAMES[i],
            display_name=CLASS_DISPLAY[i],
            score=float(probabilities[i]),
        )
        for i in range(len(CLASS_NAMES))
    ]

    return ModelInferenceOutput(
        model_name=model_name,
        predicted_class=predicted_class,
        display_name=display_name,
        confidence=confidence,
        probabilities=prob_list,
        inference_time_ms=round(latency_ms, 2),
        split_ratio=split,
    )


def _map_exception_to_error_code(exc: Exception) -> str:
    """Map exception hierarchy to PRD standard error_code enum."""
    if isinstance(exc, ModelArtifactNotFoundError):
        return "ARTIFACT_MISSING"
    if isinstance(exc, (ChecksumMismatchError, ArtifactContainmentError)):
        return "ARTIFACT_INTEGRITY"
    if isinstance(exc, ValueError):
        return "INVALID_REQUEST"
    return "INFERENCE_ERROR"


def predict_all_models(
    image: Image.Image,
    split: str = DEFAULT_SPLIT,
) -> ComparisonResult:
    """
    Execute inference across all three canonical models sequentially
    for side-by-side architectural comparison under a specified split scenario.
    Guarantees strict positional ordering matching MODEL_KEYS even during partial failures.
    """
    if split not in ALLOWED_SPLITS:
        raise ValueError(
            f"Skenario split '{split}' tidak didukung. Pilihan valid: {ALLOWED_SPLITS}"
        )

    # Validate image once at entry
    from services.input_gate import validate_pil_image
    clean_image = validate_pil_image(image)

    start_total = time.perf_counter()
    per_model_results: List[PerModelResult] = []

    for model_key in MODEL_KEYS:
        start_model = time.perf_counter()
        try:
            extractor = get_feature_extractor(model_key, split=split)
            svm_classifier = get_svm_classifier(model_key, split=split)

            features = extract_features(clean_image, extractor)
            decision_margins = svm_classifier.decision_function(features)
            probabilities = _stable_softmax(decision_margins)

            lat_ms = (time.perf_counter() - start_model) * 1000.0

            pred_idx = int(np.argmax(probabilities))
            pred_class = CLASS_NAMES[pred_idx]
            conf = float(probabilities[pred_idx])

            prob_dict: Dict[str, float] = {
                CLASS_NAMES[i]: float(probabilities[i]) for i in range(len(CLASS_NAMES))
            }

            per_model_results.append(
                PerModelResult(
                    model_key=model_key,
                    status="ok",
                    predicted_class=pred_class,
                    confidence=conf,
                    probabilities=prob_dict,
                    error_code=None,
                    latency_ms=round(lat_ms, 2),
                )
            )
        except Exception as exc:
            lat_ms = (time.perf_counter() - start_model) * 1000.0
            error_code = _map_exception_to_error_code(exc)
            logging.error(f"Inference error on {model_key} ({split}): {exc}", exc_info=True)
            per_model_results.append(
                PerModelResult(
                    model_key=model_key,
                    status="failed",
                    predicted_class=None,
                    confidence=None,
                    probabilities=None,
                    error_code=error_code,
                    latency_ms=round(lat_ms, 2),
                )
            )

    total_time_ms = (time.perf_counter() - start_total) * 1000.0
    failed_count = sum(1 for m in per_model_results if m.status == "failed")
    degraded = 1 <= failed_count < len(MODEL_KEYS)

    return ComparisonResult(
        split_ratio=split,
        models=per_model_results,
        degraded=degraded,
        failed_count=failed_count,
        total_time_ms=round(total_time_ms, 2),
    )
