import json, statistics
V1 = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-formal-20260930/N1_STATE/metrics.jsonl"
def rows(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip().startswith("{")]
R = {"v1flat": rows(V1), "K1": rows(r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-k-20261006/K1_INTENT_FULL/metrics.jsonl"), "K2": rows(r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-k-20261006/K2_INTENT_REFRESH/metrics.jsonl")}
keys = ["diag_target_recall", "diag_hard_dice_target", "diag_error_gate_recall", "diag_preserve_edit_voxels",
        "diag_target_voxels", "far_block_placed", "intent_dice_gain", "intent_hard_negative", "intent_ring_rank", "base_target_dice", "base_error", "base_preserve"]
windows = [(0, 1000), (1000, 2000), (2000, 5000), (5000, 10000), (10000, 15000), (15000, 25000), (25000, 30000), (30000, 35000), (35000, 40001)]
for k in keys:
    print("==", k)
    for name, r in R.items():
        vals = []
        for lo, hi in windows:
            v = [x[k] for x in r if lo < x["step"] <= hi and x.get(k) is not None]
            vals.append("%8.3f" % statistics.mean(v) if v else "     -  ")
        print("  %-7s %s" % (name, " ".join(vals)))
print("windows:", windows)
