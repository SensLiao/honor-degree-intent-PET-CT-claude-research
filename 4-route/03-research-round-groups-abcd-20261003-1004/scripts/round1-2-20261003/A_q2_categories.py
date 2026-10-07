"""Q2: where the Dice is lost, by the type of each round's correction target (VAL only).

Same-state oracle = fix the whole referred target and nothing else (exactly what the oracle arm does; verified in
A_transitions.py).  Shortfall S = Dice(perfect) - Dice(actual next state), Shapley-split into target incompleteness,
damage and collateral bonus.  "First-order D5 points" of a category = patient mean (styles -> scan -> patient -> equal
patients) of the per-trajectory sum of S over the transitions in that category.  Rounds interact (a weak round changes
the next target), so the sum is a first-order estimate, not an exact counterfactual; transition 0 is exact because the
flat and oracle arms start from the same state and the same stroke.
"""
import collections
import json
from pathlib import Path

from A_common import ROLL, ARMS, VAL1, read_jsonl, patient_mean, size_bin
from A_transitions import build, TOL_ML

OUT = Path(__file__).with_suffix(".json")
res = {}
CATS = ["ADD <0.5 mL", "ADD 0.5-10 mL", "ADD >=10 mL", "REMOVE <0.5 mL", "REMOVE 0.5-10 mL", "REMOVE >=10 mL"]


def traj_sum(rows, keys, pat, field, pred):
    acc = {k: 0.0 for k in keys}
    for r in rows:
        k = (r["scan"], r["style"])
        if k in acc and pred(r):
            acc[k] += r[field]
    return patient_mean(acc, pat)[0]


