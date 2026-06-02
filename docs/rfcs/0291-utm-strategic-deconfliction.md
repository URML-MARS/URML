---
rfc: 0291
title: Geometric cross-robot deconfliction — UTM-style operational volumes for fleets
author: Ido Yahalomi (ido@jacob-ai.com)
state: Implemented
created: 2026-05-31
updated: 2026-06-02
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

# RFC-0291: Geometric cross-robot deconfliction — UTM-style operational volumes

## Summary

RFC-0286 shipped a fleet collision check, but it is **name-based**: two members
"collide" iff they target the same declared-location *name* in one `parallel`. That
is wrong twice — it **false-positives** (three robots each declaring a `waypoint_a`
in their own local `floor` frame are flagged as colliding when they are not), and it
**false-negatives** while being **2D-blind** (two drones at the same (x,y) but 30 m
apart in altitude, or two ROVs 5 m apart in depth, do not collide, but a name or
footprint check cannot tell).

This RFC replaces it with **geometric strategic deconfliction modeled on UTM** (FAA /
NASA Unmanned Aircraft System Traffic Management; ASTM F3548-21). Each member's
spatial target becomes an **operational volume** — a lateral footprint plus a
**vertical band** (altitude for air, depth for water) — and two members are safe iff
their volumes are separated **laterally, vertically, by medium, or in time**. URML
already has every axis: a `parallel` is a shared time window, a **`barrier` is
temporal separation**, the signed-z convention gives the vertical band, and the
medium follows from `drive_type`. The only new surface is a per-robot **clearance**
buffer and a roster **shared-frame** declaration.

This is US-aligned by construction: UTM is the FAA/NASA framework, ASTM F3548 the
interoperability standard.

## Motivation

The fleet vision spans ground, air, and water robots. A collision check that only
compares 2D footprints (or location names) is wrong for all three of them at once: it
cannot express that altitude separates two drones, that depth separates two ROVs, or
that two robots' identically-named local waypoints are different physical places. The
engaged-partners demo had to send each robot to a *distinct* location name purely to
dodge the name-based false positive — a tell that the check was modeling names, not
space.

UTM solves exactly this problem for unmanned aircraft and is the natural model. Its
unit is the **Volume4D**: a lateral outline + an altitude band [lower, upper] + a time
window [start, end]. Two operations are **strategically deconflicted** iff their
Volume4Ds do not intersect. The same logic generalizes to ground (AGV/AMR fleet
traffic management, e.g. Open-RMF per [RFC-0053](0053-open-rmf-multirobot-integration.md))
and water (maritime / MASS traffic management). URML names the concept
domain-neutrally and credits UTM as the model.

## Detailed design

### The UTM model, mapped onto URML

| UTM concept | URML mapping |
|---|---|
| Operational volume | a member's spatial target + its declared `clearance` (lateral radius + vertical band) |
| Lateral separation | footprint circles disjoint (`xy_dist >= r1 + r2`) — the **ground** case |
| Vertical separation | altitude/depth bands disjoint — **air** (z>0) and **water** (z<0), signed-z per RFC-0002 |
| Temporal separation | a **`barrier`** ends a time window; volumes in one `parallel` with no barrier share it |
| Common geodetic reference | the roster's **`shared_frames`** (frames are string names; URML has no transforms) |
| Constraint / medium | **medium** derived from `drive_type` (air vs water never share space) |

**Time is already structural.** The existing rule "compare volumes only within one
`parallel`, never across a `barrier`" *is* UTM temporal deconfliction. No timing model
is added.

### Schema (additive, optional)

