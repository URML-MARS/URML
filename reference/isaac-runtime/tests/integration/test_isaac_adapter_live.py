"""Live smoke for IsaacAdapter under a real ``isaacsim`` install.

The Isaac analog of the PX4 runtime's
``tests/integration/test_px4_adapter_live.py``. It is the *light*
gate: it needs only the real ``isaacsim`` wheel installed. It constructs
``IsaacAdapter`` (construction requires isaacsim but does NOT load a
model — ``_sim`` is lazy and only fires on the first Protocol call) and
confirms the ``ConformanceRunner.adapter_factory`` hook accepts it. No
MJCF model is loaded here; a model-driven end-to-end run is the
documented calibration step in ``isaacsim-integration.yml``.

## Gating

The default ``pytest`` invocation skips this module entirely. The
``isaacsim-smoke`` job in ``.github/workflows/isaacsim-integration.yml``
sets ``URML_ISAAC_INTEGRATION=1`` and runs it.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_ISAAC_INTEGRATION") != "1",
    reason="Set URML_ISAAC_INTEGRATION=1 to run the Isaac live smoke (real isaacsim wheel, no model).",
)


def test_real_isaacsim_is_importable() -> None:
    """The real isaacsim module is available under the smoke env."""
    import isaacsim  # noqa: F401


def test_adapter_constructs_against_real_isaacsim() -> None:
    """IsaacAdapter constructs against real isaacsim without loading a model.

    Construction calls ``_require_isaacsim()`` (so it needs the real
    wheel) but must NOT load an MJCF model — ``_sim`` is lazy and only
    fires on the first Protocol call.
    """
    from urml_isaac_runtime import IsaacAdapter

    with IsaacAdapter() as adapter:
        assert adapter._model is None  # no Protocol method called -> no model loaded


def test_conformance_runner_accepts_real_adapter_factory() -> None:
    """The ConformanceRunner accepts a real IsaacAdapter factory.

    Does NOT run the fixture suite (that needs a real MJCF model — the
    documented calibration step). The hook itself is under test; it must
    accept a real-adapter factory without raising.
    """
    from urml_conformance import ConformanceRunner

    from urml_isaac_runtime import IsaacAdapter, IsaacConfig

    runner = ConformanceRunner(adapter_factory=lambda: IsaacAdapter(IsaacConfig(model_path="model.xml")))
    assert runner is not None
