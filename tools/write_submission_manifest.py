#!/usr/bin/env python3
"""Write a reviewer-facing manifest for the Magma paper package."""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "verification" / "submission_manifest.md"
PDF = ROOT / "output" / "pdf" / "magma_ieee_paper.pdf"
AUDIT = ROOT / "output" / "verification" / "paper_audit.md"
PDF_PRODUCTION = ROOT / "output" / "verification" / "pdf_production_check.md"
CLAIM_SCOPE = ROOT / "output" / "verification" / "claim_scope_check.md"
CLAIM_EVIDENCE = ROOT / "paper" / "claim_evidence_map.md"
CLAIM_EVIDENCE_REPORT = ROOT / "output" / "verification" / "claim_evidence_check.md"
IEEE_SUBMISSION_CHECK = ROOT / "output" / "verification" / "ieee_submission_check.md"
SUBMISSION_PACKAGE_REPORT = ROOT / "output" / "verification" / "submission_package_check.md"
PDF_EXPRESS_SOURCE_ZIP = ROOT / "output" / "submission" / "magma_ieee_pdf_express_source.zip"
REVIEW_BUNDLE_ZIP = ROOT / "output" / "submission" / "magma_ieee_review_bundle.zip"
GCODE_CSV = ROOT / "output" / "verification" / "gcode_verification_summary.csv"
FILL_PLAN = ROOT / "paper" / "fill_trial_plan.csv"
FILL_PLAN_SUMMARY = ROOT / "output" / "verification" / "fill_trial_plan_summary.md"
MOLD_MANIFEST = ROOT / "paper" / "molds" / "mold_manifest.md"
FILL_PACKET = ROOT / "output" / "trials" / "fill_trial_packet.md"
FILL_PREFILL = ROOT / "output" / "trials" / "fill_trials_prefill.csv"
TRIAL_EXECUTION_READINESS = ROOT / "output" / "verification" / "trial_execution_readiness.md"
TRIAL_EVIDENCE_CHECKLIST = ROOT / "output" / "trials" / "evidence_collection_checklist.md"
TRIAL_MINIMUM_SUBSET = ROOT / "output" / "trials" / "minimum_submission_subset.md"
PLANNED_GCODE_SUMMARY = ROOT / "output" / "trials" / "planned_injection_gcode_summary.md"
FILL_CSV = ROOT / "output" / "verification" / "fill_trial_summary.csv"
FILL_ASSETS = ROOT / "output" / "verification" / "fill_trial_assets.md"
FILL_TABLE = ROOT / "output" / "verification" / "fill_trial_table.tex"
PHYSICAL_DATA_READINESS = ROOT / "output" / "verification" / "physical_data_readiness.md"
FILL_PHOTO_PANEL_CHECK = ROOT / "output" / "verification" / "fill_photo_panel_check.md"
FILL_PHOTO_PANEL = ROOT / "output" / "figures" / "fill_trial_photo_panel.png"
EXPERIMENT_LOG = ROOT / "paper" / "experiment_log_2026-06-27.md"
TRANSCRIPT_EVIDENCE_INDEX = ROOT / "paper" / "transcript_evidence_index.md"
TRANSCRIPT_EVIDENCE_REPORT = ROOT / "output" / "verification" / "transcript_evidence_check.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def command_output(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT)


def pdf_pages(path: Path) -> str:
    if not path.exists():
        return "missing"
    info = command_output(["pdfinfo", str(path)])
    match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    return match.group(1) if match else "unknown"


def csv_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def audit_counts(path: Path) -> tuple[int, int, int]:
    if not path.exists():
        return 0, 0, 0
    text = path.read_text(errors="replace")
    return text.count("| PASS |"), text.count("| WARN |"), text.count("| FAIL |")


