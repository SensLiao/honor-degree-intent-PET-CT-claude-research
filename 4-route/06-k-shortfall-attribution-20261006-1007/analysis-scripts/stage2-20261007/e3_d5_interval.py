"""Patient-bootstrap 95% interval of the D5 patient mean of each K run (VAL; 10,000 draws, seed 3407; same method as
stage1 a7_ci.py), for the T083 table."""
import random

from b0_load import load, per_patient, POS

for name in ("K1", "K1flip", "K2", "K2flip", "v1flat"):
    six = load(name, transitions=False, remote=False)[0]
    d5 = per_patient({s: v["dice"][5] for (s, st), v in six.items() if s in POS})
    vals = list(d5.values())
    rng = random.Random(3407)
    n = len(vals)
    boots = sorted(sum(vals[rng.randrange(n)] for _ in range(n)) / n for _ in range(10000))
    print(f"{name:7s} D5 {sum(vals) / n:.4f} [{boots[250]:.3f}, {boots[9749]:.3f}] n={n}")
