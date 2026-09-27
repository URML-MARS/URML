"""Conformance fixture support for rulebooks (RFC-0702, Draft).

`FixtureCase` gains `rulebooks` (names in RULEBOOK_REGISTRY),
`default_rulebooks` and `as_of`; `ExpectedValidation` gains `warning_codes`,
so a fixture can pin a violation an exception turned into a warning. The
runner threads the three fields through validate, validate_fleet and the
runtimes.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from urml_conformance import (
    RULEBOOK_REGISTRY,
    ConformanceRunner,
    ExpectedValidation,
    FixtureCase,
    discover_fixtures,
    resolve_rulebook,
)
from urml_conformance.fixtures import rulebook_kwargs

_FLIGHT_450 = {
    "profile": "drone",
    "behavior": {"type": "sequence", "steps": [{"take_off": {"altitude": 137.16}}, {"land": {}}]},
}


def _case(**fields: object) -> FixtureCase:
    data: dict[str, object] = {
        "name": "synthetic/rulebook",
        "manifest": "drone_high_ceiling",
        "policy": "none",
        "profiles": ["drone"],
        "program": _FLIGHT_450,
    }
    data.update(fields)
    return FixtureCase.model_validate(data)


def test_the_rulebook_lane_ships_every_planned_case() -> None:
    names = {c.name for c in discover_fixtures() if c.name.startswith("rulebook/")}
    assert {
        "rulebook/take_off_450ft_rejected",
        "rulebook/take_off_450ft_waiver_accepted",
        "rulebook/capture_in_no_camera_zone_rejected",
        "rulebook/restricted_zone_entry_rejected",
        "rulebook/remote_id_missing_rejected",
        "rulebook/two_aircraft_airborne_rejected",
        "rulebook/policy_none_still_enforced_rejected",
        "rulebook/default_rulebooks_off_accepted",
    } <= names


def test_every_registered_rulebook_resolves() -> None:
    for name in RULEBOOK_REGISTRY:
        assert resolve_rulebook(name)["rulebook_id"]
    with pytest.raises(KeyError, match="unknown rulebook"):
        resolve_rulebook("nope")


def test_the_three_fields_default_to_the_validator_defaults() -> None:
    case = _case()
    assert (case.rulebooks, case.default_rulebooks, case.as_of) == ([], True, None)
    assert not case.uses_rulebook_fields
    assert rulebook_kwargs(case) == {"rulebooks": [], "default_rulebooks": True, "as_of": None}
    assert _case(default_rulebooks=False).uses_rulebook_fields


def test_as_of_is_an_iso_date() -> None:
    assert str(_case(as_of="2026-09-26").as_of_date) == "2026-09-26"
    with pytest.raises(ValidationError):
        _case(as_of="next tuesday")


def test_warning_codes_are_checked() -> None:
    passing = _case(
        rulebooks=["example_deployment"],
        as_of="2026-09-26",
        expected_validation=ExpectedValidation(accepted=True, warning_codes=["rule.cap_exceeded"]).model_dump(),
    )
    assert ConformanceRunner(cases=[passing]).run().all_passed
    missing = _case(
        expected_validation=ExpectedValidation(
            accepted=False, error_codes=["rule.cap_exceeded"], warning_codes=["rule.defaults_disabled"]
        ).model_dump(),
    )
    report = ConformanceRunner(cases=[missing]).run()
    assert not report.all_passed
    assert "expected warning codes" in report.results[0].diagnostics[0]


def test_an_unknown_rulebook_name_is_a_fixture_load_error() -> None:
    report = ConformanceRunner(cases=[_case(rulebooks=["nope"])]).run()
    assert "fixture-load error" in report.results[0].diagnostics[0]
