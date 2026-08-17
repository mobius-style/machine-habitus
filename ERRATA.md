# Errata / reading notes for frozen outputs

- `results_main.json` `holm` object was produced by the frozen `analyze_main.py`, whose Holm step lacked monotonicity enforcement. The corrected Holm-adjusted p-values (identical conclusions) are in `results_supplement.json` `holm_corrected` and are the values reported in MANUSCRIPT.md §4.5. The frozen file is preserved unmodified for auditability.
