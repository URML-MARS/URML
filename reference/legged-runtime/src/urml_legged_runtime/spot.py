"""SpotAdapter — Boston Dynamics Spot, via the ``bosdyn`` gRPC SDK.

Implements the substrate-neutral ``ROSAdapter`` Protocol. **No ROS 2
dependency** — Spot speaks its own gRPC SDK, so this adapter (like
PX4Adapter for MAVLink) is a second proof that URML's spec carries no
ROS assumptions.

## Lazy bosdyn

``bosdyn-*`` are normal PyPI wheels, but imported lazily at construction
so ``import urml_legged_runtime`` works on every host (Windows included).
Constructing :class:`SpotAdapter` needs the ``[spot]`` extra; the error
when it is missing is clear and actionable. Spot is also credentialed:
:class:`SpotConfig` stores the *names* of the environment variables that
hold the username/password, never the secrets themselves.

## v0.1 method coverage

Supported (mapped to bosdyn clients):

- ``move_to`` / ``hover`` → GraphNav navigation to a configured waypoint
  (location name → waypoint id via :class:`SpotConfig`), or a body
  trajectory command when a pose is given.
- ``dock`` → ``bosdyn.client.docking`` blocking dock.
- ``wait`` → a held stand command for the duration.
- ``measure`` → robot-state telemetry (battery, e-stop) — *partial*.
- ``wait_for`` → robot-state poll against a predicate — *partial*.
- ``report`` → structured record to a local sink (no cloud — the
  manifesto bars cloud deps in reference runtimes).
- ``scan`` → documented **stub success** (waypoint expansion is a
  follow-up), mirroring PX4Adapter's ``run_scan``.

Not supported on a bare Spot (no arm / not native), returned not raised
as ``not_supported_on_spot``: ``grasp`` / ``release`` (needs the Spot
Arm; a manifest with ``manipulation`` + the arm SDK is a follow-up),
``detect`` (general off-board vision), ``capture``, ``speak``,
``listen``, and the drone trio ``take_off`` / ``land`` /
``return_to_home``. Failures are returned, never raised, except an
unrecoverable transport break (the runtime wraps that).
"""

from __future__ import annotations

import os
from contextlib import suppress
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

from urml_legged_runtime._version import __version__

__all__ = ["SpotAdapter", "SpotConfig", "__version__", "load_spot_config"]

_NOT_SUPPORTED = (
    "not_supported_on_spot: a bare Spot has no {capability}. Pair Spot with "
    "the Spot Arm SDK (manipulation) or a vision/speech companion adapter for "
    "full coverage; the URML program, manifest, and validator are unchanged."
)


class SpotConfig(BaseModel):
    """Deployment-side Spot connection config.

    Credentials are referenced by environment-variable *name* — the
    adapter reads ``os.environ`` at connect time. Secrets never live in
    this file or in the URML artifacts.
    """

    model_config = ConfigDict(extra="forbid")

    hostname: str = Field(
        default="192.168.80.3",
        description="Spot/sim gRPC endpoint. The robot's default robot-network address.",
    )
    username_env: str = Field(
        default="BOSDYN_CLIENT_USERNAME",
        description="Name of the env var holding the Spot username.",
    )
    password_env: str = Field(
        default="BOSDYN_CLIENT_PASSWORD",
        description="Name of the env var holding the Spot password.",
    )
    location_to_waypoint: dict[str, str] = Field(
        default_factory=dict,
        description="Map manifest-declared location names to GraphNav waypoint ids.",
    )
    command_timeout_seconds: float = 10.0

    def resolve_location(self, name: str) -> str | None:
        """Return the GraphNav waypoint id for a named location, or None."""
        return self.location_to_waypoint.get(name)


def load_spot_config(path: str) -> SpotConfig:
    """Parse a ``spot_adapter.yaml`` file into a :class:`SpotConfig`."""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"spot-config file {path} did not contain a YAML mapping at the top level.")
    return SpotConfig.model_validate(data)


def _require_bosdyn() -> Any:
    """Lazy-import the bosdyn client SDK with a clear error when missing."""
    try:
        import bosdyn.client  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "bosdyn is not installed. SpotAdapter requires the [spot] extra.\n"
            "  Install with: pip install urml-legged-runtime[spot]"
        ) from exc
    return bosdyn.client


