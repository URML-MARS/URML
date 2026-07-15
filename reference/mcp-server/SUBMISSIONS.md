<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

---

# MCP registry submissions (maintainer action)

Ready-to-run playbook for publishing the URML MCP server to PyPI and the MCP
directories. The in-repo [`server.json`](server.json) is the single source; the
entries here point back to it. These steps need the maintainer's PyPI and GitHub
identity, so they are drafted for the founder to run. Contact field everywhere:
`greenvh@gmail.com`. Track progress in
[`examples/lighthouses/distribution.yaml`](../../examples/lighthouses/distribution.yaml)
(the `track: mcp` rows).

Publishing is irreversible and outward-facing. Nothing here goes live until the
0.2.0 core release is on PyPI.

---

## Prerequisite: the 0.2.0 core release (blocking)

The package `urml-mcp-server` depends on `urml-validator>=0.2.0`,
`urml-llm-bridge>=0.2.0`, and `urml-ros2-runtime>=0.2.0` (the `mock` adapter
lives in ros2-runtime). PyPI resolves those at install time, so they must be on
the index **before** `urml-mcp-server` is uploaded. As of this writing only
`urml-validator` and `urml-llm-bridge` are on PyPI, and both at `0.1.0`, so the
MCP publish is gated on cutting the full 0.2.0 release first.

Do that release per [`RELEASING.md`](../../RELEASING.md). `urml-mcp-server` is
now the sixth package in that ordered flow.

---

## Channel 1: PyPI (`urml-mcp-server`)

First-ever publish, so the name is unclaimed. Configure a **pending** Trusted
Publisher on TestPyPI and PyPI (owner `URML-MARS`, repo `URML`, workflow
`release.yml`) before the first upload, or use a token with the manual `twine`
path. The build + ordered upload commands are in
[`RELEASING.md`](../../RELEASING.md) (step-by-step, sixth in the loop).

Verify from a clean venv outside the repo before real PyPI:

```bash
urml-mcp --help          # console script resolves
python -m pytest reference/mcp-server/tests   # 10 hermetic tool tests pass
```

---

## Channel 2: Official MCP Registry (`io.github.urml-mars/urml`)

[`server.json`](server.json) is the manifest for
[registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io).
The registry hosts no code; it points at the PyPI package, so Channel 1 must be
live first.

**Steps:**
1. Install the `mcp-publisher` CLI.
2. `mcp-publisher publish` against [`server.json`](server.json). GitHub login
   verifies ownership of the `io.github.urml-mars` namespace.
3. Confirm the schema version and field casing against the CLI at publish time;
   the registry schema is still evolving.

---

## Channel 3: MCP directories (Smithery, Glama, PulseMCP, mcp.so)

These crawl the ecosystem and let you claim ownership of the listing. After the
registry entry is live, submit / claim each under `greenvh@gmail.com`. They are
directory listings, not the source of truth; [`server.json`](server.json) is.

**Listing metadata:**
- **Name:** URML MCP server (`urml-mcp-server`)
- **One-liner:** Validate-before-actuate robot intent as agent tools: validate a plain-language-derived robot program against the robot's declared capabilities and safety envelope before any actuator moves. The server never calls an LLM.
- **Tags:** robotics, robot-intent, validation, safety, ros2, px4, mcp, open-standard
- **Repo:** https://github.com/URML-MARS/URML
- **Homepage:** https://urml.dev
- **License:** Apache-2.0

---

## After publishing

Track each venue in
[`examples/lighthouses/distribution.yaml`](../../examples/lighthouses/distribution.yaml):
fill `submitted_at` / `posted_url`, keep `response: none` until real adoption
signal. Install counts and listing views are vanity, not engagement. Do not
cite them without corroboration. Keep the server in lockstep with the `urml`
CLI; if the CLI changes, update the tools and re-publish.
