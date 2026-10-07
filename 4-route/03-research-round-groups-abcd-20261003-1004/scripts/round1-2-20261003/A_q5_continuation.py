"""Q5: +8k continuation (N1_STATE_STATIC / N4_STATIC quick VAL) versus its v1 parent on the same (scan, style) roster.

The quick VAL stores only six_state.csv, so per-round moves are recovered from the volume identity: the executor is
monotone per stroke (ADD only adds, REMOVE only removes; checked on v1, opposite-sign repair is always 0), hence
  ADD:    repair = FN_t - FN_t+1, damage (new FP) = FP_t+1 - FP_t
  REMOVE: repair = FP_t - FP_t+1, damage (new FN) = FN_t+1 - FN_t
and the stroke sign follows from which of FP/FN moved.  The inference is validated on v1 against transitions.jsonl.
Round 0 starts from the same state with the same stroke in both models, so its target (sign, volume) is known from
the v1 transitions and the round-0 comparison is matched exactly.  VAL only.
"""
import collections
import json
import random
from pathlib import Path

from A_common import QUICK, six_state, arm_six, arm_transitions, patient_mean, gt_ml, dice, size_bin

OUT = Path(__file__).with_suffix(".json")
res = {}


def infer(a, b):
    dfp, dfn = b["fp_ml"] - a["fp_ml"], b["fn_ml"] - a["fn_ml"]
    eps = 1e-9
    add_like = dfn < -eps or dfp > eps
    rem_like = dfp < -eps or dfn > eps
    if add_like and rem_like:
        return "conflict", 0.0, 0.0
    if add_like:
        return "+", max(-dfn, 0.0), max(dfp, 0.0)
    if rem_like:
        return "-", max(-dfp, 0.0), max(dfn, 0.0)
    return "none", 0.0, 0.0


def per_round(d, keys, gts, pat, tr_v1=None):
    rows = []
    for k in keys:
        for t in range(5):
            a, b = d[k][t], d[k][t + 1]
            sign, rep, dmg = infer(a, b)
            g = gts[k]
            tp1, fp1, fn1 = g - b["fn_ml"], b["fp_ml"], b["fn_ml"]
            # Dice of the next state with this round's damage undone
            if sign == "+":
                d_nodmg = dice(tp1, fp1 - dmg, fn1)
            elif sign == "-":
                d_nodmg = dice(tp1 + dmg, fp1, fn1 - dmg)
            else:
                d_nodmg = b["dice"]
            rows.append({"k": k, "t": t, "sign": sign, "repair": rep, "damage": dmg, "gain": b["dice"] - a["dice"],
                         "damage_cost": d_nodmg - b["dice"]})
    return rows


