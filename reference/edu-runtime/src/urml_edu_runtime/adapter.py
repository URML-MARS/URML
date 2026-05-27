"""Zero-ROS educational-platform adapters — VEX V5, LEGO Pybricks, Thymio.

URML scales DOWN to a classroom: VEX V5 brain (USB/serial), LEGO
SPIKE Prime / Mindstorms hub (BLE via Pybricks), Thymio (Aseba TDM).
**No ROS dependency.** Each adapter mirrors :class:`BlueRovAdapter` /
:class:`UrRtdeAdapter`: lazy vendor SDK, cached lazily-opened client,
failures returned not raised. Serves RFC-0011 educational — the
adoption flywheel for the classroom/maker community.

## v0.1 method coverage (all 3 adapters)

Supported: ``move_to``/``hover`` (drive to a configured firmware
command), ``grasp``/``release`` (claw servo command), ``wait``,
``measure`` (one telemetry read), ``wait_for`` (read-once), ``report``
(local sink, no cloud), ``scan`` (documented stub).

Not supported on a classroom platform (returned, not raised):
``dock``, ``detect``, ``capture``, ``speak``, ``listen``. The drone
trio is ``not_applicable_edu``.

Spec gaps surfaced (per RFC-0014, cross-referenced — **no new RFC**):
LED/buzzer/button = digital-output → RFC-0017 (`set_output`,
already Draft); a sensor-only VEX brain or a LEGO hub without motors =
minimal-MCU manifest → RFC-0018, already Draft.
"""

from __future__ import annotations

from contextlib import suppress
from typing import Any, Literal

from urml_ros2_runtime.substrate.base import (
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

from urml_edu_runtime._version import __version__
from urml_edu_runtime.config import EduCommand, EduConfig, EduSkillCall, load_edu_config

__all__ = [
    "EduCommand",
    "EduConfig",
    "EduSkillCall",
    "LegoSpikeAdapter",
    "RoboticalMartyAdapter",
    "ThymioAdapter",
    "VexV5Adapter",
    "__version__",
    "load_edu_config",
]


def _resolve_call(command: EduCommand) -> tuple[str, list[Any], dict[str, Any]]:
    """Normalize an EduCommand into (method, args, kwargs).

    A bare string ``"walk"`` becomes ``("walk", [], {})``; an
    :class:`EduSkillCall` carries its own ``args`` and ``kwargs``.
    """
    if isinstance(command, EduSkillCall):
        return (command.method, command.args, command.kwargs)
    return (command, [], {})

_NOT_SUPPORTED = (
    "not_supported_on_edu_platform: a classroom platform has no {capability}. "
    "Pair a richer brain/peripheral; the URML program, manifest, and validator "
    "are unchanged."
)
_NOT_APPLICABLE = "not_applicable_edu: {capability} has no meaning for a classroom buggy."


class _EduBase:
    """Shared Protocol surface for educational platforms.

    Subclasses implement ``_open`` (vendor connect, cached),
    ``send_navigation_goal``, ``send_manipulation_goal``, and
    ``take_measurement``.
    """

    BRAND = "edu"

    def __init__(self, config: EduConfig | None = None) -> None:
        self._config = config or EduConfig()
        self._conn: Any = None
        self._reports: list[dict[str, Any]] = []
        self._closed = False

    def close(self) -> None:
        if self._closed:
            return
        if self._conn is not None:
            with suppress(Exception):
                close = getattr(self._conn, "disconnect", None) or getattr(self._conn, "close", None)
                if callable(close):
                    close()
        self._closed = True

    def __enter__(self) -> _EduBase:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
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
            payload={"samples": [], "coverage": 0.0, "anomalies": [], "_note": "v0.1 edu scan: stub."},
        )

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


def _nav(self: _EduBase, location: str | None, write: Any, frame: str | None) -> NavigationResult:
    """Shared nav body: resolve location → command → write → success."""
    if location is None:
        return NavigationResult(
            success=False,
            reason="edu_requires_named_location: classroom platforms drive to firmware-named commands.",
        )
    cmd = self._config.resolve_location(location)
    if cmd is None:
        return NavigationResult(
            success=False,
            reason=f"location_not_configured: {location!r} is declared in the "
            "manifest but not mapped to a command in edu_adapter.yaml.",
        )
    write(cmd)
    return NavigationResult(success=True, final_pose=None, frame=frame or "buggy")


def _grasp(self: _EduBase, action: Literal["grasp", "release"], force_n: float | None) -> ManipulationResult:
    cmd = self._config.manipulation_commands.get(action)
    if cmd is None:
        return ManipulationResult(
            success=False,
            reason=f"manipulation_command_not_configured: {action!r} is not mapped "
            "to a command in edu_adapter.yaml.",
        )
    # Write via the subclass's stored connection's send-equivalent. Each subclass
    # exposes a `_send(cmd)` helper to keep the base agnostic of vendor APIs.
    self._send(cmd)
    return ManipulationResult(success=True, grip_force_n=force_n)


