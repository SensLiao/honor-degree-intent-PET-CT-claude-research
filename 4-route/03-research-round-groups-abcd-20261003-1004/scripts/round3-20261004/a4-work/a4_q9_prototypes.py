"""E16 nine 12k prototypes (seed 3407): TRAIN monitoring only (tile-level diagnostics logged every 20 steps).
Mean over the last 2k steps (10k-12k] and the last logged row.  Not a VAL or TEST score."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import mean, dump

ROOT = Path("D:/honor-petct-data-hub/z390/prototypes/editor-sirb-mainline-20260920-R1/runs-pilot")
out = {}
for run in sorted(ROOT.iterdir()):
    mf = run / "metrics.jsonl"
    if not mf.exists():
        continue
    rows = [json.loads(l) for l in open(mf, encoding="utf-8") if l.strip()]
    steps = [r["exposure"]["optimizer_steps"] for r in rows]
    arm = run.name.split("-SIRB-")[1].split("-S3407")[0]
    win = [r for r, s in zip(rows, steps) if 10000 < s <= 12000]
    out[arm] = {"rows": len(rows), "last_step": steps[-1],
                "diag_hard_dice_target_10k_12k": mean(r["diag_hard_dice_target"] for r in win if r.get("diag_hard_dice_target") is not None),
                "diag_target_recall_10k_12k": mean(r["diag_target_recall"] for r in win if r.get("diag_target_recall") is not None),
                "diag_error_gate_recall_10k_12k": mean(r["diag_error_gate_recall"] for r in win if r.get("diag_error_gate_recall") is not None),
                "base_total_10k_12k": mean(r["base_total"] for r in win)}
dump(out, Path(__file__).with_suffix(".json"))
ref = out.get("N2", {}).get("diag_hard_dice_target_10k_12k")


def fmt(x, signed=False):
    return "NA" if x is None else (f"{x:+.4f}" if signed else f"{x:.4f}")


for arm, r in out.items():
    t = r["diag_hard_dice_target_10k_12k"]
    print(f"{arm:22s} last {r['last_step']:6d} targetDice {fmt(t)} (vs N2 {fmt(None if t is None else t - ref, True)})"
          f" recall {fmt(r['diag_target_recall_10k_12k'])} gate {fmt(r['diag_error_gate_recall_10k_12k'])}"
          f" loss {fmt(r['base_total_10k_12k'])}")
