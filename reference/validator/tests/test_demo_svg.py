"""The README hero SVG must be deterministic and must not lie.

Two guarantees:

  * ``tools/scripts/gen_demo_svg.py`` is deterministic, and the committed
    ``docs/assets/sentence-to-motion.svg`` is exactly what it produces (so
    a stale, hand-edited, or forgotten-regenerate asset fails CI).
  * Every line the hero presents as ``urml`` output is real: the two live,
    hermetic ``urml run`` beats it depicts (echo provider + kinematic
    rehearsal + mock adapter, no API key, no network) emit each of them
    verbatim — the blocked beat and the passing beat. The hero cannot
    drift from what the tool actually does.

In-process (no subprocess), mirroring test_cli_execute.py.
"""

from __future__ import annotations

import importlib.util
import xml.dom.minidom
from pathlib import Path

import pytest

from urml_validator.cli import main

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = REPO_ROOT / "examples" / "home"
MANIFEST = EXAMPLES / "red-mug.manifest.yaml"
ECHO = EXAMPLES / "red-mug.echo-response.json"
ENVELOPE = EXAMPLES / "red-mug.envelope.yaml"
REHEARSE_CFG = EXAMPLES / "red-mug.rehearse.yaml"
COMMITTED_SVG = REPO_ROOT / "docs" / "assets" / "sentence-to-motion.svg"
GEN_PATH = REPO_ROOT / "tools" / "scripts" / "gen_demo_svg.py"


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen_demo_svg", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic_and_well_formed() -> None:
    gen = _load_gen()
    a = gen.render_svg()
    b = gen.render_svg()
    assert a == b, "render_svg() is not deterministic"
    xml.dom.minidom.parseString(a)  # raises if not well-formed XML
    # No <script>, no SMIL — GitHub renders <img>-embedded SVG with pure
    # CSS @keyframes only; anything else would silently not animate.
    assert "<script" not in a
    assert "<animate" not in a
    assert "@keyframes" in a


def test_committed_svg_matches_generator() -> None:
    """Guard against a stale committed asset (regenerate before commit)."""
    gen = _load_gen()
    assert COMMITTED_SVG.exists(), f"missing {COMMITTED_SVG}"
    on_disk = COMMITTED_SVG.read_text(encoding="utf-8")
    assert on_disk == gen.render_svg(), (
        "docs/assets/sentence-to-motion.svg is out of date — run "
        "`python tools/scripts/gen_demo_svg.py` (or `make demo-record`)."
    )


def test_hero_output_lines_are_real(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every output line the hero shows is emitted by the two real hermetic beats."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    gen = _load_gen()

    base = [
        "run", "Bring me the red mug from the kitchen.",
        "-m", str(MANIFEST), "--envelope", str(ENVELOPE),
        "--profile", "home",
        "--provider", "echo", "--echo-response-file", str(ECHO),
        "--rehearse", "kinematic", "--adapter", "mock", "--no-policy",
    ]

    # Beat 1: the backend's default cruise assumption (0.5 m/s) breaks the
    # envelope's 0.4 m/s cap — the gate must block, before any real adapter.
    rc = main(base)
    out = capsys.readouterr()
    assert rc != 0, "the gate must block the default-assumption run"
    combined = out.out + out.err

    # Beat 2: the declared 0.35 m/s profile keeps the trace under the cap.
    rc = main(base + ["--rehearse-config", str(REHEARSE_CFG)])
    out = capsys.readouterr()
    assert rc == 0, out.err
    combined += out.out + out.err

    # Normalise CRLF (Windows console) before comparing.
    real_lines = combined.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    for line in gen.ASSERTED_OUTPUT_LINES:
        assert line in real_lines, (
            f"hero shows a line the tool does not emit verbatim:\n  {line!r}\n"
            f"the hero must never fabricate output"
        )

    # The wrapped display rows must re-flow real text, not paraphrase it:
    # concatenating each wrap group must reproduce a substring of the full
    # asserted line (whitespace-normalised).
    wrap_rows = [t for k, t in gen.LINES if k == "outw"]
    joined = " ".join(part.strip() for part in wrap_rows)
    full = " ".join(gen.WRAPPED_OUTPUT_LINES[0].split())
    assert joined in full, "outw display rows must be a re-flow of the real line"
