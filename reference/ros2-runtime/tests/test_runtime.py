"""URMLRuntime behavior tests.

The load-bearing claim of this skeleton: the canonical red-mug example
from MANIFESTO.md executes end-to-end against the MockROSAdapter, with
the runtime dispatching every step through the adapter and threading
variable bindings between primitives.

Also covers:
- Defense-in-depth re-validation rejects bad programs.
- Per-step failures honored via `on_error`.
- Unsupported composition (Branch / Parallel / Retry) raises a clear error.
- Bindings produced by `detect` are available to later steps via `$ref`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from urml_ros2_runtime import (
    MockROSAdapter,
    NavigationResult,
    UnsupportedCompositionError,
    URMLRuntime,
    ValidationRejectedError,
)
from urml_ros2_runtime.substrate import DetectionResult

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"
EXAMPLES_ROOT = REPO_ROOT / "examples"


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture
def red_mug_program() -> dict[str, Any]:
    return _load(EXAMPLES_ROOT / "home" / "red-mug.urml.yaml")


@pytest.fixture
def home_manifest() -> dict[str, Any]:
    return _load(VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home.yaml")


@pytest.fixture
def home_envelope() -> dict[str, Any]:
    return _load(VALIDATOR_FIXTURES / "envelopes" / "home_default.yaml")


# ---------------------------------------------------------------------------
# End-to-end happy path
# ---------------------------------------------------------------------------


def test_red_mug_executes_end_to_end(
    red_mug_program: dict[str, Any],
    home_manifest: dict[str, Any],
    home_envelope: dict[str, Any],
) -> None:
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(
        red_mug_program,
        home_manifest,
        home_envelope,
        profiles=("home",),
    )

    assert result.success is True
    # red-mug has 5 steps: move_to(kitchen), detect(mug), grasp, move_to(user), release.
    assert result.steps_executed == 5

    methods = [entry["method"] for entry in result.audit_log]
    assert methods == [
        "send_navigation_goal",   # move_to kitchen
        "query_detection",        # detect mug
        "send_manipulation_goal", # grasp
        "send_navigation_goal",   # move_to user (carrying)
        "send_manipulation_goal", # release
    ]

    # `detect` produced a binding the runtime carried forward.
    assert "target_mug" in result.bindings
    assert result.bindings["target_mug"]["class"] == "mug"
    assert result.bindings["target_mug"]["attributes"] == {"color": "red"}

    # The grasp call referenced the stored binding by name.
    grasp_call = next(e for e in result.audit_log if e.get("action") == "grasp")
    assert grasp_call["target_ref"] == "$target_mug"


# ---------------------------------------------------------------------------
# Defense-in-depth re-validation
# ---------------------------------------------------------------------------


def test_runtime_rejects_invalid_program(home_manifest: dict[str, Any]) -> None:
    """A program that the validator would reject must not reach the substrate."""
    bad_program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"move_to": {"location": "the_moon"}}],
        },
    }
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    with pytest.raises(ValidationRejectedError) as excinfo:
        runtime.execute(bad_program, home_manifest)
    # The substrate was never touched.
    assert adapter.call_log == []
    # The structured ValidationResult is attached for diagnostics.
    vr = excinfo.value.validation_result
    assert vr.accepted is False


def test_revalidate_false_lets_substrate_see_unvalidated_input(
    red_mug_program: dict[str, Any],
    home_manifest: dict[str, Any],
) -> None:
    """The opt-out flag exists for deterministic test harnesses; covered for completeness."""
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter, revalidate=False)
    result = runtime.execute(red_mug_program, home_manifest)
    assert result.success is True
    assert adapter.call_log  # substrate was driven


# ---------------------------------------------------------------------------
# Per-step failure handling
# ---------------------------------------------------------------------------


def test_step_failure_with_abort_and_report_halts_sequence(
    red_mug_program: dict[str, Any],
    home_manifest: dict[str, Any],
    home_envelope: dict[str, Any],
) -> None:
    """If a step returns success=False, the runtime returns RuntimeResult(success=False)
    and stops further steps (red-mug's on_error is abort_and_report)."""
    adapter = MockROSAdapter()
    # Make the very first navigation fail.
    adapter.set_navigation_result(NavigationResult(success=False, reason="path_blocked"))
    runtime = URMLRuntime(adapter)
    result = runtime.execute(red_mug_program, home_manifest, home_envelope, profiles=("home",))

    assert result.success is False
    assert result.steps_executed == 1  # only the failing step ran
    # Substrate was called exactly once.
    assert len(result.audit_log) == 1
    assert result.last_outcome is not None
    assert result.last_outcome.success is False
    assert result.last_outcome.reason == "path_blocked"


def test_step_failure_with_continue_keeps_going() -> None:
    """on_error: continue lets a sequence absorb a failing step and move on."""
    adapter = MockROSAdapter()
    # Two move_to steps; first fails, second succeeds.
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "continue",
            "steps": [
                {"move_to": {"location": "kitchen"}},
                {"wait": {"duration": "1s"}},
            ],
        },
    }
    manifest = _load(VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home.yaml")
    # First call fails; subsequent default success.
    adapter.set_navigation_result(NavigationResult(success=False, reason="path_blocked"))
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, manifest, profiles=("home",))
    assert result.success is True
    assert result.steps_executed == 2
    assert [e["method"] for e in result.audit_log] == ["send_navigation_goal", "wait_passively"]


