---
rfc: 0099
title: Wageningen Field Robot Event 2026 integration, research-collab proposal
author: Ido Yahalomi (greenvh@gmail.com)
state: Open
created: 2026-05-26
updated: 2026-05-30
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

# RFC-0099: Wageningen Field Robot Event 2026 integration, research-collab proposal

> **Update 2026-05-30 (surface recovered).** This RFC was deferred at posting time 2026-05-26 because the only documented FRE community channel was Discord (declined, per URML's preference for durable public surfaces). A 2026-05-30 re-check found a GitHub org, [`github.com/FieldRobotEvent`](https://github.com/FieldRobotEvent), with Issues enabled on `competition_environment`, `virtual_maize_field`, and `example_ws` — missed by the May surface check. The engagement was posted there ([competition_environment#25](https://github.com/FieldRobotEvent/competition_environment/issues/25)), not Discord, with the Discord acknowledged. State moves Draft → Open.

## Summary

URML proposes alignment with the **Field Robot Event (FRE) 2026**, the annual European ag-robotics competition originally organised by Wageningen University, hosted June 16-18, 2026 at the International DLG Crop Production Centre in Bernburg, Germany. The event is described as bringing together "the global field robotics community" via "an association of academic partners across Europe." The ask is **research-collab**: URML's substrate-neutral primitive vocabulary as a candidate teaching artifact for FRE participants. Engagement surface is the FRE Discord (the documented community channel from `fieldrobotevent.eu`). No spec change on URML's side. Eighth and final Move #7 RFC; closes the agriculture wave.

## Motivation

Field Robot Event is the largest annual European ag-robotics competition for academic teams. URML's substrate-neutral primitive vocabulary is positioned as a candidate teaching artifact for the participating teams; undergraduate and graduate students authoring robot programs against simulated and real ag-robotics platforms. The institutional reach of the FRE community across European universities is substantial; URML's outreach is an investment in the next generation of ag-robotics engineers.

Verified surface (2026-05-26):
- Next edition: **June 16-18, 2026** at the International DLG Crop Production Centre in Bernburg, Germany.
- Organising entity: "an association of academic partners across Europe" (specific committee members or lead PI not surfaced on the public landing page).
- Community channel: Discord (the front page directs interested parties to "Join our Discord").
- Simulation stack / ROS / Gazebo requirements: not surfaced on the public front page (URML's RFC asks the organising committee).
- ReFiBot or other open-source platforms: not surfaced on the public front page (URML's RFC asks the organising committee).
- Site redirect: `fieldrobot.org` → `fieldrobotevent.eu` (the current canonical surface).

URML's specific value for FRE community:
- **Teaching artifact for competition entrants.** URML's natural-language layer + primitive vocabulary is a pedagogical ladder above C++ ROS control code; entrants from labs that have not yet built ROS expertise can begin by writing URML programs and progressively descending into ROS as needed.
- **Cross-platform retargetability across competition substrates.** A URML program written against one entrant's robot retargets to another's by manifest swap. The competition's heterogeneity is exactly URML's substrate-neutral value proposition.
- **Cross-link to URML's existing ag-vertical outreach.** RFC-0067 (FarmBot), RFC-0092 (Acorn), RFC-0095 (UCLA AgriCruiser), RFC-0096 (INRAE Romea) all engage the same broad ag-robotics research community FRE participants come from.

## Detailed design (light, research-collab + community-channel)

URML's engagement is community-channel-first (FRE Discord). The proposal is:

1. **Discord-channel post in the FRE community server.** URML's identity, motivation, and the offer to support competition entrants who want to integrate URML's primitive vocabulary into their robot programs. Optional follow-up via the FRE organising committee (URML's RFC asks for a maintainer-of-record).
2. **URML primitive vocabulary as a candidate teaching artifact for entrants.** URML's existing `examples/` directory provides starting code; FRE-participating labs own the pedagogical integration.
3. **Cross-link to URML's other Move #7 RFCs.** A URML program written against an Acorn (RFC-0092) or against an INRAE Romea platform (RFC-0096) retargets to whatever robot the FRE entrant brings to Bernburg by manifest swap; the FRE community is the natural cross-pollination surface.
4. **Optional simulation-stack alignment.** URML's hermetic conformance lane for the future `agriculture-runtime` could compose with FRE's simulation environment (if one exists and is published; the front page does not surface details).

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **No verified GitHub engagement surface for FRE itself.** FRE is a competition / community event, not a software project. URML's standard Issue-thread engagement does not apply.
- **Front-page details are sparse.** No published simulation stack, no named organising committee, no public mailing list. URML's RFC asks for these via the Discord channel.
- **Discord is a real-time community channel, not a long-lived public record.** URML's RFC documents the engagement state internally in `outreach-move7.yaml`; the public ledger record is URML-side, not Discord-side.
- **Competition cadence is annual.** URML's engagement is single-shot per year; the FRE 2026 edition is the actionable window for this Move.
- **Language fluency.** FRE is European; substantive technical discussion welcome in English (the lingua franca of the community).

## Alternatives considered

1. **Open an Issue on a Wageningen-affiliated GitHub repo instead.** Rejected; no canonical Wageningen / FRE GitHub org with a public Issue surface was verified during URML's surface check. The Discord is the documented community channel.
2. **Skip FRE for Move #7 entirely.** Rejected; the FRE community reaches the European ag-robotics research audience URML's Move #7 wave targets; the community-channel engagement is appropriate for an annual-event surface.
3. **Wait for FRE 2026 to happen and engage post-event.** Rejected; pre-event engagement gives URML time to support entrants who want to integrate URML before the competition.

## Prior art

- Field Robot Event (FRE) at `fieldrobotevent.eu` (verified 2026-05-26; redirected from `fieldrobot.org`).
- FRE 2026 hosted June 16-18, 2026 at International DLG Crop Production Centre, Bernburg, Germany.
- "Association of academic partners across Europe" referenced on the front page.
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md), [RFC-0092 (Acorn)](0092-twisted-fields-acorn-outreach.md), [RFC-0094 (Burro Robotics)](0094-burro-robotics-outreach.md), [RFC-0095 (UCLA AgriCruiser)](0095-ucla-agricruiser-outreach.md), [RFC-0096 (INRAE Romea)](0096-inrae-romea-outreach.md): the rest of URML's agriculture-vertical outreach landscape, all relevant to FRE participants.
- [RFC-0088 (Imperial Personal Robotics Lab)](0088-imperial-personal-robotics-outreach.md): off-channel courtesy outreach precedent.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles.

## Unresolved questions

For the FRE 2026 organising committee:

1. **Maintainer of record.** Who is the lead PI / committee chair for FRE 2026? URML's RFC body would benefit from naming the contact.
2. **Simulation stack.** What ROS / Gazebo / other simulation environment does FRE 2026 expect entrants to use?
3. **ReFiBot platform.** URML's Move #4 research mentioned ReFiBot as an open-source Arduino-based FRE platform. Is ReFiBot still part of the 2026 edition?
4. **Public mailing list or forum.** Is the Discord the primary community channel, or is there a separate technical mailing list?
5. **URML primitive-vocabulary integration.** Is there interest in URML primitive vocabulary as a candidate teaching artifact for FRE entrants?
6. **Conformance lane.** Open to a URML conformance line in FRE 2026's published technical materials or on `fieldrobotevent.eu`?
7. **Anything else.**

## Implementation note

RFC-0099 ships as a single RFC document PR. No code in this PR. Research-collab framing; community-channel engagement (Discord). Eighth and final Move #7 RFC; closes the agriculture wave. Ledger entry in [`examples/lighthouses/outreach-move7.yaml`](../../examples/lighthouses/outreach-move7.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

URML's planned channel: post on the FRE 2026 Discord (linked from `fieldrobotevent.eu`) introducing URML and pointing at this RFC. If the FRE organising committee prefers a different surface (email, separate forum, GitHub org), URML's outreach pivots accordingly.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab + community-channel framing explicit.
- [x] FRE 2026 details verified from `fieldrobotevent.eu`.
- [x] Front-page-information gaps surfaced honestly (no simulation stack, no committee chair, no mailing list).
- [x] Cross-link to RFC-0067 / RFC-0092 / RFC-0094 / RFC-0095 / RFC-0096 (ag-vertical landscape) explicit.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no GitHub surface, sparse front page, Discord transience, annual cadence, language fluency).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: DE` (Bernburg, 2026 venue); EU US-friendly; default policy passes.
- [x] CLAUDE.md compliance check passed.
