"""Re-check of the Codex round-3 D3 claims (VAL, quick-VAL protocol, sign-routed system vs v1 flat).

1. Per round: remove-stroke count and median T-recovered share per remove stroke; five-round add/remove totals.
2. Round-2 remove strokes split by the round-1 sign.
3. Same-state comparison: scans whose round-1 stroke was an add stroke drawn by v1 in both systems (mask after round 1
   identical by prediction_sha256), and whose round-2 stroke is a remove stroke with the same target volume in both.
   On these scans v1 removes (v1 trajectory) and K2 removes (routed trajectory) from the same mask and stroke.
4. Rounds 2-5 cleared volume: T only and T + O (same-sign other errors).  Final patient-mean FP / FN ml at D5.
5. Consecutive remove-remove rounds in the routed system: how many continue on the same residual by volume, and how
   many start from an unchanged mask.
"""
import collections
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b0_paths  # noqa: E402
from b0_load import POS, PATIENT, load, patient_mean, read_six  # noqa: E402

DIAG = HERE.parent / "server-diagnostics" / "z390-queue-diag-1007" / "diag-routed-v1add-k2remove-val"
b0_paths.RUNS["routed"] = DIAG
SYSTEMS = ("v1flat", "routed")
data = {n: load(n, remote=False) for n in SYSTEMS}


def mask_hashes(name):
    """(scan, style) -> list of prediction_sha256 for rounds 0..5."""
    import csv
    out = collections.defaultdict(lambda: [None] * 6)
    with open(b0_paths.RUNS[name] / "six_state.csv", newline="", encoding="utf-8") as handle:
        for r in csv.DictReader(handle):
            out[(r["scan_id"], r["style"])][int(r["round"])] = r["prediction_sha256"]
    return out


hashes = {n: mask_hashes(n) for n in SYSTEMS}


def strokes(name):
    six, tr, _ = data[name]
    return {key: r for key, r in tr.items() if not r.get("no_stroke") and r.get("status") == "ok"}


print("== 1. Remove strokes per round and median T-recovered share per remove stroke (VAL, 99 scans)")
for n in SYSTEMS:
    st = strokes(n)
    line = []
    for k in range(5):
        rem = [r for (s, sty, t), r in st.items() if t == k and r["sign"] == "-"]
        shares = [r["target_recovery_ml"] / r["target_volume_ml"] for r in rem if (r.get("target_volume_ml") or 0) > 0]
        line.append(f"r{k + 1}: {len(rem):3d} remove, median share {statistics.median(shares):.3f}")
    totals = collections.Counter(r["sign"] for r in st.values())
    none = sum(1 for key, r in data[n][1].items() if r.get("no_stroke"))
    print(f"  {n:7s} " + " | ".join(line) + f" | five rounds: add {totals['+']}, remove {totals['-']}, no stroke {none}")

print("\n== 2. Round-2 remove strokes split by round-1 sign (scans counted)")
for n in SYSTEMS:
    st = strokes(n)
    c = collections.Counter()
    for (s, sty, t), r in st.items():
        if t != 1 or r["sign"] != "-":
            continue
        first = st.get((s, sty, 0))
        c[first["sign"] if first else "none"] += 1
    first_counts = collections.Counter(r["sign"] for (s, sty, t), r in st.items() if t == 0)
    print(f"  {n:7s} round-1 add scans {first_counts['+']}, of which round-2 remove {c['+']}; "
          f"round-1 remove scans {first_counts['-']}, of which round-2 remove {c['-']}")

