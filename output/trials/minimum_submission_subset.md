# Minimum Submission-Strength Fill Dataset

Run the full 3 x 3 matrix when possible. If time is limited, this is the smallest first-pass subset that can plausibly clear the physical-data readiness gate without pretending planned artifacts are measured results.

## Recommended First Runs

| plan | reason | temp C | flow mm3/s | expected contrast | required evidence |
| --- | --- | --- | --- | --- | --- |
| P001 | Low-temperature/low-flow lower-bound case. | 240 | 10 | freezing | `paper/gcode/P001_executed.gcode`, `paper/photos/P001_top.jpg` |
| P005 | Center-point candidate fill; section if it fills. | 255 | 20 | candidate window | `paper/gcode/P005_executed.gcode`, `paper/photos/P005_top.jpg`, `paper/photos/P005_section.jpg` |
| P009 | High-temperature/high-flow upper-bound case; section if retained. | 275 | 30 | leakage or softening | `paper/gcode/P009_executed.gcode`, `paper/photos/P009_top.jpg`, `paper/photos/P009_section.jpg` |

## Why This Subset

- Three rows can satisfy the minimum publishable-row count.
- The selected rows span three temperatures and three flow rates.
- P005 is the planned candidate success case; P001 and P009 are boundary cases likely to provide failure-mode contrast.
- P005 and P009 include section-photo targets, so one sectioned or removed-part image can satisfy the section-evidence gate.

## Fallback Rules

- If P005 is not a candidate fill, run P006 or P008 next before drawing conclusions.
- If P001 and P009 do not produce a clear failure label, run P003 or P007 to force thermal or flow-limit contrast.
- If any selected row lacks exact executed G-code, a top photo, or measured mass fields, do not copy it into `paper/fill_trials_template.csv`.
- After the subset is complete, rerun `make all`; the readiness gate still decides whether the data are publication-strength.
