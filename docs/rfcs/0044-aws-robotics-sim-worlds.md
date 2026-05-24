---
rfc: 0044
title: AWS Robotics simulation worlds conformance lane, request for comment from aws-robotics maintainers
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

# RFC-0044: AWS Robotics simulation worlds conformance lane, request for comment from aws-robotics maintainers

## Summary

URML proposes a hermetic conformance lane that runs URML programs against the open AWS RoboMaker simulation worlds maintained at `github.com/aws-robotics`. Each world maps to a URML domain profile: `aws-robomaker-small-warehouse-world` to URML's warehouse profile ([RFC-0022](0022-warehouse-domain-profile.md)), `aws-robomaker-small-house-world` to the home profile, `aws-robomaker-hospital-world` to a future hospital profile, `aws-robomaker-bookstore-world` to a retail subset of home, and `aws-robomaker-racetrack-world` to a low-altitude drone course. The worlds are MIT-0 licensed and run on Gazebo without any AWS cloud dependency. The lane builds on the Gazebo bridge proposed in [RFC-0037](0037-osrf-gazebo-integration.md). No spec change is proposed in this RFC. The lane is proposal-only; the RFC requests review and feedback from `aws-robotics` maintainers before the conformance fixtures publish.

This is a proposal-only outreach RFC in the established pattern: RFC-0037 (OSRF / Gazebo), RFC-0040 (Hugging Face LeRobot), RFC-0041 (ArduPilot), RFC-0042 (Waymo). RFC-0043 (Boston Dynamics) is the "already shipping" sibling. RFC-0044 is the fifth in the wave and the second conformance-demonstration shape after RFC-0042.

## Motivation

The AWS Robotics organization on GitHub publishes a family of free-to-use Gazebo simulation worlds that became a de facto research and education resource after the AWS RoboMaker managed service was retired in October 2023. The repositories are still maintained: `aws-robomaker-small-warehouse-world` (472 stars, MIT-0, last commit 2026-05-11), `aws-robomaker-small-house-world` (276 stars, MIT-0, last commit 2026-05-20), `aws-robomaker-hospital-world` (257 stars, 9 open issues, MIT-0, last commit 2026-05-15), plus the bookstore and racetrack siblings and the sample applications. Twelve of the most-starred `aws-robotics` repositories carry between 22 and 472 stars and are unarchived.

URML's reference adapter family commits to demonstrating that the same URML program can run across simulation and real hardware without code change, and across domain profiles without primitive surgery. The honest test is whether existing URML conformance fixtures (warehouse AMRs per [RFC-0022](0022-warehouse-domain-profile.md), home-profile programs, drone-profile inspection per `spec/profiles/drone/`) execute correctly inside a community-recognized open sim world. The AWS worlds are the most-cited open Gazebo asset family for exactly the profiles URML already covers; running URML programs in them is the conformance proof URML needs and a worked URML example the community gets.

The integration is light. The worlds are Gazebo `.world` files and SDF asset packs. URML's existing Gazebo bridge (proposed in [RFC-0037](0037-osrf-gazebo-integration.md)) executes URML programs against any Gazebo world. The conformance lane is a thin glue: load the AWS world, spawn a URML-manifested robot in it, execute the URML program, assert outcomes.

## Detailed design

URML's existing artifacts that feed into the conformance lane:

- [`docs/rfcs/0022-warehouse-domain-profile.md`](0022-warehouse-domain-profile.md): the warehouse profile, Draft. Ships eight conformance fixtures and a warehouse manifest fixture today.
- [`docs/rfcs/0037-osrf-gazebo-integration.md`](0037-osrf-gazebo-integration.md): the Gazebo bridge outreach RFC. The substrate that executes URML programs in `.world` files.
- [`spec/profiles/drone/`](../../spec/profiles/drone/): the drone profile, which the racetrack world maps to as a low-altitude course.
- [`reference/mobile-runtime/`](../../reference/mobile-runtime/): the AMR base runtime; the canonical warehouse robot is `mobile-runtime` plus an industrial-arm `CompositeAdapter`, exactly the configuration the small-warehouse-world is designed for.
- [`reference/validator/`](../../reference/validator/): the static validator that runs against URML programs before they reach the sim.

