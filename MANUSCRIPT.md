# Measuring Machine Habitus: A Pre-Registered Multiple Correspondence Analysis of LLM Disposition Space

**Version:** draft v0.4 (2026-08-18) — after three adversarial review rounds (3 independent model judges; R1: 3/3 REFUTED; R2: 2/3 SURVIVES; R3 file-access judge: narrow REFUTED with full recomputation ledger green and 1 stale numeric + 4 minor phrasings, all corrected herein; see `review_record/`)

## Abstract

Large language models exhibit consistent styles of judgment that are not reducible to capability scores, yet attempts to measure them with human psychometric instruments have been criticized as measurement artifacts. We propose a behavioral, relational alternative inspired by Bourdieu's habitus and Airoldi's *machine habitus*: a pre-registered battery of 120 forced-choice dilemmas with no correct answers, administered in seed-shuffled stateless blocks to 7 models (35 valid sessions), analyzed with multiple correspondence analysis (MCA) rather than a factor model imported from human populations. The confirmatory session-stability hypothesis was supported with a moderate effect: independent sessions of the same model cohere in disposition space (between/within distance ratio 2.40; mean silhouette 0.258, bootstrap 95% CI [0.125, 0.384]; permutation p ≤ 1/10,001; Holm-adjusted p = 0.0004). Pre-registered exploratory follow-ups show the clustering replicates independently in each half of the item domains (ratios 1.87 and 2.01, each p ≤ 2×10⁻⁴, exploratory), supporting — though not yet confirming — transposability. Three further pre-registered hypotheses (held-out generativity, a stability-capability link, and prediction of judge error decorrelation) were not supported; we diagnose the failures (a mis-specified baseline and a ceiling effect that also forced imputation in 9 of 15 correlation pairs) and demote them per protocol. We document a protocol-execution error caught by adversarial review — one session exceeding the frozen non-response threshold was initially admitted — and its rule-compliant remediation by replacement collection, after which the confirmatory result is unchanged. All materials, raw sessions, exclusion logs, and analysis code are released. 【claim grades: session stability = single pre-registered confirmatory study; domain replication = exploratory; all other findings = exploratory or null】

## 1. Introduction

When the same canon of instructions, memories, and procedures is handed to different language models, they do not run it the same way. Practitioners know this as "model feel": a disposition to prefer certain trade-offs — speed versus certainty, discretion versus procedure, building versus reusing — that persists across tasks and sessions. As AI deployment shifts toward rich user-context reuse (persistent memories, personal canons, delegated agency), the question of *how a given model will inhabit the same context* becomes a first-order engineering variable. It is also a measurement problem that existing tools handle poorly.

Two literatures frame the problem. First, *LLM psychometrics* has imported human self-report instruments wholesale, and a growing critical literature finds the resulting profiles to be largely measurement artifacts: factor structures do not replicate, response biases dominate, and self-report fails to predict behavior. Second, sociology offers a concept engineered for what practitioners describe: Bourdieu's **habitus** — durable, transposable dispositions that generate practices without explicit rules. Airoldi's *Machine Habitus* (2021) argued theoretically that algorithms trained on social data acquire such dispositions. What has been missing is an operationalization. Bourdieu's own empirical program measured habitus not with trait questionnaires but with **multiple correspondence analysis** over concrete choices, constructing a relational space in which proximity is similarity of practice.

We transplant that program to language models, with deliberately modest scope: we do not claim to measure the full sociological construct. We test two necessary marks of habitus-like structure — **durability** (stability across independent sessions) and **transposability** (recurrence of the structure across judgment domains) — and we attempt one application (judge-panel composition). Our design answers the artifact critique directly: (i) items are behavioral forced choices among defensible options, not self-reports; (ii) analysis is MCA, which imposes no human factor model; (iii) individuals are *sessions*, so within-model dispersion is measured rather than assumed; (iv) validity criteria are behavioral and pre-registered.

