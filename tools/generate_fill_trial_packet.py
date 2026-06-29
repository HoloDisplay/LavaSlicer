#!/usr/bin/env python3
"""Generate a physical fill-trial data collection packet from the plan CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MEASUREMENT_COLUMNS = [
    "trial_id",
    "date",
    "operator",
    "printer",
    "mold_file",
    "gcode_file",
    "mold_material",
    "mold_tool",
    "mold_nozzle_mm",
    "injection_material",
    "injection_density_g_cm3",
    "injection_tool",
    "injection_nozzle_mm",
    "geometry",
    "port_diameter_mm",
    "target_volume_mm3",
    "fill_ratio",
    "commanded_volume_mm3",
    "commanded_e_mm",
    "injection_temp_c",
    "bed_temp_c",
    "flow_mm3_s",
    "start_z_mm",
    "end_z_mm",
    "plunge_mm",
    "dwell_s",
    "purge_cleaned",
    "mass_before_g",
    "mass_after_g",
    "delivered_mass_g",
    "estimated_delivered_volume_mm3",
    "visible_fill_depth_mm",
    "bottom_fill_score_0_3",
    "leakage_score_0_3",
    "blockage_score_0_3",
    "mold_softening_score_0_3",
    "removal_quality_0_3",
    "failure_label_primary",
    "failure_label_secondary",
    "notes",
    "photo_top",
    "photo_side",
    "photo_section",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def commanded_e_mm(volume_mm3: str, filament_diameter_mm: float = 1.75) -> str:
    try:
        volume = float(volume_mm3)
    except ValueError:
        return ""
    area = 3.141592653589793 * (filament_diameter_mm / 2.0) ** 2
    return f"{volume / area:.3f}"


def yes(value: str) -> bool:
    return value.strip().lower() in {"yes", "true", "1", "y"}


def measurement_row(plan: dict[str, str]) -> dict[str, str]:
    plan_id = plan["plan_id"]
    section_path = f"paper/photos/{plan_id}_section.jpg" if yes(plan.get("photo_section_required", "")) else ""
    return {
        "trial_id": plan_id,
        "date": "",
        "operator": "",
        "printer": "Prusa XL-style tool-changing FFF printer",
        "mold_file": f"paper/molds/{plan_id}_mold.stl",
        "gcode_file": f"paper/gcode/{plan_id}_executed.gcode",
        "mold_material": "PETG",
        "mold_tool": "T0",
        "mold_nozzle_mm": "0.4",
        "injection_material": "PLA",
        "injection_density_g_cm3": "",
        "injection_tool": "T1",
        "injection_nozzle_mm": "0.8",
        "geometry": plan.get("geometry", ""),
        "port_diameter_mm": plan.get("port_diameter_mm", ""),
        "target_volume_mm3": plan.get("target_volume_mm3", ""),
        "fill_ratio": plan.get("fill_ratio", ""),
        "commanded_volume_mm3": plan.get("planned_commanded_volume_mm3", ""),
        "commanded_e_mm": commanded_e_mm(plan.get("planned_commanded_volume_mm3", "")),
        "injection_temp_c": plan.get("injection_temp_c", ""),
        "bed_temp_c": "",
        "flow_mm3_s": plan.get("flow_mm3_s", ""),
        "start_z_mm": plan.get("start_z_mm", ""),
        "end_z_mm": plan.get("end_z_mm", ""),
        "plunge_mm": plan.get("plunge_mm", ""),
        "dwell_s": plan.get("dwell_s", ""),
        "purge_cleaned": "",
        "mass_before_g": "",
        "mass_after_g": "",
        "delivered_mass_g": "",
        "estimated_delivered_volume_mm3": "",
        "visible_fill_depth_mm": "",
        "bottom_fill_score_0_3": "",
        "leakage_score_0_3": "",
        "blockage_score_0_3": "",
        "mold_softening_score_0_3": "",
        "removal_quality_0_3": "",
        "failure_label_primary": "",
        "failure_label_secondary": "",
        "notes": f"Plan {plan_id}; expected label: {plan.get('expected_failure_label', '')}; purpose: {plan.get('purpose', '')}",
        "photo_top": f"paper/photos/{plan_id}_top.jpg",
        "photo_side": f"paper/photos/{plan_id}_side.jpg" if yes(plan.get("photo_side_required", "")) else "",
        "photo_section": section_path,
    }


def planned_gcode_path(plan: dict[str, str]) -> str:
    target = plan.get("target_gcode_file", "")
    if not target:
        target = f"planned/{plan.get('plan_id', '').lower()}_planned_injection_block.gcode"
    return f"output/trials/{target}"


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MEASUREMENT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in MEASUREMENT_COLUMNS})


def write_run_sheet(plan: dict[str, str], row: dict[str, str], out_dir: Path) -> Path:
    path = out_dir / f"{plan['plan_id']}_run_sheet.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(f"# Fill Trial Run Sheet: {plan['plan_id']}\n\n")
        f.write("## Planned Parameters\n\n")
        f.write(f"- Run order: {plan.get('run_order', '')}\n")
        f.write(f"- Priority: {plan.get('priority', '')}\n")
        f.write(f"- Geometry: {plan.get('geometry', '')}\n")
        f.write(f"- Port diameter: {plan.get('port_diameter_mm', '')} mm\n")
        f.write(f"- Schedule: {plan.get('schedule', '')}\n")
        f.write(f"- Injection temperature: {plan.get('injection_temp_c', '')} C\n")
        f.write(f"- Flow rate: {plan.get('flow_mm3_s', '')} mm3/s\n")
        f.write(f"- Commanded volume: {plan.get('planned_commanded_volume_mm3', '')} mm3\n")
        f.write(f"- Estimated E length for 1.75 mm filament: {row.get('commanded_e_mm', '')} mm\n")
        f.write(f"- Start/end Z: {plan.get('start_z_mm', '')} / {plan.get('end_z_mm', '')} mm\n")
        f.write(f"- Plunge: {plan.get('plunge_mm', '')} mm\n")
        f.write(f"- Dwell: {plan.get('dwell_s', '')} s\n")
        f.write(f"- Primary metric: {plan.get('primary_metric', '')}\n")
        f.write(f"- Expected label: {plan.get('expected_failure_label', '')}\n")
        f.write(f"- Purpose: {plan.get('purpose', '')}\n\n")

        f.write("## Required Evidence Paths\n\n")
        f.write(f"- Planned injection block: `{planned_gcode_path(plan)}`\n")
        f.write(f"- Mold model: `{row['mold_file']}`\n")
        f.write(f"- Executed G-code: `{row['gcode_file']}`\n")
        f.write(f"- Top photo: `{row['photo_top']}`\n")
        if row.get("photo_side"):
            f.write(f"- Side photo: `{row['photo_side']}`\n")
        if row.get("photo_section"):
            f.write(f"- Section/removed photo: `{row['photo_section']}`\n")
        f.write("\n")

        f.write("## Preflight\n\n")
        f.write("- Confirm mold is printed with an open, unobstructed port.\n")
        f.write("- Review the planned injection block, but do not treat it as executed evidence.\n")
        f.write("- Save the exact mold model to the path above before slicing or printing.\n")
        f.write("- Save the exact executed G-code to the path above before or immediately after the run.\n")
        f.write("- Confirm injection tool is heated to the planned temperature before approach.\n")
        f.write("- Confirm purge/wipe is complete and the nozzle can seat at the port.\n")
        f.write("- Collision-check the port approach and plunge before running unattended motion.\n\n")

        f.write("## Failure Label Vocabulary\n\n")
        f.write(
            "Use observed labels only: `complete_fill`, `partial_fill`, `freezing`, `leakage`, "
            "`port_blockage`, `mold_softening`, `flow_limit`, `trapped_air`, "
            "`removal_damage`, `collision_risk`, or `other`.\n\n"
        )

        f.write("## Record During Trial\n\n")
        for field in [
            "date",
            "operator",
            "printer",
            "mold_file",
            "bed_temp_c",
            "purge_cleaned",
            "mass_before_g",
            "mass_after_g",
            "visible_fill_depth_mm",
            "bottom_fill_score_0_3",
            "leakage_score_0_3",
            "blockage_score_0_3",
            "mold_softening_score_0_3",
            "removal_quality_0_3",
            "failure_label_primary",
            "failure_label_secondary",
            "notes",
        ]:
            f.write(f"- {field}: \n")
    return path


def write_runbook(plans: list[dict[str, str]], rows: list[dict[str, str]], run_sheets: list[Path], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write("# Magma Fill Trial Packet\n\n")
        f.write("This generated packet turns `paper/fill_trial_plan.csv` into a run-ready data collection package. It does not contain measured results.\n\n")
        f.write("## Outputs\n\n")
        f.write("- Prefilled CSV skeleton: `output/trials/fill_trials_prefill.csv`\n")
        f.write("- Per-trial run sheets: `output/trials/run_sheets/`\n\n")
        f.write("## Use\n\n")
        f.write("1. Run each sheet in `run_order`.\n")
        f.write("2. Save the exact mold model, executed G-code, and required photos to the listed paths.\n")
        f.write("3. Copy completed rows from `output/trials/fill_trials_prefill.csv` into `paper/fill_trials_template.csv` only after the masses, scores, and evidence files exist.\n")
        f.write("4. Run `make all` and confirm the physical-data warning is replaced by publishable measured rows.\n\n")
        f.write("## Planned Trials\n\n")
        f.write("| run | plan_id | schedule | temp C | flow mm3/s | section? | run sheet |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
        for plan, row, sheet in zip(plans, rows, run_sheets):
            section = "yes" if row.get("photo_section") else "no"
            f.write(
                "| "
                + " | ".join([
                    plan.get("run_order", ""),
                    plan.get("plan_id", ""),
                    plan.get("schedule", ""),
                    plan.get("injection_temp_c", ""),
                    plan.get("flow_mm3_s", ""),
                    section,
                    f"`{sheet.relative_to(ROOT)}`",
                ])
                + " |\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=Path("paper/fill_trial_plan.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("output/trials"))
    args = parser.parse_args()

    plans = sorted(read_rows(args.plan.resolve()), key=lambda row: int(row.get("run_order", "0") or 0))
    out_dir = args.out_dir.resolve()
    rows = [measurement_row(plan) for plan in plans]
    csv_path = out_dir / "fill_trials_prefill.csv"
    run_sheet_dir = out_dir / "run_sheets"
    run_sheets = [write_run_sheet(plan, row, run_sheet_dir) for plan, row in zip(plans, rows)]
    runbook_path = out_dir / "fill_trial_packet.md"

    write_csv(rows, csv_path)
    write_runbook(plans, rows, run_sheets, runbook_path)

    print(runbook_path)
    print(csv_path)
    print(f"run_sheets={len(run_sheets)}")
    print(f"planned_trials={len(plans)}")
    return 0 if len(plans) == len(run_sheets) and len(plans) >= 10 else 1


if __name__ == "__main__":
    raise SystemExit(main())
