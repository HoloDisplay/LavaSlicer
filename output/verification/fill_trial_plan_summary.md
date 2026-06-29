# Fill Trial Plan Summary

Schema status: expected columns present.

Planned trials: 10

Core matrix coverage: pass (core_rows=9, temps=['240', '255', '275'], flows=['10', '20', '30'], missing_combos=[])

| plan_id | priority | run_order | schedule | temp C | flow mm3/s | metric | expected label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P001 | core | 1 | top-pour | 240 | 10 | bottom fill depth | freezing |
| P002 | core | 2 | top-pour | 255 | 10 | bottom fill depth | freezing |
| P003 | core | 3 | top-pour | 275 | 10 | mold softening | softening |
| P004 | core | 4 | top-pour | 240 | 20 | delivered mass | freezing |
| P005 | core | 5 | top-pour | 255 | 20 | visible fill depth | candidate window |
| P006 | core | 6 | top-pour | 275 | 20 | leakage score | leakage or softening |
| P007 | core | 7 | top-pour | 240 | 30 | flow limit | flow limit |
| P008 | core | 8 | top-pour | 255 | 30 | delivered mass | flow limit |
| P009 | core | 9 | top-pour | 275 | 30 | leakage score | leakage or softening |
| P010 | followup | 10 | rising-Z | 255 | 20 | void fraction | trapped air |
