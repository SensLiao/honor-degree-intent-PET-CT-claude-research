"""Read-only analysis of saved VAL result files (no voxels, no servers).

Part 1: SIRB systems on the quick-VAL protocol (one frozen style per scan, the style of the SIRB VAL roster).
Part 2: Baseline fold VALs vs SIRB on the scans both evaluated.
"""
import csv, json, glob, os, collections, statistics

ROOT = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer"

def read_six(path):
    """scan -> style -> [d0..d5] (positive scans only), plus patient of scan."""
    out = collections.defaultdict(dict)
    pat = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["gt_positive"] != "True":
                continue
            s, st, k = r["scan_id"], r["style"], int(r["round"])
            pat[s] = r["patient_id"]
            out[s].setdefault(st, [None] * 6)[k] = float(r["dice"]) if r["dice"] not in ("", "None") else None
    return out, pat

def nauc(c):
    return (0.5 * c[0] + c[1] + c[2] + c[3] + c[4] + 0.5 * c[5]) / 5.0

def patient_mean(curves, pat):
    """curves: scan -> [d0..d5]; scan mean within patient, then patient mean."""
    by_p = collections.defaultdict(list)
    for s, c in curves.items():
        by_p[pat[s]].append(c)
    pm = []
    for p, cs in by_p.items():
        pm.append([sum(c[k] for c in cs) / len(cs) for k in range(6)])
    mean = [sum(c[k] for c in pm) / len(pm) for k in range(6)]
    return mean, len(curves), len(pm)

def fmt(mean, ns, npat):
    return "D0 %.4f  D1 %.4f  D2 %.4f  D3 %.4f  D4 %.4f  D5 %.4f  nAUC %.4f  (%d scans/%d pts)" % (
        *mean, nauc(mean), ns, npat)

