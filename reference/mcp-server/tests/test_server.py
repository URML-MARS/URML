"""Transport-level tests for the URML MCP server.

These need the ``mcp`` SDK and skip without it, so the pure tool tests still
run on a host that lacks it. They cover the wiring the pure tests cannot see:
the agent-facing tool schemas, the startup fail-fast on a bad pin, and a
refusal reaching the agent as a tool error over the MCP protocol.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

pytest.importorskip("mcp.server.fastmcp")

import anyio  # noqa: E402  (a dependency of the mcp SDK)
from mcp.shared.memory import create_connected_server_and_client_session  # noqa: E402

from urml_mcp import server, tools  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
HOME = REPO_ROOT / "examples" / "home"
MANIFEST = HOME / "red-mug.manifest.yaml"
ENVELOPE = HOME / "red-mug.envelope.yaml"
PROGRAM = HOME / "red-mug.urml.yaml"
PIN_ENV_VARS = ("URML_MCP_MANIFEST", "URML_MCP_ENVELOPE", "URML_MCP_PROFILES", "URML_MCP_POLICY")


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


@pytest.fixture(autouse=True)
def _unpinned(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every test unpinned and restore the module state afterwards."""
    monkeypatch.setattr(server, "_PINNED", tools.Pinned())
    for var in PIN_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def test_no_tool_requires_a_manifest() -> None:
    listed = anyio.run(server.mcp.list_tools)
    required = {tool.name: set(tool.inputSchema.get("required", [])) for tool in listed}
    assert required["urml_validate"] == {"program"}
    assert required["urml_execute"] == {"program"}
    assert required["urml_get_contract"] == set()
    assert required["urml_describe_manifest"] == set()


def test_main_fails_fast_when_a_pin_does_not_load(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(server.mcp, "run", lambda *a, **k: pytest.fail("the server started"))
    with pytest.raises(SystemExit) as exc:
        server.main(["--manifest", str(tmp_path / "missing.yaml")])
    assert "--manifest" in str(exc.value.code)


def test_main_pins_then_serves(monkeypatch: pytest.MonkeyPatch) -> None:
    started: list[bool] = []
    monkeypatch.setattr(server.mcp, "run", lambda *a, **k: started.append(True))
    monkeypatch.setenv("URML_MCP_ENVELOPE", str(ENVELOPE))
    server.main(["--manifest", str(MANIFEST), "--profiles", "home"])
    assert started == [True]
    assert server._PINNED.names == ("manifest", "envelope", "profiles")
    # A pinned deployment needs nothing but the program from the agent.
    assert server.urml_validate(program=_load(PROGRAM))["accepted"] is True
    assert server.urml_describe_manifest() == tools.describe_manifest(str(MANIFEST))


def test_refusal_reaches_the_agent_as_a_tool_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "_PINNED", tools.load_pinned({"URML_MCP_MANIFEST": str(MANIFEST)}, []))

    async def _call() -> Any:
        async with create_connected_server_and_client_session(server.mcp._mcp_server) as client:
            return await client.call_tool("urml_validate", {"program": _load(PROGRAM), "manifest": {}})

    result = anyio.run(_call)
    assert result.isError is True
    assert "pinned" in result.content[0].text
