# G-code Verification Summary

Generated from local representative G-code artifacts.

| artifact | implementation | injection_command | temperature_c | flow_mm3_s | segments | tool_path |
| --- | --- | --- | --- | --- | --- | --- |
| Tiny cube | Hand-authored Phase 0 block | 1000 mm3 | 240 | 15 | 10x41.575mm | same tool |
| Mold2 pocket | Phase 0 cavity estimate | 712 mm3 | 230 | 25.0 | 2x148.01mm | T0 -> T1 |
| Cube pocket | Phase 0 cavity estimate | 936 mm3 | 240 | 25.0 | 3x129.72mm | same tool |
| 10 mm part helper | Native LavaSlicer | 0.55 cm3 | 260/265 | 4.0 | 45 x 5 mm + 1.37 mm | T0 -> T1 |
| 30 mm port helper | Native LavaSlicer | 27.00 cm3 | 260/275 | 48.1 | 2244 x 5 mm + 4.82 mm | T0 -> T1 |
