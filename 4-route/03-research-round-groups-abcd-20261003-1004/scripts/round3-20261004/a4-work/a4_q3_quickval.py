"""Quick VAL (one frozen style per scan, 99 VAL scans): patient-level paired comparison of the three +8k continuations
(N1_STATE_STATIC, N1_STATE_INDUCED, N4_STATIC) and the v1 parents cut to the same (scan, style) roster.
Bootstrap: patients resampled, 10,000, seed 3407.  VAL only."""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import (QUICK, ROLL, ARMS, six_state, patient_curves, nauc, mean, summary_stats, paired_bootstrap,
                       short, dump, read_jsonl, quantile)

EPS = 1e-9
tabs, curves = {}, {}
keysets = {}
for name, path in QUICK.items():
    d, pat, pos = six_state(path)
    tabs[name] = (d, pat, pos)
    curves[name] = patient_curves(d, pat, pos)
    keysets[name] = set(d)
assert keysets["STATIC"] == keysets["INDUCED"] == keysets["N4_STATIC"], "rosters differ"
roster = keysets["STATIC"]
for v1, arm in (("v1_flat", "flat"), ("v1_N3", "N3")):
    d, pat, pos = six_state(ROLL / ARMS[arm] / "six_state.csv", keys=roster)
    assert set(d) == roster
    tabs[v1] = (d, pat, pos)
    curves[v1] = patient_curves(d, pat, pos)

pats = sorted(curves["STATIC"])
for k in curves:
    assert set(curves[k]) == set(pats), k
# identical starts
d0max = max(abs(curves[a][p][0] - curves["STATIC"][p][0]) for a in curves for p in pats)

out = {"patients": len(pats), "scans_in_roster": len({k[0] for k in roster}),
       "positive_scans": len({k[0] for k in roster if tabs["STATIC"][2][k]}), "max_D0_difference": d0max,
       "style_counts": dict(collections.Counter(k[1] for k in roster))}
out["curves"] = {a: [mean(c[p][i] for p in pats) for i in range(6)] for a, c in curves.items()}
out["nauc"] = {a: mean(nauc(c[p]) for p in pats) for a, c in curves.items()}

def compare(a, b):
    dd5 = {p: curves[a][p][5] - curves[b][p][5] for p in pats}
    dna = {p: nauc(curves[a][p]) - nauc(curves[b][p]) for p in pats}
    dd1 = {p: curves[a][p][1] - curves[b][p][1] for p in pats}
    m5, lo5, hi5 = paired_bootstrap(dd5)
    mn, lon, hin = paired_bootstrap(dna)
    m1, lo1, hi1 = paired_bootstrap(dd1)
    vals = list(dd5.values())
    return {"D5": {"mean": m5, "ci": [lo5, hi5], **{k: v for k, v in summary_stats(vals).items() if k != "mean"},
                   "better": sum(v > EPS for v in vals), "worse": sum(v < -EPS for v in vals),
                   "tie": sum(abs(v) <= EPS for v in vals),
                   "better_gt_0.01": sum(v > 0.01 for v in vals), "worse_gt_0.01": sum(v < -0.01 for v in vals),
                   "better_gt_0.05": sum(v > 0.05 for v in vals), "worse_gt_0.05": sum(v < -0.05 for v in vals)},
            "nAUC": {"mean": mn, "ci": [lon, hin], "better": sum(v > EPS for v in dna.values()),
                     "worse": sum(v < -EPS for v in dna.values())},
            "D1": {"mean": m1, "ci": [lo1, hi1], "better": sum(v > EPS for v in dd1.values()),
                   "worse": sum(v < -EPS for v in dd1.values()), "tie": sum(abs(v) <= EPS for v in dd1.values())},
            "largest_gains": sorted(((short(p), round(v, 4)) for p, v in dd5.items()), key=lambda x: -x[1])[:5],
            "largest_losses": sorted(((short(p), round(v, 4)) for p, v in dd5.items()), key=lambda x: x[1])[:5]}

pairs = [("INDUCED", "STATIC"), ("STATIC", "v1_flat"), ("INDUCED", "v1_flat"), ("N4_STATIC", "v1_N3"),
         ("STATIC", "N4_STATIC"), ("v1_flat", "v1_N3")]
out["comparisons"] = {f"{a} - {b}": compare(a, b) for a, b in pairs}

# inferred sign per round from the six-state volumes (executor only adds or only removes)
def sign_ledger(name):
    d, pat, pos = tabs[name]
    contrib = collections.defaultdict(lambda: collections.defaultdict(float))
    cnt = collections.Counter(); worse = collections.Counter()
    for k, r in d.items():
        if not pos[k]:
            continue
        for t in range(5):
            a, b = r[t], r[t + 1]
            dfp, dfn = b["fp_ml"] - a["fp_ml"], b["fn_ml"] - a["fn_ml"]
            if dfp > 1e-9 or dfn < -1e-9:
                s = "ADD"
            elif dfp < -1e-9 or dfn > 1e-9:
                s = "REMOVE"
            else:
                s = "noedit"
            g = b["dice"] - a["dice"]
            grp = "r1" if t == 0 else "r2-5"
            contrib[k][f"{s}|{grp}"] += g
            cnt[f"{s}|{grp}"] += 1
            if g < -EPS:
                worse[f"{s}|{grp}"] += 1
    groups = sorted({g for k in contrib for g in contrib[k]})
    by_scan = collections.defaultdict(list)
    for k in contrib:
        by_scan[k[0]].append(k)
    pp = collections.defaultdict(lambda: collections.defaultdict(list))
    for scan, ks in by_scan.items():
        p = pat[ks[0]]
        for g in groups:
            pp[p][g].append(mean(contrib[k].get(g, 0.0) for k in ks))
    pm = {g: mean(mean(pp[p][g]) for p in pp) for g in groups}
    fpd = collections.defaultdict(list)
    for k, r in d.items():
        if pos[k]:
            fpd[pat[k]].append(r[5]["fp_ml"] - r[0]["fp_ml"])
    return {"contrib": pm, "counts": dict(cnt), "worse": dict(worse),
            "fp_change_d5_minus_d0_patient_mean_ml": mean(mean(v) for v in fpd.values())}
