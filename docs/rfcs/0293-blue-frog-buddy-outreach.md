---
rfc: 0293
title: Blue Frog Robotics / Buddy integration, request for comment from BlueFrogRobotics SDK maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-31
updated: 2026-05-31
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

# RFC-0293: Blue Frog Robotics / Buddy integration, request for comment from BlueFrogRobotics SDK maintainers

No spec change is proposed here. This is an Outreach RFC: it proposes a mapping from URML v0.1 to an existing target's SDK, not a change to URML's normative surface.

## Summary

URML does not yet ship a Blue Frog Robotics integration. This RFC proposes a `BuddyAdapter` under a new [`reference/home-runtime/`](../../reference/home-runtime/) package (proposed by [RFC-0100](0100-irobot-roomba-outreach.md)) targeting the Buddy SDK exposed through the [`BlueFrogRobotics/BlueFrog_SDK_examples`](https://github.com/BlueFrogRobotics/BlueFrog_SDK_examples) repository. The adapter routes URML Layer-2 primitives plus the home-profile `speak` / `listen` extensions onto Buddy's emotional-companion surface (mobility on a wheeled base, vocal and visual interaction, face / human detection) without proposing upstream changes. First of the policy-clean Move #20 home-assistance round-two targets.

Buddy is marketed as an open-platform companion robot, with a published SDK (a Java / Android API surface) and a public examples repository. The examples repository is the canonical engagement channel for a substrate-neutral integration.

## Motivation

Blue Frog Robotics (Paris, France; EU-domiciled, default-policy pass) builds Buddy, an emotional companion robot positioned across home companionship, elder support, inclusion, and education. URML's natural-language layer maps cleanly to Buddy's interaction surface: a user writes "greet me, then check whether anyone is in the living room and tell me" in URML; URML compiles to `speak(...)` + `move_to(living_room)` + `measure(human_present)` + `report(...)`; a `BuddyAdapter` dispatches the primitives onto Buddy via the SDK.

Verified surface (2026-05-31):
- [`BlueFrogRobotics/BlueFrog_SDK_examples`](https://github.com/BlueFrogRobotics/BlueFrog_SDK_examples): public examples repository for the BFR SDK, Issues enabled, not archived, last pushed 2024-09-23. The active developer-facing surface in the `BlueFrogRobotics` org.
- Buddy SDK ([`bluefrogrobotics.com/our-sdk`](https://www.bluefrogrobotics.com/our-sdk), [`sdk.buddytherobot.com`](https://sdk.buddytherobot.com/)): a Java library imported into an Android Studio project, exposing robot movement, vocal and visual interaction, emotional behaviours, and human / face detection.
- HQ: Paris, France.

URML's specific value for Buddy:
- **Natural-language authoring above the Buddy SDK.** A caregiver or family member writes intent in plain language; URML compiles to validated primitives plus Buddy dispatch. The pedagogical ladder above raw Java SDK calls is exactly URML's Layer-4 story.
- **Cross-platform retargetability.** A URML companion routine written for Buddy retargets to another speak / listen / move platform by manifest swap; the substrate-neutral story is the value proposition for a multi-vendor care setting.
- **Exercises the home-profile speech extensions.** Buddy is the first Move #20 target that natively exercises the home-profile `speak` / `listen` extensions ([`spec/profiles/home/`](../../spec/profiles/home/)), not just mobility primitives.

## Detailed design

URML's existing artifacts that feed into a Buddy adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/home/`](../../spec/profiles/home/): the home profile, including the `speak` / `listen` extensions.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles applicable to companion-robot use.
- A new `reference/home-runtime/` package (proposed by RFC-0100), parent runtime for `RoombaAdapter`, `BuddyAdapter`, etc.

### Proposed `BuddyAdapter` shape

```
reference/home-runtime/src/home_runtime/buddy/
├── __init__.py
├── adapter.py             # BuddyAdapter
├── buddy_protocol.py      # wraps the Buddy SDK interaction surface
└── manifests/
    └── blue_frog_buddy.yaml
```

The adapter implements URML's substrate Protocol. Because the Buddy SDK is a Java / Android surface, the adapter targets it through a thin RPC / bridge boundary; the hermetic test path injects a fake SDK (same pattern as the Robotical Marty adapter, [RFC-0073](0073-robotical-marty-outreach.md)).

### Proposed URML v0.1 to Buddy mapping

| URML primitive | Buddy realisation |
|---|---|
| `move_to(pose)` | Dispatched as a region / named-location move on Buddy's wheeled base. Free-coordinate navigation depends on Buddy's mapping; the manifest declares region-based mobility. |
| `grasp(...)` / `release(...)` | Not applicable (Buddy has no manipulator). Manifest declares `gripper: none`. |
| `measure(sensor_id)` | Battery state, human / face presence, ambient sensors read via the SDK. |
| `wait_for(...)` | Polling loop on a named event (e.g. `face_detected`, `docked`). |
| `report(status)` | Append to a per-session log; optional spoken summary via `speak`. |
| `speak(utterance)` (home ext.) | Buddy's vocal-interaction surface. |
| `listen(prompt, mode, timeout)` (home ext.) | Buddy's voice-capture surface. |

### Proposed capability manifest

```yaml
brand: blue_frog_buddy
profile: home
mobility: wheeled_differential
mobility_type: region_based
workspace_m: indoor_floor
transport: sdk_bridge
python_package: home_runtime.buddy
sensors:
  - battery
  - human_presence
  - face_detection
gripper: none
speech:
  speak: true
  listen: true
provenance:
  origin: FR
  ndaa_section_889_status: not_listed
  default_policy: pass
license_alignment: vendor_sdk_examples_surface
```

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed `BuddyAdapter` in `reference/home-runtime/`. Not built in this PR.
- Conformance: proposed hermetic suite first (fake-SDK injection); hardware-in-the-loop deferred.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.** No code in this RFC.
- **Java / Android SDK surface.** The Buddy SDK is Java-on-Android; URML's reference runtimes are Python. A `BuddyAdapter` requires a bridge boundary, which the RFC names honestly. Hermetic tests use a fake SDK.
- **Region-based mobility.** Buddy navigates named locations, not arbitrary coordinates; the manifest surfaces this in the static verifier.
- **SDK access posture.** The depth of the public SDK surface for third-party adapter authors may require a developer agreement. The RFC asks for clarification.

## Alternatives considered

1. **Ship a `BuddyAdapter` without engaging.** Rejected; the SDK access posture is unclear and the bridge shape benefits from maintainer signal.
2. **Treat Buddy as off-GitHub (vendor contact only), like OhmniLabs ([RFC-0292](0292-ohmnilabs-outreach.md)).** Rejected; the `BlueFrog_SDK_examples` repository is an active, Issues-enabled developer surface, so GitHub is the right channel.
3. **Fold Buddy into the educational-profile outreach.** Rejected; Buddy's primary positioning is home companionship and elder support, which is the Move #20 home-assistance frame.

## Prior art

- [`BlueFrogRobotics/BlueFrog_SDK_examples`](https://github.com/BlueFrogRobotics/BlueFrog_SDK_examples).
- Buddy SDK at [`sdk.buddytherobot.com`](https://sdk.buddytherobot.com/).
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md): the engagement → adapter-shipment precedent and the fake-SDK hermetic-test pattern.
- [RFC-0100 (iRobot Roomba)](0100-irobot-roomba-outreach.md): proposes the `reference/home-runtime/` package; home-assistance wave opener.
- [RFC-0106 (Home Assistant)](0106-home-assistant-outreach.md): the orchestration hub a companion routine composes into.

## Unresolved questions

For the Blue Frog Robotics SDK maintainers:

1. **Adapter home.** URML repo (`reference/home-runtime/src/home_runtime/buddy/`), a contributed example in `BlueFrog_SDK_examples`, or both?
2. **SDK access for third-party adapters.** Is the SDK surface available to integration authors on request, or is a developer agreement required?
3. **Bridge boundary.** Is a Python ↔ Java bridge the expected integration path, or does BFR prefer a different surface?
4. **Authoritative manifest values.** Buddy's mobility model, sensor inventory, and the canonical names for `speak` / `listen` channels.
5. **Conformance lane.** Open to a URML conformance line in the SDK documentation?
6. **Anything else.**

## Implementation note

RFC-0293 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move20.yaml`](../../examples/lighthouses/outreach-move20.yaml).

## Requested feedback

Items 1–6 from "Unresolved questions" above.

## How to respond

`BlueFrogRobotics/BlueFrog_SDK_examples` has Issues enabled (verified 2026-05-31). URML's planned channel: open a single Issue on that repository pointing to this RFC.

This RFC and its accompanying outreach post are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Motivation grounded in the verified `BlueFrog_SDK_examples` + Buddy SDK surface.
- [x] Java/Android-versus-Python bridge gap surfaced honestly.
- [x] Cross-link to RFC-0073 (engagement-to-adapter + fake-SDK pattern), RFC-0100 (home-runtime parent), RFC-0106 (orchestration hub), RFC-0292 (off-GitHub sibling).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, Java SDK bridge, region-based mobility, access posture).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added. Home-profile `speak` / `listen` reused, not extended.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-31.
- [x] Provenance `origin: FR`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
