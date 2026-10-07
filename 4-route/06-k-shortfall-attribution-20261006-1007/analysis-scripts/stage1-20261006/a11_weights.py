"""Needs k1_final.pt and k2_final.pt copied from the servers next to this file (not kept here, 80 MB each).
CPU-only read of two learned scalars/weight norms in the K final checkpoints (no patient data)."""
import torch
for name in ("k1_final.pt", "k2_final.pt"):
    ck = torch.load(name, map_location="cpu", weights_only=False)
    keys = list(ck.keys()) if isinstance(ck, dict) else []
    sd = None
    for k in ("model_state_dict", "model", "state_dict", "network"):
        if isinstance(ck, dict) and k in ck and isinstance(ck[k], dict):
            sd = ck[k]
            break
    if sd is None:
        print(name, "top keys", keys[:20]); continue
    s = sd.get("prompt_distance.log_radius_scale")
    print(name, "step", ck.get("step"), "| learned radius scale s =", None if s is None else float(s),
          "-> R =", None if s is None else 60.0 * float(torch.exp(s)), "mm")
    for k, v in sd.items():
        if any(t in k for t in ("distance_lift", "history_lift", "history_film")):
            print("   %-55s shape %-18s |w| mean %.5f max %.5f" % (k, tuple(v.shape), v.abs().mean().item(), v.abs().max().item()))
