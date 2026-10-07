"""Q7: other large, fixable losses (VAL only).

(a) D5 gap flat->oracle split into excess FP and excess FN (two-player Shapley per trajectory; TP = GT - FN).
(b) D5 gap split into persistent damage versus unrepaired original error (two-player Shapley; the FP/FN split of the
    persistent damage is not stored, so it is run at both ends of its feasible range and at the event FP:FN ratio).
(c) gap by the scan's total lesion volume (GT burden).
(d) lesion-level detection at D0/D5 by lesion size; lesions erased by the model.
(e) small targets: model-free native<->3 mm round trip of the referred target (same-state trajectory states).
(f) large REMOVE targets and isolated-FP REMOVE events (candidate physiological uptake; anatomy not available).
"""
import collections
import json
from pathlib import Path

from A_common import ROLL, ARMS, VAL1, read_jsonl, patient_mean, dice, arm_six
from A_transitions import build

OUT = Path(__file__).with_suffix(".json")
res = {}
six = {a: arm_six(a) for a in ("flat", "N3", "oracle")}
pat, pos = six["flat"][1], six["flat"][2]
rows_f, _, gts = build("flat")
keys = set(gts)


def D(g, fp, fn):
    return dice(g - fn, fp, fn)


def pm(vals):
    return patient_mean(vals, pat)[0]


