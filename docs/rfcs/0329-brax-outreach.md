---
rfc: 0329
title: Brax (JAX differentiable physics for RL) integration, request for comment from the Brax maintainers
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

# RFC-0329: Brax integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's training environment, and
requests review from that target's maintainers. It does not modify URML's
normative surface.

## Summary

Move #24 engages the simulation and digital-twin layer. This RFC reaches
[`google/brax`](https://github.com/google/brax), a JAX-based, massively-parallel
differentiable physics engine for training reinforcement-learning control
policies. It **requests review and feedback from the Brax maintainers**.

URML's fit with Brax is the **train-in-sim** angle. URML is the intent and
specification layer **above** a learned controller: a policy trained in Brax
becomes a substrate that URML dispatches to, and URML's capability manifest and
safety envelope statically bound what that learned controller is allowed to
attempt. URML intent -> validated Layer-2 primitives -> a Brax-trained policy
acting as the substrate controller. The differentiator is **static validation
against the declared capability and envelope before the learned controller is
handed an intent to realize**.

This framing (a learned controller as a URML substrate) is newer ground for
URML than the engine-as-renderer framing of its other simulation engagements,
and the RFC says so plainly.

## Motivation

Brax is built for one thing extremely well: training control policies at scale
on accelerators. That makes it a different kind of URML engagement than a
renderer or a high-fidelity validator:

1. **It is where the controller is learned, not where intent is described.** A
   Brax-trained policy maps observations to actions. URML sits above it: the
   manifest declares what the robot can do, the validator checks an intent
   against that capability and the envelope, and only an admissible intent is
   passed to the learned policy to realize. The policy is the substrate.
2. **A learned controller needs a static bound it cannot exceed.** A policy
   trained in sim can propose actions outside a robot's safe capability. URML's
   contribution is the static gate: a `move_to` is rejected before dispatch if
   the manifest's `max_velocity` or the envelope forbids it, regardless of what
   the policy would output. That is exactly the bound a learned controller
   benefits from at deployment.
3. **The acid test still holds.** A URML primitive that binds to a Brax-trained
   policy must still bind to a hand-written controller or a vendor SDK, and it
   does: URML maps a primitive to an outcome, and the policy is one realizer of
   that outcome among many. The learned controller is a substrate, not a special
   case in the language.

Repo at [`google/brax`](https://github.com/google/brax) (3,175 stars, Issues
**and** Discussions enabled, not archived, actively developed). License is asked
as a question below (understood to be Apache-2.0; the GitHub API did not surface
an SPDX id at verification time). Brax originates at Google (United States);
passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `brax_policy_cell.yaml` fixture)

| URML field | Maps to Brax attribute |
|---|---|
| `robot_id`, `description` | Brax environment / policy identity (carried at the manifest envelope, not a Brax concept) |
| `mobility.drive_type`, `manipulation` joints | The Brax environment's action space the trained policy drives (joint torques / velocities) |
| Primitive (`move_to`, `grasp`) | An outcome the trained policy is invoked to realize; the manifest declares the capability the policy must respect |
| `perception.sensors[].measurement_type` | The Brax environment's observation space the policy reads |
| `mobility.max_velocity`, `mobility.max_payload` | Bounds URML checks statically before the policy is dispatched; the policy never sees an out-of-envelope intent |
| Safety envelope limits (Pass 3) | The static bound that constrains what the learned controller is allowed to attempt; conjoined strictest-wins before dispatch |

### What URML v0.1 does not yet express for Brax

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Learned-controller / policy-substrate declaration.** URML's manifest
   declares capability, not that a deployment's controller is a learned policy
   with a defined action and observation interface. A future Spec RFC could add
   an optional policy-substrate declaration so the adapter's primitive ->
   policy binding is checkable, without modelling the policy weights (those
   stay substrate configuration).
2. **RL-environment alignment.** URML does not declare how a primitive's
   outcome aligns with an RL environment's reward, action, and observation
   structure. A future Spec RFC could add an optional environment-alignment hint
   so a fixture can state which Brax environment a primitive was validated
   against. Shared with the sibling Move #24 RFCs.

### Compatibility notes

