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
    ListenResult,
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
    "turtlebot4_home_cn_critical": _VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home_cn_critical.yaml",
    "turtlebot4_home_dji_vendor": _VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home_dji_vendor.yaml",
    "drone_civilian": _VALIDATOR_FIXTURES / "manifests" / "drone_civilian.yaml",
    # RFC-0006: connectivity-bearing variants.
    "drone_civilian_connectivity": _VALIDATOR_FIXTURES / "manifests" / "drone_civilian_connectivity.yaml",
    "drone_connectivity_no_home": _VALIDATOR_FIXTURES / "manifests" / "drone_connectivity_no_home.yaml",
    "ground_connectivity_no_station_keeping": _VALIDATOR_FIXTURES / "manifests" / "ground_connectivity_no_station_keeping.yaml",
    "industrial_cell_connectivity": _VALIDATOR_FIXTURES / "manifests" / "industrial_cell_connectivity.yaml",
    "turtlebot4_home_connectivity": _VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home_connectivity.yaml",
    # RFC-0009: legged/quadruped manifests.
    "spot_quadruped": _VALIDATOR_FIXTURES / "manifests" / "spot_quadruped.yaml",
    "unitree_quadruped_denied": _VALIDATOR_FIXTURES / "manifests" / "unitree_quadruped_denied.yaml",
    # Clearpath AMR + declared-parts (Robotiq/RealSense compliant; Hesai denied).
    "clearpath_husky": _VALIDATOR_FIXTURES / "manifests" / "clearpath_husky.yaml",
    "hesai_lidar_denied": _VALIDATOR_FIXTURES / "manifests" / "hesai_lidar_denied.yaml",
    # BlueROV2 / ArduSub — exercises drive_type: underwater_thrusters.
    "bluerov_marine": _VALIDATOR_FIXTURES / "manifests" / "bluerov_marine.yaml",
    # MuJoCo simulator substrate (zero ROS) — sentence→motion acid-test proof.
    "mujoco_arm_sim": _VALIDATOR_FIXTURES / "manifests" / "mujoco_arm_sim.yaml",
    # OPC UA Robotics industrial cell (zero ROS, US provenance).
    "opcua_cell": _VALIDATOR_FIXTURES / "manifests" / "opcua_cell.yaml",
    # Zero-ROS collaborative arm (UR / Franka native SDKs).
    "cobot_cell": _VALIDATOR_FIXTURES / "manifests" / "cobot_cell.yaml",
    # Educational micro:bit/Arduino buggy (zero ROS, serial).
    "microbit_edu": _VALIDATOR_FIXTURES / "manifests" / "microbit_edu.yaml",
    # Track C — compliant parts (grippers, FT sensor, vision, safety lidar).
    "schunk_mpg_cell": _VALIDATOR_FIXTURES / "manifests" / "schunk_mpg_cell.yaml",
    "piab_vacuum_cell": _VALIDATOR_FIXTURES / "manifests" / "piab_vacuum_cell.yaml",
    "onrobot_magnetic_cell": _VALIDATOR_FIXTURES / "manifests" / "onrobot_magnetic_cell.yaml",
    "soft_robotics_compliant_cell": _VALIDATOR_FIXTURES / "manifests" / "soft_robotics_compliant_cell.yaml",
    "ati_ft_cell": _VALIDATOR_FIXTURES / "manifests" / "ati_ft_cell.yaml",
    "cognex_vision_cell": _VALIDATOR_FIXTURES / "manifests" / "cognex_vision_cell.yaml",
    "sick_safety_lidar_cell": _VALIDATOR_FIXTURES / "manifests" / "sick_safety_lidar_cell.yaml",
    # Track I-C — more compliant parts (grippers, FT, lidar, 3D vision).
    "robotiq_2f85_cell": _VALIDATOR_FIXTURES / "manifests" / "robotiq_2f85_cell.yaml",
    "schmalz_vacuum_cell": _VALIDATOR_FIXTURES / "manifests" / "schmalz_vacuum_cell.yaml",
    "festo_dhep_cell": _VALIDATOR_FIXTURES / "manifests" / "festo_dhep_cell.yaml",
    "bota_ft_cell": _VALIDATOR_FIXTURES / "manifests" / "bota_ft_cell.yaml",
    "hokuyo_lidar_cell": _VALIDATOR_FIXTURES / "manifests" / "hokuyo_lidar_cell.yaml",
    "ouster_3d_lidar_cell": _VALIDATOR_FIXTURES / "manifests" / "ouster_3d_lidar_cell.yaml",
    "photoneo_motioncam_cell": _VALIDATOR_FIXTURES / "manifests" / "photoneo_motioncam_cell.yaml",
    "zivid_two_cell": _VALIDATOR_FIXTURES / "manifests" / "zivid_two_cell.yaml",
    # Track A — additional ROS-Industrial arm brands (all allied origins).
    "kawasaki_cell": _VALIDATOR_FIXTURES / "manifests" / "kawasaki_cell.yaml",
    "staubli_cell": _VALIDATOR_FIXTURES / "manifests" / "staubli_cell.yaml",
    "comau_cell": _VALIDATOR_FIXTURES / "manifests" / "comau_cell.yaml",
    "mitsubishi_cell": _VALIDATOR_FIXTURES / "manifests" / "mitsubishi_cell.yaml",
    "denso_cell": _VALIDATOR_FIXTURES / "manifests" / "denso_cell.yaml",
    # Track B — additional zero-ROS cobots (all allied origins).
    "doosan_cobot_cell": _VALIDATOR_FIXTURES / "manifests" / "doosan_cobot_cell.yaml",
    "techman_cobot_cell": _VALIDATOR_FIXTURES / "manifests" / "techman_cobot_cell.yaml",
    "kinova_cobot_cell": _VALIDATOR_FIXTURES / "manifests" / "kinova_cobot_cell.yaml",
    # Track D — educational platforms (zero ROS, vendor SDKs, RFC-0011).
    "vex_v5_clawbot": _VALIDATOR_FIXTURES / "manifests" / "vex_v5_clawbot.yaml",
    "lego_spike_driving_base": _VALIDATOR_FIXTURES / "manifests" / "lego_spike_driving_base.yaml",
    "thymio_classroom": _VALIDATOR_FIXTURES / "manifests" / "thymio_classroom.yaml",
    # Track E — NVIDIA Isaac Sim/Lab simulator substrate (zero ROS, RTX host).
    "isaac_arm_sim": _VALIDATOR_FIXTURES / "manifests" / "isaac_arm_sim.yaml",
    # Track F — AUTOSAR Adaptive ECU scaffold (RFC-0019 Draft).
    "autosar_ecu_cell": _VALIDATOR_FIXTURES / "manifests" / "autosar_ecu_cell.yaml",
    # Track G — Autoware research-grade AV (manifest+spec only, RFC-0020 Draft).
    "autoware_av_research": _VALIDATOR_FIXTURES / "manifests" / "autoware_av_research.yaml",
    # RFC-0009 follow-up: compliant legged/biped vendor manifests.
    "anymal_quadruped": _VALIDATOR_FIXTURES / "manifests" / "anymal_quadruped.yaml",
    # Ghost Vision 60 — US origin, SDK access-gated → manifest+spec only.
    "ghost_vision60": _VALIDATOR_FIXTURES / "manifests" / "ghost_vision60.yaml",
    "digit_biped": _VALIDATOR_FIXTURES / "manifests" / "digit_biped.yaml",
    "optimus_biped": _VALIDATOR_FIXTURES / "manifests" / "optimus_biped.yaml",
    "figure_biped": _VALIDATOR_FIXTURES / "manifests" / "figure_biped.yaml",
    "apollo_biped": _VALIDATOR_FIXTURES / "manifests" / "apollo_biped.yaml",
    "neo_biped": _VALIDATOR_FIXTURES / "manifests" / "neo_biped.yaml",
}

