"""Where the remaining Dice is lost at D5 (VAL): missed lesion (FN) or over-segmentation (FP), per system.

A TIDE-style independent fix of one error type on the final state, from the six-state volumes (fp_ml, fn_ml, Dice):
with TP volume I, FP and FN, the reference G = I + FN and the mask M = I + FP.
  fix every FN (keep FP):  Dice = 2 G / (2 G + FP)
  fix every FP (keep FN):  Dice = 2 I / (2 I + FN)
Patient mean over the 85 positive scans / 54 patients.  The two fixes are counterfactual upper references computed with
the ground truth; they are not additive and not reachable results.  Also the same split at D0 and D1.
"""
from b0_load import POS, load, patient_mean

SYSTEMS = ["v1flat", "v1N3", "K1", "K1flip", "K2", "K2flip", "oracle", "noop"]
data = {n: load(n, transitions=False, remote=False)[0] for n in SYSTEMS}


def split(v, k):
    d, fp, fn = v["dice"][k], v["fp_ml"][k], v["fn_ml"][k]
    if d is None or fp is None or fn is None:
        return None
    tp = d * (fp + fn) / (2 * (1 - d)) if d < 1 else 0.0
    g = tp + fn
    fix_fn = 2 * g / (2 * g + fp) if (2 * g + fp) > 0 else 1.0
    fix_fp = 2 * tp / (2 * tp + fn) if (2 * tp + fn) > 0 else 1.0
    return d, fix_fn, fix_fp, fp, fn


print("system   round | Dice   | +all FN fixed | +all FP fixed | sum FP ml | sum FN ml   (VAL, patient means)")
for n in SYSTEMS:
    for k in (0, 1, 5):
        rows = {s: split(v, k) for (s, st), v in data[n].items() if s in POS}
        rows = {s: r for s, r in rows.items() if r is not None}
        d = patient_mean({s: r[0] for s, r in rows.items()})[0]
        ffn = patient_mean({s: r[1] for s, r in rows.items()})[0]
        ffp = patient_mean({s: r[2] for s, r in rows.items()})[0]
        print(f"{n:8s} D{k}    | {d:.4f} | {ffn:.4f} ({ffn - d:+.4f}) | {ffp:.4f} ({ffp - d:+.4f}) | "
              f"{sum(r[3] for r in rows.values()):8.1f} | {sum(r[4] for r in rows.values()):8.1f}")
