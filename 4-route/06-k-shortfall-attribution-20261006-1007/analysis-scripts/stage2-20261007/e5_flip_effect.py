"""What left-right flip averaging changes for each network (VAL): round-1 add/remove volumes and the five-round gain split
by stroke sign, network alone vs with flip.  Flip averages the two views' logits, which pulls scores near the 0.5 line
toward their mean: for a network whose T scores sit just under 0.5 it can lower the fill."""
import collections

from b0_load import POS, load, patient_mean

PAIRS = [("K1", "K1flip"), ("K2", "K2flip"), ("cont_induced", "cont_induced_flip")]
for a, b in PAIRS:
    for name in (a, b):
        six, tr, _ = load(name)
        if not tr:
            d5 = patient_mean({s: v["dice"][5] for (s, st), v in six.items() if s in POS})[0]
            print(f"{name:18s} D5 {d5:.4f} (no transitions table)")
            continue
        gains = collections.Counter()
        for k in range(5):
            for sign in ("+", "-"):
                vals = {}
                for (s, st), v in six.items():
                    if s not in POS or None in v["dice"]:
                        continue
                    r = tr.get((s, st, k))
                    hit = r is not None and not r.get("no_stroke") and r.get("sign") == sign
                    vals[s] = (v["dice"][k + 1] - v["dice"][k]) if hit else 0.0
                gains[sign] += patient_mean(vals)[0]
        r1add = [r for (s, st, k), r in tr.items() if k == 0 and r.get("sign") == "+" and not r.get("no_stroke")]
        r1rem = [r for (s, st, k), r in tr.items() if k == 0 and r.get("sign") == "-" and not r.get("no_stroke")]
        d5 = patient_mean({s: v["dice"][5] for (s, st), v in six.items() if s in POS})[0]
        print(f"{name:18s} D5 {d5:.4f}  gain add {gains['+']:+.4f} remove {gains['-']:+.4f} | r1 add T fixed "
              f"{sum(r['target_recovery_ml'] for r in r1add):6.1f} FP {sum(r['fp_added_ml'] for r in r1add):6.1f} | "
              f"r1 remove T fixed {sum(r['target_recovery_ml'] for r in r1rem):6.1f} TP lost {sum(r['tp_lost_ml'] for r in r1rem):5.1f}")
