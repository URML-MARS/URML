"""The README hero SVG must be deterministic and must not lie.

Two guarantees:

  * ``tools/scripts/gen_demo_svg.py`` is deterministic, and the committed
    ``docs/assets/sentence-to-motion.svg`` is exactly what it produces (so
    a stale, hand-edited, or forgotten-regenerate asset fails CI).
  * Every line the hero presents as ``urml`` output is real: a live,
    hermetic translate -> validate -> execute loop (echo provider + mock
    adapter, no API key, no network) emits each of them verbatim. The hero
    cannot drift from what the tool actually does.

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
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every "out" line the hero shows is emitted by a real hermetic run."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    gen = _load_gen()
    generated = tmp_path / "redmug.generated.yaml"

    rc = main([
        "translate", "Bring me the red mug from the kitchen.",
        "-m", str(MANIFEST), "--profile", "home",
        "--provider", "echo", "--echo-response-file", str(ECHO),
        "--no-policy", "--out", str(generated),
    ])
    out = capsys.readouterr()
    assert rc == 0, out.err
    combined = out.out + out.err

    rc = main([
        "validate", str(generated), "-m", str(MANIFEST),
        "--profile", "home", "--no-policy",
    ])
    out = capsys.readouterr()
    assert rc == 0, out.err
    combined += out.out + out.err

    rc = main([
        "execute", str(generated), "-m", str(MANIFEST),
        "--profile", "home", "--no-policy", "--adapter", "mock",
    ])
    out = capsys.readouterr()
    assert rc == 0, out.err
    combined += out.out + out.err

    # Normalise CRLF (Windows console) before comparing.
    real_lines = combined.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    for line in gen.ASSERTED_OUTPUT_LINES:
        if line == "Validation passed":
            # The real line carries the machine-specific generated path.
            assert any(rl.startswith("Validation passed") for rl in real_lines), (
                "hero claims 'Validation passed' but no such line in real output"
            )
        else:
            assert line in real_lines, (
                f"hero shows a line the tool does not emit verbatim:\n  {line!r}\n"
                f"the hero must never fabricate output"
            )
