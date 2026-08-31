"""MicroduckAdapter — Pollen Robotics / Hugging Face Microduck via JSON-RPC — zero ROS.

Microduck is the 25 cm open-source biped duck from Pollen Robotics
(Bordeaux, FR; Hugging Face since 2025), announced 2026-08-27 at $399.
The whole robot stack (`pollen-robotics/microduck`, Apache-2.0) is a Rust
daemon workspace with one typed client contract: **JSON-RPC 2.0, one
object per line (NDJSON)**, spoken identically by the app, the gamepad
daemon, `robotctl`, and `duckctl`. `duck-ipc-proto` is the source of
truth; clients send *intents*, never joint commands — `robotd` stays
authoritative on what is executable. That split is exactly URML's
validate-before-actuate posture, so the adapter is thin on purpose.

Wire surface the adapter uses (`duck-ipc-proto` method constants):

- ``robot.init`` / ``robot.enable`` / ``robot.stop`` / ``robot.relax`` —
  power, policy on/off, zero velocity.
- ``robot.do`` ``{"skill": ...}`` — one-shot skills (``sit_toggle``,
  ``kick_left``, ``kick_right``, ``ground_pick``, ``roulade``).
- ``robot.move`` ``{"vx","vy","vyaw"}`` — the continuous velocity intent.
  Continuous intents are *notifications* (no ``id``), last-writer-wins.
- ``robot.sound`` / ``robot.mouth`` / ``robot.pose`` — expression.
- ``robot.health`` / ``robot.mode`` — read-back requests.

Locomotion is an ONNX policy at 50 Hz trained in ``microduck_rl``
(MuJoCo + PPO), which is why the example manifest declares an RFC-0383
``learned_policy`` block: the validator refuses a deployment whose
admissible intent exceeds the training envelope.

Transport: the daemon sockets are Unix sockets on the robot
(``/run/robotd.sock``). Off-robot clients reach them over an SSH-forwarded
stream or a TCP forward; ``duckctl`` speaks the same contract over
Bluetooth. The adapter dials ``unix://`` and ``tcp://`` itself and keeps
the framing (NDJSON) identical, per the contract's own documentation.

No vendor SDK exists yet (the stack is Rust); this adapter is pure
stdlib — no extra to install.

France — passes the default US-federal policy the way Marty (UK) does;
provenance lives in the deployment manifest as always.
"""

from __future__ import annotations

import itertools
import json
import socket
from typing import Any, Literal

from urml_ros2_runtime.substrate.base import (
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ProgramCallResult,
    unsupported_program_call,
)

from urml_edu_runtime.adapter import _EduBase, _grasp, _nav, _resolve_call
from urml_edu_runtime.config import EduCommand, EduConfig

__all__ = ["MicroduckAdapter"]

#: duck-ipc-proto: JSON-RPC version and the API handshake this adapter targets.
JSONRPC_VERSION = "2.0"
API_VERSION = 16

#: Continuous intents ride as notifications (no ``id``, no reply) per the
#: contract: robot.move / robot.head / robot.pose / robot.mouth. Everything
#: else is a request and is answered.
NOTIFICATION_METHODS = frozenset({"robot.move", "robot.head", "robot.pose", "robot.mouth"})

_DEFAULT_TIMEOUT = 10.0


class _NdjsonTransport:
    """One NDJSON line out, one line back, over a stream socket."""

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock
        self._reader = sock.makefile("r", encoding="utf-8", newline="\n")

    def write_line(self, line: str) -> None:
        self._sock.sendall((line + "\n").encode("utf-8"))

    def read_line(self) -> str:
        line = self._reader.readline()
        if not line:
            raise RuntimeError("microduck_connection_closed: the daemon closed the socket.")
        return line

    def close(self) -> None:
        try:
            self._reader.close()
        finally:
            self._sock.close()


