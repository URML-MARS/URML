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

`urml_execute` defaults to the hermetic `mock` adapter (records calls, touches no hardware). The `ros2`, `px4` and `ardupilot` adapters actuate real hardware and are disabled unless:

- `URML_MCP_ALLOW_REAL_EXECUTE` is set to `1` (or `true`/`yes`/`on`),
- the operator pinned the manifest and the envelope when starting the server (see [Pin the deployment](#pin-the-deployment)), and
- the relevant runtime is available (`rclpy` + a sourced ROS 2 for `ros2`; `urml-px4-runtime` + a reachable PX4 for `px4`; `urml-ardupilot-runtime` + a reachable ArduCopter for `ardupilot`).

Optionally point `URML_MCP_ADAPTER_CONFIG` at an adapter-config YAML. Every execute validates the program before it builds a runtime or an adapter, and the runtime re-validates before running; there is no path to an actuator that skips the validator.

## Use it now, from GitHub (no PyPI needed)

The server runs today, straight from source. The PyPI packages are not published yet (they ship with the 0.2.0 release), so install the server together with its three dependencies from their git subdirectories in a single `pip install`. Passing all four URLs at once lets the `>=0.2.0` version pins resolve against these git builds instead of PyPI:

```bash
python -m venv .urml-mcp
. .urml-mcp/bin/activate                     # Windows: .urml-mcp\Scripts\activate

pip install \
  "git+https://github.com/URML-MARS/URML.git#subdirectory=reference/validator" \
  "git+https://github.com/URML-MARS/URML.git#subdirectory=reference/llm-bridge" \
  "git+https://github.com/URML-MARS/URML.git#subdirectory=reference/ros2-runtime" \
  "git+https://github.com/URML-MARS/URML.git#subdirectory=reference/mcp-server"

urml-mcp        # runs over stdio
```

`urml-ros2-runtime` carries the hermetic `mock` adapter, so `urml_execute` works with no ROS install and no hardware.

### Register it with an MCP client

Point the client at the `urml-mcp` command (stdio transport), using the absolute path to the `urml-mcp` inside the venv above (`.../.urml-mcp/bin/urml-mcp`, or `...\.urml-mcp\Scripts\urml-mcp.exe` on Windows):

```json
{
  "mcpServers": {
    "urml": {
      "command": "/absolute/path/to/.urml-mcp/bin/urml-mcp"
    }
  }
}
```

Claude Desktop (`claude_desktop_config.json`) and Cursor (`.cursor/mcp.json`) take that shape as-is; VS Code (`.vscode/mcp.json`) uses the same fields under a top-level `servers` key instead of `mcpServers`. The agent then holds the five URML tools: it emits URML, the server validates and runs it.

Once the 0.2.0 release is on PyPI, the four git URLs collapse to `pip install urml-mcp-server`.

## Pin the deployment

By default the agent passes the manifest, envelope, profiles and policy with each call. That suits the hermetic `mock` adapter. On a real robot the agent must not choose the rules it is checked against: it could pass a manifest that claims more than the robot can do, or leave the envelope out.

Pin them when you start the server, with env vars or the matching flags. A flag wins over its env var.

| Env var | Flag | Value |
|---|---|---|
| `URML_MCP_MANIFEST` | `--manifest` | Path to the robot's capability manifest |
| `URML_MCP_ENVELOPE` | `--envelope` | Path to the site's safety envelope |
| `URML_MCP_PROFILES` | `--profiles` | Comma-separated profiles, for example `home` or `drone,fleet` |
| `URML_MCP_POLICY` | `--policy` | Path to a compliance policy, `DEFAULT` for the bundled US-federal policy, or `none` |
| `URML_MCP_RULEBOOKS` | `--rulebooks` | Rulebook files (RFC-0702, Draft), separated by the OS path separator (`;` on Windows, `:` elsewhere) |
| `URML_MCP_DEFAULT_RULEBOOKS` | `--default-rulebooks` | `on` (the default) or `off` for the bundled rulebooks, such as the FAA Part 107 subset for aircraft |
| `URML_MCP_EVIDENCE_LOG` | `--evidence-log` | Path to a local JSON Lines file that receives one [validation record](../../docs/evidence/validation-records.md) per `urml_validate` and `urml_execute` verdict. Off when unset; no tool can change it |

```json
{
  "mcpServers": {
    "urml": {
      "command": "/absolute/path/to/.urml-mcp/bin/urml-mcp",
      "env": {
        "URML_MCP_MANIFEST": "/absolute/path/to/robot.manifest.yaml",
        "URML_MCP_ENVELOPE": "/absolute/path/to/site.envelope.yaml",
        "URML_MCP_PROFILES": "home",
        "URML_MCP_POLICY": "DEFAULT"
      }
    }
  }
}
```

Use absolute paths; MCP clients do not promise a working directory. To drive real hardware, also set `"URML_MCP_ALLOW_REAL_EXECUTE": "1"` in `env`.

What pinning does:

- The server reads each pinned file once, at startup, and checks it against its schema. A file that does not load stops the server with a message that names the env var or flag.
- Every tool uses the pinned values, so the agent can leave them out. `urml_get_contract` lists what is pinned.
- An agent value that differs from a pin is refused with a tool error before any runtime or adapter is built.
- `ros2`, `px4` and `ardupilot` run only with a pinned manifest and a pinned envelope. If the profiles are not pinned, a real adapter runs with no profiles and refuses profiles from the agent.
- Rulebooks are never agent values: no tool has an argument for them, pinned or not. A deployment rulebook can carry exceptions, so an agent that could pass one could grant itself a waiver. Every validation, and the runtime's re-validation, uses the operator's rulebooks, and the bundled rulebooks stay on unless the operator switches them off.

## Develop against a local checkout

```bash
pip install -e reference/validator
pip install -e reference/llm-bridge
pip install -e reference/ros2-runtime
pip install -e reference/mcp-server

urml-mcp        # runs over stdio
```

## Layout

```
reference/mcp-server/
  src/urml_mcp/
    tools.py        # pure tool logic and operator pins (no MCP dependency, hermetically testable)
    server.py       # FastMCP wiring over stdio
  tests/
    test_tools.py   # hermetic, reuses examples/home fixtures
    test_pinned.py  # pinned manifest, envelope, profiles and policy; the real-adapter gate
    test_server.py  # transport wiring; skips when the mcp SDK is not installed
```

The split is deliberate: `tools.py` has no MCP dependency, so the validate/execute guarantees are testable without the transport. Every command stays in lockstep with the `urml` CLI.

## Publishing to MCP registries (maintainer action)

[`server.json`](server.json) is the registry manifest for the [official MCP Registry](https://registry.modelcontextprotocol.io). The full playbook (PyPI first, then `mcp-publisher`, then the Smithery/Glama/PulseMCP/mcp.so directory claims) lives in [`SUBMISSIONS.md`](SUBMISSIONS.md). It is gated on the 0.2.0 core release ([`RELEASING.md`](../../RELEASING.md)), since the registry resolves the package from PyPI.

Track each listing in [`examples/lighthouses/distribution.yaml`](../../examples/lighthouses/distribution.yaml) (`response: none` until real adoption signal). Do not cite install counts as engagement without corroboration.

