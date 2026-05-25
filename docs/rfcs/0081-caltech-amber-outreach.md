---
rfc: 0081
title: Caltech AMBER Lab integration, research-collab proposal to Aaron Ames
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

# RFC-0081: Caltech AMBER Lab integration, research-collab proposal to Aaron Ames

## Summary

URML proposes alignment with the Caltech AMBER Lab ([`Caltech-AMBER` GitHub org](https://github.com/Caltech-AMBER), 19 public repos, 39 followers; led by Prof. Aaron Ames). The ask is **research-collab** focused on the strongest formal-methods alignment URML has encountered in any outreach wave: AMBER's nonlinear control + hybrid-systems + bipedal-locomotion + prosthetics research is the natural home for URML's static-verification ([RFC-0014](0014-substrate-conformance.md) Draft) story. No spec change on URML's side. Second Move #6 RFC.

## Motivation

AMBER (Advanced Mechanical Bipedal Experimental Robotics) is the formal-methods anchor of URML's Move #6 outreach. Where AUTOLAB ([RFC-0080](0080-uc-berkeley-autolab-outreach.md)) is empirical / learning-based and Personal Robotics Lab ([RFC-0083](0083-uw-personal-robotics-outreach.md)) is HRI-focused, AMBER is **provably-safe control** for bipedal and prosthetic systems. URML's capability manifests + static-verification surface are a direct semantic match.

Verified surface (2026-05-25):
- 19 public repos, 39 followers; top-starred: `drop` (25 stars), `traj_opt` (12 stars), `obelisk` (10 stars, "a stable generic robot control interface"), `jaxosqp` (9 stars), `ambersim` (7 stars).
- `obelisk` has Issues enabled (53 open) and last commit 2026-05-20. Actively maintained.
- License pattern: MIT predominant (5 repos), LGPL-3.0 + GPL-2.0 + Apache-2.0 also represented.
- Lab website: `bipedalrobotics.com`; X/Twitter: `@AMBER_lab`.
- Aaron Ames holds the Bren Professor + CAST Director role at Caltech.

URML's specific value for AMBER:
- The capability manifest schema can encode bipedal joint limits, contact constraints, and hybrid-systems mode-switch boundaries. Exactly the formal surfaces AMBER's papers reason over.
- URML's `obelisk` integration is interesting: Obelisk is "a stable generic robot control interface" with explicit overlap to URML's substrate-Protocol abstraction. The RFC asks whether the two could compose.
- Prosthetics audience: URML's RFC-0079 (Open Bionics) opened accessibility as a documented identity. AMBER's prosthetics research is a natural research-side complement.

## Detailed design (light, research-collab)

URML proposes:

1. **`obelisk` cross-link.** Both `obelisk` and URML's substrate-Protocol design abstract over multiple control surfaces. A documented note (in `obelisk` README + URML's reference docs) clarifying the relationship: obelisk wraps the substrate, URML emits the intent. The two compose; they do not compete.
2. **Formal-methods integration.** URML's manifest schema as a declarative surface for the joint-limit / contact / mode-switch constraints AMBER's controllers verify against. Pilot a documented mapping from one AMBER publication's controller to URML manifest entries.
3. **Coursework integration (Caltech Robotics Minor).** URML primitive vocabulary as a teaching artifact in ME 11 (Intro Robotics) or the Robotics Minor CMS/MCE/EE courses.
4. **Prosthetics research-side complement to [RFC-0079](0079-open-bionics-outreach.md).** AMBER's prosthetics work is research-grade; the academic Open Bionics designs URML referenced are research-grade. A documented bridge (AMBER's prosthetics control + URML's intent vocabulary + the Open Bionics designs) is a possible joint paper / workshop direction.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **Mixed-license patterns.** Apache-2.0 + MIT + LGPL-3.0 + GPL-2.0 across the org; URML's adapter would have to be careful which repos it cites as integration targets. The `obelisk` repo (MIT) is the cleanest cross-link.
- **Caltech Robotics Minor has a separate Caltech Robotics Minor + JPL surface.** URML's plan parked that as a separate Move #7 candidate. RFC-0081 targets AMBER specifically; the Caltech Robotics Minor coursework conversation overlaps but is not identical.
- **Prosthetics conversation depends on RFC-0079's signal.** If the academic Open Bionics outreach stays silent (likely given dormancy), the prosthetics complement angle has less weight.

## Alternatives considered

1. **Ship the adapter first.** Rejected. The `obelisk` cross-link design is a maintainer-input question.
2. **Skip the Caltech Robotics Minor + JPL surface entirely for Move #6.** Accepted. RFC-0081 is AMBER-specific.

## Prior art

- `Caltech-AMBER` GitHub org (19 public repos, 39 followers, MIT predominant).
- `Caltech-AMBER/obelisk` (10 stars, MIT, Issues enabled, last commit 2026-05-20).
- AMBER lab website `bipedalrobotics.com`.
- `@AMBER_lab` on X/Twitter.
- Aaron Ames publications on hybrid-systems control + bipedal locomotion + prosthetic control.
- [RFC-0014](0014-substrate-conformance.md) (Draft): URML's substrate-conformance spec; AMBER's formal-methods alignment.
- [RFC-0079](0079-open-bionics-outreach.md): URML's accessibility-identity outreach (prosthetics-side research complement).
- [RFC-0009](0009-legged-humanoid-mobility.md): URML's legged-humanoid capability schema; AMBER's bipedal-locomotion research grounds this.

## Unresolved questions

For Prof. Ames + AMBER team:

1. **`obelisk` + URML composition.** Is `obelisk` a substrate-Protocol target for a URML adapter, or is URML's primitive layer better composed above `obelisk` at a different level?
2. **Formal-methods integration.** Is there a single AMBER publication whose controller would be a useful pilot for URML manifest encoding?
3. **Coursework integration.** Is Caltech Robotics Minor or ME 11 a candidate for URML primitive vocabulary as a teaching artifact?
4. **Prosthetics research-side complement to RFC-0079.** Interest in a documented bridge between AMBER's prosthetics work and URML's accessibility-identity outreach?
5. **Conformance lane.** Open to a URML conformance line on `obelisk` README or `bipedalrobotics.com`?
6. **Anything else.**

## Implementation note

RFC-0081 ships as a single RFC document PR. No code in this PR. Research-collab framing. Second Move #6 RFC. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–6 from "Unresolved questions" above.

## How to respond

`Caltech-AMBER/obelisk` has Issues enabled (53 open at time of writing; verified 2026-05-25). URML's planned channel: open a single Issue on `Caltech-AMBER/obelisk` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Ames via the contact listed on `bipedalrobotics.com`.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] Formal-methods alignment grounded in verified `obelisk` repo and AMBER's research focus.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, mixed licensing, Caltech Robotics Minor separate, prosthetics-complement dependency).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
