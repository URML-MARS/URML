"""An MhsAdapter scaffold: URML primitives lowered onto read/write.

Anthropic's Model Hardware Standard announcement describes a driver with
"a simple set of primitives, commands like read (get temperature) or write
(set temperature)" that any device understands. This module is the shape
of the adapter URML will ship when the specification is open: a validated
program's Layer-2 primitives lower onto ``read(key)`` / ``write(key, value)``
calls against a declared key map, over an injectable transport.

Honesty label: **the wire format is a placeholder.** The key names, the
value encodings, and the transport are illustrative; none of them is the
MHS specification, which URML has not seen. What is real is the order of
operations: nothing is lowered before the program has been validated, and
the key map is deployment configuration, not something the agent invents
(the same pattern as ``SpotConfig.location_to_waypoint``).

This is deliberately not an RFC-0014 ``ROSAdapter``; promotion to a real
``urml-mhs-runtime`` with conformance fixtures waits for the open spec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class Transport(Protocol):
    def read(self, key: str) -> Any: ...
    def write(self, key: str, value: Any) -> None: ...


class FakeTransport:
    """Records every read/write; answers reads from a canned table."""

    def __init__(self, readings: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, str, Any]] = []
        self._readings = dict(readings or {})

    def read(self, key: str) -> Any:
        self.calls.append(("read", key, None))
        return self._readings.get(key)

    def write(self, key: str, value: Any) -> None:
        self.calls.append(("write", key, value))


@dataclass
class MhsKeyMap:
    """Deployment-side mapping from URML concepts to device keys (placeholder names)."""

    arm_target: str = "arm.target_location"
    gripper_close: str = "gripper.close_force_n"
    gripper_open: str = "gripper.open"
    sensor_reading: dict[str, str] = field(default_factory=dict)  # sensor name -> key


class MhsAdapter:
    """Lower a *validated* URML program onto read/write calls."""

    def __init__(self, transport: Transport, key_map: MhsKeyMap | None = None) -> None:
        self._t = transport
        self._keys = key_map or MhsKeyMap()

    def lower(self, program: dict[str, Any]) -> list[str]:
        """Dispatch each motion or measurement step; return a human-readable log."""
        log: list[str] = []
        for step in program["behavior"]["steps"]:
            (verb, args), = step.items()
            if verb == "move_to":
                self._t.write(self._keys.arm_target, args["location"])
                log.append(f"write {self._keys.arm_target} <- {args['location']}")
            elif verb == "pick_from":
                self._t.write(self._keys.arm_target, args["source"])
                force = args.get("force", "gentle")
                self._t.write(self._keys.gripper_close, force)
                log.append(f"write {self._keys.arm_target} <- {args['source']}; write {self._keys.gripper_close} <- {force}")
            elif verb == "place_at":
                self._t.write(self._keys.arm_target, args["target"])
                self._t.write(self._keys.gripper_open, True)
                log.append(f"write {self._keys.arm_target} <- {args['target']}; write {self._keys.gripper_open} <- true")
            elif verb == "measure":
                key = self._keys.sensor_reading.get(args.get("sensor", ""), f"{args.get('sensor')}.reading")
                value = self._t.read(key)
                log.append(f"read {key} -> {value!r} (bound as ${args['store_as']})")
            else:
                log.append(f"{verb}: no device call (handled by the runtime, not the driver)")
        return log