def category_table(arm):
    rows, checks, gts = build(arm)
    pos_keys = set(gts)
    pat = {(r["scan"], r["style"]): r["patient"] for r in rows}
    act = [r for r in rows if r["pos"] and not r["no_stroke"]]
    out = {"checks": checks, "n_transitions": len(act)}
    total_ub = traj_sum(act, pos_keys, pat, "shortfall", lambda r: True)
    out["first_order_total"] = total_ub
    out["first_order_total_by_component"] = {c: traj_sum(act, pos_keys, pat, f"S_{c}", lambda r: True)
                                             for c in ("target", "damage", "collateral")}
    table = {}
    for cat in CATS + ["ALL"]:
        sel = (lambda r: True) if cat == "ALL" else (lambda r, c=cat: r["cat"] == c)
        rs = [r for r in act if sel(r)]
        if not rs:
            continue
        V = sum(r["V"] for r in rs)
        R = sum(r["R"] for r in rs)
        g_act = sum(r["gain_actual"] for r in rs)
        g_perf = sum(r["gain_perfect"] for r in rs)
        dmg = sum(r["fp_add"] + r["tp_lost"] for r in rs)
        coll = sum(r["C_same"] + r["C_opp"] for r in rs)
        table[cat] = {
            "n": len(rs), "share": len(rs) / len(act),
            "share_t0": sum(1 for r in rs if r["t"] == 0) / max(1, sum(1 for r in act if r["t"] == 0)),
            "mean_V_ml": V / len(rs), "median_V_ml": sorted(r["V"] for r in rs)[len(rs) // 2],
            "vol_weighted_recovery": R / V if V else None,
            "event_mean_recovery": sum(r["R"] / r["V"] for r in rs if r["V"] > 0) / len(rs),
            "zero_recovery_rate": sum(1 for r in rs if r["R"] <= 0) / len(rs),
            "full_recovery_rate": sum(1 for r in rs if r["R"] >= r["V"] - TOL_ML) / len(rs),
            "mean_gain_actual": g_act / len(rs), "mean_gain_perfect": g_perf / len(rs),
            "efficiency_sum_gain_over_sum_perfect": g_act / g_perf if g_perf else None,
            "dice_worse_rate": sum(1 for r in rs if r["gain_actual"] < -1e-12) / len(rs),
            "damage_ml_per_ml_target": dmg / V if V else None, "collateral_ml_per_ml_target": coll / V if V else None,
            "mean_damage_ml": dmg / len(rs),
            "D5pts_first_order": traj_sum(act, pos_keys, pat, "shortfall", sel),
            "D5pts_target_incomplete": traj_sum(act, pos_keys, pat, "S_target", sel),
            "D5pts_damage": traj_sum(act, pos_keys, pat, "S_damage", sel),
            "D5pts_collateral": traj_sum(act, pos_keys, pat, "S_collateral", sel),
            "D5pts_first_order_t0_exact": traj_sum(act, pos_keys, pat, "shortfall", lambda r, s=sel: s(r) and r["t"] == 0),
            "D5pts_first_order_t1to4": traj_sum(act, pos_keys, pat, "shortfall", lambda r, s=sel: s(r) and r["t"] > 0),
        }
    out["categories"] = table
    by_round = {}
    for t in range(5):
        sel = lambda r, tt=t: r["t"] == tt
        by_round[t] = {"shortfall": traj_sum(act, pos_keys, pat, "shortfall", sel),
                       "target": traj_sum(act, pos_keys, pat, "S_target", sel),
                       "damage": traj_sum(act, pos_keys, pat, "S_damage", sel),
                       "collateral": traj_sum(act, pos_keys, pat, "S_collateral", sel),
                       "gain_actual": traj_sum(act, pos_keys, pat, "gain_actual", sel),
                       "gain_perfect": traj_sum(act, pos_keys, pat, "gain_perfect", sel)}
    out["by_round"] = by_round
    return out, rows, pos_keys, pat


for arm in ("flat", "N3"):
    res[arm], rows, pos_keys, pat = category_table(arm)
    if arm == "flat":
        flat_rows, flat_pos, flat_pat = rows, pos_keys, pat
    elif arm == "N3":
        n3_rows = rows

# oracle's own per-round gains by category (its states differ after round 0)
o_rows, _, o_gts = build("oracle")
o_act = [r for r in o_rows if r["pos"] and not r["no_stroke"]]
res["oracle_own_states"] = {c: {"n": sum(1 for r in o_act if r["cat"] == c),
                                "mean_gain": sum(r["gain_actual"] for r in o_act if r["cat"] == c)
                                / max(1, sum(1 for r in o_act if r["cat"] == c))} for c in CATS}

# ---- distance at transition 0 (exact: oracle repairs the whole target, so its remote repair = target volume beyond R)
rem = {}
for arm in ("flat", "N3", "oracle"):
    for r in read_jsonl(ROLL / ARMS[arm] / "remote.jsonl"):
        rem[(arm, r["scan_id"], r["style"], int(r["transition"]), float(r["radius_mm"]))] = r
dist = {}
for arm, rows in (("flat", flat_rows), ("N3", n3_rows)):
    t0 = [r for r in rows if r["t"] == 0 and r["pos"] and not r["no_stroke"]]
    acc = collections.defaultdict(lambda: collections.defaultdict(float))
    split = {}
    for r in t0:
        for rad in (15.0, 30.0, 60.0):
            farV = float(rem[("oracle", r["scan"], r["style"], 0, rad)]["remote_target_repair_ml"])
            farR = float(rem[(arm, r["scan"], r["style"], 0, rad)]["remote_target_repair_ml"])
            nearV, nearR = r["V"] - farV, r["R"] - farR
            for key in ("all", r["cat"], f"size {r['size']}"):
                a = acc[(key, rad)]
                a["nearV"] += nearV
                a["nearR"] += nearR
                a["farV"] += farV
                a["farR"] += farR
                a["n"] += 1
                a["n_with_far"] += farV > TOL_ML
            if rad == 30.0:
                unrec_near = max(nearV - nearR, 0.0)
                unrec_far = max(farV - farR, 0.0)
                tot = unrec_near + unrec_far
                split[(r["scan"], r["style"])] = (r["S_target"] * (unrec_far / tot if tot > 0 else 0.0),
                                                  r["S_target"] * (unrec_near / tot if tot > 0 else 0.0),
                                                  farV > TOL_ML)
    table = {}
    for (key, rad), a in sorted(acc.items()):
        table[f"{key} | {rad:g} mm"] = {"n": int(a["n"]), "n_with_far_part": int(a["n_with_far"]),
                                        "near_ml": a["nearV"], "near_recovered": a["nearR"] / a["nearV"] if a["nearV"] else None,
                                        "far_ml": a["farV"], "far_recovered": a["farR"] / a["farV"] if a["farV"] else None,
                                        "far_share_of_target_ml": a["farV"] / (a["farV"] + a["nearV"])}
    keys = flat_pos
    far_pts = patient_mean({k: split.get(k, (0, 0, False))[0] for k in keys}, flat_pat)[0]
    near_pts = patient_mean({k: split.get(k, (0, 0, False))[1] for k in keys}, flat_pat)[0]
    with_far_pts = patient_mean({k: (split[k][0] + split[k][1]) if k in split and split[k][2] else 0.0
                                 for k in keys}, flat_pat)[0]
    dist[arm] = {"table": table, "t0_target_incomplete_D1pts_beyond_30mm": far_pts,
                 "t0_target_incomplete_D1pts_within_30mm": near_pts,
                 "t0_target_incomplete_D1pts_targets_with_any_part_beyond_30mm": with_far_pts,
                 "n_t0_targets_with_part_beyond_30mm": sum(1 for v in split.values() if v[2]),
                 "n_t0_targets": len(split)}
res["distance_t0"] = dist

# ---- distance in later rounds: flat-sourced trajectory-bank states (= flat rollout states, rounds 1-4)
ss = VAL1 / "samestate-trajectory" / "N1_STATE-s3407"
ev = {e["episode_id"]: e for e in read_jsonl(ss / "events.jsonl")}
cov = {(c["episode_id"], float(c["radius_mm"])): c for c in read_jsonl(ss / "coverage.jsonl")}
srem = {(c["episode_id"], float(c["radius_mm"])): c for c in read_jsonl(ss / "remote.jsonl")}
flat_by_key = {(r["scan"], r["style"], r["t"]): r for r in flat_rows}
match = mismatch = 0
bank = collections.defaultdict(lambda: collections.defaultdict(float))
for eid, e in ev.items():
    if ".trajbank-N1_STATE-" not in eid or e.get("status") != "ok":
        continue
    rr = flat_by_key.get((e["scan_id"], e["style"], int(e["round"])))
    if rr is None or rr["no_stroke"]:
        continue
    same = (rr["sign"] == e["sign"] and abs(rr["V"] - float(e["target_volume_ml"])) < TOL_ML
            and abs(rr["R"] - float(e["target_recovery_ml"])) < 1e-6)
    match += same
    mismatch += not same
    for rad in (15.0, 30.0, 60.0):
        c = cov.get((eid, rad))
        s = srem.get((eid, rad))
        if c is None or s is None or not c["target_voxels"]:
            continue
        V = float(e["target_volume_ml"])
        vox_ml = V / c["target_voxels"]
        farV = (c["target_voxels"] - c["covered_voxels"]) * vox_ml
        farR = float(s["remote_target_repair_ml"])
        for key in ("all", f"{'ADD' if e['sign'] == '+' else 'REMOVE'} {size_bin(V)} mL"):
            a = bank[(key, rad)]
            a["n"] += 1
            a["nearV"] += V - farV
            a["nearR"] += float(e["target_recovery_ml"]) - farR
            a["farV"] += farV
            a["farR"] += farR
# share of the target-incompleteness Shapley value beyond 30 mm: t0 (all) versus the bank states (rounds 1-4)
far_share = {"t0": [0.0, 0.0], "bank": [0.0, 0.0]}
for r in flat_rows:
    if r["t"] == 0 and r["pos"] and not r["no_stroke"]:
        farV = float(rem[("oracle", r["scan"], r["style"], 0, 30.0)]["remote_target_repair_ml"])
        farR = float(rem[("flat", r["scan"], r["style"], 0, 30.0)]["remote_target_repair_ml"])
        un_far, un_near = max(farV - farR, 0.0), max(r["V"] - farV - (r["R"] - farR), 0.0)
        if un_far + un_near > 0:
            far_share["t0"][0] += r["S_target"] * un_far / (un_far + un_near)
            far_share["t0"][1] += r["S_target"]
for eid, e in ev.items():
    if ".trajbank-N1_STATE-" not in eid or e.get("status") != "ok":
        continue
    rr = flat_by_key.get((e["scan_id"], e["style"], int(e["round"])))
    c, s = cov.get((eid, 30.0)), srem.get((eid, 30.0))
    if rr is None or rr["no_stroke"] or not rr["pos"] or c is None or s is None or not c["target_voxels"]:
        continue
    vox_ml = rr["V"] / c["target_voxels"]
    farV = (c["target_voxels"] - c["covered_voxels"]) * vox_ml
    farR = float(s["remote_target_repair_ml"])
    un_far, un_near = max(farV - farR, 0.0), max(rr["V"] - farV - (rr["R"] - farR), 0.0)
    if un_far + un_near > 0:
        far_share["bank"][0] += rr["S_target"] * un_far / (un_far + un_near)
        far_share["bank"][1] += rr["S_target"]
res["target_incompleteness_share_beyond_30mm"] = {k: (v[0] / v[1] if v[1] else None) for k, v in far_share.items()}
res["distance_bank_rounds1to4"] = {
    "bank_states_reproduce_rollout": match, "bank_states_differ": mismatch,
    "table": {f"{k} | {rad:g} mm": {"n": int(a["n"]), "near_ml": a["nearV"],
                                     "near_recovered": a["nearR"] / a["nearV"] if a["nearV"] else None,
                                     "far_ml": a["farV"], "far_recovered": a["farR"] / a["farV"] if a["farV"] else None}
              for (k, rad), a in sorted(bank.items())}}

# ---- origin of flat's later-round targets: original error (in the oracle's 5-target set), residue, damage-linked
o_by = collections.defaultdict(list)
for r in o_rows:
    if not r["no_stroke"]:
        o_by[(r["scan"], r["style"])].append((r["sign"], r["V"]))
origin = {}
for arm, rows in (("flat", flat_rows), ("N3", n3_rows)):
    by_key = {(r["scan"], r["style"], r["t"]): r for r in rows}
    cnt = collections.Counter()
    gains = collections.defaultdict(list)
    tagged = {}
    for (scan, style, t), r in by_key.items():
        if t == 0 or r["no_stroke"] or not r["pos"]:
            continue
        prev = by_key[(scan, style, t - 1)]
        orig = any(s == r["sign"] and abs(v - r["V"]) < TOL_ML for s, v in o_by[(scan, style)])
        if orig:
            tag = "original"
        elif (not prev["no_stroke"] and prev["sign"] == r["sign"] and prev["V"] - prev["R"] > TOL_ML
              and r["V"] <= prev["V"] - prev["R"] + TOL_ML):
            tag = "residue_of_previous_target"
        elif not prev["no_stroke"] and prev["sign"] != r["sign"] and (prev["fp_add"] + prev["tp_lost"]) > TOL_ML:
            tag = "after_opposite_round_with_damage"
        else:
            tag = "other_modified"
        cnt[tag] += 1
        cnt[(tag, t)] += 1
        gains[tag].append(r["gain_actual"])
        tagged[(scan, style, t)] = tag
    keys = flat_pos
    pat_ = flat_pat
    contrib = {}
    for tag in ("original", "residue_of_previous_target", "after_opposite_round_with_damage", "other_modified"):
        contrib[tag] = {
            "n": cnt[tag], "share_of_rounds_1to4": cnt[tag] / max(1, sum(cnt[x] for x in
                                                                         ("original", "residue_of_previous_target",
                                                                          "after_opposite_round_with_damage", "other_modified"))),
            "by_t": {t: cnt[(tag, t)] for t in range(1, 5)},
            "mean_gain_actual": sum(gains[tag]) / max(1, len(gains[tag])),
            "patient_mean_gain_sum": patient_mean({k: sum(by_key[(k[0], k[1], t)]["gain_actual"] for t in range(1, 5)
                                                         if tagged.get((k[0], k[1], t)) == tag) for k in keys}, pat_)[0],
            "patient_mean_shortfall_sum": patient_mean({k: sum(by_key[(k[0], k[1], t)]["shortfall"] for t in range(1, 5)
                                                              if tagged.get((k[0], k[1], t)) == tag) for k in keys}, pat_)[0],
        }
    origin[arm] = contrib
res["target_origin_rounds1to4"] = origin

OUT.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")


def show(arm):
    o = res[arm]
    print(f"===== {arm}: transitions {o['n_transitions']}  checks {o['checks']}")
    print(f"first-order total shortfall (patient-mean D5 pts) {o['first_order_total']:.4f} components",
          {k: round(v, 4) for k, v in o["first_order_total_by_component"].items()})
    print("cat | n share share_t0 | meanV medV | recVol recEvt zero full | gainAct gainPerf eff worse | dmg/ml coll/ml |"
          " D5pts first-order (target/damage/collat) t0 t1-4")
    for c, x in o["categories"].items():
        print(f"{c:18s} {x['n']:4d} {x['share']:.3f} {x['share_t0']:.3f} | {x['mean_V_ml']:7.2f} {x['median_V_ml']:6.2f} | "
              f"{x['vol_weighted_recovery']:.3f} {x['event_mean_recovery']:.3f} {x['zero_recovery_rate']:.3f} "
              f"{x['full_recovery_rate']:.3f} | {x['mean_gain_actual']:+.4f} {x['mean_gain_perfect']:+.4f} "
              f"{x['efficiency_sum_gain_over_sum_perfect']:.3f} {x['dice_worse_rate']:.3f} | "
              f"{x['damage_ml_per_ml_target']:.3f} {x['collateral_ml_per_ml_target']:.3f} | "
              f"{x['D5pts_first_order']:.4f} ({x['D5pts_target_incomplete']:.4f}/{x['D5pts_damage']:.4f}/"
              f"{x['D5pts_collateral']:+.4f}) {x['D5pts_first_order_t0_exact']:.4f} {x['D5pts_first_order_t1to4']:.4f}")
    print("by round:")
    for t, x in o["by_round"].items():
        print(f"  t{t}: " + " ".join(f"{k} {v:+.4f}" for k, v in x.items()))


show("flat")
show("N3")
print("oracle own states mean gain by category:", {c: (v["n"], round(v["mean_gain"], 4)) for c, v in res["oracle_own_states"].items()})
for arm in ("flat", "N3"):
    d = res["distance_t0"][arm]
    print(f"distance t0 {arm}: beyond30 {d['t0_target_incomplete_D1pts_beyond_30mm']:.4f} within30 "
          f"{d['t0_target_incomplete_D1pts_within_30mm']:.4f} targets-with-far-part {d['t0_target_incomplete_D1pts_targets_with_any_part_beyond_30mm']:.4f}"
          f" n_far {d['n_t0_targets_with_part_beyond_30mm']}/{d['n_t0_targets']}")
    for k, v in d["table"].items():
        if k.startswith("all") or "size" in k:
            print("   ", k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()})
print("target-incompleteness share beyond 30 mm (Dice-weighted):", res["target_incompleteness_share_beyond_30mm"])
b = res["distance_bank_rounds1to4"]
print("bank reproduce", b["bank_states_reproduce_rollout"], "differ", b["bank_states_differ"])
for k, v in b["table"].items():
    print("   ", k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()})
for arm in ("flat", "N3"):
    print("origin", arm)
    for tag, v in res["target_origin_rounds1to4"][arm].items():
        print("   ", tag, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()})
