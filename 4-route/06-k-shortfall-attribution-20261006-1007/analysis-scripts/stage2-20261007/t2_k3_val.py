"""K3 (INTENT_WIDE, trunk 1.5x) network-alone VAL against v1 flat, K1 and K2: D0..D5, nAUC, paired D5 intervals and the
five-round gain by stroke sign.  K3's VAL is read from the canonical local copy records/development_results_transfer/
(collected 10-07 10:31, sha256 checked); the others from the canonical stores, see b0_paths.  VAL only."""
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b0_paths  # noqa: E402
from b0_load import POS, load, paired_bootstrap, patient_mean  # noqa: E402

TRANSFER = HERE.parents[4] / "petct_textual_intent" / "records" / "development_results_transfer"
b0_paths.RUNS["K3"] = TRANSFER / "eval-sirb-v3-quickval-INTENT_WIDE-R1-20261006"
names = ["v1flat", "K1", "K2", "K3"]
data = {n: load(n, remote=False) for n in names}


def nauc(d):
    return (0.5 * d[0] + d[1] + d[2] + d[3] + d[4] + 0.5 * d[5]) / 5.0


def scan_values(six, fn):
    return {s: fn(v["dice"]) for (s, st), v in six.items() if s in POS and None not in v["dice"]}


print("== VAL Dice by round (patient mean over positive scans)")
for n in names:
    six = data[n][0]
    ds = [patient_mean(scan_values(six, lambda d, k=k: d[k]))[0] for k in range(6)]
    print(f"  {n:7s} " + " ".join(f"D{k} {x:.4f}" for k, x in enumerate(ds))
          + f"  nAUC {patient_mean(scan_values(six, nauc))[0]:.4f}")
a = scan_values(data["K3"][0], lambda d: d[5])
for ref in ("v1flat", "K1", "K2"):
    b = scan_values(data[ref][0], lambda d: d[5])
    common = set(a) & set(b)
    diff, lo, hi, npat = paired_bootstrap({s: a[s] for s in common}, {s: b[s] for s in common})
    print(f"  K3 minus {ref:6s} D5 {diff:+.4f} [{lo:+.4f}, {hi:+.4f}] ({npat} patients)")

print("\n== Five-round Dice gain split by stroke sign")
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
    print(f"  {n:7s} add {totals['+']:+.4f}  remove {totals['-']:+.4f}")
