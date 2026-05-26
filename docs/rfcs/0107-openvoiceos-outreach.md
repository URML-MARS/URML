---
rfc: 0107
title: OpenVoiceOS integration, research-collab proposal to OpenVoiceOS maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-26
updated: 2026-05-26
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

# RFC-0107: OpenVoiceOS integration, research-collab proposal to OpenVoiceOS maintainers

## Summary

URML proposes alignment with OpenVoiceOS (OVOS), the community-stewarded successor to Mycroft. Anchor repo: [`OpenVoiceOS/ovos-core`](https://github.com/OpenVoiceOS/ovos-core) (Apache-2.0, 275 stars, 24 open issues, Issues enabled, last commit 2026-05-14, active). The ask is **research-collab + community**: a documented composition between URML's natural-language layer ([RFC-0021](0021-on-device-llm-bridge.md)) and OVOS's intent / skill / dialogue pipeline, with URML primitives as a candidate substrate-neutral output target for OVOS skills addressing home-robotics tasks. No spec change on URML's side. **Eighth and final Move #8 RFC; closes the home-assistance wave.**

This RFC was originally scoped to [`rhasspy/rhasspy3`](https://github.com/rhasspy/rhasspy3) but pivoted to OVOS at verification time: rhasspy3 was archived shortly before this RFC drafted, while OVOS is the active, independent (i.e., outside the Home Assistant umbrella covered by [RFC-0106](0106-home-assistant-outreach.md)) community voice-assistant trajectory.

## Motivation

URML's natural-language layer (RFC-0021) compiles English-language home-robot intent into validated primitive sequences. Voice is the canonical home-context input modality; a voice assistant that emits intents into URML's compilation pipeline closes the human → voice → intent → URML primitive → substrate dispatch loop without cloud roundtrips.

OVOS specifically:
- Apache-2.0, community-stewarded post-Mycroft, on-device first.
- Skill framework where intent → URML-primitive emission is a clean composition point.
- Independent of the Home Assistant umbrella (Open Home Foundation), giving URML a second voice-stack engagement surface that complements RFC-0106 (which composes with HA's `assist_pipeline` and OHF-Voice).

Verified surface (2026-05-26):
- [`OpenVoiceOS/ovos-core`](https://github.com/OpenVoiceOS/ovos-core): Apache-2.0, 275 stars, 24 open issues, Issues enabled, last commit 2026-05-14 (active).
- NGI Zero Commons Fund grant (October 2025) supporting active development.
- Skill ecosystem inherited from Mycroft; new skills + integrations being added.
- HQ: community / Open Voice Network alignment.

URML's specific value for OVOS:
- **Substrate-neutral intent target for voice skills.** A user says "vacuum the kitchen and then dock"; OVOS's intent layer maps to a URML primitive sequence; URML compiles + validates + dispatches to whichever substrate is configured (Roomba / open-source vacuum / future home-runtime adapter). The composition: voice → OVOS intent → URML primitive → substrate. URML at the intent-validation + cross-substrate layer above OVOS's intent + dialogue layer.
- **Cross-platform retargetability.** A URML home-robot skill written for one vacuum retargets to another by manifest swap. OVOS-side skill writers benefit from URML's substrate-neutral abstraction; URML benefits from OVOS as the on-device voice substrate.
- **On-device first composition.** OVOS targets local-first execution; URML's compilation + validation runs locally without cloud roundtrips. The composition aligns with URML's offline-execution posture.
- **Strategic positioning vs Home Assistant voice stack.** RFC-0106 (Home Assistant) covers HA's `assist_pipeline` + OHF-Voice umbrella. RFC-0107 (OVOS) covers the independent voice-stack trajectory. URML composes with both, not exclusively with either.

## Detailed design (research-collab + community)

URML's existing artifacts that feed into an OVOS composition:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [RFC-0021 (on-device LLM bridge)](0021-on-device-llm-bridge.md): URML's natural-language layer; OVOS sits between voice input and URML's NL surface.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles relevant to OVOS's audience.

### Proposed composition

The proposal is **community-channel cross-citation + a candidate URML-emitter OVOS skill prototype**:

1. **A candidate `ovos-urml-skill` prototype** (Apache-2.0, in OVOS's skill format) that maps OVOS intents addressing home-robot tasks into URML primitive sequences. Prototype, not normative.
2. **Documented composition between OVOS's intent layer and URML's primitive layer** in URML's `reference/home-runtime/README.md`:
   - OVOS intent `cleaning.start_room(kitchen)` → URML `move_to(kitchen)` + `report(started)`
   - OVOS intent `lawn.mow_zone(back_yard)` → URML `move_to(back_yard)` + `wait_for(mowing_complete)`
   - OVOS intent `home.check_status(robot)` → URML `measure(battery, robot_id)` + `report(status)`
3. **Cross-link to [RFC-0021 (on-device LLM bridge)](0021-on-device-llm-bridge.md)**: OVOS's voice-input + intent layer feeds URML's NL surface; the composition direction is voice → OVOS → URML → substrate, not the reverse.
4. **Cross-link to [RFC-0106 (Home Assistant)](0106-home-assistant-outreach.md)**: URML composes with both voice stacks (HA's `assist_pipeline` + OHF-Voice, and OVOS independently). Substrate-neutrality at the voice-stack layer is itself an URML value.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML spec change.

## Drawbacks

- **Proposal-only.**
- **OVOS is community-stewarded with limited paid-maintainer bandwidth.** URML's engagement payload must be light; maintainer attention is limited compared to Home Assistant's much larger paid + sponsored team.
- **Voice-stack landscape is in flux.** rhasspy v1 archived October 2025; rhasspy3 archived shortly before this RFC drafted; OVOS, OHF-Voice, and `assist_pipeline` are the active trajectories but the relative weights are evolving. URML's composition story must be agnostic to which voice stack dominates.
- **OVOS skill format is Python-side.** URML's NL surface is language-agnostic but the OVOS composition path requires a Python-side skill prototype, adding a small dependency surface.
- **Independent of Open Home Foundation.** OVOS is outside the HA umbrella; that's a feature (alternative trajectory) but also means OVOS lacks the institutional backing HA has. URML's RFC acknowledges this openly.

## Alternatives considered

1. **Engage `rhasspy/rhasspy3` directly (the original plan).** Rejected at verification time: rhasspy3 was archived shortly before this RFC drafted. The forward voice-stack engagement target is OVOS or OHF-Voice.
2. **Engage `OHF-Voice/linux-voice-assistant` instead.** Considered. Rejected because OHF-Voice is under the Home Assistant + Open Home Foundation umbrella and is therefore already partially addressed by [RFC-0106 (Home Assistant)](0106-home-assistant-outreach.md). OVOS gives URML a separate, independent voice-stack engagement.
3. **Skip voice entirely in Move #8 and revisit in a dedicated voice-stack Move #9.** Rejected. The home-assistance audience uses voice as a primary input modality; the wave benefits from at least one voice-stack engagement to close the input-to-substrate loop.
4. **Engage `rhasspy/wyoming` (the Wyoming protocol, still maintained).** Considered. Rejected as not the right altitude. Wyoming is a protocol library, not a voice-assistant trajectory. URML's composition target is the assistant layer above Wyoming.

## Prior art

- [`OpenVoiceOS/ovos-core`](https://github.com/OpenVoiceOS/ovos-core) (Apache-2.0, 275 stars, active 2026-05-14).
- Mycroft AI (community fork lineage; OVOS is the post-Mycroft community trajectory).
- NGI Zero Commons Fund grant for OVOS (October 2025).
- [`rhasspy/rhasspy3`](https://github.com/rhasspy/rhasspy3) (archived shortly before this RFC; was the original Move #8 target).
- [`OHF-Voice/linux-voice-assistant`](https://github.com/OHF-Voice/linux-voice-assistant) (Apache-2.0, Home Assistant umbrella; covered indirectly via RFC-0106).
- [RFC-0021 (on-device LLM bridge)](0021-on-device-llm-bridge.md): URML's natural-language layer.
- [RFC-0106 (Home Assistant)](0106-home-assistant-outreach.md): the orchestration-hub sibling in Move #8.
- [RFC-0099 (Wageningen FRE)](0099-wageningen-field-robot-event-outreach.md): community-channel engagement precedent (Move #7).

## Unresolved questions

For the OpenVoiceOS maintainers:

1. **Composition appetite.** Is OVOS open to a documented composition between OVOS intents and URML primitives, with a candidate `ovos-urml-skill` prototype as an independently-maintained skill?
2. **Skill format alignment.** Which OVOS skill API version is the right composition target (OVOS v0.0.7+ stable)?
3. **Cross-link with HA's voice stack.** Does OVOS's relationship with HA's `assist_pipeline` + OHF-Voice align with URML's "compose with both" framing, or does OVOS prefer a clearer separation?
4. **On-device LLM bridge composition.** URML's RFC-0021 on-device LLM bridge is the closest URML-side architecture to OVOS's local-first voice-stack target. Interest in exploring shared infrastructure?
5. **Skill ecosystem governance.** How does OVOS govern third-party skills (review, signing, conformance)? URML's substrate-conformance discipline ([RFC-0014](0014-substrate-conformance.md)) may inform that conversation.
6. **Conformance lane.** Open to a URML conformance line on `ovos-core` README or on the OpenVoiceOS website?
7. **Anything else.**

## Implementation note

RFC-0107 ships as a single RFC document PR. No URML-side skill code in this PR. Eighth and final Move #8 RFC; closes the home-assistance wave. Ledger entry in [`examples/lighthouses/outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`OpenVoiceOS/ovos-core` has Issues enabled (24 open, verified 2026-05-26). URML's planned channel: open a single Issue on `OpenVoiceOS/ovos-core` labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Maintainer response

2026-05-26: JarbasAl ([OVOS member](https://github.com/JarbasAl)) replied on [`OpenVoiceOS/ovos-core#764`](https://github.com/OpenVoiceOS/ovos-core/issues/764) and closed the issue:

> thanks for reaching out claude, but we only engage with humans that did their proper research and validated your output

Recorded: URML's outreach prose is AI-assisted, under the maintainer's direction and review. URML now states this up-front in [`VIBE.md`](../../VIBE.md); a one-line disclosure has been added to the still-open Move #8 outreach posts. JarbasAl's preference for human-only correspondence is noted. URML accepts the close and does not pursue OVOS further on this surface unless the OVOS maintainers re-engage on a different one.

The ledger row [`examples/lighthouses/outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml) is updated to `response: wontfix` accordingly.

## Self-review (Phase 0)

- [x] Research-collab + community framing explicit.
- [x] Apache-2.0 license fit acknowledged.
- [x] Pivot from rhasspy3 (archived) to OVOS documented honestly.
- [x] Cross-link to RFC-0021 (NL layer) + RFC-0106 (HA voice-stack sibling) + RFC-0014 (conformance) explicit.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (proposal-only, limited paid-maintainer bandwidth, voice-stack landscape flux, Python skill dependency, no Foundation umbrella).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26 (with pivot from rhasspy3-archived to OVOS-active documented).
- [x] Provenance: community / Apache-2.0; default policy passes.
- [x] CLAUDE.md compliance check passed.
