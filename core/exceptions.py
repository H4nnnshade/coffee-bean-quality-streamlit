"""Domain exceptions for coffee bean quality classification system."""


class ModelArtifactNotFoundError(FileNotFoundError):
    """Raised when checkpoint weights or SVM pipeline artifacts are missing from disk."""
    pass
