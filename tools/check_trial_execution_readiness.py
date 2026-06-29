#!/usr/bin/env python3
"""Check that the physical fill-trial packet is ready for real data collection."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "paper" / "fill_trial_plan.csv"
PREFILL = ROOT / "output" / "trials" / "fill_trials_prefill.csv"
RUN_SHEET_DIR = ROOT / "output" / "trials" / "run_sheets"
PLANNED_GCODE_SUMMARY = ROOT / "output" / "trials" / "planned_injection_gcode_summary.csv"
REPORT = ROOT / "output" / "verification" / "trial_execution_readiness.md"
CHECKLIST = ROOT / "output" / "trials" / "evidence_collection_checklist.md"
MINIMUM_SUBSET = ROOT / "output" / "trials" / "minimum_submission_subset.md"
MINIMUM_SUBSET_IDS = ["P001", "P005", "P009"]

MEASURED_ONLY_FIELDS = [
    "date",
    "operator",
    "bed_temp_c",
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
]

EVIDENCE_DIRS = [
    ROOT / "paper" / "molds",
    ROOT / "paper" / "gcode",
    ROOT / "paper" / "photos",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def by_id(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows if row.get(key, "")}


def add(results: list[tuple[str, str, str]], status: str, check: str, detail: str) -> None:
    results.append((status, check, detail))


def write_checklist(plans: list[dict[str, str]], prefill_by_id: dict[str, dict[str, str]]) -> None:
    CHECKLIST.parent.mkdir(parents=True, exist_ok=True)
    with CHECKLIST.open("w") as f:
        f.write("# Evidence Collection Checklist\n\n")
        f.write(
            "This checklist is generated from `paper/fill_trial_plan.csv` and "
            "`output/trials/fill_trials_prefill.csv`. It is a physical-run handoff, "
            "not measured evidence.\n\n"
        )
        f.write("## Stop Rules\n\n")
        f.write("- Do not copy a row into `paper/fill_trials_template.csv` until the exact executed G-code and required photos exist.\n")
        f.write("- Do not use `output/trials/planned/` snippets as executed evidence.\n")
        f.write("- Do not fill `failure_label_primary` before the trial; use the observed result only.\n")
        f.write("- Keep the rising-Z trial gated until collision clearance is verified.\n\n")
        f.write("## Per-Run Evidence Targets\n\n")
        f.write("| run | plan | temp C | flow mm3/s | schedule | executed G-code | top photo | section photo | run sheet |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
        for plan in sorted(plans, key=lambda row: int(row.get("run_order", "0") or 0)):
            plan_id = plan["plan_id"]
            row = prefill_by_id.get(plan_id, {})
            sheet = RUN_SHEET_DIR / f"{plan_id}_run_sheet.md"
            f.write(
                "| "
                + " | ".join(
                    [
                        plan.get("run_order", ""),
                        plan_id,
                        plan.get("injection_temp_c", ""),
                        plan.get("flow_mm3_s", ""),
                        plan.get("schedule", ""),
                        f"`{row.get('gcode_file', '')}`",
                        f"`{row.get('photo_top', '')}`",
                        f"`{row.get('photo_section', '')}`" if row.get("photo_section", "") else "",
                        f"`{rel(sheet)}`",
                    ]
                )
                + " |\n"
            )
        f.write("\n## Minimum Submission-Strength Subset\n\n")
        f.write("- At least three publishable rows.\n")
        f.write("- At least two temperatures and two flow rates represented.\n")
        f.write("- At least one complete or candidate fill row.\n")
        f.write("- At least one labeled failure-mode row.\n")
        f.write("- At least one sectioned or removed-part photo.\n")


def write_minimum_subset(plans: list[dict[str, str]], prefill_by_id: dict[str, dict[str, str]]) -> None:
    plan_by_id = by_id(plans, "plan_id")
    MINIMUM_SUBSET.parent.mkdir(parents=True, exist_ok=True)
    with MINIMUM_SUBSET.open("w") as f:
        f.write("# Minimum Submission-Strength Fill Dataset\n\n")
        f.write(
            "Run the full 3 x 3 matrix when possible. If time is limited, this is the "
            "smallest first-pass subset that can plausibly clear the physical-data readiness gate "
            "without pretending planned artifacts are measured results.\n\n"
        )
        f.write("## Recommended First Runs\n\n")
        f.write("| plan | reason | temp C | flow mm3/s | expected contrast | required evidence |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        reasons = {
            "P001": "Low-temperature/low-flow lower-bound case.",
            "P005": "Center-point candidate fill; section if it fills.",
            "P009": "High-temperature/high-flow upper-bound case; section if retained.",
        }
        for plan_id in MINIMUM_SUBSET_IDS:
            plan = plan_by_id.get(plan_id, {})
            row = prefill_by_id.get(plan_id, {})
            evidence = [
                row.get("gcode_file", ""),
                row.get("photo_top", ""),
            ]
            if row.get("photo_section", ""):
                evidence.append(row["photo_section"])
            f.write(
                "| "
                + " | ".join(
                    [
                        plan_id,
                        reasons.get(plan_id, ""),
                        plan.get("injection_temp_c", ""),
                        plan.get("flow_mm3_s", ""),
                        plan.get("expected_failure_label", ""),
                        ", ".join(f"`{item}`" for item in evidence if item),
                    ]
                )
                + " |\n"
            )
        f.write("\n## Why This Subset\n\n")
        f.write("- Three rows can satisfy the minimum publishable-row count.\n")
        f.write("- The selected rows span three temperatures and three flow rates.\n")
        f.write("- P005 is the planned candidate success case; P001 and P009 are boundary cases likely to provide failure-mode contrast.\n")
        f.write("- P005 and P009 include section-photo targets, so one sectioned or removed-part image can satisfy the section-evidence gate.\n\n")
        f.write("## Fallback Rules\n\n")
        f.write("- If P005 is not a candidate fill, run P006 or P008 next before drawing conclusions.\n")
        f.write("- If P001 and P009 do not produce a clear failure label, run P003 or P007 to force thermal or flow-limit contrast.\n")
        f.write("- If any selected row lacks exact executed G-code, a top photo, or measured mass fields, do not copy it into `paper/fill_trials_template.csv`.\n")
        f.write("- After the subset is complete, rerun `make all`; the readiness gate still decides whether the data are publication-strength.\n")


def write_report(results: list[tuple[str, str, str]]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("w") as f:
        f.write("# Trial Execution Readiness\n\n")
        ready = all(status == "PASS" for status, _, _ in results)
        f.write(f"Physical-run packet status: {'READY' if ready else 'NOT_READY'}\n\n")
        f.write(f"Evidence checklist: `{rel(CHECKLIST)}`\n\n")
        f.write(f"Minimum subset: `{rel(MINIMUM_SUBSET)}`\n\n")
        f.write("| status | check | detail |\n")
        f.write("| --- | --- | --- |\n")
        for status, check, detail in results:
            safe = detail.replace("|", "\\|").replace("\n", " ")
            f.write(f"| {status} | {check} | {safe} |\n")


def main() -> int:
    results: list[tuple[str, str, str]] = []
    errors = 0

    missing_inputs = [path for path in [PLAN, PREFILL, PLANNED_GCODE_SUMMARY] if not path.exists()]
    if missing_inputs:
        add(results, "FAIL", "required generated inputs", "Missing: " + ", ".join(rel(path) for path in missing_inputs))
        write_report(results)
        print(REPORT)
        return 1

    plans = read_rows(PLAN)
    prefill = read_rows(PREFILL)
    planned_gcode = read_rows(PLANNED_GCODE_SUMMARY)
    plan_by_id = by_id(plans, "plan_id")
    prefill_by_id = by_id(prefill, "trial_id")
    planned_by_id = by_id(planned_gcode, "plan_id")

    plan_ids = sorted(plan_by_id)
    prefill_ids = sorted(prefill_by_id)
    planned_ids = sorted(planned_by_id)
    if len(plan_ids) == 10 and plan_ids == prefill_ids == planned_ids:
        add(results, "PASS", "trial id alignment", f"{len(plan_ids)} planned trials aligned across plan, prefill, and planned G-code summary.")
    else:
        add(results, "FAIL", "trial id alignment", f"plan={plan_ids}, prefill={prefill_ids}, planned_gcode={planned_ids}")
        errors += 1

    bad_run_orders = []
    for index, plan in enumerate(sorted(plans, key=lambda row: int(row.get("run_order", "0") or 0)), start=1):
        if plan.get("run_order", "") != str(index):
            bad_run_orders.append(f"{plan.get('plan_id', '')}:{plan.get('run_order', '')}")
    if not bad_run_orders:
        add(results, "PASS", "run order", "Run order is contiguous from 1 through 10.")
    else:
        add(results, "FAIL", "run order", ", ".join(bad_run_orders))
        errors += 1

    dirty_prefill = []
    wrong_gcode_paths = []
    photo_mismatches = []
    missing_molds = []
    for plan_id in plan_ids:
        plan = plan_by_id[plan_id]
        row = prefill_by_id.get(plan_id, {})
        filled_measured = [field for field in MEASURED_ONLY_FIELDS if row.get(field, "")]
        if filled_measured:
            dirty_prefill.append(f"{plan_id}: {', '.join(filled_measured)}")
        gcode_file = row.get("gcode_file", "")
        if not gcode_file.startswith("paper/gcode/") or "planned" in gcode_file.lower():
            wrong_gcode_paths.append(f"{plan_id}: {gcode_file}")
        if row.get("photo_top", "") != f"paper/photos/{plan_id}_top.jpg":
            photo_mismatches.append(f"{plan_id}: top={row.get('photo_top', '')}")
        if plan.get("photo_side_required", "").lower() == "yes" and row.get("photo_side", "") != f"paper/photos/{plan_id}_side.jpg":
            photo_mismatches.append(f"{plan_id}: side={row.get('photo_side', '')}")
        section_expected = plan.get("photo_section_required", "").lower() == "yes"
        expected_section = f"paper/photos/{plan_id}_section.jpg" if section_expected else ""
        if row.get("photo_section", "") != expected_section:
            photo_mismatches.append(f"{plan_id}: section={row.get('photo_section', '')}")
        mold_file = row.get("mold_file", "")
        if not mold_file or not resolve(mold_file).is_file():
            missing_molds.append(f"{plan_id}: {mold_file}")

    if not dirty_prefill:
        add(results, "PASS", "prefill measured fields", "Measured-result fields are blank before physical trials.")
    else:
        add(results, "FAIL", "prefill measured fields", "; ".join(dirty_prefill))
        errors += 1

    if not wrong_gcode_paths:
        add(results, "PASS", "executed G-code placeholders", "Prefill rows point at `paper/gcode/*_executed.gcode`, not planned snippets.")
    else:
        add(results, "FAIL", "executed G-code placeholders", "; ".join(wrong_gcode_paths))
        errors += 1

    if not photo_mismatches:
        add(results, "PASS", "photo path convention", "Top, side, and required section photo paths match the run plan.")
    else:
        add(results, "FAIL", "photo path convention", "; ".join(photo_mismatches))
        errors += 1

    if not missing_molds:
        add(results, "PASS", "standard mold files", "All prefilled mold_file paths exist.")
    else:
        add(results, "FAIL", "standard mold files", "; ".join(missing_molds))
        errors += 1

    missing_planned = []
    for plan_id in plan_ids:
        path_text = planned_by_id.get(plan_id, {}).get("planned_gcode_file", "")
        if not path_text or not resolve(path_text).is_file():
            missing_planned.append(f"{plan_id}: {path_text}")
    if not missing_planned:
        add(results, "PASS", "planned setup snippets", "All planned injection-stage snippets exist as setup aids.")
    else:
        add(results, "FAIL", "planned setup snippets", "; ".join(missing_planned))
        errors += 1

    missing_run_sheets = []
    stale_run_sheets = []
    for plan_id in plan_ids:
        sheet = RUN_SHEET_DIR / f"{plan_id}_run_sheet.md"
        if not sheet.exists():
            missing_run_sheets.append(rel(sheet))
            continue
        text = sheet.read_text(errors="replace")
        if "do not treat it as executed evidence" not in text or plan_id not in text:
            stale_run_sheets.append(rel(sheet))
    if not missing_run_sheets and not stale_run_sheets:
        add(results, "PASS", "run sheets", f"{len(plan_ids)} run sheets exist and preserve the planned-vs-executed evidence warning.")
    else:
        detail = f"missing={missing_run_sheets}, stale={stale_run_sheets}"
        add(results, "FAIL", "run sheets", detail)
        errors += 1

    missing_dirs = [rel(path) for path in EVIDENCE_DIRS if not path.is_dir()]
    missing_readmes = [rel(path / "README.md") for path in EVIDENCE_DIRS if not (path / "README.md").exists()]
    if not missing_dirs and not missing_readmes:
        add(results, "PASS", "evidence directories", "`paper/molds`, `paper/gcode`, and `paper/photos` are present with README guidance.")
    else:
        add(results, "FAIL", "evidence directories", f"missing_dirs={missing_dirs}, missing_readmes={missing_readmes}")
        errors += 1

    write_checklist(plans, prefill_by_id)
    if CHECKLIST.exists():
        add(results, "PASS", "evidence checklist", rel(CHECKLIST))
    else:
        add(results, "FAIL", "evidence checklist", rel(CHECKLIST))
        errors += 1

    write_minimum_subset(plans, prefill_by_id)
    subset_present = MINIMUM_SUBSET.exists()
    subset_ids_present = all(plan_id in plan_by_id and plan_id in prefill_by_id for plan_id in MINIMUM_SUBSET_IDS)
    subset_temps = {plan_by_id[plan_id].get("injection_temp_c", "") for plan_id in MINIMUM_SUBSET_IDS if plan_id in plan_by_id}
    subset_flows = {plan_by_id[plan_id].get("flow_mm3_s", "") for plan_id in MINIMUM_SUBSET_IDS if plan_id in plan_by_id}
    subset_sections = [prefill_by_id[plan_id].get("photo_section", "") for plan_id in MINIMUM_SUBSET_IDS if prefill_by_id.get(plan_id, {}).get("photo_section", "")]
    if subset_present and subset_ids_present and len(subset_temps) >= 2 and len(subset_flows) >= 2 and subset_sections:
        add(
            results,
            "PASS",
            "minimum submission subset",
            f"{rel(MINIMUM_SUBSET)} covers temps={sorted(subset_temps)}, flows={sorted(subset_flows)}.",
        )
    else:
        detail = (
            f"present={subset_present}, ids_present={subset_ids_present}, "
            f"temps={sorted(subset_temps)}, flows={sorted(subset_flows)}, section_targets={subset_sections}"
        )
        add(results, "FAIL", "minimum submission subset", detail)
        errors += 1

    write_report(results)
    print(REPORT)
    for status, check, detail in results:
        print(f"{status}: {check}: {detail}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
