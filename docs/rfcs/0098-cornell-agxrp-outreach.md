---
rfc: 0098
title: Cornell AgXRP integration, research-collab proposal (off-GitHub courtesy)
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

# RFC-0098: Cornell AgXRP integration, research-collab proposal (off-GitHub courtesy)

## Summary

URML proposes alignment with the Cornell AgXRP project (Jonathan Jaramillo, Cornell University; partnerships with University of Idaho, 4-H, Agriculture in the Classroom, community colleges). The lab self-describes as "an open-source autonomous platform that enables students to explore automation and precision agriculture through hands-on, affordable technology" at [`experiential.bot/agxrp`](https://www.experiential.bot/agxrp). **Engagement surface is off-GitHub**. URML's verification did not find a public GitHub repo or org under the AgXRP name; the platform's 3D-printable files live on Printables.com and the software library is described as "open-source" but with no specific license or GitHub URL surfaced on the project page. URML's outreach mirrors the off-GitHub courtesy pattern from [RFC-0088 (Imperial Personal Robotics Lab)](0088-imperial-personal-robotics-outreach.md). Seventh Move #7 RFC.

## Motivation

AgXRP fills a specific URML niche: **affordable open-source agricultural-robotics platform for STEM education** in rural K-12 and community-college audiences. The price positioning ("for the cost of a textbook") matches the same audience URML's natural-language layer most directly serves: educators teaching robotics to students who have not previously seen ROS or any programming-control surface.

Verified surface (2026-05-26):
- `experiential.bot/agxrp` page describes an integrated platform: physical robot kit + curriculum materials + open-source software library.
- 3D-printable files referenced on Printables.com (no direct GitHub link surfaced on the page).
- Open-source software library mentioned without specific license (Apache / MIT / GPL not surfaced on the page).
- Audience: K-12 STEM education, 4-H, Agriculture in the Classroom, community colleges.
- Institutional partnerships: Cornell University + University of Idaho mentioned; no specific PIs named beyond "Jonathan Jaramillo" associated with the project elsewhere.
- Documentation in English. Curriculum marked "Coming Soon".

URML's specific value for AgXRP:
- **English-to-robot-task path for K-12 students.** A student writes "drive the robot to the soil plot and measure soil moisture" in URML's natural-language layer; URML compiles to `move_to(...)` + `measure(soil_moisture, ...)`; the AgXRP controller dispatches the primitives. The pedagogical ladder URML offers; from natural-language English to validated robot programs; is the strongest match for the AgXRP audience.
- **Substrate-neutral retargetability across STEM platforms.** A URML program written for AgXRP retargets to VEX V5 (URML's [`reference/edu-runtime/`](../../reference/edu-runtime/) ships VexV5Adapter) or to LEGO SPIKE Prime (URML ships LegoSpikeAdapter) by manifest swap. Programs from one classroom platform run on another without rewrite.
- **Cross-link to RFC-0067 (FarmBot) on the K-12 + 4-H educational-channel side.** Both AgXRP and FarmBot reach the same broad audience of educators introducing students to precision agriculture; URML's substrate-neutral story across both lets a curriculum author write once, run anywhere.

## Detailed design (light, research-collab + off-GitHub)

URML's engagement is off-GitHub by default. The proposal is:

1. **Courtesy email to Jonathan Jaramillo via the `experiential.bot/agxrp` Contact form.** URML's identity, motivation, and feedback questions. Light engagement payload.
2. **If maintainers respond and confirm a public GitHub URL** for the open-source software library, URML's adapter integration follows the same path as [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md); adapter shipped externally in URML's `reference/edu-runtime/` (the established educational-platform runtime), with hermetic tests via fake-SDK injection.
3. **Coursework integration.** AgXRP's K-12 / 4-H curriculum + community-college audience is exactly the audience for URML's natural-language layer; coordinated module design is a possible future direction.
4. **Cross-link to [`reference/edu-runtime/`](../../reference/edu-runtime/).** URML's educational-runtime already ships VEX V5, LEGO SPIKE, Thymio, and one bipedal walking platform; an AgXRPAdapter would be the fifth adapter in the family if the AgXRP maintainers want a URML-side home for it.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **No verified GitHub engagement surface.** URML's standard public-Issue engagement pattern does not apply. Off-GitHub courtesy email is best-effort.
- **License posture unclear.** "Open-source" stated on the project page without specific license (Apache / MIT / GPL). URML's adapter integration depends on license clarity.
- **Curriculum + software status: "Coming Soon."** URML's RFC respects that AgXRP is still publishing materials; engagement is exploratory, not contingent on full release.
- **Single-maintainer or small-team project.** URML's RFC documents this and frames the engagement lightly.
- **Cornell + University of Idaho partnership-tier coordination.** URML's RFC engages Jaramillo directly; institutional partnership coordination is the maintainer's call.

## Alternatives considered

1. **Ship an `AgXRPAdapter` in `reference/edu-runtime/` immediately.** Rejected. No verified target software surface; license unclear; the off-GitHub courtesy pattern is established by RFC-0088 (Imperial PRL).
2. **Skip AgXRP for Move #7 entirely.** Rejected. The K-12 STEM ag-education audience is too aligned with URML's natural-language layer to skip; off-GitHub courtesy is appropriate.
3. **Fold AgXRP into RFC-0067 (FarmBot) as another K-12 ag-education target.** Rejected; different platforms, different maintainers, different software stacks (FarmBot has documented REST + MQTT; AgXRP has no surfaced URL).

## Prior art

- AgXRP project page (`experiential.bot/agxrp`).
- 3D-printable files on Printables.com (referenced from project page).
- Cornell University + University of Idaho partnerships (referenced from project page).
- 4-H, Agriculture in the Classroom, community-college outreach (referenced from project page).
- [`reference/edu-runtime/`](../../reference/edu-runtime/): URML's existing educational-runtime (VEX V5, LEGO SPIKE, Thymio, Marty).
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md), [RFC-0092 (Acorn)](0092-twisted-fields-acorn-outreach.md): agriculture-vertical precedents.
- [RFC-0088 (Imperial Personal Robotics Lab)](0088-imperial-personal-robotics-outreach.md): off-GitHub courtesy outreach precedent.
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md): the educational-runtime adapter-shipment precedent (path for AgXRPAdapter if engagement signals interest).

