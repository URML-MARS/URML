"""The rulebook pass (RFC-0702, Draft; spec/layer-1-hal/rulebook.md).

Covers the file format (schemas/rulebook.py), the bundled FAA rulebook, each
rule kind, place tracking and the fail-closed zone checks, deployment
declarations and exceptions, loading, applicability, the detail payload and
the validation report. The conformance fixtures under
conformance/fixtures/rulebook/ pin the same behavior for any runtime.
"""

from __future__ import annotations

import copy
import datetime
import json
import typing
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError as PydanticValidationError

from urml_validator import ErrorCode, ValidationResult, validate, validate_fleet
from urml_validator.rulebook_engine import bundled_rulebooks
from urml_validator.schema_export import export_schema
from urml_validator.schemas.composition import _PRIMITIVE_FIELDS
from urml_validator.schemas.manifest import Mobility
from urml_validator.schemas.rulebook import DriveType, PrimitiveName, Rulebook

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).parent / "fixtures"
EXAMPLES = REPO_ROOT / "examples" / "rulebooks"
BUNDLED_DIR = REPO_ROOT / "reference" / "validator" / "src" / "urml_validator" / "rulebooks"

THE_450_FT_MESSAGE = (
    "14 CFR 107.51(b): maximum altitude 400 feet (121.92 m) above ground level. "
    "take_off.altitude is 137.16 m; the limit is 121.92 m."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _faa() -> dict[str, Any]:
    return _yaml(BUNDLED_DIR / "us_faa_part107.yaml")


def _warehouse_rulebook() -> dict[str, Any]:
    return _yaml(EXAMPLES / "example-warehouse.yaml")


def _waiver() -> dict[str, Any]:
    return _yaml(EXAMPLES / "example-deployment.yaml")


def _drone(**mobility: Any) -> dict[str, Any]:
    manifest = _yaml(FIXTURES / "manifests" / "drone_high_ceiling.yaml")
    manifest["mobility"].update(mobility)
    return manifest


def _warehouse() -> dict[str, Any]:
    return _yaml(FIXTURES / "manifests" / "warehouse_areas.yaml")


def _square(x: float, y: float, size: float = 4.0) -> list[dict[str, float]]:
    return [
        {"x": x, "y": y},
        {"x": x + size, "y": y},
        {"x": x + size, "y": y + size},
        {"x": x, "y": y + size},
    ]


def _ground() -> dict[str, Any]:
    """A ground robot with every capability the step-level tests use.

    Frames: `map` is the root; `office` hangs off it, shifted +100 m in x;
    `island` is a second root that no transform connects to `map`.
    """
    return {
        "manifest_version": "0.1",
        "robot_id": "tester",
        "frames": [
            {"name": "map"},
            {"name": "office", "parent": "map", "transform": {"translation": {"x": 100.0}}},
            {"name": "island"},
        ],
        "declared_locations": [
            {"name": "desk", "pose": {"x": 1.0, "y": 1.0}, "frame": "map"},
            {"name": "vault_door", "pose": {"x": 20.0, "y": 2.0}, "frame": "map"},  # on the vault's edge
            {"name": "lobby", "pose": {"x": 50.0, "y": 50.0}, "frame": "map"},
            {"name": "islet", "pose": {"x": 0.0, "y": 0.0}, "frame": "island"},
            {"name": "home", "pose": {"x": 0.0, "y": 0.0}, "frame": "map"},
        ],
        "declared_areas": [
            {"name": "vault", "frame": "map", "polygon": _square(20.0, 0.0)},
            {"name": "hall", "frame": "map", "polygon": _square(18.0, -2.0, 3.0)},  # overlaps the vault's corner
            {"name": "lab", "frame": "office", "polygon": _square(0.0, 0.0)},  # map x 100..104
        ],
        "mobility": {"drive_type": "differential", "max_velocity": 2.0, "supports_relative_motion": True},
        "manipulation": {
            "arm_count": 2,
            "grippers": [
                {"name": "hand", "kind": "servo_electric", "force_min_n": 0.5, "force_max_n": 40.0},
            ],
        },
        "perception": {
            "cameras": [{"name": "cam", "movable": True, "supports_photo": True, "supports_video": True}],
            "sensors": [{"name": "mic", "measurement_type": "speech"}],
            "object_vocabulary": ["box"],
        },
        "programs": [{"name": "safe_job"}, {"name": "risky_job"}],
        "outputs": {
            "named_endpoints": ["speech"],
            "lines": [
                {"name": "lamp", "kind": "digital", "safe_state": False},
                {"name": "muting", "kind": "digital", "safe_state": False},
            ],
        },
        "docking_stations": [
            {"name": "bay", "pose": {"x": 21.0, "y": 1.0}, "frame": "map", "services": ["park", "swap_tool"]},
        ],
    }


def _program(*steps: dict[str, Any], profile: str | list[str] = "drone") -> dict[str, Any]:
    return {"profile": profile, "behavior": {"type": "sequence", "steps": list(steps)}}


def _org(*rules: dict[str, Any], rulebook_id: str = "acme_rules", **extra: Any) -> dict[str, Any]:
    book: dict[str, Any] = {
        "rulebook_version": "0.1",
        "rulebook_id": rulebook_id,
        "title": "Acme robot rules",
        "issuer": {"kind": "organization", "name": "Acme"},
        "source_status": "organization_policy",
        "rules": list(rules),
    }
    book.update(extra)
    return book


def _rule(rule_id: str, kind: str, body: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {"id": rule_id, "title": f"Rule {rule_id}", "cite": {"text": f"Acme policy {rule_id}"}, kind: body, **extra}


def _deploy(
    declarations: dict[str, Any] | None = None,
    exceptions: list[dict[str, Any]] | None = None,
    rulebook_id: str = "acme_site",
) -> dict[str, Any]:
    book: dict[str, Any] = {
        "rulebook_version": "0.1",
        "rulebook_id": rulebook_id,
        "title": "Acme site",
        "issuer": {"kind": "deployment", "name": "Acme"},
        "source_status": "deployment_declaration",
    }
    if declarations is not None:
        book["declarations"] = declarations
    if exceptions is not None:
        book["exceptions"] = exceptions
    return book


def _people_envelope(*zones: tuple[str, float, float, float, bool]) -> dict[str, Any]:
    return {
        "people_occupancy_zones": [
            {
                "name": name,
                "frame": "agl",
                "vertices": [[x, y], [x + size, y], [x + size, y + size], [x, y + size]],
                "allow_override": override,
            }
            for name, x, y, size, override in zones
        ]
    }


def _issues(result: ValidationResult, code: str) -> list[Any]:
    return [i for i in result.all_issues if i.code_str == code]


def _rule_issues(result: ValidationResult) -> list[tuple[str, str]]:
    return [(i.code_str, i.severity) for i in result.all_issues if i.code_str.startswith("rule.")]


def _parse_error(data: dict[str, Any]) -> str:
    with pytest.raises(PydanticValidationError) as exc:
        Rulebook.model_validate(data)
    return str(exc.value)


# ---------------------------------------------------------------------------
# The file format
# ---------------------------------------------------------------------------


class TestFormat:
    def test_the_shipped_files_load_and_the_template_does_not(self) -> None:
        for data in (_faa(), _warehouse_rulebook(), _waiver()):
            Rulebook.model_validate(data)
        message = _parse_error(_yaml(EXAMPLES / "industrial-template.yaml"))
        assert "rulebook_id" in message and "max" in message

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda b: b.update({"extra": 1}),
            lambda b: b["issuer"].update({"extra": 1}),
            lambda b: b["rules"][0].update({"extra": 1}),
            lambda b: b["rules"][0]["cap"].update({"extra": 1}),
            lambda b: b["obligations"][0]["cite"].update({"extra": 1}),
        ],
        ids=["top", "issuer", "rule", "cap", "cite"],
    )
    def test_unknown_keys_are_rejected_at_every_level(self, mutate: Any) -> None:
        book = _faa()
        mutate(book)
        assert "Extra inputs are not permitted" in _parse_error(book)

    def test_issuer_and_source_status_agree(self) -> None:
        book = _faa()
        book["source_status"] = "organization_policy"
        assert "a government rulebook has source_status" in _parse_error(book)

    def test_there_is_no_status_for_a_proposed_rule(self) -> None:
        book = _faa()
        book["source_status"] = "proposed_rule"
        _parse_error(book)

    def test_a_deployment_rulebook_carries_only_declarations_and_exceptions(self) -> None:
        book = _deploy({"remote_id": "broadcast_module"})
        book["rules"] = []
        assert "carries only declarations and exceptions" in _parse_error(book)
        org = _org(declarations={"indoor": True})
        assert "only a deployment rulebook carries declarations" in _parse_error(org)

    def test_government_rulebooks_cite_with_a_url_and_carry_reviewed(self) -> None:
        book = _faa()
        del book["rules"][0]["cite"]["url"]
        assert "missing on altitude_400ft_agl" in _parse_error(book)
        book = _faa()
        del book["reviewed"]
        assert "carries reviewed" in _parse_error(book)
        book = _faa()
        del book["issuer"]["jurisdiction"]
        assert "jurisdiction" in _parse_error(book)

    def test_rule_and_obligation_ids_share_one_namespace(self) -> None:
        book = _faa()
        book["obligations"][0]["id"] = "altitude_400ft_agl"
        assert "duplicated: altitude_400ft_agl" in _parse_error(book)

    def test_a_rule_carries_exactly_one_kind(self) -> None:
        none = _org({"id": "r", "title": "t"})
        assert "got none" in _parse_error(none)
        two = _org(_rule("r", "cap", {"quantity": "grip_force_n", "max": 5}, forbid_zone_entry={"zones": ["z"]}))
        assert "got cap, forbid_zone_entry" in _parse_error(two)
        null = _org({"id": "r", "title": "t", "forbid_over_people": None})
        assert "write {} when it has no keys" in _parse_error(null)
        Rulebook.model_validate(_org({"id": "r", "title": "t", "forbid_over_people": {}}))

    def test_name_filters(self) -> None:
        both = _org(_rule("r", "forbid_primitive", {"primitives": ["gesture"], "names": ["wave"], "except_names": ["nod"]}))
        assert "mutually exclusive" in _parse_error(both)
        unnamed = _org(_rule("r", "forbid_primitive", {"primitives": ["capture"], "names": ["x"]}))
        assert "capture has none" in _parse_error(unnamed)
        empty = _org(_rule("r", "forbid_primitive", {"primitives": ["set_output"], "names": []}))
        assert "non-empty" in _parse_error(empty)

    def test_max_concurrent_aircraft_takes_exactly_one_limit(self) -> None:
        for body in ({}, {"max": 1, "max_per_remote_pilot": 1}):
            assert "exactly one of max" in _parse_error(_org(_rule("r", "max_concurrent_aircraft", body)))
        _parse_error(_org(_rule("r", "max_concurrent_aircraft", {"max": 0})))
        _parse_error(_org(_rule("r", "max_concurrent_aircraft", {"max": True})))

    def test_numbers_are_strict(self) -> None:
        for bad in (True, "5", -1, float("nan")):
            _parse_error(_org(_rule("r", "cap", {"quantity": "grip_force_n", "max": bad})))
        Rulebook.model_validate(_org(_rule("r", "cap", {"quantity": "grip_force_n", "max": 5})))

    def test_dates_are_quoted_iso_strings(self) -> None:
        book = _faa()
        book["reviewed"] = datetime.date(2026, 9, 26)
        assert "quoted string" in _parse_error(book)
        book["reviewed"] = "2026-02-30"
        _parse_error(book)
        book["reviewed"] = "26 Sep 2026"
        assert "ISO-8601" in _parse_error(book)

    def test_declarations_are_strings_integers_or_booleans(self) -> None:
        Rulebook.model_validate(_deploy({"a": "x", "b": 2, "c": True}))
        _parse_error(_deploy({"a": 1.5}))
        _parse_error(_deploy({"Bad-Key": 1}))

    def test_exceptions_name_a_rule_and_a_basis(self) -> None:
        _parse_error(_deploy(exceptions=[{"rule": "no_slash", "basis": "x"}]))
        _parse_error(_deploy(exceptions=[{"rule": "a/b", "basis": "   "}]))
        _parse_error(_deploy(exceptions=[{"rule": "a/b", "basis": "x", "limit": -1}]))
        Rulebook.model_validate(_deploy(exceptions=[{"rule": "a/b", "basis": "x", "limit": 3, "expires": "2027-01-01"}]))

    def test_the_drive_type_list_matches_the_manifest(self) -> None:
        manifest_types = typing.get_args(Mobility.model_fields["drive_type"].annotation)
        assert set(typing.get_args(DriveType)) == set(manifest_types)

    def test_the_primitive_list_matches_the_step_fields(self) -> None:
        assert list(typing.get_args(PrimitiveName)) == list(_PRIMITIVE_FIELDS)

    def test_bundled_rulebooks_meet_the_bundled_invariants(self) -> None:
        books = bundled_rulebooks()
        assert [b.rulebook_id for b in books] == ["us_faa_part107"]
        for book in books:
            assert book.issuer.kind == "government"
            assert book.source_status in {"final_rule", "enacted_statute"}
            assert book.reviewed is not None
            assert book.applies_to is not None
            for entry in [*book.rules, *book.obligations]:
                assert entry.cite is not None and entry.cite.url

    def test_the_faa_rulebook_has_five_rules_and_seven_obligations(self) -> None:
        (book,) = bundled_rulebooks()
        assert [(r.id, r.kind, r.exceptable) for r in book.rules] == [
            ("altitude_400ft_agl", "cap", True),
            ("groundspeed_100mph", "cap", True),
            ("over_human_beings", "forbid_over_people", True),
            ("one_aircraft_per_pilot", "max_concurrent_aircraft", True),
            ("remote_identification", "require_declared", True),
        ]
        assert len(book.obligations) == 7

    def test_the_schema_exports(self) -> None:
        schema = export_schema("rulebook")
        assert schema["$id"].endswith("urml-rulebook.schema.json")
        assert {"rulebook_version", "rulebook_id", "issuer", "rules"} <= set(schema["properties"])


