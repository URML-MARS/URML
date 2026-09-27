"""End-to-end: a URML conformance fixture flying a simulated PX4 autopilot.

It takes the ``drone/flight_only_positive`` conformance fixture (take_off,
one waypoint, return_to_home, land) and runs it through the *same*
``ConformanceRunner`` the hermetic suite uses, with the
``adapter_factory`` wired to a live ``PX4Adapter`` talking MAVLink to a
running PX4 SITL instance:

    URML program -> validator -> ConformanceRunner -> PX4Adapter
                 -> MAVLink -> PX4 SITL autopilot.

## A green run means the vehicle flew

A passing fixture is not enough on its own: an earlier version of this
test passed in about two seconds because the adapter counted each
COMMAND_ACK as success while the simulated vehicle never armed or left
the ground. So the test also keeps an independent witness: a second
pymavlink connection on PX4 SITL's ground-station port (UDP 14550), which
only listens and never sends. After the fixture passes, the witness must
show that

  - the vehicle armed,
  - the highest relative altitude reached at least 90 percent of the
    fixture's take-off altitude,
  - the vehicle travelled at least 90 percent of the way to the waypoint
    (horizontal distance from home), and
  - the vehicle ended on the ground (EXTENDED_SYS_STATE ON_GROUND).

The witness numbers are printed (run pytest with ``-s``) so a run can be
recorded as evidence.

## Gating

  - ``URML_PX4_SITL=1`` opts in to the heavy sim test.
  - PX4 SITL must answer a MAVLink heartbeat within a short bound, and
    report itself ready to arm (home set, pre-arm checks passing) within
    ``_READY_TIMEOUT_S``. If not, the test fails with an actionable
    message rather than hanging.

The default ``pytest`` invocation skips this module entirely.

## Honest scope

PX4 SITL is a simulated autopilot, not physical hardware. This test
shows the PX4 adapter flying a simulated vehicle from a URML program. A
physical-aircraft run needs hardware, an airframe, and a licensed
operator, and is out of scope. No claim of physical-hardware
verification is made here or anywhere in this repo.

The fixture is flight-only on purpose: the PX4 adapter implements the
flight primitives and returns a documented not-supported result for
perception/manipulation, so this covers the flight slice end to end.
"""

from __future__ import annotations

import math
import os
import threading
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_PX4_SITL") != "1",
    reason="Set URML_PX4_SITL=1 (and have PX4 SITL running) to run the PX4 SITL e2e test.",
)

_ADAPTER_CONFIG = Path(__file__).parent / "px4_adapter_flight_only.yaml"
_FIXTURE_NAME = "drone/flight_only_positive"

# How long to wait for PX4 SITL's first MAVLink heartbeat before
# declaring the sim absent. Generous because a cold SITL boot is slow,
# but bounded so a missing sim fails with a clear message.
_HEARTBEAT_TIMEOUT_S = 60.0

# PX4 SITL streams its ground-station link to this port on localhost.
_WITNESS_URL = "udpin:127.0.0.1:14550"
_READY_TIMEOUT_S = 120.0
# PX4 disarms a couple of seconds after touchdown (COM_DISARM_LAND).
_SETTLE_TIMEOUT_S = 20.0

_MAV_LANDED_STATE_ON_GROUND = 1
_MAV_MODE_FLAG_SAFETY_ARMED = 128
_MAV_SYS_STATUS_PREARM_CHECK = 0x10000000
_EARTH_RADIUS_M = 6_371_000.0


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (
        math.sin((p2 - p1) / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    )
    return 2 * _EARTH_RADIUS_M * math.asin(math.sqrt(min(1.0, a)))


@dataclass
class _Seen:
    """What the witness has seen of the vehicle so far."""

    samples: int = 0
    armed_seen: bool = False
    armed_now: bool | None = None
    prearm_ok: bool = False
    home: tuple[float, float] | None = None
    landed_state: int | None = None
    landed_states: list[int] = field(default_factory=list)
    max_relative_alt_m: float | None = None
    max_distance_from_home_m: float = 0.0
    last_relative_alt_m: float | None = None


class _Witness:
    """Listens to PX4 SITL's ground-station link and records what the vehicle did.

    It never sends a message, so it cannot influence the flight; it only
    reads what the autopilot streams on its own.
    """

    def __init__(self, url: str) -> None:
        from pymavlink import mavutil

        self._conn = mavutil.mavlink_connection(url)
        self._seen = _Seen()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="px4-sitl-witness", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=5)
        self._conn.close()

    def snapshot(self) -> _Seen:
        with self._lock:
            return replace(self._seen, landed_states=list(self._seen.landed_states))

    def wait_until(self, predicate: Any, timeout_s: float) -> bool:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if predicate(self.snapshot()):
                return True
            time.sleep(0.25)
        return bool(predicate(self.snapshot()))

    def _run(self) -> None:
        while not self._stop.is_set():
            msg = self._conn.recv_match(blocking=True, timeout=0.2)
            if msg is None or msg.get_srcSystem() != 1:
                continue
            kind = msg.get_type()
            with self._lock:
                seen = self._seen
                if kind == "HEARTBEAT" and msg.get_srcComponent() == 1:
                    seen.armed_now = bool(msg.base_mode & _MAV_MODE_FLAG_SAFETY_ARMED)
                    seen.armed_seen = seen.armed_seen or seen.armed_now
                elif kind == "SYS_STATUS":
                    seen.prearm_ok = bool(msg.onboard_control_sensors_health & _MAV_SYS_STATUS_PREARM_CHECK)
                elif kind == "HOME_POSITION":
                    seen.home = (msg.latitude / 1e7, msg.longitude / 1e7)
                elif kind == "EXTENDED_SYS_STATE":
                    seen.landed_state = int(msg.landed_state)
                    if not seen.landed_states or seen.landed_states[-1] != seen.landed_state:
                        seen.landed_states.append(seen.landed_state)
                elif kind == "GLOBAL_POSITION_INT":
                    seen.samples += 1
                    rel = msg.relative_alt / 1000.0
                    seen.last_relative_alt_m = rel
                    # Before home is set PX4 reports AMSL here; count only flight with a home.
                    if seen.armed_seen and seen.home is not None:
                        seen.max_relative_alt_m = (
                            rel if seen.max_relative_alt_m is None else max(seen.max_relative_alt_m, rel)
                        )
                    if seen.home is not None:
                        d = _haversine_m(msg.lat / 1e7, msg.lon / 1e7, *seen.home)
                        seen.max_distance_from_home_m = max(seen.max_distance_from_home_m, d)


