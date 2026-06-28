# LavaSlicer Injection Mode

LavaSlicer extends OrcaSlicer with an **injection molding mode** that allows you to 3D print a mold and then inject filament into it using a second toolhead. Designed for use with multi-toolhead printers like the Prusa XL.

## How It Works

1. Design a model with two bodies: the **mold** (outer shell) and the **injection body** (the cavity to be filled)
2. Import the model into LavaSlicer
3. Configure injection settings — the injection body is excluded from printing and converted to a support blocker
4. Slice and print — the mold prints normally, then the slicer appends GCode to switch toolheads and inject filament into the cavity

## Quick Start

1. Import your 3MF file containing the mold + injection body
2. Go to **Print Settings > Others > Injection**
3. Check **Enable injection mode**
4. Enter the exact volume name of the injection body in **Injection body name** (must match the name shown in the object list sidebar)
5. Configure temperature, tool, fill ratio, and plunge depth
6. Slice — the injection body will be excluded from the mold print, and injection GCode will be appended after the print completes

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Enable injection mode | off | Master toggle for injection mode |
| Injection body name | (empty) | Name of the volume to use as the injection body. Must match exactly. |
| Injection temperature | 240 C | Nozzle temperature for the injection toolhead |
| Injection bed temperature | 0 C | Bed temperature override during injection. 0 = keep current temp. |
| Injection tool | 1 (T1) | Tool index for injection (0=T0, 1=T1, etc). If different from the mold tool, a Prusa XL tool change sequence is emitted. |
| Injection fill ratio | 100% | Fraction of the injection body volume to fill. >100% for overpacking. |
| Injection plunge depth | 2.0 mm | How far below the cavity rim the nozzle plunges during injection |

## Injection Point Detection

The injection point (where the nozzle is positioned) is determined automatically:

- The injection body's mesh vertices are transformed to bed coordinates
- The vertices at the **highest Z** of the injection body are collected (within 0.1mm tolerance)
- These vertices form the circular injection port at the top of the mold
- Their **XY centroid** is used as the injection point
- The **Z coordinate** is the mold's highest printed layer (`max_layer_z`)

## What Happens During Slicing

When injection mode is enabled and an injection body name is set:

1. **Volume exclusion**: The named volume is filtered out of the slicing pipeline — it produces no perimeters, infill, or any printed geometry. The mold remains hollow where the injection body was.

2. **Support blocking**: The injection body volume is temporarily converted to a `SUPPORT_BLOCKER` during slicing, ensuring no support material is generated inside the injection cavity even if supports are enabled.

3. **GCode generation**: After the mold finishes printing, the following GCode sequence is appended:
   - Bed temperature change (if overridden)
   - Tool change from mold tool to injection tool (with Prusa XL park/heat/pick sequence if tools differ)
   - Travel to injection point XY
   - Descend to cavity rim Z
   - Plunge into cavity
   - Extrude calculated filament volume in segments
   - Retract and lift

## Injection Volume Calculation

The injection volume is calculated from the mesh:

```
volume_to_inject = mesh_volume * (inject_fill_ratio / 100)
e_total = volume_to_inject / filament_cross_section_area
```

The extrusion is split into segments of max 180mm each to avoid firmware issues with very long extrusion moves. Feed rate is calculated from `filament_max_volumetric_speed`.

## Design Guidelines

- The injection body should have a **circular cross-section at its highest Z point** — this is the injection port where the nozzle enters
- The mold should fully enclose the injection body except at the top (injection port)
- Use 100% infill or solid walls for the mold to prevent leakage
- Set injection temperature higher than the mold printing temperature for better flow (e.g., 240C for PLA injection into a PLA mold)
- The injection body name must match the volume name in the object list **exactly** (case-sensitive)

## Architecture

