"""CompositeAdapter — route one URML program across two substrates.

Real drone deployments are not one box. A PX4 flight controller owns
flight (take-off, waypoints, land, RTL) over MAVLink; a ROS 2 companion
computer owns perception, manipulation, and speech (camera, gripper,
mic) over the ROS graph. Neither `PX4Adapter` nor `RclpyAdapter` alone
can run a program that does both — each cleanly returns
``not_supported`` for the half it doesn't own.

`CompositeAdapter` is the join. It implements the full ``ROSAdapter``
Protocol by holding two backing adapters — a ``flight`` adapter and a
``companion`` adapter — and dispatching each Protocol method to whichever
one actually owns that capability. The URML program, manifest, and
validator are unchanged and unaware: the split lives entirely at the
deployment boundary, exactly like ``adapter.yaml`` pose-resolution does.

## Default routing (the drone policy)

| Method | Backend | Why |
|---|---|---|
| send_takeoff_goal / send_land_goal / send_return_to_home_goal | flight | MAVLink flight commands |
| send_navigation_goal (move_to / hover) | flight | on a multirotor a waypoint is a flight setpoint |
| send_docking_goal | flight | n/a to a multirotor; flight adapter returns a clean not_supported |
| wait_passively | flight | "hold position" on a drone is loiter — a flight concern |
| send_manipulation_goal (grasp / release) | companion | gripper lives on the companion |
| query_detection (detect) | companion | perception lives on the companion |
| run_scan (scan) | companion | the companion has the scan executor; true fly+capture scan is a follow-up |
| take_measurement (measure) | companion | richer sensors on the companion (override to `flight` for MAVLink telemetry) |
| capture_media (capture) | companion | camera on the companion |
| wait_for_condition (wait_for) | companion | events/signals usually ride the ROS graph |
| emit_report (report) | companion | structured upstream reporting on the companion |
| emit_speech / acquire_speech (speak / listen) | companion | TTS/STT on the companion |

The policy is **explicit and overridable**, not magic. Pass
``routing={...}`` to remap any method (e.g. a drone whose rangefinder is
read over MAVLink wants ``take_measurement -> flight``). Unknown method
names or values other than ``flight``/``companion`` are rejected at
construction so a typo can't silently send a goal to the wrong box.

## Dependency posture

This module imports neither pymavlink nor rclpy. It depends only on the
substrate-neutral ``ROSAdapter`` Protocol, so it is hermetically
testable with two mock backends and loads on every host. The canonical
wiring (``flight=PX4Adapter(...)``, ``companion=RclpyAdapter(...)``) is
the caller's to assemble.
"""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from typing import Any, Literal

from urml_ros2_runtime.substrate.base import (
    ProgramCallResult,
    unsupported_program_call,
    CaptureResult,
    DetectionResult,
    ListenResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ROSAdapter,
    ScanResult,
    SubstrateResult,
    WaitResult,
)

FLIGHT = "flight"
COMPANION = "companion"
_BACKENDS = frozenset({FLIGHT, COMPANION})

#: The drone-stack default. Every Protocol method is listed explicitly —
#: an absent method would be a bug, not a "use some default", so
#: construction validates the table covers the whole surface.
_DEFAULT_ROUTING: dict[str, str] = {
    "send_navigation_goal": FLIGHT,
    "send_docking_goal": FLIGHT,
    "send_takeoff_goal": FLIGHT,
    "send_land_goal": FLIGHT,
    "send_return_to_home_goal": FLIGHT,
    "wait_passively": FLIGHT,
    "send_manipulation_goal": COMPANION,
    "query_detection": COMPANION,
    "run_scan": COMPANION,
    "take_measurement": COMPANION,
    "capture_media": COMPANION,
    "wait_for_condition": COMPANION,
    "emit_report": COMPANION,
    "emit_speech": COMPANION,
    "acquire_speech": COMPANION,
}

_PROTOCOL_METHODS = frozenset(_DEFAULT_ROUTING)


