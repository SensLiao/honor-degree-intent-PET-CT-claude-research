"""Every SIRB system on the quick-VAL protocol side by side, plus the behaviour views the six-state table hides.

VAL only (99 scans / 57 patients; Dice over 85 positive scans / 54 patients, patient mean of scan means).  Sections:
  1. D0..D5 and nAUC of every system; D5 and nAUC minus v1 flat with a patient-paired bootstrap interval.
  2. Lesion-level outcomes from trajectories.jsonl: lesions lost from detection, initial lesions erased, damage that
     persists to D5, wrong-at-final-but-correct-at-start volume.
  3. Remote edits from remote.jsonl: how much T repair, O repair and new error happen beyond 15/30/60 mm of the stroke,
     round 1 and rounds 2-5.
  4. Negative scans (no lesion): false-positive volume at D0 and D5.
  5. Strokes that changed (almost) nothing, repeats of the previous stroke, and big single-stroke drops.
  6. By drawing style.
  7. Seconds per round (model and robot).
"""
import collections
import statistics

from b0_load import KEYS, PATIENT, POS, jl, load, paired_bootstrap, patient_mean
from b0_paths import RUNS

FULL = ["v1flat", "v1N3", "K1", "K1flip", "K2", "K2flip", "oracle", "noop"]
SIX_ONLY = ["cont_static", "cont_induced", "cont_induced_flip", "cont_spatial", "cont_N3ES", "cont_N4",
            "groupA_induced", "weightavg"]
LABEL = {"v1flat": "v1 flat 40k", "v1N3": "v1 N3 40k", "K1": "K1", "K2": "K2", "K2flip": "K2 + flip", "K1flip": "K1 + flip",
         "oracle": "ideal repair", "noop": "no edit", "cont_static": "v1 flat +8k cont.",
         "cont_induced": "v1 flat +8k induced states", "cont_induced_flip": "  same + flip",
         "cont_spatial": "+8k spatial branch", "cont_N3ES": "N3 +8k error-sees-stroke", "cont_N4": "N3 +8k cont.",
         "groupA_induced": "induced + group A executor", "weightavg": "weight average of two cont."}

data = {}
for name in FULL:
    data[name] = load(name)
for name in SIX_ONLY:
    if (RUNS[name] / "six_state.csv").exists():
        data[name] = load(name, transitions=False, remote=False)


def nauc(d):
    return (0.5 * d[0] + d[1] + d[2] + d[3] + d[4] + 0.5 * d[5]) / 5.0


def scan_values(six, fn):
    return {s: fn(v["dice"]) for (s, st), v in six.items() if s in POS and None not in v["dice"]}


print("== 1. Quick-VAL Dice by round (patient mean; positive scans), D5 and nAUC minus v1 flat [95% patient bootstrap]")
ref_d5 = scan_values(data["v1flat"][0], lambda d: d[5])
ref_auc = scan_values(data["v1flat"][0], nauc)
print(f"{'system':32s} {'n':>3s} " + " ".join(f"D{k:<5d}" for k in range(6)) + "  nAUC    dD5 vs v1 [CI]            dnAUC [CI]")
for name in FULL + [n for n in SIX_ONLY if n in data]:
    six = data[name][0]
    ds = [patient_mean(scan_values(six, lambda d, k=k: d[k]))[0] for k in range(6)]
    n = patient_mean(scan_values(six, lambda d: d[5]))[1]
    auc = patient_mean(scan_values(six, nauc))[0]
    if name == "v1flat":
        extra = ""
    else:
        a = scan_values(six, lambda d: d[5])
        common = set(a) & set(ref_d5)
        d1, lo1, hi1, _ = paired_bootstrap({s: a[s] for s in common}, {s: ref_d5[s] for s in common})
        b = scan_values(six, nauc)
        d2, lo2, hi2, _ = paired_bootstrap({s: b[s] for s in common}, {s: ref_auc[s] for s in common})
        extra = f"{d1:+.4f} [{lo1:+.4f},{hi1:+.4f}]  {d2:+.4f} [{lo2:+.4f},{hi2:+.4f}]"
    print(f"{LABEL[name]:32s} {n:3d} " + " ".join(f"{x:.4f}" for x in ds) + f"  {auc:.4f}  {extra}")

print("\n== 2. Lesion-level outcomes (sums over the 99 scans; trajectories.jsonl)")
print(f"{'system':14s} {'lesions':>7s} {'det.loss ev':>11s} {'scans w/ loss':>13s} {'init.erased':>11s} {'erased@D5':>9s} "
      f"{'damage ev ml':>12s} {'persist D5 ml':>13s} {'wrong@final ml':>14s}")
for name in FULL:
    folder = RUNS[name]
    rows = [r for r in jl(folder / "trajectories.jsonl") if (r.get("scan_id"), r.get("style")) in KEYS
            and r.get("lesions") and r.get("cumulative_damage")] if (folder / "trajectories.jsonl").exists() else []
    if not rows:
        continue
    les = sum(r["lesions"]["n_lesions"] for r in rows)
    det = sum(r["lesions"]["detection_loss_events"] for r in rows)
    scans_loss = sum(1 for r in rows if r["lesions"]["any_detection_loss"])
    erased = sum(len(r["lesions"]["initial_lesion_erasure_lesions"]) for r in rows)
    erased5 = sum(len(r["lesions"]["initial_lesion_erasure_persistent_d5_lesions"]) for r in rows)
    dmg = sum(r["cumulative_damage"]["damage_event_ml"] for r in rows)
    pers = sum(r["cumulative_damage"]["damage_persistent_d5_ml"] for r in rows)
    wrong = sum(r["cumulative_damage"]["wrong_at_final_correct_at_start_ml"] for r in rows)
    print(f"{name:14s} {les:7d} {det:11d} {scans_loss:13d} {erased:11d} {erased5:9d} {dmg:12.1f} {pers:13.1f} {wrong:14.1f}")

