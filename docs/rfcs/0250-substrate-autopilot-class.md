---
rfc: 0250
title: substrate.autopilot_class — declaring the drone-autopilot substrate in the Layer-1 manifest
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

# RFC-0250: `substrate.autopilot_class` — declaring the drone-autopilot substrate

## Summary

URML v0.1 declares `substrate.class` (`ros2`, `px4`, etc.) but doesn't declare which autopilot stack a drone deployment actually runs. A `move_to` against a quadrotor lands on PX4 in one deployment and ArduPilot in another, and URML's manifest can't say which. This RFC adds a `substrate.autopilot_class` enum to the Layer-1 manifest and defines its semantics, allowed values, validator behavior, and conformance test additions. The field is optional for non-drone deployments and required when `substrate.class` is one of the drone-substrate values. No primitive changes. Backward compatible (additive optional field).

The surfaces that demanded this RFC are RFC-0196 (PX4-Autopilot outreach), RFC-0008 (drone profile), and the broader Move-16 substrate-spine wave. URML's drone-runtime track cannot honestly claim substrate-neutrality until the manifest can declare which autopilot the runtime is targeting.

## Motivation

PX4 and ArduPilot are both targetable open-source drone autopilots and they are not interchangeable at the dispatch layer. They share the MAVLink protocol but diverge on flight-mode enumeration, geofence semantics, parameter sets, sensor calibration conventions, mission file format, and failsafe behavior. URML's manifest currently has no place to capture which autopilot the runtime targets. A deployment maintainer can write a Layer-2 program that validates against the same manifest in both cases and produces different runtime behavior. That is exactly the failure URML's validator-as-static-gate posture is supposed to prevent.

Three concrete consequences follow from the gap:

1. URML's drone profile (RFC-0008) declares `mobility.drive_type: multirotor | fixed_wing | vtol` but never says which autopilot interprets the mode. A validator cannot check that a Layer-2 program is consistent with the deployment's autopilot capability matrix.
2. Move-16 RFC-0196 (PX4-Autopilot outreach) explicitly requests this field. The PX4 maintainers cannot give substrate-fit feedback if URML has no place to declare PX4 vs the alternatives.
3. The eventual sibling fields (`autopilot_version`, `flight_mode_set`, `airframe_id`, `parameter_pin`) all depend on `autopilot_class` being declared first to be coherent.

## Detailed design

### Field shape

Add `substrate.autopilot_class` to the Layer-1 capability-manifest YAML schema. Field is **optional** when the deployment is not a drone. Field is **required** when `mobility.drive_type` is one of `multirotor`, `fixed_wing`, or `vtol`, or when `substrate.class` is `px4`.

```yaml
substrate:
  class: ros2                    # existing v0.1 field
  autopilot_class: px4           # NEW — this RFC
```

### Allowed values

The enum is closed under URML's substrate-neutral posture. Values that pass the validator are exactly those URML has engaged at the outreach level or that have shipped reference-runtime adapters. Adding a new value requires its own follow-up RFC and a real engagement trail.

| Value | Description | Reference / origin |
|---|---|---|
| `px4` | PX4-Autopilot stack | Linux Foundation Dronecode (RFC-0196) |
| `ardupilot` | ArduPilot stack | ArduPilot community (Move-2 RFC-0041, declined; URML still recognizes the substrate, the engagement was declined-not-rejected) |
| `pixhawk_classic` | Pre-PX4 Pixhawk firmware | Historical; deprecated but still deployed; supported for legacy manifests |
| `custom` | A non-public or vendor-specific autopilot | Escape hatch; the manifest must accompany `custom` with a free-text `autopilot_class_note` describing the substrate |

### Schema fragment (JSON Schema additions to Layer-1)

```jsonc
{
  "substrate": {
    "type": "object",
    "properties": {
      "class": { "$ref": "#/$defs/SubstrateClass" },
      "autopilot_class": {
        "type": "string",
        "enum": ["px4", "ardupilot", "pixhawk_classic", "custom"],
        "description": "Drone-autopilot substrate class. Required for drone deployments."
      },
      "autopilot_class_note": {
        "type": "string",
        "description": "Free-text description; required when autopilot_class == custom."
      }
    },
    "if": {
      "properties": {
        "autopilot_class": { "const": "custom" }
      }
    },
    "then": {
      "required": ["autopilot_class_note"]
    }
  }
}
```

### Validator behavior

`urml validate` adds three checks:

1. **Required-when-drone.** If `mobility.drive_type` is `multirotor`, `fixed_wing`, or `vtol`, the manifest must declare `substrate.autopilot_class`. Otherwise, validation fails with a clear error pointing to this RFC.
2. **Custom note.** If `autopilot_class: custom`, `autopilot_class_note` must be a non-empty string. Validator fails otherwise.
3. **Forward-compat for unknown values.** A value outside the enum produces a clear validator error pointing to this RFC's RFC-amendment process. The validator does not silently accept unknown values; substrate enumeration is intentional and growth is RFC-gated.

### Reference-runtime behavior

