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

# Social Profile

**Status:** Draft (v0.1)
**Targets:** URML v0.1
**Created:** 2026-09-19
**RFC:** [RFC-0698](../../docs/rfcs/0698-expressive-platform.md)

A profile for expressive robots that look and gesture. This class has no wheels
and no gripper: a head that orients, a body that turns, and a vocabulary of
recorded or parametric expressive motions. Reachy Mini (Hugging Face / Pollen
Robotics), Furhat, ARI, Blossom, and desk animatronics are the motivating
platforms. The gap the profile closes is that URML could describe none of them:
the manifest had no head-pose envelope and there was no primitive for "look at
me" or "nod".

## Application domain

Consumer and research desk robots whose job is presence and interaction, not
locomotion or manipulation. Typically LLM-driven: a model requests an intent and
never moves anything directly, and the robot's runtime refuses an inadmissible
request with a typed reason the model hears back. URML's value on this class is
exactly that refusal: the head limits as a declaration, the check before
dispatch, the refusal as text.

## In scope

- Orienting the head (and body, if declared) toward a target: a face, a sound, a
  named object, or a numeric direction (`look_at`).
- Performing a named expressive motion from a declared vocabulary (`gesture`).
- Speaking and listening, shared with the home profile (`speak`, `listen`), when
  the manifest declares a `speech` endpoint.
- Single-axis expressive actuators (antennas, ears, eyelids) as RFC-0017
  `outputs.lines[]` driven by `set_output`. No new mechanism.

## Out of scope

- Locomotion and manipulation. A social robot declares `minimal_node` (RFC-0018)
  for the fact that it does not move, or composes `expression` with `mobility`
  when it is a mobile robot that also has an expressive head (ARI, TIAGo).
- The animation content of a gesture. URML checks the name, the nominal
  duration, and the declared envelope; the trajectory is the platform's, exactly
  as a `call_program` body is.
- The resolved pose for `face` / `sound` / `object` gaze. URML checks that the
  platform declared it can resolve that target kind; kinematics and perception
  are the substrate's job. Only `direction` is numerically checked.

## Profile-required Layer-1 manifest fields

A social-profile manifest declares an [`expression`](../layer-1-hal/) block: a
head pose envelope (`roll` / `pitch` / `yaw` ranges in degrees, optional
translation axes in metres, `max_angular_velocity` in rad/s), an optional
`body_yaw` range and `max_head_body_yaw_gap`, the closed `gaze` set of targets
the platform resolves, and a `gestures[]` vocabulary with per-gesture nominal
durations. At least one of `head` or `body_yaw` is present. The `gaze` set is
capability-gated against the rest of the manifest (a `face` target needs a
camera; `sound` a speech sensor; `object` an object vocabulary; `direction` a
head with a yaw or pitch axis).

## Default safety envelope

The default social-profile envelope leaves the `expression` sub-block empty, so
the manifest's declared head/body ranges and gesture durations apply until a
deployment tightens them. A deployment envelope may narrow any head or body
range (strictest-wins, never wider), cap gesture duration
(`max_gesture_duration_s`), or allow-list gestures (`gestures_allowed`).

The fixture lives at
[`reference/validator/tests/fixtures/envelopes/social_default.yaml`](../../reference/validator/tests/fixtures/envelopes/social_default.yaml).

## Primitives

Beyond the twelve-primitive core, the social profile adds two verbs, gated to
the profile and on a declared `expression` block:

- **`look_at`**: orient the head (and body) toward `face`, `sound`, `object`,
  or a numeric `direction`. See [Layer 2 §3](../layer-2-primitives/).
- **`gesture`**: perform a named motion from `expression.gestures[]`.

`speak` and `listen` are available when the manifest declares a `speech`
endpoint, as in the home profile.

## Worked example

[`examples/social/reachy-mini-greeting.*`](../../examples/social/): a Reachy Mini
manifest with the reachy-nova deployment's real head/body limits and gesture
durations, a "look at me, nod, say hello, then glance up and to the left"
program, and a companion rejected program (an undeclared `wave`, a pitch beyond
the declared range) showing the two refusals the profile exists to produce.
