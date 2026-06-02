---
rfc: 0331
title: Gymnasium (RL environment API standard) integration, request for comment from the Farama Foundation maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-02
updated: 2026-06-02
state: Draft
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

# RFC-0331: Gymnasium integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #24 is URML's simulation and digital-twin wave. This RFC reaches a
**conceptual peer**, not a simulator or a substrate:
[`Farama-Foundation/Gymnasium`](https://github.com/Farama-Foundation/Gymnasium),
the de-facto reinforcement-learning environment API (the
`step` / `reset` / `action_space` / `observation_space` contract). It **requests
review and feedback from the Farama Foundation maintainers**.

URML is an intent and specification layer. It is **not** an RL environment, so
this is framed as a conceptual-peer and possible-adapter conversation, not a
substrate mapping. Two directions are interesting and exploratory:

1. A URML-validated policy could expose a Gymnasium environment so URML intent
   **constrains the action space** a learned agent is allowed to explore.
2. URML's capability manifest could **bound a Gym env's action space** to the
   declared-safe subset, so an agent never proposes an action outside the
   declared capability and the active safety envelope.

URML and Gymnasium operate at different layers. URML's contribution is **static
validation against the capability manifest and the active safety envelope before
anything executes**; Gymnasium's is the environment-interaction contract a
learning agent trains against. The fit is exploratory, and this RFC is honest
about that.

The sibling Farama repos
[`Farama-Foundation/PettingZoo`](https://github.com/Farama-Foundation/PettingZoo)
(the multi-agent RL API) and
[`Farama-Foundation/Gymnasium-Robotics`](https://github.com/Farama-Foundation/Gymnasium-Robotics)
are named here and folded into this one thread; URML does not open separate posts
for them.

## Motivation

URML and Gymnasium are peers at different layers, and the seam between an intent
layer and an RL environment API is worth mapping out loud:

1. **Action-space bounding is a validation problem.** A Gym env declares an
   `action_space`. URML's capability manifest
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) declares
   what a robot can do, and the safety envelope declares what it is allowed to do
   right now. Intersecting the two yields a declared-safe action subset. Bounding
   a learned agent's action space to that subset is exactly URML's "validate
   before you move" applied to RL exploration.
2. **A URML-validated policy could be an environment.** URML primitives
   (`move_to`, `grasp`, `scan`) are typed outcomes. A thin adapter could expose a
   URML-constrained command surface as a Gymnasium environment, so the action
   space an agent explores is the validated primitive set, not raw actuator
   commands. This keeps the learning loop inside the declared capability.
3. **Multi-agent maps onto fleet.** PettingZoo is the multi-agent RL API. URML's
   fleet work ([RFC-0286](0286-multi-robot-fleet-addressing.md)) addresses many
   robots with `peer_link` and barrier semantics. A multi-agent Gym env of
   URML-validated agents is the natural meeting point between the two.

Repo at [`Farama-Foundation/Gymnasium`](https://github.com/Farama-Foundation/Gymnasium)
(11,985 stars, Issues **and** Discussions enabled, not archived, last push
2026-05-30). License is asked as a question below (understood to be MIT; the
GitHub API did not surface an SPDX id at verification time). Origin is the Farama
Foundation (US non-profit; passes US-federal default policy).

## Detailed design

### URML v0.1 capability-manifest mapping (exploratory `gym_env_cell.yaml` fixture)

This is a conceptual-peer mapping, not a substrate dispatch mapping. The manifest
bounds an action space rather than naming a runtime target.

| URML field | Maps to Gymnasium concept |
|---|---|
| Validated Layer-2 primitive set (`move_to`, `dock`, `scan`, `grasp`, `release`, `detect`, `measure`, `capture`, `wait_for`, `report`, `call_program`) | The env `action_space` (the agent may only select validated primitives) |
| `mobility` / `manipulation` limits + safety envelope | Bounds on continuous action dimensions (velocity, force) and on which discrete actions are admissible |
| `perception.cameras[]` / `perception.sensors[].measurement_type` | The `observation_space` shape a URML-aware env exposes |
| `declared_locations`, `frames` | Discrete navigation targets in a navigation env's action / observation space |
| `programs` (`call_program`) | Composite actions an env exposes as single steps |
| Multi-agent roster (RFC-0286 fleet) | PettingZoo agents, one per URML-validated robot |

### What URML v0.1 does not yet express for Gymnasium

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **RL-environment / action-space alignment.** URML has no notion of an
   `action_space` or an `observation_space`. A future Spec RFC could define an
   optional projection from the validated primitive set and the conjoined
   envelope to a declared-safe action space, so a Gym adapter derives its bounds
   from the manifest rather than restating them. This would not make URML an RL
   framework; it would make the manifest the source of an env's safe bounds.

### Compatibility notes

- **Vendor org.** [`Farama-Foundation`](https://github.com/Farama-Foundation) is a
  US non-profit foundation stewarding the RL environment-API standards.
- **Engagement repo.** [`Farama-Foundation/Gymnasium`](https://github.com/Farama-Foundation/Gymnasium)
  is the RL environment API standard (the maintained successor to OpenAI Gym).
- **Sibling repos (folded into this thread).**
  [`Farama-Foundation/PettingZoo`](https://github.com/Farama-Foundation/PettingZoo)
  (multi-agent RL API; ties to URML fleet, RFC-0286) and
  [`Farama-Foundation/Gymnasium-Robotics`](https://github.com/Farama-Foundation/Gymnasium-Robotics)
  (robotics environments). Tracked in the ledger; no separate posts.
- **Origin / policy.** Farama Foundation (US non-profit). Passes US-federal
  default policy (open-source foundation, no provenance gate at the framework
  layer).
- **License fit.** Understood to be MIT; asked below. MIT and URML's Apache-2.0
  are compatible, and the engagement is cross-citation plus a possible adapter,
  not vendoring.
- **Substrate-neutrality.** Gymnasium is not a substrate; URML does not dispatch
  through it. An action-space bound derived from the manifest is substrate-neutral
  by construction, since the manifest is.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The RL-environment / action-space
  alignment is a queued Spec RFC, not proposed here.
- Reference runtime: no change. A Gymnasium adapter, if pursued, would be a thin
  layer that reads a validated URML manifest and exposes a bounded `action_space`;
  the exploratory `gym_env_cell.yaml` fixture would show the manifest -> bounded
  action-space derivation, with no learning loop required to prove the bound.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes. URML stays an intent layer; nothing here makes it an RL
framework.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Different layers, honest about the fit.** URML is an intent and capability
  layer; Gymnasium is an RL environment API. The fit is exploratory, and a
  maintainer may reasonably judge a URML -> Gymnasium adapter out of scope for
  Gymnasium (question 2 below). This RFC opens the conversation rather than
  asserting a clean mapping.
- **Adapter ownership is unclear.** A URML-constrained Gym env could live in
  URML, in a Farama repo, or in neither. The RFC does not presume; it asks.

## Alternatives considered

1. **Treat Gymnasium as a substrate and map primitives to `step()` calls.**
   Rejected. Gymnasium is a training-environment API, not a runtime URML
   dispatches through; forcing a substrate mapping would misrepresent both
   layers. The honest framing is conceptual-peer plus possible-adapter.
2. **Open three separate posts (Gymnasium, PettingZoo, Gymnasium-Robotics).**
   Rejected. Carpet-bombing one foundation with three Issues in a day is the
   pattern that has drawn AI-content closes elsewhere. One anchor thread that
   names the siblings is more respectful and just as discoverable.
3. **Engage at Brax (RFC-0329) and skip Gymnasium.** Rejected. Brax is an RL
   physics engine that uses the Gym-style API; Gymnasium is the API standard
   itself. The standard is the higher-leverage conversation about the env-API
   relationship, and Brax remains a sibling engagement in the same wave.

## Prior art

- [RFC-0286 (multi-robot fleet addressing)](0286-multi-robot-fleet-addressing.md)
  is URML's multi-agent layer; the meeting point with PettingZoo.
- [RFC-0329 (Brax outreach)](0329-brax-outreach.md): sibling Move #24 RFC; an RL
  physics engine that uses the Gym-style API, distinct from the API standard
  itself.
- Sibling Move #24 RFCs: RFC-0322 (Genesis), RFC-0323 (Isaac Sim), RFC-0325
  (CARLA), the simulator side of the wave.
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md): the substrate
  spine URML dispatches through; Gymnasium sits at a different (training) layer.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md):
  the validated primitive set that would form a URML-aware env's action space.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the manifest
  whose limits would bound that action space.

## Unresolved questions

For the Farama Foundation maintainers:

1. **Env-API vs intent-layer relationship.** Does framing URML (an intent and
   capability layer) as a conceptual peer to Gymnasium (an environment-interaction
   API) read correctly, or do you see a tighter or looser relationship?
2. **Adapter interest or out of scope.** Is a URML -> Gymnasium adapter (a
   URML-constrained environment whose action space is the validated, envelope-bounded
   primitive set) interesting to Farama, or is it firmly out of Gymnasium's scope
   and better owned entirely by URML?
3. **Action-space bounding.** Is deriving a Gym env's admissible action space from
   a declared capability manifest plus a safety envelope a pattern you would find
   useful, or one that fights the way `action_space` is meant to be used?
4. **PettingZoo and fleet.** Does the multi-agent tie (PettingZoo agents, one per
   URML-validated robot, mapped onto URML's fleet work in
   [RFC-0286](0286-multi-robot-fleet-addressing.md)) seem worth pursuing?
5. **License.** What is the current license of `Farama-Foundation/Gymnasium` (the
   GitHub API did not surface an SPDX id at verification time; understood MIT)?
6. **Conformance listing.** Would the Farama Foundation consider a project link to
   URML's compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0331 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).
The `PettingZoo` and `Gymnasium-Robotics` rows share this RFC; a dedicated row is
added only if the engagement forks to one of them.

## How to respond

The live channel is a GitHub Issue or Discussion on
[`Farama-Foundation/Gymnasium`](https://github.com/Farama-Foundation/Gymnasium)
pointing at this RFC (the repo has both enabled). If the maintainers prefer the
Farama Discord or a different repo for the conversation, URML will move the thread
there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (11,985 stars, not archived, Issues and
      Discussions enabled, last push 2026-05-30).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, different-layers fit, adapter ownership
      unclear).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gap (RL-environment / action-space
      alignment) flagged as a queued Spec RFC, not proposed here.
- [x] Provenance: Farama Foundation, US non-profit; default policy passes at the
      framework layer.
- [x] CLAUDE.md compliance check passed (Gymnasium is not a substrate; URML stays
      an intent layer, the conceptual-peer framing is honest about the layer gap).
