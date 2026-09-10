---
rfc: 0698
title: Expressive platform, the `expression` manifest block and the home-profile `look_at` / `gesture` primitives
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-10
updated: 2026-09-10
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

# RFC-0698: Expressive platform, the `expression` manifest block and the home-profile `look_at` / `gesture` primitives

## Summary

A growing class of robots has no wheels and no gripper. It has a head that looks, a body that turns, and a vocabulary of expressive motions: Reachy Mini (Hugging Face / Pollen Robotics, `pollen-robotics/reachy_mini`, Apache-2.0), Blossom, ARI, Furhat, desk animatronics. URML cannot describe them today. The manifest has no place to declare a head-pose envelope, `drive_type` has no non-locomoting value, and there is no primitive for "look at me" or "nod". The only honest declaration is RFC-0018's `minimal_node`, with every head motion hidden behind `call_program`, which declares nothing about the one envelope that matters on such a robot.

The gap became concrete in a Reachy Mini deployment driven by a speech-to-speech LLM ([`OriNachum/reachy-nova`](https://github.com/OriNachum/reachy-nova), MIT). Its harness already has the URML posture: the model requests intents and never moves anything, the body runtime refuses with a typed reason the model hears back. Its head limits (yaw ±45°, pitch −15° to +25°, body yaw ±25°, head-body yaw gap ≤30°) are hard-coded in three places (`safety.py`, `gestures.py`, and the prose of the skill the model reads), with nothing that reads them as one declaration.

This RFC proposes an optional Layer-1 `expression` block (head pose ranges, body yaw, gaze targets, a declared gesture vocabulary) and two home-profile primitives gated on it, `look_at` and `gesture`, the way `speak` is gated on the `speech` endpoint. Antennas and similar single-axis expressive actuators stay RFC-0017 output lines; no new mechanism is added for them. It is a **Draft for maintainer decision**. No schema, validator, or adapter change lands until it advances.

## Motivation

The failure today is not that an expressive robot cannot be driven. It is that URML cannot **refuse** anything about it. On reachy-nova the model tool `goto` accepts a full head pose; the runtime clamps or rejects out-of-range values in code the model never sees. URML's value on this platform is exactly the missing piece: the limits as a declaration, the check before dispatch, the refusal as text a model can act on. Without a place to declare the head envelope, URML has nothing to check.

Three earlier touches hit the same wall and were parked: Furhat skills (RFC-0552, "social robotics is a different world from actuation"), Bottango animatronics (RFC-0608), and the animatronics lane banked in Move #60. Reachy Mini is the highest-traction instance of the class (the SDK has about 1,500 stars and is pushed daily), and RFC-0384 already gave the manifest a `KinematicChain` of `kind: head`. This RFC gives that chain a task-space envelope and two verbs.

## Detailed design

All additions are optional. A manifest without `expression` behaves exactly as today; a program using `look_at` or `gesture` against such a manifest is rejected at Pass 2, the same rule `speak` follows.

### 1. The `expression` manifest block (Layer 1)

```yaml
expression:
  head:
    chain_ref: head              # optional; a whole_body.chains[] entry of kind head (RFC-0384)
    roll:  { min: -30, max: 30 }    # degrees; each axis optional; omitted = not commandable
    pitch: { min: -15, max: 25 }
    yaw:   { min: -45, max: 45 }
    x: { min: -0.02, max: 0.02 }    # metres; translation axes optional (Stewart-platform heads)
    y: { min: -0.02, max: 0.02 }
    z: { min: -0.01, max: 0.03 }
    max_angular_velocity: 3.0       # rad/s; optional
  body_yaw: { min: -25, max: 25 }   # degrees; optional; omitted = the body does not turn
  max_head_body_yaw_gap: 30         # degrees; optional
  gaze: [face, sound, object, direction]   # closed set: the look_at targets this platform resolves
  gestures:                          # the declared vocabulary; names are identifiers
    - name: yes
      duration_s: 1.2
      description: Nod.
    - name: curious
      duration_s: 1.8
      description: Head tilt with a slow settle.
```

Rules:

- At least one of `head` or `body_yaw` is present. A `head` block declares at least one rotation axis.
- Angles are degrees, translations metres, angular velocity rad/s. This matches the manifest's existing convention (`max_slope` and `max_body_tilt` in degrees, `max_angular_velocity` in rad/s). Adapters convert to whatever the SDK wants.
- `chain_ref`, when present, must resolve to a `whole_body.chains[]` entry with `kind: head`. `whole_body` is not required; a desk robot declares `expression` alone.
- `gaze` entries are capability-gated: `face` requires at least one `perception.cameras[]` entry; `object` requires a non-empty `perception.object_vocabulary`; `sound` requires a `perception.sensors[]` entry with `measurement_type: speech` (a microphone array able to report direction of arrival); `direction` requires `head` with at least one of `yaw` or `pitch`. Codes: `capability.gaze_face_requires_camera`, `capability.gaze_object_requires_vocabulary`, `capability.gaze_sound_requires_speech_sensor`, `capability.gaze_direction_requires_head`.
- `gestures[].name` are unique identifiers. `duration_s` is the platform's nominal duration and is what the envelope caps.
- `expression` composes with `minimal_node` (RFC-0018): a robot that does not locomote declares `minimal_node` for that fact and `expression` for what it can do. It also composes with `mobility` (a mobile robot with an expressive head, such as ARI or TIAGo). Neither is required.
- Antennas, ears, eyelids, and other single-axis expressive actuators are `outputs.lines[]` analog lines (RFC-0017) with `safe_state` as the rest angle, driven by `set_output`. No new mechanism.

### 2. `look_at` (home profile)

```yaml
- look_at:
    target: face | sound | object | direction   # required
    object: <identifier>       # required iff target == object; in perception.object_vocabulary
    direction:                 # required iff target == direction; degrees
      yaw: <number>
      pitch: <number>
      roll: <number>           # optional
      body_yaw: <number>       # optional
    duration: <duration>       # optional; default 1s; must be positive
    hold: <duration>           # optional; default 0s; keep the gaze after arriving
```

**Semantics.** The robot orients its head (and body, if declared and requested) toward the target. For `face`, `sound`, and `object` the runtime resolves the target to a pose itself; kinematics and perception are the substrate's job, and URML checks only that the platform declared it can resolve that target kind. For `direction` the request is numeric and URML checks it against the declared ranges before dispatch. `hold` keeps the gaze for the stated duration; the runtime resumes its idle behavior afterward.

**Capability requirements (Layer 1).** `manifest.expression` is present (`capability.expression_not_declared`). `target` is in `expression.gaze` (`capability.gaze_target_not_declared`). For `direction`, every stated axis is inside its declared range (`capability.head_pose_outside_envelope`, naming the axis, the requested value, and the declared range), `body_yaw` is inside `expression.body_yaw`, and when `max_head_body_yaw_gap` is declared, `|yaw − body_yaw|` does not exceed it (`capability.head_body_yaw_gap_exceeded`). For `object`, the identifier is in `object_vocabulary` (the existing `detect` rule).

**Safety-envelope checks.** The envelope's `expression` sub-block (§4) tightens the ranges strictest-wins.

**Variable bindings.** None in v1. A later revision may add `store_as` resolving to the reached pose.

### 3. `gesture` (home profile)

```yaml
- gesture:
    name: <identifier>         # required; in expression.gestures[].name
    intensity: <0.0..1.0>      # optional; default 1.0; scales amplitude within the envelope
    interrupt: true | false    # optional; default false; queue behind a running gesture
```

**Semantics.** The robot performs the named expressive motion from its declared vocabulary. The animation content is the platform's (a recorded move, a parametric curve, a `play_motion` entry); URML checks the name, the nominal duration, and nothing about the trajectory. That is the same honesty line as `call_program`: the difference is that a gesture is declared with a duration in a closed vocabulary, so the validator can refuse an unknown name and an over-long motion instead of passing an opaque string through.

**Capability requirements (Layer 1).** `manifest.expression` is present. `name` is declared (`capability.gesture_not_declared`; the message lists the declared vocabulary, which is what reachy-nova's own error string does today).

**Safety-envelope checks.** `duration_s` of the named gesture does not exceed the envelope's `max_gesture_duration_s`; `name` is in `gestures_allowed` when that allow-list is present.

**Variable bindings.** None.

### 4. Envelope additions (Layer 1)

```yaml
expression:                        # optional sub-block of the safety envelope
  head:
    yaw:   { min: -30, max: 30 }   # strictest-wins against the manifest
    pitch: { min: -10, max: 20 }
  body_yaw: { min: -15, max: 15 }
  max_angular_velocity: 1.5
  max_gesture_duration_s: 4.0
  gestures_allowed: [yes, no, curious]
```

An envelope cannot widen a manifest range (the existing rule). The home profile's default envelope leaves the sub-block empty, so the manifest's declared ranges apply until a deployment tightens them.

### 5. Spec changes

- **Layer 1.** `Manifest.expression` (new optional model: `Expression`, `HeadEnvelope`, `AxisRange`, `GestureDecl`); `SafetyEnvelope.expression`. Cross-checks listed above. The v0.2.0 manifest document gains an `expression` section next to `minimal_node`.
- **Layer 2.** Two profile-scoped primitives, `look_at` and `gesture`, documented in §3 next to `speak` and `listen`, with `LookAtArgs` and `GestureArgs` added to the primitive registries (`PRIMITIVE_NAMES`, `PRIMITIVE_MODELS`, the composition `Step` fields). The core twelve are untouched.
- **Layer 3.** Unchanged. Whether `speak` and `gesture` may run concurrently is a composition question this RFC does not open; the first landing runs them in sequence.
- **Layer 4.** No grammar change. The prompt contract is generated from the schemas, so the two primitives appear with their argument shapes, and the declared `gestures[].name` and `gaze` sets are inlined the way `object_vocabulary` is, so the model emits only declared names. The existing rule that the model MUST NOT invent capability covers "wave" on a robot that declared no `wave`.
- **Home profile.** The profile README lists `look_at` and `gesture` beside `speak` and `listen` and relaxes the "must declare mobility" line for manifests that declare `expression` (a stationary expressive robot is a home-profile robot that cannot run fetch-and-carry programs, which the README already says).
- **Validator.** Pass 2 gains the checks and codes above. Pass 4 (envelope) gains the strictest-wins comparison for the `expression` sub-block.

### 6. Reference-runtime sketches

Every sketch passes the substrate-neutrality acid test; two of the three have no ROS anywhere.

- **Reachy Mini (zero ROS).** A `ReachyMiniAdapter` in `reference/edu-runtime`, the Microduck shape. `look_at direction` becomes `ReachyMini.goto_target(head=create_head_pose(yaw, pitch, roll, degrees=True), body_yaw=radians(body_yaw), duration=...)`; `look_at sound` reads the daemon's direction-of-arrival (`GET /api/state/doa`) and turns it into a yaw; `look_at face` uses the runtime's own tracker (`look_at_image(u, v)`) and refuses when no detector is configured; `gesture` plays a recorded move (`POST /api/move/play/recorded-move-dataset/{dataset}/{move}`) or a configured named move; antennas ride `set_output` into `goto_target(antennas=[right, left])` in radians. The SDK speaks radians and 4×4 matrices; the adapter converts.
- **reachy-nova (an LLM harness above the SDK).** An optional pre-flight in the harness's tool dispatch, before the intent is written to the spool: the tool call is rendered as a one-step URML program, validated against the Reachy Mini manifest and the deployment envelope, and a refusal is returned in the harness's existing `{"ok": false, "error": ...}` shape. Fail-open when the validator is not installed, matching the harness's own feature-switch convention. This is the co-designed change, built only with the maintainer.
- **ROS 2 (pan-tilt or humanoid head).** `look_at direction` publishes a `JointTrajectory` on the head joints; `gesture` maps to a `play_motion` entry (ARI, TIAGo) or a named behavior in the robot's expression node. The `mock` adapter records the calls for hermetic conformance.

### 7. Motivating example

[`examples/home/reachy-mini-greeting.*`](../../examples/home/) ships with this Draft: a manifest declaring reachy-nova's actual limits and its eight gestures with their measured durations, a program for "Look at me, nod, and say hello. Then glance up and to the left.", and a companion `rejected` program (an undeclared `wave`, a pitch of 60°) showing the two refusals this RFC exists to produce. The files are marked non-validating until the schema lands.

## Backward compatibility

Fully compatible. `expression` is optional on manifest and envelope; existing manifests, envelopes, programs, and adapters are unchanged. Two primitive names are added to the registries; no existing name or argument changes. Pre-v1.0.

## Drawbacks

- **Two new primitives.** Adding a primitive is a one-way door. The mitigation is that neither can be composed from the existing twelve: `move_to` is a base-frame navigation goal, `turn` (RFC-0630) is relative locomotion, and `call_program` declares nothing. The alternatives below were tried on paper first.
- **`face`, `sound`, and `object` gaze are not numerically checkable.** URML checks the declaration, not the resolved pose; the runtime owns kinematics and perception. `direction` is the only target with a numeric refusal. This is stated rather than papered over.
- **Gesture content is opaque.** URML refuses an unknown name and an over-long motion, and nothing about what the trajectory does inside the envelope. The platform owns that, the same way it owns a `call_program` body.
- **Units.** Degrees in the manifest, radians in most SDKs. Every adapter converts; the conformance fixtures include a boundary value to catch a missed conversion.

## Alternatives considered

1. **`call_program` for gestures, `set_output` for antennas, nothing for head pose.** Works today and declares nothing about the head envelope, which is the whole safety story on this class. Rejected as the permanent answer; it remains the fallback for platforms that do not adopt the block.
2. **A new `social` profile.** Cleaner name, heavier process (a profile RFC, a spec directory, a default envelope). The home profile already owns voice-driven consumer flows and `speak` / `listen`, and every motivating robot is a consumer or research desk device. Deferred; the primitives are profile-scoped so they can move if a `social` profile is later drafted. **This is the decision for the maintainer.**
3. **A `stationary` value in `mobility.drive_type`.** Rejected: `mobility` is locomotion, and RFC-0018's `minimal_node` already states "does not move" honestly.
4. **`look_at` with a 3D point.** The natural target for a runtime (`look_at_world(x, y, z)`), and not checkable without kinematics. Rejected for v1; `direction` in degrees is checkable and matches how reachy-nova's `control` skill is written. A `point` target can be added later without breaking anything.
5. **Extending `move_to` with a head pose.** Rejected: it changes what `move_to` means, which profiles may not do.
6. **Naming.** `gesture` collides in spirit with `wait_for(condition.input: gesture)`, where it means the human's gesture. `perform` and `express` were considered. `gesture` is kept because it is the word every motivating platform uses; the collision is documented in the Layer-2 text.

## Prior art

RFC-0384 (`KinematicChain` with `kind: head`, the structural hook this block hangs on), RFC-0017 (`set_output`, which antennas ride), RFC-0018 (`minimal_node`, the non-locomoting declaration), RFC-0015 (`call_program`, the opaque fallback), RFC-0630 (`turn`, why body yaw here is not locomotion), RFC-0383 (`learned_policy`, the precedent for declaring an envelope the validator refuses outside of). The Reachy Mini SDK (`goto_target`, `look_at_image`, `look_at_world`, `play_move`; daemon REST `/api/move`, `/api/state`). reachy-nova's `goto`, `run_behavior`, `look_at_face`, `look_at_sound` tools and its `SafetyConfig`. Furhat's gaze and gesture skill API, PAL's `play_motion`, Blossom, Bottango.

## Unresolved questions

- **Home profile or a new `social` profile** (alternative 2). Maintainer decision.
- **Should `look_at face` require a declared face detector** (`perception.object_detection` on class `person`) rather than any camera? Stricter and more honest; also more friction for the first adopters. Proposed: camera-only in v1, tighten when a second platform lands.
- **`intensity` on `gesture`.** Useful on parametric animations (reachy-nova scales amplitude), meaningless on recorded moves. Keep as optional, or drop until asked for.
- **First-class antennas.** Output lines are honest and a little ugly for a robot whose antennas are half its expressiveness. Revisit if a second antenna-bearing platform arrives.
- **Degrees.** The block uses degrees because every human-facing limit in the motivating code is in degrees. The rest of the manifest mixes units already; a units-normalization RFC is a separate conversation.

## Implementation note

This RFC is a **Draft**. Nothing lands until it advances. On advance it lands additively in the `0.1.x` line as one vertical slice, the RFC-0384 way: the Layer-1 models and envelope sub-block, `LookAtArgs` and `GestureArgs` in the primitive registries, the Pass-2 and Pass-4 checks with the codes above, the Layer-2 §3 sections, the home-profile README lines, conformance fixtures (accept, refuse on undeclared gesture, refuse on out-of-range direction, refuse on a manifest without `expression`), the `mock` adapter mapping, the `ReachyMiniAdapter` with a hermetic fake transport, a regenerated schema export, and the motivating example turned validating. The harness pre-flight for reachy-nova is a separate, co-designed change in that repository.

## Self-review (Phase 1)

- [x] The Summary alone tells a reader what is proposed and why now.
- [x] The Motivation is grounded in a concrete deployment and three earlier parked touches, not a hypothetical.
- [x] Every affected layer is named; a zero-ROS sketch (Reachy Mini SDK), an LLM-harness sketch, and a ROS-2 sketch are present, so the acid test holds.
- [x] Six alternatives are considered on their merits; the maintainer decision is called out, not silently made.
- [x] Drawbacks are real: a one-way door, three non-numeric gaze targets, opaque gesture content, a unit mismatch.
- [x] Backward compatibility is honest: additive, defaults reproduce today.
- [x] No provider, vendor, or substrate is encoded: the block names ranges and vocabularies, never an SDK, a model, or a cloud service.
- [x] Prose checked against [`AGENTS.md`](../../AGENTS.md): no em-dashes, no hedging adverbs, no empty intensifiers.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed compliance.
