import json, statistics
V1 = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-formal-20260930/N1_STATE/metrics.jsonl"
def rows(p, last=100):
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line.startswith("{"):
            out.append(json.loads(line))
    return out[-last:]
keys = ["diag_hard_dice_target", "diag_target_recall", "diag_binding_accuracy_in_error", "diag_error_gate_recall",
        "diag_preserve_edit_voxels", "diag_target_voxels", "diag_other_voxels", "sampled_target"]
for name, p in [("v1flat", V1), ("K1", "k1_metrics_tail.jsonl"), ("K2", "k2_metrics_tail.jsonl")]:
    r = rows(p)
    print("%-7s steps %d-%d" % (name, r[0]["step"], r[-1]["step"]))
    for k in keys:
        v = [x[k] for x in r if k in x and x[k] is not None]
        if v:
            print("   %-32s mean %10.4f" % (k, statistics.mean(v)))
    extra = sorted(k for k in r[-1] if k.startswith("base_") or k.startswith("loss_") or k.startswith("intent") or k.startswith("b1") or k.startswith("edit") or k.startswith("dice_gain") or k.startswith("pair"))
    print("   other keys:", extra[:40])
