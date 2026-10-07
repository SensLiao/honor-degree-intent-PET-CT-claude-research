"""Data description from local TRAIN/VAL files only: native voxel spacing and shape (case-cache meta.json, 506),
lesion burden per scan (VAL from the rollout trajectories' GT lesion list; TRAIN from the six-state Dice identity),
start-state errors.  No TEST image or label is read."""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import DEV, ROLL, ARMS, six_state, read_jsonl, gt_ml, summary_stats, mean, dump, quantile

CACHE = Path("D:/honor-petct-data-hub/z390/cache-inputs/dataset-sirb-cases-gen-20260919-R2/cache/inputs")
sp = collections.Counter()
sp_split = collections.defaultdict(collections.Counter)
shapes = []
for meta_path in sorted(CACHE.glob("*/meta.json")):
    m = json.load(open(meta_path, encoding="utf-8"))
    A = m["affine_dhw"]
    import math
    spacing = tuple(round(math.sqrt(sum(A[r][c] ** 2 for r in range(3))), 3) for c in range(3))  # per array axis d,h,w
    sp[spacing] += 1
    sp_split[m["split"]][spacing] += 1
    shapes.append(m["native_shape_dhw"])
out = {"spacing_dhw_mm_counts": {str(k): v for k, v in sp.most_common()},
       "spacing_by_split": {s: {str(k): v for k, v in c.most_common()} for s, c in sp_split.items()},
       "native_shape_d": summary_stats(s[0] for s in shapes)}

# VAL lesion burden from trajectories (GT lesions, 18-connected)
les = {}
for t in read_jsonl(ROLL / ARMS["flat"] / "trajectories.jsonl"):
    L = t.get("lesions") or {}
    vols = [float(x["volume_ml"]) for x in L.get("lesions", [])]
    les[t["scan_id"]] = vols
pos_val = [s for s, v in les.items() if v]
out["VAL_lesions"] = {"positive_scans": len(pos_val), "negative_scans": sum(1 for v in les.values() if not v),
                      "gt_ml_per_positive_scan": summary_stats(sum(les[s]) for s in pos_val),
                      "lesions_per_positive_scan": summary_stats(len(les[s]) for s in pos_val),
                      "lesion_volume_ml_all": summary_stats(v for s in pos_val for v in les[s]),
                      "share_lesions_lt_0.5ml": sum(1 for s in pos_val for v in les[s] if v < 0.5) / sum(len(les[s]) for s in pos_val),
                      "share_lesions_lt_0.1ml": sum(1 for s in pos_val for v in les[s] if v < 0.1) / sum(len(les[s]) for s in pos_val)}

# TRAIN lesion burden (GT volume via the round-0 Dice identity on the oracle six-state table)
d, pat, pos = six_state(DEV / "eval-segbase-fivefold-val-repair-upper-20260930" / "server-originals" / "rollout-train" / "six_state.csv")
gt_train = {}
for k, r in d.items():
    if pos[k] and k[0] not in gt_train:
        g = gt_ml(r[0])
        if g is not None:
            gt_train[k[0]] = g
out["TRAIN_gt_ml_per_positive_scan"] = summary_stats(gt_train.values())
# VAL the same way for a like-for-like comparison
dv, patv, posv = six_state(ROLL / ARMS["oracle"] / "six_state.csv")
gt_val = {}
for k, r in dv.items():
    if posv[k] and k[0] not in gt_val:
        g = gt_ml(r[0])
        if g is not None:
            gt_val[k[0]] = g
out["VAL_gt_ml_per_positive_scan_identity"] = summary_stats(gt_val.values())

# start-state errors (VAL): FP/FN at D0 per positive scan
fp0 = [dv[(s, "centerline")][0]["fp_ml"] for s in gt_val]
fn0 = [dv[(s, "centerline")][0]["fn_ml"] for s in gt_val]
out["VAL_start_fp_ml"] = summary_stats(fp0)
out["VAL_start_fn_ml"] = summary_stats(fn0)
out["VAL_start_d0_zero_scans"] = sum(1 for s in gt_val if dv[(s, "centerline")][0]["dice"] == 0.0)
dump(out, Path(__file__).with_suffix(".json"))
print(json.dumps(out, indent=1, ensure_ascii=False)[:5000])
