"""More angles on the same saved VAL files: lesion F1, FP/FN volume, negatives, drawing style, per patient, stuck strokes."""
import csv, json, os, collections, statistics

ROOT = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer"
B1 = os.path.join(ROOT, "eval-sirb-batch1-val-20260925/rollout")
DIRS = collections.OrderedDict([
    ("v1flat", os.path.join(B1, "N1_STATE-s3407")),
    ("K1", os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_FULL-R1-20261006")),
    ("K2", os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006")),
    ("K2flip", os.path.join(ROOT, "eval-sirb-v3-quickval-flip-INTENT_REFRESH-R1-20261006")),
    ("oracle", os.path.join(B1, "oracle")),
])

def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

k2 = rows(os.path.join(DIRS["K2"], "six_state.csv"))
assigned = {r["scan_id"]: r["style"] for r in k2}
pat = {r["scan_id"]: r["patient_id"] for r in k2}
positive = {r["scan_id"] for r in k2 if r["gt_positive"] == "True"}

def table(name):
    out = collections.defaultdict(dict)
    for r in rows(os.path.join(DIRS[name], "six_state.csv")):
        s = r["scan_id"]
        if r["style"] != assigned.get(s):
            continue
        out[s][int(r["round"])] = r
    return out

T = {n: table(n) for n in DIRS}

def pmean(per_scan):
    by = collections.defaultdict(list)
    for s, v in per_scan.items():
        if v is not None:
            by[pat[s]].append(v)
    vals = [sum(v) / len(v) for v in by.values()]
    return sum(vals) / len(vals), len(vals)

def num(x):
    return None if x in ("", "None", None) else float(x)

print("A. Round-5 lesion F1 (DMM), FP ml, FN ml on positive scans (patient mean); FP ml on negative scans (scan mean)")
neg = sorted(set(assigned) - positive)
for n in DIRS:
    f1, n1 = pmean({s: num(T[n][s][5]["dmm"]) for s in positive})
    f10, _ = pmean({s: num(T[n][s][0]["dmm"]) for s in positive})
    fp, _ = pmean({s: num(T[n][s][5]["fp_ml"]) for s in positive})
    fn, _ = pmean({s: num(T[n][s][5]["fn_ml"]) for s in positive})
    fp0, _ = pmean({s: num(T[n][s][0]["fp_ml"]) for s in positive})
    fn0, _ = pmean({s: num(T[n][s][0]["fn_ml"]) for s in positive})
    negfp = statistics.mean(num(T[n][s][5]["fp_ml"]) for s in neg)
    negfp0 = statistics.mean(num(T[n][s][0]["fp_ml"]) for s in neg)
    print("  %-7s lesion F1 %.3f->%.3f  FP ml %.2f->%.2f  FN ml %.2f->%.2f  | negatives (%d scans) FP ml %.2f->%.2f" % (
        n, f10, f1, fp0, fp, fn0, fn, len(neg), negfp0, negfp))

print("\nB. Round-5 Dice by drawing style (patient mean within style)")
for st in ("centerline", "boundary", "random"):
    scans = {s for s in positive if assigned[s] == st}
    line = "  %-10s n=%2d scans:" % (st, len(scans))
    for n in DIRS:
        m, k = pmean({s: num(T[n][s][5]["dice"]) for s in scans})
        line += "  %s %.4f" % (n, m)
    print(line)

print("\nC. Per patient: K1 minus v1 flat at round 5 against how big the missed volume was at the start (FN ml at round 0)")
by_p = collections.defaultdict(list)
for s in positive:
    by_p[pat[s]].append(s)
rowsp = []
for p, scans in by_p.items():
    d_k1 = statistics.mean(num(T["K1"][s][5]["dice"]) for s in scans)
    d_v1 = statistics.mean(num(T["v1flat"][s][5]["dice"]) for s in scans)
    fn0 = statistics.mean(num(T["K1"][s][0]["fn_ml"]) for s in scans)
    d0 = statistics.mean(num(T["K1"][s][0]["dice"]) for s in scans)
    orc = statistics.mean(num(T["oracle"][s][5]["dice"]) for s in scans)
    rowsp.append((fn0, d_k1 - d_v1, d0, d_k1, d_v1, orc, p))
rowsp.sort()
third = len(rowsp) // 3
for name, part in (("smallest missed volume", rowsp[:third]), ("middle", rowsp[third:2 * third]), ("largest missed volume", rowsp[2 * third:])):
    print("  %-23s %2d pts: FN at start %.1f ml (median), K1-v1flat %+.4f, D0 %.3f, K1 D5 %.3f, v1 D5 %.3f, ideal D5 %.3f" % (
        name, len(part), statistics.median(r[0] for r in part), statistics.mean(r[1] for r in part),
        statistics.mean(r[2] for r in part), statistics.mean(r[3] for r in part), statistics.mean(r[4] for r in part),
        statistics.mean(r[5] for r in part)))

print("\nD. Lesion voxels wrongly deleted (tp_lost ml) by remove strokes, rounds 1 and 2-5, all 99 scans")
def jl(p):
    with open(p) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
TR = {}
for n in DIRS:
    TR[n] = {(r["scan_id"], r["transition"]): r for r in jl(os.path.join(DIRS[n], "transitions.jsonl"))
             if r["style"] == assigned.get(r["scan_id"])}
for n in DIRS:
    r1 = sum((r["tp_lost_ml"] or 0) for (s, t), r in TR[n].items() if t == 0 and r.get("sign") == "-")
    r25 = sum((r["tp_lost_ml"] or 0) for (s, t), r in TR[n].items() if t >= 1 and r.get("sign") == "-")
    fa1 = sum((r["fp_added_ml"] or 0) for (s, t), r in TR[n].items() if t == 0 and r.get("sign") == "+")
    fa25 = sum((r["fp_added_ml"] or 0) for (s, t), r in TR[n].items() if t >= 1 and r.get("sign") == "+")
    print("  %-7s tp_lost by REMOVE: round1 %6.1f ml, rounds2-5 %6.1f ml | fp_added by ADD: round1 %6.1f, rounds2-5 %6.1f" % (n, r1, r25, fa1, fa25))

print("\nE. Stuck: scans whose ADD strokes of rounds 2-5 point at a target of (almost) the same size as the round before and recover < 1%")
for n in ("v1flat", "K1", "K2"):
    stuck_scans = 0
    stuck_strokes = 0
    for s in assigned:
        count = 0
        for t in range(1, 5):
            a, b = TR[n].get((s, t - 1)), TR[n].get((s, t))
            if not a or not b or b.get("sign") != "+" or a.get("sign") != "+":
                continue
            ta, tb = a["target_volume_ml"] or 0, b["target_volume_ml"] or 0
            if tb > 0 and abs(ta - tb) <= 0.05 * tb and (b["target_recovery_ml"] or 0) < 0.01 * tb:
                count += 1
        if count:
            stuck_scans += 1
            stuck_strokes += count
    print("  %-7s %2d scans, %3d strokes repeat on the same unfilled target" % (n, stuck_scans, stuck_strokes))
