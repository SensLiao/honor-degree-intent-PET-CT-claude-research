"""c1: training dynamics of v1 flat, v1 N3, K1, K2 and K3 (partial) side by side, from the training logs only.

Reads (read-only): data/val-and-train-results/<run>/metrics.jsonl and run_manifest.json, resolved_config.json.
Writes: ../figures/train-curves-*.png (150 dpi) and prints every table (saved as c1_out.txt).
Run from this folder:  D:/Anaconda/python.exe -W ignore c1_training_dynamics.py > c1_out.txt

Every number here is a TRAINING-LOG diagnostic computed on the training units of each run (not a validation score).
K runs draw a different training mix (half offline states, half model-induced states, gap-weighted, plus a relation
stroke per unit), so a K-versus-v1 difference in a diagnostic mixes model and data differences; section 10 measures
the data part with the v1 continuations (history only).

Log facts used (petct_sirb_training.py): one log row = a window of 20 optimiser steps x 2 pair units; per-unit values
are averaged over the window, keys starting with pair_type_/pool_/sampled_/relation_/far_block_ are SUMMED over the
window (40 units); grad_norm_<term> is the UNWEIGHTED gradient 2-norm of one logged term on the FIRST unit of the
0-based optimiser steps 0, 200, 400, ... (registry TERM_GRAD_NORM_EVERY_STEPS), which land in the log rows 20, 220, ...
"""
import json
import math
import os

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "val-and-train-results")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

RUNS = {  # label -> run folder
    "v1 flat": "train-sirb-formal-20260930/N1_STATE",
    "v1 N3": "train-sirb-formal-20260930/N3",
    "K1": "train-sirb-k-20261006/K1_INTENT_FULL",
    "K2": "train-sirb-k-20261006/K2_INTENT_REFRESH",
    "K3": "train-sirb-k-20261006/K3_INTENT_WIDE_partial-20261007",
}
CONTINUATIONS = {  # history only: 8k continuations of the v1 40k models (step axis 0-8k of the continuation)
    "c N1_STATE_STATIC": "train-sirb-v2-continuations-20261005/N1_STATE_STATIC",
    "c N1_STATE_INDUCED": "train-sirb-v2-continuations-20261005/N1_STATE_INDUCED",
    "c N1_STATE_SPATIAL": "train-sirb-v2-continuations-20261005/N1_STATE_SPATIAL",
    "c N3_ES": "train-sirb-v2-continuations-20261005/N3_ES",
    "c N4_STATIC": "train-sirb-v2-continuations-20261005/N4_STATIC",
}
COLORS = {"v1 flat": "#222222", "v1 N3": "#a6a6a6", "K1": "#1f5fbf", "K2": "#f28e1c", "K3": "#2ca02c"}
STYLES = {"v1 flat": "-", "v1 N3": "-", "K1": "-", "K2": "-", "K3": "-"}
PHASES = [(0, 1000), (1000, 2000), (2000, 5000), (5000, 10000), (10000, 20000), (20000, 30000), (30000, 40000)]
PHASE_LABELS = ["0-1k", "1-2k", "2-5k", "5-10k", "10-20k", "20-30k", "30-40k"]
CONT_PHASES = [(0, 1000), (1000, 2000), (2000, 5000), (5000, 8000)]
CONT_LABELS = ["0-1k", "1-2k", "2-5k", "5-8k"]
SMOOTH_ROWS = 10           # rolling mean over 10 log rows = 200 optimiser steps
SMOOTH_GRAD_ROWS = 10      # rolling mean over 10 gradient rows = 2000 optimiser steps
COUNT_PREFIXES = ("pair_type_", "pool_", "sampled_", "relation_", "far_block_")   # summed per window (trainer)
GRAD_EVERY = 200           # registry TERM_GRAD_NORM_EVERY_STEPS
LOG_EVERY = 20             # monitoring.log_every_steps
UNITS_PER_STEP = 2         # training.gradient_accumulation_pair_units
CLIP_NORM = 5.0            # training.gradient_clip_norm

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 400)


def heading(text):
    print()
    print("=" * 110)
    print(text)
    print("=" * 110)


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_rows(path):
    """metrics.jsonl -> DataFrame, one row per logged step; a step logged by two attempts (resume) keeps the later one."""
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("{"):
                rows.append(json.loads(line))
    by_step = {}
    for row in rows:
        step = row["step"]
        if step not in by_step or row.get("attempt", 0) >= by_step[step].get("attempt", 0):
            by_step[step] = row
    flat = []
    for step in sorted(by_step):
        row = {k: v for k, v in by_step[step].items() if not isinstance(v, (dict, list))}
        flat.append(row)
    return pd.DataFrame(flat), len(rows) - len(by_step)


# ------------------------------------------------------------------ load
resolved = read_json(os.path.join(DATA, RUNS["v1 flat"], "resolved_config.json"))
BASE_WEIGHTS = {k: float(v) for k, v in resolved["science"]["loss"]["weights"].items()}   # error binding preserve state target_dice
D = {}
MAN = {}
for label, rel in RUNS.items():
    df, dups = load_rows(os.path.join(DATA, rel, "metrics.jsonl"))
    D[label] = df
    MAN[label] = read_json(os.path.join(DATA, rel, "run_manifest.json"))
    MAN[label]["_dups"] = dups
C = {}
CMAN = {}
for label, rel in CONTINUATIONS.items():
    df, dups = load_rows(os.path.join(DATA, rel, "metrics.jsonl"))
    C[label] = df
    CMAN[label] = read_json(os.path.join(DATA, rel, "run_manifest.json"))
    CMAN[label]["_dups"] = dups


def count_keys(df):
    return [k for k in df.columns if k.startswith(COUNT_PREFIXES)]


def per_unit(df):
    """Summed window counts -> per training unit (divide by 2 units x the window's steps).  A count key that a window
    does not carry means no unit of that window had the event (the trainer only writes keys it saw), so it counts 0;
    averaging only the windows that carry the key would overstate rare events (relation_none: 3.4% instead of 1.5%)."""
    out = df.copy()
    units = UNITS_PER_STEP * out["steps"]
    for key in count_keys(out):
        out[key] = out[key].fillna(0.0) / units
    return out


PU = {label: per_unit(df) for label, df in D.items()}
CPU = {label: per_unit(df) for label, df in C.items()}

