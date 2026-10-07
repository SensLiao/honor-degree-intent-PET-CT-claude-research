"""Q1 gap structure on the three-style VAL (VAL only).  flat (N1_STATE) and N3 versus the oracle arm.

Outputs: patient-mean D0..D5 per arm; per-round gap to oracle; per-transition zero-change / worse counts; patient
concentration of the D5 gap; worst patients with per-round curves.  Writes A_q1_gap_structure.json next to this file.
"""
import collections
import json
from pathlib import Path

from A_common import arm_six, arm_transitions, patient_mean, nauc

OUT = Path(__file__).with_suffix(".json")
res = {}
six = {a: arm_six(a) for a in ("flat", "N3", "oracle", "noop")}
pat = six["flat"][1]
pos = six["flat"][2]
pos_keys = {k for k, v in pos.items() if v}

# 1. patient-mean curves
curves, pcurves = {}, {}
for a, (d, p, ps) in six.items():
    assert set(d) == set(six["flat"][0])
    cur, per_pat = [], collections.defaultdict(list)
    for r in range(6):
        m, pm = patient_mean({k: d[k][r]["dice"] for k in pos_keys}, pat)
        cur.append(m)
        for pid, v in pm.items():
            per_pat[pid].append(v)
    curves[a] = cur
    pcurves[a] = dict(per_pat)
res["curves_patient_mean"] = curves
res["nauc_patient_mean"] = {a: sum(nauc(c) for c in pcurves[a].values()) / len(pcurves[a]) for a in pcurves}
res["n_patients"] = len(pcurves["flat"])
res["n_positive_scans"] = len({k[0] for k in pos_keys})
for a in ("flat", "N3"):
    gap = [curves["oracle"][r] - curves[a][r] for r in range(6)]
    res[f"gap_{a}"] = {"per_round": gap, "increment": [gap[r] - gap[r - 1] for r in range(1, 6)],
                       "share_of_d5_gap_present_at_d1": gap[1] / gap[5],
                       "gain_per_round_arm": [curves[a][r] - curves[a][r - 1] for r in range(1, 6)],
                       "gain_per_round_oracle": [curves["oracle"][r] - curves["oracle"][r - 1] for r in range(1, 6)]}

# 2. per-transition change counts (positive scans for Dice; all scans for edits)
for a in ("flat", "N3", "oracle"):
    d = six[a][0]
    tr = arm_transitions(a)
    cnt = collections.Counter()
    by_round = collections.defaultdict(collections.Counter)
    for (scan, style, t), row in tr.items():
        k = (scan, style)
        no_stroke = bool(row.get("no_stroke"))
        flip = row.get("flip_ml") or 0.0
        cnt["all_transitions"] += 1
        cnt["no_stroke"] += no_stroke
        cnt["no_edit_with_stroke"] += (flip == 0.0 and not no_stroke)
        if pos[k]:
            dd = d[k][t + 1]["dice"] - d[k][t]["dice"]
            cnt["pos_transitions"] += 1
            cnt["pos_no_stroke"] += no_stroke
            cnt["pos_no_edit_with_stroke"] += (flip == 0.0 and not no_stroke)
            cnt["pos_dice_zero_change"] += abs(dd) <= 1e-12
            cnt["pos_dice_worse"] += dd < -1e-12
            cnt["pos_dice_worse_by_more_than_0.01"] += dd < -0.01
            cnt["pos_dice_worse_by_more_than_0.05"] += dd < -0.05
            cnt["pos_dice_better"] += dd > 1e-12
            br = by_round[t]
            br["n"] += 1
            br["zero"] += abs(dd) <= 1e-12
            br["worse"] += dd < -1e-12
            br["no_stroke"] += no_stroke
    res[f"transition_counts_{a}"] = dict(cnt)
    res[f"transition_counts_by_round_{a}"] = {t: dict(c) for t, c in sorted(by_round.items())}

# 3. scan-level: how many positive scan-style trajectories end below their own best state, and below D0
for a in ("flat", "N3"):
    d = six[a][0]
    below_best = sum(1 for k in pos_keys if d[k][5]["dice"] < max(d[k][r]["dice"] for r in range(6)) - 1e-12)
    below_d0 = sum(1 for k in pos_keys if d[k][5]["dice"] < d[k][0]["dice"] - 1e-12)
    # patient-mean D5 if every trajectory stopped at its best state (an oracle stopping rule, upper reference only)
    best_m, _ = patient_mean({k: max(d[k][r]["dice"] for r in range(6)) for k in pos_keys}, pat)
    res[f"stopping_{a}"] = {"trajectories": len(pos_keys), "d5_below_own_best_state": below_best,
                            "d5_below_d0": below_d0, "patient_mean_best_state_oracle_stop": best_m}

