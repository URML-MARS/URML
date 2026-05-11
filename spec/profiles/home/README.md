# Home Profile

**Status:** Pre-draft. v1.0 target; first profile to ship. See roadmap in [`MANIFESTO.md`](../../../MANIFESTO.md).

## Application domain

Indoor service robots operating in spaces shared with people: kitchens, living rooms, offices, small clinics. The defining shape of the home profile is *natural-language input from a non-expert end user, executed by a robot that has to navigate human-occupied space gracefully*.

## In scope

- **Fetch-and-carry tasks.** "Bring me the red mug from the kitchen." The canonical home example (see [`/examples/home/red-mug.urml.yaml`](../../../examples/home/red-mug.urml.yaml)).
- **Navigation in human-occupied space.** The runtime is expected to honor proxemics, give right-of-way to people, and slow near unexpected motion. URML expresses the *intent*; the runtime's Layer-0 implementation handles the social-navigation specifics.
- **Charging-station docking.** A `dock` primitive that returns the robot to its declared station.
- **Voice- or text-driven natural-language flows.** The home profile is one of the first profiles where Layer-4 (the LLM bridge) is exercised end-to-end with a non-expert in the loop.
- **Multi-step household errands.** Composable through Layer-3 `sequence`, `branch`, and error handling.

## Out of scope

- **Outdoor navigation.** Home robots that move between indoor and outdoor environments are common; their outdoor behavior is covered by other profiles (drone for aerial, vehicle for ground), not by the home profile.
- **Manipulation requiring industrial-grade safety (force ceilings beyond gentle-grasp categories).** That is the industrial profile.
- **Continuous monitoring or surveillance.** Out of scope; URML's design principles prohibit collecting user data without explicit opt-in.

## Safety envelope class

A home robot operates in **shared, unsupervised space with non-expert end users**. The default safety envelope:

- Maximum velocity declared in the manifest, capped to a human-walking-pace default unless overridden by deployment.
- Force ceilings on `grasp` default to "gentle" (calibrated so an inadvertent contact with a person yields).
- No motion in declared "people-only" zones (children's rooms, bathrooms by default) without an explicit override in the manifest.
- A required emergency-stop pathway that any URML program must respect.

Profile-specific safety-envelope schema details are part of this layer's eventual specification document.

## Required manifest fields

When this profile is drafted, the capability manifest of a home-profile-conformant robot will be required to declare at least:

- Mobility (drive type, max velocity, max payload, declared frame).
- Manipulation (gripper, DOF, force range, reachable workspace) — if the robot has any.
- Perception (camera, depth sensor, microphone) — at minimum what the natural-language interface depends on for object detection.
- Declared locations in the home (`kitchen`, `living_room`, `user`, charging-station `dock`).
- Declared safety zones and any override policy.

## Layer-2 primitives this profile adds

To be defined. Likely candidates: `dock` (return to charging station), `release(mode: hand_to_user | place_on_surface)`, possibly `wait_for_user` for conversational hand-offs.

## Layer-2 primitives this profile constrains

- `grasp.force` defaults to `gentle` in the home profile.
- `move_to.location` accepts the declared home-location vocabulary or coordinates within the declared mapped area.

## Conformance points

When this profile is drafted, the conformance suite will include:

- The `red-mug` example as a baseline end-to-end test.
- Negative tests that the validator rejects programs that violate the default safety envelope.
- Tests that the home profile's added primitives behave as specified.

## Related documents

- [`/docs/architecture.md`](../../../docs/architecture.md) §Profiles.
- [`/examples/home/`](../../../examples/home/) — the runnable example pair for this profile.
- [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Home: the multilingual grandparent*.
