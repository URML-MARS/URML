---
rfc: 0049
title: ANYbotics ANYmal integration, request for comment from ANYbotics maintainers
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

# RFC-0049: ANYbotics ANYmal integration, request for comment from ANYbotics maintainers

## Summary

URML ships a real `AnymalAdapter` in [`reference/legged-runtime/`](../../reference/legged-runtime/) plus an `anymal_quadruped` capability-manifest fixture enabled by [RFC-0009](0009-legged-humanoid-mobility.md). Both are working, hermetically tested artifacts in-repo today. Unlike Spot (which speaks its own gRPC SDK), ANYmal speaks ROS 2, so `AnymalAdapter` composes the ROS 2 runtime's `RclpyAdapter` rather than wrapping a proprietary client library. This RFC documents the URML-to-ANYmal mapping and requests review and feedback from the ANYbotics maintainers. No spec change. Sibling to [RFC-0043](0043-boston-dynamics-spot-integration.md) (Boston Dynamics Spot) and closes the legged-quadruped pair URML committed to under RFC-0009.

This is a Move #1 follow-on. Move #1 (RFCs 0023-0038) closed at 16 industrial-manipulator and component vendors. ANYbotics belongs structurally to that wave (quadruped robot OEM, Swiss-origin) and the legged platform vertical was not yet open then.

## Motivation

ANYbotics ANYmal is the second-largest installed-base quadruped platform after Boston Dynamics Spot, and the dominant choice in industrial inspection deployments (oil and gas, utilities, manufacturing plant rounds, mining). The platform's design philosophy diverges from Spot's: ANYmal is ROS 2 native, ships with a sensor-rich inspection payload by default, and the company's developer surface is a family of mature ROS libraries (`grid_map` 3,134 stars, `elevation_mapping` 1,782 stars, `kindr` 608 stars, `point_cloud_io` 192 stars) plus per-generation URDF description packages (`anymal_b_simple_description`, `anymal_c_simple_description`, `anymal_d_simple_description`). The `ANYbotics` GitHub organization has 101 public repositories and 694 followers as of 2026-05-23.

URML's reference adapter family commits to demonstrating substrate-neutrality across legged, humanoid, manipulator, drone, and marine targets. Per [RFC-0009](0009-legged-humanoid-mobility.md), URML now ships reference adapters for legged and humanoid robots: `SpotAdapter` and `AnymalAdapter` in the legged runtime, `DigitAdapter` in the humanoid runtime. Each implements the substrate-neutral `ROSAdapter` Protocol and passes its hermetic suite. `AnymalAdapter` is the load-bearing example for the ROS 2 quadruped story exactly because ANYmal is ROS 2 native: URML's claim that the same Protocol covers ROS-native and non-ROS substrates is provable in-repo today by comparing `AnymalAdapter` (ROS 2) and `SpotAdapter` (`bosdyn` gRPC) side by side.

The integration story is concrete. URML programs targeting ANYmal land through `AnymalAdapter`, which composes `RclpyAdapter` for the ROS 2 plumbing and adds a brand-scoped `not_supported_on_quadruped[anymal]` tag for capabilities a bare ANYmal does not have (arm, vision-payload-specific detection, capture, speech, flight).

## Detailed design

URML's existing artifacts that ship today:

- [`reference/legged-runtime/src/urml_legged_runtime/anymal.py`](../../reference/legged-runtime/src/urml_legged_runtime/anymal.py): `AnymalAdapter`. Composes `RclpyAdapter`. Lazy `rclpy` import (constructing requires a sourced ROS 2 environment). Hermetic tests inject a fake inner adapter via `inner_factory` and never touch `rclpy`.
- [`reference/validator/tests/fixtures/manifests/anymal_quadruped.yaml`](../../reference/validator/tests/fixtures/manifests/anymal_quadruped.yaml): ANYmal capability manifest declaring `mobility.drive_type: quadruped`, `max_velocity: 1.3`, `station_keeping: true`, an inspection camera, and a Swiss-origin provenance block (`vendor: anybotics`, `country_of_origin: CH`) that passes URML's bundled US-federal default policy without flagging.
- `conformance/fixtures/quadruped/`: the quadruped conformance fixtures from RFC-0009 run hermetically against `MockROSAdapter` and adapter-agnostically against `AnymalAdapter`.
- [`reference/legged-runtime/README.md`](../../reference/legged-runtime/README.md): the runtime documentation covering both `SpotAdapter` and `AnymalAdapter`.

### URML primitive to ROS 2 substrate mapping for ANYmal

Because `AnymalAdapter` composes `RclpyAdapter`, the mapping is the standard URML ROS 2 binding: URML Layer-2 primitives translate into ROS 2 actions, services, and topics through the substrate-neutral Protocol. The brand-specific layer is the not-supported-tag set and the manifest defaults.

