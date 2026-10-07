# -*- coding: utf-8 -*-
"""Round-2 extra cross-checks (read-only, VAL; TRAIN bank logs for one sensitivity line).

a. Total new error of the 97 / 80 flat REMOVE bank states (the 621 mL quoted by the coordinator).
b. Lesion-damage class x REPAIR tag; lesions per state in the 'two or more lesions' class.
c. Round-1 ADD counterfactuals: recover all missed volume within 30 mm only, or beyond 30 mm only (first order, D1).
d. D1 -> D5 retention between existing models on VAL (for the first-order projection).
e. TRAIN bank: share of states whose other same-sign error is at least 10 voxels (sensitivity only).
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
from a4_common import VAL1, ROLL, ARMS, QUICK, read_jsonl, mean, quantile, dump, six_state, patient_curves  # noqa: E402
from A_transitions import build, _apply, TOL_ML  # noqa: E402
from A_common import dice  # noqa: E402

out = {}
flat_rows, _, flat_gts = build("flat")
o_rows, _, _ = build("oracle")
fk = {(r["scan"], r["style"], r["t"]): r for r in flat_rows}
d_flat, pat_flat, pos_flat = six_state(ROLL / ARMS["flat"] / "six_state.csv")
keys = [k for k in d_flat if pos_flat[k]]


def pmean(dct):
    by_scan = collections.defaultdict(list)
    for k in keys:
        by_scan[k[0]].append(dct.get(k, 0.0))
    by_pat = collections.defaultdict(list)
    for scan, v in by_scan.items():
        by_pat[pat_flat[(scan, "centerline")]].append(mean(v))
    return mean(mean(v) for v in by_pat.values())


# tags as in A_q2
o_by = collections.defaultdict(list)
for r in o_rows:
    if not r["no_stroke"]:
        o_by[(r["scan"], r["style"])].append((r["sign"], r["V"]))
tags = {}
for (scan, style, t), r in fk.items():
    if t == 0 or r["no_stroke"] or not r["pos"]:
        continue
    prev = fk[(scan, style, t - 1)]
    if any(s == r["sign"] and abs(v - r["V"]) < TOL_ML for s, v in o_by[(scan, style)]):
        tags[(scan, style, t)] = "original"
    elif (not prev["no_stroke"] and prev["sign"] == r["sign"] and prev["V"] - prev["R"] > TOL_ML
          and r["V"] <= prev["V"] - prev["R"] + TOL_ML):
        tags[(scan, style, t)] = "residue"
    elif not prev["no_stroke"] and prev["sign"] != r["sign"] and (prev["fp_add"] + prev["tp_lost"]) > TOL_ML:
        tags[(scan, style, t)] = "repair"
    else:
        tags[(scan, style, t)] = "other"

# a + b
traj = {(t["scan_id"], t["style"]): t for t in read_jsonl(ROLL / ARMS["flat"] / "trajectories.jsonl")}
tev = [e for e in read_jsonl(VAL1 / "samestate-trajectory" / "N1_STATE-s3407" / "events.jsonl")
       if ".trajbank-N1_STATE-" in e["episode_id"] and e.get("status") == "ok" and e["sign"] == "-"]
tot97 = sum(float(e["new_error_ml"] or 0) for e in tev)
in97 = sum(float(e["new_error_inside_touched_component_ml"] or 0) for e in tev)
e80 = [e for e in tev if e.get("touched_component_has_preserve")]
tot80 = sum(float(e["new_error_ml"] or 0) for e in e80)
cross = collections.Counter()
cross_ml = collections.Counter()
multi_detail = []
for e in e80:
    t = int(e["round"])
    les = traj[(e["scan_id"], e["style"])]["lesions"]["lesions"]
    dmg = [(L["overlap_voxels"][t] - L["overlap_voxels"][t + 1], L["overlap_voxels"][t + 1] == 0, float(L["volume_ml"]))
           for L in les if L["overlap_voxels"][t + 1] < L["overlap_voxels"][t]]
    n = len(dmg)
    er = sum(1 for _, z, _ in dmg if z)
    c = "none" if n == 0 else ("one_partial" if n == 1 and er == 0 else ("one_erased" if n == 1 else "two_plus"))
    tag = tags.get((e["scan_id"], e["style"], t), "untagged")
    cross[(c, tag)] += 1
    cross_ml[(c, tag)] += float(e["tp_lost_ml"] or 0)
    if c == "two_plus":
        multi_detail.append({"lesions_hit": n, "lesions_erased": er, "tp_lost_ml": float(e["tp_lost_ml"] or 0),
                             "target_ml": float(e["target_volume_ml"]), "tag": tag})
out["a_remove_bank_new_error"] = {"states_97_total_new_error_ml": tot97, "states_97_inside_touched_ml": in97,
                                  "states_80_total_new_error_ml": tot80}
out["b_lesion_class_by_tag"] = {f"{c} | {t}": v for (c, t), v in sorted(cross.items())}
out["b_lesion_class_by_tag_tp_lost_ml"] = {f"{c} | {t}": v for (c, t), v in sorted(cross_ml.items())}
out["b_two_plus_detail"] = {"states": len(multi_detail),
                            "lesions_hit_median": quantile([m["lesions_hit"] for m in multi_detail], 0.5),
                            "lesions_hit_max": max(m["lesions_hit"] for m in multi_detail),
                            "states_with_an_erased_lesion": sum(1 for m in multi_detail if m["lesions_erased"] > 0),
                            "target_ml_median": quantile([m["target_ml"] for m in multi_detail], 0.5),
                            "tp_lost_ml_median": quantile([m["tp_lost_ml"] for m in multi_detail], 0.5)}

# c: near-only / far-only counterfactuals for round-1 ADD (first order on D1)
rem = {}
for arm in ("flat", "oracle"):
    for x in read_jsonl(ROLL / ARMS[arm] / "remote.jsonl"):
        if "remote_target_repair_ml" in x:
            rem[(arm, x["scan_id"], x["style"], int(x["transition"]), float(x["radius_mm"]))] = float(x["remote_target_repair_ml"])
dn, df, dall = {}, {}, {}
miss_near = miss_far = 0.0
for r in flat_rows:
    if r["t"] != 0 or r["no_stroke"] or not r["pos"] or r["sign"] != "+":
        continue
    k = (r["scan"], r["style"])
    of30, ff30 = rem[("oracle", k[0], k[1], 0, 30.0)], rem[("flat", k[0], k[1], 0, 30.0)]
    m_far = of30 - ff30
    m_near = (r["V"] - of30) - (r["R"] - ff30)
    miss_near += m_near
    miss_far += m_far
    tp = flat_gts[k] - r["fn0"]

    def d_with(rec):
        return dice(*_apply(tp, r["fp0"], r["fn0"], "+", rec, r["C_same"], r["C_opp"], r["fp_add"], r["tp_lost"]))
    base = d_with(r["R"])
    dn[k] = d_with(r["R"] + m_near) - base
    df[k] = d_with(r["R"] + m_far) - base
    dall[k] = d_with(r["V"]) - base
rows0 = [r for r in flat_rows if r["t"] == 0 and r["pos"] and not r["no_stroke"] and r["sign"] == "+"]
V0, R0 = sum(r["V"] for r in rows0), sum(r["R"] for r in rows0)
out["c_round1_add_counterfactuals"] = {
    "recovery_now": R0 / V0,
    "recovery_if_all_missed_within_30mm_fixed": (R0 + miss_near) / V0,
    "recovery_if_all_missed_beyond_30mm_fixed": (R0 + miss_far) / V0,
    "deltaD1_fix_within_30mm": pmean(dn), "deltaD1_fix_beyond_30mm": pmean(df), "deltaD1_fix_all_missed": pmean(dall)}

# d: D1 -> D5 retention on VAL between existing models
ret = {}
cv = {arm: patient_curves(*six_state(ROLL / ARMS[arm] / "six_state.csv")) for arm in ("flat", "N3")}
m = {arm: [mean(c[i] for c in cv[arm].values()) for i in range(6)] for arm in cv}
ret["VAL three-style flat vs N3"] = (m["flat"][5] - m["N3"][5]) / (m["flat"][1] - m["N3"][1])
qs = {n: patient_curves(*six_state(p)) for n, p in QUICK.items()}
roster = set(six_state(QUICK["STATIC"])[0])
for v1, arm in (("v1flat", "flat"), ("v1N3", "N3")):
    qs[v1] = patient_curves(*six_state(ROLL / ARMS[arm] / "six_state.csv", keys=roster))
qm = {n: [mean(c[i] for c in cs.values()) for i in range(6)] for n, cs in qs.items()}
ret["quick VAL v1 flat vs v1 N3"] = (qm["v1flat"][5] - qm["v1N3"][5]) / (qm["v1flat"][1] - qm["v1N3"][1])
ret["quick VAL flat +8k vs N3 +8k"] = (qm["STATIC"][5] - qm["N4_STATIC"][5]) / (qm["STATIC"][1] - qm["N4_STATIC"][1])
out["d_D1_to_D5_retention_VAL"] = ret

# e: TRAIN bank sensitivity
BANK = Path("D:/honor-petct-data-hub/z390/banks/editor-sirb-mainline-20260920-R1/episodes")
gen = [x for x in read_jsonl(BANK / "generation_log.jsonl") if x.get("event") == "episode_generated"]
out["e_TRAIN_other_ge_10_voxels_share"] = sum(1 for x in gen if int(x.get("other_voxels") or 0) >= 10) / len(gen)
out["e_TRAIN_scans_in_bank"] = len({x["case_id"] for x in gen})

dump(out, HERE / "a4_r2_extra.json")
print(json.dumps(out, indent=1, ensure_ascii=False))