# ---------------------------------------------------------------------------
# The bundled FAA rulebook, on by default
# ---------------------------------------------------------------------------


class TestBundledFaa:
    def test_a_450_foot_take_off_is_refused_with_the_citation(self) -> None:
        result = validate(_program({"take_off": {"altitude": 137.16}}), _drone(), policy=None)
        assert not result.accepted
        (issue,) = _issues(result, "rule.cap_exceeded")
        assert issue.message == THE_450_FT_MESSAGE
        assert issue.severity == "error"
        assert issue.primitive == "take_off"
        assert issue.path == ["behavior", "steps", "0"]
        assert issue.field == "altitude"
        detail = issue.detail
        assert detail["rulebook_id"] == "us_faa_part107"
        assert detail["rule_id"] == "altitude_400ft_agl"
        assert detail["rule_kind"] == "cap"
        assert detail["cite"]["text"] == "14 CFR 107.51(b)"
        assert detail["cite"]["url"].startswith("https://www.ecfr.gov/")
        assert detail["issuer"] == {"kind": "government", "name": "Federal Aviation Administration", "jurisdiction": "US"}
        assert detail["exception"] is None
        assert detail["remediation_hint"] == "revise_program"
        assert (detail["quantity"], detail["value"], detail["limit"]) == ("altitude_agl_m", 137.16, 121.92)

    def test_the_limit_itself_is_allowed(self) -> None:
        result = validate(_program({"take_off": {"altitude": 121.92}}), _drone(), policy=None)
        assert result.accepted
        assert _rule_issues(result) == [("rule.declaration_missing", "warning")]

    @pytest.mark.parametrize("policy", [None, "DEFAULT"])
    def test_the_compliance_policy_never_skips_the_pass(self, policy: Any) -> None:
        result = validate(_program({"take_off": {"altitude": 137.16}}), _drone(), policy=policy)
        assert result.has("rule.cap_exceeded")

    def test_the_manifest_ceiling_and_the_envelope_still_report_on_their_own(self) -> None:
        # The strictest limit wins and each file reports its own violation.
        result = validate(
            _program({"take_off": {"altitude": 137.16}}), _drone(), {"max_altitude": 120.0}, policy=None
        )
        codes = [e.code_str for e in result.errors]
        assert codes.index("envelope.altitude_exceeded") < codes.index("rule.cap_exceeded")

    def test_default_rulebooks_false_switches_off_only_the_bundled_rulebooks(self) -> None:
        program = _program({"take_off": {"altitude": 137.16}})
        result = validate(program, _drone(), policy=None, default_rulebooks=False)
        assert result.accepted
        (warning,) = _issues(result, "rule.defaults_disabled")
        assert warning.path == ["<rulebook>", "us_faa_part107"]
        assert "rule_id" not in warning.detail
        assert result.rulebooks == []
        # A caller rulebook still applies.
        cap = _org(_rule("low", "cap", {"quantity": "altitude_agl_m", "max": 50}))
        result = validate(program, _drone(), policy=None, default_rulebooks=False, rulebooks=[cap])
        assert result.has("rule.cap_exceeded") and result.has("rule.defaults_disabled")

    def test_defaults_disabled_fires_only_when_a_bundled_rulebook_would_apply(self) -> None:
        home = _program({"move_to": {"location": "desk"}}, profile="home")
        result = validate(home, _ground(), policy=None, default_rulebooks=False)
        assert result.accepted and not result.warnings

    def test_a_loaded_copy_under_the_same_id_replaces_the_bundled_one(self) -> None:
        mine = _faa()
        mine["rules"][0]["cap"]["max"] = 150.0
        result = validate(
            _program({"take_off": {"altitude": 137.16}}), _drone(), policy=None,
            default_rulebooks=False, rulebooks=[mine],
        )
        assert result.accepted
        assert not result.has("rule.defaults_disabled")
        assert [r.bundled for r in result.rulebooks] == [False]

    def test_in_scope_by_the_program_profile_or_the_manifest_drive_type(self) -> None:
        # A drone profile on a ground robot: in scope through the profile.
        ground = validate(_program({"move_to": {"location": "desk"}}, profile="drone"), _ground(), policy=None)
        assert [r.rulebook_id for r in ground.rulebooks] == ["us_faa_part107"]
        # An aircraft under another profile: in scope through the drive type.
        drone = validate(_program({"take_off": {"altitude": 137.16}}, profile="home"), _drone(), policy=None)
        assert drone.has("rule.cap_exceeded")
        # The caller's profiles count too.
        caller = validate(
            _program({"move_to": {"location": "desk"}}, profile="home"), _ground(), profiles=("drone",), policy=None
        )
        assert [r.rulebook_id for r in caller.rulebooks] == ["us_faa_part107"]

    def test_out_of_scope_programs_are_unchanged(self) -> None:
        result = validate(_program({"move_to": {"location": "desk"}}, profile="home"), _ground(), policy=None)
        assert result.accepted and not result.warnings and result.rulebooks == []
        assert set(result.model_dump()) == {"accepted", "errors", "warnings"}
        assert "rulebooks" not in json.loads(result.model_dump_json())

    def test_obligations_are_listed_whether_accepted_or_refused(self) -> None:
        for altitude in (30.0, 137.16):
            result = validate(_program({"take_off": {"altitude": altitude}}), _drone(), policy=None)
            (report,) = result.rulebooks
            assert report.applied and report.bundled
            assert [o["id"] for o in report.obligations] == [
                "remote_pilot_certificate",
                "visual_line_of_sight",
                "night_and_twilight_lighting",
                "controlled_airspace_authorization",
                "flight_visibility",
                "cloud_clearance",
                "people_outside_declared_zones",
            ]
            assert report.obligations[1]["cite"]["text"] == "14 CFR 107.31"

    def test_an_indoor_declaration_switches_the_rulebook_off(self) -> None:
        indoor = _deploy({"indoor": True})
        result = validate(_program({"take_off": {"altitude": 137.16}}), _drone(), policy=None, rulebooks=[indoor])
        assert result.accepted and _rule_issues(result) == []
        faa, site = result.rulebooks
        assert (faa.rulebook_id, faa.applied, faa.obligations) == ("us_faa_part107", False, [])
        assert faa.reason is not None and faa.reason.startswith("switched off: the deployment declares indoor: true")
        assert (site.rulebook_id, site.declarations) == ("acme_site", {"indoor": True})

    @pytest.mark.parametrize("value", ["true", 1])
    def test_declarations_compare_type_strictly(self, value: Any) -> None:
        indoor = _deploy({"indoor": value})
        result = validate(_program({"take_off": {"altitude": 137.16}}), _drone(), policy=None, rulebooks=[indoor])
        assert result.has("rule.cap_exceeded")

    def test_remote_id_is_a_warning_without_a_deployment_and_an_error_with_one(self) -> None:
        program = _program({"take_off": {"altitude": 30.0}})
        warn = validate(program, _drone(), policy=None)
        (issue,) = _issues(warn, "rule.declaration_missing")
        assert issue.severity == "warning"
        assert issue.primitive is None and issue.path == ["<rulebook>", "us_faa_part107"]
        assert issue.detail["remediation_hint"] == "fix_deployment"
        assert issue.detail["key"] == "remote_id" and issue.detail["declared_value"] is None
        error = validate(program, _drone(), policy=None, rulebooks=[_deploy({"remote_pilots_in_command": 1})])
        assert _issues(error, "rule.declaration_missing")[0].severity == "error"
        wrong = validate(program, _drone(), policy=None, rulebooks=[_deploy({"remote_id": "sticker"})])
        (issue,) = _issues(wrong, "rule.declaration_missing")
        assert issue.detail["declared_value"] == "sticker" and "not an allowed value" in issue.message
        ok = validate(program, _drone(), policy=None, rulebooks=[_deploy({"remote_id": "broadcast_module"})])
        assert ok.accepted and _rule_issues(ok) == []

    def test_named_places_are_judged_at_their_declared_altitude(self) -> None:
        result = validate(_program({"move_to": {"location": "tower_top"}}), _drone(), policy=None)
        (issue,) = _issues(result, "rule.cap_exceeded")
        assert issue.field == "location" and "move_to.location 'tower_top' altitude is 140 m" in issue.message
        assert issue.suggestion == "Name a place at or below 121.92 m."
        # A landing ends on the ground: land.at is not judged.
        landing = validate(_program({"land": {"at": "tower_top"}}), _drone(), policy=None)
        assert not landing.has("rule.cap_exceeded")

    @pytest.mark.parametrize(
        ("step", "field"),
        [
            ({"return_to_home": {"altitude": 130.0}}, "altitude"),
            ({"scan": {"area": {"named_region": "x"}, "altitude": 130.0, "store_as": "s"}}, "altitude"),
            ({"move_to": {"pose": {"x": 1.0, "y": 1.0, "z": 130.0}, "frame": "agl"}}, "pose.z"),
            ({"hover": {"over": "tower_top"}}, "over"),
        ],
    )
    def test_every_altitude_the_envelope_compares_is_judged(self, step: dict[str, Any], field: str) -> None:
        result = validate(_program(step), _drone(), policy=None)
        assert [i.field for i in _issues(result, "rule.cap_exceeded")] == [field]

    def test_the_climb_rate_is_not_a_speed(self) -> None:
        result = validate(_program({"take_off": {"altitude": 30.0, "climb_rate": 50.0}}), _drone(), policy=None)
        assert not result.has("rule.cap_exceeded")

    def test_the_groundspeed_cap(self) -> None:
        fast = _drone(max_velocity=60.0)
        result = validate(_program({"move_to": {"location": "home", "speed": 50.0}}), fast, policy=None)
        (issue,) = _issues(result, "rule.cap_exceeded")
        assert issue.detail["rule_id"] == "groundspeed_100mph" and issue.detail["limit"] == 44.704
        fraction = {"move_to": {"location": "home", "speed": {"value": 0.8, "units": "fraction"}}}
        (issue,) = _issues(validate(_program(fraction), fast, policy=None), "rule.cap_exceeded")
        assert issue.detail["value"] == pytest.approx(48.0)
        assert "fraction 0.8 of the manifest maximum 60 m/s" in issue.message

    def test_over_people_judges_zones_the_envelope_marks_allow_override(self) -> None:
        manifest = _drone()
        manifest["declared_locations"].append({"name": "stage", "pose": {"x": 5.0, "y": 5.0, "z": 30.0}, "frame": "agl"})
        program = _program({"take_off": {"altitude": 30.0}}, {"move_to": {"location": "stage"}})
        envelope = _people_envelope(("crowd", 0.0, 0.0, 10.0, True))
        result = validate(program, manifest, envelope, policy=None)
        (issue,) = _issues(result, "rule.over_people")
        assert not result.has("envelope.occupancy_zone_intrusion")
        assert issue.detail["zone"] == "crowd" and issue.detail["target"] == "move_to.location 'stage'"
        assert "allow_override: true" in issue.message
        # A declared operations-over-people category satisfies the rule.
        category = _deploy({"operations_over_people_category": "category_2", "remote_id": "broadcast_module"})
        assert validate(program, manifest, envelope, policy=None, rulebooks=[category]).accepted

    def test_over_people_judges_the_home_a_return_flies_to(self) -> None:
        program = _program({"take_off": {"altitude": 30.0}}, {"return_to_home": {}})
        result = validate(program, _drone(), _people_envelope(("pad", -1.0, -1.0, 2.0, False)), policy=None)
        (issue,) = _issues(result, "rule.over_people")
        assert issue.primitive == "return_to_home" and issue.field == "home"

    def test_over_people_judges_only_aircraft(self) -> None:
        ground = _ground()
        program = _program({"move_to": {"location": "desk"}}, profile="drone")
        envelope = {"people_occupancy_zones": [{"name": "crowd", "frame": "map", "vertices": [[0, 0], [5, 0], [5, 5], [0, 5]], "allow_override": True}]}
        assert not validate(program, ground, envelope, policy=None).has("rule.over_people")

    def test_over_people_with_no_people_zones_judges_nothing(self) -> None:
        program = _program({"take_off": {"altitude": 30.0}}, {"hover": {"over": "$spot"}})
        assert not validate(program, _drone(), policy=None).has("rule.place_unknown")

    def test_over_people_fails_closed_on_a_runtime_binding(self) -> None:
        program = _program({"take_off": {"altitude": 30.0}}, {"hover": {"over": "$spot"}})
        result = validate(program, _drone(), _people_envelope(("crowd", 50.0, 50.0, 5.0, False)), policy=None)
        (issue,) = _issues(result, "rule.place_unknown")
        assert "runtime binding" in issue.detail["reason"] and issue.field == "over"


