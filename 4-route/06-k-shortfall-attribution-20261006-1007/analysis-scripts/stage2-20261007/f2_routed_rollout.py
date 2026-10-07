"""Diagnostic D3 read-out: the sign-routed system (add strokes by v1 flat, remove strokes by K2) on VAL, five real
rounds on its own trajectory, against v1 flat, K1, K2 and K2 + flip on the same quick-VAL protocol.

Input: server-diagnostics/z390-queue-diag-1007/diag-routed-*/ (six_state.csv, transitions.jsonl, trajectories.jsonl;
copied back with sha256 checked).  Sections: D0..D5 and nAUC with patient-paired bootstrap intervals; five-round gain
split by stroke sign; round-1 identity check (round 1 of the routed system must equal v1 flat on add strokes and K2 on
remove strokes exactly, the same start and the same stroke); lesion-level outcomes; add/remove stroke volumes.
VAL only; a two-network system, never a single-model result.
"""
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b0_paths  # noqa: E402
from b0_load import KEYS, POS, jl, load, paired_bootstrap, patient_mean  # noqa: E402

DIAG = HERE.parent / "server-diagnostics" / "z390-queue-diag-1007"
routed_dirs = sorted(p for p in DIAG.glob("diag-routed-*") if (p / "six_state.csv").exists())
for folder in routed_dirs:
    b0_paths.RUNS[folder.name] = folder
names = ["v1flat", "K1", "K2", "K2flip"] + [f.name for f in routed_dirs]
data = {n: load(n) for n in names}


def nauc(d):
    return (0.5 * d[0] + d[1] + d[2] + d[3] + d[4] + 0.5 * d[5]) / 5.0


def scan_values(six, fn):
    return {s: fn(v["dice"]) for (s, st), v in six.items() if s in POS and None not in v["dice"]}


print("== 1. VAL Dice by round (patient mean over positive scans) and paired differences [95% patient bootstrap]")
for n in names:
    six = data[n][0]
    ds = [patient_mean(scan_values(six, lambda d, k=k: d[k]))[0] for k in range(6)]
    print(f"  {n:38s} " + " ".join(f"D{k} {x:.4f}" for k, x in enumerate(ds))
          + f"  nAUC {patient_mean(scan_values(six, nauc))[0]:.4f}")
for n in [f.name for f in routed_dirs]:
    a = scan_values(data[n][0], lambda d: d[5])
    for ref in ("v1flat", "K1", "K2", "K2flip"):
        b = scan_values(data[ref][0], lambda d: d[5])
        common = set(a) & set(b)
        diff, lo, hi, npat = paired_bootstrap({s: a[s] for s in common}, {s: b[s] for s in common})
        print(f"  {n} minus {ref:7s} D5 {diff:+.4f} [{lo:+.4f}, {hi:+.4f}] ({npat} patients)")

print("\n== 2. Five-round Dice gain split by the sign of each round's stroke (patient mean of per-round deltas)")
for n in names:
    six, tr, _ = data[n]
    totals = collections.Counter()
    for k in range(5):
        contrib = {"+": {}, "-": {}}
        for (s, st), v in six.items():
            if s not in POS or None in v["dice"]:
                continue
            delta = v["dice"][k + 1] - v["dice"][k]
            r = tr.get((s, st, k))
            sign = r["sign"] if r and not r.get("no_stroke") else None
            for key in contrib:
                contrib[key][s] = delta if sign == key else 0.0
        for key in contrib:
            totals[key] += patient_mean(contrib[key])[0]
    print(f"  {n:38s} add {totals['+']:+.4f}  remove {totals['-']:+.4f}  total {totals['+'] + totals['-']:+.4f}")

print("\n== 3. Round 1 identity: routed system vs v1 flat (add strokes) and K2 (remove strokes), same start, same stroke")
for folder in routed_dirs:
    six, tr, _ = data[folder.name]
    same = diff = 0
    for (s, st, k), r in tr.items():
        if k != 0 or r.get("no_stroke"):
            continue
        ref = data["v1flat" if r["sign"] == "+" else "K2"][1].get((s, st, 0))
        fields = ("target_recovery_ml", "fp_added_ml", "tp_lost_ml")
        if ref and all(abs((r.get(f) or 0) - (ref.get(f) or 0)) < 1e-9 for f in fields):
            same += 1
        else:
            diff += 1
    print(f"  {folder.name}: round-1 strokes identical to the expected network {same}, different {diff}")

print("\n== 4. Volumes (ml, sums over the 99 scans): add T fixed / FP added, remove T fixed / true lesion removed, r1 and r2-5")
for n in names:
    six, tr, _ = data[n]
    out = []
    for label, rounds in (("r1", {0}), ("r2-5", {1, 2, 3, 4})):
        add = [r for (s, st, k), r in tr.items() if k in rounds and r.get("sign") == "+" and not r.get("no_stroke")]
        rem = [r for (s, st, k), r in tr.items() if k in rounds and r.get("sign") == "-" and not r.get("no_stroke")]
        out.append(f"{label}: +T {sum(r.get('target_recovery_ml') or 0 for r in add):6.1f} +FP {sum(r.get('fp_added_ml') or 0 for r in add):6.1f}"
                   f" -T {sum(r.get('target_recovery_ml') or 0 for r in rem):6.1f} -TP {sum(r.get('tp_lost_ml') or 0 for r in rem):6.1f}")
    print(f"  {n:38s} " + " | ".join(out))

print("\n== 5. Lesion-level outcomes (trajectories.jsonl)")
for n in names:
    folder = b0_paths.RUNS[n]
    rows = [r for r in jl(folder / "trajectories.jsonl") if (r.get("scan_id"), r.get("style")) in KEYS
            and r.get("lesions") and r.get("cumulative_damage")] if (folder / "trajectories.jsonl").exists() else []
    if rows:
        print(f"  {n:38s} lesions erased {sum(len(r['lesions']['initial_lesion_erasure_lesions']) for r in rows):3d}"
              f"  persistent damage at D5 {sum(r['cumulative_damage']['damage_persistent_d5_ml'] for r in rows):7.1f} ml"
              f"  detection-loss events {sum(r['lesions']['detection_loss_events'] for r in rows):3d}")