# ---------------------------------------------------------------------------
# Unsupported composition
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Branch
# ---------------------------------------------------------------------------


def test_branch_always_true_runs_if_true(home_manifest: dict[str, Any]) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "branch",
            "condition": "always",
            "if_true": {"wait": {"duration": "1s"}},
            "if_false": {"move_to": {"location": "kitchen"}},
        },
    }
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    assert [e["method"] for e in result.audit_log] == ["wait_passively"]


def test_branch_always_false_runs_if_false(home_manifest: dict[str, Any]) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "branch",
            "condition": "false",
            "if_true": {"wait": {"duration": "1s"}},
            "if_false": {"move_to": {"location": "kitchen"}},
        },
    }
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    assert [e["method"] for e in result.audit_log] == ["send_navigation_goal"]


def test_branch_condition_uses_prior_binding(home_manifest: dict[str, Any]) -> None:
    """detect binds $target_mug; the branch reads it via condition."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"detect": {"object": "mug", "store_as": "target_mug"}},
                {
                    "type": "branch",
                    "condition": "$target_mug.attributes.color == \"red\"",
                    "if_true": {"wait": {"duration": "1s"}},
                    "if_false": {"move_to": {"location": "kitchen"}},
                },
            ],
        },
    }
    # MockROSAdapter's default detection returns class+attributes echoed back.
    # `attributes` is {} by default; we override to inject `color: red`.
    adapter = MockROSAdapter()
    adapter.set_detection_result(
        DetectionResult(
            success=True,
            payload={
                "class": "mug",
                "pose": {"x": 0.0, "y": 0.0},
                "frame": "map",
                "attributes": {"color": "red"},
                "confidence": 0.95,
            },
        )
    )
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    methods = [e["method"] for e in result.audit_log]
    assert methods == ["query_detection", "wait_passively"]


def test_branch_missing_if_false_is_noop_skip(home_manifest: dict[str, Any]) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "branch",
            "condition": "false",
            "if_true": {"wait": {"duration": "1s"}},
        },
    }
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    assert result.audit_log == []


# ---------------------------------------------------------------------------
# Parallel
# ---------------------------------------------------------------------------


def test_parallel_all_succeeds_when_every_branch_succeeds(home_manifest: dict[str, Any]) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"wait": {"duration": "1s"}},
                {"wait": {"duration": "2s"}},
            ],
            "complete_when": "all",
        },
    }
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    assert len(result.audit_log) == 2


def test_parallel_all_fails_on_any_branch_failure(home_manifest: dict[str, Any]) -> None:
    """One failing branch in `complete_when: all` fails the parallel block."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"move_to": {"location": "kitchen"}},
                {"wait": {"duration": "1s"}},
            ],
            "complete_when": "all",
        },
    }
    adapter = MockROSAdapter()
    adapter.set_navigation_result(NavigationResult(success=False, reason="path_blocked"))
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert not result.success
    assert result.last_outcome is not None
    assert result.last_outcome.reason == "path_blocked"


def test_parallel_any_succeeds_when_at_least_one_branch_succeeds(home_manifest: dict[str, Any]) -> None:
    """First branch fails, second succeeds; `complete_when: any` => overall success."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"move_to": {"location": "kitchen"}},  # will fail
                {"wait": {"duration": "1s"}},          # will succeed
            ],
            "complete_when": "any",
        },
    }
    adapter = MockROSAdapter()
    adapter.set_navigation_result(NavigationResult(success=False, reason="path_blocked"))
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    assert result.last_outcome is not None
    assert result.last_outcome.reason == "parallel.any:1"


def test_parallel_any_fails_when_all_branches_fail(home_manifest: dict[str, Any]) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"move_to": {"location": "kitchen"}},
                {"move_to": {"location": "user"}},
            ],
            "complete_when": "any",
        },
    }
    adapter = MockROSAdapter()
    adapter.set_navigation_result(NavigationResult(success=False, reason="path_blocked"))
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert not result.success


def test_parallel_first_to_succeed_short_circuits(home_manifest: dict[str, Any]) -> None:
    """`first_to_succeed`: stop after the first successful branch."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"wait": {"duration": "1s"}},
                {"wait": {"duration": "2s"}},  # would also succeed, but we stop earlier
            ],
            "complete_when": "first_to_succeed",
        },
    }
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    # Only one branch ran.
    assert len(result.audit_log) == 1


