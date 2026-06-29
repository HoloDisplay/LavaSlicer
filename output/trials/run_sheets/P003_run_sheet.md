# Fill Trial Run Sheet: P003

## Planned Parameters

- Run order: 3
- Priority: core
- Geometry: 10 mm open cup
- Port diameter: 3 mm
- Schedule: top-pour
- Injection temperature: 275 C
- Flow rate: 10 mm3/s
- Commanded volume: 550 mm3
- Estimated E length for 1.75 mm filament: 228.663 mm
- Start/end Z: 12 / 12 mm
- Plunge: 2 mm
- Dwell: 1 s
- Primary metric: mold softening
- Expected label: softening
- Purpose: High-temperature low-flow trial checks thermal margin and mold softening.

## Required Evidence Paths

- Planned injection block: `output/trials/planned/p003_275c_10mm3s_top_pour.gcode`
- Mold model: `paper/molds/P003_mold.stl`
- Executed G-code: `paper/gcode/P003_executed.gcode`
- Top photo: `paper/photos/P003_top.jpg`
- Side photo: `paper/photos/P003_side.jpg`

## Preflight

- Confirm mold is printed with an open, unobstructed port.
- Review the planned injection block, but do not treat it as executed evidence.
- Save the exact mold model to the path above before slicing or printing.
- Save the exact executed G-code to the path above before or immediately after the run.
- Confirm injection tool is heated to the planned temperature before approach.
- Confirm purge/wipe is complete and the nozzle can seat at the port.
- Collision-check the port approach and plunge before running unattended motion.

## Failure Label Vocabulary

Use observed labels only: `complete_fill`, `partial_fill`, `freezing`, `leakage`, `port_blockage`, `mold_softening`, `flow_limit`, `trapped_air`, `removal_damage`, `collision_risk`, or `other`.

## Record During Trial

- date: 
- operator: 
- printer: 
- mold_file: 
- bed_temp_c: 
- purge_cleaned: 
- mass_before_g: 
- mass_after_g: 
- visible_fill_depth_mm: 
- bottom_fill_score_0_3: 
- leakage_score_0_3: 
- blockage_score_0_3: 
- mold_softening_score_0_3: 
- removal_quality_0_3: 
- failure_label_primary: 
- failure_label_secondary: 
- notes: 