def write() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    passes, warns, fails = audit_counts(AUDIT)
    with OUT.open("w") as f:
        f.write("# Magma Submission Manifest\n\n")
        f.write("## Build\n\n")
        f.write("- Command: `make all`\n")
        f.write(f"- Deliverable PDF: `{rel(PDF)}`\n")
        f.write(f"- PDF pages: {pdf_pages(PDF)}\n")
        f.write(f"- Audit report: `{rel(AUDIT)}`\n")
        f.write(f"- PDF production report: `{rel(PDF_PRODUCTION)}`\n")
        f.write(f"- Claim scope report: `{rel(CLAIM_SCOPE)}`\n")
        f.write(f"- Claim-evidence report: `{rel(CLAIM_EVIDENCE_REPORT)}`\n")
        f.write(f"- IEEE submission readiness report: `{rel(IEEE_SUBMISSION_CHECK)}`\n")
        f.write(f"- Submission package report: `{rel(SUBMISSION_PACKAGE_REPORT)}`\n")
        f.write(f"- Audit status counts: {passes} pass, {warns} warn, {fails} fail\n\n")

        f.write("## Evidence Artifacts\n\n")
        f.write(f"- Manuscript source: `{rel(ROOT / 'paper' / 'magma_ieee.tex')}`\n")
        f.write(f"- Rendered-page contact sheet: `{rel(ROOT / 'tmp' / 'pdfs' / 'magma_ieee_contact_sheet.png')}`\n")
        f.write(f"- G-code verification CSV: `{rel(GCODE_CSV)}` ({csv_count(GCODE_CSV)} rows)\n")
        f.write(f"- Fill trial plan CSV: `{rel(FILL_PLAN)}` ({csv_count(FILL_PLAN)} planned rows)\n")
        f.write(f"- Fill trial plan summary: `{rel(FILL_PLAN_SUMMARY)}`\n")
        f.write(f"- Standard mold manifest: `{rel(MOLD_MANIFEST)}`\n")
        f.write(f"- Planned injection G-code summary: `{rel(PLANNED_GCODE_SUMMARY)}`\n")
        f.write(f"- Fill trial execution packet: `{rel(FILL_PACKET)}`\n")
        f.write(f"- Trial execution readiness report: `{rel(TRIAL_EXECUTION_READINESS)}`\n")
        f.write(f"- Evidence collection checklist: `{rel(TRIAL_EVIDENCE_CHECKLIST)}`\n")
        f.write(f"- Minimum submission-strength subset: `{rel(TRIAL_MINIMUM_SUBSET)}`\n")
        f.write(f"- Fill trial prefilled CSV skeleton: `{rel(FILL_PREFILL)}` ({csv_count(FILL_PREFILL)} planned rows)\n")
        f.write(f"- Fill trial summary CSV: `{rel(FILL_CSV)}` ({csv_count(FILL_CSV)} measured rows)\n")
        f.write(f"- Fill trial asset report: `{rel(FILL_ASSETS)}`\n")
        f.write(f"- Fill trial LaTeX table: `{rel(FILL_TABLE)}`\n")
        f.write(f"- Physical data readiness report: `{rel(PHYSICAL_DATA_READINESS)}`\n")
        f.write(f"- Fill photo panel check: `{rel(FILL_PHOTO_PANEL_CHECK)}`\n")
        if FILL_PHOTO_PANEL.exists():
            f.write(f"- Fill photo panel: `{rel(FILL_PHOTO_PANEL)}`\n")
        f.write(f"- Transcript-backed experiment log: `{rel(EXPERIMENT_LOG)}`\n")
        f.write(f"- Transcript evidence index: `{rel(TRANSCRIPT_EVIDENCE_INDEX)}`\n")
        f.write(f"- Transcript evidence check: `{rel(TRANSCRIPT_EVIDENCE_REPORT)}`\n")
        f.write(f"- Claim-evidence map: `{rel(CLAIM_EVIDENCE)}`\n")
        f.write(f"- IEEE submission checklist: `{rel(ROOT / 'paper' / 'ieee_submission_checklist.md')}`\n")
        f.write(f"- PDF eXpress source archive: `{rel(PDF_EXPRESS_SOURCE_ZIP)}`\n")
        f.write(f"- Local review bundle: `{rel(REVIEW_BUNDLE_ZIP)}`\n")
        f.write(f"- Reviewer risk matrix: `{rel(ROOT / 'paper' / 'reviewer_risk_matrix.md')}`\n")
        f.write("- Native slicer source evidence snapshots:\n")
        f.write("  - `paper/source_evidence/LavaSlicer/src/libslic3r/GCode.cpp`\n")
        f.write("  - `paper/source_evidence/LavaSlicer/src/libslic3r/PrintObjectSlice.cpp`\n")
        f.write("  - `paper/source_evidence/PrusaSlicer/src/libslic3r/PrintConfig.hpp`\n")
        f.write("  - `paper/source_evidence/PrusaSlicer/src/libslic3r/GCode.cpp`\n\n")

        f.write("## Submission Caveat\n\n")
        f.write(
            "The package currently verifies the manuscript, source-code evidence, and generated "
            "G-code artifacts. It does not yet contain measured fill-trial rows or publication-ready "
            "physical-result photos, which remain the acceptance-critical gap for a manufacturing-results submission.\n"
        )


if __name__ == "__main__":
    write()
    print(OUT)
