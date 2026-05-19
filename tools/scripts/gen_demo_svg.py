#!/usr/bin/env python3
"""Generate the README "sentence to motion" hero: a committed, CSS-animated
terminal SVG of the real hermetic loop.

Why this exists: a visitor who opens the README should *see* one English
sentence become a validated URML program become an executed trace in the
first 15 seconds, without cloning or scrolling. The only proof before this
was a stdout trace buried in a docs page.

Design constraints (match the repo ethos):

  * Pure standard library. No asciinema/termtosvg (Linux-PTY only), no
    vhs/agg/ffmpeg, no Node. Runs in the bootstrap venv on every OS,
    including the founder's Windows box. Zero new dependency.
  * Deterministic: no timestamps, no random ids. Re-running produces a
    byte-identical file (clean diffs, regenerable).
  * Honest: every line tagged ``out`` is real ``urml`` output, asserted
    byte-for-byte against a live hermetic run by
    ``reference/validator/tests/test_demo_svg.py``. The mock is captioned
    as a mock. Nothing shown is fabricated.
  * GitHub renders SVG embedded as ``<img>`` and animates pure CSS
    ``@keyframes`` (the proven svg-term/termtosvg technique). No
    ``<script>``, no SMIL.

Regenerate: ``python tools/scripts/gen_demo_svg.py`` (or ``make demo-record``).
Output: ``docs/assets/sentence-to-motion.svg``.
"""

from __future__ import annotations

from pathlib import Path

# --- Brand palette (from docs/assets/urml-logomark.svg) --------------------
BG = "#181715"        # brand ink — terminal background
BAR = "#26241f"       # title bar
FG = "#e8e4da"        # warm off-white — body text
ACCENT = "#cc6b1f"    # brand orange — prompt, highlights
DIM = "#8a857a"       # comments / chrome
OK = "#7fae5f"        # success

# --- The transcript --------------------------------------------------------
# kind: "cmd"  -> what the user types (shown; not output-asserted)
#       "out"  -> real urml output (asserted byte-for-byte by the test)
#       "gap"  -> blank spacer line
#       "hdr"  -> the env-specific `URML execute: <path>` header (shown with
#                 a clean basename; NOT asserted — the real path is the
#                 machine temp dir)
#
# The "out" lines are exactly the CRLF-stripped lines a real hermetic run
# emits (translate --provider echo  ->  validate --no-policy  ->  execute
# --adapter mock against the committed examples/home/red-mug.echo-response
# .json). test_demo_svg.py runs that loop and asserts each is present.

LINES: list[tuple[str, str]] = [
    ("cmd", '$ urml translate "Bring me the red mug from the kitchen." \\'),
    ("cmd", "      --provider echo --echo-response-file red-mug.echo-response.json"),
    ("out", "Translation accepted after 0 revision(s); profile(s)=home"),
    ("gap", ""),
    ("cmd", "$ urml validate redmug.generated.yaml --profile home --no-policy"),
    ("out", "Validation passed"),
    ("gap", ""),
    ("cmd", "$ urml execute redmug.generated.yaml --profile home --no-policy"),
    ("hdr", "URML execute: redmug.generated.yaml"),
    ("out", "  adapter:   mock"),
    ("out", "  trace (5 step(s) executed, 5 adapter call(s)):"),
    ("out", "   1. send_navigation_goal  location=kitchen"),
    ("out", "   2. query_detection  object_class=mug attributes={'color': 'red'}"),
    ("out", "   3. send_manipulation_goal  action=grasp target={'class': 'mug', "
            "'pose': {'x': 1.0, 'y': 1.0, 'z': 0.0}, ... force_n=1.5 approach=auto"),
    ("out", "   4. send_navigation_goal  location=user carrying={'class': 'mug', "
            "'pose': {'x': 1.0, 'y': 1.0, 'z': 0.0}, ..."),
    ("out", "   5. send_manipulation_goal  action=release approach=auto "
            "release_mode=hand_to_user"),
    ("out", "  RESULT: SUCCESS (5 step(s) executed)"),
]

# Exactly the lines the test asserts appear, verbatim, in a real hermetic
# run (CRLF-normalised). "Validation passed" is asserted as a line *prefix*
# because the real line carries the machine-specific generated-file path.
ASSERTED_OUTPUT_LINES: list[str] = [t for k, t in LINES if k == "out"]

TITLE = "urml · sentence to motion · hermetic · no API key · no robot"
CAPTION = ("hermetic mock — language + validator + executor, end to end. "
           "no actuator moved.")

# --- Layout ----------------------------------------------------------------
CHAR_W = 7.6          # px per monospace char at FONT px
FONT = 13
LH = 21               # line height
PAD_X = 22
BAR_H = 34
TOP = BAR_H + 24      # first body line baseline offset
BOT = 30              # caption + padding

_max_chars = max(len(t) for _, t in LINES)
WIDTH = int(PAD_X * 2 + _max_chars * CHAR_W) + 8
HEIGHT = int(TOP + len(LINES) * LH + BOT)

DUR = 15.0            # full loop seconds
STEP = 0.5            # seconds between line reveals
HOLD_PCT = 95.0       # hold fully visible until here, then reset for the loop


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _color(kind: str, text: str) -> str:
    if kind == "cmd":
        return ACCENT
    if kind == "hdr":
        return DIM
    if "RESULT: SUCCESS" in text or text.startswith("Validation passed") \
            or text.startswith("Translation accepted"):
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

    # A blinking caret that sits at the end of the loop's last command,
    # giving the "live terminal" feel without per-line cursor tracking.
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
        f'becomes an executed trace, on a hermetic mock (no robot).">\n'
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
    out = Path(__file__).resolve().parents[2] / "docs" / "assets" / "sentence-to-motion.svg"
    out.write_text(render_svg(), encoding="utf-8", newline="\n")
    print(f"wrote {out} ({out.stat().st_size} bytes, {len(LINES)} lines)")


if __name__ == "__main__":
    main()
