---
rfc: 0108
title: NASA-JPL ROSA integration, request for comment from nasa-jpl/rosa maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-27
updated: 2026-05-27
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

# RFC-0108: NASA-JPL ROSA integration, request for comment from nasa-jpl/rosa maintainers

## Summary

URML does not yet ship a ROSA integration. This RFC proposes a `urml_rosa_tool` Langchain tool that the `nasa-jpl/rosa` agent can register alongside its existing ROS / IsaacSim / domain tools. The tool accepts a natural-language request from ROSA's planner, emits a URML program (a sequence of Layer-2 primitives), validates it against the active URML capability manifest, and returns the validated program for ROSA (or URML's substrate adapter) to execute. On validation failure it returns a typed reason that ROSA's agent can re-plan against. No spec change on URML's side. This RFC documents the proposed bridge shape and requests review and feedback from the `nasa-jpl/rosa` maintainers.

This is the first Move #9 RFC. Move #9 is URML's first NASA-robotics outreach wave, drawn from a verified 2026-05-27 shortlist of JPL / Ames Apache-2.0 robotics projects with active maintainer surfaces. ROSA leads the wave because, of every project URML has surveyed across nine outreach moves, ROSA's natural-language-to-ROS-tool-call loop is the closest semantic overlap with URML's reason for existing.

## Motivation

ROSA (the **R**ob**O**t **S**ystem **A**gent, arXiv:2410.06472, `jpl-rosa` on PyPI) is JPL's Langchain-based agent for natural-language interaction with ROS 1 and ROS 2 systems. A user calls `ROSA(ros_version=1, llm=llm).invoke("Show me a list of topics that have publishers but no subscribers")` and the agent reasons through ROS introspection + actuation to satisfy the request. The framework is Apache-2.0, 1,527 stars at time of writing, ROS Noetic / Humble / Iron / Jazzy supported, with a documented extension model for custom agents and tools via the `nasa-jpl/rosa` Wiki.

ROSA and URML solve adjacent halves of the same problem. ROSA is the live conversational front end: it owns the LLM, the prompt orchestration, the tool registration, and the ROS-side execution path. URML is the formal contract one layer below: a substrate-neutral primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `wait`, `report`, plus `dock`, `scan`, `capture`, `speak`, `listen`, `detect`), a Layer-1 capability manifest that names what a target robot can and cannot do, and a validator that statically rejects any program a manifest cannot honor.

