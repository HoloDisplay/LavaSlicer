#!/usr/bin/env python3
"""Generate the Magma hybrid FFF/injection molding paper PDF."""

from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "magma_hybrid_fff_injection_molding_paper.pdf"

W, H = letter
MARGIN = 42
GUTTER = 18
COL_W = (W - 2 * MARGIN - GUTTER) / 2

NAVY = colors.HexColor("#14213D")
BLUE = colors.HexColor("#1D4E89")
TEAL = colors.HexColor("#14919B")
ORANGE = colors.HexColor("#F39C12")
ORANGE_DARK = colors.HexColor("#B96900")
MAGENTA = colors.HexColor("#C2185B")
GREEN = colors.HexColor("#2A9D55")
LIME = colors.HexColor("#7BC96F")
GRAY = colors.HexColor("#5D6673")
LIGHT = colors.HexColor("#F4F7FA")
LIGHT2 = colors.HexColor("#E9EEF3")
INK = colors.HexColor("#1F2933")


def clean(text: str) -> str:
    return (
        text.replace("FFF-printed", "FFF-printed")
        .replace("low-pressure", "low-pressure")
        .replace("multi-tool", "multi-tool")
        .replace("one-off", "one-off")
    )


def draw_header(c: canvas.Canvas, page_no: int) -> None:
    c.setStrokeColor(BLUE)
    c.setLineWidth(0.8)
    c.line(MARGIN, H - 28, W - MARGIN, H - 28)
    c.setFont("Helvetica", 6.8)
    c.setFillColor(GRAY)
    c.drawString(MARGIN, H - 22, "Magma: hybrid FFF-printed mold injection on a desktop multi-tool printer")
    c.drawRightString(W - MARGIN, H - 22, f"Internal research draft | page {page_no}")


def draw_caption(c: canvas.Canvas, x: float, y: float, w: float, label: str, text: str) -> float:
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 6.7)
    c.drawString(x, y, label)
    offset = stringWidth(label + " ", "Helvetica-Bold", 6.7)
    c.setFont("Helvetica", 6.7)
    lines = wrap(text, "Helvetica", 6.7, w - offset)
    if lines:
        c.drawString(x + offset, y, lines[0])
        yy = y - 8
        for line in lines[1:]:
            c.drawString(x, yy, line)
            yy -= 8
        return yy - 3
    return y - 10


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    words = clean(text).split()
    lines: list[str] = []
    line = ""
    for word in words:
        trial = word if not line else f"{line} {word}"
        if stringWidth(trial, font, size) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def paragraph(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    text: str,
    font: str = "Times-Roman",
    size: float = 8.2,
    leading: float = 10.1,
    color=INK,
) -> float:
    c.setFont(font, size)
    c.setFillColor(color)
    for para in clean(text).split("\n\n"):
        for line in wrap(para, font, size, w):
            c.drawString(x, y, line)
            y -= leading
        y -= leading * 0.55
    return y


def bullet_list(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    items: list[tuple[str, str] | str],
    size: float = 7.8,
    leading: float = 9.2,
) -> float:
    for item in items:
        if isinstance(item, tuple):
            head, body = item
            text = f"{head}: {body}"
        else:
            head, body = "", item
            text = item
        c.setFillColor(TEAL)
        c.circle(x + 2.2, y + 2.2, 1.5, fill=1, stroke=0)
        if head:
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", size)
            c.drawString(x + 8, y, f"{head}:")
            start = stringWidth(f"{head}: ", "Helvetica-Bold", size)
            c.setFont("Helvetica", size)
            lines = wrap(body, "Helvetica", size, w - 8 - start)
            if lines:
                c.drawString(x + 8 + start, y, lines[0])
                y -= leading
                for line in lines[1:]:
                    c.drawString(x + 8, y, line)
                    y -= leading
            else:
                y -= leading
        else:
            c.setFillColor(INK)
            c.setFont("Helvetica", size)
            for line in wrap(text, "Helvetica", size, w - 8):
                c.drawString(x + 8, y, line)
                y -= leading
        y -= 2.8
    return y


def section_title(c: canvas.Canvas, x: float, y: float, title: str) -> float:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, title.upper())
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.1)
    c.line(x, y - 3, x + 58, y - 3)
    return y - 13


