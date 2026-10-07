"""c3: configuration and arm-spec differences between v1 flat, K1, K2 and K3 (v1 N3 as an extra column), plus the
training exposure each run received.

Reads (read-only): resolved_config.json, run_manifest.json and metrics.jsonl of each run under <code tree>/records/development_results_transfer,
and a few named constants from the code tree source (text only, nothing imported).
Run from this folder:  D:/Anaconda/python.exe -W ignore c3_config_diff.py > c3_out.txt
"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # the stage folder
PROJECT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(ROOT))), "petct_textual_intent")
DATA = os.path.join(PROJECT, "records", "development_results_transfer")
RUNS = {
    "v1 flat": "train-sirb-formal-20260930/N1_STATE",
    "K1": "train-sirb-k-20261006/K1_INTENT_FULL",
    "K2": "train-sirb-k-20261006/K2_INTENT_REFRESH",
    "K3": "train-sirb-k-20261006/K3_INTENT_WIDE_partial-20261007",
    "v1 N3": "train-sirb-formal-20260930/N3",
}
ORDER = list(RUNS)
COUNT_PREFIXES = ("pair_type_", "pool_", "sampled_", "relation_", "far_block_")
TRAIN_SPLIT_FROM_VAULT = ("vault wiki/tasks/petct-t076-sirb-episode-pair-generation.md: TRAIN main corpus (09-20) = 407 "
                          "scans, 7,414 episodes, 17,872 pairs, sha 2b65638f... (the offline pool every run reads)")


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def flatten(node, prefix=""):
    out = {}
    if isinstance(node, dict):
        for key, value in node.items():
            out.update(flatten(value, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(node, list) and node and all(isinstance(v, dict) for v in node):
        for i, value in enumerate(node):
            out.update(flatten(value, f"{prefix}[{i}]"))
    else:
        out[prefix] = node
    return out


def short(value, width=34):
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return text if len(text) <= width else text[:width - 3] + "..."


def heading(text):
    print()
    print("=" * 120)
    print(text)
    print("=" * 120)


def table(rows, labels=ORDER, width=34, key_width=58):
    print(f"  {'field':{key_width}s}" + "".join(f"{lab:>{width + 2}s}" for lab in labels))
    for key, values in rows:
        print(f"  {key[:key_width]:{key_width}s}" + "".join(f"{short(v, width):>{width + 2}s}" for v in values))


resolved = {label: read_json(os.path.join(DATA, rel, "resolved_config.json")) for label, rel in RUNS.items()}
manifest = {label: read_json(os.path.join(DATA, rel, "run_manifest.json")) for label, rel in RUNS.items()}

# ----------------------------------------------------------------------------- 1. resolved_config
heading("1. resolved_config.json: is anything different between the runs?")
for label, rel in RUNS.items():
    print(f"  {label:8s} sha256 {sha256(os.path.join(DATA, rel, 'resolved_config.json'))}  training_sha256 "
          f"{resolved[label]['training_sha256'][:16]}...  plan {resolved[label]['plan_version']}")
flat_cfg = {label: flatten(cfg) for label, cfg in resolved.items()}
keys = sorted(set().union(*[set(f) for f in flat_cfg.values()]))
differ = [k for k in keys if len({json.dumps(flat_cfg[lab].get(k), sort_keys=True) for lab in ORDER}) > 1]
print(f"  {len(keys)} leaf fields compared, {len(differ)} differ" + (": " + ", ".join(differ) if differ else
                                                                       " - every run trained on the same resolved config;"
                                                                       " the arms differ only through the arm spec and the"
                                                                       " experiment file (below)."))
cfg = resolved["v1 flat"]
sci, imp = cfg["science"], cfg["implementation"]
print("\n  The shared recipe (identical for all runs), as read from resolved_config.json:")
shared = [
    ("optimiser", sci["training"]["optimizer"]),
    ("learning rate / schedule", f"{sci['training']['lr_proposed']} / {sci['training']['lr_schedule']}"),
    ("weight decay / gradient clip norm", f"{sci['training']['weight_decay_proposed']} / {sci['training']['gradient_clip_norm']}"),
    ("optimiser steps", sci["training"]["formal_optimizer_steps_proposed"]),
    ("pair units per step (micro-batch x accumulation)",
     f"{sci['training']['microbatch_pair_units']} x {sci['training']['gradient_accumulation_pair_units']}"),
    ("one pair unit", "2 sides (before/after state) x 2 tiles of " + "x".join(map(str, sci["geometry"]["local_patch_proposed"]))
     + f" research voxels at {sci['geometry']['research_spacing_mm_proposed']} mm"),
    ("global frame / token grid", f"{sci['geometry']['global_grid_proposed']} / {sci['geometry']['global_token_grid_proposed']}"),
    ("tile overlap (inference)", sci["geometry"]["local_overlap"]),
    ("second-tile category draw", imp["tiles"]["train_tile_fractions"]),
    ("sampled voxels per tile", f"all T; O budget {sci['loss']['sampling']['other_budget']}; P budget "
                                f"{sci['loss']['sampling']['preserve_budget']}; near/far {sci['loss']['sampling']['near_fraction']}/"
                                f"{sci['loss']['sampling']['far_fraction']} inside/outside {sci['loss']['sampling']['envelope_radius_mm']} mm;"
                                f" hard share of near P {imp['sampling']['hard_fraction_of_near']}"),
    ("base loss weights", sci["loss"]["weights"]),
    ("state loss constants", f"margin {sci['loss']['state_margin']}, stable weight {sci['loss']['stable_weight']}, "
                             f"weight {sci['loss']['weights']['state']} after {sci['training']['base_warmup_steps']} "
                             f"base-only steps and a {sci['training']['state_loss_ramp_steps']}-step ramp"),
    ("state-pair type mix", sci["training"]["state_pair_mix"]),
    ("state pool", imp["state_pool"]),
    ("induced-pool share when a run reads two pools", imp["continuation"]["on_policy_fraction"]),
    ("augmentation", imp["augmentation"]),
    ("stroke distance truncation (v1) / start radius (K)", f"{imp['prompt']['distance_truncation_mm']} mm"),
    ("network sizes", {k: sci["network"][k] for k in ("encoder_widths_proposed", "decoder_feature_dim", "query_dim",
                                                      "attention_heads", "cross_attention_layers")}),
    ("numerics", "float32 storage, TF32 profile (superseded_plan_keys: no fp16/bf16)"),
    ("TRAIN split (plan's expected counts)", sci["data"]["splits_expected"]["TRAIN"]),
]
for name, value in shared:
    print(f"    {name:50s} {json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value}")

# ----------------------------------------------------------------------------- 2. arm spec / plan / recipe blocks
heading("2. Arm spec, plan and the K-only blocks of run_manifest.json, side by side (every field that differs; '-' = absent)")
BLOCKS = ["identity.arm_spec", "plan", "data_recipe", "experiment.document.switches", "experiment.document.refresh",
          "experiment.document.init", "experiment.document.reads_state_pool", "loss_alignment", "schedule", "refresh",
          "pools", "parameters", "exposure", "numerics", "identity.pair_manifest_sha256", "identity.seed",
          "identity.sequence_offset", "identity.total_steps", "matched_input_signature", "activation_checkpointing",
          "final_checkpoint", "status", "wall_hours_total", "training_sha256", "scientific_sha256"]
flat_man = {label: flatten(m) for label, m in manifest.items()}
for block in BLOCKS:
    keys = sorted({k for f in flat_man.values() for k in f if k == block or k.startswith(block + ".")})
    rows, same = [], []
    for key in keys:
        values = [flat_man[lab].get(key, "-") for lab in ORDER]
        if len({json.dumps(v, sort_keys=True) for v in values}) > 1:
            rows.append((key, values))
        else:
            same.append(key)
    print(f"\n-- {block}: {len(rows)} differing field(s); identical in all runs: "
          + (", ".join(k[len(block) + 1:] or k for k in same) if same else "none"))
    if rows:
        table(rows)

# ----------------------------------------------------------------------------- 3. everything else that differs
heading("3. Every other differing field of run_manifest.json (attempts summarised in section 4; per-file code hashes in 5)")
covered = tuple(BLOCKS) + ("attempts",)
keys = sorted({k for f in flat_man.values() for k in f})
rows = []
for key in keys:
    if key.startswith(covered) or key in ("run_id", "arm", "checkpoint_sha256"):
        continue
    values = [flat_man[lab].get(key, "-") for lab in ORDER]
    if len({json.dumps(v, sort_keys=True) for v in values}) > 1:
        rows.append((key, values))
print("  run ids: " + "; ".join(f"{lab} = {manifest[lab]['run_id']}" for lab in ORDER))
if rows:
    table(rows)
else:
    print("  none")

# ----------------------------------------------------------------------------- 4. attempts
heading("4. Attempts: machine, software, loader and time")
for label in ORDER:
    for a in manifest[label].get("attempts", []):
        env = a.get("environment", {})
        print(f"  {label:8s} attempt {a.get('index')}: status {a.get('status')}, resumed from {a.get('resumed_from_step')}, "
              f"steps {a.get('steps_done')}, wall {a.get('wall_hours') if a.get('wall_hours') is None else round(a['wall_hours'], 2)} h, "
              f"host {env.get('host')}, GPU {env.get('gpu')}, torch {env.get('torch')}, CUDA {env.get('cuda')}, "
              f"workers {a.get('loader', {}).get('num_workers')}, activation checkpointing {a.get('activation_checkpointing')}, "
              f"code {a.get('code', {}).get('sha256', '')[:12]}, {a.get('started_at')} -> {a.get('ended_at')}")

# ----------------------------------------------------------------------------- 5. code files
heading("5. Code version: per-file sha256 recorded at training time (file identity only)")
files = {}
for label in ORDER:
    for a in manifest[label].get("attempts", []):
        recorded = a.get("code", {}).get("files")
        if recorded:
            files.setdefault(label, recorded)
print("  runs whose manifest records per-file hashes: " + ", ".join(files) + "; whole-code sha256 for the others in section 4")
if files:
    names = sorted(set().union(*[set(f) for f in files.values()]))
    diff_names = [n for n in names if len({files[lab].get(n) for lab in files}) > 1]
    print(f"  {len(names)} files recorded; files whose hash differs between {', '.join(files)}: {diff_names or 'none'}")
    for name in diff_names:
        print("    " + name + ": " + ", ".join(f"{lab} {str(files[lab].get(name))[:12]}" for lab in files))
for rel in ("scripts/common/petct_sirb_training.py", "scripts/common/petct_sirb_network.py", "scripts/common/petct_sirb_losses.py",
            "scripts/common/petct_sirb_dataset.py"):
    local = sha256(os.path.join(PROJECT, rel))
    print(f"  local code tree {rel:42s} = {local[:12]}; equal to the copy recorded by: "
          + (", ".join(lab for lab in files if files[lab].get(rel) == local) or "none"))

# ----------------------------------------------------------------------------- 6. constants in code that shape K
heading("6. Code constants (not in the resolved config) that shape the K recipe, read from the source text")
CONSTANTS = [
    ("scripts/common/petct_sirb_registry.py", "LOSS_ALIGNMENT_CALIBRATION_STEP"),
    ("scripts/common/petct_sirb_registry.py", "TERM_GRAD_NORM_EVERY_STEPS"),
    ("scripts/common/petct_sirb_registry.py", "CONNECTIVITY_MAIN"),
    ("scripts/common/petct_sirb_training.py", "ALIGNMENT_UNITS_PER_TERM"),
    ("scripts/common/petct_sirb_training.py", "ALIGNMENT_MAX_UNITS"),
    ("scripts/common/petct_sirb_dataset.py", "RELATION_STROKE_ATTEMPTS"),
    ("scripts/common/petct_sirb_dataset.py", "DISTINCT_TILE_ATTEMPTS"),
]
for rel, name in CONSTANTS:
    with open(os.path.join(PROJECT, rel), encoding="utf-8") as handle:
        text = handle.read()
    match = re.search(rf"^{name}\s*=\s*([^\n#]+)", text, flags=re.M)
    print(f"  {name:34s} = {match.group(1).strip() if match else 'NOT FOUND':10s} ({rel})")
print("  B1 hard negative: k = |T| of the state, the O/P voxels with the highest current pT, loss -log(1 - pT), "
      "multiplier 1 (petct_sirb_losses.hard_negative_loss); B1 ring rank: 18-connected T/P neighbour pairs, "
      "softplus(s_P - s_T), multiplier 1; B1 soft Dice gain: multiplier set once at step 1000 from 4 units.")

# ----------------------------------------------------------------------------- 7. exposure
heading("7. Training exposure: units seen, where they came from, and how often each scan / pair was seen")


def load_rows(path):
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip().startswith("{"):
                rows.append(json.loads(line))
    by_step = {}
    for row in rows:
        if row["step"] not in by_step or row.get("attempt", 0) >= by_step[row["step"]].get("attempt", 0):
            by_step[row["step"]] = row
    return [by_step[s] for s in sorted(by_step)]


TRAIN = sci["data"]["splits_expected"]["TRAIN"]
print(f"  TRAIN split: {TRAIN['patients']} patients, {TRAIN['scans']} scans (plan's expected counts in resolved_config).")
print(f"  Offline pool: {TRAIN_SPLIT_FROM_VAULT}.")
print("  Distinct patients/scans of the induced (on-policy) pool and of K2's refresh pools: not in the local records "
      "(UNVERIFIED); the manifests give only pair counts.")
for label in ORDER:
    rows = load_rows(os.path.join(DATA, RUNS[label], "metrics.jsonl"))
    last = rows[-1]
    exposure = manifest[label].get("exposure") or last.get("exposure")
    source = "run_manifest" if manifest[label].get("exposure") else f"last log row (step {last['step']})"
    sums = {}
    for row in rows:
        for key, value in row.items():
            if key.startswith(COUNT_PREFIXES) and isinstance(value, (int, float)):
                sums[key] = sums.get(key, 0.0) + value
    units = exposure["pair_count"]
    pools = manifest[label].get("pools", {})
    print(f"\n  {label} ({manifest[label]['arm']}), exposure from {source}:")
    print(f"    optimiser steps {exposure['optimizer_steps']:,}, pair units {units:,}, state forwards "
          f"{exposure['state_forward_count']:,}, tiles {exposure['tile_count']:,}, valid voxels {exposure['valid_voxels']:.3e}, "
          f"classification voxels {exposure['classification_voxels']:.3e}")
    print(f"    pools: {pools.get('total_pairs')} pairs, of which induced {pools.get('on_policy_pairs')} "
          f"(manifest sources {[s[:8] for s in pools.get('pair_manifest_sources', [])]})")
    offline = sums.get("pool_offline", 0)
    induced = sums.get("pool_on_policy", 0)
    gap = sums.get("pool_share_gap", 0)
    refresh = sums.get("pool_share_refresh", 0)
    print(f"    units by source (summed log counts): offline {offline:,.0f}, induced {induced:,.0f} (gap-weighted {gap:,.0f}, "
          f"refreshed {refresh:,.0f}, induced natural draw {induced - gap - refresh:,.0f})")
    rel_units = sums.get("relation_swap", 0) + sums.get("relation_same_scope", 0)
    if rel_units:
        print(f"    units with a relation stroke: {rel_units:,.0f} ({100 * rel_units / units:.1f}%: swap {sums.get('relation_swap', 0):,.0f}, "
              f"same target {sums.get('relation_same_scope', 0):,.0f}) -> about {2 + rel_units / units:.2f} supervised stroke-states "
              f"per unit (v1: 2)")
    if "far_block_placed" in sums:
        print(f"    far second block placed in {sums['far_block_placed']:,.0f} of {units:,} units "
              f"({100 * sums['far_block_placed'] / units:.2f}%)")
    print(f"    averages: {units / TRAIN['scans']:.1f} units per TRAIN scan, {units / TRAIN['patients']:.1f} per TRAIN patient "
          f"(patients are drawn uniformly, then a scan, then an episode); offline draws per offline pair "
          f"{offline / 17872:.2f}" + (f"; induced draws per induced pair {(induced - refresh) / pools['on_policy_pairs']:.2f}"
                                      if pools.get("on_policy_pairs") else ""))
    if manifest[label].get("refresh"):
        for pool in manifest[label]["refresh"]["pools"]:
            print(f"    refresh at step {pool['step']}: {pool['n_pairs']} pairs from TRAIN patient half {pool['patient_half']}, "
                  f"drawn from micro index {pool['first_micro_index']:,}")
print("\nDone.")
