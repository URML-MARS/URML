"""The OPC UA worked example must be deterministic and true.

Mirrors the fieldbus / VLA / world-model example guards: the generator is
deterministic, the committed ``method-mapping-report.txt`` matches it, and the
example demonstrates the one-URML-operation-to-one-OPC-UA-method grain that jpfr
gave on open62541#8077 (RFC-0313) and marcschier endorsed on
UA-.NETStandard#3827 (RFC-0314). Hermetic: the example injects a fake asyncua,
so no live OPC UA server and no [opcua] extra are needed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "opcua"
GEN_PATH = EX / "intent_to_methods.py"
COMMITTED = EX / "method-mapping-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("intent_to_methods", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic() -> None:
    gen = _load_gen()
    assert gen.render_report() == gen.render_report()


def test_committed_report_matches_generator() -> None:
    gen = _load_gen()
    assert COMMITTED.exists(), f"missing {COMMITTED}"
    assert COMMITTED.read_text(encoding="utf-8") == gen.render_report(), (
        "examples/opcua/method-mapping-report.txt is stale; "
        "run `python examples/opcua/intent_to_methods.py` and commit."
    )


def test_program_validates_and_grain_is_one_to_one() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # The gate passes before anything is called.
    assert "[VALID]" in report
    assert "[REJECTED]" not in report
    # Seven operations, seven method calls on the ObjectsNode, one each.
    assert "7 URML operations issued 7 method calls on i=85, one each:" in report
    assert "all 7 operations succeeded: True" in report
    # The RFC-0013 station-service and RFC-0015 call_program seams are present.
    assert "ns=2;s=SwapTool('wide')" in report
    assert "ns=2;s=PickPlaceCycle()" in report
