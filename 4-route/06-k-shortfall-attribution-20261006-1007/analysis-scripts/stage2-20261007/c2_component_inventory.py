"""c2: component inventory of the SIRB networks: parameter count per module and the input channels of each arm.

Builds every arm on the CPU with NO weights loaded, through the code tree's own builder exactly as the trainer does
(petct_sirb_training._train: ``model = build_sirb_network(resolved, arm_id, plan.seed)``), with the run's own
resolved_config.json and seed 3407.  Nothing is trained or evaluated; no checkpoint, image or mask is opened.

The code tree needs Python >= 3.10 (it uses zip(strict=True)), so run it with the project's local CPU environment:
  D:/Anaconda/envs/petct-sirb310/python.exe -W ignore c2_component_inventory.py > c2_out.txt
"""
import hashlib
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "val-and-train-results")
PROJECT = os.path.abspath(os.path.join(ROOT, "..", "..", ".."))           # projects/petct_textual_intent
CODE = os.path.join(PROJECT, "scripts")
sys.path.insert(0, CODE)

if sys.version_info < (3, 10):
    sys.exit(f"needs Python >= 3.10 for the code tree (zip strict); this is {sys.version.split()[0]}")

import torch  # noqa: E402

torch.set_num_threads(1)
from common.petct_sirb_network import (  # noqa: E402
    HEAD_MODULE_NAMES,
    INTENT_TRANSFER_ZEROED_KEYS,
    build_sirb_network,
    context_token_count,
    parameter_report,
    scaled_encoder_widths,
)
from common.petct_sirb_registry import (  # noqa: E402
    ARM_REGISTRY,
    HISTORY_DELTA_MAPS,
    INTERACTION_FLAG_FEATURES,
    P0_ABSENT_VALUE,
    PROMPT_DENSE_RAW_CHANNELS,
    PROMPT_DENSE_TRUNCATED_CHANNELS,
    STATE_CHANNELS,
)

RUN_DIRS = {
    "N1_STATE": "train-sirb-formal-20260930/N1_STATE",                 # v1 flat
    "N3": "train-sirb-formal-20260930/N3",                             # v1 N3
    "INTENT_FULL": "train-sirb-k-20261006/K1_INTENT_FULL",             # K1
    "INTENT_REFRESH": "train-sirb-k-20261006/K2_INTENT_REFRESH",       # K2
    "INTENT_WIDE": "train-sirb-k-20261006/K3_INTENT_WIDE_partial-20261007",  # K3
}
SHORT = {"N1_STATE": "v1 flat", "N3": "v1 N3", "INTENT_FULL": "K1", "INTENT_REFRESH": "K2", "INTENT_WIDE": "K3"}
SEED = 3407


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# Module groups, by parameter-name prefix (first match wins).  Names are the network's own attribute paths.
GROUPS = [
    ("state encoder: encoder levels (4 levels x 2 residual blocks)", "state.encoder."),
    ("state encoder: up-convolutions", "state.up."),
    ("state encoder: decoder levels", "state.decoder."),
    ("state encoder: 1x1 projection to the 32 decoder features", "state.project."),
    ("global branch: 3 stride-2 stages", "global_encoder.stages."),
    ("global branch: injected map (16 channels)", "global_encoder.inject."),
    ("global branch: token projection to the query size", "global_encoder.token_project."),
    ("fusion of tile and global features", "fuse."),
    ("query encoder: sign embedding", "query.sign."),
    ("query encoder: stroke position MLP", "query.position."),
    ("query encoder: pooled-stroke MLP", "query.mlp."),
    ("query encoder: tile-token projection", "query.tile_token_project."),
    ("query encoder: token position encoder", "query.token_position."),
    ("query encoder: token type embedding", "query.token_type."),
    ("query encoder: cross-attention (2 layers)", "query.attention."),
    ("query encoder: attention norms", "query.attention_norm."),
    ("query encoder: feed-forward (2 layers)", "query.ffn."),
    ("query encoder: feed-forward norms", "query.ffn_norm."),
    ("B2 learnable radius (one scalar, log scale)", "prompt_distance."),
    ("B2 log-distance input layer (zero start)", "flat_head.local.distance_lift."),
    ("B3 history maps input layer (zero start)", "flat_head.local.history_lift."),
    ("B3 interaction-flag FiLM (zero start)", "flat_head.local.history_film."),
    ("flat head: query-dot term", "flat_head.dot."),
    ("flat head: local 1x1 MLP (lift, norm, sign FiLM, output)", "flat_head.local."),
    ("factorized head: error branch (no stroke input)", "error_head."),
    ("factorized head: binding branch (query-dot + local)", "binding_head."),
    ("v2 spatial residual branch", "spatial_head."),
]
SUPER = OrderedDict([
    ("state trunk / encoder", ("state.",)),
    ("global branch", ("global_encoder.",)),
    ("fusion", ("fuse.",)),
    ("prompt / query encoder", ("query.",)),
    ("B2 distance layers (radius + log-distance lift)", ("prompt_distance.", "flat_head.local.distance_lift.")),
    ("B3 history channels (maps lift + flag FiLM)", ("flat_head.local.history_lift.", "flat_head.local.history_film.")),
    ("output head (v1 parts)", ("flat_head.", "error_head.", "binding_head.", "spatial_head.")),
])


