"""End-to-end: URML conformance fixtures flying ArduCopter SITL.

Mirrors the PX4 runtime's ``test_px4_sitl_e2e.py``. Runs the
``drone/flight_only_positive`` conformance fixture through the same
``ConformanceRunner`` the hermetic suite uses, with a live
``ArduCopterAdapter`` pointed at a running ArduCopter SITL:

    sim_vehicle.py -v ArduCopter --console --out udp:<host>:14550

Then the two flight-test example programs (site photogrammetry, parcel
delivery) run through ``URMLRuntime`` against the same SITL with their
example manifests and envelopes. SITL acks camera, gripper, and winch
commands when ``CAM_TRIGG_TYPE``, ``GRIP_TYPE``, and ``WINCH_TYPE`` are set;
the runbook lists the parameters.

Gated on ``URML_ARDUPILOT_SITL=1``. ``URML_ARDUPILOT_SITL_URL`` overrides
the connection (default ``udp:127.0.0.1:14550``). A missing SITL fails
fast with an actionable message instead of hanging.

This is a simulated autopilot. No physical flight is claimed here.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_ARDUPILOT_SITL") != "1",
    reason="Set URML_ARDUPILOT_SITL=1 (and run ArduCopter SITL) to run the ArduPilot SITL e2e.",
)

_URL = os.environ.get("URML_ARDUPILOT_SITL_URL", "udp:127.0.0.1:14550")
_HEARTBEAT_TIMEOUT_S = 60.0
_EXAMPLES = Path(__file__).resolve().parents[4] / "examples" / "drone"


def _load(name: str) -> dict:
    with (_EXAMPLES / name).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _sitl_config(**extra: object) -> object:
    from urml_px4_runtime.config import NEDPosition

    from urml_ardupilot_runtime import ArduPilotAdapterConfig

    return ArduPilotAdapterConfig(
        connection_url=_URL,
        heartbeat_timeout_seconds=_HEARTBEAT_TIMEOUT_S,
        arm_timeout_seconds=30.0,
        takeoff_timeout_seconds=90.0,
        arrival_timeout_seconds=180.0,
        location_to_pose={
            "roof_north": NEDPosition(north=15.0, east=0.0, alt=30.0),
            "home": NEDPosition(north=0.0, east=0.0, alt=0.0),
        },
        **extra,
    )


def _assert_sitl_up() -> None:
    from pymavlink import mavutil

    conn = mavutil.mavlink_connection(_URL)
    try:
        hb = conn.wait_heartbeat(timeout=_HEARTBEAT_TIMEOUT_S)
    finally:
        conn.close()
    assert hb is not None, (
        f"ArduCopter SITL did not answer a heartbeat on {_URL} within {_HEARTBEAT_TIMEOUT_S:.0f}s. "
        "Start it with: sim_vehicle.py -v ArduCopter --out udp:<this-host>:14550"
    )


def test_flight_only_fixture_runs_against_sitl() -> None:
    from urml_conformance import ConformanceRunner, discover_fixtures

    from urml_ardupilot_runtime import ArduCopterAdapter

    _assert_sitl_up()
    cases = [c for c in discover_fixtures() if c.name == "drone/flight_only_positive"]
    assert cases
    runner = ConformanceRunner(cases=cases, adapter_factory=lambda: ArduCopterAdapter(_sitl_config()))  # type: ignore[arg-type]
    report = runner.run()
    assert report.all_passed, report.render()


def test_site_photogrammetry_example_runs_against_sitl() -> None:
    from urml_ros2_runtime import URMLRuntime

    from urml_ardupilot_runtime import ArduCopterAdapter, load_ardupilot_config

    _assert_sitl_up()
    cfg = load_ardupilot_config(_EXAMPLES / "site-photogrammetry.adapter.yaml")
    cfg = cfg.model_copy(update={"connection_url": _URL, "takeoff_timeout_seconds": 120.0})
    with ArduCopterAdapter(cfg) as adapter:
        result = URMLRuntime(adapter).execute(
            _load("site-photogrammetry.urml.yaml"),
            _load("site-photogrammetry.manifest.yaml"),
            envelope=_load("site-photogrammetry.envelope.yaml"),
            profiles=("drone",),
        )
    assert result.success, result.last_outcome
    assert all(f"shot_{k}" in result.bindings for k in range(1, 6))


def test_parcel_delivery_example_runs_against_sitl() -> None:
    from urml_ros2_runtime import URMLRuntime

    from urml_ardupilot_runtime import ArduCopterAdapter, load_ardupilot_config

    _assert_sitl_up()
    cfg = load_ardupilot_config(_EXAMPLES / "parcel-delivery.adapter.yaml")
    cfg = cfg.model_copy(update={"connection_url": _URL})
    with ArduCopterAdapter(cfg) as adapter:
        result = URMLRuntime(adapter).execute(
            _load("parcel-delivery.urml.yaml"),
            _load("parcel-delivery.manifest.yaml"),
            envelope=_load("parcel-delivery.envelope.yaml"),
            profiles=("drone",),
        )
    assert result.success, result.last_outcome