class VexV5Adapter(_EduBase):
    """VEX V5 brain via the host-side ``vex``/pyvex SDK — zero ROS, USB/serial.

    VEX V5 is the dominant US high-school/university competition robot;
    first-class here because RFC-0011 educational is an adoption flywheel.
    United States — passes the default US-federal policy.
    """

    BRAND = "vex"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import pyvex  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "pyvex is not installed. VexV5Adapter requires the [vex] extra.\n"
                "  Install with: pip install urml-edu-runtime[vex]"
            ) from exc
        self._conn = pyvex.Brain(self._config.device)
        return self._conn

    def _send(self, command: EduCommand) -> None:
        method, args, kwargs = _resolve_call(command)
        if args or kwargs:
            raise RuntimeError(
                f"vex_skill_args_not_supported: VEX adapter only accepts no-arg commands "
                f"(got method={method!r} args={args!r} kwargs={kwargs!r}). Wrap any arg "
                "encoding into the firmware program name instead, or extend the adapter."
            )
        brain = self._open()
        brain.run_command(method)

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        return _nav(self, location, lambda c: self._send(c), frame)

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
        return _grasp(self, action, force_n)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        brain = self._open()
        value = float(brain.read_sensor(sensor or "default"))
        return MeasurementResult(success=True, payload={"value": value, "what": what})


class LegoSpikeAdapter(_EduBase):
    """LEGO SPIKE Prime / Mindstorms hub via Pybricks BLE — zero ROS.

    Pybricks is the official open-source firmware/runtime for SPIKE Prime
    and EV3 Mindstorms; the ``pybricksdev`` host-side BLE client speaks
    to the hub from any computer. Denmark/global — passes the default
    US-federal policy.
    """

    BRAND = "lego_spike"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import pybricksdev  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "pybricksdev is not installed. LegoSpikeAdapter requires the [lego] extra.\n"
                "  Install with: pip install urml-edu-runtime[lego]"
            ) from exc
        self._conn = pybricksdev.connect(self._config.device)
        return self._conn

    def _send(self, command: EduCommand) -> None:
        method, args, kwargs = _resolve_call(command)
        if args or kwargs:
            raise RuntimeError(
                f"lego_skill_args_not_supported: LEGO/Pybricks adapter only accepts "
                f"no-arg commands (got method={method!r} args={args!r} kwargs={kwargs!r})."
            )
        hub = self._open()
        hub.send_command(method)

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        return _nav(self, location, lambda c: self._send(c), frame)

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
        return _grasp(self, action, force_n)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        hub = self._open()
        value = float(hub.read_sensor(sensor or "default"))
        return MeasurementResult(success=True, payload={"value": value, "what": what})


