"""How much of each system's Dice gain comes from fixing the stroke's own error (T) versus other same-sign errors (O),
and how much true lesion / background it damages, by round and stroke sign.  VAL, quick-VAL protocol.

transitions.jsonl fields per step: target_volume_ml (|T|), target_recovery_ml (T fixed), same_sign_other_repair_ml
(O fixed), fp_added_ml (background wrongly added), tp_lost_ml (true lesion wrongly removed), opposite_sign_repair_ml.
"""
import collections
import statistics

from b0_load import POS, load, patient_mean

SYSTEMS = ["v1flat", "K1", "K2", "K2flip", "oracle"]
FIELDS = ["target_volume_ml", "target_recovery_ml", "same_sign_other_repair_ml", "fp_added_ml", "tp_lost_ml",
          "opposite_sign_repair_ml", "new_error_ml"]

data = {name: load(name) for name in SYSTEMS}
print("Sums over the 99 VAL scans (ml).  r1 = round 1 (identical start and stroke for every system), r2-5 = later rounds")
for sign in ("+", "-"):
    print(f"\n=== stroke sign {sign}")
    print(f"{'system':8s} {'rounds':6s} {'n':>4s} " + " ".join(f"{f[:18]:>18s}" for f in FIELDS))
    for name in SYSTEMS:
        six, tr, rem = data[name]
        for label, rounds in (("r1", {0}), ("r2-5", {1, 2, 3, 4})):
            rows = [r for (s, st, t), r in tr.items() if t in rounds and r.get("sign") == sign and not r.get("no_stroke")]
            sums = [sum(float(r.get(f) or 0.0) for r in rows) for f in FIELDS]
            print(f"{name:8s} {label:6s} {len(rows):4d} " + " ".join(f"{x:18.1f}" for x in sums))

print("\n=== round-1 ADD strokes: per-stroke medians (ml) and share of T recovered / O recovered")
for name in SYSTEMS:
    six, tr, rem = data[name]
    rows = [r for (s, st, t), r in tr.items() if t == 0 and r.get("sign") == "+" and not r.get("no_stroke")]
    t_share = [float(r["target_recovery_ml"]) / float(r["target_volume_ml"]) for r in rows if float(r["target_volume_ml"]) > 0]
    o_fix = [float(r.get("same_sign_other_repair_ml") or 0) for r in rows]
    fp = [float(r.get("fp_added_ml") or 0) for r in rows]
    print(f"{name:8s} n={len(rows)} T-share median={statistics.median(t_share):.3f} mean={statistics.mean(t_share):.3f}  "
          f"O fixed median={statistics.median(o_fix):.2f} sum={sum(o_fix):.1f}  FP added median={statistics.median(fp):.2f} sum={sum(fp):.1f}")
