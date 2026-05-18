"""End-to-end: a URML pick-place fixture run on a simulated industrial arm.

The PX4 analog is ``reference/px4-runtime/tests/integration/
test_px4_sitl_e2e.py``. This takes the existing ``industrial/
pick_red_positive`` conformance fixture and runs it through the *same*
``ConformanceRunner`` the hermetic suite uses, with ``adapter_factory``
wired to a live brand arm composed with a vision companion.

## Why a composite

``GraspArgs.target`` is a required ``VarRef`` — URML ``grasp`` always
acts on a *detected* target, so a pick-place program necessarily
contains a ``detect`` step. A bare fixed-base arm has no onboard
perception (it returns ``not_supported_on_industrial_arm`` for
``query_detection``), exactly as a bare PX4 autopilot has no
perception. The honest deployment, and the one this test exercises, is
the brand arm paired with a vision companion via the already-tested
``urml_px4_runtime.CompositeAdapter`` (a generic two-backend router;
the ``flight``/``companion`` slot names are role-neutral). Arm owns
motion + manipulation + report; the vision companion owns detection.

## Gating

Two gates, both required:

  - ``URML_INDUSTRIAL_ARM_SIM=1`` opts in to the heavy sim test.
  - ``URML_ARM_BRAND`` selects the vendor (abb | fanuc | kuka |
    yaskawa); defaults to ``abb``.

The default ``pytest`` invocation skips this module entirely. The
``industrial-arm-integration.yml`` workflow brings up a ROS 2 + MoveIt 2
sim, sets the env vars, and runs it per brand; it uploads ROS logs and
the pytest output as artifacts on ``always()``.

## Honest scope

A MoveIt 2 sim with fake controllers is not physical hardware. This
proves the brand adapter actually drives a simulated arm from a URML
program. The first run is a calibration run (the vendor moveit_config /
launch names below are best-effort, authored without the ability to run
the sim — same convention as the px4 and ros2 integration workflows),
not a regression signal.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_INDUSTRIAL_ARM_SIM") != "1",
    reason="Set URML_INDUSTRIAL_ARM_SIM=1 (and have a MoveIt 2 sim running) to run this.",
)

_FIXTURE_NAME = "industrial/pick_red_positive"


def test_pick_place_fixture_runs_against_sim() -> None:
    """The pick-place fixture passes when run against a simulated arm + vision."""
    from urml_conformance import ConformanceRunner, discover_fixtures
    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    # CompositeAdapter is a generic two-backend router shipped with the
    # px4 runtime; reused here so no industrial-specific composite code
    # is duplicated. Imported lazily so the package keeps no px4 dep.
    from urml_px4_runtime import CompositeAdapter

    from urml_industrial_arm_runtime import BRAND_ADAPTERS

    brand = os.environ.get("URML_ARM_BRAND", "abb").strip().lower()
    if brand not in BRAND_ADAPTERS:
        pytest.fail(f"URML_ARM_BRAND={brand!r} is not one of {sorted(BRAND_ADAPTERS)!r}")

    cases = [c for c in discover_fixtures() if c.name == _FIXTURE_NAME]
    assert cases, f"fixture {_FIXTURE_NAME!r} not found in the conformance suite"

    # Arm in the `flight` slot (motion + manipulation + report); vision
    # in the `companion` slot (perception). Override the default routing
    # so manipulation/report/wait_for go to the ARM, not the vision box.
    arm_to_flight = {
        "send_manipulation_goal": "flight",
        "take_measurement": "flight",
        "wait_for_condition": "flight",
        "emit_report": "flight",
    }

    def _factory() -> CompositeAdapter:
        arm = BRAND_ADAPTERS[brand]()  # brand default ROS-Industrial config
        vision = RclpyAdapter(AdapterConfig(), node_name=f"urml_{brand}_vision")
        return CompositeAdapter(flight=arm, companion=vision, routing=arm_to_flight)

    runner = ConformanceRunner(cases=cases, adapter_factory=_factory)
    report = runner.run()
    assert report.all_passed, (
        f"{_FIXTURE_NAME} failed against the {brand} MoveIt 2 sim:\n" + report.render()
    )
