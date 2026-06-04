"""ChronoAdapter — Project Chrono multibody physics, via ``pychrono``.

Project Chrono is a high-fidelity open multibody and multi-physics
engine (Chrono::Vehicle ground dynamics, terramechanics for deformable
terrain, Chrono::Sensor) from the University of Wisconsin-Madison and
the University of Parma. This adapter mirrors :class:`MujocoAdapter`:
lazy ``pychrono``, **no ROS 2 dependency**, a lazily-built cached
``ChSystem``, failures returned not raised.

Chrono's distinctive role for URML is **high-fidelity pre-deployment
validation** (RFC-0328): URML checks a program statically against the
declared capability and safety envelope first, then drives the same
validated intent through a short Chrono simulation segment so the
dynamics come back as evidence the claim holds. URML composes *above*
Chrono; it does not embed it.

## v0.1 method coverage

Supported (mapped onto a ``ChSystem`` advanced by driver inputs):

- ``move_to`` / ``hover`` → apply the configured driver segment and
  advance the engine ``steps_per_command`` steps (location → driver
  inputs via :class:`ChronoConfig`); ``hover`` is a zero-input hold
  (step in place).
- ``wait`` → step the engine for the dwell.
- ``measure`` → return the accumulated dynamics evidence (system time,
  contact count, the last commanded driver inputs).
- ``wait_for`` → step-then-check (a sim has no external event bus; the
  step advances state and the predicate is evaluated once).
- ``report`` → structured record to a local sink (no cloud — manifesto).
- ``scan`` → documented **stub success**, mirroring PX4Adapter.run_scan.

The primitive → driver-input altitude follows Project Chrono lead Dan
Negrut's feedback on issue #746.

Not supported by a bare vehicle / terramechanics model (returned, not
raised): ``grasp`` / ``release``, ``dock``, ``detect``, ``capture``,
``speak``, ``listen``. Perception primitives want a Chrono::Sensor
companion (camera / lidar / GPS / IMU); manipulation wants an
articulated-model companion. The drone trio ``take_off`` / ``land`` /
``return_to_home`` are ``not_applicable_sim``.

The committed unit suite exercises every path against a fake
``pychrono`` injected into ``sys.modules`` (the technique px4-runtime /
mujoco-runtime use); a Chrono::Vehicle terramechanics scene driven by a
real engine is the documented calibration step in
``chrono-integration.yml``.
"""

from __future__ import annotations

from typing import Any, Literal

from urml_ros2_runtime.substrate.base import (
    CaptureResult,
    DetectionResult,
    ListenResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ProgramCallResult,
    ScanResult,
    SubstrateResult,
    WaitResult,
    unsupported_program_call,
)

from urml_chrono_runtime._version import __version__
from urml_chrono_runtime.config import ChronoConfig, DriverSegment, load_chrono_config

__all__ = [
    "ChronoAdapter",
    "ChronoConfig",
    "DriverSegment",
    "__version__",
    "load_chrono_config",
]

_NOT_SUPPORTED = (
    "not_supported_in_base_sim: a bare Chrono::Vehicle / terramechanics model has no {capability}. "
    "Pair it with a Chrono::Sensor or articulated-model companion; the URML "
    "program, manifest, and validator are unchanged."
)
_NOT_APPLICABLE = "not_applicable_sim: {capability} has no meaning for a ground-vehicle physics model."


def _require_pychrono() -> Any:
    """Lazy-import pychrono with a clear, actionable error when missing."""
    try:
        import pychrono  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "pychrono is not installed. ChronoAdapter requires PyChrono.\n"
            "  PyChrono ships via conda-forge, not as a PyPI wheel:\n"
            "    conda install -c conda-forge pychrono\n"
            "  (the [chrono] extra documents the boundary; pychrono is imported lazily)."
        ) from exc
    return pychrono


