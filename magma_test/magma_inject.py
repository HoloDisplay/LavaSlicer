#!/usr/bin/env python3
"""
magma_inject.py — operationalized Magma injection post-processor.

Takes a sliced mold G-code (and optionally its STL), auto-detects the
injection cavity (open pocket at the top), computes the fill volume, and
splices an injection block into the G-code before the end sequence.

Cavity detection (shape-agnostic — square OR circular holes):
  * default: from the G-CODE itself. Each layer's extrusion is rasterized,
    flood-filled from outside; the enclosed empty region is the cavity.
    Nozzle-aware (line width read from the G-code) so walls close correctly.
    XY comes out directly in bed coordinates — no model->bed mapping.
  * --stl mold.stl: use the mesh instead (highest interior up-facing floor
    facet group below the top rim). Mapped to bed via objects_info.

Tooling: detects the active ("mold") tool at the end of the print. If the
requested --inject-tool differs, a real Prusa XL tool change is emitted
(park mold tool, heat+pick inject tool) so mold and fill are different
materials and can be separated.

Usage:
  python3 magma_inject.py --gcode mold.gcode --out out.gcode \
      [--stl mold.stl] [--temp 240] [--inject-tool 0] [--fill 1.0] \
      [--plunge 2.0] [--flow 0] [--volume-mm3 N] [--no-strip-color-change]

  --flow 0    use filament_max_volumetric_speed from the G-code (full flow)
  --fill      fraction of detected cavity volume to inject (1.0 = full)
"""
import argparse, math, re, struct
from collections import deque

NUM = r'(-?\d*\.?\d+)'          # matches ".5", "127", "-.15", "127.5"

def cfg(text, key, default=None):
    m = re.search(rf"^; {re.escape(key)} = (.*)$", text, re.M)
    return m.group(1).strip() if m else default

def first_float(s, default):
    if s is None: return default
    m = re.search(r"-?\d*\.?\d+", s.split(",")[0])
    return float(m.group()) if m else default

# ---------- cavity detection from G-CODE (rasterize + flood fill) ----------

def detect_cavity_gcode(text, nozzle, cell=0.2):
    cur = dict(x=0.0, y=0.0, h=0.2)
    layers = []; L = None
    for ln in text.split("\n"):
        s = ln.strip()
        if s.startswith(";Z:"):
            try: z = float(s[3:].split()[0])
            except: z = 0.0
            L = dict(z=z, h=cur["h"], segs=[]); layers.append(L)
        elif s.startswith(";HEIGHT:"):
            try:
                cur["h"] = float(s[8:].split()[0])
                if L: L["h"] = cur["h"]
            except: pass
        elif s.startswith(("G1", "G0")):
            m = {}
            for ax in "XYE":
                r = re.search(rf'{ax}{NUM}', s)
                if r: m[ax] = float(r.group(1))
            nx, ny = m.get("X", cur["x"]), m.get("Y", cur["y"])
            if m.get("E", 0.0) > 0 and ("X" in m or "Y" in m) and L is not None:
                L["segs"].append((cur["x"], cur["y"], nx, ny))
            cur["x"], cur["y"] = nx, ny

    pts = [(x, y) for La in layers for (x0, y0, x1, y1) in La["segs"]
           for (x, y) in ((x0, y0), (x1, y1))]
    if not pts:
        raise SystemExit("No extrusion found in G-code.")
    minx = min(p[0] for p in pts); maxx = max(p[0] for p in pts)
    miny = min(p[1] for p in pts); maxy = max(p[1] for p in pts)
    W = int((maxx - minx) / cell) + 4; H = int((maxy - miny) / cell) + 4
    gx = lambda x: int((x - minx) / cell) + 2
    gy = lambda y: int((y - miny) / cell) + 2
    # stamp radius = half the extrusion width (~1.125*nozzle) -> closes walls
    rad = max(1, round((nozzle * 1.125 / 2) / cell))

    def stamp(grid, x0, y0, x1, y1):
        n = max(1, int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 / (cell * 0.5)))
        for i in range(n + 1):
            t = i / n
            cx, cy = gx(x0 + (x1 - x0) * t), gy(y0 + (y1 - y0) * t)
            for dx in range(-rad, rad + 1):
                for dy in range(-rad, rad + 1):
                    px, py = cx + dx, cy + dy
                    if 0 <= px < W and 0 <= py < H: grid[py * W + px] = 1

    total = 0.0; cav_layers = []
    sumx = sumy = 0.0; ncells = 0
    for La in layers:
        if not La["segs"]: continue
        grid = bytearray(W * H)
        for seg in La["segs"]: stamp(grid, *seg)
        outside = bytearray(W * H); dq = deque()
        for x in range(W):
            for y in (0, H - 1):
                i = y * W + x
                if not grid[i] and not outside[i]: outside[i] = 1; dq.append((x, y))
        for y in range(H):
            for x in (0, W - 1):
                i = y * W + x
                if not grid[i] and not outside[i]: outside[i] = 1; dq.append((x, y))
        while dq:
            x, y = dq.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy; j = ny * W + nx
                if 0 <= nx < W and 0 <= ny < H and not grid[j] and not outside[j]:
                    outside[j] = 1; dq.append((nx, ny))
        # largest enclosed-empty component = the cavity (ignores infill gaps)
        seen = bytearray(W * H); best = 0; best_cells = None
        for sy in range(H):
            for sx in range(W):
                i0 = sy * W + sx
                if grid[i0] or outside[i0] or seen[i0]: continue
                cells = []; dq = deque([(sx, sy)]); seen[i0] = 1
                while dq:
                    x, y = dq.popleft(); cells.append((x, y))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy; j = ny * W + nx
                        if 0 <= nx < W and 0 <= ny < H and not grid[j] and not outside[j] and not seen[j]:
                            seen[j] = 1; dq.append((nx, ny))
                if len(cells) > best: best = len(cells); best_cells = cells
        area = best * cell * cell
        if area > 1.0:
            total += area * La["h"]; cav_layers.append((La["z"], area))
            for (x, y) in best_cells:
                sumx += minx + (x - 2) * cell; sumy += miny + (y - 2) * cell
            ncells += len(best_cells)

    if not cav_layers:
        raise SystemExit("No enclosed cavity detected in G-code.")
    top_z = max(z for z, a in cav_layers)
    floor_z = min(z for z, a in cav_layers)
    return {
        "volume": total, "hole_x": sumx / ncells, "hole_y": sumy / ncells,
        "top_z": top_z, "floor_z": floor_z, "depth": top_z - floor_z,
        "area": max(a for z, a in cav_layers), "bed_coords": True,
        "n_layers": len(cav_layers), "stamp_radius_cells": rad,
    }

