"""Live smoke for MujocoAdapter under a real ``mujoco`` install.

The MuJoCo analog of the PX4 runtime's
``tests/integration/test_px4_adapter_live.py``. It is the *light*
gate: it needs only the real ``mujoco`` wheel installed. It constructs
``MujocoAdapter`` (construction requires mujoco but does NOT load a
model — ``_sim`` is lazy and only fires on the first Protocol call) and
confirms the ``ConformanceRunner.adapter_factory`` hook accepts it. No
MJCF model is loaded here; a model-driven end-to-end run is the
documented calibration step in ``mujoco-integration.yml``.

## Gating

The default ``pytest`` invocation skips this module entirely. The
``mujoco-smoke`` job in ``.github/workflows/mujoco-integration.yml``
sets ``URML_MUJOCO_INTEGRATION=1`` and runs it.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_MUJOCO_INTEGRATION") != "1",
    reason="Set URML_MUJOCO_INTEGRATION=1 to run the MuJoCo live smoke (real mujoco wheel, no model).",
)


def test_real_mujoco_is_importable() -> None:
    """The real mujoco module is available under the smoke env."""
    import mujoco  # noqa: F401


def test_adapter_constructs_against_real_mujoco() -> None:
    """MujocoAdapter constructs against real mujoco without loading a model.

    Construction calls ``_require_mujoco()`` (so it needs the real
    wheel) but must NOT load an MJCF model — ``_sim`` is lazy and only
    fires on the first Protocol call.
    """
    from urml_mujoco_runtime import MujocoAdapter

    with MujocoAdapter() as adapter:
        assert adapter._model is None  # no Protocol method called -> no model loaded


def test_conformance_runner_accepts_real_adapter_factory() -> None:
    """The ConformanceRunner accepts a real MujocoAdapter factory.

    Does NOT run the fixture suite (that needs a real MJCF model — the
    documented calibration step). The hook itself is under test; it must
    accept a real-adapter factory without raising.
    """
    from urml_conformance import ConformanceRunner

    from urml_mujoco_runtime import MujocoAdapter, MujocoConfig

    runner = ConformanceRunner(adapter_factory=lambda: MujocoAdapter(MujocoConfig(model_path="model.xml")))
    assert runner is not None
