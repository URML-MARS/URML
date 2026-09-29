"""ReachyMiniAdapter — expressive gaze + gesture for the Hugging Face Reachy Mini.

The first substrate to implement URML's ``ExpressionAdapter`` Protocol
(RFC-0698, the ``social`` profile). Until now only ``MockROSAdapter`` did.

Reachy Mini (Pollen Robotics / Hugging Face, Apache-2.0 SDK) is a desktop
expressive robot: a moving head (roll / pitch / yaw), a rotating body, and two
antennas. URML's ``look_at`` orients the head and body toward a direction;
``gesture`` plays a named expressive move.

## Client contract (honest, config-overridable)

Like the CircuitPython adapter, this does not hard-code one vendor build. It
drives a *client object* exposing a small surface, imported lazily from a
configurable ``module:attr`` factory:

- ``goto_target(head=<4x4>, body_yaw=<rad>, duration=<s>, method=<str>)`` for
  gaze. ``head`` is a 4x4 homogeneous head-orientation matrix (row-major list
  of lists) the adapter builds from the range-checked yaw / pitch / roll; wrap
  it if your SDK build wants a numpy array. Antennas are left at the SDK
  default (``look_at`` does not drive them).
- a named move method (from ``gesture_moves``) for each declared gesture,
  dispatched like the Marty / Petoi skill calls.

The real ``reachy_mini`` SDK, or a thin wrapper over it (or over Ori Nachum's
``reachy-nova`` daemon REST ``POST /api/move/goto``), provides that surface.
Hermetic tests run against a fake; hardware validation is a follow-up, never
claimed from the hermetic suite.

The validator has already confirmed the manifest declares ``expression``, the
gesture name is in the vocabulary, and any numeric ``direction`` is inside the
declared head/body ranges, so the adapter just orients or plays the move.
"""

from __future__ import annotations

import importlib
import math
import time
from contextlib import suppress
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from urml_ros2_runtime.substrate.base import SubstrateResult

from urml_edu_runtime.config import EduSkillCall

__all__ = ["ReachyConfig", "ReachyMiniAdapter"]


class ReachyConfig(BaseModel):
    """Deployment config for :class:`ReachyMiniAdapter`."""

    model_config = ConfigDict(extra="forbid")

    client_factory: str = Field(
        default="reachy_mini:ReachyMini",
        description="`module:attr` of the SDK client class, imported lazily and constructed with `host`.",
    )
    host: str | None = Field(
        default=None,
        description="Optional host/connection string passed to the client factory; omitted when None.",
    )
    goto_method: str = Field(
        default="goto_target",
        description="Client method that orients the head/body (RFC-0698 `look_at`).",
    )
    move_method: str = Field(
        default="minjerk",
        description="Interpolation method passed to goto_target.",
    )
    default_duration_s: float = Field(default=1.0, gt=0)
    gesture_moves: dict[str, EduSkillCall] = Field(
        default_factory=dict,
        description="Map each declared gesture name to the SDK move call that plays it.",
    )


def _import_factory(spec: str) -> Any:
    module_name, _, attr = spec.partition(":")
    if not attr:
        raise ValueError(f"client_factory {spec!r} must be 'module:attr'")
    return getattr(importlib.import_module(module_name), attr)


def _rotation_matrix(roll_deg: float, pitch_deg: float, yaw_deg: float) -> list[list[float]]:
    """A 4x4 homogeneous rotation (row-major) from roll/pitch/yaw degrees.

    R = Rz(yaw) @ Ry(pitch) @ Rx(roll); translation is zero.
    """
    r, p, y = math.radians(roll_deg), math.radians(pitch_deg), math.radians(yaw_deg)
    cr, sr = math.cos(r), math.sin(r)
    cp, sp = math.cos(p), math.sin(p)
    cy, sy = math.cos(y), math.sin(y)
    return [
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr, 0.0],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr, 0.0],
        [-sp, cp * sr, cp * cr, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


class ReachyMiniAdapter:
    """Reachy Mini expressive-platform backing for URML `look_at` / `gesture`."""

    def __init__(self, config: ReachyConfig | None = None) -> None:
        self._config = config or ReachyConfig()
        self._client: Any = None
        self._closed = False

    def _open(self) -> Any:
        if self._client is not None:
            return self._client
        factory = _import_factory(self._config.client_factory)
        self._client = factory(self._config.host) if self._config.host is not None else factory()
        return self._client

    def close(self) -> None:
        if self._closed:
            return
        if self._client is not None:
            with suppress(Exception):
                close = getattr(self._client, "disconnect", None) or getattr(self._client, "close", None)
                if callable(close):
                    close()
        self._closed = True

    def __enter__(self) -> ReachyMiniAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ---- ExpressionAdapter (RFC-0698) ----

    def orient_gaze(
        self,
        *,
        target: Literal["face", "sound", "object", "direction"],
        object: str | None = None,
        yaw: float | None = None,
        pitch: float | None = None,
        roll: float | None = None,
        body_yaw: float | None = None,
        duration_seconds: float | None = None,
        hold_seconds: float | None = None,
    ) -> SubstrateResult:
        if target != "direction":
            return SubstrateResult(
                success=False,
                reason=(
                    f"reachy_gaze_target_not_supported: only `direction` is driven; {target!r} needs a "
                    "tracker (face detector / sound localizer / object detector) not in the base SDK. "
                    "Pair one and map it in a wrapper."
                ),
            )
        head = _rotation_matrix(roll or 0.0, pitch or 0.0, yaw or 0.0)
        duration = duration_seconds if duration_seconds is not None else self._config.default_duration_s
        client = self._open()
        goto = getattr(client, self._config.goto_method, None)
        if not callable(goto):
            return SubstrateResult(
                success=False,
                reason=(
                    f"reachy_client_missing_method: the client has no callable {self._config.goto_method!r}. "
                    "Point `goto_method` at the SDK's head/body orient call."
                ),
            )
        goto(
            head=head,
            body_yaw=math.radians(body_yaw) if body_yaw is not None else 0.0,
            duration=duration,
            method=self._config.move_method,
        )
        if hold_seconds is not None:
            time.sleep(hold_seconds)
        return SubstrateResult(success=True)

    def perform_gesture(
        self,
        *,
        name: str,
        intensity: float | None = None,
        interrupt: bool = False,
    ) -> SubstrateResult:
        call = self._config.gesture_moves.get(name)
        if call is None:
            return SubstrateResult(
                success=False,
                reason=(
                    f"reachy_gesture_not_configured: {name!r} is declared in the manifest but not mapped "
                    "to an SDK move in `gesture_moves`."
                ),
            )
        client = self._open()
        move = getattr(client, call.method, None)
        if not callable(move):
            return SubstrateResult(
                success=False,
                reason=(
                    f"reachy_client_missing_method: the client has no callable {call.method!r} for gesture "
                    f"{name!r}. Map it to a real SDK move in `gesture_moves`."
                ),
            )
        move(*call.args, **call.kwargs)
        return SubstrateResult(success=True)