print("\n== 3. Remote edits (remote.jsonl), sums in ml: T repaired / O repaired / new error beyond each radius")
for name in FULL:
    six, tr, rem = data[name]
    if not rem:
        continue
    for label, rounds in (("r1", {0}), ("r2-5", {1, 2, 3, 4})):
        parts = []
        for radius in (15.0, 30.0, 60.0):
            t = o = e = 0.0
            for (s, st, k), by_r in rem.items():
                if k in rounds and radius in by_r:
                    r = by_r[radius]
                    t += r.get("remote_target_repair_ml") or 0.0
                    o += r.get("remote_same_sign_other_repair_ml") or 0.0
                    e += r.get("remote_new_error_ml") or 0.0
            parts.append(f">{int(radius)}mm T {t:7.1f} O {o:5.1f} new {e:6.1f}")
        total_t = sum((r.get("target_recovery_ml") or 0.0) for (s, st, k), r in tr.items() if k in rounds)
        print(f"{name:8s} {label:5s} T total {total_t:7.1f} | " + " | ".join(parts))

print("\n== 3b. Remote edits split by stroke sign (ml beyond 30 mm and 60 mm): T repaired / new error")
for name in FULL:
    six, tr, rem = data[name]
    if not rem:
        continue
    for label, rounds in (("r1", {0}), ("r2-5", {1, 2, 3, 4})):
        parts = []
        for sign in ("+", "-"):
            for radius in (30.0, 60.0):
                t = e = 0.0
                for (s, st, k), by_r in rem.items():
                    r0 = tr.get((s, st, k))
                    if k in rounds and radius in by_r and r0 and r0.get("sign") == sign:
                        t += by_r[radius].get("remote_target_repair_ml") or 0.0
                        e += by_r[radius].get("remote_new_error_ml") or 0.0
                parts.append(f"{sign}>{int(radius)} T {t:6.1f} new {e:6.1f}")
        print(f"{name:8s} {label:5s} " + " | ".join(parts))

print("\n== 4. Negative scans (no lesion in the reference): false-positive volume, ml")
for name in FULL:
    six = data[name][0]
    neg = [(s, v) for (s, st), v in six.items() if s not in POS]
    fp0 = [v["fp_ml"][0] for s, v in neg if v["fp_ml"][0] is not None]
    fp5 = [v["fp_ml"][5] for s, v in neg if v["fp_ml"][5] is not None]
    if fp0:
        print(f"{name:8s} n={len(neg)} FP@D0 sum {sum(fp0):7.2f} median {statistics.median(fp0):6.3f} | FP@D5 sum "
              f"{sum(fp5):7.2f} median {statistics.median(fp5):6.3f}")

print("\n== 5. Strokes: tiny effect (|T fixed| < 1% of |T| and new error < 0.1 ml), repeats, single-stroke Dice drops")
for name in FULL:
    six, tr, rem = data[name]
    if not tr:
        continue
    strokes = [r for r in tr.values() if not r.get("no_stroke") and r.get("status") == "ok"]
    tiny = [r for r in strokes if (r.get("target_volume_ml") or 0) > 0 and
            (r.get("target_recovery_ml") or 0) < 0.01 * r["target_volume_ml"] and (r.get("new_error_ml") or 0) < 0.1]
    zero_dmg = sum(1 for r in strokes if r.get("zero_recovery_with_damage"))
    drops = []
    for (s, st), v in six.items():
        if s not in POS:
            continue
        d = v["dice"]
        for k in range(5):
            if d[k] is not None and d[k + 1] is not None and d[k + 1] - d[k] <= -0.3:
                drops.append((s, k + 1, round(d[k + 1] - d[k], 3)))
    by_sign = collections.Counter(r["sign"] for r in tiny)
    print(f"{name:8s} strokes {len(strokes):4d}  tiny-effect {len(tiny):3d} (add {by_sign['+']}, remove {by_sign['-']})  "
          f"zero-recovery-with-damage {zero_dmg:3d}  drops<=-0.3: {len(drops)} on {len(set(d[0] for d in drops))} scans")

print("\n== 6. By drawing style: D0 -> D5 (patient mean within the style's scans)")
styles = sorted({st for (s, st) in KEYS})
for name in ["v1flat", "K1", "K2", "K2flip", "oracle"]:
    six = data[name][0]
    parts = []
    for style in styles:
        d0 = {s: v["dice"][0] for (s, st), v in six.items() if st == style and s in POS}
        d5 = {s: v["dice"][5] for (s, st), v in six.items() if st == style and s in POS}
        parts.append(f"{style}: {patient_mean(d0)[0]:.3f}->{patient_mean(d5)[0]:.3f} (n={len(d5)})")
    print(f"{name:8s} " + " | ".join(parts))

print("\n== 7. Seconds per round (latency.jsonl, warm rounds): median model / robot / round")
for name in FULL:
    folder = RUNS[name]
    if not (folder / "latency.jsonl").exists():
        continue
    rows = [r for r in jl(folder / "latency.jsonl") if (r.get("scan_id"), r.get("style")) in KEYS and r.get("phase") == "warm"]
    if rows and any(r.get("model_seconds") is not None for r in rows):
        med = lambda f: statistics.median([r[f] for r in rows if r.get(f) is not None])
        print(f"{name:8s} n={len(rows)} model {med('model_seconds'):.1f}s robot {med('robot_seconds'):.2f}s round {med('round_seconds'):.1f}s")
