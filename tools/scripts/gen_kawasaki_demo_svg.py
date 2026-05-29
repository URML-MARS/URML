#!/usr/bin/env python3
"""Generate the Kawasaki "sentence to AS-program" hero: a committed,
CSS-animated terminal SVG of the real hermetic `call_program` loop (RFC-0015).

Why this exists: the `call_program` primitive is the one Kawasaki-shaped
capability in URML — invoking a commissioned on-controller AS-language program
by name, the binding kurita-taisuke (Kawasaki-Robotics) endorsed on khi_ros2
issue #9. This hero shows one English sentence become a validated URML program
become an executed trace whose steps are `call_named_program`, on a hermetic
mock (no robot, no API key).

Design constraints match the repo ethos (see ``gen_demo_svg.py``): pure
standard library, deterministic (byte-identical re-runs), honest (every
``out`` line is real ``urml`` output, asserted byte-for-byte by
``reference/validator/tests/test_kawasaki_demo_svg.py``), and GitHub-renderable
pure-CSS ``@keyframes`` (no ``<script>``, no SMIL).

Regenerate: ``python tools/scripts/gen_kawasaki_demo_svg.py``
(or ``make kawasaki-demo-record``).
Output: ``docs/assets/kawasaki-as-program-to-motion.svg``.
"""

from __future__ import annotations

from pathlib import Path

# --- Brand palette (shared with gen_demo_svg.py) ---------------------------
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
#       "hdr"  -> the env-specific `URML execute: <path>` header (shown with a
#                 clean basename; NOT asserted — the real path is the temp dir)
#
# The "out" lines are exactly the CRLF-stripped lines a real hermetic run emits
# (translate --provider echo -> validate --no-policy -> execute --adapter mock
# against examples/industrial/kawasaki-as-program.echo-response.json).
# test_kawasaki_demo_svg.py runs that loop and asserts each is present.

LINES: list[tuple[str, str]] = [
    ("cmd", '$ urml translate "After the safety door closes, run the cell\'s \\'),
    ("cmd", '      pick-and-place job, then home all axes." \\'),
    ("cmd", "      --provider echo --echo-response-file kawasaki-as-program.echo-response.json"),
    ("out", "Translation accepted after 0 revision(s); profile(s)=industrial"),
    ("gap", ""),
    ("cmd", "$ urml validate kawasaki.generated.yaml --profile industrial --no-policy"),
    ("out", "Validation passed"),
    ("gap", ""),
    ("cmd", "$ urml execute kawasaki.generated.yaml --profile industrial --no-policy"),
    ("hdr", "URML execute: kawasaki.generated.yaml"),
    ("out", "  adapter:   mock"),
    ("out", "  trace (4 step(s) executed, 4 adapter call(s)):"),
    ("out", "   1. wait_for_condition  kind=event name=safety_door_closed"),
    ("out", "   2. call_named_program  name=pick_place_cycle"),
    ("out", "   3. call_named_program  name=home_all"),
    ("out", "   4. emit_report  to=line_controller facts={'cycle': 'run_commissioned_job', "
            "'result': 'ok'} status=success severity=info"),
    ("out", "  RESULT: SUCCESS (4 step(s) executed)"),
]

# Exactly the lines the test asserts appear, verbatim, in a real hermetic run
# (CRLF-normalised). "Validation passed" is asserted as a line *prefix* because
# the real line carries the machine-specific generated-file path.
ASSERTED_OUTPUT_LINES: list[str] = [t for k, t in LINES if k == "out"]

TITLE = "urml · sentence to AS-program · call_program · hermetic · no robot"
CAPTION = ("hermetic mock — `call_program` invokes commissioned Kawasaki AS "
           "programs by name. no actuator moved.")

# --- Layout (shared with gen_demo_svg.py) ----------------------------------
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

    # A blinking caret at the end of the loop's last command.
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
        f'whose steps invoke named Kawasaki AS-language programs, executed on a '
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
    out = (
        Path(__file__).resolve().parents[2]
        / "docs" / "assets" / "kawasaki-as-program-to-motion.svg"
    )
    out.write_text(render_svg(), encoding="utf-8", newline="\n")
    print(f"wrote {out} ({out.stat().st_size} bytes, {len(LINES)} lines)")


if __name__ == "__main__":
    main()