def boxed_note(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, body: str) -> None:
    c.setFillColor(LIGHT)
    c.setStrokeColor(LIGHT2)
    c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8.2)
    c.drawString(x + 9, y - 14, title)
    paragraph(c, x + 9, y - 27, w - 18, body, font="Helvetica", size=7.2, leading=8.7, color=INK)


def draw_system_diagram(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.saveState()
    c.setFillColor(colors.white)
    c.setStrokeColor(LIGHT2)
    c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)

    bx = x + 18
    by = y - h + 30
    bw = w - 36
    bh = h - 70

    # build plate
    c.setFillColor(colors.HexColor("#D8DEE5"))
    c.setStrokeColor(colors.HexColor("#AAB4BF"))
    c.rect(bx + 8, by, bw - 16, 10, fill=1, stroke=1)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 6.4)
    c.drawCentredString(bx + bw / 2, by - 10, "heated build plate / temporary mold floor")

    # mold walls
    wall_w = 28
    mold_x = bx + 30
    mold_y = by + 10
    mold_w = bw - 60
    mold_h = bh - 26
    c.setFillColor(ORANGE)
    c.setStrokeColor(ORANGE_DARK)
    c.roundRect(mold_x, mold_y, wall_w, mold_h, 2, fill=1, stroke=1)
    c.roundRect(mold_x + mold_w - wall_w, mold_y, wall_w, mold_h, 2, fill=1, stroke=1)
    c.rect(mold_x + wall_w, mold_y, mold_w - 2 * wall_w, 12, fill=1, stroke=1)

    # translucent cavity fill
    fill_x = mold_x + wall_w + 5
    fill_w = mold_w - 2 * wall_w - 10
    c.setFillColor(colors.Color(0.78, 0.09, 0.36, alpha=0.75))
    c.roundRect(fill_x, mold_y + 12, fill_w, mold_h * 0.63, 6, fill=1, stroke=0)
    c.setFillColor(colors.Color(0.78, 0.09, 0.36, alpha=0.18))
    c.roundRect(fill_x, mold_y + 12, fill_w, mold_h - 18, 6, fill=1, stroke=0)

    # nozzle
    nx = x + w / 2
    top = y - 18
    c.setFillColor(colors.HexColor("#434B56"))
    c.setStrokeColor(colors.HexColor("#242A31"))
    c.roundRect(nx - 13, top - 28, 26, 27, 4, fill=1, stroke=1)
    path = c.beginPath()
    path.moveTo(nx - 13, top - 28)
    path.lineTo(nx + 13, top - 28)
    path.lineTo(nx + 5.5, top - 50)
    path.lineTo(nx - 5.5, top - 50)
    path.close()
    c.drawPath(path, fill=1, stroke=1)
    c.setStrokeColor(MAGENTA)
    c.setLineWidth(2.0)
    c.line(nx, top - 50, nx, mold_y + mold_h * 0.74)
    c.setLineWidth(0.8)

    # port rim
    c.setStrokeColor(MAGENTA)
    c.setFillColor(colors.Color(0.78, 0.09, 0.36, alpha=0.15))
    c.ellipse(nx - 18, mold_y + mold_h - 13, nx + 18, mold_y + mold_h + 4, fill=1, stroke=1)

    # rising z arrow
    c.setStrokeColor(TEAL)
    c.setFillColor(TEAL)
    c.setLineWidth(1.4)
    c.line(mold_x + mold_w + 16, mold_y + 28, mold_x + mold_w + 16, mold_y + mold_h - 25)
    c.line(mold_x + mold_w + 16, mold_y + mold_h - 25, mold_x + mold_w + 11, mold_y + mold_h - 33)
    c.line(mold_x + mold_w + 16, mold_y + mold_h - 25, mold_x + mold_w + 21, mold_y + mold_h - 33)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(mold_x + mold_w + 22, mold_y + mold_h / 2, "optional")
    c.drawString(mold_x + mold_w + 22, mold_y + mold_h / 2 - 8, "rising Z")

    # labels
    def label(px: float, py: float, txt: str, col=INK) -> None:
        c.setFillColor(col)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(px, py, txt)

    label(mold_x - 5, mold_y + mold_h + 11, "PETG mold printed by tool 1", ORANGE_DARK)
    label(fill_x + 5, mold_y + 31, "PLA melt volume", MAGENTA)
    label(nx + 20, top - 34, "0.8 mm injection nozzle", INK)
    c.restoreState()


