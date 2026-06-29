#!/usr/bin/env python3
"""Validate the Magma claim-evidence map used for reviewer-facing scope control."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "paper" / "claim_evidence_map.md"
OUT = ROOT / "output" / "verification" / "claim_evidence_check.md"

REQUIRED_PHRASES = [
    "C1 | Slicer semantics",
    "C2 | Volume planning",
    "C3 | Machine sequence",
    "C4 | Native slicer prototype",
    "C5 | Preliminary material delivery",
    "C6 | Complete cavity fill",
    "C7 | Industrial equivalence",
    "C8 | Quantitative physical validation",
    "C9 | Reproducibility package",
    "C10 | Planned trial execution setup",
    "C11 | Novelty versus rapid tooling",
    "Preliminary observation only",
    "Not claimed yet",
    "Required next evidence",
    "Setup artifact only",
    "Backed by scoped prior-work positioning",
    "transcript_evidence_index.md",
    "not yet defensible as a complete experimental manufacturing-results paper",
    "do not replace executed evidence",
    "distinction from conventional printed-mold rapid tooling",
]


def write_report(results: list[tuple[str, str, str]]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        f.write("# Claim-Evidence Map Check\n\n")
        f.write("| status | check | detail |\n")
        f.write("| --- | --- | --- |\n")
        for status, check, detail in results:
            f.write(f"| {status} | {check} | {detail.replace('|', '\\\\|')} |\n")


def main() -> int:
    results: list[tuple[str, str, str]] = []
    errors = 0

    if not MAP.exists():
        results.append(("FAIL", "claim evidence map exists", str(MAP.relative_to(ROOT))))
        write_report(results)
        print(OUT)
        return 1

    text = MAP.read_text(errors="replace")
    missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in text]
    if missing:
        results.append(("FAIL", "required claim boundaries", ", ".join(missing)))
        errors += 1
    else:
        results.append(("PASS", "required claim boundaries", f"{len(REQUIRED_PHRASES)} required phrases present."))

    if text.count("| C") >= 9:
        results.append(("PASS", "claim count", "At least nine claim rows present."))
    else:
        results.append(("FAIL", "claim count", "Expected at least nine claim rows."))
        errors += 1

    write_report(results)
    print(OUT)
    for status, check, detail in results:
        print(f"{status}: {check}: {detail}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
