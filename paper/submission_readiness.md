# Submission Readiness Notes

## Current Strengths

- IEEEtran manuscript compiles to a 5-page PDF.
- Local audit checks IEEE-facing front matter: conference template mode, title capitalization, one-paragraph 150-250 word abstract, and alphabetized keywords.
- PDF production audit checks letter page size, PDF version, encryption, JavaScript/forms, embedded/subset fonts, link/bookmark/package markers, and embedded-file absence.
- IEEE submission readiness audit checks template mode, page size, page count, embedded fonts, searchable PDF text, and required figure assets.
- Claim-scope audit requires the manuscript caveats that separate software verification from physical fill validation.
- Claim-evidence map separates backed claims, preliminary observations, and claims that are explicitly not made yet.
- Related work now cites rapid tooling, additive manufactured mold inserts, and deformation monitoring.
- Software contribution is concrete: post-processor path, native slicer hooks, role-based model semantics, and generated G-code verification.
- G-code verification table is reproducible from local artifacts using `tools/summarize_injection_gcode.py`.
- Native slicer implementation claims are checked against source evidence snapshots in `paper/source_evidence/LavaSlicer/src/libslic3r/` and `paper/source_evidence/PrusaSlicer/src/libslic3r/`.
- Fill-trial ingestion is ready through `tools/summarize_fill_trials.py`, including a generated LaTeX table, but it currently reports zero measured rows.
- Submission-strength physical data are checked through `tools/check_physical_data_readiness.py`, which requires publishable rows, process-window spread, success/failure contrast, and sectioned or removed-part evidence.
- A concrete planned trial matrix is checked through `tools/summarize_fill_trial_plan.py` and `paper/fill_trial_plan.csv`.
- Standard open-cup mold STLs are generated through `tools/generate_standard_molds.py` and tracked in `paper/molds/mold_manifest.md`.
- Planned injection-stage snippets are generated through `tools/generate_planned_injection_gcode.py` under `output/trials/planned/`, but they are setup artifacts only and do not replace executed G-code evidence.
- A generated physical trial packet is available through `tools/generate_fill_trial_packet.py`, with per-trial run sheets and a prefilled CSV skeleton under `output/trials/`.
- Preliminary observations are traced to `paper/experiment_log_2026-06-27.md` and `paper/transcript_evidence_index.md`, a narrowed technical index for the Jun 27 setup transcript.
- Claim boundaries are tracked in `paper/claim_evidence_map.md` and checked by `tools/check_claim_evidence_map.py`.
- PDF eXpress/source handoff is prepared through `paper/ieee_submission_checklist.md`, `tools/check_ieee_submission_readiness.py`, and `tools/build_submission_package.py`.
- A reviewer-facing manifest is generated at `output/verification/submission_manifest.md`.
- The paper avoids claiming industrial injection molding equivalence.

## Remaining Acceptance Risks

- Physical validation is still preliminary and mostly observational.
- No measured trial table currently reports commanded volume, delivered mass, fill depth, leakage, blockage, or mold softening.
- No measured trial table currently includes explicit primary/secondary failure labels.
- No publication-ready mold files, photos, or sectioned-part figures are included.
- Likely reviewer objections are tracked in `paper/reviewer_risk_matrix.md`; the largest unresolved items all require physical trial evidence.
- Rising-Z injection is verified as a software stress case, not as a safe physical process.

## Minimum Next Dataset

Run a compact matrix on one standardized 10 mm cavity:

- Nozzle temperature: 240, 255, 275 C.
- Flow rate: 10, 20, 30 mm3/s.
- Use `paper/fill_trial_plan.csv` for run order and photo/sectioning requirements.
- Use `output/trials/run_sheets/` during the run and copy completed rows from `output/trials/fill_trials_prefill.csv` only after the evidence files exist.
- Record: mold file, executed G-code, mold mass before, mold mass after, delivered mass, visible fill depth, leakage, blockage, softening, removal quality.
- Include: injected-filament density or a calibrated delivered-volume estimate.
- Photograph: top view, side view, removed/sectioned part when possible.

That dataset would let the paper replace the current validation-plan section with a real results section.
