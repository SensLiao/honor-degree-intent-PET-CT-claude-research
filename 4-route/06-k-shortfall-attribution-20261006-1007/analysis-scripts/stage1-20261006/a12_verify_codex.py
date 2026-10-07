"""Check Codex's corrections and new numbers (10-07) on the saved VAL files only."""
import csv, json, os, collections, statistics
import numpy as np

ROOT = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer"
B1 = os.path.join(ROOT, "eval-sirb-batch1-val-20260925/rollout")
DIRS = {"v1flat": os.path.join(B1, "N1_STATE-s3407"), "oracle": os.path.join(B1, "oracle"),
        "K1": os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_FULL-R1-20261006"),
        "K2": os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006"),
        "K2flip": os.path.join(ROOT, "eval-sirb-v3-quickval-flip-INTENT_REFRESH-R1-20261006")}

def jl(p):
    with open(p) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

k2rows = list(csv.DictReader(open(os.path.join(DIRS["K2"], "six_state.csv"), newline="")))
assigned = {r["scan_id"]: r["style"] for r in k2rows}
pat = {r["scan_id"]: r["patient_id"] for r in k2rows}
pos = {r["scan_id"] for r in k2rows if r["gt_positive"] == "True"}

def six(n):
    out = collections.defaultdict(dict)
    for r in csv.DictReader(open(os.path.join(DIRS[n], "six_state.csv"), newline="")):
        if r["style"] == assigned.get(r["scan_id"]) and r["gt_positive"] == "True":
            out[r["scan_id"]][int(r["round"])] = r
    return out

def trans(n):
    return {(r["scan_id"], r["transition"]): r for r in jl(os.path.join(DIRS[n], "transitions.jsonl"))
            if r["style"] == assigned.get(r["scan_id"])}

S = {n: six(n) for n in DIRS}
T = {n: trans(n) for n in DIRS}

def pmean(d):
    by = collections.defaultdict(list)
    for s, v in d.items():
        by[pat[s]].append(v)
    return statistics.mean(statistics.mean(v) for v in by.values())

print("1. Round-1 ADD fill fraction, true median (statistics.median) over strokes with a target")
for n in ("v1flat", "K1", "K2"):
    fr = [(r["target_recovery_ml"] or 0) / r["target_volume_ml"] for (s, t), r in T[n].items()
          if t == 0 and r.get("sign") == "+" and r["target_volume_ml"]]
    print("   %-6s n=%d median %.2f%%" % (n, len(fr), 100 * statistics.median(fr)))

print("2. Round-1 ADD strokes with target < 5 ml: Dice gain D1-D0, scan mean and patient mean")
small = [s for s in pos if T["oracle"].get((s, 0), {}).get("sign") == "+" and (T["oracle"][(s, 0)]["target_volume_ml"] or 0) < 5]
for n in ("v1flat", "K1", "K2"):
    g = {s: float(S[n][s][1]["dice"]) - float(S[n][s][0]["dice"]) for s in small}
    print("   %-6s n=%d scan mean %+.5f patient mean %+.5f" % (n, len(g), statistics.mean(g.values()), pmean(g)))

print("3. First strokes: scans with a stroke in round 1, and same sign/target as the oracle")
for n in ("v1flat", "K1", "K2"):
    with_stroke = [s for s in assigned if T[n].get((s, 0)) and not T[n][(s, 0)].get("no_stroke") and T[n][(s, 0)].get("sign")]
    same = sum(1 for s in with_stroke if T["oracle"][(s, 0)].get("sign") == T[n][(s, 0)]["sign"]
               and abs((T["oracle"][(s, 0)]["target_volume_ml"] or 0) - (T[n][(s, 0)]["target_volume_ml"] or 0)) < 1e-9)
    same2 = sum(1 for s in assigned if T[n].get((s, 1)) and T["oracle"].get((s, 1)) and T[n][(s, 1)].get("sign") == T["oracle"][(s, 1)].get("sign")
                and abs((T["oracle"][(s, 1)]["target_volume_ml"] or 0) - (T[n][(s, 1)]["target_volume_ml"] or 0)) < 1e-9)
    print("   %-6s first stroke on %d scans, same as oracle %d; second stroke same as oracle %d of 99" % (n, len(with_stroke), same, same2))