**`FleetRoster.shared_frames: list[Identifier]`** (`schemas/roster.py`, default `[]`).
The frames that denote one common physical reference across members. The deconfliction
check **only compares targets whose frame is in this list**; a member's own local
frame (each partner robot's private `floor`) is never compared. This is what fixes the
false positive: distinct robots' identically-named local frames are not the same place.

**`Mobility.clearance: OperationalClearance | None`** (`schemas/manifest.py`):
`radius_m` (lateral footprint) + `vertical_m` (vertical half-band — altitude for air,
depth for water). Optional; absent means name-based fallback for pairs involving that
robot. Forward path (additive, no rename): `vertical_up_m` / `vertical_down_m` and a
polygon footprint when finer fidelity is needed.

**Medium** is derived, not declared: air = `{multirotor, fixed_wing, vtol}`, water =
`{underwater_thrusters}`, ground = the rest.

### Validator (`reference/validator/src/urml_validator/validator.py`)

`_check_concurrent_workspace` is rewritten around `_volumes_conflict(a, b, shared)`,
which short-circuits: **frame gate** (same frame, in `shared`) → **medium gate** (air
≠ water → safe) → **geometric** (lateral circles overlap AND vertical bands overlap,
`z=None→0`) → **name fallback** (now frame- and medium-gated). The check still emits
`fleet.concurrent_shared_workspace`, with richer `detail` (lateral distance, required
clearance, medium, reason). A new `fleet.shared_frame_undeclared` **warning** fires
when a roster names a shared frame no member declares (a typo would otherwise silently
disable the check). The geofence interval logic is reused for the vertical-band test.

### Conformance + tests

Ten geometric unit tests (`reference/validator/tests/test_fleet_validation.py`) and
six per-medium conformance fixtures (`conformance/fixtures/fleet/07–11, 13`) over
`utm_ground` / `utm_drone` / `utm_rov` manifests cover: ground footprint overlap
(reject), air altitude separation (accept) and same-altitude (reject), water depth
separation (accept) and same-depth (reject), cross-medium (accept), temporal-barrier
(accept), local-frame (accept — the false-positive fix), and the name fallback. The
engaged-partners demo is simplified so the three mobile robots **converge on one
`waypoint_a`** (legitimate now, since each `floor` frame is local) — the fix doubles as
the demo.

## Backward compatibility

Additive: both new fields are optional; a fleet with no `shared_frames` and no
`clearance` keeps the name-based behavior, except for one deliberate change.

**Behavior change (one):** the name-based fallback is now **frame-gated**. The previous
check rejected two members targeting the same location *name* even in different frames;
it no longer does unless the frame is declared shared. This is the correct behavior
(different frames are different spaces), and it is what fixes the false positive. The
courier-to-arm fixtures were reconciled by giving `handoff_dock` a shared `site` frame
and declaring `shared_frames: [site]`.

## Drawbacks

1. **No frame transforms.** `Frame` is name + parent only; URML has no transform graph.
   So only same-shared-frame comparisons are possible — a drone's `agl` target cannot
   be geometrically compared with a rover's `site` target. The medium gate covers the
   common air-vs-ground/water case meanwhile. A transform graph is named as future work.
2. **Temporal deconfliction is structural,** not explicit 4D time windows with
   durations — URML has no static timing model. True Volume4D (with durations) is future.
3. **The footprint is a circle and the band is symmetric** — not a polygon or an
   asymmetric up/down band (a drone's downwash wants more vertical clearance below). The
   field is named generically so these are additive upgrades.
4. **Static, per-`parallel`, endpoint check** — it compares target volumes, not swept
   trajectories between waypoints.

## Alternatives considered

**A clearance sphere (`safety_radius_m`).** Rejected in favor of the UTM volume: a
sphere conflates lateral and vertical clearance, and the three domains care about the
vertical axis specifically (altitude/depth separation). The UTM footprint + band is the
faithful model and the field path to a polygon/asymmetric volume is additive.

**Keep the name-based check, just frame-gate it.** Rejected: frame-gating alone fixes
the false positive but leaves the check 2D-blind and unable to express altitude/depth
separation, which is the whole point for air and water.

**Encode full ASTM F3548 Volume4D with explicit time.** Deferred: URML has no static
timing model, and the structural time window (parallel / barrier) is the honest v0.1
temporal axis. Named as future work.

## Prior art

- **FAA / NASA UTM ConOps** and **ASTM F3548-21** (UAS Service Supplier
  interoperability; strategic conflict detection over Volume4D operational intents) —
  the model this RFC adopts.
- **Open-RMF** ([RFC-0053](0053-open-rmf-multirobot-integration.md)) — the ground
  AGV/AMR fleet-traffic analog URML composes with at building scale.
- **Maritime MASS / IMO e-navigation** — the emerging water analog.
- Prior URML RFCs: RFC-0286 (the fleet surface this refines), RFC-0006 (the optional
  opt-in block + additive-error pattern), the geofence altitude-band machinery this
  reuses for the vertical band.

## Unresolved questions

1. **Frame transforms.** What is the minimal transform-graph URML needs to compare a
   drone's `agl` target against a rover's `site` target in the same physical space?
2. **Explicit Volume4D time.** Once URML has a static timing/duration model, should the
   temporal axis become explicit windows rather than the structural parallel/barrier?
3. **Anisotropic / polygon volumes.** Which domains first need asymmetric vertical
   clearance (drone downwash) or a polygon footprint, and what is the additive schema?

## Implementation note

Shipped on `rfc/0287-utm-deconfliction`: schema + validator + the unit matrix +
fixture reconciliation in one commit; conformance fixtures + harness `shared_frames`
alongside; the RFC, spec updates, and the converged engaged-partners demo to follow.
DCO-signed; merge commit; the founder runs the `--admin` merge. The RFC stays
**Accepted** until all lands, then **Implemented**.

## Self-review (Phase 1)

- [x] The Summary alone tells a reader what is proposed and why UTM.
- [x] Motivation is grounded in a concrete failure (the three-domain blindness and the
      partners-demo distinct-name dodge), not a hypothetical.
- [x] Detailed design names every affected layer and reuses existing geometry.
- [x] Alternatives genuinely considered (sphere; frame-gate-only; full Volume4D).
- [x] Drawbacks honest (no transforms; structural time; circle+symmetric band; static).
- [x] Backward compatibility states the one deliberate behavior change (frame-gated
      fallback) and how the existing fixtures were reconciled.
- [x] Re-checked against `CLAUDE.md`: the new surface is substrate-neutral (a clearance
      volume and a frame name, no medium-specific transport), the safety boundary is
      strengthened, no cloud dependency, US-federal alignment is reinforced (UTM is the
      US framework), scope stays civilian/industrial/research.