# ---------------------------------------------------------------------------
# Retry
# ---------------------------------------------------------------------------


def test_retry_succeeds_on_first_attempt(home_manifest: dict[str, Any]) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "retry",
            "max_attempts": 3,
            "behavior": {"wait": {"duration": "1s"}},
        },
    }
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    # Only one wait was issued — no retry needed.
    assert len(result.audit_log) == 1


def test_retry_exhausts_attempts_on_persistent_failure(home_manifest: dict[str, Any]) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "retry",
            "max_attempts": 3,
            "behavior": {"move_to": {"location": "kitchen"}},
        },
    }
    adapter = MockROSAdapter()
    adapter.set_navigation_result(NavigationResult(success=False, reason="path_blocked"))
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert not result.success
    # Every attempt issued a substrate call.
    assert len(result.audit_log) == 3


def test_retry_until_condition_short_circuits_on_match(home_manifest: dict[str, Any]) -> None:
    """`until` lets retry stop based on a condition rather than success/failure."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "retry",
            "max_attempts": 5,
            "until": "$detected.confidence > 0.9",
            "behavior": {"detect": {"object": "mug", "store_as": "detected"}},
        },
    }
    adapter = MockROSAdapter()
    # Default detection's confidence is 0.95, so `until` is true on the first
    # pass and retry stops immediately.
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    assert len(result.audit_log) == 1


def test_retry_until_unsatisfied_after_max_attempts(home_manifest: dict[str, Any]) -> None:
    """`until` never matches; the retry exhausts and returns failure."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "retry",
            "max_attempts": 2,
            "until": "$detected.confidence > 99",  # never satisfied
            "behavior": {"detect": {"object": "mug", "store_as": "detected"}},
        },
    }
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert not result.success
    assert result.last_outcome is not None
    assert result.last_outcome.reason == "retry.until_unsatisfied_after_max_attempts"
    assert len(result.audit_log) == 2  # max_attempts attempts


# ---------------------------------------------------------------------------
# Genuinely unknown composition node
# ---------------------------------------------------------------------------


def test_unknown_composition_type_raises_unsupported(home_manifest: dict[str, Any]) -> None:
    """If the runtime sees a Behavior subclass it doesn't recognise, it raises a clear error.

    This test inserts a synthetic class (subclass of BaseModel that quacks
    like a behavior node) to confirm the catch-all path still works after
    Branch/Parallel/Retry became supported."""
    from pydantic import BaseModel

    from urml_ros2_runtime.runtime import URMLRuntime as _URMLRuntime

    class _FakeBehavior(BaseModel):
        type: str = "fake"

    # Directly invoke the internal walker to test the unsupported path
    # without faking a full URMLProgram model.
    runtime = _URMLRuntime(MockROSAdapter())
    with pytest.raises(UnsupportedCompositionError):
        runtime._exec_behavior(
            _FakeBehavior(),
            path=["behavior"],
            bindings={},
            steps_executed=0,
        )


# ---------------------------------------------------------------------------
# Bindings produced by other primitives surface to the runtime
# ---------------------------------------------------------------------------


def test_scan_binding_is_threaded_to_runtime_result(home_manifest: dict[str, Any]) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {
                    "scan": {
                        "area": {"named_region": "kitchen"},
                        "store_as": "kitchen_scan",
                    }
                },
            ],
        },
    }
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    assert "kitchen_scan" in result.bindings
    assert result.bindings["kitchen_scan"]["coverage"] == 1.0


def test_custom_detection_payload_flows_to_bindings(home_manifest: dict[str, Any]) -> None:
    adapter = MockROSAdapter()
    adapter.set_detection_result(
        DetectionResult(
            success=True,
            payload={
                "class": "mug",
                "pose": {"x": 0.5, "y": 0.0},
                "frame": "map",
                "attributes": {"color": "red", "tag": "ceramic-A1"},
                "confidence": 0.99,
            },
        )
    )
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"detect": {"object": "mug", "store_as": "the_mug"}},
            ],
        },
    }
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, home_manifest, profiles=("home",))
    assert result.success
    assert result.bindings["the_mug"]["attributes"]["tag"] == "ceramic-A1"
