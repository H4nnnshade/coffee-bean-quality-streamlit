"""Singleton and lazy caching loader for PyTorch CNN backbones and SVM pipelines."""

import logging
from functools import lru_cache
from typing import Any, Callable, Dict, Tuple
import warnings
import joblib
import torch
import torch.nn as nn
from torchvision import models

warnings.filterwarnings("ignore", message=".*Trying to unpickle estimator.*")

import config
from core.constants import (
    ALLOWED_SPLITS,
    DEFAULT_SPLIT,
    MODEL_FEATURE_DIMS,
    MODEL_KEYS,
    NUM_CLASSES,
)
from core.exceptions import ModelArtifactNotFoundError

logger = logging.getLogger(__name__)

# Streamlit cache wrapper with fallback
try:
    import streamlit as st
    cache_decorator: Callable = st.cache_resource
except Exception:
    def cache_decorator(func: Callable) -> Callable:
        return lru_cache(maxsize=32)(func)


def _init_torch_runtime() -> None:
    """Configure CPU optimization and thread allocation."""
    if hasattr(torch, "set_num_threads"):
        try:
            torch.set_num_threads(config.NUM_THREADS)
        except RuntimeError:
            pass


def _validate_split(split: str) -> str:
    """Enforce strict whitelist check for split scenario (CWE-22 Path Traversal Guard)."""
    if split not in ALLOWED_SPLITS:
        raise ValueError(
            f"Skenario split '{split}' tidak didukung. Pilihan yang valid: {ALLOWED_SPLITS}"
        )
    return split


def _validate_model_name(model_name: str) -> str:
    """Enforce strict whitelist check for model name."""
    if model_name not in MODEL_KEYS:
        raise ValueError(
            f"Model '{model_name}' tidak didukung. Pilihan yang valid: {MODEL_KEYS}"
        )
    return model_name


@cache_decorator
def load_feature_extractor(model_name: str, split: str = DEFAULT_SPLIT) -> nn.Module:
    """
    Build CNN backbone, load checkpoint weights for a specific split scenario,
    and replace classification head with nn.Identity() to obtain penultimate feature representations.
    """
    _validate_model_name(model_name)
    _validate_split(split)

    ckpt_path = config.get_checkpoint_path(model_name, split)
    if not ckpt_path.is_file():
        logger.error(
            "Checkpoint file not found on disk: %s (model: %s, split: %s)",
            str(ckpt_path),
            model_name,
            split,
        )
        raise ModelArtifactNotFoundError(
            f"Checkpoint model '{model_name}' untuk skenario split '{split}' tidak ditemukan."
        )

    _init_torch_runtime()

    if model_name == "MobileNetV3-Small":
        model = models.mobilenet_v3_small(weights=None)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(in_features, NUM_CLASSES)
        head_attr = ("classifier", 3)
    elif model_name == "ShuffleNetV2":
        model = models.shufflenet_v2_x1_0(weights=None)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, NUM_CLASSES)
        head_attr = ("fc", None)
    elif model_name == "EfficientNet-B0":
        model = models.efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, NUM_CLASSES)
        head_attr = ("classifier", 1)
    else:
        raise ValueError(f"Arsitektur tidak dikenali: {model_name}")

    # Load trained checkpoint weights
    checkpoint = torch.load(ckpt_path, map_location=config.DEVICE)
    if isinstance(checkpoint, dict):
        if "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
        elif "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint
    else:
        state_dict = checkpoint

    model.load_state_dict(state_dict)

    # Convert head to Identity for penultimate feature extraction
    if head_attr[1] is None:
        setattr(model, head_attr[0], nn.Identity())
    else:
        container = getattr(model, head_attr[0])
        container[head_attr[1]] = nn.Identity()

    # Freeze all parameters and set eval mode
    for param in model.parameters():
        param.requires_grad = False
    model.eval()
    model.to(config.DEVICE)

    return model


@cache_decorator
def load_svm_classifier(model_name: str, split: str = DEFAULT_SPLIT) -> Any:
    """Load Scikit-learn SVM pipeline (StandardScaler + OneVsRest(SVC)) for a specific split scenario."""
    _validate_model_name(model_name)
    _validate_split(split)

    svm_path = config.get_svm_path(model_name, split)
    if not svm_path.is_file():
        logger.error(
            "SVM artifact not found on disk: %s (model: %s, split: %s)",
            str(svm_path),
            model_name,
            split,
        )
        raise ModelArtifactNotFoundError(
            f"Berkas SVM pipeline untuk model '{model_name}' skenario split '{split}' tidak ditemukan."
        )

    svm_artifact = joblib.load(svm_path)
    if isinstance(svm_artifact, dict) and "model" in svm_artifact:
        svm_pipeline = svm_artifact["model"]
    else:
        svm_pipeline = svm_artifact
    return svm_pipeline


# Architecture Spec Section 12 Aliases
load_cnn_backbone = load_feature_extractor
load_svm_pipeline = load_svm_classifier


def get_feature_extractor(model_name: str, split: str = DEFAULT_SPLIT) -> nn.Module:
    """Public accessor for cached feature extractor."""
    return load_feature_extractor(model_name, split=split)


def get_svm_classifier(model_name: str, split: str = DEFAULT_SPLIT) -> Any:
    """Public accessor for cached SVM classifier."""
    return load_svm_classifier(model_name, split=split)


def get_all_models(split: str = DEFAULT_SPLIT) -> Dict[str, Tuple[nn.Module, Any]]:
    """Retrieve all (backbone, svm) pairs eagerly for a specific split."""
    return {
        name: (get_feature_extractor(name, split=split), get_svm_classifier(name, split=split))
        for name in MODEL_KEYS
    }