def draw_pipeline(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.saveState()
    c.setFillColor(colors.white)
    c.setStrokeColor(LIGHT2)
    c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)
    stages = [
        ("Named CAD bodies", "mold halves\\ninjected part\\nport marker", GREEN),
        ("Role classifier", "print mold\\nsuppress part\\nlocate port", TEAL),
        ("Volume solver", "mesh volume\\nE length\\nflow profile", MAGENTA),
        ("G-code emitter", "toolchange\\nheat/purge\\ninject + dwell", BLUE),
    ]
    box_w = (w - 48) / 4
    yy = y - 25
    for i, (title, body, col) in enumerate(stages):
        bx = x + 12 + i * (box_w + 8)
        c.setFillColor(colors.Color(col.red, col.green, col.blue, alpha=0.1))
        c.setStrokeColor(col)
        c.roundRect(bx, yy - 58, box_w, 58, 5, fill=1, stroke=1)
        c.setFillColor(col)
        c.setFont("Helvetica-Bold", 7.1)
        c.drawCentredString(bx + box_w / 2, yy - 12, title)
        c.setFillColor(INK)
        c.setFont("Helvetica", 6.5)
        for j, line in enumerate(body.split("\\n")):
            c.drawCentredString(bx + box_w / 2, yy - 27 - j * 9, line)
        if i < len(stages) - 1:
            ax = bx + box_w + 2
            ay = yy - 29
            c.setStrokeColor(GRAY)
            c.line(ax, ay, ax + 6, ay)
            c.line(ax + 6, ay, ax + 2, ay + 3)
            c.line(ax + 6, ay, ax + 2, ay - 3)
    c.restoreState()


def draw_model_roles(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.saveState()
    c.setFillColor(colors.white)
    c.setStrokeColor(LIGHT2)
    c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)
    base_y = y - h + 33
    centers = [x + w * 0.22, x + w * 0.50, x + w * 0.78]
    labels = [("Mold bodies", ORANGE), ("Injected part body", MAGENTA), ("Injection port marker", TEAL)]
    for cx, (lab, col) in zip(centers, labels):
        c.setFillColor(colors.Color(col.red, col.green, col.blue, alpha=0.13))
        c.setStrokeColor(col)
        if lab == "Mold bodies":
            c.rect(cx - 34, base_y, 22, 82, fill=1, stroke=1)
            c.rect(cx + 12, base_y, 22, 82, fill=1, stroke=1)
            c.setStrokeColor(ORANGE_DARK)
            c.line(cx - 12, base_y + 12, cx + 12, base_y + 12)
        elif lab == "Injected part body":
            c.roundRect(cx - 28, base_y + 10, 56, 58, 10, fill=1, stroke=1)
            c.setFillColor(colors.Color(col.red, col.green, col.blue, alpha=0.32))
            c.roundRect(cx - 18, base_y + 21, 36, 36, 8, fill=1, stroke=0)
        else:
            c.ellipse(cx - 21, base_y + 63, cx + 21, base_y + 83, fill=1, stroke=1)
            c.rect(cx - 10, base_y + 28, 20, 45, fill=1, stroke=1)
            c.ellipse(cx - 10, base_y + 22, cx + 10, base_y + 34, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7.1)
        c.drawCentredString(cx, y - 16, lab)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 6.3)
    c.drawCentredString(x + w / 2, y - h + 12, "The injected part and port marker drive process planning; they are not ordinary printable mold solids.")
    c.restoreState()


