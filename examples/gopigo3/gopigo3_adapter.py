#!/usr/bin/env python3
"""A native (non-ROS) GoPiGo3 URML adapter, for Discussion #523.

@slowrunner asked for an example runtime that drives a basic GoPiGo3 from a
validated URML program, on the Raspberry Pi, without ROS. This is that headstart.

The adapter implements the URML substrate surface a frameless educational buggy
needs: the RFC-0630 relative-motion methods ``drive_by`` / ``turn_by`` (so the
runtime's ``drive`` / ``turn`` primitives dispatch here), plus ``emit_speech``
for "announce" and ``emit_report``. It drives the wheels through Dexter
Industries' ``easygopigo3`` library (``EasyGoPiGo3.drive_cm`` /
``turn_degrees`` / ``orbit``), lazily imported so this file is importable on any
machine; the real library is only needed when you actually move a robot.

Everything else on the substrate surface (grasp, dock, detect, capture, listen,
the drone verbs) is returned as not-supported, not raised, exactly as the other
zero-ROS educational adapters do: a basic GoPiGo3 has no arm, no camera pipeline,
no speaker beyond espeak. Add them by extending this class.

Run it with ``run_gopigo3.py``, which binds to the real ``easygopigo3`` when the
GoPiGo3 software is installed and falls back to a fake otherwise (no edits either
way). Installing the GoPiGo3 software is the platform's job, per Dexter
Industries' Installation FAQ:
https://github.com/DexterInd/GoPiGo3/blob/main/Installation_FAQ.md
"""

from __future__ import annotations

import math
import shutil
import subprocess
import sys
from typing import Any, Callable, Literal

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

_NOT_SUPPORTED = (
    "not_supported_on_basic_gopigo3: a basic GoPiGo3 has no {capability}. "
    "Add a servo/sensor and extend the adapter; the URML program, manifest, and "
    "validator are unchanged."
)
_NOT_APPLICABLE = "not_applicable_ground: {capability} has no meaning for a ground buggy."


def _espeak(utterance: str) -> None:
    """Default speech backend: espeak-ng (or espeak) on the Pi.

    Speaks the utterance through whichever of ``espeak-ng`` / ``espeak`` is on the
    system, and says so out loud (on stderr) when it cannot, so a silent robot is
    explained rather than mysterious. If your robot has its own speech path (for
    example a ROS say node), pass your own callable as ``GoPiGo3Adapter(speak=...)``
    instead of relying on espeak.

    The utterance is passed as a list argument, never interpolated into a shell
    string, so quotes or shell metacharacters in the text are literal and there is
    no injection path. That is why there is no ``shell=True`` here.
    """
    binary = "espeak-ng" if shutil.which("espeak-ng") else "espeak"
    try:
        result = subprocess.run([binary, utterance], check=False)
    except FileNotFoundError:
        print(
            f"[gopigo3 speak] neither espeak-ng nor espeak is installed, so "
            f"{utterance!r} was not spoken. Install one, or pass a speak= backend "
            "to GoPiGo3Adapter.",
            file=sys.stderr,
        )
        return
    if result.returncode != 0:
        print(
            f"[gopigo3 speak] {binary} exited {result.returncode}; {utterance!r} may "
            "not have been audible (check the Pi's audio output device).",
            file=sys.stderr,
        )


# The manifest's `speak.language.tts_engine_class` is a closed Layer-1 vocabulary
# (openvoice | piper | mozilla_tts | espeak | custom). It is an advisory
# declaration, not a Python identifier: the adapter maps a declared class to a
# backend here. A hyphenated real binary (piper-tts) lives in the backend's
# subprocess args or as a dict key, never as a function name (Discussion #589).
# To add piper: write a `_piper(utterance)` that shells out to it (piper is
# GPL-3.0, so cross a subprocess boundary rather than importing it) and add it
# under the "piper" key.
_TTS_ENGINES: dict[str, Callable[[str], None]] = {
    "espeak": _espeak,
}