**Contributions.** (1) A 120-item forced-choice battery for LLM disposition measurement, pilot-calibrated to remove consensus items; (2) a pre-registered MCA study across 7 models / 35 sessions supporting session-stable, model-specific disposition, with exploratory evidence of cross-domain replication; (3) an honest negative report on three application hypotheses with diagnoses that fix the next iteration; (4) a documented case study in enforcement of frozen protocols, including a data-admission error caught by adversarial model review and remediated under the frozen rule; (5) release of all materials under a hash-sealed protocol.

## 2. Related work

**Machine habitus and the sociology of algorithms.** Airoldi (2021) extends Bourdieu to algorithmic agents theoretically; follow-up work examines chatbot taste qualitatively. We contribute a quantitative operationalization with pre-registered validity criteria.

**LLM psychometrics and its critics.** Human questionnaires have been shown to mischaracterize LLM behavior: latent factors are arbitrary, response bias dominates and shrinks with capability, and profiles disagree across frameworks. The closest prior study administers an LLM-native instrument to 25 models (300 items, largely Likert self-report, exploratory factor analysis, model-level individuals) and finds self-report predicts neither ratings nor objective text measures. We differ on four design axes: behavioral forced choice only; MCA instead of EFA; sessions as individuals; validation by stability/transposability/application rather than convergence with self-report.

**Behavioral fingerprinting.** Fingerprinting identifies models from response patterns for provenance and IP protection. Our H1, taken alone, is congruent with that literature's premise — model responses are identifiable — and we do not claim novelty for identifiability itself. The added value lies in (a) the *relational geometry* (positions and distances, not just identity), (b) the habitus-derived validity program (session-individuals, domain replication), and (c) the application target (panel composition), which identification does not address.

## 3. Method

All confirmatory decisions were frozen before main collection in `PREREG.md` (SHA-256-sealed with the battery, judge task, runners, and analysis code; `FREEZE_RECORD.txt`). Post-freeze events are governed by the frozen exclusion and deviation rules; every exception that occurred is documented in §4.1 and `EXCLUSION_LOG.txt`.

### 3.1 Instrument

**Battery.** 120 forced-choice dilemmas, 4 options each, in Japanese, across 8 domains: resource allocation, build-vs-search, reversibility, verification demands, delegation, risk/time preference, candor, and rule-exception handling. Every option is defensible by design. A 30-item pilot (5 models × 3 sessions) calibrated the pool: 8 items on which every pilot model gave the same modal answer were removed under a pre-stated rule and retained descriptively as **machine doxa** (§5.1). Final pool = 22 pilot survivors + 98 new items; provenance layers (8 canon-derived / 112 neutral) support a robustness check that is underpowered as realized (§4.4).

**Judge task.** 40 claims with objective TRUE/FALSE gold labels (20/20) across six content areas, authored to punish pattern-matching, with self-verified rationales.

### 3.2 Subjects and administration

Seven models spanning four families and three deployment regimes: gemma4-26b-a4b-it-qat, gemma4-12b-it-qat, qwen3.6-27b-q4_K_M (local, quantized, Ollama); openai/gpt-oss-120b (Groq); deepseek-v4-pro (vendor API; the 2026-08-13 GA checkpoint was current at collection); claude-haiku and claude-sonnet (Claude Code agent runtime, 2026-08 production aliases). Collection dates: pilot 2026-08-17; main and judge 2026-08-17/18 JST. Five valid battery sessions per model; three judge sessions per model. A session is a set of three **stateless** 40-item calls whose item order, option order, and block assignment derive from seed sha256(model|s{n}|main-v1.0); no context is shared between blocks; presented-to-original option mappings are stored. Temperatures are backend defaults; numeric values are not exposed by all backends and were not recorded — sessions should therefore be read as *presentation-perturbed replicates* (item and option order differ per session), and H1 as robustness of position to presentation, not as sampling-temperature variance (limitation §7.2). Known backend traps were pre-committed in the frozen runner (think:false, num_ctx=8192 for Ollama; reasoning_effort:low for gpt-oss).

