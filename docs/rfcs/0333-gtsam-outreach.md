---
rfc: 0333
title: GTSAM (factor-graph optimization backend) integration, request for comment from the GTSAM maintainers
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

# RFC-0333: GTSAM integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
conceptual touch between URML v0.1 and an existing target's backend, and requests
review from that target's maintainers. It does not modify URML's normative
surface.

## Summary

Move #25 is URML's SLAM and state-estimation wave, round two. This RFC reaches
[`borglab/gtsam`](https://github.com/borglab/gtsam), the factor-graph
optimization backend that many SLAM and state-estimation systems run on, and
**requests review and feedback from the GTSAM maintainers**.

This is the lowest-direct-fit target in the wave, and the RFC is honest about
that up front. URML sits far above GTSAM and does not map onto it directly. URML
benefits indirectly: the pose and graph estimate GTSAM produces ultimately
grounds the `frames` and `declared_locations` URML's Layer-1 manifest declares
over. The factor-graph estimate is a pose source URML consumes; the optimization
internals are Layer 0.

URML composes **above** the systems that use GTSAM, not above GTSAM itself. A
factor-graph optimization yields a pose estimate -> a SLAM or fusion system
exposes that estimate against named frames -> URML validates intent against those
frames and the safety envelope before dispatch. This RFC is an ecosystem and
conceptual touch plus a boundary clarification, not a control mapping.

## Motivation

GTSAM is the optimization engine under a large fraction of modern SLAM and
state-estimation stacks, which makes a boundary clarification with its
maintainers worthwhile even though the direct fit is small:

1. **It grounds URML's frames at a distance.** URML's Layer-1 manifest
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) declares
   `frames` and `declared_locations`. The values those frames carry are produced,
   in many systems, by a GTSAM factor-graph optimization. URML never sees GTSAM;
   it sees the pose estimate a downstream system exposes. Naming that chain is the
   point of the touch.
2. **It is a backend, not an intent layer.** A factor-graph optimization answers
   where the robot and landmarks are, given measurements. URML's contribution is
   one layer up and unrelated to optimization: given the resulting estimate, does
   the declared capability and the safety envelope admit the requested intent
   before the robot moves.
3. **It clarifies a boundary the wave needs drawn.** Several Move #25 targets are
   estimators built on GTSAM. Drawing the line once, with the backend's
   maintainers, keeps the rest of the wave honest: URML consumes a pose source,
   it does not consume or reach into the optimizer that produced it.

Repo at [`borglab/gtsam`](https://github.com/borglab/gtsam) (about 3,499 stars,
Issues and Discussions enabled, not archived, last push 2026-05-29, active).
Maintained by the Georgia Tech Borg Lab (Frank Dellaert). License is asked as a
question below (the GitHub API did not surface an SPDX id at verification time;
understood to be BSD). Origin: United States (Georgia Tech); passes US-federal
default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (conceptual; no in-repo fixture planned)

The mapping is deliberately thin. GTSAM is a math / optimization backend, so the
alignment is at the level of "the estimate GTSAM produces grounds a frame URML
declares," not a field-by-field control mapping.

| URML field | Relation to GTSAM |
|---|---|
| `frames`, `declared_locations` | The pose values these carry may originate, downstream, in a GTSAM factor-graph estimate; URML reads the exposed estimate, never GTSAM directly |
| `frames[].parent` | The transform relationships a SLAM system derives from a GTSAM solution; URML consumes the result, not the graph |
| `perception.sensors[].measurement_type` | The measurements that, in a SLAM system, become factors in a GTSAM graph; declared at URML's altitude as manifest inputs, far above the factors |
| Safety envelope limits (Pass 3) | Unrelated to GTSAM; conjoined strictest-wins against platform limits before dispatch, using the exposed estimate (and its uncertainty, queued below) |

### What URML v0.1 does not yet express for GTSAM

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Localization / pose-source declaration.** URML's manifest does not record
   that its frames are grounded by a named estimate (which, here, a factor-graph
   backend ultimately produces). A future Spec RFC could add an optional
   pose-source declaration, shared with the wave anchor (RFC-0332).
2. **Covariance / quality threshold for the envelope.** A factor-graph solution
   carries an uncertainty. URML's safety envelope has no notion of estimate
   quality. A future Spec RFC could add an optional covariance or quality
   threshold so the envelope can reason about confidence before a primitive
   dispatches.

### Compatibility notes

- **Vendor org.** [`borglab`](https://github.com/borglab) (Georgia Tech Borg Lab,
  Frank Dellaert).
