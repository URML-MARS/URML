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

# AV Profile (research-grade autonomous vehicle)

**Status:** Draft (v0.1)
**Targets:** URML v0.1 + [RFC-0020](../../../docs/rfcs/0020-autoware-av-substrate.md)
**Created:** 2026-06-06

The research-grade autonomous-vehicle profile: ground vehicles that plan a path against an HD map within an operational design domain (ODD) and follow a precomputed trajectory. Autoware (on ROS 2) is the reference target; a non-ROS Apex.OS binding is a follow-on. This profile adds the two AV primitives `plan_path` and `follow_trajectory`, and the manifest `av` block (HD map, ODD, MRM).

> **Scope note: research-grade, not production-certified.** `production_safety_certified` is **false** for this profile, normatively. URML does not certify autonomous-vehicle safety; this profile is for research, simulation, and demonstration. The framing matches the [Manifesto](../../../MANIFESTO.md) stretch-goal scope (Autoware named as a *research-grade* target). Production AV safety (ISO 21448 SOTIF, UNECE R157) is a separate concern URML does not claim to discharge.

## Application domain

Autonomous ground vehicles whose operational model is **plan-then-follow**: compute a trajectory in a cost-map bound to an HD map, subject to an ODD, then execute that timed trajectory. This is a different shape from the core `move_to(named_location)` — "go to a named pose" versus "compute a trajectory across a mapped area and drive it" are different verbs with different validation surfaces, which is why the profile adds primitives rather than overloading `move_to`.

## In scope

- **Trajectory planning.** `plan_path` cost-maps a route from a start to a goal against the manifest's HD map and binds it (a compute verb; it does not actuate).
- **Trajectory following.** `follow_trajectory` executes a bound trajectory under a speed envelope; the only AV verb that actuates.
- **ODD enforcement (static).** The validator checks a trajectory's declared speed envelope against the ODD speed cap; the MRM declares the fallback when the ODD is exited or a trajectory aborts.

## Out of scope

- **Production safety certification.** See the scope note. This profile is research-grade.
- **Perception and prediction stacks.** URML governs intent and capability, not the AV's object detection / tracking / prediction, which live in the substrate (Autoware).
- **Real-time trajectory re-planning semantics** beyond the declared `on_off_route: abort | replan` intent. The control-theoretic realization is a substrate concern.

## Primitives

| Primitive | Kind | Binds | Consumes |
|---|---|---|---|
| [`plan_path`](../../layer-2-primitives/v0.1.0.md) | compute | a `trajectory` (`store_as`) | — |
| [`follow_trajectory`](../../layer-2-primitives/v0.1.0.md) | actuate | — | a `trajectory` (from `plan_path`) |

## Manifest

The profile reads the optional `av` block (Layer-1 §2.16): `hd_map` (the bound map a planner cost-maps against), `odd` (regions, `max_velocity_mps` cap, permitted `weather`), and `mrm` (the Minimum-Risk Maneuver strategy). `plan_path` requires `av.hd_map` to be declared.

## Safety envelope

The AV profile tightens the envelope with the ODD speed cap (`av.odd.max_velocity_mps`): a `follow_trajectory` speed envelope above the strictest of the ODD cap, the mobility max, and the envelope max is rejected (`envelope.velocity_exceeded`). HD-map-alignment and perception-latency SLAs are named in RFC-0020 as future envelope tightenings.

## Compliance

The bundled US-federal default policy lands no automotive-specific rules at v0.1; the standard provenance and origin rules still apply. Production-safety certification is explicitly out of scope (see the scope note).
