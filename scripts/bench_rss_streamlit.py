"""Run the Streamlit-runtime RSS probe once, in this process (S4 / PRD.md:184).

One invocation = one fresh interpreter = one attributable ru_maxrss. Loop in the
shell for repeats; do not call twice in the same process.

    python scripts/bench_rss_streamlit.py --parallel --out bench/rss_streamlit_par_run1.json
"""
import argparse
import os
import sys
from pathlib import Path

REPO = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, REPO)
os.chdir(REPO)

# Sample image path comes from the environment, never from a baked absolute path.
SAMPLE_ENV = "COFFEE_SAMPLE_IMAGE"
DEFAULT_SAMPLE = os.getenv(SAMPLE_ENV, "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--sample", default=DEFAULT_SAMPLE)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    os.environ["PROBE_OUT"] = str(Path(args.out).resolve())
    os.environ["PROBE_PARALLEL"] = "1" if args.parallel else "0"
    os.environ["PROBE_SAMPLE"] = args.sample
    os.environ["PROBE_SAMPLE_LABEL"] = Path(args.sample).name or "synthetic"

    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(os.path.join(REPO, "scripts", "rss_probe_app.py"), default_timeout=300)
    at.run()
    excs = [str(e.value)[:200] for e in at.exception]
    if excs:
        print("EXCEPTIONS:", excs)
        return 1
    if not Path(args.out).exists():
        print("probe produced no output")
        return 1
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
