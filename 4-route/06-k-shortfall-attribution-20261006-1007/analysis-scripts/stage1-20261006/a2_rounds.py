"""Where the Dice is lost: per round, per stroke sign, matched round-1 comparison with the ideal repair.

Read-only on saved VAL files.  Systems on the quick-VAL protocol (SIRB roster style per scan).
"""
import csv, json, os, collections, statistics

ROOT = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer"
B1 = os.path.join(ROOT, "eval-sirb-batch1-val-20260925/rollout")
K2 = os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006")

def jl(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def six(path):
    out, pat = collections.defaultdict(dict), {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            s, st, k = r["scan_id"], r["style"], int(r["round"])
            pat[s] = r["patient_id"]
            d = r["dice"]
            out[(s, st)].setdefault("dice", [None] * 6)[k] = float(d) if d not in ("", "None") else None
            out[(s, st)]["pos"] = r["gt_positive"] == "True"
    return out, pat

k2six, pat = six(os.path.join(K2, "six_state.csv"))
assigned = {s: st for (s, st), v in k2six.items()}
keys = set((s, st) for (s, st) in k2six)
pos = {s for (s, st), v in k2six.items() if v["pos"]}

def load(dirpath):
    sx, p = six(os.path.join(dirpath, "six_state.csv"))
    pat.update(p)
    tr = {}
    for r in jl(os.path.join(dirpath, "transitions.jsonl")):
        if (r["scan_id"], r["style"]) in keys:
            tr[(r["scan_id"], r["style"], r["transition"])] = r
    rem = {}
    for r in jl(os.path.join(dirpath, "remote.jsonl")):
        if (r["scan_id"], r["style"]) in keys:
            rem[(r["scan_id"], r["style"], r["transition"], r["radius_mm"])] = r
    return {k: v for k, v in sx.items() if k in keys}, tr, rem

systems = collections.OrderedDict()
systems["K2"] = load(K2)
systems["K1"] = load(os.path.join(ROOT, "eval-sirb-v3-quickval-INTENT_FULL-R1-20261006"))
systems["K2flip"] = load(os.path.join(ROOT, "eval-sirb-v3-quickval-flip-INTENT_REFRESH-R1-20261006"))
systems["v1flat"] = load(os.path.join(B1, "N1_STATE-s3407"))
systems["oracle"] = load(os.path.join(B1, "oracle"))

def pmean(values):
    """values: scan -> number; patient mean of scan means."""
    by = collections.defaultdict(list)
    for s, v in values.items():
        by[pat[s]].append(v)
    pm = [sum(v) / len(v) for v in by.values()]
    return sum(pm) / len(pm), len(pm)

print("Per-round Dice gain (patient mean over 85 positive scans / 54 pts), split by the sign of that round's stroke")
print("contribution = patient mean of (Dice_k - Dice_k-1) where the round had that sign, else 0; rows sum to the round gain")
for name, (sx, tr, rem) in systems.items():
    print("== %s" % name)
    tot = collections.Counter()
    for t in range(5):
        contrib = {"+": {}, "-": {}, "none": {}}
        for (s, st), v in sx.items():
            if s not in pos:
                continue
            d = v["dice"]
            delta = d[t + 1] - d[t]
            r = tr.get((s, st, t))
            sign = r["sign"] if r and not r.get("no_stroke") else "none"
            for k in contrib:
                contrib[k][s] = delta if k == sign else 0.0
        row = []
        for k in ("+", "-", "none"):
            m, n = pmean(contrib[k])
            tot[k] += m
            row.append("%s %+.4f" % (k, m))
        # counts
        cnt = collections.Counter((tr.get((s, assigned[s], t)) or {}).get("sign", "none") for s in pos)
        print("  round %d: %s   strokes on pos scans: ADD %d  REMOVE %d" % (t + 1, "  ".join(row), cnt["+"], cnt["-"]))
    print("  5 rounds: ADD %+.4f  REMOVE %+.4f  none %+.4f  total %+.4f" % (tot["+"], tot["-"], tot["none"], sum(tot.values())))

print("\nStroke-level repair of the targeted error component (all 99 scans incl. negatives; volumes in ml)")
for name, (sx, tr, rem) in systems.items():
    print("== %s" % name)
    for t in range(5):
        for sign in ("+", "-"):
            rows = [r for (s, st, tt), r in tr.items() if tt == t and r.get("sign") == sign and not r.get("no_stroke")]
            if not rows:
                continue
            tv = sum(r["target_volume_ml"] or 0 for r in rows)
            rec = sum(r["target_recovery_ml"] or 0 for r in rows)
            ne = sum(r["new_error_ml"] or 0 for r in rows)
            other = sum(r["same_sign_other_repair_ml"] or 0 for r in rows)
            tpl = sum(r["tp_lost_ml"] or 0 for r in rows)
            fpa = sum(r["fp_added_ml"] or 0 for r in rows)
            ratios = [(r["target_recovery_ml"] or 0) / r["target_volume_ml"] for r in rows if r["target_volume_ml"]]
            zero = sum(1 for r in rows if not r["target_recovery_ml"])
            print("  r%d %s n=%3d target %8.2f  recovered %7.2f (%5.1f%% by vol, median stroke %5.1f%%)  zero-recovery %3d  "
                  "other same-sign %6.2f  new error %6.2f (tp_lost %5.2f fp_added %5.2f)" % (
                      t + 1, "ADD" if sign == "+" else "REM", len(rows), tv, rec, 100 * rec / tv if tv else 0,
                      100 * statistics.median(ratios) if ratios else 0, zero, other, ne, tpl, fpa))

# ---- matched round 1: same state (D0) and same first stroke for every system ----
print("\nMatched round 1 (identical D0 mask and identical first stroke for every system)")
o_tr = systems["oracle"][1]
for name in ("K1", "K2", "v1flat"):
    tr = systems[name][1]
    same = 0
    for s in assigned:
        a, b = tr.get((s, assigned[s], 0)), o_tr.get((s, assigned[s], 0))
        if a and b and a.get("sign") == b.get("sign") and abs((a["target_volume_ml"] or 0) - (b["target_volume_ml"] or 0)) < 1e-9:
            same += 1
    print("  %s: first stroke identical to oracle's (sign and target volume) on %d of %d scans" % (name, same, len(assigned)))

print("\nRound 1 ADD strokes: target volume beyond R mm of the stroke (oracle repairs all of it) and what the model repaired there")
o_rem = systems["oracle"][2]
for name in ("K1", "K2", "v1flat"):
    rem, tr = systems[name][2], systems[name][1]
    for R in (15.0, 30.0, 60.0):
        tgt_far = rep_far = tgt_all = rep_all = 0.0
        for s in assigned:
            r0 = tr.get((s, assigned[s], 0))
            if not r0 or r0.get("sign") != "+":
                continue
            o = o_rem.get((s, assigned[s], 0, R))
            m = rem.get((s, assigned[s], 0, R))
            tgt_far += o["remote_target_repair_ml"]
            rep_far += m["remote_target_repair_ml"]
            tgt_all += r0["target_volume_ml"]
            rep_all += r0["target_recovery_ml"]
        print("  %-6s R=%2d mm: target beyond R %7.2f of %7.2f ml (%4.1f%%); model repaired beyond R %6.2f (%4.1f%% of it); "
              "within R target %7.2f repaired %6.2f (%4.1f%%)" % (
                  name, R, tgt_far, tgt_all, 100 * tgt_far / tgt_all, rep_far, 100 * rep_far / tgt_far if tgt_far else 0,
                  tgt_all - tgt_far, rep_all - rep_far, 100 * (rep_all - rep_far) / (tgt_all - tgt_far)))