- **Vendor org.** [`google`](https://github.com/google); Brax is a Google
  Research project.
- **Engagement repo.** [`google/brax`](https://github.com/google/brax), the
  JAX differentiable physics engine and RL training environments.
- **Origin.** United States (Google). Passes US-federal default policy
  (open-source training engine, no provenance gate at the simulation layer).
- **License fit.** Understood to be Apache-2.0; asked below as a question.
  Apache-2.0 matches URML's own posture exactly; a validated-intent mapping
  carries no license entanglement.
- **Substrate-neutrality.** A Brax-trained policy is one substrate among many;
  the same URML primitives map to a MuJoCo-trained policy
  ([RFC-0060](0060-mujoco-integration.md)), an MJX / mujoco_playground policy
  ([RFC-0144](0144-deepmind-mujoco-playground-outreach.md)), or a hand-written
  controller.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The policy-substrate and
  RL-environment-alignment declarations are queued Spec RFCs.
- Reference runtime: a Brax mapping would dispatch a validated primitive to a
  trained policy acting as the substrate controller, with the policy reading the
  environment observation and emitting actions inside URML's statically-checked
  bound; the planned `brax_policy_cell.yaml` fixture would prove the mapping
  hermetically against a small trained policy.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Newer ground for URML.** The learned-controller-as-substrate framing is less
  established than URML's engine-as-renderer engagements. The mapping is honest
  about that: it is a request to test whether the framing resonates, not a
  settled design.
- **Training vs deployment gap.** Brax is a training engine; URML's value is at
  deployment, when a trained policy realizes an intent. A demo that shows the
  full loop (train in Brax, deploy under URML's gate) is heavier than URML's
  hermetic-demo posture, so the first artifact is likely the static-bound
  validation, not the training run.

## Alternatives considered

1. **Fold Brax into RFC-0144 (mujoco_playground).** Rejected. mujoco_playground
   is the closest sibling (MJX-based RL on MuJoCo physics), and Brax and MJX are
   related in the JAX RL ecosystem, but Brax is a distinct engine with its own
   maintainers; it earns a dedicated request for comment, cross-linked to the
   sibling rather than buried in it.
2. **Engage at a downstream RL library that uses Brax instead of the engine.**
   Rejected as the anchor. The learned-controller-as-substrate question is about
   the environment and policy interface Brax defines; the engine repo is where
   that interface and its maintainers live.
3. **Model the policy itself in the URML manifest.** Rejected. Policy weights
   and the training objective are substrate configuration; modelling them in the
   capability manifest would fail the substrate-neutrality acid test. URML
   declares the capability the policy must respect, not the policy.

## Prior art

- [RFC-0144 (DeepMind mujoco_playground outreach)](0144-deepmind-mujoco-playground-outreach.md)
  (the closest sibling: MJX-based RL training environments on MuJoCo physics).
- [RFC-0060 (MuJoCo integration outreach)](0060-mujoco-integration.md), the
  MuJoCo physics engine beneath MJX; note the MJX / MuJoCo relationship Brax
  sits alongside in the JAX RL ecosystem.
- [RFC-0050 (NVIDIA Isaac Lab integration)](0050-nvidia-isaac-lab-integration.md)
  (an earlier RL-training-environment engagement).
- Sibling Move #24 RFCs: RFC-0322 (Genesis), RFC-0323 (Isaac Sim), RFC-0325
  (CARLA), RFC-0331 (Gymnasium).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  (the spec surfaces this engagement exercises: capability declaration and the
  primitive outcomes a policy realizes).

## Unresolved questions

For the Brax maintainers:

1. **Environment-definition boundary.** Is the right URML boundary "URML
   primitive -> action in a Brax environment the trained policy drives", with
   the environment definition and reward left in Brax? Where does URML's intent
   layer end and Brax's environment begin?
2. **Learned-controller-as-substrate framing.** Does the framing (a Brax-trained
   policy as a URML substrate, with URML's manifest and envelope as a static
   bound the policy cannot exceed at deployment) resonate, or is the more
   natural integration something else entirely?
3. **MJX / playground relationship.** Brax and MJX / mujoco_playground both live
   in the JAX RL ecosystem. From the maintainers' view, is URML better engaging
   Brax, MJX, or both, and how do they relate for a deployment-time gate?
4. **Action / observation alignment.** Does URML's capability altitude map
   cleanly onto a Brax environment's action and observation spaces, or does the
   policy interface expect detail URML deliberately leaves to substrate
   configuration?
5. **License.** What is the current license of `google/brax` (the GitHub API did
   not surface an SPDX id at verification time; understood to be Apache-2.0)?
6. **Conformance listing.** Would Brax consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0329 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`google/brax`](https://github.com/google/brax) pointing at this RFC (the repo
has both enabled). If the maintainers prefer their own forum, URML will move the
thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (3,175 stars, not archived, Issues and
      Discussions enabled, last push 2026-05-18).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, newer-ground framing, training vs
      deployment gap).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US-origin (Google) training engine; default policy passes at
      the simulation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; a Brax-trained
      policy is one substrate among many, composed-above not assumed).
