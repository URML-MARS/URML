"""Conformance fixture model + loader.

A fixture is a single declarative test case: a URML program (inline),
references to a capability manifest and optional envelope, expected
validation + execution outcomes, and optional MockROSAdapter overrides.

Fixtures live as YAML files under ``conformance/fixtures/<profile>/``.
The loader resolves manifest/envelope *names* against a registry of
canonical fixtures (the validator's test fixtures are the v0.1 registry)
so authors don't have to inline the full manifest in every case.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field
from urml_ros2_runtime.substrate import (
    CaptureResult,
    DetectionResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ScanResult,
    SubstrateResult,
    WaitResult,
)

# ---------------------------------------------------------------------------
# Manifest / envelope registry — by-name lookup against the validator's fixtures
# ---------------------------------------------------------------------------


# conformance/src/urml_conformance/fixtures.py -> ../../../.. would be too many.
# parents[0]=urml_conformance, [1]=src, [2]=conformance, [3]=URML repo root.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_VALIDATOR_FIXTURES = _REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"

#: Public registry: maps a short manifest name to its YAML path. Authors
#: reference these by name in fixture files so the loader resolves them
#: against the validator's canonical fixtures.
MANIFEST_REGISTRY: dict[str, Path] = {
    "turtlebot4_home": _VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home.yaml",
    "industrial_cell": _VALIDATOR_FIXTURES / "manifests" / "industrial_cell.yaml",
}

ENVELOPE_REGISTRY: dict[str, Path] = {
    "home_default": _VALIDATOR_FIXTURES / "envelopes" / "home_default.yaml",
}


# ---------------------------------------------------------------------------
# Expected-outcome models
# ---------------------------------------------------------------------------


class ExpectedValidation(BaseModel):
    """What the validator should produce for this case."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool = True
    error_codes: list[str] = Field(
        default_factory=list,
        description=(
            "Required when `accepted` is False. Every code listed must appear "
            "in the validator's emitted errors. Extra emitted codes are tolerated."
        ),
    )


class ExpectedExecution(BaseModel):
    """What the runtime should produce when the program is executed."""

    model_config = ConfigDict(extra="forbid")

    success: bool = True
    steps_executed: int | None = Field(
        None,
        description="If set, the runtime must report exactly this many executed steps.",
    )
    audit_methods: list[str] | None = Field(
        None,
        description=(
            "If set, the adapter's call_log methods must match this list "
            "exactly in order."
        ),
    )
    bindings_contains: dict[str, Any] | None = Field(
        None,
        description=(
            "If set, every key here must be present in the final bindings, "
            "and the bound value's top-level fields must include the listed entries."
        ),
    )
    last_reason: str | None = Field(
        None,
        description="If set, last_outcome.reason must equal this value.",
    )


class FixtureCase(BaseModel):
    """One declarative test case."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None

    manifest: str = Field(..., description="Name of a registered manifest.")
    envelope: str | None = Field(
        None, description="Name of a registered envelope (optional)."
    )
    profiles: list[str] = Field(default_factory=list)

    program: dict[str, Any] = Field(..., description="The URML program (inline).")

    adapter_overrides: AdapterOverrides | None = Field(
        None,
        description="Optional pre-configured adapter responses for deterministic failure tests.",
    )

    expected_validation: ExpectedValidation = Field(
        default_factory=ExpectedValidation,
        alias="expected_validation",
    )
    expected_execution: ExpectedExecution | None = Field(
        None,
        description=(
            "If omitted, the case is a validator-only test — the runtime is "
            "not invoked. Set this for any test that exercises execution."
        ),
    )


class AdapterOverrides(BaseModel):
    """Pre-set adapter responses for deterministic execution tests.

    Each field corresponds to one of MockROSAdapter's `set_*` methods. The
    response is applied as the *next* return value for that method's
    set-override slot. (Per-call sequencing isn't supported in v0.1; one
    override per method covers the cases we ship.)
    """

    model_config = ConfigDict(extra="forbid")

    navigation: NavigationResult | None = None
    docking: NavigationResult | None = None
    manipulation: ManipulationResult | None = None
    detection: DetectionResult | None = None
    scan: ScanResult | None = None
    measurement: MeasurementResult | None = None
    capture: CaptureResult | None = None
    wait_for: WaitResult | None = None
    wait_passive: SubstrateResult | None = None
    report: SubstrateResult | None = None


# Resolve the forward reference after AdapterOverrides is defined.
FixtureCase.model_rebuild()


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


_PACKAGE_FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"
_REPO_FIXTURES_ROOT = _REPO_ROOT / "conformance" / "fixtures"


def fixtures_root() -> Path:
    """Path to the fixtures directory bundled with the package or in the repo."""
    if _PACKAGE_FIXTURES_ROOT.is_dir():
        return _PACKAGE_FIXTURES_ROOT
    return _REPO_FIXTURES_ROOT


def load_fixture(path: Path) -> FixtureCase:
    """Parse one fixture YAML into a FixtureCase."""
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return FixtureCase.model_validate(data)


def discover_fixtures(root: Path | None = None) -> list[FixtureCase]:
    """Walk the fixtures directory and return every parsed case.

    Order is stable: sorted by file path (so test reports are deterministic).
    """
    base = root or fixtures_root()
    if not base.is_dir():
        return []
    cases: list[FixtureCase] = []
    for path in sorted(base.rglob("*.yaml")):
        cases.append(load_fixture(path))
    return cases


def resolve_manifest(name: str) -> dict[str, Any]:
    """Load a registered manifest by name."""
    if name not in MANIFEST_REGISTRY:
        raise KeyError(
            f"unknown manifest {name!r}; registered: {sorted(MANIFEST_REGISTRY.keys())!r}"
        )
    with MANIFEST_REGISTRY[name].open(encoding="utf-8") as fh:
        result = yaml.safe_load(fh)
    if not isinstance(result, dict):
        raise ValueError(f"manifest {name!r} did not parse as a mapping")
    return result


def resolve_envelope(name: str) -> dict[str, Any]:
    """Load a registered envelope by name."""
    if name not in ENVELOPE_REGISTRY:
        raise KeyError(
            f"unknown envelope {name!r}; registered: {sorted(ENVELOPE_REGISTRY.keys())!r}"
        )
    with ENVELOPE_REGISTRY[name].open(encoding="utf-8") as fh:
        result = yaml.safe_load(fh)
    if not isinstance(result, dict):
        raise ValueError(f"envelope {name!r} did not parse as a mapping")
    return result
