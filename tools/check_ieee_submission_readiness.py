#!/usr/bin/env python3
"""Run IEEE submission-facing checks that are separate from paper science claims."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "magma_ieee.tex"
PDF = ROOT / "output" / "pdf" / "magma_ieee_paper.pdf"
OUT = ROOT / "output" / "verification" / "ieee_submission_check.md"


def command_output(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT)


def add(results: list[tuple[str, str, str]], status: str, check: str, detail: str) -> None:
    results.append((status, check, detail))


def write_report(results: list[tuple[str, str, str]]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        f.write("# IEEE Submission Readiness Check\n\n")
        f.write("| status | check | detail |\n")
        f.write("| --- | --- | --- |\n")
        for status, check, detail in results:
            safe_detail = detail.replace("|", "\\|").replace("\n", " ")
            f.write(f"| {status} | {check} | {safe_detail} |\n")


def pdfinfo_map() -> dict[str, str]:
    info: dict[str, str] = {}
    for line in command_output(["pdfinfo", str(PDF)]).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        info[key.strip()] = value.strip()
    return info


def pdffonts_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in command_output(["pdffonts", str(PDF)]).splitlines():
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


def included_graphics(tex: str) -> list[Path]:
    paths: list[Path] = []
    for name in re.findall(r"\\includegraphics(?:\[[^]]+\])?\{([^}]+)\}", tex):
        paths.append(ROOT / "paper" / name)
    return paths


def main() -> int:
    results: list[tuple[str, str, str]] = []
    errors = 0

    if not TEX.exists():
        add(results, "FAIL", "TeX source", str(TEX.relative_to(ROOT)))
        write_report(results)
        print(OUT)
        return 1

    tex = TEX.read_text(errors="replace")
    if "\\documentclass[conference]{IEEEtran}" in tex:
        add(results, "PASS", "IEEE conference template", "IEEEtran conference mode.")
    else:
        add(results, "FAIL", "IEEE conference template", "Expected IEEEtran conference mode.")
        errors += 1

    required_author_terms = [
        "Brian Machado",
        "Clayton Haight",
        "Ethan Childerhose",
        "Samuel Sun",
        "Bracket Bot Research, San Francisco, CA, USA",
        "sunday.ai, Mountain View, CA, USA",
        "Steinmetz Motors, San Francisco, CA, USA",
    ]
    missing_author_terms = [term for term in required_author_terms if term not in tex]
    if missing_author_terms:
        add(results, "FAIL", "Author affiliation metadata", "Missing: " + ", ".join(missing_author_terms))
        errors += 1
    else:
        add(results, "PASS", "Author affiliation metadata", "Four named authors and affiliations are present.")

    graphics = included_graphics(tex)
    missing_graphics = [str(path.relative_to(ROOT)) for path in graphics if not path.exists()]
    if missing_graphics:
        add(results, "FAIL", "External figure assets", "Missing: " + ", ".join(missing_graphics))
        errors += 1
    else:
        add(results, "PASS", "External figure assets", f"{len(graphics)} includegraphics target(s) present.")

    if not PDF.exists():
        add(results, "FAIL", "Deliverable PDF", str(PDF.relative_to(ROOT)))
        write_report(results)
        print(OUT)
        return 1

    info = pdfinfo_map()
    pages = int(info.get("Pages", "0") or 0)
    if 1 <= pages <= 6:
        add(results, "PASS", "PDF page count", f"{pages} pages.")
    else:
        add(results, "FAIL", "PDF page count", f"{pages} pages.")
        errors += 1

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

    if info.get("Form", "").lower() == "none":
        add(results, "PASS", "PDF forms", "none")
    else:
        add(results, "FAIL", "PDF forms", info.get("Form", "missing"))
        errors += 1

    if info.get("JavaScript", "").lower() == "no":
        add(results, "PASS", "PDF JavaScript", "none")
    else:
        add(results, "FAIL", "PDF JavaScript", info.get("JavaScript", "missing"))
        errors += 1

    fonts = pdffonts_rows()
    unembedded = [font["name"] for font in fonts if font["embedded"] != "yes"]
    unsubsets = [font["name"] for font in fonts if font["subset"] != "yes"]
    if fonts and not unembedded and not unsubsets:
        add(results, "PASS", "PDF fonts", f"{len(fonts)} fonts embedded and subset.")
    else:
        add(results, "FAIL", "PDF fonts", f"fonts={len(fonts)}, unembedded={unembedded}, unsubsets={unsubsets}")
        errors += 1

    text = command_output(["pdftotext", str(PDF), "-"])
    required_text = [
        "Magma: Low-Pressure Thermoplastic Injection",
        "Index Terms",
        "R EFERENCES",
    ]
    missing_text = [term for term in required_text if term not in text]
    if missing_text:
        add(results, "FAIL", "Searchable PDF text", "Missing text: " + ", ".join(missing_text))
        errors += 1
    else:
        add(results, "PASS", "Searchable PDF text", "Title, keywords, and references text extracted.")

    write_report(results)
    print(OUT)
    for status, check, detail in results:
        print(f"{status}: {check}: {detail}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
