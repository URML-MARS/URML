"""Live smoke for ArduCopterAdapter under a real pymavlink install — no autopilot.

The ArduPilot analog of the PX4 runtime's ``test_px4_adapter_live.py``.
It needs only the real ``pymavlink`` and ``pyserial`` wheels (the
``[ardupilot]`` extra). It constructs the adapter (lazy connect: nothing
is contacted) and confirms the conformance runner accepts it as a
factory.

Gated on ``URML_ARDUPILOT_INTEGRATION=1`` so the default pytest run stays
hermetic on every host.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_ARDUPILOT_INTEGRATION") != "1",
    reason="Set URML_ARDUPILOT_INTEGRATION=1 to run the ArduPilot live smoke (real pymavlink, no autopilot).",
)


def test_real_pymavlink_and_pyserial_importable() -> None:
    import serial  # noqa: F401
    from pymavlink import mavutil  # noqa: F401


def test_adapter_constructs_without_connecting() -> None:
    from urml_ardupilot_runtime import ArduCopterAdapter

    with ArduCopterAdapter() as adapter:
        assert adapter._connection is None


def test_conformance_runner_accepts_factory() -> None:
    from urml_conformance import ConformanceRunner

    from urml_ardupilot_runtime import ArduCopterAdapter

    runner = ConformanceRunner(adapter_factory=lambda: ArduCopterAdapter())
    assert runner is not None
