"""K4 (hard negatives on remove strokes, P only) against K1 and v1 flat over the first training steps: error-gate recall,
target recall and wrong edits on preserve voxels, 200-step rolling means (training-log diagnostics, not validation)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
K4 = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "server-diagnostics/z390-queue-k4-1007/train-early/metrics.jsonl"
RUNS = {"v1 flat": ROOT / "data/val-and-train-results/train-sirb-formal-20260930/N1_STATE/metrics.jsonl",
        "K1": ROOT / "data/val-and-train-results/train-sirb-k-20261006/K1_INTENT_FULL/metrics.jsonl",
        "K4": K4}


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


data = {name: {r["step"]: r for r in rows(path)} for name, path in RUNS.items()}
last = max(data["K4"])
print(f"K4 last logged step {last}")
for key in ("diag_error_gate_recall", "diag_target_recall", "diag_preserve_edit_voxels"):
    print(f"\n{key} (mean of the 10 log rows ending at the step; nan = no value)")
    for step in [s for s in (200, 400, 600, 800, 1000, 1400, 2000, 3000, 4000, 6000, 8000, 10000) if s <= last]:
        parts = []
        for name in RUNS:
            vals = [data[name][s][key] for s in range(step - 180, step + 1, 20)
                    if s in data[name] and data[name][s].get(key) is not None]
            parts.append(f"{name} {sum(vals) / len(vals):.3f}" if vals else f"{name} nan")
        print(f"  step {step:5d}: " + " | ".join(parts))