def draw_z_profile(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.saveState()
    c.setFillColor(colors.white)
    c.setStrokeColor(LIGHT2)
    c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)
    px = x + 34
    py = y - h + 28
    pw = w - 58
    ph = h - 58
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.7)
    c.line(px, py, px + pw, py)
    c.line(px, py, px, py + ph)
    c.setFont("Helvetica", 6.2)
    c.setFillColor(GRAY)
    c.drawCentredString(px + pw / 2, py - 14, "time / injected volume")
    c.saveState()
    c.translate(px - 21, py + ph / 2)
    c.rotate(90)
    c.drawCentredString(0, 0, "nozzle Z")
    c.restoreState()
    # Z trajectory
    pts = [(0.05, 0.18), (0.22, 0.18), (0.45, 0.42), (0.70, 0.68), (0.92, 0.83)]
    c.setStrokeColor(TEAL)
    c.setLineWidth(2)
    for (a, b), (c1, d) in zip(pts, pts[1:]):
        c.line(px + a * pw, py + b * ph, px + c1 * pw, py + d * ph)
    c.setFillColor(TEAL)
    for a, b in pts:
        c.circle(px + a * pw, py + b * ph, 2.1, fill=1, stroke=0)
    # flow pulses
    c.setFillColor(colors.Color(MAGENTA.red, MAGENTA.green, MAGENTA.blue, alpha=0.22))
    for i in range(10):
        bx = px + pw * (0.08 + i * 0.082)
        bh = ph * (0.18 + 0.02 * (i % 3))
        c.rect(bx, py, pw * 0.045, bh, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(px + 3, py + ph + 9, "Bottom-up/rising-Z injection schedule")
    c.setFont("Helvetica", 6.4)
    c.setFillColor(INK)
    c.drawString(px + 4, py + ph - 10, "Start near cavity floor; rise as the melt front fills.")
    c.restoreState()


def draw_process_window(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.saveState()
    c.setFillColor(colors.white)
    c.setStrokeColor(LIGHT2)
    c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)
    px = x + 35
    py = y - h + 31
    pw = w - 63
    ph = h - 62
    # colored operating regions
    regions = [
        (0.0, 0.0, 0.45, 0.45, colors.HexColor("#FADBD8"), "underfill / freezes"),
        (0.52, 0.0, 0.48, 0.48, colors.HexColor("#FDEBD0"), "too fast / unmelted"),
        (0.0, 0.55, 0.42, 0.45, colors.HexColor("#E8DAEF"), "leak / mold softens"),
        (0.34, 0.32, 0.38, 0.38, colors.HexColor("#D5F5E3"), "candidate window"),
    ]
    for rx, ry, rw, rh, col, lab in regions:
        c.setFillColor(col)
        c.setStrokeColor(colors.white)
        c.roundRect(px + rx * pw, py + ry * ph, rw * pw, rh * ph, 6, fill=1, stroke=1)
        c.setFillColor(INK)
        c.setFont("Helvetica", 5.9)
        c.drawCentredString(px + (rx + rw / 2) * pw, py + (ry + rh / 2) * ph, lab)
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.8)
    c.line(px, py, px + pw, py)
    c.line(px, py, px, py + ph)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 6.2)
    c.drawCentredString(px + pw / 2, py - 14, "volumetric flow rate")
    c.saveState()
    c.translate(px - 22, py + ph / 2)
    c.rotate(90)
    c.drawCentredString(0, 0, "injection temperature")
    c.restoreState()
    # nominal point
    c.setFillColor(MAGENTA)
    c.circle(px + 0.62 * pw, py + 0.58 * ph, 3.2, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 6.4)
    c.drawString(px + 0.62 * pw + 5, py + 0.58 * ph + 2, "test point")
    c.restoreState()


def draw_parameter_table(c: canvas.Canvas, x: float, y: float, w: float) -> float:
    rows = [
        ("Mold tool/material", "T1, 0.4 mm nozzle, PETG", "stable cavity, thermal margin"),
        ("Injection tool/material", "T2, 0.8 mm nozzle, PLA", "larger melt outlet, lower melt temp"),
        ("Initial geometry", "10 mm scale cup/cube", "fast iteration, low material risk"),
        ("Injection command", "part/cavity volume", "matches actual molded volume"),
        ("Near-term sweep", "240-275 C, 10-30 mm3/s", "map fill window before complex molds"),
    ]
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.1)
    c.drawString(x, y, "Parameter")
    c.drawString(x + w * 0.31, y, "Current value")
    c.drawString(x + w * 0.62, y, "Reason")
    y -= 7
    c.setStrokeColor(LIGHT2)
    c.line(x, y, x + w, y)
    y -= 9
    for i, (a, b, d) in enumerate(rows):
        if i % 2 == 0:
            c.setFillColor(colors.HexColor("#F8FAFC"))
            c.rect(x - 3, y - 3, w + 6, 15, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 6.2)
        c.drawString(x, y, a)
        c.setFont("Helvetica", 6.2)
        c.drawString(x + w * 0.31, y, b)
        c.drawString(x + w * 0.62, y, d)
        y -= 16
    return y