class MicroduckAdapter(_EduBase):
    """Microduck over its JSON-RPC NDJSON contract (`duck-ipc-proto`)."""

    BRAND = "microduck"

    def __init__(self, config: EduConfig | None = None) -> None:
        super().__init__(config)
        self._ids = itertools.count(1)

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def _dial(self) -> _NdjsonTransport:
        """Open the stream the deployment's ``device`` names.

        ``unix:///run/robotd.sock`` on the robot (or over an SSH-forwarded
        socket), ``tcp://host:port`` for a TCP forward. The default
        ``auto`` means the on-robot ``robotd`` socket.
        """
        device = self._config.device
        if device in ("auto", ""):
            device = "unix:///run/robotd.sock"
        if device.startswith("unix://"):
            path = device[len("unix://") :]
            family = getattr(socket, "AF_UNIX", None)
            if family is None:
                raise RuntimeError(
                    "microduck_transport_unavailable: this host has no AF_UNIX sockets. "
                    "Use device='tcp://<host>:<port>' with a forward "
                    "(e.g. ssh -L) to the robot's /run/robotd.sock."
                )
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(_DEFAULT_TIMEOUT)
            sock.connect(path)
            return _NdjsonTransport(sock)
        if device.startswith("tcp://"):
            host, _, port = device[len("tcp://") :].partition(":")
            if not port:
                raise RuntimeError(f"microduck_device_invalid: {device!r} needs tcp://<host>:<port>.")
            sock = socket.create_connection((host, int(port)), timeout=_DEFAULT_TIMEOUT)
            return _NdjsonTransport(sock)
        raise RuntimeError(
            f"microduck_device_invalid: {device!r}. Use 'unix:///run/robotd.sock' "
            "on the robot or 'tcp://<host>:<port>' for a forwarded stream."
        )

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        transport = self._dial()
        self._conn = transport
        # Version handshake: the first call on a connection, per the contract.
        self._request(transport, "hello", {"api_version": API_VERSION})
        return self._conn

    # ------------------------------------------------------------------
    # JSON-RPC
    # ------------------------------------------------------------------

    def _request(self, transport: _NdjsonTransport, method: str, params: dict[str, Any] | None) -> Any:
        """Send one request and return its ``result``. Errors become RuntimeError."""
        request_id = next(self._ids)
        message: dict[str, Any] = {"jsonrpc": JSONRPC_VERSION, "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        transport.write_line(json.dumps(message, separators=(",", ":")))
        # Notifications (progress, streamed frames) may interleave; skip
        # anything that is not the answer to this id.
        while True:
            reply = json.loads(transport.read_line())
            if reply.get("id") != request_id:
                continue
            if "error" in reply:
                err = reply["error"]
                raise RuntimeError(
                    f"microduck_rpc_error: {method} -> {err.get('code')}: {err.get('message')}"
                )
            return reply.get("result")

    def _notify(self, transport: _NdjsonTransport, method: str, params: dict[str, Any] | None) -> None:
        message: dict[str, Any] = {"jsonrpc": JSONRPC_VERSION, "method": method}
        if params is not None:
            message["params"] = params
        transport.write_line(json.dumps(message, separators=(",", ":")))

    # ------------------------------------------------------------------
    # EduCommand dispatch
    # ------------------------------------------------------------------

    def _send(self, command: EduCommand) -> None:
        """Dispatch a configured command as a wire call.

        The configured ``method`` is the wire method name (``robot.do``,
        ``robot.sound``, ``robot.init``, ...); ``kwargs`` become the JSON-RPC
        ``params`` object verbatim. Positional ``args`` are not part of
        JSON-RPC and are rejected with a typed error. Continuous intents
        (``robot.move`` and friends) go out as notifications, per the
        contract; everything else is a request whose refusal surfaces as a
        typed RuntimeError.

        Example ``edu_adapter.yaml`` entries::

            location_to_command:
              sit_spot:   { method: robot.do,    kwargs: { skill: sit_toggle } }
              step_ahead: { method: robot.move,  kwargs: { vx: 0.1, vy: 0.0, vyaw: 0.0 } }
              stand_up:   robot.init
            manipulation_commands:
              grasp:   { method: robot.do, kwargs: { skill: ground_pick } }
              release: { method: robot.relax }
        """
        method, args, kwargs = _resolve_call(command)
        if args:
            raise RuntimeError(
                f"microduck_positional_args_not_supported: JSON-RPC params are an object; "
                f"use kwargs (got method={method!r} args={args!r}). "
                "Example: {method: robot.do, kwargs: {skill: sit_toggle}}."
            )
        transport = self._open()
        params = kwargs or None
        if method in NOTIFICATION_METHODS:
            self._notify(transport, method, params)
            return
        self._request(transport, method, params)

    # ------------------------------------------------------------------
    # Protocol methods
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
        arm: str | None = None,
    ) -> ManipulationResult:
        return _grasp(self, action, force_n)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        """One read-back request; ``sensor`` is the wire method name.

        The natural reads are ``robot.health`` (the post-update health gate)
        and ``robot.mode`` (walk or roller). The result object passes through
        as the payload value, the Marty dict-pass-through convention.
        """
        method = sensor or "robot.health"
        if not method.startswith(("robot.", "system.", "net.")):
            return MeasurementResult(
                success=False,
                reason=(
                    f"microduck_sensor_not_found: {method!r} is not a read-back method. "
                    "Use a wire method name such as 'robot.health' or 'robot.mode'."
                ),
            )
        transport = self._open()
        try:
            result = self._request(transport, method, None)
        except RuntimeError as exc:
            return MeasurementResult(success=False, reason=str(exc))
        return MeasurementResult(success=True, payload={"value": result, "what": what})

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call("edu")
