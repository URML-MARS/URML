---
rfc: 0089
title: Oxford Robotics Institute (ORI) integration, research-collab proposal to Paul Newman
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

# RFC-0089: Oxford Robotics Institute (ORI) integration, research-collab proposal to Paul Newman

## Summary

URML proposes alignment with the Oxford Robotics Institute (ORI) via the [`oxford-robotics-institute` GitHub org](https://github.com/oxford-robotics-institute) (2 public repos, 76 followers; led by Prof. Paul Newman). The lab's research focus. Mobile robotics, SLAM, autonomous systems, perception. Is a strong URML cross-link, but the **public GitHub presence is thin**: only 2 public repos verified, with `radar-robotcar-dataset-sdk` (90 stars) as the most-visible. ORI's research is heavily published but the engagement surface is the lab website plus Paul Newman's email. No spec change on URML's side. Tenth Move #6 RFC.

## Motivation

Oxford ORI is one of the UK's leading mobile-robotics + SLAM + autonomous-driving research labs. Paul Newman's RobotCar Dataset (2014, refreshed with the Radar RobotCar Dataset) is a globally-cited research artifact.

Verified surface (2026-05-25):
- 2 public repos in `oxford-robotics-institute`: `radar-robotcar-dataset-sdk` (90 stars, Python; "Supplementary tools for the Oxford Radar RobotCar Dataset"), `oord-dataset` (1 star, HTML).
- 76 followers.
- The `ori-drs` and `ori-systems` orgs that the Move #6 research plan mentioned were NOT verified during surface check; they may exist as private orgs or under a different naming convention.
- Lab website: `ori.ox.ac.uk`.
- PI: Paul Newman (lab founder).

URML's specific value for Oxford ORI:
- **RobotCar Dataset cross-link.** URML's existing [RFC-0042 (Waymo Open Dataset)](0042-waymo-open-dataset.md) outreach proposed an annotation pattern for dataset trajectories. The same annotation pattern could apply to the Oxford Radar RobotCar Dataset; the cross-link is documentation.
- **Mobile robotics + SLAM coursework.** Oxford's Engineering Science department teaches robotics within the engineering curriculum; URML primitive vocabulary as a teaching artifact is a possible coursework module.
- **Autonomous-driving research cross-link.** ORI publishes against the autonomous-vehicle research community; URML's [RFC-0020 (Autoware AV substrate)](0020-autoware-av-substrate.md) Draft is the institutional bridge.

## Detailed design (light, research-collab)

URML's engagement with Oxford ORI mirrors the off-GitHub-mostly pattern from RFC-0088 (Imperial PRL) because the GitHub footprint is thin. The proposal is:

1. **Issue on `oxford-robotics-institute/radar-robotcar-dataset-sdk`.** The most-active ORI repo; URML files there as a pointer to the RFC.
2. **Courtesy email to Prof. Newman.** Via the lab website at `ori.ox.ac.uk/people/paul-newman` or `paul.newman@eng.ox.ac.uk`.
3. **Radar RobotCar Dataset annotation cross-link to [RFC-0042 (Waymo)](0042-waymo-open-dataset.md).** Documented note that URML's annotation pattern applies to both datasets.
4. **Coursework integration.** Engineering Science robotics curriculum as candidate audience.
5. **Autonomous-driving cross-link to [RFC-0020 (Autoware)](0020-autoware-av-substrate.md).** ORI's AV research and URML's AV substrate work are adjacent; documented note.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero code today.

## Drawbacks

- **Thin GitHub presence.** Only 2 public repos in the verified `oxford-robotics-institute` org. URML's standard public-Issue engagement is constrained.
- **Possible private orgs.** `ori-drs` and `ori-systems` were mentioned in the Move #6 planning but not verified; URML's RFC documents this honestly.
- **PI attention scarce.** Paul Newman is one of the UK's most senior robotics PIs; inbound traffic is high.
- **Dataset focus narrows the engagement.** Most of ORI's open-source surface is dataset-specific (RobotCar, OORD); a URML adapter against ORI's research is composition with the dataset annotation, not adapter shipping.

## Alternatives considered

1. **Ship an `OxfordORIAdapter`.** Rejected. No clear substrate surface to wrap; ORI's research outputs are mostly datasets + papers + dataset SDKs.
2. **Skip Oxford ORI entirely.** Rejected. The lab's UK leadership reputation plus the dataset cross-link to [RFC-0042](0042-waymo-open-dataset.md) make engagement worthwhile despite the thin GitHub footprint.

## Prior art

- `oxford-robotics-institute` GitHub org (2 public repos, 76 followers).
- `oxford-robotics-institute/radar-robotcar-dataset-sdk` (90 stars, Python).
- `oxford-robotics-institute/oord-dataset` (1 star).
- Oxford Radar RobotCar Dataset (the canonical mobile-robotics dataset Newman's group published).
- Oxford ORI website: `ori.ox.ac.uk`.
- [RFC-0042](0042-waymo-open-dataset.md): URML's Waymo Open Dataset outreach with documented annotation pattern.
- [RFC-0020](0020-autoware-av-substrate.md): URML's Autoware AV substrate Draft.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles.

## Unresolved questions

For Prof. Newman + Oxford ORI team:

1. **Engagement surface.** Is there a maintainer-preferred surface (a private GitHub org URML did not surface, an internal mailing list, the lab website's contact form) for substantive engagement?
2. **Radar RobotCar Dataset annotation.** Is the URML annotation pattern from [RFC-0042](0042-waymo-open-dataset.md) applicable to the Oxford Radar RobotCar Dataset?
3. **Coursework integration.** Is Engineering Science's robotics curriculum a candidate for URML primitive vocabulary?
4. **Autonomous-driving cross-link.** Should URML's open [RFC-0020 (Autoware)](0020-autoware-av-substrate.md) Draft coordinate with ORI's autonomous-driving research direction?
5. **`ori-drs` and `ori-systems` clarification.** Are these public GitHub orgs (URML did not verify) or private internal surfaces?
6. **Conformance lane.** Open to a URML conformance line on `ori.ox.ac.uk` or in the RobotCar Dataset SDK README?
7. **Anything else.**

## Implementation note

RFC-0089 ships as a single RFC document PR. No code in this PR. Research-collab framing with light off-GitHub fallback. Tenth Move #6 RFC. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

URML's planned channel: open a single Issue on `oxford-robotics-institute/radar-robotcar-dataset-sdk` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Newman via `ori.ox.ac.uk/people/paul-newman`. If the maintainers redirect to a private org or different surface, follow that.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] Thin GitHub presence acknowledged directly.
- [x] Cross-links to RFC-0042 (Waymo) and RFC-0020 (Autoware) explicit.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (thin GitHub, possible private orgs, PI attention, dataset-narrow focus).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25; `ori-drs` / `ori-systems` unverified status flagged.
- [x] Provenance `origin: UK`; default policy passes.
- [x] CLAUDE.md compliance check passed.
