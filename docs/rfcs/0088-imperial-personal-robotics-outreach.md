---
rfc: 0088
title: Imperial College London Personal Robotics Lab integration, research-collab proposal to Yiannis Demiris
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-25
updated: 2026-05-25
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

# RFC-0088: Imperial College London Personal Robotics Lab integration, research-collab proposal to Yiannis Demiris

## Summary

URML proposes alignment with the Imperial College London Personal Robotics Lab (led by Prof. Yiannis Demiris). The lab's research focus. Human-centred robotics, learning from demonstration, assistive systems, HRI. Is a near-direct semantic match for URML's English-to-primitive translation path. **Engagement surface is off-GitHub.** Imperial's PRL does not have a verified standalone public GitHub org under `imperial-prl` or `Personal-Robotics-Lab-Imperial`; the umbrella `ImperialCollegeLondon` org's 746 repos do not surface PRL-specific repos in standard listings. URML's outreach mirrors the off-GitHub courtesy pattern from [RFC-0079 (Open Bionics commercial side)](0079-open-bionics-outreach.md): email Prof. Demiris via the lab website at `imperial.ac.uk/personal-robotics`. No spec change on URML's side. Ninth Move #6 RFC.

## Motivation

Imperial's Personal Robotics Lab is one of the leading UK assistive / HRI labs. The lab teaches a Human-Centred Robotics course (4th year / master level) with ROS, OpenCV, and RGB-D practicals. Exactly the audience URML's primitive vocabulary serves.

Distinction worth flagging: this is **Imperial College London's Personal Robotics Lab (Demiris)**, a different lab from the **University of Washington Personal Robotics Lab (Srinivasa)** covered in [RFC-0083](0083-uw-personal-robotics-outreach.md). Same lab name, different country, different PIs, different research focus. URML's manifests namespace them distinctly: `imperial_personal_robotics_*` vs `uw_personal_robotics_*`. The RFCs cross-reference each other so readers do not collapse them.

Surface verification (2026-05-25):
- No verified standalone `imperial-prl` or `Personal-Robotics-Lab-Imperial` GitHub org. The umbrella `ImperialCollegeLondon` org (746 repos) does not surface PRL-specific manipulation or HRI repos in standard listings.
- Lab website: `imperial.ac.uk/personal-robotics`. The documented engagement surface.
- Course: Human-Centred Robotics, 4th year / master level.
- PI email per lab website: `y.demiris@imperial.ac.uk`.

URML's specific value for Imperial PRL:
- The English-to-primitive translation path is the lab's research domain. URML's [`reference/llm-bridge/`](../../reference/llm-bridge/) plus the [RFC-0021 (on-device LLM bridge)](0021-on-device-llm-bridge.md) spec are direct collaboration candidates.
- HRI + learning-from-demonstration audience is the natural home for URML primitive vocabulary as a teaching artifact in coursework.
- Cross-link to UW Personal Robotics ([RFC-0083](0083-uw-personal-robotics-outreach.md)) makes URML's substrate-neutral story concrete across two same-named labs at different universities.

## Detailed design (light, research-collab, off-GitHub)

URML's engagement with Imperial PRL is off-GitHub by default. The proposal is:

1. **Courtesy email to Prof. Demiris.** URML's identity, motivation, and feedback questions. Light engagement payload.
2. **Cross-link mention in [RFC-0083 (UW Personal Robotics)](0083-uw-personal-robotics-outreach.md).** Already done; the two RFCs reference each other.
3. **Optional: URML's `reference/llm-bridge/` cross-citation.** If the lab maintains any public LLM-to-robot-action work, URML cites it in the bridge documentation; vice versa, the lab is invited to mention URML.
4. **Coursework integration.** Human-Centred Robotics course at Imperial as candidate for URML primitive vocabulary lecture.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero code today.

## Drawbacks

- **No verified GitHub Issue engagement surface.** URML's standard public-Issue engagement pattern (Moves #1–#5) does not apply. Off-GitHub courtesy email is best-effort.
- **Same-name lab confusion with UW PRL.** Disambiguation handled in RFC bodies and manifests; the risk is real but bounded.
- **PI attention scarce.** Imperial is a research-intensive university; Demiris's inbox is full.
- **Imperial may maintain private GitHub orgs URML did not surface.** The verification check looked for public PRL-specific repos but found none; private maintainer surfaces may exist.

## Alternatives considered

1. **Ship a `ImperialPersonalRoboticsAdapter`.** Rejected. No verified target software surface, no adapter to write.
2. **Fold Imperial and UW PRL into one RFC.** Rejected. Different countries, different PIs, different audiences; collapsing them obscures the disambiguation work.
3. **Skip Imperial PRL entirely.** Rejected. The lab's research focus is too aligned with URML's English-to-primitive path to skip; off-GitHub courtesy outreach is appropriate.

## Prior art

- Imperial College London Personal Robotics Lab website: `imperial.ac.uk/personal-robotics`.
- Yiannis Demiris's publications on assistive robotics + learning from demonstration + HRI.
- Human-Centred Robotics course (Imperial, 4th year / master).
- [RFC-0083](0083-uw-personal-robotics-outreach.md): the same-named UW Personal Robotics Lab outreach.
- [RFC-0021](0021-on-device-llm-bridge.md): URML's on-device LLM bridge spec.
- [RFC-0079](0079-open-bionics-outreach.md): the off-GitHub courtesy outreach pattern (commercial side of Open Bionics).

## Unresolved questions

For Prof. Demiris + Imperial PRL team:

1. **Engagement surface.** Is there a maintainer-preferred surface (email / lab website form / a private GitHub org URML missed) for substantive engagement?
2. **Coursework integration.** Is Human-Centred Robotics a candidate course for URML primitive vocabulary?
3. **LLM-bridge cross-link.** Does the lab maintain LLM-to-robot-action work that URML's `reference/llm-bridge/` should cite or coordinate with?
4. **Name-collision disambiguation.** URML's manifest namespacing (`imperial_personal_robotics_*` vs `uw_personal_robotics_*`) keeps the two PRLs distinct. Any maintainer concerns?
5. **Conformance lane.** Open to a URML conformance line on `imperial.ac.uk/personal-robotics` (where the lab leadership decides)?
6. **Anything else.**

## Implementation note

RFC-0088 ships as a single RFC document PR. No code in this PR. Research-collab + off-GitHub framing. Ninth Move #6 RFC. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–6 from "Unresolved questions" above.

## How to respond

URML's planned channel: courtesy email to Prof. Demiris via `y.demiris@imperial.ac.uk` per the lab website at `imperial.ac.uk/personal-robotics`. If the lab maintains a public engagement surface URML did not surface during verification, the founder can pivot to that. The courtesy email is best-effort; no URML public GitHub Issue.

URML's own public Discussions for the broader Move #6 conversation: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab + off-GitHub framing explicit.
- [x] Name-collision with UW PRL disambiguated.
- [x] No verified GitHub Issue surface flagged honestly.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no GitHub Issue surface, name collision, PI attention, possible private surfaces).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25; absence of public PRL-specific GitHub presence documented.
- [x] Provenance `origin: UK`; default policy passes.
- [x] CLAUDE.md compliance check passed.
