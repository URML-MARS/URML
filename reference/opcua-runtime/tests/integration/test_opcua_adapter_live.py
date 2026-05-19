"""Live smoke for OpcUaAdapter under a real ``asyncua`` install.

The OPC UA analog of the PX4 runtime's
``tests/integration/test_px4_adapter_live.py``. The *light* gate: it
needs only the real ``asyncua`` wheel. It constructs ``OpcUaAdapter``
(construction requires asyncua but does NOT connect — ``_connect`` is
lazy) and confirms the ``ConformanceRunner.adapter_factory`` hook
accepts it. A real-server end-to-end run against a local asyncua
demo server is the documented calibration step in
``opcua-integration.yml``.

## Gating

The default ``pytest`` invocation skips this module entirely. The
``opcua-smoke`` job in ``.github/workflows/opcua-integration.yml`` sets
``URML_OPCUA_INTEGRATION=1`` and runs it.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_OPCUA_INTEGRATION") != "1",
    reason="Set URML_OPCUA_INTEGRATION=1 to run the OPC UA live smoke (real asyncua, no server).",
)


def test_real_asyncua_is_importable() -> None:
    """The real asyncua sync client is available under the smoke env."""
    from asyncua.sync import Client  # noqa: F401


def test_adapter_constructs_against_real_asyncua() -> None:
    """OpcUaAdapter constructs against real asyncua without connecting.

    Construction calls ``_require_asyncua()`` (so it needs the real
    wheel) but must NOT open a session — ``_connect`` is lazy and only
    fires on the first Protocol call.
    """
    from urml_opcua_runtime import OpcUaAdapter

    with OpcUaAdapter() as adapter:
        assert adapter._client is None  # no Protocol method called -> no session


def test_conformance_runner_accepts_real_adapter_factory() -> None:
    """The ConformanceRunner accepts a real OpcUaAdapter factory.

    Does NOT run the fixture suite (that needs a live OPC UA server —
    the documented calibration step). The hook itself is under test.
    """
    from urml_conformance import ConformanceRunner

    from urml_opcua_runtime import OpcUaAdapter

    runner = ConformanceRunner(adapter_factory=lambda: OpcUaAdapter())
    assert runner is not None