# ------------------------------------------------------------------ 1. run facts
heading("1. Runs, log coverage and the weights each term enters the total loss with")
for label, df in D.items():
    man = MAN[label]
    plan = man["plan"]
    hosts = [a.get("environment", {}).get("host") for a in man.get("attempts", [])]
    ac = [a.get("activation_checkpointing") for a in man.get("attempts", [])]
    workers = [a.get("loader", {}).get("num_workers") for a in man.get("attempts", [])]
    grad_rows = df[[c for c in df.columns if c.startswith("grad_norm_base_")]].notna().any(axis=1).sum()
    la = man.get("loss_alignment", {})
    print(f"{label:8s} arm={man['arm']:15s} rows={len(df):4d} steps {int(df.step.min())}-{int(df.step.max())} "
          f"duplicate-step rows dropped={man['_dups']} gradient rows={grad_rows} status={man.get('status')} "
          f"hosts={hosts} activation_checkpointing={ac} workers={workers}")
    print(f"         plan: lr={plan['base_lr']} warmup={plan['warmup_steps']} total={plan['total_steps']} "
          f"accumulation={plan['accumulation']} clip={plan['clip_norm']} state warm-up={plan['state_base_warmup']} "
          f"ramp={plan['state_ramp']} final state weight={plan['state_final_weight']}")
    if la:
        print(f"         B6: calibration step={la.get('calibration_step')} multipliers={la.get('multipliers')} "
              f"(reference grad norm {la.get('reference_gradient_norm'):.3f}, dice-gain grad norm "
              f"{la.get('term_gradient_norms', {}).get('dice_gain'):.3f}, from {la.get('units_examined')} units)")
print()
print("Base loss weights (resolved_config science.loss.weights, used by petct_sirb_losses.base_loss):", BASE_WEIGHTS)
print("K2 refresh steps:", MAN["K2"].get("schedule", {}).get("refresh_steps"),
      "new-state share:", MAN["K2"].get("schedule", {}).get("new_state_share"))
print("K3 is still training: last logged step", int(D["K3"].step.max()), "of 40000.")


def state_weight_at(step, warmup, ramp, final):
    """petct_sirb_losses.state_weight_at (0-based optimiser step)."""
    if step < warmup or final == 0.0:
        return 0.0
    if ramp <= 0:
        return float(final)
    return float(final) * min(1.0, (step - warmup + 1) / float(ramp))


def multiplier_at(label, term, step):
    """B6 multiplier of an intent term at 0-based optimiser step (petct_sirb_training: 1 before the calibration step)."""
    la = MAN[label].get("loss_alignment", {})
    if not la:
        return 1.0
    if term == "dice_gain" and step < int(la.get("calibration_step", 0)):
        return 1.0
    return float(la.get("multipliers", {}).get(term, 1.0))


# ------------------------------------------------------------------ 2. checks of the weighting assumption
heading("2. Check: do the logged totals equal the weighted sum of the logged terms? (validates the weights used below)")
print("base_total - (w_error*error + w_binding*binding + w_target_dice*target_dice + w_preserve*preserve), and")
print("total - (base_total + state_weight*state_total + sum_k m_k*intent_k), m_dice_gain = 1 before step 1000 then the")
print("manifest multiplier.  Residuals ~1e-5 come from the state weight changing inside a log window during its ramp.")
for label, df in D.items():
    base = sum(BASE_WEIGHTS[k] * df["base_" + k] for k in ("error", "binding", "target_dice", "preserve"))
    r_base = (df["base_total"] - base).abs()
    rebuilt = df["base_total"] + df["state_weight"] * df["state_total"]
    for term in ("ring_rank", "hard_negative", "dice_gain", "pair_swap", "pair_same_scope"):
        key = "intent_" + term
        if key in df.columns:
            m = np.array([multiplier_at(label, term, s - LOG_EVERY) for s in df["step"]])
            rebuilt = rebuilt + m * df[key].fillna(0.0)
    r_total = (df["total"] - rebuilt).abs()
    print(f"  {label:8s} max |base residual| = {r_base.max():.2e}   max |total residual| = {r_total.max():.2e}  "
          f"(rows with |total residual| > 1e-3: {(r_total > 1e-3).sum()})")
# learning rate identical across runs at matched steps?
ref = D["v1 flat"].set_index("step")["lr"]
for label, df in D.items():
    other = df.set_index("step")["lr"]
    common = ref.index.intersection(other.index)
    print(f"  lr {label:8s} vs v1 flat at {len(common)} matched steps: max |difference| = "
          f"{(ref[common] - other[common]).abs().max():.2e}")


# ------------------------------------------------------------------ phase helpers
def phase_mean(df, key, lo, hi):
    if key not in df.columns:
        return np.nan
    sel = df[(df["step"] > lo) & (df["step"] <= hi)][key]
    return float(sel.mean()) if sel.notna().any() else np.nan


def phase_table(frames, key, phases=PHASES, labels=PHASE_LABELS):
    table = {}
    for label, df in frames.items():
        table[label] = [phase_mean(df, key, lo, hi) for lo, hi in phases]
    return pd.DataFrame(table, index=labels).T


def print_phase(frames, key, note="", fmt="{:9.4f}", phases=PHASES, labels=PHASE_LABELS):
    table = phase_table(frames, key, phases, labels)
    if table.isna().all().all():
        return
    print(f"-- {key} {note}")
    head = "   " + " " * 20 + "".join(f"{c:>11s}" for c in table.columns)
    print(head)
    for label, values in table.iterrows():
        cells = "".join(("   " + fmt.format(v))[-11:] if not np.isnan(v) else f"{'-':>11s}" for v in values)
        print(f"   {label:20s}{cells}")


LOSS_KEYS = ["total", "base_total", "base_target_dice", "base_error", "base_binding", "base_preserve",
             "state_total", "state_change", "state_stable",
             "intent_hard_negative", "intent_ring_rank", "intent_dice_gain", "intent_pair_swap", "intent_pair_same_scope"]
INTENT_COUNT_KEYS = ["intent_hard_negative_count", "intent_ring_rank_count", "intent_dice_gain_count",
                     "intent_pair_swap_count", "intent_pair_same_scope_count"]
RAW_GRAD_KEYS = ["grad_norm", "grad_norm_base_target_dice", "grad_norm_base_error", "grad_norm_base_binding",
                 "grad_norm_base_preserve", "grad_norm_state_total", "grad_norm_intent_hard_negative",
                 "grad_norm_intent_ring_rank", "grad_norm_intent_dice_gain", "grad_norm_intent_pair_swap",
                 "grad_norm_intent_pair_same_scope"]
DIAG_KEYS = ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target", "diag_binding_accuracy_in_error",
             "diag_preserve_edit_voxels", "diag_target_voxels", "diag_other_voxels", "diag_preserve_voxels"]
MIX_KEYS = ["far_block_placed", "pair_type_peripheral", "pair_type_other_error", "pair_type_bridge", "pair_fallback",
            "pool_offline", "pool_on_policy", "pool_share_natural", "pool_share_gap", "pool_share_refresh",
            "relation_none", "relation_same_scope", "relation_swap",
            "sampled_target", "sampled_other", "sampled_preserve_near", "sampled_preserve_far", "sampled_preserve_hard"]