class TestExceptions:
    def _run(self, altitude: float, as_of: datetime.date) -> ValidationResult:
        return validate(
            _program({"take_off": {"altitude": altitude}}), _drone(), policy=None,
            rulebooks=[_waiver()], as_of=as_of,
        )

    def test_a_covered_violation_is_a_warning_that_names_the_basis(self) -> None:
        result = self._run(137.16, datetime.date(2026, 9, 26))
        assert result.accepted
        (issue,) = _issues(result, "rule.cap_exceeded")
        assert issue.severity == "warning" and issue.suggestion is None
        assert issue.message.startswith(
            "14 CFR 107.51(b): maximum altitude 400 feet (121.92 m) above ground level. "
            "take_off.altitude is 137.16 m; allowed by exception: Certificate of waiver 107W-EXAMPLE-0001"
        )
        assert issue.message.endswith("(limit 152.4 m, expires 2027-03-31).")
        assert issue.detail["exception"] == {
            "rulebook_id": "example_aerial_survey_north_tower",
            "basis": issue.detail["exception"]["basis"],
            "limit": 152.4,
            "expires": "2027-03-31",
            "expired": False,
            "exceeds_limit": False,
        }
        assert "107W-EXAMPLE-0001" in issue.detail["exception"]["basis"]

    def test_an_expired_exception_leaves_the_error(self) -> None:
        result = self._run(137.16, datetime.date(2027, 4, 1))
        (issue,) = _issues(result, "rule.cap_exceeded")
        assert issue.severity == "error" and issue.detail["exception"]["expired"] is True
        assert "expired on 2027-03-31" in issue.message
        # The expiry day itself is still covered.
        assert self._run(137.16, datetime.date(2027, 3, 31)).accepted

    def test_a_value_above_the_exception_limit_stays_an_error(self) -> None:
        result = self._run(160.0, datetime.date(2026, 9, 26))
        (issue,) = _issues(result, "rule.cap_exceeded")
        assert issue.severity == "error" and issue.detail["exception"]["exceeds_limit"] is True
        assert "above the exception's limit of 152.4 m" in issue.message
        assert issue.suggestion == "Use a value at or below 152.4 m."

    def test_as_of_defaults_to_today(self) -> None:
        # The example waiver expires on 2027-03-31; without as_of the date is today in UTC.
        result = validate(_program({"take_off": {"altitude": 137.16}}), _drone(), policy=None, rulebooks=[_waiver()])
        expired = datetime.datetime.now(datetime.UTC).date() > datetime.date(2027, 3, 31)
        assert result.accepted is not expired

    def test_an_exception_to_a_zone_rule_downgrades_it(self) -> None:
        work_order = _deploy(exceptions=[{"rule": "example_logistics_operations/restricted_rooms", "basis": "Work order 42"}])
        result = validate(
            _program({"move_to": {"location": "server_room"}}, profile="warehouse"), _warehouse(), policy=None,
            rulebooks=[_warehouse_rulebook(), work_order],
        )
        assert result.accepted
        (issue,) = _issues(result, "rule.zone_forbidden")
        assert issue.severity == "warning" and "allowed by exception: Work order 42" in issue.message

    def test_an_exception_to_a_declaration_rule(self) -> None:
        authorized = _deploy(
            {"remote_pilots_in_command": 1},
            [{"rule": "us_faa_part107/remote_identification", "basis": "FAA authorization under 89.120"}],
        )
        result = validate(_program({"take_off": {"altitude": 30.0}}), _drone(), policy=None, rulebooks=[authorized])
        assert result.accepted
        assert _issues(result, "rule.declaration_missing")[0].severity == "warning"


