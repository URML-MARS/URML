---
rfc: 0058
title: OpenAI robotics integration, request for comment from OpenAI
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

# RFC-0058: OpenAI robotics integration, request for comment from OpenAI

## Summary

OpenAI restarted an in-house robotics group in February 2025 and has been hiring humanoid researchers and operating a Franka-plus-GELLO teleoperation lab in San Francisco. To date, OpenAI has not published a public robotics API, SDK, or model. This RFC is a deliberate cold-knock: it documents URML's intended integration shape against an eventual public OpenAI robotics surface, surfaces the proposal on OpenAI's most-active community-facing repo (`openai/openai-cookbook`), and asks the OpenAI team to consider URML's substrate-neutral action vocabulary as an integration target when the robotics work becomes public. No spec change on URML's side. No bridge code (there is nothing to bridge to yet).

Move #2 Outreach RFC. Proposal-only and explicitly forward-looking. Expected response cadence: slow, possibly none until OpenAI ships a public robotics surface.

## Motivation

The Move #2 outreach program is comprehensive by intent. Every other major US AI lab with substantive robotics work has a Move #2 RFC: Anthropic (RFC-0048, MCP plus Agent Skills), Google DeepMind (RFC-0046 via OXE governance), Meta FAIR (RFC-0052, V-JEPA 2), NVIDIA (RFC-0050, RFC-0055, RFC-0057), Allen Institute (RFC-0047), TRI (RFC-0054), Physical Intelligence (RFC-0045), HF LeRobot (RFC-0040). Filing nothing against OpenAI would create an asymmetry that an external reader would notice; the cold knock closes that asymmetry honestly.

What we know about OpenAI's current robotics posture, verified from public sources:

- A new robotics team was assembled in February 2025 in San Francisco, co-located with the finance team. The team has grown to roughly 100 data collectors working three shifts.
- Trademarks were filed in January 2025 mentioning "user-programmable humanoid robots" with communication and learning capabilities.
- The training pipeline uses Franka arms teleoperated through GELLO controllers (a low-cost 3D-printed teleop rig).
- OpenAI invested in 1X Technologies; the Figure AI partnership ended in early 2025.
- OpenAI has shipped no public robotics SDK, no robotics model release, and no robotics-specific repo under the `openai` GitHub organization. The most active OpenAI public repos (`openai/openai-cookbook` 73.7k stars, `openai/openai-python` 30.8k stars, `openai/openai-agents-python` 26.6k stars) are general-purpose LLM tooling.

The URML integration story is short because the surface to integrate with is not yet public. When OpenAI does publish a robotics API or model, URML's value proposition is identical to RFC-0040 through RFC-0057: URML's substrate-neutral primitive vocabulary lets an OpenAI-trained robotics model emit actions that retarget across ROS 2, PX4, Isaac, MuJoCo, AUTOSAR Adaptive, and OPC UA Robotics without retraining.

## Detailed design

There is no public surface to design against. The proposed shape is forward-looking and tracks the patterns established in Move #2:

- **If OpenAI publishes a Python SDK with a policy or action API**, URML integration follows the wrapper pattern in [RFC-0040](0040-hugging-face-lerobot.md) (LeRobot) and [RFC-0045](0045-physical-intelligence-openpi.md) (openpi): a thin wrapper that intercepts the action stream and emits URML primitives alongside.
- **If OpenAI publishes a reasoning-style robotics model with constrained decoding support**, URML integration follows the pattern in [RFC-0055](0055-nvidia-cosmos-reason.md) (Cosmos-Reason1): a grammar-constrained decoder that emits URML programs.
- **If OpenAI publishes a hosted robotics API behind authentication**, URML's existing `reference/llm-bridge/` is already provider-agnostic (Anthropic, OpenAI, open-weights, on-device) and would gain an OpenAI-robotics adapter the same way it has other adapters today.

URML's [`reference/llm-bridge/`](../../reference/llm-bridge/) already supports OpenAI's general-purpose LLM API. The robotics-specific extension is the integration this RFC is forward-declaring.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: none. A future `reference/openai-robotics-bridge/` follows once OpenAI publishes a robotics surface.
- Conformance suite: none.

## Backward compatibility

Not applicable. There is nothing to integrate with yet.

## Drawbacks

