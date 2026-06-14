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

# Move #51 post bodies: the AV / ADAS / off-road wave

Eight targets, all GitHub Issues. Post under idoco2003. No license-ask
anywhere (state each repo's actual license, never ask). AI-assisted-authoring
disclosure up front. Titles carry no em-dash. f1tenth_system + f1tenth_gym are
one post (on f1tenth_system, referencing the gym). Unifying framing: URML
declares the goal + constraints, validates admissibility against the vehicle's
capabilities and a safety envelope (its operating design domain), and consumes
the planned trajectory. opendbc is the anchor exception: a Layer-1 actuation
HAL seam.

---

## RFC-0558: opendbc (anchor)

**Post to (Issue):** https://github.com/commaai/opendbc/issues/new
**Title:** URML (open robot intent language): a validated-intent layer above a vehicle actuation HAL (request for comment)

```
Hi opendbc maintainers,

opendbc is, in effect, a vehicle actuation HAL: it documents how to read a car's state and actuate steering, gas, and brakes over CAN across a huge range of vehicles. URML (urml.dev) is a small, Apache-2.0 language for robot intent, and its Layer 1 is exactly the abstraction that wants a HAL like opendbc underneath it. This is a request for comment about the seam.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: URML does not define CAN messages and never should -- that is opendbc's domain, done better than a language could. What URML adds is the typed, statically-validated intent that sits above actuation. An intent is checked (argument typing, capability against a manifest, safety envelope, bindings, policy) before any actuation command is produced; opendbc then turns the validated command into CAN. And a car's actuatable ranges and supported controls -- the kind of thing opendbc encodes per platform -- map onto a URML Layer-1 capability manifest, so an intent can be rejected before it reaches the bus if the vehicle cannot do it.

Two real questions: (1) is a typed, statically-validated intent layer above a vehicle actuation HAL useful, or does the safety story already live entirely at the controls layer? (2) Could a vehicle's actuation envelope (as opendbc encodes it per platform) inform a URML Layer-1 capability manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0558-opendbc-outreach.md

Thanks for opendbc; a clean, broad vehicle-actuation HAL is exactly what makes a substrate-neutral intent layer testable on real cars.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0559: sunnypilot

**Post to (Issue):** https://github.com/sunnypilot/sunnypilot/issues/new
**Title:** URML (open robot intent language): a typed operating-design-domain check in front of a maneuver (request for comment)

```
Hi sunnypilot maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Every driver-assistance system has an operational design domain -- the conditions and maneuvers under which it is allowed to act -- and URML's safety envelope is a typed, declarative way to state those bounds and check a maneuver against them.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a driver-assistance system acts only within an ODD. URML expresses an active safety envelope (speed, geometry, conditions) plus a capability manifest, and validates an intended maneuver against both before dispatch. The point is not to replace the controls stack but to give the "is this maneuver allowed right now" check a typed, declarative form. URML declares and checks the maneuver intent; sunnypilot plans and actuates it. URML does not drive; it gates.

Two real questions: (1) is a typed, declarative operating-design-domain check a useful layer in front of an ADAS maneuver? (2) Does URML's capability manifest map onto how sunnypilot reasons about what a given vehicle is allowed to do?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0559-sunnypilot-outreach.md

Thanks for sunnypilot; an actively-maintained ADAS on real vehicles is exactly where a declarative ODD check has to prove its worth.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0560: F1TENTH (system + gym)

**Post to (Issue):** https://github.com/f1tenth/f1tenth_system/issues/new
**Title:** URML (open robot intent language): declared, validated racing intent on the car and in the gym (request for comment)

```
Hi F1TENTH maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. F1TENTH is a wonderful platform for teaching and researching autonomous racing, and URML is interesting at the intent layer above both the on-car system and the gym.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a racing task (follow the line, overtake within limits) is a goal plus constraints. URML expresses that goal, validates it against the car's declared capabilities and a safety envelope, then consumes the trajectory the planner produces. URML does not plan a racing line; it declares the goal and checks admissibility. And because URML is runtime-neutral, the same declared-and-validated intent applies whether the target is f1tenth_system on the car or f1tenth_gym in simulation -- a natural fit for a teaching loop that moves between the two.

Two real questions: (1) is a typed, validated intent layer (declare goal + constraints, validate, consume the trajectory) useful on the F1TENTH platform? (2) Does a runtime-neutral intent that targets both the car and the gym fit how F1TENTH is taught and researched?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0560-f1tenth-outreach.md

Thanks for F1TENTH; a platform that lives in both the classroom and the lab is exactly where a runtime-neutral intent layer is easiest to try.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0561: ForzaETH race_stack

**Post to (Issue):** https://github.com/ForzaETH/race_stack/issues/new
**Title:** URML (open robot intent language): declare and validate, then let the race stack plan (request for comment)

```
Hi ForzaETH maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. race_stack is a full autonomous-racing stack, and URML sits above a stack like this at the intent layer -- it declares the racing goal and constraints, validates admissibility, and consumes the trajectory the stack plans.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a racing objective is a goal plus constraints (stay on track, respect dynamic limits, overtake only where admissible). URML expresses that, validates it against the car's declared capabilities and an envelope, then consumes the planned trajectory. The stack keeps full ownership of how the line is computed and followed. The value URML adds is a typed, statically-checkable statement of what is allowed before the planner runs, not a competing planner.

Two real questions: (1) is a typed, validated intent layer (declare goal + constraints, validate admissibility, consume the trajectory) useful above a full racing stack? (2) Does URML's capability + safety-envelope model fit how race_stack bounds a maneuver?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0561-race-stack-outreach.md

Thanks for race_stack; a complete, real racing stack is the honest test of whether a declare-and-validate layer earns its place above the planner.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0562: NATURE stack

**Post to (Issue):** https://github.com/CGoodin/nature-stack/issues/new
**Title:** URML (open robot intent language): a typed off-road operating envelope above the planner (request for comment)

```
Hi NATURE stack maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. The NATURE stack handles off-road autonomous navigation over unstructured terrain, and URML is interesting at the intent layer above it.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: off-road navigation has hard operating bounds (slope, traversability, standoff). URML expresses the goal plus those bounds as a safety envelope, validates the intent against the platform's declared capabilities, then consumes the path the stack plans. The stack keeps ownership of terrain reasoning and planning. The contribution is a typed, declarative statement of where the vehicle is allowed to operate, checked before the planner commits.

Two real questions: (1) is a typed, validated intent layer (goal + off-road operating bounds, validated, then consume the path) useful above an off-road stack? (2) Does URML's safety-envelope model map onto how off-road operating bounds like slope and traversability are expressed?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0562-nature-stack-outreach.md

Thanks for the NATURE stack; unstructured terrain is where an explicit, typed operating envelope is hardest and most worth having.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0563: EasyNavigation

**Post to (Issue):** https://github.com/EasyNavigation/EasyNavigation/issues/new
**Title:** URML (open robot intent language): a typed front door to a navigation framework (request for comment)

```
Hi EasyNavigation maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. EasyNavigation is a modular navigation framework, and URML sits above a framework like this at the intent layer -- declare the goal, validate it, let the framework plan and execute.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a navigation task is a goal plus constraints (reach the pose, respect keep-out zones and speed limits). URML expresses that, validates it against the robot's declared capabilities and a safety envelope, then hands off to EasyNavigation to plan and execute. The framework keeps full ownership of planning and control. URML gives a navigation framework a typed, declarative, runtime-neutral way to state a goal and have it checked before planning -- including from a natural-language instruction.

Two real questions: (1) is a typed, validated intent layer (declare goal + constraints, validate, then navigate) a useful front door to EasyNavigation? (2) Does URML's capability + safety-envelope model fit how EasyNavigation bounds a navigation task?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0563-easynavigation-outreach.md

Thanks for EasyNavigation; a clean, modular nav framework is exactly the kind of thing a typed intent front door wants to sit above.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0564: AgOpenGPS

**Post to (Issue):** https://github.com/AgOpenGPS-Official/AgOpenGPS/issues/new
**Title:** URML (open robot intent language): a validated field-operation front door for auto-steer (request for comment)

```
Hi AgOpenGPS maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the machine's declared capabilities and a safety envelope, then dispatched. AgOpenGPS plans field coverage and steers an implement along guidance lines, and a field operation is exactly the kind of goal-plus-constraints intent URML is built to declare and validate.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a coverage task is a goal (cover this field, follow this pattern) plus constraints (implement width, headland, keep-out). URML expresses it, validates against the machine and implement's declared capabilities and an operating envelope, then consumes the guidance plan AgOpenGPS produces. AgOpenGPS keeps ownership of guidance and steering. Because URML's natural-language layer turns an instruction into validated intent, something like "cover the north field, 6 metre swath, skip the wet corner" can become a checked field operation -- the agricultural framing is a real vertical, not a metaphor.

Two real questions: (1) is a typed, validated intent layer (declare the field operation + constraints, validate, then guide) useful above AgOpenGPS? (2) Does URML's capability + safety-envelope model fit how a machine and implement's operating bounds are expressed?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0564-agopengps-outreach.md

Thanks for AgOpenGPS; a large, real auto-steer community is exactly where a natural-language-to-validated-field-operation path would be worth getting right.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0565: GEMstack

**Post to (Issue):** https://github.com/krishauser/GEMstack/issues/new
**Title:** URML (open robot intent language): a typed intent and ODD layer for a teaching AV stack (request for comment)

```
Hi GEMstack maintainer,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the vehicle's declared capabilities and a safety envelope, then dispatched. GEMstack teaches the full autonomous-driving pipeline end to end, and URML is a good pedagogical companion at the top of that pipeline.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: GEMstack teaches the whole pipeline. URML adds a small, readable layer at the top -- declare the driving goal and the operating bounds (an ODD), validate against the vehicle's declared capabilities and a safety envelope, then let the stack plan and execute. For students it makes "what are we allowed to do, and why was this rejected" explicit and checkable. And URML's natural-language layer lets a teaching scenario start from an English instruction and show exactly how it becomes a typed, validated plan, which is a useful thing to make visible in a course.

Two real questions: (1) is a typed, validated intent + ODD layer a useful teaching companion above the GEMstack pipeline? (2) Does showing the natural-language to validated-intent path add pedagogical value in an AV course?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0565-gemstack-outreach.md

Thanks for GEMstack; a teaching stack is exactly where making intent and its bounds explicit pays off for the people learning the pipeline.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