class TestDeploymentSetChecks:
    def _invalid(self, *books: dict[str, Any]) -> list[Any]:
        result = validate(_program({"take_off": {"altitude": 30.0}}), _drone(), policy=None, rulebooks=list(books))
        return _issues(result, "rule.rulebook_invalid")

    def test_conflicting_declarations_make_the_set_invalid_and_neither_value_counts(self) -> None:
        a = _deploy({"indoor": True, "remote_id": "broadcast_module"}, rulebook_id="site_a")
        b = _deploy({"indoor": False}, rulebook_id="site_b")
        result = validate(_program({"take_off": {"altitude": 137.16}}), _drone(), policy=None, rulebooks=[a, b])
        (issue,) = _issues(result, "rule.rulebook_invalid")
        assert "declare indoor with different values (true and false)" in issue.message
        assert issue.detail["remediation_hint"] == "fix_deployment"
        # The conflicting key is dropped, so the FAA rulebook stays switched on.
        assert result.has("rule.cap_exceeded")

    def test_an_exception_needs_an_exceptable_rule_that_exists(self) -> None:
        strict = _org(_rule("no_cameras", "forbid_primitive", {"primitives": ["capture"]}))
        not_exceptable = _deploy(exceptions=[{"rule": "acme_rules/no_cameras", "basis": "b"}])
        (issue,) = self._invalid(strict, not_exceptable)
        assert "not exceptable" in issue.message and issue.path == ["<rulebook>", "acme_site"]
        missing = _deploy(exceptions=[{"rule": "us_faa_part107/no_such_rule", "basis": "b"}])
        assert "has no rule no_such_rule" in self._invalid(missing)[0].message

    def test_an_exception_to_a_rulebook_that_is_not_loaded_is_inert(self) -> None:
        assert self._invalid(_deploy(exceptions=[{"rule": "someone_else/rule", "basis": "b"}])) == []

    def test_a_rule_has_at_most_one_exception(self) -> None:
        one = _deploy(exceptions=[{"rule": "us_faa_part107/altitude_400ft_agl", "basis": "a", "limit": 200}], rulebook_id="one")
        two = _deploy(exceptions=[{"rule": "us_faa_part107/altitude_400ft_agl", "basis": "b", "limit": 200}], rulebook_id="two")
        result = validate(_program({"take_off": {"altitude": 137.16}}), _drone(), policy=None, rulebooks=[one, two])
        assert "a rule has at most one exception" in _issues(result, "rule.rulebook_invalid")[0].message
        # Neither exception is used.
        assert _issues(result, "rule.cap_exceeded")[0].severity == "error"

    @pytest.mark.parametrize(
        ("exception", "problem"),
        [
            ({"rule": "us_faa_part107/altitude_400ft_agl", "basis": "b"}, "states no limit"),
            ({"rule": "us_faa_part107/one_aircraft_per_pilot", "basis": "b"}, "states no limit"),
            ({"rule": "us_faa_part107/one_aircraft_per_pilot", "basis": "b", "limit": 1.5}, "integer of 1 or more"),
            ({"rule": "us_faa_part107/over_human_beings", "basis": "b", "limit": 3}, "only cap and max_concurrent_aircraft"),
        ],
    )
    def test_limits_match_the_rule_kind(self, exception: dict[str, Any], problem: str) -> None:
        (issue,) = self._invalid(_deploy(exceptions=[exception]))
        assert problem in issue.message


