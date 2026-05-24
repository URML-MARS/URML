"""The homepage architecture diagram must be deterministic and must not lie.

Three guarantees, mirroring the hero-SVG test next door:

  * ``tools/scripts/gen_architecture_svg.py`` is deterministic, and the
    committed ``docs/assets/architecture-stack.svg`` is exactly what it
    produces (so a stale, hand-edited, or forgotten-regenerate asset
    fails CI).
  * Every layer title and body shown in the diagram traces back to
    ``docs/architecture.md`` (the canonical layer document). If the docs
    rename a layer and the diagram falls behind, this test fails.
  * Every profile name in the pill traces back to either
    ``MANIFESTO.md`` or ``docs/architecture.md``. Same drift catch.

The em-dash in architecture.md's L0 title is normalised to a comma before
the substring check, so the diagram can follow the no-em-dash style rule
without falsely failing.
"""

from __future__ import annotations

import importlib.util
import xml.dom.minidom
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
COMMITTED_SVG = REPO_ROOT / "docs" / "assets" / "architecture-stack.svg"
GEN_PATH = REPO_ROOT / "tools" / "scripts" / "gen_architecture_svg.py"
ARCH_MD = REPO_ROOT / "docs" / "architecture.md"
MANIFESTO_MD = REPO_ROOT / "MANIFESTO.md"


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen_architecture_svg", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _normalise(s: str) -> str:
    # Architecture.md's L0 title uses an em-dash; the diagram label uses a
    # comma (style rule: no em-dashes in new public copy). Normalise both
    # sides so the drift check still catches real renames.
    return s.replace(" — ", ", ").replace("—", ",")


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
        "docs/assets/architecture-stack.svg is out of date — run "
        "`python tools/scripts/gen_architecture_svg.py` (or "
        "`make architecture-record`)."
    )


def test_layer_labels_trace_to_architecture_doc() -> None:
    """Every layer title and body in the diagram appears in architecture.md."""
    gen = _load_gen()
    arch = _normalise(ARCH_MD.read_text(encoding="utf-8"))
    for lid, title, body in gen.LAYERS:
        assert _normalise(title) in arch, (
            f"diagram layer {lid} title {title!r} no longer appears in "
            f"docs/architecture.md — update LAYERS in "
            f"tools/scripts/_urml_layers.py and re-run "
            f"`make architecture-record`."
        )
        assert _normalise(body) in arch, (
            f"diagram layer {lid} body {body!r} no longer appears in "
            f"docs/architecture.md — update LAYERS in "
            f"tools/scripts/_urml_layers.py and re-run "
            f"`make architecture-record`."
        )


def test_profile_names_trace_to_canonical_docs() -> None:
    """Every profile name in the pill appears in MANIFESTO.md or architecture.md."""
    gen = _load_gen()
    sources = (
        MANIFESTO_MD.read_text(encoding="utf-8")
        + ARCH_MD.read_text(encoding="utf-8")
    )
    for name in gen.PROFILES:
        assert name in sources, (
            f"diagram profile {name!r} appears in neither MANIFESTO.md nor "
            f"docs/architecture.md — update PROFILES in "
            f"tools/scripts/_urml_layers.py and re-run "
            f"`make architecture-record`."
        )
