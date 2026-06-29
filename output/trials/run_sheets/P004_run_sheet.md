# Fill Trial Run Sheet: P004

## Planned Parameters

- Run order: 4
- Priority: core
- Geometry: 10 mm open cup
- Port diameter: 3 mm
- Schedule: top-pour
- Injection temperature: 240 C
- Flow rate: 20 mm3/s
- Commanded volume: 550 mm3
- Estimated E length for 1.75 mm filament: 228.663 mm
- Start/end Z: 12 / 12 mm
- Plunge: 2 mm
- Dwell: 1 s
- Primary metric: delivered mass
- Expected label: freezing
- Purpose: Low-temperature mid-flow trial separates flow-rate benefit from low thermal authority.

## Required Evidence Paths

- Planned injection block: `output/trials/planned/p004_240c_20mm3s_top_pour.gcode`
- Mold model: `paper/molds/P004_mold.stl`
- Executed G-code: `paper/gcode/P004_executed.gcode`
- Top photo: `paper/photos/P004_top.jpg`
- Side photo: `paper/photos/P004_side.jpg`

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
