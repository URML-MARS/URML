---
rfc: 0327
title: Habitat (embodied-AI simulator) integration, request for comment from the Habitat maintainers
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

# RFC-0327: Habitat integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's simulator, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #24 is URML's simulation and digital-twin wave. This RFC reaches Habitat,
the high-performance embodied-AI simulator for navigation and interaction in
photorealistic indoor scenes. The engine is [`facebookresearch/habitat-sim`](https://github.com/facebookresearch/habitat-sim);
the task and training layer is the sibling [`facebookresearch/habitat-lab`](https://github.com/facebookresearch/habitat-lab).
This RFC anchors on habitat-sim and folds habitat-lab into the same thread, and
**requests review and feedback from the Habitat maintainers**.

URML's navigation and interaction subset (`move_to`, `scan`, `detect`,
`measure`, `report`) maps onto a Habitat agent's action space. The differentiator
is **static validation of the intent against the declared agent capability and
the active safety envelope before the agent acts**.

This RFC is honest about altitude up front, per the
[RFC-0014](0014-substrate-conformance.md) honest-substrate-limit norm: a Habitat
embodied-navigation agent is a navigation-and-perception-first body, not a full
manipulator, so the capability manifest URML declares for it is a lower-bound
subset. URML does not claim Habitat does more than it does.

## Motivation

Habitat is a fast, photoreal indoor simulator widely used for embodied-AI
research. Running a URML program against a Habitat agent is a clean way to
exercise the navigation and perception subset with no hardware in the loop:

1. **The action space is URML's navigation subset.** A Habitat agent moves,
   turns, and senses in a scene. URML's `move_to`, `scan`, `detect`, `measure`,
   and `report` map onto that action space directly. The acid test holds: those
   primitives are the same ones that drive a real mobile robot or a zero-ROS
   runtime, so a Habitat agent is one more Layer-1 target.
2. **Photorealistic scenes are a real perception surface.** Habitat renders
   photoreal indoor scenes from datasets, so `detect`, `measure`, and `capture`
   exercise a meaningful perception manifest rather than a toy one. The
   `object_vocabulary` and `sensors[].measurement_type` blocks have something to
   bind against.
3. **It is where validate-before-you-act is cheap to show.** A simulated agent
   is the cheapest place to demonstrate URML's contribution: a static check,
   before the agent takes its first action, that the declared agent capability
   and the safety envelope admit the requested intent.

Engine repo at [`facebookresearch/habitat-sim`](https://github.com/facebookresearch/habitat-sim)
(3,696 stars, Issues enabled, Discussions disabled, not archived, last push
2026-05-07). Task layer at [`facebookresearch/habitat-lab`](https://github.com/facebookresearch/habitat-lab)
(roughly 3,000 stars). License is asked as a question below (the GitHub API did
not surface an SPDX id at verification time; understood to be MIT). Origin: Meta
/ FAIR (United States); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `habitat_agent_cell.yaml` fixture)

| URML field | Maps to Habitat attribute |
|---|---|
| `robot_id`, `description` | Agent identity (not a Habitat concept; carried at the manifest envelope) |
| `frames`, `declared_locations` | The scene's coordinate frame and named navigable positions / episode goals |
| `mobility.drive_type` | The agent's locomotion model (a navigable embodied agent over a scene's navmesh) |
| `mobility.max_velocity` | The agent's per-step move magnitude, conjoined with the envelope |
| `perception.cameras[]` | The agent's RGB sensor (Habitat's sensor suite) |
| `perception.sensors[].measurement_type: depth` | The agent's depth sensor |
| `perception.object_vocabulary` | The scene dataset's object / semantic categories `detect.object` draws from |
| Navigation subset (`move_to`, `scan`, `detect`, `measure`, `report`) | The agent's action space; honest lower-bound subset (no `grasp` / `release` for a navigation-first agent) |
| Safety envelope limits (Pass 3) | Scene bounds + URML envelope; URML conjoins strictest-wins before the action |

### What URML v0.1 does not yet express for Habitat

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Embodied-agent / scene-dataset profile.** URML has no profile describing an
   embodied navigation agent operating over a named scene dataset (its episodes,
   goals, and semantic categories). A future Spec RFC could add an optional
   embodied-agent profile so the manifest can declare the dataset and episode
   surface the agent is bound to. It would not model the simulator itself.
2. **Simulator-target class hint.** As with the other Move #24 targets, URML's
   manifest does not declare that a deployment targets a simulator rather than
   hardware; a queued Spec RFC could add an optional simulator-target class hint.

### Compatibility notes