SCHED_KEYS = ["lr", "state_weight", "seconds_per_step", "data_wait_fraction", "data_wait_seconds",
              "state_down_count", "state_stable_count", "state_common_count", "valid_voxels", "classification_voxels",
              "peak_allocated_gb", "max_rss_gb"]

# ------------------------------------------------------------------ 3. phase tables
heading("3. Phase tables (mean of the raw log rows whose step lies in (lo, hi]; K3 '30-40k' = 30,000-32,240 only)")
print("Loss terms are the logged (unweighted) values; intent_dice_gain is the minimised value = minus the soft Dice gain.")
print("\n### 3a. Loss terms")
for key in LOSS_KEYS:
    print_phase(D, key)
print("\n### 3b. Supervised counts of the intent terms (mean per unit)")
for key in INTENT_COUNT_KEYS:
    print_phase(D, key, fmt="{:9.1f}")
print("\n### 3c. Logged gradient norms, UNWEIGHTED (grad_norm = window mean of the clipped-before total norm of each step;")
print("###     grad_norm_<term> = one unit every 200 steps; a phase of 1k steps holds 5 such measurements)")
for key in RAW_GRAD_KEYS:
    print_phase(D, key, fmt="{:9.3f}")
print("\n### 3d. Diagnostics (per tile-side entry, averaged; relation-stroke tiles of K units are included by the trainer)")
for key in DIAG_KEYS:
    print_phase(D, key, fmt="{:9.4f}" if "voxels" not in key else "{:9.1f}")
print("\n### 3e. Training mix, per unit (window sums / 40 units); sampled_* = classification voxels per unit")
for key in MIX_KEYS:
    print_phase(PU, key, fmt="{:9.4f}" if not key.startswith("sampled_") else "{:9.0f}")
print("\n### 3f. Schedule, speed, memory (hardware differs: v1 runs and K1 on the z390 RTX 3090, K2 on the RTX 5090,")
print("###     K3 on the A6000; K1/K2 use activation checkpointing, which costs time but not results)")
for key in SCHED_KEYS:
    fmt = "{:9.2e}" if key in ("lr", "valid_voxels", "classification_voxels") else "{:9.3f}"
    print_phase(D, key, fmt=fmt)

# share of steps whose total gradient norm exceeded the clip norm (window means only: a lower bound on clipping)
print("\n-- share of log windows whose mean total grad norm > clip norm 5.0 (every step in such a window is likely clipped)")
for label, df in D.items():
    vals = [float(((df[(df.step > lo) & (df.step <= hi)]["grad_norm"]) > CLIP_NORM).mean()) if
            ((df.step > lo) & (df.step <= hi)).any() else np.nan for lo, hi in PHASES]
    print(f"   {label:20s}" + "".join(f"{v:11.3f}" if not np.isnan(v) else f"{'-':>11s}" for v in vals))

# ------------------------------------------------------------------ 4. weighted gradient norms and shares
heading("4. WEIGHTED gradient-norm shares (what the optimiser sees, per term)")
print("Weight of each logged gradient norm, as the trainer builds the loss (petct_sirb_training.unit_loss):")
print("  base_error x 1.0, base_binding x 1.0, base_target_dice x 1.0, base_preserve x 0.5  (science.loss.weights; the")
print("    logged base_<k> is already the mean over both pair sides and both tiles - plus the relation-stroke tiles for K -")
print("    exactly the average the total uses, so no extra 0.5 side factor; section 2 confirms base_total to 1e-7);")
print("  state_total x state_weight(step) = 0 before step 2000, linear to 0.25 at step 3999, then 0.25")
print("    (petct_sirb_losses.state_weight_at; plan state_base_warmup 2000, state_ramp 2000, state_final_weight 0.25);")
print("  intent_<k> x B6 multiplier (run_manifest loss_alignment.multipliers): dice_gain 1.0 before step 1000, then")
print("    K1 0.463 / K2 0.593 / K3 0.299; hard_negative, ring_rank, pair_swap, pair_same_scope 1.0 throughout.")
print("The common 1/accumulation factor cancels.  Shares = sum over the phase of each weighted norm / sum over all")
print("terms ('ratio of sums').  An intent pair term absent on the measured unit (the unit had no relation of that kind)")
print("counts 0.  Caveats: each measurement is ONE unit; norms of different terms do not add like vectors (their angles")
print("are not logged), and AdamW rescales each parameter, so a share is a relative-magnitude measure, not the")
print("composition of the update.")

GRAD_TERMS = ["base_target_dice", "base_error", "base_binding", "base_preserve", "state_total",
              "intent_hard_negative", "intent_ring_rank", "intent_dice_gain", "intent_pair_swap", "intent_pair_same_scope"]
TERM_LABEL = {"base_target_dice": "target soft Dice", "base_error": "error BCE", "base_binding": "binding BCE",
              "base_preserve": "preserve (x0.5)", "state_total": "state (x lambda)",
              "intent_hard_negative": "hard negative (new)", "intent_ring_rank": "boundary ring rank (new)",
              "intent_dice_gain": "soft Dice gain x m (new)", "intent_pair_swap": "pair swap (new)",
              "intent_pair_same_scope": "same-target consistency (new)"}
TERM_COLOR = {"base_target_dice": "#1b9e77", "base_error": "#7570b3", "base_binding": "#a6761d",
              "base_preserve": "#66a61e", "state_total": "#999999", "intent_hard_negative": "#d62728",
              "intent_ring_rank": "#e7298a", "intent_dice_gain": "#17becf", "intent_pair_swap": "#ff9896",
              "intent_pair_same_scope": "#9467bd"}


def weight_of(label, term, step):
    plan = MAN[label]["plan"]
    if term.startswith("base_"):
        return BASE_WEIGHTS[term[len("base_"):]]
    if term == "state_total":
        return state_weight_at(step, plan["state_base_warmup"], plan["state_ramp"], plan["state_final_weight"])
    return multiplier_at(label, term[len("intent_"):], step)


def weighted_grads(label):
    df = D[label]
    rows = df[df[[c for c in df.columns if c.startswith("grad_norm_base_")]].notna().any(axis=1)]
    out = []
    for _, r in rows.iterrows():
        step0 = int(r["step"]) - LOG_EVERY          # 0-based optimiser step that was measured
        assert step0 % GRAD_EVERY == 0, (label, r["step"])
        rec = {"step": int(r["step"]), "step0": step0}
        for term in GRAD_TERMS:
            key = "grad_norm_" + term
            raw = r[key] if key in r.index and not pd.isna(r[key]) else np.nan
            applicable = term.startswith("base_") or term == "state_total" or ("intent_" in term and
                                                                               "intent_hard_negative" in df.columns)
            if not applicable:
                continue
            w = weight_of(label, term, step0)
            rec["raw_" + term] = raw
            rec["w_" + term] = w
            rec["wn_" + term] = 0.0 if pd.isna(raw) else w * raw
        out.append(rec)
    return pd.DataFrame(out)


