"""URML MCP server.

Exposes URML's validate-before-actuate loop as Model Context Protocol tools so
any MCP-capable agent can check and run robot intent. The tool *logic* lives in
``urml_mcp.tools`` (pure functions, no MCP dependency, hermetically testable);
the transport wiring lives in ``urml_mcp.server``.

Design rule: the server is the safety boundary, never the model. It exposes
validation and execution, and never calls an LLM. The calling agent is already a
model; it emits the URML, the server checks and runs it. This keeps URML's
provider-neutrality intact by construction.
"""

from __future__ import annotations

from urml_mcp.tools import (
    AVAILABLE_PROFILES,
    describe_manifest,
    execute_program,
    get_contract,
    list_profiles,
    validate_program,
)

__all__ = [
    "AVAILABLE_PROFILES",
    "describe_manifest",
    "execute_program",
    "get_contract",
    "list_profiles",
    "validate_program",
]