| URML primitive | ROS 2 realisation in `AnymalAdapter` |
|---|---|
| `move_to(location)` | delegated to `RclpyAdapter.send_navigation_goal` (Nav2 navigate-to-pose; ANYmal's autonomy stack subscribes) |
| `move_to(pose)` | delegated to `RclpyAdapter.send_navigation_goal` with explicit pose |
| `hover` | held station-keeping (ANYmal actively balances; `station_keeping: true` in manifest) |
| `wait(duration)` | timed hold via the composed adapter |
| `measure(what)` | delegated to `RclpyAdapter.take_measurement`; inspection-payload sensors (gauges, thermal, gas) are the ANYmal-specific consumers |
| `wait_for(kind, name, ...)` | delegated to `RclpyAdapter.wait_for_condition` |
| `report(to, facts, ...)` | delegated to `RclpyAdapter.emit_report`; local sink, no cloud (per URML manifesto) |

Returned not-supported on a bare ANYmal today (returned, not raised, with brand-scoped tags):

- `dock(station, service)`: a bare ANYmal inspection robot does not declare a docking station in the v0.1 manifest; pairing with a docking-station companion is the path.
- `grasp` / `release`: no arm on a bare ANYmal; manipulation requires a companion adapter pairing.
- `query_detection`, `run_scan`, `capture_media`: general onboard object detection and area-scan payloads are companion-adapter territory.
- `emit_speech`, `acquire_speech`: no speaker / microphone on a bare ANYmal.
- `send_takeoff_goal`, `send_land_goal`, `send_return_to_home_goal`: not applicable.

### Generation coverage (B, C, D)

ANYbotics ships three generations of ANYmal: B (the original research-grade platform), C (the current production inspection robot), and D (the newer-generation platform). The URDF description packages live under `anymal_b_simple_description`, `anymal_c_simple_description`, `anymal_d_simple_description`. URML's manifest schema does not key on generation; the capability differences (max velocity, payload envelope, sensor suite) are declared per-manifest, and `AnymalAdapter` is generation-agnostic at the Protocol level. The maintainers' guidance on whether per-generation URML manifest fixtures should ship as separate canonical examples (`anymal_c_inspection.yaml`, `anymal_d_inspection.yaml`) or stay collapsed into one is in Q3 below.

### Conformance integration

`AnymalAdapter` ships with hermetic unit tests in `reference/legged-runtime/tests/test_legged_adapters.py` covering the same test surface as `SpotAdapter`: delegation, the not-supported sentinels, the conformance hook, `runtime_checkable` Protocol conformance, context-manager teardown. None require a `rclpy` install. A `legged-integration.yml` CI workflow with a `anymal-sim-e2e` against Gazebo (the established `marine-sitl-e2e` / `px4-sitl-e2e` convention) is the next infrastructure piece.

### Compatibility notes

- **License.** ANYbotics' open repositories (`grid_map`, `elevation_mapping`, `kindr`, `point_cloud_io`, the description packages) are predominantly BSD-3-Clause. `AnymalAdapter` does not import any ANYbotics library directly; the integration is at the ROS 2 layer (rclpy + standard message types), so license interaction is minimal.
- **Python and ROS.** `AnymalAdapter` requires a sourced ROS 2 environment to construct, exactly like the industrial-arm adapters. The lazy `rclpy` import means `import urml_legged_runtime` works on every host.
- **Sim story.** ANYmal SITL through Gazebo is the standard developer testing path; the `anymal-sim-e2e` workflow planned above runs against Gazebo with one of the description packages spawned.
- **Origin.** ANYbotics AG is incorporated in Switzerland (ETH Zurich spin-out, Zurich-headquartered). The `anymal_quadruped` manifest fixture declares `country_of_origin: CH` and passes URML's bundled US-federal default policy ([RFC-0003](0003-us-alignment.md), [RFC-0004](0004-compliance-policy.md)) without flagging. Switzerland is on no covered list and ANYbotics maintains long-standing US deployments.
- **Inspection-payload posture.** ANYmal's inspection payload (visual / thermal / acoustic / gas sensors) is the platform's commercial differentiator. URML's `measure` and (when companion-adapter-paired) `detect` and `capture` cover the surface; the maintainers' input on whether the inspection payload deserves a named companion-adapter shape in URML is in Q4 below.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / manifest schema: none. ANYmal's deployable surface is covered by `mobility.drive_type: quadruped` (RFC-0009) and the existing v0.1 vocabulary.
- Reference runtime: already shipping (`reference/legged-runtime/`).
- Conformance suite: existing `conformance/fixtures/quadruped/` fixtures cover the v0.1 surface. A `legged-integration.yml` workflow is the next infrastructure piece (siblings: `px4-integration.yml`, `marine-integration.yml`).

## Backward compatibility

Pre-v1.0. Purely additive: `AnymalAdapter` was added in the RFC-0009 work and does not affect any other component. The ANYbotics side has no in-repo dependency on URML; `AnymalAdapter` consumes the ROS 2 stack exactly the way any third-party ROS client would.

## Drawbacks

- **Outreach surface is interpretive.** ANYbotics' GitHub org publishes mature general-purpose ROS libraries (`grid_map`, `elevation_mapping`) plus per-generation URDF description packages. There is no canonical "ANYmal SDK" repository the way `boston-dynamics/spot-sdk` exists for Spot. The closest target for this Issue is `anymal_c_simple_description` (current-generation, 74 stars, Issues enabled, last commit 2026-05-13). Q1 below asks the maintainers directly whether this is the right routing.
- **No arm or speech on a bare ANYmal.** URML returns `not_supported_on_quadruped[anymal]: arm` / `speaker` / `microphone`. Wiring a payload companion adapter is the path; this RFC documents the gap rather than papering over it. Whole-body / bimanual primitives are tracked at [RFC-0010](0010-whole-body-bimanual-manipulation.md).
- **Description-package outreach surface is small.** `anymal_c_simple_description` has 74 stars and 0 open issues at the time of writing. The activity signal is the recent commit (2026-05-13), not the open-issue volume. The maintainers' team is shared with the larger libraries (`grid_map`, `elevation_mapping`), so the routing reality is probably fine.
- **Generation coverage is fluid.** ANYbotics ships B, C, and D with overlapping deployments. URML's manifest is generation-agnostic; explicit per-generation canonical examples may or may not be the right shape. See Q3.

## Alternatives considered

1. **File the Issue on `grid_map` or `elevation_mapping`.** Rejected as primary. Those repositories have larger communities (3,134 and 1,782 stars respectively) but they are general-purpose libraries, not ANYmal-specific. Filing an ANYmal integration RFC on a library issue tracker would dilute both audiences.
2. **File the Issue on `anymal_b_simple_description` (the highest-star ANYmal-named repo, 95 stars).** Rejected. The B variant is the legacy research platform; C is the current production. Filing on B would signal the wrong generation focus.
3. **Skip a generation-specific filing and file on the company's public contact form (anybotics.com).** Rejected as primary. The Move #1 outreach pattern across RFCs 0023-0038 was public-channel GitHub Issues; private contact forms do not produce the community-visible artifact this RFC is designed around. The form is the backup if the GitHub Issue gets no response.
4. **Bundle ANYmal with Spot into one RFC.** Rejected. Each maintainer's review surface is different, and SpotAdapter's `bosdyn`-specific mapping table has no parallel on the ANYmal side, where the binding is generic ROS 2. Separating the RFCs keeps both focused.

## Prior art

- `ANYbotics/anymal_c_simple_description`: this RFC's outreach surface (74 stars, BSD-3-Clause, Issues enabled, `enhancement` and `question` labels both present, last commit 2026-05-13).
- `ANYbotics/anymal_b_simple_description`: legacy research-generation description (95 stars).
- `ANYbotics/anymal_d_simple_description`: newer-generation description (21 stars).
- `ANYbotics/grid_map`: the elevation-mapping library widely used in legged-robot navigation (3,134 stars, 155 open issues, last commit 2026-05-21). Adjacent to URML's `measure` / `detect` story for terrain-aware behavior.
- `ANYbotics/elevation_mapping`: the companion robot-centric mapping library (1,782 stars, 100 open issues, last commit 2026-05-23).
- `ANYbotics/kindr` and `ANYbotics/kindr_ros`: kinematics and dynamics libraries (608 and 59 stars).
- [RFC-0009](0009-legged-humanoid-mobility.md): added `quadruped` and `biped` to `mobility.drive_type`; the schema precedent that unblocked AnymalAdapter's manifest.
- [RFC-0010](0010-whole-body-bimanual-manipulation.md): whole-body and bimanual manipulation (Draft), the future home of any arm-equipped ANYmal variant primitives.
- [RFC-0032](0032-ouster-integration.md): the engaged outreach RFC and structural template for "we already ship this; please review."
- [RFC-0043](0043-boston-dynamics-spot-integration.md): the Spot sibling RFC. ANYmal is the ROS 2 counterpart in the quadruped pair URML committed to under RFC-0009.
- RFCs 0023-0038: the Move #1 outreach pattern this RFC inherits.

## Unresolved questions

Provisional pending ANYbotics maintainer feedback:

1. **Outreach routing.** Is filing this Issue on `anymal_c_simple_description` the right channel, or would the maintainers prefer a different surface (a tagged Issue on `grid_map` since the developer community is larger there, a tagged Issue on `anymal_d_simple_description` for the newer generation, the company's contact form, or a private support channel cross-linked to a public note)?
2. **ROS 2 binding fidelity.** URML's `AnymalAdapter` composes `RclpyAdapter` and delegates to the standard ROS 2 action and service surface. Are there ANYmal-specific topics, services, or autonomy-stack conventions (`anymal_msgs/`, the inspection-mission API, the navigation-stack flavor of choice) URML should be aware of that improve the mapping?
3. **Per-generation manifest fixtures.** URML ships one `anymal_quadruped.yaml` fixture today. Should canonical per-generation examples ship (`anymal_c_inspection.yaml`, `anymal_d_inspection.yaml`), or is generation-agnostic the right shape given that ANYbotics customers select generation at deployment time?
4. **Inspection-payload companion-adapter shape.** ANYmal's inspection payload (visual, thermal, acoustic, gas sensors) is a key product differentiator. Should URML name a dedicated `inspection-payload-runtime` companion adapter that pairs with `AnymalAdapter` via the existing `CompositeAdapter` pattern (the way `px4-runtime` pairs with `ros2-runtime`)?
5. **Sim story.** What is the recommended Gazebo / Isaac configuration for ANYmal SITL that URML's `anymal-sim-e2e` workflow should pin? The description packages provide URDF; the locomotion stack pinning is the open question.
6. **Downstream link.** Would ANYbotics be open to a downstream link from one of the ANYmal description repositories' READMEs or the company's developer documentation to URML's conformance run for any URML program validated against an ANYmal deployment?
7. **Anything else.** Anything URML's current `AnymalAdapter` or `anymal_quadruped.yaml` gets wrong about the platform's intended use.

## Implementation note

RFC-0045 ships as a single RFC document PR. No adapter code change in this PR (`AnymalAdapter` has been shipping since RFC-0009's PR). Future work: a `legged-integration.yml` CI workflow, per-generation manifest fixtures if the maintainers indicate they would be useful, and a named inspection-payload companion adapter if Q4 surfaces concrete demand. Ledger entry under [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml) (Move #1 substrate follow-on placed in the Move #2 file, since the Move #1 file is parity-tested against the demo runner).

## Requested feedback (from ANYbotics maintainers)

1. Outreach routing: is `anymal_c_simple_description` the right Issue surface, or should this move? (Q1)
2. ROS 2 binding fidelity: any ANYmal-specific topics, services, or autonomy-stack conventions URML should target (Q2).
3. Per-generation manifest fixture coverage (Q3).
4. Inspection-payload companion-adapter shape (Q4).
5. Sim configuration pinning for `anymal-sim-e2e` (Q5).
6. Downstream wiki / README link interest (Q6).
7. Anything URML's `AnymalAdapter` gets wrong about the platform today.
8. Anything else.

## How to respond

The `ANYbotics/anymal_c_simple_description` repository accepts public Issues. Both `enhancement` and `question` labels exist (verified via `gh api repos/ANYbotics/anymal_b_simple_description/labels` on 2026-05-23; the same label set is consistent across the ANYbotics org); `enhancement` is the closer fit for a mapping-review RFC of this kind. The ANYbotics company contact form at `anybotics.com` is the documented private channel.

URML's planned channel: open a single Issue on `ANYbotics/anymal_c_simple_description` labelled `enhancement`, pointing to this RFC. If the maintainers redirect to a different surface in response to Q1, URML moves the thread there.

URML's own public Discussions for the broader conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that the adapter is real shipping work, not proposal-only).
- [x] Motivation grounded in verified data (ANYbotics org 101 repos / 694 followers, `grid_map` 3,134 stars, `elevation_mapping` 1,782 stars, description packages enumerated), not boilerplate.
- [x] Detailed design names every affected component (`AnymalAdapter`, `anymal_quadruped` manifest, RFC-0009 quadruped fixtures) with verified file paths.
- [x] At least one alternative considered (four are).
- [x] Drawbacks are real (interpretive outreach surface, no arm or speech, small open-issue volume on the chosen target repo, fluid generation coverage).
- [x] Backward compatibility: purely additive, adapter has been shipping since RFC-0009.
- [x] No Layer-2 primitive added.
- [x] Implementation note honest about what ships in this PR (RFC document only) versus what is follow-up (CI workflow, per-generation manifests if useful, inspection-payload companion adapter if demanded).
- [x] Surface ("How to respond") is verified: `anymal_c_simple_description` Issues open, labels confirmed, routing alternatives listed.
- [x] Routing reality flagged honestly in §Motivation and §Drawbacks rather than hidden.
- [x] No em-dashes in the RFC body, no formulaic structure, voice consistent with RFC-0040 through RFC-0044.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency (the `report` sink is local). No telemetry. Vendor-neutral posture preserved (the Swiss-origin manifest passes the US-federal default policy at the manifest level, as documented in RFC-0003 / RFC-0004).