WG = {label: weighted_grads(label) for label in D}
# check the state weight recomputed at the measured step against the logged window mean of the same row
for label in D:
    wg = WG[label]
    logged = D[label].set_index("step").loc[wg["step"], "state_weight"].to_numpy()
    print(f"  check {label:8s}: |state weight at measured step - logged window mean| max = "
          f"{np.max(np.abs(wg['w_state_total'].to_numpy() - logged)):.4f} (window mean; differs only during the ramp)")


def share_table(label, phases=PHASES, labels=PHASE_LABELS):
    wg = WG[label]
    terms = [t for t in GRAD_TERMS if "wn_" + t in wg.columns]
    rows = {}
    for (lo, hi), name in zip(phases, labels):
        sel = wg[(wg["step"] > lo) & (wg["step"] <= hi)]
        if sel.empty:
            continue
        sums = {t: sel["wn_" + t].sum() for t in terms}
        total = sum(sums.values())
        rows[name] = {t: sums[t] / total for t in terms}
        rows[name]["n_units"] = len(sel)
    return pd.DataFrame(rows).T


def mean_of_shares(label, phases=PHASES, labels=PHASE_LABELS):
    wg = WG[label]
    terms = [t for t in GRAD_TERMS if "wn_" + t in wg.columns]
    w = wg[["wn_" + t for t in terms]].to_numpy()
    shares = w / w.sum(axis=1, keepdims=True)
    rows = {}
    for (lo, hi), name in zip(phases, labels):
        sel = ((wg["step"] > lo) & (wg["step"] <= hi)).to_numpy()
        if sel.any():
            rows[name] = dict(zip(terms, shares[sel].mean(axis=0)))
    return pd.DataFrame(rows).T


SHARES = {}
for label in D:
    st = share_table(label)
    SHARES[label] = st
    print(f"\n-- {label}: weighted share of each term (ratio of sums), %; n_units = gradient measurements in the phase")
    show = st.copy()
    for c in show.columns:
        if c != "n_units":
            show[c] = 100 * show[c]
    show.columns = [TERM_LABEL.get(c, c) for c in show.columns]
    print(show.round(1).to_string())
    ms = mean_of_shares(label)
    ms.columns = [TERM_LABEL.get(c, c) for c in ms.columns]
    print(f"   robustness: mean over units of each unit's share, %")
    print((100 * ms).round(1).to_string())

print("\n-- Mean WEIGHTED gradient norm per term (same weights), per phase")
for label in D:
    wg = WG[label]
    terms = [t for t in GRAD_TERMS if "wn_" + t in wg.columns]
    rows = {}
    for (lo, hi), name in zip(PHASES, PHASE_LABELS):
        sel = wg[(wg["step"] > lo) & (wg["step"] <= hi)]
        if not sel.empty:
            rows[name] = {TERM_LABEL[t]: sel["wn_" + t].mean() for t in terms}
    print(f"   {label}")
    print(pd.DataFrame(rows).T.round(3).to_string())

print("\n-- Robustness: shares built from the per-phase MEDIAN of each weighted norm (less sensitive to single large units), %")
for label in D:
    wg = WG[label]
    terms = [t for t in GRAD_TERMS if "wn_" + t in wg.columns]
    rows = {}
    for (lo, hi), name in zip(PHASES, PHASE_LABELS):
        sel = wg[(wg["step"] > lo) & (wg["step"] <= hi)]
        if not sel.empty:
            med = {t: sel["wn_" + t].median() for t in terms}
            total = sum(med.values())
            rows[name] = {TERM_LABEL[t]: 100 * med[t] / total for t in terms}
    print(f"   {label}")
    print(pd.DataFrame(rows).T.round(1).to_string())

print("\n-- The first 15 gradient measurements one by one (0-based steps 0-2800): weighted norm per term")
for label in ("v1 flat", "K1", "K3"):
    wg = WG[label]
    terms = [t for t in GRAD_TERMS if "wn_" + t in wg.columns]
    early = wg[wg["step0"] < 3000].set_index("step0")[["wn_" + t for t in terms]]
    early.columns = [TERM_LABEL[t] for t in terms]
    print(f"   {label}")
    print(early.round(2).to_string())

print("\n-- Grouped weighted shares, %: inherited base terms (4) / state term / new intent terms (5);")
print("   'suppress' = preserve + hard negative (both only push pT down on non-target voxels);")
print("   'dice' = target soft Dice + soft Dice gain x m (both reward overlap with T)")
for label in D:
    st = SHARES[label]
    base = st[[c for c in st.columns if c.startswith("base_")]].sum(axis=1)
    state = st["state_total"] if "state_total" in st.columns else 0 * base
    intent = st[[c for c in st.columns if c.startswith("intent_")]].sum(axis=1) if any(
        c.startswith("intent_") for c in st.columns) else 0 * base
    suppress = st["base_preserve"] + (st["intent_hard_negative"] if "intent_hard_negative" in st.columns else 0)
    dice = st["base_target_dice"] + (st["intent_dice_gain"] if "intent_dice_gain" in st.columns else 0)
    top = st[[c for c in st.columns if c != "n_units"]].idxmax(axis=1).map(TERM_LABEL)
    g = pd.DataFrame({"base": 100 * base, "state": 100 * state, "intent": 100 * intent, "suppress": 100 * suppress,
                      "dice": 100 * dice, "largest term": top})
    print(f"   {label}")
    print(g.round(1).to_string())


# ------------------------------------------------------------------ 5. values at given steps
def trailing(df, key, step, rows=SMOOTH_ROWS):
    sel = df[(df["step"] > step - rows * LOG_EVERY) & (df["step"] <= step)][key]
    return float(sel.mean()) if len(sel) else np.nan


heading("5. Values at given steps = mean of the 10 log rows ending at that step (200 optimiser steps); K3 last = 32,240")
AT = [1000, 2000, 5000, 10000, 20000, 30000, 40000]
for key in ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target", "diag_binding_accuracy_in_error",
            "diag_preserve_edit_voxels", "diag_target_voxels"]:
    print(f"-- {key}")
    print("   " + " " * 10 + "".join(f"{s:>10d}" for s in AT) + f"{'K3 last':>10s}")
    for label, df in D.items():
        vals = [trailing(df, key, s) if s <= df["step"].max() else np.nan for s in AT]
        last = trailing(df, key, int(df["step"].max())) if label == "K3" else np.nan
        print(f"   {label:10s}" + "".join(f"{v:10.4f}" if not np.isnan(v) else f"{'-':>10s}" for v in vals)
              + (f"{last:10.4f}" if not np.isnan(last) else f"{'':>10s}"))


