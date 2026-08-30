"""Gallery rot-guard: every example bundle stays schema-valid.

CLAUDE.md: "All examples in spec documents must be runnable against the
current reference runtime. A broken example is fixed or removed in the
same commit, never left dangling." `test_schemas_parse.py` only guards
the single red-mug file; this guards the whole `examples/` tree so a
schema change can never silently rot a published example.

This is a *schema-parse* guard, not the four-pass validator. Negative
policy variants (e.g. `red-mug.dji-camera.manifest.yaml`) are still
schema-valid — they fail Pass 5, which this guard deliberately does not
run — so they parse here exactly as they should.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from urml_validator.schemas.envelope import SafetyEnvelope
from urml_validator.schemas.manifest import CapabilityManifest
from urml_validator.schemas.program import URMLProgram

_EXAMPLES_ROOT = Path(__file__).resolve().parents[3] / "examples"


def _ids(paths: list[Path]) -> list[str]:
    return [str(p.relative_to(_EXAMPLES_ROOT)) for p in paths]


def _glob(suffix: str) -> list[Path]:
    return sorted(_EXAMPLES_ROOT.rglob(f"*{suffix}"))


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


_PROGRAMS = _glob(".urml.yaml")
_MANIFESTS = _glob(".manifest.yaml")
_ENVELOPES = _glob(".envelope.yaml")


def test_examples_tree_is_present() -> None:
    """Guard the guard: at least the canonical bundle must be discovered."""
    assert _PROGRAMS, f"no *.urml.yaml found under {_EXAMPLES_ROOT}"
    assert _MANIFESTS, f"no *.manifest.yaml found under {_EXAMPLES_ROOT}"


@pytest.mark.parametrize("path", _PROGRAMS, ids=_ids(_PROGRAMS))
def test_example_program_parses(path: Path) -> None:
    URMLProgram.model_validate(_load(path))


@pytest.mark.parametrize("path", _MANIFESTS, ids=_ids(_MANIFESTS))
def test_example_manifest_parses(path: Path) -> None:
    CapabilityManifest.model_validate(_load(path))


@pytest.mark.parametrize("path", _ENVELOPES, ids=_ids(_ENVELOPES))
def test_example_envelope_parses(path: Path) -> None:
    SafetyEnvelope.model_validate(_load(path))


# ---------------------------------------------------------------------------
# Drone bundles run the full validator, not just the schema parse.
#
# RFC-0250 made `substrate.autopilot_class` mandatory for drone-class
# manifests and the published drone examples silently rotted for a while
# because this file only parsed them. Each bundle below is validated the
# way the docs tell a reader to validate it (`--profile drone --no-policy`).
# ---------------------------------------------------------------------------

from urml_validator import validate  # noqa: E402

_DRONE = _EXAMPLES_ROOT / "drone"
_DRONE_BUNDLES: list[tuple[str, str, str | None]] = [
    ("roof-inspection", "roof-inspection", None),
    ("bridge-survey", "bridge-survey", None),
    ("parallel-watch", "parallel-watch", None),
    ("link-aware-patrol", "link-aware-patrol", "link-aware-patrol"),
    ("bench-battery", "pixhawk-ardupilot", None),
    ("bench-hop", "pixhawk-ardupilot", None),
    ("site-photogrammetry", "site-photogrammetry", "site-photogrammetry"),
    ("parcel-delivery", "parcel-delivery", "parcel-delivery"),
    ("parcel-delivery-servo", "parcel-delivery", "parcel-delivery"),
    ("site-photogrammetry.gemini", "site-photogrammetry", "site-photogrammetry"),
    ("parcel-delivery.gemini", "parcel-delivery", "parcel-delivery"),
]


@pytest.mark.parametrize(("program", "manifest", "envelope"), _DRONE_BUNDLES, ids=[b[0] for b in _DRONE_BUNDLES])
def test_drone_bundle_validates(program: str, manifest: str, envelope: str | None) -> None:
    env = _load(_DRONE / f"{envelope}.envelope.yaml") if envelope else None
    result = validate(
        _load(_DRONE / f"{program}.urml.yaml"),
        _load(_DRONE / f"{manifest}.manifest.yaml"),
        envelope=env,
        profiles=("drone",),
        policy=None,
    )
    assert result.accepted, [e.message for e in result.errors]
