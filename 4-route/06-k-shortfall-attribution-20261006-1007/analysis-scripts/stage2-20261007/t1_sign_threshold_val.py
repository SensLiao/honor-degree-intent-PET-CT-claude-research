"""T1 read-out (VAL): K1 with one add and one remove execution threshold learned on TRAIN round-1 scores (half of the
TRAIN patients; fit_petct_sirb_sign_thresholds.py), frozen and run for five real rounds on the quick-VAL protocol, against
K1 at 0.5 and v1 flat.

Input: server-diagnostics/rtx5090-signthr-1007/ (train-sign-thresholds.json, quickval-signthr/ six_state.csv,
transitions.jsonl; copied back with sha256 checked).  Sections: 1 the learned thresholds and the TRAIN round-1 check;
2 D0..D5 and nAUC with patient-paired bootstrap intervals; 3 five-round gain split by stroke sign; 4 round-1 and
rounds 2-5 volumes (T fixed, background added, true lesion removed) and stroke counts; 5 lesion-level outcomes.
VAL only; the thresholds were never chosen on VAL.
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b0_paths  # noqa: E402
from b0_load import KEYS, POS, jl, load, paired_bootstrap, patient_mean  # noqa: E402

T1 = HERE.parent / "server-diagnostics" / "rtx5090-signthr-1007"
b0_paths.RUNS["K1signthr"] = T1 / "quickval-signthr"
names = ["v1flat", "K1", "K1signthr"]
data = {n: load(n, remote=False) for n in names}


def nauc(d):
    return (0.5 * d[0] + d[1] + d[2] + d[3] + d[4] + 0.5 * d[5]) / 5.0


def scan_values(six, fn):
    return {s: fn(v["dice"]) for (s, st), v in six.items() if s in POS and None not in v["dice"]}


fit = json.loads((T1 / "train-sign-thresholds.json").read_text(encoding="utf-8"))["networks"]["K1"]
print("== 1. Thresholds learned on TRAIN (fit half) and the TRAIN round-1 Dice at 0.5 / 0.5 and at the learned pair")
print(f"  add {fit['add']['threshold']}  remove {fit['remove']['threshold']}")
for part in ("fit", "check", "all"):
    x = fit[part]
    print(f"  {part:5s} {x['patients']:3d} patients {x['scans']:3d} scans: {x['round1_dice_at_half']:.4f} -> "
          f"{x['round1_dice_at_thresholds']:.4f} ({x['round1_dice_at_thresholds'] - x['round1_dice_at_half']:+.4f})")
record = json.loads((T1 / "quickval-signthr" / "sign_thresholds.json").read_text(encoding="utf-8"))
print(f"  rollout used add {record['threshold_add_by_round']} remove {record['threshold_remove_by_round']}")

print("\n== 2. VAL Dice by round (patient mean over positive scans) and paired differences [95% patient bootstrap]")
for n in names:
    six = data[n][0]
    ds = [patient_mean(scan_values(six, lambda d, k=k: d[k]))[0] for k in range(6)]
    print(f"  {n:10s} " + " ".join(f"D{k} {x:.4f}" for k, x in enumerate(ds))
          + f"  nAUC {patient_mean(scan_values(six, nauc))[0]:.4f}")
for k in (1, 5):
    a = scan_values(data["K1signthr"][0], lambda d, k=k: d[k])
    for ref in ("K1", "v1flat"):
        b = scan_values(data[ref][0], lambda d, k=k: d[k])
        common = set(a) & set(b)
        diff, lo, hi, npat = paired_bootstrap({s: a[s] for s in common}, {s: b[s] for s in common})
        print(f"  K1signthr minus {ref:6s} D{k} {diff:+.4f} [{lo:+.4f}, {hi:+.4f}] ({npat} patients)")

print("\n== 3. Five-round Dice gain split by the sign of each round's stroke (patient mean of per-round deltas)")
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
    print(f"  {n:10s} add {totals['+']:+.4f}  remove {totals['-']:+.4f}  total {totals['+'] + totals['-']:+.4f}")

print("\n== 4. Volumes (ml, sums over the 99 scans) and stroke counts: round 1 and rounds 2-5")
for n in names:
    six, tr, _ = data[n]
    out = []
    for label, rounds in (("r1", {0}), ("r2-5", {1, 2, 3, 4})):
        add = [r for (s, st, k), r in tr.items() if k in rounds and r.get("sign") == "+" and not r.get("no_stroke")]
        rem = [r for (s, st, k), r in tr.items() if k in rounds and r.get("sign") == "-" and not r.get("no_stroke")]
        out.append(f"{label}: add {len(add):3d} +T {sum(r.get('target_recovery_ml') or 0 for r in add):6.1f} "
                   f"+FP {sum(r.get('fp_added_ml') or 0 for r in add):6.1f} | remove {len(rem):3d} "
                   f"-T {sum(r.get('target_recovery_ml') or 0 for r in rem):6.1f} "
                   f"-TP {sum(r.get('tp_lost_ml') or 0 for r in rem):6.1f}")
    print(f"  {n:10s} " + " || ".join(out))

print("\n== 5. Lesion-level outcomes (trajectories.jsonl)")
for n in names:
    folder = b0_paths.RUNS[n]
    rows = [r for r in jl(folder / "trajectories.jsonl") if (r.get("scan_id"), r.get("style")) in KEYS
            and r.get("lesions") and r.get("cumulative_damage")]
    if rows:
        print(f"  {n:10s} lesions erased {sum(len(r['lesions']['initial_lesion_erasure_lesions']) for r in rows):3d}"
              f"  persistent damage at D5 {sum(r['cumulative_damage']['damage_persistent_d5_ml'] for r in rows):7.1f} ml"
              f"  detection-loss events {sum(r['lesions']['detection_loss_events'] for r in rows):3d}")
