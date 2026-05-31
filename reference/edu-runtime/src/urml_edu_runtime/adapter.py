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

from urml_edu_runtime._version import __version__
from urml_edu_runtime.config import EduCommand, EduConfig, EduSkillCall, load_edu_config

__all__ = [
    "CircuitPythonAdapter",
    "EduCommand",
    "EduConfig",
    "EduSkillCall",
    "LegoSpikeAdapter",
    "PetoiAdapter",
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

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('edu')


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

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('edu')


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

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('edu')


class PetoiAdapter(_EduBase):
    """Petoi Bittle X / Bittle / Nybble Q via the OpenCat skill library — zero ROS.

    Petoi is the open-hardware bipedal-quadruped vendor from Shenzhen, CN
    (founder Dr. Rongzhong Li, since 2016). Bittle X ($299, BiBoard ESP32)
    is the canonical hero target; Bittle (original, ATmega NyBoard) and
    Nybble Q (cat-form quadruped) share the OpenCat firmware command
    surface. The maintainer (borntoleave / Dr. Rongzhong Li) confirmed on
    PetoiCamp/OpenCat-Quadruped-Robot#113 (2026-05-28) that:

    - The ESP32 line is now canonical
      ([PetoiCamp/OpenCatEsp32-Quadruped-Robot](
      https://github.com/PetoiCamp/OpenCatEsp32-Quadruped-Robot)).
    - The skill table lives at ``src/InstinctBittleESP.h`` in that repo.
    - Commands are parametric and use OpenCat's single-letter tokens:
      ``kwkF 5`` (walk forward, 5 cycles), ``ktrF 2000`` (trot forward,
      2000 ms), ``kcrL 30`` (crawl left, 30 degrees), plus posture tokens
      (``ksit``, ``krest``, ``kstr``, ``klap``) and the gait family
      (``kwk`` walk, ``ktr`` trot, ``kbd`` bound, ``kbk`` backward) with
      direction suffix ``F`` / ``B`` / ``L`` / ``R``.
    - Commands can be sent via serial, Bluetooth, or WebSocket.
    - One parametric ``petoi`` manifest works for all models (Bittle X /
      Bittle / Nybble Q) with a one-line macro modification on the
      firmware side.
    - Add-ons (gripper, claw, sensors) can be deferred.
    - URML-side conformance lane on OpenCat README is open once URML
      ships a working demo link.

    Connection: lazy ``import petoi_mindpluslib`` (placeholder — the
    actual canonical Python wrapper name is a round-2 ask of the
    maintainer; ``PetoiCamp/Petoi_MindPlusLib`` is Mind+ block-coding
    integration, not necessarily a general Python SDK). The adapter only
    requires *some* Python object that either exposes named skill
    methods (``walk``, ``trot``, ...) OR a generic
    ``send_command(token, *args)`` channel; URML's
    :class:`EduSkillCall` dispatch supports both. For raw OpenCat tokens
    configure ``EduSkillCall(method='send_command', args=['kwkF', 5])``;
    for named methods configure
    ``EduSkillCall(method='walk', args=['forward', 5])``.

    Manipulation is not applicable on stock Bittle / Nybble (no
    gripper); ``manipulation_commands`` may map ``grasp`` / ``release``
    to OpenCat tokens for after-market gripper add-ons (deferred per
    round-1 maintainer guidance 2026-05-28).

    United States operator using a Petoi: provenance ``origin: CN`` in
    the manifest; the operator's policy file
    ([RFC-0004](../../../docs/rfcs/0004-compliance-policy.md)) decides
    whether the manifest is acceptable in a given deployment context.
    """

    BRAND = "petoi"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import petoi_mindpluslib  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "petoi_mindpluslib is not installed. PetoiAdapter requires the [petoi] extra.\n"
                "  Install with: pip install urml-edu-runtime[petoi]\n"
                "  (Canonical Python-wrapper package name is a round-2 ask of "
                "the PetoiCamp maintainer on OpenCat-Quadruped-Robot#113; the "
                "adapter only requires *some* Python object that exposes the "
                "OpenCat skill-library command surface.)"
            ) from exc
        self._conn = petoi_mindpluslib.Petoi(self._config.device)
        return self._conn

    def _send(self, command: EduCommand) -> None:
        """Dispatch an OpenCat skill-library call to the connected Petoi board.

        Two configured-command shapes are supported (same as Marty per
        the production-graduation contract on robotical/martypy#52):

        1. **String form** (bare method name) — for skills called
           without arguments. Example: ``"ksit"`` invokes
           ``petoi.ksit()`` (or whatever named no-arg method the
           wrapper exposes for that posture token).

        2. **:class:`EduSkillCall` form** (method + args + kwargs) —
           required for OpenCat's parametric commands:

           - ``EduSkillCall(method='send_command', args=['kwkF', 5])``
             sends the raw OpenCat token ``kwkF 5`` (walk forward, 5
             cycles).
           - ``EduSkillCall(method='walk', args=['forward', 5])`` calls
             ``petoi.walk('forward', 5)`` if the wrapper exposes a
             named ``walk`` method.

        Unknown skill names are reported as a typed RuntimeError so the
        validator step can surface them as
        ``manipulation_command_not_configured`` /
        ``location_not_configured`` rather than a crash inside the
        wrapper.

        OpenCat command vocabulary per round-1 maintainer engagement
        (PetoiCamp/OpenCat-Quadruped-Robot#113, 2026-05-28):

        - Gait tokens: ``kwk`` (walk), ``ktr`` (trot), ``kbd`` (bound),
          ``kbk`` (backward), ``kcr`` (crawl), with direction suffix
          ``F`` (forward), ``B`` (backward), ``L`` (left), ``R``
          (right). Example: ``kwkF 5`` walks forward 5 cycles;
          ``kcrL 30`` crawls left 30 degrees.
        - Posture tokens: ``ksit``, ``krest``, ``kstr`` (stretch),
          ``klap`` (lap-sit), no arguments.
        - Authoritative skill table: ``src/InstinctBittleESP.h`` in
          PetoiCamp/OpenCatEsp32-Quadruped-Robot (maintainer pointer).
        """
        method_name, args, kwargs = _resolve_call(command)
        petoi = self._open()
        skill = getattr(petoi, method_name, None)
        if not callable(skill):
            raise RuntimeError(
                f"petoi_skill_not_found: connected Petoi wrapper has no callable "
                f"named {method_name!r}. Map the location/manipulation entry to an "
                "OpenCat token (e.g. EduSkillCall(method='send_command', "
                "args=['kwkF', 5])) or a wrapper-exposed named method "
                "(e.g. EduSkillCall(method='walk', args=['forward', 5])); see "
                "src/InstinctBittleESP.h in PetoiCamp/OpenCatEsp32-Quadruped-Robot "
                "for the authoritative skill table."
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
        petoi = self._open()
        # OpenCat sensor surface: IMU (gyro + accel), battery, optional
        # ultrasonic. The exact Python-wrapper getter names are a
        # round-2 ask of the PetoiCamp maintainer; the adapter uses
        # whatever getter name the manifest declares (default
        # 'read_imu' as a placeholder). Pass the raw return through
        # into the payload so the URML program receives the structure
        # the wrapper returns (list / dict / scalar all supported per
        # the Marty round-3 trace handling precedent).
        getter_name = sensor or "read_imu"
        getter = getattr(petoi, getter_name, None)
        if not callable(getter):
            return MeasurementResult(
                success=False,
                reason=(
                    f"petoi_sensor_not_found: connected Petoi wrapper has no "
                    f"callable named {getter_name!r}. Use a wrapper-exposed "
                    "getter; the authoritative sensor getter list is a "
                    "round-2 ask of the PetoiCamp maintainer on "
                    "PetoiCamp/OpenCat-Quadruped-Robot#113."
                ),
            )
        raw = getter()
        if isinstance(raw, (tuple, list)):
            payload_value: Any = list(raw)
        elif isinstance(raw, dict):
            payload_value = raw
        else:
            payload_value = raw if isinstance(raw, int) else float(raw)
        return MeasurementResult(success=True, payload={"value": payload_value, "what": what})

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('edu')


class CircuitPythonAdapter(_EduBase):
    """Adafruit CircuitPython (Python on MCU) via a host-side comms bridge — zero ROS.

    Adafruit Industries (US, New York) ships CircuitPython across 400+
    board variants (Feather / Trinket / QT Py plus third-party boards on
    RP2040 / SAMD21/51 / nRF52 / STM32 / ESP32). Adafruit's @dhalbert
    (COLLABORATOR) engaged on adafruit/circuitpython#11035 (2026-05-28)
    and gave five points that shape this adapter:

    - **Drag-drop ``code.py`` deploy (USB mass storage) is not universal**
      — some boards lack an MSC drive. URML does not assume it. The
      integration is a **host-side comms program** talking to the board
      over a serial / REPL channel, which is exactly the direction
      @dhalbert said CircuitPython/MicroPython favour over MSC.
    - **Adafruit will not maintain the adapter**; the device-side helper
      library's home is the [Adafruit CircuitPython Community Bundle](
      https://github.com/adafruit/CircuitPython_Community_Bundle), not
      core. This host-side adapter pairs with that (future, hardware-
      validated) device-side receiver.
    - CircuitPython is a **friendly fork of MicroPython** sharing the base
      language but with different hardware modules — the two are distinct
      mappings (URML's substrate landing is RFC-0270, which gives
      ``circuitpython`` and ``micropython`` separate ``substrate.class``
      enum values).
    - A pointer to URML can be added to
      [awesome-circuitpython](https://github.com/adafruit/awesome-circuitpython)
      once the adapter is hardware-validated (founder action).

    Connection: lazy ``import circuitpython_host`` (placeholder — the
    host-side wrapper package is pending hardware validation and pairs
    with the Community-Bundle device-side receiver; the canonical name is
    a follow-up with the Adafruit maintainers). Like the Petoi adapter,
    the adapter only requires *some* Python object that either exposes
    named skill methods (``blink``, ``move``, ``set_neopixel``, ...) OR a
    generic ``send_command(token, *args)`` channel; URML's
    :class:`EduSkillCall` dispatch supports both shapes.

    United States operator using an Adafruit board: provenance
    ``origin: US`` in the manifest; the default US-federal policy accepts
    it (US origin, no covered-list vendor).
    """

    BRAND = "circuitpython"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import circuitpython_host  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "circuitpython_host is not installed. CircuitPythonAdapter requires "
                "the [circuitpython] extra.\n"
                "  Install with: pip install urml-edu-runtime[circuitpython]\n"
                "  (The host-side wrapper pairs with a device-side receiver whose home "
                "is the Adafruit CircuitPython Community Bundle per @dhalbert on "
                "adafruit/circuitpython#11035; pending hardware validation. The adapter "
                "only requires *some* Python object exposing CircuitPython skill methods "
                "or a generic send_command(token, *args) channel.)"
            ) from exc
        # ``self._config.device`` carries the board identifier or serial
        # connection string (e.g. 'adafruit_feather_rp2040',
        # 'serial:///dev/ttyACM0', 'COM3').
        self._conn = circuitpython_host.Board(self._config.device)
        return self._conn

    def _send(self, command: EduCommand) -> None:
        """Dispatch a CircuitPython skill call to the connected board.

        Two configured-command shapes are supported (same as Marty / Petoi):

        1. **String form** (bare method name) — for skills called without
           arguments. Example: ``"blink"`` invokes ``board.blink()``.
        2. **:class:`EduSkillCall` form** (method + args + kwargs) — for
           skills that take arguments, e.g.
           ``EduSkillCall(method='set_neopixel', args=[255, 0, 0])`` or a
           raw host-bridge token via
           ``EduSkillCall(method='send_command', args=['move', 10])``.

        Unknown skill names are reported as a typed RuntimeError so the
        validator step surfaces them cleanly rather than crashing inside
        the wrapper.
        """
        method_name, args, kwargs = _resolve_call(command)
        board = self._open()
        skill = getattr(board, method_name, None)
        if not callable(skill):
            raise RuntimeError(
                f"circuitpython_skill_not_found: connected CircuitPython host bridge has "
                f"no callable named {method_name!r}. Map the location/manipulation entry "
                "to a CircuitPython skill method (e.g. 'blink', 'move', 'set_neopixel') or "
                "a generic EduSkillCall(method='send_command', args=[...]); use an "
                "EduSkillCall for methods that take arguments."
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
        board = self._open()
        # CircuitPython sensor surface depends on the loaded
        # Adafruit_CircuitPython_* libraries (analog in, distance, temp,
        # IMU, ...). Treat ``sensor`` as the host-bridge getter name with
        # an analog-read default; pass the raw return through so the URML
        # program receives whatever structure the wrapper returns (list /
        # dict / scalar all supported per the Marty / Petoi precedent).
        getter_name = sensor or "read_analog"
        getter = getattr(board, getter_name, None)
        if not callable(getter):
            return MeasurementResult(
                success=False,
                reason=(
                    f"circuitpython_sensor_not_found: connected CircuitPython host bridge "
                    f"has no callable named {getter_name!r}. Use a getter exposed by a "
                    "loaded Adafruit_CircuitPython_* library."
                ),
            )
        raw = getter()
        if isinstance(raw, (tuple, list)):
            payload_value: Any = list(raw)
        elif isinstance(raw, dict):
            payload_value = raw
        else:
            payload_value = raw if isinstance(raw, int) else float(raw)
        return MeasurementResult(success=True, payload={"value": payload_value, "what": what})

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('edu')


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

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('edu')
