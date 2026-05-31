---
rfc: 0286
title: Multi-robot fleet addressing and synchronized execution
author: Ido Yahalomi (ido@jacob-ai.com)
state: Accepted
created: 2026-05-31
updated: 2026-05-31
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

# RFC-0286: Multi-robot fleet addressing and synchronized execution

## Summary

URML today describes one robot at a time. A program is one tree of Layer-3
composition nodes whose leaves are Layer-2 primitives, validated against one
Layer-1 manifest, executed by one adapter. This RFC adds the minimum surface that
lets one program command a **heterogeneous fleet**: a Layer-1 `roster` binding N
existing per-robot manifests under English-callable handles, two additive Layer-3
nodes — `on:` (scope a subtree to a named member) and `barrier:` (synchronize
members at a rendezvous) — and a multi-robot validation entry point,
`validate_fleet`, that re-runs every single-robot pass re-keyed by member and adds
four cross-robot checks. A reference `FleetRuntime` executes the result
hermetically.

The load-bearing value is **not** the syntax. It is the validator catching, before
anything actuates, the cross-robot failure class no single vendor SDK can see —
two robots driven into the same workspace at the same instant — because no single
SDK sees both robots. This extends URML's validation moat from one robot to a
fleet.

This RFC adds no Layer-2 primitive. It does not add a `target_robot` field to any
of the 21 primitives. Every existing single-robot program validates and executes
exactly as before.

## Motivation

Heterogeneous multi-robot coordination is a real, currently-unmet need, and URML
has already admitted it in two places without being able to express it:

- The [warehouse profile](../../spec/profiles/warehouse/README.md) documents
  AMR-to-AMR handoff at declared docks as a genuine requirement, then explicitly
  punts the coordination to "a single fleet-management layer above the warehouse
  AMRs (Open-RMF, vendor-specific, or custom)" and consumes the result through
  `wait_for(condition.event)`. URML can wait on a handoff it cannot itself
  describe.
- [RFC-0006](0006-connectivity-and-link-loss.md) reserved a `peer_link`
  connectivity role with no behavioural semantics, stating it exists "so the future
  multi-robot RFC is additive rather than a breaking enum change." This is that
  RFC; it cashes that reserved slot.

The concrete worked case is a **courier-to-arm handoff**: a mobile base
(`HuskyAdapter`) brings a tray to a shared dock; a stationary Kawasaki arm
(`KawasakiAdapter`) picks a widget from the dock and places it on a conveyor; the
courier leaves only after the arm has cleared. Two heterogeneous robots, real
shipped adapters, one job neither can do alone. Choreographing this today means
two vendor SDKs plus hand-rolled timing glue with no static safety net. With a
roster and one program it is one language, one validator, one synchronizer — and
the validator rejects, before execution, an arm that reaches into the dock before
the courier has stopped.

