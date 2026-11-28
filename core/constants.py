"""Constants and static mappings for coffee bean quality classification."""

import os
from typing import Dict, List, Tuple

# Allowed file formats & size constraints
ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]
MAX_FILE_SIZE_MB: int = 10
MAX_IMAGE_PIXELS: int = 4096 * 4096  # Security: Decompression bomb guard (16 MP)

# Image dimensions & normalizations
IMAGE_SIZE: Tuple[int, int] = (224, 224)
IMAGENET_MEAN: List[float] = [0.485, 0.456, 0.406]
IMAGENET_STD: List[float] = [0.229, 0.224, 0.225]

# Quality classes (matching notebook order)
# defect (0), longberry (1), peaberry (2), premium (3)
CLASS_NAMES: List[str] = ["defect", "longberry", "peaberry", "premium"]
CLASS_DISPLAY: List[str] = ["Defect", "Longberry", "Peaberry", "Premium"]
NUM_CLASSES: int = len(CLASS_NAMES)

CLASS_MAP: Dict[str, str] = {
    name: display for name, display in zip(CLASS_NAMES, CLASS_DISPLAY)
}

# Brand and UI Palette (High contrast & semantic)
CLASS_COLORS: Dict[str, str] = {
    "defect": "#BE123C",     # Rose-700 (§19.4 WCAG AA)
    "longberry": "#B45309",  # Amber-700 (§19.4 WCAG AA)
    "peaberry": "#2563EB",   # Blue-600
    "premium": "#047857",    # Emerald-700 (§19.4 WCAG AA)
}

# Canonical Model Keys & Feature Dimensions
MODEL_KEYS: List[str] = [
    "MobileNetV3-Small",
    "ShuffleNetV2",
    "EfficientNet-B0",
]

MODEL_DISPLAY_NAMES: Dict[str, str] = {
    "MobileNetV3-Small": "MobileNetV3-Small + SVM",
    "ShuffleNetV2": "ShuffleNetV2 + SVM",
    "EfficientNet-B0": "EfficientNet-B0 + SVM",
}

MODEL_FEATURE_DIMS: Dict[str, int] = {
    "MobileNetV3-Small": 1024,
    "ShuffleNetV2": 1024,
    "EfficientNet-B0": 1280,
}

REVIEW_THRESHOLD: float = 0.55

# Parallel fan-out budget (decision D2: conditional, default OFF).
# 3 workers x TORCH_NUM_THREADS=2 = 6 torch threads; on hosts with fewer cores
# this oversubscribes and loses to the sequential path, so the win must be
# measured per target machine before the flag is flipped. Benchmark artifact
# lives in scripts/bench_fanout.py (S4, @dorowani); no figure is claimed here.
MAX_PARALLEL_WORKERS: int = 3

# Kill switch for D2. Default OFF: sequential fan-out unless explicitly opted in
# via ENABLE_PARALLEL=1. Amend to ON only after the bench artifact shows >=20%
# speedup on the target host.
ENABLE_PARALLEL: bool = os.getenv("ENABLE_PARALLEL", "0").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)

# Dataset Split Scenarios (Section 12 Architecture Spec)
ALLOWED_SPLITS: Tuple[str, ...] = ("60-20-20", "70-15-15", "80-10-10")
DEFAULT_SPLIT: str = "60-20-20"
SPLIT_DISPLAY_NAMES: Dict[str, str] = {
    "60-20-20": "60:20:20 (Standar Skripsi)",
    "70-15-15": "70:15:15 (Eksperimen 2)",
    "80-10-10": "80:10:10 (Eksperimen 3)",
}
