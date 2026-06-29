#!/usr/bin/env python3
"""Build local submission archives for IEEE PDF eXpress and internal review."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "magma_ieee.tex"
PDF = ROOT / "output" / "pdf" / "magma_ieee_paper.pdf"
OUT_DIR = ROOT / "output" / "submission"
VERIFY_DIR = ROOT / "output" / "verification"
SOURCE_ZIP = OUT_DIR / "magma_ieee_pdf_express_source.zip"
REVIEW_ZIP = OUT_DIR / "magma_ieee_review_bundle.zip"
REPORT = VERIFY_DIR / "submission_package_check.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def tex_graphics() -> list[Path]:
    text = TEX.read_text(errors="replace")
    return [ROOT / "paper" / name for name in re.findall(r"\\includegraphics(?:\[[^]]+\])?\{([^}]+)\}", text)]


def write_zip(path: Path, entries: list[tuple[Path, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for source, archive_name in entries:
            zf.write(source, archive_name)


def write_report(results: list[tuple[str, str, str]]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("w") as f:
        f.write("# Submission Package Check\n\n")
        f.write("| status | check | detail |\n")
        f.write("| --- | --- | --- |\n")
        for status, check, detail in results:
            safe_detail = detail.replace("|", "\\|").replace("\n", " ")
            f.write(f"| {status} | {check} | {safe_detail} |\n")


def main() -> int:
    results: list[tuple[str, str, str]] = []
    errors = 0

    graphics = tex_graphics()
    source_files = [TEX, *graphics]
    missing_source = [rel(path) for path in source_files if not path.exists()]
    if missing_source:
        results.append(("FAIL", "PDF eXpress source inputs", "Missing: " + ", ".join(missing_source)))
        errors += 1
    else:
        source_entries = [(path, str(path.relative_to(ROOT / "paper"))) for path in source_files]
        write_zip(SOURCE_ZIP, source_entries)
        results.append(("PASS", "PDF eXpress source zip", f"{rel(SOURCE_ZIP)} with {len(source_entries)} source file(s)."))

    review_candidates = [
        PDF,
        SOURCE_ZIP,
        ROOT / "paper" / "magma_ieee.tex",
        ROOT / "paper" / "claim_evidence_map.md",
        ROOT / "paper" / "ieee_submission_checklist.md",
        ROOT / "paper" / "submission_readiness.md",
        ROOT / "paper" / "molds" / "README.md",
        ROOT / "paper" / "molds" / "mold_manifest.md",
        ROOT / "paper" / "gcode" / "README.md",
        ROOT / "paper" / "photos" / "README.md",
        VERIFY_DIR / "paper_audit.md",
        VERIFY_DIR / "pdf_production_check.md",
        VERIFY_DIR / "ieee_submission_check.md",
        VERIFY_DIR / "claim_scope_check.md",
        VERIFY_DIR / "claim_evidence_check.md",
        VERIFY_DIR / "transcript_evidence_check.md",
        VERIFY_DIR / "gcode_verification_summary.csv",
        VERIFY_DIR / "fill_trial_plan_summary.md",
        VERIFY_DIR / "fill_trial_assets.md",
        VERIFY_DIR / "fill_trial_summary.csv",
        VERIFY_DIR / "physical_data_readiness.md",
        VERIFY_DIR / "fill_photo_panel_check.md",
        VERIFY_DIR / "trial_execution_readiness.md",
        ROOT / "output" / "trials" / "fill_trial_packet.md",
        ROOT / "output" / "trials" / "evidence_collection_checklist.md",
        ROOT / "output" / "trials" / "minimum_submission_subset.md",
        ROOT / "output" / "trials" / "fill_trials_prefill.csv",
        ROOT / "output" / "trials" / "planned_injection_gcode_summary.md",
        ROOT / "output" / "trials" / "planned_injection_gcode_summary.csv",
        ROOT / "paper" / "fill_trial_plan.csv",
        ROOT / "paper" / "fill_trials_template.csv",
        ROOT / "paper" / "experiment_log_2026-06-27.md",
        ROOT / "paper" / "transcript_evidence_index.md",
    ]
    review_candidates.extend(sorted((ROOT / "paper" / "molds").glob("P*_mold.stl")))
    review_candidates.extend(sorted((ROOT / "paper" / "gcode" / "representative").glob("*.gcode")))
    review_candidates.extend(sorted(path for path in (ROOT / "paper" / "source_evidence").glob("**/*") if path.is_file()))
    review_candidates.extend(sorted((ROOT / "output" / "figures").glob("fill_trial_photo_panel.png")))
    review_candidates.extend(sorted((ROOT / "output" / "trials" / "planned").glob("*.gcode")))
    review_candidates.extend(sorted((ROOT / "output" / "trials" / "run_sheets").glob("P*_run_sheet.md")))
    missing_review = [rel(path) for path in review_candidates if not path.exists()]
    if missing_review:
        results.append(("FAIL", "review bundle inputs", "Missing: " + ", ".join(missing_review)))
        errors += 1
    else:
        review_entries = [(path, rel(path)) for path in review_candidates]
        write_zip(REVIEW_ZIP, review_entries)
        results.append(("PASS", "review bundle", f"{rel(REVIEW_ZIP)} with {len(review_entries)} file(s)."))

    write_report(results)
    print(REPORT)
    for status, check, detail in results:
        print(f"{status}: {check}: {detail}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
