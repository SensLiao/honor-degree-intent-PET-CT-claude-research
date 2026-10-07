# -*- coding: utf-8 -*-
"""Second-round computations for A4 (read-only, CPU, seconds).  VAL unless stated; item 6 also reads TRAIN bank logs.

1. Round-1 single-step selectable space from the 101-list sweep (round 0 = first stroke on the OOF start), same
   algorithm as research/scripts/S_oracle_threshold_per_state.py.
2. Round-1 ADD missed target volume by distance band, exact from the rollout remote records (flat vs oracle).
3. REMOVE damage on the flat trajectory-bank states, split by lesion-level overlap loss.
4. Check of the 'REPAIR' (after an opposite-sign damaging round) tag of A_q2 with volume tests.
5. First-order projection: round-1 ADD target recovery 22% -> 40% / 60%, new errors unchanged.
6. Share of states with >= 2 same-sign error components (TRAIN generator bank and VAL flat rollout).
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PLAN_SCRIPTS = Path("C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/"
                    "petct-sirb-v2-referent-scope-plan-20261003/research/scripts")
sys.path.insert(0, str(PLAN_SCRIPTS))
from a4_common import VAL1, ROLL, ARMS, read_jsonl, mean, quantile, dump, six_state, gt_ml  # noqa: E402
from A_transitions import build, _apply, TOL_ML  # noqa: E402
from A_common import dice  # noqa: E402

out = {}

# ---------------------------------------------------------------- shared
flat_rows, _, flat_gts = build("flat")
o_rows, _, _ = build("oracle")
fk = {(r["scan"], r["style"], r["t"]): r for r in flat_rows}
d_flat, pat_flat, pos_flat = six_state(ROLL / ARMS["flat"] / "six_state.csv")


def patient_mean_of(values):
    """values: list of (patient, value) at event level -> mean over patients of per-patient means."""
    by = collections.defaultdict(list)
    for p, v in values:
        by[p].append(v)
    return mean(mean(v) for v in by.values()), len(by)


# ---------------------------------------------------------------- 1. round-1 single-step space
sw = [s for s in read_jsonl(VAL1 / "samestate-list" / "N1_STATE-s3407" / "sweep.jsonl")
      if int(s["round"]) == 0 and s["state_source"] == "m0_oof_raw"]
ev = {e["episode_id"]: e for e in read_jsonl(VAL1 / "samestate-list" / "N1_STATE-s3407" / "events.jsonl")}
per_ep = collections.defaultdict(dict)
meta = {}
check = []
for s in sw:
    key = (s["scan_id"], s["style"])
    row0 = d_flat[key][0]
    if not pos_flat[key]:
        continue  # empty reference: Dice undefined
    g = gt_ml(row0)
    tp, fp, fn = g - row0["fn_ml"], row0["fp_ml"], row0["fn_ml"]
    R, C, H = float(s["target_recovery_ml"]), float(s["other_repaired_ml"]), float(s["new_error_ml"])
    sign = ev[s["episode_id"]]["sign"]
    d1 = dice(tp + R + C, fp + H, fn - R - C) if sign == "+" else dice(tp - H, fp - R - C, fn + H)
    thr = round(float(s["threshold"]), 2)
    per_ep[s["episode_id"]][thr] = (d1 - row0["dice"], R, C, H)
    meta[s["episode_id"]] = (sign, pat_flat[key], float(ev[s["episode_id"]]["target_volume_ml"]), key)
    if thr == 0.5:
        check.append(abs(d1 - d_flat[key][1]["dice"]))
res1 = {"events": len(per_ep), "max_abs_diff_vs_rollout_D1_at_0.5": max(check) if check else None}
for sign in ("+", "-"):
    eps = [e for e in per_ep if meta[e][0] == sign]
    vals = collections.defaultdict(list)
    below = at = above = 0
    for e in eps:
        gains = {t: v[0] for t, v in per_ep[e].items()}
        g05 = gains[0.5]
        best_t = max(gains, key=lambda t: (gains[t], -abs(t - 0.5)))
        best = gains[best_t]
        p = meta[e][1]
        vals["at_0.5"].append((p, g05))
        vals["best_threshold"].append((p, best))
        vals["best_or_no_edit"].append((p, max(best, 0.0)))
        vals["no_edit_only_if_harmful_at_0.5"].append((p, max(g05, 0.0)))
        below += best_t < 0.5 - 1e-9
        at += abs(best_t - 0.5) < 1e-9
        above += best_t > 0.5 + 1e-9
    r = {"events": len(eps), "patients": len({meta[e][1] for e in eps}),
         "best_threshold_below_0.5": below, "best_threshold_at_0.5": at, "best_threshold_above_0.5": above}
    for k, v in vals.items():
        r[k] = patient_mean_of(v)[0]
    curve = {}
    for t in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        V = sum(meta[e][2] for e in eps)
        R = sum(per_ep[e][t][1] for e in eps)
        H = sum(per_ep[e][t][3] for e in eps)
        curve[t] = {"recovered_fraction_volume": R / V if V else None, "new_error_ml_total": H,
                    "new_error_per_ml_recovered": H / R if R else None,
                    "patient_mean_gain": patient_mean_of([(meta[e][1], per_ep[e][t][0]) for e in eps])[0]}
    r["curve"] = curve
    res1[sign] = r
out["1_round1_single_step"] = res1

# ---------------------------------------------------------------- 2. round-1 ADD missed volume by distance
rem = {}
for arm in ("flat", "oracle"):
    for x in read_jsonl(ROLL / ARMS[arm] / "remote.jsonl"):
        if "remote_target_repair_ml" not in x:
            continue  # status empty_prompt_NA: no stroke this round
        rem[(arm, x["scan_id"], x["style"], int(x["transition"]), float(x["radius_mm"]))] = float(x["remote_target_repair_ml"])
bands = ("<=15", "15-30", "30-60", ">60")
pooled = collections.Counter()
per_key = {}
for r in flat_rows:
    if r["t"] != 0 or r["no_stroke"] or not r["pos"] or r["sign"] != "+":
        continue
    k = (r["scan"], r["style"])
    of = {rad: rem[("oracle", k[0], k[1], 0, rad)] for rad in (15.0, 30.0, 60.0)}
    ff = {rad: rem[("flat", k[0], k[1], 0, rad)] for rad in (15.0, 30.0, 60.0)}
    m = {"<=15": (r["V"] - of[15.0]) - (r["R"] - ff[15.0]),
         "15-30": (of[15.0] - of[30.0]) - (ff[15.0] - ff[30.0]),
         "30-60": (of[30.0] - of[60.0]) - (ff[30.0] - ff[60.0]),
         ">60": of[60.0] - ff[60.0]}
    tv = {"<=15": r["V"] - of[15.0], "15-30": of[15.0] - of[30.0], "30-60": of[30.0] - of[60.0], ">60": of[60.0]}
    for b in bands:
        pooled["miss " + b] += m[b]
        pooled["target " + b] += tv[b]
    per_key[k] = (r["patient"], m)
tot_miss = sum(pooled["miss " + b] for b in bands)
res2 = {"strokes": len(per_key), "pooled_missed_ml": {b: pooled["miss " + b] for b in bands},
        "pooled_target_ml": {b: pooled["target " + b] for b in bands},
        "pooled_share_missed_beyond_30mm": (pooled["miss 30-60"] + pooled["miss >60"]) / tot_miss,
        "pooled_recovery_by_band": {b: 1 - pooled["miss " + b] / pooled["target " + b] if pooled["target " + b] else None
                                    for b in bands}}
# patient weighting: style-mean within scan -> scan-mean within patient (scans without a round-1 ADD count as 0)
by_scan = collections.defaultdict(list)
for k, (p, m) in per_key.items():
    by_scan[k[0]].append((p, m))
all_pos = {k[0] for k in d_flat if pos_flat[k]}
pat_scan = collections.defaultdict(list)
for scan in all_pos:
    p = pat_flat[(scan, "centerline")]
    items = by_scan.get(scan, [])
    vals = {b: (sum(m[b] for _, m in items) / 3.0) for b in bands}  # three styles; a style without ADD adds 0
    pat_scan[p].append(vals)
pat_band = {p: {b: mean(v[b] for v in vs) for b in bands} for p, vs in pat_scan.items()}
shares = [(sum(v[b] for b in ("30-60", ">60")) / sum(v.values())) for v in pat_band.values() if sum(v.values()) > 1e-9]
res2["patients_with_missed_volume"] = len(shares)
res2["patient_mean_of_share_beyond_30mm"] = mean(shares)
res2["patient_median_of_share_beyond_30mm"] = quantile(shares, 0.5)
pm = {b: mean(v[b] for v in pat_band.values()) for b in bands}
res2["patient_mean_missed_ml"] = pm
res2["share_of_patient_mean_volumes_beyond_30mm"] = (pm["30-60"] + pm[">60"]) / sum(pm.values())
res2["patients_with_any_missed_beyond_30mm"] = sum(1 for v in pat_band.values() if v["30-60"] + v[">60"] > 1e-9)
res2["patients_total"] = len(pat_band)
out["2_round1_add_missed_by_distance"] = res2

# ---------------------------------------------------------------- 3. REMOVE damage split by lesions
traj = {(t["scan_id"], t["style"]): t for t in read_jsonl(ROLL / ARMS["flat"] / "trajectories.jsonl")}
tev = [e for e in read_jsonl(VAL1 / "samestate-trajectory" / "N1_STATE-s3407" / "events.jsonl")
       if ".trajbank-N1_STATE-" in e["episode_id"] and e.get("status") == "ok" and e["sign"] == "-"]
cls = collections.Counter()
cls_ml = collections.Counter()
consistency = []
n_preserve = 0
inside_total = 0.0
for e in tev:
    if not e.get("touched_component_has_preserve"):
        continue
    n_preserve += 1
    inside_total += float(e["new_error_inside_touched_component_ml"] or 0.0)
    t = int(e["round"])
    rr = fk.get((e["scan_id"], e["style"], t))
    if rr is None:
        cls["unmapped"] += 1
        continue
    consistency.append(abs(rr["tp_lost"] - float(e["tp_lost_ml"] or 0.0)))
    les = traj[(e["scan_id"], e["style"])]["lesions"]["lesions"]
    damaged, erased, ml = 0, 0, 0.0
    for L in les:
        a, b = L["overlap_voxels"][t], L["overlap_voxels"][t + 1]
        if b < a:
            damaged += 1
            erased += (b == 0)
            ml += (a - b) * float(L["volume_ml"]) / float(L["voxels"])
    if damaged == 0:
        c = "no lesion overlap lost"
    elif damaged == 1 and erased == 0:
        c = "one lesion partly cut"
    elif damaged == 1:
        c = "one lesion fully erased"
    else:
        c = "two or more lesions hit"
    cls[c] += 1
    cls_ml[c] += ml
out["3_remove_damage_by_lesion"] = {
    "remove_bank_states": len(tev), "touched_component_has_true_lesion": n_preserve,
    "new_error_inside_touched_component_ml": inside_total,
    "max_abs_diff_tp_lost_event_vs_rollout": max(consistency) if consistency else None,
    "class_counts": dict(cls), "class_lesion_volume_lost_ml": dict(cls_ml)}

# ---------------------------------------------------------------- 4. REPAIR tag check
o_by = collections.defaultdict(list)
for r in o_rows:
    if not r["no_stroke"]:
        o_by[(r["scan"], r["style"])].append((r["sign"], r["V"]))
morph = {}
for m in read_jsonl(ROLL / ARMS["flat"] / "morphology.jsonl"):
    lc = m["largest_component_fraction"]
    morph[(m["scan_id"], m["style"], int(m["round"]), m["sign"])] = (
        (lc or 0.0) * float(m["error_volume_ml"] or 0.0), int(m["component_count"]))
anchor = {(x["scan_id"], x["style"], int(x["transition"])): x.get("anchor_status")
          for x in read_jsonl(ROLL / ARMS["flat"] / "transitions.jsonl")}
tags = {}
for (scan, style, t), r in fk.items():
    if t == 0 or r["no_stroke"] or not r["pos"]:
        continue
    prev = fk[(scan, style, t - 1)]
    orig = any(s == r["sign"] and abs(v - r["V"]) < TOL_ML for s, v in o_by[(scan, style)])
    if orig:
        tag = "original"
    elif (not prev["no_stroke"] and prev["sign"] == r["sign"] and prev["V"] - prev["R"] > TOL_ML
          and r["V"] <= prev["V"] - prev["R"] + TOL_ML):
        tag = "residue"
    elif not prev["no_stroke"] and prev["sign"] != r["sign"] and (prev["fp_add"] + prev["tp_lost"]) > TOL_ML:
        tag = "repair"
    else:
        tag = "other"
    tags[(scan, style, t)] = tag
res4 = {"tag_counts": dict(collections.Counter(tags.values()))}
groups = collections.defaultdict(lambda: collections.Counter())
ratios = collections.defaultdict(list)
for (scan, style, t), tag in tags.items():
    r, prev = fk[(scan, style, t)], fk[(scan, style, t - 1)]
    opp = (not prev["no_stroke"]) and prev["sign"] != r["sign"]
    X = (prev["fp_add"] if prev["sign"] == "+" else prev["tp_lost"]) if opp else 0.0
    Lprev, _ = morph[(scan, style, t - 1, r["sign"])]
    single = anchor.get((scan, style, t)) == "valid"
    g = groups[(tag, "after_opposite" if opp else "after_same_or_none")]
    g["n"] += 1
    if single:
        g["single_anchor"] += 1
        g["target_larger_than_any_same_type_component_before"] += r["V"] > Lprev + 1e-6
    if opp and X > TOL_ML:
        g["target_le_prev_new_error"] += r["V"] <= X + 1e-9
        ratios[tag].append(r["V"] / X)
        # undo: same-type error removed this round versus new error created last round
        removed = r["R"] + r["C_same"]
        g["removed_ge_prev_new_error"] += removed >= X - 1e-9
    g["worse"] += r["gain_actual"] < -1e-12
    g["damage_this_round"] += (r["fp_add"] + r["tp_lost"]) > TOL_ML
res4["groups"] = {f"{a} | {b}": dict(v) for (a, b), v in sorted(groups.items())}
res4["V_over_prev_new_error_median"] = {k: quantile(v, 0.5) for k, v in ratios.items()}
# round-2 REPAIR contribution (patient mean, three-style), as claimed by A3
contrib = {}
for (scan, style), _ in d_flat.items():
    pass
from a4_common import patient_curves  # noqa: E402,F401
gain_t1 = collections.defaultdict(float)
short_t1 = collections.defaultdict(float)
allshort_t1 = collections.defaultdict(float)
keys = [k for k in d_flat if pos_flat[k]]
for k in keys:
    r = fk.get((k[0], k[1], 1))
    if r is None or r["no_stroke"]:
        continue
    allshort_t1[k] += r["shortfall"]
    if tags.get((k[0], k[1], 1)) == "repair":
        gain_t1[k] += r["gain_actual"]
        short_t1[k] += r["shortfall"]


def pmean(d):
    by_scan = collections.defaultdict(list)
    for k in keys:
        by_scan[k[0]].append(d.get(k, 0.0))
    by_pat = collections.defaultdict(list)
    for scan, v in by_scan.items():
        by_pat[pat_flat[(scan, "centerline")]].append(mean(v))
    return mean(mean(v) for v in by_pat.values())


res4["round2_repair_patient_mean_gain"] = pmean(gain_t1)
res4["round2_repair_patient_mean_shortfall"] = pmean(short_t1)
res4["round2_all_patient_mean_shortfall"] = pmean(allshort_t1)
# trajectory-bank cross-check: do REPAIR-tagged REMOVE states touch a predicted block that holds true lesion more often?
tb = collections.Counter()
for e in tev:
    t = int(e["round"])
    tag = tags.get((e["scan_id"], e["style"], t))
    if tag is None:
        continue
    grp = "repair" if tag == "repair" else "not_repair"
    tb[(grp, "n")] += 1
    tb[(grp, "holds_true_lesion")] += bool(e.get("touched_component_has_preserve"))
    tb[(grp, "tp_lost_ml")] += float(e["tp_lost_ml"] or 0.0)
res4["bank_remove_states"] = {f"{a} {b}": v for (a, b), v in tb.items()}
out["4_repair_tag_check"] = res4

# ---------------------------------------------------------------- 5. first-order projection
rows0 = [r for r in flat_rows if r["t"] == 0 and r["pos"] and not r["no_stroke"] and r["sign"] == "+"]
Vtot, Rtot = sum(r["V"] for r in rows0), sum(r["R"] for r in rows0)
base_rate = Rtot / Vtot
res5 = {"round1_add_strokes": len(rows0), "volume_weighted_recovery_now": base_rate,
        "per_stroke_mean_recovery_now": mean(r["R"] / r["V"] for r in rows0 if r["V"] > 0)}
for target in (0.40, 0.60):
    lam = (target - base_rate) / (1 - base_rate)
    dd = {}
    for r in rows0:
        k = (r["scan"], r["style"])
        Rn = r["R"] + lam * (r["V"] - r["R"])
        tp = flat_gts[k] - r["fn0"]
        new = dice(*_apply(tp, r["fp0"], r["fn0"], "+", Rn, r["C_same"], r["C_opp"], r["fp_add"], r["tp_lost"]))
        old = dice(*_apply(tp, r["fp0"], r["fn0"], "+", r["R"], r["C_same"], r["C_opp"], r["fp_add"], r["tp_lost"]))
        dd[k] = new - old
    res5[f"target_{target:.2f}"] = {"lambda_share_of_each_missed_part_closed": lam,
                                    "patient_mean_delta_D1_first_order": pmean(dd),
                                    "by_size": {sz: pmean({k: v for k, v in dd.items()
                                                           if fk[(k[0], k[1], 0)]["size"] == sz})
                                                for sz in ("<0.5", "0.5-10", ">=10")}}
out["5_first_order_projection"] = res5

# ---------------------------------------------------------------- 6. >= 2 same-sign error components
BANK = Path("D:/honor-petct-data-hub/z390/banks/editor-sirb-mainline-20260920-R1/episodes")
gen = [x for x in read_jsonl(BANK / "generation_log.jsonl") if x.get("event") == "episode_generated"]
tr6 = collections.defaultdict(list)
for x in gen:
    multi = x.get("anchor_status") not in ("valid", None)
    two = (int(x.get("other_voxels") or 0) > 0) or multi
    grp = "round 0 (start state)" if int(x["round_index"]) == 0 else "rounds 1-4 (generator states)"
    tr6[grp].append((x["case_id"], two))
    tr6["all"].append((x["case_id"], two))


def shares(items):
    by = collections.defaultdict(list)
    for scan, v in items:
        by[scan].append(v)
    return {"states": len(items), "share_by_state": sum(v for _, v in items) / len(items),
            "scans": len(by), "share_by_scan_mean": mean(mean(v) for v in by.values()),
            "scans_with_at_least_one": sum(1 for v in by.values() if any(v)) / len(by)}


res6 = {"TRAIN_bank": {k: shares(v) for k, v in tr6.items()},
        "TRAIN_anchor_status": dict(collections.Counter(x.get("anchor_status") for x in gen))}
va = collections.defaultdict(list)
for (scan, style, t), r in fk.items():
    if r["no_stroke"] or not r["pos"]:
        continue
    _, n = morph[(scan, style, t, r["sign"])]
    two = n >= 2 or anchor.get((scan, style, t)) == "multi"
    va["round 1" if t == 0 else "rounds 2-5"].append((scan, two))
res6["VAL_flat_rollout"] = {k: shares(v) for k, v in va.items()}
out["6_two_or_more_same_sign_components"] = res6

dump(out, HERE / "a4_r2_rounds.json")
print(json.dumps(out, indent=1, ensure_ascii=False, default=str)[:12000])
