"""Operator-pinned rulebooks on the MCP tools (RFC-0702, Draft).

A deployment rulebook can carry exceptions, so an agent that could supply one
could grant itself a waiver. The operator sets the rulebooks and the switch
for the bundled ones with URML_MCP_RULEBOOKS / URML_MCP_DEFAULT_RULEBOOKS (or
the matching flags); no tool takes them as an argument; every validation,
including the runtime's re-validation, uses them.
"""

from __future__ import annotations

import ast
import inspect
import os
from pathlib import Path
from typing import Any

import pytest
import yaml
from urml_ros2_runtime import RuntimeResult, ValidationRejectedError

from urml_mcp import tools

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"
EXAMPLE_RULEBOOKS = REPO_ROOT / "examples" / "rulebooks"
WAREHOUSE = FIXTURES / "manifests" / "warehouse_areas.yaml"
WAREHOUSE_RULES = EXAMPLE_RULEBOOKS / "example-warehouse.yaml"
WAIVER = EXAMPLE_RULEBOOKS / "example-deployment.yaml"
DRONE = FIXTURES / "manifests" / "drone_high_ceiling.yaml"

SERVER_ROOM = {
    "profile": "warehouse",
    "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "server_room"}}]},
}
FLIGHT_450 = {
    "profile": "drone",
    "behavior": {"type": "sequence", "steps": [{"take_off": {"altitude": 137.16}}, {"land": {}}]},
}


def _codes(result: dict[str, Any]) -> list[str]:
    return [err["code"] for err in result["errors"]]


def test_nothing_set_leaves_the_bundled_rulebooks_on() -> None:
    pins = tools.load_pinned({}, [])
    assert pins.rulebooks == () and pins.default_rulebooks is True
    assert "rule.cap_exceeded" in _codes(tools.validate_program(FLIGHT_450, str(DRONE), policy="none"))


def test_the_env_var_takes_paths_separated_by_the_os_path_separator() -> None:
    pins = tools.load_pinned(
        {"URML_MCP_RULEBOOKS": f" {WAREHOUSE_RULES}{os.pathsep}{WAIVER} ", "URML_MCP_DEFAULT_RULEBOOKS": "OFF"}, []
    )
    assert [book["rulebook_id"] for book in pins.rulebooks] == [
        "example_logistics_operations",
        "example_aerial_survey_north_tower",
    ]
    assert pins.rulebook_paths == (WAREHOUSE_RULES.resolve(), WAIVER.resolve())
    assert pins.default_rulebooks is False
    assert pins.names == ("rulebooks", "default_rulebooks")


def test_flags_win_over_the_env_vars(tmp_path: Path) -> None:
    pins = tools.load_pinned(
        {"URML_MCP_RULEBOOKS": str(tmp_path / "missing.yaml"), "URML_MCP_DEFAULT_RULEBOOKS": "off"},
        ["--rulebooks", str(WAIVER), "--default-rulebooks", "on"],
    )
    assert [book["rulebook_id"] for book in pins.rulebooks] == ["example_aerial_survey_north_tower"]
    assert pins.default_rulebooks is True and pins.names == ("rulebooks",)


@pytest.mark.parametrize(
    ("environ", "source"),
    [
        ({"URML_MCP_RULEBOOKS": "missing-rulebook.yaml"}, "URML_MCP_RULEBOOKS"),
        ({"URML_MCP_RULEBOOKS": str(EXAMPLE_RULEBOOKS / "industrial-template.yaml")}, "URML_MCP_RULEBOOKS"),
        ({"URML_MCP_DEFAULT_RULEBOOKS": "maybe"}, "URML_MCP_DEFAULT_RULEBOOKS"),
    ],
    ids=["missing", "breaks-the-format", "not-on-or-off"],
)
def test_a_bad_pin_stops_the_server_at_startup(environ: dict[str, str], source: str) -> None:
    with pytest.raises(tools.PinnedConfigError, match=source):
        tools.load_pinned(environ, [])


