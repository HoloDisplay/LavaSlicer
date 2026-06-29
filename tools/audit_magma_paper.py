#!/usr/bin/env python3
"""Audit the Magma IEEE paper package for submission-facing issues."""

from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX_PATH = ROOT / "paper" / "magma_ieee.tex"
PDF_PATH = ROOT / "paper" / "magma_ieee.pdf"
OUTPUT_PDFS = [
    ROOT / "output" / "pdf" / "magma_ieee_paper.pdf",
    ROOT / "output" / "tex" / "magma_ieee.pdf",
]
VERIFY_CSV = ROOT / "output" / "verification" / "gcode_verification_summary.csv"
FILL_TRIAL_CSV = ROOT / "paper" / "fill_trials_template.csv"
FILL_PLAN_CSV = ROOT / "paper" / "fill_trial_plan.csv"
FILL_PLAN_SUMMARY_MD = ROOT / "output" / "verification" / "fill_trial_plan_summary.md"
FILL_TRIAL_PACKET_MD = ROOT / "output" / "trials" / "fill_trial_packet.md"
FILL_TRIAL_PREFILL_CSV = ROOT / "output" / "trials" / "fill_trials_prefill.csv"
FILL_TRIAL_RUN_SHEET_DIR = ROOT / "output" / "trials" / "run_sheets"
TRIAL_EXECUTION_READINESS_REPORT = ROOT / "output" / "verification" / "trial_execution_readiness.md"
TRIAL_EVIDENCE_CHECKLIST = ROOT / "output" / "trials" / "evidence_collection_checklist.md"
TRIAL_MINIMUM_SUBSET = ROOT / "output" / "trials" / "minimum_submission_subset.md"
PLANNED_GCODE_SUMMARY_CSV = ROOT / "output" / "trials" / "planned_injection_gcode_summary.csv"
PLANNED_GCODE_SUMMARY_MD = ROOT / "output" / "trials" / "planned_injection_gcode_summary.md"
MOLD_MANIFEST_MD = ROOT / "paper" / "molds" / "mold_manifest.md"
FILL_SUMMARY_MD = ROOT / "output" / "verification" / "fill_trial_summary.md"
FILL_ASSET_REPORT = ROOT / "output" / "verification" / "fill_trial_assets.md"
FILL_TABLE_TEX = ROOT / "output" / "verification" / "fill_trial_table.tex"
PHYSICAL_DATA_READINESS_REPORT = ROOT / "output" / "verification" / "physical_data_readiness.md"
FILL_PHOTO_PANEL_REPORT = ROOT / "output" / "verification" / "fill_photo_panel_check.md"
EXPERIMENT_LOG = ROOT / "paper" / "experiment_log_2026-06-27.md"
TRANSCRIPT_EVIDENCE_INDEX = ROOT / "paper" / "transcript_evidence_index.md"
TRANSCRIPT_EVIDENCE_REPORT = ROOT / "output" / "verification" / "transcript_evidence_check.md"
PDF_PRODUCTION_REPORT = ROOT / "output" / "verification" / "pdf_production_check.md"
CLAIM_SCOPE_REPORT = ROOT / "output" / "verification" / "claim_scope_check.md"
CLAIM_EVIDENCE_MAP = ROOT / "paper" / "claim_evidence_map.md"
CLAIM_EVIDENCE_REPORT = ROOT / "output" / "verification" / "claim_evidence_check.md"
IEEE_SUBMISSION_REPORT = ROOT / "output" / "verification" / "ieee_submission_check.md"
REPORT_PATH = ROOT / "output" / "verification" / "paper_audit.md"
RENDER_GLOB = "magma_ieee_page-*.png"
SOURCE_EVIDENCE = [
    (
        "LavaSlicer G-code emission",
        ROOT / "paper" / "source_evidence" / "LavaSlicer" / "src" / "libslic3r" / "GCode.cpp",
        ["LAVASLICER INJECTION", "inject_mode", "inject_tool"],
    ),
    (
        "LavaSlicer volume suppression",
        ROOT / "paper" / "source_evidence" / "LavaSlicer" / "src" / "libslic3r" / "PrintObjectSlice.cpp",
        ["lavaslicer_is_injection_only_object", "inject_object_name", "slice_volumes"],
    ),
    (
        "PrusaSlicer injection-pour config",
        ROOT / "paper" / "source_evidence" / "PrusaSlicer" / "src" / "libslic3r" / "PrintConfig.hpp",
        ["injection_pour_enabled", "injection_pour_end_z", "injection_pour_flow"],
    ),
    (
        "PrusaSlicer injection-pour emission",
        ROOT / "paper" / "source_evidence" / "PrusaSlicer" / "src" / "libslic3r" / "GCode.cpp",
        ["InjectionPourModelTarget", ";TYPE:Injection pour", "injection_pour_model_target"],
    ),
]
PUBLISHABLE_TRIAL_COLUMNS = [
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
FILL_PLAN_REQUIRED_TEMPS = {"240", "255", "275"}
FILL_PLAN_REQUIRED_FLOWS = {"10", "20", "30"}


def add(result: list[tuple[str, str, str]], status: str, check: str, detail: str) -> None:
    result.append((status, check, detail))


def command_output(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT)


def unique(items: list[str]) -> list[str]:
    return sorted(set(items))


def strip_tex_commands(text: str) -> str:
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^]]*\])?(?:\{([^{}]*)\})?", r" \1 ", text)
    text = re.sub(r"\\.", " ", text)
    return text


