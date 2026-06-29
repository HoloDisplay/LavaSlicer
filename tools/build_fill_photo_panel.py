#!/usr/bin/env python3
"""Build a publication-style photo panel from measured fill-trial photos."""

from __future__ import annotations

import csv
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "paper" / "fill_trials_template.csv"
OUT_DIR = ROOT / "output" / "figures"
PANEL = OUT_DIR / "fill_trial_photo_panel.png"
REPORT = ROOT / "output" / "verification" / "fill_photo_panel_check.md"

PHOTO_FIELDS = [
    ("photo_top", "top"),
    ("photo_side", "side"),
    ("photo_section", "section"),
]
try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_LANCZOS = Image.LANCZOS


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def has_measurement(row: dict[str, str]) -> bool:
    fields = [
        "delivered_mass_g",
        "estimated_delivered_volume_mm3",
        "visible_fill_depth_mm",
        "bottom_fill_score_0_3",
        "failure_label_primary",
        "photo_top",
        "photo_side",
        "photo_section",
    ]
    return row.get("trial_id", "").strip() and any(row.get(field, "").strip() for field in fields)


def photo_entries(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[str]]:
    entries: list[dict[str, str]] = []
    missing: list[str] = []
    for row in rows:
        if not has_measurement(row):
            continue
        for field, view in PHOTO_FIELDS:
            value = row.get(field, "").strip()
            if not value:
                continue
            path = resolve(value)
            if not path.is_file():
                missing.append(f"{row.get('trial_id', '(missing trial_id)')} {field}={value}")
                continue
            entries.append(
                {
                    "trial_id": row.get("trial_id", ""),
                    "view": view,
                    "path": str(path),
                    "temp": row.get("injection_temp_c", ""),
                    "flow": row.get("flow_mm3_s", ""),
                    "label": row.get("failure_label_primary", ""),
                    "fill": row.get("visible_fill_depth_mm", ""),
                }
            )
    return entries, missing


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont, fill: str, width: int) -> None:
    x, y = xy
    for line in wrap(text, width=width):
        draw.text((x, y), line, fill=fill, font=font)
        y += 14


def make_tile(entry: dict[str, str], tile_size: tuple[int, int], image_size: tuple[int, int]) -> Image.Image:
    tile_w, tile_h = tile_size
    image_w, image_h = image_size
    font = ImageFont.load_default()

    tile = Image.new("RGB", tile_size, "white")
    image = Image.open(entry["path"]).convert("RGB")
    image = ImageOps.exif_transpose(image)
    image = ImageOps.contain(image, image_size, method=RESAMPLE_LANCZOS)
    x = (image_w - image.width) // 2
    y = (image_h - image.height) // 2
    tile.paste(image, (x, y))

    draw = ImageDraw.Draw(tile)
    draw.rectangle([(0, 0), (tile_w - 1, image_h - 1)], outline=(40, 40, 40), width=2)
    draw.rectangle([(0, image_h), (tile_w - 1, tile_h - 1)], fill=(246, 246, 246), outline=(180, 180, 180), width=1)
    caption = f"{entry['trial_id']} {entry['view']}"
    if entry["temp"] or entry["flow"]:
        caption += f" | {entry['temp']} C, {entry['flow']} mm3/s"
    if entry["label"]:
        caption += f" | {entry['label']}"
    if entry["fill"]:
        caption += f" | fill {entry['fill']} mm"
    draw_wrapped(draw, (8, image_h + 8), caption, font, "black", width=58)
    return tile


def build_panel(entries: list[dict[str, str]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tile_size = (520, 400)
    image_size = (520, 315)
    cols = 3
    rows = (len(entries) + cols - 1) // cols
    gutter = 18
    margin = 24
    panel_w = margin * 2 + cols * tile_size[0] + (cols - 1) * gutter
    panel_h = margin * 2 + rows * tile_size[1] + (rows - 1) * gutter
    panel = Image.new("RGB", (panel_w, panel_h), "white")

    for index, entry in enumerate(entries):
        row = index // cols
        col = index % cols
        x = margin + col * (tile_size[0] + gutter)
        y = margin + row * (tile_size[1] + gutter)
        panel.paste(make_tile(entry, tile_size, image_size), (x, y))

    panel.save(PANEL, quality=95)


def write_report(status: str, measured_count: int, entries: list[dict[str, str]], missing: list[str]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("w") as f:
        f.write("# Fill Photo Panel Check\n\n")
        f.write(f"Photo panel status: {status}\n\n")
        f.write(f"Measured rows scanned: {measured_count}\n")
        f.write(f"Photo entries included: {len(entries)}\n")
        f.write(f"Panel path: `{PANEL.relative_to(ROOT)}`\n\n")
        f.write("| status | check | detail |\n")
        f.write("| --- | --- | --- |\n")
        if entries:
            f.write(f"| PASS | photo panel entries | {len(entries)} existing photo(s) included. |\n")
        else:
            f.write("| WARN | photo panel entries | No measured-trial photos are available yet. |\n")
        if missing:
            f.write(f"| WARN | missing declared photos | {'; '.join(missing)} |\n")
        else:
            f.write("| PASS | missing declared photos | No declared photo paths are missing. |\n")
        if status == "READY":
            f.write(f"| PASS | panel image | `{PANEL.relative_to(ROOT)}` generated. |\n")
        else:
            f.write("| WARN | panel image | Not generated because no existing measured-trial photos were found. |\n")


def main() -> int:
    if PANEL.exists():
        PANEL.unlink()
    if not INPUT.exists():
        write_report("NOT_READY", 0, [], [str(INPUT.relative_to(ROOT))])
        print(REPORT)
        return 0

    rows = read_rows(INPUT)
    measured = [row for row in rows if has_measurement(row)]
    entries, missing = photo_entries(rows)
    if entries:
        build_panel(entries)
        status = "READY"
    else:
        status = "NOT_READY"
    write_report(status, len(measured), entries, missing)
    print(REPORT)
    if PANEL.exists():
        print(PANEL)
    print(f"photo_entries={len(entries)}")
    print(f"missing_declared_photos={len(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
