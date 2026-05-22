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

# SPEC-GAPS — urml-edu-runtime

Per the spec-gap protocol (RFC-0014): built strictly against the
frozen substrate Protocol. Anything an educational platform needs that
URML cannot express is recorded here and cross-referenced — never a
silent primitive/schema change.

## Cross-references to existing Draft RFCs (no NEW RFC)

The three educational platforms surface only gaps that prior runtimes
already filed:

- **RFC-0017 — digital-I/O actuation** (already Draft from
  cobot-runtime). The VEX V5 brain LED, the LEGO hub status light + the
  LEGO speaker beep, the Thymio LED ring + buzzer + buttons are all
  the same "write a named declared digital line" gap. Cross-referenced
  here; not duplicated.

- **RFC-0018 — minimal-MCU capability subset** (already Draft from
  embedded-runtime). A VEX V5 brain on its own (no motors), a LEGO
  hub used only for sensor reads, a fixed Thymio used as a
  push-button stand are all the same "non-mobile sensor/actuator
  node, no honest mobility/perception block" gap. Cross-referenced;
  not duplicated.

## Composable (no gap, documented)

- A two-motor VEX clawbot / a LEGO driving base / a moving Thymio is
  honestly `differential` drive (RFC-0009's enum value). `move_to`
  resolves via config-side `EduConfig.location_to_command` (the
  `cobot_adapter.yaml` precedent) — no URML surface change.
- `grasp`/`release` for the VEX claw / LEGO claw / Thymio gripper map
  through `EduConfig.manipulation_commands` to a single firmware
  command. Honest for a buggy-with-claw; absent ⇒ an unsuccessful
  result with a clear reason, not a gap.

## Scope note

Serves the RFC-0011 educational profile. `program.profile` is an
open `Identifier`, so `educational` validates with **no** schema
change, and RFC-0011 is documented-not-enforced in v0.1.
