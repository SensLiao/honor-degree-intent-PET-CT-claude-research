"""Patient bootstrap 95% percentile interval of the round-5 Dice (10,000 draws, seed 3407), as in the T083 K table."""
import csv, collections, os
import numpy as np
ROOT = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer"
for name in ["eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006", "eval-sirb-v3-quickval-INTENT_FULL-R1-20261006",
             "eval-sirb-v3-quickval-flip-INTENT_REFRESH-R1-20261006"]:
    by = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(ROOT, name, "six_state.csv"), newline="")):
        if r["gt_positive"] == "True" and r["round"] == "5":
            by[r["patient_id"]].append(float(r["dice"]))
    pm = np.array([np.mean(v) for v in by.values()])
    rng = np.random.default_rng(3407)
    boot = pm[rng.integers(0, len(pm), size=(10000, len(pm)))].mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print("%-55s D5 %.4f  95%% %.3f-%.3f  n=%d" % (name, pm.mean(), lo, hi, len(pm)))