### Proposed conformance lane shape

A new `conformance/lanes/aws-worlds/` directory in the URML repository, sibling to the existing `conformance/fixtures/`. Each lane subdirectory pairs one AWS world with the URML programs that validate against it:

```
conformance/lanes/aws-worlds/
├── README.md                          # licensing + Gazebo install posture
├── warehouse/
│   ├── world.url                      # pointer to aws-robomaker-small-warehouse-world commit SHA
│   ├── manifest.yaml                  # URML capability manifest matching the world's robot spawn
│   ├── programs/                      # URML programs validated against the manifest
│   └── expectations.yaml              # asserted outcomes
├── house/
├── hospital/
├── bookstore/
└── racetrack/
```

World assets stay at AWS Robotics' upstream repositories. URML pins each lane to a specific upstream commit SHA. The lane does not redistribute world content; it references it via `world.url` and `git submodule` instructions (or `vcstool` in ROS 2 deployments) so users fetch the assets directly from `aws-robotics` under MIT-0 terms.

### Proposed world to profile mapping

| AWS world | URML profile | URML primitive emphasis | Status |
|---|---|---|---|
| `aws-robomaker-small-warehouse-world` (472 stars, MIT-0) | warehouse | `move_to`, `pick_from`, `place_at`, `wait_for`, multi-AMR mixed-traffic | profile shipped (RFC-0022 Draft) |
| `aws-robomaker-small-house-world` (276 stars, MIT-0) | home | `move_to`, `detect`, `report`, room-by-room navigation | profile shipped |
| `aws-robomaker-hospital-world` (257 stars, MIT-0) | (no URML hospital profile yet) | `move_to`, `detect`, `wait_for(person)`, corridor navigation | deferred; a future RFC adds a hospital profile if demand surfaces |
| `aws-robomaker-bookstore-world` (87 stars, MIT-0) | home (retail subset) | shelf-aware navigation, `detect(object: book)` | scoped under home; a retail profile is a future RFC |
| `aws-robomaker-racetrack-world` (54 stars, MIT-0) | drone | `take_off`, `move_to(waypoint)`, `scan(course)`, `land` | profile shipped |

Sample applications (`aws-robomaker-sample-application-helloworld`, the archived `aws-robomaker-sample-application-cloudwatch`) are out of scope; the lane targets the world repositories.

### Proposed validation methodology

Each lane fixture passes three checks before publication:

1. Parse and validate the URML program against the lane's manifest using the URML static validator.
2. Validate the manifest against the world's robot spawn (drive type, sensors, base footprint, max velocity).
3. Execute the program in Gazebo with the AWS world loaded, via the bridge proposed in [RFC-0037](0037-osrf-gazebo-integration.md). Outcomes (final pose, success state, declared events fired) are asserted against `expectations.yaml`.

Failures are documented in the lane README, not silently dropped. The lane is a coverage proof, not a curated success rate.

### Compatibility notes

- **License posture.** AWS Robotics world repositories ship under MIT-0 (MIT No Attribution), the most permissive widely used OSS license. URML's lane code is Apache 2.0. The lane references AWS worlds without redistribution, so the licenses do not interact at the artifact level. MIT-0 permits redistribution and modification even without attribution, which would let URML vendor or fork worlds if upstream stalls; the lane intentionally does not exercise that path by default.
- **Gazebo version.** AWS worlds were authored against Gazebo Classic (Gazebo 11) and various Ignition / Gazebo Sim versions over time. The lane targets Gazebo Sim (the modern, ignition-derived line) to align with [RFC-0037](0037-osrf-gazebo-integration.md). Per-world Gazebo-version pinning lives in each lane subdirectory's README.
- **AWS RoboMaker.** The managed cloud service was retired by AWS in October 2023. The GitHub world repositories are the surviving artifact; the lane targets them directly and has no AWS cloud dependency. Per URML's manifesto, reference work runs fully offline once validated.
- **Python and ROS.** The lane consumes URML's existing validator and runtime stack; no new Python or ROS dependencies beyond what the Gazebo bridge already requires.
- **Origin.** AWS is a US entity (Amazon Web Services, Inc., a subsidiary of Amazon.com, Inc., incorporated in Delaware). The world repositories pass URML's bundled US-federal default policy ([RFC-0003](0003-us-alignment.md), [RFC-0004](0004-compliance-policy.md)) without flagging at the asset level.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none in this RFC.
- Conformance suite: a new `conformance/lanes/aws-worlds/` directory ships with each per-world lane subdirectory, gated behind a `URML_AWS_WORLDS_LANE=1` env flag in CI to keep the default suite hermetic.