# ------------------------------------------------------------------ 6. divergence
def smooth(series, rows=SMOOTH_ROWS):
    return series.rolling(rows, center=True, min_periods=max(1, rows // 2)).mean()


heading("6a. The first 3,000 steps in detail: mean of the 10 log rows ending at each step (200 optimiser steps)")
EARLY = [200, 400, 600, 800, 1000, 1200, 1400, 1600, 2000, 2500, 3000]
for key in ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target", "diag_preserve_edit_voxels",
            "intent_hard_negative", "base_target_dice", "base_preserve"]:
    print(f"-- {key}")
    print("   " + " " * 10 + "".join(f"{s:>9d}" for s in EARLY))
    for label, df in D.items():
        if key not in df.columns:
            continue
        vals = [trailing(df, key, s) for s in EARLY]
        fmt = "{:9.1f}" if "voxels" in key else "{:9.4f}"
        print(f"   {label:10s}" + "".join(fmt.format(v) for v in vals))

heading("6. When do K and v1 flat separate? (centred 10-row rolling means aligned on step)")
print("'persistent' = the first logged step from which v1 flat minus K stays above the margin until the end of the log.")
print("First-crossing = first step at which a run's rolling mean reaches the level.")
for key in ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target"]:
    print(f"-- {key}")
    ref = D["v1 flat"].set_index("step")[key]
    ref_s = smooth(ref)
    for label in ("v1 N3", "K1", "K2", "K3"):
        other = D[label].set_index("step")[key]
        common = ref.index.intersection(other.index)
        diff = (ref_s[common] - smooth(other)[common])
        out = []
        for margin in (0.05, 0.10, 0.20):
            above = diff > margin
            # persistent: last index where it is NOT above, then the next step
            if above.all():
                first = int(common[0])
            elif not above.iloc[-1]:
                first = None
            else:
                last_bad = np.where(~above.to_numpy())[0][-1]
                first = int(common[last_bad + 1])
            any_first = int(common[np.argmax(above.to_numpy())]) if above.any() else None
            out.append(f"margin {margin:.2f}: first exceeds at {any_first}, persistent from {first}")
        at = {s: float(diff.loc[s]) for s in (200, 500, 1000, 1500, 2000, 3000, 5000, 10000, 20000, 30000)
              if s in diff.index}
        print(f"   {label:6s} " + " | ".join(out))
        print(f"          v1 flat minus {label} at steps: " + ", ".join(f"{s}: {v:+.3f}" for s, v in at.items()))
    if key == "diag_target_recall":
        print("   first step at which the rolling mean reaches a recall level:")
        for label, df in D.items():
            s = smooth(df.set_index("step")[key])
            cross = []
            for level in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
                hit = s[s >= level]
                cross.append(f"{level:.1f}: {int(hit.index[0]) if len(hit) else '-'}")
            print(f"     {label:8s} " + ", ".join(cross))


# ------------------------------------------------------------------ 7. slope at the end
def ols_slope(df, key, lo, hi):
    sel = df[(df["step"] > lo) & (df["step"] <= hi)][["step", key]].dropna()
    x = sel["step"].to_numpy(dtype=float)
    y = sel[key].to_numpy(dtype=float)
    if len(x) < 3:
        return np.nan, np.nan, 0
    xm = x - x.mean()
    b = (xm * (y - y.mean())).sum() / (xm ** 2).sum()
    resid = y - y.mean() - b * xm
    se = math.sqrt((resid ** 2).sum() / (len(x) - 2) / (xm ** 2).sum())
    return b * 10000, se * 10000, len(x)


heading("7. Is recall still rising at the end?  OLS slope of the raw log rows, per 10k steps (+- naive SE; rows are")
print("autocorrelated, so the SE is optimistic).  The learning rate follows a cosine to 0 at 40k for every run, so every")
print("curve flattens near 40k by construction.  K3 (partial) is shown over its own last 10k logged steps.")
for key in ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target", "diag_preserve_edit_voxels"]:
    print(f"-- {key}")
    for label, df in D.items():
        hi = int(df["step"].max())
        lo = hi - 10000
        b, se, n = ols_slope(df, key, lo, hi)
        b5, se5, _ = ols_slope(df, key, hi - 5000, hi)
        m1 = phase_mean(df, key, lo, lo + 5000)
        m2 = phase_mean(df, key, lo + 5000, hi)
        print(f"   {label:8s} window ({lo}, {hi}]: slope {b:+.4f} +- {se:.4f} per 10k (n={n}); last 5k slope {b5:+.4f} "
              f"+- {se5:.4f}; mean last 5k minus previous 5k = {m2 - m1:+.4f}")
    # matched window 22,240-32,240 for every run, to compare K3 at the same schedule position
    print(f"   same window as K3's last 10k, (22240, 32240]:")
    for label, df in D.items():
        b, se, n = ols_slope(df, key, 22240, 32240)
        print(f"     {label:8s} slope {b:+.4f} +- {se:.4f} per 10k")


# ------------------------------------------------------------------ 8. K2 refresh
heading("8. K2 state-pool refreshes at steps 10,000 and 25,000: just before vs just after (K1 in the same windows as the")
print("no-refresh control).  Windows of 200 steps (10 rows) and 1,000 steps (50 rows).  Note: the diagnostics are computed")
print("on the training units, and after a refresh half of the induced-state draws come from the new pool, so a jump right")
print("after the refresh is first of all a change of the data being scored, not necessarily of the model.")
REFRESH_KEYS = ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target", "diag_preserve_edit_voxels",
                "diag_target_voxels", "diag_other_voxels", "diag_binding_accuracy_in_error", "base_target_dice",
                "base_error", "base_binding", "base_preserve", "state_total", "intent_hard_negative", "intent_ring_rank",
                "intent_dice_gain", "total", "pool_share_refresh", "pool_share_gap", "pool_share_natural",
                "sampled_target", "seconds_per_step", "data_wait_fraction"]
for refresh in (10000, 25000):
    for width in (200, 1000):
        print(f"\n-- refresh at {refresh}, window {width} steps: before ({refresh - width}, {refresh}] vs after "
              f"({refresh}, {refresh + width}]")
        print(f"   {'key':32s}{'K2 before':>11s}{'K2 after':>11s}{'K2 change':>11s}{'K1 before':>11s}{'K1 after':>11s}"
              f"{'K1 change':>11s}{'K2-K1 chg':>11s}")
        for key in REFRESH_KEYS:
            vals = []
            for label in ("K2", "K1"):
                df = PU[label]
                b = phase_mean(df, key, refresh - width, refresh)
                a = phase_mean(df, key, refresh, refresh + width)
                vals += [b, a, a - b]
            did = vals[2] - vals[5] if not (np.isnan(vals[2]) or np.isnan(vals[5])) else np.nan
            cells = "".join(f"{v:11.4f}" if not np.isnan(v) else f"{'-':>11s}" for v in vals + [did])
            print(f"   {key:32s}{cells}")