Based on [Clayton Haight's `magma_inject.py`](../magma_test/) post-processor, integrated natively into the OrcaSlicer slicing pipeline.

### Key source files

| File | Purpose |
|------|---------|
| `src/libslic3r/PrintConfig.hpp` | Injection setting declarations |
| `src/libslic3r/PrintConfig.cpp` | Injection setting registration |
| `src/libslic3r/Preset.cpp` | Settings added to print preset options list |
| `src/slic3r/GUI/Tab.cpp` | Injection section on Others tab |
| `src/slic3r/GUI/GUI_Factories.cpp` | Per-object injection category |
| `src/libslic3r/PrintObjectSlice.cpp` | Volume filtering during slicing |
| `src/libslic3r/Model.hpp` / `Model.cpp` | `inject_skip_volume_name` for mesh filtering |
| `src/libslic3r/Print.cpp` | Volume type change to SUPPORT_BLOCKER, skip name setup |
| `src/libslic3r/PrintObject.cpp` | Region config volume filtering |
| `src/libslic3r/GCode.cpp` | Injection GCode generation |

---

# Building on Apple Silicon Mac

## Prerequisites

- **Xcode Command Line Tools**: `xcode-select --install`
- **Homebrew texinfo** (for makeinfo): `brew install texinfo`
- Add to PATH: `export PATH="/opt/homebrew/opt/texinfo/bin:$PATH"`

## Build Steps

### 1. Build Dependencies (first time only)

```bash
SDKROOT=$(xcrun --show-sdk-path) ./build_release_macos.sh -d
```

**Important**: The `SDKROOT` env var is required to ensure the build uses the correct SDK. Without it, GMP and other dependencies may fail to find the system linker libraries.

### 2. Build the Slicer

```bash
# Using Ninja (faster):
SDKROOT=$(xcrun --show-sdk-path) ./build_release_macos.sh -s -x

# Using Xcode generator (default):
SDKROOT=$(xcrun --show-sdk-path) ./build_release_macos.sh -s
```

The built app will be at: `build/arm64/src/Release/OrcaSlicer.app`

### 3. Incremental Rebuild (after code changes)

For fast incremental builds after modifying source files:

```bash
SDKROOT=$(xcrun --show-sdk-path) cmake --build build/arm64 --config Release --target OrcaSlicer
```

This only recompiles changed files and is much faster than a full build. Note: changes to header files (especially `PrintConfig.hpp`, `Model.hpp`) trigger wide recompilation since they're included in precompiled headers.

### 4. Launch

```bash
open build/arm64/src/Release/OrcaSlicer.app
```

## Known Build Issues

### MacPorts Conflict

If you have MacPorts installed (`/opt/local`), its libpng headers may conflict with OrcaSlicer's patched libpng (which uses a `prusaslicer_` symbol prefix). Symptoms: linker error `_prusaslicer_png_create_write_struct not found`.

**Fix**: After building deps, check if the PNG library has prefixed symbols:
```bash
nm -g deps/build/arm64/OrcaSlicer_dep/usr/local/lib/libpng16.a | grep prusaslicer_png_create_write
```

If no output, the PNG dep used MacPorts' zlib headers. Fix by editing the PNG cmake cache:
```bash
SDKROOT=$(xcrun --show-sdk-path)
CACHE=deps/build/arm64/dep_PNG-prefix/src/dep_PNG-build/CMakeCache.txt
sed -i '' "s|ZLIB_INCLUDE_DIR:PATH=/opt/local/include|ZLIB_INCLUDE_DIR:PATH=$SDKROOT/usr/include|g" "$CACHE"
sed -i '' "s|/opt/local/lib/libz.dylib|$SDKROOT/usr/lib/libz.tbd|g" "$CACHE"
cd deps/build/arm64/dep_PNG-prefix/src/dep_PNG-build
cmake . && cmake --build . --clean-first && make install
```

Then rebuild the slicer.

### GMP Compiler Error

If GMP fails with "could not find a working compiler", ensure `SDKROOT` is set:
```bash
SDKROOT=$(xcrun --show-sdk-path) ./build_release_macos.sh -d
```
