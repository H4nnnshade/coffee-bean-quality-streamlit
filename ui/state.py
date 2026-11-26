"""State resolution logic for multi-model inference results (S5 / PRD D11).

Pure state mapping function: no streamlit import, no ui.components import.
"""

from typing import List, Literal
from core.schemas import PerModelResult


def resolve_result_state(models: List[PerModelResult]) -> Literal["ok", "partial", "empty", "error"]:
    """
    Resolve the high-level UI result state from a list of PerModelResult.

    Returns:
    - "ok": All models succeeded (status == 'ok').
    - "partial": Degraded success: at least one model succeeded and at least one failed.
    - "empty": All models failed specifically with ARTIFACT_MISSING.
    - "error": All models failed and at least one is ARTIFACT_INTEGRITY, INVALID_REQUEST,
               INFERENCE_ERROR, or unknown. Also returns "error" if models list is empty.
    """
    if not models:
        return "error"

    ok_count = sum(1 for m in models if m.status == "ok")
    if ok_count == len(models):
        return "ok"
    if ok_count > 0:
        return "partial"

    # All models failed:
    if all(m.error_code == "ARTIFACT_MISSING" for m in models):
        return "empty"

    return "error"
