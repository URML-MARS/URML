---
rfc: 0013
title: Industrial-profile Layer-2 primitives — pick_from, place_at, swap_tool
author: Ido Yahalomi (ido@jacob-ai.com)
state: Draft
created: 2026-05-19
updated: 2026-05-19
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

# RFC-0013: Industrial-profile Layer-2 primitives — `pick_from`, `place_at`, `swap_tool`

## Summary

Promote the three industrial-profile primitives from "preview" prose in
[`spec/profiles/industrial/README.md`](../../spec/profiles/industrial/README.md)
to a specified, validated, runnable surface: `pick_from`, `place_at`, and
`swap_tool`. This adds three pydantic arg models, three Pass-2 capability
checks, three ROS-2 reference executors, conformance fixtures, and a runnable
example. It adds **no new substrate Protocol method**: `pick_from`/`place_at`
compose existing adapter calls, and `swap_tool` dispatches through the existing
`send_docking_goal` station-service mechanism. [RFC-0002](0002-initial-primitive-vocabulary.md)
§Design-Principles already authorizes these three by name; this RFC
operationalizes them.

## Motivation

The industrial profile is the one named URML profile shipped as a skeleton. Its
three Layer-2 primitives exist only as a "Signature (preview…)" block in the
profile README; they are absent from the validator schema, absent from every
runtime executor, and absent from conformance. The single industrial
conformance fixture (`conformance/fixtures/industrial/01_pick_red_positive.yaml`)
fakes the canonical pick-and-place with a `move_to + detect + grasp + move_to +
release` composition. A line integrator who reads "industrial profile" and
writes `pick_from:` gets an unknown-primitive rejection.

This is the high-value gap for the manufacturer and federal-procurement
audience the project is actively courting. The line-reconfiguration scenario in
[`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios — *"same as before,
but pick red instead of blue"* — is an industrial-profile story; it should run.

Why these are primitives and not left as composition: the argument already
stated in the profile README applies and is adopted here verbatim. A user
*could* write `move_to(source) + detect(object) + grasp($target)`. The profile
adds `pick_from` because (a) the composition is so frequent that the primitive
removes visible repetition from every industrial program, and (b) industrial
substrates routinely expose a single atomic "pick at station" operation (a
configured PLC sequence, an OPC UA station-service method) that maps cleanly to
one primitive rather than three. The existing
`examples/industrial/simple-pick-and-place.urml.yaml` is **retained unchanged**
as the documented composition-equivalent, so the macro-vs-primitive trade-off
stays visible per CLAUDE.md's "prefer composition" principle.

## Detailed design

### Spec changes

- **Layer-2** ([`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)):
  add §3.6 `pick_from`, §3.7 `place_at`, §3.8 `swap_tool`, profile-scoped to
  industrial, in the same subsection house style as `speak`/`take_off`
  (signature, semantics, capability requirements, safety-envelope checks,
  variable bindings, substrate sketches). Update the profile-scoped count
  (five → eight).
- **Industrial profile** ([`spec/profiles/industrial/README.md`](../../spec/profiles/industrial/README.md)):
  promote the three "Signature (preview…)" blocks to normative; reconcile the
  "Conformance points … (not yet created)" section with the now-existing
  fixtures.

Signatures (now normative; unchanged from the README preview):

```yaml
- pick_from:
    source: <station_name>           # required; resolved against declared_locations
    object: <class>                  # required; resolved against object_vocabulary
    attributes: { color: red, ... }  # optional; same shape as detect.attributes
    force: gentle | firm | <newtons> # optional; default per gripper
    store_as: <name>                 # required if subsequent steps reference $name

- place_at:
    target: <station_name>           # required
    held: $name                      # required; the object held (from a prior pick_from/detect)
    mode: place | drop               # optional; default: place
    height: <distance>               # optional; advisory in v0.1 (see Unresolved questions)

- swap_tool:
    at: <station_name>               # required; the station must declare a `swap_tool` service
    to: <tool_name>                  # required; the tool to mount
```

### Validator changes

- Three pydantic arg models in `reference/validator/src/urml_validator/schemas/primitives.py`
  (`PickFromArgs`, `PlaceAtArgs`, `SwapToolArgs`), registered in
  `PRIMITIVE_NAMES` and `PRIMITIVE_MODELS`; the same three names added to
  `_PRIMITIVE_NAMES_FROZEN` in `validator.py` (pydantic-error path
  attribution). `extra="forbid"` like every sibling model.
