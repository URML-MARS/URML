"""Hermetic tests for the URML MCP tool logic.

These test ``urml_mcp.tools`` directly (no MCP transport, no network, no
hardware), reusing the committed home-profile fixtures. They are the conformance
bar for the tool layer: the same translate -> validate -> execute guarantees the
CLI gives, exposed as MCP tools.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from urml_mcp import tools

REPO_ROOT = Path(__file__).resolve().parents[3]
HOME = REPO_ROOT / "examples" / "home"
MANIFEST = HOME / "red-mug.manifest.yaml"
PROGRAM = HOME / "red-mug.urml.yaml"


def test_get_contract_returns_prompt_and_schema() -> None:
    out = tools.get_contract(str(MANIFEST), profiles=["home"])
    assert isinstance(out["system_prompt"], str) and out["system_prompt"]
    assert isinstance(out["program_schema"], dict)
    assert out["profiles"] == ["home"]


def test_validate_accepts_the_good_program() -> None:
    out = tools.validate_program(str(PROGRAM), str(MANIFEST), profiles=["home"])
    assert out["accepted"] is True
    assert out["errors"] == []


def test_validate_rejects_against_empty_manifest() -> None:
    # The program needs capabilities an empty manifest does not declare.
    out = tools.validate_program(str(PROGRAM), {}, profiles=["home"])
    assert out["accepted"] is False
    assert len(out["errors"]) > 0
    # Errors carry the documented structured shape.
    err = out["errors"][0]
    assert "code" in err and "message" in err


def test_execute_mock_runs_the_program() -> None:
    out = tools.execute_program(str(PROGRAM), str(MANIFEST), profiles=["home"], adapter="mock")
    assert out["success"] is True
    assert out["steps_executed"] >= 1
    assert isinstance(out["audit_log"], list)


def test_execute_real_adapter_is_gated_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("URML_MCP_ALLOW_REAL_EXECUTE", raising=False)
    with pytest.raises(PermissionError):
        tools.execute_program(str(PROGRAM), str(MANIFEST), profiles=["home"], adapter="ros2")


def test_execute_unknown_adapter_errors() -> None:
    with pytest.raises(ValueError):
        tools.execute_program(str(PROGRAM), str(MANIFEST), adapter="bogus")


def test_list_profiles_includes_home() -> None:
    names = [p["name"] for p in tools.list_profiles()["profiles"]]
    assert "home" in names
    assert "industrial" in names


def test_describe_manifest_summarizes_structure() -> None:
    out = tools.describe_manifest(str(MANIFEST))
    assert isinstance(out["top_level_keys"], list) and out["top_level_keys"]
    assert "summary" in out


def test_as_dict_accepts_mapping_and_path() -> None:
    assert tools._as_dict({"a": 1}, kind="x") == {"a": 1}
    loaded = tools._as_dict(str(MANIFEST), kind="manifest")
    assert isinstance(loaded, dict)
    with pytest.raises(FileNotFoundError):
        tools._as_dict("does/not/exist.yaml", kind="manifest")


def test_profiles_tuple_normalizes_inputs() -> None:
    assert tools._profiles_tuple(None) == ()
    assert tools._profiles_tuple("home, drone") == ("home", "drone")
    assert tools._profiles_tuple(["home", "drone"]) == ("home", "drone")
