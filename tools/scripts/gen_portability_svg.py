#!/usr/bin/env python3
"""Generate the "one intent, many bodies" portability SVG: a committed
three-column comparison showing the same URML program executed against
three different body manifests (multirotor, quadruped, differential AMR).

Why this exists: substrate independence is URML's core claim, but until
now it lived only in prose ("our 14 runtimes…") and in the CompositeAdapter
docstring. A reader scanning the README had no single image proving
*the same intent file* runs unchanged across body classes. This asset
closes that gap.

Design constraints (match gen_demo_svg.py and the repo ethos):

  * Pure standard library. No asciinema, no ffmpeg, no Node.
  * Deterministic: no timestamps, no random ids. Re-running produces a
    byte-identical file.
  * Honest: every trace line shown here is real `urml execute` output,
    asserted byte-for-byte against a live hermetic run by
    `reference/validator/tests/test_portability_svg.py`. Nothing
    fabricated.
  * Static (no CSS animation). The hero is a typewriter narrative;
    this is a comparison. Animation would distract.

Regenerate: `python tools/scripts/gen_portability_svg.py`
            (or `make portability-record`).
Output: `docs/assets/one-intent-many-bodies.svg`.
"""

from __future__ import annotations

from pathlib import Path

# --- Brand palette (matches gen_demo_svg.py) -------------------------------
BG = "#181715"
BAR = "#26241f"
FG = "#e8e4da"
ACCENT = "#cc6b1f"
DIM = "#8a857a"
OK = "#7fae5f"
COL_BG = "#1f1d1a"   # slightly lighter than BG, marks each column

# --- The program (committed at examples/portability/inspect.urml.yaml) -----
# Shown verbatim in the top half of the asset.
PROGRAM_LINES: list[str] = [
    "profile: home",
    "behavior:",
    "  type: sequence",
    "  on_error: abort_and_report",
    "  steps:",
    "    - move_to:",
    "        location: inspection_point",
    "    - detect:",
    "        object: person",
    "        store_as: people_in_view",
    "    - report:",
    "        to: ops",
    "        facts:",
    "          inspected: site",
]

# --- The three bodies ------------------------------------------------------
# Each column's trace is real `urml execute --adapter mock` output against
# that manifest. The trace text is identical across bodies (the mock is
# substrate-neutral); the *manifest* is what differs, which is the point.
#
# ASSERTED_TRACE_LINES are checked byte-for-byte by the guard test against
# a live in-process run. The body labels and command lines are NOT asserted
# (they are layout chrome).

ASSERTED_TRACE_LINES: list[str] = [
    "  trace (3 step(s) executed, 3 adapter call(s)):",
    "   1. send_navigation_goal  location=inspection_point",
    "   2. query_detection  object_class=person",
    "   3. emit_report  to=ops facts={'inspected': 'site'} status=success severity=info",
    "  RESULT: SUCCESS (3 step(s) executed)",
]

# Per-column metadata. Each tuple is (header, drive_type, manifest_path).
# The command line shown is the one the reader can copy verbatim.
COLUMNS: list[tuple[str, str, str]] = [
    ("DRONE",     "multirotor   · 12.0 m/s",  "drone.manifest.yaml"),
    ("QUADRUPED", "quadruped    ·  1.6 m/s",  "legged.manifest.yaml"),
    ("AMR",       "differential ·  1.0 m/s",  "mobile.manifest.yaml"),
]

# What each column shows under its header. The trace is the same; chrome
# differs. Lines flagged "out" are part of ASSERTED_TRACE_LINES.
COLUMN_BODY: list[tuple[str, str]] = [
    ("cmd", "$ urml execute inspect.urml.yaml \\"),
    ("cmd", "      -m <manifest> --adapter mock --no-policy"),
    ("gap", ""),
    ("out", "  trace (3 step(s) executed,"),
    ("out", "         3 adapter call(s)):"),
    ("out", "   1. send_navigation_goal"),
    ("out", "        location=inspection_point"),
    ("out", "   2. query_detection"),
    ("out", "        object_class=person"),
    ("out", "   3. emit_report"),
    ("out", "        to=ops"),
    ("out", "        facts={'inspected': 'site'}"),
    ("gap", ""),
    ("out", "  RESULT: SUCCESS"),
]

TITLE = "urml · one intent · many bodies · same program file"
CAPTION = ("same .urml.yaml file, three substrates. the manifest is the "
           "bridge. no code change between bodies.")

# --- Layout ----------------------------------------------------------------
CHAR_W = 7.6
FONT = 13
LH = 20
PAD = 20

BAR_H = 34
TITLE_GAP = 28              # space below the title bar
SECTION_GAP = 18            # space between program block and columns
CAPTION_GAP = 28

PROGRAM_HEADER = "THE PROGRAM  (examples/portability/inspect.urml.yaml)"
PROGRAM_TOP = BAR_H + TITLE_GAP + LH      # first program line baseline
PROGRAM_BOT = PROGRAM_TOP + len(PROGRAM_LINES) * LH

