"""Streamlit probe app: cold-load 3 split RSS, run under AppTest (S4, 20 / PRD.md:184).

Not an application module. Invoked only by scripts/bench_rss_streamlit.py, which
measures the process that hosts the Streamlit runtime -- the fan-out path in a
bare interpreter (scripts/bench_fanout.py) is a different measurement and is kept
separate on purpose.
"""
import json, os, platform, subprocess, sys, threading, time
from datetime import datetime, timezone
from pathlib import Path

REPO = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, REPO)
os.chdir(REPO)

import streamlit as st  # noqa: E402


def rss_mb() -> float:
    """Resident set of THIS process. `ps -o rss=` on macOS reports KiB, so MB is one division."""
    try:
        out = subprocess.check_output(
            ["ps", "-o", "rss=", "-p", str(os.getpid())]
        ).decode().strip()
        return round(int(out) / 1024.0, 1) if out else 0.0
    except Exception:
        return 0.0


def peak_ru_mb() -> float:
    """Process high-water mark. Darwin: ru_maxrss is bytes, so MB is /1024/1024."""
    import resource
    v = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(v / 1024.0 / 1024.0, 1)


st.set_page_config(page_title="rss-probe", layout="wide")

out_path = os.environ["PROBE_OUT"]
parallel = os.environ.get("PROBE_PARALLEL", "0") == "1"
sample = os.environ["PROBE_SAMPLE"]

if st.session_state.get("done"):
    st.write("done " + out_path)
else:
    peak = {"v": 0.0}
    stop = threading.Event()

    def poll():
        while not stop.is_set():
            v = rss_mb()
            if v > peak["v"]:
                peak["v"] = v
            time.sleep(0.02)

    poller = threading.Thread(target=poll, daemon=True)
    poller.start()

    from PIL import Image
    import services.predictor as predictor
    from core.constants import ALLOWED_SPLITS

    predictor.ENABLE_PARALLEL = parallel
    before = rss_mb()
    image = Image.open(sample)
    if image.mode != "RGB":
        image = image.convert("RGB")

    per = {}
    t0 = time.perf_counter()
    for split in ALLOWED_SPLITS:
        s = time.perf_counter()
        res = predictor.predict_all_models(image, split=split)
        per[split] = {
            "ms": round((time.perf_counter() - s) * 1000.0, 2),
            "failed_count": res.failed_count,
            "order_ok": [m.model_key for m in res.models] == list(predictor.MODEL_KEYS),
        }
    total_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    after = rss_mb()

    stop.set()
    poller.join(timeout=2)

    payload = {
        "mode": "rss_streamlit",
        "runtime": "streamlit",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "torch_threads_per_worker": int(os.getenv("TORCH_NUM_THREADS", "2")),
        "parallel": parallel,
        "python": sys.version.split()[0],
        "sample": os.getenv("PROBE_SAMPLE_LABEL", "synthetic"),
        "rss_before_load_mb": before,
        "rss_after_load_all_splits_mb": after,
        "rss_peak_sampled_mb": peak["v"],
        "rss_peak_ru_maxrss_mb": peak_ru_mb(),
        "cold_all_splits_ms": total_ms,
        "per_split": per,
        "prd_gate_650_peak_sampled": peak["v"] <= 650.0,
        "prd_gate_650_ru_maxrss": peak_ru_mb() <= 650.0,
    }
    Path(out_path).write_text(json.dumps(payload, indent=1))
    st.session_state["done"] = True
    st.json(payload)
