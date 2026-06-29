#!/usr/bin/env python3
"""Generate QuiverAI SVG assets for the Magma paper.

The API key is intentionally not stored here. Provide it with
QUIVERAI_API_KEY or paste it when prompted.
"""

from __future__ import annotations

import getpass
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "paper" / "figures"
API_URL = "https://api.quiver.ai/v1/svgs/generations"
MODEL = "arrow-1.1"


FIGURES = [
    {
        "name": "quiver_system_concept",
        "prompt": (
            "A clean IEEE paper technical vector diagram of a hybrid 3D printing and injection molding process. "
            "Show a desktop multi-tool FFF printer cross-section: orange PETG mold walls on a gray build plate, "
            "a dark nozzle above a circular injection port, magenta molten PLA filling the cavity, and a teal "
            "vertical arrow for rising Z. Use flat vector shapes, crisp lines, white background. No text, no labels, "
            "no letters, no words."
        ),
        "instructions": (
            "Landscape technical schematic, not photorealistic. Do not include any text inside the SVG. "
            "Use professional scientific figure style."
        ),
    },
    {
        "name": "quiver_slicer_pipeline",
        "prompt": (
            "A professional vector flowchart for an IEEE paper showing the software pipeline for hybrid FFF mold "
            "injection. Four rounded boxes left to right connected by arrows. The boxes are distinct colors: green, "
            "teal, magenta, and blue. Use white background and restrained colors. No text, no labels, no letters, no words."
        ),
        "instructions": (
            "Make it a clean editable SVG flowchart, landscape aspect ratio, aligned boxes, strong typographic hierarchy, "
            "no decorative clutter, and no text."
        ),
    },
    {
        "name": "quiver_model_roles",
        "prompt": (
            "A vector diagram for a research paper explaining role-based CAD bodies. Show three small panels: "
            "orange split mold halves, magenta injected part body, teal injection port marker. "
            "Use an orthographic CAD-like style with thin outlines and light fills."
        ),
        "instructions": (
            "Technical IEEE figure, white background, simple geometry, sharp lines, no perspective complexity, "
            "no text, no labels, no letters, no words."
        ),
    },
    {
        "name": "quiver_process_window",
        "prompt": (
            "A clean vector chart for an IEEE paper showing a process window for low-pressure plastic injection. "
            "Show x and y axes, four pastel colored regions, and a magenta test point dot inside a green candidate "
            "region. Use no text, no labels, no letters, no words."
        ),
        "instructions": (
            "Scientific chart style, white background, vector shapes, professional and compact. No text."
        ),
    },
]


def get_key() -> str:
    key = os.environ.get("QUIVERAI_API_KEY", "").strip()
    if key:
        return key
    if sys.stdin.isatty():
        return getpass.getpass("QuiverAI API key: ").strip()
    return sys.stdin.readline().strip()


def generate_svg(key: str, prompt: str, instructions: str) -> str:
    body = {
        "model": MODEL,
        "prompt": prompt,
        "instructions": instructions,
        "n": 1,
        "stream": False,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"Quiver API error {exc.code}: {detail}") from exc

    try:
        return data["data"][0]["svg"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected Quiver response shape: {data}") from exc


def sanitize_svg(svg: str) -> str:
    """Remove generated text from Quiver SVGs and normalize font metadata."""
    svg = re.sub(r"<text\b[^>]*>.*?</text>", "", svg, flags=re.DOTALL | re.IGNORECASE)
    svg = re.sub(r"<tspan\b[^>]*/>", "", svg, flags=re.IGNORECASE)
    svg = re.sub(r"<tspan\b[^>]*>.*?</tspan>", "", svg, flags=re.DOTALL | re.IGNORECASE)
    svg = re.sub(r"font-family=\"[^\"]*\"", 'font-family="Arial"', svg)
    return svg


def convert_svg(svg_path: Path) -> None:
    png_path = svg_path.with_suffix(".png")
    pdf_path = svg_path.with_suffix(".pdf")
    cmd_png = [
        "magick",
        "-density",
        "360",
        str(svg_path),
        "-resize",
        "1800x",
        str(png_path),
    ]
    subprocess.run(cmd_png, check=True)
    # PDF conversion can fail on some ImageMagick builds; PNG is enough for pdflatex.
    cmd_pdf = ["magick", str(svg_path), str(pdf_path)]
    subprocess.run(cmd_pdf, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    key = get_key()
    if not key:
        raise SystemExit("Missing QuiverAI API key.")
    manifest = []
    for spec in FIGURES:
        print(f"generating {spec['name']}...", flush=True)
        svg = generate_svg(key, spec["prompt"], spec["instructions"])
        svg_path = FIG_DIR / f"{spec['name']}.svg"
        raw_path = FIG_DIR / f"{spec['name']}.raw.svg"
        raw_path.write_text(svg, encoding="utf-8")
        svg_path.write_text(sanitize_svg(svg), encoding="utf-8")
        convert_svg(svg_path)
        manifest.append(
            {
                "name": spec["name"],
                "svg": str(svg_path.relative_to(ROOT)),
                "png": str(svg_path.with_suffix(".png").relative_to(ROOT)),
            }
        )
        time.sleep(0.5)
    (FIG_DIR / "quiver_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
