# Magma Fill Trial Protocol

This is the minimum dataset needed to turn the current IEEE draft from a software/process paper into a stronger experimental submission.

## Fixed Test Article

- Geometry: one 10 mm-scale open cup or block cavity with a circular top port.
- Mold: PETG, T0, 0.4 mm nozzle, solid walls.
- Injection: PLA, T1, 0.8 mm nozzle when available.
- Density: record measured injected-filament density, or use a calibrated value and mark it in the notes.
- Starting process window: 240, 255, and 275 C; 10, 20, and 30 mm3/s.
- Compare top-pour and rising-Z schedules only after the tool approach is collision-checked.

## Planned Matrix

The executable trial plan is tracked in `paper/fill_trial_plan.csv` and summarized by `make fill-plan`.

- Core matrix: nine top-pour trials spanning 240, 255, and 275 C crossed with 10, 20, and 30 mm3/s.
- Follow-up: one rising-Z center-point trial after collision clearance is verified.
- Sectioning priority: section at least the center-point candidate fill and one high-temperature/high-flow boundary case.

## Per-Trial Procedure

1. Slice with the injected body suppressed and the port open.
2. Export G-code and record the generated injection block parameters.
3. Weigh the mold before injection.
4. Run the print and injection sequence.
5. Weigh the mold plus injected material after cooling.
6. Photograph the part from top, side, and removed/sectioned views if possible.
7. Record visible fill depth, leakage, blockage, softening, tool collision risk, removal quality, and primary/secondary failure labels.
8. Rerun `make fill-summary` to regenerate `output/verification/fill_trial_summary.md` and `output/verification/fill_trial_table.tex`.

## Evidence File Convention

Use repository-relative paths in `paper/fill_trials_template.csv` so the audit can verify that evidence files exist.

- Executed G-code: `paper/gcode/P001_executed.gcode`
- Mold file: `paper/molds/P001_mold.stl`
- Top-view photo: `paper/photos/P001_top.jpg`
- Side-view photo: `paper/photos/P001_side.jpg`
- Removed or sectioned photo: `paper/photos/P001_section.jpg`

The mold path should point to the exact model used to generate the mold print. The G-code path should point to the exact file executed on the printer, not only a planned target from `paper/fill_trial_plan.csv`. For a publishable row, the executed G-code must live under `paper/gcode/`; files marked `NOT EXECUTED EVIDENCE` or generated under `output/trials/planned/` are rejected by the readiness checks. Mold file, top-view photo, and executed G-code are required before a measured row is counted as publishable. Side and section photos are optional per row, but any path entered in the CSV must resolve to a real file.

Planned injection-stage snippets generated under `output/trials/planned/` are setup aids only. They must be replaced by the exact executed printer job path in `paper/fill_trials_template.csv`.

## Publishable Metrics

- Commanded injected volume versus delivered mass-derived volume.
- Bottom fill depth or sectioned fill fraction.
- Failure labels: use `failure_label_primary` and, when useful, `failure_label_secondary`. Allowed labels are `complete_fill`, `partial_fill`, `freezing`, `leakage`, `port_blockage`, `mold_softening`, `flow_limit`, `trapped_air`, `removal_damage`, `collision_risk`, and `other`.
- Representative photos for best fill, underfill, leak, and blocked-port cases.
- A publishable row should include the executed G-code file, commanded volume, temperature, flow, delivered mass or density-derived delivered volume, visible fill depth, failure scores, failure label, and an existing top-view photo.
