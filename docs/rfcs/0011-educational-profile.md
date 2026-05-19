---
rfc: 0011
title: Educational profile
author: URML Maintainers (maintainers@urml.dev)
state: Draft
created: 2026-05-18
updated: 2026-05-18
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

# RFC-0011: Educational profile

## Summary

Add an `educational` profile for classroom and teaching robots (TurtleBot, Franka in a teaching cell, LeRobot arms, micro:bit/VEX-class platforms). v0.1 of the profile **adds no new primitives**: it constrains the core vocabulary for safety around students and beginners, defines a conservative default safety envelope, and sets manifest expectations. It is one of the five names in URML's canonical maintenance scope (civilian, consumer, **educational**, industrial, research) and is the single highest-leverage adoption flywheel: the people who learn robotics on URML become the people who deploy it.

## Motivation

The manifesto optimizes for inevitability through adoption, and CLAUDE.md calls the educational community a core adoption flywheel. Today URML has home/drone/industrial profiles but nothing that says "this program runs in a classroom, with a beginner author, near students." A teacher cannot express the one constraint that matters most to them (move slowly, never near a person at speed, stop on any uncertainty) without hand-writing an envelope. Educational platforms are also exactly the cheap, reproducible robots a contributor can actually own, which makes this profile the most collaboration-generative one to ship.

`spec/profiles/README.md` already lists Education as a stretch target with a "becomes a subdirectory when drafting begins" note. This RFC begins it.

## Detailed design

A profile spec at `spec/profiles/educational/README.md`, structured like the industrial profile. v0.1 scope:

- **No new primitives.** Educational programs use the twelve core primitives (RFC-0002). Profiles-over-forks: a classroom does not need a new verb, it needs tighter defaults.
- **Constrains core primitives**: `grasp.force` defaults to and is capped at `gentle`; `move_to` near a declared person-occupied zone is speed-limited; unrecognized `detect` results fail closed (a teaching robot stops and reports rather than guessing).
- **Default safety envelope**: the most conservative of all profiles — low `max_velocity`, mandatory station-keeping disabled-unless-declared, every `on_error` defaulting to `abort_and_report` so a student program halts loudly rather than improvising.
- **Manifest expectations**: `mobility` with a ground `drive_type` (`differential`/`omnidirectional`/`tracked`); flight drive types rejected for v0.1 (classroom drones are a deliberate future tightening, not a v0.1 default). `declared_locations` are the norm; pose-based motion discouraged.

### Spec changes

- New `spec/profiles/educational/README.md`. Update `spec/profiles/README.md` (move Education out of "stretch", into the profile table). No Layer-1/2/3 schema change: profile names are an open `Identifier` in `URMLProgram`, and v0.1 adds no primitive or manifest-field, so the validator needs no code change. The profile's tighter defaults are documented constraints a conformant runtime applies; new *enforced* checks are a deliberate follow-up RFC, not v0.1.

### Validator changes

None in v0.1 (intentional). The profile is declared and documented; mechanically-enforced educational-specific checks (the speed-near-people rule, the fail-closed-detect rule) are a tracked follow-up so this RFC stays small and reviewable, exactly as the industrial profile shipped its envelope before all its enforcement.

### Conformance suite changes

A later PR adds `conformance/fixtures/educational/` once the enforced constraints land. v0.1 educational programs are already covered by the core fixtures (they are core-primitive programs); no fixture is faked for enforcement that does not exist yet.

## Backward compatibility

Fully compatible. Additive: a new profile name and a new spec document. No existing program, manifest, runtime, or fixture changes. Pre-v1.0.

## Drawbacks

A profile that documents constraints the validator does not yet enforce risks a reader assuming enforcement. Mitigation: the profile spec states explicitly, at the top, which constraints are *documented defaults a runtime must apply* versus *validator-enforced in v0.1* (the latter set is empty by design in v0.1). This is the same staged path the industrial profile took and is honest as long as the line is stated, not blurred.

## Alternatives considered

- **Fold education into `home`.** Rejected: the home profile assumes a competent adult author and a serviced robot; the educational profile's whole point is a beginner author and a safety posture tuned for students, which are different defaults, not a subset.
- **Add educational primitives (`teach`, `demonstrate`).** Rejected for v0.1: speculative, and adding a primitive is a one-way door (RFC-0002). If a real teaching interaction proves inexpressible by composition, that is its own future RFC.
- **Ship enforcement in v0.1.** Rejected: it would make this RFC a large multi-pass validator change. Staging (spec now, enforcement next) is the pattern the industrial profile already set.

## Prior art

The home/drone/industrial profile specs (structure and the constrain-don't-extend pattern). Educational robotics platforms: TurtleBot/ROS classrooms, Franka teaching cells, LeRobot, micro:bit, VEX. RFC-0002 (primitive economy) motivates adding zero primitives here.

## Unresolved questions

- The exact enforced rule set for the follow-up (speed-near-people thresholds, fail-closed-detect semantics). Each needs one concrete classroom program before it is specified.
- Whether classroom drones are an educational sub-case or stay in the drone profile. Deferred; v0.1 educational is ground-only.

## Implementation note

One PR with RFC-0012 (research profile; same shape): the two RFCs plus the two `spec/profiles/*/README.md` documents plus the `spec/profiles/README.md` table update. No code. Enforcement and `conformance/fixtures/educational/` are tracked follow-ups, filed when the enforced rules are specified.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is proposed and that v0.1 adds no primitives.
- [x] The Motivation is grounded in the manifesto's stated adoption flywheel and the existing stretch-list note, not a hypothetical.
- [x] Alternatives are genuinely considered and rejected with reasons.
- [x] Backward compatibility is explicit (additive, pre-v1.0, no code change).
- [x] The documented-vs-enforced line is stated as a drawback, not blurred.