# (a) FP/FN split of the D5 gap and of 1 - D0, 1 - D5
for arm in ("flat", "N3"):
    d, o = six[arm][0], six["oracle"][0]
    fpS, fnS, d0fp, d0fn, d5fp, d5fn = {}, {}, {}, {}, {}, {}
    for k in keys:
        g = gts[k]
        a5, b5 = d[k][5], o[k][5]
        fp1, fn1, fp2, fn2 = a5["fp_ml"], a5["fn_ml"], b5["fp_ml"], b5["fn_ml"]
        fpS[k] = 0.5 * ((D(g, fp2, fn1) - D(g, fp1, fn1)) + (D(g, fp2, fn2) - D(g, fp1, fn2)))
        fnS[k] = 0.5 * ((D(g, fp1, fn2) - D(g, fp1, fn1)) + (D(g, fp2, fn2) - D(g, fp2, fn1)))
        for (tgtfp, tgtfn, r) in ((d0fp, d0fn, 0), (d5fp, d5fn, 5)):
            s = d[k][r]
            tgtfp[k] = 0.5 * ((D(g, 0, s["fn_ml"]) - D(g, s["fp_ml"], s["fn_ml"])) + (1.0 - D(g, s["fp_ml"], 0)))
            tgtfn[k] = 0.5 * ((D(g, s["fp_ml"], 0) - D(g, s["fp_ml"], s["fn_ml"])) + (1.0 - D(g, 0, s["fn_ml"])))
    res[f"a_{arm}"] = {"gap_from_excess_FP": pm(fpS), "gap_from_excess_FN": pm(fnS),
                       "one_minus_D0_from_FP": pm(d0fp), "one_minus_D0_from_FN": pm(d0fn),
                       "one_minus_D5_from_FP": pm(d5fp), "one_minus_D5_from_FN": pm(d5fn),
                       "patient_mean_FP0_FN0_ml": [pm({k: d[k][0]["fp_ml"] for k in keys}), pm({k: d[k][0]["fn_ml"] for k in keys})],
                       "patient_mean_FP5_FN5_ml": [pm({k: d[k][5]["fp_ml"] for k in keys}), pm({k: d[k][5]["fn_ml"] for k in keys})],
                       "oracle_patient_mean_FP5_FN5_ml": [pm({k: o[k][5]["fp_ml"] for k in keys}), pm({k: o[k][5]["fn_ml"] for k in keys})],
                       "median_scan_FP0_FN0_ml": [sorted(d[k][0]["fp_ml"] for k in keys)[len(keys) // 2],
                                                  sorted(d[k][0]["fn_ml"] for k in keys)[len(keys) // 2]]}

# (b) persistent damage vs unrepaired original error
for arm in ("flat", "N3"):
    d, o = six[arm][0], six["oracle"][0]
    rows, _, _ = build(arm)
    ev_fp, ev_fn = collections.defaultdict(float), collections.defaultdict(float)
    for r in rows:
        if r["pos"] and not r["no_stroke"]:
            ev_fp[(r["scan"], r["style"])] += r["fp_add"]
            ev_fn[(r["scan"], r["style"])] += r["tp_lost"]
    traj = {(t["scan_id"], t["style"]): t for t in read_jsonl(ROLL / ARMS[arm] / "trajectories.jsonl")}
    out = {}
    for mode in ("max_fp", "max_fn", "event_ratio"):
        phiP, phiO = {}, {}
        for k in keys:
            g = gts[k]
            fp5, fn5 = d[k][5]["fp_ml"], d[k][5]["fn_ml"]
            fpo, fno = o[k][5]["fp_ml"], o[k][5]["fn_ml"]
            p = float(traj[k]["cumulative_damage"]["damage_persistent_d5_ml"])
            lo, hi = max(0.0, p - fn5), min(p, fp5)
            if mode == "max_fp":
                pfp = hi
            elif mode == "max_fn":
                pfp = lo
            else:
                e = ev_fp[k] + ev_fn[k]
                pfp = min(max(p * (ev_fp[k] / e if e > 0 else 0.5), lo), hi)
            pfn = p - pfp
            d_f = D(g, fp5, fn5)
            d_f_minus = D(g, fp5 - pfp, fn5 - pfn)
            d_o = D(g, fpo, fno)
            d_o_plus = D(g, fpo + pfp, min(fno + pfn, g))
            phiP[k] = 0.5 * ((d_f_minus - d_f) + (d_o - d_o_plus))
            phiO[k] = 0.5 * ((d_o_plus - d_f) + (d_o - d_f_minus))
        out[mode] = {"persistent_damage_share_pts": pm(phiP), "unrepaired_original_error_pts": pm(phiO)}
        if mode == "event_ratio":
            pP = patient_mean(phiP, pat)[1]
            pO = patient_mean(phiO, pat)[1]
            gt_p = patient_mean({k: gts[k] for k in keys}, pat)[1]
            order = sorted(pP, key=lambda p: -(pP[p] + pO[p]))
            out["worst12_patients"] = [{"patient": p, "gap": pP[p] + pO[p], "damage_part": pP[p], "unrepaired_part": pO[p],
                                        "mean_scan_gt_ml": gt_p[p]} for p in order[:12]]
            out["patients_damage_part_larger"] = sum(1 for p in pP if pP[p] > pO[p])
            out["patients"] = len(pP)
            top10 = order[:10]
            out["top10_damage_part_sum_share"] = sum(pP[p] for p in top10) / sum(pP[p] + pO[p] for p in top10)
    res[f"b_{arm}"] = out

# (c) gap by GT burden of the scan
bins = ((0, 5, "<5 mL"), (5, 50, "5-50 mL"), (50, 200, "50-200 mL"), (200, 1e9, ">=200 mL"))
d, o = six["flat"][0], six["oracle"][0]
scan_gt = {}
for k in keys:
    scan_gt[k[0]] = gts[k]
tab = {}
for lo, hi, name in bins:
    sel = {k for k in keys if lo <= scan_gt[k[0]] < hi}
    if not sel:
        continue
    contrib = {k: (o[k][5]["dice"] - d[k][5]["dice"]) if k in sel else 0.0 for k in keys}
    tab[name] = {"scans": len({k[0] for k in sel}), "patients": len({pat[k] for k in sel}),
                 "flat_D0": pm({k: d[k][0]["dice"] for k in sel}), "flat_D5": pm({k: d[k][5]["dice"] for k in sel}),
                 "oracle_D5": pm({k: o[k][5]["dice"] for k in sel}),
                 "contribution_to_overall_gap_pts": pm(contrib),
                 "fn5_share_of_error": sum(d[k][5]["fn_ml"] for k in sel) / sum(d[k][5]["fn_ml"] + d[k][5]["fp_ml"] for k in sel)}
res["c_gap_by_gt_burden"] = tab
res["c_scan_gt_ml_quartiles"] = [sorted(scan_gt.values())[int(q * (len(scan_gt) - 1))] for q in (0, 0.25, 0.5, 0.75, 1.0)]

# (d) lesion-level detection
lesion = {}
for arm in ("flat", "N3", "oracle"):
    cnt = collections.Counter()
    for t in read_jsonl(ROLL / ARMS[arm] / "trajectories.jsonl"):
        if not t["summary"]["gt_positive"]:
            continue
        les = t["lesions"]
        for L in les["lesions"]:
            v = float(L["volume_ml"])
            b = "<0.5" if v < 0.5 else ("0.5-10" if v < 10 else ">=10")
            m = L["matched"]
            cnt[(b, "n")] += 1
            cnt[(b, "matched0")] += m[0]
            cnt[(b, "matched5")] += m[5]
            cnt[(b, "lost_from_d0_to_d5")] += (m[0] and not m[5])
            cnt[(b, "gained_d0_to_d5")] += (not m[0] and m[5])
            cnt[(b, "erasure_event")] += bool(L.get("initial_lesion_erasure"))
            cnt[(b, "erasure_persistent_d5")] += bool(L.get("initial_lesion_erasure_persistent_d5"))
    lesion[arm] = {b: {f: cnt[(b, f)] for f in ("n", "matched0", "matched5", "lost_from_d0_to_d5", "gained_d0_to_d5",
                                               "erasure_event", "erasure_persistent_d5")} for b in ("<0.5", "0.5-10", ">=10")}
res["d_lesions_three_styles_trajectory_count"] = lesion

# (e) model-free round trip of the referred target (trajectory states and list)
rt = {}
for lst in ("samestate-trajectory", "samestate-list"):
    rr = read_jsonl(VAL1 / lst / "model-free" / "roundtrip.jsonl")
    agg = collections.defaultdict(list)
    for r in rr:
        v = float(r["target_ml"])
        b = "<0.1" if v < 0.1 else ("0.1-0.5" if v < 0.5 else ("0.5-10" if v < 10 else ">=10"))
        agg[b].append((float(r["roundtrip_dice"]) if r.get("roundtrip_dice") is not None else 0.0, bool(r.get("target_survives"))))
    rt[lst] = {b: {"n": len(x), "mean_roundtrip_dice": sum(a for a, _ in x) / len(x), "survive_rate": sum(s for _, s in x) / len(x)}
               for b, x in sorted(agg.items())}
res["e_roundtrip"] = rt
# flat's own recovery of tiny targets in the rollout
tiny = [r for r in rows_f if r["pos"] and not r["no_stroke"] and r["V"] < 0.1]
small = [r for r in rows_f if r["pos"] and not r["no_stroke"] and 0.1 <= r["V"] < 0.5]
res["e_rollout_small_targets"] = {
    "lt0.1": {"n": len(tiny), "event_mean_recovery": sum(r["R"] / r["V"] for r in tiny) / max(1, len(tiny)),
              "first_order_target_pts": pm({k: sum(r["S_target"] for r in tiny if (r["scan"], r["style"]) == k) for k in keys}),
              "first_order_total_pts": pm({k: sum(r["shortfall"] for r in tiny if (r["scan"], r["style"]) == k) for k in keys})},
    "0.1-0.5": {"n": len(small), "event_mean_recovery": sum(r["R"] / r["V"] for r in small) / max(1, len(small)),
                "first_order_target_pts": pm({k: sum(r["S_target"] for r in small if (r["scan"], r["style"]) == k) for k in keys}),
                "first_order_total_pts": pm({k: sum(r["shortfall"] for r in small if (r["scan"], r["style"]) == k) for k in keys})}}

# (f) large FP removals at round 0 and isolated-FP REMOVE events
t0_rem = [r for r in rows_f if r["pos"] and not r["no_stroke"] and r["t"] == 0 and r["sign"] == "-"]
big = [r for r in t0_rem if r["V"] >= 10]
res["f_round0_remove_ge10"] = {"n_trajectories": len(big), "scans": len({r["scan"] for r in big}),
                               "patients": len({r["patient"] for r in big}),
                               "median_V_ml": sorted(r["V"] for r in big)[len(big) // 2] if big else None,
                               "vol_weighted_recovery": sum(r["R"] for r in big) / sum(r["V"] for r in big) if big else None,
                               "D1_pts_shortfall": pm({k: sum(r["shortfall"] for r in big if (r["scan"], r["style"]) == k) for k in keys})}
ev = [e for e in read_jsonl(VAL1 / "samestate-trajectory" / "N1_STATE-s3407" / "events.jsonl")
      if e.get("status") == "ok" and e["sign"] == "-" and e.get("touched_predicted_components")]
iso = [e for e in ev if not e.get("touched_component_has_preserve")]
mix = [e for e in ev if e.get("touched_component_has_preserve")]


def szs(es):
    c = collections.Counter("<0.5" if float(e["target_volume_ml"]) < 0.5 else ("0.5-10" if float(e["target_volume_ml"]) < 10 else ">=10") for e in es)
    rec = {b: [float(e["target_recovery_ml"]) / float(e["target_volume_ml"]) for e in es
               if ("<0.5" if float(e["target_volume_ml"]) < 0.5 else ("0.5-10" if float(e["target_volume_ml"]) < 10 else ">=10")) == b]
           for b in c}
    return {b: {"n": c[b], "event_mean_recovery": sum(rec[b]) / len(rec[b])} for b in sorted(c)}
res["f_remove_isolated_vs_attached"] = {"isolated_fp_component": szs(iso), "component_contains_true_lesion": szs(mix)}

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
for k, v in res.items():
    print("=====", k)
    if isinstance(v, dict):
        for kk, vv in v.items():
            print("   ", kk, json.dumps(vv) if not isinstance(vv, float) else round(vv, 4))
    else:
        print("   ", v)
