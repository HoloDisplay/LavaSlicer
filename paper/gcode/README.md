# Executed Fill Trial G-code

Place the exact G-code files executed during measured fill trials here and reference them from `paper/fill_trials_template.csv` with repository-relative paths.

Recommended name:

- `P001_executed.gcode`

Do not use this folder for planned targets only. A publishable measured row must point to the executed file that produced the recorded mass, fill-depth, and photo evidence. The build rejects G-code evidence that is outside `paper/gcode/` or still contains a planned-only marker such as `NOT EXECUTED EVIDENCE`.

The `representative/` subfolder is different: it contains small G-code artifacts used by the manuscript's software-verification table. Those files support command-generation checks only and are not physical fill-trial evidence.