print("\n-- K2 minus K1 by phase (rolling differences of the whole run; refreshes at 10k and 25k)")
for key in ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target", "diag_preserve_edit_voxels",
            "diag_target_voxels"]:
    t = phase_table({"K2": D["K2"], "K1": D["K1"]}, key)
    print(f"   {key:30s}" + "".join(f"{v:+11.4f}" for v in (t.loc['K2'] - t.loc['K1'])))
print("   phases: " + ", ".join(PHASE_LABELS))

# ------------------------------------------------------------------ 9. K3 vs K1
heading("9. K3 (wider state encoder, 14.1M parameters) vs K1 (6.65M) at matched steps, up to K3's last step 32,240")
K3_PHASES = [(0, 1000), (1000, 2000), (2000, 5000), (5000, 10000), (10000, 20000), (20000, 30000), (30000, 32240)]
K3_LABELS = ["0-1k", "1-2k", "2-5k", "5-10k", "10-20k", "20-30k", "30-32.2k"]
for key in ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target", "diag_binding_accuracy_in_error",
            "diag_preserve_edit_voxels", "diag_target_voxels", "base_target_dice", "base_error", "base_binding",
            "base_preserve", "intent_hard_negative", "intent_ring_rank", "intent_dice_gain", "total"]:
    t = phase_table({"K3": D["K3"], "K1": D["K1"]}, key, K3_PHASES, K3_LABELS)
    print(f"-- {key}")
    print("   " + " " * 12 + "".join(f"{c:>11s}" for c in t.columns))
    for name in ("K3", "K1"):
        print(f"   {name:12s}" + "".join(f"{v:11.4f}" for v in t.loc[name]))
    print(f"   {'K3 - K1':12s}" + "".join(f"{v:+11.4f}" for v in (t.loc['K3'] - t.loc['K1'])))
print("-- K3 weighted gradient shares vs K1 at matched phases: see section 4.")
print("-- seconds per step and data wait (hardware differs: K3 on the A6000 without activation checkpointing)")
for key in ("seconds_per_step", "data_wait_fraction"):
    t = phase_table({"K3": D["K3"], "K1": D["K1"]}, key, K3_PHASES, K3_LABELS)
    print(f"   {key:20s} K3 " + "".join(f"{v:9.3f}" for v in t.loc["K3"]) + "   K1 " + "".join(
        f"{v:9.3f}" for v in t.loc["K1"]))

# ------------------------------------------------------------------ 10. continuations: the data-mix part of the gap
heading("10. History only: v1 continuations (8k steps from the v1 40k checkpoints).  Their first rows run at a tiny")
print("learning rate (linear warm-up from 2e-7), so rows 20-200 measure the v1 40k weights on each continuation's mix:")
print("N1_STATE_STATIC = offline states only (the v1 mix); N1_STATE_INDUCED = half offline, half model-induced states")
print("(natural draw, 7,747 induced pairs; K draws half its induced share gap-weighted from a 9,831-pair pool).")
cont_keys = ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target", "diag_preserve_edit_voxels",
             "diag_target_voxels", "diag_binding_accuracy_in_error"]
print(f"   {'run':22s}{'rows':>6s}" + "".join(f"{k.replace('diag_', ''):>24s}" for k in cont_keys))
for label, df in [("v1 flat last 200 steps", D["v1 flat"][D["v1 flat"].step > 39800])] + [
        (k + " first 200", v[v.step <= 200]) for k, v in C.items()]:
    print(f"   {label[:22]:22s}{len(df):6d}" + "".join(f"{df[k].mean():24.4f}" for k in cont_keys))
print()
for key in cont_keys + ["base_target_dice", "base_error", "total"]:
    print_phase(C, key, phases=CONT_PHASES, labels=CONT_LABELS,
                fmt="{:9.4f}" if "voxels" not in key else "{:9.1f}")
print_phase(CPU, "pool_on_policy", note="(per unit)", phases=CONT_PHASES, labels=CONT_LABELS)
for label, man in CMAN.items():
    print(f"   {label:22s} pools total={man.get('pools', {}).get('total_pairs')} on-policy="
          f"{man.get('pools', {}).get('on_policy_pairs')} duplicate-step rows dropped={man['_dups']}")


# ------------------------------------------------------------------ 11. figures
def mark_events(ax, k2=True):
    ax.axvline(1000, color="#bbbbbb", lw=0.8, ls=":")
    ax.axvspan(2000, 4000, color="#eeeeee", lw=0, zorder=0)
    if k2:
        for s in (10000, 25000):
            ax.axvline(s, color=COLORS["K2"], lw=0.8, ls="--", alpha=0.6)


def curve(ax, key, frames=None, logy=False, transform=None, labels=None):
    frames = frames or D
    for label in (labels or frames):
        df = frames[label]
        if key not in df.columns or df[key].notna().sum() == 0:
            continue
        y = df.set_index("step")[key]
        if transform is not None:
            y = transform(y)
        ax.plot(y.index, smooth(y), color=COLORS[label], ls=STYLES[label], lw=1.4 if label != "v1 N3" else 1.2,
                label=label)
    if logy:
        ax.set_yscale("log")
    ax.set_xlim(0, 40000)
    ax.set_xticks(range(0, 40001, 5000))
    ax.set_xticklabels([f"{x // 1000}k" for x in range(0, 40001, 5000)])
    ax.set_xlabel("optimiser step")
    ax.grid(alpha=0.25)