class TestLoading:
    def test_a_rulebook_that_breaks_the_format_is_reported_and_not_applied(self) -> None:
        broken = _org(_rule("slow", "cap", {"quantity": "speed_m_per_s", "max": "fast"}))
        result = validate(_program({"move_to": {"location": "desk", "speed": 1.9}}, profile="home"), _ground(), policy=None, rulebooks=[broken])
        (issue,) = _issues(result, "rule.rulebook_invalid")
        assert not result.accepted and not result.has("rule.cap_exceeded")
        assert issue.path == ["<rulebook>", "acme_rules"] and issue.detail["source"] == "acme_rules"
        assert any("rules[0].cap.max" in p for p in issue.detail["problems"])
        assert "rule_id" not in issue.detail

    def test_a_non_mapping_is_named_by_its_position(self) -> None:
        result = validate(_program({"move_to": {"location": "desk"}}, profile="home"), _ground(), policy=None, rulebooks=[["not", "a", "mapping"]])  # type: ignore[list-item]
        (issue,) = _issues(result, "rule.rulebook_invalid")
        assert issue.detail["source"] == "rulebooks[0]"

    def test_a_repeated_rulebook_id_is_invalid_and_the_later_copy_is_not_applied(self) -> None:
        mine = _faa()
        mine["rules"][0]["cap"]["max"] = 500.0
        result = validate(_program({"take_off": {"altitude": 137.16}}), _drone(), policy=None, rulebooks=[mine])
        assert "loaded twice" in _issues(result, "rule.rulebook_invalid")[0].message
        assert result.has("rule.cap_exceeded")  # the bundled 121.92 m still applies
        assert [r.rulebook_id for r in result.rulebooks] == ["us_faa_part107"]

    def test_rulebook_models_are_accepted(self) -> None:
        model = Rulebook.model_validate(_org(_rule("low", "cap", {"quantity": "altitude_agl_m", "max": 50})))
        result = validate(_program({"take_off": {"altitude": 60.0}}), _drone(), policy=None, rulebooks=[model])
        assert [i.detail["rule_id"] for i in _issues(result, "rule.cap_exceeded")] == ["low"]

    def test_load_order_is_bundled_then_the_callers_in_order(self) -> None:
        a = _org(rulebook_id="first_rules")
        b = _org(rulebook_id="second_rules")
        result = validate(_program({"take_off": {"altitude": 30.0}}), _drone(), policy=None, rulebooks=[a, b, _waiver()])
        assert [r.rulebook_id for r in result.rulebooks] == [
            "us_faa_part107", "first_rules", "second_rules", "example_aerial_survey_north_tower",
        ]

    def test_the_callers_rulebooks_are_not_changed(self) -> None:
        books = [_warehouse_rulebook(), _waiver()]
        before = copy.deepcopy(books)
        validate(_program({"move_to": {"location": "restroom"}}, profile="warehouse"), _warehouse(), policy=None, rulebooks=books)
        assert books == before

    def test_applies_to_with_no_lists_applies_everywhere(self) -> None:
        book = _org(
            _rule("low", "cap", {"quantity": "speed_m_per_s", "max": 1.0}),
            applies_to={"unless_declared": [{"key": "trial", "allowed": [True]}]},
        )
        program = _program({"move_to": {"location": "desk", "speed": 1.5}}, profile="home")
        assert validate(program, _ground(), policy=None, rulebooks=[book]).has("rule.cap_exceeded")
        off = validate(program, _ground(), policy=None, rulebooks=[book, _deploy({"trial": True})])
        assert off.accepted and off.rulebooks[0].applied is False


