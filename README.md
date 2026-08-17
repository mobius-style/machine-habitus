# machine-habitus — study artifacts

Artifacts for **"Measuring Machine Habitus: A Pre-Registered Multiple Correspondence Analysis of LLM Disposition Space"** (Toeda, 2026; DOI 10.5281/zenodo.21982393, live on Zenodo publication).

A pre-registered, hash-frozen measurement study: 120 forced-choice dilemmas (no correct answers), 7 LLM subjects × 5 sessions, multiple correspondence analysis. One confirmed hypothesis (session-stable, model-specific disposition; Holm p = 0.0004), three diagnosed nulls, one protocol breach caught by adversarial model review and remediated under the frozen rule.

## Layout

- `PREREG.md`, `FREEZE_RECORD.txt` — frozen pre-registration + SHA-256 seals
- `battery_main.json` / `battery_pilot.json` — 120-item main battery / 30-item pilot (Japanese)
- `judge_task.json` — 40 TRUE/FALSE claims (H1b/H3 instrument)
- `run_main.py`, `run_judge.py` — frozen collection runners; `assemble_claude.py` — Claude-subject assembly
- `responses_main/`, `responses_judge/` — raw valid sessions; `responses_*_excluded/` + `EXCLUSION_LOG.txt` — frozen-rule exclusions
- `claude_main/`, `claude_judge/` — Claude-subject prompts, presented→original mappings, raw answers
- `analyze_main.py` (frozen) → `results_main.json`; disclosed corrections & exploratory analyses → `results_supplement.json`; `ERRATA.md`
- `analyze_pilot.py`, `responses/` — pilot calibration
- `review_record/` — three rounds of adversarial model review (verdicts + summaries)
- `MANUSCRIPT.md`, `DESIGN.md` — paper draft v0.4 and design document

## Reproduce

```
python3 analyze_main.py          # confirmatory pipeline on responses_main/ + responses_judge/
```
Deterministic seeds: session shuffles = sha256(model|s{n}|main-v1.0); held-out split = sha256("holdout|main-v1.0").

## License

AGPL-3.0-or-later (battery, data, code). The paper text is CC BY-NC-SA 4.0 (see the Zenodo record).
