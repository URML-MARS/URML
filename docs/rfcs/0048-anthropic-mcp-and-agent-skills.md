---
rfc: 0048
title: Anthropic integration via MCP and Agent Skills, request for comment from Anthropic
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-23
updated: 2026-05-23
supersedes: —
superseded-by: —
---

<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# RFC-0048: Anthropic integration via MCP and Agent Skills, request for comment from Anthropic

## Summary

URML proposes two complementary integration vectors with Anthropic's open-standard ecosystem: a Model Context Protocol (MCP) server that exposes URML's translate / validate / execute pipeline as MCP tools (so any MCP client can drive robots through URML with full validation), and an Agent Skill (`urml`) that teaches Claude the URML grammar so Claude can natively author URML programs. No spec change on URML's side. This RFC documents both vectors and requests review and feedback from the MCP and Agent Skills maintainers at Anthropic.

Move #2 Outreach RFC. Proposal-only: no MCP server and no Skill bundle in this PR.

## Motivation

Anthropic has placed two open standards into the AI-tooling ecosystem in the last year:

- **Model Context Protocol** (`modelcontextprotocol/specification`): an open spec for connecting AI assistants to external tools and data. Client-server architecture, JSON Schema and TypeScript spec, formal Specification Enhancement Proposals (SEPs) for spec evolution, an emerging public registry. Latest spec version 2025-11-25. 8.2k+ stars at time of writing. Discussions and Issues both enabled. Created by David Soria Parra and Justin Spahr-Summers at Anthropic.
- **Agent Skills** (`anthropics/skills`): an open standard at `agentskills.io`. A Skill is a folder with a `SKILL.md` file (YAML frontmatter for name and description, markdown body for instructions, examples, and guidelines). Apache 2.0 for the example skills; 139k+ stars; very active (626 open PRs, 246 open Issues at time of writing).

Both are deliberately positioned as standards Anthropic does not control unilaterally. URML's open-core posture and Anthropic's standards posture are unusually aligned: both are built on the bet that the standard creates more value when it is genuinely open than when it is owned.

The integration story for URML has two complementary halves:

- **MCP server.** Any MCP client (Claude Desktop, Claude Code, Cursor, future MCP-aware tools) becomes a URML driver. The server exposes three tools: `urml_translate` (English to URML), `urml_validate` (program plus manifest plus profile to pass / fail with envelope), `urml_execute` (validated program plus substrate brand to hermetic execution trace). A robotics workflow goes from "ask Claude" to "Claude drives the robot" without leaving the conversation, with URML's static validation as the safety boundary.
- **Agent Skill.** Claude with the URML skill loaded can write URML programs natively. The skill teaches the grammar, the primitive vocabulary, the manifest format, the validation rules, and when to call the URML MCP server. This is a Layer-4 NL bridge done from Claude's side, complementary to URML's own `reference/llm-bridge/`.

The two vectors are independent and additive: either alone is useful, both together are more useful. The RFC documents both because separating them into two RFCs would lose the symmetry.

## Detailed design

URML's existing artifacts that feed into Anthropic integration:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the primitive vocabulary the Skill would teach and the MCP server would validate against.
- [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md): the NL grammar the Skill makes accessible to Claude.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference. The MCP server's `urml_translate` tool is a thin wrapper over this.
- [`reference/validator/`](../../reference/validator/): the validator the MCP server's `urml_validate` tool exposes.

### Proposed MCP server

A new package `reference/mcp-server/` (and PyPI mirror `urml-mcp-server`), implementing the MCP server protocol per the published spec.

```
urml_mcp_server/
├── pyproject.toml
└── src/
    └── urml_mcp_server/
        ├── __init__.py
        ├── server.py              # MCP server entry point
        ├── tools/
        │   ├── translate.py       # urml_translate tool
        │   ├── validate.py        # urml_validate tool
        │   └── execute.py         # urml_execute tool
        └── resources/
            └── primitives.py      # exposes the primitive vocabulary as an MCP Resource
```

The three tools:

| MCP Tool | Inputs | Output | Backed by |
|---|---|---|---|
| `urml_translate` | English sentence, manifest path, profile name | URML program YAML | `reference/llm-bridge/` |
| `urml_validate` | URML program, manifest path, profile name | Pass / fail, envelope, diagnostic trace | `reference/validator/` |
| `urml_execute` | Validated URML program, substrate brand, manifest path | Hermetic execution trace | `reference/ros2-runtime/` (or selected substrate adapter) |

A fourth optional element is an MCP `Resource` exposing the URML primitive vocabulary as a fetchable document the client can read to ground its prompts.