### 3.3 Analysis (frozen) and disclosed corrections

Indicator-matrix correspondence analysis over the 96 training items (non-response recorded but not used to construct the space); session coordinates on the top-2 dimensions (a projection fixed ex ante; it carries 14.7% of inertia, §4.2). **H1**: mean between-model minus within-model distance, label permutation (10,000), silhouette with bootstrap CI. **H2**: nearest-neighbor prediction of 24 seed-selected held-out items vs a random-neighbor null. **H1b**: Spearman ρ between per-model dispersion and judge accuracy (one-sided negative). **H3**: Spearman ρ between centroid distances and error-vector φ correlations (Mantel permutation, one-sided negative). Holm correction over the four tests.

Four implementation defects in the frozen analysis script were identified by adversarial review and are corrected *with disclosure* (the frozen script is unmodified; corrections are in `results_supplement.json` and reported here): (a) the Holm step-down lacked monotonicity enforcement; corrected adjusted p-values are reported below; (b) H3's implementation imputes φ = 0 whenever an error vector has zero variance, which occurred in **9 of 15 pairs** (the algebraically forced count given two perfect-accuracy models) — H3 as run is therefore not interpretable and is reported as such; (c) permutation floors are reported as p ≤ 1/(B+1) rather than point values; (d) the Spearman implementation assigns arbitrary ranks to ties rather than midranks, so ρ values on tie-bearing vectors are order-dependent — the midrank-corrected H1b coefficient is ρ = −0.44 (supplement; conclusions unchanged), and H3 is unaffected because it is already excluded from interpretation under (b). Additionally, the H1 bootstrap CI resamples 35 mutually dependent per-session silhouettes nested in 7 models; it quantifies sampling noise of the mean silhouette, not model-level generalization (limitation §7.6).

## 4. Results

### 4.1 Data quality, frozen-rule enforcement, and a disclosed protocol-execution error

39 battery sessions were collected in total (30 across six models plus a nine-session replacement chain for deepseek-v4); 4 were excluded under the frozen rule (deepseek-v4 s1, s6, s7, s8, all NR ≥ 50%), leaving 35 valid sessions, five per model. Per-session non-response counts are published in `results_supplement.json`; the distribution is: median 2/120, with heavier valid sessions deepseek-v4 s9 = 46, s5 = 40, s4 = 31, gemma4-26b s4 = 33, qwen3.6-27b s4 = 19, gemma4-26b s1 = 15, gpt-oss-120b s3 = 11.

**Disclosed error and remediation.** In the first analysis run, deepseek-v4 s1 (NR = 81/120 = 67.5%) was admitted in violation of the frozen §4 exclusion rule, and the initial manuscript draft misattributed the heavy-NR sessions. Both faults were caught by the adversarial review panel (§ review_record), not by the authors. Remediation followed the frozen rule only: s1 was excluded and replacement sessions were collected under the pre-registered seed rule until a valid session existed (s6: NR 80 → excluded; s7: 120 → excluded; s8: 80 → excluded; s9: 46 → retained). All confirmatory numbers reported in this version derive from the compliant 35-session set. The repeated failures share one mechanism, analyzed in §5.3.

**Judge task.** deepseek-v4 returned empty content in 6/6 judge attempts (3 original + 3 replacements under the same rule); with no valid verdicts, the model necessarily drops out of the judge-dependent analyses. Because a model-level exit was *not* pre-specified (only session-level exclusion was), H1b and H3 as run constitute a deviation and are **demoted to exploratory** under the frozen deviation policy — independently of their outcomes, which were null in any case.

### 4.2 H1 — Session stability: supported (moderate effect)

Sessions of the same model cohere in disposition space:

- between/within mean distance ratio = **2.40** (difference = 0.442);
- mean silhouette = **0.258**, bootstrap 95% CI **[0.125, 0.384]** (dependence caveat, §3.3);
- label permutation **p ≤ 1/10,001** (0 exceedances in 10,000 draws); corrected Holm-adjusted p = **0.0004**;
- top-2 dimensions carry 8.2% + 6.5% = **14.7%** of inertia.

【grade: 実証中 — single pre-registered confirmatory study】 The effect is moderate, not overwhelming: silhouette 0.258 indicates clearly separated but adjacent clusters in the fixed 2-D projection. What the result establishes is the minimal durability mark: five memoryless sessions of a model, each seeing different item and option orders, land in the same region of practice space, and models land apart — measured without self-report and without a human trait model.

**Disclosed relabeling.** PREREG §1 names H1 "Transposability"; as frozen and implemented, the test measures session-level coherence over the pooled item space and does not itself separate domains. We therefore report H1 under the more precise name *session stability* and treat domain-level transposability as an exploratory follow-up (§4.3). This is a narrowing of the registered claim's name, disclosed here; no statistic or threshold was altered.

**Robustness (exploratory).** Excluding the four valid-but-heavy sessions (NR > 20) *raises* the ratio to 2.78 (p ≤ 2×10⁻⁴), so the clustering is not an artifact of shared missingness patterns; direct NR-set overlap between deepseek's heavy sessions is at chance (Jaccard 0.15–0.24 vs ≈0.17 expected). Dropping the canon-layer items from the training space (7 of the 8 fall within it; 89 neutral training items remain) leaves the ratio at 2.65, so the clustering does not depend on the canon-derived layer. The exclusion of the four heavy sessions also removes three deepseek sessions (reducing that subject to two), so part of the ratio rise reflects composition, not only missingness removal. Raw within-model answer agreement on training items (pairwise, non-NR) spans 54.4–72.4% against a between-model baseline of 52.8%; for the weakest subject (qwen3.6-27b, 54.4%) the margin over baseline is minimal, so the session-stability evidence is thinnest for that model — consistent with its largest dispersion in §5.2.

### 4.3 Transposability — exploratory support

H1 as frozen tests session clustering on the pooled item space; it does not by itself test the second habitus mark. Two exploratory analyses address it directly:

1. **Independent domain halves.** Building separate MCA spaces from disjoint domain halves (build/candor/delegation/resource vs reversibility/risk/rules/verification), model clustering replicates in each: ratios **1.87** and **2.01**, each permutation p ≤ 2×10⁻⁴. Whatever generates the clustering is not confined to one content region.
2. **Cross-domain geometry.** The rank ordering of inter-model centroid distances agrees positively but non-significantly between the halves (Spearman ρ = 0.39, p = 0.11, 21 pairs): *who is distinct* transposes; *exactly how far* is not yet resolved at n = 7 models.

【grade: exploratory — pre-registered follow-up status not claimed】

### 4.4 H2, H1b, H3 — not supported

- **H2 generativity:** nearest-neighbor held-out accuracy 73.0%, not significant against the random-neighbor null (p = 0.242; corrected Holm 0.726). The null is high because models share substantial answer mass (doxa); the frozen test conflates disposition-specific and population-baseline prediction. The corrected design (a new study) tests incremental accuracy over the grand modal answer.
- **H1b stability × capability** (exploratory per §4.1): ρ = −0.31 as computed by the frozen script (−0.44 with midrank tie correction, supplement), direction as predicted, p = 0.28. Judge accuracies span only 0.90–1.00 — a ceiling effect destroyed the variance required.
- **H3 judge independence** (exploratory per §4.1, and **not interpretable as run**): the nominal ρ = 0.08 is the output of an invalid procedure — 9 of 15 φ values are zero-variance imputations (§3.3b) — and is reported solely for audit completeness, not as an estimate. No conclusion — positive or negative — should be drawn from H3 in this study.
- The canon/neutral layer robustness check: the neutral-only clustering ratio (2.65, §4.2; 7 canon items removed from the 96-item training space) shows the confirmatory structure does not depend on the canon layer; with so few canon items, no canon-side inference is attempted.