print("4. Round-1 splice: v1flat on ADD scans + K on REMOVE scans, D1 patient mean (states identical before round 1)")
for k in ("K1", "K2"):
    d1 = {}
    for s in pos:
        sign = T["oracle"][(s, 0)].get("sign")
        src = "v1flat" if sign == "+" else k
        d1[s] = float(S[src][s][1]["dice"])
    own = {s: float(S[k][s][1]["dice"]) for s in pos}
    print("   v1-ADD + %s-REMOVE D1 %.5f vs %s own D1 %.5f (diff %+.5f)" % (k, pmean(d1), k, pmean(own), pmean(d1) - pmean(own)))

print("5. Paired patient bootstrap (10000, seed 3407) for K2-K1 and K2flip-K2 at D5")
def per_patient_d5(n):
    by = collections.defaultdict(list)
    for s in pos:
        by[pat[s]].append(float(S[n][s][5]["dice"]))
    return {p: statistics.mean(v) for p, v in by.items()}
P = {n: per_patient_d5(n) for n in ("K1", "K2", "K2flip")}
pts = sorted(P["K1"])
rng = np.random.default_rng(3407)
idx = rng.integers(0, len(pts), size=(10000, len(pts)))
for a, b in (("K2", "K1"), ("K2flip", "K2")):
    d = np.array([P[a][p] - P[b][p] for p in pts])
    lo, hi = np.percentile(d[idx].mean(axis=1), [2.5, 97.5])
    print("   %s - %s mean %+.5f 95%% [%+.4f, %+.4f]" % (a, b, d.mean(), lo, hi))

print("6. Round-1 ideal top-up of the model's own round-1 result: fill the remaining T within / beyond 30 mm")
def reconstruct(r):
    d, fp, fn = float(r["dice"]), float(r["fp_ml"]), float(r["fn_ml"])
    tp = d * (fp + fn) / (2 * (1 - d)) if d < 1 else None
    return tp, fp, fn
REM = {}
for n in ("K1", "K2", "oracle"):
    REM[n] = {(r["scan_id"], r["transition"], r["radius_mm"]): r for r in jl(os.path.join(DIRS[n], "remote.jsonl"))
              if r["style"] == assigned.get(r["scan_id"])}
for k in ("K1", "K2"):
    near_gain, far_gain, bad = {}, {}, 0
    for s in pos:
        r0 = T[k][(s, 0)]
        tp, fp, fn = reconstruct(S[k][s][1])
        if tp is None:
            bad += 1
            near_gain[s] = far_gain[s] = 0.0
            continue
        d1 = float(S[k][s][1]["dice"])
        if r0.get("sign") != "+":
            near_gain[s] = far_gain[s] = 0.0
            continue
        tgt_far = REM["oracle"][(s, 0, 30.0)]["remote_target_repair_ml"]
        rep_far = REM[k][(s, 0, 30.0)]["remote_target_repair_ml"]
        tgt_all, rep_all = r0["target_volume_ml"], r0["target_recovery_ml"]
        x_near = (tgt_all - tgt_far) - (rep_all - rep_far)
        x_far = tgt_far - rep_far
        for x, out in ((x_near, near_gain), (x_far, far_gain)):
            out[s] = 2 * (tp + x) / (2 * tp + x + fp + fn) - d1
    print("   %s: fill remaining T within 30 mm %+.5f, beyond 30 mm %+.5f (patient mean of D1 change; %d states not reconstructable)" % (
        k, pmean(near_gain), pmean(far_gain), bad))

print("7. Dice rebuilt from the GT volume (sum of lesion volumes in trajectories.jsonl) and fp_ml / fn_ml")
err, n_states = 0.0, 0
for n in ("K1", "K2", "v1flat", "oracle"):
    G = {}
    for r in jl(os.path.join(DIRS[n], "trajectories.jsonl")):
        if r.get("style") == assigned.get(r.get("scan_id")) and r["scan_id"] in pos:
            G[r["scan_id"]] = sum(les["volume_ml"] for les in r["lesions"]["lesions"])
    for s in pos:
        for k in range(6):
            r = S[n][s][k]
            d, fp, fn = float(r["dice"]), float(r["fp_ml"]), float(r["fn_ml"])
            tp = G[s] - fn
            rec = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
            err = max(err, abs(rec - d)); n_states += 1
print("   %d states, max abs error %.2e" % (n_states, err))
