#!/usr/bin/env python3
"""Summarize measured Magma fill trials for the paper package.

The template may exist before any publishable measurements do. In that case the
script still emits a summary so the audit can distinguish "pipeline ready" from
"physical data collected".
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_COLUMNS = [
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

MEASUREMENT_COLUMNS = [
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
    "photo_top",
    "photo_side",
    "photo_section",
]

SUMMARY_COLUMNS = [
    "trial_id",
    "geometry",
    "injection_temp_c",
    "flow_mm3_s",
    "commanded_volume_mm3",
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
    "photo_top",
    "photo_side",
    "photo_section",
]

PUBLISHABLE_COLUMNS = [
    "trial_id",
    "date",
    "printer",
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

LATEX_COLUMNS = [
    "trial_id",
    "injection_temp_c",
    "flow_mm3_s",
    "commanded_volume_mm3",
    "estimated_delivered_volume_mm3",
    "visible_fill_depth_mm",
    "bottom_fill_score_0_3",
    "failure_label_primary",
]

ASSET_COLUMNS = [
    "mold_file",
    "gcode_file",
    "photo_top",
    "photo_side",
    "photo_section",
]

REQUIRED_PUBLISHABLE_ASSET_COLUMNS = [
    "mold_file",
    "gcode_file",
    "photo_top",
]

PLANNED_GCODE_MARKERS = [
    "NOT EXECUTED EVIDENCE",
    "MAGMA PLANNED INJECTION BLOCK",
    "not a complete printable job",
]


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
        return list(reader.fieldnames or []), rows


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    normalized = dict(row)
    before = parse_float(normalized.get("mass_before_g", ""))
    after = parse_float(normalized.get("mass_after_g", ""))
    if not normalized.get("delivered_mass_g") and before is not None and after is not None:
        normalized["delivered_mass_g"] = f"{after - before:.4g}"

    delivered_mass = parse_float(normalized.get("delivered_mass_g", ""))
    density = parse_float(normalized.get("injection_density_g_cm3", ""))
    if not normalized.get("estimated_delivered_volume_mm3") and delivered_mass is not None and density and density > 0:
        normalized["estimated_delivered_volume_mm3"] = f"{(delivered_mass / density) * 1000.0:.4g}"
    return normalized


def has_measurement(row: dict[str, str]) -> bool:
    return any(row.get(col, "").strip() for col in MEASUREMENT_COLUMNS)


def measured_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [normalize_row(row) for row in rows if row.get("trial_id", "").strip() and has_measurement(row)]


def missing_publishable_columns(row: dict[str, str]) -> list[str]:
    return [col for col in PUBLISHABLE_COLUMNS if not row.get(col, "").strip()]


def resolve_asset_path(value: str, root: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def asset_path_exists(value: str, root: Path) -> bool:
    if not value.strip():
        return True
    return resolve_asset_path(value, root).is_file()


def missing_declared_asset_paths(row: dict[str, str], root: Path) -> list[str]:
    missing: list[str] = []
    for col in ASSET_COLUMNS:
        value = row.get(col, "").strip()
        if value and not asset_path_exists(value, root):
            missing.append(f"{col}={value}")
    return missing


def missing_publishable_asset_paths(row: dict[str, str], root: Path) -> list[str]:
    missing: list[str] = []
    for col in REQUIRED_PUBLISHABLE_ASSET_COLUMNS:
        value = row.get(col, "").strip()
        if value and not asset_path_exists(value, root):
            missing.append(f"{col}={value}")
    return missing


def gcode_publishable_issues(row: dict[str, str], root: Path) -> list[str]:
    value = row.get("gcode_file", "").strip()
    if not value:
        return []

    issues: list[str] = []
    path = resolve_asset_path(value, root)
    try:
        relative = path.relative_to(root)
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


def missing_publishable_requirements(row: dict[str, str], root: Path) -> list[str]:
    missing = missing_publishable_columns(row)
    missing.extend(missing_publishable_asset_paths(row, root))
    missing.extend(gcode_publishable_issues(row, root))
    return missing


def publishable_rows(rows: list[dict[str, str]], root: Path = ROOT) -> list[dict[str, str]]:
    return [row for row in rows if not missing_publishable_requirements(row, root)]


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in SUMMARY_COLUMNS})


def write_markdown(rows: list[dict[str, str]], missing_columns: list[str], path: Path, root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        f.write("# Fill Trial Summary\n\n")
        if missing_columns:
            f.write("Schema status: missing columns: " + ", ".join(missing_columns) + "\n\n")
        else:
            f.write("Schema status: expected columns present.\n\n")

        ready = publishable_rows(rows, root)
        f.write(f"Publishable rows: {len(ready)}\n\n")

        if not rows:
            f.write("Measured trials: 0\n\n")
            f.write(
                "No measured fill-trial rows are present yet. Populate "
                "`paper/fill_trials_template.csv` with mass, fill-depth, failure-label, "
                "and photo evidence, then rerun `make fill-summary`.\n"
            )
            return

        f.write(f"Measured trials: {len(rows)}\n\n")
        headers = [
            "trial_id",
            "injection_temp_c",
            "flow_mm3_s",
            "commanded_volume_mm3",
            "delivered_mass_g",
            "visible_fill_depth_mm",
            "bottom_fill_score_0_3",
            "failure_label_primary",
        ]
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for row in rows:
            f.write("| " + " | ".join(row.get(h, "") for h in headers) + " |\n")
        incomplete = [
            (row.get("trial_id", "(missing trial_id)"), missing_publishable_requirements(row, root))
            for row in rows
            if missing_publishable_requirements(row, root)
        ]
        if incomplete:
            f.write("\n## Rows Needing More Evidence\n\n")
            for trial_id, missing in incomplete:
                f.write(f"- `{trial_id}`: " + ", ".join(missing) + "\n")


def write_asset_report(rows: list[dict[str, str]], path: Path, root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    missing_declared = [
        (row.get("trial_id", "(missing trial_id)"), missing_declared_asset_paths(row, root))
        for row in rows
        if missing_declared_asset_paths(row, root)
    ]
    missing_publishable = [
        (row.get("trial_id", "(missing trial_id)"), missing_publishable_requirements(row, root))
        for row in rows
        if missing_publishable_requirements(row, root)
    ]

    with path.open("w") as f:
        f.write("# Fill Trial Asset Check\n\n")
        f.write("Paths are resolved relative to the repository root unless absolute paths are supplied.\n\n")
        f.write(f"Measured trials: {len(rows)}\n")
        f.write(f"Missing declared assets: {sum(len(items) for _, items in missing_declared)}\n")
        f.write(f"Publishable rows: {len(publishable_rows(rows, root))}\n\n")

        if not rows:
            f.write("No measured fill-trial rows are present yet; no asset paths were checked.\n")
            return

        f.write("## Asset Status\n\n")
        f.write("| trial_id | asset | path | status |\n")
        f.write("| --- | --- | --- | --- |\n")
        for row in rows:
            trial_id = row.get("trial_id", "(missing trial_id)")
            for col in ASSET_COLUMNS:
                value = row.get(col, "").strip()
                if not value:
                    status = "required for publishable row" if col in REQUIRED_PUBLISHABLE_ASSET_COLUMNS else "not declared"
                    f.write(f"| {trial_id} | {col} |  | {status} |\n")
                    continue
                status = "exists" if asset_path_exists(value, root) else "missing"
                f.write(f"| {trial_id} | {col} | `{value}` | {status} |\n")

        if missing_declared:
            f.write("\n## Missing Declared Assets\n\n")
            for trial_id, missing in missing_declared:
                f.write(f"- `{trial_id}`: " + ", ".join(missing) + "\n")

        if missing_publishable:
            f.write("\n## Publishable-Row Requirements Not Met\n\n")
            for trial_id, missing in missing_publishable:
                f.write(f"- `{trial_id}`: " + ", ".join(missing) + "\n")


def escape_latex(value: str) -> str:
    return (
        value.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("~", r"\textasciitilde{}")
        .replace("^", r"\textasciicircum{}")
    )


def write_latex_table(rows: list[dict[str, str]], path: Path) -> None:
    ready = publishable_rows(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write("% Auto-generated by tools/summarize_fill_trials.py\n")
        if not ready:
            f.write("% No publishable measured fill-trial rows are present yet.\n")
            return

        f.write("\\begin{table}[t]\n")
        f.write("\\caption{Measured Fill Trials}\n")
        f.write("\\label{tab:fillresults}\n")
        f.write("\\centering\n")
        f.write("\\scriptsize\n")
        f.write("\\setlength{\\tabcolsep}{2.0pt}\n")
        f.write("\\begin{tabular}{@{}llllllll@{}}\n")
        f.write("\\toprule\n")
        f.write("Trial & Temp. & Flow & Cmd. vol. & Deliv. vol. & Fill depth & Bottom & Label \\\\\n")
        f.write("\\midrule\n")
        for row in ready:
            values = [escape_latex(row.get(col, "")) for col in LATEX_COLUMNS]
            f.write(" & ".join(values) + " \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("paper/fill_trials_template.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("output/verification"))
    args = parser.parse_args()

    input_path = args.input.resolve()
    out_dir = args.out_dir.resolve()
    columns, rows = read_rows(input_path)
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in columns]
    measured = measured_rows(rows)

    csv_path = out_dir / "fill_trial_summary.csv"
    md_path = out_dir / "fill_trial_summary.md"
    tex_path = out_dir / "fill_trial_table.tex"
    asset_path = out_dir / "fill_trial_assets.md"
    write_csv(measured, csv_path)
    write_markdown(measured, missing_columns, md_path, ROOT)
    write_asset_report(measured, asset_path, ROOT)
    write_latex_table(measured, tex_path)
    print(csv_path)
    print(md_path)
    print(asset_path)
    print(tex_path)
    print(f"measured_trials={len(measured)}")
    print(f"publishable_trials={len(publishable_rows(measured, ROOT))}")
    missing_declared_count = sum(len(missing_declared_asset_paths(row, ROOT)) for row in measured)
    print(f"missing_declared_assets={missing_declared_count}")
    if missing_columns:
        print("missing_columns=" + ",".join(missing_columns))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
