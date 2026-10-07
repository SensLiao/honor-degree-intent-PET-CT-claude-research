"""Q3: damage (new false positives / false negatives) created per round and what it costs in patient-mean Dice (VAL).

Per-round damage volumes come straight from transitions.jsonl (fp_added_ml, tp_lost_ml; new_error_ml = their sum).
Cost estimates:
  first-order: Shapley damage share of each round's shortfall (A_transitions.py), summed over rounds -> upper-side,
               because damage repaired in a later round is still counted;
  persistent at D5: trajectories.jsonl cumulative_damage.damage_persistent_d5_ml (voxels damaged at some round that are
               still wrong at D5) removed from the D5 state; its FP/FN split is not stored, so it is bounded by "all FP"
               and "all FN" and estimated with the trajectory's own event FP:FN ratio -> lower-side, because the rounds
               spent repairing damage are not given back.
Location: rollout remote.jsonl remote_new_error_ml beyond 15/30/60 mm of the stroke.
"""
import collections
import json
from pathlib import Path

from A_common import ROLL, ARMS, read_jsonl, patient_mean, dice, arm_six
from A_transitions import build

OUT = Path(__file__).with_suffix(".json")
res = {}


def pm(values, pat):
    return patient_mean(values, pat)[0]


for arm in ("flat", "N3"):
    rows, checks, gts = build(arm)
    pos_keys = set(gts)
    pat = {(r["scan"], r["style"]): r["patient"] for r in rows}
    act = [r for r in rows if r["pos"] and not r["no_stroke"]]
    out = {}
    # per round volumes
    per_round = {}
    for t in range(5):
        rs = [r for r in act if r["t"] == t]
        per_round[t] = {
            "n": len(rs),
            "mean_fp_added_ml": sum(r["fp_add"] for r in rs) / len(rs),
            "mean_tp_lost_ml": sum(r["tp_lost"] for r in rs) / len(rs),
            "median_new_error_ml": sorted(r["fp_add"] + r["tp_lost"] for r in rs)[len(rs) // 2],
            "share_with_damage": sum(1 for r in rs if r["fp_add"] + r["tp_lost"] > 0) / len(rs),
            "share_damage_exceeds_target_repair": sum(1 for r in rs if r["fp_add"] + r["tp_lost"] > r["R"]) / len(rs),
            "patient_mean_new_fp_ml": pm({k: sum(r["fp_add"] for r in rs if (r["scan"], r["style"]) == k) for k in pos_keys}, pat),
            "patient_mean_new_fn_ml": pm({k: sum(r["tp_lost"] for r in rs if (r["scan"], r["style"]) == k) for k in pos_keys}, pat),
            "D_pts_first_order_damage": pm({k: sum(r["S_damage"] for r in rs if (r["scan"], r["style"]) == k) for k in pos_keys}, pat),
            "share_ADD": sum(1 for r in rs if r["sign"] == "+") / len(rs),
        }
    out["per_round"] = per_round
    out["five_round_totals"] = {
        "patient_mean_new_fp_ml": pm({k: sum(r["fp_add"] for r in act if (r["scan"], r["style"]) == k) for k in pos_keys}, pat),
        "patient_mean_new_fn_ml": pm({k: sum(r["tp_lost"] for r in act if (r["scan"], r["style"]) == k) for k in pos_keys}, pat),
        "patient_mean_target_repaired_ml": pm({k: sum(r["R"] for r in act if (r["scan"], r["style"]) == k) for k in pos_keys}, pat),
        "D5pts_first_order_damage": pm({k: sum(r["S_damage"] for r in act if (r["scan"], r["style"]) == k) for k in pos_keys}, pat),
    }
    # damage relative to target, by sign and size
    rel = {}
    for sign in ("+", "-"):
        for size in ("<0.5", "0.5-10", ">=10"):
            rs = [r for r in act if r["sign"] == sign and r["size"] == size]
            dmg = [(r["fp_add"] + r["tp_lost"]) for r in rs]
            ratio = sorted(d / r["V"] for d, r in zip(dmg, rs))
            rel[f"{'ADD' if sign == '+' else 'REMOVE'} {size}"] = {
                "n": len(rs), "median_damage_over_target": ratio[len(ratio) // 2],
                "p75_damage_over_target": ratio[int(len(ratio) * 0.75)],
                "share_damage_gt_target_repair": sum(1 for d, r in zip(dmg, rs) if d > r["R"]) / len(rs),
                "share_damage_gt_half_target": sum(1 for d, r in zip(dmg, rs) if d > 0.5 * r["V"]) / len(rs)}
    out["damage_relative_to_target"] = rel
    # concentration of damage volume and of its first-order Dice cost
    dm = sorted((r["fp_add"] + r["tp_lost"] for r in act), reverse=True)
    sd = sorted((r["S_damage"] for r in act), reverse=True)
    out["concentration"] = {"top10pct_events_share_of_damage_ml": sum(dm[:len(dm) // 10]) / sum(dm),
                            "top10pct_events_share_of_damage_dice": sum(sd[:len(sd) // 10]) / sum(sd)}
    # rounds that made Dice worse: how much of their loss is damage
    worse = [r for r in act if r["gain_actual"] < -1e-12]
    out["worse_rounds"] = {"n": len(worse), "share": len(worse) / len(act),
                           "by_sign": dict(collections.Counter(r["sign"] for r in worse)),
                           "share_with_damage_gt_target_repair": sum(1 for r in worse if r["fp_add"] + r["tp_lost"] > r["R"]) / len(worse),
                           "patient_mean_sum_of_negative_gains": pm({k: sum(r["gain_actual"] for r in worse if (r["scan"], r["style"]) == k) for k in pos_keys}, pat)}
    # location of the damage
    rem = {}
    for r in read_jsonl(ROLL / ARMS[arm] / "remote.jsonl"):
        rem[(r["scan_id"], r["style"], int(r["transition"]), float(r["radius_mm"]))] = r
    loc = {}
    for sign_name, sel in (("all", lambda r: True), ("ADD", lambda r: r["sign"] == "+"), ("REMOVE", lambda r: r["sign"] == "-")):
        rs = [r for r in act if sel(r)]
        tot = sum(r["fp_add"] + r["tp_lost"] for r in rs)
        for rad in (15.0, 30.0, 60.0):
            far = sum(float(rem[(r["scan"], r["style"], r["t"], rad)]["remote_new_error_ml"] or 0.0) for r in rs)
            loc[f"{sign_name} beyond_{rad:g}mm_share_of_new_error_ml"] = far / tot
            far_ev = [float(rem[(r["scan"], r["style"], r["t"], rad)]["remote_new_error_ml"] or 0.0) / (r["fp_add"] + r["tp_lost"])
                      for r in rs if r["fp_add"] + r["tp_lost"] > 0]
            loc[f"{sign_name} beyond_{rad:g}mm_event_mean_share"] = sum(far_ev) / len(far_ev)
    out["location"] = loc
    # persistent damage at D5
    d6, _, _ = arm_six(arm)
    traj = {(t["scan_id"], t["style"]): t for t in read_jsonl(ROLL / ARMS[arm] / "trajectories.jsonl")}
    ev_fp = collections.defaultdict(float)
    ev_fn = collections.defaultdict(float)
    for r in act:
        ev_fp[(r["scan"], r["style"])] += r["fp_add"]
        ev_fn[(r["scan"], r["style"])] += r["tp_lost"]
    d5 = {}
    cf = {"all_fp": {}, "all_fn": {}, "ratio": {}}
    persist = {}
    for k in pos_keys:
        s5 = d6[k][5]
        g = gts[k]
        tp, fp, fn = g - s5["fn_ml"], s5["fp_ml"], s5["fn_ml"]
        d5[k] = s5["dice"]
        p = float(traj[k]["cumulative_damage"]["damage_persistent_d5_ml"])
        persist[k] = p
        assert p <= fp + fn + 1e-6, (k, p, fp, fn)
        # persistent damage voxels are wrong at D5, so its FP part p_fp lies in [max(0, p - FN5), min(p, FP5)]
        lo, hi = max(0.0, p - fn), min(p, fp)

        def without(pfp):
            pfn = p - pfp
            return dice(tp + pfn, fp - pfp, fn - pfn)
        cf["all_fp"][k] = without(hi)   # as much as possible counted as FP
        cf["all_fn"][k] = without(lo)   # as much as possible counted as FN
        e = ev_fp[k] + ev_fn[k]
        share_fp = ev_fp[k] / e if e > 0 else 0.5
        pfp_est = min(max(p * share_fp, lo), hi)
        cf["ratio"][k] = without(pfp_est)
        # one damage type at a time (event-ratio split): FP part only (ADD leaks) / FN part only (REMOVE over-cut)
        cf.setdefault("fp_only", {})[k] = dice(tp, fp - pfp_est, fn)
        cf.setdefault("fn_only", {})[k] = dice(tp + (p - pfp_est), fp, fn - (p - pfp_est))
        cf.setdefault("fp_only_max", {})[k] = dice(tp, fp - hi, fn)
        cf.setdefault("fn_only_max", {})[k] = dice(tp + (p - lo), fp, fn - (p - lo))
    base = pm(d5, pat)
    out["persistent_by_type_event_ratio"] = {"D5_without_FP_damage_only": pm(cf["fp_only"], pat),
                                             "D5_without_FN_damage_only": pm(cf["fn_only"], pat),
                                             "D5_without_FP_damage_only_max_feasible": pm(cf["fp_only_max"], pat),
                                             "D5_without_FN_damage_only_max_feasible": pm(cf["fn_only_max"], pat)}
    out["persistent_d5"] = {"patient_mean_persistent_damage_ml": pm(persist, pat),
                            "patient_mean_wrong_at_final_correct_at_start_ml":
                                pm({k: float(traj[k]["cumulative_damage"]["wrong_at_final_correct_at_start_ml"]) for k in pos_keys}, pat),
                            "D5": base,
                            "D5_without_persistent_damage_all_fp": pm(cf["all_fp"], pat),
                            "D5_without_persistent_damage_all_fn": pm(cf["all_fn"], pat),
                            "D5_without_persistent_damage_event_ratio": pm(cf["ratio"], pat)}
    res[arm] = out

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
for arm, o in res.items():
    print(f"===== {arm}")
    for t, x in o["per_round"].items():
        print(f"  t{t}: " + " ".join(f"{k} {v:.4f}" if isinstance(v, float) else f"{k} {v}" for k, v in x.items()))
    print("  totals:", {k: round(v, 4) for k, v in o["five_round_totals"].items()})
    for c, x in o["damage_relative_to_target"].items():
        print("  ", c, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in x.items()})
    print("  concentration:", {k: round(v, 3) for k, v in o["concentration"].items()})
    print("  worse rounds:", o["worse_rounds"])
    print("  location:", {k: round(v, 3) for k, v in o["location"].items()})
    print("  persistent:", {k: round(v, 4) for k, v in o["persistent_d5"].items()})
    print("  by type:", {k: round(v, 4) for k, v in o["persistent_by_type_event_ratio"].items()})
