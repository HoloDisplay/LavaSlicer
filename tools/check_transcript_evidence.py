#!/usr/bin/env python3
"""Check the narrowed transcript evidence used for preliminary observations."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT = Path("/Users/bmachado/.codex/attachments/207f5df1-709a-472b-9dac-609c0637ed53/pasted-text.txt")
INDEX = ROOT / "paper" / "transcript_evidence_index.md"
EXPERIMENT_LOG = ROOT / "paper" / "experiment_log_2026-06-27.md"
OUT = ROOT / "output" / "verification" / "transcript_evidence_check.md"

EVIDENCE_ITEMS = [
    (
        "E1",
        "Simple first article",
        [
            "make a cup, basically",
            "fill the cup",
            "10 millimeters or less",
        ],
    ),
    (
        "E2",
        "Larger nozzle and tool-changing setup",
        [
            "0.8",
            "0.6",
            "multi nozzle printer",
        ],
    ),
    (
        "E3",
        "Post-processor path",
        [
            "take the g-code and just modify the g code",
            "insert a g-code thing halfway",
        ],
    ),
    (
        "E4",
        "Injected-part role model",
        [
            "model also the injected molded part",
            "select that as the injection part",
            "topmost face",
        ],
    ),
    (
        "E5",
        "PETG mold and PLA injection split",
        [
            "Print with ptg and then inject into it with PLA",
        ],
    ),
    (
        "E6",
        "Volumetric-flow limit",
        [
            "tried to inject it too fast",
            "the printer just said, no",
        ],
    ),
    (
        "E7",
        "Preliminary material delivery and messy fill",
        [
            "goes spaghetti",
            "cool. At the bottom",
        ],
    ),
    (
        "E8",
        "Standby temperature and heat-wait need",
        [
            "temperature is gonna be 180",
            "because it's parked",
        ],
    ),
    (
        "E9",
        "Purge and nozzle residue",
        [
            "junk on the nozzle",
            "no way to clean it",
            "no way to purge",
        ],
    ),
    (
        "E10",
        "Collision and downward-approach constraint",
        [
            "can't inject downwards",
            "it's gonna hit everything",
            "be very careful",
        ],
    ),
    (
        "E11",
        "Manual intervention boundary",
        [
            "manually jogging this",
            "manual injection",
            "manually edited the g codes",
        ],
    ),
]

REQUIRED_INDEX_PHRASES = [
    "not a controlled quantitative dataset",
    "does not establish complete fill, packing, repeatability, or mechanical equivalence",
    "Do not upload the raw transcript",
]


def write_report(results: list[tuple[str, str, str]]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        f.write("# Transcript Evidence Check\n\n")
        f.write("| status | check | detail |\n")
        f.write("| --- | --- | --- |\n")
        for status, check, detail in results:
            safe = detail.replace("|", "\\|").replace("\n", " ")
            f.write(f"| {status} | {check} | {safe} |\n")


def missing_fragments(text: str, fragments: list[str]) -> list[str]:
    lowered = text.lower()
    return [fragment for fragment in fragments if fragment.lower() not in lowered]


def main() -> int:
    results: list[tuple[str, str, str]] = []
    errors = 0

    if not INDEX.exists():
        results.append(("FAIL", "evidence index exists", str(INDEX.relative_to(ROOT))))
        write_report(results)
        print(OUT)
        return 1

    index_text = INDEX.read_text(errors="replace")
    missing_ids = [item_id for item_id, _, _ in EVIDENCE_ITEMS if f"| {item_id} |" not in index_text]
    missing_index_phrases = missing_fragments(index_text, REQUIRED_INDEX_PHRASES)
    if missing_ids or missing_index_phrases:
        detail = f"missing_ids={missing_ids}, missing_phrases={missing_index_phrases}"
        results.append(("FAIL", "evidence index coverage", detail))
        errors += 1
    else:
        results.append(("PASS", "evidence index coverage", f"{len(EVIDENCE_ITEMS)} evidence rows and boundary phrases present."))

    if EXPERIMENT_LOG.exists():
        log_text = EXPERIMENT_LOG.read_text(errors="replace")
        required_log_terms = ["paper/transcript_evidence_index.md", "preliminary observational evidence"]
        missing_log = missing_fragments(log_text, required_log_terms)
        if missing_log:
            results.append(("FAIL", "experiment log cross-reference", ", ".join(missing_log)))
            errors += 1
        else:
            results.append(("PASS", "experiment log cross-reference", str(EXPERIMENT_LOG.relative_to(ROOT))))
    else:
        results.append(("FAIL", "experiment log cross-reference", str(EXPERIMENT_LOG.relative_to(ROOT))))
        errors += 1

    if TRANSCRIPT.exists():
        transcript_text = TRANSCRIPT.read_text(errors="replace")
        missing_by_item = []
        for item_id, label, fragments in EVIDENCE_ITEMS:
            missing = missing_fragments(transcript_text, fragments)
            if missing:
                missing_by_item.append(f"{item_id} {label}: {missing}")
        if missing_by_item:
            results.append(("FAIL", "source transcript anchors", "; ".join(missing_by_item)))
            errors += 1
        else:
            results.append(("PASS", "source transcript anchors", f"{len(EVIDENCE_ITEMS)} items found in local source transcript."))
    else:
        results.append(("WARN", "source transcript anchors", f"Local transcript unavailable: {TRANSCRIPT}"))

    write_report(results)
    print(OUT)
    for status, check, detail in results:
        print(f"{status}: {check}: {detail}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