ENVELOPE_REGISTRY: dict[str, Path] = {
    "home_default": _VALIDATOR_FIXTURES / "envelopes" / "home_default.yaml",
    "drone_default": _VALIDATOR_FIXTURES / "envelopes" / "drone_default.yaml",
    "drone_with_geofence": _VALIDATOR_FIXTURES / "envelopes" / "drone_with_geofence.yaml",
    "drone_with_altitude_band": _VALIDATOR_FIXTURES / "envelopes" / "drone_with_altitude_band.yaml",
    "drone_with_occupancy_zone": _VALIDATOR_FIXTURES / "envelopes" / "drone_with_occupancy_zone.yaml",
    # RFC-0006: structured link-loss policies.
    "link_loss_rth": _VALIDATOR_FIXTURES / "envelopes" / "link_loss_rth.yaml",
    "link_loss_continue_autonomous": _VALIDATOR_FIXTURES / "envelopes" / "link_loss_continue_autonomous.yaml",
    "link_loss_hover": _VALIDATOR_FIXTURES / "envelopes" / "link_loss_hover.yaml",
    "link_loss_outage_relaxed": _VALIDATOR_FIXTURES / "envelopes" / "link_loss_outage_relaxed.yaml",
    "link_loss_halt": _VALIDATOR_FIXTURES / "envelopes" / "link_loss_halt.yaml",
}

#: Compliance policies (RFC-0004). Names map to YAML files under
#: reference/validator/tests/fixtures/policies/. Two sentinel values are
#: reserved: a fixture may set ``policy: default`` to explicitly load the
#: bundled US-federal default, or ``policy: none`` to skip Pass 5 entirely.
POLICY_REGISTRY: dict[str, Path] = {
    "permissive": _VALIDATOR_FIXTURES / "policies" / "permissive.yaml",
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
    policy: str | None = Field(
        None,
        description=(
            "Compliance policy for Pass 5 (RFC-0004). Names map to "
            "POLICY_REGISTRY; the literal 'none' skips Pass 5; the literal "
            "'default' (or omitting the field) loads the bundled US-federal "
            "default policy."
        ),
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
    speech: SubstrateResult | None = None
    listen: ListenResult | None = None


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


def resolve_policy(name: str | None) -> dict[str, Any] | None | str:
    """Resolve a fixture's `policy:` field to the argument the validator expects.

    Returns one of:
      - ``None`` if the fixture passes ``policy: none`` (Pass 5 should be skipped).
      - ``"DEFAULT"`` (sentinel string) if the fixture omits ``policy:`` or
        passes ``policy: default``. The validator interprets this as
        "load the bundled US-federal default policy".
      - A parsed dict if ``policy`` names a key in ``POLICY_REGISTRY``.
    """
    if name is None or name == "default":
        return "DEFAULT"
    if name == "none":
        return None
    if name not in POLICY_REGISTRY:
        raise KeyError(
            f"unknown policy {name!r}; registered: "
            f"{sorted(POLICY_REGISTRY.keys())!r} (also 'default' and 'none')"
        )
    with POLICY_REGISTRY[name].open(encoding="utf-8") as fh:
        result = yaml.safe_load(fh)
    if not isinstance(result, dict):
        raise ValueError(f"policy {name!r} did not parse as a mapping")
    return result
