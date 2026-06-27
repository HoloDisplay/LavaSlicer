# Magma injection — Phase 0 post-processor

`magma_inject.py` takes a mold **STL** + its sliced **G-code** and splices an
injection sequence in before the end G-code. This is the fast "learn the flow"
path while the native Orca/Magma implementation is built.

## Usage

```bash
python3 magma_inject.py --stl mold.stl --gcode mold.gcode --out out.gcode \
    [--temp 240] [--inject-tool 0] [--fill 1.0] [--plunge 2.0] \
    [--flow 0] [--volume-mm3 N]
```

- `--temp`         injection nozzle temp (default 240 = hot end of PLA range)
- `--inject-tool`  tool to inject with. If it differs from the detected mold
                   tool, a real Prusa XL tool change is emitted (separate
                   nozzles → separable materials).
- `--fill`         fraction of detected cavity volume (1.0 = full)
- `--flow`         mm³/s; `0` = use `filament_max_volumetric_speed` (full flow)
- `--plunge`       mm the nozzle dips below the cavity rim
- `--volume-mm3`   hard override of injected volume

## How injection-spot detection works (shape-agnostic)

The cavity is found geometrically, with **no shape assumption** — so it already
handles **circular** holes as well as square ones:

1. Collect up-facing horizontal facets (normal z ≈ +1), grouped by Z level.
2. The highest level is the top rim; the largest interior level below it is the
   **pocket floor**.
3. Floor centroid → injection XY. Floor area × (top − floor) → cavity volume.

Model-space XY is mapped to bed coordinates using the `objects_info` part
footprint in the G-code.

### Current assumptions / future work
- Blind pocket (closed-bottom cavity with a floor). A through-hole can't hold
  melt, so that's the right model for a mold.
- Object placed without rotation/scale by the slicer (axis-aligned mapping).
- Single cavity (takes the largest if several). Multi-injection is what the
  native Magma solver handles — a later step.
- **Mold should be 100% one material**; only the injection is the other tool.
  Slice the whole object on the mold tool (no top-layer color/tool split).
