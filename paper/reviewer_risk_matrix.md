# Reviewer Risk Matrix

This note tracks likely IEEE reviewer objections and the concrete evidence needed to answer them.

| Risk | Current manuscript handling | Evidence needed before strong submission |
| --- | --- | --- |
| Novelty may look like ordinary printed-mold rapid tooling | Section II explicitly distinguishes transferred printed-mold inserts from keeping the mold on a tool-changing printer and making CAD roles, slicer state, tool changes, and bounded injection G-code first-class. | Keep reviewer framing centered on slicer/process semantics; do not present the work as another press-based printed-insert study. |
| Physical validation is too preliminary | Frames Magma as low-pressure molded deposition, not industrial injection molding; separates G-code success from fill success; includes a threats-to-validity section. | Measured fill rows with mass change, fill depth, failure labels, and photos. |
| Results are software-only | Includes source-backed native slicer hooks and regenerated G-code verification table. | One compact physical matrix on a standardized 10 mm cavity. |
| Process may be unsafe or collision-prone | Discusses tool-changing geometry, plunge depth, and port location as collision-checked motion. | Photo or video evidence of safe approach path plus documented port clearance. |
| No pressure or packing control | Explicitly lists lack of pressure sensing, clamp force, fill-front observation, and packing control. | Keep claim scoped; do not compare mechanical properties to molded parts until real tests exist. |
| Fill may only be surface deposition | Validation plan requires sectioned trials to distinguish surface fill from true bottom fill. | Sectioned-part figure or bottom-fill score for representative trials. |
| Reproducibility concerns | Build regenerates G-code summary, audit, PDF render, PDF production report, manifest, transcript-backed experiment log, fill-trial asset report, and future fill-trial table. | Archive exact G-code files, trial CSV, and photos with final submission package. |

Minimum evidence for a materially stronger submission:

1. Three to nine trials on one standardized 10 mm cavity.
2. At least one successful fill, one underfill/freeze case, and one failure-mode example.
3. Top-view photo for every measured row, plus at least one sectioned or removed-part image.
4. Completed `paper/fill_trials_template.csv` with commanded volume, delivered mass or density-derived delivered volume, fill depth, primary/secondary failure labels, executed G-code, and photo evidence.
