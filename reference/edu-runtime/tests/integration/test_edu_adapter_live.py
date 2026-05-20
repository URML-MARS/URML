"""Live smoke for the edu-runtime adapters under real vendor SDKs.

Mirrors the cobot-runtime live-smoke gate. Needs the real
pyvex/pybricksdev/tdmclient wheels. Constructs each adapter (cheap;
``_open`` is lazy) and confirms ``ConformanceRunner.adapter_factory``
accepts them. A board-driven end-to-end run is the documented
calibration step in ``edu-integration.yml``.

## Gating

Default ``pytest`` skips this module. The ``edu-smoke`` job in
``.github/workflows/edu-integration.yml`` sets
``URML_EDU_INTEGRATION=1`` and runs it.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_EDU_INTEGRATION") != "1",
    reason="Set URML_EDU_INTEGRATION=1 to run the edu live smoke (real vendor SDKs, no board).",
)


def test_real_sdks_are_importable() -> None:
    """The real edu SDKs are available under the smoke env."""
    import pybricksdev  # noqa: F401
    import pyvex  # noqa: F401
    import tdmclient  # noqa: F401


def test_conformance_runner_accepts_real_adapter_factories() -> None:
    """ConformanceRunner accepts each real edu adapter factory."""
    from urml_conformance import ConformanceRunner

    from urml_edu_runtime import LegoSpikeAdapter, ThymioAdapter, VexV5Adapter

    for cls in (VexV5Adapter, LegoSpikeAdapter, ThymioAdapter):
        assert ConformanceRunner(adapter_factory=lambda c=cls: c()) is not None
