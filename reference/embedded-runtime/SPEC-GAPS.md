# SPEC-GAPS — urml-embedded-runtime

Per the spec-gap protocol (RFC-0014): built strictly against the
frozen substrate Protocol. Needs surfaced are recorded here; the
genuinely inexpressible become RFC Drafts for maintainer decision —
never a silent primitive/schema change.

## Genuinely inexpressible → RFC Draft filed

- **RFC-0018 — minimal-MCU capability subset.** A *mobile* educational
  buggy (the conformance fixture here) fits the v0.1 schema honestly:
  it is genuinely `mobility.drive_type: differential`. But a large
  class of educational MCU nodes — a fixed micro:bit with only an LED,
  a buzzer, and a light sensor; a breadboard with a servo — has **no
  honest `mobility`**, no camera/`perception` block, and no
  manipulator. The manifest's blocks are individually optional, yet
  there is no way to declare "this is a minimal actuator/sensor node"
  such that the conformance suite can check it as a coherent class.
  Pretending such a board has `differential` mobility to satisfy a
  fixture would be a lie. Filed as RFC-0018 (Draft) — a *manifest*
  minimal-subset declaration. It explicitly cross-references **RFC-0017**
  (digital-I/O actuation): "blink the LED" is an actuation-verb gap
  owned by RFC-0017, not duplicated here; RFC-0018 is only the
  capability-declaration half.

## Composable (no gap, documented)

- A 2-wheel micro:bit/Arduino buggy is honestly `differential`;
  `move_to` over a named, firmware-mapped command (config-side
  `location_to_command`, the px4 `location_to_pose` pattern). No URML
  surface change — this is the shipped, green path.
- `grasp`/`release` → a configured gripper-servo command. Honest for a
  buggy with a claw; absent ⇒ a clear unsuccessful result, not a gap.

## Scope note

This serves the RFC-0011 educational profile. `program.profile` is an
open `Identifier`, so `educational` validates with **no** schema
change, and RFC-0011's profile is documented-not-enforced in v0.1 —
the fixture is honest as a core-primitive program under that profile.