def group_of(name):
    for label, prefix in GROUPS:
        if name.startswith(prefix):
            return label
    return "UNGROUPED " + name


def super_of(name):
    for label, prefixes in SUPER.items():
        if any(name.startswith(p) for p in prefixes):
            return label
    return "UNGROUPED"


print("Code tree:", CODE)
print("Python", sys.version.split()[0], "| torch", torch.__version__, "| CPU only, no checkpoint loaded")
print("Files of the code tree used here vs the per-file sha256 that K1's run manifest recorded at training time")
k1_files = read_json(os.path.join(DATA, RUN_DIRS["INTENT_FULL"], "run_manifest.json"))["attempts"][0]["code"]["files"]
for rel in ("scripts/common/petct_sirb_network.py", "scripts/common/petct_sirb_registry.py",
            "scripts/common/petct_sirb_inputs.py", "scripts/common/petct_sirb_config.py",
            "scripts/common/petct_sirb_experiments.py", "scripts/common/petct_sirb_prompt.py",
            "scripts/common/petct_sirb_losses.py", "scripts/common/petct_sirb_dataset.py",
            "scripts/common/petct_sirb_training.py"):
    local = sha256(os.path.join(PROJECT, rel))
    print(f"  {rel:45s} same as K1's training copy: {local == k1_files.get(rel)}"
          + ("" if local == k1_files.get(rel) else f" (local {local[:12]}, recorded {str(k1_files.get(rel))[:12]})"))
exp_dir = os.path.join(PROJECT, "configs", "sirb", "experiments")
for name in sorted(os.listdir(exp_dir)):
    copy = os.path.join(ROOT, "data", "configs", name)
    print(f"  experiment file {name:40s} same as the analysis copy: {sha256(os.path.join(exp_dir, name)) == sha256(copy)}")

models = {}
reports = {}
for arm, rel in RUN_DIRS.items():
    resolved = read_json(os.path.join(DATA, rel, "resolved_config.json"))
    model = build_sirb_network(resolved, arm, SEED)
    models[arm] = model
    reports[arm] = parameter_report(model)

print()
print("=" * 110)
print("1. Totals: built here vs recorded in each run_manifest.json 'parameters'")
print("=" * 110)
for arm, rel in RUN_DIRS.items():
    recorded = read_json(os.path.join(DATA, rel, "run_manifest.json"))["parameters"]
    built = reports[arm]
    same = all(built[k] == recorded[k] for k in ("total_parameters", "trunk_parameters", "head_parameters"))
    print(f"  {SHORT[arm]:7s} {arm:15s} total {built['total_parameters']:>11,d} (manifest {recorded['total_parameters']:>11,d})"
          f"  trunk {built['trunk_parameters']:>11,d} (manifest {recorded['trunk_parameters']:>11,d})"
          f"  head {built['head_parameters']:>7,d} (manifest {recorded['head_parameters']:>7,d})  match={same}")
