# Magma Paper Audit

| status | check | detail |
| --- | --- | --- |
| PASS | ASCII TeX source | No direct non-ASCII characters in manuscript source. |
| PASS | Placeholder scan | No TODO/TBD/FIXME-style tokens found. |
| PASS | IEEEtran conference mode | Uses IEEEtran conference document class. |
| PASS | IEEE title capitalization | No lowercase long title prepositions found. |
| PASS | IEEE abstract shape | 195 words, one paragraph, no citations or display math. |
| PASS | IEEE keywords | 6 alphabetized keywords. |
| PASS | Citation coverage | 10 cited keys resolved. |
| PASS | Unused bibliography entries | Every bibitem is cited. |
| PASS | Reference coverage | 7 refs resolved. |
| PASS | Figure files | All includegraphics targets exist. |
| PASS | Required sections | 12 expected sections present. |
| PASS | Novelty versus rapid tooling | Prior-work distinction is explicit and scoped. |
| PASS | Reproducibility and validity language | Claim classes and physical-data requirements are explicit. |
| PASS | PDF page count | 6 pages. |
| PASS | Output PDFs | PDF copies exist under output/pdf and output/tex. |
| PASS | Rendered page PNGs | 6 rendered pages in tmp/pdfs. |
| PASS | G-code verification table backing | 5 verifier rows; all artifact names appear in manuscript. |
| PASS | Verifier flow values in TeX | All exact flow values appear in manuscript. |
| PASS | Native slicer source evidence | 4 source checks passed. |
| PASS | Transcript-backed experiment log | paper/experiment_log_2026-06-27.md |
| PASS | Transcript evidence index | paper/transcript_evidence_index.md |
| WARN | Physical fill trial data | No measured fill-trial rows yet; acceptance-critical physical dataset is still missing. |
| PASS | Fill trial summary artifact | output/verification/fill_trial_summary.md |
| PASS | Fill trial asset artifact | output/verification/fill_trial_assets.md |
| PASS | Fill trial LaTeX artifact | output/verification/fill_trial_table.tex |
| WARN | Physical data readiness | Submission-strength physical dataset is not ready yet. |
| PASS | Fill photo panel report | output/verification/fill_photo_panel_check.md |
| PASS | Fill trial plan coverage | core_rows=9, missing_combos=[], section_required=['P005', 'P009', 'P010'] |
| PASS | Fill trial plan artifact | output/verification/fill_trial_plan_summary.md |
| PASS | Fill trial execution packet | 10 run sheets; 10 prefill rows. |
| PASS | Trial execution readiness | output/verification/trial_execution_readiness.md |
| PASS | Planned injection G-code snippets | 10 planned snippets. |
| PASS | Standard mold assets | 10 mold STLs; paper/molds/mold_manifest.md |
| PASS | Claim scope check | output/verification/claim_scope_check.md |
| PASS | Claim-evidence map check | output/verification/claim_evidence_check.md |
| PASS | IEEE submission readiness check | output/verification/ieee_submission_check.md |
| PASS | PDF production check | output/verification/pdf_production_check.md |
