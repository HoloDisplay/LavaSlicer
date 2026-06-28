#!/bin/bash
# Headless slice of a mold STL with our OrcaSlicer build + Prusa XL PETG presets.
# Usage: ./slice_mold.sh mold.stl out.gcode
# Then run magma_inject.py on out.gcode to add the injection.
set -e
STL="$1"; OUT="${2:-mold.gcode}"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
APP="$REPO/build/arm64/OrcaSlicer/OrcaSlicer.app/Contents/MacOS/OrcaSlicer"
CFG="$HERE/cli_cfg"   # flattened machine.json/process.json/filament.json (inheritance resolved)

rm -rf "$HERE/cli_out"; mkdir -p "$HERE/cli_out" "$HERE/cli_datadir"
"$APP" --datadir "$HERE/cli_datadir" \
  --slice 0 --arrange 1 --orient 0 \
  --load-settings "$CFG/machine.json;$CFG/process.json" \
  --load-filaments "$CFG/filament.json" \
  --outputdir "$HERE/cli_out" \
  "$STL" > "$HERE/cli_slice.log" 2>&1
cp "$HERE/cli_out/plate_1.gcode" "$OUT"
echo "sliced -> $OUT"