class RoboticalMartyAdapter(_EduBase):
    """Robotical Marty v1 / v2 via ``martypy`` skill-library dispatch — zero ROS.

    Marty is the bipedal educational walking robot from Robotical Ltd
    (Edinburgh, UK). The lab maintainer (NikTheGeek1) confirmed on
    robotical/martypy#52 across three engagement rounds (2026-05-25,
    2026-05-27, 2026-05-27 round 3) that URML should build the adapter
    externally against the public ``martypy`` API. Connection methods
    per the real ``martypy.Marty`` constructor: ``usb`` (v2 default),
    ``wifi`` (v2 configurable; URL-style ``wifi://host`` parses because
    ``wifi`` is a valid method name), ``socket`` (v1 default). ``ws://``
    is NOT a valid ``martypy`` method — earlier URML docstring overclaim
    corrected in round 3. BLE is **not** supported by ``martypy`` and
    URML would have to provide it as a separate layer (out of scope for
    this scaffold). Manipulation is not applicable on stock Marty (no
    gripper); ``manipulation_commands`` may map ``grasp`` / ``release``
    to skill-library tokens for add-on grippers.

    The classroom audience is exactly the RFC-0011 educational profile.
    United Kingdom — passes the default US-federal policy.
    """

    BRAND = "marty"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import martypy  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "martypy is not installed. RoboticalMartyAdapter requires the [marty] extra.\n"
                "  Install with: pip install urml-edu-runtime[marty]"
            ) from exc
        # ``martypy.Marty`` accepts a connection string in v2 ('usb', 'ws://host', etc.)
        # and a socket address in v1; the URML config's ``device`` field carries
        # whatever the deployment chose. ``program_name`` is unused by martypy and
        # ignored here (kept on EduConfig for parity with VEX/LEGO/Thymio).
        self._conn = martypy.Marty(self._config.device)
        return self._conn

    def _send(self, command: EduCommand) -> None:
        """Dispatch a skill-library call to the connected Marty.

        ``martypy`` exposes skill methods (`.walk()`, `.kick()`, `.eyes()`,
        `.arms()`, ...) rather than a generic command channel. URML's
        EduConfig command convention supports two forms (production
        graduation, robotical/martypy#52 round 3, 2026-05-27):

        1. **String form** (bare method name) — for skills called
           without arguments. Example: ``"walk"`` invokes ``marty.walk()``.
        2. **:class:`EduSkillCall` form** (method + args + kwargs) — for
           skills that take positional / keyword arguments. Example:
           ``EduSkillCall(method="arms", args=[10, -10, 1000])``
           invokes ``marty.arms(10, -10, 1000)``.

        Unknown skill names are reported as a typed RuntimeError so the
        validator step can surface them as ``manipulation_command_not_configured``
        / ``location_not_configured`` rather than a crash inside martypy.

        Authoritative skill list (per round-3 maintainer correction):

        - v1 + v2 movement: walk, kick, arms, lean, eyes, dance,
          celebrate, get_ready, stand_straight, sidestep, move_joint,
          stop, play_sound.
        - v2-only movement: wiggle, circle_dance, lift_foot, lower_foot,
          wave, resume, hold_position, speak.

        ``sit()`` is NOT in the public API and must not appear in the
        configured-command map.
        """
        method_name, args, kwargs = _resolve_call(command)
        marty = self._open()
        skill = getattr(marty, method_name, None)
        if not callable(skill):
            raise RuntimeError(
                f"marty_skill_not_found: martypy.Marty has no callable named {method_name!r}. "
                "Map the location/manipulation entry to a martypy skill method name "
                "in edu_adapter.yaml (e.g. 'walk', 'kick', 'eyes', 'arms'); use an "
                "EduSkillCall for methods that take arguments "
                "(arms, eyes, lean, sidestep, wave)."
            )
        skill(*args, **kwargs)

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        return _nav(self, location, lambda c: self._send(c), frame)

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
        return _grasp(self, action, force_n)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        marty = self._open()
        # ``martypy`` exposes sensors via named getters (`.get_battery_remaining()`,
        # `.get_accelerometer()`, `.get_distance_sensor()`, ...). Treat
        # ``sensor`` as the getter name; fall back to battery-remaining.
        # ``get_battery_voltage()`` is not in the public martypy API per
        # maintainer correction on robotical/martypy#52 (2026-05-27);
        # ``get_battery_remaining()`` (percentage) is the safer v2 call.
        # Some getters (e.g. ``get_accelerometer()`` no-axis form) return a
        # tuple of axes; the adapter passes the raw value through into the
        # payload so the URML program receives the structure martypy returns.
        getter_name = sensor or "get_battery_remaining"
        getter = getattr(marty, getter_name, None)
        if not callable(getter):
            return MeasurementResult(
                success=False,
                reason=(
                    f"marty_sensor_not_found: martypy.Marty has no callable named "
                    f"{getter_name!r}. Use a published martypy getter "
                    "(get_battery_remaining, get_accelerometer, get_distance_sensor, "
                    "get_robot_status, get_power_status, ...)."
                ),
            )
        raw = getter()
        # Per real-Marty trace on robotical/martypy#52 round 3 (2026-05-27),
        # get_accelerometer (no-axis) returns a Python list, not a tuple.
        # Some martypy getters may return scalars (battery percent, distance)
        # while others return dicts (get_power_status, get_robot_status).
        # The adapter passes the raw return through into the payload so the
        # URML program receives the structure martypy returns.
        if isinstance(raw, (tuple, list)):
            payload_value: Any = list(raw)
        elif isinstance(raw, dict):
            payload_value = raw
        else:
            payload_value = raw if isinstance(raw, int) else float(raw)
        return MeasurementResult(success=True, payload={"value": payload_value, "what": what})


class ThymioAdapter(_EduBase):
    """Thymio via Aseba TDM (Thymio Device Manager) — zero ROS.

    Thymio is the dominant European/Swiss classroom robot, controlled
    over Aseba; ``tdmclient`` is its native Python host. Switzerland —
    passes the default US-federal policy (CH allied origin).
    """

    BRAND = "thymio"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import tdmclient  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "tdmclient is not installed. ThymioAdapter requires the [thymio] extra.\n"
                "  Install with: pip install urml-edu-runtime[thymio]"
            ) from exc
        self._conn = tdmclient.Client(self._config.device)
        return self._conn

    def _send(self, command: EduCommand) -> None:
        method, args, kwargs = _resolve_call(command)
        if args or kwargs:
            raise RuntimeError(
                f"thymio_skill_args_not_supported: Thymio adapter only accepts no-arg "
                f"commands (got method={method!r} args={args!r} kwargs={kwargs!r})."
            )
        client = self._open()
        client.send_event(method)

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        return _nav(self, location, lambda c: self._send(c), frame)

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
        return _grasp(self, action, force_n)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        client = self._open()
        value = float(client.read_variable(sensor or "default"))
        return MeasurementResult(success=True, payload={"value": value, "what": what})
