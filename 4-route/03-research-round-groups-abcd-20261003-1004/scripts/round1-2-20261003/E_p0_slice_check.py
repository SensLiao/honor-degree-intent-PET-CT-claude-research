"""E_ one-off (read-only, CPU): are the p0 input filters of a network that never read p0 still at their seeded init?

Builds the formal-plan network of an arm at seed 3407 (the trainer builds it exactly so: torch.manual_seed(seed) then
build_sirb_network) and compares, input channel by input channel, the first-layer weights with a trained 12k prototype
checkpoint from the local data hub (E16_N1_STATE: flat + state loss, p0 blanked; E16_N2_P0: reads p0).  Also prints the
parameter counts of the candidate additions.  Opens no data and no label; writes nothing.
"""
import sys
from pathlib import Path

import torch

PROJECT = Path(r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent")
sys.path.insert(0, str(PROJECT / "scripts"))

from common.petct_sirb_config import resolve_from_files  # noqa: E402
from common.petct_sirb_network import build_sirb_network, parameter_report  # noqa: E402
from common.petct_sirb_registry import STATE_CHANNELS  # noqa: E402

HUB = Path(r"D:/honor-petct-data-hub/z390/prototypes/editor-sirb-mainline-20260920-R1/runs-pilot")
RUNS = {"E16_N1_STATE": "PETCT-EDITOR-SIRB-E16_N1_STATE-S3407-TRAIN-20260924-R1",
        "E16_N2_P0": "PETCT-EDITOR-SIRB-E16_N2_P0-S3407-TRAIN-20260925-R1"}
FIRST_LAYERS = ("state.encoder.0.0.conv1.weight", "state.encoder.0.0.skip.0.weight", "global_encoder.stages.0.0.weight")


def main() -> None:
    torch.set_num_threads(2)
    resolved = resolve_from_files()
    for arm, run in RUNS.items():
        torch.manual_seed(3407)
        init = build_sirb_network(resolved, arm, 3407).state_dict()
        payload = torch.load(HUB / run / "checkpoints" / "final.pt", map_location="cpu", weights_only=False)
        trained = payload["model"]
        print(f"== {arm} step={payload['step']} identity arm_spec={payload['identity'].get('arm_spec')}")
        for key in FIRST_LAYERS:
            a, b = init[key], trained[key]
            for channel, name in enumerate(STATE_CHANNELS):
                drift = (b[:, channel] - a[:, channel]).abs().max().item()
                scale = a[:, channel].abs().max().item()
                print(f"  {key:36s} ch{channel} {name:17s} max|trained-init|={drift:.3e} (init max|w|={scale:.3e})")
    model = build_sirb_network(resolved, "N1_STATE", 3407)
    print("N1_STATE parameters", parameter_report(model))
    for key in ("state.encoder.0.0.conv1.weight", "state.encoder.0.0.skip.0.weight", "global_encoder.stages.0.0.weight",
                "flat_head.local.lift.weight"):
        print("  shape", key, tuple(model.state_dict()[key].shape))


if __name__ == "__main__":
    sys.exit(main())
