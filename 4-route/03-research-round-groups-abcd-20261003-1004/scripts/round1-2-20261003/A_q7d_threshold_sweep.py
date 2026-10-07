"""Q7 add-on: would a different executor threshold trade damage for recovery well?  Single step only (VAL).

States: the 200 flat-sourced trajectory-bank states (= flat's own rollout states at rounds 2-5, verified to reproduce
the rollout in A_q2).  For each state the rollout gives TP/FP/FN before the step; the same-state sweep gives target
repair, same-sign other repair and new error at thresholds 0.05..0.95.  The executor is monotone per stroke, so the new
error is FP for ADD and lost TP for REMOVE.  Next-state Dice is recomputed per threshold (checked against the rollout
at 0.5).  Patient-weighted: mean within patient, then patients equal.  One step only: later rounds are not simulated.
"""
import collections
import json
from pathlib import Path

from A_common import VAL1, read_jsonl, dice
from A_transitions import build

OUT = Path(__file__).with_suffix(".json")
rows, _, gts = build("flat")
by_key = {(r["scan"], r["style"], r["t"]): r for r in rows}
sweep = [r for r in read_jsonl(VAL1 / "samestate-trajectory" / "N1_STATE-s3407" / "sweep.jsonl")
         if ".trajbank-N1_STATE-" in r["episode_id"]]
res = {"check_max_abs_vs_rollout_at_0.5": 0.0}
acc = collections.defaultdict(lambda: collections.defaultdict(list))  # (sign, thr) -> patient -> gains
dmg = collections.defaultdict(float)
rec = collections.defaultdict(float)
tot = collections.defaultdict(float)
for s in sweep:
    r = by_key.get((s["scan_id"], s["style"], int(s["round"])))
    if r is None or r["no_stroke"] or not r["pos"]:
        continue
    g = gts[(r["scan"], r["style"])]
    tp, fp, fn = g - r["fn0"], r["fp0"], r["fn0"]
    R, C, H = float(s["target_recovery_ml"]), float(s["other_repaired_ml"]), float(s["new_error_ml"])
    if r["sign"] == "+":
        d1 = dice(tp + R + C, fp + H, fn - R - C)
    else:
        d1 = dice(tp - H, fp - R - C, fn + H)
    thr = round(float(s["threshold"]), 2)
    if abs(thr - 0.5) < 1e-9:
        res["check_max_abs_vs_rollout_at_0.5"] = max(res["check_max_abs_vs_rollout_at_0.5"], abs(d1 - r["d1"]))
    acc[(r["sign"], thr)][r["patient"]].append(d1 - r["d0"])
    dmg[(r["sign"], thr)] += H
    rec[(r["sign"], thr)] += R
    tot[(r["sign"], thr)] += r["V"]
table = {}
for (sign, thr), byp in sorted(acc.items()):
    pm = sum(sum(v) / len(v) for v in byp.values()) / len(byp)
    table[f"{sign} {thr:.2f}"] = {"patients": len(byp), "events": sum(len(v) for v in byp.values()),
                                  "patient_mean_single_step_gain": pm,
                                  "vol_recovery": rec[(sign, thr)] / tot[(sign, thr)],
                                  "new_error_per_ml_target": dmg[(sign, thr)] / tot[(sign, thr)]}
res["table"] = table
# full rollout (not the bank sample): patient-weighted mean single-step gain by sign and round, at the default 0.5
roll = {}
for sign in ("+", "-"):
    for tset, name in (((0,), "round1"), ((1, 2, 3, 4), "rounds2to5")):
        byp = collections.defaultdict(list)
        for r in rows:
            if r["pos"] and not r["no_stroke"] and r["sign"] == sign and r["t"] in tset:
                byp[r["patient"]].append(r["gain_actual"])
        roll[f"{sign} {name}"] = {"patients": len(byp), "events": sum(len(v) for v in byp.values()),
                                  "patient_mean_gain": sum(sum(v) / len(v) for v in byp.values()) / len(byp)}
res["rollout_gain_by_sign_round"] = roll
print("rollout by sign/round:", {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in roll.items()})
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print("check vs rollout at 0.5:", res["check_max_abs_vs_rollout_at_0.5"])
for k, v in table.items():
    thr = float(k.split()[1])
    if thr in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        print(k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()})