- **Vendor org.** [`facebookresearch`](https://github.com/facebookresearch)
  (Meta / FAIR, Fundamental AI Research).
- **Engagement repo.** [`facebookresearch/habitat-sim`](https://github.com/facebookresearch/habitat-sim),
  the simulation engine (the integration anchor).
- **Sibling repo (folded into this thread).**
  [`facebookresearch/habitat-lab`](https://github.com/facebookresearch/habitat-lab),
  the task, episode, and training layer. The engine is habitat-sim; the tasks
  are habitat-lab. Which is the right integration surface is an open question
  below.
- **Origin / policy.** United States (Meta / FAIR). Passes US-federal default
  policy (open-source research simulator, no provenance gate at the simulation
  layer).
- **License fit.** Understood to be MIT; not SPDX-detected at verification time,
  so asked below as a question.
- **Substrate-neutrality.** Habitat is one embodied-AI simulator among several;
  the same URML primitives map to AI2-THOR ([RFC-0147](0147-allenai-ai2thor-outreach.md)),
  Webots ([RFC-0234](0234-webots-outreach.md)), or a real mobile robot.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The embodied-agent / scene-dataset
  profile and the simulator-target class hint are queued Spec RFCs.
- Reference runtime: no change. A Habitat adapter would translate a primitive's
  navigation goal into the agent's action space; a planned
  `habitat_agent_cell.yaml` fixture would document the lower-bound navigation
  manifest. The honest subset (navigation-and-perception, no manipulation) is
  declared, not papered over.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Lower-bound capability.** A Habitat navigation agent is not a full
  manipulator, so the mapped manifest is a deliberate subset (`move_to`, `scan`,
  `detect`, `measure`, `report`, no `grasp` / `release`). This is the honest
  altitude, not a limitation to hide, but it does narrow the demo to navigation
  and perception.
- **Two-repo ambiguity.** habitat-sim (engine) and habitat-lab (tasks) split the
  surface. Anchoring on the engine and folding the lab into one thread risks
  under-serving whichever repo the maintainers consider the real integration
  point; question 3 below asks them to settle it.

## Alternatives considered

1. **Anchor on habitat-lab instead of habitat-sim.** Rejected as the default
   anchor. The engine (habitat-sim) is where the agent's action space and sensor
   suite live, which is what URML's primitives map onto; the lab is the task and
   training layer above it. habitat-lab is named and folded in, and the anchor
   moves if the maintainers say the lab is the right surface.
2. **Two separate RFCs, one per repo.** Rejected. habitat-sim and habitat-lab
   share a maintainer community at facebookresearch; two Issues in a day to one
   org is the pattern that has drawn AI-content closes elsewhere. One anchor
   thread that names both is more respectful and just as discoverable.
3. **Claim a full manipulation manifest for the Habitat agent.** Rejected. It
   would over-promise. The honest-substrate-limit norm (RFC-0014) requires
   declaring the navigation-and-perception subset the agent actually has.

## Prior art

- [RFC-0147 (AI2-THOR outreach)](0147-allenai-ai2thor-outreach.md): the sibling
  embodied-AI simulator engagement (already engaged), the closest precedent for
  a navigation-and-interaction manifest subset.
- [RFC-0234 (Webots outreach)](0234-webots-outreach.md): sibling robot-simulator
  engagement in this lineage.
- Sibling Move #24 RFCs: RFC-0322 (Genesis) and RFC-0323 (Isaac Sim), the other
  simulation and digital-twin targets in this wave.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  honest-substrate-limit norm this RFC applies to the navigation subset.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md):
  the capability and primitive surfaces this engagement exercises.

## Unresolved questions

For the Habitat maintainers:

1. **Agent-action API boundary.** Is "URML intent -> validated primitive ->
   Habitat agent action" the right boundary, with URML producing the agent's
   navigation and sensing actions and staying entirely above the simulator?
2. **Scene / episode-dataset alignment.** Should a URML manifest record the scene
   dataset and the episode goals an agent is bound to (so `declared_locations`
   and `object_vocabulary` stay consistent with the dataset), and is that a
   habitat-sim or a habitat-lab concern?
3. **habitat-sim vs habitat-lab.** Which repo is the right integration surface:
   the engine (habitat-sim) for the action space and sensors, or the task layer
   (habitat-lab) for episodes and goals? Should the engagement stay one thread or
   fork?
4. **License.** What is the current license of habitat-sim and habitat-lab (the
   GitHub API did not surface an SPDX id at verification time; understood to be
   MIT)?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0327 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).
The `habitat-lab` row in the ledger shares this RFC; a dedicated row is added
only if the engagement forks to it.

## How to respond

The live channel is a GitHub Issue on
[`facebookresearch/habitat-sim`](https://github.com/facebookresearch/habitat-sim)
pointing at this RFC (Discussions are disabled on the repo). If the maintainers
prefer habitat-lab or another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (habitat-sim 3,696 stars, not archived, Issues
      enabled, Discussions disabled, last push 2026-05-07; habitat-lab named and
      folded in).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, lower-bound capability, two-repo ambiguity).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (Meta / FAIR); default policy passes at the simulation
      layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Habitat is one
      embodied-AI simulator among many, honest navigation subset declared,
      composed-above not assumed).
