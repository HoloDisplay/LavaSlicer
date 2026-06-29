# Magma Submission Manifest

## Build

- Command: `make all`
- Deliverable PDF: `output/pdf/magma_ieee_paper.pdf`
- PDF pages: 6
- Audit report: `output/verification/paper_audit.md`
- PDF production report: `output/verification/pdf_production_check.md`
- Claim scope report: `output/verification/claim_scope_check.md`
- Claim-evidence report: `output/verification/claim_evidence_check.md`
- IEEE submission readiness report: `output/verification/ieee_submission_check.md`
- Submission package report: `output/verification/submission_package_check.md`
- Audit status counts: 35 pass, 2 warn, 0 fail

## Evidence Artifacts

- Manuscript source: `paper/magma_ieee.tex`
- Rendered-page contact sheet: `tmp/pdfs/magma_ieee_contact_sheet.png`
- G-code verification CSV: `output/verification/gcode_verification_summary.csv` (5 rows)
- Fill trial plan CSV: `paper/fill_trial_plan.csv` (10 planned rows)
- Fill trial plan summary: `output/verification/fill_trial_plan_summary.md`
- Standard mold manifest: `paper/molds/mold_manifest.md`
- Planned injection G-code summary: `output/trials/planned_injection_gcode_summary.md`
- Fill trial execution packet: `output/trials/fill_trial_packet.md`
- Trial execution readiness report: `output/verification/trial_execution_readiness.md`
- Evidence collection checklist: `output/trials/evidence_collection_checklist.md`
- Minimum submission-strength subset: `output/trials/minimum_submission_subset.md`
- Fill trial prefilled CSV skeleton: `output/trials/fill_trials_prefill.csv` (10 planned rows)
- Fill trial summary CSV: `output/verification/fill_trial_summary.csv` (0 measured rows)
- Fill trial asset report: `output/verification/fill_trial_assets.md`
- Fill trial LaTeX table: `output/verification/fill_trial_table.tex`
- Physical data readiness report: `output/verification/physical_data_readiness.md`
- Fill photo panel check: `output/verification/fill_photo_panel_check.md`
- Transcript-backed experiment log: `paper/experiment_log_2026-06-27.md`
- Transcript evidence index: `paper/transcript_evidence_index.md`
- Transcript evidence check: `output/verification/transcript_evidence_check.md`
- Claim-evidence map: `paper/claim_evidence_map.md`
- IEEE submission checklist: `paper/ieee_submission_checklist.md`
- PDF eXpress source archive: `output/submission/magma_ieee_pdf_express_source.zip`
- Local review bundle: `output/submission/magma_ieee_review_bundle.zip`
- Reviewer risk matrix: `paper/reviewer_risk_matrix.md`
- Native slicer source evidence snapshots:
  - `paper/source_evidence/LavaSlicer/src/libslic3r/GCode.cpp`
  - `paper/source_evidence/LavaSlicer/src/libslic3r/PrintObjectSlice.cpp`
  - `paper/source_evidence/PrusaSlicer/src/libslic3r/PrintConfig.hpp`
  - `paper/source_evidence/PrusaSlicer/src/libslic3r/GCode.cpp`

## Submission Caveat

The package currently verifies the manuscript, source-code evidence, and generated G-code artifacts. It does not yet contain measured fill-trial rows or publication-ready physical-result photos, which remain the acceptance-critical gap for a manufacturing-results submission.