COL_TOP = PROGRAM_BOT + SECTION_GAP       # top of column boxes (y of header)
COL_HEADER_LINES = 3                      # body name, drive_type, command label
COL_BODY_TOP = COL_TOP + (COL_HEADER_LINES + 1) * LH  # first body-line baseline
COL_BOT = COL_BODY_TOP + len(COLUMN_BODY) * LH

HEIGHT = COL_BOT + CAPTION_GAP + 16

COL_W = 320
COL_GAP = 16
WIDTH = PAD * 2 + 3 * COL_W + 2 * COL_GAP


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _color(kind: str, text: str) -> str:
    if kind == "cmd":
        return ACCENT
    if "RESULT: SUCCESS" in text:
        return OK
    if kind == "hdr":
        return DIM
    return FG


def render_svg() -> str:
    out: list[str] = []

    # Terminal bar with traffic-light dots (same as hero).
    out.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="{BG}"/>')
    out.append(f'<rect width="{WIDTH}" height="{BAR_H}" rx="10" fill="{BAR}"/>')
    out.append(f'<rect y="{BAR_H - 10}" width="{WIDTH}" height="10" fill="{BAR}"/>')
    out.append('<circle cx="20" cy="17" r="6" fill="#e06c5a"/>')
    out.append('<circle cx="40" cy="17" r="6" fill="#e0b04a"/>')
    out.append(f'<circle cx="60" cy="17" r="6" fill="{OK}"/>')
    out.append(
        f'<text x="84" y="22" class="chrome">{_esc(TITLE)}</text>'
    )

    # Program block header.
    y = BAR_H + TITLE_GAP
    out.append(
        f'<text x="{PAD}" y="{y}" class="chrome" style="fill:{DIM}">'
        f"{_esc(PROGRAM_HEADER)}</text>"
    )

    # Program body.
    for i, line in enumerate(PROGRAM_LINES):
        ly = PROGRAM_TOP + i * LH
        out.append(
            f'<text x="{PAD}" y="{ly}" class="ln">{_esc(line)}</text>'
        )

    # Three columns.
    for c, (head, drive, mpath) in enumerate(COLUMNS):
        x0 = PAD + c * (COL_W + COL_GAP)
        # Column background.
        out.append(
            f'<rect x="{x0}" y="{COL_TOP - LH + 4}" width="{COL_W}" '
            f'height="{COL_BOT - COL_TOP + LH - 4}" rx="6" fill="{COL_BG}"/>'
        )
        # Column header (body name + drive_type + manifest path).
        out.append(
            f'<text x="{x0 + 12}" y="{COL_TOP}" class="ln" '
            f'style="fill:{ACCENT};font-weight:bold">{_esc(head)}</text>'
        )
        out.append(
            f'<text x="{x0 + 12}" y="{COL_TOP + LH}" class="ln" '
            f'style="fill:{DIM}">{_esc(drive)}</text>'
        )
        out.append(
            f'<text x="{x0 + 12}" y="{COL_TOP + 2 * LH}" class="ln" '
            f'style="fill:{DIM}">-m {_esc(mpath)}</text>'
        )
        # Column body (per-column trace).
        for i, (kind, line) in enumerate(COLUMN_BODY):
            if kind == "gap":
                continue
            ly = COL_BODY_TOP + i * LH
            out.append(
                f'<text x="{x0 + 12}" y="{ly}" class="ln" '
                f'style="fill:{_color(kind, line)}">{_esc(line)}</text>'
            )

    # Caption.
    out.append(
        f'<text x="{PAD}" y="{HEIGHT - 12}" class="chrome" '
        f'style="fill:{DIM}">{_esc(CAPTION)}</text>'
    )

    style = (
        f"text{{font-family:ui-monospace,'SF Mono',SFMono-Regular,Menlo,"
        f"Consolas,'Liberation Mono',monospace;white-space:pre}}"
        f".ln{{font-size:{FONT}px;fill:{FG}}}"
        f".chrome{{font-size:12px;fill:{DIM}}}"
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" role="img" '
        f'aria-label="One URML program executed against three different body '
        f'manifests (multirotor, quadruped, differential AMR) — same intent '
        f'file, three substrates, no code change.">\n'
        f"<style>{style}</style>\n"
        + "\n".join(out)
        + "\n</svg>\n"
    )


def main() -> None:
    out_path = (
        Path(__file__).resolve().parents[2]
        / "docs" / "assets" / "one-intent-many-bodies.svg"
    )
    out_path.write_text(render_svg(), encoding="utf-8", newline="\n")
    print(
        f"wrote {out_path} ({out_path.stat().st_size} bytes, "
        f"{len(PROGRAM_LINES)} program lines, {len(COLUMNS)} columns)"
    )


if __name__ == "__main__":
    main()
