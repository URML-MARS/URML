---
rfc: 0630
title: Relative-motion primitives for frameless robots (drive, turn)
author: Ido Yahalomi (greenvh@gmail.com)
state: Accepted
created: 2026-06-22
updated: 2026-06-22
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

# RFC-0630: Relative-motion primitives for frameless robots (`drive`, `turn`)

**Kind: Spec.** Adds two new Layer-2 primitives. Adding a primitive is a one-way
door; the design below was settled with the maintainer (see Resolved decisions).

## Summary

URML expresses all ground motion as `move_to` a named place in a declared frame.
That fits robots that localize against a frame (a map, a cell, a set of declared
locations). It does not fit a large, important class of beginner and classroom
robots that are **frameless**: differential-drive buggies with wheel encoders and
no global localization, whose natural motion vocabulary is relative, "drive
forward 30 cm", "spin 90 degrees". Today URML has no verb for that. The only
workaround is to pre-declare every destination as a named waypoint, which cannot
express a parametric utterance like "drive forward a foot" and is awkward to
author.

This RFC adds two new Layer-2 primitives, `drive` and `turn`, for relative
(odometric) motion, gated behind a new `mobility.supports_relative_motion`
capability so the validator still refuses motion a robot cannot perform, and
gated to the `educational` profile to start.

**State: Accepted.** The design was settled with the maintainer; see Resolved
decisions. Implementation follows (schema, validator, runtime, conformance,
worked example).

## Motivation

