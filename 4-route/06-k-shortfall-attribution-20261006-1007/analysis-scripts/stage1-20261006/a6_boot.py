"""Paired patient bootstrap (10,000 draws, seed 3407) of D5 and of the ADD / REMOVE contributions, K vs v1 flat."""
import csv, json, os, collections
import numpy as np
ROOT = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer"
B1 = os.path.join(ROOT, "eval-sirb-batch1-val-20260925/rollout")
D = {"K1": os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_FULL-R1-20261006"),
     "K2": os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006"),
     "K2flip": os.path.join(ROOT, "eval-sirb-v3-quickval-flip-INTENT_REFRESH-R1-20261006"),
     "v1flat": os.path.join(B1, "N1_STATE-s3407")}
def six(p):
    c, pat = collections.defaultdict(lambda: [None]*6), {}
    for r in csv.DictReader(open(p, newline="")):
        if r["gt_positive"] == "True":
            c[(r["scan_id"], r["style"])][int(r["round"])] = float(r["dice"]); pat[r["scan_id"]] = r["patient_id"]
    return c, pat
k2, pat = six(os.path.join(D["K2"], "six_state.csv"))
assigned = {s: st for (s, st) in k2}
def per_patient(name):
    c, _ = six(os.path.join(D[name], "six_state.csv"))
    tr = {}
    for l in open(os.path.join(D[name], "transitions.jsonl")):
        r = json.loads(l); tr[(r["scan_id"], r["style"], r["transition"])] = r
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for s, st in assigned.items():
        d = c[(s, st)]
        add = sum(d[t+1]-d[t] for t in range(5) if tr[(s, st, t)].get("sign") == "+")
        rem = sum(d[t+1]-d[t] for t in range(5) if tr[(s, st, t)].get("sign") == "-")
        p = pat[s]
        out[p]["d5"].append(d[5]); out[p]["add"].append(add); out[p]["rem"].append(rem)
    return {p: {k: float(np.mean(v)) for k, v in m.items()} for p, m in out.items()}
P = {n: per_patient(n) for n in D}
pts = sorted(P["K2"])
rng = np.random.default_rng(3407)
idx = rng.integers(0, len(pts), size=(10000, len(pts)))
for a in ("K1", "K2", "K2flip"):
    for k in ("d5", "add", "rem"):
        diff = np.array([P[a][p][k] - P["v1flat"][p][k] for p in pts])
        boot = diff[idx].mean(axis=1)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        print("%-6s - v1flat  %-3s  mean %+.4f  95%% [%+.4f, %+.4f]  (%d patients)" % (a, k, diff.mean(), lo, hi, len(pts)))