# ---------------------------------------------------------------------------
# Rule kinds on a ground robot
# ---------------------------------------------------------------------------


class TestCaps:
    def test_a_fraction_speed_is_the_fraction_of_the_manifest_maximum(self) -> None:
        slow = _org(_rule("aisle", "cap", {"quantity": "speed_m_per_s", "max": 1.5}))
        fast = _program({"move_to": {"location": "desk", "speed": {"value": 0.9, "units": "fraction"}}}, profile="home")
        (issue,) = _issues(validate(fast, _ground(), policy=None, rulebooks=[slow]), "rule.cap_exceeded")
        assert issue.detail["value"] == pytest.approx(1.8)
        ok = _program({"move_to": {"location": "desk", "speed": {"value": 0.5, "units": "fraction"}}}, profile="home")
        assert validate(ok, _ground(), policy=None, rulebooks=[slow]).accepted

    def test_drive_and_trajectory_speeds(self) -> None:
        slow = _org(_rule("aisle", "cap", {"quantity": "speed_m_per_s", "max": 0.5}))
        program = _program(
            {"drive": {"distance": 1.0, "speed": 0.8}},
            {"follow_trajectory": {"trajectory": "$route", "speed_envelope": {"max_velocity_mps": 0.9}}},
            profile=["home", "educational"],
        )
        result = validate(program, _ground(), policy=None, rulebooks=[slow])
        assert [i.field for i in _issues(result, "rule.cap_exceeded")] == ["speed", "speed_envelope"]

    def test_grip_force_resolves_named_levels_and_judges_each_bimanual_side(self) -> None:
        soft = _org(_rule("hands", "cap", {"quantity": "grip_force_n", "max": 5.0}))
        program = _program(
            {"detect": {"object": "box", "store_as": "b"}},
            {"grasp": {"target": "$b", "force": "gentle"}},
            {"grasp": {"target": "$b", "force": "firm"}},
            {"bimanual": {"mode": "together", "left": {"target": "$b", "force": 6.0}, "right": {"target": "$b", "force": 7.0}}},
            profile="home",
        )
        issues = _issues(validate(program, _ground(), policy=None, rulebooks=[soft]), "rule.cap_exceeded")
        assert [(i.path[-1], i.detail["value"]) for i in issues] == [("2", 8.0), ("left", 6.0), ("right", 7.0)]


class TestForbidPrimitive:
    def _run(self, rule: dict[str, Any], *steps: dict[str, Any]) -> ValidationResult:
        return validate(
            _program(*steps, profile=["home", "educational"]), _ground(), policy=None, rulebooks=[_org(rule)]
        )

    def test_a_forbidden_primitive(self) -> None:
        result = self._run(_rule("quiet", "forbid_primitive", {"primitives": ["speak"]}), {"speak": {"utterance": "hi"}})
        (issue,) = _issues(result, "rule.primitive_forbidden")
        assert issue.detail["primitive"] == "speak" and "used_by" not in issue.detail
        assert issue.message == "Acme policy quiet: rule quiet. The step uses speak, which the rule forbids."

    @pytest.mark.parametrize(
        ("forbidden", "step", "used"),
        [
            ("speak", {"listen": {"prompt": "Ready?"}}, True),
            ("speak", {"listen": {}}, False),
            ("capture", {"scan": {"area": {"named_region": "vault"}, "store_as": "s"}}, True),
            ("capture", {"scan": {"area": {"named_region": "vault"}, "media": "sensor_only", "store_as": "s"}}, False),
            ("grasp", {"pick_from": {"source": "desk", "object": "box"}}, True),
            ("detect", {"pick_from": {"source": "desk", "object": "box"}}, True),
            ("release", {"place_at": {"target": "desk", "held": "$b"}}, True),
            ("grasp", {"bimanual": {"mode": "independent", "left": {"target": "$b"}, "right": {"mode": "drop"}}}, True),
            ("release", {"bimanual": {"mode": "independent", "left": {"target": "$b"}, "right": {"mode": "drop"}}}, True),
        ],
    )
    def test_composite_uses_count(self, forbidden: str, step: dict[str, Any], used: bool) -> None:
        result = self._run(_rule("r", "forbid_primitive", {"primitives": [forbidden]}), step)
        issues = _issues(result, "rule.primitive_forbidden")
        assert bool(issues) is used
        if used:
            assert issues[0].detail["used_by"] == next(iter(step))

    def test_names_and_allowlists(self) -> None:
        names = _rule("outputs", "forbid_primitive", {"primitives": ["set_output"], "names": ["muting"]})
        assert self._run(names, {"set_output": {"output": "muting", "value": True}}).has("rule.primitive_forbidden")
        assert not self._run(names, {"set_output": {"output": "lamp", "value": True}}).has("rule.primitive_forbidden")
        allow = _rule("programs", "forbid_primitive", {"primitives": ["call_program"], "except_names": ["safe_job"]})
        (issue,) = _issues(self._run(allow, {"call_program": {"name": "risky_job"}}), "rule.primitive_forbidden")
        assert issue.detail["name"] == "risky_job" and "not on the rule's allowed list (safe_job)" in issue.message
        assert not self._run(allow, {"call_program": {"name": "safe_job"}}).has("rule.primitive_forbidden")