The motivating case is concrete and current. In
[Discussion #497](https://github.com/URML-MARS/URML/discussions/497), a user is
running URML on a Raspberry Pi GoPiGo3, a two-motor, wheel-encoder, speaker
robot, and translating natural language to URML with a 986 MB local LLM on the Pi
itself. The robot is frameless by construction: dead reckoning from encoders, no
map, no global frame. Its natural commands are "drive forward X" and "spin X
degrees", optionally preceded by an announcement over the speaker. He asked how
to write a manifest for it.

The honest answer today is that the classroom pattern works (a local floor frame
with named corner waypoints, `move_to` between them), and his local LLM already
produced a valid four-corner program that way. But "drive forward 12 inches" and
"spin 90 degrees clockwise" have no direct verb. You can only approximate them by
pre-declaring a waypoint a foot ahead or a heading 90 degrees over, which defeats
the point of a natural-language front door: the whole value is turning an
arbitrary spoken instruction into validated motion.

This is not a niche. It is the canonical motion model of beginner robotics: LEGO
SPIKE and EV3 (drive distance, turn degrees), Logo turtle graphics (forward,
right), Blockly and Bloxter move blocks, the GoPiGo3 and Create APIs. URML's
educational reach depends on speaking this vocabulary, and the GoPiGo engagement
(RFC-0572, the maintainer's interest in the kids/natural-language angle) makes it
timely.

## Why not an existing mechanism

**Extend `move_to`.** Rejected. `move_to` means "go to a named place in a
frame"; its argument resolves against `declared_locations`. Relative motion is
"change my pose by a delta, with no destination". Overloading one verb with two
different semantics muddies both the language and the safety story (the validator
reasons differently about a destination than about a delta). URML prefers a small
vocabulary, but it also prefers each primitive to mean one thing.

**Compose from existing primitives.** Not possible. There is no relative-motion
building block to compose from. `move_to` is the only motion verb and it is
destination-based.

**Local-frame waypoints (the status-quo workaround).** Works for fixed routines
(the four-corner classroom exercise) but cannot express a parametric utterance,
and forces the author to enumerate destinations in advance. It is a real pattern
worth documenting, but it is not a substitute for a relative verb.

So a new primitive is genuinely warranted. The remaining design question is its
shape, which is what this RFC asks the maintainer to settle.

## Proposal

### The primitives

Add two Layer-2 primitives, `turn` and `drive`.

```yaml
- turn:
    angle: 90             # signed degrees (+ counterclockwise / left). required.
- drive:
    distance: 0.30        # signed metres along the current heading (+ forward, - back). required.
    arc: 30               # optional signed degrees swept over the drive (turns it into a circular arc)
    speed: { value: 0.2, units: m_per_s }   # optional; reuses the existing Speed type
```

`turn` rotates in place by a signed `angle` in degrees (`+` counterclockwise).

`drive` translates by a signed `distance` in metres along the current heading.
With the optional `arc` field (signed degrees swept over the distance) it follows
a circular arc instead of a straight line; this is the simultaneous
translation-plus-rotation case. Omit `arc` for a straight line.

Rules:

- Two single-purpose verbs, not one combined verb. A step holds exactly one of
  `turn` / `drive`.
- `distance` is in metres; Layer 4 normalizes human units ("12 inches", "a foot",
  "30 cm") to metres before emission.
- `angle` and `arc` are in degrees, signed, `+` counterclockwise.
- **Combined motion is an ordered sequence.** "Turn left 90, then drive forward a
  foot" compiles to `[turn, drive]`, and the canonical execution order is
  turn-then-drive (face, then go). True simultaneous arc motion is expressed by
  `drive.arc`, not by combining two steps.
- Both verbs require `mobility`, like the other motion primitives, plus the
  relative-motion capability and the `educational` profile (below).

### The capability gate (manifest)

A robot must declare that it can perform odometric relative motion, so the
validator still refuses `move_by` on a robot that cannot. Add to `Mobility`:

```python
supports_relative_motion: bool = False
# The robot can execute odometric drive/turn-by-amount commands (wheel
# encoders or equivalent dead reckoning). Required by `move_by`.

max_relative_distance: float | None = None  # m, per single move_by; optional bound
```

Angular and acceleration bounds already exist from RFC-0518
(`max_angular_velocity`, `max_linear_acceleration`, `max_angular_acceleration`)
and apply here unchanged.

The validator (Pass 2, capability) rejects `drive` / `turn` when
`supports_relative_motion` is false or `mobility` is absent, rejects a `distance`
whose magnitude exceeds `max_relative_distance` when that bound is declared, and
rejects either verb when `educational` is not among the program's profiles (the
profile gate from decision 5).

### Honesty: dead reckoning drifts

Relative motion on encoders accumulates error. This RFC is explicit that
`move_by` is for approximate, short-range, classroom-and-hobby motion, not
precision navigation. A frameless robot also has no global frame to geofence
against, so the safety story for these robots is per-move bounds
(`max_relative_distance`, the RFC-0518 velocity/acceleration limits) plus
onboard obstacle/occupancy checks, not a global geofence polygon. The manifest
should not claim accuracy it does not have; the RFC recommends documenting the
encoder/dead-reckoning basis in the manifest description.

### Substrate mapping

`move_by` maps cleanly onto every odometric drive API:

- GoPiGo3: drive-distance and turn-degrees calls over the encoder API.
- ROS 2 differential/tracked bases: a drive-distance action, or integrating
  `Twist` over odometry, or a nav2 relative goal.
- LEGO SPIKE / EV3, Create, generic differential drive: the native move-distance
  and turn-angle blocks.

The runtime owns the closed-loop control; URML declares and validates the intent.

## Prior art

- LEGO SPIKE / MINDSTORMS EV3: "move forward N cm", "turn N degrees".
- Logo turtle graphics: `forward`, `back`, `right`, `left`.
- Blockly / Bloxter / Scratch robotics blocks: drive and turn by amount.
- GoPiGo3, iRobot Create, TurtleBot drive_distance: odometric move primitives.
- ROS 2 `nav2` relative goals and `cmd_vel` integration.

This is the single most common motion model in beginner robotics, which is
exactly URML's educational audience.

## Implementation plan

1. `TurnArgs` (`angle`) and `DriveArgs` (`distance`, optional `arc`, optional
   `speed`) schemas, added to the `Step` union and `_PRIMITIVE_FIELDS`.
2. `Mobility.supports_relative_motion` and `max_relative_distance` fields.
3. Validator Pass-2 checks (capability present; `educational` profile present;
   `|distance|` within bound), with clear error codes
   (`capability.relative_motion_unsupported`, `capability.relative_distance_exceeded`,
   `profile.relative_motion_requires_educational`).
4. Reference runtime mapping (a `send_relative_motion` adapter Protocol method,
   implemented in MockROSAdapter and at least one runtime; a clear
   not-supported sentinel elsewhere), plus a frameless example manifest.
5. Conformance fixtures: positive (a relative-motion-capable educational buggy
   drives, turns, and arcs) and negative (a robot without the capability, and a
   non-educational profile, both rejected).
6. A runnable worked example (a frameless classroom buggy: announce, then turn
   and drive).
7. Layer-4 grammar note: unit normalization (inches/cm/feet to metres; degree
   sign convention) and a few-shot for the bridge.

## Resolved decisions

Settled with the maintainer 2026-06-22:

1. **Two verbs**, `drive` and `turn`, each single-purpose (not one combined
   `move_by`).
2. **Degrees** for `angle` and `arc` (human-natural; the natural-language layer
   does not have to teach a small model radians). The runtime converts to its
   native unit.
3. **Combined motion is an ordered sequence.** Turn-then-drive is the canonical
   order when the two are sequenced; a step holds one verb.
4. **Arc motion is in scope**, expressed by the optional `drive.arc` field
   (simultaneous translation plus rotation along a circular arc).
5. **Gated to the `educational` profile first.** `drive` / `turn` are valid only
   when `educational` is among the program's profiles; widening to general ground
   robots is a later RFC once the verbs are proven.
6. **Frameless envelope confirmed.** Per-move bounds (`max_relative_distance`, the
   RFC-0518 velocity/acceleration limits) plus onboard obstacle/occupancy checks
   are the safety model; there is no global geofence for a frameless robot.

## Strategic note

This is the cleanest kind of feature request: an active user, on a real robot,
hitting a real limitation, in URML's core educational audience. It also lines up
with the GoPiGo maintainer engagement (RFC-0572). The risk to manage is primitive
sprawl; the mitigation is to settle the open questions above before any code, and
to keep the verb minimal.
