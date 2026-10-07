"""Q4: differences by drawing style (centerline / random / boundary), VAL three-style rollout.

Per style the patient mean uses only that style's trajectory of each positive scan (scan -> patient -> equal patients).
"""
import collections
import json
from pathlib import Path

from A_common import arm_six, patient_mean, STYLES
from A_transitions import build

OUT = Path(__file__).with_suffix(".json")
res = {}
six = {a: arm_six(a) for a in ("flat", "N3", "oracle")}
pat, pos = six["flat"][1], six["flat"][2]
for arm in ("flat", "N3", "oracle"):
    d = six[arm][0]
    for st in STYLES:
        keys = {k for k in d if k[1] == st and pos[k]}
        res.setdefault(arm, {})[st] = {"curve": [patient_mean({k: d[k][r]["dice"] for k in keys}, pat)[0] for r in range(6)]}

# targets identical across styles for the oracle / at t0?
for arm in ("flat", "N3"):
    rows, _, gts = build(arm)
    act = [r for r in rows if r["pos"] and not r["no_stroke"]]
    pk = {(r["scan"], r["style"]): r["patient"] for r in rows}
    for st in STYLES:
        keys = {k for k in gts if k[1] == st}
        rs = [r for r in act if r["style"] == st]

        def pmsum(field, pred=lambda r: True):
            acc = {k: 0.0 for k in keys}
            for r in rs:
                if pred(r):
                    acc[(r["scan"], r["style"])] += r[field]
            return patient_mean(acc, pk)[0]
        V = sum(r["V"] for r in rs)
        o = res[arm][st]
        o.update({
            "n": len(rs),
            "first_order_total": pmsum("shortfall"), "first_order_target": pmsum("S_target"),
            "first_order_damage": pmsum("S_damage"), "first_order_collateral": pmsum("S_collateral"),
            "t0_shortfall": pmsum("shortfall", lambda r: r["t"] == 0),
            "t0_target": pmsum("S_target", lambda r: r["t"] == 0), "t0_damage": pmsum("S_damage", lambda r: r["t"] == 0),
            "vol_weighted_recovery": sum(r["R"] for r in rs) / V,
            "event_mean_recovery": sum(r["R"] / r["V"] for r in rs) / len(rs),
            "t0_event_mean_recovery": sum(r["R"] / r["V"] for r in rs if r["t"] == 0) / sum(1 for r in rs if r["t"] == 0),
            "damage_ml_per_ml_target": sum(r["fp_add"] + r["tp_lost"] for r in rs) / V,
            "patient_mean_new_error_ml": pmsum("fp_add") + pmsum("tp_lost"),
            "dice_worse_rate": sum(1 for r in rs if r["gain_actual"] < -1e-12) / len(rs),
            "by_cat_first_order": {c: pmsum("shortfall", lambda r, c=c: r["cat"] == c) for c in
                                   sorted({r["cat"] for r in rs})},
            "by_cat_event_recovery": {c: sum(r["R"] / r["V"] for r in rs if r["cat"] == c) / max(1, sum(1 for r in rs if r["cat"] == c))
                                      for c in sorted({r["cat"] for r in rs})},
            "by_cat_damage_per_ml": {c: sum(r["fp_add"] + r["tp_lost"] for r in rs if r["cat"] == c) / max(1e-9, sum(r["V"] for r in rs if r["cat"] == c))
                                     for c in sorted({r["cat"] for r in rs})},
        })
# oracle: are the per-style oracle targets the same?
orows, _, _ = build("oracle")
by = collections.defaultdict(dict)
for r in orows:
    by[(r["scan"], r["t"])][r["style"]] = (r["sign"], round(r["V"], 6), r["no_stroke"])
same = sum(1 for v in by.values() if len(set(v.values())) == 1)
res["oracle_targets_same_across_styles"] = {"same": same, "total": len(by)}

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
for arm in ("flat", "N3", "oracle"):
    for st in STYLES:
        o = res[arm][st]
        line = f"{arm:6s} {st:10s} curve " + " ".join(f"{x:.4f}" for x in o["curve"])
        if arm != "oracle":
            line += (f" | FO total {o['first_order_total']:.4f} tgt {o['first_order_target']:.4f} dmg {o['first_order_damage']:.4f}"
                     f" | t0 {o['t0_shortfall']:.4f} (tgt {o['t0_target']:.4f} dmg {o['t0_damage']:.4f}) | rec vol {o['vol_weighted_recovery']:.3f}"
                     f" evt {o['event_mean_recovery']:.3f} t0evt {o['t0_event_mean_recovery']:.3f} | dmg/ml {o['damage_ml_per_ml_target']:.3f}"
                     f" newerr {o['patient_mean_new_error_ml']:.2f} worse {o['dice_worse_rate']:.3f}")
        print(line)
        if arm != "oracle":
            print("        FO by cat:", {c: round(v, 4) for c, v in o["by_cat_first_order"].items()})
            print("        evt rec by cat:", {c: round(v, 3) for c, v in o["by_cat_event_recovery"].items()})
            print("        dmg/ml by cat:", {c: round(v, 3) for c, v in o["by_cat_damage_per_ml"].items()})
print("oracle targets same across styles:", res["oracle_targets_same_across_styles"])
