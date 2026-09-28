"""Hermetic tests for operator-pinned constraints on the MCP tools.

The agent proposes a program. The operator's manifest, envelope, profiles and
policy decide whether it runs. These tests hold that split in place:

- ``load_pinned`` reads the pins once, from flags or ``URML_MCP_*`` env vars,
  and a pin that does not load stops the server at startup;
- every tool uses the pinned values when the agent omits them;
- an agent value that differs from a pin is refused before any runtime or
  adapter is built;
- the real adapters refuse to run unless the manifest and the envelope are
  pinned, while the hermetic mock keeps working with no pins at all.
"""

from __future__ import annotations

import ast
import copy
import dataclasses
from pathlib import Path
from typing import Any

import pytest
import yaml
from urml_ros2_runtime import MockROSAdapter, RuntimeResult, URMLRuntime, ValidationRejectedError

from urml_mcp import tools

REPO_ROOT = Path(__file__).resolve().parents[3]
HOME = REPO_ROOT / "examples" / "home"
MANIFEST = HOME / "red-mug.manifest.yaml"
ENVELOPE = HOME / "red-mug.envelope.yaml"
PROGRAM = HOME / "red-mug.urml.yaml"
# Same robot with a CN-origin critical part: the bundled policy rejects it.
CN_MANIFEST = HOME / "red-mug.cn-critical.manifest.yaml"

ALLOW_REAL = "URML_MCP_ALLOW_REAL_EXECUTE"
PIN_ENV_VARS = ("URML_MCP_MANIFEST", "URML_MCP_ENVELOPE", "URML_MCP_PROFILES", "URML_MCP_POLICY")
REAL_ADAPTERS = ("ros2", "px4", "ardupilot", "autoware")

# 4 N is inside the manifest's 5 N gripper limit and above the envelope's 3 N
# cap, so only the envelope can reject it.
GRASP_4N: dict[str, Any] = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"detect": {"object": "mug", "store_as": "target"}},
            {"grasp": {"target": "$target", "force": 4.0}},
        ],
    },
}

# A site policy stricter than the bundled one: the red-mug gripper servo is
# JP-origin, so this policy rejects a manifest the bundled policy accepts.
SITE_POLICY_YAML = """\
policy_version: "0.1"
policy_id: test_site_policy
description: Test site policy that denies JP-origin critical parts.
issued_by: urml_mcp_tests
rules:
  - id: no_jp_critical_parts
    applies_to: { component_role: critical }
    deny:
      country_of_origin_in: [JP]
    on_violation:
      code: policy.country_denied
      message: JP-origin critical part denied by the site policy.
"""


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _codes(result: dict[str, Any]) -> list[str]:
    return [err["code"] for err in result["errors"]]


@pytest.fixture
def pinned() -> tools.Pinned:
    """Manifest, envelope and profiles pinned the way an operator would."""
    return tools.load_pinned(
        {
            "URML_MCP_MANIFEST": str(MANIFEST),
            "URML_MCP_ENVELOPE": str(ENVELOPE),
            "URML_MCP_PROFILES": "home",
        },
        [],
    )


