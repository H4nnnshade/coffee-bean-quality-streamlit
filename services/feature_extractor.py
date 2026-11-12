"""Image transformation and penultimate layer feature extraction service."""

from typing import Union
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms

import config
from core.constants import IMAGE_SIZE, IMAGENET_MEAN, IMAGENET_STD

# Standard transformation matching experiment notebook
_PREPROCESS_PIPELINE = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


def preprocess_image(image: Image.Image) -> torch.Tensor:
    """
    Sanitize and transform a PIL image into standard 4D tensor (1, C, H, W).
    """
    if not isinstance(image, Image.Image):
        raise TypeError(
            f"Expected PIL.Image.Image, got {type(image).__name__} instead."
        )

    # Guarantee 3-channel RGB representation
    if image.mode != "RGB":
        image = image.convert("RGB")

    tensor = _PREPROCESS_PIPELINE(image)
    tensor = tensor.unsqueeze(0)  # Add batch dimension -> (1, 3, 224, 224)
    return tensor.to(config.DEVICE)


@torch.no_grad()
def extract_features(
    image: Union[Image.Image, torch.Tensor],
    model: nn.Module,
) -> np.ndarray:
    """
    Extract penultimate representation from CNN backbone.
    Returns 2D NumPy array of shape (1, feature_dim).
    """
    if isinstance(image, Image.Image):
        tensor = preprocess_image(image)
    elif isinstance(image, torch.Tensor):
        tensor = image.to(config.DEVICE)
        if tensor.ndim == 3:
            tensor = tensor.unsqueeze(0)
    else:
        raise TypeError("Input image must be PIL.Image.Image or torch.Tensor")

    features = model(tensor)
    if isinstance(features, torch.Tensor):
        features = features.detach().cpu().numpy()

    # Flatten extra dimensions if present (e.g. 1x1 conv or spatial pool output)
    if features.ndim > 2:
        features = features.reshape(features.shape[0], -1)

    return features
