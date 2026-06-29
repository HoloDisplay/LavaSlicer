#!/usr/bin/env python3
"""Generate planned injection-block G-code snippets from the fill-trial plan."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILAMENT_DIAMETER_MM = 1.75
FILAMENT_AREA_MM2 = math.pi * (FILAMENT_DIAMETER_MM / 2.0) ** 2
MAX_E_SEGMENT_MM = 5.0


SUMMARY_COLUMNS = [
    "plan_id",
    "planned_gcode_file",
    "schedule",
    "injection_temp_c",
    "flow_mm3_s",
    "commanded_volume_mm3",
    "commanded_e_mm",
    "feed_mm_min",
    "segments",
    "start_z_mm",
    "end_z_mm",
]


def read_plan(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def parse_float(row: dict[str, str], key: str) -> float:
    return float(row.get(key, "0") or 0)


def e_length_for_volume(volume_mm3: float) -> float:
    return volume_mm3 / FILAMENT_AREA_MM2


def feed_for_flow(flow_mm3_s: float) -> float:
    return (flow_mm3_s / FILAMENT_AREA_MM2) * 60.0


def segment_lengths(total_e_mm: float) -> list[float]:
    segments: list[float] = []
    remaining = total_e_mm
    while remaining > MAX_E_SEGMENT_MM + 1e-9:
        segments.append(MAX_E_SEGMENT_MM)
        remaining -= MAX_E_SEGMENT_MM
    if remaining > 1e-9:
        segments.append(remaining)
    return segments


def planned_path(row: dict[str, str], out_dir: Path) -> Path:
    target = row.get("target_gcode_file", "")
    if not target:
        target = f"planned/{row.get('plan_id', 'unknown').lower()}_planned_injection_block.gcode"
    return out_dir / target


def write_block(row: dict[str, str], path: Path) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    plan_id = row["plan_id"]
    volume = parse_float(row, "planned_commanded_volume_mm3")
    total_e = e_length_for_volume(volume)
    flow = parse_float(row, "flow_mm3_s")
    feed = feed_for_flow(flow)
    start_z = parse_float(row, "start_z_mm")
    end_z = parse_float(row, "end_z_mm")
    dwell = parse_float(row, "dwell_s")
    segments = segment_lengths(total_e)
    schedule = row.get("schedule", "")
    temp = row.get("injection_temp_c", "")
    z_values: list[float] = []
    if schedule == "rising-Z" and len(segments) > 1:
        for idx, _ in enumerate(segments):
            t = idx / (len(segments) - 1)
            z_values.append(start_z + t * (end_z - start_z))
    else:
        z_values = [start_z for _ in segments]

    with path.open("w") as f:
        f.write("; MAGMA PLANNED INJECTION BLOCK - NOT EXECUTED EVIDENCE\n")
        f.write(f"; plan_id: {plan_id}\n")
        f.write(f"; schedule: {schedule}\n")
        f.write(f"; geometry: {row.get('geometry', '')}\n")
        f.write(f"; port_diameter_mm: {row.get('port_diameter_mm', '')}\n")
        f.write(f"; injection_temp_c: {temp}\n")
        f.write(f"; flow_mm3_s: {flow:g}\n")
        f.write(f"; commanded_volume_mm3: {volume:g}\n")
        f.write(f"; commanded_e_mm: {total_e:.3f}\n")
        f.write(f"; feed_mm_min: {feed:.1f}\n")
        f.write(f"; start_z_mm: {start_z:g}\n")
        f.write(f"; end_z_mm: {end_z:g}\n")
        f.write("; This is an injection-stage snippet, not a complete printable job.\n")
        f.write("; Before use, verify mold print G-code, port XY, tool selection, purge, and collision clearance.\n")
        f.write(f"; Save the exact executed job as paper/gcode/{plan_id}_executed.gcode after running.\n")
        f.write("M83 ; relative extrusion\n")
        f.write("T1 ; select injection tool\n")
        f.write(f"M109 S{temp} T1 ; wait for injection tool temperature\n")
        f.write("; PRECONDITION: machine is already at the verified port XY before the plunge.\n")
        f.write(f"G1 Z{start_z:.3f} F600 ; planned port/plunge Z\n")
        for idx, (length, z) in enumerate(zip(segments, z_values), start=1):
            if schedule == "rising-Z":
                f.write(f"G1 Z{z:.3f} E{length:.3f} F{feed:.1f} ; planned injection segment {idx}/{len(segments)}\n")
            else:
                f.write(f"G1 E{length:.3f} F{feed:.1f} ; planned injection segment {idx}/{len(segments)}\n")
        if dwell > 0:
            f.write(f"G4 S{dwell:g} ; dwell after injection\n")
        f.write("G1 E-2.000 F1800 ; retract after injection\n")
        f.write(f"G1 Z{max(start_z, end_z) + 2.0:.3f} F600 ; lift clear\n")
        f.write("; END MAGMA PLANNED INJECTION BLOCK\n")

    return {
        "plan_id": plan_id,
        "planned_gcode_file": str(path.relative_to(ROOT)),
        "schedule": schedule,
        "injection_temp_c": temp,
        "flow_mm3_s": f"{flow:g}",
        "commanded_volume_mm3": f"{volume:g}",
        "commanded_e_mm": f"{total_e:.3f}",
        "feed_mm_min": f"{feed:.1f}",
        "segments": str(len(segments)),
        "start_z_mm": f"{start_z:g}",
        "end_z_mm": f"{end_z:g}",
    }


def write_summary(rows: list[dict[str, str]], out_dir: Path) -> None:
    csv_path = out_dir / "planned_injection_gcode_summary.csv"
    md_path = out_dir / "planned_injection_gcode_summary.md"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    with md_path.open("w") as f:
        f.write("# Planned Injection G-code Summary\n\n")
        f.write("These files are planned injection-stage snippets only. They are not executed evidence and are not counted as measured fill-trial data.\n\n")
        f.write("| plan_id | file | schedule | temp C | flow mm3/s | E mm | segments |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
        for row in rows:
            f.write(
                "| "
                + " | ".join([
                    row["plan_id"],
                    f"`{row['planned_gcode_file']}`",
                    row["schedule"],
                    row["injection_temp_c"],
                    row["flow_mm3_s"],
                    row["commanded_e_mm"],
                    row["segments"],
                ])
                + " |\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=Path("paper/fill_trial_plan.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("output/trials"))
    args = parser.parse_args()

    plan_rows = sorted(read_plan(args.plan.resolve()), key=lambda row: int(row.get("run_order", "0") or 0))
    out_dir = args.out_dir.resolve()
    summary_rows = [write_block(row, planned_path(row, out_dir)) for row in plan_rows]
    write_summary(summary_rows, out_dir)

    print(out_dir / "planned_injection_gcode_summary.md")
    print(f"planned_gcode={len(summary_rows)}")
    return 0 if len(summary_rows) == len(plan_rows) and len(summary_rows) >= 10 else 1


if __name__ == "__main__":
    raise SystemExit(main())