Three value claims gate every piece of new surface (no surface ships that does not
serve at least one): it **deletes N-SDK glue**; it adds **static cross-robot
safety** no SDK provides; and it makes orchestration **substrate-fungible** (swap a
member's robot and the choreography is unchanged — only the roster entry changes).

## Detailed design

### Layer 3 — two additive composition nodes

`reference/validator/src/urml_validator/schemas/composition.py`. Two new
`_BaseBehavior` subclasses, tagged like every other composition node so the
discriminator stays one closed switch:

- **`OnMember`** — `type: "on"`, `member: Identifier`, `body: BehaviorOrStep`.
  Scopes its single child to one fleet member; every primitive beneath it is
  dispatched to that member's robot. Exactly one child, so the single-root-tree
  invariant is preserved — it is a tagged wrapper, not a fan-out.
- **`Barrier`** — `type: "barrier"`, `members: list[Identifier]` (≥ 2, unique). A
  leaf: execution does not proceed until every named member reaches it. This is the
  "sync command" that makes a handoff safe.

`_TAG_TYPES` and the `BehaviorOrStep` discriminated union gain the two tags. A
program with no `on:`/`barrier:` node is unchanged.

> **YAML note (one honest wart).** The `on:` tag is spelled `type: "on"` —
> **quoted**. YAML 1.1 reads a bare `on` as the boolean `true` (the same reason
> `yes`/`no` are quoted). `barrier`/`sequence`/`parallel` need no quoting. The spec
> writes the tagged form as normative; the LLM bridge emits `"on"` quoted.

### Layer 1 — the roster

New module `reference/validator/src/urml_validator/schemas/roster.py` (symmetry
with how RFC-0004 added `policy.py`, RFC-0006 added `connectivity.py`):

- **`RosterMember`** — `name: Identifier` (the handle `on:`/`barrier:` address),
  `manifest: str` (an opaque reference the caller resolves).
- **`FleetRoster`** — `roster_version`, `members` (≥ 1, unique names).

`CapabilityManifest` is **unchanged**. The roster binds N existing manifests by
handle; it does not nest or alter them. The validator receives a resolved
`{member -> CapabilityManifest}` alongside the roster, exactly as single-robot
loading resolves one manifest before validation. A fleet mission is a
two-document YAML (`roster` `---` `behavior`).

### Validator — `validate_fleet` and four cross-robot checks

`reference/validator/src/urml_validator/validator.py`, with four additive
`fleet.*` codes in `errors.py`. `validate()` is the single-robot entry point,
untouched on the no-roster path. `validate_fleet(roster, member_manifests,
program, member_envelopes=None, profiles=(), policy="DEFAULT")` adds:

| Code | Catches |
|---|---|
| `fleet.undeclared_member` | an `on:`/`barrier:` names a member not in the roster, or a step in a multi-member fleet is unaddressed (a fleet of one resolves the sole member) |
| `fleet.capability_unsupported_on_member` | a primitive scoped to a member whose manifest fails the existing per-robot capability check |
| `fleet.concurrent_shared_workspace` | two distinct members targeting the same declared location concurrently in one `parallel` with no barrier between them |
| `fleet.barrier_missing_peer_link` | a `barrier` member whose manifest does not declare the `peer_link` connectivity role |

The capability check is the existing `_check_capabilities` **reused verbatim**,
re-keyed by member via a new `walk_program_scoped` walker that yields `(path, step,
member)`; its result is re-wrapped as `fleet.capability_unsupported_on_member` with
`detail={member, underlying}` so the LLM bridge knows the fix belongs to one
member's manifest, not the shared program. The `peer_link` check uses the existing
`connectivity.link_for(LinkRole.PEER_LINK)` helper. Pass 4 (bindings) runs across
the whole fleet tree unchanged — a `$ref` produced under one member and consumed
under another resolves because the fleet is one tree, and the `barrier` is what
makes that cross-member binding *temporally* real (the validator checks lexical
order; the barrier makes it true at runtime). Pass 5 (policy) runs per member
manifest.

### Reference runtime — `FleetRuntime`

`reference/ros2-runtime/src/urml_ros2_runtime/fleet.py`, the inter-robot analogue
of `URMLRuntime`, reusing the `CompositeAdapter` routing pattern. It holds a
`{member -> ROSAdapter}` map, dispatches each `on:` subtree to that member's
adapter, and keeps a fleet-global bindings dict so a `$ref` flows across members.
Execution is deterministic and sequential — matching the single-robot runtime,
which also runs `parallel` branches sequentially and treats real concurrency as a
substrate concern. A `barrier` is therefore a rendezvous marker (a no-op join)
under sequential execution; its teeth are in the validator, which runs before
anything actuates. Each member owns its adapter, so `per_member_audit` is one clean
call-log per robot. Defense-in-depth: `execute` re-validates via `validate_fleet`
first. Hermetic path: one `MockROSAdapter` per member — the whole fleet runs
offline, any OS, no ROS, no cloud.

`CompositeAdapter` is the *intra*-robot split (flight + companion); `FleetRuntime`
is the *inter*-robot split. They compose — a member's adapter could itself be a
Composite.

### Conformance

`conformance/src/urml_conformance/fixtures.py` gains an optional `roster`
(exactly one of `manifest`/`roster`) and `per_member_audit`; `runner.py` branches
to a fleet path. Five substrate-agnostic fixtures under
`conformance/fixtures/fleet/`: one positive (the courier-to-arm handoff, validated
and executed with asserted per-member audit) and four validator-only negatives
(one per `fleet.*` code).

### The open/commercial line

The roster, the `on:`/`barrier:` operators, `validate_fleet`, and the reference
`FleetRuntime` are Apache-2.0 open core, here forever. The fleet-management
**product** — a hosted dashboard, fleet observability, building-scale traffic
management — is a commercial surround and stays out of this repository
(`CLAUDE.md` lists "fleet management" among the eventual commercial surfaces).
Large-scale, multi-site coordination routes to Open-RMF as an external layer
([RFC-0053](0053-open-rmf-multirobot-integration.md)). This RFC defines the
*language*, not a management app.

## Backward compatibility

URML is pre-1.0, but this RFC needs no break: every change is additive. The two
new Layer-3 nodes are new union members; the roster is a new optional document;
`CapabilityManifest` is untouched; `validate()` and `URMLRuntime` behave
identically on any program with no `on:`/`barrier:` node. A single-robot program is
a fleet of one with an implicit member. `peer_link` was already a closed-enum
member (RFC-0006), so activating its semantics is additive.

## Drawbacks

1. **The `type: "on"` YAML-quoting wart.** A bare `on` is a YAML 1.1 boolean.
   Hand-authored YAML and the LLM bridge must quote it. Documented; the alternative
   (a non-colliding tag like `on_member`) loses the headline elegance, and quoting
   `yes`/`no`/`on` is already standard YAML practice.
2. **Workspace collision is name-based, not geometric.** v0.1 has no
   workspace-volume concept in the manifest (`DeclaredLocation` is name + pose +
   frame; `reachable_workspace_m` is a scalar radius). Two members "share a
   workspace" iff they target the same declared *location name* concurrently. This
   is conservative and honest; it is not true overlap geometry. A `workspace_volumes`
   block with polygon overlap is named below as future work — the same path the
   geofence check took (names first, geometry later).
3. **`barrier` has no executed teeth in v0.1.** Under deterministic sequential
   execution a barrier is a rendezvous marker; the runtime does not simulate a real
   concurrency hazard. The static rejection is the contract v0.1 delivers — the
   same honest stance RFC-0006 took for link-loss (static now, executed scenario
   later).
4. **`pick_from.source: $tray` is not modeled.** `PickFromArgs.source` is a declared
   location name, so a tray carried as a binding across members needs a small future
   decision (treat a VarRef source as runtime-resolved, or model the tray as a
   declared location). The demo sidesteps it: the arm produces `$part` and consumes
   it within its own subtree.

## Alternatives considered

**A `target_robot` field on every Layer-2 primitive.** Rejected. It would touch all
21 primitives (a one-way door on every arg shape), pollute Layer 2 with a
deployment concern, and break the single-robot program (every primitive would carry
a fleet-only field). RFC-0002's principle is composition over expansion; the `on:`
scope node is additive, reversible, and leaves Layer 2 untouched. A single-robot
program stays valid because it is a fleet of one.

**Bare-key surface (`on:`, `barrier:` as mapping keys).** Rejected for v0.1. It
reads beautifully but collides with the existing tagged discriminator (and `on` as
a YAML key is *also* the boolean `true`), and it would create two ways to spell
every node — "every knob is debt" (`CLAUDE.md`). The tagged form matches every
in-repo fixture and the LLM bridge. A bare-key sugar layer is a possible future
ergonomic RFC, not a v0.1 requirement.

**A separate `fleet-runtime` package.** Rejected as over-engineering for v0.1. The
reference `FleetRuntime` sits beside `URMLRuntime` in `ros2-runtime`, reusing
`MockROSAdapter`, `execute_step`, and the `CompositeAdapter` pattern with zero new
dependency. A future extraction is the natural seam for the commercial fleet-manager
surround, but the open-core reference belongs here.

**Encode fleet traffic management in URML.** Rejected. Building-scale, multi-site
traffic coordination (lift queuing, aisle reservation, charge scheduling) is
Open-RMF's domain; RFC-0053 already routes it there. URML stops at "this robot
executes this intent, synchronized with these peers"; RMF starts at "these N robots
share these aisles."

## Prior art

- **RFC-0006** — reserved `peer_link` for exactly this RFC; the optional-block
  opt-in pattern, additive error codes, and the static-rejection-now / executed-later
  stance are all reused here.
- **RFC-0053 / Open-RMF** — the external fleet-traffic layer URML composes with
  rather than replaces; the warehouse profile's `wait_for(event)` handoff is the
  event-driven complement to this RFC's in-language synchronization.
- **`CompositeAdapter` (PX4 runtime)** — the intra-robot multi-adapter routing
  pattern `FleetRuntime` generalizes to the inter-robot case.
- **Behavior trees / PDDL** — the "a declared condition must hold or a safe branch
  triggers" structure; URML keeps the cross-robot check static.

## Unresolved questions

1. **Geometric workspace volumes.** A `workspace_volumes:` manifest block plus
   polygon-overlap reasoning would replace name-based collision with true geometry.
   What is the substrate-neutral shape of a workspace volume, and how does it relate
   to `reachable_workspace_m` and to envelope geofences?
2. **Executed concurrency-hazard conformance.** A future minor should add a scenario
   where the runtime actually interleaves member branches and a missing barrier
   produces an observable hazard, not just a static rejection.
3. **Cross-member binding semantics.** Should a `$ref` produced under member A and
   consumed under member B require an intervening `barrier` for the validator to
   accept it (making the temporal dependency explicit), rather than relying on
   lexical order alone?
4. **Bare-key ergonomic sugar.** Is a normalizer that accepts `on:`/`barrier:` as
   single-key sugar worth a follow-on RFC, given the LLM-bridge reliability cost of
   the `type: "on"` quoting requirement?

## Implementation note

Shipped as six DCO-signed PRs, PR-1 load-bearing, mirroring RFC-0006's sequencing.
Merge commits to `main`, never squash; the founder runs the `--admin` merges.

1. **PR-1 — schema + validator (the teeth). Blocks the rest.** `roster.py`,
   `composition.py` (+`OnMember`/`Barrier`), `errors.py` (+4 codes), `validator.py`
   (+`validate_fleet`, +`walk_program_scoped`, +4 checks). 13 unit tests including a
   single-robot-unchanged regression.
2. **PR-2 — `FleetRuntime`** (hermetic). 6 tests.
3. **PR-3 — runnable demo** under `examples/fleet/` + a don't-rot guard.
4. **PR-4 — conformance** fixtures + runner branch.
5. **PR-5 — LLM bridge prompt + spec docs** (Layer-3 scope/barrier, Layer-1 roster).
6. **PR-6 — JSON-Schema export** of the roster + fleet-node regression guards.

The RFC stays **Accepted** until all land, then advances to **Implemented**
(RFC-0004 / RFC-0006 precedent).

## Self-review (Phase 1)

In Phase 1 the author still reviews their own work against the documented checklist.

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete, already-documented need (the
      warehouse profile's admitted-but-inexpressible handoff; the reserved
      `peer_link` slot), not a hypothetical.
- [x] The Detailed design names every affected layer and reference component.
- [x] At least one alternative is genuinely considered (the rejected per-primitive
      `target_robot` field, with the composition-over-expansion reasoning; the
      rejected bare-key surface; the rejected separate package).
- [x] Drawbacks are listed and at least one is a real downside (the YAML-quoting
      wart; name-based-not-geometric collision; no executed barrier teeth).
- [x] Backward compatibility is honest: every change is additive; single-robot is
      unaffected.
- [x] This RFC adds no Layer-2 primitive, so the substrate-neutrality acid test
      applies to the new Layer-3 nodes — `on:` and `barrier:` are pure declarations,
      implementable on any zero-ROS runtime (the reference runtime executes them
      hermetically with no ROS).
- [x] The open/commercial line is re-checked against `CLAUDE.md` §What Claude should
      never do: the language and reference runtime are open core; the fleet-manager
      product is a commercial surround kept out of this repo; no cloud dependency, no
      LLM-provider coupling, scope stays civilian/industrial.
- [x] The implementation note explains how this lands (six sequenced PRs, PR-1
      blocking).
