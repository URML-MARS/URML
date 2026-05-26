---
rfc: 0106
title: Home Assistant integration, research-collab proposal to home-assistant/core maintainers
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

# RFC-0106: Home Assistant integration, research-collab proposal to home-assistant/core maintainers

## Summary

URML proposes alignment with Home Assistant via the [`home-assistant/core`](https://github.com/home-assistant/core) GitHub repository (87.3k stars, Apache-2.0, ~4000 open issues, Issues enabled, active 2026-05-26). The ask is **research-collab + community**: a documented mapping between URML's substrate-neutral primitive vocabulary and Home Assistant's automation / script / template engine, with URML primitive sequences compiling into Home Assistant automation YAML for robotic entities (vacuum, lawnmower, pool cleaner, etc.). No spec change on URML's side. **Seventh Move #8 RFC and strategic anchor for the home-assistance wave**; every other Move #8 target (Roomba via `roomba` integration, Husqvarna via `husqvarna_automower`, Maytronics Dolphin via `dolphin-robot`, ROBOTIS-driven platforms via custom integrations) already lives natively as a Home Assistant integration. URML composes with Home Assistant, not against it.

## Motivation

Home Assistant is the de facto orchestration hub for home robotics and home automation globally. The project is community-stewarded under the Open Home Foundation (formed 2024), Apache-2.0-licensed, and the largest open-source home-automation codebase by community engagement. Every meaningful home-assistance robot vendor either ships with a first-class Home Assistant integration or has a community-maintained integration in `home-assistant/core` or HACS.

Verified surface (2026-05-26):
- [`home-assistant/core`](https://github.com/home-assistant/core): Apache-2.0, 87.3k stars, ~4000 open issues, Issues enabled, last commit 2026-05-26 (active). Very large maintainer community + sponsoring foundation.
- Robot vacuum integrations: `roomba`, `roborock` (PRC, off URML default policy), `ecovacs` (PRC, off URML default policy), `neato` (EOL).
- Outdoor robot integrations: `husqvarna_automower`, `worx_landroid`.
- Pool cleaner integration: `dolphin-robot` (via HACS community store).
- Voice / NLP integrations: `assist_pipeline`, integrations with OHF-Voice, OpenVoiceOS, Rhasspy-class wyoming-protocol satellites.
- Open Home Foundation (the umbrella) governs Home Assistant + ESPHome + Voice + several other community projects.

URML's specific value for Home Assistant:
- **Compilation target.** URML primitives compile into Home Assistant automation YAML; a URML program describing "vacuum the kitchen at 7 AM unless someone is home" compiles to an HA automation with a `vacuum.start` action gated by a person tracker. Home Assistant's existing entity / template / blueprint model is the substrate.
- **Cross-vendor consistency.** Home Assistant abstracts vendor-specific quirks at the entity level (every vacuum exposes `start`, `stop`, `return_to_base`, `set_fan_speed`, etc.). URML's substrate-neutrality benefits from that abstraction; URML's value-add is the natural-language layer ([RFC-0021 on-device LLM bridge](0021-on-device-llm-bridge.md)) plus formal verification ([RFC-0014 substrate conformance](0014-substrate-conformance.md)) above the HA entity layer.
- **Strategic anchor for URML's Move #8 wave.** Every other Move #8 target ([RFC-0100 iRobot Roomba](0100-irobot-roomba-outreach.md), [RFC-0101 Husqvarna Automower](0101-husqvarna-automower-outreach.md), [RFC-0103 Maytronics Dolphin](0103-maytronics-dolphin-outreach.md)) already integrates with Home Assistant. URML's home-assistance story is most coherent when paired with HA as the orchestration layer.
- **Apache-2.0 license fit.** Both URML and HA are Apache-2.0; no license-fit nuance.

## Detailed design (research-collab + community)

URML's existing artifacts that feed into a Home Assistant cross-citation:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): URML's static-verification path; Home Assistant entities are a candidate substrate to conform against.
- [RFC-0021 (on-device LLM bridge)](0021-on-device-llm-bridge.md): URML's natural-language layer; HA's voice + assist pipeline is the canonical home-side composition target.

### Proposed composition

The proposal is **community-channel cross-citation + a candidate `urml` integration prototype**, not a stand-alone URML adapter against HA:

1. **A candidate `urml` integration for Home Assistant** (Python, in HACS-style format) that exposes URML compilation as a HA service. A user writes a URML program (natural-language English); the `urml` integration compiles it to HA automation YAML, validates against the user's HA entity manifest, and offers to install. Prototype, not normative.
2. **Documented mapping between URML primitives and HA entity actions** in URML's `reference/home-runtime/README.md`:
   - URML `move_to(region)` → HA `vacuum.send_command(custom_room_id)` / `lawn_mower.start_with_zone(...)`
   - URML `measure(battery)` → HA `sensor.battery_level` state
   - URML `wait_for(docked)` → HA `vacuum.docked` state polling
   - URML `report(...)` → HA `notify` / `mqtt.publish`
3. **Cross-link to OHF-Voice / OpenVoiceOS / `assist_pipeline`**: URML's natural-language layer compiles into HA's voice intent surface, not in competition with it.
4. **Community-channel engagement framing**, similar to but distinct from RFC-0099 (Wageningen FRE community channel): HA has well-defined GitHub Issues + Discussions, no Discord-only constraint.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML spec change. Zero modification to HA core in this RFC.

## Drawbacks

- **Very large maintainer community.** `home-assistant/core` has ~4000 open issues at verification time; the URML RFC is small relative to that volume. URML's engagement payload must be sized appropriately (one Issue or one Discussion, not many).
- **HA's automation language is intentionally accessible to non-coders.** URML's natural-language layer overlaps with HA's existing blueprints + UI editor. URML's value-add must be framed honestly (formal verification + substrate-neutrality + LLM-bridge composition) rather than as a competitor.
- **Voice-stack overlap with OHF-Voice / OpenVoiceOS / `assist_pipeline`.** URML's RFC-0021 LLM bridge composes above these voice layers, not below; the RFC body must make that composition direction explicit to avoid confusion.
- **Engagement-channel choice.** HA has many sub-projects (`core`, `frontend`, `operating-system`, `architecture`); URML's RFC engages `core` as the canonical primary surface. If maintainers redirect to a different channel (e.g. `architecture`), URML pivots.
- **Foundation politics.** Open Home Foundation governs HA + ESPHome + Voice + several adjacent projects. URML's RFC engages the HA maintainer community directly; broader Foundation engagement is downstream of any substantive HA-side response.

## Alternatives considered

1. **Skip Home Assistant entirely and engage only the specific vendor integrations (Roomba, Husqvarna, Dolphin).** Rejected. HA is where home-assistance robots already live; engaging the orchestration layer directly is higher-leverage than engaging only the individual integration repos.
2. **Engage Open Home Foundation directly (the umbrella).** Rejected as a first move. The Foundation is the governing body; substantive technical discussion lives at the project level (HA core, ESPHome, Voice). Foundation engagement is downstream of project-level engagement.
3. **Engage Home Assistant's `architecture` repo for a formal architecture-decision-record process.** Considered but rejected as the first move. The `core` repo Issues + Discussions are the canonical entry point; if HA maintainers indicate `architecture` is the right surface, URML pivots accordingly.

## Prior art

- [`home-assistant/core`](https://github.com/home-assistant/core): Apache-2.0, 87.3k stars.
- Open Home Foundation (formed 2024) governing HA + ESPHome + Voice.
- HA integrations relevant to URML's Move #8 wave: `roomba` (paired with [RFC-0100](0100-irobot-roomba-outreach.md)), `husqvarna_automower` (paired with [RFC-0101](0101-husqvarna-automower-outreach.md)), `dolphin-robot` via HACS (paired with [RFC-0103](0103-maytronics-dolphin-outreach.md)).
- [RFC-0021 (on-device LLM bridge)](0021-on-device-llm-bridge.md): URML's natural-language layer; HA's voice pipeline is the canonical home-side substrate.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): URML's static-verification path; HA entities are a candidate conformance target.
- [RFC-0099 (Wageningen FRE)](0099-wageningen-field-robot-event-outreach.md): community-channel engagement precedent (Move #7); RFC-0106 is the same framing without the Discord-only constraint.

## Unresolved questions

For the `home-assistant/core` maintainers + Open Home Foundation:

1. **Engagement-channel preference.** Is `home-assistant/core` Issues the right surface, or would HA prefer GitHub Discussions / `architecture` / a different repo?
2. **`urml` integration prototype.** Would HA welcome a community-maintained `urml` HACS integration, or would the maintainer community prefer URML's compilation surface to live entirely externally?
3. **Voice-stack composition.** How does URML's natural-language layer (RFC-0021) compose with HA's existing voice / assist pipeline + OHF-Voice / OpenVoiceOS without overlap?
4. **Blueprint format.** Could URML compile to HA Blueprint YAML (the existing community-share format) as well as / instead of automation YAML?
5. **Formal-verification angle.** URML's static-verification path (RFC-0014) could check user automation safety against entity manifests. Is there appetite from the HA community for that surface?
6. **Cross-vendor entity-model normalisation.** HA already normalises vacuum / lawn_mower / pool entity classes. Are there gaps URML's substrate-neutral story could surface back to the HA maintainer community?
7. **Conformance lane.** Open to a URML conformance line on the `home-assistant/core` README or in HA's developer docs?
8. **Anything else.**

## Implementation note

RFC-0106 ships as a single RFC document PR. No URML-side adapter code in this PR. Seventh Move #8 RFC; strategic anchor for the home-assistance wave. Ledger entry in [`examples/lighthouses/outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml).

## Requested feedback

Items 1–8 from "Unresolved questions" above.

## How to respond

`home-assistant/core` has both Issues (~4000 open) and the broader GitHub Discussions / community forum (community.home-assistant.io) (verified 2026-05-26). URML's planned channel: open a single Issue on `home-assistant/core` labelled with the closest `question` / `feature_request` equivalent, pointing to this RFC. If HA maintainers redirect to Discussions or the community forum, URML pivots accordingly.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab + community framing explicit.
- [x] Strategic-anchor positioning surfaced (Home Assistant is where every other Move #8 target lives).
- [x] Apache-2.0 license fit acknowledged.
- [x] Cross-link to RFC-0100 / 0101 / 0103 (the Move #8 vendor RFCs that depend on HA) + RFC-0021 (NL layer) + RFC-0014 (conformance) explicit.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (large maintainer-community surface, automation-language overlap, voice-stack overlap, channel-choice ambiguity, foundation politics).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added. Home-profile question deferred to a future Spec RFC.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance: community / Apache-2.0 / Open Home Foundation; default policy passes.
- [x] CLAUDE.md compliance check passed.
