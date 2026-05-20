"""Live smoke for AutosarAdaptiveAdapter under a real ``ara`` install.

The AUTOSAR Adaptive analog of the PX4 runtime's
``tests/integration/test_px4_adapter_live.py``. The *light* gate: it
needs only the real ``ara`` wheel. It constructs ``AutosarAdaptiveAdapter``
(construction requires ara but does NOT connect — ``_connect`` is
lazy) and confirms the ``ConformanceRunner.adapter_factory`` hook
accepts it. A real-server end-to-end run against a local ara
demo server is the documented calibration step in
``autosar-integration.yml``.

## Gating

The default ``pytest`` invocation skips this module entirely. The
``autosar-smoke`` job in ``.github/workflows/autosar-integration.yml`` sets
``URML_AUTOSAR_INTEGRATION=1`` and runs it.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_AUTOSAR_INTEGRATION") != "1",
    reason="Set URML_AUTOSAR_INTEGRATION=1 to run the AUTOSAR Adaptive live smoke (real ara, no server).",
)


def test_real_ara_is_importable() -> None:
    """The real ara sync client is available under the smoke env."""
    from ara.sync import Client  # noqa: F401


def test_adapter_constructs_against_real_ara() -> None:
    """AutosarAdaptiveAdapter constructs against real ara without connecting.

    Construction calls ``_require_ara()`` (so it needs the real
    wheel) but must NOT open a session — ``_connect`` is lazy and only
    fires on the first Protocol call.
    """
    from urml_autosar_runtime import AutosarAdaptiveAdapter

    with AutosarAdaptiveAdapter() as adapter:
        assert adapter._client is None  # no Protocol method called -> no session


def test_conformance_runner_accepts_real_adapter_factory() -> None:
    """The ConformanceRunner accepts a real AutosarAdaptiveAdapter factory.

    Does NOT run the fixture suite (that needs a live AUTOSAR Adaptive server —
    the documented calibration step). The hook itself is under test.
    """
    from urml_conformance import ConformanceRunner

    from urml_autosar_runtime import AutosarAdaptiveAdapter

    runner = ConformanceRunner(adapter_factory=lambda: AutosarAdaptiveAdapter())
    assert runner is not None