Plugged together: ROSA's LLM emits, via a single new tool, a URML program instead of a stream of raw `rospy.Publisher(...).publish(...)` calls. URML's validator gates the program against the active manifest. The program either executes (via URML's substrate adapter, ROSA's own ROS bridge, or both), or returns a typed reason ("no `grasp` primitive: this manifest declares `gripper: none`") that ROSA's agent can plan against. The user gets natural-language interaction (ROSA's contribution) **and** static safety before any actuator publishes (URML's contribution). Neither side gives up its strengths.

Three things make this RFC concrete rather than aspirational. First, ROSA's published extension model (`nasa-jpl/rosa/wiki/Custom-Agents`) names exactly the surface URML needs: a Langchain tool the agent registers at construction. Second, URML already ships an LLM-bridge reference (`reference/llm-bridge/`) whose prompt contract turns natural-language into validated URML programs; the same contract plugs into ROSA's tool layer with no architectural delta on URML's side. Third, ROSA's own README flags an IsaacSim extension as "coming soon"; URML's `reference/isaac-runtime/` is the substrate-side complement that would let a ROSA + IsaacSim demo run a URML program in physics before any real hardware touches it. The pieces line up.

JPL's posture is the open-standards posture: Apache-2.0 inbound = outbound, no CLA, CONTRIBUTING.md + CODE_OF_CONDUCT + GOVERNANCE all present, Issues and Discussions both enabled with Discussions named in CONTRIBUTING as the preferred design-discussion channel. URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation. NASA-JPL is the rights-holder; @RobRoyce is the published key contact. NASA's SLIM best-practices framework (referenced in ROSA's README) is the documentation discipline URML's RFC follows by default.

## Detailed design

URML's existing artifacts that feed into a ROSA bridge:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives a ROSA-emitted URML program would use.
- [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md): URML's NL layer above the primitives. ROSA's planner is one concrete implementation of this layer for the ROS-bridge target.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference. The ROSA bridge reuses its prompt contract.
- [`reference/ros2-runtime/`](../../reference/ros2-runtime/): URML's ROS 2 reference runtime. A ROSA bridge can hand the validated URML program to this runtime for execution, or hand the equivalent ROS commands back to ROSA for ROSA to publish via its existing tool layer.
- [`reference/isaac-runtime/`](../../reference/isaac-runtime/): URML's IsaacSim substrate. Direct complement to the ROSA IsaacSim extension flagged as coming soon in ROSA's README.

### Proposed `urml_rosa_tool` shape

Following ROSA's published tool-registration convention (custom Langchain `BaseTool` registered at agent construction). Package layout (sketch):

```
urml_rosa_bridge/
├── pyproject.toml                 # name = "urml-rosa-bridge"
└── src/
    └── urml_rosa_bridge/
        ├── __init__.py
        ├── tool.py                # URMLProgramTool(BaseTool)
        ├── prompt_contract.py     # the URML prompt-contract reused from reference/llm-bridge/
        └── manifest_seed.py       # helper to seed ROSA's system prompt with a URML manifest
```

The key class (sketch):

```python
# tool.py
from langchain.tools import BaseTool
from urml.validator import validate
from urml.manifest import load_manifest

class URMLProgramTool(BaseTool):
    name = "urml_program"
    description = (
        "Translate a natural-language robot request into a validated URML "
        "program (a typed sequence of Layer-2 primitives). The program is "
        "checked against the active capability manifest before return; if "
        "the manifest cannot honor the request, returns a typed reason."
    )

    def __init__(self, manifest_path: str):
        super().__init__()
        self._manifest = load_manifest(manifest_path)

    def _run(self, request: str) -> dict:
        program = self._llm_translate(request)  # reuses URML's llm-bridge prompt
        result = validate(program, manifest=self._manifest)
        if not result.ok:
            return {"status": "rejected", "reason": result.reason, "primitive": result.failing_primitive}
        return {"status": "validated", "program": program.to_dict()}
```

The tool is a wrapper, not a model. It reuses ROSA's LLM (Langchain hands the LLM in via the agent's existing config), inserts URML's validator between the raw NL request and the substrate, and returns either a validated URML program or a typed rejection. The wrapper pattern preserves ROSA's contracts (the agent decides when to call the tool; the tool's return is a string the agent can reason against) while making the substrate-neutral safety check testable in isolation.

### Proposed bridge contract

| URML role | ROSA role |
|---|---|
| Owns the Layer-2 primitive vocabulary, the Layer-1 manifest schema, and the validator. | Owns the LLM, the prompt orchestration, the tool registration, and the existing ROS introspection / actuation tools. |
| Provides `URMLProgramTool` as a Langchain `BaseTool` and the prompt contract that turns NL into URML. | Registers `URMLProgramTool` at agent construction alongside its other tools; calls it when the user's request involves actuation. |
| Returns either `{"status": "validated", "program": ...}` or `{"status": "rejected", "reason": ...}`. | Re-plans on rejection (its existing capability); executes on validation, either by handing the program to URML's substrate adapter or by lowering it to ROS commands itself. |
| Hosts `reference/ros2-runtime/` as the canonical URML-to-ROS execution path. Composes with ROSA's existing ROS interface; does not replace it. | Keeps its tool layer authoritative for ROS execution. URML adds a typed pre-flight check, not a replacement. |

### Proposed manifest-seed pattern

ROSA's system prompt today is target-agnostic (the agent introspects the live ROS graph). For URML's safety check to be useful, ROSA's planner benefits from knowing the active manifest's capability surface at planning time, not just at execution time. `manifest_seed.py` builds a compact prompt fragment from a URML manifest:

```
You are controlling a robot with the following declared capabilities:
- mobility: tracked_aquatic; workspace: aquatic_pool
- supported primitives: move_to(region), measure, wait_for, report
- NOT supported: grasp, release (manifest declares gripper: none)
- NOT supported: scan (substrate cannot produce coverage)
Plan within these limits; the URML validator will reject any program that uses an unsupported primitive.
```

This is optional; ROSA can call `URMLProgramTool` without it. The seed makes rejection cheaper and the resulting plans tighter.

### Execution path: two options for the maintainer's input

A validated URML program can run two ways. URML has no preference; this is exactly the kind of design point that benefits from the ROSA team's read.

1. **URML executes.** The bridge hands the validated program to URML's substrate adapter (`reference/ros2-runtime/`), which publishes the ROS commands. ROSA's tool returns "executed" to the agent. Cleaner separation; URML is a black-box safety+execution layer.
2. **ROSA executes.** The bridge returns the lowered ROS commands (or the validated URML program structure) to ROSA's tool layer; ROSA's existing tools publish. URML is a pre-flight check only. Cleaner integration into ROSA's existing model.

Either is implementable. The choice depends on whether the ROSA team prefers URML inside ROSA's tool layer (option 2) or alongside it (option 1).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: a new `reference/llm-bridge/rosa/` sub-package (or sibling repo `urml-rosa-bridge`) hosting `URMLProgramTool` and `manifest_seed.py`. Not built in this PR.
- Conformance suite: proposed new `rosa-integration.yml` CI workflow + `URML_ROSA_INTEGRATION` env gate. Hermetic suite first (mock Langchain LLM); ROSA + real-LLM in the loop deferred behind the maintainer-engagement gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code lands in this RFC.

## Drawbacks

- **Proposal-only.** No bridge code in this RFC. Same posture as RFC-0040 (LeRobot) and RFC-0073 (Robotical Marty, round 1). Adapter / bridge ships engagement-driven.
- **Two-layer LLM cost.** If URML's prompt contract calls a separate LLM completion before ROSA's planner sees the result, the user pays for two completions per request. Mitigations: route both through ROSA's existing LLM handle (the bridge reuses ROSA's `llm` parameter), or cache the NL-to-URML translation when ROSA repeats a similar request. The RFC asks the ROSA team's preference.
- **Manifest seeding adds prompt-budget weight.** A non-trivial capability manifest in ROSA's system prompt eats tokens. The seed format above is intentionally compact, but a 50-sensor robot stretches it. RFC asks whether ROSA's planner benefits more from a small seed (URML's call) or a fuller capability dump (let the LLM read it like documentation).
- **NASA documentation discipline.** ROSA cites NASA's SLIM framework for best practices. URML's outreach norms (RFC + ledger + AGENTS.md authoring disclosure) overlap with SLIM but are not identical; the RFC names this and asks whether anything in SLIM constrains URML's contribution shape.

## Alternatives considered

1. **Skip the manifest-seed pattern; let ROSA discover the manifest at tool-call time.** Considered. Cleaner architecturally but produces worse plans, because the LLM proposes primitives it then learns are rejected. Rejected for v0.1; reconsider if the ROSA team prefers it.
2. **Hard-fork ROSA's prompt orchestration into URML's `reference/llm-bridge/`.** Rejected. URML does not want to maintain a ROS-aware prompt orchestration layer; that is ROSA's domain. The bridge stays a thin tool, not a fork.
3. **Bypass ROSA, point users directly at URML's existing `reference/llm-bridge/` + `reference/ros2-runtime/`.** Considered but loses the ROSA audience entirely. The whole point of this RFC is to compose with ROSA, not to compete.
4. **Wait for ROSA's IsaacSim extension to ship.** Rejected. URML's `reference/isaac-runtime/` is independent of the ROSA + IsaacSim work and need not block. RFC notes the parallel as future-aligned, not blocking.

## Prior art

- [`nasa-jpl/rosa`](https://github.com/nasa-jpl/rosa) — the upstream agent. Apache-2.0, 1.5k stars, last push 2026-03-17.
- [ROSA paper, arXiv:2410.06472](https://arxiv.org/abs/2410.06472).
- [NASA SLIM Best Practices](https://nasa-ammos.github.io/slim/) — the framework ROSA's README references and that URML's RFC follows by default.
- [`reference/llm-bridge/`](../../reference/llm-bridge/) — URML's existing LLM-to-URML translation reference; the bridge prompt contract is reused.
- [RFC-0040](0040-hugging-face-lerobot.md) — the LeRobot Move #2 RFC; same proposal-only / bridge-via-published-extension-model pattern.
- [RFC-0073](0073-robotical-marty-outreach.md) — Robotical Marty Move #5 RFC; precedent for the engagement-driven adapter-ship pattern this RFC follows.

## Unresolved questions

For the `nasa-jpl/rosa` maintainers (@RobRoyce and the JPL AI Group):

1. **Bridge home.** Should the URML bridge live as (a) an example folder inside `nasa-jpl/rosa` (e.g. `examples/urml-bridge/`), (b) a separately-maintained `nasa-jpl/rosa-urml-bridge` repo under the same org, or (c) external in `URML-MARS/URML` only? URML's default assumption is (c) until invited otherwise.
2. **Execution path.** Should the bridge return execution to ROSA's existing tool layer (URML as pre-flight check only), or hand off to URML's substrate adapter (URML as execution layer)? Either is implementable; the choice depends on how cleanly the ROSA team wants URML factored into the existing model.
3. **LLM reuse.** Should the bridge reuse ROSA's `llm` parameter for the NL-to-URML translation step (one LLM, two completions per request), or hold a separate LLM handle URML provides (cleaner separation, two LLMs)?
4. **Manifest seeding.** Does ROSA's planner benefit from URML's compact manifest-seed pattern (50 to 200 tokens summarizing supported primitives), or is the LLM better served by reading a full URML manifest as plain context like documentation?
5. **IsaacSim extension alignment.** ROSA's IsaacSim extension is flagged as coming soon. Is there a near-term timeline where URML's `reference/isaac-runtime/` could compose with that extension as the URML-side simulation target?
6. **NASA SLIM / governance constraints.** Are there documentation, governance, or process constraints from NASA's SLIM framework (or JPL-specific) that should shape how URML contributes to or cross-cites ROSA? URML's outreach norms (AGENTS.md authoring-disclosure, DCO-signed commits, Apache-2.0 inbound = outbound) overlap with SLIM, but the RFC asks for any deltas explicitly.
7. **Conformance lane.** Would the ROSA team consider a README or Wiki link to URML once a working bridge ships, basic tests pass against ROSA + a mock LLM, and an example agent (TurtleSim or another low-friction target) demonstrates the loop?

## Implementation note

RFC-0108 ships as a single RFC document PR. No bridge code in this PR. First Move #9 RFC. Ledger entry in [`examples/lighthouses/outreach-move9.yaml`](../../examples/lighthouses/outreach-move9.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`nasa-jpl/rosa` has both Issues and Discussions enabled; the upstream CONTRIBUTING.md names Discussions as the preferred surface for design discussion (Issues are for concrete scoped bugs or features). URML's planned channel: open a single Discussion on `nasa-jpl/rosa` pointing at this RFC, with a one-paragraph authoring disclosure per [AGENTS.md L67](../../AGENTS.md#L67) + [VIBE.md](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] Summary, Motivation, and Detailed design grounded in verified `nasa-jpl/rosa` surface (Apache-2.0, 1527 stars, 3 open issues, Issues + Discussions both enabled, CONTRIBUTING + GOVERNANCE present, last commit 2026-03-17, @RobRoyce key contact).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (proposal-only, two-layer LLM cost, manifest-seed prompt-budget weight, NASA documentation discipline).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change of any kind.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-27.
- [x] Provenance: NASA-JPL Caltech, US; US-federal default policy passes without flagging.
- [x] CLAUDE.md compliance check passed.