def _wait_for_px4_heartbeat(connection_url: str, timeout_s: float) -> bool:
    """Return True once PX4 SITL answers a MAVLink heartbeat."""
    from pymavlink import mavutil

    conn = mavutil.mavlink_connection(connection_url)
    try:
        hb = conn.wait_heartbeat(timeout=timeout_s)
        return hb is not None
    finally:
        conn.close()


def _step_args(program: dict[str, Any], verb: str) -> dict[str, Any]:
    for step in program["behavior"]["steps"]:
        if verb in step:
            args: dict[str, Any] = step[verb]
            return args
    raise AssertionError(f"fixture program has no {verb!r} step")


def test_flight_only_fixture_flies_px4_sitl() -> None:
    """The flight-only fixture passes against live PX4 SITL, and the vehicle flew it."""
    from urml_conformance import ConformanceRunner, discover_fixtures

    from urml_px4_runtime import PX4Adapter
    from urml_px4_runtime.config import load_px4_config

    config = load_px4_config(_ADAPTER_CONFIG)

    # Fail fast + actionable if PX4 SITL isn't actually up.
    assert _wait_for_px4_heartbeat(config.connection_url, _HEARTBEAT_TIMEOUT_S), (
        f"PX4 SITL did not answer a MAVLink heartbeat on "
        f"{config.connection_url} within {_HEARTBEAT_TIMEOUT_S:.0f}s. Is PX4 "
        "SITL running headless (make px4_sitl sihsim_quadx)?"
    )

    cases = [c for c in discover_fixtures() if c.name == _FIXTURE_NAME]
    assert cases, f"fixture {_FIXTURE_NAME!r} not found in the conformance suite"
    takeoff_alt = float(_step_args(cases[0].program, "take_off")["altitude"])
    waypoint = config.resolve_location(str(_step_args(cases[0].program, "move_to")["location"]))
    assert waypoint is not None, "the adapter config does not bind the fixture's waypoint"
    waypoint_distance = math.hypot(waypoint.north, waypoint.east)

    witness = _Witness(_WITNESS_URL)
    witness.start()
    adapters: list[PX4Adapter] = []
    started = time.monotonic()
    try:
        ready = witness.wait_until(
            lambda s: s.prearm_ok
            and s.home is not None
            and s.landed_state == _MAV_LANDED_STATE_ON_GROUND
            and s.armed_now is False,
            _READY_TIMEOUT_S,
        )
        assert ready, (
            f"PX4 SITL did not report ready to arm on the ground within {_READY_TIMEOUT_S:.0f}s "
            f"(witness on {_WITNESS_URL} saw {witness.snapshot()})."
        )

        def _factory() -> PX4Adapter:
            adapter = PX4Adapter(config)
            adapters.append(adapter)
            return adapter

        # Run ONLY the flight-only fixture through the same runner the
        # hermetic suite uses. The only difference is the adapter.
        report = ConformanceRunner(cases=cases, adapter_factory=_factory).run()
        flown_s = time.monotonic() - started
        witness.wait_until(
            lambda s: s.landed_state == _MAV_LANDED_STATE_ON_GROUND and s.armed_now is False,
            _SETTLE_TIMEOUT_S,
        )
    finally:
        for adapter in adapters:
            adapter.close()
        witness.stop()

    seen = witness.snapshot()
    print(
        "\nPX4 SITL witness (udp 14550, listen-only): "
        f"samples={seen.samples} armed_seen={seen.armed_seen} "
        f"max_relative_alt_m={seen.max_relative_alt_m} (take-off target {takeoff_alt:.1f}) "
        f"max_distance_from_home_m={seen.max_distance_from_home_m:.2f} (waypoint {waypoint_distance:.1f}) "
        f"landed_states={seen.landed_states} final_landed_state={seen.landed_state} "
        f"armed_at_end={seen.armed_now} fixture_seconds={flown_s:.1f}"
    )

    assert report.all_passed, "flight-only fixture failed against live PX4 SITL:\n" + report.render()
    assert seen.samples > 0, f"the witness on {_WITNESS_URL} received no GLOBAL_POSITION_INT"
    assert seen.armed_seen, "the fixture passed but PX4 never reported itself armed"
    assert seen.max_relative_alt_m is not None and seen.max_relative_alt_m >= 0.9 * takeoff_alt, (
        f"the fixture passed but the vehicle only reached {seen.max_relative_alt_m} m "
        f"of a {takeoff_alt:.1f} m take-off"
    )
    assert seen.max_distance_from_home_m >= 0.9 * waypoint_distance, (
        f"the fixture passed but the vehicle only got {seen.max_distance_from_home_m:.1f} m "
        f"from home toward a {waypoint_distance:.1f} m waypoint"
    )
    assert seen.landed_state == _MAV_LANDED_STATE_ON_GROUND, (
        f"the vehicle did not end on the ground (landed_state={seen.landed_state})"
    )
