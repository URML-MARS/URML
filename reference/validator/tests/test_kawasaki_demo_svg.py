"""The Kawasaki `call_program` hero SVG must be deterministic and must not lie.

Mirrors test_demo_svg.py for the RFC-0015 demo
(examples/industrial/kawasaki-as-program.*):

  * ``tools/scripts/gen_kawasaki_demo_svg.py`` is deterministic, and the
    committed ``docs/assets/kawasaki-as-program-to-motion.svg`` is exactly what
    it produces (a stale or hand-edited asset fails CI).
  * Every line the hero presents as ``urml`` output is real: a live, hermetic
    translate -> validate -> execute loop (echo provider + mock adapter, no API
    key, no network) emits each verbatim, including the two
    ``call_named_program`` trace lines.
  * The illustrative JP-origin manifest passes the bundled US-federal policy
    (policy-on validate succeeds), so the demo is honest about compliance too.

In-process (no subprocess), mirroring test_demo_svg.py.
"""

from __future__ import annotations

import importlib.util
import xml.dom.minidom
from pathlib import Path

import pytest

from urml_validator.cli import main

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = REPO_ROOT / "examples" / "industrial"
MANIFEST = EXAMPLES / "kawasaki-as-program.manifest.yaml"
ECHO = EXAMPLES / "kawasaki-as-program.echo-response.json"
COMMITTED_SVG = REPO_ROOT / "docs" / "assets" / "kawasaki-as-program-to-motion.svg"
GEN_PATH = REPO_ROOT / "tools" / "scripts" / "gen_kawasaki_demo_svg.py"

SENTENCE = "After the safety door closes, run the cell's pick-and-place job, then home all axes."


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen_kawasaki_demo_svg", GEN_PATH)
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
    assert "<script" not in a
    assert "<animate" not in a
    assert "@keyframes" in a


def test_committed_svg_matches_generator() -> None:
    """Guard against a stale committed asset (regenerate before commit)."""
    gen = _load_gen()
    assert COMMITTED_SVG.exists(), f"missing {COMMITTED_SVG}"
    on_disk = COMMITTED_SVG.read_text(encoding="utf-8")
    assert on_disk == gen.render_svg(), (
        "docs/assets/kawasaki-as-program-to-motion.svg is out of date — run "
        "`python tools/scripts/gen_kawasaki_demo_svg.py`."
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
    generated = tmp_path / "kawasaki.generated.yaml"

    rc = main([
        "translate", SENTENCE,
        "-m", str(MANIFEST), "--profile", "industrial",
        "--provider", "echo", "--echo-response-file", str(ECHO),
        "--no-policy", "--out", str(generated),
    ])
    out = capsys.readouterr()
    assert rc == 0, out.err
    combined = out.out + out.err

    rc = main([
        "validate", str(generated), "-m", str(MANIFEST),
        "--profile", "industrial", "--no-policy",
    ])
    out = capsys.readouterr()
    assert rc == 0, out.err
    combined += out.out + out.err

    rc = main([
        "execute", str(generated), "-m", str(MANIFEST),
        "--profile", "industrial", "--no-policy", "--adapter", "mock",
    ])
    out = capsys.readouterr()
    assert rc == 0, out.err
    combined += out.out + out.err

    real_lines = combined.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    for line in gen.ASSERTED_OUTPUT_LINES:
        if line == "Validation passed":
            assert any(rl.startswith("Validation passed") for rl in real_lines), (
                "hero claims 'Validation passed' but no such line in real output"
            )
        else:
            assert line in real_lines, (
                f"hero shows a line the tool does not emit verbatim:\n  {line!r}\n"
                f"the hero must never fabricate output"
            )


def test_jp_manifest_passes_us_federal_policy(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The illustrative Kawasaki (JP-origin) manifest passes the bundled policy.

    The demo runs --no-policy for the clean headline, but the manifest is
    honest under compliance too: a policy-on validate accepts it (JP is an
    allied origin), with at most the self-declared-attestation warning.
    """
    generated = tmp_path / "kawasaki.generated.yaml"
    rc = main([
        "translate", SENTENCE,
        "-m", str(MANIFEST), "--profile", "industrial",
        "--provider", "echo", "--echo-response-file", str(ECHO),
        "--no-policy", "--out", str(generated),
    ])
    assert rc == 0, capsys.readouterr().err

    # Policy ON (no --no-policy): must still pass.
    rc = main([
        "validate", str(generated), "-m", str(MANIFEST), "--profile", "industrial",
    ])
    out = capsys.readouterr()
    assert rc == 0, f"JP-origin manifest unexpectedly failed the default policy:\n{out.err}\n{out.out}"
