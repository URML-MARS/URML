#!/usr/bin/env python3
"""Generate the RFC-0062 Petoi/Bittle hero: an English sentence becoming
OpenCat-bound motion on a $299 desktop quadruped, hermetic mock.

Why this exists: PetoiCamp/OpenCat-Quadruped-Robot#113 Q6 (Dr. Rongzhong
Li, round-1 engagement 2026-05-28) gated the OpenCat-side conformance line
on URML shipping a working demo link. The Bittle demo is URML's "$299 robot
dog on a desk acting out an English sentence" — the smallest-scale,
most-shareable legged-robot target in URML's outreach landscape.

Design constraints, identical to the home/red-mug hero:

  * Pure standard library. No asciinema, no vhs, no ffmpeg, no Node.
    Runs in the bootstrap venv on every OS, including the founder's
    Windows box. Zero new dependency.
  * Deterministic: no timestamps, no random ids. Re-running produces a
    byte-identical file (clean diffs, regenerable).
  * Honest: every line tagged ``out`` is real ``urml`` output, asserted
    byte-for-byte against a live hermetic run by
    ``reference/validator/tests/test_bittle_demo_svg.py``. Nothing shown
    is fabricated.
  * GitHub renders SVG embedded as ``<img>`` and animates pure CSS
    ``@keyframes``. No ``<script>``, no SMIL.

The trace shown is the hermetic mock-adapter output. On a real Bittle X
via the edu-runtime's PetoiAdapter, those abstract `send_navigation_goal`
calls become OpenCat tokens — `kbalance`, `kwkF 5` (walk forward 5
cycles), `ksit` (sit posture) — via the maintainer-confirmed
``PetoiRobot`` module-level API. The OpenCat-token mapping lives in the
adapter and in the docstring; the hero stays honest about the abstract
URML layer.

Regenerate: ``python tools/scripts/gen_bittle_demo_svg.py`` (or
``make demo-record``).
Output: ``docs/assets/bittle-sentence-to-motion.svg``.
"""

from __future__ import annotations

from pathlib import Path

# Same brand palette as the home/red-mug hero (docs/assets/urml-logomark.svg).
BG = "#181715"
BAR = "#26241f"
FG = "#e8e4da"
ACCENT = "#cc6b1f"
DIM = "#8a857a"
OK = "#7fae5f"

# The transcript. Kinds:
#   "cmd"  -> what the user types
#   "out"  -> real urml output (asserted byte-for-byte by the test)
#   "gap"  -> blank spacer line
#   "hdr"  -> the env-specific `URML execute: <path>` header
#
# "out" lines are exactly what a real hermetic run emits
# (translate --provider echo  ->  validate --no-policy  ->  execute
# --adapter mock against examples/legged/bittle-sentence.*).
# test_bittle_demo_svg.py runs that loop and asserts each is present.

LINES: list[tuple[str, str]] = [
    ("cmd", '$ urml translate "Walk forward to the waypoint, then sit on the rest mat." \\'),
    ("cmd", "      --provider echo --echo-response-file bittle-sentence.echo-response.json \\"),
    ("cmd", "      -m bittle-sentence.manifest.yaml --profile educational --no-policy"),
    ("out", "Translation accepted after 0 revision(s); profile(s)=educational"),
    ("gap", ""),
    ("cmd", "$ urml validate bittle.generated.yaml \\"),
    ("cmd", "      -m bittle-sentence.manifest.yaml --profile educational --no-policy"),
    ("out", "Validation passed"),
    ("gap", ""),
    ("cmd", "$ urml execute bittle.generated.yaml --adapter mock \\"),
    ("cmd", "      -m bittle-sentence.manifest.yaml --profile educational --no-policy"),
    ("hdr", "URML execute: bittle.generated.yaml"),
    ("out", "  adapter:   mock"),
    ("out", "  trace (3 step(s) executed, 3 adapter call(s)):"),
    ("out", "   1. send_navigation_goal  location=start_mat"),
    ("out", "   2. send_navigation_goal  location=waypoint_a"),
    ("out", "   3. send_navigation_goal  location=rest_mat"),
    ("out", "  RESULT: SUCCESS (3 step(s) executed)"),
    ("gap", ""),
    ("cmd", "# On a real Bittle X via PetoiAdapter, those calls become OpenCat tokens:"),
    ("cmd", "#   start_mat  -> PetoiRobot.sendSkillStr('kbalance', 0)"),
    ("cmd", "#   waypoint_a -> PetoiRobot.sendCmdStr('kwkF 5', 0)   # walk forward 5 cycles"),
    ("cmd", "#   rest_mat   -> PetoiRobot.sendSkillStr('ksit', 0)"),
]

