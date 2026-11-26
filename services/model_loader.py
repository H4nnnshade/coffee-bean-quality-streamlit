"""Singleton and lazy caching loader for PyTorch CNN backbones and SVM pipelines."""

import hashlib
import io
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, Tuple
import joblib
import torch
import torch.nn as nn
from torchvision import models

import config
from core.constants import (
    ALLOWED_SPLITS,
    DEFAULT_SPLIT,
    MODEL_KEYS,
    NUM_CLASSES,
)
from core.exceptions import ChecksumMismatchError, ModelArtifactNotFoundError

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


def _get_manifest_path() -> Path:
    """Path to models/MANIFEST.sha256."""
    return config.BASE_DIR / "models" / "MANIFEST.sha256"


@lru_cache(maxsize=1)
def load_manifest() -> Dict[str, str]:
    """
    Load committed models/MANIFEST.sha256 into memory.
    Fail-closed: raises ChecksumMismatchError if manifest is missing or invalid.
    Returns mapping of rel_path -> sha256_hexdigest.
    """
    manifest_path = _get_manifest_path()
    if not manifest_path.is_file():
        logger.critical(
            "Integrity manifest missing on disk: %s. Fail-closed: refusing all loads.",
            str(manifest_path),
        )
        raise ChecksumMismatchError(
            f"Berkas manifest integritas tidak ditemukan di sistem: {manifest_path.name}"
        )

    mapping: Dict[str, str] = {}
    with manifest_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                raise ChecksumMismatchError(
                    f"Format baris manifest tidak valid pada baris {line_num}: {line}"
                )
            digest, rel_path = parts[0].strip().lower(), parts[1].strip()
            if rel_path in mapping:
                raise ChecksumMismatchError(
                    f"Entri duplikat ditemukan dalam manifest: {rel_path}"
                )
            mapping[rel_path] = digest

    if len(mapping) != 18:
        raise ChecksumMismatchError(
            f"Manifest harus memuat tepat 18 entri artefak, ditemukan {len(mapping)} entri."
        )

    return mapping


def verify_and_buffer_artifact(path: Path) -> io.BytesIO:
    """
    Stream-read artifact chunk-by-chunk (1 MB), compute SHA-256 digest,
    assert match against committed manifest BEFORE returning loaded in-memory buffer.
    Fail-closed: raises ChecksumMismatchError on mismatch, unlisted file, or missing manifest.
    """
    if not path.is_file():
        raise ModelArtifactNotFoundError(
            f"Berkas artefak tidak ditemukan di sistem: {path.name}"
        )

    manifest = load_manifest()
    try:
        rel_path = path.resolve().relative_to(config.BASE_DIR.resolve()).as_posix()
    except ValueError:
        # Path outside BASE_DIR
        raise ChecksumMismatchError(
            f"Artefak di luar workspace tidak diizinkan: {path.name}"
        )

    if rel_path not in manifest:
        logger.error("Unlisted artifact rejected by manifest guard: %s", rel_path)
        raise ChecksumMismatchError(
            f"Artefak '{rel_path}' tidak terdaftar dalam manifest integritas."
        )

    expected_digest = manifest[rel_path]
    hasher = hashlib.sha256()
    buf = io.BytesIO()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
            buf.write(chunk)

    computed_digest = hasher.hexdigest().lower()
    if computed_digest != expected_digest:
        logger.critical(
            "Checksum mismatch for artifact %s! Expected: %s, Computed: %s",
            rel_path,
            expected_digest,
            computed_digest,
        )
        raise ChecksumMismatchError(
            f"Integritas artefak '{rel_path}' terkompromi (hash SHA-256 tidak cocok)."
        )

    buf.seek(0)
    return buf


@cache_decorator
def load_feature_extractor(model_name: str, split: str = DEFAULT_SPLIT) -> nn.Module:
    """
    Build CNN backbone, verify checkpoint integrity against manifest,
    load checkpoint weights with explicit weights_only=True,
    and replace classification head with nn.Identity() to obtain penultimate feature representations.
    """
    _validate_model_name(model_name)
    _validate_split(split)

    ckpt_path = config.get_checkpoint_path(model_name, split)
    buf = verify_and_buffer_artifact(ckpt_path)

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

    # Load trained checkpoint weights securely from memory buffer with weights_only=True
    checkpoint = torch.load(buf, map_location=config.DEVICE, weights_only=True)
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
    """
    Verify Scikit-learn SVM pipeline artifact integrity against manifest,
    then deserialize from memory buffer via joblib.load().
    """
    _validate_model_name(model_name)
    _validate_split(split)

    svm_path = config.get_svm_path(model_name, split)
    buf = verify_and_buffer_artifact(svm_path)

    svm_artifact = joblib.load(buf)
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