The server is offline by default and validates every program against a manifest before any `urml_execute` call can be issued. The validator is non-bypassable from the MCP surface: this matches the URML rule that programs execute only after static verification (see [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do).

### Proposed Agent Skill

A single `SKILL.md` plus a small supporting folder, following the `anthropics/skills` repository convention:

```
skills/urml/
├── SKILL.md
├── grammar/
│   ├── layer-2-primitives-summary.md   # 20 primitives, one-line each
│   ├── manifest-format.md              # how to read a capability manifest
│   └── validation-rules.md             # what the validator will reject and why
└── examples/
    ├── home-red-mug.urml.yaml          # canonical 3-line demo program
    ├── industrial-pick-and-place.urml.yaml
    └── drone-survey.urml.yaml
```

The `SKILL.md` YAML frontmatter:

```yaml
---
name: urml
description: |
  Author URML (Universal Robot Language) programs from English requests.
  Use this skill when the user wants to describe robot intent, generate a
  URML program, validate it against a capability manifest, or execute it
  on a substrate. When the URML MCP server is available, call its tools
  (urml_translate, urml_validate, urml_execute) directly. When it is not,
  emit the URML program inline and the user runs `urml validate` locally.
---
```

The body teaches: the primitive vocabulary at a high level, how to read a manifest, what the validator rejects (so Claude does not produce invalid programs by accident), and when to defer to the MCP server vs. emit inline.

Distribution: the skill folder lives in URML's repo under `tools/agent-skills/urml/` and is mirrored as a PR to `anthropics/skills` (the documented distribution channel for community skills, per the skills repo CONTRIBUTING and the agentskills.io spec).

### Compatibility notes

- **License.** MCP spec is open (multiple repos under the modelcontextprotocol organization carry MIT or Apache 2.0 licenses depending on the repo); Agent Skills examples are Apache 2.0. URML's MCP server and Skill are Apache 2.0 by default.
- **Provider neutrality.** URML's Core Commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) prohibits LLM-provider lock-in. MCP is a provider-agnostic standard (Anthropic created it but it is implemented by clients across vendors). Agent Skills is documented as an open standard at agentskills.io with non-Anthropic clients adopting it. URML's integration with both does not violate provider neutrality precisely because Anthropic positioned both as open. URML's `reference/llm-bridge/` retains its multi-provider posture; the MCP server and Skill are additional integration surfaces, not replacements.
- **Offline rule.** MCP servers can run locally. The URML MCP server runs offline by default, with no required cloud dependency. The Skill is a markdown bundle, also offline.
- **Origin.** Anthropic is incorporated in San Francisco, CA, US. Passes the URML US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.
- **MCP registry.** The MCP spec references a registry for discoverable servers. URML's server would be a registry candidate once shipped.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed two new packages, `reference/mcp-server/` and `tools/agent-skills/urml/`. Not built in this PR.
- Conformance suite: optional `mcp-server-integration.yml` workflow that smokes the MCP tool surface against the existing red-mug fixture.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. Neither MCP nor Agent Skills require changes from Anthropic; URML conforms to their published specs.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping server and shipping skill.** URML wants Anthropic input on the tool surface (which tools to expose, which resources to expose) and on the Skill content (how much grammar to inline vs. defer to the spec) before writing the bundle.
- **Two surfaces is two integration burdens.** Maintaining both an MCP server and an Agent Skill is more than one. The mitigation is that the Skill points at the MCP server when it is available, so the two reinforce rather than duplicate.
- **Self-referential.** URML is being authored partly with Claude's help. A Claude-skill for URML feeds back into URML's own development loop. That is intentional and is documented in URML's existing AI-assist conventions ([`CLAUDE.md`](../../CLAUDE.md), [`AGENTS.md`](../../AGENTS.md)), but the recursion is worth naming.
- **Provider-neutrality optics.** Even though MCP is provider-agnostic in spec, in practice it has been pushed by Anthropic. URML's deeper investment in MCP could be read as a tilt toward Claude despite the Core Commitment. The mitigation: URML's `reference/llm-bridge/` continues to support all major providers as first-class, the MCP server is one surface among several, and URML's documentation will name this explicitly.

## Alternatives considered

1. **MCP server only.** Rejected. The Skill makes Claude immediately useful as a URML author without requiring the user to install and configure an MCP server. The Skill is the lower-friction entry point.
2. **Agent Skill only.** Rejected. The Skill alone cannot validate or execute; it can only teach Claude to author. The MCP server is what makes Claude *drive* robots, not just author programs.
3. **Wait for MCP to mature further.** Rejected. The MCP spec is at 2025-11-25 and stable; the registry is forming; the right time to land a substantive server is now, not after the standard fully crystallizes.
4. **Embed only in Claude Code's prompt context (no Skill).** Rejected. The Skill is the documented standard for teaching Claude domain knowledge; bypassing it for a custom prompt would be unforced.

## Prior art

- `modelcontextprotocol/specification`: the MCP spec repo (8.2k+ stars, Issues and Discussions enabled, `/seps` directory for spec evolution, created by David Soria Parra and Justin Spahr-Summers).
- `anthropics/skills`: the Agent Skills public repository (139k+ stars, 626 open PRs, very active).
- `agentskills.io`: the published open standard for Agent Skills.
- The Skill Creator skill in `anthropics/skills`: the interactive bootstrap for authoring a new Skill.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation, the MCP server's `urml_translate` backing.
- [`reference/validator/`](../../reference/validator/): the validator the MCP server exposes.
- [RFC-0021](0021-on-device-llm-bridge.md): on-device LLM bridge. Relevant when the MCP client uses an on-device model rather than a hosted one.
- [RFC-0040](0040-hugging-face-lerobot.md), [RFC-0045](0045-physical-intelligence-openpi.md), [RFC-0046](0046-open-x-embodiment.md), [RFC-0047](0047-allen-institute-molmoact.md): the parallel Move #2 RFCs.

## Unresolved questions

Provisional pending Anthropic feedback:

1. **Tool surface.** Are the three proposed MCP tools (`urml_translate`, `urml_validate`, `urml_execute`) the right granularity, or should they be merged, split, or augmented with additional tools (e.g., `urml_lint`, `urml_explain`)?
2. **Resource surface.** Should the primitive vocabulary be exposed as an MCP Resource, an MCP Prompt, or both?
3. **Skill scope.** How much of the URML grammar should the Skill inline vs. defer to the spec via the MCP Resource? The trade-off is Skill weight vs. self-containment.
4. **Server distribution.** Should URML publish the MCP server to the emerging MCP registry, or rely on PyPI distribution only at first?
5. **Skill distribution.** PR to `anthropics/skills` for the canonical channel, mirror in `URML-MARS/URML` for ownership, both?
6. **MCP SEP if any.** If the URML MCP server surfaces a need for a spec extension (e.g., richer telemetry-stream semantics), is the SEP process at `modelcontextprotocol/specification/seps` the right channel?
7. **Anything else.**

## Implementation note

RFC-0048 ships as a single RFC document PR. No MCP server code and no Skill bundle in this PR. The actual `reference/mcp-server/` and `tools/agent-skills/urml/` packages follow in later sessions, gated on Anthropic feedback. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from Anthropic MCP and Agent Skills maintainers)

