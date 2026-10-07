"""D3 follow-up (VAL): how many remove and add strokes each system drew in rounds 2-5, the over-segmentation they pointed
at (target volume) and how much of it they cleared; per-stroke cleared share (median)."""
import collections
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b0_paths  # noqa: E402
from b0_load import load  # noqa: E402

DIAG = HERE.parent / "server-diagnostics" / "z390-queue-diag-1007" / "diag-routed-v1add-k2remove-val"
b0_paths.RUNS["routed"] = DIAG
for n in ("v1flat", "K1", "K2", "routed"):
    six, tr, _ = load(n, remote=False)
    c = collections.defaultdict(collections.Counter)
    shares = collections.defaultdict(list)
    for (s, st, k), r in tr.items():
        if k == 0 or r.get("no_stroke") or r.get("status") != "ok":
            continue
        sign = r["sign"]
        c[sign]["n"] += 1
        c[sign]["target"] += r.get("target_volume_ml") or 0.0
        c[sign]["fixed"] += r.get("target_recovery_ml") or 0.0
        c[sign]["fp_added"] += r.get("fp_added_ml") or 0.0
        c[sign]["tp_lost"] += r.get("tp_lost_ml") or 0.0
        if (r.get("target_volume_ml") or 0) > 0:
            shares[sign].append((r.get("target_recovery_ml") or 0.0) / r["target_volume_ml"])
    out = []
    for sign in ("+", "-"):
        x = c[sign]
        out.append(f"{sign} n={x['n']:3d} target {x['target']:7.1f} fixed {x['fixed']:6.1f} "
                   f"(median share {statistics.median(shares[sign]):.3f}) fp+ {x['fp_added']:6.1f} tp- {x['tp_lost']:6.1f}")
    print(f"{n:7s} rounds 2-5 | " + " | ".join(out))