# 4. patient concentration of the D5 gap
for a in ("flat", "N3"):
    gaps = {p: pcurves["oracle"][p][5] - pcurves[a][p][5] for p in pcurves[a]}
    order = sorted(gaps, key=lambda p: -gaps[p])
    tot = sum(gaps.values())
    pos_tot = sum(g for g in gaps.values() if g > 0)
    cum = []
    run = 0.0
    for i, p in enumerate(order):
        run += gaps[p]
        cum.append(run / tot)
    res[f"concentration_{a}"] = {
        "patients": len(gaps), "sum_gap": tot, "mean_gap": tot / len(gaps),
        "negative_gap_patients": sum(1 for g in gaps.values() if g < 0),
        "top5_share": cum[4], "top10_share": cum[9], "top20_share": cum[19],
        "patients_gap_ge_0.30": sum(1 for g in gaps.values() if g >= 0.30),
        "patients_gap_ge_0.20": sum(1 for g in gaps.values() if g >= 0.20),
        "patients_gap_ge_0.10": sum(1 for g in gaps.values() if g >= 0.10),
        "patients_gap_lt_0.05": sum(1 for g in gaps.values() if g < 0.05),
        "median_gap": sorted(gaps.values())[len(gaps) // 2],
        "gap_at_d1_share_top10": sum(pcurves["oracle"][p][1] - pcurves[a][p][1] for p in order[:10])
        / sum(pcurves["oracle"][p][1] - pcurves[a][p][1] for p in pcurves[a]),
    }
    # patient-mean D5 if the 10 worst-gap patients reached oracle D5 (everyone else unchanged)
    fixed = {p: (pcurves["oracle"][p][5] if p in order[:10] else pcurves[a][p][5]) for p in gaps}
    res[f"concentration_{a}"]["d5_if_top10_reached_oracle"] = sum(fixed.values()) / len(fixed)
    worst = []
    tr = arm_transitions(a)
    d = six[a][0]
    for p in order[:12]:
        scans = sorted({k[0] for k in pos_keys if pat[k] == p})
        tseq = []
        for scan in scans:
            for style in ("centerline", "random", "boundary"):
                seq = []
                for t in range(5):
                    row = tr[(scan, style, t)]
                    seq.append(f"{row['sign']}{row['target_volume_ml']:.1f}" if not row.get("no_stroke") else "none")
                tseq.append((scan[-10:], style[:4], seq))
        worst.append({"patient": p, "gap_d5": gaps[p], "n_pos_scans": len(scans),
                      "arm_curve": [round(x, 4) for x in pcurves[a][p]],
                      "oracle_curve": [round(x, 4) for x in pcurves["oracle"][p]],
                      "gt_ml_scans": None,
                      "fp_d0_ml": [round(d[(s, 'centerline')][0]["fp_ml"], 2) for s in scans],
                      "fn_d0_ml": [round(d[(s, 'centerline')][0]["fn_ml"], 2) for s in scans],
                      "fp_d5_ml_mean_styles": [round(sum(d[(s, st)][5]["fp_ml"] for st in ("centerline", "random", "boundary")) / 3, 2) for s in scans],
                      "fn_d5_ml_mean_styles": [round(sum(d[(s, st)][5]["fn_ml"] for st in ("centerline", "random", "boundary")) / 3, 2) for s in scans],
                      "targets_sign_ml": tseq})
    res[f"worst_patients_{a}"] = worst

OUT.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print("curves:")
for a, c in curves.items():
    print(f"  {a:6s}", " ".join(f"{x:.4f}" for x in c), f"nAUC {res['nauc_patient_mean'][a]:.4f}")
for a in ("flat", "N3"):
    g = res[f"gap_{a}"]
    print(f"gap {a}: per round", " ".join(f"{x:.4f}" for x in g["per_round"]), f"| increment",
          " ".join(f"{x:+.4f}" for x in g["increment"]), f"| share at D1 {g['share_of_d5_gap_present_at_d1']:.3f}")
    print(f"   gains {a}:", " ".join(f"{x:+.4f}" for x in g["gain_per_round_arm"]), "| oracle gains:",
          " ".join(f"{x:+.4f}" for x in g["gain_per_round_oracle"]))
    print(f"   transitions {a}:", res[f"transition_counts_{a}"])
    print(f"   by round {a}:", res[f"transition_counts_by_round_{a}"])
    print(f"   stopping {a}:", res[f"stopping_{a}"])
    c = res[f"concentration_{a}"]
    print(f"   concentration {a}:", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()})
print("oracle transitions:", res["transition_counts_oracle"])
for w in res["worst_patients_flat"][:12]:
    print(f"  {w['patient']} gap {w['gap_d5']:.3f} scans {w['n_pos_scans']} flat {w['arm_curve']} oracle {w['oracle_curve']}")
    print(f"      FP0 {w['fp_d0_ml']} FN0 {w['fn_d0_ml']} FP5 {w['fp_d5_ml_mean_styles']} FN5 {w['fn_d5_ml_mean_styles']}")
    for s in w["targets_sign_ml"][:6]:
        print("      ", s)