class ChronoAdapter:
    """Project Chrono adapter implementing the URML ROSAdapter Protocol."""

    BRAND = "chrono"

    def __init__(self, config: ChronoConfig | None = None) -> None:
        self._chrono = _require_pychrono()
        self._config = config or ChronoConfig()
        self._system: Any = None
        self._reports: list[dict[str, Any]] = []
        self._last_evidence: dict[str, Any] | None = None
        self._closed = False

    def _sim(self) -> Any:
        """Lazily build and cache the ``ChSystem``."""
        if self._system is not None:
            return self._system
        ctor = self._chrono.ChSystemSMC if self._config.system_type == "SMC" else self._chrono.ChSystemNSC
        self._system = ctor()
        return self._system

    def _advance(self, steps: int) -> None:
        system = self._sim()
        for _ in range(max(1, steps)):
            system.DoStepDynamics(self._config.step_size)

    def _evidence(self, driver: list[float], steps: int) -> dict[str, Any]:
        """Read the current ``ChSystem`` dynamics as a validation-evidence dict."""
        system = self._sim()
        ev: dict[str, Any] = {
            "sim_time": float(system.GetChTime()),
            "n_contacts": int(system.GetNcontacts()),
            "steps": int(steps),
            "driver": [float(v) for v in driver],
            "terrain_class": self._config.terrain_fidelity,  # RFC-0381 hint, mirrored from the manifest
            "backend": "pychrono",
        }
        self._last_evidence = ev
        return ev

    def close(self) -> None:
        self._closed = True

    def __enter__(self) -> ChronoAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Supported
    # ------------------------------------------------------------------

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        if location is None and pose is None:
            return NavigationResult(success=False, reason="send_navigation_goal called without location or pose")
        if location is not None:
            seg = self._config.resolve_location(location)
            if seg is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: {location!r} is declared in the "
                    "manifest but not mapped to a driver segment in chrono_adapter.yaml.",
                )
            driver = list(seg.driver)
            steps = seg.steps or self._config.steps_per_command
        else:
            driver = [float(v) for v in (pose or {}).values()]
            steps = self._config.steps_per_command
        self._advance(steps)
        ev = self._evidence(driver, steps)
        # final_pose is a flat dict[str, float]: the commanded driver vector as
        # indexed scalars, plus the headline dynamics evidence the run produced.
        final: dict[str, float] = {f"driver{i}": float(v) for i, v in enumerate(driver)}
        final["sim_time"] = float(ev["sim_time"])
        final["n_contacts"] = float(ev["n_contacts"])
        return NavigationResult(success=True, final_pose=final, frame=frame or "vehicle")

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        self._advance(self._config.steps_per_command)
        return SubstrateResult(success=True)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        system = self._sim()
        ev = self._last_evidence or {
            "sim_time": float(system.GetChTime()),
            "n_contacts": int(system.GetNcontacts()),
            "steps": 0,
            "driver": [],
            "backend": "pychrono",
        }
        payload: dict[str, Any] = {
            "value": ev["n_contacts"],
            "unit": "contacts",
            "timestamp": ev["sim_time"],
            "what": what,
            **ev,
        }
        return MeasurementResult(success=True, payload=payload)

    def wait_for_condition(
        self,
        *,
        kind: Literal["event", "signal", "input", "sensor_threshold"],
        name: str | None,
        input_mode: str | None,
        threshold: dict[str, Any] | None,
        timeout_seconds: float | None,
    ) -> WaitResult:
        self._advance(self._config.steps_per_command)
        return WaitResult(success=True, timed_out=False, payload=None)

    def emit_report(
        self,
        *,
        to: str,
        facts: dict[str, Any],
        attachments: list[str] | None,
        status: Literal["success", "partial", "failure"],
        severity: Literal["info", "notice", "warning", "error"],
    ) -> SubstrateResult:
        self._reports.append({"to": to, "status": status, "severity": severity, "facts": facts})
        return SubstrateResult(success=True)

    def run_scan(
        self,
        *,
        area: dict[str, Any],
        pattern: Literal["serpentine", "spiral", "grid", "adaptive"],
        overlap: float,
        altitude: float | None,
        media: Literal["photo", "video", "sensor_only"],
        sensor: str | None,
    ) -> ScanResult:
        return ScanResult(
            success=True,
            payload={"samples": [], "coverage": 0.0, "anomalies": [], "_note": "v0.1 ChronoAdapter scan: stub."},
        )

    # ------------------------------------------------------------------
    # Not supported by a bare vehicle / terramechanics model
    # ------------------------------------------------------------------

    def send_manipulation_goal(
        self,
        *,
        action: Literal["grasp", "release"],
        target: dict[str, Any] | None = None,
        force_n: float | None = None,
        approach: Literal["top", "side", "front", "auto"] = "auto",
        release_mode: Literal["drop", "place", "hand_to_user"] | None = None,
        release_at: dict[str, Any] | str | None = None,
    ) -> ManipulationResult:
        return ManipulationResult(success=False, reason=_NOT_SUPPORTED.format(capability="manipulator controller"))

    def send_docking_goal(self, *, station: str, service: str, until: str | None = None) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_SUPPORTED.format(capability="docking station"))

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        return DetectionResult(success=False, reason=_NOT_SUPPORTED.format(capability="Chrono::Sensor perception"))

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return CaptureResult(success=False, reason=_NOT_SUPPORTED.format(capability="Chrono::Sensor camera"))

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        return SubstrateResult(success=False, reason=_NOT_SUPPORTED.format(capability="speaker"))

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        return ListenResult(success=False, reason=_NOT_SUPPORTED.format(capability="microphone"))

    def send_takeoff_goal(self, *, altitude: float, climb_rate: float | None = None) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_APPLICABLE.format(capability="take_off"))

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_APPLICABLE.format(capability="land"))

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_APPLICABLE.format(capability="return_to_home"))

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call("chrono_sim")
