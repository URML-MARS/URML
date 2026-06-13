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

# Move #48 post bodies: the domain / standards / conceptual-peer wave

Thirteen targets, all GitHub Issues. Post under idoco2003. No license-ask
anywhere (MOOS-IvP and OpenExo: state the repo's actual license, never ask).
AI-assisted-authoring disclosure up front. OpenExo framing is research-scope,
no clinical claim. Titles carry no em-dash. This wave completes the
2026-06-13 candidate slate.

---

## RFC-0529: OSGAR (anchor)

**Post to (Issue):** https://github.com/robotika/osgar/issues/new
**Title:** URML (open robot intent language): a validated mission-intent layer for an OSGAR fleet (request for comment)

```
Hi Team Robotika,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. OSGAR drives a heterogeneous fleet (wheeled, tracked, flying) for underground mapping and search, and URML is interesting as the intent layer above such a multi-robot, multi-substrate fleet.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a heterogeneous OSGAR fleet maps onto URML's multi-robot roster -- each robot a member with its own capability manifest, a mission addressing members or the whole fleet, with cross-robot deconfliction (the kind of constraint underground operations need). URML validates a mission against the members' capabilities and the coordination constraints, then dispatches to OSGAR's nodes. URML is the typed intent + fleet-coordination gate; OSGAR stays the runtime.

Two real questions: (1) does a URML fleet roster (per-robot manifests + cross-robot constraints) fit a heterogeneous SubT-style fleet? (2) Is a validated mission-intent layer above OSGAR's nodes interesting for underground / search work -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0529-osgar-outreach.md

Thanks for OSGAR; a real heterogeneous-fleet SubT stack is exactly where fleet-level validated intent earns its keep.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0530: MOOS-IvP

**Post to (Issue):** https://github.com/moos-ivp/moos-ivp/issues/new
**Title:** URML (open robot intent language): declared intent above the IvP Helm (request for comment)

```
Hi MOOS-IvP community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the vehicle's declared capabilities and a safety envelope, then dispatched. MOOS-IvP arbitrates between behaviors via the IvP Helm; URML is a conceptual peer at a different layer -- a declarative, validatable representation of intent that sits above a behavior-arbitration helm.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The layering: a URML program declares the mission intent for a marine vehicle, validated against the vehicle's capabilities and a safety envelope; the IvP Helm then arbitrates the behaviors that realize it. URML is the typed declaration of what should happen; IvP is the runtime arbitration of how. The vehicle's mobility and operating limits map onto a URML manifest so the intent is checkable before it reaches the helm. (No code reuse proposed, only a layering relationship.)

Two real questions: (1) is "URML declares the validated mission intent, the IvP Helm arbitrates the behaviors" a sensible layering for a marine vehicle? (2) Does a URML marine-vehicle manifest fit how MOOS-IvP models a platform -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0530-moos-ivp-outreach.md

Thanks for MOOS-IvP; the helm's behavior-arbitration design is exactly the runtime a declarative intent layer wants to sit above.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0531: Project 11

**Post to (Issue):** https://github.com/CCOMJHC/project11/issues/new
**Title:** URML (open robot intent language): a validated mission spec above the Project 11 mission manager (request for comment)

```
Hi Project 11 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the vehicle's declared capabilities and a safety envelope, then dispatched. Project 11 is a ROS backseat-driver framework for ASVs with mission and helm managers, and URML is interesting as the front door above the mission manager.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a URML program declares an ASV survey / transit mission, validated against the vehicle's declared mobility and a safety envelope (operating area, depth band), then handed to Project 11's mission manager. Your backseat-driver architecture is exactly the clean boundary URML likes: URML produces the validated mission; the autopilot / helm executes it.

Two real questions: (1) does a URML ASV mission program (mobility + operating-area envelope) fit how Project 11's mission manager is driven? (2) Is a validated-intent front door above the mission manager interesting for survey ASVs -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0531-project11-outreach.md

Thanks for Project 11; the backseat-driver boundary is the cleanest place a validated-mission layer plugs in.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0532: bsk_rl

**Post to (Issue):** https://github.com/AVSLab/bsk_rl/issues/new
**Title:** URML (open robot intent language): spacecraft task intent + a learned scheduling envelope (request for comment)

```
Hi bsk_rl community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a high-level task becomes a typed primitive, validated against the system's declared capabilities and a safety envelope, then dispatched. bsk_rl is RL for spacecraft autonomy (planning / scheduling on Basilisk), and URML extends its robot-intent frame to a spacecraft.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a spacecraft tasking intent (image this target, downlink, recharge) maps onto typed URML primitives validated against a manifest of the spacecraft's capabilities and a constraint envelope (power, attitude, keep-out). Validate the plan, then execute. And a bsk_rl-trained scheduling policy can declare, via URML's "LearnedPolicy" declaration, the observation/action spaces and domain it learned, so a deployment is validated against it.

Two real questions: (1) does URML's capability-manifest + safety-envelope frame extend sensibly to spacecraft tasking / scheduling? (2) Is declaring a trained scheduling policy's envelope useful for the deployment side -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0532-bsk-rl-outreach.md

Thanks for bsk_rl; spacecraft scheduling under hard constraints is a striking test of a capability-and-envelope intent frame.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0533: PX4-Space-Systems

**Post to (Issue):** https://github.com/DISCOWER/PX4-Space-Systems/issues/new
**Title:** URML (open robot intent language): the PX4 substrate mapping applied to a space free-flyer (request for comment)

```
Hi DISCOWER community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched to a substrate. URML already targets PX4 (a PX4 runtime / adapter), and your PX4-Space-Systems fork is the same substrate in a microgravity domain.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: URML's PX4 adapter dispatches validated intent to a PX4 autopilot. A free-flyer running PX4-Space-Systems is that same substrate for a space platform: the manifest declares the free-flyer's mobility and constraints, and URML validates intent against them before dispatch. This is not a new mechanism -- it is URML's existing PX4 substrate mapping applied to a free-flyer.

Two real questions: (1) does URML's existing PX4 substrate mapping extend cleanly to a PX4-based free-flyer? (2) What does a free-flyer manifest need that a drone manifest does not (microgravity mobility, attitude / translation constraints) -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0533-px4-space-systems-outreach.md

Thanks for PX4-Space-Systems; a PX4 free-flyer is a great way to test the substrate mapping in an unfamiliar domain.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0534: Feldfreund

**Post to (Issue):** https://github.com/zauberzeug/feldfreund_devkit_ros/issues/new
**Title:** URML (open robot intent language): an English field-task front door for Feldfreund (request for comment)

```
Hi Zauberzeug community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: "weed row 4" / "return to charge" becomes a typed primitive, validated against the platform's declared mobility and tool, then dispatched to the ROS 2 stack. Feldfreund is an autonomous field-weeding platform, and URML is interesting as the natural-language front door above it.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: Feldfreund's mobility (field navigation) and its weeding tool map onto a URML manifest; a field task is validated against that manifest and a safety envelope (the field boundary as a geofence) before dispatch. URML adds the capability/envelope gate above the ROS 2 stack.

Two real questions: (1) does mapping the Feldfreund platform (field mobility + weeding tool + field-boundary geofence) onto a URML manifest read right? (2) Is an English-to-validated-field-task front door above the ROS 2 stack interesting -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0534-feldfreund-outreach.md

Thanks for Feldfreund; a real field-weeding platform with a clean ROS 2 stack is a great fit for the field-task front door.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0535: OpenExo

**Post to (Issue):** https://github.com/naubiomech/OpenExo/issues/new
**Title:** URML (open robot intent language): an envelope-bounded assistance declaration for OpenExo (request for comment, research scope)

```
Hi OpenExo community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the device's declared capabilities and a safety envelope, then applied. OpenExo is an open modular exoskeleton framework on a Teensy / Arduino substrate, and URML is interesting as a typed, validatable declaration of an assistance intent and the safety envelope it must stay within. This is a research-scope request for comment; it makes no clinical claim.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: an exoskeleton's assistance configuration (which joint, torque profile, mode) can be expressed as a typed URML declaration, validated against the device's declared actuation capabilities and a safety envelope (torque / range limits) before it is applied. The envelope is the load-bearing part: an assistance command outside the declared safe limits is refused. OpenExo's Teensy / Arduino target also fits URML's minimal-MCU and output-actuation work (dependency-free, on any OS).

Two real questions: (1) is a typed, envelope-bounded declaration of an assistance configuration useful for an open exoskeleton (research scope)? (2) Does URML's MCU-substrate / actuation model fit the Teensy / Arduino target -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0535-openexo-outreach.md

Thanks for OpenExo; an open, MCU-based exoskeleton framework is exactly where an envelope-bounded assistance declaration is worth exploring (research scope).

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0536: CleanIt

**Post to (Issue):** https://github.com/Sollimann/CleanIt/issues/new
**Title:** URML (open robot intent language): an English front door above CleanIt's vacuum autonomy (request for comment)

```
Hi CleanIt community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: "clean the kitchen" / "go home" becomes a typed primitive, validated against the robot's declared mobility and a safety envelope, then dispatched. CleanIt is open Rust + gRPC autonomy for Roomba-series vacuums, and URML is interesting as the natural-language front door above it. (The Rust core also matches URML's preference for Rust in long-running infrastructure.)

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the vacuum's mobility and named areas map onto a URML manifest; a cleaning / navigation intent is validated against it and a safety envelope before dispatch to CleanIt's autonomy over gRPC. URML produces the validated intent; CleanIt executes it.

