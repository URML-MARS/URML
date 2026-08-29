"""Bench test against a real ArduPilot board. PROPS OFF.

Gated on ``URML_ARDUPILOT_BENCH=<connection>`` (for example ``COM5`` or
``/dev/ttyACM0``). What it proves, in order:

1. The link works and the board identifies as an ArduCopter (read-only
   probe; no state change).
2. A read-only URML program (``measure`` battery voltage, ``report``)
   runs end to end through ``URMLRuntime`` with this adapter.
3. A ``take_off`` is *refused*: the autopilot's own pre-arm checks say no
   (no GPS fix indoors, or whatever else is unmet) and the adapter
   returns that refusal as a clean result. Nothing here disables
   ``ARMING_CHECK``.

The third step sends a real mode-change and arm request. If the vehicle
is already armed, or has a GPS fix and passes pre-arm, the take-off could
succeed and motors would spin. The test therefore refuses to run step 3
unless the probe reports disarmed and no 3D fix, and it must never be run
with propellers fitted.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

_PORT = os.environ.get("URML_ARDUPILOT_BENCH")

pytestmark = pytest.mark.skipif(
    not _PORT,
    reason="Set URML_ARDUPILOT_BENCH=<port> (props OFF) to run the ArduPilot bench test.",
)

_EXAMPLES = Path(__file__).resolve().parents[4] / "examples" / "drone"


def _config() -> object:
    from urml_ardupilot_runtime import ArduPilotAdapterConfig

    assert _PORT is not None
    return ArduPilotAdapterConfig(
        connection_url=_PORT,
        heartbeat_timeout_seconds=10.0,
        ack_timeout_seconds=5.0,
        mode_timeout_seconds=3.0,
        arm_timeout_seconds=3.0,
    )


def _load(name: str) -> dict:
    with (_EXAMPLES / name).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_probe_identifies_an_arducopter() -> None:
    from urml_ardupilot_runtime import ArduCopterAdapter

    with ArduCopterAdapter(_config()) as adapter:  # type: ignore[arg-type]
        info = adapter.probe(listen_seconds=4.0)
    assert info["autopilot"] == "ArduPilot"
    assert info["mav_type"] in {2, 13, 14, 15, 29}
    assert info["armed"] is False, "bench test refuses to run against an armed vehicle"
    assert info["firmware"] is not None


def test_battery_program_runs_through_runtime() -> None:
    from urml_ros2_runtime import URMLRuntime

    from urml_ardupilot_runtime import ArduCopterAdapter

    program = _load("bench-battery.urml.yaml")
    manifest = _load("pixhawk-ardupilot.manifest.yaml")
    with ArduCopterAdapter(_config()) as adapter:  # type: ignore[arg-type]
        result = URMLRuntime(adapter).execute(program, manifest, profiles=("drone",))
    assert result.success, result.last_outcome
    reading = result.bindings.get("battery")
    assert reading is not None
    assert 0.0 <= float(reading["value"]) <= 60.0


def test_takeoff_is_refused_by_prearm() -> None:
    from urml_ardupilot_runtime import ArduCopterAdapter

    with ArduCopterAdapter(_config()) as adapter:  # type: ignore[arg-type]
        info = adapter.probe(listen_seconds=3.0)
        if info["armed"] or (info["gps_fix"] or 0) >= 3:
            pytest.skip("vehicle is armed or has a 3D fix: refusing to send a take-off on the bench")
        result = adapter.send_takeoff_goal(altitude=3.0)
        after = adapter.probe(listen_seconds=2.0)
    assert result.success is False
    assert result.reason is not None
    assert result.reason.startswith(("mode_rejected:", "arm_rejected:")), result.reason
    assert after["armed"] is False
