#!/usr/bin/env python3
"""Generate the homepage architecture diagram: a committed SVG of the
five-layer URML stack, a validator gate on the left, and a domain-profiles
pill on the right.

Why this exists: the current urml.dev homepage shows "LAYER STACK" as plain
text. A first-time roboticist gets the conceptual frame faster from one
clean diagram than from prose. This asset gives them that frame in a
single image, with three things made visually explicit that the text
cannot say:

  * The validator is a gate between L4 and L1, not a footnote.
  * L0 is named (substrate), not specified by URML — drawn dashed and dim.
  * Domain profiles attach orthogonally to L3 and L2, not as a sixth layer.

Design constraints (match the hero SVG ethos in gen_demo_svg.py):

  * Pure standard library. No SVG libraries, no Node, no headless browser.
    Runs in the bootstrap venv on every OS including the founder's Windows
    box. Zero new dependency.
  * Deterministic: no timestamps, no random ids. Re-running produces a
    byte-identical file (clean diffs, regenerable).
  * Honest: layer titles and bodies come from a shared module
    (``_urml_layers.LAYERS``) that the guard test pins to
    ``docs/architecture.md``. The diagram cannot drift from the canonical
    layer doc.
  * GitHub renders SVG embedded as ``<img>`` and animates pure CSS
    ``@keyframes`` only. No ``<script>``, no SMIL ``<animate>``.

Regenerate: ``python tools/scripts/gen_architecture_svg.py`` (or
``make architecture-record``). Output: ``docs/assets/architecture-stack.svg``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _urml_layers import LAYERS, PROFILES  # noqa: E402

# --- Brand palette (mirrors gen_demo_svg.py; same visual identity) --------
BG = "#181715"        # canvas
BAR = "#26241f"       # titlebar
FG = "#e8e4da"        # primary text on dark
ACCENT = "#cc6b1f"    # layer ids, validator rail, pill border, connectors
DIM = "#8a857a"       # L0 text, captions, secondary text

# --- Layout ---------------------------------------------------------------
WIDTH = 1085

BAR_H = 34            # titlebar
TOP_GAP = 18          # gap below titlebar before first row
ROW_H = 72            # per-layer row height
ROWS = len(LAYERS)    # 5
CAPTION_H = 44        # caption strip at the bottom

PAD_X = 22
RAIL_W = 38           # validator rail width
RAIL_GAP = 12         # gap between rail and layer rows
PILL_W = 196          # profiles pill width
PILL_GAP = 14         # gap between layer rows and pill

ROW_LEFT = PAD_X + RAIL_W + RAIL_GAP                       # 22+38+12 = 72
ROW_RIGHT = WIDTH - PAD_X - PILL_W - PILL_GAP              # 1085-22-196-14 = 853
ROW_W = ROW_RIGHT - ROW_LEFT                               # 781

ROWS_TOP = BAR_H + TOP_GAP                                 # 52
ROWS_BOTTOM = ROWS_TOP + ROWS * ROW_H                      # 52 + 360 = 412
HEIGHT = ROWS_BOTTOM + CAPTION_H                           # 456

# Validator rail spans L4..L1 only (4 rows). The gate stops at the spec
# boundary; making this visible is the whole point of the diagram.
RAIL_X = PAD_X
RAIL_Y = ROWS_TOP
RAIL_H = 4 * ROW_H                                         # 288

# Pill is vertically centred across the L3 and L2 rows.
PILL_Y = ROWS_TOP + ROW_H + (ROW_H // 2) - 12              # roughly centred
PILL_X = ROW_RIGHT + PILL_GAP
PILL_H = ROW_H + 24

TITLE = "urml · architecture · spec covers L4..L1 · L0 substrate is not part of URML"
CAPTION = ("every program checked against capability manifest and safety "
           "envelope before any actuator moves")


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _row_y(i: int) -> int:
    """Top edge of layer row i (0 = L4 at top, 4 = L0 at bottom)."""
    return ROWS_TOP + i * ROW_H


def _layer_rect(i: int, is_l0: bool) -> str:
    y = _row_y(i)
    stroke_dash = ' stroke-dasharray="4 4"' if is_l0 else ""
    return (
        f'<rect x="{ROW_LEFT}" y="{y}" width="{ROW_W}" height="{ROW_H - 8}" '
        f'rx="6" fill="{BG}" stroke="{DIM}" stroke-width="1"{stroke_dash}/>'
    )


def _layer_text(i: int, lid: str, title: str, body: str, is_l0: bool) -> str:
    y = _row_y(i)
    label_color = DIM if is_l0 else ACCENT
    title_color = DIM if is_l0 else FG
    body_color = DIM
    # Layer ID badge: vertical centred on first text line.
    lid_x = ROW_LEFT + 16
    title_x = ROW_LEFT + 76
    title_y = y + 28
    body_y = y + 50
    return (
        f'<text x="{lid_x}" y="{title_y}" class="lid" '
        f'style="fill:{label_color}">{_esc(lid)}</text>'
        f'<text x="{title_x}" y="{title_y}" class="ltitle" '
        f'style="fill:{title_color}">{_esc(title)}</text>'
        f'<text x="{title_x}" y="{body_y}" class="lbody" '
        f'style="fill:{body_color}">{_esc(body)}</text>'
    )


def _validator_rail() -> str:
    # Rail body (filled, pulsing opacity via CSS).
    rail = (
        f'<rect class="rail" x="{RAIL_X}" y="{RAIL_Y}" '
        f'width="{RAIL_W}" height="{RAIL_H}" rx="6" '
        f'fill="{BG}" stroke="{ACCENT}" stroke-width="1"/>'
    )
    # Vertical rail label, rotated -90 around its own anchor.
    label_cx = RAIL_X + RAIL_W // 2
    label_cy = RAIL_Y + RAIL_H // 2
    label = (
        f'<text class="rlabel" x="{label_cx}" y="{label_cy}" '
        f'transform="rotate(-90 {label_cx} {label_cy})" '
        f'style="fill:{ACCENT}">VALIDATOR · 5 PASSES</text>'
    )
    # Tick marks bridging the rail into L4..L1 (NOT L0).
    ticks: list[str] = []
    tick_x1 = RAIL_X + RAIL_W
    tick_x2 = ROW_LEFT
    for i in range(4):  # L4..L1 only
        y = _row_y(i) + (ROW_H - 8) // 2
        ticks.append(
            f'<line x1="{tick_x1}" y1="{y}" x2="{tick_x2}" y2="{y}" '
            f'stroke="{ACCENT}" stroke-width="1"/>'
        )
    return rail + label + "".join(ticks)


def _profiles_pill() -> str:
    rect = (
        f'<rect x="{PILL_X}" y="{PILL_Y}" width="{PILL_W}" height="{PILL_H}" '
        f'rx="10" fill="{BG}" stroke="{ACCENT}" stroke-width="1"/>'
    )
    header = (
        f'<text x="{PILL_X + 14}" y="{PILL_Y + 24}" class="ptitle" '
        f'style="fill:{ACCENT}">PROFILES</text>'
    )
    lines: list[str] = []
    for j, name in enumerate(PROFILES):
        lines.append(
            f'<text x="{PILL_X + 14}" y="{PILL_Y + 48 + j * 20}" '
            f'class="pname" style="fill:{FG}">{_esc(name)}</text>'
        )
    # Connector lines from pill left edge into L3 and L2 right edges.
    cx1 = ROW_RIGHT
    cx2 = PILL_X
    l3_y = _row_y(1) + (ROW_H - 8) // 2
    l2_y = _row_y(2) + (ROW_H - 8) // 2
    connectors = (
        f'<line x1="{cx1}" y1="{l3_y}" x2="{cx2}" y2="{l3_y}" '
        f'stroke="{ACCENT}" stroke-width="1"/>'
        f'<line x1="{cx1}" y1="{l2_y}" x2="{cx2}" y2="{l2_y}" '
        f'stroke="{ACCENT}" stroke-width="1"/>'
    )
    return rect + header + "".join(lines) + connectors


def render_svg() -> str:
    style = (
        "text{font-family:ui-monospace,'SF Mono',SFMono-Regular,Menlo,"
        "Consolas,'Liberation Mono',monospace;white-space:pre}"
        ".titletext{font-size:12px}"
        ".lid{font-size:15px;font-weight:600}"
        ".ltitle{font-size:15px;font-weight:600}"
        ".lbody{font-size:12px}"
        ".rlabel{font-size:12px;font-weight:600;text-anchor:middle;"
        "dominant-baseline:middle;letter-spacing:1px}"
        ".ptitle{font-size:11px;font-weight:600;letter-spacing:1px}"
        ".pname{font-size:13px}"
        ".caption{font-size:12px}"
        ".rail{animation:pulse 4s ease-in-out infinite}"
        "@keyframes pulse{0%,100%{opacity:0.55}50%{opacity:1}}"
    )

    aria = (
        "URML architecture: five-layer stack. Layer 4 natural language "
        "interface, Layer 3 behavior composition, Layer 2 intent primitives, "
        "Layer 1 hardware abstraction, Layer 0 substrate (not part of URML). "
        "A validator runs five passes across layers 4 through 1 before any "
        "actuator moves. Domain profiles extend layers 3 and 2."
    )

    rows: list[str] = []
    for i, (lid, title, body) in enumerate(LAYERS):
        is_l0 = lid == "L0"
        rows.append(_layer_rect(i, is_l0))
        rows.append(_layer_text(i, lid, title, body, is_l0))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" role="img" '
        f'aria-label="{_esc(aria)}">\n'
        f"<style>{style}</style>\n"
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="{BG}"/>\n'
        f'<rect width="{WIDTH}" height="{BAR_H}" rx="10" fill="{BAR}"/>\n'
        f'<rect y="{BAR_H - 10}" width="{WIDTH}" height="10" fill="{BAR}"/>\n'
        f'<text x="{PAD_X}" y="22" class="titletext" '
        f'style="fill:{DIM}">{_esc(TITLE)}</text>\n'
        f"{_validator_rail()}\n"
        f'{"".join(rows)}\n'
        f"{_profiles_pill()}\n"
        f'<text x="{PAD_X}" y="{HEIGHT - 16}" class="caption" '
        f'style="fill:{DIM}">{_esc(CAPTION)}</text>\n'
        f"</svg>\n"
    )


def main() -> None:
    out = Path(__file__).resolve().parents[2] / "docs" / "assets" / "architecture-stack.svg"
    out.write_text(render_svg(), encoding="utf-8", newline="\n")
    print(f"wrote {out} ({out.stat().st_size} bytes, {len(LAYERS)} layers)")


if __name__ == "__main__":
    main()