class GoPiGo3Adapter:
    """Drives a basic GoPiGo3 from URML intent over ``easygopigo3`` (no ROS).

    Implements ``drive_by`` / ``turn_by`` (RFC-0630 RelativeMotionAdapter), so a
    ``URMLRuntime`` dispatches ``drive`` / ``turn`` here, plus ``emit_speech`` and
    ``emit_report``.

    Speech backend selection (Discussion #589). ``speak`` is injectable: pass a
    callable to capture speech (a dry run records ``spoken.append``) or to route it
    to your own path. If ``speak`` is omitted, the backend is chosen by
    ``tts_engine_class`` from the manifest's closed vocabulary (``espeak`` by
    default, mapped through ``_TTS_ENGINES``). An explicit ``speak`` always wins,
    which is how the runner keeps a dry run silent while ``--execute`` speaks for
    real.
    """

    BRAND = "gopigo3"

    def __init__(
        self,
        *,
        speak: Callable[[str], None] | None = None,
        tts_engine_class: str = "espeak",
    ) -> None:
        # An explicit `speak` overrides the declared class; otherwise the manifest's
        # tts_engine_class selects the backend, defaulting to espeak.
        self._speak = speak if speak is not None else _TTS_ENGINES.get(tts_engine_class, _espeak)
        self._gpg: Any = None
        self._reports: list[dict[str, Any]] = []
        self.call_log: list[dict[str, Any]] = []
        self._closed = False

    # ------------------------------------------------------------------
    # easygopigo3 connection (lazy, so this file imports without hardware)
    # ------------------------------------------------------------------

    def _robot(self) -> Any:
        if self._gpg is not None:
            return self._gpg
        try:
            from easygopigo3 import EasyGoPiGo3  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "easygopigo3 is not available. Installing the GoPiGo3 software is "
                "the platform's responsibility, not URML's; follow Dexter "
                "Industries' Installation FAQ:\n"
                "  https://github.com/DexterInd/GoPiGo3/blob/main/Installation_FAQ.md\n"
                "The run_gopigo3.py example falls back to a fake when the library "
                "is absent, so it runs anywhere without edits."
            ) from exc
        self._gpg = EasyGoPiGo3()
        return self._gpg

    def close(self) -> None:
        if self._closed:
            return
        if self._gpg is not None:
            stop = getattr(self._gpg, "stop", None)
            if callable(stop):
                stop()
        self._closed = True

    def __enter__(self) -> GoPiGo3Adapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # RFC-0630 relative motion: the methods that make this a buggy runtime
    # ------------------------------------------------------------------

    def drive_by(
        self,
        *,
        distance: float,
        arc: float | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        """Drive a signed distance (m). With `arc` (signed degrees) follow a curve."""
        gpg = self._robot()
        cm = distance * 100.0
        if arc is None or arc == 0:
            gpg.drive_cm(cm)
            hw = f"drive_cm({cm:.1f})"
        else:
            # RFC-0630: `distance` is the path length swept over `arc` degrees, so
            # the arc radius is distance / arc-in-radians. easygopigo3.orbit takes
            # (degrees, radius_cm), a radius, not a path length.
            radius_cm = abs(cm) / abs(math.radians(arc))
            # URML FLU (+CCW) -> GoPiGo3 RFD (+CW): negate at the hardware
            # boundary only, so call_log stays in the URML frame (#591, #598).
            gpg.orbit(-arc, radius_cm)
            hw = f"orbit({-arc:.1f}, {radius_cm:.1f})"
        self.call_log.append({"method": "drive_by", "distance": distance, "arc": arc, "hw": hw})
        return NavigationResult(success=True, final_pose=None, frame="gopigo3")

    def turn_by(self, *, angle: float) -> NavigationResult:
        """Rotate in place by a signed angle (degrees, + counterclockwise)."""
        gpg = self._robot()
        # URML FLU (+CCW) -> GoPiGo3 RFD (+CW): negate at the hardware
        # boundary only, so call_log stays in the URML frame (#591, #598).
        gpg.turn_degrees(-angle)
        self.call_log.append({"method": "turn_by", "angle": angle, "hw": f"turn_degrees({-angle:.1f})"})
        return NavigationResult(success=True, final_pose=None, frame="gopigo3")

    # ------------------------------------------------------------------
    # Speech ("announce"), report, waits, and one telemetry read
    # ------------------------------------------------------------------

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        self._speak(utterance)
        self.call_log.append({"method": "emit_speech", "utterance": utterance})
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
        self._reports.append({"to": to, "status": status, "facts": facts})
        self.call_log.append({"method": "emit_report", "to": to, "status": status})
        return SubstrateResult(success=True)

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        self.call_log.append({"method": "wait_passively", "duration_seconds": duration_seconds})
        return SubstrateResult(success=True)

    def wait_for_condition(
        self,
        *,
        kind: Literal["event", "signal", "input", "sensor_threshold"],
        name: str | None,
        input_mode: str | None,
        threshold: dict[str, Any] | None,
        timeout_seconds: float | None,
    ) -> WaitResult:
        # A bare buggy has no external event bus; a threshold read could be added
        # via the distance sensor. v0.1: read-once success.
        self.call_log.append({"method": "wait_for_condition", "kind": kind})
        return WaitResult(success=True, timed_out=False, payload=None)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        """Read the GoPiGo3 distance sensor (cm -> m)."""
        gpg = self._robot()
        init = getattr(gpg, "init_distance_sensor", None)
        if not callable(init):
            return MeasurementResult(success=False, reason=_NOT_SUPPORTED.format(capability="distance sensor"))
        ds = init()
        metres = float(ds.read_mm()) / 1000.0
        self.call_log.append({"method": "take_measurement", "what": what, "value_m": metres})
        return MeasurementResult(success=True, payload={"value": metres, "what": what})

    # ------------------------------------------------------------------
    # Not supported on a basic GoPiGo3 (returned, not raised)
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
        # A frameless buggy has no fixed map to navigate a named location against;
        # use `drive` / `turn` (relative motion) instead of `move_to`.
        return NavigationResult(
            success=False,
            reason="not_supported_on_basic_gopigo3: a frameless buggy drives by amount "
            "(`drive` / `turn`), not to a named location. See RFC-0630.",
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
        arm: str | None = None,
    ) -> ManipulationResult:
        return ManipulationResult(success=False, reason=_NOT_SUPPORTED.format(capability="gripper"))

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
        return ScanResult(success=False, reason=_NOT_SUPPORTED.format(capability="survey controller"))

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
        return DetectionResult(success=False, reason=_NOT_SUPPORTED.format(capability="onboard detection"))

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return CaptureResult(success=False, reason=_NOT_SUPPORTED.format(capability="recordable camera"))

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
        self, *, at: str | None = None, precision: Literal["standard", "precise"] = "standard"
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_APPLICABLE.format(capability="land"))

    def send_return_to_home_goal(
        self, *, speed: float | None = None, altitude: float | None = None
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_APPLICABLE.format(capability="return_to_home"))

    def call_named_program(self, *, name: str, args: dict[str, Any] | None = None) -> ProgramCallResult:
        return unsupported_program_call("gopigo3")
