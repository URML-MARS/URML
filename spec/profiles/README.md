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

# URML Profiles

A **profile** is a domain-specific extension to the core URML specification. The core stays small and substrate-neutral; domain richness lives in profiles. This pattern lets URML serve very different settings (a kitchen, a roof inspection, a manufacturing cell) without bloating the core vocabulary.

## What a profile can do

A profile may:

1. **Add domain-specific primitives.** A drone profile adds `hover`, `take_off`, `land`. An industrial profile adds `pick_from_pallet`. A home profile adds `dock` (the robot returns to its charging station).
2. **Constrain core primitives.** The drone profile's `move_to` must declare altitude. The industrial profile's `move_to` must declare frame. The home profile's `grasp` defaults force to "gentle."
3. **Declare a profile-specific safety-envelope class.** Drones default to no-fly above declared population density; industrial cells default to "no motion unless safety door is closed."
4. **Declare profile-specific capability-manifest fields.** A drone manifest must declare maximum service ceiling; an industrial manifest must declare cell perimeter.

## What a profile cannot do

A profile may not:

- **Weaken core safety guarantees.** A profile that allows a primitive to bypass validation, or that disables a safety-envelope check, is rejected.
- **Break the substrate-neutrality acid test.** Profile primitives must, like core primitives, be cleanly implementable on a runtime with zero ROS dependencies.
- **Re-define core primitives.** A profile may constrain `move_to` (require altitude); it may not change what `move_to` means.
- **Conflict with other profiles.** Two profiles that both extend `move_to` must define compatible constraints. The validator rejects programs whose declared profile set is internally inconsistent.

## Canonical maintenance scope

The canonical URML organization maintains profiles within its declared scope: **civilian, consumer, educational, industrial, research**. Profiles outside that scope are architecturally permitted on top of URML (the Apache 2.0 license is not narrowed) but are not maintained in this repository. See [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`MANIFESTO.md`](../../MANIFESTO.md) §Scope.

## V1.0 profiles

| Profile | Status | What it covers |
|---|---|---|
| [`home/`](home/) | Phase 1 target | Indoor service robots: fetch-and-carry, navigation in human-occupied spaces, charging-station docking, voice-/text-driven natural-language flows. |
| [`drone/`](drone/) | Phase 2 target (**civilian only**) | Small unmanned aircraft used for inspection, photography, mapping, and similar non-combat tasks. Hard ceiling on altitude per civil aviation authority defaults; configurable by deployment. |
| [`industrial/`](industrial/) | Phase 3 target | Single-arm manipulators and mobile bases in controlled industrial cells: pick-and-place, line reconfiguration, safety-door-gated motion. |
| [`educational/`](educational/) | Draft ([RFC-0011](../../docs/rfcs/0011-educational-profile.md)) | Low-cost classroom/teaching robots, beginner authors, students nearby: conservative fail-loud defaults. v0.1 adds no primitives. |
| [`research/`](research/) | Draft ([RFC-0012](../../docs/rfcs/0012-research-profile.md)) | Robotics research platforms in attended labs: reproducibility-first (required provenance, explicit error policy), pose-based motion permitted. v0.1 adds no primitives. |

## Stretch profiles

Named in [`MANIFESTO.md`](../../MANIFESTO.md) §Scope as v1.x stretch targets, not yet stubbed in this repository:

- Agricultural
- Autonomous vehicle (research-grade; not production safety-certified)
- Healthcare / assistive
- Search-and-rescue
- Underwater

(Education has moved out of stretch: it is now drafted as the [`educational/`](educational/) profile above. The canonical maintenance scope — civilian, consumer, educational, industrial, research — is now fully stubbed.)

Each becomes a subdirectory under `/spec/profiles/` when its drafting begins.

## Adding a new profile

1. Open a [feature request](../../.github/ISSUE_TEMPLATE/feature_request.md) describing the domain, the v1.0 use cases, and the safety-envelope class. The maintainer routes it.
2. If routed forward, file an RFC that defines the profile's added primitives, constrained core primitives, manifest fields, and safety envelope.
3. On Accepted, draft the spec document, write a reference example, write conformance tests. Only then does the profile reach Implemented.

A profile is a smaller commitment than a core change but still a commitment. Profiles that have shipped should not be silently retired; a profile's removal needs an RFC.

## Related documents

- [`/docs/architecture.md`](../../docs/architecture.md) §Profiles.
- [`/spec/layer-2-primitives/`](../layer-2-primitives/) — core primitives that profiles extend.
- [`/spec/layer-1-hal/`](../layer-1-hal/) — capability manifest, which profiles may add required fields to.
- [`/examples/`](../../examples/) — per-profile example programs.