out["sign_ledger"] = {name: sign_ledger(name) for name in ("STATIC", "INDUCED", "N4_STATIC", "v1_flat", "v1_N3")}

# check: inferred signs agree with the v1 transitions on the roster
tr = {(r["scan_id"], r["style"], int(r["transition"])): r for r in read_jsonl(ROLL / ARMS["flat"] / "transitions.jsonl")}
agree = disagree = 0
d, pat, pos = tabs["v1_flat"]
for k, r in d.items():
    if not pos[k]:
        continue
    for t in range(5):
        a, b = r[t], r[t + 1]
        dfp, dfn = b["fp_ml"] - a["fp_ml"], b["fn_ml"] - a["fn_ml"]
        s = "+" if (dfp > 1e-9 or dfn < -1e-9) else ("-" if (dfp < -1e-9 or dfn > 1e-9) else None)
        x = tr[(k[0], k[1], t)]
        if s is None:
            continue
        if s == x["sign"]:
            agree += 1
        else:
            disagree += 1
out["sign_inference_check_v1_flat"] = {"agree": agree, "disagree": disagree}

# does the INDUCED - STATIC difference relate to lesion burden or start quality?
lesion = {}
for t in read_jsonl(ROLL / ARMS["flat"] / "trajectories.jsonl"):
    les = t.get("lesions") or {}
    lesion[t["scan_id"]] = sum(float(x["volume_ml"]) for x in les.get("lesions", []))
dS, patS, posS = tabs["STATIC"]
pat_gt = collections.defaultdict(list)
for k in dS:
    if posS[k]:
        pat_gt[patS[k]].append(lesion[k[0]])
gtm = {p: mean(v) for p, v in pat_gt.items()}
diff = {p: curves["INDUCED"][p][5] - curves["STATIC"][p][5] for p in pats}
small = [p for p in pats if gtm[p] < 5.0]
large = [p for p in pats if gtm[p] >= 5.0]
out["INDUCED_minus_STATIC_by_burden"] = {
    "small_lt5ml": {"patients": len(small), "mean_D5_diff": mean(diff[p] for p in small)},
    "large_ge5ml": {"patients": len(large), "mean_D5_diff": mean(diff[p] for p in large)}}
d0 = {p: curves["STATIC"][p][0] for p in pats}
lo = [p for p in pats if d0[p] < quantile(list(d0.values()), 0.5)]
hi = [p for p in pats if p not in lo]
out["INDUCED_minus_STATIC_by_D0"] = {"low_D0": {"patients": len(lo), "mean_D5_diff": mean(diff[p] for p in lo)},
                                     "high_D0": {"patients": len(hi), "mean_D5_diff": mean(diff[p] for p in hi)}}

dump(out, Path(__file__).with_suffix(".json"))
print("patients", out["patients"], "roster scans", out["scans_in_roster"], "pos", out["positive_scans"],
      "maxD0diff", out["max_D0_difference"], out["style_counts"])
for a in curves:
    print(f"{a:10s}", " ".join(f"{x:.4f}" for x in out["curves"][a]), f"nAUC {out['nauc'][a]:.4f}")
for name, c in out["comparisons"].items():
    print("==", name)
    print("   D5 mean %+.4f CI [%+.4f, %+.4f] median %+.4f q1 %+.4f q3 %+.4f better/worse/tie %d/%d/%d  >0.01 %d/%d  >0.05 %d/%d" % (
        c["D5"]["mean"], c["D5"]["ci"][0], c["D5"]["ci"][1], c["D5"]["median"], c["D5"]["q1"], c["D5"]["q3"],
        c["D5"]["better"], c["D5"]["worse"], c["D5"]["tie"], c["D5"]["better_gt_0.01"], c["D5"]["worse_gt_0.01"],
        c["D5"]["better_gt_0.05"], c["D5"]["worse_gt_0.05"]))
    print("   nAUC mean %+.4f CI [%+.4f, %+.4f] better/worse %d/%d" % (
        c["nAUC"]["mean"], c["nAUC"]["ci"][0], c["nAUC"]["ci"][1], c["nAUC"]["better"], c["nAUC"]["worse"]))
    print("   D1 mean %+.4f CI [%+.4f, %+.4f] better/worse/tie %d/%d/%d" % (
        c["D1"]["mean"], c["D1"]["ci"][0], c["D1"]["ci"][1], c["D1"]["better"], c["D1"]["worse"], c["D1"]["tie"]))
    print("   gains", c["largest_gains"], "losses", c["largest_losses"])
for name, s in out["sign_ledger"].items():
    print("ledger", name, {k: round(v, 4) for k, v in sorted(s["contrib"].items())}, s["counts"], "worse", s["worse"],
          "FP change mL", round(s["fp_change_d5_minus_d0_patient_mean_ml"], 2))
print("sign inference check", out["sign_inference_check_v1_flat"])
print("by burden", out["INDUCED_minus_STATIC_by_burden"], "by D0", out["INDUCED_minus_STATIC_by_D0"])
