<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

---

# URML MCP server: scope and design (for review, not yet built)

A scoping document for a URML [Model Context Protocol](https://modelcontextprotocol.io) server. This is a plan to approve before building, not an implemented feature.

## Goal

Ship a URML MCP server so any MCP-capable agent or client (Claude, Cursor, VS Code, Goose, OpenHands, and the rest of the MCP ecosystem) can call URML's validate-before-actuate loop as native tools, and discover it through the MCP registries (the official Registry, Smithery, Glama, PulseMCP, mcp.so).

This is the callable sibling of the [agent skill](../../.github/skills/urml-robot-intent/SKILL.md): the skill teaches an agent the loop in prose; the MCP server exposes the loop as tools the agent invokes directly. Together they are the agent-adoption surface for URML, complementing the third-party outreach in [RFC-0640](../rfcs/0640-moltbook.md).

## Design principle: the server is the safety boundary, never the model

The MCP server exposes validation and execution. It does **not** call an LLM. The calling agent is already a model; it emits the URML, the server checks and runs it. This keeps URML's provider-neutrality intact by construction (the server privileges no LLM and embeds no provider) and keeps the validator as the safety boundary, exactly as the CLI does.

So there is no `translate` tool. The agent uses `get_contract` to learn the target, emits URML itself, then calls `validate` and `execute`.

## Tools exposed

| Tool | Input | Output | Safety |
|---|---|---|---|
| `urml_get_contract` | manifest, profiles, optional envelope | the Layer-4 system prompt + the URML program JSON Schema the agent should emit against | read-only |
| `urml_validate` | program, manifest, optional envelope, profiles | `ValidationResult`: accepted flag + structured errors (`{code, primitive, path, field, message, suggestion}`) | read-only, the safety check |
| `urml_execute` | program, manifest, adapter (default `mock`) | step-by-step execution trace; re-validates first (defense in depth) | **gated**, see below |
| `urml_list_profiles` | none | available profiles (home, industrial, drone, ...) | read-only |
| `urml_describe_manifest` | manifest | compact capability summary the agent can reason over | read-only |

Each tool is a thin wrapper over the existing `urml_validator` / runtime functions the CLI already calls. No new validation logic.

## Execution gating (the one real risk)

`urml_validate` and the read-only tools are safe to expose to any agent. `urml_execute` actuates, so:

- Default adapter is `mock` (hermetic, records calls, touches no hardware).
- Real adapters (`ros2`, `px4`) require explicit server-side opt-in (a config flag or env var). The server never drives real hardware from an unconfigured default.
- `urml_execute` always re-validates before running, the same defense-in-depth the CLI uses. There is no fast path that skips the validator.

## Packaging and transport

- New package `reference/mcp-server/` (Python, the official `mcp` SDK). It depends on `urml-validator` (always) and `urml-ros2-runtime` (only for the `mock`/`ros2` execute path). No cloud dependency: a stdio MCP server is local, so it stays inside the no-cloud-in-`reference` rule.
- Transport: **stdio** first (local, what Claude Code / Cursor / VS Code use). An optional streamable-HTTP variant for hosted registries (Smithery remote) would be a separate deployment concern, kept out of the core package.
- Tests: hermetic, reusing the existing fixtures (`examples/home/red-mug.*`) and the `mock` adapter. Every tool exercised end to end with no network.

## Distribution

Once built, list it where agents discover MCP servers:

- **Official MCP Registry**: publish a `server.json` under a name URML proves it owns.
- **Smithery**: install/CLI + optional hosted endpoint.
- **Glama, PulseMCP, mcp.so**: directory listings (these crawl and let you claim ownership).

These listings are outreach-ledger-trackable the same way GitHub targets are. Contact `greenvh@gmail.com`.

## Effort estimate

Small to moderate. One package, five thin tools over existing functions, stdio transport via the official SDK, hermetic tests. The bulk of the work is schema plumbing for the tool inputs/outputs and the execute-gating config, not new logic.

## Open questions (for the founder)

1. **Package home**: `reference/mcp-server/` (treats it as a reference integration) versus `tools/urml-mcp/` (treats it as tooling). The no-cloud rule allows either; `reference/` signals it is a first-class, conformance-grade integration.
2. **Expose `urml_execute` at all**, or ship validate-only first and add execute behind a later opt-in? Validate-only is the lowest-risk launch and still useful (an agent can check admissibility without running anything).
3. **Hosted variant**: do we want a Smithery-hosted remote endpoint, or stdio/local only for the first release? Hosted implies a deployment surface (commercial-adjacent, separate repo per CLAUDE.md).
4. **Naming**: `urml`, `urml-mcp`, or `urml-robot-intent` (matching the skill name) for the registry identity.

## Recommendation

Build a **validate-first, stdio, local** MCP server in `reference/mcp-server/` (the read-only tools plus `urml_execute` gated to `mock` by default), list it on the official Registry + Smithery + Glama + PulseMCP, and defer the hosted HTTP variant. That is the lowest-risk, highest-fit slice: it puts URML's safety check one tool-call away for the entire MCP ecosystem without taking on a deployment or a hardware-actuation surface on day one.
