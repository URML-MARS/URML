"""MCP transport wiring for URML.

Registers the tools from ``urml_mcp.tools`` on a FastMCP server and runs it over
stdio (what Claude Code, Cursor, VS Code, and most local MCP clients use). The
tool docstrings become the tool descriptions an agent reads.

Run it directly with ``urml-mcp`` (installed console script) or
``python -m urml_mcp.server``. The operator pins the manifest, envelope,
profiles, policy and rulebooks with flags or ``URML_MCP_*`` env vars (see
``main``). No tool takes a rulebook as an argument.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from typing import Any

from mcp.server.fastmcp import FastMCP

from urml_mcp import tools

mcp = FastMCP("urml")

#: The operator's pinned constraints. ``main`` loads them once, before serving.
_PINNED = tools.Pinned()


@mcp.tool()
def urml_get_contract(
    manifest: dict[str, Any] | None = None,
    profiles: list[str] | None = None,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the Layer-4 contract to emit URML against: the system prompt plus
    the URML program JSON Schema, given a robot capability manifest and optional
    safety envelope and profiles. Call this first, emit a URML program yourself,
    then call urml_validate. The server never calls an LLM. If the operator
    pinned the manifest, envelope or profiles, omit them: the pinned values are
    used, a different value is refused, and the result lists what is pinned."""
    return tools.get_contract(manifest, profiles, envelope, pinned=_PINNED)


@mcp.tool()
def urml_validate(
    program: dict[str, Any],
    manifest: dict[str, Any] | None = None,
    envelope: dict[str, Any] | None = None,
    profiles: list[str] | None = None,
    policy: str | None = None,
) -> dict[str, Any]:
    """Validate a URML program against a robot's capability manifest and safety
    envelope. This is the safety check and it is read-only. Returns accepted plus
    structured errors and warnings. policy is 'DEFAULT' (bundled US-federal
    compliance, the default) or 'none' to skip compliance. If the operator
    pinned the manifest, envelope, profiles or policy, omit them: the pinned
    values are used and a different value is refused. Rulebooks (government
    and company rules, rule.* codes) are set by the operator only and apply to
    every call; the result lists them with their obligations."""
    return tools.validate_program(program, manifest, envelope, profiles, policy, pinned=_PINNED)


@mcp.tool()
def urml_execute(
    program: dict[str, Any],
    manifest: dict[str, Any] | None = None,
    envelope: dict[str, Any] | None = None,
    profiles: list[str] | None = None,
    adapter: str = "mock",
) -> dict[str, Any]:
    """Execute a URML program against a substrate adapter and return the run
    trace. adapter defaults to 'mock' (hermetic, no hardware). 'ros2', 'px4' and
    'ardupilot' actuate real hardware: they need the URML_MCP_ALLOW_REAL_EXECUTE
    env var, a manifest and an envelope pinned by the operator, and the relevant
    runtime. The program is validated before any runtime or adapter is built,
    and the runtime re-validates before running; nothing reaches an actuator
    without passing the validator. If the operator pinned the manifest, envelope
    or profiles, omit them: the pinned values are used and a different value is
    refused. The operator's rulebooks apply to both checks."""
    return tools.execute_program(program, manifest, envelope, profiles, adapter, pinned=_PINNED)


@mcp.tool()
def urml_list_profiles() -> dict[str, Any]:
    """List the URML profiles available (home, industrial, drone, educational,
    fleet) with a one-line description of each."""
    return tools.list_profiles()


@mcp.tool()
def urml_describe_manifest(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a compact structural summary of a capability manifest so you can
    see what a robot declares before emitting intent. Omit manifest to describe
    the one the operator pinned."""
    return tools.describe_manifest(manifest, pinned=_PINNED)


def main(argv: Sequence[str] | None = None) -> None:
    """Console-script entry point: load the operator's pins, then serve over stdio.

    Pins come from ``--manifest``, ``--envelope``, ``--profiles``,
    ``--policy``, ``--rulebooks`` and ``--default-rulebooks``, or the matching
    ``URML_MCP_*`` env vars; a flag wins over its env var. A pinned file that
    does not load stops the server before it serves a single call.
    """
    global _PINNED
    try:
        _PINNED = tools.load_pinned(os.environ, sys.argv[1:] if argv is None else argv)
    except tools.PinnedConfigError as exc:
        raise SystemExit(f"urml-mcp: {exc}") from exc
    if _PINNED.names:
        # stdout carries the MCP protocol, so the note goes to stderr.
        print(f"urml-mcp: pinned {', '.join(_PINNED.names)}", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
