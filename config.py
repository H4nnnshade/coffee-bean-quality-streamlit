"""Application configuration module (12-Factor App pattern)."""

import os
from pathlib import Path
from typing import Dict, List

# Base Project Directories
BASE_DIR = Path(__file__).resolve().parent

# Model Checkpoints & Artifacts Directory
DEFAULT_MODEL_DIR = Path("/Users/agusfarhan/Downloads/skenario_60-20-20")
MODEL_BASE_DIR = Path(os.getenv("MODEL_DIR", str(DEFAULT_MODEL_DIR)))

CHECKPOINT_DIR = MODEL_BASE_DIR / "checkpoint"
SVM_DIR = MODEL_BASE_DIR / "svm"

# Scenario & Model Identifiers
SKENARIO_NAME = "60:20:20"
SKENARIO_SLUG = "60-20-20"

MODEL_NAMES: List[str] = [
    "MobileNetV3-Small",
    "ShuffleNetV2",
    "EfficientNet-B0",
]

# File naming mappings
CHECKPOINT_FILES: Dict[str, Path] = {
    name: CHECKPOINT_DIR / f"{name}_{SKENARIO_SLUG}.pt" for name in MODEL_NAMES
}

SVM_FILES: Dict[str, Path] = {
    name: SVM_DIR / f"{name}_{SKENARIO_SLUG}_svm.joblib" for name in MODEL_NAMES
}

# Image Preprocessing & Inference Configuration
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 1
DEVICE = os.getenv("TORCH_DEVICE", "cpu")
NUM_THREADS = int(os.getenv("TORCH_NUM_THREADS", "2"))