def draw_validation_matrix(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.saveState()
    c.setFillColor(colors.HexColor("#FBFCFE"))
    c.setStrokeColor(LIGHT2)
    c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8.3)
    c.drawString(x + 10, y - 15, "Validation measurements for the first paper-quality dataset")
    cols = [0.0, 0.24, 0.49, 0.74, 1.0]
    heads = ["Variable", "Sweep", "Primary metric", "Failure label"]
    row_y = y - 31
    c.setFillColor(colors.HexColor("#EAF3F8"))
    c.rect(x + 9, row_y - 4, w - 18, 14, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 6.6)
    for i, head in enumerate(heads):
        c.drawString(x + 13 + cols[i] * (w - 26), row_y, head)
    rows = [
        ("Nozzle temp", "240, 255, 275 C", "bottom fill depth", "freezing"),
        ("Flow rate", "10, 20, 30 mm3/s", "delivered mass", "under/over-extrusion"),
        ("Port geometry", "diameter + chamfer", "leakage and blockage", "port failure"),
        ("Z schedule", "top pour vs rising-Z", "voids and fill front", "trapped air"),
    ]
    row_y -= 16
    c.setFont("Helvetica", 6.2)
    c.setFillColor(INK)
    for i, row in enumerate(rows):
        if i % 2 == 1:
            c.setFillColor(colors.HexColor("#F4F7FA"))
            c.rect(x + 9, row_y - 4, w - 18, 13, fill=1, stroke=0)
            c.setFillColor(INK)
        for j, cell in enumerate(row):
            c.drawString(x + 13 + cols[j] * (w - 26), row_y, cell)
        row_y -= 14
    c.restoreState()


def title_page(c: canvas.Canvas) -> None:
    draw_header(c, 1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(MARGIN, H - 65, "Magma")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, H - 85, "Hybrid FFF-Printed Mold Injection on a Multi-Tool Desktop Printer")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 8.2)
    c.drawString(MARGIN, H - 101, "Brian Machado and collaborators | Internal research manuscript | June 2026")
    c.setStrokeColor(TEAL)
    c.setLineWidth(2)
    c.line(MARGIN, H - 111, W - MARGIN, H - 111)

    # Abstract box
    ax, ay, aw, ah = MARGIN, H - 130, W - 2 * MARGIN, 107
    c.setFillColor(colors.HexColor("#EEF7F8"))
    c.setStrokeColor(colors.HexColor("#C4E3E7"))
    c.roundRect(ax, ay - ah, aw, ah, 5, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9.2)
    c.drawString(ax + 12, ay - 16, "ABSTRACT")
    abstract = (
        "We present Magma, an experimental hybrid manufacturing workflow in which a desktop multi-tool fused "
        "filament fabrication printer first fabricates a thermoplastic mold and then uses a second heated tool "
        "as a low-pressure melt delivery system. The near-term platform is a Prusa XL-style printer configured "
        "with a PETG mold tool and a larger PLA injection nozzle. Unlike infill reinforcement approaches, the "
        "target part is represented as a separate molded volume: the slicer or post-processor suppresses that "
        "body from normal printing, computes its volume, locates an injection port, and emits a controlled "
        "toolchange, heating, and extrusion sequence. Early trials show that injected melt can be delivered "
        "into printed cavities, but reliable filling depends on port geometry, thermal management, flow rate, "
        "tool pickup sequencing, and collision-safe nozzle motion."
    )
    paragraph(c, ax + 12, ay - 30, aw - 24, abstract, font="Times-Roman", size=8.4, leading=9.7)

    lx, rx = MARGIN, MARGIN + COL_W + GUTTER
    y = ay - ah - 23
    y1 = section_title(c, lx, y, "1. Introduction")
    intro = (
        "Fused filament fabrication is effective for rapid iteration, but its final parts inherit the limitations "
        "of layer-wise bead deposition: anisotropic bonding, visible toolpaths, and flow histories that are very "
        "different from molded plastic. Injection molding provides dense parts with continuous melt flow, yet "
        "usually requires machined tooling, clamping, and a dedicated press. Magma investigates a smaller and "
        "more accessible middle ground: using the printer itself to fabricate a mold and then using another "
        "printer toolhead to fill that mold with molten thermoplastic.\n\n"
        "The initial goal is deliberately simple. Rather than starting with a sealed, high-pressure injection "
        "system, the project begins with cup-like and block-like molds that can be filled through a top opening. "
        "This establishes the thermal and geometric process window before moving to split molds, modeled ports, "
        "or more complex part shapes."
    )
    y1 = paragraph(c, lx, y1, COL_W, intro)
    y1 = section_title(c, lx, y1 - 5, "Contributions")
    y1 = bullet_list(
        c,
        lx,
        y1,
        COL_W,
        [
            ("Hybrid process", "a two-stage print-then-inject workflow on an existing multi-tool FFF platform"),
            ("Model roles", "separate mold, injected part, and port-marker bodies in CAD rather than a single printable mesh"),
            ("Volume-driven extrusion", "filament length computed from the desired molded volume instead of arbitrary purge length"),
            ("Slicer path", "a Phase 0 G-code post-processor with a roadmap toward native Orca/Prusa-style integration"),
        ],
    )

    draw_system_diagram(c, rx, y, COL_W, 248)
    draw_caption(
        c,
        rx,
        y - 257,
        COL_W,
        "Figure 1.",
        "Conceptual cross-section. Tool 1 prints a PETG mold; tool 2 injects PLA through a port. "
        "Later versions can start lower in the cavity and rise during extrusion.",
    )

    boxed_note(
        c,
        rx,
        165,
        COL_W,
        74,
        "Key distinction",
        "The project is not simply depositing material into sparse infill. The desired workflow treats the molded "
        "part as a separate designed volume and uses the printed geometry as temporary or functional tooling.",
    )


