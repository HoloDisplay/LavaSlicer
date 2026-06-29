# Fill Trial Mold Files

Place the exact mold model files used for measured fill trials here and reference them from `paper/fill_trials_template.csv` with repository-relative paths.

Recommended name:

- `P001_mold.stl`

`make fill-molds` generates standardized open-cup mold STLs from `paper/fill_trial_plan.csv`, plus `mold_manifest.md`. A publishable measured row must point to the mold model used to generate the executed G-code. If a trial uses a revised mold, replace the generated STL with the actual printed mold model before copying the row into `paper/fill_trials_template.csv`. Do not use this folder for unrelated reference geometry.