# ---------- SIRB quick VAL style per scan (from K2) ----------
k2, pat = read_six(os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006/six_state.csv"))
assigned = {s: list(v.keys())[0] for s, v in k2.items()}
assert all(len(v) == 1 for v in k2.values())

systems = collections.OrderedDict()
def single(name, folder):
    d, p = read_six(os.path.join(ROOT, folder, "six_state.csv"))
    pat.update(p)
    for s, v in d.items():
        assert list(v.keys()) == [assigned[s]], (folder, s, v.keys(), assigned[s])
    systems[name] = {s: list(v.values())[0] for s, v in d.items()}

def batch1(name, sub):
    d, p = read_six(os.path.join(ROOT, "eval-sirb-batch1-val-20260925/rollout", sub, "six_state.csv"))
    pat.update(p)
    systems[name] = {s: d[s][assigned[s]] for s in assigned}
    return d

single("K2 INTENT_REFRESH 40k scratch", "eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006")
single("K1 INTENT_FULL 40k scratch", "eval-sirb-v3-quickval-INTENT_FULL-R1-20261006")
single("K2 + flip", "eval-sirb-v3-quickval-flip-INTENT_REFRESH-R1-20261006")
v1flat_all = batch1("v1 flat N1_STATE 40k scratch", "N1_STATE-s3407")
v1n3_all = batch1("v1 N3 40k scratch", "N3-s3407")
oracle_all = batch1("oracle (ideal repair, upper ref)", "oracle")
noop_all = batch1("noop (no edit)", "noop")
for name, folder in [("STATIC = v1flat +8k cont.", "eval-sirb-v2-quickval-N1_STATE_STATIC-R1-20261003"),
                     ("INDUCED = v1flat +8k cont.", "eval-sirb-v2-quickval-N1_STATE_INDUCED-R1-20261003"),
                     ("SPATIAL = v1flat +8k cont.", "eval-sirb-v2-quickval-N1_STATE_SPATIAL-R1-20261004"),
                     ("N4_STATIC = v1N3 +8k cont.", "eval-sirb-v2-quickval-N4_STATIC-R1-20261003"),
                     ("N3_ES = v1N3 +8k cont.", "eval-sirb-v2-quickval-N3_ES-R1-20261004"),
                     ("INDUCED + flip", "eval-sirb-v3-quickval-flip-N1_STATE_INDUCED-R1-20261005"),
                     ("INDUCED + groupA", "eval-sirb-v3-intent-quickval-N1_STATE_INDUCED-R1-20261005"),
                     ("weightavg STATIC/INDUCED", "eval-sirb-v3-quickval-weightavg-N1_STATE-STATIC-INDUCED-R1-20261005")]:
    if os.path.exists(os.path.join(ROOT, folder, "six_state.csv")):
        single(name, folder)

print("PART 1  SIRB VAL, quick-VAL protocol (one frozen style per scan), patient mean")
for name, curves in systems.items():
    print("%-34s %s" % (name, fmt(*patient_mean(curves, pat))))

# three-style average of v1 flat for reference
def all_styles_mean(d):
    curves = {}
    by_p = collections.defaultdict(list)
    for s, v in d.items():
        for st, c in v.items():
            by_p[pat[s]].append(c)
    pm = [[sum(c[k] for c in cs) / len(cs) for k in range(6)] for cs in by_p.values()]
    return [sum(c[k] for c in pm) / len(pm) for k in range(6)], sum(len(v) for v in d.values()), len(pm)
print("%-34s %s" % ("v1 flat, all 3 styles (batch1)", fmt(*all_styles_mean(v1flat_all))))
print("%-34s %s" % ("oracle, all 3 styles (batch1)", fmt(*all_styles_mean(oracle_all))))

# style mix
print("\nassigned style mix on SIRB VAL positive scans:", collections.Counter(assigned.values()))

# ---------- Part 2: baselines on shared scans ----------
def read_baseline(folder):
    out = {}
    for f in glob.glob(os.path.join(ROOT, folder, "cases", "*.json")):
        x = json.load(open(f))
        if x.get("partition") != "VAL":
            continue
        ds = [s["dice"] for s in x["states"]]
        if any(v is None for v in ds):
            continue           # empty GT
        out[x["case_id"]] = (x["strategy"], ds)
    return out

base = collections.OrderedDict()
for name, folder in [("2S-ICR fold0", "baseline-2sicr-fold0-val-20261003"),
                     ("2S-ICR fold1", "baseline-2sicr-fold1-val-20261003"),
                     ("2S-ICR fold2", "baseline-2sicr-fold2-val-20261004"),
                     ("UAM fold0", "baseline-uam-fold0-val-20261005"),
                     ("UAM fold1", "baseline-uam-fold1-val-20261005")]:
    base[name] = read_baseline(folder)

def pid(scan):
    return "_".join(scan.split("_")[:2])

print("\nPART 2  baseline fold VAL vs SIRB on the SAME scans (positive GT, both evaluated)")
allpairs = collections.defaultdict(dict)   # system -> scan -> curve
for name, b in base.items():
    own = {s: c for s, (st, c) in b.items()}
    for s in own:
        pat.setdefault(s, pid(s))
    print("\n== %s: own VAL %s" % (name, fmt(*patient_mean(own, pat))))
    shared = sorted(set(b) & set(assigned))
    same_style = [s for s in shared if b[s][0] == assigned[s]]
    print("   shared with SIRB VAL: %d scans / %d pts; same style as SIRB quick VAL: %d" % (
        len(shared), len({pat[s] for s in shared}), len(same_style)))
    if not shared:
        continue
    rows = {
        name + " (own start)": {s: b[s][1] for s in shared},
        "v1 flat, baseline's style": {s: v1flat_all[s][b[s][0]] for s in shared},
        "v1 flat, SIRB style": {s: systems["v1 flat N1_STATE 40k scratch"][s] for s in shared},
        "K2, SIRB style": {s: systems["K2 INTENT_REFRESH 40k scratch"][s] for s in shared},
        "K1, SIRB style": {s: systems["K1 INTENT_FULL 40k scratch"][s] for s in shared},
        "INDUCED+flip, SIRB style": {s: systems["INDUCED + flip"][s] for s in shared},
        "oracle, baseline's style": {s: oracle_all[s][b[s][0]] for s in shared},
    }
    for r, curves in rows.items():
        print("   %-28s %s" % (r, fmt(*patient_mean(curves, pat))))
        key = r.replace(name + " ", "baseline ")
        for s, c in curves.items():
            allpairs[(name.split()[0], key)][s] = c

# pooled over folds of the same method (each scan appears in exactly one fold VAL)
print("\nPOOLED over folds (each shared scan once)")
for method in ["2S-ICR", "UAM"]:
    print("== %s" % method)
    for (m, key), curves in allpairs.items():
        if m == method:
            print("   %-28s %s" % (key, fmt(*patient_mean(curves, pat))))
