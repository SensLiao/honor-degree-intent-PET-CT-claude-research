"""E_ one-off (read-only): TRAIN-side monitoring of the 12k prototypes, N2 against E16_N2_P0 (N2 plus the p0 channel)
and E16_N2_ES (error branch reads the stroke).  TRAIN sampled tiles only, never VAL; the last 2,000 steps are averaged.
Also prints the speed / data-wait medians of every prototype for the loader section."""
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(r"C:/Users/廖神/Desktop/Honor degree/.tmp/z390-pull/protos")
KEYS = ("base_total", "diag_hard_dice_target", "diag_error_gate_recall", "diag_target_recall", "base_target_dice")


def main() -> None:
    for run in sorted(ROOT.iterdir()):
        path = run / "metrics.jsonl"
        if not path.is_file():
            continue
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        last = max(r["step"] for r in rows)
        tail = [r for r in rows if r["step"] > last - 2000]
        values = {k: statistics.mean([r[k] for r in tail if r.get(k) is not None]) for k in KEYS
                  if any(r.get(k) is not None for r in tail)}
        speed = statistics.median(r["seconds_per_step"] for r in rows if r.get("seconds_per_step"))
        wait = statistics.median(r["data_wait_fraction"] for r in rows if r.get("data_wait_fraction") is not None)
        peak = max((r.get("peak_allocated_gb") or 0) for r in rows)
        print(f"{run.name[:40]:40s} last={last} " + " ".join(f"{k.replace('diag_', '')}={v:.4f}" for k, v in values.items())
              + f" | s/step med={speed:.2f} wait med={wait:.2f} peak={peak:.2f}GB")


if __name__ == "__main__":
    sys.exit(main())