class TestZoneScopedPrimitive:
    RULE = _rule("no_photos", "forbid_primitive", {"primitives": ["capture"], "in_zones": ["vault"]})
    CAPTURE = {"capture": {"media": "photo", "store_as": "p"}}

    def _run(self, *steps: dict[str, Any], rule: dict[str, Any] | None = None) -> ValidationResult:
        return validate(
            _program(*steps, profile=["home", "educational"]), _ground(), policy=None,
            rulebooks=[_org(rule or self.RULE)],
        )

    def _codes(self, *steps: dict[str, Any]) -> list[str]:
        return [code for code, _ in _rule_issues(self._run(*steps))]

    def test_the_current_place_decides(self) -> None:
        assert self._codes({"move_to": {"location": "vault"}}, self.CAPTURE) == ["rule.primitive_forbidden"]
        assert self._codes({"move_to": {"location": "desk"}}, self.CAPTURE) == []
        # A point on the zone's boundary is inside it.
        assert self._codes({"move_to": {"location": "vault_door"}}, self.CAPTURE) == ["rule.primitive_forbidden"]

    def test_a_capture_target_that_names_a_zone(self) -> None:
        aimed = {"capture": {"media": "photo", "target": "vault", "store_as": "p"}}
        assert self._codes({"move_to": {"location": "desk"}}, aimed) == ["rule.primitive_forbidden"]

    def test_an_unknown_place_fails_closed(self) -> None:
        result = self._run(self.CAPTURE)
        (issue,) = _issues(result, "rule.place_unknown")
        assert issue.detail["reason"] == "the robot's place is not known at this step"
        assert issue.suggestion == "Move to a declared place before this step."
        for mover in ({"drive": {"distance": 1.0}}, {"turn": {"angle": 90.0}}, {"call_program": {"name": "safe_job"}}):
            assert self._codes({"move_to": {"location": "desk"}}, mover, self.CAPTURE) == ["rule.place_unknown"]

    def test_other_steps_leave_the_place_unchanged(self) -> None:
        assert self._codes({"move_to": {"location": "vault"}}, {"wait": {"duration": 1}}, self.CAPTURE) == [
            "rule.primitive_forbidden"
        ]

    def test_branch_arms_that_end_apart_leave_the_place_unknown(self) -> None:
        apart = {"type": "branch", "condition": "$x", "if_true": {"move_to": {"location": "desk"}}, "if_false": {"move_to": {"location": "lobby"}}}
        assert self._codes(apart, self.CAPTURE) == ["rule.place_unknown"]
        together = {"type": "branch", "condition": "$x", "if_true": {"move_to": {"location": "desk"}}, "if_false": {"move_to": {"location": "desk"}}}
        assert self._codes(together, self.CAPTURE) == []
        # A missing if_false arm leaves the entry place: desk, then maybe desk.
        one_arm = {"type": "branch", "condition": "$x", "if_true": {"move_to": {"location": "desk"}}}
        assert self._codes({"move_to": {"location": "desk"}}, one_arm, self.CAPTURE) == []

    def test_a_parallel_arm_does_not_know_where_a_moving_arm_took_the_robot(self) -> None:
        both = {"type": "parallel", "branches": [{"move_to": {"location": "desk"}}, self.CAPTURE]}
        assert self._codes({"move_to": {"location": "desk"}}, both) == ["rule.place_unknown"]
        still = {"type": "parallel", "branches": [{"wait": {"duration": 1}}, self.CAPTURE]}
        assert self._codes({"move_to": {"location": "desk"}}, still) == []

    def test_a_retry_body_that_moves_starts_unknown(self) -> None:
        body = {"type": "sequence", "steps": [self.CAPTURE, {"move_to": {"location": "desk"}}]}
        retry = {"type": "retry", "max_attempts": 2, "behavior": body}
        assert self._codes({"move_to": {"location": "desk"}}, retry) == ["rule.place_unknown"]

    def test_an_undeclared_zone_warns_once_and_the_others_are_judged(self) -> None:
        rule = _rule("no_photos", "forbid_primitive", {"primitives": ["capture"], "in_zones": ["ghost", "vault"]})
        result = self._run({"move_to": {"location": "vault"}}, self.CAPTURE, self.CAPTURE, rule=rule)
        assert _rule_issues(result) == [
            ("rule.primitive_forbidden", "error"),
            ("rule.primitive_forbidden", "error"),
            ("rule.zone_undeclared", "warning"),
        ]
        (warning,) = _issues(result, "rule.zone_undeclared")
        assert warning.detail["zone"] == "ghost" and warning.path == ["<rulebook>", "acme_rules"]

    def test_a_rule_with_no_resolved_zone_judges_nothing(self) -> None:
        rule = _rule("no_photos", "forbid_primitive", {"primitives": ["capture"], "in_zones": ["ghost"]})
        assert [c for c, _ in _rule_issues(self._run(self.CAPTURE, rule=rule))] == ["rule.zone_undeclared"]

    def test_places_are_judged_in_the_zone_frame(self) -> None:
        lab = _rule("no_photos", "forbid_primitive", {"primitives": ["capture"], "in_zones": ["lab"]})
        inside = {"move_to": {"pose": {"x": 101.0, "y": 1.0}, "frame": "map"}}
        assert [c for c, _ in _rule_issues(self._run(inside, self.CAPTURE, rule=lab))] == ["rule.primitive_forbidden"]
        cut_off = {"move_to": {"location": "islet"}}
        result = self._run(cut_off, self.CAPTURE, rule=lab)
        (issue,) = _issues(result, "rule.place_unknown")
        assert "cannot be expressed in the frame 'office'" in issue.detail["reason"] and issue.detail["zone"] == "lab"


class TestForbidZoneEntry:
    RULE = _rule("keep_out", "forbid_zone_entry", {"zones": ["vault"]})

    def _issues(self, *steps: dict[str, Any], envelope: dict[str, Any] | None = None) -> list[Any]:
        result = validate(
            _program(*steps, profile="home"), _ground(), envelope, policy=None, rulebooks=[_org(self.RULE)]
        )
        return _issues(result, "rule.zone_forbidden") + _issues(result, "rule.place_unknown")

    def test_points_and_areas(self) -> None:
        (issue,) = self._issues({"move_to": {"location": "vault"}})
        assert issue.detail["target"] == "move_to.location 'vault'" and issue.field == "location"
        assert len(self._issues({"move_to": {"location": "vault_door"}})) == 1  # on the boundary
        assert len(self._issues({"move_to": {"location": "hall"}})) == 1  # an area that overlaps
        assert self._issues({"move_to": {"location": "desk"}}) == []
        assert len(self._issues({"move_to": {"pose": {"x": 22.0, "y": 2.0}, "frame": "map"}})) == 1

    @pytest.mark.parametrize(
        "step",
        [
            {"pick_from": {"source": "vault", "object": "box"}},
            {"place_at": {"target": "vault_door", "held": "$b"}},
            {"dock": {"at": "bay"}},
            {"dock": {}},
            {"swap_tool": {"at": "bay", "to": "drill"}},
            {"scan": {"area": {"polygon": [{"x": 23.0, "y": 3.0}, {"x": 30.0, "y": 3.0}, {"x": 30.0, "y": 9.0}]}, "store_as": "s"}},
            {"scan": {"area": {"bounding_box": {"min_x": 10.0, "max_x": 20.0, "min_y": 0.0, "max_y": 1.0}}, "store_as": "s"}},
        ],
        ids=["pick_from", "place_at", "dock_at", "dock_default", "swap_tool", "scan_polygon", "scan_box_touching"],
    )
    def test_every_target_kind(self, step: dict[str, Any]) -> None:
        assert [i.code_str for i in self._issues(step)] == ["rule.zone_forbidden"]

    def test_a_runtime_binding_fails_closed(self) -> None:
        (issue,) = self._issues({"hover": {"over": "$spot"}})
        assert issue.code_str == "rule.place_unknown" and issue.field == "over"

    def test_zones_resolve_through_areas_then_people_zones_then_geofences(self) -> None:
        rule = _rule("keep_out", "forbid_zone_entry", {"zones": ["crowd", "yard"]})
        envelope = {
            "people_occupancy_zones": [{"name": "crowd", "frame": "map", "vertices": [[0, 0], [2, 0], [2, 2], [0, 2]]}],
            "geofences": [{"name": "yard", "frame": "map", "vertices": [[49, 49], [51, 49], [51, 51], [49, 51]]}],
        }
        result = validate(
            _program({"move_to": {"location": "desk"}}, {"move_to": {"location": "lobby"}}, profile="home"),
            _ground(), envelope, policy=None, rulebooks=[_org(rule)],
        )
        assert [i.detail["zone"] for i in _issues(result, "rule.zone_forbidden")] == ["crowd", "yard"]