print("\n== 3. Same-state round-2 remove: v1 removes (v1 run) vs K2 removes (routed run), identical mask after round 1")
st_v1, st_rt = strokes("v1flat"), strokes("routed")
six_v1, six_rt = data["v1flat"][0], data["routed"][0]
same_mask = mismatch = 0
subgroup = []
for key in six_rt:
    s, sty = key
    r1_v1, r1_rt = st_v1.get((s, sty, 0)), st_rt.get((s, sty, 0))
    if not (r1_v1 and r1_rt and r1_v1["sign"] == "+" and r1_rt["sign"] == "+"):
        continue
    if hashes["v1flat"][key][1] == hashes["routed"][key][1]:
        same_mask += 1
    else:
        mismatch += 1
        continue
    r2_v1, r2_rt = st_v1.get((s, sty, 1)), st_rt.get((s, sty, 1))
    if (r2_v1 and r2_rt and r2_v1["sign"] == "-" and r2_rt["sign"] == "-"
            and abs(r2_v1["target_volume_ml"] - r2_rt["target_volume_ml"]) < 1e-9):
        subgroup.append(key)
print(f"  round-1 add in both systems: mask after round 1 identical {same_mask}, different {mismatch}")
print(f"  of these, round-2 remove in both with the same target volume: {len(subgroup)} scans, "
      f"{len({PATIENT[s] for s, sty in subgroup})} patients")
for label, st, six in (("v1 removes", st_v1, six_v1), ("K2 removes", st_rt, six_rt)):
    rows = [st[(s, sty, 1)] for s, sty in subgroup]
    shares = [r["target_recovery_ml"] / r["target_volume_ml"] for r in rows if r["target_volume_ml"] > 0]
    delta = {s: six[(s, sty)]["dice"][2] - six[(s, sty)]["dice"][1] for s, sty in subgroup if s in POS}
    print(f"  {label}: target {sum(r['target_volume_ml'] for r in rows):7.2f} ml, T fixed "
          f"{sum(r['target_recovery_ml'] for r in rows):7.2f}, O fixed {sum(r.get('same_sign_other_repair_ml') or 0 for r in rows):6.2f}, "
          f"true lesion removed {sum(r.get('tp_lost_ml') or 0 for r in rows):7.2f}, median T share {statistics.median(shares):.3f}, "
          f"patient-mean round-2 Dice change {patient_mean(delta)[0]:+.4f} ({patient_mean(delta)[1]} patients)")
for label, st in (("v1 run", st_v1), ("routed run", st_rt)):
    n3 = sum(1 for s, sty in subgroup if (st.get((s, sty, 2)) or {}).get("sign") == "-")
    print(f"  round 3 on the same scans, {label}: {n3} remove strokes")

print("\n== 4. Rounds 2-5 cleared volume by remove strokes (ml) and final patient-mean FP / FN at D5 (positive scans)")
for n in SYSTEMS:
    st = strokes(n)
    rem = [r for (s, sty, t), r in st.items() if t >= 1 and r["sign"] == "-"]
    t_fixed = sum(r["target_recovery_ml"] for r in rem)
    o_fixed = sum(r.get("same_sign_other_repair_ml") or 0 for r in rem)
    six = data[n][0]
    fp = patient_mean({s: v["fp_ml"][5] for (s, sty), v in six.items() if s in POS})[0]
    fn = patient_mean({s: v["fn_ml"][5] for (s, sty), v in six.items() if s in POS})[0]
    print(f"  {n:7s} T {t_fixed:8.2f}  T+O {t_fixed + o_fixed:8.2f}  | D5 patient-mean FP {fp:6.2f} ml, FN {fn:6.2f} ml")

print("\n== 5. Routed system: consecutive remove-remove rounds")
pairs = consistent = unchanged = 0
for (s, sty, t), r in st_rt.items():
    nxt = st_rt.get((s, sty, t + 1))
    if r["sign"] != "-" or not nxt or nxt["sign"] != "-":
        continue
    pairs += 1
    if abs(nxt["target_volume_ml"] - (r["target_volume_ml"] - r["target_recovery_ml"])) < 1e-6:
        consistent += 1
    if hashes["routed"][(s, sty)][t] == hashes["routed"][(s, sty)][t + 1]:
        unchanged += 1
print(f"  pairs {pairs}; next target = previous target - previous T fixed: {consistent}; mask unchanged by the first: {unchanged}")