def save(fig, name):
    path = os.path.join(FIG, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", os.path.relpath(path, ROOT))


heading("11. Figures (all curves: centred rolling mean over 10 log rows = 200 optimiser steps unless stated)")
EVENT_NOTE = ("dotted line: step 1k (end of LR warm-up, B6 calibration); grey band: state-loss ramp 2k-4k; "
              "orange dashed: K2 refreshes")

fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
curve(axes[0], "diag_target_recall")
axes[0].set_ylabel("target recall (pT >= 0.5 on T)")
axes[0].set_title("Target recall on the training units")
curve(axes[1], "diag_hard_dice_target")
axes[1].set_ylabel("hard Dice of T")
axes[1].set_title("Hard Dice of the target on the training units")
for ax in axes:
    mark_events(ax)
    ax.set_ylim(0, 1)
axes[0].legend(loc="lower right", fontsize=9)
fig.suptitle("Training-log diagnostics (not validation); rolling mean over 10 log rows. " + EVENT_NOTE, fontsize=8)
save(fig, "train-curves-target-recall.png")

fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
curve(axes[0], "diag_error_gate_recall")
axes[0].set_ylabel("error-gate recall (e >= 0.5 on T)")
axes[0].set_title("Error-gate recall (upper bound of target recall)")
curve(axes[1], "diag_binding_accuracy_in_error")
axes[1].set_ylabel("binding accuracy inside T and O")
axes[1].set_title("Binding accuracy inside the errors")
for ax in axes:
    mark_events(ax)
axes[0].set_ylim(0.0, 1.0)      # full range: K's dip to about 0.1 near step 400 must stay visible
axes[1].set_ylim(0.4, 1.0)
axes[0].legend(loc="lower right", fontsize=9)
fig.suptitle("Training-log diagnostics (not validation); rolling mean over 10 log rows. " + EVENT_NOTE, fontsize=8)
save(fig, "train-curves-gate-recall.png")

fig, ax = plt.subplots(1, 1, figsize=(8, 4.6))
curve(ax, "diag_preserve_edit_voxels", logy=True)
mark_events(ax)
ax.set_ylabel("preserve voxels with pT >= 0.5, per tile-side (log)")
ax.set_title("Wrong edits on preserve voxels in the training tiles")
ax.legend(fontsize=9)
fig.suptitle("Training-log diagnostic; rolling mean over 10 log rows", fontsize=8)
save(fig, "train-curves-preserve-edits.png")

fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
curve(axes[0], "diag_target_voxels")
axes[0].set_ylabel("T voxels per tile-side")
axes[0].set_title("Target size in the training tiles")
curve(axes[1], "sampled_target", frames=PU)
axes[1].set_ylabel("T voxels sampled per unit")
axes[1].set_title("Target voxels per training unit (all of T)")
curve(axes[2], "diag_other_voxels")
axes[2].set_ylabel("O voxels per tile-side")
axes[2].set_title("Other-error size in the training tiles")
for ax in axes:
    mark_events(ax)
axes[0].legend(fontsize=9)
fig.suptitle("Training mix (training-log diagnostics); rolling mean over 10 log rows. Lines overlap where runs draw "
             "identical units: v1 flat = v1 N3; K1 = K2 before 10k; K1 = K3 up to 32k", fontsize=8)
save(fig, "train-curves-target-size.png")

loss_panels = ["total", "base_target_dice", "base_error", "base_binding", "base_preserve", "state_total",
               "intent_hard_negative", "intent_ring_rank", "intent_dice_gain", "intent_pair_swap",
               "intent_pair_same_scope", "base_total"]
fig, axes = plt.subplots(3, 4, figsize=(18, 11))
for ax, key in zip(axes.ravel(), loss_panels):
    curve(ax, key)
    mark_events(ax)
    ax.set_title(key + (" (minus soft Dice gain)" if key == "intent_dice_gain" else ""), fontsize=10)
    ax.tick_params(labelsize=8)
    ax.set_xlabel("")
axes[0, 0].legend(fontsize=9)
fig.suptitle("Logged loss terms (unweighted values; total = weighted sum, section 2 of c1_out.txt); rolling mean over "
             "10 log rows. " + EVENT_NOTE, fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.97))
save(fig, "train-curves-loss-terms.png")

fig, axes = plt.subplots(1, 5, figsize=(22, 4.8), sharey=True)
for ax, label in zip(axes, D):
    wg = WG[label]
    terms = [t for t in GRAD_TERMS if "wn_" + t in wg.columns]
    sm = wg[["wn_" + t for t in terms]].rolling(SMOOTH_GRAD_ROWS, center=True, min_periods=3).mean()
    share = sm.div(sm.sum(axis=1), axis=0).fillna(0)
    ax.stackplot(wg["step"], [share["wn_" + t] for t in terms], colors=[TERM_COLOR[t] for t in terms],
                 labels=[TERM_LABEL[t] for t in terms], alpha=0.9)
    ax.set_title(label)
    ax.set_xlim(0, 40000)
    ax.set_ylim(0, 1)
    ax.set_xticks(range(0, 40001, 10000))
    ax.set_xticklabels([f"{x // 1000}k" for x in range(0, 40001, 10000)])
    ax.set_xlabel("optimiser step")
    ax.axvline(1000, color="white", lw=0.8, ls=":")
axes[0].set_ylabel("share of summed weighted gradient norms")
handles, labels_ = axes[2].get_legend_handles_labels()
fig.legend(handles, labels_, loc="lower center", ncol=5, fontsize=9, bbox_to_anchor=(0.5, -0.08))
fig.suptitle("Weighted gradient-norm shares (logged norm x loss weight x state weight x B6 multiplier); one unit every "
             "200 steps, rolling mean over 10 measurements = 2,000 steps", fontsize=9)
save(fig, "train-curves-weighted-grad-share.png")

fig, axes = plt.subplots(2, 5, figsize=(22, 8.5))
for ax, term in zip(axes.ravel(), GRAD_TERMS):
    for label in D:
        wg = WG[label]
        if "wn_" + term not in wg.columns:
            continue
        y = wg.set_index("step")["wn_" + term]
        if term == "state_total":                    # weight 0 before step 2000: nothing reaches the optimiser
            y = y.where(wg.set_index("step")["w_state_total"] > 0)
        ax.plot(y.index, y.rolling(SMOOTH_GRAD_ROWS, center=True, min_periods=3).mean(), color=COLORS[label],
                lw=1.3, label=label)
    ax.set_yscale("log")
    ax.set_title(TERM_LABEL[term], fontsize=10)
    ax.set_xlim(0, 40000)
    ax.set_xticks(range(0, 40001, 10000))
    ax.set_xticklabels([f"{x // 1000}k" for x in range(0, 40001, 10000)], fontsize=8)
    ax.grid(alpha=0.25)
axes[0, 0].legend(fontsize=9)
fig.suptitle("Weighted gradient norm of each term (log scale); one unit every 200 steps, rolling mean over 10 "
             "measurements = 2,000 steps", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.96))
save(fig, "train-curves-weighted-grad-norms.png")

fig, axes = plt.subplots(2, 2, figsize=(14, 8.5))
curve(axes[0, 0], "lr")
axes[0, 0].set_title("Learning rate (identical schedule for every run; the lines overlap)")
curve(axes[0, 1], "grad_norm", logy=True)
axes[0, 1].axhline(CLIP_NORM, color="red", lw=0.9, ls="--")
axes[0, 1].set_title("Total gradient norm before clipping (window mean); red: clip norm 5")
curve(axes[1, 0], "seconds_per_step")
axes[1, 0].set_title("Seconds per optimiser step (hardware differs per run)")
axes[1, 0].set_ylim(0, None)
curve(axes[1, 1], "data_wait_fraction")
axes[1, 1].set_title("Share of time waiting for data")
axes[1, 1].set_ylim(0, None)
axes[0, 0].legend(fontsize=9)
fig.suptitle("Schedule and speed; rolling mean over 10 log rows", fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.97))
save(fig, "train-curves-lr.png")

