"""Constants and static mappings for coffee bean quality classification."""

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
    "defect": "#DC2626",     # Red-600
    "longberry": "#D97706",  # Amber-600
    "peaberry": "#2563EB",   # Blue-600
    "premium": "#059669",    # Emerald-600
}

# Canonical Model Keys & Feature Dimensions
MODEL_KEYS: List[str] = [
    "MobileNetV3-Small",
    "ShuffleNetV2",
    "EfficientNet-B0",
]

MODEL_FEATURE_DIMS: Dict[str, int] = {
    "MobileNetV3-Small": 1024,
    "ShuffleNetV2": 1024,
    "EfficientNet-B0": 1280,
}