def test_validate_applies_the_pinned_rulebooks() -> None:
    pins = tools.load_pinned({"URML_MCP_MANIFEST": str(WAREHOUSE), "URML_MCP_RULEBOOKS": str(WAREHOUSE_RULES)}, [])
    out = tools.validate_program(SERVER_ROOM, profiles=["warehouse"], policy="none", pinned=pins)
    assert out["accepted"] is False and "rule.zone_forbidden" in _codes(out)
    assert [book["rulebook_id"] for book in out["rulebooks"]] == ["example_logistics_operations"]
    assert out["rulebooks"][0]["obligations"][0]["id"] == "trained_operators"


def test_the_default_switch_applies_to_validate() -> None:
    pins = tools.load_pinned({"URML_MCP_DEFAULT_RULEBOOKS": "off"}, [])
    out = tools.validate_program(FLIGHT_450, str(DRONE), policy="none", pinned=pins)
    assert out["accepted"] is True
    assert [w["code"] for w in out["warnings"]] == ["rule.defaults_disabled"]


def test_execute_refuses_before_any_runtime_is_built(monkeypatch: pytest.MonkeyPatch) -> None:
    def _refuse(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("_build_runtime was called")

    monkeypatch.setattr(tools, "_build_runtime", _refuse)
    pins = tools.load_pinned({"URML_MCP_MANIFEST": str(WAREHOUSE), "URML_MCP_RULEBOOKS": str(WAREHOUSE_RULES)}, [])
    with pytest.raises(ValidationRejectedError, match="rule.zone_forbidden"):
        tools.execute_program(SERVER_ROOM, profiles=["warehouse"], pinned=pins)


def test_execute_hands_the_pinned_rulebooks_to_the_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[dict[str, Any]] = []

    class _RecordingRuntime:
        def execute(self, program: Any, manifest: Any, **kwargs: Any) -> RuntimeResult:
            seen.append(kwargs)
            return RuntimeResult(success=True)

    monkeypatch.setattr(tools, "_build_runtime", lambda adapter: (_RecordingRuntime(), []))
    pins = tools.load_pinned(
        {"URML_MCP_MANIFEST": str(WAREHOUSE), "URML_MCP_RULEBOOKS": str(WAREHOUSE_RULES), "URML_MCP_DEFAULT_RULEBOOKS": "off"},
        [],
    )
    program = {"profile": "warehouse", "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "dock_a"}}]}}
    assert tools.execute_program(program, profiles=["warehouse"], pinned=pins)["success"] is True
    (kwargs,) = seen
    assert [book["rulebook_id"] for book in kwargs["rulebooks"]] == ["example_logistics_operations"]
    assert kwargs["default_rulebooks"] is False and kwargs["as_of"] is not None


def test_a_call_cannot_change_the_pinned_rulebooks() -> None:
    pins = tools.load_pinned({"URML_MCP_RULEBOOKS": str(WAREHOUSE_RULES)}, [])
    before = yaml.safe_dump(list(pins.rulebooks))
    tools.validate_program(SERVER_ROOM, str(WAREHOUSE), profiles=["warehouse"], pinned=pins)
    assert yaml.safe_dump(list(pins.rulebooks)) == before


@pytest.mark.parametrize("name", ["get_contract", "validate_program", "execute_program", "describe_manifest"])
def test_no_tool_takes_a_rulebook_argument(name: str) -> None:
    params = set(inspect.signature(getattr(tools, name)).parameters)
    assert not {p for p in params if "rulebook" in p}


def test_no_server_tool_takes_a_rulebook_argument() -> None:
    """The MCP tool schemas come from these signatures; read them without the mcp SDK."""
    tree = ast.parse((Path(tools.__file__).parent / "server.py").read_text(encoding="utf-8"))
    tool_args = {
        node.name: [arg.arg for arg in node.args.args + node.args.kwonlyargs]
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("urml_")
    }
    assert set(tool_args) == {
        "urml_get_contract", "urml_validate", "urml_execute", "urml_list_profiles", "urml_describe_manifest",
    }
    assert not [arg for args in tool_args.values() for arg in args if "rulebook" in arg]