### 4.5 Corrected multiplicity summary

Corrected Holm-adjusted p-values over the four registered tests: H1 = 0.0004; H2 = H1b = H3 = 0.726 (monotone). Conclusions are unchanged from the nominal analysis: one confirmed, three null.

## 5. Exploratory findings

**5.1 Machine doxa.** Eight pilot items produced identical modal answers across all five pilot models: *search before building; report failures immediately with logs; distrust too-good results; include minor defects in reports*, among others. In Bourdieu's terms these are doxa — positions so naturalized that no position-taking occurs. Alignment training appears to have homogenized these regions; disposition measurement must be built where training objectives do not dictate a unique answer. This finding also explains H2's high baseline.

**5.2 Structure of the space (descriptive).** Session coordinates are released with the data. Within-model dispersions (top-2 projection; `H1b.withins`) order as: claude-sonnet 0.10 (tightest), claude-haiku 0.13, gemma4-12b 0.13, deepseek-v4 0.17, gpt-oss-120b 0.36, gemma4-26b 0.54, qwen3.6-27b 0.77 (loosest). The ordering does not follow a clean scale or quantization story: the smallest local subject (gemma4-12b, dense QAT) is among the tightest, while the larger MoE sibling (gemma4-26b-a4b, ~4B active parameters, also QAT) and the PTQ-quantized qwen are loosest. An active-parameter account would explain the MoE sibling but not qwen (the largest active count yet loosest), and all three locals are quantized, so no single hardware variable carries the pattern — with 7 models this remains description, not inference. The two gemma4 scales occupy clearly distinguishable positions (centroid distance 0.572, larger than several cross-family distances), so within-family variants do differ in disposition. We refrain from axis interpretation at 14.7% retained inertia.

**5.3 Reasoning-budget collapse as an instrument hazard.** deepseek-v4-pro returned empty content in all 6 judge attempts and, on the battery side, in one original session and three failed replacement attempts (NR 80–120), whenever its reasoning channel consumed the entire token budget under the frozen max_tokens; the failure mode is silence, not error. This is the third variant of the same trap we have observed across backends (gemma think flag; gpt-oss reasoning_effort). Verdict-style tasks provoke reasoning expenditure; batteries for reasoning-mode models must cap reasoning explicitly or verify non-empty content per block at collection time. The frozen protocol's session-replacement rule handled the battery case; the judge case exposed a gap (no pre-specified model-level rule), which the deviation policy then converted into demotion — the intended fail-safe.

## 6. Discussion

**For measurement.** The confirmed result is the one the artifact critique cannot explain away: no self-report, no imposed factor structure, session-level individuals — and still a stable, model-specific position in practice space, replicated (exploratorily) across disjoint domains. This is deliberately less than "measuring habitus"; it is evidence that the two necessary marks Bourdieu's concept requires — durability and transposability — are present in measurable form. The sufficient conditions (genesis in training history, structuring force on downstream practice) remain untested here.

**For panel design.** The practical goal — selecting judge panels by measured disposition distance — remains open. The geometry exists (H1); the link to error decorrelation was not testable in this study because the error-elicitation instrument saturated (accuracies 0.90–1.00) and the analysis imputed most correlation pairs. The negative lesson is itself useful: *for tasks that strong models all solve, panel diversity is irrelevant.* The corrected H3 requires an error-rich regime (target accuracy 0.6–0.8).

**For the user-context era.** If deployment increasingly means handing one persistent context to interchangeable models, context portability is bounded by disposition distance: the same canon will be executed differently at different positions in this space. A 120-item battery measurable in minutes per model gives context owners an instrument for deciding what to delegate to which model — provided the geometry's consequences (H3-type links) are established by future work.

