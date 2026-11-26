"""Domain exceptions for coffee bean quality classification system."""


class ModelArtifactNotFoundError(FileNotFoundError):
    """Raised when checkpoint weights or SVM pipeline artifacts are missing from disk."""
    pass


class ChecksumMismatchError(RuntimeError):
    """Raised when artifact SHA-256 hash does not match committed manifest."""
    pass


class ArtifactContainmentError(ValueError):
    """Raised when resolved artifact path escapes MODEL_BASE_DIR (CWE-22 path traversal)."""
    pass


class ImageValidationError(ValueError):
    """Raised when input image violates size, format, dimension, or decompression constraints."""
    pass