@pytest.fixture
def no_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail the test if any runtime or adapter gets built."""

    def _refuse(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError(f"_build_runtime was called with {args!r}")

    monkeypatch.setattr(tools, "_build_runtime", _refuse)


@pytest.fixture
def site_policy(tmp_path: Path) -> Path:
    path = tmp_path / "site.policy.yaml"
    path.write_text(SITE_POLICY_YAML, encoding="utf-8")
    return path


# --- load_pinned: env and argv parsing ---------------------------------------


def test_nothing_set_pins_nothing() -> None:
    pins = tools.load_pinned({}, [])
    assert pins == tools.Pinned()
    assert pins.names == ()


def test_env_vars_pin_every_constraint() -> None:
    pins = tools.load_pinned(
        {
            "URML_MCP_MANIFEST": str(MANIFEST),
            "URML_MCP_ENVELOPE": str(ENVELOPE),
            "URML_MCP_PROFILES": " home , drone ",
            "URML_MCP_POLICY": "none",
        },
        [],
    )
    assert pins.manifest == _load(MANIFEST)
    assert pins.manifest_path == MANIFEST.resolve()
    assert pins.envelope == _load(ENVELOPE)
    assert pins.envelope_path == ENVELOPE.resolve()
    assert pins.profiles == ("home", "drone")
    assert pins.policy == "none"
    assert pins.names == ("manifest", "envelope", "profiles", "policy")


def test_flags_pin_every_constraint(site_policy: Path) -> None:
    pins = tools.load_pinned(
        {},
        [
            "--manifest", str(MANIFEST),
            "--envelope", str(ENVELOPE),
            "--profiles", "home",
            "--policy", str(site_policy),
        ],
    )
    assert pins.manifest == _load(MANIFEST)
    assert pins.envelope == _load(ENVELOPE)
    assert pins.profiles == ("home",)
    assert pins.policy == _load(site_policy)
    assert pins.policy_path == site_policy.resolve()


def test_flags_win_over_env(tmp_path: Path) -> None:
    pins = tools.load_pinned(
        {
            # The env manifest does not exist: it must never be read.
            "URML_MCP_MANIFEST": str(tmp_path / "missing.yaml"),
            "URML_MCP_PROFILES": "home",
            "URML_MCP_POLICY": "none",
        },
        ["--manifest", str(CN_MANIFEST), "--profiles", "industrial", "--policy", "DEFAULT"],
    )
    assert pins.manifest == _load(CN_MANIFEST)
    assert pins.profiles == ("industrial",)
    assert pins.policy == "DEFAULT"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("DEFAULT", "DEFAULT"), ("default", "DEFAULT"), ("none", "none"), ("NONE", "none")],
)
def test_policy_literals(raw: str, expected: str) -> None:
    assert tools.load_pinned({"URML_MCP_POLICY": raw}, []).policy == expected


def test_blank_values_pin_nothing() -> None:
    blanks = {var: "  " for var in PIN_ENV_VARS}
    assert tools.load_pinned(blanks, []) == tools.Pinned()


@pytest.mark.parametrize("env_var", ["URML_MCP_MANIFEST", "URML_MCP_ENVELOPE", "URML_MCP_POLICY"])
def test_missing_pinned_file_fails_fast(env_var: str, tmp_path: Path) -> None:
    with pytest.raises(tools.PinnedConfigError, match=env_var):
        tools.load_pinned({env_var: str(tmp_path / "missing.yaml")}, [])


@pytest.mark.parametrize("env_var", ["URML_MCP_MANIFEST", "URML_MCP_ENVELOPE", "URML_MCP_POLICY"])
def test_schema_invalid_pinned_file_fails_fast(env_var: str, tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("not_a_field_of_any_schema: 1\n", encoding="utf-8")
    with pytest.raises(tools.PinnedConfigError, match=env_var):
        tools.load_pinned({env_var: str(bad)}, [])


def test_non_mapping_pinned_file_fails_fast(tmp_path: Path) -> None:
    bad = tmp_path / "list.yaml"
    bad.write_text("- just\n- a list\n", encoding="utf-8")
    with pytest.raises(tools.PinnedConfigError, match="--manifest"):
        tools.load_pinned({}, ["--manifest", str(bad)])


def test_profiles_with_no_names_fail_fast() -> None:
    with pytest.raises(tools.PinnedConfigError, match="URML_MCP_PROFILES"):
        tools.load_pinned({"URML_MCP_PROFILES": " , ,"}, [])


def test_unknown_flag_exits_with_usage() -> None:
    with pytest.raises(SystemExit):
        tools.load_pinned({}, ["--bogus"])


def test_pins_are_frozen(pinned: tools.Pinned) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        pinned.manifest = {}  # type: ignore[misc]


# --- pinned values are used ---------------------------------------------------


def test_validate_uses_the_pinned_envelope(pinned: tools.Pinned) -> None:
    # The agent passes only the program: the pinned envelope rejects the 4 N grasp.
    out = tools.validate_program(GRASP_4N, pinned=pinned)
    assert out["accepted"] is False
    assert "envelope.force_exceeded" in _codes(out)
    # Without the pin, the agent could drop the envelope and pass.
    assert tools.validate_program(GRASP_4N, str(MANIFEST), profiles=["home"])["accepted"] is True


def test_validate_accepts_agent_values_equal_to_the_pins(pinned: tools.Pinned) -> None:
    out = tools.validate_program(str(PROGRAM), _load(MANIFEST), str(ENVELOPE), ["home"], pinned=pinned)
    assert out["accepted"] is True


def test_validate_uses_the_pinned_policy() -> None:
    pins = tools.load_pinned({"URML_MCP_MANIFEST": str(CN_MANIFEST), "URML_MCP_POLICY": "none"}, [])
    assert tools.validate_program(str(PROGRAM), profiles=["home"], pinned=pins)["accepted"] is True
    # Unpinned, the bundled policy rejects the same manifest.
    unpinned = tools.validate_program(str(PROGRAM), str(CN_MANIFEST), profiles=["home"])
    assert "policy.country_denied" in _codes(unpinned)


def test_validate_applies_the_pinned_site_policy(site_policy: Path) -> None:
    pins = tools.load_pinned({"URML_MCP_MANIFEST": str(MANIFEST), "URML_MCP_POLICY": str(site_policy)}, [])
    out = tools.validate_program(str(PROGRAM), profiles=["home"], pinned=pins)
    assert "policy.country_denied" in _codes(out)


def test_get_contract_uses_the_pins(pinned: tools.Pinned) -> None:
    out = tools.get_contract(pinned=pinned)
    assert out["profiles"] == ["home"]
    assert out["pinned"] == ["manifest", "envelope", "profiles"]
    expected = tools.get_contract(str(MANIFEST), ["home"], str(ENVELOPE))
    assert out["system_prompt"] == expected["system_prompt"]
    assert expected["pinned"] == []


def test_describe_manifest_uses_the_pin(pinned: tools.Pinned) -> None:
    assert tools.describe_manifest(pinned=pinned) == tools.describe_manifest(str(MANIFEST))


def test_execute_uses_the_pinned_envelope(pinned: tools.Pinned, no_runtime: None) -> None:
    with pytest.raises(ValidationRejectedError, match="envelope.force_exceeded"):
        tools.execute_program(GRASP_4N, adapter="mock", pinned=pinned)


def test_execute_applies_the_pinned_site_policy(site_policy: Path, no_runtime: None) -> None:
    # The runtime re-validates with the bundled policy only, so the pinned
    # site policy has to be applied before the runtime is built.
    pins = tools.load_pinned({"URML_MCP_MANIFEST": str(MANIFEST), "URML_MCP_POLICY": str(site_policy)}, [])
    with pytest.raises(ValidationRejectedError, match="policy.country_denied"):
        tools.execute_program(str(PROGRAM), profiles=["home"], adapter="mock", pinned=pins)


def test_execute_hands_the_pinned_values_to_the_runtime(
    monkeypatch: pytest.MonkeyPatch, pinned: tools.Pinned
) -> None:
    calls: list[tuple[Any, Any, Any]] = []
    rulebook_kwargs: list[dict[str, Any]] = []

    class _RecordingRuntime:
        def execute(
            self,
            program: Any,
            manifest: Any,
            envelope: Any = None,
            profiles: tuple[str, ...] = (),
            **kwargs: Any,
        ) -> RuntimeResult:
            calls.append((manifest, envelope, profiles))
            rulebook_kwargs.append(kwargs)
            return RuntimeResult(success=True)

    monkeypatch.setattr(tools, "_build_runtime", lambda adapter, **_: (_RecordingRuntime(), []))
    assert tools.execute_program(str(PROGRAM), pinned=pinned)["success"] is True
    assert calls == [(_load(MANIFEST), _load(ENVELOPE), ("home",))]
    # RFC-0702: the runtime re-validates with the operator's rulebooks (none
    # pinned here) and the bundled ones on.
    (kwargs,) = rulebook_kwargs
    assert kwargs["rulebooks"] == [] and kwargs["default_rulebooks"] is True
    assert kwargs["as_of"] is not None


def test_execute_mock_runs_with_pins(pinned: tools.Pinned) -> None:
    out = tools.execute_program(str(PROGRAM), pinned=pinned)
    assert out["success"] is True
    assert out["steps_executed"] >= 1


def test_calls_do_not_change_the_pins(pinned: tools.Pinned) -> None:
    before = copy.deepcopy(dataclasses.asdict(pinned))
    tools.get_contract(pinned=pinned)
    tools.validate_program(str(PROGRAM), pinned=pinned)
    tools.execute_program(str(PROGRAM), pinned=pinned)
    assert dataclasses.asdict(pinned) == before


# --- differing agent values are refused before anything is built -------------


@pytest.mark.parametrize(
    "override",
    [
        {"manifest": {}},
        {"manifest": str(CN_MANIFEST)},
        {"envelope": {"envelope_version": "0.1", "deployment_id": "agent_pick", "max_velocity": 5.0}},
        {"profiles": ["home", "educational"]},
        {"profiles": []},
    ],
    ids=["empty-manifest", "other-manifest", "loose-envelope", "extra-profile", "no-profiles"],
)
@pytest.mark.parametrize("adapter", ["mock", "ros2"])
def test_execute_refuses_values_that_differ_from_the_pins(
    monkeypatch: pytest.MonkeyPatch,
    pinned: tools.Pinned,
    no_runtime: None,
    override: dict[str, Any],
    adapter: str,
) -> None:
    monkeypatch.setenv(ALLOW_REAL, "1")
    with pytest.raises(PermissionError, match="pinned"):
        tools.execute_program(str(PROGRAM), adapter=adapter, pinned=pinned, **override)


@pytest.mark.parametrize(
    "override",
    [
        {"manifest": {}},
        {"envelope": {"envelope_version": "0.1", "deployment_id": "agent_pick"}},
        {"profiles": ["educational"]},
    ],
    ids=["empty-manifest", "other-envelope", "other-profiles"],
)
def test_validate_refuses_values_that_differ_from_the_pins(
    pinned: tools.Pinned, override: dict[str, Any]
) -> None:
    with pytest.raises(PermissionError, match="pinned"):
        tools.validate_program(str(PROGRAM), pinned=pinned, **override)


def test_validate_refuses_a_policy_that_differs_from_the_pin() -> None:
    pins = tools.load_pinned({"URML_MCP_MANIFEST": str(MANIFEST), "URML_MCP_POLICY": "DEFAULT"}, [])
    with pytest.raises(PermissionError, match="policy"):
        tools.validate_program(str(PROGRAM), profiles=["home"], policy="none", pinned=pins)
    # Repeating the pinned value is fine.
    out = tools.validate_program(str(PROGRAM), profiles=["home"], policy="default", pinned=pins)
    assert out["accepted"] is True


def test_get_contract_refuses_a_different_manifest(pinned: tools.Pinned) -> None:
    with pytest.raises(PermissionError, match="manifest"):
        tools.get_contract({}, pinned=pinned)


def test_describe_manifest_refuses_a_different_manifest(pinned: tools.Pinned) -> None:
    with pytest.raises(PermissionError, match="manifest"):
        tools.describe_manifest(str(CN_MANIFEST), pinned=pinned)


def test_manifest_is_required_when_not_pinned() -> None:
    with pytest.raises(ValueError, match="URML_MCP_MANIFEST"):
        tools.validate_program(str(PROGRAM))


def test_rejected_program_builds_no_runtime(no_runtime: None) -> None:
    with pytest.raises(ValidationRejectedError):
        tools.execute_program(str(PROGRAM), {}, profiles=["home"], adapter="mock")


# --- real adapters need the operator's pins -----------------------------------


@pytest.mark.parametrize("adapter", REAL_ADAPTERS)
def test_real_adapter_refused_without_pins(
    monkeypatch: pytest.MonkeyPatch, no_runtime: None, adapter: str
) -> None:
    monkeypatch.setenv(ALLOW_REAL, "1")
    # The agent's own manifest and envelope do not count.
    with pytest.raises(PermissionError, match="URML_MCP_MANIFEST") as exc:
        tools.execute_program(str(PROGRAM), str(MANIFEST), str(ENVELOPE), ["home"], adapter=adapter)
    assert "URML_MCP_ENVELOPE" in str(exc.value)


@pytest.mark.parametrize("adapter", REAL_ADAPTERS)
def test_real_adapter_refused_with_only_the_manifest_pinned(
    monkeypatch: pytest.MonkeyPatch, no_runtime: None, adapter: str
) -> None:
    monkeypatch.setenv(ALLOW_REAL, "1")
    pins = tools.load_pinned({"URML_MCP_MANIFEST": str(MANIFEST)}, [])
    with pytest.raises(PermissionError, match="URML_MCP_ENVELOPE"):
        tools.execute_program(str(PROGRAM), adapter=adapter, pinned=pins)


@pytest.mark.parametrize("adapter", REAL_ADAPTERS)
def test_real_adapter_still_needs_the_opt_in(
    monkeypatch: pytest.MonkeyPatch, no_runtime: None, pinned: tools.Pinned, adapter: str
) -> None:
    monkeypatch.delenv(ALLOW_REAL, raising=False)
    with pytest.raises(PermissionError, match=ALLOW_REAL):
        tools.execute_program(str(PROGRAM), adapter=adapter, pinned=pinned)


def test_real_adapter_refuses_agent_profiles_when_profiles_are_not_pinned(
    monkeypatch: pytest.MonkeyPatch, no_runtime: None
) -> None:
    monkeypatch.setenv(ALLOW_REAL, "1")
    pins = tools.load_pinned({"URML_MCP_MANIFEST": str(MANIFEST), "URML_MCP_ENVELOPE": str(ENVELOPE)}, [])
    with pytest.raises(PermissionError, match="URML_MCP_PROFILES"):
        tools.execute_program(str(PROGRAM), profiles=["educational"], adapter="ros2", pinned=pins)


def test_real_adapter_runs_with_pins_and_opt_in(monkeypatch: pytest.MonkeyPatch, pinned: tools.Pinned) -> None:
    # The recording mock stands in for the substrate: the gate is under test.
    built: list[str] = []

    def _build(adapter: str, **_: Any) -> tuple[Any, list[Any]]:
        built.append(adapter)
        return URMLRuntime(MockROSAdapter()), []

    monkeypatch.setattr(tools, "_build_runtime", _build)
    monkeypatch.setenv(ALLOW_REAL, "1")
    out = tools.execute_program(str(PROGRAM), adapter="ros2", pinned=pinned)
    assert out["success"] is True
    assert built == ["ros2"]


def test_mock_needs_no_pins_and_no_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in (ALLOW_REAL, *PIN_ENV_VARS):
        monkeypatch.delenv(var, raising=False)
    out = tools.execute_program(str(PROGRAM), str(MANIFEST), str(ENVELOPE), ["home"], adapter="mock")
    assert out["success"] is True


# --- the pure/transport split -------------------------------------------------


def test_tools_module_does_not_import_mcp() -> None:
    tree = ast.parse(Path(tools.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "mcp" not in imported
