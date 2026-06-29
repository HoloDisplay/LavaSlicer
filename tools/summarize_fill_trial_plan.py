#!/usr/bin/env python3
"""Summarize and validate the planned Magma fill-trial matrix."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_COLUMNS = [
    "plan_id",
    "priority",
    "run_order",
    "geometry",
    "port_diameter_mm",
    "schedule",
    "injection_temp_c",
    "flow_mm3_s",
    "target_volume_mm3",
    "fill_ratio",
    "planned_commanded_volume_mm3",
    "start_z_mm",
    "end_z_mm",
    "plunge_mm",
    "dwell_s",
    "target_gcode_file",
    "primary_metric",
    "expected_failure_label",
    "photo_top_required",
    "photo_side_required",
    "photo_section_required",
    "purpose",
]


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
        return list(reader.fieldnames or []), rows


def core_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("priority") == "core"]


def missing_required_values(rows: list[dict[str, str]]) -> list[str]:
    missing: list[str] = []
    for row in rows:
        plan_id = row.get("plan_id", "(missing plan_id)")
        for col in EXPECTED_COLUMNS:
            if not row.get(col, ""):
                missing.append(f"{plan_id}:{col}")
    return missing


def coverage_status(rows: list[dict[str, str]]) -> tuple[bool, str]:
    core = core_rows(rows)
    temps = sorted({row.get("injection_temp_c", "") for row in core})
    flows = sorted({row.get("flow_mm3_s", "") for row in core})
    combos = {(row.get("injection_temp_c", ""), row.get("flow_mm3_s", "")) for row in core}
    expected_temps = {"240", "255", "275"}
    expected_flows = {"10", "20", "30"}
    expected_combos = {(temp, flow) for temp in expected_temps for flow in expected_flows}
    missing_combos = sorted(expected_combos - combos)
    ok = len(core) >= 9 and set(temps) == expected_temps and set(flows) == expected_flows and not missing_combos
    detail = f"core_rows={len(core)}, temps={temps}, flows={flows}, missing_combos={missing_combos}"
    return ok, detail


def write_markdown(rows: list[dict[str, str]], missing_columns: list[str], missing_values: list[str], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    ok, detail = coverage_status(rows)
    with out.open("w") as f:
        f.write("# Fill Trial Plan Summary\n\n")
        if missing_columns:
            f.write("Schema status: missing columns: " + ", ".join(missing_columns) + "\n\n")
        else:
            f.write("Schema status: expected columns present.\n\n")
        f.write(f"Planned trials: {len(rows)}\n\n")
        f.write(f"Core matrix coverage: {'pass' if ok else 'fail'} ({detail})\n\n")
        if missing_values:
            f.write("Rows with missing required values:\n\n")
            for item in missing_values:
                f.write(f"- `{item}`\n")
            f.write("\n")
        f.write("| plan_id | priority | run_order | schedule | temp C | flow mm3/s | metric | expected label |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")
        for row in rows:
            values = [
                row.get("plan_id", ""),
                row.get("priority", ""),
                row.get("run_order", ""),
                row.get("schedule", ""),
                row.get("injection_temp_c", ""),
                row.get("flow_mm3_s", ""),
                row.get("primary_metric", ""),
                row.get("expected_failure_label", ""),
            ]
            f.write("| " + " | ".join(values) + " |\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("paper/fill_trial_plan.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("output/verification"))
    args = parser.parse_args()

    columns, rows = read_rows(args.input.resolve())
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in columns]
    missing_values = missing_required_values(rows)
    out = args.out_dir.resolve() / "fill_trial_plan_summary.md"
    write_markdown(rows, missing_columns, missing_values, out)
    ok, detail = coverage_status(rows)
    print(out)
    print(f"planned_trials={len(rows)}")
    print(f"core_matrix={'pass' if ok else 'fail'}")
    print(detail)
    if missing_columns:
        print("missing_columns=" + ",".join(missing_columns))
    if missing_values:
        print("missing_values=" + ",".join(missing_values))
    return 1 if missing_columns or missing_values or not ok else 0


if __name__ == "__main__":
    raise SystemExit(main())
