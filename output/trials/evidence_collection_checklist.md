# Evidence Collection Checklist

This checklist is generated from `paper/fill_trial_plan.csv` and `output/trials/fill_trials_prefill.csv`. It is a physical-run handoff, not measured evidence.

## Stop Rules

- Do not copy a row into `paper/fill_trials_template.csv` until the exact executed G-code and required photos exist.
- Do not use `output/trials/planned/` snippets as executed evidence.
- Do not fill `failure_label_primary` before the trial; use the observed result only.
- Keep the rising-Z trial gated until collision clearance is verified.

## Per-Run Evidence Targets

| run | plan | temp C | flow mm3/s | schedule | executed G-code | top photo | section photo | run sheet |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | P001 | 240 | 10 | top-pour | `paper/gcode/P001_executed.gcode` | `paper/photos/P001_top.jpg` |  | `output/trials/run_sheets/P001_run_sheet.md` |
| 2 | P002 | 255 | 10 | top-pour | `paper/gcode/P002_executed.gcode` | `paper/photos/P002_top.jpg` |  | `output/trials/run_sheets/P002_run_sheet.md` |
| 3 | P003 | 275 | 10 | top-pour | `paper/gcode/P003_executed.gcode` | `paper/photos/P003_top.jpg` |  | `output/trials/run_sheets/P003_run_sheet.md` |
| 4 | P004 | 240 | 20 | top-pour | `paper/gcode/P004_executed.gcode` | `paper/photos/P004_top.jpg` |  | `output/trials/run_sheets/P004_run_sheet.md` |
| 5 | P005 | 255 | 20 | top-pour | `paper/gcode/P005_executed.gcode` | `paper/photos/P005_top.jpg` | `paper/photos/P005_section.jpg` | `output/trials/run_sheets/P005_run_sheet.md` |
| 6 | P006 | 275 | 20 | top-pour | `paper/gcode/P006_executed.gcode` | `paper/photos/P006_top.jpg` |  | `output/trials/run_sheets/P006_run_sheet.md` |
| 7 | P007 | 240 | 30 | top-pour | `paper/gcode/P007_executed.gcode` | `paper/photos/P007_top.jpg` |  | `output/trials/run_sheets/P007_run_sheet.md` |
| 8 | P008 | 255 | 30 | top-pour | `paper/gcode/P008_executed.gcode` | `paper/photos/P008_top.jpg` |  | `output/trials/run_sheets/P008_run_sheet.md` |
| 9 | P009 | 275 | 30 | top-pour | `paper/gcode/P009_executed.gcode` | `paper/photos/P009_top.jpg` | `paper/photos/P009_section.jpg` | `output/trials/run_sheets/P009_run_sheet.md` |
| 10 | P010 | 255 | 20 | rising-Z | `paper/gcode/P010_executed.gcode` | `paper/photos/P010_top.jpg` | `paper/photos/P010_section.jpg` | `output/trials/run_sheets/P010_run_sheet.md` |

## Minimum Submission-Strength Subset

- At least three publishable rows.
- At least two temperatures and two flow rates represented.
- At least one complete or candidate fill row.
- At least one labeled failure-mode row.
- At least one sectioned or removed-part photo.
