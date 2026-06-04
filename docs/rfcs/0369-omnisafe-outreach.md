---
rfc: 0369
title: OmniSafe (safe reinforcement learning framework) integration, request for comment from the OmniSafe maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-04
updated: 2026-06-04
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

# RFC-0369: OmniSafe integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 is URML's safety and runtime-verification wave. This RFC reaches
[`PKU-Alignment/omnisafe`](https://github.com/PKU-Alignment/omnisafe) (an
infrastructural framework for safe reinforcement learning research, with
constrained-RL algorithms and benchmarks) and folds in its sibling environment
suite [`PKU-Alignment/safety-gymnasium`](https://github.com/PKU-Alignment/safety-gymnasium).
It **requests review and feedback from the OmniSafe maintainers**.

URML and OmniSafe meet at the safety constraint. OmniSafe trains policies under
explicit safety constraints, formulated as constrained Markov decision
processes: a policy is optimized to maximize return while keeping a cost (the
constraint signal) below a threshold. URML declares safety limits at the
**intent** level: a capability manifest plus a safety envelope (geofence,
occupancy, velocity and altitude limits, link-loss behavior), statically checked
at validator Pass 3 before a request is dispatched.

The composition: a URML safety envelope is a constraint declaration, and an
OmniSafe-trained policy is a learned controller that was optimized to respect
constraints. URML declares the safety constraints as intent-level limits and
validates dispatch against them; the trained policy is the substrate that runs
an admitted request, and URML statically bounds what that policy is allowed to
attempt. This mirrors the learned-policy-as-substrate framing from robomimic
([RFC-0360](0360-robomimic-outreach.md), Move #27) and Brax (Move #24). URML
does not train policies and does not solve a constrained MDP; it bounds and
validates what is dispatched to a policy that was trained to stay safe.

## Motivation

OmniSafe is a mature safe-RL framework, and its constrained-MDP formulation is a
clean dual to URML's safety envelope:

1. **A safe-RL constraint is a URML envelope from the other side.** OmniSafe's
   cost constraint bounds what a policy learns to do; URML's envelope bounds what
   intent is admitted before a policy runs. The same limit is expressed as a
   constrained-optimization objective below and a static declaration above.
2. **A trained policy is a learned controller URML can bound.** A safe-RL policy
   is a substrate: it consumes an admitted request and produces control. URML's
   contribution is the static Pass 3 check that the request is inside the
   declared envelope before the policy ever acts, so a learned policy never gets
   a request that exceeds the declared safety limits.
3. **safety-gymnasium gives the constraints something concrete to bind to.** The
   environment suite defines constrained tasks with cost signals. Those cost
   constraints are the control-level counterpart of a URML envelope limit, which
   makes the suite a natural place to show the intent-to-constraint mapping.
4. **It is substrate-neutral evidence.** A safety envelope that maps onto a
   constrained-MDP cost, and also onto a classical safety monitor, is evidence
   that URML's envelope is a portable declaration rather than a framework-shaped
   artifact.

OmniSafe repo at [`PKU-Alignment/omnisafe`](https://github.com/PKU-Alignment/omnisafe)
(about 1,123 stars, Issues enabled, not archived, last push 2025-03-17, so a
little over a year since the last push). safety-gymnasium at
[`PKU-Alignment/safety-gymnasium`](https://github.com/PKU-Alignment/safety-gymnasium)
(about 564 stars). Origin: Peking University, PKU-Alignment (China). Per
[RFC-0003](0003-us-alignment.md), the PRC-hardware provenance exclusion does not
apply to citing and consuming open-source academic software (same precedent as
GraspNet, RFC-0356, and Petoi); URML cites and composes, it does not vendor
hardware.

## Detailed design

### URML v0.1 envelope-to-constraint mapping (conceptual; no fixture lands here)

| URML field | Maps to OmniSafe / safety-gymnasium concept |
|---|---|
| `robot_id`, `description` | The agent's identity (carried at the manifest envelope; not a framework concept) |
| `mobility.max_velocity` | A velocity bound expressed as a cost constraint in the constrained MDP |
| `mobility.service_ceiling` / altitude limits | An altitude bound expressed as a cost constraint |
| Safety envelope geofence / occupancy (Pass 3) | A spatial cost constraint in a safety-gymnasium task |
| Safety envelope velocity / altitude limits (Pass 3) | Cost-constraint thresholds, conjoined strictest-wins before dispatch |
| Link-loss behavior ([RFC-0006](0006-connectivity-and-link-loss.md)) | A degraded-mode constraint regime the trained policy must respect on link loss |
| A trained safe policy | A learned-controller substrate URML statically bounds before dispatch (queued gap below) |

### What URML v0.1 does not yet express for OmniSafe

These are **gaps surfaced by the mapping**, flagged as *queued Spec RFCs* for
separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Constraint / safety-specification export.** URML's safety envelope is an
   internal validator artifact; it has no portable export a constrained-RL
   objective could consume. A future Spec RFC could define a constraint export
   from the envelope (limits, geofence, occupancy) that a constrained-MDP cost
   formulation could read as a target constraint set.
2. **Learned-safe-policy-as-substrate declaration.** A constrained-RL policy is a
   candidate substrate. URML has no manifest declaration for a learned safe
   controller as the body a primitive dispatches to. A future Spec RFC could add
   one, cross-referencing the learned-controller framing from robomimic
   (RFC-0360, Move #27) and Brax (Move #24).

### Compatibility notes

- **Origin / policy.** China (Peking University, PKU-Alignment). Per RFC-0003,
  citing and consuming open-source academic software is not gated; the
  PRC-hardware exclusion does not apply to open-source cross-citation (GraspNet
  RFC-0356 and Petoi precedents). No hardware is procured.
- **Relationship.** Open-source; the relationship is cross-citation and
  composition, not vendoring. URML composes above the learning layer and would
  cite OmniSafe and safety-gymnasium as constraint surfaces, not bundle them.
- **Substrate-neutrality.** A safe-RL policy is one learned-controller substrate
  among several; the same URML envelope limits map onto a classical safety
  monitor or a CBF-based controller with no change to the declaration.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The constraint export and the
  learned-safe-policy-as-substrate declaration are queued Spec RFCs.
- Reference runtime: no change. A mapping would express a URML envelope's limits
  as a constrained-MDP cost target; URML's contribution stays the static Pass 3
  check before dispatch, above the trained policy.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, envelope,
fixture, or runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Mild staleness.** OmniSafe's last push is 2025-03-17, a little over a year
  ago. The framework is mature and widely cited, but a thread may sit before a
  maintainer picks it up. safety-gymnasium is the more active of the pair.
- **Boundary risk.** A static intent-level bound and a learned constraint
  satisfaction are different guarantees. URML declares and validates before
  dispatch; it does not certify that a trained policy never violates its cost
  constraint. Question 2 below asks the maintainers to help draw that line.

## Alternatives considered

1. **Claim URML guarantees the policy's constraint satisfaction.** Rejected. A
   constrained-RL policy's safety is a property of training and the cost
   formulation, not of URML. URML statically validates intent against a declared
   envelope before dispatch; overstating this would fail the
   honest-substrate-limit norm ([RFC-0014](0014-substrate-conformance.md)).
2. **Engage safety-gymnasium alone and skip OmniSafe.** Rejected as the anchor.
   The framework (OmniSafe) is where the constrained-MDP formulation and the
   training live, which is what URML's envelope-as-constraint maps onto;
   safety-gymnasium is the environment surface. The environment suite is named
   and folded in, and the anchor moves if the maintainers say it is the right
   surface (question 3).
3. **Two separate RFCs, one per repo.** Rejected. OmniSafe and safety-gymnasium
   share the PKU-Alignment maintainer community; two Issues in a day to one org
   is the pattern that has drawn AI-content closes elsewhere. One anchor thread
   that names both is more respectful and just as discoverable.

## Prior art

- [RFC-0362 (RTAMT)](0362-rtamt-outreach.md): the Move #28 wave anchor;
  runtime-verification of temporal-logic specifications, the verification-side
  sibling to this learning-side engagement.
- [RFC-0360 (robomimic)](0360-robomimic-outreach.md): the learned-policy-as-substrate
  precedent (Move #27) this RFC cross-references for a safe policy.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  control-framework engagement URML's envelope limits dispatch above.
- [RFC-0291 (UTM strategic deconfliction)](0291-utm-strategic-deconfliction.md):
  related work where URML's envelope (geofence, altitude) meets an external
  constraint authority.
- [RFC-0006 (connectivity and link-loss)](0006-connectivity-and-link-loss.md):
  the link-loss behavior a degraded-mode constraint regime must respect.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  honest-substrate-limit norm this RFC applies to the altitude boundary.
- Sibling Move #28 RFC: RFC-0368 (safe-control-gym), the safe-control benchmark
  engaged alongside this framework.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  capability and safety-envelope surface this engagement exercises.

## Unresolved questions

For the OmniSafe maintainers:

1. **Envelope-to-cost mapping.** Does a URML safety-envelope constraint
   (velocity and altitude limits, geofence, occupancy) map cleanly onto a
   constrained-MDP cost or constraint in OmniSafe, or is the abstraction mismatch
   too large for a direct mapping?
2. **The boundary.** Is "URML declares and validates an intent-level static bound
   before dispatch; the trained policy provides learned constraint satisfaction
   during execution" the right division of labor, with URML staying above the
   policy?
3. **Integration surface.** Is OmniSafe (the framework, where the constrained-MDP
   formulation lives) or safety-gymnasium (the constrained-environment suite) the
   right surface for a mapping, and should the engagement stay one thread or
   fork?
4. **Trained-policy declaration.** Could a trained safe policy be described to
   URML as a learned-controller substrate (so URML can statically bound what it
   is dispatched), or is that outside the framework's intended use?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0369 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).
The `safety-gymnasium` row in the ledger shares this RFC; a dedicated row is
added only if the engagement forks to it.

## How to respond

The live channel is a GitHub Issue on
[`PKU-Alignment/omnisafe`](https://github.com/PKU-Alignment/omnisafe) pointing at
this RFC (the repo has Issues enabled). If the maintainers prefer
safety-gymnasium or another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (omnisafe about 1,123 stars, not archived,
      Issues enabled, last push 2025-03-17; safety-gymnasium about 564 stars,
      named and folded in).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, mild staleness, boundary risk).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; envelope-export and learned-safe-policy gaps
      flagged as queued Spec RFCs, not proposed here.
- [x] Provenance: China (PKU-Alignment); RFC-0003 open-source cross-citation is
      not gated (GraspNet / Petoi precedent), no hardware procured.
- [x] CLAUDE.md compliance check passed (substrate-neutral; URML composes above
      the learning layer, declares and validates intent, does not train policies).
