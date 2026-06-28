---
rfc: 0640
title: Moltbook agent integration, request for comment from the Moltbook developer team
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-28
updated: 2026-06-28
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

# RFC-0640: Moltbook agent integration, request for comment from the Moltbook developer team

## Summary

Moltbook is a social network for AI agents: agents post, comment, and vote in topic communities ("submolts"), agents are verified through their human owner's X "claim" tweet, and a developer API lets third parties authenticate an agent and build integrations. Onboarding is done by having an agent read a "skills document." **No spec change is proposed here.** This RFC proposes that URML publish (a) a venue-neutral agent-integration skill an AI agent can read to go from a natural-language goal to a validated URML program, and (b) a verified URML agent presence on Moltbook that demonstrates the hermetic "one English sentence to a validated, executable robot program" round-trip. It documents the mapping from URML's existing Layer-4 LLM bridge onto Moltbook's agent surface, and requests review from the Moltbook developer team.

This is a distribution-and-adoption RFC, not a robotics-substrate RFC. Unlike the Move #1 OEM targets or the Move #2-onward AI/ML-layer targets, Moltbook is not a runtime URML executes on and not a model that drives a robot. It is the place the consumers of URML's Layer-4 contract (AI agents) already congregate. The honest framing is in §Drawbacks.

## Motivation

URML's Layer-4 LLM bridge is provider-agnostic: any caller invokes `Bridge.translate("English") -> validated URML program`, the emission is checked by the full five-pass validator against a capability manifest and safety envelope, and only an accepted program reaches a substrate adapter (see [`reference/llm-bridge/`](../../reference/llm-bridge/) and [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md)). The bridge does not care which model sits behind it (Anthropic, OpenAI, open-weights, on-device) and it does not require the network once a program is validated.

An AI agent that wants to make a physical robot move is precisely the consumer URML was built for. Moltbook is where a large population of such agents, and the humans who build them, can be reached in one place. Two properties make it worth a deliberate, proportionate effort:

1. **The "skills document" onboarding model maps directly onto a URML agent skill.** Moltbook agents are told to read a skill and act on it. URML ships no agent-onboarding document today; the closest artifacts are [`AGENTS.md`](../../AGENTS.md) (written for repo *contributors*, not consumers) and the [LLM-bridge README](../../reference/llm-bridge/README.md). Writing the agent-facing skill is independently valuable: it is the document a roboticist's agent, a LangChain/Claude/AutoGPT-style agent, or a Moltbook agent all read to learn the emit-then-validate loop. Moltbook is the forcing function, not the lock-in.

2. **AI-authored content is native and welcome on Moltbook.** URML's outreach has repeatedly drawn an "is this AI-generated?" reaction on human-maintained code forges, even with the up-front [`VIBE.md`](../../VIBE.md) disclosure. On a network *for* agents that objection does not apply; the medium is the message. This makes Moltbook a lower-friction venue to demonstrate the language than a code-review thread.

URML's value as a standard depends on the language being the obvious choice for natural-language robot control. Reaching the agent population where it already gathers, with a precise and runnable demonstration rather than a pitch, serves that directly.

## Detailed design

Nothing in URML's normative surface changes. The design is two artifacts plus a documented mapping.

### Artifact A: the agent-integration skill (venue-neutral)

A new document, [`docs/integrations/urml-for-ai-agents.md`](../../docs/integrations/urml-for-ai-agents.md), written for an AI agent (and the human building it) rather than a contributor. It teaches the loop URML already implements:

1. Take a natural-language goal.
2. Emit a URML program following the published Layer-4 prompt contract.
3. Validate it with `urml validate` against the target robot's capability manifest and active safety envelope.
4. Execute the accepted program via a substrate adapter (`mock` for a hermetic dry run; `ros2` / `px4` against a real runtime).

The skill leads with the **hermetic, zero-dependency path** (the bundled `EchoProvider` and `MockROSAdapter`) so an agent can prove the whole loop offline, with no API key, no network, and no robot. It reuses the existing contract verbatim (the `LLMProvider` protocol stays the integration surface; no new API is invented) and keeps the provider-agnostic posture explicit. A short "Moltbook quickstart" subsection covers registering the agent, reading the skill, and posting the demo result, without coupling the rest of the document to Moltbook.

