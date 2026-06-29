# Experiment Log: Initial Magma Setup and Open-Cavity Trials

Source: `/Users/bmachado/.codex/attachments/207f5df1-709a-472b-9dac-609c0637ed53/pasted-text.txt`

The attachment identifies the meeting date as Jun 27. This log records it as 2026-06-27 because the repository work occurred on 2026-06-28.

## Purpose

The session explored whether a tool-changing desktop FFF printer could print a simple thermoplastic mold and then deliver molten filament into that mold through a second tool. The transcript supports using this session only as preliminary observational evidence, not as a controlled quantitative dataset. The narrow technical anchors used by the manuscript are indexed in `paper/transcript_evidence_index.md`; the raw transcript should not be used as a publication artifact.

## Setup Observations

- Geometry discussion converged from larger closed shapes toward a simpler first article: a cup, cube, cylinder, or similar open cavity near 10 mm scale.
- The team identified a circular top opening as the simplest first injection port.
- Larger nozzle options were discussed, including 0.8 mm and 0.6 mm nozzles, with Prusa/E3D-style hotend adapters.
- The tool-changing printer was used because it can print with one material/tool and then switch to another tool for injection.
- The intended material split was PETG for the printed mold and PLA for the injected material.
- Upload and execution work used Prusa Link / Prusa Connect style G-code transfer and a USB storage path during setup.

## Software and G-code Observations

- The first implementation direction was deliberately simple: modify or insert G-code around an ordinary sliced print rather than depend immediately on a full slicer rebuild.
- The transcript supports a role-based model: model both the mold and the injected part, mark the injected part as the process volume, and derive the target from the topmost face or port region.
- Manual jogging and manually edited G-code were used during early tests, which is why the paper should not present these observations as an automated validated process.
- One attempted injection path was described as too fast; the printer did not deliver the intended operation cleanly. This supports treating volumetric-flow limits as a first-class software constraint.

## Process Observations

- Molten material was visibly delivered during the session, but the transcript describes messy deposition and incomplete early behavior rather than a controlled packed mold fill.
- A 260 C injection-temperature target was discussed during one early run.
- A parked tool was observed around 180 C, supporting the need for explicit heat-wait commands before injection-tool use.
- The nozzle and port interface was recognized as important: cleaning, purging, sealing, and residue on the nozzle can affect whether the tool seats cleanly.
- The team identified the risk that simply squirting material into an open geometry could produce a spaghetti-like extrusion rather than reliable fill.

## Safety and Motion Constraints

- The Prusa XL-style tool-changing geometry was observed to constrain vertical injection approaches.
- The team noted that a downward injection path could collide with the toolhead envelope, dock area, printed mold walls, or nearby calibration structures.
- Manual intervention and emergency-stop/panic behavior were discussed, so the validation plan should require collision-checked approach paths before rising-Z or deep-plunge schedules.

## Manuscript Implications

- The manuscript can safely claim preliminary feasibility of material delivery into simple printed cavities.
- It should continue to state that the session does not prove complete cavity fill, packing, repeatability, or mechanical equivalence to industrial injection molding.
- The strongest paper framing remains software/process contribution plus a planned quantitative validation matrix.
- Before submission as an experimental manufacturing paper, the team still needs measured rows in `paper/fill_trials_template.csv`, executed G-code files in `paper/gcode/`, and photos in `paper/photos/`.
