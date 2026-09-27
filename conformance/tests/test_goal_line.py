"""The goal-line lane: a program the validator rejects sends zero commands.

The main conformance run stops a rejected fixture at the validator. The goal
line hands every rejected fixture to the runtime itself and requires three
things: the runtime refuses, the refusal carries the fixture's expected codes,
and the recording adapter saw zero calls. The negative tests prove the lane
fails a runtime that leaks.
"""

from __future__ import annotations

from typing import Any

from urml_ros2_runtime import MockROSAdapter, URMLRuntime

from urml_conformance import (
    ExpectedValidation,
    FixtureCase,
    RecordingAdapter,
    discover_fixtures,
    run_goal_line,
)

# The three rejected compliance fixtures that still dispatched
# send_navigation_goal when the runtime re-validated under the default policy
# with no manifest directory.
_POLICY_FIXTURES = {
    "compliance/hbom_cn_chip_rejected",
    "compliance/hbom_vendor_of_vendor_rejected",
    "compliance/evidence_required_rejected",
}

# RFC-0702: the rejected rulebook fixtures refused by a rulebook the fixture
# loads. A runtime that drops the caller's rulebooks accepts them. (The other
# rejected rulebook fixtures rest on the bundled FAA rulebook, which a runtime
# that drops the keywords still applies by default.)
_CALLER_RULEBOOK_FIXTURES = {
    "rulebook/capture_in_no_camera_zone_rejected",
    "rulebook/restricted_zone_entry_rejected",
    "rulebook/remote_id_missing_rejected",
    "rulebook/policy_none_still_enforced_rejected",
    "rulebook/capture_at_unknown_place_rejected",
    "rulebook/call_program_not_allowlisted_rejected",
}


def test_every_rejected_fixture_is_refused_with_zero_adapter_calls() -> None:
    cases = discover_fixtures()
    rejected = [c.name for c in cases if not c.expected_validation.accepted]
    report = run_goal_line(cases)
    assert report.all_passed, "\n" + report.render()
    # The lane covers every rejected fixture and nothing else.
    assert sorted(r.name for r in report.results) == sorted(rejected)
    names = {r.name for r in report.results}
    assert _POLICY_FIXTURES <= names
    assert _CALLER_RULEBOOK_FIXTURES <= names
    assert "rulebook/two_aircraft_airborne_rejected" in names  # a fleet rulebook fixture
    assert any(n.startswith("fleet/") for n in names), "the fleet lane must be covered"


def test_the_lane_fails_a_runtime_that_skips_validation() -> None:
    report = run_goal_line(runtime_factory=lambda adapter: URMLRuntime(adapter, revalidate=False))
    assert not report.all_passed
    failed = {r.name: r.diagnostics for r in report.failed_cases()}
    assert _POLICY_FIXTURES <= set(failed)
    hbom = " ".join(failed["compliance/hbom_cn_chip_rejected"])
    assert "did not refuse" in hbom
    assert "adapter call(s)" in hbom and "send_navigation_goal" in hbom


class _DefaultPolicyRuntime:
    """The runtime before the fix: re-validates, but drops the caller's policy."""

    def __init__(self, adapter: Any) -> None:
        self._runtime = URMLRuntime(adapter)

    def execute(
        self,
        program: Any,
        manifest: Any,
        envelope: Any = None,
        profiles: tuple[str, ...] = (),
        **_dropped: Any,
    ) -> Any:
        return self._runtime.execute(program, manifest, envelope, profiles)


def test_the_lane_fails_a_runtime_that_drops_the_policy() -> None:
    """The three policy fixtures leak through a runtime that drops its keywords,
    and so do the rulebook fixtures that load their own rulebooks."""
    report = run_goal_line(runtime_factory=_DefaultPolicyRuntime)
    assert {r.name for r in report.failed_cases()} == _POLICY_FIXTURES | _CALLER_RULEBOOK_FIXTURES


class _DropsRulebooksRuntime:
    """A runtime that keeps the policy but re-validates with the bundled rulebooks only."""

    def __init__(self, adapter: Any) -> None:
        self._runtime = URMLRuntime(adapter)

    def execute(
        self,
        program: Any,
        manifest: Any,
        envelope: Any = None,
        profiles: tuple[str, ...] = (),
        *,
        policy: Any = "DEFAULT",
        manifest_base_dir: Any = None,
        **_dropped: Any,
    ) -> Any:
        return self._runtime.execute(
            program, manifest, envelope, profiles, policy=policy, manifest_base_dir=manifest_base_dir
        )


def test_the_lane_fails_a_runtime_that_drops_the_rulebooks() -> None:
    """RFC-0702: a runtime re-check that drops the caller's rulebooks sends commands."""
    report = run_goal_line(runtime_factory=_DropsRulebooksRuntime)
    failed = {r.name: r.diagnostics for r in report.failed_cases()}
    assert set(failed) == _CALLER_RULEBOOK_FIXTURES
    zone = " ".join(failed["rulebook/restricted_zone_entry_rejected"])
    assert "did not refuse" in zone and "send_navigation_goal" in zone


def test_the_lane_requires_the_expected_codes() -> None:
    """A refusal for some other reason is not enough."""
    case = FixtureCase.model_validate(
        {
            "name": "synthetic/wrong_code",
            "manifest": "turtlebot4_home",
            "policy": "none",
            "profiles": ["home"],
            "program": {
                "profile": "home",
                "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "the_moon"}}]},
            },
            "expected_validation": ExpectedValidation(
                accepted=False, error_codes=["envelope.velocity_exceeded"]
            ).model_dump(),
        }
    )
    report = run_goal_line([case])
    assert not report.all_passed
    assert "expected error codes" in report.results[0].diagnostics[0]


def test_the_lane_skips_accepted_fixtures() -> None:
    accepted = [c for c in discover_fixtures() if c.expected_validation.accepted][:3]
    assert run_goal_line(accepted).results == []


def test_recording_adapter_answers_capability_checks_statically() -> None:
    """Python 3.12+ checks runtime Protocols with inspect.getattr_static, which
    skips __getattr__. The proxy binds its methods up front so those checks see
    the same capabilities the wrapped adapter has, on every Python version."""
    import inspect

    from urml_ros2_runtime.substrate.base import RelativeMotionAdapter, ROSAdapter

    recorder = RecordingAdapter(MockROSAdapter())
    for name in ("send_navigation_goal", "drive_by", "turn_by", "sample_signals"):
        inspect.getattr_static(recorder, name)  # AttributeError if not bound
    assert isinstance(recorder, ROSAdapter)
    assert isinstance(recorder, RelativeMotionAdapter)
    assert recorder.calls == []  # binding is not calling


def test_recording_adapter_records_calls_and_forwards_them() -> None:
    inner = MockROSAdapter()
    recorder = RecordingAdapter(inner)
    result = recorder.send_navigation_goal(location="kitchen")
    assert result.success is True
    assert [c.method for c in recorder.calls] == ["send_navigation_goal"]
    assert recorder.calls[0].kwargs == {"location": "kitchen"}
    # The call reached the wrapped adapter; plain attribute reads are not calls.
    assert recorder.call_log is inner.call_log
    assert len(inner.call_log) == 1
    assert len(recorder.calls) == 1
