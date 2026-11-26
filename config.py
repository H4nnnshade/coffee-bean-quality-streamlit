"""Application configuration module (12-Factor App pattern)."""

import os
from pathlib import Path
from typing import Dict, List

from core.exceptions import ArtifactContainmentError

# Base Project Directories
BASE_DIR = Path(__file__).resolve().parent

# Model Checkpoints & Artifacts Directory (12-Factor config with containment guard)
# Defaults to repository models/ directory, configurable via MODEL_DIR env
DEFAULT_MODEL_DIR = (BASE_DIR / "models").resolve()
MODEL_BASE_DIR = Path(os.getenv("MODEL_DIR", str(DEFAULT_MODEL_DIR))).resolve()

CHECKPOINT_DIR = (MODEL_BASE_DIR / "checkpoint").resolve()
SVM_DIR = (MODEL_BASE_DIR / "svm").resolve()

# Scenario & Model Identifiers
SKENARIO_NAME = "60:20:20"
SKENARIO_SLUG = "60-20-20"

MODEL_NAMES: List[str] = [
    "MobileNetV3-Small",
    "ShuffleNetV2",
    "EfficientNet-B0",
]


def _assert_path_containment(resolved_path: Path, expected_parent: Path) -> Path:
    """
    Ensure resolved artifact path is strictly strictly within the designated parent folder.
    Guards against path traversal / directory climb attacks (CWE-22).
    """
    try:
        if not resolved_path.is_relative_to(expected_parent):
            raise ArtifactContainmentError(
                f"Path traversal terdeteksi: '{resolved_path}' berada di luar batas '{expected_parent}'."
            )
    except AttributeError:
        # Python <3.9 fallback if is_relative_to is unavailable
        try:
            resolved_path.relative_to(expected_parent)
        except ValueError:
            raise ArtifactContainmentError(
                f"Path traversal terdeteksi: '{resolved_path}' berada di luar batas '{expected_parent}'."
            )
    return resolved_path


def get_checkpoint_path(model_name: str, split_slug: str = SKENARIO_SLUG) -> Path:
    """Resolve and enforce containment check on checkpoint file path."""
    target_path = (CHECKPOINT_DIR / f"{model_name}_{split_slug}.pt").resolve()
    return _assert_path_containment(target_path, CHECKPOINT_DIR)


def get_svm_path(model_name: str, split_slug: str = SKENARIO_SLUG) -> Path:
    """Resolve and enforce containment check on SVM artifact file path."""
    target_path = (SVM_DIR / f"{model_name}_{split_slug}_svm.joblib").resolve()
    return _assert_path_containment(target_path, SVM_DIR)


# File naming mappings (backward compatibility for default scenario)
CHECKPOINT_FILES: Dict[str, Path] = {
    name: get_checkpoint_path(name, SKENARIO_SLUG) for name in MODEL_NAMES
}

SVM_FILES: Dict[str, Path] = {
    name: get_svm_path(name, SKENARIO_SLUG) for name in MODEL_NAMES
}

# Image Preprocessing & Inference Configuration
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 1
DEVICE = os.getenv("TORCH_DEVICE", "cpu")
NUM_THREADS = int(os.getenv("TORCH_NUM_THREADS", "2"))
