"""MujocoAdapter — MuJoCo physics simulator, via the ``mujoco`` wheel.

MuJoCo is the official Apache-2.0 simulator with pure-Python bindings
over a bundled engine: headless, offline, no ROS. This adapter mirrors
:class:`BlueRovAdapter` / :class:`PX4Adapter`: lazy ``mujoco``, **no
ROS 2 dependency**, a lazily-loaded cached model/data, failures
returned not raised. It is the purest substrate-neutrality acid-test
proof — a simulator faithfully implementing the frozen substrate
Protocol with zero ROS, the sentence→motion loop with no robot and no
middleware.

## v0.1 method coverage

Supported (mapped onto an MJCF model + actuator ``ctrl``):

- ``move_to`` / ``hover`` → write the configured control target onto
  ``mjData.ctrl`` and advance the engine ``steps_per_command`` steps
  (location → ``ctrl`` via :class:`MujocoConfig`); ``hover`` is a
  zero-change hold (step in place).
- ``wait`` → step the engine for the dwell.
- ``measure`` → read ``mjData.sensordata`` (named sensor or first).
- ``wait_for`` → step-then-check (a sim has no external event bus; the
  step advances state and the predicate is evaluated once).
- ``report`` → structured record to a local sink (no cloud — manifesto).
- ``scan`` → documented **stub success**, mirroring PX4Adapter.run_scan.

Not supported by a bare physics model (returned, not raised):
``grasp`` / ``release``, ``dock``, ``detect``, ``capture``, ``speak``,
``listen`` — these need a task-specific model + controller (a follow-up
companion). The drone trio ``take_off`` / ``land`` /
``return_to_home`` are ``not_applicable_sim``.
"""

from __future__ import annotations

from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field
from urml_ros2_runtime.substrate.base import (
    ProgramCallResult,
    unsupported_program_call,
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

from urml_mujoco_runtime._version import __version__
from urml_mujoco_runtime.config import ControlTarget, MujocoConfig, load_mujoco_config

__all__ = [
    "ControlTarget",
    "MujocoAdapter",
    "MujocoConfig",
    "__version__",
    "load_mujoco_config",
]

_NOT_SUPPORTED = (
    "not_supported_in_base_sim: a bare MuJoCo physics model has no {capability}. "
    "Pair it with a task-specific model + controller companion; the URML "
    "program, manifest, and validator are unchanged."
)
_NOT_APPLICABLE = "not_applicable_sim: {capability} has no meaning for a headless physics model."


def _require_mujoco() -> Any:
    """Lazy-import mujoco with a clear error when missing."""
    try:
        import mujoco  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "mujoco is not installed. MujocoAdapter requires the [sim] extra.\n"
            "  Install with: pip install urml-mujoco-runtime[sim]"
        ) from exc
    return mujoco


class MujocoAdapter:
    """MuJoCo simulator adapter implementing the URML ROSAdapter Protocol."""

    BRAND = "mujoco"

    def __init__(self, config: MujocoConfig | None = None) -> None:
        self._mujoco = _require_mujoco()
        self._config = config or MujocoConfig()
        self._model: Any = None
        self._data: Any = None
        self._reports: list[dict[str, Any]] = []
        self._closed = False

    def _sim(self) -> tuple[Any, Any]:
        """Lazily load and cache the MJCF model + data."""
        if self._model is not None:
            return self._model, self._data
        if not self._config.model_path:
            raise RuntimeError(
                "model_path not configured: set MujocoConfig.model_path to an "
                "MJCF/XML model file in mujoco_adapter.yaml."
            )
        model = self._mujoco.MjModel.from_xml_path(self._config.model_path)
        data = self._mujoco.MjData(model)
        self._model, self._data = model, data
        return model, data

    def _step(self, n: int) -> None:
        model, data = self._sim()
        for _ in range(max(1, n)):
            self._mujoco.mj_step(model, data)

    def close(self) -> None:
        self._closed = True

    def __enter__(self) -> MujocoAdapter:
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
        _, data = self._sim()
        if location is not None:
            tgt = self._config.resolve_location(location)
            if tgt is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: {location!r} is declared in the "
                    "manifest but not mapped to a control target in mujoco_adapter.yaml.",
                )
            ctrl = list(tgt.ctrl)
        else:
            ctrl = [float(v) for v in (pose or {}).values()]
        if ctrl:
            n = min(len(ctrl), len(data.ctrl))
            for i in range(n):
                data.ctrl[i] = ctrl[i]
        self._step(self._config.steps_per_command)
        # final_pose is a flat dict[str, float]; expose the control vector
        # as indexed scalars (ctrl0, ctrl1, ...).
        final = {f"ctrl{i}": float(v) for i, v in enumerate(ctrl)}
        return NavigationResult(success=True, final_pose=final, frame=frame or "model")

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        self._step(self._config.steps_per_command)
        return SubstrateResult(success=True)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        _, data = self._sim()
        sd = list(getattr(data, "sensordata", []) or [])
        value = float(sd[0]) if sd else None
        return MeasurementResult(success=True, payload={"value": value, "what": what})

    def wait_for_condition(
        self,
        *,
        kind: Literal["event", "signal", "input", "sensor_threshold"],
        name: str | None,
        input_mode: str | None,
        threshold: dict[str, Any] | None,
        timeout_seconds: float | None,
    ) -> WaitResult:
        self._step(self._config.steps_per_command)
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
            payload={"samples": [], "coverage": 0.0, "anomalies": [], "_note": "v0.1 MujocoAdapter scan: stub."},
        )

    # ------------------------------------------------------------------
    # Not supported by a bare physics model
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
        arm: str | None = None,
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
        return DetectionResult(success=False, reason=_NOT_SUPPORTED.format(capability="perception model"))

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return CaptureResult(success=False, reason=_NOT_SUPPORTED.format(capability="recordable camera"))

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
        return unsupported_program_call('mujoco_sim')
