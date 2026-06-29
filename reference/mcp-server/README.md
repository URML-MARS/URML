<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

---

# URML MCP server

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes URML's validate-before-actuate loop as tools any MCP-capable agent (Claude Code, Cursor, VS Code, Goose, OpenHands, and the rest of the ecosystem) can call. Design and rationale: [`docs/integrations/mcp-server-scope.md`](../../docs/integrations/mcp-server-scope.md).

**The server is the safety boundary, never the model.** It exposes validation and execution and never calls an LLM. The calling agent is already a model: it emits the URML, the server checks and runs it. That keeps URML's provider-neutrality intact by construction and keeps the validator as the safety boundary.

## Tools

| Tool | What it does | Safety |
|---|---|---|
| `urml_get_contract` | Returns the Layer-4 system prompt + the URML program JSON Schema to emit against | read-only |
| `urml_validate` | Validates a program against a manifest + safety envelope; returns `accepted` + structured errors | read-only, the safety check |
| `urml_execute` | Runs a program against an adapter; re-validates first | gated, see below |
| `urml_list_profiles` | Lists available profiles (home, industrial, drone, educational, fleet) | read-only |
| `urml_describe_manifest` | Compact structural summary of a capability manifest | read-only |

There is no `translate` tool by design. The agent calls `urml_get_contract`, emits the URML itself, then `urml_validate`. No LLM is embedded.

## Execution gating

`urml_execute` defaults to the hermetic `mock` adapter (records calls, touches no hardware). The `ros2` and `px4` adapters actuate real hardware and are disabled unless:

- `URML_MCP_ALLOW_REAL_EXECUTE` is set to `1` (or `true`/`yes`/`on`), and
- the relevant runtime is available (`rclpy` + a sourced ROS 2 for `ros2`; `urml-px4-runtime` + a reachable PX4 for `px4`).

Optionally point `URML_MCP_ADAPTER_CONFIG` at an adapter-config YAML. Every execute re-validates before running; there is no path to an actuator that skips the validator.

## Install and run

```bash
pip install -e reference/validator
pip install -e reference/llm-bridge
pip install -e reference/ros2-runtime
pip install -e reference/mcp-server

urml-mcp        # runs over stdio
```

Register it with an MCP client by pointing the client at the `urml-mcp` command (stdio transport).

## Layout

```
reference/mcp-server/
  src/urml_mcp/
    tools.py      # pure tool logic (no MCP dependency, hermetically testable)
    server.py     # FastMCP wiring over stdio
  tests/
    test_tools.py # hermetic, reuses examples/home fixtures
```

The split is deliberate: `tools.py` has no MCP dependency, so the validate/execute guarantees are testable without the transport. Every command stays in lockstep with the `urml` CLI.

## Publishing to MCP registries (maintainer action)

[`server.json`](server.json) is the registry manifest for the [official MCP Registry](https://registry.modelcontextprotocol.io). Publishing is a maintainer action under the project's GitHub identity:

1. **Publish the package** so the registry can resolve it: `urml-mcp-server` to PyPI (the `server.json` `packages` entry references it). The registry does not host code, it points at a package.
2. **Publish the manifest** with the `mcp-publisher` CLI, which validates `server.json` and verifies ownership of the `io.github.urml-mars` namespace via GitHub login. Confirm the schema version and field casing against the CLI at publish time; the registry schema is still evolving.
3. **Directory listings**: Smithery, Glama, PulseMCP, and mcp.so crawl the ecosystem and let you claim ownership of the listing. Submit / claim under `greenvh@gmail.com`.

Track each listing like any other outreach (a row per venue, `response: none` until real adoption signal). Do not cite install counts as engagement without corroboration.