## Backward compatibility

Pre-v1.0. Purely additive. No URML artifact changes. The lane consumes upstream AWS world repositories by pinned SHA and does not modify them.

## Drawbacks

- **Proposal-only is a weaker artifact than a published lane.** The honest framing matches RFC-0042: URML wants `aws-robotics` maintainer input on the upstream-pinning approach and the per-world Gazebo-version-pinning question before the lane publishes, because both are choices with real downstream consequences.
- **Five worlds is wider than the current URML profile set.** Hospital and bookstore do not yet have URML profile homes. The lane covers them as deferred entries rather than papering over the gap with a forced mapping.
- **Gazebo Sim version drift.** AWS worlds were authored against different Gazebo lines over the years. Maintaining per-world version pins is real ongoing work. Mitigation: each lane README pins a known-working Gazebo version and CI gates on that.
- **AWS RoboMaker context.** The managed service is retired; some readers will conflate the GitHub world repos with the discontinued cloud product. The lane README and the RFC both state the posture explicitly: this work targets the open GitHub worlds, not a cloud service.

## Alternatives considered

1. **Vendor the world assets into URML's repository.** Rejected. MIT-0 permits it, but vendoring drift-locks the worlds at one URML commit and divorces them from upstream improvements. The reference-by-SHA approach keeps URML aligned with `aws-robotics` upstream.
2. **Skip AWS worlds and use only OSRF's Fuel-distributed assets.** Rejected. OSRF Fuel is the right long-term home for community Gazebo worlds, but the AWS worlds are the most-cited concrete artifacts for the URML profiles that already ship, and the OSRF outreach (RFC-0037) is independent of which assets the lane targets.
3. **Defer until URML adds a hospital profile.** Rejected. Three of the five worlds (warehouse, house, racetrack) map cleanly to shipping URML profiles; deferring the lane until all five worlds have URML profile homes is letting perfect be the enemy of good.
4. **Publish the lane without consulting `aws-robotics` maintainers.** Rejected. The same posture as RFC-0040 and RFC-0042: a pre-RFC saves rework on pinning and Gazebo-version choices, and a downstream link from the world repositories to URML's conformance lane is meaningfully more useful than a one-way reference.

## Prior art

- `aws-robotics/aws-robomaker-small-warehouse-world`: the warehouse world (472 stars, MIT-0, Issues enabled, `enhancement` and `question` labels both present, last commit 2026-05-11).
- `aws-robotics/aws-robomaker-small-house-world`: the home world (276 stars, MIT-0, last commit 2026-05-20).
- `aws-robotics/aws-robomaker-hospital-world`: the hospital world (257 stars, 9 open issues, MIT-0, last commit 2026-05-15).
- `aws-robotics/aws-robomaker-bookstore-world` and `aws-robomaker-racetrack-world`: bookstore and drone-course worlds (87 and 54 stars respectively, both MIT-0).
- `aws-robotics/aws-robomaker-sample-application-helloworld` and related sample apps: out of scope for the lane.
- [RFC-0022](0022-warehouse-domain-profile.md): the warehouse profile, which the small-warehouse-world maps to directly.
- [RFC-0037](0037-osrf-gazebo-integration.md): the Gazebo bridge outreach RFC; the substrate the lane runs on.
- [RFC-0040](0040-hugging-face-lerobot.md): proposal-only outreach precedent (AI/ML layer).
- [RFC-0041](0041-ardupilot-integration.md): proposal-only outreach precedent (substrate).
- [RFC-0042](0042-waymo-open-dataset.md): proposal-only conformance-demo precedent.
- [RFC-0043](0043-boston-dynamics-spot-integration.md): the "already shipping" sibling RFC.

