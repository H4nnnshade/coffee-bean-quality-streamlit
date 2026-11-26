#!/usr/bin/env python3
"""Generate models/MANIFEST.sha256 containing SHA-256 digests for all 18 model artifacts."""

import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MANIFEST_PATH = MODELS_DIR / "MANIFEST.sha256"


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> None:
    artifact_paths = sorted(
        list((MODELS_DIR / "checkpoint").glob("*.pt"))
        + list((MODELS_DIR / "svm").glob("*.joblib"))
    )

    if len(artifact_paths) != 18:
        raise RuntimeError(
            f"Expected exactly 18 model artifacts, found {len(artifact_paths)}"
        )

    lines = []
    for p in artifact_paths:
        rel_path = p.relative_to(BASE_DIR).as_posix()
        digest = compute_sha256(p)
        lines.append(f"{digest}  {rel_path}\n")

    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Generated {MANIFEST_PATH} with {len(lines)} entries.")


if __name__ == "__main__":
    main()
