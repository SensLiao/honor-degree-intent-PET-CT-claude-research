import json, statistics
V1 = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-formal-20260930/N1_STATE/metrics.jsonl"
def rows(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip().startswith("{")]
R = {"v1flat": rows(V1), "K1": rows(r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-k-20261006/K1_INTENT_FULL/metrics.jsonl"), "K2": rows(r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-k-20261006/K2_INTENT_REFRESH/metrics.jsonl")}
keys = ["pool_offline", "pool_on_policy", "pool_share_gap", "pool_share_natural", "relation_none", "relation_same_scope",
        "relation_swap", "pair_type_bridge", "pair_type_other_error", "pair_type_peripheral", "pair_fallback",
        "sampled_target", "sampled_other", "sampled_preserve_near", "sampled_preserve_far", "sampled_preserve_hard",
        "intent_hard_negative_count", "intent_ring_rank_count", "intent_dice_gain_count", "intent_pair_swap_count", "intent_pair_same_scope_count",
        "diag_other_voxels", "diag_binding_accuracy_in_error", "state_change"]
windows = [(0, 10000), (10000, 25000), (25000, 40001)]
for k in keys:
    line = "%-30s" % k
    for name, r in R.items():
        for lo, hi in windows:
            v = [x[k] for x in r if lo < x["step"] <= hi and isinstance(x.get(k), (int, float))]
            line += " %9.3f" % statistics.mean(v) if v else "        - "
        line += " |"
    print(line)
print("columns: v1flat(0-10k,10-25k,25-40k) | K1(...) | K2(...)")
