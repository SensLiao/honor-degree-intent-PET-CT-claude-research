"""Shared paths for the stage-2 scripts: every input is read from this folder's data/ copy."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data" / "val-and-train-results"
TEST = ROOT / "data" / "test-results"
OUT = HERE

#: VAL rollout folders (99 scans / 57 patients; quick VAL = each scan its one frozen style).
RUNS = {
    "v1flat": DATA / "eval-sirb-batch1-val-20260925/rollout/N1_STATE-s3407",
    "v1N3": DATA / "eval-sirb-batch1-val-20260925/rollout/N3-s3407",
    "oracle": DATA / "eval-sirb-batch1-val-20260925/rollout/oracle",
    "noop": DATA / "eval-sirb-batch1-val-20260925/rollout/noop",
    "K1": DATA / "eval-sirb-v3-quickval-INTENT_FULL-R1-20261006",
    "K2": DATA / "eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006",
    "K2flip": DATA / "eval-sirb-v3-quickval-flip-INTENT_REFRESH-R1-20261006",
    "K1flip": DATA / "eval-sirb-v3-quickval-flip-INTENT_FULL-R1-20261006",
    "cont_static": DATA / "eval-sirb-v2-quickval-N1_STATE_STATIC-R1-20261003",
    "cont_induced": DATA / "eval-sirb-v2-quickval-N1_STATE_INDUCED-R1-20261003",
    "cont_induced_flip": DATA / "eval-sirb-v3-quickval-flip-N1_STATE_INDUCED-R1-20261005",
    "cont_spatial": DATA / "eval-sirb-v2-quickval-N1_STATE_SPATIAL-R1-20261004",
    "cont_N3ES": DATA / "eval-sirb-v2-quickval-N3_ES-R1-20261004",
    "cont_N4": DATA / "eval-sirb-v2-quickval-N4_STATIC-R1-20261003",
    "groupA_induced": DATA / "eval-sirb-v3-intent-quickval-N1_STATE_INDUCED-R1-20261005",
    "weightavg": DATA / "eval-sirb-v3-quickval-weightavg-N1_STATE-STATIC-INDUCED-R1-20261005",
}
