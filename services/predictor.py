"""Inference service executing CNN feature extraction and SVM decision function."""

import time
from typing import List, Union
import numpy as np
from PIL import Image

from core.constants import CLASS_DISPLAY, CLASS_NAMES, MODEL_KEYS
from core.schemas import ClassProbability, ModelInferenceOutput
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
) -> ModelInferenceOutput:
    """
    Execute full inference pipeline (Feature Extraction + SVM Classification)
    for a single CNN-SVM model combination.
    """
    if model_name not in MODEL_KEYS:
        raise ValueError(
            f"Model '{model_name}' tidak valid. Pilihan yang tersedia: {MODEL_KEYS}"
        )

    # 1. Retrieve cached model instances
    extractor = get_feature_extractor(model_name)
    svm_classifier = get_svm_classifier(model_name)

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
    )


def predict_all_models(
    image: Image.Image,
) -> List[ModelInferenceOutput]:
    """
    Execute inference across all three canonical models sequentially
    for side-by-side architectural comparison.
    """
    results: List[ModelInferenceOutput] = []
    for model_name in MODEL_KEYS:
        output = predict_single_model(image, model_name)
        results.append(output)
    return results