for label, v1arm in (("flat8k", "flat"), ("N3_8k", "N3")):
    q, qpat, qpos = six_state(QUICK[label])
    v, vpat, vpos = arm_six(v1arm)
    tr = arm_transitions(v1arm)
    keys = sorted(k for k in q if qpos[k])
    assert all(k in v for k in keys)
    gts = {k: gt_ml(v[k][0]) for k in keys}
    d0diff = max(abs(q[k][0]["dice"] - v[k][0]["dice"]) for k in keys)
    out = {"positive_trajectories": len(keys), "max_D0_diff": d0diff}
    # validate inference on v1 (all positive keys of the three-style run)
    ok = bad = 0
    for (scan, style, t), x in tr.items():
        kk = (scan, style)
        if not vpos[kk] or x.get("no_stroke"):
            continue
        s, rep, dmg = infer(v[kk][t], v[kk][t + 1])
        exp_rep = float(x["target_recovery_ml"]) + float(x["same_sign_other_repair_ml"])
        exp_dmg = float(x["fp_added_ml"]) + float(x["tp_lost_ml"])
        if s == "none":
            good = exp_rep < 1e-9 and exp_dmg < 1e-9
        else:
            good = s == x["sign"] and abs(rep - exp_rep) < 1e-6 and abs(dmg - exp_dmg) < 1e-6
        ok += good
        bad += not good
    out["inference_check_on_v1"] = {"agree": ok, "disagree": bad}
    rq = per_round(q, keys, gts, qpat)
    rv = per_round(v, keys, gts, vpat)
    curves = {}
    for name, d in (("v1", v), ("8k", q)):
        curves[name] = [patient_mean({k: d[k][r]["dice"] for k in keys}, qpat)[0] for r in range(6)]
    out["curves"] = curves

    def pm(rows, field, pred=lambda r: True):
        acc = {k: 0.0 for k in keys}
        for r in rows:
            if pred(r):
                acc[r["k"]] += r[field]
        return patient_mean(acc, qpat)[0]
    out["by_round"] = {}
    for t in range(5):
        o = {}
        for name, rows in (("v1", rv), ("8k", rq)):
            rs = [r for r in rows if r["t"] == t]
            o[name] = {"gain": pm(rows, "gain", lambda r, t=t: r["t"] == t),
                       "damage_cost_first_order": pm(rows, "damage_cost", lambda r, t=t: r["t"] == t),
                       "mean_damage_ml": sum(r["damage"] for r in rs) / len(rs),
                       "share_ADD": sum(r["sign"] == "+" for r in rs) / len(rs),
                       "share_no_edit": sum(r["sign"] == "none" for r in rs) / len(rs),
                       "worse_rate": sum(r["gain"] < -1e-12 for r in rs) / len(rs)}
        out["by_round"][t] = o
    out["five_round"] = {name: {"damage_cost_first_order": pm(rows, "damage_cost"),
                                "patient_mean_new_error_ml": pm(rows, "damage"),
                                "patient_mean_repair_ml": pm(rows, "repair"),
                                "worse_rate": sum(r["gain"] < -1e-12 for r in rows) / len(rows),
                                "no_edit_rate": sum(r["sign"] == "none" for r in rows) / len(rows)}
                         for name, rows in (("v1", rv), ("8k", rq))}
    out["final_state"] = {name: {"patient_mean_fp5_ml": patient_mean({k: d[k][5]["fp_ml"] for k in keys}, qpat)[0],
                                 "patient_mean_fn5_ml": patient_mean({k: d[k][5]["fn_ml"] for k in keys}, qpat)[0]}
                          for name, d in (("v1", v), ("8k", q))}
    # round 0 matched by target category (same state, same stroke)
    cats = collections.defaultdict(lambda: {"v1": [], "8k": []})
    for k in keys:
        x = tr[(k[0], k[1], 0)]
        if x.get("no_stroke"):
            continue
        cat = f"{'ADD' if x['sign'] == '+' else 'REMOVE'} {size_bin(float(x['target_volume_ml']))} mL"
        V = float(x["target_volume_ml"])
        for name, rows in (("v1", rv), ("8k", rq)):
            r = next(r for r in rows if r["k"] == k and r["t"] == 0)
            cats[cat][name].append((k, r["gain"], r["repair"] / V, r["damage"] / V, r["damage_cost"]))
    t0 = {}
    for cat, dd in sorted(cats.items()):
        t0[cat] = {"n": len(dd["v1"])}
        for name in ("v1", "8k"):
            xs = dd[name]
            t0[cat][name] = {"mean_gain": sum(x[1] for x in xs) / len(xs), "mean_repair_frac": sum(x[2] for x in xs) / len(xs),
                             "mean_damage_per_ml_target": sum(x[3] for x in xs) / len(xs),
                             "mean_damage_cost": sum(x[4] for x in xs) / len(xs)}
        diffs = [b[1] - a[1] for a, b in zip(dd["v1"], dd["8k"])]
        t0[cat]["gain_diff_mean"] = sum(diffs) / len(diffs)
        t0[cat]["better_worse_tie"] = (sum(x > 1e-9 for x in diffs), sum(x < -1e-9 for x in diffs), sum(abs(x) <= 1e-9 for x in diffs))
    out["round0_by_category_matched"] = t0
    # damage monitor readable from six_state alone: per-sign patient-weighted mean gain, round 1 vs rounds 2-5;
    # patient-mean FP at D0 and D5
    mon = {}
    for name, rows in (("v1", rv), ("8k", rq)):
        m = {}
        for sign in ("+", "-"):
            for tset, tname in (((0,), "round1"), ((1, 2, 3, 4), "rounds2to5")):
                byp = collections.defaultdict(list)
                for r in rows:
                    if r["sign"] == sign and r["t"] in tset:
                        byp[qpat[r["k"]]].append(r["gain"])
                m[f"{sign} {tname}"] = {"events": sum(len(v) for v in byp.values()),
                                        "patient_mean_gain": sum(sum(v) / len(v) for v in byp.values()) / len(byp)}
        d = v if name == "v1" else q
        m["patient_mean_fp0_ml"] = patient_mean({k: d[k][0]["fp_ml"] for k in keys}, qpat)[0]
        m["patient_mean_fp5_ml"] = patient_mean({k: d[k][5]["fp_ml"] for k in keys}, qpat)[0]
        mon[name] = m
    out["damage_monitor"] = mon
    print(label, "damage monitor:", json.dumps(mon))
    # bootstrap of the patient-mean difference in five-round damage cost and in D5
    pats = sorted({qpat[k] for k in keys})
    def per_pat(rows, field):
        acc = {k: 0.0 for k in keys}
        for r in rows:
            acc[r["k"]] += r[field]
        return patient_mean(acc, qpat)[1]
    dv, dq = per_pat(rv, "damage_cost"), per_pat(rq, "damage_cost")
    rng = random.Random(3407)
    boots = []
    for _ in range(5000):
        s = [rng.choice(pats) for _ in pats]
        boots.append(sum(dq[p] - dv[p] for p in s) / len(s))
    boots.sort()
    out["damage_cost_diff_8k_minus_v1"] = {"mean": sum(dq[p] - dv[p] for p in pats) / len(pats),
                                           "ci95": [boots[125], boots[4874]]}
    res[label] = out

OUT.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
for label, o in res.items():
    print("=====", label, "positive trajectories", o["positive_trajectories"], "max D0 diff", o["max_D0_diff"],
          "inference check", o["inference_check_on_v1"])
    for n, c in o["curves"].items():
        print(f"   {n:3s} " + " ".join(f"{x:.4f}" for x in c))
    for t, x in o["by_round"].items():
        print(f"   t{t}: " + " | ".join(f"{n}: " + " ".join(f"{k} {v:+.4f}" for k, v in y.items()) for n, y in x.items()))
    print("   five-round:", {n: {k: round(v, 4) for k, v in y.items()} for n, y in o["five_round"].items()})
    print("   final:", {n: {k: round(v, 3) for k, v in y.items()} for n, y in o["final_state"].items()})
    print("   damage cost diff 8k-v1:", o["damage_cost_diff_8k_minus_v1"])
    for cat, x in o["round0_by_category_matched"].items():
        print(f"   t0 {cat:18s} n {x['n']:3d} v1 gain {x['v1']['mean_gain']:+.4f} rep {x['v1']['mean_repair_frac']:.3f} dmg/ml {x['v1']['mean_damage_per_ml_target']:.3f}"
              f" | 8k gain {x['8k']['mean_gain']:+.4f} rep {x['8k']['mean_repair_frac']:.3f} dmg/ml {x['8k']['mean_damage_per_ml_target']:.3f}"
              f" | diff {x['gain_diff_mean']:+.4f} b/w/t {x['better_worse_tie']}")
