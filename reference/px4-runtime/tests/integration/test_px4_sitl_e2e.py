"""End-to-end: a URML conformance fixture flying a simulated autopilot.

This is the real thing, not a smoke test. It takes the
``drone/flight_only_positive`` conformance fixture (take_off, one
waypoint, return_to_home, land) and runs it through the *same*
``ConformanceRunner`` the hermetic suite uses, but with the
``adapter_factory`` wired to a live ``PX4Adapter``. The adapter sends
MAVLink commands to a running PX4 SITL instance. If the simulated
autopilot takes off, flies the waypoint, returns to launch, and lands,
and every command is acked, the fixture passes, proving the full path
closes:

    URML program -> validator -> ConformanceRunner -> PX4Adapter
                 -> MAVLink -> PX4 SITL autopilot actually flies.

## Gating

Two independent gates, both required:

  - ``URML_PX4_SITL=1`` opts in to the heavy sim test.
  - PX4 SITL must answer a MAVLink heartbeat within a short bound. If it
    does not, the test fails fast with an actionable message ("is PX4
    SITL actually up on udp:14540?") rather than hanging.

The default ``pytest`` invocation skips this module entirely. The
``px4-sitl-e2e`` job in ``.github/workflows/px4-integration.yml`` boots
PX4 SITL headless, sets the env var, and runs it; it also uploads the
SITL log and the pytest output as artifacts on ``always()`` so a failed
first run is diagnosable, not opaque.

## Honest scope

PX4 SITL is a simulated autopilot, not physical hardware. This test
proves the PX4 adapter actually flies a simulated vehicle from a URML
program. A physical-aircraft run needs hardware, an airframe, and a
licensed operator and is out of Phase-0 scope. No claim of
physical-hardware verification is made here or anywhere in this repo.

The fixture is flight-only on purpose: the PX4 adapter implements the
flight primitives for real and returns a documented not-supported
result for perception/manipulation, so this covers the *flight* slice
end to end, the load-bearing one for "does the adapter actually fly a
real autopilot".
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_PX4_SITL") != "1",
    reason="Set URML_PX4_SITL=1 (and have PX4 SITL running) to run the PX4 SITL e2e test.",
)

_ADAPTER_CONFIG = Path(__file__).parent / "px4_adapter_flight_only.yaml"
_FIXTURE_NAME = "drone/flight_only_positive"

# How long to wait for PX4 SITL's first MAVLink heartbeat before
# declaring the sim absent. Generous because a cold SITL boot is slow,
# but bounded so a missing sim fails fast-ish with a clear message
# instead of an opaque hang.
_HEARTBEAT_TIMEOUT_S = 60.0


def _wait_for_px4_heartbeat(connection_url: str, timeout_s: float) -> bool:
    """Return True once PX4 SITL answers a MAVLink heartbeat."""
    from pymavlink import mavutil

    conn = mavutil.mavlink_connection(connection_url)
    try:
        hb = conn.wait_heartbeat(timeout=timeout_s)
        return hb is not None
    finally:
        conn.close()


def test_flight_only_fixture_runs_against_px4_sitl() -> None:
    """The flight-only fixture passes when flown against live PX4 SITL."""
    from urml_conformance import ConformanceRunner, discover_fixtures
    from urml_px4_runtime import PX4Adapter
    from urml_px4_runtime.config import load_px4_config

    config = load_px4_config(_ADAPTER_CONFIG)

    # Fail fast + actionable if PX4 SITL isn't actually up.
    assert _wait_for_px4_heartbeat(config.connection_url, _HEARTBEAT_TIMEOUT_S), (
        f"PX4 SITL did not answer a MAVLink heartbeat on "
        f"{config.connection_url} within {_HEARTBEAT_TIMEOUT_S:.0f}s. Is PX4 "
        "SITL running headless? See .github/workflows/px4-integration.yml for "
        "the boot invocation."
    )

    # Run ONLY the flight-only fixture through the same runner the
    # hermetic suite uses. The only difference is the adapter.
    cases = [c for c in discover_fixtures() if c.name == _FIXTURE_NAME]
    assert cases, f"fixture {_FIXTURE_NAME!r} not found in the conformance suite"

    runner = ConformanceRunner(
        cases=cases,
        adapter_factory=lambda: PX4Adapter(config),
    )
    report = runner.run()
    assert report.all_passed, (
        "flight-only fixture failed against live PX4 SITL:\n" + report.render()
    )
