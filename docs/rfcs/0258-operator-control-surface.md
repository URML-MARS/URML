---
rfc: 0258
title: operator_control_surface — declaring the operator-control UI in the Layer-1 manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0258: `operator_control_surface` — declaring the operator-control UI

## Summary

URML's runtime stack ends at the autopilot dispatch layer (PX4 / MAVLink / MAVSDK). The operator-control surface (ground-station UI, mission upload, telemetry display, manual override) is where operators actually interact with the deployment. URML's manifest has no place today to declare which operator-control surface the deployment composes with. This RFC adds `operator_control_surface` as a top-level optional field with a closed enum, a `operator_control` sub-block for MAVLink subset / mission-file format / manual-override declarations, and defines validator behavior. Optional. Backward compatible.

The surface that demanded this RFC is Move-16 RFC-0208 (QGroundControl outreach).

## Motivation

Production drone deployments routinely include operator-control surface declaration as deployment metadata, separate from the autopilot stack itself. URML's manifest captures the autopilot (RFC-0250) and the protocol (RFC-0256) but leaves the operator-UI layer undeclared. Three concrete consequences:

1. **Deployment-tier introspection gap.** A deployment running QGroundControl as ground-station differs from one running Mission Planner or Auterion Suite. URML's manifest cannot today express the difference.
2. **MAVLink message-subset declaration.** Operator-control surfaces consume specific MAVLink message subsets (different from the autopilot's full set). Declaring the subset at the manifest layer surfaces deployment-tier expectations.
3. **Manual-override declaration is safety-relevant.** Some operator-control surfaces enable manual-override channels (RC passthrough, joystick override); others don't. URML's manifest should declare whether manual override is enabled as part of the deployment posture.

The Move-16 RFC-0208 explicitly requests this field.

## Detailed design

### Field shape

`operator_control_surface` is **top-level** (not nested under `substrate`) because the operator-UI is structurally separate from the substrate layer.

```yaml
operator_control_surface: qgroundcontrol     # NEW — this RFC, top-level optional
operator_control:                            # NEW — sub-block
  mavlink_message_subset: standard           # standard | extended | custom
  plan_format: qgc_plan_v1                   # qgc_plan_v1 | mp_plan_v1 | auterion_plan_v1 | custom
  telemetry_subset: standard                 # standard | extended | custom
  manual_override:
    enabled: true
    channel: rc_passthrough                  # rc_passthrough | joystick | none
```

### Allowed values for `operator_control_surface`

| Value | Description | Reference |
|---|---|---|
| `qgroundcontrol` | QGroundControl (Dronecode) | RFC-0208 |
| `mission_planner` | Mission Planner (ArduPilot ecosystem) | Cross-reference; URML not yet engaged at this surface |
| `auterion_suite` | Auterion Suite (commercial PX4 downstream) | Cross-reference |
| `custom` | Vendor-specific or experimental operator-UI | escape hatch + `operator_control_surface_note` required |
| `none` | Deployment runs without operator-UI declaration | n/a |

### Schema fragment (Layer-1)

```jsonc
{
  "operator_control_surface": {
    "type": "string",
    "enum": ["qgroundcontrol", "mission_planner", "auterion_suite", "custom", "none"]
  },
  "operator_control_surface_note": { "type": "string" },
  "operator_control": {
    "type": "object",
    "properties": {
      "mavlink_message_subset": { "enum": ["standard", "extended", "custom"] },
      "plan_format": { "enum": ["qgc_plan_v1", "mp_plan_v1", "auterion_plan_v1", "custom"] },
      "telemetry_subset": { "enum": ["standard", "extended", "custom"] },
      "manual_override": {
        "type": "object",
        "properties": {
          "enabled": { "type": "boolean" },
          "channel": { "enum": ["rc_passthrough", "joystick", "none"] }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional field.** Missing field is acceptable; deployment runs without operator-UI declaration.
2. **Custom requires note.** `operator_control_surface: custom` requires non-empty `operator_control_surface_note`.
3. **Autopilot-compatibility soft check.** The validator emits a warning when the declared operator-control surface and autopilot class are an unusual pairing. `qgroundcontrol + px4` is common. `qgroundcontrol + ardupilot` is supported. `mission_planner + px4` is unusual. The warning is informational; the manifest validates.
4. **`manual_override.enabled: true` requires `channel`.** If manual override is enabled, the channel must be declared (not `none`).
5. **Forward-compat.** Closed enums on the surface and on sub-fields.

### Reference-runtime behavior

Reference runtimes read `operator_control_surface` for deployment-log diagnostics. The runtime does not orchestrate the operator-UI itself; the UI is external to URML's dispatch path. URML's manifest declaring the surface lets downstream deployment tooling (deployment configurators, audit-log consumers) consume the field.

### Conformance test additions

`conformance/tests/test_manifest_operator_control_surface.py`:

1. Manifest without `operator_control_surface` passes (optional).
2. Manifest with `operator_control_surface: qgroundcontrol` passes.
3. Manifest with `operator_control_surface: qgroundcontrol + substrate.autopilot_class: px4` passes silently.
4. Manifest with `operator_control_surface: mission_planner + substrate.autopilot_class: px4` passes with warning.
5. Manifest with `manual_override.enabled: true` and `channel: none` fails (consistency violation).

## Backward compatibility

Pre-v1.0. Additive. No migration required.

## Drawbacks

- **Declaration without enforcement.** URML's runtime doesn't actually compose with the operator-UI; declaring the surface is documentation. The discipline is deployment-tier introspection, not validator gating.
- **Closed enum is small.** Three named values plus `custom` and `none`. Mission Planner and Auterion Suite are listed but URML has not engaged either via outreach. The values exist because they are operationally common; URML may engage them in future moves.
- **MAVLink-subset and plan-format enums are coarse.** `standard`, `extended`, `custom` is the practical enumeration. A finer-grained shape (per-message-class subset declaration) is over-engineering for v0.1.

## Alternatives considered

1. **Skip the field; let deployment configurators handle UI declaration.** Rejected. URML's manifest is the canonical deployment declaration; operator-UI belongs there.
2. **Nest under `substrate` rather than top-level.** Rejected. Operator-UI is structurally separate from substrate layer; the asymmetry of placing it top-level matches its actual relationship (substrate + operator-UI compose at the deployment, not at the substrate).
3. **Free-string `operator_control_surface` field.** Rejected. Defeats the validator-as-static-gate posture. Closed enum with `custom` escape hatch is the URML convention.
4. **Cross-reference `operator_control_surface` with `autopilot_class` as a hard error.** Rejected. The pairings are operationally diverse (some deployments use unusual combinations intentionally); soft warning is the right strength.

## Prior art

- [RFC-0208 (QGroundControl outreach)](0208-qgroundcontrol-outreach.md) — the outreach RFC that surfaced this field.
- [RFC-0250 (substrate.autopilot_class)](0250-substrate-autopilot-class.md) — sibling Spec RFC; declares the autopilot stack the operator-UI composes against.
- [RFC-0256 (protocol.embedded_class)](0256-protocol-embedded-class.md) — sibling Spec RFC; declares the MAVLink layer the operator-UI consumes.
- [RFC-0008 (drone profile)](0008-drone-profile.md) — URML's drone profile, which consumes this field.

## Unresolved questions

1. **Per-deployment multi-operator-UI.** Some deployments use multiple operator-UIs (one ground-station + one mobile companion app). v0.1 of this field is single-surface; multi-surface is future work.
2. **Plan-format version detail.** `qgc_plan_v1` covers the JSON-format mission file used by QGC. Variant versions exist; URML's enum is coarse-grained for v0.1.
3. **Telemetry-subset semantics.** What "standard" vs "extended" means is left to the operator-UI's own documentation; URML's manifest declares the choice but does not enumerate the message lists.

## Implementation plan

1. JSON Schema fragment.
2. Validator with autopilot-compatibility soft warning.
3. Conformance tests.
4. Update drone-profile example manifests.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly.
- [x] Backward compatibility additive (optional).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to outreach RFCs (0208) and sibling Spec RFCs (0250, 0256, 0008).
- [x] CLAUDE.md compliance: enum closure preserves moat; top-level placement matches the operator-UI's structural relationship to the substrate.