# Exactly the lines the test asserts appear, verbatim, in a real hermetic
# run (CRLF-normalised). "Validation passed" is asserted as a line *prefix*
# because the real line carries the machine-specific generated-file path.
ASSERTED_OUTPUT_LINES: list[str] = [t for k, t in LINES if k == "out"]

TITLE = "urml · bittle x · sentence to motion · hermetic · no robot"
CAPTION = ("hermetic mock — language + validator + executor, end to end. "
           "no actuator moved.")

# Layout (mirrors gen_demo_svg.py).
CHAR_W = 7.6
FONT = 13
LH = 21
PAD_X = 22
BAR_H = 34
TOP = BAR_H + 24
BOT = 30

_max_chars = max(len(t) for _, t in LINES)
WIDTH = int(PAD_X * 2 + _max_chars * CHAR_W) + 8
HEIGHT = int(TOP + len(LINES) * LH + BOT)

DUR = 18.0            # slightly longer loop than red-mug (more lines)
STEP = 0.5
HOLD_PCT = 95.0


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _color(kind: str, text: str) -> str:
    if kind == "cmd":
        # Lines that start with "#" are commentary, not user-typed shell
        # commands. Render them dim so the visual difference is clear.
        if text.lstrip().startswith("#"):
            return DIM
        return ACCENT
    if kind == "hdr":
        return DIM
    if ("RESULT: SUCCESS" in text or text.startswith("Validation passed")
            or text.startswith("Translation accepted")):
        return OK
    return FG


def render_svg() -> str:
    keyframes: list[str] = []
    rows: list[str] = []
    for i, (kind, text) in enumerate(LINES):
        appear = round((i * STEP) / DUR * 100.0, 3)
        pre = max(appear - 0.001, 0.0)
        keyframes.append(
            f"@keyframes r{i}{{0%,{pre}%{{opacity:0}}"
            f"{appear}%,{HOLD_PCT}%{{opacity:1}}100%{{opacity:0}}}}"
        )
        if kind == "gap":
            continue
        y = TOP + i * LH
        rows.append(
            f'<text x="{PAD_X}" y="{y}" class="ln" '
            f'style="fill:{_color(kind, text)};animation-name:r{i}">'
            f"{_esc(text)}</text>"
        )

    caret_y = TOP + (len(LINES) - 1) * LH - 14

    style = (
        f"text{{font-family:ui-monospace,'SF Mono',SFMono-Regular,Menlo,"
        f"Consolas,'Liberation Mono',monospace;font-size:{FONT}px;"
        f"white-space:pre}}"
        f".ln{{opacity:0;animation-duration:{DUR}s;"
        f"animation-timing-function:linear;animation-iteration-count:infinite}}"
        f".caret{{fill:{ACCENT};animation:blink 1s steps(1) infinite}}"
        f"@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}"
        + "".join(keyframes)
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" role="img" '
        f'aria-label="One English sentence becomes a validated URML program '
        f'becomes an executed trace on a Petoi Bittle X via OpenCat, '
        f'hermetic mock (no robot).">\n'
        f"<style>{style}</style>\n"
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="{BG}"/>\n'
        f'<rect width="{WIDTH}" height="{BAR_H}" rx="10" fill="{BAR}"/>\n'
        f'<rect y="{BAR_H - 10}" width="{WIDTH}" height="10" fill="{BAR}"/>\n'
        f'<circle cx="20" cy="17" r="6" fill="#e06c5a"/>'
        f'<circle cx="40" cy="17" r="6" fill="#e0b04a"/>'
        f'<circle cx="60" cy="17" r="6" fill="{OK}"/>\n'
        f'<text x="84" y="22" style="fill:{DIM};font-size:12px">'
        f"{_esc(TITLE)}</text>\n"
        f'{"".join(rows)}\n'
        f'<rect class="caret" x="{PAD_X}" y="{caret_y}" width="{int(CHAR_W)}" '
        f'height="{FONT + 2}"/>\n'
        f'<text x="{PAD_X}" y="{HEIGHT - 12}" style="fill:{DIM};font-size:12px">'
        f"{_esc(CAPTION)}</text>\n"
        f"</svg>\n"
    )


def main() -> None:
    out = Path(__file__).resolve().parents[2] / "docs" / "assets" / "bittle-sentence-to-motion.svg"
    out.write_text(render_svg(), encoding="utf-8", newline="\n")
    print(f"wrote {out} ({out.stat().st_size} bytes, {len(LINES)} lines)")


if __name__ == "__main__":
    main()
