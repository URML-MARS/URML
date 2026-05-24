---
rfc: 0043
title: Boston Dynamics Spot integration, request for comment from boston-dynamics SDK maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-23
updated: 2026-05-23
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

# RFC-0043: Boston Dynamics Spot integration, request for comment from boston-dynamics SDK maintainers

## Summary

URML ships a real `SpotAdapter` in [`reference/legged-runtime/`](../../reference/legged-runtime/) against the `bosdyn` Python gRPC SDK, plus a `spot_quadruped` capability-manifest fixture enabled by [RFC-0009](0009-legged-humanoid-mobility.md). Both are working, hermetically tested artifacts in-repo today. This RFC documents the URML to Spot SDK mapping and requests review and feedback from the Boston Dynamics SDK maintainers. No spec change. Like the engaged Ouster RFC ([RFC-0032](0032-ouster-integration.md)), this is the "we already ship this; please review the mapping" posture rather than a proposal-only ask.

This is a Move #1 follow-on. Move #1 (RFCs 0023-0038) closed at 16 industrial-manipulator and component vendors. Boston Dynamics belongs structurally to that wave (quadruped robot OEM, like the manipulator vendors in 0023-0030) and the legged platform vertical was not yet open then.

## Motivation

Boston Dynamics Spot is the largest publicly available quadruped platform with a stable developer SDK. The Python `bosdyn-*` packages on PyPI are the canonical client surface; the C++ port at `spot-cpp-sdk` (86 stars, 10 open issues, last commit 2026-05-20, default branch `master`) tracks the same API surface for embedded and performance-sensitive deployments. The Spot ecosystem also includes `bosdyn-hospital-bot` (288 stars), `spot-rl-example` (36 stars), and the recent `mjlab` work.

URML's reference adapter family commits to demonstrating substrate-neutrality across legged, humanoid, manipulator, drone, and marine targets. Per [RFC-0009](0009-legged-humanoid-mobility.md), URML now ships reference adapters for legged and humanoid robots: `SpotAdapter` and `AnymalAdapter` in the legged runtime, `DigitAdapter` in the humanoid runtime. Each implements the substrate-neutral `ROSAdapter` Protocol and passes its hermetic suite without a ROS environment. `SpotAdapter` is a load-bearing example because the `bosdyn` gRPC SDK has no ROS dependency: it is URML's second proof, after the PX4 / marine MAVLink work, that the Protocol carries no ROS assumptions.

The integration story is concrete, not aspirational. URML programs targeting Spot today land through `SpotAdapter`, which translates Layer-2 primitives into the right `bosdyn.client.*` calls. The mapping is small enough to review in one sitting and large enough that maintainer feedback measurably improves it.

### A routing note about the outreach surface

URML's `SpotAdapter` targets the **Python** `bosdyn-*` SDK whose canonical home is `boston-dynamics/spot-sdk` (2,484 stars, last commit 2026-05-15). That repository has Issues *disabled* at the repo level (verified via `gh api repos/boston-dynamics/spot-sdk` on 2026-05-23) and Discussions disabled (HTTP 410). URML's outreach pattern across Move #1 (RFCs 0023-0036) has been to file an Issue on the maintainer's primary repository; that surface is closed on Spot's Python SDK.

URML's planned channel is therefore an Issue on `boston-dynamics/spot-cpp-sdk`, which is the most active sibling with Issues enabled and whose maintainers overlap with the Python SDK team. The C++ port mirrors the Python API surface, so the mapping discussion translates cleanly. The RFC asks the maintainers in Q1 below whether this is the right routing or whether another channel (forum, support email, an explicit `enhancement`-tagged Issue on a different sibling) would be preferred.

## Detailed design

URML's existing artifacts that ship today:

- [`reference/legged-runtime/src/urml_legged_runtime/spot.py`](../../reference/legged-runtime/src/urml_legged_runtime/spot.py): `SpotAdapter` plus `SpotConfig`. Lazy `bosdyn` import (constructing requires the `[spot]` extra), credentialed by environment variable name (secrets never live in URML artifacts), full lifecycle with `power_off(cut_immediately=False)` on close.
- [`reference/validator/tests/fixtures/manifests/spot_quadruped.yaml`](../../reference/validator/tests/fixtures/manifests/spot_quadruped.yaml): Spot's capability manifest declaring `mobility.drive_type: quadruped` (per RFC-0009), `max_velocity: 1.6` (Spot's walk-speed cap in m/s), `station_keeping: true` (active balancing, which gates `hover`).
- `conformance/fixtures/quadruped/`: the quadruped conformance fixtures from RFC-0009 (`01_patrol_positive.yaml` runs hermetically against `MockROSAdapter` and against `SpotAdapter` adapter-agnostically).
- [`reference/legged-runtime/README.md`](../../reference/legged-runtime/README.md): the runtime's documentation, including the ANYmal sibling adapter.

