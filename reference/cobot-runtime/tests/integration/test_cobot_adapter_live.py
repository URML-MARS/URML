"""Live smoke for the cobot adapters under real vendor SDKs.

The cobot analog of the PX4 runtime's
``tests/integration/test_px4_adapter_live.py``. The *light* gate: it
needs the real ``ur_rtde`` / ``panda-python`` wheels. It constructs the
adapters (construction is cheap; the vendor connection is lazy in
``_open``) and confirms the ``ConformanceRunner.adapter_factory`` hook
accepts them. A real-controller end-to-end run is the documented
calibration step in ``cobot-integration.yml`` (it needs a UR
controller / a Franka with FCI enabled).

## Gating

The default ``pytest`` invocation skips this module entirely. The
``cobot-smoke`` job in ``.github/workflows/cobot-integration.yml`` sets
``URML_COBOT_INTEGRATION=1`` and runs it.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_COBOT_INTEGRATION") != "1",
    reason="Set URML_COBOT_INTEGRATION=1 to run the cobot live smoke (real vendor SDKs, no controller).",
)


def test_real_sdks_are_importable() -> None:
    """The real vendor SDKs are available under the smoke env."""
    import panda_py  # noqa: F401
    import rtde_control  # noqa: F401
    import rtde_receive  # noqa: F401


def test_conformance_runner_accepts_real_adapter_factories() -> None:
    """The ConformanceRunner accepts real cobot adapter factories.

    Does NOT run the fixture suite (that needs a UR controller / a
    Franka with FCI — the documented calibration step). Construction is
    lazy, so this does not contact any robot.
    """
    from urml_conformance import ConformanceRunner

    from urml_cobot_runtime import FrankaFciAdapter, UrRtdeAdapter

    assert ConformanceRunner(adapter_factory=lambda: UrRtdeAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: FrankaFciAdapter()) is not None