Two real questions: (1) does mapping a vacuum's mobility + named areas onto a URML manifest fit? (2) Is an English-to-validated-intent front door above CleanIt's autonomy interesting for service robots -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0536-cleanit-outreach.md

Thanks for CleanIt; open Rust autonomy for a common service robot is a clean place to try a validated-intent front door.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0537: Roomi

**Post to (Issue):** https://github.com/jadechoghari/roomi/issues/new
**Title:** URML (open robot intent language): validated mobile-manipulation intent for Roomi (request for comment)

```
Hi Roomi community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Roomi is an open cleaning / housekeeping robot -- a mobile base with dual arms and multi-camera sensing -- and URML is interesting as the validated-intent layer above a mobile-manipulation service robot, where the dual arms tie directly to URML's bimanual model.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: Roomi's mobile base and two arms map onto a URML manifest -- mobility plus per-arm declarations (manipulation.arms) -- so a "tidy this surface" task is a composition of move_to and arm primitives, including coordinated two-arm work via the bimanual primitive. Each step is validated against the manifest and safety envelope. Apache-2.0 enables a RoomiAdapter against the published stack, the established URML pattern.

Two real questions: (1) does mapping Roomi (mobile base + dual arms + cameras) onto a URML manifest (mobility + manipulation.arms + bimanual) read right? (2) Is a validated mobile-manipulation intent layer interesting -- and which is the cleaner first seam, the manifest mapping or a RoomiAdapter?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0537-roomi-outreach.md

Thanks for Roomi; an open mobile-manipulation housekeeping robot is a natural fit for the bimanual-manipulation model.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0538: OpenAMR

**Post to (Issue):** https://github.com/openAMRobot/openamr/issues/new
**Title:** URML (open robot intent language): validated transport intent for an OpenAMR + Open-RMF deployment (request for comment)

```
Hi OpenAMR community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a transport task becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. OpenAMR is an affordable modular AMR for SME intralogistics that integrates Open-RMF, and URML is interesting at the open-platform altitude with vocabulary that already covers the cell.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: OpenAMR's mobility and the deployment's named locations / occupancy zones map onto a URML manifest under its warehouse profile (zero new vocabulary). A pick-to-conveyor or transport task is validated against the manifest and a safety envelope before dispatch. Because OpenAMR integrates Open-RMF, URML's fleet roster and cross-robot deconfliction are the static-validation complement to RMF's runtime orchestration -- one intent description, validated before it reaches the fleet manager.

