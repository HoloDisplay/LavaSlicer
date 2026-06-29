# Magma Fill Trial Packet

This generated packet turns `paper/fill_trial_plan.csv` into a run-ready data collection package. It does not contain measured results.

## Outputs

- Prefilled CSV skeleton: `output/trials/fill_trials_prefill.csv`
- Per-trial run sheets: `output/trials/run_sheets/`

## Use

1. Run each sheet in `run_order`.
2. Save the exact mold model, executed G-code, and required photos to the listed paths.
3. Copy completed rows from `output/trials/fill_trials_prefill.csv` into `paper/fill_trials_template.csv` only after the masses, scores, and evidence files exist.
4. Run `make all` and confirm the physical-data warning is replaced by publishable measured rows.

## Planned Trials

| run | plan_id | schedule | temp C | flow mm3/s | section? | run sheet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | P001 | top-pour | 240 | 10 | no | `output/trials/run_sheets/P001_run_sheet.md` |
| 2 | P002 | top-pour | 255 | 10 | no | `output/trials/run_sheets/P002_run_sheet.md` |
| 3 | P003 | top-pour | 275 | 10 | no | `output/trials/run_sheets/P003_run_sheet.md` |
| 4 | P004 | top-pour | 240 | 20 | no | `output/trials/run_sheets/P004_run_sheet.md` |
| 5 | P005 | top-pour | 255 | 20 | yes | `output/trials/run_sheets/P005_run_sheet.md` |
| 6 | P006 | top-pour | 275 | 20 | no | `output/trials/run_sheets/P006_run_sheet.md` |
| 7 | P007 | top-pour | 240 | 30 | no | `output/trials/run_sheets/P007_run_sheet.md` |
| 8 | P008 | top-pour | 255 | 30 | no | `output/trials/run_sheets/P008_run_sheet.md` |
| 9 | P009 | top-pour | 275 | 30 | yes | `output/trials/run_sheets/P009_run_sheet.md` |
| 10 | P010 | rising-Z | 255 | 20 | yes | `output/trials/run_sheets/P010_run_sheet.md` |
