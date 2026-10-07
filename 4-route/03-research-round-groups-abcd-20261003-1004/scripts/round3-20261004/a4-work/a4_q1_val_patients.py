"""VAL (three-style full VAL, v1 40k): per-patient D0..D5 distribution, worst patients, per-round, per-style.
Read-only on records/development_results_transfer/eval-sirb-batch1-val-20260925."""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import (ROLL, ARMS, STYLES, six_state, patient_curves, nauc, mean, summary_stats, read_jsonl,
                       gt_ml, short, dump, quantile)

out = {}
curves = {}
tabs = {}
for arm in ("flat", "N3", "oracle", "noop"):
    d, pat, pos = six_state(ROLL / ARMS[arm] / "six_state.csv")
    tabs[arm] = (d, pat, pos)
    curves[arm] = patient_curves(d, pat, pos)

flat_d, flat_pat, flat_pos = tabs["flat"]
pats = sorted(curves["flat"])
assert set(pats) == set(curves["N3"]) == set(curves["oracle"])

# per-round patient-mean curves
out["curves"] = {arm: [mean(c[i] for c in curves[arm].values()) for i in range(6)] for arm in curves}
out["nauc"] = {arm: mean(nauc(c) for c in curves[arm].values()) for arm in curves}
out["n_patients"] = len(pats)
out["n_positive_scans"] = len({k[0] for k in flat_d if flat_pos[k]})
out["n_scans"] = len({k[0] for k in flat_d})
out["n_patients_all"] = len({flat_pat[k] for k in flat_d})

# distributions (flat and N3)
for arm in ("flat", "N3", "oracle"):
    c = curves[arm]
    out[f"dist_{arm}"] = {
        "D0": summary_stats(v[0] for v in c.values()),
        "D1": summary_stats(v[1] for v in c.values()),
        "D5": summary_stats(v[5] for v in c.values()),
        "D5_minus_D0": summary_stats(v[5] - v[0] for v in c.values()),
        "nAUC": summary_stats(nauc(v) for v in c.values()),
        "n_D5_below_D0": sum(1 for v in c.values() if v[5] < v[0] - 1e-9),
        "n_gain_below_0.05": sum(1 for v in c.values() if v[5] - v[0] < 0.05),
        "n_D5_ge_0.80": sum(1 for v in c.values() if v[5] >= 0.80),
        "n_D5_ge_0.90": sum(1 for v in c.values() if v[5] >= 0.90),
        "n_D5_lt_0.50": sum(1 for v in c.values() if v[5] < 0.50),
    }

# scan-level lesion facts from the flat trajectories (GT does not depend on the model)
lesion = {}
for t in read_jsonl(ROLL / ARMS["flat"] / "trajectories.jsonl"):
    les = t.get("lesions") or {}
    vols = [float(x["volume_ml"]) for x in les.get("lesions", [])]
    lesion[t["scan_id"]] = {"n_lesions": les.get("n_lesions", len(vols)), "gt_ml": sum(vols),
                            "max_lesion_ml": max(vols) if vols else 0.0}

# per patient facts
pos_scans = collections.defaultdict(set)
all_scans = collections.defaultdict(set)
for k in flat_d:
    all_scans[flat_pat[k]].add(k[0])
    if flat_pos[k]:
        pos_scans[flat_pat[k]].add(k[0])

def fp_fn_d5(arm, p):
    d, pat, pos = tabs[arm]
    fps, fns, fp0s, fn0s = [], [], [], []
    for scan in pos_scans[p]:
        vals = [d[(scan, st)] for st in STYLES if (scan, st) in d]
        fps.append(mean(v[5]["fp_ml"] for v in vals)); fns.append(mean(v[5]["fn_ml"] for v in vals))
        fp0s.append(mean(v[0]["fp_ml"] for v in vals)); fn0s.append(mean(v[0]["fn_ml"] for v in vals))
    return mean(fp0s), mean(fn0s), mean(fps), mean(fns)

