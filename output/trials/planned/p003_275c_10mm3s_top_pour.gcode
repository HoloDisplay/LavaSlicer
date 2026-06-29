; MAGMA PLANNED INJECTION BLOCK - NOT EXECUTED EVIDENCE
; plan_id: P003
; schedule: top-pour
; geometry: 10 mm open cup
; port_diameter_mm: 3
; injection_temp_c: 275
; flow_mm3_s: 10
; commanded_volume_mm3: 550
; commanded_e_mm: 228.663
; feed_mm_min: 249.5
; start_z_mm: 12
; end_z_mm: 12
; This is an injection-stage snippet, not a complete printable job.
; Before use, verify mold print G-code, port XY, tool selection, purge, and collision clearance.
; Save the exact executed job as paper/gcode/P003_executed.gcode after running.
M83 ; relative extrusion
T1 ; select injection tool
M109 S275 T1 ; wait for injection tool temperature
; PRECONDITION: machine is already at the verified port XY before the plunge.
G1 Z12.000 F600 ; planned port/plunge Z
G1 E5.000 F249.5 ; planned injection segment 1/46
G1 E5.000 F249.5 ; planned injection segment 2/46
G1 E5.000 F249.5 ; planned injection segment 3/46
G1 E5.000 F249.5 ; planned injection segment 4/46
G1 E5.000 F249.5 ; planned injection segment 5/46
G1 E5.000 F249.5 ; planned injection segment 6/46
G1 E5.000 F249.5 ; planned injection segment 7/46
G1 E5.000 F249.5 ; planned injection segment 8/46
G1 E5.000 F249.5 ; planned injection segment 9/46
G1 E5.000 F249.5 ; planned injection segment 10/46
G1 E5.000 F249.5 ; planned injection segment 11/46
G1 E5.000 F249.5 ; planned injection segment 12/46
G1 E5.000 F249.5 ; planned injection segment 13/46
G1 E5.000 F249.5 ; planned injection segment 14/46
G1 E5.000 F249.5 ; planned injection segment 15/46
G1 E5.000 F249.5 ; planned injection segment 16/46
G1 E5.000 F249.5 ; planned injection segment 17/46
G1 E5.000 F249.5 ; planned injection segment 18/46
G1 E5.000 F249.5 ; planned injection segment 19/46
G1 E5.000 F249.5 ; planned injection segment 20/46
G1 E5.000 F249.5 ; planned injection segment 21/46
G1 E5.000 F249.5 ; planned injection segment 22/46
G1 E5.000 F249.5 ; planned injection segment 23/46
G1 E5.000 F249.5 ; planned injection segment 24/46
G1 E5.000 F249.5 ; planned injection segment 25/46
G1 E5.000 F249.5 ; planned injection segment 26/46
G1 E5.000 F249.5 ; planned injection segment 27/46
G1 E5.000 F249.5 ; planned injection segment 28/46
G1 E5.000 F249.5 ; planned injection segment 29/46
G1 E5.000 F249.5 ; planned injection segment 30/46
G1 E5.000 F249.5 ; planned injection segment 31/46
G1 E5.000 F249.5 ; planned injection segment 32/46
G1 E5.000 F249.5 ; planned injection segment 33/46
G1 E5.000 F249.5 ; planned injection segment 34/46
G1 E5.000 F249.5 ; planned injection segment 35/46
G1 E5.000 F249.5 ; planned injection segment 36/46
G1 E5.000 F249.5 ; planned injection segment 37/46
G1 E5.000 F249.5 ; planned injection segment 38/46
G1 E5.000 F249.5 ; planned injection segment 39/46
G1 E5.000 F249.5 ; planned injection segment 40/46
G1 E5.000 F249.5 ; planned injection segment 41/46
G1 E5.000 F249.5 ; planned injection segment 42/46
G1 E5.000 F249.5 ; planned injection segment 43/46
G1 E5.000 F249.5 ; planned injection segment 44/46
G1 E5.000 F249.5 ; planned injection segment 45/46
G1 E3.663 F249.5 ; planned injection segment 46/46
G4 S1 ; dwell after injection
G1 E-2.000 F1800 ; retract after injection
G1 Z14.000 F600 ; lift clear
; END MAGMA PLANNED INJECTION BLOCK