class CompositeAdapter:
    """Implements ``ROSAdapter`` by routing each method to one of two backends."""

    def __init__(
        self,
        *,
        flight: ROSAdapter,
        companion: ROSAdapter,
        routing: Mapping[str, str] | None = None,
    ) -> None:
        self._flight = flight
        self._companion = companion
        table = dict(_DEFAULT_ROUTING)
        if routing is not None:
            for method, backend in routing.items():
                if method not in _PROTOCOL_METHODS:
                    raise ValueError(
                        f"unknown ROSAdapter method in routing override: {method!r}. "
                        f"Known: {sorted(_PROTOCOL_METHODS)}"
                    )
                if backend not in _BACKENDS:
                    raise ValueError(
                        f"routing[{method!r}] must be {FLIGHT!r} or {COMPANION!r}, "
                        f"got {backend!r}"
                    )
                table[method] = backend
        self._routing = table
        self._closed = False

    # ------------------------------------------------------------------
    # Routing + lifecycle
    # ------------------------------------------------------------------

    def _backend(self, method: str) -> ROSAdapter:
        return self._flight if self._routing[method] == FLIGHT else self._companion

    def routing_for(self, method: str) -> str:
        """Return ``'flight'`` or ``'companion'`` for a Protocol method name.

        Exposed for diagnostics and tests — lets a caller verify where a
        given primitive will dispatch without invoking it.
        """
        if method not in self._routing:
            raise KeyError(f"{method!r} is not a routed ROSAdapter method")
        return self._routing[method]

    def close(self) -> None:
        """Close both backends if they expose ``close()``.

        Idempotent: a second call is a no-op, matching the contract
        ``PX4Adapter`` / ``RclpyAdapter`` follow, so wrapping them in a
        composite doesn't double-invoke their teardown.
        """
        if self._closed:
            return
        self._closed = True
        for backend in (self._flight, self._companion):
            close = getattr(backend, "close", None)
            if callable(close):
                with suppress(Exception):
                    close()

    def __enter__(self) -> CompositeAdapter:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Protocol surface — each method is a thin route-and-delegate.
    # Signatures mirror ROSAdapter exactly (mypy --strict checks this
    # against the Protocol via the conformance test).
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
        return self._backend("send_navigation_goal").send_navigation_goal(
            location=location, pose=pose, frame=frame, carrying=carrying, speed=speed
        )

    def send_docking_goal(
        self, *, station: str, service: str, until: str | None = None
    ) -> NavigationResult:
        return self._backend("send_docking_goal").send_docking_goal(
            station=station, service=service, until=until
        )

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
        return self._backend("send_manipulation_goal").send_manipulation_goal(
            action=action,
            target=target,
            force_n=force_n,
            approach=approach,
            release_mode=release_mode,
            release_at=release_at,
        )

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        return self._backend("query_detection").query_detection(
            object_class=object_class,
            attributes=attributes,
            where_near=where_near,
            where_within=where_within,
        )

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
        return self._backend("run_scan").run_scan(
            area=area,
            pattern=pattern,
            overlap=overlap,
            altitude=altitude,
            media=media,
            sensor=sensor,
        )

    def take_measurement(
        self, *, what: str, target: str | None, sensor: str | None
    ) -> MeasurementResult:
        return self._backend("take_measurement").take_measurement(
            what=what, target=target, sensor=sensor
        )

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return self._backend("capture_media").capture_media(
            media=media,
            target=target,
            duration_seconds=duration_seconds,
            attributes=attributes,
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
        return self._backend("wait_for_condition").wait_for_condition(
            kind=kind,
            name=name,
            input_mode=input_mode,
            threshold=threshold,
            timeout_seconds=timeout_seconds,
        )

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        return self._backend("wait_passively").wait_passively(
            duration_seconds=duration_seconds
        )

    def emit_report(
        self,
        *,
        to: str,
        facts: dict[str, Any],
        attachments: list[str] | None,
        status: Literal["success", "partial", "failure"],
        severity: Literal["info", "notice", "warning", "error"],
    ) -> SubstrateResult:
        return self._backend("emit_report").emit_report(
            to=to,
            facts=facts,
            attachments=attachments,
            status=status,
            severity=severity,
        )

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        return self._backend("emit_speech").emit_speech(
            utterance=utterance, locale=locale, style=style, interrupt=interrupt
        )

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        return self._backend("acquire_speech").acquire_speech(
            prompt=prompt,
            locale=locale,
            timeout_seconds=timeout_seconds,
            expected=expected,
            choices=choices,
        )

    def send_takeoff_goal(
        self, *, altitude: float, climb_rate: float | None = None
    ) -> NavigationResult:
        return self._backend("send_takeoff_goal").send_takeoff_goal(
            altitude=altitude, climb_rate=climb_rate
        )

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        return self._backend("send_land_goal").send_land_goal(at=at, precision=precision)

    def send_return_to_home_goal(
        self, *, speed: float | None = None, altitude: float | None = None
    ) -> NavigationResult:
        return self._backend("send_return_to_home_goal").send_return_to_home_goal(
            speed=speed, altitude=altitude
        )

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('bare_autopilot')
