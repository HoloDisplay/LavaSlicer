# Trial Execution Readiness

Physical-run packet status: READY

Evidence checklist: `output/trials/evidence_collection_checklist.md`

Minimum subset: `output/trials/minimum_submission_subset.md`

| status | check | detail |
| --- | --- | --- |
| PASS | trial id alignment | 10 planned trials aligned across plan, prefill, and planned G-code summary. |
| PASS | run order | Run order is contiguous from 1 through 10. |
| PASS | prefill measured fields | Measured-result fields are blank before physical trials. |
| PASS | executed G-code placeholders | Prefill rows point at `paper/gcode/*_executed.gcode`, not planned snippets. |
| PASS | photo path convention | Top, side, and required section photo paths match the run plan. |
| PASS | standard mold files | All prefilled mold_file paths exist. |
| PASS | planned setup snippets | All planned injection-stage snippets exist as setup aids. |
| PASS | run sheets | 10 run sheets exist and preserve the planned-vs-executed evidence warning. |
| PASS | evidence directories | `paper/molds`, `paper/gcode`, and `paper/photos` are present with README guidance. |
| PASS | evidence checklist | output/trials/evidence_collection_checklist.md |
| PASS | minimum submission subset | output/trials/minimum_submission_subset.md covers temps=['240', '255', '275'], flows=['10', '20', '30']. |