- **Engagement repo.** [`borglab/gtsam`](https://github.com/borglab/gtsam), the
  factor-graph optimization library.
- **Origin / policy.** United States (Georgia Tech). Passes US-federal default
  policy (open-source academic backend, no provenance gate at the optimization
  layer).
- **License fit.** Understood to be BSD; not SPDX-detected at verification time,
  so asked below as a question.
- **Substrate-neutrality.** GTSAM is a backend many estimators share; URML's
  consume-the-estimate posture is independent of which optimizer produced it, so
  the boundary holds on a zero-ROS, zero-GTSAM runtime equally.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The pose-source declaration and the
  covariance / quality threshold are queued Spec RFCs, shared with the wave
  anchor.
- Reference runtime: no change. There is no GTSAM adapter to build; URML consumes
  the estimate a downstream system exposes, not the optimizer. No in-repo fixture
  is planned for GTSAM specifically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Lowest direct fit in the wave.** This is stated plainly: URML does not map
  onto GTSAM, there is no adapter, and no in-repo fixture is planned. The value is
  a boundary clarification and an ecosystem touch, not an integration. URML
  benefits far more from the conceptual clarity than GTSAM benefits from the
  engagement.
- **Indirection.** URML's relation to GTSAM runs through a downstream estimator,
  so the touch is one layer removed. A maintainer could reasonably ask why URML
  reaches them at all; the answer is the boundary clarification the wave needs.

## Alternatives considered

1. **Skip GTSAM and engage only the estimators built on it.** Rejected. The wave
   draws a boundary (URML consumes a pose source, not the optimizer). Naming that
   boundary once with the backend's maintainers keeps the estimator engagements
   honest and avoids implying URML reaches into the solver in any of them.
2. **Claim a direct URML-to-GTSAM mapping.** Rejected. It would over-promise.
   URML has no factor, no graph, no optimization surface; pretending otherwise
   would fail the substrate-neutrality acid test and misrepresent the altitude.
3. **Model the factor graph in the URML manifest.** Rejected. The graph, the
   factors, and the solver are Layer 0. URML declares the frames the resulting
   estimate grounds, not the structure that produced them.

## Prior art

- [RFC-0332 (robot_localization outreach)](0332-robot-localization-outreach.md):
  the Move #25 wave anchor; the pose-source and frame contract this RFC defers to.
- [RFC-0290 (frame-transform graph)](0290-frame-transform-graph.md): URML's frame
  graph, the surface the exposed estimate ultimately grounds.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  the link roles a remote estimate stream may ride.
- Move #16 SLAM upstreams this round extends: [RFC-0205 (Cartographer)](0205-cartographer-outreach.md),
  [RFC-0206 (ORB-SLAM3)](0206-orb-slam3-outreach.md),
  [RFC-0207 (RTAB-Map)](0207-rtabmap-outreach.md),
  [RFC-0211 (Stella VSLAM)](0211-stella-vslam-outreach.md). Several run on GTSAM.
- Sibling Move #25 RFCs: RFC-0334 (OpenVINS), RFC-0335 (KISS-ICP), RFC-0337
  (OctoMap), RFC-0338 (Ceres Solver), RFC-0339 (fuse).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm referenced below.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, where `frames` and `declared_locations` live.

## Unresolved questions

For the GTSAM maintainers:

1. **Sensible alignment, if any.** Is there any sensible alignment between a URML
   frame or localization declaration and a factor-graph estimate's output frames,
   or is the only honest relation "URML consumes the downstream estimate, GTSAM is
   invisible to it"?
2. **Backend-vs-intent boundary.** Is "the factor-graph estimate is a pose source
   URML consumes, the optimization internals are Layer 0" the right boundary
   statement from your side, or does it mischaracterize where GTSAM sits?
3. **Estimate uncertainty.** A factor-graph solution carries uncertainty. Is the
   solution covariance something a downstream consumer like URML could reasonably
   read as a confidence signal, or is that better left to the system that wraps
   GTSAM?
4. **Ecosystem framing.** Is naming GTSAM as the backend several Move #25
   estimators share, while keeping URML strictly above it, a fair and welcome
   framing, or would you prefer the engagement stay with the estimators alone?
5. **License.** What is the current license of GTSAM (the GitHub API did not
   surface an SPDX id at verification time; understood to be BSD)?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0333 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`borglab/gtsam`](https://github.com/borglab/gtsam) pointing at this RFC (the repo
has both enabled). If the maintainers prefer another channel, URML will move the
thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 3,499 stars, not archived, Issues and
      Discussions enabled, last push 2026-05-29).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, lowest direct fit in the wave, indirection).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (Georgia Tech Borg Lab); default policy passes at the
      optimization layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; GTSAM is a backend
      URML never touches directly, the boundary holds on a zero-GTSAM runtime,
      composed-above and honest about the lowest-fit altitude).
