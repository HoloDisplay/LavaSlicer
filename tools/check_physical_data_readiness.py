#!/usr/bin/env python3
"""Report whether measured fill data are strong enough for submission claims."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "paper" / "fill_trials_template.csv"
OUT = ROOT / "output" / "verification" / "physical_data_readiness.md"

REQUIRED_COLUMNS = [
    "trial_id",
    "date",
    "printer",
    "mold_file",
    "gcode_file",
    "geometry",
    "commanded_volume_mm3",
    "injection_temp_c",
    "flow_mm3_s",
    "delivered_mass_g",
    "estimated_delivered_volume_mm3",
    "visible_fill_depth_mm",
    "bottom_fill_score_0_3",
    "leakage_score_0_3",
    "blockage_score_0_3",
    "mold_softening_score_0_3",
    "failure_label_primary",
    "photo_top",
]

ASSET_COLUMNS = ["mold_file", "gcode_file", "photo_top", "photo_side", "photo_section"]
REQUIRED_ASSET_COLUMNS = ["mold_file", "gcode_file", "photo_top"]
FAILURE_LABELS = {
    "partial_fill",
    "freezing",
    "leakage",
    "port_blockage",
    "mold_softening",
    "flow_limit",
    "trapped_air",
    "removal_damage",
    "collision_risk",
}
PLANNED_GCODE_MARKERS = [
    "NOT EXECUTED EVIDENCE",
    "MAGMA PLANNED INJECTION BLOCK",
    "not a complete printable job",
]


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def asset_exists(path_text: str) -> bool:
    return not path_text.strip() or resolve(path_text).is_file()


def gcode_publishable_issues(row: dict[str, str]) -> list[str]:
    value = row.get("gcode_file", "").strip()
    if not value:
        return []

    issues: list[str] = []
    path = resolve(value)
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        issues.append(f"gcode_file outside repository evidence folder: {value}")
    else:
        if len(relative.parts) < 2 or relative.parts[0] != "paper" or relative.parts[1] != "gcode":
            issues.append(f"gcode_file must be exact executed evidence under paper/gcode: {value}")

    if path.is_file():
        text = path.read_text(errors="replace")
        if any(marker in text for marker in PLANNED_GCODE_MARKERS):
            issues.append(f"gcode_file is marked as planned/not executed evidence: {value}")

    return issues


def has_measurement(row: dict[str, str]) -> bool:
    fields = [
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
        "photo_top",
        "photo_side",
        "photo_section",
    ]
    return row.get("trial_id", "").strip() and any(row.get(field, "").strip() for field in fields)


def missing_required(row: dict[str, str]) -> list[str]:
    missing = [col for col in REQUIRED_COLUMNS if not row.get(col, "").strip()]
    for col in REQUIRED_ASSET_COLUMNS:
        value = row.get(col, "").strip()
        if value and not asset_exists(value):
            missing.append(f"{col} missing file: {value}")
    missing.extend(gcode_publishable_issues(row))
    return missing


def publishable_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if has_measurement(row) and not missing_required(row)]


def float_value(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def success_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    successful = []
    for row in rows:
        label = row.get("failure_label_primary", "").strip().lower()
        score = float_value(row.get("bottom_fill_score_0_3", ""))
        if label == "complete_fill" or (score is not None and score >= 2.0):
            successful.append(row)
    return successful


def failure_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    failed = []
    for row in rows:
        labels = {
            row.get("failure_label_primary", "").strip().lower(),
            row.get("failure_label_secondary", "").strip().lower(),
        }
        if labels & FAILURE_LABELS:
            failed.append(row)
    return failed


def existing_section_photos(rows: list[dict[str, str]]) -> list[str]:
    paths = []
    for row in rows:
        value = row.get("photo_section", "").strip()
        if value and asset_exists(value):
            paths.append(value)
    return paths


def write_report(results: list[tuple[str, str, str]], measured: list[dict[str, str]], publishable: list[dict[str, str]]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        f.write("# Physical Data Readiness\n\n")
        ready = all(status == "PASS" for status, _, _ in results)
        f.write(f"Submission-strength physical dataset: {'READY' if ready else 'NOT_READY'}\n\n")
        f.write(f"Measured rows: {len(measured)}\n")
        f.write(f"Publishable rows: {len(publishable)}\n\n")
        f.write("| status | check | detail |\n")
        f.write("| --- | --- | --- |\n")
        for status, check, detail in results:
            safe = detail.replace("|", "\\|").replace("\n", " ")
            f.write(f"| {status} | {check} | {safe} |\n")

        incomplete = [(row.get("trial_id", "(missing trial_id)"), missing_required(row)) for row in measured if missing_required(row)]
        if incomplete:
            f.write("\n## Rows Needing Evidence\n\n")
            for trial_id, missing in incomplete:
                f.write(f"- `{trial_id}`: " + ", ".join(missing) + "\n")


def main() -> int:
    results: list[tuple[str, str, str]] = []
    if not INPUT.exists():
        write_report([("WARN", "trial CSV", str(INPUT.relative_to(ROOT)))], [], [])
        print(OUT)
        return 0

    columns, rows = read_rows(INPUT)
    measured = [row for row in rows if has_measurement(row)]
    publishable = publishable_rows(rows)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in columns]
    if missing_columns:
        results.append(("WARN", "schema", "missing columns: " + ", ".join(missing_columns)))
    else:
        results.append(("PASS", "schema", "required submission-readiness columns present."))

    if len(publishable) >= 3:
        results.append(("PASS", "minimum publishable rows", f"{len(publishable)} rows."))
    else:
        results.append(("WARN", "minimum publishable rows", f"{len(publishable)} rows; need at least 3."))

    temps = {row.get("injection_temp_c", "") for row in publishable if row.get("injection_temp_c", "")}
    flows = {row.get("flow_mm3_s", "") for row in publishable if row.get("flow_mm3_s", "")}
    if len(temps) >= 2 and len(flows) >= 2:
        results.append(("PASS", "process-window spread", f"temps={sorted(temps)}, flows={sorted(flows)}"))
    else:
        results.append(("WARN", "process-window spread", f"temps={sorted(temps)}, flows={sorted(flows)}; need at least two of each."))

    successes = success_rows(publishable)
    if successes:
        results.append(("PASS", "successful/candidate fill evidence", ", ".join(row["trial_id"] for row in successes)))
    else:
        results.append(("WARN", "successful/candidate fill evidence", "need one row with complete_fill or bottom_fill_score_0_3 >= 2."))

    failures = failure_rows(publishable)
    if failures:
        results.append(("PASS", "failure-mode contrast", ", ".join(row["trial_id"] for row in failures)))
    else:
        results.append(("WARN", "failure-mode contrast", "need at least one labeled failure-mode row."))

    section_photos = existing_section_photos(publishable)
    if section_photos:
        results.append(("PASS", "section/removed-part evidence", ", ".join(section_photos)))
    else:
        results.append(("WARN", "section/removed-part evidence", "need at least one existing section or removed-part photo."))

    bad_declared_assets = []
    for row in measured:
        for col in ASSET_COLUMNS:
            value = row.get(col, "").strip()
            if value and not asset_exists(value):
                bad_declared_assets.append(f"{row.get('trial_id', '(missing trial_id)')} {col}={value}")
        for issue in gcode_publishable_issues(row):
            bad_declared_assets.append(f"{row.get('trial_id', '(missing trial_id)')} {issue}")
    if bad_declared_assets:
        results.append(("WARN", "declared asset paths", "; ".join(bad_declared_assets)))
    else:
        results.append(("PASS", "declared asset paths", "No declared asset paths are missing."))

    write_report(results, measured, publishable)
    print(OUT)
    for status, check, detail in results:
        print(f"{status}: {check}: {detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
