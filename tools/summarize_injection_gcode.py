#!/usr/bin/env python3
"""Summarize representative Magma injection G-code artifacts.

The paper's verification table is intentionally based on generated G-code,
not on physical fill quality. This script extracts the machine-plan evidence
from the representative files used in the manuscript.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path


FILAMENT_DIAMETER_MM = 1.75
FILAMENT_AREA_MM2 = 3.141592653589793 * (FILAMENT_DIAMETER_MM / 2.0) ** 2
NUMBER_RE = r"-?(?:\d+(?:\.\d*)?|\.\d+)"


@dataclass
class Case:
    artifact: str
    path: Path
    implementation: str


CASES = [
    Case("Tiny cube", Path("paper/gcode/representative/TinyCube_INJECT.gcode"), "Hand-authored Phase 0 block"),
    Case("Mold2 pocket", Path("paper/gcode/representative/Mold2_INJECT.gcode"), "Phase 0 cavity estimate"),
    Case("Cube pocket", Path("paper/gcode/representative/mehran_cube_INJECT.gcode"), "Phase 0 cavity estimate"),
    Case("10 mm part helper", Path("paper/gcode/representative/object-driven-injection-demo-multipart-volume.gcode"), "Native LavaSlicer"),
    Case("30 mm port helper", Path("paper/gcode/representative/cube30-open-mold-20mms-275c.gcode"), "Native LavaSlicer"),
]


def read(path: Path) -> str:
    return path.read_text(errors="replace")


def first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else default


def count_lines(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, re.MULTILINE))


def sum_e_for_comments(text: str, comment_re: str) -> float:
    total = 0.0
    for match in re.finditer(r"^G1\b(?=[^\n]*\bE(" + NUMBER_RE + r"))(?=[^\n]*" + comment_re + r")", text, re.MULTILINE):
        total += float(match.group(1))
    return total


def parse_phase0(case: Case, text: str) -> dict[str, str]:
    if "MAGMA PHASE-0 INJECTION" in text:
        volume = first_match(r"; Fill .*?~(\d+(?:\.\d+)?) mm\^3", text)
        temp_flow_match = re.search(r"; (\d+)C, full flow (\d+(?:\.\d+)?) mm\^3/s", text)
        temp_c, flow = temp_flow_match.groups() if temp_flow_match else ("", "")
        e_total = first_match(r"; E_total=(\d+(?:\.\d+)?)mm", text)
        segments = first_match(r"split into ([^@]+) @", text)
        tool_path = "same tool"
        sequence = "relative E; heat wait; center approach; 2 mm plunge; dwell; retract; lift"
        return row(case, volume, "mm3", temp_c, flow, e_total, segments, tool_path, sequence)

    header = first_match(r"; cavity .*\n; ([^\n]+)\n; ([^\n]+)\n; ([^\n]+)", text)
    volume = first_match(r"->\s*inject\s*(\d+(?:\.\d+)?) mm\^3", text)
    temp_c = first_match(r"; (\d+)C\s+flow", text)
    flow = first_match(r"; \d+C\s+flow\s+(\d+(?:\.\d+)?) mm\^3/s", text)
    e_total = first_match(r"; \d+C\s+flow\s+\d+(?:\.\d+)? mm\^3/s\s+E=(\d+(?:\.\d+)?)mm", text)
    segments = first_match(r"; \d+C\s+flow\s+\d+(?:\.\d+)? mm\^3/s\s+E=\d+(?:\.\d+)?mm in ([^@]+) @", text)
    tool_path = "T0 -> T1" if "tool change: mold T0 -> inject T1" in text else "same tool"
    sequence_parts = ["relative E", "heat wait", "port travel", "2 mm plunge", "dwell", "retract", "lift"]
    if tool_path == "T0 -> T1":
        sequence_parts.insert(1, "mold unload/cool")
        sequence_parts.insert(2, "tool change")
    return row(case, volume, "mm3", temp_c, flow, e_total, segments, tool_path, "; ".join(sequence_parts))


def parse_native(case: Case, text: str) -> dict[str, str]:
    if "; injection pour start" in text:
        text = text[text.index("; injection pour start") :]
    source = first_match(r"; injection pour part source: ([^\n]+)", text, "(manual)")
    port = first_match(r"; injection pour port source: ([^\n]+)", text, "(manual)")
    z_range = first_match(r"; injection pour z range: ([^\n]+)", text)
    temp_values = re.findall(r"^M109 S(\d+) T\d\b", text, re.MULTILINE)
    temp_c = "/".join(dict.fromkeys(temp_values))
    flow_feed = first_match(r"^G1 F(\d+(?:\.\d+)?) ; set injection pour bulk flow", text)
    e_bulk_stationary = sum_e_for_comments(text, "stationary injection pour bulk chunk")
    e_bulk_rising = sum_e_for_comments(text, "rising injection pour bulk chunk")
    e_marker = sum_e_for_comments(text, "injection pour marker")
    e_total = e_marker + e_bulk_stationary + e_bulk_rising
    volume_mm3 = e_total * FILAMENT_AREA_MM2
    flow = ""
    if flow_feed:
        flow = f"{(float(flow_feed) / 60.0) / (1.0 / FILAMENT_AREA_MM2):.1f}"
    stationary_chunks = count_lines(r"stationary injection pour bulk chunk", text)
    rising_chunks = count_lines(r"rising injection pour bulk chunk", text)
    if rising_chunks:
        segments = f"{rising_chunks - 1} x 5 mm + {e_bulk_rising - max(rising_chunks - 1, 0) * 5:.2f} mm"
        motion = "rising-Z"
    else:
        segments = f"{max(stationary_chunks - 1, 0)} x 5 mm + {e_bulk_stationary - max(stationary_chunks - 1, 0) * 5:.2f} mm"
        motion = "stationary"
    tool_path = "T0 -> T1" if "Change Tool0 -> Tool1" in text else "same tool"
    sequence = f"typed Injection pour layer; source={source}; port={port}; z={z_range}; {motion}; heat wait; tool path {tool_path}"
    return row(case, f"{volume_mm3 / 1000.0:.2f}", "cm3", temp_c, flow, f"{e_total:.2f}", segments, tool_path, sequence)


def row(
    case: Case,
    volume: str,
    volume_unit: str,
    temp_c: str,
    flow_mm3s: str,
    e_total_mm: str,
    segments: str,
    tool_path: str,
    verified_sequence: str,
) -> dict[str, str]:
    return {
        "artifact": case.artifact,
        "path": str(case.path),
        "implementation": case.implementation,
        "injection_command": f"{volume} {volume_unit}".strip(),
        "temperature_c": temp_c,
        "flow_mm3_s": flow_mm3s,
        "e_total_mm": e_total_mm,
        "segments": re.sub(r"\s+", " ", segments).strip(),
        "tool_path": tool_path,
        "verified_sequence": verified_sequence,
    }


def parse_case(case: Case, root: Path) -> dict[str, str]:
    text = read(root / case.path)
    if case.implementation == "Native LavaSlicer":
        return parse_native(case, text)
    return parse_phase0(case, text)


def write_markdown(rows: list[dict[str, str]], path: Path) -> None:
    headers = ["artifact", "implementation", "injection_command", "temperature_c", "flow_mm3_s", "segments", "tool_path"]
    with path.open("w", newline="") as f:
        f.write("# G-code Verification Summary\n\n")
        f.write("Generated from local representative G-code artifacts.\n\n")
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for r in rows:
            f.write("| " + " | ".join(r[h] for h in headers) + " |\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out-dir", type=Path, default=Path("output/verification"))
    args = parser.parse_args()

    root = args.root.resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = [parse_case(case, root) for case in CASES]
    csv_path = out_dir / "gcode_verification_summary.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    write_markdown(rows, out_dir / "gcode_verification_summary.md")
    print(csv_path)
    print(out_dir / "gcode_verification_summary.md")


if __name__ == "__main__":
    main()
