"""Shape checks for the rulebook files RFC-0702 (Draft) ships.

These tests pin the files to the format frozen in
spec/layer-1-hal/rulebook.md: the bundled FAA rulebook's citations and unit
conversions, the two examples, and the industrial template. They read the
YAML directly. The validator's own schema and the rulebook pass are tested in
test_rulebooks.py.
"""

from __future__ import annotations

import re
from importlib import resources
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = REPO_ROOT / "examples" / "rulebooks"
BUNDLED = resources.files("urml_validator.rulebooks").joinpath("us_faa_part107.yaml")

TOP_LEVEL_KEYS = {
    "rulebook_version",
    "rulebook_id",
    "title",
    "issuer",
    "maintained_by",
    "source_status",
    "effective",
    "reviewed",
    "description",
    "applies_to",
    "rules",
    "obligations",
    "declarations",
    "exceptions",
}
RULE_KINDS = {
    "cap",
    "forbid_primitive",
    "forbid_zone_entry",
    "forbid_over_people",
    "require_declared",
    "max_concurrent_aircraft",
}
RULE_COMMON_KEYS = {"id", "title", "cite", "exceptable", "note"}
STATUS_FOR_ISSUER = {
    "government": {"final_rule", "enacted_statute"},
    "organization": {"organization_policy"},
    "deployment": {"deployment_declaration"},
}
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ECFR_TITLE_14 = "https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/"

FEET = 0.3048  # meters per international foot
KNOT = 1852 / 3600  # meters per second per knot
MPH = 1609.344 / 3600  # meters per second per statute mile per hour


def _load(text: str) -> dict[str, Any]:
    data = yaml.safe_load(text)
    assert isinstance(data, dict), "a rulebook is a YAML mapping"
    return data


def _faa() -> dict[str, Any]:
    return _load(BUNDLED.read_text(encoding="utf-8"))


def _example(name: str) -> dict[str, Any]:
    return _load((EXAMPLES / name).read_text(encoding="utf-8"))


def _rule(book: dict[str, Any], rule_id: str) -> dict[str, Any]:
    matches = [r for r in book["rules"] if r["id"] == rule_id]
    assert len(matches) == 1, f"{book['rulebook_id']} has no single rule {rule_id!r}"
    return matches[0]


ALL_FILES = [
    ("us_faa_part107.yaml", _faa),
    ("example-warehouse.yaml", lambda: _example("example-warehouse.yaml")),
    ("example-deployment.yaml", lambda: _example("example-deployment.yaml")),
    ("industrial-template.yaml", lambda: _example("industrial-template.yaml")),
]
FILLED_FILES = ALL_FILES[:3]  # the template is invalid on purpose until filled in


def test_the_faa_rulebook_ships_as_package_data() -> None:
    assert BUNDLED.is_file()


@pytest.mark.parametrize(("name", "load"), ALL_FILES, ids=[n for n, _ in ALL_FILES])
def test_top_level_keys_and_issuer_status(name: str, load: Any) -> None:
    book = load()
    assert set(book) <= TOP_LEVEL_KEYS, f"{name}: unknown keys {set(book) - TOP_LEVEL_KEYS}"
    assert book["rulebook_version"] == "0.1"
    kind = book["issuer"]["kind"]
    assert book["source_status"] in STATUS_FOR_ISSUER[kind], name
    if kind == "deployment":
        assert not {"applies_to", "rules", "obligations"} & set(book), name
    else:
        assert not {"declarations", "exceptions"} & set(book), name


@pytest.mark.parametrize(("name", "load"), FILLED_FILES, ids=[n for n, _ in FILLED_FILES])
def test_ids_dates_and_rule_kinds(name: str, load: Any) -> None:
    book = load()
    assert IDENTIFIER.match(book["rulebook_id"]), name
    for key in ("effective", "reviewed"):
        if key in book:
            assert isinstance(book[key], str) and ISO_DATE.match(book[key]), f"{name}: {key}"
    ids = [entry["id"] for entry in book.get("rules", []) + book.get("obligations", [])]
    assert len(ids) == len(set(ids)), f"{name}: duplicate ids"
    assert all(IDENTIFIER.match(i) for i in ids), name
    for rule in book.get("rules", []):
        kinds = set(rule) & RULE_KINDS
        assert len(kinds) == 1, f"{name}/{rule['id']}: one kind key, got {kinds}"
        assert set(rule) - RULE_KINDS <= RULE_COMMON_KEYS, f"{name}/{rule['id']}"


def test_every_faa_rule_and_obligation_cites_the_ecfr() -> None:
    book = _faa()
    assert book["issuer"] == {
        "kind": "government",
        "name": "Federal Aviation Administration",
        "jurisdiction": "US",
    }
    assert book["reviewed"] == "2026-09-26"
    for entry in book["rules"] + book["obligations"]:
        cite = entry["cite"]
        assert cite["text"].startswith("14 CFR "), entry["id"]
        assert cite["url"].startswith(ECFR_TITLE_14), entry["id"]


def test_part_108_is_not_encoded() -> None:
    """Part 108 is a proposed rule on 2026-09-26; bundled rulebooks encode final rules only."""
    for entry in _faa()["rules"] + _faa()["obligations"]:
        assert "part-108" not in entry["cite"]["url"]
        assert "Part 108" not in entry["cite"]["text"]


