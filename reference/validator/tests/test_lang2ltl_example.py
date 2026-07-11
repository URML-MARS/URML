"""The Lang2LTL capability-gate example must be deterministic and true.

Mirrors the vitra / robotiq-hande guards. From a conversation with Prof. Tellex:
URML is the necessary-not-sufficient capability gate below an LTL task spec. The
example validates one pick-and-place action sequence three ways: admissible;
out-of-envelope (refused statically); and a self-declared gripper refused under a
policy that requires verified evidence (RFC-0631).
"""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "lang2ltl"
GEN_PATH = EX / "run_lang2ltl.py"
COMMITTED = EX / "lang2ltl-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_lang2ltl", GEN_PATH)
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
        "examples/lang2ltl/lang2ltl-report.txt is stale; "
        "run `python examples/lang2ltl/run_lang2ltl.py` and commit."
    )


def test_three_cases_decide_correctly() -> None:
    gen = _load_gen()
    from urml_validator import validate

    manifest = gen._load(gen.MANIFEST)
    policy = gen._load(gen.POLICY)

    # 1. Verified evidence + in-envelope grasp -> admissible.
    ok = validate(gen._task_program(60.0), manifest, profiles=gen._PROFILES, policy=policy)
    assert ok.accepted

    # 2. Out of the gripper's rated range -> refused statically (necessary check).
    over = validate(gen._task_program(250.0), manifest, profiles=gen._PROFILES, policy=policy)
    assert not over.accepted
    assert "envelope.force_exceeded" in {e.code_str for e in over.errors}

    # 3. Same admissible action, but the gripper is only self-declared -> refused
    #    under the verified-evidence policy (RFC-0631). Declared != actual.
    declared = copy.deepcopy(manifest)
    declared["manipulation"]["grippers"][0]["evidence"]["source"] = "declared"
    under = validate(gen._task_program(60.0), declared, profiles=gen._PROFILES, policy=policy)
    assert not under.accepted
    assert "policy.evidence_insufficient" in {e.code_str for e in under.errors}


def test_report_states_the_honest_boundary() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "necessary-not-sufficient" in report
    assert "policy.evidence_insufficient" in report
    assert "does not, and cannot, promise that an admissible action" in report