def word_count_tex(text: str) -> int:
    plain = strip_tex_commands(text)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", plain))


def extract_required_env(tex: str, env: str) -> str:
    match = re.search(rf"\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}", tex, re.DOTALL)
    if not match:
        raise ValueError(f"Missing {env} environment")
    return match.group(1).strip()


def parse_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows: list[dict[str, str]] = []
        for row in csv.DictReader(f):
            rows.append({k: (v or "").strip() for k, v in row.items() if k is not None})
        return rows


def write_report(results: list[tuple[str, str, str]]) -> None:
    write_table_report(REPORT_PATH, "Magma Paper Audit", results)


def write_table_report(path: Path, title: str, results: list[tuple[str, str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(f"# {title}\n\n")
        f.write("| status | check | detail |\n")
        f.write("| --- | --- | --- |\n")
        for status, check, detail in results:
            safe_detail = detail.replace("|", "\\|").replace("\n", " ")
            f.write(f"| {status} | {check} | {safe_detail} |\n")


def numeric_value_present_in_tex(value: str, tex: str) -> bool:
    """Accept both CSV-style and paper-style numeric formatting."""
    if not value:
        return True
    candidates = {value}
    try:
        candidates.add(f"{float(value):g}")
    except ValueError:
        pass
    return any(candidate in tex for candidate in candidates)


def row_has_measurement(row: dict[str, str]) -> bool:
    measurement_columns = [
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
    return any(row.get(col, "").strip() for col in measurement_columns)


def resolve_asset_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def asset_path_exists(value: str) -> bool:
    if not value.strip():
        return True
    return resolve_asset_path(value).is_file()


def missing_required_publishable_assets(row: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for col in REQUIRED_PUBLISHABLE_ASSET_COLUMNS:
        value = row.get(col, "").strip()
        if value and not asset_path_exists(value):
            missing.append(f"{col}={value}")
    missing.extend(gcode_publishable_issues(row))
    return missing


def gcode_publishable_issues(row: dict[str, str]) -> list[str]:
    value = row.get("gcode_file", "").strip()
    if not value:
        return []

    issues: list[str] = []
    path = resolve_asset_path(value)
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


def row_is_publishable_text_complete(row: dict[str, str]) -> bool:
    return all(row.get(col, "").strip() for col in PUBLISHABLE_TRIAL_COLUMNS)


def row_is_publishable(row: dict[str, str]) -> bool:
    return row_is_publishable_text_complete(row) and not missing_required_publishable_assets(row)


def fill_plan_coverage(rows: list[dict[str, str]]) -> tuple[bool, str]:
    core = [row for row in rows if row.get("priority") == "core"]
    combos = {(row.get("injection_temp_c", ""), row.get("flow_mm3_s", "")) for row in core}
    expected = {(temp, flow) for temp in FILL_PLAN_REQUIRED_TEMPS for flow in FILL_PLAN_REQUIRED_FLOWS}
    missing = sorted(expected - combos)
    sectioned = [row.get("plan_id", "") for row in rows if row.get("photo_section_required", "").lower() == "yes"]
    ok = len(core) >= 9 and not missing and len(sectioned) >= 2
    return ok, f"core_rows={len(core)}, missing_combos={missing}, section_required={sectioned}"


def pdfinfo_map(path: Path) -> dict[str, str]:
    info: dict[str, str] = {}
    for line in command_output(["pdfinfo", str(path)]).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        info[key.strip()] = value.strip()
    return info


def pdffonts_rows(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in command_output(["pdffonts", str(path)]).splitlines():
        if not line or line.startswith("name ") or line.startswith("---"):
            continue
        parts = line.split()
        if len(parts) < 9:
            continue
        rows.append({
            "name": parts[0],
            "embedded": parts[-5],
            "subset": parts[-4],
            "unicode": parts[-3],
        })
    return rows


def pdf_embedded_file_count(path: Path) -> int | None:
    try:
        output = command_output(["pdfdetach", "-list", str(path)])
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    match = re.search(r"(\d+)\s+embedded files?", output)
    return int(match.group(1)) if match else None


def check_pdf_production(path: Path) -> tuple[list[tuple[str, str, str]], int]:
    results: list[tuple[str, str, str]] = []
    errors = 0
    if not path.exists():
        add(results, "FAIL", "PDF production input", str(path.relative_to(ROOT)))
        return results, 1

    info = pdfinfo_map(path)
    page_size = info.get("Page size", "")
    if "612 x 792 pts" in page_size and "letter" in page_size.lower():
        add(results, "PASS", "PDF page size", page_size)
    else:
        add(results, "FAIL", "PDF page size", page_size or "missing")
        errors += 1

    version = info.get("PDF version", "")
    try:
        version_value = float(version)
    except ValueError:
        version_value = 0.0
    if 1.4 <= version_value <= 1.7:
        add(results, "PASS", "PDF version", version)
    else:
        add(results, "FAIL", "PDF version", version or "missing")
        errors += 1

    if info.get("Encrypted", "").lower() == "no":
        add(results, "PASS", "PDF encryption", "not encrypted")
    else:
        add(results, "FAIL", "PDF encryption", info.get("Encrypted", "missing"))
        errors += 1

    if info.get("JavaScript", "").lower() == "no":
        add(results, "PASS", "PDF JavaScript", "none")
    else:
        add(results, "FAIL", "PDF JavaScript", info.get("JavaScript", "missing"))
        errors += 1

    if info.get("Form", "").lower() == "none":
        add(results, "PASS", "PDF forms", "none")
    else:
        add(results, "FAIL", "PDF forms", info.get("Form", "missing"))
        errors += 1

    fonts = pdffonts_rows(path)
    unembedded = [font["name"] for font in fonts if font["embedded"] != "yes"]
    unsubsets = [font["name"] for font in fonts if font["subset"] != "yes"]
    if fonts and not unembedded and not unsubsets:
        add(results, "PASS", "PDF fonts", f"{len(fonts)} fonts embedded and subset.")
    else:
        add(results, "FAIL", "PDF fonts", f"fonts={len(fonts)}, unembedded={unembedded}, unsubsets={unsubsets}")
        errors += 1

    embedded_count = pdf_embedded_file_count(path)
    if embedded_count == 0:
        add(results, "PASS", "PDF embedded files", "0 embedded files")
    elif embedded_count is None:
        raw = path.read_bytes()
        if b"/EmbeddedFiles" in raw or b"/Filespec" in raw:
            add(results, "FAIL", "PDF embedded files", "Embedded-file marker found in PDF bytes.")
            errors += 1
        else:
            add(results, "PASS", "PDF embedded files", "No embedded-file markers found.")
    else:
        add(results, "FAIL", "PDF embedded files", f"{embedded_count} embedded files")
        errors += 1

    raw = path.read_bytes()
    risky_tokens = [token for token in [b"/Launch", b"/OpenAction", b"/AcroForm", b"/JavaScript", b"/Encrypt"] if token in raw]
    if risky_tokens:
        add(results, "FAIL", "PDF risky object tokens", ", ".join(token.decode("ascii") for token in risky_tokens))
        errors += 1
    else:
        add(results, "PASS", "PDF risky object tokens", "No launch, open-action, form, JavaScript, or encryption tokens found.")

    structural_tokens = [token for token in [b"/Annots", b"/URI", b"/Outlines", b"/Collection"] if token in raw]
    if structural_tokens:
        add(results, "FAIL", "PDF links/bookmarks/packages", ", ".join(token.decode("ascii") for token in structural_tokens))
        errors += 1
    else:
        add(results, "PASS", "PDF links/bookmarks/packages", "No annotation, URI, outline, or collection markers found.")

    return results, errors


def main() -> int:
    results: list[tuple[str, str, str]] = []
    errors = 0

    tex = TEX_PATH.read_text(errors="replace")

    direct_non_ascii = sorted({ch for ch in tex if ord(ch) > 127})
    if direct_non_ascii:
        add(results, "FAIL", "ASCII TeX source", f"Non-ASCII characters present: {direct_non_ascii}")
        errors += 1
    else:
        add(results, "PASS", "ASCII TeX source", "No direct non-ASCII characters in manuscript source.")

    forbidden = ["TODO", "TBD", "PLACEHOLDER", "???", "FIXME"]
    found_forbidden = [token for token in forbidden if token in tex.upper()]
    if found_forbidden:
        add(results, "FAIL", "Placeholder scan", ", ".join(found_forbidden))
        errors += 1
    else:
        add(results, "PASS", "Placeholder scan", "No TODO/TBD/FIXME-style tokens found.")

    if "\\documentclass[conference]{IEEEtran}" in tex:
        add(results, "PASS", "IEEEtran conference mode", "Uses IEEEtran conference document class.")
    else:
        add(results, "FAIL", "IEEEtran conference mode", "Expected \\documentclass[conference]{IEEEtran}.")
        errors += 1

    title_match = re.search(r"\\title\{([^}]*)\}", tex)
    if title_match:
        title_source = title_match.group(1).replace("\\magma", "Magma")
        lowercase_long_preps = [
            word for word in ["about", "above", "after", "among", "below", "between", "from", "into", "through", "under", "without"]
            if re.search(rf"\b{word}\b", title_source)
        ]
        if lowercase_long_preps:
            add(results, "FAIL", "IEEE title capitalization", f"Lowercase long title words: {lowercase_long_preps}")
            errors += 1
        else:
            add(results, "PASS", "IEEE title capitalization", "No lowercase long title prepositions found.")
    else:
        add(results, "FAIL", "Title present", "No \\title found.")
        errors += 1

    try:
        abstract = extract_required_env(tex, "abstract")
        abstract_words = word_count_tex(abstract)
        abstract_paragraphs = [p for p in re.split(r"\n\s*\n", abstract) if p.strip()]
        abstract_has_cites = "\\cite" in abstract
        abstract_has_display_math = "\\begin{equation" in abstract or "$$" in abstract
        if 150 <= abstract_words <= 250 and len(abstract_paragraphs) == 1 and not abstract_has_cites and not abstract_has_display_math:
            add(results, "PASS", "IEEE abstract shape", f"{abstract_words} words, one paragraph, no citations or display math.")
        else:
            detail = (
                f"{abstract_words} words, paragraphs={len(abstract_paragraphs)}, "
                f"citations={abstract_has_cites}, display_math={abstract_has_display_math}"
            )
            add(results, "FAIL", "IEEE abstract shape", detail)
            errors += 1
    except ValueError as exc:
        add(results, "FAIL", "IEEE abstract shape", str(exc))
        errors += 1

    try:
        keywords = extract_required_env(tex, "IEEEkeywords")
        keyword_items = [item.strip() for item in strip_tex_commands(keywords).split(",") if item.strip()]
        keyword_ordered = keyword_items == sorted(keyword_items, key=str.lower)
        if 3 <= len(keyword_items) <= 10 and keyword_ordered:
            add(results, "PASS", "IEEE keywords", f"{len(keyword_items)} alphabetized keywords.")
        else:
            add(results, "FAIL", "IEEE keywords", f"count={len(keyword_items)}, alphabetized={keyword_ordered}: {keyword_items}")
            errors += 1
    except ValueError as exc:
        add(results, "FAIL", "IEEE keywords", str(exc))
        errors += 1

    cite_keys: list[str] = []
    for cite_body in re.findall(r"\\cite\{([^}]+)\}", tex):
        cite_keys.extend(k.strip() for k in cite_body.split(",") if k.strip())
    bib_keys = re.findall(r"\\bibitem\{([^}]+)\}", tex)
    missing_bibs = sorted(set(cite_keys) - set(bib_keys))
    unused_bibs = sorted(set(bib_keys) - set(cite_keys))
    if missing_bibs:
        add(results, "FAIL", "Citation coverage", f"Missing bibitems: {missing_bibs}")
        errors += 1
    else:
        add(results, "PASS", "Citation coverage", f"{len(unique(cite_keys))} cited keys resolved.")
    if unused_bibs:
        add(results, "WARN", "Unused bibliography entries", str(unused_bibs))
    else:
        add(results, "PASS", "Unused bibliography entries", "Every bibitem is cited.")

    labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
    refs = set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", tex))
    missing_labels = sorted(refs - labels)
    if missing_labels:
        add(results, "FAIL", "Reference coverage", f"Missing labels: {missing_labels}")
        errors += 1
    else:
        add(results, "PASS", "Reference coverage", f"{len(refs)} refs resolved.")

    missing_figures: list[str] = []
    for fig in re.findall(r"\\includegraphics(?:\[[^]]+\])?\{([^}]+)\}", tex):
        fig_path = ROOT / "paper" / fig
        if not fig_path.exists():
            missing_figures.append(str(fig_path.relative_to(ROOT)))
    if missing_figures:
        add(results, "FAIL", "Figure files", f"Missing: {missing_figures}")
        errors += 1
    else:
        add(results, "PASS", "Figure files", "All includegraphics targets exist.")

    required_sections = [
        "Introduction",
        "Related Work and Gap",
        "Process Model",
        "Role-Based CAD and Slicer Semantics",
        "Software Implementation",
        "G-code Verification",
        "Experimental Method",
        "Preliminary Observations",
        "Validation Plan",
        "Reproducibility and Threats to Validity",
        "Discussion",
        "Conclusion",
    ]
    missing_sections = [section for section in required_sections if f"\\section{{{section}}}" not in tex]
    if missing_sections:
        add(results, "FAIL", "Required sections", f"Missing: {missing_sections}")
        errors += 1
    else:
        add(results, "PASS", "Required sections", f"{len(required_sections)} expected sections present.")

    novelty_terms = [
        "the mold is typically transferred to a separate injection machine",
        "keeps the printed mold on the printer build plate",
        "not printed tooling by itself",
        "missing CAD role model",
        "suppress the injected body from ordinary slicing",
        "bounded low-pressure injection operation",
    ]
    missing_novelty_terms = [term for term in novelty_terms if term not in tex]
    if missing_novelty_terms:
        add(results, "FAIL", "Novelty versus rapid tooling", f"Missing: {missing_novelty_terms}")
        errors += 1
    else:
        add(results, "PASS", "Novelty versus rapid tooling", "Prior-work distinction is explicit and scoped.")

    reproducibility_terms = [
        "The submission package is organized",
        "G-code verification table",
        "fill-trial asset report",
        "existing executed G-code and photo evidence",
        "not counted as publishable",
    ]
    missing_reproducibility_terms = [term for term in reproducibility_terms if term not in tex]
    if missing_reproducibility_terms:
        add(results, "FAIL", "Reproducibility and validity language", f"Missing: {missing_reproducibility_terms}")
        errors += 1
    else:
        add(results, "PASS", "Reproducibility and validity language", "Claim classes and physical-data requirements are explicit.")

    if PDF_PATH.exists():
        info = command_output(["pdfinfo", str(PDF_PATH)])
        page_match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
        pages = int(page_match.group(1)) if page_match else -1
        if 1 <= pages <= 6:
            add(results, "PASS", "PDF page count", f"{pages} pages.")
        else:
            add(results, "FAIL", "PDF page count", f"Unexpected page count: {pages}")
            errors += 1
    else:
        add(results, "FAIL", "PDF exists", str(PDF_PATH.relative_to(ROOT)))
        errors += 1

    missing_outputs = [str(p.relative_to(ROOT)) for p in OUTPUT_PDFS if not p.exists()]
    if missing_outputs:
        add(results, "FAIL", "Output PDFs", f"Missing: {missing_outputs}")
        errors += 1
    else:
        add(results, "PASS", "Output PDFs", "PDF copies exist under output/pdf and output/tex.")

    rendered_pages = sorted((ROOT / "tmp" / "pdfs").glob(RENDER_GLOB))
    if len(rendered_pages) >= 1:
        add(results, "PASS", "Rendered page PNGs", f"{len(rendered_pages)} rendered pages in tmp/pdfs.")
    else:
        add(results, "FAIL", "Rendered page PNGs", "No rendered pages found.")
        errors += 1

    if VERIFY_CSV.exists():
        rows = parse_csv_rows(VERIFY_CSV)
        artifacts = [r["artifact"] for r in rows]
        missing_artifacts = [artifact for artifact in artifacts if artifact not in tex]
        if len(rows) >= 5 and not missing_artifacts:
            add(results, "PASS", "G-code verification table backing", f"{len(rows)} verifier rows; all artifact names appear in manuscript.")
        else:
            add(results, "FAIL", "G-code verification table backing", f"Rows={len(rows)}, missing in TeX={missing_artifacts}")
            errors += 1
        flow_values = [r["flow_mm3_s"] for r in rows]
        missing_flows = [v for v in flow_values if not numeric_value_present_in_tex(v, tex)]
        if missing_flows:
            add(results, "WARN", "Verifier flow values in TeX", f"Missing exact strings: {missing_flows}")
        else:
            add(results, "PASS", "Verifier flow values in TeX", "All exact flow values appear in manuscript.")
    else:
        add(results, "FAIL", "G-code verification CSV", str(VERIFY_CSV.relative_to(ROOT)))
        errors += 1

    missing_source: list[str] = []
    for name, path, tokens in SOURCE_EVIDENCE:
        if not path.exists():
            missing_source.append(f"{name}: missing {path.relative_to(ROOT)}")
            continue
        text = path.read_text(errors="replace")
        missing_tokens = [token for token in tokens if token not in text]
        if missing_tokens:
            missing_source.append(f"{name}: missing tokens {missing_tokens}")
    if missing_source:
        add(results, "FAIL", "Native slicer source evidence", "; ".join(missing_source))
        errors += 1
    else:
        add(results, "PASS", "Native slicer source evidence", f"{len(SOURCE_EVIDENCE)} source checks passed.")

    if EXPERIMENT_LOG.exists():
        log_text = EXPERIMENT_LOG.read_text(errors="replace")
        required_log_terms = [
            "2026-06-27",
            "paper/transcript_evidence_index.md",
            "10 mm",
            "0.8 mm",
            "PETG",
            "PLA",
            "too fast",
            "collision",
            "does not prove complete cavity fill",
        ]
        missing_log_terms = [term for term in required_log_terms if term not in log_text]
        if missing_log_terms:
            add(results, "FAIL", "Transcript-backed experiment log", f"Missing terms: {missing_log_terms}")
            errors += 1
        else:
            add(results, "PASS", "Transcript-backed experiment log", str(EXPERIMENT_LOG.relative_to(ROOT)))
    else:
        add(results, "FAIL", "Transcript-backed experiment log", str(EXPERIMENT_LOG.relative_to(ROOT)))
        errors += 1

    if TRANSCRIPT_EVIDENCE_INDEX.exists() and TRANSCRIPT_EVIDENCE_REPORT.exists():
        report_text = TRANSCRIPT_EVIDENCE_REPORT.read_text(errors="replace")
        if "| FAIL |" in report_text:
            add(results, "FAIL", "Transcript evidence index", str(TRANSCRIPT_EVIDENCE_REPORT.relative_to(ROOT)))
            errors += 1
        else:
            add(results, "PASS", "Transcript evidence index", str(TRANSCRIPT_EVIDENCE_INDEX.relative_to(ROOT)))
    else:
        missing_transcript_evidence = [
            str(path.relative_to(ROOT))
            for path in [TRANSCRIPT_EVIDENCE_INDEX, TRANSCRIPT_EVIDENCE_REPORT]
            if not path.exists()
        ]
        add(results, "FAIL", "Transcript evidence index", "Missing: " + ", ".join(missing_transcript_evidence))
        errors += 1

    if FILL_TRIAL_CSV.exists():
        trial_rows = parse_csv_rows(FILL_TRIAL_CSV)
        measured_rows = [row for row in trial_rows if row.get("trial_id", "").strip() and row_has_measurement(row)]
        publishable_rows = [row for row in measured_rows if row_is_publishable(row)]
        text_complete_missing_assets = [
            f"{row.get('trial_id', '(missing trial_id)')}: {', '.join(missing_required_publishable_assets(row))}"
            for row in measured_rows
            if row_is_publishable_text_complete(row) and missing_required_publishable_assets(row)
        ]
        if text_complete_missing_assets:
            add(
                results,
                "FAIL",
                "Physical fill trial data",
                "Text-complete measured rows point at missing required assets: " + "; ".join(text_complete_missing_assets),
            )
            errors += 1
        elif publishable_rows:
            add(results, "PASS", "Physical fill trial data", f"{len(publishable_rows)} publishable measured trial rows present.")
        elif measured_rows:
            add(results, "WARN", "Physical fill trial data", f"{len(measured_rows)} measured rows present, but none meet publishable-row completeness.")
        else:
            add(results, "WARN", "Physical fill trial data", "No measured fill-trial rows yet; acceptance-critical physical dataset is still missing.")
    else:
        add(results, "WARN", "Physical fill trial data", str(FILL_TRIAL_CSV.relative_to(ROOT)))

    if FILL_SUMMARY_MD.exists():
        add(results, "PASS", "Fill trial summary artifact", str(FILL_SUMMARY_MD.relative_to(ROOT)))
    else:
        add(results, "WARN", "Fill trial summary artifact", str(FILL_SUMMARY_MD.relative_to(ROOT)))

    if FILL_ASSET_REPORT.exists():
        add(results, "PASS", "Fill trial asset artifact", str(FILL_ASSET_REPORT.relative_to(ROOT)))
    else:
        add(results, "WARN", "Fill trial asset artifact", str(FILL_ASSET_REPORT.relative_to(ROOT)))

    if FILL_TABLE_TEX.exists():
        add(results, "PASS", "Fill trial LaTeX artifact", str(FILL_TABLE_TEX.relative_to(ROOT)))
    else:
        add(results, "WARN", "Fill trial LaTeX artifact", str(FILL_TABLE_TEX.relative_to(ROOT)))

    if PHYSICAL_DATA_READINESS_REPORT.exists():
        readiness_text = PHYSICAL_DATA_READINESS_REPORT.read_text(errors="replace")
        if "Submission-strength physical dataset: READY" in readiness_text:
            add(results, "PASS", "Physical data readiness", str(PHYSICAL_DATA_READINESS_REPORT.relative_to(ROOT)))
        else:
            add(results, "WARN", "Physical data readiness", "Submission-strength physical dataset is not ready yet.")
    else:
        add(results, "WARN", "Physical data readiness", str(PHYSICAL_DATA_READINESS_REPORT.relative_to(ROOT)))

    if FILL_PHOTO_PANEL_REPORT.exists():
        add(results, "PASS", "Fill photo panel report", str(FILL_PHOTO_PANEL_REPORT.relative_to(ROOT)))
    else:
        add(results, "WARN", "Fill photo panel report", str(FILL_PHOTO_PANEL_REPORT.relative_to(ROOT)))

    if FILL_PLAN_CSV.exists():
        plan_rows = parse_csv_rows(FILL_PLAN_CSV)
        plan_ok, plan_detail = fill_plan_coverage(plan_rows)
        if plan_ok:
            add(results, "PASS", "Fill trial plan coverage", plan_detail)
        else:
            add(results, "FAIL", "Fill trial plan coverage", plan_detail)
            errors += 1
    else:
        add(results, "FAIL", "Fill trial plan coverage", str(FILL_PLAN_CSV.relative_to(ROOT)))
        errors += 1

    if FILL_PLAN_SUMMARY_MD.exists():
        add(results, "PASS", "Fill trial plan artifact", str(FILL_PLAN_SUMMARY_MD.relative_to(ROOT)))
    else:
        add(results, "WARN", "Fill trial plan artifact", str(FILL_PLAN_SUMMARY_MD.relative_to(ROOT)))

    missing_trial_packet = [
        str(path.relative_to(ROOT))
        for path in [FILL_TRIAL_PACKET_MD, FILL_TRIAL_PREFILL_CSV]
        if not path.exists()
    ]
    run_sheets = sorted(FILL_TRIAL_RUN_SHEET_DIR.glob("P*_run_sheet.md")) if FILL_TRIAL_RUN_SHEET_DIR.exists() else []
    prefill_rows = parse_csv_rows(FILL_TRIAL_PREFILL_CSV) if FILL_TRIAL_PREFILL_CSV.exists() else []
    if missing_trial_packet:
        add(results, "FAIL", "Fill trial execution packet", "Missing: " + ", ".join(missing_trial_packet))
        errors += 1
    elif len(run_sheets) >= 10 and len(prefill_rows) >= 10:
        add(results, "PASS", "Fill trial execution packet", f"{len(run_sheets)} run sheets; {len(prefill_rows)} prefill rows.")
    else:
        add(results, "FAIL", "Fill trial execution packet", f"run_sheets={len(run_sheets)}, prefill_rows={len(prefill_rows)}")
        errors += 1

    if TRIAL_EXECUTION_READINESS_REPORT.exists() and TRIAL_EVIDENCE_CHECKLIST.exists() and TRIAL_MINIMUM_SUBSET.exists():
        readiness_text = TRIAL_EXECUTION_READINESS_REPORT.read_text(errors="replace")
        if "| FAIL |" in readiness_text:
            add(results, "FAIL", "Trial execution readiness", str(TRIAL_EXECUTION_READINESS_REPORT.relative_to(ROOT)))
            errors += 1
        else:
            add(results, "PASS", "Trial execution readiness", str(TRIAL_EXECUTION_READINESS_REPORT.relative_to(ROOT)))
    else:
        missing_trial_readiness = [
            str(path.relative_to(ROOT))
            for path in [TRIAL_EXECUTION_READINESS_REPORT, TRIAL_EVIDENCE_CHECKLIST, TRIAL_MINIMUM_SUBSET]
            if not path.exists()
        ]
        add(results, "FAIL", "Trial execution readiness", "Missing: " + ", ".join(missing_trial_readiness))
        errors += 1

    planned_rows = parse_csv_rows(PLANNED_GCODE_SUMMARY_CSV) if PLANNED_GCODE_SUMMARY_CSV.exists() else []
    missing_planned_gcode = [
        row.get("planned_gcode_file", "")
        for row in planned_rows
        if row.get("planned_gcode_file") and not (ROOT / row["planned_gcode_file"]).exists()
    ]
    if PLANNED_GCODE_SUMMARY_MD.exists() and len(planned_rows) >= 10 and not missing_planned_gcode:
        add(results, "PASS", "Planned injection G-code snippets", f"{len(planned_rows)} planned snippets.")
    else:
        detail = (
            f"summary_exists={PLANNED_GCODE_SUMMARY_MD.exists()}, "
            f"planned_rows={len(planned_rows)}, missing={missing_planned_gcode}"
        )
        add(results, "FAIL", "Planned injection G-code snippets", detail)
        errors += 1

    mold_files = sorted((ROOT / "paper" / "molds").glob("P*_mold.stl"))
    if MOLD_MANIFEST_MD.exists() and len(mold_files) >= 10:
        add(results, "PASS", "Standard mold assets", f"{len(mold_files)} mold STLs; {MOLD_MANIFEST_MD.relative_to(ROOT)}")
    else:
        detail = f"manifest_exists={MOLD_MANIFEST_MD.exists()}, mold_stls={len(mold_files)}"
        add(results, "FAIL", "Standard mold assets", detail)
        errors += 1

    if CLAIM_SCOPE_REPORT.exists():
        report_text = CLAIM_SCOPE_REPORT.read_text(errors="replace")
        if "| FAIL |" in report_text:
            add(results, "FAIL", "Claim scope check", str(CLAIM_SCOPE_REPORT.relative_to(ROOT)))
            errors += 1
        else:
            add(results, "PASS", "Claim scope check", str(CLAIM_SCOPE_REPORT.relative_to(ROOT)))
    else:
        add(results, "FAIL", "Claim scope check", str(CLAIM_SCOPE_REPORT.relative_to(ROOT)))
        errors += 1

    if CLAIM_EVIDENCE_MAP.exists() and CLAIM_EVIDENCE_REPORT.exists():
        report_text = CLAIM_EVIDENCE_REPORT.read_text(errors="replace")
        if "| FAIL |" in report_text:
            add(results, "FAIL", "Claim-evidence map check", str(CLAIM_EVIDENCE_REPORT.relative_to(ROOT)))
            errors += 1
        else:
            add(results, "PASS", "Claim-evidence map check", str(CLAIM_EVIDENCE_REPORT.relative_to(ROOT)))
    else:
        missing_claim_evidence = [
            str(path.relative_to(ROOT))
            for path in [CLAIM_EVIDENCE_MAP, CLAIM_EVIDENCE_REPORT]
            if not path.exists()
        ]
        add(results, "FAIL", "Claim-evidence map check", "Missing: " + ", ".join(missing_claim_evidence))
        errors += 1

    if IEEE_SUBMISSION_REPORT.exists():
        report_text = IEEE_SUBMISSION_REPORT.read_text(errors="replace")
        if "| FAIL |" in report_text:
            add(results, "FAIL", "IEEE submission readiness check", str(IEEE_SUBMISSION_REPORT.relative_to(ROOT)))
            errors += 1
        else:
            add(results, "PASS", "IEEE submission readiness check", str(IEEE_SUBMISSION_REPORT.relative_to(ROOT)))
    else:
        add(results, "FAIL", "IEEE submission readiness check", str(IEEE_SUBMISSION_REPORT.relative_to(ROOT)))
        errors += 1

    pdf_results, pdf_errors = check_pdf_production(OUTPUT_PDFS[0])
    write_table_report(PDF_PRODUCTION_REPORT, "PDF Production Check", pdf_results)
    errors += pdf_errors
    if pdf_errors:
        add(results, "FAIL", "PDF production check", f"{PDF_PRODUCTION_REPORT.relative_to(ROOT)} has {pdf_errors} failing checks.")
    else:
        add(results, "PASS", "PDF production check", str(PDF_PRODUCTION_REPORT.relative_to(ROOT)))

    write_report(results)
    print(REPORT_PATH)
    for status, check, detail in results:
        print(f"{status}: {check}: {detail}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