def test_the_altitude_cap_is_400_feet_above_ground() -> None:
    rule = _rule(_faa(), "altitude_400ft_agl")
    assert rule["cite"]["text"] == "14 CFR 107.51(b)"
    assert rule["cap"]["quantity"] == "altitude_agl_m"
    assert rule["cap"]["max"] == pytest.approx(400 * FEET)
    assert rule["cap"]["max"] == 121.92


def test_the_speed_cap_is_the_stricter_of_87_knots_and_100_mph() -> None:
    rule = _rule(_faa(), "groundspeed_100mph")
    assert rule["cite"]["text"] == "14 CFR 107.51(a)"
    assert 100 * MPH < 87 * KNOT, "100 mph is the stricter reading"
    assert rule["cap"]["quantity"] == "speed_m_per_s"
    assert rule["cap"]["max"] == pytest.approx(100 * MPH)
    assert rule["cap"]["max"] == 44.704


def test_the_faa_rule_set() -> None:
    rules = {r["id"]: r for r in _faa()["rules"]}
    assert set(rules) == {
        "altitude_400ft_agl",
        "groundspeed_100mph",
        "over_human_beings",
        "one_aircraft_per_pilot",
        "remote_identification",
    }
    assert all(r["exceptable"] is True for r in rules.values())
    assert rules["one_aircraft_per_pilot"]["max_concurrent_aircraft"] == {"max_per_remote_pilot": 1}
    categories = rules["over_human_beings"]["forbid_over_people"]["unless_declared"][0]
    assert categories["key"] == "operations_over_people_category"
    assert categories["allowed"] == ["category_1", "category_2", "category_3", "category_4"]
    remote_id = rules["remote_identification"]["require_declared"]
    assert remote_id == {
        "key": "remote_id",
        "allowed": ["standard_remote_id", "broadcast_module", "faa_recognized_identification_area"],
    }
    obligations = {o["id"] for o in _faa()["obligations"]}
    assert {
        "remote_pilot_certificate",
        "visual_line_of_sight",
        "night_and_twilight_lighting",
        "controlled_airspace_authorization",
        "flight_visibility",
        "cloud_clearance",
    } <= obligations


def test_the_faa_rulebook_follows_the_aircraft_and_stops_indoors() -> None:
    applies_to = _faa()["applies_to"]
    assert applies_to["profiles"] == ["drone"]
    assert applies_to["drive_types"] == ["multirotor", "fixed_wing", "vtol"]
    assert applies_to["unless_declared"][0]["key"] == "indoor"
    assert applies_to["unless_declared"][0]["allowed"] == [True]


def test_the_deployment_example_excepts_an_exceptable_faa_rule_with_a_higher_limit() -> None:
    deployment = _example("example-deployment.yaml")
    assert deployment["declarations"] == {"remote_id": "broadcast_module"}
    (exception,) = deployment["exceptions"]
    rulebook_id, rule_id = exception["rule"].split("/")
    assert rulebook_id == _faa()["rulebook_id"]
    rule = _rule(_faa(), rule_id)
    assert rule["exceptable"] is True
    assert "107W-EXAMPLE-0001" in exception["basis"] and "fictional" in exception["basis"]
    assert exception["limit"] == pytest.approx(500 * FEET)
    assert exception["limit"] > rule["cap"]["max"]
    assert ISO_DATE.match(exception["expires"])
    allowed = _rule(_faa(), "remote_identification")["require_declared"]["allowed"]
    assert deployment["declarations"]["remote_id"] in allowed


def test_the_warehouse_example_uses_the_organization_rule_kinds() -> None:
    rules = {r["id"]: r for r in _example("example-warehouse.yaml")["rules"]}
    assert rules["no_capture_in_private_rooms"]["forbid_primitive"]["in_zones"] == ["restroom", "hr_office"]
    assert rules["restricted_rooms"]["forbid_zone_entry"]["zones"] == ["server_room", "hazmat_cage"]
    assert rules["approved_programs_only"]["forbid_primitive"]["primitives"] == ["call_program"]
    assert rules["approved_programs_only"]["forbid_primitive"]["except_names"]
    assert rules["shared_aisle_speed"]["cap"] == {"quantity": "speed_m_per_s", "max": 1.5}


def test_the_industrial_template_carries_no_values() -> None:
    """ISO text is copyrighted: every limit and list stays FILL_IN, so an unfilled file fails to load."""
    template = _example("industrial-template.yaml")
    assert template["rulebook_id"] == "FILL_IN"
    assert template["reviewed"] == "FILL_IN"
    for rule in template["rules"]:
        (kind,) = set(rule) & RULE_KINDS
        body = rule[kind]
        if kind == "cap":
            assert body["max"] == "FILL_IN", rule["id"]
        else:
            lists = [v for k, v in body.items() if k in {"zones", "names", "except_names"}]
            assert lists and all(v == ["FILL_IN"] for v in lists), rule["id"]
    for entry in template["rules"] + template["obligations"]:
        assert "FILL_IN" in entry["cite"]["text"], entry["id"]


RULEBOOK_TEXTS = [
    ("us_faa_part107.yaml", lambda: BUNDLED.read_text(encoding="utf-8")),
    *[(p.name, lambda p=p: p.read_text(encoding="utf-8")) for p in sorted(EXAMPLES.glob("*"))],
]


@pytest.mark.parametrize(("name", "read"), RULEBOOK_TEXTS, ids=[n for n, _ in RULEBOOK_TEXTS])
def test_no_em_dash_in_the_rulebook_files(name: str, read: Any) -> None:
    assert chr(0x2014) not in read(), name