- Three Pass-2 capability checks wired into the `_check_capabilities`
  dispatch, reusing existing helpers (no new `ErrorCode` values):
  - `_check_pick_from_caps`: requires `mobility` (reuses the `move_to` mobility
    check), `source` ∈ `declared_locations` (`_location_declared` →
    `CAPABILITY_MISSING_LOCATION`), `perception` with a camera/sensor and
    `object` ∈ `perception.object_vocabulary`
    (`CAPABILITY_MISSING_PERCEPTION` / `CAPABILITY_MISSING_OBJECT_CLASS`),
    `manipulation` with a gripper covering the requested force
    (`_resolve_force` + `_gripper_in_range` → `CAPABILITY_MISSING_MANIPULATION`
    / `CAPABILITY_MISSING_GRIPPER`).
  - `_check_place_at_caps`: requires `mobility`, `target` ∈
    `declared_locations`, and `manipulation` with a gripper (mirrors
    `_check_release_caps` + the location check).
  - `_check_swap_tool_caps`: mirrors `_check_dock_caps` but **requires an
    explicit `at`** (no default-station fallback): the named station must be
    in `manifest.docking_stations` (`CAPABILITY_MISSING_DOCKING_STATION`) and
    must declare the `swap_tool` service (`CAPABILITY_MISSING_DOCKING_SERVICE`).
- Variable bindings: `pick_from` is registered as a producer of type
  `"object"` (the same tag `detect` produces, so `$ref.field` and downstream
  `{"object"}` consumers interoperate). `place_at.held` is registered as an
  `{"object"}`-typed consumer in `_references_used_with_type`. `place_at` and
  `swap_tool` produce no binding (no `store_as`).

### Reference runtime changes

`reference/ros2-runtime/src/urml_ros2_runtime/primitives.py` gains three
executors, registered in `PRIMITIVE_EXECUTORS`. **No `substrate/` file
changes** — every call below already exists on the `ROSAdapter` Protocol and
on every adapter implementation:

- `exec_pick_from`: `send_navigation_goal(location=source)` →
  `query_detection(object_class, attributes, where_near=source)` →
  `send_manipulation_goal(action="grasp", target=<detection payload>,
  force_n=_force_newtons(force), approach="auto")`; if `store_as`, binds the
  detection payload (identical shape to `detect`).
- `exec_place_at`: `resolve(held)` → `send_navigation_goal(location=target,
  carrying=<held dict>)` → `send_manipulation_goal(action="release",
  release_mode=mode, release_at=target)`.
- `exec_swap_tool`: `send_docking_goal(station=at, service="swap_tool",
  until=to)`.

That zero-adapter-churn property is the substrate-neutrality result, not an
accident — see the acid-test section below. Non-ROS reference runtimes
(`px4-runtime`, `industrial-arm-runtime`, etc.) require **no change** and their
suites must stay green; that is the proof.

### Conformance suite changes

`conformance/fixtures/industrial/` gains (auto-discovered, no registry edit):

- `04_pick_from_positive.yaml` — `wait_for(safety_door_closed)` then
  `pick_from` → `place_at` → `report`, against the `industrial_cell` manifest;
  asserts `success`, `steps_executed`, the exact `audit_methods` order, and
  `bindings_contains.red_widget.class == widget_red`.
- `05_swap_tool_positive.yaml` — `swap_tool(at: tool_change_station, to:
  gripper_wide)`; asserts `audit_methods: [send_docking_goal]` (pins the
  decision: swap_tool rides docking).
- `06_swap_tool_undeclared_service_rejected.yaml` — negative; `swap_tool` at a
  location that is not a docking station → `expected_validation.accepted:
  false` with `capability.missing_docking_station`.

The manifest fixture `reference/validator/tests/fixtures/manifests/industrial_cell.yaml`
gains one `docking_stations` entry (`tool_change_station`, services
`[swap_tool, park]`); its empty `docking_stations: []` is replaced.
`industrial_cell_connectivity.yaml` is left unchanged so its negative fixture
keeps failing on the link rule, not on a newly-present station.

A new `examples/industrial/pick-place-tool-change.{urml.yaml,manifest.yaml,en.txt,ja.txt}`
exercises all three primitives end to end with a US-compliant provenance block
(so RFC-0004 Pass 5 accepts it). `simple-pick-and-place.*` is untouched.

### Substrate-neutrality acid test (RFC-0001 mandatory item)

- **`pick_from`** — ROS 2: Nav2 navigate + perception query + MoveIt 2 grasp,
  composed in the executor (or a single station-controller action when one
  exists). Non-ROS: OPC UA Robotics `Manipulation.PickFrom(station, object)`;
  PLC + EtherNet/IP vendor pick-at-station function block.
- **`place_at`** — ROS 2: Nav2 navigate(carrying) + MoveIt 2 release with
  place/drop mode. Non-ROS: OPC UA `Manipulation.PlaceAt(station)`; PLC
  place-at-station function block.
- **`swap_tool`** — ROS 2: a tool-change action behind the station's
  `swap_tool` service, dispatched through the existing `send_docking_goal`.
  Non-ROS: OPC UA `ToolChanger.ChangeTo(tool)` exposed as the station service;
  PLC tool-change function block. Flight substrates (PX4) legitimately do not
  implement tool change — and need no code change, because the dispatch verb
  (`send_docking_goal`) already exists everywhere and a flight adapter already
  answers it per its own capabilities.

## Backward compatibility

Purely additive and pre-v1.0. No existing primitive, schema, fixture, example,
or runtime behavior changes. Programs valid before remain valid;
`simple-pick-and-place.urml.yaml` (the composition form) keeps working
unchanged. No `ErrorCode` is renamed or removed; the three new checks reuse
existing capability codes.

## Drawbacks