**On enforcement.** One admission error survived the authors' own checks and was caught only by independent adversarial review with file-level access; the frozen rule then determined the remediation mechanically. We take this as evidence for the review protocol itself: self-checking is structurally insufficient, and pre-registration only binds when an external party audits admission against the frozen rules.

## 7. Limitations

1. **Stimulus language** is Japanese only; disposition geometry may be language-dependent.
2. **Temperatures/decoding parameters were not recorded**; sessions are presentation-perturbed replicates, and H1 measures robustness to presentation, not sampling variance. Model snapshots for API subjects are dated, not pinned.
3. **Seven models, one time point**; API models are moving targets — coordinates are dated measurements.
4. **Local subjects are quantized**; quantization, scale, and family are partially confounded.
5. **Judge-task ceiling** invalidated H1b/H3 as run; a recalibrated set (0.6–0.8 accuracy) is required, and the H3 implementation must handle zero-variance vectors by exclusion, not imputation.
6. **Silhouette CI** treats dependent session-level values as exchangeable; model-level uncertainty is larger than the interval suggests.
7. **Two MCA dimensions carry 14.7% of inertia**; the confirmatory statistic was defined on this projection ex ante, but conclusions about the full geometry are correspondingly limited.
8. **No a-priori power analysis**; null results are inconclusive, not evidence of absence.
9. **Author-tool circularity**: two subjects share a vendor with the authoring toolchain; the canon/neutral layer split intended to probe this is underpowered as realized.

## 8. Conclusion

Bourdieu's answer to "what is tacit knowledge?" was: dispositions — measurable not by asking, but by mapping choices relationally. Transplanted to language models under a frozen protocol, the program yields a first supported result: **LLM sessions occupy stable, model-specific positions in a practice space, and the clustering replicates across disjoint judgment domains.** The application hypotheses that motivated the study did not survive their first pre-registered contact with data, for instrument reasons we document and fix; and the study's own protocol enforcement failed once and was repaired only by independent adversarial review. Both facts are part of the result. The battery, data, exclusion logs, and code are released so that the confirmation, the failures, and the enforcement record can be replicated.

## Data and code availability

Project repository contents: frozen pre-registration and hash record (`PREREG.md`, `FREEZE_RECORD.txt`); battery (`battery_main.json`); judge task (`judge_task.json`); collection runners (`run_main.py`, `run_judge.py`, frozen); raw sessions (`responses_main/`, `responses_judge/`); excluded sessions with reasons (`responses_main_excluded/`, `responses_judge_excluded/`, `EXCLUSION_LOG.txt`); frozen analysis (`analyze_main.py`) and outputs (`results_main.json`); disclosed corrections and exploratory analyses (`results_supplement.json`); reading notes for frozen outputs (`ERRATA.md`, including the uncorrected in-file Holm values); pilot materials; adversarial review record (`review_record/`).

## Acknowledgments

Battery and judge-task drafts and all subject sessions were produced by multiple model instances under the supervising author's protocol. Adversarial review was performed by three independent model judges (two model families external to the drafting model); their round-1 refutations materially changed this manuscript, including the detection of the §4.1 admission error.

## References

- Airoldi, M. (2021). *Machine Habitus: Toward a Sociology of Algorithms.* Polity.
- Bourdieu, P. (1979). *La Distinction: Critique sociale du jugement.* Minuit.
- [LLM psychometrics critique cluster — arXiv:2606.20205; arXiv:2509.10078; arXiv:2510.11254]
- [LLM-native instrument study — arXiv:2606.09843]
- [Behavioral/evaluative fingerprinting — arXiv:2601.05114; arXiv:2505.16723]
- [Airoldi-lineage empirical follow-up on chatbot taste — ResearchGate 383582709]

*(Reference list to be completed with full bibliographic entries at deposit formatting.)*
