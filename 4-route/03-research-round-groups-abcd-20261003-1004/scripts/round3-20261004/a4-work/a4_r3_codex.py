# -*- coding: utf-8 -*-
"""Checks requested after Codex round 8 (VAL, read-only, seconds).

a. Share of true-lesion deletion (tp_lost volume) from REPAIR-tagged strokes over ALL 414 later-round REMOVE strokes
   of the flat three-style rollout (same tag rule as A_q2), next to the 97 bank-state figure.
b. Round-2 REPAIR: patient-mean actual gain, same-state ideal gain and shortfall.
c. Single-step oracle tables with the final plan's label g_T: execute the candidate with its O part removed,
   recompute whole-case Dice (ADD: TP+R, FP+H, FN-R; REMOVE: TP-H, FP-R, FN+H).
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "planscripts"))  # archived copy of research/scripts
_unused = ("C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/"
                   "petct-sirb-v2-referent-scope-plan-20261003/research/scripts")
from a4_common import VAL1, ROLL, ARMS, read_jsonl, mean, dump, six_state, gt_ml  # noqa: E402
from A_transitions import build, TOL_ML  # noqa: E402
from A_common import dice  # noqa: E402

out = {}
flat_rows, _, flat_gts = build("flat")
o_rows, _, _ = build("oracle")
fk = {(r["scan"], r["style"], r["t"]): r for r in flat_rows}
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

# a
rem = [(k, r) for k, r in fk.items() if k[2] >= 1 and not r["no_stroke"] and r["pos"] and r["sign"] == "-"]
tot = sum(r["tp_lost"] for _, r in rem)
by = collections.Counter()
cnt = collections.Counter()
for k, r in rem:
    by[tags[k]] += r["tp_lost"]
    cnt[tags[k]] += 1
out["a_all_later_remove"] = {"strokes": len(rem), "tp_lost_total_ml": tot,
                             "tp_lost_by_tag_ml": dict(by), "strokes_by_tag": dict(cnt),
                             "repair_share_of_tp_lost": by["repair"] / tot}

# b
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


g, p, s, s_all = {}, {}, {}, {}
for k in keys:
    r = fk.get((k[0], k[1], 1))
    if r is None or r["no_stroke"]:
        continue
    s_all[k] = r["shortfall"]
    if tags.get((k[0], k[1], 1)) == "repair":
        g[k], p[k], s[k] = r["gain_actual"], r["gain_perfect"], r["shortfall"]
out["b_round2_repair"] = {"actual_gain": pmean(g), "ideal_gain": pmean(p), "shortfall": pmean(s),
                          "round2_total_shortfall": pmean(s_all)}

# c: single-step tables with g_T (O part removed) next to the true Delta Dice


def single_step(sweep_rows, state_of, sign_of):
    per = collections.defaultdict(dict)
    meta = {}
    for sw in sweep_rows:
        st = state_of(sw)
        if st is None:
            continue
        tp, fp, fn, d0, patient = st
        R, C, H = float(sw["target_recovery_ml"]), float(sw["other_repaired_ml"]), float(sw["new_error_ml"])
        sg = sign_of(sw)
        if sg == "+":
            dt = dice(tp + R + C, fp + H, fn - R - C)
            dg = dice(tp + R, fp + H, fn - R)
        else:
            dt = dice(tp - H, fp - R - C, fn + H)
            dg = dice(tp - H, fp - R, fn + H)
        per[sw["episode_id"]][round(float(sw["threshold"]), 2)] = (dt - d0, dg - d0)
        meta[sw["episode_id"]] = (sg, patient)
    res = {}
    for sg in ("+", "-"):
        eps = [e for e in per if meta[e][0] == sg]
        for idx, name in ((0, "true_dDice"), (1, "g_T")):
            vals = collections.defaultdict(lambda: collections.defaultdict(list))
            for e in eps:
                gains = {t: v[idx] for t, v in per[e].items()}
                g05 = gains[0.5]
                bt = max(gains, key=lambda t: (gains[t], -abs(t - 0.5)))
                pt = meta[e][1]
                vals["at_0.5"][pt].append(g05)
                vals["best_or_no_edit"][pt].append(max(gains[bt], 0.0))
                vals["skip_harmful_at_0.5"][pt].append(max(g05, 0.0))
            res[f"{sg} {name}"] = {k: mean(mean(v) for v in d.values()) for k, d in vals.items()}
            res[f"{sg} {name}"]["events"] = len(eps)
    return res


# round 1: list sweep, round 0, positive scans
ev_list = {e["episode_id"]: e for e in read_jsonl(VAL1 / "samestate-list" / "N1_STATE-s3407" / "events.jsonl")}
sw_list = [x for x in read_jsonl(VAL1 / "samestate-list" / "N1_STATE-s3407" / "sweep.jsonl")
           if int(x["round"]) == 0 and x["state_source"] == "m0_oof_raw"]


def state_round0(sw):
    k = (sw["scan_id"], sw["style"])
    if not pos_flat[k]:
        return None
    row0 = d_flat[k][0]
    gt = gt_ml(row0)
    return gt - row0["fn_ml"], row0["fp_ml"], row0["fn_ml"], row0["dice"], pat_flat[k]


out["c_round1"] = single_step(sw_list, state_round0, lambda sw: ev_list[sw["episode_id"]]["sign"])

# later rounds: flat trajectory-bank states, round r = rollout transition r (verified 200/200)
sw_traj = [x for x in read_jsonl(VAL1 / "samestate-trajectory" / "N1_STATE-s3407" / "sweep.jsonl")
           if ".trajbank-N1_STATE-" in x["episode_id"]]


def state_bank(sw):
    r = fk.get((sw["scan_id"], sw["style"], int(sw["round"])))
    if r is None or r["no_stroke"] or not r["pos"]:
        return None
    gt = flat_gts[(r["scan"], r["style"])]
    return gt - r["fn0"], r["fp0"], r["fn0"], r["d0"], r["patient"]


out["c_later"] = single_step(sw_traj, state_bank,
                             lambda sw: fk[(sw["scan_id"], sw["style"], int(sw["round"]))]["sign"])
dump(out, HERE / "a4_r3_codex.json")
print(json.dumps(out, indent=1, ensure_ascii=False))
