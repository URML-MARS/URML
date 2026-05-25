---
rfc: 0083
title: UW Personal Robotics Lab integration, research-collab proposal to Siddhartha Srinivasa
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

# RFC-0083: UW Personal Robotics Lab integration, research-collab proposal to Siddhartha Srinivasa

## Summary

URML proposes alignment with the University of Washington Personal Robotics Lab ([`personalrobotics` GitHub org](https://github.com/personalrobotics), 242 public repos, 85 followers; led by Prof. Siddhartha Srinivasa). The ask is **research-collab** focused on assistive robotics, dexterous manipulation under clutter, learning from demonstration, and human-robot interaction. Exactly the domain where URML's English-to-primitive path lands hardest. No spec change on URML's side. Fourth Move #6 RFC.

## Motivation

The UW Personal Robotics Lab anchors **assistive + clutter + HRI** at URML's Move #6 wave. ADA (the assistive feeding robot) and HERB (the home robot) are platforms where the user's interface is fundamentally natural language and the substrate's job is to do safe motion under clutter. URML's primitive vocabulary plus static-verification surface plus English-to-primitive translation is a near-direct fit.

Verified surface (2026-05-25):
- 242 public repos, 85 followers.
- Top-starred: `aikido` (231 stars, "Artificial Intelligence for Kinematics, Dynamics, and Optimisation", C++), `prpy` (65 stars, "Python utilities used by the Personal Robotics Laboratory"), `herbpy` (7 stars, "Python library for interacting with HERB"), `ssik` (3 stars, analytical inverse kinematics), `mj_manipulator` (1 star, generic MuJoCo manipulator control).
- ADA and `pr_assets` visible in the listing.
- License pattern: BSD-3-Clause + MIT.
- Course: CSE 490R (Robot Programming & Learning) with hardware-centric labs.

Distinction worth flagging: this is the UW Personal Robotics Lab (Srinivasa, Seattle, US). Imperial College London's Personal Robotics Lab (Demiris, London, UK) is a **different lab with the same name**, covered separately by [RFC-0088 (Imperial Personal Robotics)](0088-imperial-personal-robotics-outreach.md). URML's RFCs disambiguate them by university prefix in the manifest namespacing.

URML's specific value for UW PRL:
- ADA's assistive feeding use case is the canonical example for URML's English-to-primitive path: a user instruction like "give me a bite of the broccoli" decomposes into URML primitives (`measure(bowl_location)`, `move_to(broccoli_pose)`, `grasp(food_item)`, `move_to(user_mouth_pose)`, `release(food_item)`) that the substrate executes.
- `aikido` is a kinematics-and-dynamics optimisation library; URML's substrate-Protocol abstraction sits one layer above it. Composition, not competition.
- HRI focus is the natural home for URML's English-to-primitive translation work.

## Detailed design (light, research-collab)

URML proposes:

1. **`aikido` cross-link.** A documented note clarifying that URML emits primitives at the intent layer; `aikido` solves the kinematics-and-dynamics layer; the two compose.
2. **ADA assistive-feeding pilot.** A documented mapping from URML primitives to ADA's feeding-task action surface. The mapping is paper-worthy.
3. **Coursework integration.** CSE 490R as a candidate course for URML primitive vocabulary in graduate robotics teaching.
4. **Cross-link to Imperial PRL ([RFC-0088](0088-imperial-personal-robotics-outreach.md)).** Same-named lab at a different university. URML's outreach to both is explicit; the RFCs cross-reference each other so a reader does not collapse them.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **Name collision with Imperial PRL.** Static readers might confuse the two labs. The RFC body and the manifest namespacing disambiguate, but the risk is real.
- **ADA is research-grade assistive hardware.** URML's adapter against ADA has no clinical-deployment standing; URML's posture is education and research, not medical-device certification. Same caveat as [RFC-0079 (Open Bionics)](0079-open-bionics-outreach.md).
- **`pr_assets` star counts are low.** The lab's GitHub presence underweights the actual research impact; the engagement value is in the published papers and the ADA / HERB hardware, not in repo-star metrics.

## Alternatives considered

1. **Ship the adapter first.** Rejected. The `aikido` cross-link design and the ADA mapping are research-collab questions worth maintainer input.
2. **Fold the two Personal Robotics Labs (UW + Imperial) into one RFC.** Rejected. Different PIs, different institutions, different audiences. The name collision deserves disambiguation, not collapse.

## Prior art

- `personalrobotics` GitHub org (242 public repos, 85 followers).
- `personalrobotics/aikido` (231 stars), `prpy` (65 stars), `herbpy` (7 stars), `ssik` (3 stars), `mj_manipulator` (1 star), `ada`, `pr_assets`.
- UW PRL website: `personalrobotics.cs.washington.edu`.
- CSE 490R course page.
- [RFC-0088](0088-imperial-personal-robotics-outreach.md): the parallel Imperial Personal Robotics Lab RFC; same-named lab at different university.
- [RFC-0079](0079-open-bionics-outreach.md): URML's accessibility-identity outreach; the assistive-robotics audience overlap.

## Unresolved questions

For Prof. Srinivasa + UW PRL team:

1. **`aikido` + URML composition.** Is `aikido` the right composition target for URML's substrate-Protocol implementation, or is the natural composition at a different level (e.g., on `prpy`)?
2. **ADA assistive-feeding pilot.** Interest in a documented mapping from URML primitives to ADA's task surface?
3. **Coursework integration.** Is CSE 490R a candidate course for URML primitive vocabulary?
4. **Name-collision disambiguation.** URML's manifest namespacing (`uw_personal_robotics_*` vs `imperial_personal_robotics_*`) keeps the two PRLs distinct. Any maintainer concerns?
5. **Conformance lane.** Open to a URML conformance line on `aikido` README or `personalrobotics.cs.washington.edu`?
6. **Anything else.**

## Implementation note

RFC-0083 ships as a single RFC document PR. No code in this PR. Research-collab framing. Fourth Move #6 RFC. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–6 from "Unresolved questions" above.

## How to respond

`personalrobotics/aikido` is the highest-visibility repo at 231 stars (verified 2026-05-25). URML's planned channel: open a single Issue on `personalrobotics/aikido` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Srinivasa via `sidd@cs.washington.edu` per the lab website.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] PI attribution correct (Srinivasa, UW, distinct from Demiris/Imperial).
- [x] Name-collision with Imperial PRL flagged and disambiguated.
- [x] Motivation grounded in verified `personalrobotics` surface and named repos.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, name collision, ADA clinical standing, low star counts vs. impact).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