`reference/ros2-runtime/` and the future `reference/drone-runtime/` track read `substrate.autopilot_class` when present and use it to select the dispatch path. The ROS 2 runtime's drone dispatch composes onto MAVLink (sibling RFC-0197) regardless of autopilot value; the difference shows up in flight-mode mapping, parameter pinning, and failsafe semantics that downstream RFCs in this series cover.

### Conformance test additions

`conformance/tests/test_manifest_autopilot_class.py` adds three test cases:

1. A drone manifest without `autopilot_class` fails validation.
2. A drone manifest with `autopilot_class: px4` and no `autopilot_class_note` passes.
3. A drone manifest with `autopilot_class: custom` and no `autopilot_class_note` fails; with a note, passes.

## Backward compatibility

Pre-v1.0. Additive: existing non-drone manifests continue to validate without change. Existing drone manifests (if any exist in the wild without declaring autopilot class) fail validation after this RFC lands; this is intentional. URML's drone-profile reference manifest (`spec/profiles/drone/example.yaml`) is updated in the same PR to declare `autopilot_class: px4` for consistency.

The drone-profile fixture in `examples/profiles/drone/` is updated to declare the field. No downstream URML programs need code changes; the change is at the manifest layer.

## Drawbacks

- **Enum closure is opinionated.** URML refuses to validate unknown autopilot classes. This is the URML stance generally (per CLAUDE.md, the validator is not a fast path; it is a static gate); the cost is that a deployment using a brand-new autopilot has to file an RFC before its manifest validates. The cost is intentional: substrate enumeration is the moat.
- **Required-when-drone is a breaking change for non-conformant existing manifests.** No such manifest is known on main, but anyone running URML against a private drone manifest must update.
- **`custom` is a known weakness.** It escapes the enum and weakens the substrate-fingerprint guarantee. The free-text note plus an explicit deprecation review at v1.0 are the discipline that holds it in line.

## Alternatives considered

1. **Free-text `autopilot_class` string with no enum.** Rejected. Defeats the validator's static-gate posture. Any string would validate; the gate would be moot.
2. **Use a more general `runtime_profile` field instead of an autopilot-specific class.** Rejected. The autopilot is one of several substrate-class-determining choices (RMW for ROS 2, IPC for shared-memory, etc.); each gets its own field per the principle that a manifest declares what is actually configurable, not a coarse runtime profile that hides the structure.
3. **Bundle `autopilot_class` with `flight_mode_set` and `airframe_id` in one RFC.** Rejected. `autopilot_class` is the foundational field; the others depend on it. A composite RFC would block all three on the most contentious one. URML's discipline is to land the simpler fields first.

## Prior art

- [RFC-0008 (drone profile)](0008-drone-profile.md) — the URML drone profile that consumes this field.
- [RFC-0196 (PX4 outreach)](0196-px4-autopilot-outreach.md) — the outreach RFC that surfaced the field.
- [RFC-0197 (MAVLink outreach)](0197-mavlink-outreach.md), [RFC-0198 (MAVSDK outreach)](0198-mavsdk-outreach.md) — sibling drone-protocol and SDK engagements.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — the conformance framework this RFC extends with a new test case.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — relevant because some autopilot enum values (custom, vendor-specific) interact with the default-policy file's procurement-gating posture.

## Unresolved questions

1. **Versioning.** `substrate.autopilot_class` declares the class. The version (PX4 v1.14 vs v1.15) is a separate concern; a follow-up RFC `substrate.autopilot_version` is queued. The question for this RFC is whether the version field should be required or optional when it lands; the lean is optional with a recommendation.
2. **`pixhawk_classic` retention.** This value covers pre-PX4 Pixhawk firmware that is increasingly rare. Whether URML keeps it past v1.0 is a v1.0-stability decision; for now, retain.
3. **`custom` validation depth.** Should the validator do anything with `autopilot_class_note` beyond non-emptiness? The current design says no; the note is documentation, not a parsed field. A future RFC could add structured custom-substrate declarations.

## Implementation plan

1. Land the JSON Schema fragment in `spec/layer-1-hal/schema.json` (or wherever the current schema source lives; verify at land time).
2. Land the validator check in `reference/validator/`.
3. Land the conformance test in `conformance/tests/`.
4. Update the drone-profile example manifest in `examples/profiles/drone/`.
5. Update the drone-profile spec doc (RFC-0008's downstream impl) to reference this RFC.

All five land in a single PR to preserve atomicity. The downstream Spec RFCs in this series (`substrate.autopilot_version`, `substrate.flight_mode_set`, `substrate.airframe_id`) are separate PRs.

## How to respond

This is a Spec RFC. Comments belong in the RFC's PR thread on `URML-MARS/URML`. Implementation tracks in the same PR.

## Self-review (Phase 0)

- [x] At least one alternative considered (three).
- [x] Drawbacks named honestly (enum-closure opinion, breaking-change for non-conformant drone manifests, `custom` escape hatch).
- [x] Backward compatibility documented (additive at field level; breaking for non-conformant drone manifests that were never validating cleanly anyway).
- [x] No new Layer-2 primitive.
- [x] Conformance test added.
- [x] Validator behavior fully specified.
- [x] Cross-references to outreach RFCs that surfaced the gap.
- [x] CLAUDE.md compliance check passed: enum-closure preserves the moat; `custom` escape hatch is bounded.
