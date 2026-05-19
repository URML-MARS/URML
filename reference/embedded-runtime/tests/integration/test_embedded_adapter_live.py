"""Live smoke for EmbeddedAdapter under a real ``pyserial`` install.

The educational-MCU analog of the PX4 runtime's
``tests/integration/test_px4_adapter_live.py``. The *light* gate: it
needs only the real ``pyserial`` wheel. It opens the ``loop://``
loopback (no board) and confirms the ``ConformanceRunner.adapter_factory``
hook accepts the adapter. A real micro:bit/Arduino-driven run is the
documented calibration step in ``embedded-integration.yml``.

## Gating

The default ``pytest`` invocation skips this module entirely. The
``embedded-smoke`` job in ``.github/workflows/embedded-integration.yml``
sets ``URML_EMBEDDED_INTEGRATION=1`` and runs it.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_EMBEDDED_INTEGRATION") != "1",
    reason="Set URML_EMBEDDED_INTEGRATION=1 to run the embedded live smoke (real pyserial, loopback).",
)


def test_real_pyserial_is_importable() -> None:
    """The real pyserial module is available under the smoke env."""
    import serial  # noqa: F401


def test_adapter_opens_loopback_against_real_pyserial() -> None:
    """EmbeddedAdapter opens the real pyserial loop:// loopback (no board)."""
    from urml_embedded_runtime import EmbeddedAdapter, EmbeddedConfig

    with EmbeddedAdapter(EmbeddedConfig(port="loop://")) as buggy:
        assert buggy.wait_passively(duration_seconds=0.0).success  # forces a real _open()


def test_conformance_runner_accepts_real_adapter_factory() -> None:
    """The ConformanceRunner accepts a real EmbeddedAdapter factory."""
    from urml_conformance import ConformanceRunner

    from urml_embedded_runtime import EmbeddedAdapter

    runner = ConformanceRunner(adapter_factory=lambda: EmbeddedAdapter())
    assert runner is not None