Two real questions: (1) does mapping an OpenAMR onto a URML warehouse-profile manifest read right? (2) Is a validated transport-intent layer (with fleet validation as the RMF complement) interesting for SME intralogistics -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0538-openamr-outreach.md

Thanks for OpenAMR; an open intralogistics AMR with Open-RMF is exactly the platform altitude where validated transport intent fits.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0539: AIPlan4EU Unified Planning

**Post to (Issue):** https://github.com/aiplan4eu/unified-planning/issues/new
**Title:** URML (open robot intent language): a robot-intent peer to the Unified Planning Library (request for comment)

```
Hi Unified Planning community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. URML and Unified Planning are both declarative languages for what a system should do, at different layers: URML declares robot intent validated against a physical capability manifest and a safety envelope; Unified Planning declares a planning problem solved by a planner (PDDL / ANML / HDDL). This is a request for comment on how they compose.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: a URML program's goal and constraints could compile to a Unified Planning problem (the planner produces a plan), and the resulting plan steps could lower back to validated URML primitives for dispatch. URML contributes the physical-capability and safety-envelope validation a pure planning formalism does not carry; Unified Planning contributes the solver abstraction. Two declarative layers, cleanly divided: URML grounded in a robot's declared capabilities, Unified Planning grounded in a domain/problem model.

Two real questions: (1) is a URML-intent-to-Unified-Planning-problem (and plan-back-to-validated-primitives) composition sensible? (2) Is the physical-capability / safety-envelope validation URML adds a useful complement for robot deployment -- and which direction is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0539-unified-planning-outreach.md

Thanks for the Unified Planning Library; as a fellow declarative-over-many-backends project, you are the closest language peer we have found.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0540: MTConnect (cppagent)

**Post to (Issue):** https://github.com/mtconnect/cppagent/issues/new
**Title:** URML (open robot intent language): a robot-intent standard beside MTConnect on the shop floor (request for comment)

```
Hi MTConnect community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. MTConnect is the US manufacturing-interoperability standard for reading data off machine tools; URML's relationship is at the data / interop boundary -- MTConnect reports equipment state, URML declares and validates intent for a robot operating alongside that equipment.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: an MTConnect agent reports machine state (availability, mode, condition). A URML program for a robot in that cell can condition a typed intent on that state, validated against the robot's capabilities and a safety envelope before dispatch. URML consumes the equipment data as a fact; it does not replace MTConnect. The two are complementary shop-floor standards: robot intent beside equipment data.

