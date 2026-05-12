"""Run the shipped conformance fixtures against URMLRuntime + MockROSAdapter.

The load-bearing test: every fixture YAML under ``conformance/fixtures/``
must pass via ``ConformanceRunner.run()``. The fixtures themselves are the
contract — they declare what URML-compatible behavior looks like for the
v0.1 surface.

This file also covers loader correctness (fixtures parse) and the
runner's diagnostic output on intentional failures.
"""

from __future__ import annotations

import pytest

from urml_conformance import (
    AdapterOverrides,
    ConformanceRunner,
    ExpectedExecution,
    ExpectedValidation,
    FixtureCase,
    discover_fixtures,
)

# ---------------------------------------------------------------------------
# Fixture loader smoke tests
# ---------------------------------------------------------------------------


def test_discover_fixtures_finds_the_shipped_set() -> None:
    cases = discover_fixtures()
    assert len(cases) >= 7
    names = [c.name for c in cases]
    # Every shipped case is uniquely named.
    assert len(set(names)) == len(names)


def test_every_fixture_parses_into_a_valid_case_model() -> None:
    for case in discover_fixtures():
        assert isinstance(case, FixtureCase)
        assert case.name
        assert case.manifest
        assert isinstance(case.profiles, list)
        assert "behavior" in case.program


# ---------------------------------------------------------------------------
# The headline test: every shipped fixture passes
# ---------------------------------------------------------------------------


def test_full_suite_passes_against_mock_runtime() -> None:
    runner = ConformanceRunner()
    report = runner.run()
    assert report.all_passed, "\n" + report.render()
    # Sanity: at least one of each category is exercised.
    names = [r.name for r in report.results]
    assert any("positive" in n for n in names)
    assert any("rejected" in n for n in names)
    assert any("branch" in n for n in names)
    assert any("retry" in n for n in names)
    assert any("parallel" in n for n in names)


def test_report_render_includes_pass_count() -> None:
    runner = ConformanceRunner()
    report = runner.run()
    text = report.render()
    assert "Conformance:" in text
    assert f"{report.passed_count}/" in text


# ---------------------------------------------------------------------------
# Per-fixture parametrized tests for clear pytest output
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", discover_fixtures(), ids=lambda c: c.name)
def test_fixture_individually_passes(case: FixtureCase) -> None:
    """One pytest entry per fixture so the runner output names what failed."""
    runner = ConformanceRunner(cases=[case])
    report = runner.run()
    assert report.all_passed, "\n" + report.render()


# ---------------------------------------------------------------------------
# Runner produces useful diagnostics on synthetic failures
# ---------------------------------------------------------------------------


def test_runner_diagnoses_expected_acceptance_mismatch() -> None:
    """A case whose `expected_validation.accepted` disagrees with reality is reported as failed."""
    case = FixtureCase(
        name="synthetic/should_fail",
        manifest="turtlebot4_home",
        envelope="home_default",
        profiles=["home"],
        program={
            "profile": "home",
            "behavior": {
                "type": "sequence",
                "steps": [{"move_to": {"location": "kitchen"}}],
            },
        },
        expected_validation=ExpectedValidation(accepted=False, error_codes=["argument.type"]),
        # No expected_execution -> validator-only.
    )
    runner = ConformanceRunner(cases=[case])
    report = runner.run()
    assert not report.all_passed
    result = report.results[0]
    assert any("accepted=True" in d for d in result.diagnostics)


def test_runner_diagnoses_audit_method_mismatch() -> None:
    """A case whose `audit_methods` doesn't match the actual run is flagged."""
    case = FixtureCase(
        name="synthetic/wrong_audit_methods",
        manifest="turtlebot4_home",
        envelope="home_default",
        profiles=["home"],
        program={
            "profile": "home",
            "behavior": {
                "type": "sequence",
                "steps": [{"move_to": {"location": "kitchen"}}],
            },
        },
        expected_execution=ExpectedExecution(
            success=True,
            steps_executed=1,
            audit_methods=["wait_passively"],  # wrong: a move_to triggers send_navigation_goal
        ),
    )
    runner = ConformanceRunner(cases=[case])
    report = runner.run()
    assert not report.all_passed
    diag_blob = " | ".join(report.results[0].diagnostics)
    assert "audit methods" in diag_blob


def test_runner_diagnoses_missing_binding() -> None:
    """When an expected binding key is absent, the runner says so."""
    case = FixtureCase(
        name="synthetic/missing_binding",
        manifest="turtlebot4_home",
        envelope="home_default",
        profiles=["home"],
        program={
            "profile": "home",
            "behavior": {
                "type": "sequence",
                "steps": [{"move_to": {"location": "kitchen"}}],
            },
        },
        expected_execution=ExpectedExecution(
            bindings_contains={"target_mug": {"class": "mug"}},
        ),
    )
    runner = ConformanceRunner(cases=[case])
    report = runner.run()
    assert not report.all_passed
    assert any("binding 'target_mug' missing" in d for d in report.results[0].diagnostics)


def test_runner_applies_adapter_overrides() -> None:
    """The adapter_overrides block actually drives MockROSAdapter setters."""
    from urml_ros2_runtime import NavigationResult

    case = FixtureCase(
        name="synthetic/overrides",
        manifest="turtlebot4_home",
        envelope="home_default",
        profiles=["home"],
        program={
            "profile": "home",
            "behavior": {
                "type": "sequence",
                "steps": [{"move_to": {"location": "kitchen"}}],
            },
        },
        adapter_overrides=AdapterOverrides(
            navigation=NavigationResult(success=False, reason="custom_failure_for_test"),
        ),
        expected_execution=ExpectedExecution(
            success=False,
            steps_executed=1,
            last_reason="custom_failure_for_test",
        ),
    )
    runner = ConformanceRunner(cases=[case])
    report = runner.run()
    assert report.all_passed, "\n" + report.render()
