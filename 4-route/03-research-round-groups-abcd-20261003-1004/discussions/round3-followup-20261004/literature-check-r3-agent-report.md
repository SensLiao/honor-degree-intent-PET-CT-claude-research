Literature verification for ChatGPT round 3 (10-04 AEDT, Claude Code background agent, web read-only).
Claude Code additionally re-fetched the LIM-Net arXiv abstract page (2412.08315): title "Lightweight Method for Interactive 3D Medical Image Segmentation with Multi-Round Result Fusion", Shen, Chang, Chen, Guo, Liu, submitted 11 Dec 2024; the abstract states a Multi-Round Result Fusion module that selects and merges optimal masks from multiple rounds. The per-slice revert detail below comes from the agent's full-text read.

Summary: no published method matches the planned local undo candidates, but rollback to the system's own previous round already exists in a coarser form, so that claim needs narrowing. On paired consistency, the "same target, different prompt -> same output" half is published; the "target swap" half exists in referring segmentation, not in corrective-stroke editing.

1. CPC-SAM (Miao et al., MICCAI 2024, arXiv 2407.05416)
- Verified: yes. Section name is "Prompt Consistency Regularization" (Sec. 2.3), not "Prompting".
- Sec. 2.2 "SAM-enabled Cross Prompting": the unprompted output of one decoder branch generates point prompts for the other branch, whose prompted output supervises the first.
- Sec. 2.3: a center point and a random point from the largest connected component of the other branch's unprompted prediction (noisy pseudo-label); both through the same decoder; the random-point output is pulled toward the average of the two outputs with Dice + cross-entropy, symmetric, unlabeled images only.
- No target swap (no negative prompts, no prompts on a different object).
- Read: arXiv HTML v1 and MICCAI 2024 PDF (papers.miccai.org/miccai-2024/paper/0321_paper.pdf).

2. Correction-aware interactive 3D tumor segmentation with sparse and revisable prompts (The Visual Computer 2026)
- Verified from full text (CC BY 4.0; WebFetch hit a login page, PDF downloaded directly).
- Authors Hao Li (Vanderbilt), Haoxuan Li (Shanghai University of Sport). Vis Comput 42:370, online 29 June 2026. Backbone follows PRISM (MICCAI 2024).
- Full text has: residual correction (selected logit + learned gate x residual map); prompts sampled from FN and FP regions; a "latest-write rule" for positive/negative prompt maps; a cumulative revision channel marking voxels whose user label flipped.
- Inputs each round: image, previous prediction (dense mask prompt), accumulated prompt history.
- Candidate selection: decoder outputs several whole masks each with regressed Dice; top-scored goes to refinement.
- No rollback/undo candidates built from its own previous-round changes; "revision" = user relabels a prompt location.
- Test Dice PRISM -> theirs: MSD-Colon 93.79 -> 95.43, KiTS21 96.58 -> 97.19; single split, single seed; revision test synthetic.
- Contrast for us: they track user-label flips; we track system-write flips.

3. EFPNet (ICML 2026, PMLR 306:45689-45702)
- Verified: partly (substance matches, wording does not). Title "Interactive Segmentation with Elaborate Focus Prior". Authors Kangpeng Hu, Yinghui Sun, Tao Wang, Weihao Zhang, Quansen Sun.
- Abstract: predicts an error mask from "historical feedback" plus the new click, largest connected component = focus region, then corrects using image/feature/mask similarity. "Historical feedback" = previous-round mask, not a click log. "Attention range" is not the abstract's wording.
- Full text: inputs image, disk maps of all clicks, previous mask; training target = connected FP or FN component of the previous mask that contains the new click; correction pulls the previous mask toward the click label inside the focus box.
- Single output; no candidate set; no undo.
- Read: abstract page and PDF (local text extraction).

4. SCISSR (MICCAI 2026)
- Verified: yes, one correction. Title "SCISSR: Scribble-Conditioned Interactive Surgical Segmentation and Refinement". Authors Haonan Ping, Jian Jiang, Cheng Yuan, Qizhen Sun, Lv Wu, Yutong Ban. Official MICCAI 2026 open-access page.
- Mechanism matches: union of all scribbles = dense prompt for SAM 2 mask decoder; only the latest scribble goes into the memory-attention query via a binary on/off gate plus a zero-initialised learnable scalar; memory holds only the previous round's prediction.
- Correction: 79.42 / 90.03 / 91.60 = sample-average mIoU on EndoVis 2018 (N = 4,616) for the Contour-scribble variant at R0/R2/R4; Adaptive variant 75.72 / 88.32 / 90.18.