# ---------- cavity detection from STL (mesh) ----------

def load_stl(path):
    data = open(path, "rb").read(); tris = []
    if data[:5] == b"solid" and b"facet" in data[:2048]:
        nx = ny = nz = None; verts = []
        for line in data.decode("utf-8", "replace").splitlines():
            t = line.split()
            if not t: continue
            if t[0] == "facet" and t[1] == "normal":
                nx, ny, nz = map(float, t[2:5])
            elif t[0] == "vertex":
                verts.append(tuple(map(float, t[1:4])))
                if len(verts) == 3: tris.append(((nx, ny, nz), verts)); verts = []
    else:
        n = struct.unpack_from("<I", data, 80)[0]; off = 84
        for _ in range(n):
            nx, ny, nz = struct.unpack_from("<3f", data, off); off += 12
            v = [struct.unpack_from("<3f", data, off + 12 * k) for k in range(3)]
            off += 36 + 2; tris.append(((nx, ny, nz), v))
    return tris

def tri_area_xy(v):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = v
    return abs((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)) / 2.0

def detect_cavity_stl(tris):
    xs = [p[0] for _, v in tris for p in v]; ys = [p[1] for _, v in tris for p in v]
    zs = [p[2] for _, v in tris for p in v]
    top_z = max(zs)
    levels = {}
    for (nx, ny, nz), v in tris:
        if nz > 0.9:
            levels.setdefault(round(sum(p[2] for p in v) / 3, 3), []).append(v)
    rim = max(levels) if levels else top_z
    cands = []
    for z, faces in levels.items():
        if z >= rim - 1e-3: continue
        area = sum(tri_area_xy(f) for f in faces)
        cx = sum(sum(p[0] for p in f) for f in faces) / (3 * len(faces))
        cy = sum(sum(p[1] for p in f) for f in faces) / (3 * len(faces))
        cands.append((area, z, cx, cy))
    if not cands: raise SystemExit("No interior pocket floor found in STL.")
    cands.sort(reverse=True); area, floor_z, cx, cy = cands[0]
    return {"volume": area * (top_z - floor_z), "hole_x": cx, "hole_y": cy,
            "top_z": top_z, "floor_z": floor_z, "depth": top_z - floor_z,
            "area": area, "bed_coords": False, "model_cx": (min(xs)+max(xs))/2,
            "model_cy": (min(ys)+max(ys))/2}