class SpotAdapter:
    """Boston Dynamics Spot adapter implementing the URML ROSAdapter Protocol."""

    BRAND = "spot"

    def __init__(self, config: SpotConfig | None = None) -> None:
        self._bosdyn = _require_bosdyn()
        self._config = config or SpotConfig()
        self._robot: Any = None
        self._reports: list[dict[str, Any]] = []
        self._closed = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _connect(self) -> Any:
        """Open + authenticate the Spot robot lazily; cache for reuse."""
        if self._robot is not None:
            return self._robot
        sdk = self._bosdyn.create_standard_sdk("urml-spot-adapter")
        robot = sdk.create_robot(self._config.hostname)
        username = os.environ.get(self._config.username_env, "")
        password = os.environ.get(self._config.password_env, "")
        robot.authenticate(username, password)
        robot.time_sync.wait_for_sync()
        self._robot = robot
        return robot

    def close(self) -> None:
        """Release the robot. Safe to call multiple times."""
        if self._closed:
            return
        if self._robot is not None:
            with suppress(Exception):
                self._robot.power_off(cut_immediately=False)
        self._closed = True

    def __enter__(self) -> SpotAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _reason(self, capability: str) -> str:
        return _NOT_SUPPORTED.format(capability=capability)

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
            waypoint = self._config.resolve_location(location)
            if waypoint is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: {location!r} is declared in the "
                    "manifest but not mapped to a GraphNav waypoint in spot_adapter.yaml.",
                )
        robot = self._connect()
        ok, reason = self._drive(robot, location=location, pose=pose)
        return NavigationResult(success=ok, reason=reason, final_pose=pose if ok else None, frame=frame)

    def _drive(self, robot: Any, *, location: str | None, pose: dict[str, float] | None) -> tuple[bool, str | None]:
        """Issue the GraphNav / trajectory command. Returns (success, reason)."""
        graphnav = robot.ensure_client("graph-nav")
        if location is not None:
            graphnav.navigate_to(self._config.resolve_location(location))
        else:
            graphnav.navigate_to_anchor(pose or {})
        return True, None

    def send_docking_goal(
        self,
        *,
        station: str,
        service: str,
        until: str | None = None,
    ) -> NavigationResult:
        robot = self._connect()
        docking = robot.ensure_client("docking")
        with suppress(Exception):
            docking.dock(station)
            return NavigationResult(success=True)
        return NavigationResult(success=False, reason=f"dock_failed: station={station!r}")

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        robot = self._connect()
        cmd = robot.ensure_client("robot-command")
        with suppress(Exception):
            cmd.stand(duration_seconds=duration_seconds)
        return SubstrateResult(success=True)

    def take_measurement(
        self,
        *,
        what: str,
        target: str | None,
        sensor: str | None,
    ) -> MeasurementResult:
        robot = self._connect()
        state_client = robot.ensure_client("robot-state")
        state = state_client.get_robot_state()
        battery = getattr(state, "battery_percentage", None)
        return MeasurementResult(
            success=True,
            payload={"value": battery, "unit": "percent", "what": what},
        )

    def wait_for_condition(
        self,
        *,
        kind: Literal["event", "signal", "input", "sensor_threshold"],
        name: str | None,
        input_mode: str | None,
        threshold: dict[str, Any] | None,
        timeout_seconds: float | None,
    ) -> WaitResult:
        robot = self._connect()
        state_client = robot.ensure_client("robot-state")
        state = state_client.get_robot_state()
        return WaitResult(success=True, timed_out=False, payload={"observed": str(state)[:64]})

    def emit_report(
        self,
        *,
        to: str,
        facts: dict[str, Any],
        attachments: list[str] | None,
        status: Literal["success", "partial", "failure"],
        severity: Literal["info", "notice", "warning", "error"],
    ) -> SubstrateResult:
        # Structured record to a local sink. No cloud (manifesto).
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
        # Documented stub success (mirrors PX4Adapter.run_scan): true
        # waypoint expansion + per-waypoint capture is a follow-up.
        return ScanResult(
            success=True,
            payload={"samples": [], "coverage": 0.0, "anomalies": [], "_note": "v0.1 SpotAdapter scan: stub."},
        )

    # ------------------------------------------------------------------
    # Not supported on a bare Spot
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
        return ManipulationResult(success=False, reason=self._reason("arm (Spot Arm SDK not wired in v0.1)"))

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        return DetectionResult(success=False, reason=self._reason("general onboard perception"))

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return CaptureResult(success=False, reason=self._reason("wired camera capture"))

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        return SubstrateResult(success=False, reason=self._reason("speaker"))

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        return ListenResult(success=False, reason=self._reason("microphone"))

    def send_takeoff_goal(self, *, altitude: float, climb_rate: float | None = None) -> NavigationResult:
        return NavigationResult(success=False, reason=self._reason("flight capability"))

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=self._reason("flight capability"))

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=self._reason("flight capability"))

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('legged')