class TestConcurrency:
    @staticmethod
    def _fleet(program: dict[str, Any], *, members: int = 2, **kwargs: Any) -> ValidationResult:
        drone = _yaml(FIXTURES / "manifests" / "utm_drone.yaml")
        names = ["a", "b", "c"][:members]
        roster = {"members": [{"name": n, "manifest": "utm_drone"} for n in names]}
        return validate_fleet(roster, {n: copy.deepcopy(drone) for n in names}, program, policy=None, **kwargs)

    @staticmethod
    def _on(member: str, step: dict[str, Any]) -> dict[str, Any]:
        return {"type": "on", "member": member, "body": step}

    def _seq(self, *nodes: dict[str, Any]) -> dict[str, Any]:
        return {"profile": "drone", "behavior": {"type": "sequence", "steps": list(nodes)}}

    def test_one_aircraft_at_a_time(self) -> None:
        up_a, up_b = self._on("a", {"take_off": {"altitude": 10.0}}), self._on("b", {"take_off": {"altitude": 10.0}})
        down_a, down_b = self._on("a", {"land": {}}), self._on("b", {"land": {}})
        assert self._fleet(self._seq(up_a, down_a, up_b, down_b)).accepted
        result = self._fleet(self._seq(up_a, up_b, down_a, down_b))
        (issue,) = _issues(result, "rule.concurrency_exceeded")
        assert issue.path == ["<rulebook>", "us_faa_part107"] and issue.primitive is None
        assert (issue.detail["count"], issue.detail["limit"], issue.detail["aircraft"]) == (2, 1, ["a", "b"])
        assert issue.detail["remote_pilots_in_command"] == 1
        assert issue.message.startswith(
            "14 CFR 107.35: one unmanned aircraft at a time per remote pilot in command. "
            "The program can have 2 aircraft airborne at once (a, b); the limit is 1"
        )

    def test_a_member_whose_first_flight_step_is_not_take_off_is_airborne_from_the_start(self) -> None:
        program = self._seq(self._on("a", {"move_to": {"location": "alt_high"}}), self._on("b", {"take_off": {"altitude": 10.0}}))
        assert self._fleet(program).has("rule.concurrency_exceeded")

    def test_parallel_arms_count_together(self) -> None:
        both = {"type": "parallel", "branches": [self._on("a", {"take_off": {"altitude": 10.0}}), self._on("b", {"take_off": {"altitude": 20.0}})]}
        assert self._fleet(self._seq(both)).has("rule.concurrency_exceeded")

    def test_a_branch_counts_its_larger_arm(self) -> None:
        maybe = {"type": "branch", "condition": "$x", "if_true": self._on("b", {"take_off": {"altitude": 10.0}})}
        program = self._seq(self._on("a", {"take_off": {"altitude": 10.0}}), maybe)
        assert self._fleet(program).has("rule.concurrency_exceeded")

    def test_a_retry_keeps_the_state_before_it(self) -> None:
        body = {"type": "sequence", "steps": [self._on("b", {"take_off": {"altitude": 10.0}}), self._on("b", {"land": {}})]}
        program = self._seq(
            self._on("a", {"take_off": {"altitude": 10.0}}),
            self._on("a", {"land": {}}),
            {"type": "retry", "max_attempts": 2, "behavior": body},
        )
        assert self._fleet(program).accepted

    def test_more_pilots_or_an_exception_raise_the_limit(self) -> None:
        program = self._seq(self._on("a", {"take_off": {"altitude": 10.0}}), self._on("b", {"take_off": {"altitude": 20.0}}))
        two_pilots = _deploy({"remote_pilots_in_command": 2, "remote_id": "broadcast_module"})
        assert self._fleet(program, rulebooks=[two_pilots]).accepted
        waiver = _deploy(
            {"remote_id": "broadcast_module"},
            [{"rule": "us_faa_part107/one_aircraft_per_pilot", "basis": "Waiver 107W-TEST", "limit": 3}],
        )
        result = self._fleet(program, rulebooks=[waiver])
        assert result.accepted and _issues(result, "rule.concurrency_exceeded")[0].severity == "warning"
        low = _deploy(
            {"remote_id": "broadcast_module"},
            [{"rule": "us_faa_part107/one_aircraft_per_pilot", "basis": "Waiver 107W-TEST", "limit": 1}],
        )
        assert _issues(self._fleet(program, rulebooks=[low]), "rule.concurrency_exceeded")[0].severity == "error"

    def test_the_max_form(self) -> None:
        three = self._seq(*[self._on(n, {"take_off": {"altitude": 10.0}}) for n in ("a", "b", "c")])
        cap = _org(_rule("swarm", "max_concurrent_aircraft", {"max": 2}))
        result = self._fleet(three, members=3, rulebooks=[cap], default_rulebooks=False)
        (issue,) = _issues(result, "rule.concurrency_exceeded")
        assert issue.detail["limit"] == 2 and issue.detail["remote_pilots_in_command"] is None

    def test_never_judged_by_validate(self) -> None:
        cap = _org(_rule("solo", "max_concurrent_aircraft", {"max": 1}))
        result = validate(_program({"take_off": {"altitude": 10.0}}), _drone(), policy=None, rulebooks=[cap])
        assert not result.has("rule.concurrency_exceeded")

    def test_fleet_step_issues_name_the_member(self) -> None:
        program = self._seq(self._on("b", {"take_off": {"altitude": 137.16}}))
        (issue,) = _issues(self._fleet(program), "rule.cap_exceeded")
        assert issue.detail["member"] == "b" and issue.path == ["behavior", "steps", "0", "body"]


class TestReportAndOrder:
    def test_the_report_serializes_and_round_trips(self) -> None:
        result = validate(
            _program({"take_off": {"altitude": 137.16}}), _drone(), policy=None,
            rulebooks=[_waiver()], as_of=datetime.date(2026, 9, 26),
        )
        data = json.loads(result.model_dump_json())
        faa, site = data["rulebooks"]
        assert faa["rulebook_id"] == "us_faa_part107" and faa["source_status"] == "final_rule"
        assert faa["reviewed"] == "2026-09-26" and faa["declarations"] is None
        assert site["declarations"] == {"remote_id": "broadcast_module"}
        assert site["exceptions"][0]["rule"] == "us_faa_part107/altitude_400ft_agl"
        assert ValidationResult.model_validate(data) == result

    def test_rule_issues_sit_between_the_envelope_and_the_binding_pass(self) -> None:
        program = _program(
            {"take_off": {"altitude": 137.16}},
            {"hover": {"over": "$nowhere"}},
        )
        result = validate(program, _drone(), {"max_altitude": 100.0}, policy=None)
        codes = [e.code_str for e in result.errors]
        assert codes.index("envelope.altitude_exceeded") < codes.index("rule.cap_exceeded")
        assert codes.index("rule.cap_exceeded") < codes.index("binding.unresolved_reference")

    def test_a_program_that_fails_to_parse_gets_no_report(self) -> None:
        result = validate({"profile": "drone", "behavior": {"take_off": {}}}, _drone())
        assert not result.accepted and result.rulebooks == []