### Artifact B: the verified URML agent presence

A verified URML agent on Moltbook (claimed under the maintainer's identity per Moltbook's X-tweet verification), whose first contributions are the deterministic sentence-to-motion demo trace and a pointer to Artifact A, posted in the most relevant submolt(s). The posting glue is operational, lives under [`tools/`](../../tools/) alongside the existing outreach tooling, and is kept out of the reference runtimes, because Moltbook is a cloud service and [`CLAUDE.md`](../../CLAUDE.md) prohibits cloud dependencies in `reference/`. Draft post bodies are committed for review before anything goes live.

### Proposed URML v0.1 to Moltbook mapping

| Moltbook concept | URML realization |
|---|---|
| A "skill" an agent reads to gain a capability | `docs/integrations/urml-for-ai-agents.md`: read this skill to gain "turn an English goal into a validated robot program." |
| An agent action / post body | The hermetic `translate -> validate -> execute` trace (the same one the README hero renders), shown as a runnable, copy-pasteable demonstration. |
| Agent identity / developer-API auth | A thin client under `tools/moltbook/` that authenticates the verified URML agent via env-supplied credentials; never embedded in the bridge, never a privileged provider. |
| A submolt (topic community) | The venue for the demo + skill pointer (robotics / agent-building communities). |

No part of this mapping touches Layer 1-4, the validator, or any primitive. The bridge contract an agent follows is the one already published; Moltbook is a new *reader* of it, not a new requirement on it.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- New documentation: `docs/integrations/urml-for-ai-agents.md`.
- New operational tooling: `tools/moltbook/` (posting client + reviewable draft bodies), outside `reference/`.
- Conformance: none. The skill's examples are guarded the same way every other doc example is: they must run against the current reference runtime.

## Backward compatibility

Pre-v1.0. Purely additive and documentation-plus-tooling only. No change to any existing URML artifact, schema, or primitive.

## Drawbacks

- **Most Moltbook agents are not wired to a physical robot.** The direct robotics-integration overlap is thin; the realistic win is awareness and adoption of the agent skill, not a fleet of Moltbook agents driving hardware. This RFC is scoped to that honest goal, not oversold as a robotics channel.
- **Moltbook metrics skew toward vanity.** Agent counts, upvotes, and "verified agent" totals are not engagement evidence, and some viral Moltbook activity has been reported as human-puppeted. URML will not derive any engagement or adoption claim from Moltbook counters, consistent with the repo's standing "traffic reality" discipline.
- **Meta-owned, early-access API.** Moltbook was acquired by Meta in March 2026 and its developer API is early-access. Artifact B is gated on access approval and the agent-claim tweet; if access does not materialize, Artifact A (the venue-neutral skill) still stands on its own and ships regardless.
- **Proposal-plus-doc, not a deep integration.** This is deliberately a light touch. The durable deliverable is the agent skill; the Moltbook presence is a demonstration, not a product.

## Alternatives considered

1. **Do nothing; Moltbook is a fad.** Rejected as the default but respected as the risk. The hedge is that the load-bearing artifact (the agent skill) is useful with or without Moltbook, so the effort is not stranded if Moltbook fades.
2. **Build a Moltbook-specific provider into the LLM bridge.** Rejected. Moltbook is not an inference provider, and privileging any platform inside the bridge violates the provider-neutrality rule in [`CLAUDE.md`](../../CLAUDE.md). The integration stays in `tools/`, the bridge stays neutral.
3. **Skip the venue-neutral skill; write a Moltbook-only post.** Rejected. The skill is the reusable asset; a one-off post is not. Writing the skill first and pointing Moltbook at it is strictly better.
4. **Mass-register agents to inflate presence.** Rejected on ethics and on the vanity-metric discipline above. One verified, honest, AI-authorship-disclosed agent.

## Prior art

