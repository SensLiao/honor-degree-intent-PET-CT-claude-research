"""Two-stage data flow check (TRAIN/VAL only; no TEST image or label is read).

Reads the 506 local case-cache meta.json files (D:/honor-petct-data-hub, byte copies of the z390 SIRB case cache):
SIRB split (train/val), held-out segmentation-base fold, state source and the p0 path.  Checks:
  1. every TRAIN/VAL start state is out-of-fold (p0 path fold == held_out_fold, state_source segbase_out_of_fold);
  2. TRAIN and VAL are patient-disjoint;
  3. for each base fold model (trained on the other four folds): how many SIRB VAL scans/patients it was trained on,
     and how many TRAIN scans got their start state from it;
  4. the 2S-ICR fold0/fold1 VAL case lists equal base folds 0/1 held-out lists;
  5. the locked TEST patients (IDs only, from the archived SIRB TEST six_state.csv) are absent from the 506 pool.
"""
import collections
import csv
import glob
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import DEV, TST, dump

CACHE = Path("D:/honor-petct-data-hub/z390/cache-inputs/dataset-sirb-cases-gen-20260919-R2/cache/inputs")
cases = {}
problems = []
for meta_path in sorted(CACHE.glob("*/meta.json")):
    m = json.load(open(meta_path, encoding="utf-8"))
    prov = m.get("provenance", {})
    ver = prov.get("verified_against_frozen_documents", {})
    p0_path = prov.get("source_paths", {}).get("p0", "")
    fold = ver.get("held_out_fold")
    mo = re.search(r"/fold_(\d)/", p0_path)
    p0_fold = int(mo.group(1)) if mo else None
    cases[m["case_id"]] = {"patient": m["patient_id"], "split": m["split"], "fold": fold, "p0_fold": p0_fold,
                           "state_source": ver.get("state_source"), "m0_rule": m.get("m0_rule"),
                           "m0_disagree": m.get("m0_voxels_disagreeing_with_rule"),
                           "oof_run": "PETCT-M0-V6-OOF-20260817-R1" in p0_path}
    if fold is None or p0_fold != fold:
        problems.append((m["case_id"], "p0 fold mismatch", fold, p0_fold))
    if ver.get("state_source") != "segbase_out_of_fold":
        problems.append((m["case_id"], "state source", ver.get("state_source")))

out = {"cases": len(cases), "problems": problems}
split_counts = collections.Counter(c["split"] for c in cases.values())
out["split_scans"] = dict(split_counts)
pat_split = collections.defaultdict(set)
for c in cases.values():
    pat_split[c["patient"]].add(c["split"])
out["split_patients"] = dict(collections.Counter(next(iter(s)) if len(s) == 1 else "MIXED" for s in pat_split.values()))
out["patients_in_both_train_and_val"] = sum(1 for s in pat_split.values() if len(s) > 1)
out["all_from_oof_run"] = all(c["oof_run"] for c in cases.values())
out["m0_rule"] = dict(collections.Counter(c["m0_rule"] for c in cases.values()))
out["m0_voxels_disagreeing_max"] = max(c["m0_disagree"] or 0 for c in cases.values())

# fold x split table
tab = collections.defaultdict(lambda: collections.Counter())
tabp = collections.defaultdict(lambda: collections.defaultdict(set))
for cid, c in cases.items():
    tab[c["fold"]][c["split"]] += 1
    tabp[c["fold"]][c["split"]].add(c["patient"])
out["fold_split_scans"] = {f: dict(v) for f, v in sorted(tab.items())}
out["fold_split_patients"] = {f: {s: len(p) for s, p in v.items()} for f, v in sorted(tabp.items())}
# patient-disjointness of folds
pat_folds = collections.defaultdict(set)
for c in cases.values():
    pat_folds[c["patient"]].add(c["fold"])
out["patients_spanning_two_folds"] = sum(1 for f in pat_folds.values() if len(f) > 1)

# exposure: base fold model k is trained on folds != k
val_scans = {cid for cid, c in cases.items() if c["split"] == "val"}
val_pats = {c["patient"] for c in cases.values() if c["split"] == "val"}
exp = {}
for k in sorted(tab):
    trained_on = {cid for cid, c in cases.items() if c["fold"] != k}
    exp[k] = {"model_trained_on_scans": len(trained_on),
              "val_scans_in_its_training": len(trained_on & val_scans),
              "val_patients_in_its_training": len({cases[c]["patient"] for c in trained_on & val_scans}),
              "train_scans_it_produced_start_for": sum(1 for c in cases.values() if c["fold"] == k and c["split"] == "train"),
              "val_scans_it_produced_start_for": sum(1 for c in cases.values() if c["fold"] == k and c["split"] == "val")}
out["base_fold_exposure"] = exp
out["train_scans_whose_start_model_saw_some_val_labels"] = sum(
    1 for c in cases.values() if c["split"] == "train" and exp[c["fold"]]["val_scans_in_its_training"] > 0)

# 2S-ICR fold0/fold1 VAL lists vs base folds
for f in (0, 1):
    listed = {Path(p).stem for p in glob.glob(str(DEV / f"baseline-2sicr-fold{f}-val-20261003" / "cases" / "*.json"))}
    base = {cid for cid, c in cases.items() if c["fold"] == f}
    out[f"2sicr_fold{f}_val_equals_base_fold"] = {"listed": len(listed), "base": len(base), "equal": listed == base,
                                                  "sirb_val_overlap": len(listed & val_scans),
                                                  "sirb_train_overlap": len(listed - val_scans)}

# SIRB VAL rollout case list equals cache VAL
rows = list(csv.DictReader(open(DEV / "eval-sirb-batch1-val-20260925" / "rollout" / "N1_STATE-s3407" / "six_state.csv", encoding="utf-8")))
out["sirb_val_rollout_equals_cache_val"] = {r["scan_id"] for r in rows} == val_scans
# TRAIN oracle reference covers the 407 TRAIN scans
rows = list(csv.DictReader(open(DEV / "eval-segbase-fivefold-val-repair-upper-20260930" / "server-originals" / "rollout-train" / "six_state.csv", encoding="utf-8")))
out["train_oracle_equals_cache_train"] = {r["scan_id"] for r in rows} == {cid for cid, c in cases.items() if c["split"] == "train"}

# TEST patients (IDs only) vs the 506 pool
rows = list(csv.DictReader(open(TST / "eval-sirb-lockedtest-20260928-R1" / "server-originals" / "N1_STATE-s3407" / "segbase-fivefold-mean" / "rollout" / "six_state.csv", encoding="utf-8")))
test_pats = {r["patient_id"] for r in rows}
test_scans = {r["scan_id"] for r in rows}
pool_pats = {c["patient"] for c in cases.values()}
out["test"] = {"scans": len(test_scans), "patients": len(test_pats), "patient_overlap_with_pool": len(test_pats & pool_pats),
               "scan_overlap_with_pool": len(test_scans & set(cases))}

dump(out, Path(__file__).with_suffix(".json"))
print(json.dumps({k: v for k, v in out.items() if k != "problems"}, indent=1, ensure_ascii=False))
print("problems:", len(problems), problems[:5])
