"""Per-patient spread of the gap and round-1 ADD fill by target size (saved VAL files only)."""
import csv, json, os, collections, statistics

ROOT = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer"
B1 = os.path.join(ROOT, "eval-sirb-batch1-val-20260925/rollout")
DIRS = {"K1": os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_FULL-R1-20261006"),
        "K2": os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006"),
        "v1flat": os.path.join(B1, "N1_STATE-s3407"),
        "oracle": os.path.join(B1, "oracle")}

def jl(p):
    with open(p) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def six(p):
    out, pat = collections.defaultdict(lambda: [None] * 6), {}
    style = {}
    with open(p, newline="") as f:
        for r in csv.DictReader(f):
            if r["gt_positive"] != "True":
                continue
            out[(r["scan_id"], r["style"])][int(r["round"])] = float(r["dice"])
            pat[r["scan_id"]] = r["patient_id"]
    return out, pat

k2, pat = six(os.path.join(DIRS["K2"], "six_state.csv"))
assigned = {s: st for (s, st) in k2}
curves = {}
for name, d in DIRS.items():
    c, p = six(os.path.join(d, "six_state.csv"))
    curves[name] = {s: c[(s, assigned[s])] for s in assigned}

def per_patient(c, k):
    by = collections.defaultdict(list)
    for s, v in c.items():
        by[pat[s]].append(v[k])
    return {p: sum(v) / len(v) for p, v in by.items()}

d5 = {n: per_patient(c, 5) for n, c in curves.items()}
d0 = per_patient(curves["K2"], 0)
pts = sorted(d5["K2"])
print("patients:", len(pts))
for a, b in [("K1", "v1flat"), ("K2", "v1flat"), ("K2", "K1")]:
    diff = [d5[a][p] - d5[b][p] for p in pts]
    print("%s - %s at D5: mean %+.4f  median %+.4f  better %d  worse %d  |diff|<0.01 %d" % (
        a, b, statistics.mean(diff), statistics.median(diff), sum(x > 0.01 for x in diff),
        sum(x < -0.01 for x in diff), sum(abs(x) <= 0.01 for x in diff)))

gap = sorted(((d5["oracle"][p] - d5["K1"][p], p) for p in pts), reverse=True)
tot = sum(g for g, p in gap)
print("\noracle - K1 at D5: mean %.4f; share of the summed gap from the 10 worst patients %.0f%%, 20 worst %.0f%%" % (
    tot / len(pts), 100 * sum(g for g, p in gap[:10]) / tot, 100 * sum(g for g, p in gap[:20]) / tot))
print("patients with K1 D5 < 0.5: %d ; their D0 mean %.3f, K1 D5 mean %.3f, oracle D5 mean %.3f" % (
    sum(d5["K1"][p] < 0.5 for p in pts),
    statistics.mean([d0[p] for p in pts if d5["K1"][p] < 0.5]),
    statistics.mean([d5["K1"][p] for p in pts if d5["K1"][p] < 0.5]),
    statistics.mean([d5["oracle"][p] for p in pts if d5["K1"][p] < 0.5])))
# what the mean would be if the worst-k patients reached the oracle
for k in (5, 10):
    worst = {p for g, p in gap[:k]}
    m = statistics.mean([d5["oracle"][p] if p in worst else d5["K1"][p] for p in pts])
    print("  if the %d worst-gap patients reached the ideal repair, K1 D5 mean would be %.4f" % (k, m))

# round-1 ADD strokes by target size (same state, same stroke for all systems)
tr = {n: {(r["scan_id"], r["style"]): r for r in jl(os.path.join(d, "transitions.jsonl")) if r["transition"] == 0}
      for n, d in DIRS.items()}
rows = []
for s in assigned:
    r = tr["oracle"].get((s, assigned[s]))
    if r and r["sign"] == "+" and r["target_volume_ml"]:
        rows.append((r["target_volume_ml"], s))
rows.sort()
print("\nround-1 ADD strokes: %d; target volume ml: median %.1f, quartiles %.1f / %.1f, max %.1f" % (
    len(rows), statistics.median(v for v, s in rows), rows[len(rows) // 4][0], rows[3 * len(rows) // 4][0], rows[-1][0]))
bins = [(0, 5), (5, 20), (20, 80), (80, 1e9)]
for lo, hi in bins:
    sel = [s for v, s in rows if lo <= v < hi]
    if not sel:
        continue
    line = "  target %4s-%-4s ml: n=%2d  share of volume %4.1f%%  fill fraction (median):" % (
        lo, "inf" if hi > 1e8 else int(hi), len(sel), 100 * sum(v for v, s in rows if lo <= v < hi) / sum(v for v, s in rows))
    for n in ("v1flat", "K1", "K2"):
        fr = [(tr[n][(s, assigned[s])]["target_recovery_ml"] or 0) / tr[n][(s, assigned[s])]["target_volume_ml"] for s in sel]
        line += "  %s %4.0f%%" % (n, 100 * statistics.median(fr))
    # Dice gain of round 1 on these scans
    for n in ("oracle", "v1flat", "K1", "K2"):
        g = statistics.mean(curves[n][s][1] - curves[n][s][0] for s in sel)
        line += "  dD1 %s %+.3f" % (n, g)
    print(line)

# repeated ADD strokes that change nothing: rounds 2-5, model K1/K2/v1flat
print("\nADD strokes in rounds 2-5 that recovered < 1% of their target:")
for n in ("v1flat", "K1", "K2"):
    allr = [r for r in jl(os.path.join(DIRS[n], "transitions.jsonl"))
            if (r["scan_id"], r["style"]) in {(s, assigned[s]) for s in assigned} and r["transition"] >= 1
            and r["sign"] == "+" and not r.get("no_stroke") and r["target_volume_ml"]]
    low = [r for r in allr if (r["target_recovery_ml"] or 0) < 0.01 * r["target_volume_ml"]]
    print("  %-6s %3d of %3d ADD strokes (%.0f%%)" % (n, len(low), len(allr), 100 * len(low) / len(allr)))