Two real questions: (1) is "MTConnect reports equipment state, a URML robot intent conditions on it" a sensible interop boundary on a shop floor? (2) Is there value in a documented URML-beside-MTConnect pattern for robot-plus-machine cells -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0540-mtconnect-cppagent-outreach.md

Thanks for MTConnect; a complementary equipment-interop standard is exactly the kind of boundary worth naming for robot-plus-machine cells.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0541: AutoAPMS

**Post to (Issue):** https://github.com/AutoAPMS/auto-apms/issues/new
**Title:** URML (open robot intent language): a validated-intent layer beside AutoAPMS skills / behavior trees (request for comment)

```
Hi AutoAPMS community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. Its Layer-3 behavior composition is a peer to a behavior tree, so URML and AutoAPMS compose in either direction rather than compete.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two directions: (1) a URML program lowers onto an AutoAPMS behavior tree; or (2) an AutoAPMS skill-leaf calls a single URML primitive validated against the robot's capability manifest and envelope before it executes. Either way URML adds the typed, statically-validated intent, and AutoAPMS stays the deliberation / BT executor. Separately, AutoAPMS's skill registrations describe what the robot can do, which lines up with a URML capability manifest the validator checks against.

Two real questions: (1) is lowering URML composition onto an AutoAPMS BT the more natural direction, or is a skill-dispatches-a-validated-URML-primitive cleaner? (2) Could AutoAPMS skill declarations inform a URML capability manifest -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0541-auto-apms-outreach.md

Thanks for AutoAPMS; a skill-based BT framework with a deliberation layer is a natural place to ask where a validated-intent layer fits.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
