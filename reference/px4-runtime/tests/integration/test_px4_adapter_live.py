"""Live smoke for PX4Adapter under a real pymavlink install — no SITL.

This is the PX4 analog of the ROS 2 runtime's
``tests/integration/test_rclpy_adapter_live.py`` `rclpy-smoke`. It is
deliberately the *light* gate, distinct from the heavy
``test_px4_sitl_e2e.py`` which actually flies a simulated autopilot:

  - This file needs only the real ``pymavlink`` wheel installed. It
    constructs ``PX4Adapter`` (construction requires pymavlink but does
    NOT open a MAVLink connection — ``_connect`` is lazy) and confirms
    the ``ConformanceRunner.adapter_factory`` hook accepts it. No
    autopilot, real or simulated, is contacted.
  - ``test_px4_sitl_e2e.py`` needs a running PX4 SITL and flies the
    ``drone/flight_only_positive`` fixture end to end.

## Gating

The default ``pytest`` invocation skips this module entirely. The
``px4-smoke`` job in ``.github/workflows/px4-integration.yml`` sets
``URML_PX4_INTEGRATION=1`` (mirroring the ROS 2 runtime's
``URML_ROS2_INTEGRATION``) and runs it. The two PX4 gates are kept
distinct on purpose: ``URML_PX4_INTEGRATION`` for this no-sim smoke,
``URML_PX4_SITL`` for the heavy flight e2e.

## What this proves

That the ``[px4]`` extra's real ``pymavlink`` resolves the adapter's
lazy import, that ``PX4Adapter`` construction works against the real
wheel (not just the hermetic fake the unit suite injects), and that the
conformance hook will accept a live-adapter factory. It is the
load-bearing "the real dependency is sufficient" check; behavior under
real MAVLink is covered by the SITL e2e.
"""

from __future__ import annotations

import os

import pytest

# Skip the whole module unless the integration flag is set. This keeps
# the default `pytest` invocation hermetic on every host.
pytestmark = pytest.mark.skipif(
    os.environ.get("URML_PX4_INTEGRATION") != "1",
    reason="Set URML_PX4_INTEGRATION=1 to run the PX4 live smoke (real pymavlink, no SITL).",
)


def test_real_pymavlink_is_importable() -> None:
    """The real pymavlink module is available under the smoke env."""
    from pymavlink import mavutil  # noqa: F401


def test_adapter_constructs_against_real_pymavlink() -> None:
    """PX4Adapter constructs against real pymavlink without connecting.

    Construction calls ``_require_pymavlink()`` (so it needs the real
    wheel) but must NOT open a MAVLink connection — ``_connect`` is lazy
    and only fires on the first Protocol call. A bare construct is the
    PX4 analog of the rclpy smoke's "constructs and closes".
    """
    from urml_px4_runtime import PX4Adapter

    with PX4Adapter() as adapter:
        # No Protocol method called -> no connection opened.
        assert adapter._connection is None


def test_conformance_runner_accepts_real_adapter_factory() -> None:
    """The ConformanceRunner accepts a real PX4Adapter factory.

    Mirrors the rclpy smoke: this does NOT run the fixture suite (that
    needs a live autopilot — see ``test_px4_sitl_e2e.py``). The hook
    itself is what's under test; it must accept a real-adapter factory
    without raising.
    """
    from urml_conformance import ConformanceRunner
    from urml_px4_runtime import PX4Adapter

    runner = ConformanceRunner(adapter_factory=lambda: PX4Adapter())
    assert runner is not None
