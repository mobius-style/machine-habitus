# Pre-Registration — Machine Habitus: Measuring LLM Disposition Space via Multiple Correspondence Analysis

Status: **FROZEN** upon insertion of timestamp and SHA-256 hashes in §6. No post-freeze modification of hypotheses, materials, protocol, exclusion rules, or analysis code. Deviations demote the affected claim to exploratory (one-way valve).

## 1. Confirmatory hypotheses (4 tests, Holm correction)

- **H1 (Transposability).** The 5 sessions of each model cohere in the top-2-dimension MCA space built from the 96 training items. Statistic: mean between-model distance − mean within-model distance. Test: label permutation, 10,000 draws, one-sided. Effect size: mean silhouette with bootstrap 95% CI (5,000 draws).
- **H1b (Stability × capability).** Per-model within-session dispersion correlates negatively with judge-task accuracy. Spearman ρ, permutation 10,000, one-sided (negative).
- **H2 (Generativity).** Each session's answers on 24 held-out items (selected before collection by seed hash("holdout|main-v1.0")) are predicted by its nearest-neighbor session in training space. Accuracy must exceed a random-neighbor permutation null (2,000 draws), one-sided.
- **H3 (Judge independence).** Distance between model centroids in MCA space correlates negatively with the φ correlation of the models' error-indicator vectors on the judge task. Spearman ρ, Mantel-type label permutation 10,000, one-sided (negative).

**Consequences of rejection.** If H1 fails, the study is written up as a negative result ("session-level disposition stability is not detectable under this design") with no re-framing. H1b/H2/H3 may fail individually; the corresponding claim is then demoted to exploratory.

## 2. Materials (frozen)

- Battery: `battery_main.json`, 120 forced-choice items, 4 options each, all options defensible. Composition: 22 pilot survivors + 98 new items; the 8 pilot items with zero discriminative power (identical modal answer across all pilot models) were removed under the pre-stated calibration rule. Layers: canon 8 / neutral 112. Stimulus language: Japanese (frozen design choice; discussed as a limitation).
- Judge task: `judge_task.json`, 40 claims with objective TRUE/FALSE gold labels (20/20), six content areas, self-verified rationales at authoring time.
- Subjects (7): gemma4:26b-a4b-it-qat, gemma4:12b-it-qat, qwen3.6:27b-q4_K_M (Ollama; think:false, num_ctx:8192), openai/gpt-oss-120b (Groq; reasoning_effort:low), deepseek-v4-pro (DeepSeek API), claude-haiku, claude-sonnet (Claude Code Agent runtime).
- Sessions: battery 5 per model; judge task 3 per model. Temperatures: backend defaults, unchanged.

## 3. Administration protocol (frozen)

- A session = the set of 3 stateless calls (blocks of 40 items) whose item order, option order, and block assignment are determined by seed sha256(model|s{n}|main-v1.0). No context is shared between blocks. Presented-letter → original-letter mappings are stored for every session.
- Judge task: one call of 40 claims, item order shuffled by seed sha256(judge|model|s{n}). A model's verdict per claim = modal answer over its 3 sessions (tie or all-NR → NR).

## 4. Preprocessing and exclusion rules (frozen)

- Parsing: "(item-ID) N: letter" with presented→original remapping; unparseable or missing = NR. NR is retained as data but **NR columns are not used to construct the MCA space**.
- Session exclusion: any session with NR ≥ 50% is excluded and replaced by an additional session (s6, s7, …) under the same seed rule until 5 valid sessions exist; exclusions are logged.
- Analysis implementation: `analyze_main.py`, frozen together with this document.

## 5. Deviation policy

Post-freeze changes demote affected claims to exploratory. Any additional analyses are reported in a separate exploratory section.

## 6. Freeze record

- Frozen at: 2026-08-17T23:53:53+09:00 (hashes below computed at freeze; see FREEZE_RECORD.txt for the machine-generated line including this file's own hash)
- battery_main.json SHA-256: `9ed083fe2480627c162dca6328659d47b6dbf64fa73af1f9c5931d50711f1120`
- judge_task.json SHA-256: `fc5bdc0b97ca4634c234d5062b4fb2f70ee7763bfb4cdecb5225be29a02cf28f`
- analyze_main.py SHA-256: `34cb24c109cedf47d6f63e94a36c36f0793dffb80495a29ce99b8cfa0f000387`
- run_main.py SHA-256: `c1c4a51a079dc9fbf75cdbf648294110f8724be5e0f03129707d439db3d86c9c`
- run_judge.py SHA-256: `358039894508396c0982e688408e05172e1a91d943b5ec0d586b2b222c4845c8`