## Unresolved questions

For Jonathan Jaramillo + AgXRP team:

1. **Public GitHub URL.** Is there a GitHub repository or org for the AgXRP open-source software library? URML's verification did not surface one on `experiential.bot/agxrp`.
2. **License posture.** Specific license (Apache-2.0 / MIT / BSD / GPL) on the software library + 3D-printable files?
3. **Curriculum + software release timeline.** When is the curriculum (marked "Coming Soon") expected to publish?
4. **Coursework integration.** Is URML primitive vocabulary a candidate teaching artifact for the AgXRP curriculum or for Cornell / University of Idaho coursework?
5. **AgXRPAdapter home.** If URML ships an adapter, would `reference/edu-runtime/` (URML-side) be the right home, or would the AgXRP maintainers prefer a contributed example in their own repo when published?
6. **Cross-link to RFC-0067 (FarmBot) K-12 + 4-H audience.** Interest in coordinating?
7. **Anything else.**

## Implementation note

RFC-0098 ships as a single RFC document PR. No code in this PR. Research-collab + off-GitHub framing. Seventh Move #7 RFC. Ledger entry in [`examples/lighthouses/outreach-move7.yaml`](../../examples/lighthouses/outreach-move7.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`experiential.bot/agxrp` lists a "Contact Us" link without a specific email surfaced (verified 2026-05-26). URML's planned channel: courtesy outreach via the Contact form on `experiential.bot/agxrp` directed to Jonathan Jaramillo + AgXRP team. If the maintainer responds with a public GitHub URL, URML pivots to a standard Issue-thread engagement.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Off-GitHub + research-collab framing explicit.
- [x] No verified GitHub Issue surface acknowledged honestly.
- [x] License-posture gap surfaced.
- [x] Cross-link to RFC-0067 (FarmBot, K-12 + 4-H audience) + RFC-0088 (off-GitHub courtesy precedent) + RFC-0073 (educational-runtime adapter-shipment precedent) explicit.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no GitHub surface, license unclear, curriculum "Coming Soon", small-team, partnership coordination).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26 (absence of GitHub presence documented honestly).
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
