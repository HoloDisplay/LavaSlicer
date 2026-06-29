# Magma IEEE Paper Package

Primary manuscript:

- `paper/magma_ieee.tex`
- `paper/magma_ieee.pdf`
- `output/pdf/magma_ieee_paper.pdf`

## Rebuild

From the repository root:

```bash
make all
```

This regenerates the G-code verification summary, compiles the IEEEtran PDF with `tectonic`, copies the deliverable PDFs into `output/`, renders page PNGs into `tmp/pdfs/` for visual inspection, runs the submission audit, and writes a reviewer-facing manifest.

Individual targets:

```bash
make verify
make fill-plan
make fill-summary
make physical-readiness
make fill-photo-panel
make fill-molds
make planned-gcode
make fill-packet
make trial-readiness
make transcript-evidence
make claim-scope
make claim-evidence
make ieee-readiness
make submission-package
make audit
make manifest
make paper
make outputs
make render
```

## Verification Evidence

The paper's G-code verification table is backed by:

- `tools/summarize_injection_gcode.py`
- `output/verification/gcode_verification_summary.csv`
- `output/verification/gcode_verification_summary.md`
- `tools/audit_magma_paper.py`
- `output/verification/paper_audit.md`
- `output/verification/pdf_production_check.md`
- `tools/check_claim_scope.py`
- `output/verification/claim_scope_check.md`
- `paper/claim_evidence_map.md`
- `tools/check_claim_evidence_map.py`
- `output/verification/claim_evidence_check.md`
- `paper/ieee_submission_checklist.md`
- `tools/check_ieee_submission_readiness.py`
- `output/verification/ieee_submission_check.md`
- `tools/build_submission_package.py`
- `output/verification/submission_package_check.md`
- `output/submission/magma_ieee_pdf_express_source.zip`
- `output/submission/magma_ieee_review_bundle.zip`
- `tools/summarize_fill_trials.py`
- `tools/check_physical_data_readiness.py`
- `tools/build_fill_photo_panel.py`
- `tools/summarize_fill_trial_plan.py`
- `tools/generate_standard_molds.py`
- `tools/generate_fill_trial_packet.py`
- `tools/check_trial_execution_readiness.py`
- `paper/fill_trial_plan.csv`
- `paper/molds/mold_manifest.md`
- `paper/molds/P001_mold.stl` through `paper/molds/P010_mold.stl`
- `tools/generate_planned_injection_gcode.py`
- `output/trials/planned_injection_gcode_summary.md`
- `output/trials/planned/`
- `output/verification/fill_trial_plan_summary.md`
- `output/trials/fill_trial_packet.md`
- `output/verification/trial_execution_readiness.md`
- `output/trials/evidence_collection_checklist.md`
- `output/trials/minimum_submission_subset.md`
- `output/trials/fill_trials_prefill.csv`
- `output/trials/run_sheets/`
- `output/verification/fill_trial_summary.md`
- `output/verification/fill_trial_assets.md`
- `output/verification/fill_trial_table.tex`
- `output/verification/physical_data_readiness.md`
- `output/verification/fill_photo_panel_check.md`
- `output/figures/fill_trial_photo_panel.png`
- `paper/experiment_log_2026-06-27.md`
- `paper/transcript_evidence_index.md`
- `tools/check_transcript_evidence.py`
- `output/verification/transcript_evidence_check.md`
- `tools/write_submission_manifest.py`
- `output/verification/submission_manifest.md`

The verifier parses representative generated G-code artifacts from `paper/gcode/representative/`, extracting commanded volume, temperature waits, flow, segmentation, and tool path. This supports the software-planning claim only; it does not prove physical cavity fill quality. Native slicer source evidence used by the audit is snapshotted under `paper/source_evidence/` so the paper package does not depend on local nested slicer checkouts.

The audit checks IEEE-facing package details including conference-mode `IEEEtran`, title capitalization, abstract length/shape, alphabetized keywords, citation/reference coverage, figure files, output PDFs, rendered pages, native slicer source evidence, G-code table backing, claim scope, and PDF production constraints such as letter page size, unencrypted PDF, embedded/subset fonts, no links/bookmarks/packages, and no embedded files. Physical fill data are tracked as a warning until measured trial rows are added to `paper/fill_trials_template.csv`. `output/verification/physical_data_readiness.md` adds a stricter submission-strength gate: at least three publishable rows, process-window spread, one success/candidate fill, one labeled failure-mode row, and at least one sectioned or removed-part photo.

`paper/claim_evidence_map.md` is the reviewer-facing claim ledger. It separates backed software/process claims from preliminary observations and from claims that are explicitly not made yet.

`paper/ieee_submission_checklist.md` tracks the PDF-format and package-readiness checks. `make submission-package` produces a minimal PDF eXpress source archive and a local review bundle; the review bundle is for internal handoff, not a substitute for the official conference upload unless explicitly requested.

## Experimental Data Gap

For a substantially stronger IEEE submission, collect the dataset described in:

- `paper/fill_trial_protocol.md`
- `paper/fill_trials_template.csv`

The missing evidence is a measured fill table with commanded volume versus delivered mass/fill depth, explicit failure labels, plus representative photos or sectioned views. Until those are added, the manuscript is best framed as a software/process paper with preliminary physical observations, not a complete manufacturing-performance paper.

The planned experiment matrix lives in `paper/fill_trial_plan.csv`. It covers the required 3 x 3 temperature/flow sweep plus one gated rising-Z follow-up; `make fill-plan` verifies this plan before the paper audit runs.

`make fill-molds` generates standardized open-cup mold STLs under `paper/molds/`. `make planned-gcode` generates injection-stage planning snippets under `output/trials/planned/`; these are not executed evidence. `make fill-packet` turns the plan into a run-ready physical trial packet under `output/trials/`. `make trial-readiness` verifies that the run sheets, prefilled CSV, mold STLs, planned snippets, evidence directories, and generated checklist align before physical data collection. Use the per-trial run sheets during data collection, then copy completed rows from `output/trials/fill_trials_prefill.csv` into `paper/fill_trials_template.csv` only after real masses, scores, executed G-code, and photos exist.

If the full 3 x 3 matrix cannot be run before submission, start with `output/trials/minimum_submission_subset.md`. It selects P001, P005, and P009 to span temperature, flow, candidate-fill, failure-contrast, and section-photo requirements as quickly as possible.

`make fill-photo-panel` turns declared measured-trial photos into `output/figures/fill_trial_photo_panel.png` for a later results figure. It deletes stale output when no measured photos exist, so an old panel cannot be mistaken for current evidence.

The preliminary observations in the manuscript are traced to `paper/experiment_log_2026-06-27.md` and `paper/transcript_evidence_index.md`. The index keeps only technical anchors from the Jun 27 setup transcript and explicitly excludes the raw transcript from submission artifacts.

When measurements are available, add them to `paper/fill_trials_template.csv` and place mold models under `paper/molds/`, executed G-code under `paper/gcode/`, and trial photos under `paper/photos/`. The fill-summary step checks that required publishable-row assets exist and writes `output/verification/fill_trial_assets.md`. Rerun `make all`; the build will emit a LaTeX-ready results table at `output/verification/fill_trial_table.tex`, which can replace or supplement the current validation-plan table once rows are complete.

`paper/reviewer_risk_matrix.md` tracks the likely reviewer objections and the minimum evidence needed to answer them.