- **The cold knock is a thin artifact.** Without a public OpenAI robotics surface, this RFC is a placeholder. The honest framing is that we are filing it for completeness and to put URML on OpenAI's radar when the team is ready to share their work publicly.
- **Expected response: low or none.** OpenAI's robotics work is intentionally non-public. The cold knock asks them to remember URML's name and contact when their public roadmap allows. That is the realistic ceiling.
- **Outreach channel is suboptimal.** `openai/openai-cookbook` is a recipe and example repo; the proposal does not fit the cookbook's typical Issue shape. The fallback is the `community.openai.com` forum, which has even less expectation of a substantive engineering response.

## Alternatives considered

1. **Skip OpenAI entirely.** Rejected. Asymmetric coverage of Move #2 would be noticed; filing nothing creates more questions than it answers. The cold knock is honest and small.
2. **Wait until OpenAI ships a public robotics surface.** Considered. The forward-declared RFC has marginal value over silence, but the marginal value is positive: when OpenAI looks at integration partners, they will find URML documented and reachable.
3. **Route via 1X Technologies (OpenAI-backed humanoid manufacturer) instead.** Considered. 1X Technologies is a separate company with its own decision-making; an OpenAI RFC does not block a future 1X RFC, and the two have different surfaces. A future 1X Move #2 RFC remains possible.
4. **Submit through OpenAI's research partner program.** Rejected for this RFC. The partner program is not a public outreach channel; URML is not currently a research partner. The cold-knock-via-public-repo path is the appropriate channel for Phase 1 outreach.

## Prior art

- `openai/openai-cookbook`: most-active OpenAI public repo, the chosen outreach surface (73.7k stars, Issues enabled, primarily Jupyter notebooks of LLM-API recipes; not robotics-specific but the most plausible OpenAI surface that accepts community proposals).
- `openai/openai-python`, `openai/openai-agents-python`: general-purpose SDKs URML already targets via `reference/llm-bridge/`.
- OpenAI robotics revival press coverage: TechCrunch, Built In, Tekedia, LinkedIn announcements (Feb 2025 onward).
- OpenAI trademark filings for "user-programmable humanoid robots" (January 2025).
- 1X Technologies NEO (OpenAI-backed humanoid, $20K preorder Oct 2025, 2026 delivery).
- [RFC-0040](0040-hugging-face-lerobot.md), [RFC-0045](0045-physical-intelligence-openpi.md), [RFC-0055](0055-nvidia-cosmos-reason.md): the integration patterns that an eventual OpenAI robotics integration would follow.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing OpenAI-compatible LLM integration surface.

## Unresolved questions

These are open by design; the cold knock does not expect immediate answers.

1. **Is there a public surface (current or planned) where URML's integration proposal could be reviewed by the OpenAI robotics team directly?**
2. **What is the expected shape of OpenAI's first public robotics artifact: SDK, model release, hosted API, or something else?**
3. **Would OpenAI be open to URML being a documented integration target in OpenAI's robotics documentation when the team is ready to publish?**
4. **Is the `openai/openai-cookbook` Issue tracker the right channel for this cold knock, or is there a better surface URML should use?**
5. **Anything else.**

## Implementation note

RFC-0058 ships as a single RFC document PR. No bridge code, no integration scaffolding. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from OpenAI)

1. Public-surface availability or planned timing.
2. Expected shape of the first robotics artifact.
3. Openness to URML as a documented integration target.
4. Right outreach channel for cold-knock proposals.
5. Anything else.

## How to respond

URML's planned channel: file an Issue on `openai/openai-cookbook` referencing this RFC, framed honestly as a cold knock pending OpenAI's robotics public surface. The Issue is labelled as a question rather than a feature request. Optional cross-post on `community.openai.com` if the cookbook Issue gets redirected.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is a deliberate cold knock with no public OpenAI robotics surface yet.
- [x] Motivation grounded in verified facts (verified against OpenAI's public GitHub org on 2026-05-23: no robotics-specific repos, openai-cookbook 73.7k stars and openai-python 30.8k stars and openai-agents-python 26.6k stars are general-purpose; press coverage confirms Feb 2025 robotics team restart, ~100 data collectors, Franka plus GELLO teleop, 1X Technologies investment, Figure partnership end early 2025, January 2025 trademark filings).
- [x] The thinness of the RFC is documented honestly rather than padded.
- [x] Four alternatives considered.
- [x] Drawbacks are real (thin artifact, low expected response, suboptimal channel).
- [x] Backward compatibility: not applicable.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no bridge code in this PR (and none possible until OpenAI publishes a robotics surface).
- [x] Surface verified: openai org browsed, no robotics repos found, most-active repos catalogued.
- [x] Cold-knock framing made explicit throughout: Summary, Motivation, Drawbacks, How to respond.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant. Provider neutrality preserved.
