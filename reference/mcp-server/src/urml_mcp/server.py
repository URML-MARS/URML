"""MCP transport wiring for URML.

Registers the tools from ``urml_mcp.tools`` on a FastMCP server and runs it over
stdio (what Claude Code, Cursor, VS Code, and most local MCP clients use). The
tool docstrings become the tool descriptions an agent reads.

Run it directly with ``urml-mcp`` (installed console script) or
``python -m urml_mcp.server``.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from urml_mcp import tools

mcp = FastMCP("urml")


@mcp.tool()
def urml_get_contract(
    manifest: dict[str, Any],
    profiles: list[str] | None = None,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the Layer-4 contract to emit URML against: the system prompt plus
    the URML program JSON Schema, given a robot capability manifest and optional
    safety envelope and profiles. Call this first, emit a URML program yourself,
    then call urml_validate. The server never calls an LLM."""
    return tools.get_contract(manifest, profiles or (), envelope)


@mcp.tool()
def urml_validate(
    program: dict[str, Any],
    manifest: dict[str, Any],
    envelope: dict[str, Any] | None = None,
    profiles: list[str] | None = None,
    policy: str = "DEFAULT",
) -> dict[str, Any]:
    """Validate a URML program against a robot's capability manifest and safety
    envelope. This is the safety check and it is read-only. Returns accepted plus
    structured errors and warnings. policy is 'DEFAULT' (bundled US-federal
    compliance), 'none' to skip compliance, or a policy object."""
    return tools.validate_program(program, manifest, envelope, profiles or (), policy)


@mcp.tool()
def urml_execute(
    program: dict[str, Any],
    manifest: dict[str, Any],
    envelope: dict[str, Any] | None = None,
    profiles: list[str] | None = None,
    adapter: str = "mock",
) -> dict[str, Any]:
    """Execute a URML program against a substrate adapter and return the run
    trace. adapter defaults to 'mock' (hermetic, no hardware). 'ros2' and 'px4'
    actuate real hardware and require the URML_MCP_ALLOW_REAL_EXECUTE env var to
    be set plus the relevant runtime. The runtime re-validates before running;
    nothing reaches an actuator without passing the validator."""
    return tools.execute_program(program, manifest, envelope, profiles or (), adapter)


@mcp.tool()
def urml_list_profiles() -> dict[str, Any]:
    """List the URML profiles available (home, industrial, drone, educational,
    fleet) with a one-line description of each."""
    return tools.list_profiles()


@mcp.tool()
def urml_describe_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return a compact structural summary of a capability manifest so you can
    see what a robot declares before emitting intent."""
    return tools.describe_manifest(manifest)


def main() -> None:
    """Console-script entry point: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