1. MCP tool surface (granularity, additions, removals).
2. MCP Resource vs. Prompt for the primitive vocabulary.
3. Skill scope (inline grammar vs. defer to MCP Resource).
4. MCP registry placement timing.
5. Skill distribution channels (PR to anthropics/skills, mirror in URML repo, both).
6. SEP route if URML surfaces a spec-extension need.
7. Anything else.

## How to respond

Two surfaces, two channels:

- **MCP feedback:** the `modelcontextprotocol/specification` repo has both Discussions and Issues enabled. URML's planned channel: open a Discussion in the modelcontextprotocol repo pointing to this RFC. SEP-shaped feedback would go to `/seps` if Anthropic prefers.
- **Agent Skills feedback:** `anthropics/skills` is very active (Issues, PRs). URML's planned channel: file an Issue on `anthropics/skills` labelled as a feature proposal, with a parallel draft PR for the `skills/urml/` folder once the RFC has signal.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only.
- [x] Motivation grounded in verified facts about MCP and Agent Skills (verified against the repos on 2026-05-23: MCP spec version 2025-11-25, modelcontextprotocol/specification has Discussions and Issues, anthropics/skills has 139k+ stars and 626 open PRs, both are documented as open standards at modelcontextprotocol.io and agentskills.io).
- [x] Detailed design proposes a concrete three-tool MCP server surface and a concrete Skill folder layout following the published conventions.
- [x] Four alternatives considered.
- [x] Drawbacks are real (proposal-only, two surfaces, self-referential recursion, provider-neutrality optics).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added. The integration exposes existing URML capabilities through Anthropic's standards.
- [x] Implementation note explicitly says no server and no Skill bundle in this PR.
- [x] Surface verified: MCP Discussions and Issues enabled, anthropics/skills accepts PRs and Issues, both standards documented at modelcontextprotocol.io and agentskills.io.
- [x] Provider-neutrality check: URML's MCP server and Skill add Anthropic-ecosystem surfaces without removing or downgrading other-provider integration. `reference/llm-bridge/` stays multi-provider first-class. Compliant with [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do (no LLM-vendor lock-in).
- [x] Re-read [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant.