## Unresolved questions

Provisional pending `aws-robotics` maintainer feedback:

1. **Upstream pinning approach.** URML pins each lane to a specific upstream commit SHA. Is that the right granularity, or would the maintainers prefer URML pin to release tags (when present) for forward-compatibility signals?
2. **Gazebo version targeting.** The lane targets Gazebo Sim. Some of the AWS world repos still mention Gazebo Classic (Gazebo 11) in their READMEs. What is the maintainers' planned position on Classic versus Sim for these worlds going forward?
3. **Robot spawns.** The world repositories ship empty worlds (no spawned robot). URML's manifest declares the robot. Is the implied separation correct, or do the maintainers prefer the lane to also pin a specific Turtlebot / Husky / other robot URDF for each world's canonical demo?
4. **Hospital and bookstore profiles.** URML defers these to future RFCs. Would `aws-robotics` find a hospital profile useful, or is the current hospital world a single-purpose demo without a community pulling for a URML-side profile?
5. **Downstream link.** Would `aws-robotics` be open to a one-line link from each targeted world repository's README to the URML conformance lane once it publishes? Similar to existing third-party tool references in those READMEs.
6. **AWS Robotics roadmap.** Are there worlds in development that URML should be aware of (factory floor, agricultural, warehouse-v2, anything else)? The lane can grow with the family if so.
7. **Anything else.**

## Implementation note

RFC-0044 ships as a single RFC document PR. No lane code in this PR. The `conformance/lanes/aws-worlds/` directory and its per-world subdirectories are the mechanical follow-up, contingent on `aws-robotics` maintainer feedback. Ledger entry under [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from aws-robotics maintainers)

1. Upstream-pinning approach (commit SHA vs release tag) (Q1).
2. Gazebo Sim versus Gazebo Classic targeting (Q2).
3. Robot-spawn pinning vs leaving robot choice to URML manifests (Q3).
4. Hospital and bookstore profile interest from the user side of the worlds (Q4).
5. Downstream link interest from the world READMEs (Q5).
6. Roadmap visibility for future worlds (Q6).
7. Anything URML's planned lane gets wrong about how the maintainers intend the worlds to be used.
8. Anything else.

## How to respond

The world repositories accept public Issues. Both `enhancement` and `question` labels exist across the family (verified via `gh api repos/aws-robotics/aws-robomaker-small-warehouse-world/labels` on 2026-05-23). The maintainers' overlap across the world family suggests filing on the most-starred repository (`aws-robomaker-small-warehouse-world`) and cross-referencing the others in the Issue body, rather than filing five parallel Issues.

URML's planned channel: a single Issue on `aws-robotics/aws-robomaker-small-warehouse-world` labelled `enhancement`, listing the other worlds the RFC touches and pointing to this RFC.

URML's own public Discussions for the broader conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, builds on RFC-0037, runs offline without AWS cloud).
- [x] Motivation grounded in verified data (472 / 276 / 257 stars on the top three worlds, MIT-0 license, Issues enabled, last commits in May 2026), not boilerplate.
- [x] Detailed design names every affected component (RFC-0022, RFC-0037, `mobile-runtime`, validator, the five world repositories) with verified file paths.
- [x] At least one alternative considered (four are).
- [x] Drawbacks are real (proposal-only weaker artifact, two world types lack URML profile homes, Gazebo version drift, retired-RoboMaker conflation risk).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no lane code in this PR; later session contingent on feedback.
- [x] Surface ("How to respond") is verified: Issues open, `enhancement` and `question` labels exist, single-Issue approach justified by maintainer overlap.
- [x] No em-dashes in the RFC body, no formulaic structure, voice consistent with RFC-0040 through RFC-0043.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No AWS cloud dependency (the worlds run offline in Gazebo). No telemetry. License posture respected (MIT-0 reference-by-SHA, no redistribution by default).