print("  ('head' = every arm-specific module of network.HEAD_MODULE_NAMES:", HEAD_MODULE_NAMES, ")")

print()
print("=" * 110)
print("2. Parameters per module")
print("=" * 110)
arms = list(RUN_DIRS)
counts = {arm: OrderedDict() for arm in arms}
super_counts = {arm: OrderedDict((k, 0) for k in SUPER) for arm in arms}
for arm in arms:
    for name, p in models[arm].named_parameters():
        counts[arm][group_of(name)] = counts[arm].get(group_of(name), 0) + p.numel()
        super_counts[arm][super_of(name)] = super_counts[arm].get(super_of(name), 0) + p.numel()
labels = [label for label, _ in GROUPS]
print(f"  {'module':62s}" + "".join(f"{SHORT[a]:>13s}" for a in arms))
for label in labels:
    row = [counts[a].get(label, 0) for a in arms]
    if any(row):
        print(f"  {label:62s}" + "".join(f"{v:>13,d}" for v in row))
print(f"  {'TOTAL':62s}" + "".join(f"{sum(counts[a].values()):>13,d}" for a in arms))
print()
print("  Grouped as asked (B2/B3 rows are the K-only layers; 'output head (v1 parts)' is the rest of the head):")
print(f"  {'group':62s}" + "".join(f"{SHORT[a]:>13s}" for a in arms))
for label in SUPER:
    print(f"  {label:62s}" + "".join(f"{super_counts[a].get(label, 0):>13,d}" for a in arms))
ungrouped = [k for a in arms for k in super_counts[a] if k == "UNGROUPED" and super_counts[a][k]]
print("  ungrouped parameters:", ungrouped or "none")
k1, v1 = sum(counts["INTENT_FULL"].values()), sum(counts["N1_STATE"].values())
k3 = sum(counts["INTENT_WIDE"].values())
print(f"\n  K1 - v1 flat = {k1 - v1:,d} parameters (all in the B2/B3 layers); K3 / K1 = {k3 / k1:.3f}")

print()
print("=" * 110)
print("3. Sizes that differ between the arms")
print("=" * 110)
for arm in arms:
    m = models[arm]
    spec = ARM_REGISTRY[arm]
    widths = list(m.state.widths)
    print(f"  {SHORT[arm]:7s} state-encoder widths {widths} (trunk_width_scale {spec.trunk_width_scale}); "
          f"decoder features {m.state.project.out_channels}; query dim {m.query.mlp[-1].out_features}; "
          f"global widths {[s[0].out_channels for s in m.global_encoder.stages]}; head kind {spec.head}")
    if m.prompt_distance is not None:
        print(f"          learnable radius: R = {m.prompt_distance.initial_radius_mm} mm x exp(s), s starts at "
              f"{float(m.prompt_distance.log_radius_scale):.1f} (stage 1, a11: trained s gives R = 61.04 mm K1, "
              f"61.01 mm K2)")
resolved = read_json(os.path.join(DATA, RUN_DIRS["N1_STATE"], "resolved_config.json"))
net_cfg = resolved["science"]["network"]
groups = int(resolved["implementation"]["network"]["groupnorm_groups"])
print(f"  scaled_encoder_widths({net_cfg['encoder_widths_proposed']}, 1.5, {groups}) = "
      f"{scaled_encoder_widths(net_cfg['encoder_widths_proposed'], 1.5, groups)}")
print(f"  attention context: {context_token_count(resolved['science'])} tokens (8x8x8 global + 12x12x12 tile cells "
      f"of a 96^3 tile)")

