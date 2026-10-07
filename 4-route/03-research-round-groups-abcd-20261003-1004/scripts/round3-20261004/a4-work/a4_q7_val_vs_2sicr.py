"""VAL-only comparison of SIRB v1 flat/N3 with 2S-ICR on the scans that are in BOTH the SIRB VAL (99) and the 2S-ICR
fold0/fold1 held-out VAL lists (= segmentation-base folds 0/1).  Neither model saw these patients in training.
SIRB curve is taken for the same style the 2S-ICR case used.  Different start states (SIRB: base OOF; 2S-ICR: its own
automatic stage), so this is a system-level comparison, descriptive."""
import collections
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import DEV, ROLL, ARMS, QUICK, six_state, mean, nauc, paired_bootstrap, dump, short

sirb = {arm: six_state(ROLL / ARMS[arm] / "six_state.csv") for arm in ("flat", "N3", "oracle")}
quick = {name: six_state(path) for name, path in QUICK.items()}
quick_style = {k[0]: k[1] for k in quick["STATIC"][0]}
rows = []
style_match = collections.Counter()
for f in (0, 1):
    for p in glob.glob(str(DEV / f"baseline-2sicr-fold{f}-val-20261003" / "cases" / "*.json")):
        c = json.load(open(p, encoding="utf-8"))
        scan = c["case_id"]
        st = c["strategy"]
        key = (scan, st)
        if key not in sirb["flat"][0]:
            continue  # not a SIRB VAL scan
        if not c["states"][0]["metric_eligible"]:
            continue
        style_match[st == quick_style.get(scan)] += 1
        s2 = [s["dice"] for s in c["states"]]
        r = {"fold": f, "scan": scan, "patient": sirb["flat"][1][key], "style": st, "2sicr": s2}
        for arm in ("flat", "N3", "oracle"):
            d = sirb[arm][0][key]
            r[arm] = [d[i]["dice"] for i in range(6)]
        rows.append(r)

by_pat = collections.defaultdict(list)
for r in rows:
    by_pat[r["patient"]].append(r)
pc = {m: {p: [mean(x[m][i] for x in rs) for i in range(6)] for p, rs in by_pat.items()} for m in ("2sicr", "flat", "N3", "oracle")}
pats = sorted(by_pat)
out = {"scans": len(rows), "patients": len(pats), "folds": dict(collections.Counter(r["fold"] for r in rows)),
       "style_same_as_quickval_roster": dict(style_match),
       "curves": {m: [mean(pc[m][p][i] for p in pats) for i in range(6)] for m in pc},
       "nauc": {m: mean(nauc(pc[m][p]) for p in pats) for m in pc}}
cmp = {}
for i in range(6):
    dd = {p: pc["flat"][p][i] - pc["2sicr"][p][i] for p in pats}
    m, lo, hi = paired_bootstrap(dd)
    cmp[f"D{i}"] = {"mean": m, "ci": [lo, hi], "flat_higher": sum(v > 1e-9 for v in dd.values()),
                    "2sicr_higher": sum(v < -1e-9 for v in dd.values())}
out["flat_minus_2sicr"] = cmp
out["increments"] = {m: [mean(pc[m][p][i] - pc[m][p][i - 1] for p in pats) for i in range(1, 6)] for m in pc}
out["gain"] = {m: mean(pc[m][p][5] - pc[m][p][0] for p in pats) for m in pc}
dump(out, Path(__file__).with_suffix(".json"))
print("scans", out["scans"], "patients", out["patients"], out["folds"], "style==quickVAL roster", out["style_same_as_quickval_roster"])
for m in pc:
    print(f"{m:7s}", " ".join(f"{x:.4f}" for x in out["curves"][m]), f"nAUC {out['nauc'][m]:.4f}", "incr",
          " ".join(f"{x:+.4f}" for x in out["increments"][m]), f"gain {out['gain'][m]:+.4f}")
for i in range(6):
    c = cmp[f"D{i}"]
    print(f"  D{i} flat-2S {c['mean']:+.4f} CI [{c['ci'][0]:+.4f}, {c['ci'][1]:+.4f}] flat higher {c['flat_higher']} 2S higher {c['2sicr_higher']}")
