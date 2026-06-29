# Transcript Evidence Index: Jun 27 Setup Session

Source: `/Users/bmachado/.codex/attachments/207f5df1-709a-472b-9dac-609c0637ed53/pasted-text.txt`

This index narrows the Jun 27 transcript to technical anchors that support the manuscript's preliminary-observation language. It is not a controlled quantitative dataset, and it does not establish complete fill, packing, repeatability, or mechanical equivalence. Do not upload the raw transcript to a conference system; it contains unrelated meeting content and is not a publication artifact.

| id | Manuscript use | Transcript anchor | Boundary |
| --- | --- | --- | --- |
| E1 | First article should be simple and open. | "make a cup, basically"; "fill the cup"; "10 millimeters or less" | Supports using a 10 mm-scale open cavity, not a complex closed mold. |
| E2 | Larger injection nozzle and tool-changing printer are relevant. | "0.8"; "0.6"; "multi nozzle printer" | Supports setup description only; exact nozzle installed still needs run-sheet evidence. |
| E3 | Fastest first implementation is G-code insertion. | "take the g-code and just modify the g code"; "insert a g-code thing halfway" | Supports the Phase 0 post-processor path. |
| E4 | Injected-part role model is a real design intent. | "model also the injected molded part"; "select that as the injection part"; "topmost face" | Supports slicer-semantics claim, not physical fill quality. |
| E5 | PETG mold and PLA injected material were the intended split. | "Print with ptg and then inject into it with PLA" | Transcript spelling is noisy; the run sheet must record the actual materials used. |
| E6 | Volumetric flow can exceed what the printer will accept. | "tried to inject it too fast"; "the printer just said, no" | Supports flow limiting as a planning constraint. |
| E7 | Early physical result was messy and preliminary. | "goes spaghetti"; "cool. At the bottom" | Supports failure taxonomy only, not a publishable success result. |
| E8 | Parked-tool temperature requires explicit heat waits. | "temperature is gonna be 180"; "because it's parked" | Supports explicit injection-tool heat-wait commands. |
| E9 | Nozzle cleaning and purge matter. | "junk on the nozzle"; "no way to clean it"; "no way to purge" | Supports process-risk discussion and preflight requirements. |
| E10 | Downward approach and collision constraints are real. | "can't inject downwards"; "it's gonna hit everything"; "be very careful" | Supports collision-check language before deep plunges or rising-Z motion. |
| E11 | Manual intervention was part of early tests. | "manually jogging this"; "manual injection"; "manually edited the g codes" | Supports the boundary that early observations are not a fully automated validated process. |

The manuscript may use these observations only as preliminary process context. Publishable physical validation still requires measured rows in `paper/fill_trials_template.csv`, executed G-code under `paper/gcode/`, and photo evidence under `paper/photos/`.