def part_center_from_gcode(text):
    m = re.search(r"objects_info = (\{.*\})", text)
    if m:
        pts = re.findall(r"\[([\d.\-]+),([\d.\-]+)\]", m.group(1))
        if pts:
            xs = [float(a) for a, b in pts]; ys = [float(b) for a, b in pts]
            return (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    return None

# ---------- G-code helpers ----------

def active_tool_at_end(lines):
    tool = 0
    for ln in lines:
        if re.match(r"^T\d( |$)", ln.strip()): tool = int(ln.strip()[1])
    return tool

def inject_tool_initialized(lines, tool):
    # startup ends at first ;LAYER_CHANGE; is the tool picked there?
    for ln in lines:
        if ln.strip().startswith(";LAYER_CHANGE"): return False
        if re.match(rf"^T{tool} S1 L0 D0", ln.strip()): return True
    return False

def build_tool_init(tool, flt, idle):
    # Mirror PrusaSlicer/Orca XL "purge Nth tool": park, heat, pick, purge in
    # the tool's front lane, retract. Registers the tool so the firmware treats
    # the job as multi-tool and the later Tn change is accepted.
    lane = {0: 30, 1: 150, 2: 210, 3: 330, 4: 330}[tool]
    sign = 1 if tool in (0, 2) else -1
    x_to, x_pg = lane + sign * 10, lane + sign * 40
    y = -7 if tool < 4 else -4.5
    b = []; a = b.append
    a(f"; --- magma: register inject tool T{tool} (added so the toolchange is recognized) ---")
    a("G1 F24000")
    a("P0 S1 L2 D0; park the tool")
    a(f"M109 T{tool} S{flt}")
    a(f"T{tool} S1 L0 D0; pick the tool")
    a("G92 E0")
    a(f"G0 X{lane} Y{y} Z10 F24000 ; to purge lane")
    a(f"G0 E10 X{x_to} Z0.2 F500 ; purge")
    a(f"G0 X{x_pg} E9 F800 ; purge + wipe")
    a(f"G0 X{x_pg + sign*3} Z0.05 F8000 ; wipe")
    a(f"G0 X{x_pg + sign*6} Z0.2 F8000 ; wipe away")
    a("G1 E-1.2 F2400 ; retract")
    a("G92 E0")
    a(f"M104 S{idle} T{tool} ; idle temp")
    a("; --- end inject tool init ---")
    return b

def patch_filament_used(lines, tool, e_mm, area, density=1.24):
    # Update per-tool '; filament used [mm]/[cm3]/[g]' arrays + totals so the
    # metadata registers the inject tool (firmware/UI read these).
    cm3 = e_mm * area / 1000.0
    g = cm3 * density
    val = {"[mm]": e_mm, "[cm3]": cm3, "[g]": g}
    out = []
    for l in lines:
        m = re.match(r"^(; filament used (\[mm\]|\[cm3\]|\[g\]) = )(.*)$", l)
        if m and m.group(2) in val:
            arr = [x.strip() for x in m.group(3).split(",")]
            while len(arr) <= tool: arr.append("0.00")
            arr[tool] = f"{val[m.group(2)]:.2f}"
            out.append(m.group(1) + ", ".join(arr)); continue
        mt = re.match(r"^(; total filament used (\[g\]|\[cm3\]) = )([\d.]+)$", l)
        if mt:
            add = g if mt.group(2) == "[g]" else cm3
            out.append(mt.group(1) + f"{float(mt.group(3)) + add:.2f}"); continue
        out.append(l)
    return out

def find_end_anchor(lines):
    for i in range(len(lines) - 1):
        if lines[i].strip() in (";TYPE:Custom",) and \
           lines[i + 1].strip().startswith("; Filament-specific end gcode"):
            return i
    for pat in ("; Filament-specific end gcode", "EXECUTABLE_BLOCK_END",
                "; filament used", "M104 S0"):
        idx = [i for i, l in enumerate(lines) if l.strip().startswith(pat)]
        if idx: return idx[-1]
    raise SystemExit("Could not find end-gcode anchor.")

# ---------- injection block ----------

def build_block(p, args, gc):
    area = math.pi * (gc["dia"] / 2) ** 2
    volume = args.volume_mm3 if args.volume_mm3 else p["volume"] * args.fill
    e_total = volume / area
    flow = args.flow if args.flow > 0 else gc["max_vol"]
    feed = flow / area * 60.0
    nseg = max(1, math.ceil(e_total / 180.0))
    e_seg = e_total / nseg
    rim_z = p["top_z"]
    if gc["max_layer_z"]: rim_z = min(rim_z, gc["max_layer_z"])
    plunge_z = rim_z - args.plunge
    X, Y = gc["bed_x"], gc["bed_y"]; rel = gc["relative_e"]

    b = []; a = b.append
    a(";===================================================")
    a("; MAGMA INJECTION (auto, magma_inject.py)")
    a(f"; cavity {p['area']:.1f} mm^2 max x ~{p['depth']:.2f} mm = {p['volume']:.0f} mm^3"
      f"  ->  inject {volume:.0f} mm^3")
    a(f"; XY {X:.3f},{Y:.3f}  rim z={rim_z:.2f}  plunge {args.plunge}mm -> z={plunge_z:.2f}")
    a(f"; {args.temp}C  flow {flow:.1f} mm^3/s  E={e_total:.1f}mm in {nseg}x{e_seg:.2f}mm @ F{feed:.0f}")
    a(";===================================================")
    a("M83 ; relative E" if rel else "G92 E0")
    if args.inject_tool != gc["mold_tool"]:
        tc = gc["tc_retract"]
        a(f"; --- tool change: mold T{gc['mold_tool']} -> inject T{args.inject_tool} ---")
        a(f"G1 E-{tc:.1f} F2100        ; unload mold filament")
        a(f"M104 S70 T{gc['mold_tool']}      ; cool mold tool")
        a("G1 F21000")
        a("P0 S1 L2 D0               ; park mold tool")
        a(f"M109 S{args.temp} T{args.inject_tool}      ; heat inject tool + wait")
        a("M106 S255                 ; fan")
        a(f"T{args.inject_tool} S1 L0 D0            ; pick inject tool")
        a(f"G1 E{tc:.1f} F1500         ; reload inject filament")
    else:
        a(f"M104 S{args.temp}                 ; heat inject tool T{args.inject_tool}")
        a(f"M109 S{args.temp}                 ; wait")
    a("G1 Z20 F600                ; lift clear")
    a(f"G1 X{X:.3f} Y{Y:.3f} F9000   ; travel to injection point")
    a(f"G1 Z{rim_z:.3f} F600          ; descend to cavity rim")
    a(f"G1 Z{plunge_z:.3f} F60         ; plunge {args.plunge}mm")
    if rel:
        a("G1 E0.8 F2100             ; prime")
        a(f"; --- inject {volume:.0f} mm^3 ---")
        for _ in range(nseg): a(f"G1 E{e_seg:.3f} F{feed:.0f}")
        a("G4 P800"); a("G1 E-1.5 F2100            ; retract")
    else:
        a("G92 E0"); e = 0.8; a(f"G1 E{e:.3f} F2100")
        a(f"; --- inject {volume:.0f} mm^3 ---")
        for _ in range(nseg): e += e_seg; a(f"G1 E{e:.3f} F{feed:.0f}")
        a("G4 P800"); e -= 1.5; a(f"G1 E{e:.3f} F2100")
    a("G1 Z40 F600                ; lift back up")
    a(";===================== END MAGMA INJECTION =========")
    return b, dict(volume=volume, e_total=e_total, feed=feed, nseg=nseg,
                   rim_z=rim_z, plunge_z=plunge_z, flow=flow)

# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gcode", required=True)
    ap.add_argument("--out")
    ap.add_argument("--stl", help="optional; detect cavity from mesh instead of G-code")
    ap.add_argument("--temp", type=int, default=240)
    ap.add_argument("--inject-tool", type=int, default=0)
    ap.add_argument("--fill", type=float, default=1.0)
    ap.add_argument("--plunge", type=float, default=2.0)
    ap.add_argument("--flow", type=float, default=0.0)
    ap.add_argument("--volume-mm3", type=float, default=0.0)
    ap.add_argument("--no-strip-color-change", action="store_true")
    ap.add_argument("--no-tool-init", action="store_true",
                    help="don't splice inject-tool init even if it's uninitialized")
    ap.add_argument("--measure-only", action="store_true",
                    help="just report the cavity volume; don't write G-code")
    args = ap.parse_args()

    text = open(args.gcode).read()
    lines = text.split("\n")
    nozzle = first_float(cfg(text, "nozzle_diameter"), 0.4)

    if args.stl:
        p = detect_cavity_stl(load_stl(args.stl))
        center = part_center_from_gcode(text)
        if center is None: raise SystemExit("No objects_info to map STL->bed.")
        bed_x = center[0] + (p["hole_x"] - p["model_cx"])
        bed_y = center[1] + (p["hole_y"] - p["model_cy"])
        src = "STL mesh"
    else:
        p = detect_cavity_gcode(text, nozzle)
        bed_x, bed_y = p["hole_x"], p["hole_y"]
        src = f"G-code raster (nozzle {nozzle}mm, stamp r={p['stamp_radius_cells']}cell)"

    print(f"detection: {src}")
    print(f"cavity: {p['area']:.1f} mm^2 max x ~{p['depth']:.2f} mm "
          f"= {p['volume']:.0f} mm^3   (z {p['floor_z']:.2f}..{p['top_z']:.2f})")
    print(f"inject XY (bed): {bed_x:.2f}, {bed_y:.2f}")

    if args.measure_only:
        print(f">>> internal volume = {p['volume']:.0f} mm^3 <<<"); return
    if not args.out: raise SystemExit("--out required (or use --measure-only)")

    stripped = 0
    if not args.no_strip_color_change:
        out = []; i = 0
        while i < len(lines):
            if lines[i].startswith(";COLOR_CHANGE") and i + 1 < len(lines) \
               and lines[i + 1].strip() == "M600":
                stripped += 1; i += 2; continue
            out.append(lines[i]); i += 1
        lines = out

    gc = {
        "dia": first_float(cfg(text, "filament_diameter"), 1.75),
        "max_vol": first_float(cfg(text, "filament_max_volumetric_speed"), 15.0),
        "max_layer_z": first_float(cfg(text, "max_layer_z"), 0.0),
        "relative_e": (cfg(text, "use_relative_e_distances", "1") == "1"),
        "tc_retract": first_float(cfg(text, "filament_retract_length_toolchange"), 20.0),
        "mold_tool": active_tool_at_end(lines),
        "bed_x": bed_x, "bed_y": bed_y,
    }
    # If injecting on a different tool that the slice never initialized at
    # startup, splice in its init so the firmware accepts the tool change.
    tool_init = False
    if (args.inject_tool != gc["mold_tool"] and not args.no_tool_init
            and not inject_tool_initialized(lines, args.inject_tool)):
        flt_list = [int(float(v)) for v in
                    (cfg(text, "nozzle_temperature_initial_layer")
                     or cfg(text, "first_layer_temperature") or "220").split(",")]
        standby = first_float(cfg(text, "standby_temperature_delta"), -40.0)
        flt = flt_list[args.inject_tool] if args.inject_tool < len(flt_list) else 220
        idle = max(0, int(flt + standby))
        init = build_tool_init(args.inject_tool, flt, idle)
        # insert before the initial tool's purge (fallback: first ;LAYER_CHANGE)
        ins = next((i for i, l in enumerate(lines)
                    if l.strip() == "; purge initial tool"), None)
        if ins is None:
            ins = next(i for i, l in enumerate(lines)
                       if l.strip().startswith(";LAYER_CHANGE"))
        lines = lines[:ins] + init + lines[ins:]
        # widen MBL probe area to cover the 2nd tool's purge lane
        lines = [l.replace("X30 Y0 W50 H20 C", "X30 Y0 W130 H20 C") for l in lines]
        tool_init = True

    block, info = build_block(p, args, gc)

    # register the inject tool in the filament-used metadata (E + ~20mm purge)
    meta_patched = False
    if args.inject_tool != gc["mold_tool"]:
        area = math.pi * (gc["dia"] / 2) ** 2
        lines = patch_filament_used(lines, args.inject_tool, info["e_total"] + 20.0, area)
        meta_patched = True

    anchor = find_end_anchor(lines)
    open(args.out, "w").write("\n".join(lines[:anchor] + block + lines[anchor:]))

    print(f"mold tool T{gc['mold_tool']} -> inject tool T{args.inject_tool}"
          + ("  (tool change)" if args.inject_tool != gc['mold_tool'] else "  (same tool)")
          + ("  + startup init spliced" if tool_init else ""))
    print(f"inject {info['volume']:.0f} mm^3 = E{info['e_total']:.1f}mm in {info['nseg']} seg "
          f"@ F{info['feed']:.0f} ({info['flow']:.0f} mm^3/s), {args.temp}C, plunge z={info['plunge_z']:.2f}")
    if stripped: print(f"stripped {stripped} stray M600 color-change(s)")
    if meta_patched: print(f"patched filament-used metadata for T{args.inject_tool}")
    print(f"wrote {args.out}")

if __name__ == "__main__":
    main()
