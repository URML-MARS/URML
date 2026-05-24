"""The portability SVG must be deterministic and must not lie.

Three guarantees:

  * ``tools/scripts/gen_portability_svg.py`` is deterministic, and the
    committed ``docs/assets/one-intent-many-bodies.svg`` is exactly what
    it produces.
  * Every trace line listed in ``ASSERTED_TRACE_LINES`` is real: a live,
    hermetic ``urml execute --adapter mock`` run against each of the
    three body manifests emits each of them verbatim. The asset cannot
    drift from what the tool actually does on any of the three bodies.
  * Every "out" fragment shown in the SVG's column layout is a substring
    of one of the asserted real-output lines, after whitespace
    normalisation. The column layout wraps long lines for visual layout
    but never fabricates content.

In-process (no subprocess), mirroring test_demo_svg.py.
"""

from __future__ import annotations

import importlib.util
import re
import xml.dom.minidom
from pathlib import Path

import pytest

from urml_validator.cli import main

REPO_ROOT = Path(__file__).resolve().parents[3]
PROGRAM = REPO_ROOT / "examples" / "portability" / "inspect.urml.yaml"
MANIFESTS = {
    "drone":  REPO_ROOT / "examples" / "portability" / "drone.manifest.yaml",
    "legged": REPO_ROOT / "examples" / "portability" / "legged.manifest.yaml",
    "mobile": REPO_ROOT / "examples" / "portability" / "mobile.manifest.yaml",
}
COMMITTED_SVG = REPO_ROOT / "docs" / "assets" / "one-intent-many-bodies.svg"
GEN_PATH = REPO_ROOT / "tools" / "scripts" / "gen_portability_svg.py"


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen_portability_svg", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _norm(s: str) -> str:
    """Collapse internal whitespace; strip ends. Used for substring checks."""
    return re.sub(r"\s+", " ", s).strip()


def test_generator_is_deterministic_and_well_formed() -> None:
    gen = _load_gen()
    a = gen.render_svg()
    b = gen.render_svg()
    assert a == b, "render_svg() is not deterministic"
    xml.dom.minidom.parseString(a)
    # Static asset: no <script>, no SMIL, no CSS animation. Side-by-side
    # comparison is a static read, not a typewriter narrative.
    assert "<script" not in a
    assert "<animate" not in a
    assert "@keyframes" not in a


def test_committed_svg_matches_generator() -> None:
    """Guard against a stale committed asset (regenerate before commit)."""
    gen = _load_gen()
    assert COMMITTED_SVG.exists(), f"missing {COMMITTED_SVG}"
    on_disk = COMMITTED_SVG.read_text(encoding="utf-8")
    assert on_disk == gen.render_svg(), (
        "docs/assets/one-intent-many-bodies.svg is out of date — run "
        "`python tools/scripts/gen_portability_svg.py` "
        "(or `make portability-record`)."
    )


@pytest.mark.parametrize("body", list(MANIFESTS.keys()))
def test_asserted_trace_lines_are_real_per_body(
    body: str,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every asserted trace line is emitted verbatim by a real hermetic run
    of the program against each of the three body manifests."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    gen = _load_gen()
    manifest = MANIFESTS[body]
    rc = main([
        "execute", str(PROGRAM),
        "-m", str(manifest),
        "--profile", "home", "--no-policy", "--adapter", "mock",
    ])
    out = capsys.readouterr()
    assert rc == 0, out.err
    real_lines = (out.out + out.err).replace("\r\n", "\n").split("\n")

    for line in gen.ASSERTED_TRACE_LINES:
        assert line in real_lines, (
            f"[{body}] asset claims trace line not in real output:\n"
            f"  expected: {line!r}\n"
            f"asset must never fabricate trace text"
        )


def test_column_body_fragments_are_substrings_of_real_output() -> None:
    """Every 'out' fragment shown in the SVG's column layout must appear,
    after whitespace normalisation, as a substring of one of the asserted
    real-output trace lines. The layout wraps long lines for column width;
    it never invents content the tool didn't emit."""
    gen = _load_gen()
    asserted_blob = _norm(" ".join(gen.ASSERTED_TRACE_LINES))
    for kind, line in gen.COLUMN_BODY:
        if kind != "out":
            continue
        frag = _norm(line)
        if not frag:
            continue
        assert frag in asserted_blob, (
            f"SVG column shows an 'out' fragment that is not a substring "
            f"of any asserted real-output line:\n  fragment: {frag!r}\n"
            f"the asset must never claim output the tool does not produce"
        )
