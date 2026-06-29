#!/usr/bin/env python3
"""Check that the Magma manuscript keeps its claims scoped to evidence."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "magma_ieee.tex"
OUT = ROOT / "output" / "verification" / "claim_scope_check.md"

REQUIRED_CAVEATS = [
    ("industrial replacement disclaimer", "not a replacement for industrial injection molding"),
    ("low-pressure framing", "low-pressure molded deposition"),
    ("G-code versus fill distinction", "They do not prove that a cavity fills completely"),
    ("physical result limitation", "not yet a controlled, fully packed molded part"),
    ("next dataset requirement", "next decisive step is a compact quantitative dataset"),
]

FORBIDDEN_CLAIMS = [
    r"\bindustrial-equivalent\b",
    r"\bfully validated\b",
    r"\bproduction-ready\b",
    r"\bmechanically equivalent\b",
    r"\bguarantees? complete fill\b",
    r"\breplaces industrial injection molding\b",
    r"\bclosed-loop fill control\b",
]


def write_report(rows: list[tuple[str, str, str]]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        f.write("# Claim Scope Check\n\n")
        f.write("| status | check | detail |\n")
        f.write("| --- | --- | --- |\n")
        for status, check, detail in rows:
            f.write(f"| {status} | {check} | {detail.replace('|', '\\|')} |\n")


def main() -> int:
    tex = TEX.read_text(errors="replace")
    rows: list[tuple[str, str, str]] = []
    errors = 0

    for name, phrase in REQUIRED_CAVEATS:
        if phrase in tex:
            rows.append(("PASS", name, phrase))
        else:
            rows.append(("FAIL", name, f"Missing phrase: {phrase}"))
            errors += 1

    matches: list[str] = []
    for pattern in FORBIDDEN_CLAIMS:
        if re.search(pattern, tex, re.IGNORECASE):
            matches.append(pattern)
    if matches:
        rows.append(("FAIL", "forbidden overclaims", ", ".join(matches)))
        errors += 1
    else:
        rows.append(("PASS", "forbidden overclaims", "No unqualified industrial/validation-equivalence claims found."))

    write_report(rows)
    print(OUT)
    for status, check, detail in rows:
        print(f"{status}: {check}: {detail}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
