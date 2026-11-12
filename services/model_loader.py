"""Singleton and lazy caching loader for PyTorch CNN backbones and SVM pipelines."""

import os
from functools import lru_cache
from typing import Any, Callable, Dict, Tuple
import warnings
import joblib
import torch
import torch.nn as nn
from torchvision import models

warnings.filterwarnings("ignore", message=".*Trying to unpickle estimator.*")

import config
from core.constants import MODEL_FEATURE_DIMS, MODEL_KEYS, NUM_CLASSES

# Streamlit cache wrapper with fallback
try:
    import streamlit as st
    cache_decorator: Callable = st.cache_resource
except Exception:
    def cache_decorator(func: Callable) -> Callable:
        return lru_cache(maxsize=16)(func)


def _init_torch_runtime() -> None:
    """Configure CPU optimization and thread allocation."""
    if hasattr(torch, "set_num_threads"):
        try:
            torch.set_num_threads(config.NUM_THREADS)
        except RuntimeError:
            pass


@cache_decorator
def load_feature_extractor(model_name: str) -> nn.Module:
    """
    Build CNN backbone, load checkpoint weights, and replace classification head
    with nn.Identity() to obtain penultimate feature representations.
    """
    if model_name not in MODEL_KEYS:
        raise ValueError(
            f"Model '{model_name}' tidak didukung. Pilihan: {MODEL_KEYS}"
        )

    ckpt_path = config.CHECKPOINT_FILES.get(model_name)
    if not ckpt_path or not ckpt_path.exists():
        raise FileNotFoundError(
            f"Checkpoint file tidak ditemukan: {ckpt_path}. "
            f"Pastikan folder '{config.CHECKPOINT_DIR}' tersedia."
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
def load_svm_classifier(model_name: str) -> Any:
    """Load Scikit-learn SVM pipeline (StandardScaler + OneVsRest(SVC))."""
    if model_name not in MODEL_KEYS:
        raise ValueError(
            f"Model '{model_name}' tidak didukung. Pilihan: {MODEL_KEYS}"
        )

    svm_path = config.SVM_FILES.get(model_name)
    if not svm_path or not svm_path.exists():
        raise FileNotFoundError(
            f"Berkas SVM pipeline tidak ditemukan: {svm_path}. "
            f"Pastikan folder '{config.SVM_DIR}' tersedia."
        )

    svm_artifact = joblib.load(svm_path)
    if isinstance(svm_artifact, dict) and "model" in svm_artifact:
        svm_pipeline = svm_artifact["model"]
    else:
        svm_pipeline = svm_artifact
    return svm_pipeline


def get_feature_extractor(model_name: str) -> nn.Module:
    """Public accessor for cached feature extractor."""
    return load_feature_extractor(model_name)


def get_svm_classifier(model_name: str) -> Any:
    """Public accessor for cached SVM classifier."""
    return load_svm_classifier(model_name)


def get_all_models() -> Dict[str, Tuple[nn.Module, Any]]:
    """Retrieve all (backbone, svm) pairs eagerly."""
    return {
        name: (get_feature_extractor(name), get_svm_classifier(name))
        for name in MODEL_KEYS
    }
