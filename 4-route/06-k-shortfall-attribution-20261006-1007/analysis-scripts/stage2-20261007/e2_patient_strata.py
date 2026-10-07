"""Where K wins and loses against v1 flat, by patient (VAL, quick-VAL protocol).

1. Patients split into three equal groups by the start's missed lesion volume (fn_ml at D0, patient mean of scans) and
   by the reference lesion volume; D5 of each system and the difference to v1 flat per group.
2. Spearman correlation of the per-patient D5 difference (K minus v1) with start Dice, start missed volume, start
   over-segmentation volume and reference volume.
3. Add-stroke recovery share (T fixed / |T|) in round 1 and in rounds 2-5, median per system (Codex round 2 quoted
   v1 50.0%, K1 4.94%, K2 9.02% for the later rounds; recomputed here).
"""
import collections
import statistics

from b0_load import PATIENT, POS, load, per_patient

SYSTEMS = ["v1flat", "K1", "K2", "K2flip"]
data = {n: load(n) for n in SYSTEMS + ["oracle"]}
six_v1 = data["v1flat"][0]


def rank(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2.0
        i = j + 1
    return ranks


def spearman(x, y):
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx) ** 0.5
    vy = sum((b - my) ** 2 for b in ry) ** 0.5
    return cov / (vx * vy)


def scan_field(six, field, rnd):
    return {s: v[field][rnd] for (s, st), v in six.items() if s in POS and v[field][rnd] is not None}


start_fn = per_patient(scan_field(six_v1, "fn_ml", 0))
start_fp = per_patient(scan_field(six_v1, "fp_ml", 0))
start_dice = per_patient(scan_field(six_v1, "dice", 0))
d5 = {n: per_patient(scan_field(data[n][0], "dice", 5)) for n in SYSTEMS + ["oracle"]}
# reference volume = intersection + fn; intersection from Dice, fp, fn: I = D (fp + fn) / (2 (1 - D))
ref_scan = {}
for (s, st), v in six_v1.items():
    if s not in POS:
        continue
    d, fp, fn = v["dice"][0], v["fp_ml"][0], v["fn_ml"][0]
    inter = d * (fp + fn) / (2 * (1 - d)) if d < 1 else 0.0
    ref_scan[s] = inter + fn
ref_vol = per_patient(ref_scan)
patients = sorted(start_fn)

for label, key in (("start missed volume (fn_ml at D0)", start_fn), ("reference lesion volume", ref_vol)):
    order = sorted(patients, key=lambda p: key[p])
    thirds = [order[:len(order) // 3], order[len(order) // 3: 2 * len(order) // 3], order[2 * len(order) // 3:]]
    print(f"== 1. Patients by {label}, three groups (VAL D5, patient mean)")
    for name, group in zip(("low", "mid", "high"), thirds):
        med = statistics.median(key[p] for p in group)
        row = " ".join(f"{n} {sum(d5[n][p] for p in group) / len(group):.4f}" for n in SYSTEMS + ["oracle"])
        diffs = " ".join(f"{n}-v1 {sum(d5[n][p] - d5['v1flat'][p] for p in group) / len(group):+.4f}" for n in SYSTEMS[1:])
        print(f"  {name:4s} n={len(group)} median {med:8.2f} ml | {row} | {diffs}")

print("\n== 2. Spearman correlation of per-patient D5(K) - D5(v1) with start features (n patients)")
for n in SYSTEMS[1:]:
    diff = [d5[n][p] - d5["v1flat"][p] for p in patients]
    out = []
    for label, key in (("start Dice", start_dice), ("start missed ml", start_fn), ("start over-seg ml", start_fp),
                       ("reference ml", ref_vol)):
        out.append(f"{label} {spearman([key[p] for p in patients], diff):+.3f}")
    wins = sum(1 for x in diff if x > 0.005)
    losses = sum(1 for x in diff if x < -0.005)
    print(f"  {n:7s} n={len(patients)} " + " | ".join(out) + f" | wins {wins} / ties {len(diff) - wins - losses} / losses {losses}")

print("\n== 3. Add-stroke recovery share (T fixed / |T|), median and mean over strokes")
for n in SYSTEMS + ["oracle"]:
    six, tr, rem = data[n]
    for label, rounds in (("r1", {0}), ("r2-5", {1, 2, 3, 4})):
        shares = [float(r["target_recovery_ml"]) / float(r["target_volume_ml"]) for (s, st, k), r in tr.items()
                  if k in rounds and r.get("sign") == "+" and not r.get("no_stroke") and r.get("status") == "ok"
                  and (r.get("target_volume_ml") or 0) > 0]
        print(f"  {n:7s} {label:5s} n={len(shares):3d} median {statistics.median(shares):.3f} mean {statistics.mean(shares):.3f}")
