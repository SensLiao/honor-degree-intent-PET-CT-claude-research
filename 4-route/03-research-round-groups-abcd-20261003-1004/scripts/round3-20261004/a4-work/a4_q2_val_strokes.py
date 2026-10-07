"""VAL three-style full VAL (v1 40k): ADD/REMOVE stroke accounting.

Exact decomposition: for every (scan, style), D5 - D0 = sum over rounds of (D_{t+1} - D_t).  Each round is tagged by the
robot's sign (ADD/REMOVE) or 'no stroke'.  Averaging is linear (style mean -> scan mean -> patient mean -> patients
equally), so the patient-mean D5 - D0 splits exactly into per-(sign, round-group) contributions.
Also: counts, share of strokes that lower Dice, and the later-round REMOVE ledger with volumes."""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import ROLL, ARMS, six_state, read_jsonl, mean, summary_stats, dump

EPS = 1e-9
out = {}
for arm in ("flat", "N3", "oracle"):
    d, pat, pos = six_state(ROLL / ARMS[arm] / "six_state.csv")
    trans = {(r["scan_id"], r["style"], int(r["transition"])): r
             for r in read_jsonl(ROLL / ARMS[arm] / "transitions.jsonl")}
    # contributions per (scan, style)
    contrib = collections.defaultdict(lambda: collections.defaultdict(float))  # key -> group -> value
    counts = collections.Counter()
    worse = collections.Counter()
    better = collections.Counter()
    zero = collections.Counter()
    gains = collections.defaultdict(list)
    vol = collections.defaultdict(lambda: collections.defaultdict(float))
    for k, rounds in d.items():
        if not pos[k]:
            continue
        for t in range(5):
            x = trans[(k[0], k[1], t)]
            g = rounds[t + 1]["dice"] - rounds[t]["dice"]
            if x.get("no_stroke"):
                sign = "none"
            else:
                sign = "ADD" if x["sign"] == "+" else "REMOVE"
            grp = "r1" if t == 0 else "r2-5"
            contrib[k][f"{sign}|{grp}"] += g
            counts[(sign, grp)] += 1
            gains[(sign, grp)].append(g)
            if g < -EPS:
                worse[(sign, grp)] += 1
            elif g > EPS:
                better[(sign, grp)] += 1
            else:
                zero[(sign, grp)] += 1
            if sign != "none":
                v = vol[(sign, grp)]
                v["target_volume_ml"] += float(x["target_volume_ml"] or 0.0)
                v["target_recovery_ml"] += float(x["target_recovery_ml"] or 0.0)
                v["new_error_ml"] += float(x["new_error_ml"] or 0.0)
                v["fp_added_ml"] += float(x["fp_added_ml"] or 0.0)
                v["tp_lost_ml"] += float(x["tp_lost_ml"] or 0.0)
                v["other_repair_ml"] += float(x["same_sign_other_repair_ml"] or 0.0) + float(x["opposite_sign_repair_ml"] or 0.0)
                v["zero_recovery_with_damage"] += 1.0 if x.get("zero_recovery_with_damage") else 0.0
    groups = sorted({g for k in contrib for g in contrib[k]})
    # patient-mean of each group contribution (styles -> scans -> patients)
    by_scan = collections.defaultdict(list)
    for k in contrib:
        by_scan[k[0]].append(k)
    per_patient = collections.defaultdict(lambda: collections.defaultdict(list))
    for scan, ks in by_scan.items():
        p = pat[ks[0]]
        for g in groups:
            per_patient[p][g].append(mean(contrib[k].get(g, 0.0) for k in ks))
    pm = {g: mean(mean(per_patient[p][g]) for p in per_patient) for g in groups}
    total = sum(pm.values())
    # D5 - D0 check
    from a4_common import patient_curves
    c = patient_curves(d, pat, pos)
    check = mean(v[5] - v[0] for v in c.values())
    # per patient: share of patients whose later REMOVE net is negative
    later_remove_pat = {p: mean(per_patient[p].get("REMOVE|r2-5", [0.0])) for p in per_patient}
    res = {
        "patient_mean_contribution": pm,
        "sum_contributions": total,
        "check_patient_mean_D5_minus_D0": check,
        "counts": {f"{s}|{g}": n for (s, g), n in counts.items()},
        "worse": {f"{s}|{g}": n for (s, g), n in worse.items()},
        "better": {f"{s}|{g}": n for (s, g), n in better.items()},
        "zero": {f"{s}|{g}": n for (s, g), n in zero.items()},
        "per_stroke_gain": {f"{s}|{g}": summary_stats(v) for (s, g), v in gains.items()},
        "volumes": {f"{s}|{g}": dict(v) for (s, g), v in vol.items()},
        "patients_later_remove_net_negative": sum(1 for v in later_remove_pat.values() if v < -EPS),
        "patients_later_remove_net_positive": sum(1 for v in later_remove_pat.values() if v > EPS),
        "patients_total": len(per_patient),
    }
    # first-order: Dice lost by REMOVE strokes that lowered Dice in rounds 2-5 (patient-mean of the negative parts)
    neg = collections.defaultdict(lambda: collections.defaultdict(float))
    for k, rounds in d.items():
        if not pos[k]:
            continue
        for t in range(5):
            x = trans[(k[0], k[1], t)]
            if x.get("no_stroke"):
                continue
            g = rounds[t + 1]["dice"] - rounds[t]["dice"]
            sign = "ADD" if x["sign"] == "+" else "REMOVE"
            grp = "r1" if t == 0 else "r2-5"
            if g < 0:
                neg[k][f"{sign}|{grp}"] += g
    pp = collections.defaultdict(lambda: collections.defaultdict(list))
    for scan, ks in by_scan.items():
        p = pat[ks[0]]
        for g in groups:
            pp[p][g].append(mean(neg[k].get(g, 0.0) for k in ks))
    res["patient_mean_negative_part"] = {g: mean(mean(pp[p][g]) for p in pp) for g in groups}
    out[arm] = res

dump(out, Path(__file__).with_suffix(".json"))
for arm, res in out.items():
    print("==", arm, "sum", round(res["sum_contributions"], 4), "check", round(res["check_patient_mean_D5_minus_D0"], 4))
    for g, v in sorted(res["patient_mean_contribution"].items()):
        n = res["counts"].get(g, 0)
        w = res["worse"].get(g, 0)
        b = res["better"].get(g, 0)
        s = res["per_stroke_gain"].get(g, {})
        print(f"  {g:14s} contrib {v:+.4f}  neg-part {res['patient_mean_negative_part'].get(g, 0):+.4f}  strokes {n:4d}"
              f"  better {b:4d} worse {w:4d} ({(w / n * 100 if n else 0):.1f}%)  mean/stroke {s.get('mean', 0):+.4f}"
              f" median {s.get('median', 0):+.4f}")
    for g, v in sorted(res["volumes"].items()):
        print("   vol", g, {kk: round(vv, 1) for kk, vv in v.items()})
    print("  patients later-REMOVE net negative/positive", res["patients_later_remove_net_negative"],
          res["patients_later_remove_net_positive"], "of", res["patients_total"])