1. **`until` overload.** `swap_tool` reuses `send_docking_goal(station, service,
   until)` and passes the target tool name in `until`, a field whose name
   suggests a completion condition. This is documented in `exec_swap_tool`'s
   docstring and asserted by conformance (the logged call carries
   `service: swap_tool`, `until: <tool>`). A future RFC may add a typed
   `payload` to `send_docking_goal`; see Unresolved questions.
2. **`accepted_tools` deferred.** The profile spec marks the per-station
   `accepted_tools` manifest field as deferred. So `swap_tool` validation
   checks only that the station declares the `swap_tool` service, not that
   `to:` is an accepted tool. A program naming a nonexistent tool validates and
   fails (or no-ops) at the substrate. This mirrors other v0.1 primitives'
   deferred sub-checks and is called out as a v0.1 limitation, not hidden.
3. **One more primitive surface to teach.** Three new verbs the LLM bridge,
   docs, and integrators must learn. Mitigated by the strong frequency
   argument and by keeping the composition example as the teaching contrast.
4. **`place_at.height` is advisory.** The substrate `send_manipulation_goal`
   has no height parameter; threading one through would force the exact
   cross-adapter churn this RFC avoids. `height` is accepted and
   schema-validated but not enacted in v0.1.

## Alternatives considered

- **No primitives; keep composing.** Rejected: the composition is the single
  most frequent industrial pattern, and the profile already commits to these
  three by name in RFC-0002. The composition example is retained so the
  trade-off remains inspectable rather than erased.
- **`swap_tool` as a new `send_tool_change_goal()` Protocol method.** The
  genuine, non-strawman alternative. Rejected: it touches `substrate/base.py`
  plus every adapter (`mock`, `rclpy`, `industrial-arm`, `px4`, `composite`,
  and the niche runtimes) for a primitive whose semantics are a strict
  specialization of the existing "go to a declared station, perform a named
  service" verb. The spec's own capability binding for `swap_tool` is
  `manifest.docking_stations[].services` includes `swap_tool` — i.e. the
  `send_docking_goal` contract. Reusing it makes the runtime dispatch and the
  validator check bind to the *same* manifest field, so they cannot drift, and
  keeps the substrate-neutrality acid test trivially satisfied. The accepted
  cost is the `until` overload (Drawback 1).
- **Fold into RFC-0002.** Rejected: RFC-0002 is Implemented; its own
  §Profile-extensibility clause explicitly says each profile primitive set
  follows as its own RFC under that template. This is that RFC.

## Prior art

The `dock(service: ...)` primitive (RFC-0002) already routes arbitrary named
station services through `send_docking_goal`; `swap_tool` is the validated,
profile-scoped front door to the same mechanism. The `pick_from`/`place_at`
pairing mirrors PDDL `pick`/`place` action schemas and the OPC UA Robotics
companion-spec station-service model. The home (`speak`/`listen`, PR #25) and
drone (`take_off`/`land`/`return_to_home`, PR #30) profile-extension PRs
established the exact schema → validator → executor → conformance → example
pattern this RFC follows.

## Unresolved questions

- Whether `send_docking_goal` should gain a typed `payload: dict | None` so
  `swap_tool` stops overloading `until`. Small, additive, and substrate-neutral
  when it lands; out of scope here to keep this RFC zero-adapter-churn.
- When `accepted_tools` (the deferred per-station manifest field) is
  introduced, `_check_swap_tool_caps` gains a tool-membership check. Tracked,
  not in this RFC.
- Whether `place_at.height` should be enacted (needs a substrate height
  parameter, i.e. the same `payload` question for manipulation).

## Implementation note

One PR set, mirroring the RFC-0006 precedent (RFC doc + code land together;
the `Accepted -> Implemented` frontmatter flip is the final commit, after all
suites and conformance are green). Commit order: (1) this RFC at `Draft` +
index row; (2) schema + validator caps + binding; (3) ROS-2 executors; (4)
manifest fixture + conformance fixtures + example; (5) spec-doc promotion; (6)
paired front-page number updates (primitive count 17 → 20, fixture count, the
claims-audit pass totals — measured, not guessed); (7) verification matrix
green; (8) flip this RFC `Draft → Open → Accepted → Implemented`. The RFC-0001
Phase-0 seven-day Open→Accepted comment window is a founder-triggered calendar
step tracked separately; it gates the state flip, not the code.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case (the line-reconfiguration scenario; the skeleton industrial fixture).
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (the `send_tool_change_goal` Protocol method — argued, not strawmanned).
- [x] Drawbacks are listed; the `until` overload and the deferred `accepted_tools` check are real downsides.
- [x] Backward compatibility is honest: purely additive, pre-v1.0, nothing breaks.
- [x] This RFC adds Layer-2 primitives and presents both ROS-2 and non-ROS sketches for all three (substrate-neutrality acid test).
- [x] The implementation note explains how this lands (commit order, the one-PR-set + final state-flip precedent), not just what.
- [x] The author re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do: these primitives are in the canonical industrial scope, do not bypass the validator, add no cloud dependency, embed no vendor, and stay substrate-neutral (zero adapter churn).
