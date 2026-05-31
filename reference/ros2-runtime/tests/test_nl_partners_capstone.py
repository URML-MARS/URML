"""Guard: the NL -> fleet capstone (examples/fleet/run_nl_partners_demo.py) runs.

The full RFC-0286 loop: an English sentence -> FleetBridge -> concurrent
FleetRuntime over the four real partner robots. Skipped if the LLM bridge is not
installed in this environment (it lives in a separate package).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("urml_llm_bridge", reason="capstone needs the urml_llm_bridge package")

_DEMO = Path(__file__).resolve().parents[3] / "examples" / "fleet" / "run_nl_partners_demo.py"


def _load_demo():
    spec = importlib.util.spec_from_file_location("nl_partners_demo", _DEMO)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_capstone_runs_end_to_end():
    result = _load_demo().main(verbose=False)
    assert result.success
    assert result.steps_executed == 12
    assert set(result.per_member_audit) == {"marty", "petoi", "feather", "arm"}