def page_two(c: canvas.Canvas) -> None:
    draw_header(c, 2)
    y = H - 47
    draw_pipeline(c, MARGIN, y, W - 2 * MARGIN, 98)
    draw_caption(
        c,
        MARGIN,
        y - 108,
        W - 2 * MARGIN,
        "Figure 2.",
        "Planned software pipeline. Named CAD bodies let the slicer classify the printable mold separately "
        "from the injected volume and the port marker.",
    )
    lx, rx = MARGIN, MARGIN + COL_W + GUTTER
    ytop = y - 132
    yl = section_title(c, lx, ytop, "2. System Method")
    body = (
        "The printer is treated as a programmable thermal material-delivery platform. During the first stage, a "
        "standard FFF slicing pass produces the mold walls, floor, split bodies, or test cup. During the second "
        "stage, the printer selects the injection tool, raises it to the injection temperature, moves to the port, "
        "and extrudes a calculated melt volume.\n\n"
        "The working hardware configuration separates accuracy from throughput. A smaller nozzle is used for the "
        "PETG mold because wall definition and port geometry matter. A larger nozzle is used for PLA injection "
        "because the operation is volumetric and benefits from lower back-pressure. A 0.8 mm injection nozzle is "
        "large enough to test high flow while still fitting a desktop toolhead envelope."
    )
    yl = paragraph(c, lx, yl, COL_W, body)
    yl = section_title(c, lx, yl - 3, "Volume Model")
    vol = (
        "The injected filament length is computed from cavity volume rather than tuned by eye. For filament "
        "diameter d_f and desired injected volume V_i, the commanded extrusion length is:"
    )
    yl = paragraph(c, lx, yl, COL_W, vol)
    c.setFillColor(colors.HexColor("#F8FAFC"))
    c.setStrokeColor(LIGHT2)
    c.roundRect(lx, yl - 42, COL_W, 37, 4, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(lx + COL_W / 2, yl - 23, "E = 4 V_i / (pi d_f^2)")
    yl -= 55
    yl = paragraph(
        c,
        lx,
        yl,
        COL_W,
        "A multiplier can compensate for leakage, shrinkage, port dead volume, or intentional overfill.",
        font="Helvetica",
        size=7.3,
        leading=8.6,
    )

    yr = section_title(c, rx, ytop, "3. Software Implementation")
    sw = (
        "The current fast-learning path is a G-code post-processor. The local prototype, magma_inject.py, can "
        "take a sliced mold and splice an injection sequence before the end code. Its cavity detector can rasterize "
        "extruded G-code paths and flood-fill enclosed empty regions, or use STL geometry to detect an open pocket. "
        "It then estimates cavity volume, maps the injection XY location, and emits an XL-style toolchange and "
        "injection block.\n\n"
        "A native slicer implementation should expose the same operation as a normal process feature. The user "
        "should be able to import a STEP assembly, assign roles to bodies, preview the mold and injection path, "
        "and export G-code without hand editing coordinates."
    )
    yr = paragraph(c, rx, yr, COL_W, sw)
    yr = section_title(c, rx, yr - 3, "Native Settings")
    yr = bullet_list(
        c,
        rx,
        yr,
        COL_W,
        [
            ("Geometry", "mold bodies, injected part body, port marker, optional vent bodies"),
            ("Thermal", "tool selection, target nozzle temperature, dwell, mold/bed preheat"),
            ("Flow", "target mm3/s, volume multiplier, extrusion chunking, firmware-safe maximums"),
            ("Motion", "start Z, end Z, plunge depth, rising-Z schedule, collision envelope"),
            ("Preview", "cutaway mold display, colored injected volume, port and vent annotations"),
        ],
    )
    draw_model_roles(c, MARGIN, 188, W - 2 * MARGIN, 118)
    draw_caption(
        c,
        MARGIN,
        61,
        W - 2 * MARGIN,
        "Figure 3.",
        "Role-based modeling convention. The injected part body is used for process planning and visualization, "
        "while the mold bodies are the geometry actually printed by the FFF stage.",
    )


def page_three(c: canvas.Canvas) -> None:
    draw_header(c, 3)
    lx, rx = MARGIN, MARGIN + COL_W + GUTTER
    y = H - 48
    yl = section_title(c, lx, y, "4. Experimental Protocol")
    exp = (
        "The first experiments are intentionally small. A 10 mm-scale cup, cylinder, or cube-shaped cavity can be "
        "printed quickly, filled with little material, and inspected immediately. This makes the process suitable "
        "for rapid parameter sweeps before moving to a Benchy-derived cavity or a realistic split mold.\n\n"
        "The mold should be sliced as a single mold material; the injection port must be a real opening into the "
        "cavity, not a separate solid body printed on top. For the native slicer path, the port marker may be a "
        "non-printing body used only to identify the injection location."
    )
    yl = paragraph(c, lx, yl, COL_W, exp)
    yl = section_title(c, lx, yl - 3, "Test Sequence")
    yl = bullet_list(
        c,
        lx,
        yl,
        COL_W,
        [
            ("Print mold", "PETG mold walls and cavity, preferably without avoidable top closure over the port"),
            ("Prepare tool", "select PLA injection tool, heat to target temperature, purge/clean if needed"),
            ("Fill cavity", "extrude computed volume at controlled mm3/s; optionally move upward in Z"),
            ("Inspect", "record fill depth, leakage, port blockage, mold deformation, stringing, and removal quality"),
        ],
    )
    draw_parameter_table(c, lx, yl - 2, COL_W)

    draw_z_profile(c, rx, y, COL_W, 163)
    draw_caption(
        c,
        rx,
        y - 173,
        COL_W,
        "Figure 4.",
        "Rising-Z injection concept. Starting closer to the cavity floor may reduce bottom underfill and freezing.",
    )
    draw_process_window(c, rx, y - 213, COL_W, 160)
    draw_caption(
        c,
        rx,
        y - 383,
        COL_W,
        "Figure 5.",
        "Expected process window. Too little heat or flow freezes early; excessive flow can exceed hotend melting "
        "capacity or firmware limits.",
    )
    yy = y - 427
    yy = section_title(c, rx, yy, "5. Preliminary Findings")
    findings = (
        "Transcripted test work supports the feasibility of the concept while exposing a narrow operating window. "
        "The team successfully uploaded and ran custom G-code, printed small mold-like geometries, and observed "
        "molten plastic delivery into a cavity. The most important failure modes were insufficient delivered "
        "volume, bottom underfill, blocked or misinterpreted ports, tool temperature uncertainty during pickup, "
        "and messy extrusion when flow was not matched to hotend heating capacity.\n\n"
        "These results motivate a controlled sweep of temperature, flow rate, nozzle diameter, port diameter, and "
        "Z schedule before treating the process as a robust slicer feature."
    )
    paragraph(c, rx, yy, COL_W, findings)


def page_four(c: canvas.Canvas) -> None:
    draw_header(c, 4)
    lx, rx = MARGIN, MARGIN + COL_W + GUTTER
    y = H - 48
    yl = section_title(c, lx, y, "6. Discussion")
    disc = (
        "Magma differs from conventional injection molding in pressure, thermal mass, and tooling stiffness. A "
        "desktop hotend cannot instantly melt arbitrary flow rates, and a printed mold can soften, leak, or block "
        "if its port geometry is poorly designed. The process is therefore best understood as low-pressure molded "
        "deposition into additively manufactured tooling. This framing is useful because it avoids overclaiming "
        "while still capturing the practical opportunity: a programmable printer can run both the tooling step and "
        "the material-delivery step in one setup.\n\n"
        "The main engineering risk is visibility. A slicer preview of normal toolpaths does not reveal whether the "
        "cavity is open, whether the injected part body lines up with the mold, or whether the toolhead can safely "
        "approach the port. A credible implementation must make those states explicit."
    )
    yl = paragraph(c, lx, yl, COL_W, disc)
    yl = section_title(c, lx, yl - 4, "Limitations")
    yl = bullet_list(
        c,
        lx,
        yl,
        COL_W,
        [
            ("Pressure", "current experiments are pour-like and do not create industrial packing pressure"),
            ("Heat transfer", "the injected material may freeze before filling tall or thin cavities"),
            ("Venting", "air escape and overflow reservoirs are required for closed molds"),
            ("Preview fidelity", "the injected volume is not a normal printed toolpath and needs a dedicated view"),
        ],
    )

    yr = section_title(c, rx, y, "7. Development Roadmap")
    yr = bullet_list(
        c,
        rx,
        yr,
        COL_W,
        [
            ("Phase 0", "post-process G-code for simple open cavities and manual parameter sweeps"),
            ("Phase 1", "native slicer settings for injection volume, port location, tool selection, and preview"),
            ("Phase 2", "CAD role import from named STEP bodies with mold/part/port validation"),
            ("Phase 3", "rising-Z fill paths, vents, overflow channels, and collision checking"),
            ("Phase 4", "mechanical and dimensional benchmarks against conventional FFF parts"),
        ],
    )
    boxed_note(
        c,
        rx,
        yr - 2,
        COL_W,
        85,
        "Near-term experiment",
        "Use a 10 mm cavity with a real top port, sweep PLA injection from 240-275 C and 10-30 mm3/s, and record "
        "fill depth, leakage, and bottom completeness. The first paper-quality dataset should be simple enough "
        "that failures are interpretable.",
    )

    draw_validation_matrix(c, MARGIN, 436, W - 2 * MARGIN, 98)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, 275, "8. CONCLUSION")
    c.setStrokeColor(TEAL)
    c.line(MARGIN, 272, MARGIN + 58, 272)
    conclusion = (
        "Magma shows a plausible route to desktop-scale hybrid molding using hardware that already exists on "
        "multi-tool FFF printers. The concept is strongest when the slicer understands three separate roles: the "
        "printable mold, the non-printing injected part volume, and the injection port. The current G-code "
        "post-processing path is sufficient for process discovery, while a native slicer workflow is needed for "
        "repeatable geometry handling, preview, and safety. The next critical step is a clean experimental matrix "
        "that quantifies the fill window before scaling to complex molds."
    )
    paragraph(c, MARGIN, 260, W - 2 * MARGIN, conclusion, size=8.4, leading=10.2)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, 153, "REFERENCES")
    c.setStrokeColor(TEAL)
    c.line(MARGIN, 150, MARGIN + 58, 150)
    refs = [
        "[1] ISO/ASTM 52900:2021, Additive manufacturing - General principles - Fundamentals and vocabulary.",
        "[2] Prusa Research, Original Prusa XL product and technical documentation.",
        "[3] Prusa Research, PrusaSlicer open-source repository, github.com/prusa3d/PrusaSlicer.",
        "[4] SoftFever, OrcaSlicer open-source repository, github.com/SoftFever/OrcaSlicer.",
        "[5] Local Magma prototype, magma_inject.py post-processor and generated test G-code, June 2026.",
    ]
    yy = 138
    c.setFillColor(INK)
    c.setFont("Times-Roman", 7.2)
    for ref in refs:
        for line in wrap(ref, "Times-Roman", 7.2, W - 2 * MARGIN):
            c.drawString(MARGIN, yy, line)
            yy -= 8.3
        yy -= 2


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=letter)
    c.setTitle("Magma: Hybrid FFF-Printed Mold Injection on a Multi-Tool Desktop Printer")
    c.setAuthor("Brian Machado and collaborators")
    title_page(c)
    c.showPage()
    page_two(c)
    c.showPage()
    page_three(c)
    c.showPage()
    page_four(c)
    c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()
