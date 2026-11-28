#!/usr/bin/env python3
"""S4 fan-out benchmark artifact (PRD.md:184, PRD.md:233).

Reproducible on the target host, no figures quoted from chat threads.

Modes
-----
latency : sequential baseline vs shipped parallel fan-out, workers x torch threads.
rss     : cold-load peak RSS of the whole fan-out path in a fresh process.
rss3    : PRD memory gate -- cold-load ALL three splits in one process and
          report peak RSS during load only (drift would be charged to it).
drift   : PRD drift gate for ONE split -- warm once, then 50 sequential
          requests, report RSS final - after_warm. One split per process.

Usage
-----
    .venv/bin/python scripts/bench_fanout.py --mode latency --iters 20 \
        --out bench/fanout_bench.json
    .venv/bin/python scripts/bench_fanout.py --mode rss --parallel \
        --out bench/rss_parallel_60-20-20.json
    .venv/bin/python scripts/bench_fanout.py --mode rss3 --parallel --drift-iters 50 \
        --out bench/rss3_parallel.json

Every number written to the JSON is measured by this script on the running host.
Host core count, TORCH_NUM_THREADS, and worker count travel with the figures so
a reader can tell whether the measurement applies to their machine.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.constants import (  # noqa: E402
    ALLOWED_SPLITS,
    DEFAULT_SPLIT,
    MAX_PARALLEL_WORKERS,
    MODEL_KEYS,
)
from services import predictor  # noqa: E402
from services.predictor import _predict_one_model, predict_all_models  # noqa: E402

# Sample image path comes from the environment, never from a baked absolute path.
# Unset -> a synthetic image is generated, so the benchmark still runs anywhere.
SAMPLE_ENV = "COFFEE_SAMPLE_IMAGE"
DEFAULT_SAMPLE = Path(os.getenv(SAMPLE_ENV, ""))


def _sample_label(p) -> str:
    """Artifact metadata never embeds a host-specific absolute path."""
    name = Path(p).name if str(p) else ""
    return name or "synthetic"


def _peak_rss_mb() -> float:
    """Peak RSS of this process. ru_maxrss is bytes on Darwin, KiB on Linux."""
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    divisor = 1024.0 * 1024.0 if sys.platform == "darwin" else 1024.0
    return round(raw / divisor, 1)


def _current_rss_mb() -> float:
    """Resident set size right now (not the high-water mark)."""
    try:
        if sys.platform == "darwin":
            out = subprocess.check_output(
                ["ps", "-o", "rss=", "-p", str(os.getpid())], text=True
            )
            return round(int(out.strip()) / 1024.0, 1)  # KiB -> MB
        with open("/proc/self/statm", "r", encoding="utf-8") as fh:
            pages = int(fh.read().split()[1])
        return round(pages * os.sysconf("SC_PAGE_SIZE") / (1024.0 * 1024.0), 1)
    except Exception:
        return _peak_rss_mb()


def _load_image(path: Path) -> Image.Image:
    if str(path) and path.is_file():
        return Image.open(path).convert("RGB")
    arr = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _torch_threads() -> int:
    import torch

    return int(torch.get_num_threads())


def _percentile(values: List[float], q: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    idx = min(len(ordered) - 1, max(0, int(round((q / 100.0) * (len(ordered) - 1)))))
    return ordered[idx]


def _stats(values: List[float]) -> Dict[str, float]:
    return {
        "p50": round(statistics.median(values), 2),
        "p90": round(_percentile(values, 90), 2),
        "p99": round(_percentile(values, 99), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "n": len(values),
    }


def _host_header(split: str) -> Dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "torch_threads_per_worker": _torch_threads(),
        "split": split,
        "models": list(MODEL_KEYS),
        "python": platform.python_version(),
    }


def _run_sequential(image: Image.Image, split: str, iters: int) -> List[float]:
    """Force the sequential branch: the D2 default path."""
    timings: List[float] = []
    for _ in range(iters):
        start = time.perf_counter()
        predict_all_models(image, split=split)  # ENABLE_PARALLEL is False by default
        timings.append((time.perf_counter() - start) * 1000.0)
    return timings


def _run_shipped_parallel(image: Image.Image, split: str, iters: int) -> List[float]:
    timings: List[float] = []
    previous = predictor.ENABLE_PARALLEL
    predictor.ENABLE_PARALLEL = True
    try:
        for _ in range(iters):
            start = time.perf_counter()
            predict_all_models(image, split=split)
            timings.append((time.perf_counter() - start) * 1000.0)
    finally:
        predictor.ENABLE_PARALLEL = previous
    return timings


def _run_worker_sweep(
    image: Image.Image, split: str, iters: int, workers: List[int]
) -> Dict[str, Any]:
    """1 vs 3 vs 8 workers over the same _predict_one_model unit of work.

    Bypasses the shipped cap so the sweep can show the oversubscription cost that
    decision D2 asks to measure; results are collected in submission order.
    """
    from concurrent.futures import ThreadPoolExecutor

    sweep: Dict[str, Any] = {}
    for count in workers:
        # warmup (loader caches warm; excluded from timing)
        with ThreadPoolExecutor(max_workers=count) as pool:
            [f.result() for f in [pool.submit(_predict_one_model, image, k, split) for k in MODEL_KEYS]]
        timings: List[float] = []
        order_ok = True
        for _ in range(iters):
            start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=max(1, min(count, len(MODEL_KEYS)))) as pool:
                futures = [pool.submit(_predict_one_model, image, k, split) for k in MODEL_KEYS]
                results = [f.result() for f in futures]
            timings.append((time.perf_counter() - start) * 1000.0)
            if [r.model_key for r in results] != list(MODEL_KEYS):
                order_ok = False
        sweep[str(count)] = {
            "effective_workers": max(1, min(count, len(MODEL_KEYS))),
            "torch_threads_total": _torch_threads() * max(1, min(count, len(MODEL_KEYS))),
            "order_preserved": order_ok,
            **_stats(timings),
        }
    return sweep


def mode_latency(args: argparse.Namespace) -> Dict[str, Any]:
    image = _load_image(Path(args.sample))
    workers = [int(w) for w in args.workers.split(",") if w.strip()]
    rss_start = _peak_rss_mb()

    # Warm the loader caches once so the comparison is warm-vs-warm, then cold
    # numbers are reported separately by --mode rss.
    predict_all_models(image, split=args.split)
    rss_warm = _peak_rss_mb()

    seq = _run_sequential(image, args.split, args.iters)
    par = _run_shipped_parallel(image, args.split, args.iters)
    sweep = _run_worker_sweep(image, args.split, args.iters, workers)

    seq_p50 = statistics.median(seq)
    par_p50 = statistics.median(par)
    speedup_p50 = round((seq_p50 - par_p50) / seq_p50 * 100.0, 2) if seq_p50 else 0.0

    payload: Dict[str, Any] = {
        "mode": "latency",
        **_host_header(args.split),
        "sample": _sample_label(args.sample),
        "iters": args.iters,
        "shipped_parallel_workers": max(1, min(MAX_PARALLEL_WORKERS, len(MODEL_KEYS))),
        "sequential": _stats(seq),
        "shipped_parallel": _stats(par),
        "speedup_p50_percent": speedup_p50,
        "d2_threshold_percent": 20.0,
        "d2_met_on_this_host": speedup_p50 >= 20.0,
        "worker_sweep": sweep,
        "rss_mb": {"at_start": rss_start, "after_warm": rss_warm, "peak": _peak_rss_mb()},
    }

    # Ordering invariant under both branches, measured not assumed.
    seq_models = predict_all_models(image, split=args.split)
    previous = predictor.ENABLE_PARALLEL
    predictor.ENABLE_PARALLEL = True
    try:
        par_models = predict_all_models(image, split=args.split)
    finally:
        predictor.ENABLE_PARALLEL = previous
    payload["order_preserved"] = {
        "sequential": [m.model_key for m in seq_models.models] == list(MODEL_KEYS),
        "parallel": [m.model_key for m in par_models.models] == list(MODEL_KEYS),
    }
    payload["parity_max_abs_delta"] = _parity_delta(seq_models, par_models)
    return payload


def _parity_delta(a: Any, b: Any) -> float:
    """Max absolute probability delta between the two branches."""
    worst = 0.0
    for left, right in zip(a.models, b.models):
        lp = left.probabilities or {}
        rp = right.probabilities or {}
        for key in set(lp) | set(rp):
            worst = max(worst, abs(float(lp.get(key, 0.0)) - float(rp.get(key, 0.0))))
    return round(worst, 12)


def mode_rss(args: argparse.Namespace) -> Dict[str, Any]:
    """Cold-load peak RSS of a fresh interpreter walking the fan-out path."""
    image = _load_image(Path(args.sample))
    rss_before = _peak_rss_mb()
    start = time.perf_counter()
    previous = predictor.ENABLE_PARALLEL
    predictor.ENABLE_PARALLEL = bool(args.parallel)
    try:
        result = predict_all_models(image, split=args.split)
    finally:
        predictor.ENABLE_PARALLEL = previous
    cold_ms = round((time.perf_counter() - start) * 1000.0, 2)
    peak = _peak_rss_mb()
    return {
        "mode": "rss",
        **_host_header(args.split),
        "parallel": bool(args.parallel),
        "sample": _sample_label(args.sample),
        "cold_load_and_first_inference_ms": cold_ms,
        "rss_mb": {
            "before_import_of_models": rss_before,
            "peak_after_fanout": peak,
            "prd_gate_650": peak <= 650.0,
        },
        "failed_count": result.failed_count,
        "order_preserved": [m.model_key for m in result.models] == list(MODEL_KEYS),
        "note": "ru_maxrss is process peak, not incremental; run in a fresh interpreter per branch",
    }


def mode_rss3(args: argparse.Namespace) -> Dict[str, Any]:
    """PRD memory gate: cold-load ALL three splits in one process, then drift.

    PRD.md:184 -> "RSS pasca-load 3 split <= 650 MB; lalu 50 request/split
    berurutan: RSS akhir - pasca-warm <= 5 MB". Measured in a fresh interpreter
    per branch so ru_maxrss is attributable to this branch only.
    """
    image = _load_image(Path(args.sample))
    rss_before = _current_rss_mb()
    previous = predictor.ENABLE_PARALLEL
    predictor.ENABLE_PARALLEL = bool(args.parallel)
    per_split: Dict[str, Any] = {}
    try:
        load_start = time.perf_counter()
        for split in ALLOWED_SPLITS:
            split_start = time.perf_counter()
            if args.prewarm and args.parallel:
                # Serial pre-warm: fill st.cache_resource from the main thread
                # before fanning out, so three workers never race to build the
                # same loader (which is what inflates peak RSS).
                predictor.ENABLE_PARALLEL = False
                predict_all_models(image, split=split)
                predictor.ENABLE_PARALLEL = bool(args.parallel)
            result = predict_all_models(image, split=split)
            per_split[split] = {
                "cold_load_and_first_inference_ms": round(
                    (time.perf_counter() - split_start) * 1000.0, 2
                ),
                "rss_after_load_mb": _current_rss_mb(),
                "failed_count": result.failed_count,
                "order_preserved": [m.model_key for m in result.models]
                == list(MODEL_KEYS),
            }
        cold_all_splits_ms = round((time.perf_counter() - load_start) * 1000.0, 2)
        rss_after_load = _current_rss_mb()
        peak_load = _peak_rss_mb()
    finally:
        predictor.ENABLE_PARALLEL = previous

    return {
        "mode": "rss3",
        **_host_header(",".join(ALLOWED_SPLITS)),
        "parallel": bool(args.parallel),
        "prewarm_serial": bool(getattr(args, "prewarm", False)),
        "sample": _sample_label(args.sample),
        "rss_mb": {
            "before_load": rss_before,
            "after_load_all_splits": rss_after_load,
            "peak_during_load": peak_load,
            "prd_gate_650_peak_during_load": peak_load <= 650.0,
        },
        "cold_all_splits_ms": cold_all_splits_ms,
        "per_split": per_split,
        "note": (
            "load-only gate: fresh interpreter per branch, no drift loop. "
            "ru_maxrss is a process high-water mark, so anything allocated "
            "afterwards would be charged to the gate. Drift is a separate mode."
        ),
    }


def mode_drift(args: argparse.Namespace) -> Dict[str, Any]:
    """PRD drift gate for ONE split: 50 sequential requests after warm.

    PRD.md:184 -> "lalu 50 request/split berurutan: RSS akhir - pasca-warm <= 5 MB".
    One split per process: measuring three splits in one interpreter makes every
    baseline after the first one contaminated by the previous split's allocations.
    """
    image = _load_image(Path(args.sample))
    previous = predictor.ENABLE_PARALLEL
    predictor.ENABLE_PARALLEL = bool(args.parallel)
    try:
        # exactly one request warms every loader for this split
        predict_all_models(image, split=args.split)
        rss_warm = _current_rss_mb()
        started = time.perf_counter()
        for _ in range(args.drift_iters):
            predict_all_models(image, split=args.split)
        elapsed = round((time.perf_counter() - started) * 1000.0, 1)
        rss_final = _current_rss_mb()
    finally:
        predictor.ENABLE_PARALLEL = previous

    return {
        "mode": "drift",
        **_host_header(args.split),
        "parallel": bool(args.parallel),
        "sample": _sample_label(args.sample),
        "iters": args.drift_iters,
        "rss_mb": {
            "after_warm": rss_warm,
            "final": rss_final,
            "drift": round(rss_final - rss_warm, 1),
            "prd_gate_5_mb": (rss_final - rss_warm) <= 5.0,
        },
        "elapsed_ms": elapsed,
        "note": "one split per process; fresh interpreter per branch",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="S4 fan-out benchmark (reproducible artifact)")
    parser.add_argument(
        "--mode", choices=["latency", "rss", "rss3", "drift"], default="latency"
    )
    parser.add_argument("--split", default=DEFAULT_SPLIT)
    parser.add_argument("--iters", type=int, default=20)
    parser.add_argument("--workers", default="1,3,8")
    parser.add_argument("--sample", default=str(DEFAULT_SAMPLE))
    parser.add_argument("--parallel", action="store_true", help="rss mode: use the fan-out branch")
    parser.add_argument("--drift-iters", type=int, default=50)
    parser.add_argument(
        "--prewarm",
        action="store_true",
        help="rss3: serial pre-warm each split before fan-out (cold-load RSS fix)",
    )
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    payload = {
        "latency": mode_latency,
        "rss": mode_rss,
        "rss3": mode_rss3,
        "drift": mode_drift,
    }[args.mode](args)

    target = Path(args.out) if args.out else REPO_ROOT / "bench" / f"{args.mode}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=False))
    print(f"\nartifact -> {target}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
