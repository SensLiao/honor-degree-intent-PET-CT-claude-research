import json, statistics
V1 = r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-formal-20260930/N1_STATE/metrics.jsonl"
def rows(p, last=100):
    out = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip().startswith("{")]
    return out[-last:]
for name, p in [("v1flat", V1), ("K1", "k1_metrics_tail.jsonl"), ("K2", "k2_metrics_tail.jsonl")]:
    r = rows(p)
    ks = sorted(k for k in r[-1] if (k.startswith("base_") or k.startswith("intent_") or k in ("total", "state_total", "state_weight")) and not k.endswith("_count"))
    print(name, "  ".join("%s=%.4f" % (k, statistics.mean(x[k] for x in r if x.get(k) is not None)) for k in ks))
    g = sorted(k for k in r[-1] if k.startswith("grad_norm_"))
    if g:
        print("   grads:", "  ".join("%s=%.3f" % (k[10:], statistics.mean(x[k] for x in r if x.get(k) is not None)) for k in g))
    w = sorted(k for k in r[-1] if "weight" in k or "multiplier" in k or "calib" in k)
    print("   weights:", {k: r[-1][k] for k in w})