5. Jeurissen, Self & Roelfsema 2016 (eLife 5:e14320)
- Verified. Experiment 1B (30 new participants): Euclidean model (and pixel-by-pixel model) 49% of RT variance; growth-cone 72%, significantly better (bootstrap, p < 0.01); slope 22 ms per growth cone (95% CI 17-27).
- Growth-cone size = largest inscribed circle diameter with a floor: minimum 1 degree, fixed a priori (about the smallest V1 receptive-field size), not fitted; no sensitivity test found. Only the regression intercept and slope are fitted.
- Read: PMC HTML; sentences checked in Europe PMC full-text XML.

6. LORE (MICCAI 2026 satellite, CLiMeM)
- Verified. Title "Learning to Reason Over Physician Corrections: An Interactive Agentic Framework for 3D Tumor Segmentation". Authors Nourhan Bayasi, Fereshteh Yousefirizi, Arman Rahmim (UBC / BC Cancer). LNCS 17263 satellite index.
- Method: frozen 3D SAM with LoRA plus a Double-DQN agent choosing next prompt type (point, box, scribble, stop); part of the reward predicts where the physician will correct next.
- Information condition (Sec. 2.4): GT FP/FN maps, Dice features and stop rules in training and simulated evaluation; at clinical inference uses the gap between current mask and physician's correction.
- All reported results come from GT-informed simulation (incl. FDG-PET head-and-neck and lung sets); no evaluation of the GT-free variant found.

7. Bouthillier et al., MLSys 2021, "Accounting for Variance in Machine Learning Benchmarks"
- Verified. Variance sources: data sampling (bootstrap), augmentation, weight init, dropout, data order, numerical noise, hyperparameter tuning. Data bootstrap largest; weight init usually under half the bootstrap variance, similar to data order.
- Recommendation: randomize as many sources as possible incl. data splits; decide A vs B by P(A outperforms B) (suggested 0.75) with CI, not by mean difference.

8. Novelty search (~20 WebSearch queries; Exa rate-limited). No explicit equivalent found. Closest:
a) LIM-Net (Shen et al., arXiv 2412.08315, Dec 2024; no peer-reviewed version found): per slice, a network compares previous and current masks and estimates whether the previous one is better; above a threshold that slice reverts. Learned rollback to its own last output, but whole slices, not limited to changed voxels, not tied to the user's new correction location.
b) IBISAgent (CVPR 2026 per official repo, arXiv 2601.03054): MLLM issues clicks to MedSAM2; training data include synthetic sequences where the agent detects a wrong action, reverts to the previous state and re-reasons. Whole-step self-retraction; actions are clicks and stop only; no user in the loop.
c) FocalClick Progressive Merge (CVPR 2022), VTMR (AAAI 2024), Clore (arXiv 2603.27625, 2026): keep only the connected part of the new-vs-previous mask difference touching the new click. Rejects the current round's distant changes by rule; never retracts the previous round's edit; no scorer.
d) TIA (Wei, Zhang, Yong, BMVC 2024): feeds the difference between a coarse current prediction and the previous mask as an error hint; delta as input only. Stability metrics reusable.
e) Candidate set plus learned selector without undo: Latent Diversity (CVPR 2018), PRISM (MICCAI 2024), Visual Computer 2026, PiClick (Neurocomputing 2024), SegAgent (CVPR 2025).
f) History used, no candidates/undo: Visual Computer 2026, SCISSR, MAIS (MIDL 2025, abstract only), LORE, MediRound (arXiv 2025, corrects internal features). SLIP (arXiv 2607.22332): undo exists but user-triggered.
Paired consistency: invariance half published (CPC-SAM; VTMR agreement across two starting masks of matched quality). Swap-like loss published in referring segmentation: Prompt-RIS (CVPR 2024) raises overlap for the same object, lowers it for different objects. Not found: corrective-stroke pairs sharing the same current mask where the stroke picks one of several coexisting errors.
Caveat: web search, not a full database sweep; very recent preprints could be missed.

Required changes to the novelty statement:
1. Replace "undo candidates from own previous-round edits not seen": claim only local undo candidates limited to voxels written back last round, opposite sign, triggered where the new stroke lands.
2. Do not claim learned scorer among candidates or no-op as new.
3. Do not claim stroke-anchored connected-component edits; the new part is undo + along-stroke + continue-repair + no-op competing under one scorer.
4. Do not claim residual correction, latest-stroke-wins or a revision channel; contrast user-label flips vs system-write flips.
5. Paired consistency: cite CPC-SAM and VTMR (invariance) and Prompt-RIS (same/different target); claim only same-state corrective-stroke pairs with redraw invariance plus a target swap where the unmarked error must stay unchanged.