### URML primitive to bosdyn SDK mapping

| URML primitive | bosdyn realisation in `SpotAdapter` |
|---|---|
| `move_to(location)` | `GraphNavClient.navigate_to(waypoint_id)` after resolving the manifest's location name to a GraphNav waypoint id via `SpotConfig.location_to_waypoint` |
| `move_to(pose)` | `GraphNavClient.navigate_to_anchor(pose)` |
| `hover` | held stand command via `RobotCommandClient` (Spot actively balances; `station_keeping: true` in the manifest gates this) |
| `dock(station, service)` | `bosdyn.client.docking.dock(station)` |
| `wait(duration)` | `RobotCommandClient.stand(duration_seconds)` (Spot holds station during the wait) |
| `measure(what)` | `RobotStateClient.get_robot_state()` returning battery, e-stop, and related telemetry |
| `wait_for(kind, name, ...)` | robot-state poll against a predicate |
| `report(to, facts, ...)` | structured record to a local sink (no cloud, per URML's manifesto) |
| `scan(area, pattern, ...)` | documented stub success in v0.1 (mirrors `PX4Adapter.run_scan`); waypoint expansion is a follow-up |

Returned not-supported on a bare Spot today (returned, not raised, with brand-scoped tags):

- `grasp` / `release`: Spot Arm is not wired in v0.1. A future RFC covers Spot Arm via the `bosdyn-arm-*` client; pairing Spot + Arm against URML's existing `manipulation` block in the manifest is a follow-up.
- `detect` / `capture`: general off-board perception is not URML's brief on a bare Spot; a vision companion adapter handles this.
- `speak` / `listen`: not present on a bare Spot.
- `take_off` / `land` / `return_to_home`: not applicable.

### Authentication and credentials posture

`SpotConfig` references credentials by environment-variable *name*, not by value. The adapter reads `os.environ` at connect time. Secrets never appear in URML manifests, programs, fixtures, or Git history. This matches URML's broader posture: trust is the most valuable asset, and the easiest to lose, per [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do.

### Conformance integration

`SpotAdapter` ships with hermetic unit tests in `reference/legged-runtime/tests/test_legged_adapters.py` covering delegation, the not-supported sentinels, the conformance hook, `runtime_checkable` Protocol conformance, and context-manager teardown. None of these require a `bosdyn` install. A `legged-integration.yml` CI workflow (the legged sibling of the existing `px4-integration.yml` and `marine-integration.yml`) is the next infrastructure piece, including a `spot-sitl-e2e` against Spot's simulator when available.

### Compatibility notes

- **License.** Boston Dynamics' Spot SDK is released under permissive terms (the Python and C++ SDKs ship under their published Apache-style license; the API itself is documented and stable). URML is Apache 2.0. `SpotAdapter` imports `bosdyn-*` from PyPI exactly the way `PX4Adapter` imports `pymavlink`: lazily, via an installable extra, with a clear actionable error when missing. The maintainers' confirmation of the current license string on `spot-sdk` would help URML pin the wording.
- **Python.** The `bosdyn-*` packages target a modern Python; URML's reference packages target Python 3.10+. No dependency-band friction.
- **Network.** Spot's gRPC client over the robot's WiFi or wired network. `SpotConfig.hostname` defaults to `192.168.80.3`, Spot's documented robot-network default.
- **Substrate-neutrality.** `SpotAdapter` has zero ROS imports. The fact that the same `ROSAdapter` Protocol covers both ROS-native targets (the industrial cluster) and the `bosdyn` non-ROS target is the substrate-neutrality acid test in action.
- **Origin.** Boston Dynamics is incorporated in Massachusetts, US; Spot is US-manufactured. Spot passes URML's bundled US-federal default policy ([RFC-0003](0003-us-alignment.md), [RFC-0004](0004-compliance-policy.md)) without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / manifest schema: none. Spot's deployable surface is covered by `mobility.drive_type: quadruped` (RFC-0009) and the existing v0.1 vocabulary.
- Reference runtime: already shipping (`reference/legged-runtime/`).
- Conformance suite: existing `conformance/fixtures/quadruped/` fixtures cover the v0.1 surface. A `legged-integration.yml` workflow is the next infrastructure piece.

## Backward compatibility

Pre-v1.0. Purely additive: `SpotAdapter` was added in the RFC-0009 work and does not affect any other component. The Boston Dynamics SDK side has no in-repo dependency on URML; `SpotAdapter` consumes `bosdyn-*` exactly the way any third-party Python client would.

## Drawbacks

- **Outreach surface is indirect.** The canonical `spot-sdk` repo has Issues disabled, so this RFC's outreach lands on `spot-cpp-sdk`. The C++ team is adjacent to but not identical with the Python SDK team. The honest framing: this is the best public channel available without a private support relationship, and Q1 below asks the maintainers directly whether a better channel exists.
- **Spot Arm not wired in v0.1.** A bare Spot has no manipulation, so URML returns `not_supported_on_spot: arm (Spot Arm SDK not wired in v0.1)`. Wiring `bosdyn-arm-*` is the obvious next milestone; this RFC documents the gap rather than papering over it. The whole-body / bimanual primitives are tracked at [RFC-0010](0010-whole-body-bimanual-manipulation.md).
- **`scan` is a stub.** Mirrors `PX4Adapter.run_scan`. True patrol-area waypoint expansion + per-waypoint capture is a follow-up RFC.
- **SDK version cadence.** Boston Dynamics ships SDK updates (Spot 3.x, 4.x) and URML's `[spot]` extra needs to track them. The mitigation is the same as for `pymavlink`: depend on a documented major version, pin tests, and update on each SDK release.

## Alternatives considered

1. **File the Issue on `spot-rl-example` or `bosdyn-hospital-bot`.** Rejected. Both have Issues enabled but are more niche than `spot-cpp-sdk`. The C++ port tracks the Python SDK's API surface most closely.
2. **Wait for `spot-sdk` to re-enable Issues.** Rejected. There is no public signal that the maintainers plan to. Sitting on the RFC is worse than posting it where it can be triaged.
3. **Go through `forum.bostondynamics.com` or a private support email.** Rejected as primary, considered as backup. The Move #1 pattern across RFCs 0023-0038 was public-channel outreach; private channels do not produce the same community-visible artifact. The RFC body itself stays in the URML repo regardless of where the outreach Issue lives.
4. **Bundle Spot into a multi-quadruped RFC alongside ANYmal.** Rejected. ANYbotics ANYmal has its own SDK posture and its own US-federal compliance picture (Switzerland-origin); separating the RFCs keeps each maintainer's review surface focused.

## Prior art

- `boston-dynamics/spot-sdk`: the canonical Python SDK home (2,484 stars, last commit 2026-05-15, Issues disabled).
- `boston-dynamics/spot-cpp-sdk`: the C++ port and this RFC's outreach surface (86 stars, 10 open issues, last commit 2026-05-20, `enhancement` and `question` labels both present).
- `boston-dynamics/spot-rl-example`: the Spot RL Research Kit example (36 stars, Issues enabled).
- `boston-dynamics/bosdyn-hospital-bot`: hospital-application resources (288 stars, Issues enabled).
- `boston-dynamics/mjlab`: recent Isaac Lab API powered by MuJoCo-Warp (Issues disabled).
- [RFC-0009](0009-legged-humanoid-mobility.md): added `quadruped` and `biped` to `mobility.drive_type`; the schema precedent that unblocked SpotAdapter's manifest.
- [RFC-0010](0010-whole-body-bimanual-manipulation.md): whole-body and bimanual manipulation (Draft), the future home of Spot Arm primitives.
- [RFC-0032](0032-ouster-integration.md): the engaged outreach RFC and structural template for "we already ship this; please review."
- RFCs 0023-0038: the Move #1 outreach pattern this RFC inherits.

## Unresolved questions

Provisional pending Boston Dynamics SDK maintainer feedback:

1. **Outreach routing.** Is filing this Issue on `spot-cpp-sdk` the right channel, or would the maintainers prefer a different surface (a specific tag on `spot-rl-example`, a forum thread on `forum.bostondynamics.com`, a private support ticket cross-linked to a public note)? Confirming the canonical channel for SDK proposals would also help future URML follow-ons.
2. **Spot Arm SDK integration.** URML returns `not_supported_on_spot: arm` today. What is the recommended path for wiring `bosdyn-arm-*` into an adapter that also drives the base via `bosdyn-graph-nav-*`? The whole-body / bimanual primitives are tracked at [RFC-0010](0010-whole-body-bimanual-manipulation.md); maintainer guidance there would feed into both.
3. **License pinning.** `gh api repos/boston-dynamics/spot-cpp-sdk` returns `license: NOASSERTION` because GitHub does not resolve the SPDX. What is the current license string URML should cite in the RFC and in the `[spot]` extra's documentation? The Spot SDK's published license appears to be permissive in the Apache-2.0 family but URML should pin the exact name.
4. **Mission / Orbit integration.** URML's `move_to(location)` resolves a manifest-declared location to a GraphNav waypoint via `SpotConfig.location_to_waypoint`. For deployments that use Mission Editor / Orbit, is there a recommended bridge from URML's named locations to Mission's waypoint identifiers, or should that remain a deployment concern outside URML?
5. **Spot 4.x cadence and breaking changes.** What is the maintainers' guidance on tracking Spot SDK majors? URML's adapter pinning strategy is the same as for `pymavlink`: depend on a documented major, pin tests, update on each release. Any heads-up on near-term breaking changes that affect the mapped surface would help.
6. **Conformance lane interest.** Would Boston Dynamics be open to a downstream link from one of the Spot SDK repositories' READMEs or wiki to URML's conformance run for any URML program validated against a Spot deployment, similar to existing third-party SDK references?
7. **Anything else.** Anything URML's current SpotAdapter gets wrong about the `bosdyn` SDK's intended use, before the legged runtime gains further coverage.

## Implementation note

RFC-0043 ships as a single RFC document PR. No adapter code change in this PR (`SpotAdapter` has been shipping since RFC-0009's PR). Future work: a `legged-integration.yml` CI workflow, wiring `bosdyn-arm-*` for the Spot Arm path, and the real `scan` implementation. Ledger entry under [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml) (Move #1 substrate follow-on placed in the Move #2 file, since the Move #1 file is parity-tested against the demo runner).

## Requested feedback (from boston-dynamics SDK maintainers)

1. Outreach routing: is `spot-cpp-sdk` the right Issue surface for a Python-SDK proposal, or should this move? (Q1)
2. Spot Arm SDK integration path (Q2).
3. License string to pin (Q3).
4. Mission / Orbit waypoint-identifier bridging guidance (Q4).
5. Spot SDK major-version cadence and any near-term breaking changes (Q5).
6. Downstream wiki / README link interest (Q6).
7. Anything URML's `SpotAdapter` gets wrong about `bosdyn` usage today.
8. Anything else.

## How to respond

The `boston-dynamics/spot-cpp-sdk` repository accepts public Issues. Both `enhancement` and `question` labels exist (verified via `gh api repos/boston-dynamics/spot-cpp-sdk/labels` on 2026-05-23); `enhancement` is the closer fit for a mapping-review RFC of this kind. `boston-dynamics/spot-sdk` itself has Issues and Discussions disabled.

URML's planned channel: open a single Issue on `boston-dynamics/spot-cpp-sdk` labelled `enhancement`, pointing to this RFC. If the maintainers redirect to a different surface in response to Q1, URML moves the thread there.

URML's own public Discussions for the broader conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that the adapter is real shipping work, not proposal-only).
- [x] Motivation grounded in verified data (spot-sdk 2,484 stars Issues disabled, spot-cpp-sdk 86 stars 10 open issues, `enhancement` and `question` labels confirmed), not boilerplate.
- [x] Detailed design names every affected component (`SpotAdapter`, `spot_quadruped` manifest, RFC-0009 quadruped fixtures) with verified file paths.
- [x] At least one alternative considered (four are).
- [x] Drawbacks are real (indirect outreach surface, Spot Arm gap, `scan` stub, SDK cadence).
- [x] Backward compatibility: purely additive, adapter has been shipping since RFC-0009.
- [x] No Layer-2 primitive added. The mapping uses existing v0.1 vocabulary.
- [x] Implementation note honest about what ships in this PR (RFC document only) versus what is follow-up (CI workflow, Spot Arm wiring, real scan).
- [x] Surface ("How to respond") is verified: `spot-cpp-sdk` Issues open, labels confirmed, the canonical `spot-sdk` Issues-disabled fact recorded with a verifiable command for the next maintainer who checks.
- [x] Routing reality flagged honestly in §Motivation rather than hidden.
- [x] No em-dashes in the RFC body, no formulaic structure, voice consistent with RFC-0040 / RFC-0041 / RFC-0042.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency (the `report` sink is local; the manifesto bars cloud in reference runtimes). No telemetry. Credentials handled by env-var-name indirection, never stored.