fig, axes = plt.subplots(2, 4, figsize=(20, 8))
for row, refresh in enumerate((10000, 25000)):
    for col, key in enumerate(["diag_target_recall", "diag_error_gate_recall", "diag_target_voxels",
                               "diag_preserve_edit_voxels"]):
        ax = axes[row, col]
        for label in ("K1", "K2"):
            df = D[label]
            sel = df[(df.step > refresh - 2000) & (df.step <= refresh + 2000)].set_index("step")[key]
            ax.plot(sel.index, sel, color=COLORS[label], lw=0.6, alpha=0.35)
            ax.plot(sel.index, smooth(sel), color=COLORS[label], lw=1.6, label=label)
        ax.axvline(refresh, color=COLORS["K2"], ls="--", lw=1)
        ax.set_title(f"{key.replace('diag_', '')} around {refresh // 1000}k", fontsize=10)
        ax.grid(alpha=0.25)
axes[0, 0].legend(fontsize=9)
fig.suptitle("K2 state-pool refreshes (orange dashed) vs K1 without refresh; thin = raw log rows, thick = rolling mean "
             "over 10 log rows (training-log diagnostics)", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.96))
save(fig, "train-curves-k2-refresh.png")

fig, axes = plt.subplots(1, 4, figsize=(20, 4.4))
for ax, key in zip(axes, ["diag_target_recall", "diag_error_gate_recall", "diag_hard_dice_target",
                          "diag_preserve_edit_voxels"]):
    k3 = D["K3"].set_index("step")[key]
    k1 = D["K1"].set_index("step")[key]
    common = k3.index.intersection(k1.index)
    diff = (smooth(k3[common]) - smooth(k1[common]))
    diff = diff[diff.index > 1000]                   # the first 1k steps reflect the different starting weights
    ax.plot(diff.index, diff, color=COLORS["K3"], lw=1.4)
    lo_q, hi_q = np.nanpercentile(diff, [1, 99])
    pad = 0.15 * (hi_q - lo_q)
    ax.set_ylim(min(lo_q - pad, -pad), max(hi_q + pad, pad))   # a few single-window spikes fall outside
    ax.axhline(0, color="black", lw=0.8)
    ax.set_title(f"K3 minus K1: {key.replace('diag_', '')}", fontsize=10)
    ax.set_xlim(1000, 33000)
    ax.set_xlabel("optimiser step")
    ax.grid(alpha=0.25)
fig.suptitle("K3 (wider trunk) minus K1 at matched steps, from step 1k; difference of rolling means over 10 log rows "
             "(training-log diagnostics; y-axis set to the 1st-99th percentile, isolated spikes are cut off)",
             fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.94))
save(fig, "train-curves-k3-vs-k1.png")

fig, axes = plt.subplots(1, 4, figsize=(20, 4.4))
mix_panels = [("pool_on_policy", "induced (on-policy) states per unit"), ("pool_share_gap", "gap-weighted draws per unit"),
              ("pool_share_refresh", "refreshed states per unit (K2)"), ("relation_swap", "units with a swap relation")]
for ax, (key, title) in zip(axes, mix_panels):
    curve(ax, key, frames=PU)
    mark_events(ax)
    ax.set_title(title, fontsize=10)
    ax.set_ylim(0, 1)
axes[0].legend(fontsize=9)
fig.suptitle("Training mix per unit (window sums / 40 units); rolling mean over 10 log rows. K1, K2 and K3 draw "
             "identical units until K2's first refresh at 10k, and K1 = K3 up to 32k, so their lines overlap there",
             fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.94))
save(fig, "train-curves-data-mix.png")

# first 3,000 steps: where the runs separate
fig = plt.figure(figsize=(20, 9))
grid = fig.add_gridspec(2, 3, height_ratios=(1, 1))
top = [fig.add_subplot(grid[0, i]) for i in range(3)]
for ax, (key, title, logy) in zip(top, [("diag_target_recall", "target recall", False),
                                        ("diag_error_gate_recall", "error-gate recall", False),
                                        ("diag_preserve_edit_voxels", "wrong edits on preserve voxels (log)", True)]):
    for label, df in D.items():
        sel = df[df.step <= 3000].set_index("step")[key]
        ax.plot(sel.index, sel, color=COLORS[label], lw=0.5, alpha=0.3)
        ax.plot(sel.index, smooth(sel), color=COLORS[label], lw=1.6, label=label)
    if logy:
        ax.set_yscale("log")
    ax.axvline(1000, color="#bbbbbb", lw=0.8, ls=":")
    ax.axvspan(2000, 3000, color="#eeeeee", lw=0, zorder=0)
    ax.set_xlim(0, 3000)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("optimiser step")
    ax.grid(alpha=0.25)
top[0].legend(fontsize=9)
bottom = [fig.add_subplot(grid[1, i]) for i in range(3)]
for ax, label in zip(bottom, ("v1 flat", "K1", "K3")):
    wg = WG[label]
    early = wg[wg["step0"] < 3000]
    terms = [t for t in GRAD_TERMS if "wn_" + t in wg.columns]
    w = early[["wn_" + t for t in terms]].to_numpy()
    shares = w / w.sum(axis=1, keepdims=True)
    bottom_edge = np.zeros(len(early))
    for j, t in enumerate(terms):
        ax.bar(early["step0"], shares[:, j], width=160, bottom=bottom_edge, color=TERM_COLOR[t], label=TERM_LABEL[t])
        bottom_edge += shares[:, j]
    ax.set_xlim(-150, 2950)
    ax.set_ylim(0, 1)
    ax.set_title(f"{label}: weighted gradient-norm share of each measured unit", fontsize=11)
    ax.set_xlabel("optimiser step of the measured unit")
handles, labels_ = bottom[1].get_legend_handles_labels()
fig.legend(handles, labels_, loc="lower center", ncol=5, fontsize=9, bbox_to_anchor=(0.5, -0.04))
fig.suptitle("First 3,000 steps. Top: thin = raw log rows, thick = rolling mean over 10 log rows (training-log "
             "diagnostics; dotted = step 1k, grey = state-loss ramp). Bottom: one unit every 200 steps, unsmoothed",
             fontsize=10)
fig.tight_layout(rect=(0, 0.04, 1, 0.96))
save(fig, "train-curves-first-3k.png")
print("\nDone.")
