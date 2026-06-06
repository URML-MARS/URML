"""MockROSAdapter — hermetic substrate for tests and development without ROS.

The mock implements ``ROSAdapter`` end-to-end:

- Every call is recorded in ``call_log`` for assertions.
- Every method returns a configurable result; sensible success defaults
  cover the canonical red-mug demo without any setup.
- Per-method overrides let tests inject failures, custom detection
  payloads, etc.

This lets the URML runtime be developed and tested on any host, including
CI and Windows machines, with no ROS 2 installation. The real
``RclpyAdapter`` lands as a follow-up.
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
    TrajectoryPlanResult,
    WaitResult,
)


class MockROSAdapter:
    """Implements ``ROSAdapter`` without ROS. Tests should use this.

    All methods record into ``call_log`` and return success by default. Test
    cases can override the per-method defaults to inject failures or
    custom payloads — see the ``set_*`` setters.
    """

    def __init__(self) -> None:
        self.call_log: list[dict[str, Any]] = []

        # Overrides — None means "use the sensible default for this call".
        self._navigation_override: NavigationResult | None = None
        self._dock_override: NavigationResult | None = None
        self._takeoff_override: NavigationResult | None = None
        self._land_override: NavigationResult | None = None
        self._rth_override: NavigationResult | None = None
        self._manipulation_override: ManipulationResult | None = None
        self._detection_override: DetectionResult | None = None
        self._scan_override: ScanResult | None = None
        self._measurement_override: MeasurementResult | None = None
        self._capture_override: CaptureResult | None = None
        self._wait_for_override: WaitResult | None = None
        self._wait_passive_override: SubstrateResult | None = None
        self._report_override: SubstrateResult | None = None
        self._speech_override: SubstrateResult | None = None
        self._listen_override: ListenResult | None = None
        self._call_program_override: ProgramCallResult | None = None

    # ----- Overrides -----

    def set_navigation_result(self, result: NavigationResult) -> None:
        """Make the next `send_navigation_goal` return this result."""
        self._navigation_override = result

    def set_dock_result(self, result: NavigationResult) -> None:
        self._dock_override = result

    def set_takeoff_result(self, result: NavigationResult) -> None:
        self._takeoff_override = result

    def set_land_result(self, result: NavigationResult) -> None:
        self._land_override = result

    def set_return_to_home_result(self, result: NavigationResult) -> None:
        self._rth_override = result

    def set_manipulation_result(self, result: ManipulationResult) -> None:
        self._manipulation_override = result

    def set_detection_result(self, result: DetectionResult) -> None:
        self._detection_override = result

    def set_scan_result(self, result: ScanResult) -> None:
        self._scan_override = result

    def set_measurement_result(self, result: MeasurementResult) -> None:
        self._measurement_override = result

    def set_capture_result(self, result: CaptureResult) -> None:
        self._capture_override = result

    def set_wait_for_result(self, result: WaitResult) -> None:
        self._wait_for_override = result

    def set_wait_passive_result(self, result: SubstrateResult) -> None:
        self._wait_passive_override = result

    def set_report_result(self, result: SubstrateResult) -> None:
        self._report_override = result

    def set_speech_result(self, result: SubstrateResult) -> None:
        """Make the next `emit_speech` return this result."""
        self._speech_override = result

    def set_listen_result(self, result: ListenResult) -> None:
        """Make the next `acquire_speech` return this result."""
        self._listen_override = result

    def set_call_program_result(self, result: ProgramCallResult) -> None:
        """Make the next `call_named_program` return this result."""
        self._call_program_override = result

    # ----- Substrate methods -----

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        self.call_log.append(
            {
                "method": "send_navigation_goal",
                "location": location,
                "pose": pose,
                "frame": frame,
                "carrying": carrying,
                "speed": speed,
            }
        )
        if self._navigation_override is not None:
            return self._navigation_override
        # Default success: echo back the target as the "final pose".
        return NavigationResult(
            success=True,
            final_pose=pose,
            frame=frame,
        )

    def send_docking_goal(
        self,
        *,
        station: str,
        service: str,
        until: str | None = None,
    ) -> NavigationResult:
        self.call_log.append(
            {
                "method": "send_docking_goal",
                "station": station,
                "service": service,
                "until": until,
            }
        )
        if self._dock_override is not None:
            return self._dock_override
        return NavigationResult(success=True)

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
        self.call_log.append(
            {
                "method": "send_manipulation_goal",
                "action": action,
                "target": target,
                "force_n": force_n,
                "approach": approach,
                "release_mode": release_mode,
                "release_at": release_at,
            }
        )
        if self._manipulation_override is not None:
            return self._manipulation_override
        return ManipulationResult(success=True, grip_force_n=force_n)

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        self.call_log.append(
            {
                "method": "query_detection",
                "object_class": object_class,
                "attributes": attributes,
                "where_near": where_near,
                "where_within": where_within,
            }
        )
        if self._detection_override is not None:
            return self._detection_override
        # Default: a stub detection that matches the requested class.
        return DetectionResult(
            success=True,
            payload={
                "class": object_class,
                "pose": {"x": 1.0, "y": 1.0, "z": 0.0},
                "frame": "map",
                "attributes": attributes or {},
                "confidence": 0.95,
            },
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
        self.call_log.append(
            {
                "method": "run_scan",
                "area": area,
                "pattern": pattern,
                "overlap": overlap,
                "altitude": altitude,
                "media": media,
                "sensor": sensor,
            }
        )
        if self._scan_override is not None:
            return self._scan_override
        return ScanResult(
            success=True,
            payload={"samples": [], "coverage": 1.0, "anomalies": []},
        )

    def take_measurement(
        self,
        *,
        what: str,
        target: str | None,
        sensor: str | None,
    ) -> MeasurementResult:
        self.call_log.append(
            {
                "method": "take_measurement",
                "what": what,
                "target": target,
                "sensor": sensor,
            }
        )
        if self._measurement_override is not None:
            return self._measurement_override
        return MeasurementResult(
            success=True,
            payload={"value": 0.0, "unit": "unspecified", "timestamp": 0.0},
        )

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        self.call_log.append(
            {
                "method": "capture_media",
                "media": media,
                "target": target,
                "duration_seconds": duration_seconds,
                "attributes": attributes,
            }
        )
        if self._capture_override is not None:
            return self._capture_override
        return CaptureResult(
            success=True,
            payload={
                "type": media,
                "format": (attributes or {}).get("format", "default"),
                "pose": {"x": 0.0, "y": 0.0},
                "frame": "map",
                "uri": "mock://capture/0001",
            },
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
        self.call_log.append(
            {
                "method": "wait_for_condition",
                "kind": kind,
                "name": name,
                "input_mode": input_mode,
                "threshold": threshold,
                "timeout_seconds": timeout_seconds,
            }
        )
        if self._wait_for_override is not None:
            return self._wait_for_override
        return WaitResult(success=True, timed_out=False)

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        self.call_log.append(
            {"method": "wait_passively", "duration_seconds": duration_seconds}
        )
        if self._wait_passive_override is not None:
            return self._wait_passive_override
        return SubstrateResult(success=True)

    def emit_report(
        self,
        *,
        to: str,
        facts: dict[str, Any],
        attachments: list[str] | None,
        status: Literal["success", "partial", "failure"],
        severity: Literal["info", "notice", "warning", "error"],
    ) -> SubstrateResult:
        self.call_log.append(
            {
                "method": "emit_report",
                "to": to,
                "facts": facts,
                "attachments": attachments,
                "status": status,
                "severity": severity,
            }
        )
        if self._report_override is not None:
            return self._report_override
        return SubstrateResult(success=True)

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        self.call_log.append(
            {
                "method": "emit_speech",
                "utterance": utterance,
                "locale": locale,
                "style": style,
                "interrupt": interrupt,
            }
        )
        if self._speech_override is not None:
            return self._speech_override
        return SubstrateResult(success=True)

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        self.call_log.append(
            {
                "method": "acquire_speech",
                "prompt": prompt,
                "locale": locale,
                "timeout_seconds": timeout_seconds,
                "expected": expected,
                "choices": choices,
            }
        )
        if self._listen_override is not None:
            return self._listen_override
        # Default: a deterministic mock transcription.
        # `expected: choice` picks the first declared choice (index 0).
        # `expected: confirmation` returns "yes".
        # `expected: free_form` returns a generic transcription.
        if expected == "choice":
            assert choices is not None  # validated by ListenArgs at parse time
            payload = {
                "transcription": choices[0],
                "confidence": 0.95,
                "choice_index": 0,
            }
        elif expected == "confirmation":
            payload = {"transcription": "yes", "confidence": 0.95, "choice_index": None}
        else:
            payload = {
                "transcription": "(mock spoken input)",
                "confidence": 0.95,
                "choice_index": None,
            }
        return ListenResult(success=True, timed_out=False, payload=payload)

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        self.call_log.append(
            {
                "method": "call_named_program",
                "name": name,
                "args": args,
            }
        )
        if self._call_program_override is not None:
            return self._call_program_override
        return ProgramCallResult(success=True)

    # ----- Drone-profile dispatch -----

    def send_takeoff_goal(
        self,
        *,
        altitude: float,
        climb_rate: float | None = None,
    ) -> NavigationResult:
        self.call_log.append(
            {
                "method": "send_takeoff_goal",
                "altitude": altitude,
                "climb_rate": climb_rate,
            }
        )
        if self._takeoff_override is not None:
            return self._takeoff_override
        return NavigationResult(
            success=True,
            final_pose={"x": 0.0, "y": 0.0, "z": altitude},
            frame="agl",
        )

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        self.call_log.append(
            {
                "method": "send_land_goal",
                "at": at,
                "precision": precision,
            }
        )
        if self._land_override is not None:
            return self._land_override
        return NavigationResult(success=True, final_pose={"x": 0.0, "y": 0.0, "z": 0.0}, frame="agl")

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        self.call_log.append(
            {
                "method": "send_return_to_home_goal",
                "speed": speed,
                "altitude": altitude,
            }
        )
        if self._rth_override is not None:
            return self._rth_override
        return NavigationResult(success=True)

    # ----- AV-profile dispatch (RFC-0020; also satisfies TrajectoryAdapter) -----

    def plan_trajectory(
        self,
        *,
        start: dict[str, float] | str | None,
        goal: dict[str, float] | str,
        along: str | None = None,
    ) -> TrajectoryPlanResult:
        self.call_log.append(
            {
                "method": "plan_trajectory",
                "start": start,
                "goal": goal,
                "along": along,
            }
        )
        # A deterministic stub trajectory: two waypoints (start -> goal).
        return TrajectoryPlanResult(
            success=True,
            payload={
                "waypoints": [start, goal],
                "duration_s": 0.0,
                "frame": "map",
            },
        )

    def follow_trajectory_goal(
        self,
        *,
        trajectory: dict[str, Any] | None,
        max_velocity_mps: float | None = None,
        max_accel_mps2: float | None = None,
        on_off_route: Literal["abort", "replan"] = "abort",
    ) -> NavigationResult:
        self.call_log.append(
            {
                "method": "follow_trajectory_goal",
                "trajectory": trajectory,
                "max_velocity_mps": max_velocity_mps,
                "max_accel_mps2": max_accel_mps2,
                "on_off_route": on_off_route,
            }
        )
        return NavigationResult(success=True)
