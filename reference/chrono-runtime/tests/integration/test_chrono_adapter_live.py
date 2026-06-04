"""Live smoke for ChronoAdapter under a real ``pychrono`` install.

The Chrono analog of the MuJoCo runtime's
``tests/integration/test_mujoco_adapter_live.py``. It is the *light*
gate: it needs only a real ``pychrono`` (from conda-forge). It
constructs ``ChronoAdapter`` (construction requires pychrono but does
NOT build a ``ChSystem`` — ``_sim`` is lazy and only fires on the first
Protocol call) and confirms the ``ConformanceRunner.adapter_factory``
hook accepts it. No Chrono::Vehicle scene is built here; a
terramechanics-driven end-to-end run is the documented calibration step
in ``chrono-integration.yml``.

## Gating

The default ``pytest`` invocation skips this module entirely. The
``chrono-smoke`` job in ``.github/workflows/chrono-integration.yml``
sets ``URML_CHRONO_INTEGRATION=1`` and runs it.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_CHRONO_INTEGRATION") != "1",
    reason="Set URML_CHRONO_INTEGRATION=1 to run the Chrono live smoke (real pychrono, no scene).",
)


def test_real_pychrono_is_importable() -> None:
    """The real pychrono module is available under the smoke env."""
    import pychrono  # noqa: F401


def test_adapter_constructs_against_real_pychrono() -> None:
    """ChronoAdapter constructs against real pychrono without building a system.

    Construction calls ``_require_pychrono()`` (so it needs the real
    package) but must NOT build a ``ChSystem`` — ``_sim`` is lazy and
    only fires on the first Protocol call.
    """
    from urml_chrono_runtime import ChronoAdapter

    with ChronoAdapter() as adapter:
        assert adapter._system is None  # no Protocol method called -> no system built


def test_conformance_runner_accepts_real_adapter_factory() -> None:
    """The ConformanceRunner accepts a real ChronoAdapter factory.

    Does NOT run the fixture suite (that needs a real Chrono::Vehicle
    scene — the documented calibration step). The hook itself is under
    test; it must accept a real-adapter factory without raising.
    """
    from urml_conformance import ConformanceRunner

    from urml_chrono_runtime import ChronoAdapter, ChronoConfig

    runner = ConformanceRunner(adapter_factory=lambda: ChronoAdapter(ChronoConfig()))
    assert runner is not None