- Moltbook: social network for AI agents, launched 2026-01-28, acquired by Meta 2026-03-10; "claim tweet" verification, submolts, developer API, skills-document onboarding (public reporting: CNN, NPR, Wikipedia "Moltbook").
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's provider-agnostic LLM-to-URML bridge, the contract an agent follows.
- [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md): the normative Layer-4 prompt contract.
- [`docs/demos/bridge-roundtrip.md`](../../docs/demos/bridge-roundtrip.md): the hermetic `translate -> validate -> execute` walkthrough the demo post reuses.
- [`VIBE.md`](../../VIBE.md): the AI-assisted-authoring disclosure carried into every outreach artifact.
- [RFC-0040](0040-hugging-face-lerobot.md) and RFCs 0023-0038: the per-target outreach-RFC pattern this document inherits.
- [RFC-0021](0021-on-device-llm-bridge.md): on-device bridge, relevant to agents running the loop fully offline.

## Unresolved questions

Provisional, pending Moltbook developer-team feedback:

1. **Skill ingestion.** Is a linked Markdown document the right shape for a Moltbook agent skill, or does Moltbook expect a specific machine-readable skill manifest / endpoint?
2. **Developer-API scope.** What does the developer API authorize (post/comment/vote on behalf of a verified agent), and what are the rate and content rules for a demonstration agent?
3. **Listing.** Is there an agent-directory listing an open-standard project like URML can occupy, and what verification does it require beyond the claim tweet?
4. **Content norms.** What is the norm for an agent that posts a reproducible demo plus a pointer to a skill, versus self-promotion the community down-votes?
5. **Anything else.**

## Implementation note

RFC-0640 ships as this document plus the venue-neutral agent skill (Artifact A) and the reviewable `tools/moltbook/` glue and draft bodies (Artifact B, not yet posted). Going live with Artifact B is founder-gated on Moltbook developer-API access and the agent-claim tweet, the same public-identity split used throughout URML's outreach. Ledger entry in [`examples/lighthouses/outreach-move62.yaml`](../../examples/lighthouses/outreach-move62.yaml); the row stays `response: none` with an empty `posted_url` until a post actually lands.

## Requested feedback (from the Moltbook developer team)

1. Skill shape (linked Markdown vs a machine-readable manifest/endpoint).
2. Developer-API scope, auth, and content/rate rules for a demonstration agent.
3. Agent-directory listing path for an open-standard project.
4. Community norms for reproducible-demo posts.
5. Anything else.

## How to respond

Moltbook's developer surface is its early-access developer program and the agent/developer API. URML's planned channel: request developer-API access, register and claim the URML agent, and open the conversation through whatever issue/feedback channel the developer program exposes. URML's own public Discussions for the broader thread:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is proposed (an agent skill + a verified demo presence), and that no spec change is proposed.
- [x] Motivation grounded in a concrete technical fit (the provider-agnostic Layer-4 bridge is exactly what an agent calls) plus the skills-document onboarding model and the AI-content-welcome venue.
- [x] Detailed design names real, existing artifacts (`reference/llm-bridge/`, the Layer-4 spec, the hermetic demo) and invents no new API surface; the `LLMProvider` protocol stays the contract.
- [x] At least one alternative considered (four: do-nothing, bridge-embed, Moltbook-only post, mass-register).
- [x] Drawbacks are real and lead, not bury: thin robotics overlap, vanity metrics, Meta-owned early-access API, light-touch scope.
- [x] Backward compatibility: purely additive, docs + out-of-core tooling only.
- [x] No Layer-1-4 primitive, schema, or validator change.
- [x] Provider-neutrality preserved: Moltbook is not embedded as a provider; the posting glue lives in `tools/`, not the bridge, not `reference/`.
- [x] No cloud dependency enters `reference/`; the validated-runs-offline guarantee is untouched.
- [x] AI-authorship disclosed (VIBE.md posture) and the vanity-metric / no-engagement-claim discipline stated explicitly.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial surface, no telemetry, no data collection, DCO sign-off applies to the commit.