print()
print("=" * 110)
print("4. Same start? Shared parameters of K1 vs v1 flat built with the same seed (the trainer builds with seed 3407)")
print("=" * 110)
for a, b in (("INTENT_FULL", "N1_STATE"), ("INTENT_REFRESH", "INTENT_FULL"), ("INTENT_WIDE", "INTENT_FULL"),
             ("N3", "N1_STATE")):
    sa, sb = models[a].state_dict(), models[b].state_dict()
    common = [k for k in sa if k in sb and sa[k].shape == sb[k].shape]
    differ = [k for k in common if not torch.equal(sa[k], sb[k])]
    only_a = [k for k in sa if k not in sb]
    shape_differ = [k for k in sa if k in sb and sa[k].shape != sb[k].shape]
    print(f"  {SHORT[a]} vs {SHORT[b]}: tensors in common with equal shape {len(common)}, of which bit-different "
          f"{len(differ)}; only in {SHORT[a]} {len(only_a)}; same name but other shape {len(shape_differ)}")
    if differ[:4]:
        print(f"      first different: {differ[:4]}")
    if only_a:
        print(f"      only in {SHORT[a]}: {only_a}")
sd = models["INTENT_FULL"].state_dict()
print("  values of the K-only tensors at build time (all must be 0, so K1 starts as the v1 function):")
for key in INTENT_TRANSFER_ZEROED_KEYS:
    print(f"      {key:45s} shape {tuple(sd[key].shape)!s:18s} max |value| {float(sd[key].abs().max()):.1f}")

print()
print("=" * 110)
print("5. Input channels per arm (code: registry STATE_CHANNELS / PROMPT_DENSE_* / HISTORY_DELTA_MAPS / "
      "INTERACTION_FLAG_FEATURES)")
print("=" * 110)
for arm in arms:
    spec = ARM_REGISTRY[arm]
    print(f"\n  {SHORT[arm]} ({arm}):")
    state = []
    for ch in STATE_CHANNELS:
        note = f"blanked to {P0_ABSENT_VALUE} inside the network (use_p0={spec.use_p0})" if ch == "p0" and not \
            spec.use_p0 else "on"
        state.append(f"{ch} [{note}]")
    print(f"    state encoder and global branch ({len(STATE_CHANNELS)} channels, global branch use_global="
          f"{spec.use_global}): " + "; ".join(state))
    print("    query encoder: current-stroke points (features sampled at the exact stroke coordinates on feature levels "
          "0-3, mean+max pooled), sign embedding (ADD/REMOVE), 9-number stroke position code; attends to the global "
          "tokens and the anchor tile's deepest-level tokens")
    if spec.distance_mode == "truncated":
        print(f"    head dense prompt input (computed on the CPU): {list(PROMPT_DENSE_TRUNCATED_CHANNELS)} = "
              "[1 - min(d, 60 mm)/60, occupancy]; every voxel farther than 60 mm reads 0")
    else:
        print(f"    head dense prompt input delivered: {list(PROMPT_DENSE_RAW_CHANNELS)} (distance NOT truncated); the "
              "network turns it into [1 - min(d, R)/R with learnable R (start 60 mm), occupancy] for the same head "
              "inputs, and feeds log(1 + d / voxel edge) through the zero-start distance layer")
    if spec.history_delta:
        print(f"    B3 history: maps {list(HISTORY_DELTA_MAPS)} -> zero-start 1x1 layer into the head's hidden layer; "
              f"{len(INTERACTION_FLAG_FEATURES)} flags {list(INTERACTION_FLAG_FEATURES)} -> zero-start FiLM; both are "
              "all-zero for an offline-bank state (flags_valid 0) and for round 1 at inference")
    else:
        print("    B3 history inputs: none")
    print(f"    switches: error_reads_prompt={spec.error_reads_prompt} spatial_residual={spec.spatial_residual!r} "
          f"state_loss={spec.state_loss} state_change_on={spec.state_change_on!r} far_block={spec.far_block} "
          f"edit_contract={spec.edit_contract} pair_relations={spec.pair_relations} loss_alignment="
          f"{spec.loss_alignment!r} pool_mix={spec.pool_mix!r} trunk_width_scale={spec.trunk_width_scale}")
print("\n  Not wired in any arm: the multi-scale occupancy pyramid (network.py comment: heads read level 0 only; "
      "the query samples every level at the stroke coordinates).")
print("\nDone.")