rows = []
for p in pats:
    c, n3, orc = curves["flat"][p], curves["N3"][p], curves["oracle"][p]
    scans = sorted(pos_scans[p])
    gts = [lesion[s]["gt_ml"] for s in scans]
    nles = [lesion[s]["n_lesions"] for s in scans]
    fp0, fn0, fp5, fn5 = fp_fn_d5("flat", p)
    rows.append({"patient": short(p), "pos_scans": len(scans), "all_scans": len(all_scans[p]),
                 "gt_ml_per_scan_mean": mean(gts), "lesions_per_scan_mean": mean(nles),
                 "max_lesion_ml": max(lesion[s]["max_lesion_ml"] for s in scans),
                 "flat_curve": [round(x, 4) for x in c], "flat_nauc": nauc(c),
                 "n3_d5": n3[5], "oracle_d5": orc[5], "gain": c[5] - c[0],
                 "fp0_ml": fp0, "fn0_ml": fn0, "fp5_ml": fp5, "fn5_ml": fn5,
                 "best_state_round": max(range(6), key=lambda i: c[i]), "best_state": max(c)})
rows.sort(key=lambda r: r["flat_curve"][5])
out["worst10_by_D5"] = rows[:10]
out["best10_by_D5"] = rows[-10:]
out["worst10_by_gain"] = sorted(rows, key=lambda r: r["gain"])[:10]

