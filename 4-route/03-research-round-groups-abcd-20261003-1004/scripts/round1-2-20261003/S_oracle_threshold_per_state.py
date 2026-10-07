"""One-off CPU check (VAL, flat v1, 200 own later-round states, single step).
Per state: gain at 0.5, best gain over the 19 swept thresholds, best gain allowing 'no edit' (gain 0),
and how the best threshold moves with the state's current Dice D0, per sign."""
import collections, json, statistics, sys
from pathlib import Path
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from A_common import VAL1, read_jsonl, dice
from A_transitions import build

rows, _, gts = build("flat")
by_key = {(r["scan"], r["style"], r["t"]): r for r in rows}
sweep = [r for r in read_jsonl(VAL1 / "samestate-trajectory" / "N1_STATE-s3407" / "sweep.jsonl")
         if ".trajbank-N1_STATE-" in r["episode_id"]]
per_state = collections.defaultdict(dict)   # state key -> thr -> gain
meta = {}
for s in sweep:
    r = by_key.get((s["scan_id"], s["style"], int(s["round"])))
    if r is None or r["no_stroke"] or not r["pos"]:
        continue
    g = gts[(r["scan"], r["style"])]
    tp, fp, fn = g - r["fn0"], r["fp0"], r["fn0"]
    R, C, H = float(s["target_recovery_ml"]), float(s["other_repaired_ml"]), float(s["new_error_ml"])
    d1 = dice(tp + R + C, fp + H, fn - R - C) if r["sign"] == "+" else dice(tp - H, fp - R - C, fn + H)
    key = (s["episode_id"],)
    per_state[key][round(float(s["threshold"]), 2)] = d1 - r["d0"]
    meta[key] = (r["sign"], r["patient"], r["d0"])
out = {}
for sign in ("+", "-"):
    keys = [k for k in per_state if meta[k][0] == sign]
    byp = collections.defaultdict(lambda: collections.defaultdict(list))
    pairs = []
    for k in keys:
        gains = per_state[k]
        g05 = gains.get(0.5)
        if g05 is None:
            continue
        best_thr = max(gains, key=lambda t: (gains[t], -abs(t - 0.5)))
        best = gains[best_thr]
        best_noedit = max(best, 0.0)
        p = meta[k][1]
        byp["at_0.5"][p].append(g05)
        byp["best_threshold"][p].append(best)
        byp["best_or_no_edit"][p].append(best_noedit)
        byp["no_edit_only_if_harmful_at_0.5"][p].append(max(g05, 0.0))
        pairs.append((meta[k][2], best_thr))
    res = {"states": len(pairs), "patients": len(byp["at_0.5"])}
    for name, d in byp.items():
        res[name] = sum(statistics.mean(v) for v in d.values()) / len(d)
    # best threshold vs D0: Spearman-like via ranks
    if len(pairs) > 5:
        xs = [a for a, _ in pairs]; ys = [b for _, b in pairs]
        def ranks(v):  # average ranks for ties (Spearman)
            o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0]*len(v); i = 0
            while i < len(o):
                j = i
                while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                    j += 1
                for k in range(i, j + 1):
                    r[o[k]] = (i + j) / 2.0
                i = j + 1
            return r
        rx, ry = ranks(xs), ranks(ys)
        mx, my = statistics.mean(rx), statistics.mean(ry)
        cov = sum((a-mx)*(b-my) for a, b in zip(rx, ry)); vx = sum((a-mx)**2 for a in rx); vy = sum((b-my)**2 for b in ry)
        res["spearman_bestthr_vs_D0"] = cov / (vx*vy) ** 0.5 if vx and vy else None
        # median best threshold by D0 tercile
        srt = sorted(pairs)
        n = len(srt)
        res["median_best_thr_by_D0_tercile"] = [
            {"D0_range": [round(srt[i*n//3][0], 3), round(srt[min((i+1)*n//3, n)-1][0], 3)],
             "median_best_thr": statistics.median(b for _, b in srt[i*n//3:(i+1)*n//3])} for i in range(3)]
    out[sign] = res
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False)[:400])