# characteristics of bottom-quartile vs rest (by flat D5)
n = len(rows)
bottom = rows[: n // 4]
rest = rows[n // 4:]
def describe(group):
    return {"patients": len(group),
            "median_gt_ml_per_scan": quantile([r["gt_ml_per_scan_mean"] for r in group], 0.5),
            "median_lesions_per_scan": quantile([r["lesions_per_scan_mean"] for r in group], 0.5),
            "mean_pos_scans": mean(r["pos_scans"] for r in group),
            "mean_D0": mean(r["flat_curve"][0] for r in group),
            "mean_D5": mean(r["flat_curve"][5] for r in group),
            "mean_oracle_D5": mean(r["oracle_d5"] for r in group),
            "mean_fp5_ml": mean(r["fp5_ml"] for r in group), "mean_fn5_ml": mean(r["fn5_ml"] for r in group),
            "median_fp5_ml": quantile([r["fp5_ml"] for r in group], 0.5),
            "median_fn5_ml": quantile([r["fn5_ml"] for r in group], 0.5)}
out["bottom_quartile_vs_rest"] = {"bottom": describe(bottom), "rest": describe(rest)}

# patients by GT volume per scan tertile
srt = sorted(rows, key=lambda r: r["gt_ml_per_scan_mean"])
terc = [srt[: n // 3], srt[n // 3: 2 * n // 3], srt[2 * n // 3:]]
out["by_gt_volume_tertile"] = [{"gt_ml_range": [round(g[0]["gt_ml_per_scan_mean"], 2), round(g[-1]["gt_ml_per_scan_mean"], 2)],
                                **describe(g)} for g in terc]

# D0 tertile
srt0 = sorted(rows, key=lambda r: r["flat_curve"][0])
terc0 = [srt0[: n // 3], srt0[n // 3: 2 * n // 3], srt0[2 * n // 3:]]
out["by_D0_tertile"] = [{"D0_range": [round(g[0]["flat_curve"][0], 3), round(g[-1]["flat_curve"][0], 3)],
                         "gain_mean": mean(r["gain"] for r in g), **describe(g)} for g in terc0]

# correlation of D0 with gain (Spearman)
def spearman(xs, ys):
    def ranks(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2.0
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = mean(rx), mean(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx); vy = sum((b - my) ** 2 for b in ry)
    return cov / (vx * vy) ** 0.5
out["spearman_D0_vs_gain"] = spearman([r["flat_curve"][0] for r in rows], [r["gain"] for r in rows])
out["spearman_gtml_vs_D5"] = spearman([r["gt_ml_per_scan_mean"] for r in rows], [r["flat_curve"][5] for r in rows])

# flat vs N3 per patient at D5
diff = {r["patient"]: r["flat_curve"][5] - r["n3_d5"] for r in rows}
out["flat_minus_N3_D5"] = {"better": sum(v > 1e-9 for v in diff.values()), "worse": sum(v < -1e-9 for v in diff.values()),
                           "tie": sum(abs(v) <= 1e-9 for v in diff.values()), **summary_stats(diff.values())}

# per style patient means
per_style = {}
for arm in ("flat", "N3", "oracle"):
    d, pat, pos = tabs[arm]
    per_style[arm] = {}
    for st in STYLES:
        keys = {k for k in d if k[1] == st}
        sub = {k: d[k] for k in keys}
        c = patient_curves(sub, pat, pos)
        per_style[arm][st] = {"curve": [mean(v[i] for v in c.values()) for i in range(6)],
                              "nauc": mean(nauc(v) for v in c.values()), "patients": len(c)}
out["per_style"] = per_style

# per-patient spread across styles (flat D5): max-min over styles averaged over scans
spread = []
for scan in {k[0] for k in flat_d if flat_pos[k]}:
    vals = [flat_d[(scan, st)][5]["dice"] for st in STYLES]
    spread.append(max(vals) - min(vals))
out["flat_style_spread_D5_per_scan"] = summary_stats(spread)

# best state anywhere in trajectory vs D5 (patient level, oracle-known stop)
out["flat_best_round_hist"] = dict(collections.Counter(r["best_state_round"] for r in rows))
out["flat_mean_best_state"] = mean(r["best_state"] for r in rows)

dump(out, Path(__file__).with_suffix(".json"))
print("patients", out["n_patients"], "pos scans", out["n_positive_scans"], "scans", out["n_scans"])
for arm in ("flat", "N3", "oracle", "noop"):
    print(arm, " ".join(f"{x:.4f}" for x in out["curves"][arm]), f"nAUC {out['nauc'][arm]:.4f}")
for arm in ("flat", "N3"):
    ds = out[f"dist_{arm}"]
    print(arm, "D5 median/q1/q3", round(ds["D5"]["median"], 4), round(ds["D5"]["q1"], 4), round(ds["D5"]["q3"], 4),
          "min/max", round(ds["D5"]["min"], 4), round(ds["D5"]["max"], 4))
    print(arm, "gain median/q1/q3", round(ds["D5_minus_D0"]["median"], 4), round(ds["D5_minus_D0"]["q1"], 4),
          round(ds["D5_minus_D0"]["q3"], 4), "n D5<D0", ds["n_D5_below_D0"], "n gain<0.05", ds["n_gain_below_0.05"],
          ">=0.8", ds["n_D5_ge_0.80"], ">=0.9", ds["n_D5_ge_0.90"], "<0.5", ds["n_D5_lt_0.50"])
    print(arm, "D0 median/q1/q3", round(ds["D0"]["median"], 4), round(ds["D0"]["q1"], 4), round(ds["D0"]["q3"], 4))
print("worst10 by D5:")
for r in out["worst10_by_D5"]:
    print(" ", r["patient"], r["pos_scans"], round(r["gt_ml_per_scan_mean"], 1), round(r["lesions_per_scan_mean"], 1),
          r["flat_curve"], "N3", round(r["n3_d5"], 3), "orc", round(r["oracle_d5"], 3),
          "FP0/FN0", round(r["fp0_ml"], 1), round(r["fn0_ml"], 1), "FP5/FN5", round(r["fp5_ml"], 1), round(r["fn5_ml"], 1))
print("worst10 by gain:")
for r in out["worst10_by_gain"]:
    print(" ", r["patient"], r["pos_scans"], round(r["gt_ml_per_scan_mean"], 1), r["flat_curve"], round(r["gain"], 3),
          "FP0/FP5", round(r["fp0_ml"], 1), round(r["fp5_ml"], 1))
print("bottom quartile vs rest", out["bottom_quartile_vs_rest"])
print("by GT tertile", [(t["gt_ml_range"], round(t["mean_D0"], 3), round(t["mean_D5"], 3), round(t["mean_oracle_D5"], 3)) for t in out["by_gt_volume_tertile"]])
print("by D0 tertile", [(t["D0_range"], round(t["mean_D0"], 3), round(t["mean_D5"], 3), round(t["gain_mean"], 3)) for t in out["by_D0_tertile"]])
print("spearman D0~gain", round(out["spearman_D0_vs_gain"], 3), "gtml~D5", round(out["spearman_gtml_vs_D5"], 3))
print("flat-N3 D5", out["flat_minus_N3_D5"])
for arm in ("flat", "N3", "oracle"):
    print(arm, {st: round(v["curve"][5], 4) for st, v in out["per_style"][arm].items()})
print("style spread", out["flat_style_spread_D5_per_scan"])
print("best round hist", out["flat_best_round_hist"], "mean best", round(out["flat_mean_best_state"], 4))
