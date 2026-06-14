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

# Move #52 post bodies: the education / competition wave (round 2)

Ten targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(state each repo's actual license, never ask; GPL and non-standard licenses:
no code reuse). AI-assisted-authoring disclosure up front. Titles carry no
em-dash. Framing: URML is the typed-intent + English front door for student
robots, and the consume-the-output layer for the motion/vision tools (URML
does not plan, optimize, or do vision; it declares, validates, and consumes).

---

## RFC-0566: FTC Robot Controller (anchor)

**Post to (Issue):** https://github.com/FIRST-Tech-Challenge/FtcRobotController/issues/new
**Title:** URML (open robot intent language): a typed, English-friendly intent layer above an FTC op-mode (request for comment)

```
Hi FTC SDK maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction (including an English one) becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Tens of thousands of students program competition robots with the FTC SDK each season, and URML is interesting as a teaching companion at the top of an op-mode.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: students write op-modes against the SDK. URML adds a small layer at the top -- a declared intent (drive here, grab that, within these limits) that is checked against the robot's declared capabilities before it runs, and that can start from an English sentence. The SDK stays the runtime; URML makes "what did we ask the robot to do, and why was that rejected" explicit and checkable, which is exactly the kind of thing that helps a student team reason about their robot. URML already has an educational profile direction, so FTC is a natural place to test whether this earns its keep.

Two real questions: (1) is a typed, validated intent layer (declare intent, check against the robot's capabilities, optionally from English) a useful teaching companion above an FTC op-mode? (2) Does URML's capability manifest map onto how an FTC robot's configuration is described?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0566-ftc-robotcontroller-outreach.md

Thanks for the FTC SDK; it is one of the largest on-ramps into robotics there is, and that is exactly where making intent explicit could help students most.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0567: PathPlanner

**Post to (Issue):** https://github.com/mjansen4857/pathplanner/issues/new
**Title:** URML (open robot intent language): declare and validate, then consume the PathPlanner path (request for comment)

```
Hi PathPlanner maintainer,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. PathPlanner plans and follows paths for FRC robots, and URML sits above a planner like this at the intent layer.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a driving task is a goal plus constraints. URML expresses it, validates against the robot's declared capabilities and an envelope, then consumes the path PathPlanner produces. URML does not plan; it declares, validates, and consumes. And because URML's natural-language layer turns an instruction into validated intent, a student could express a routine in plain language and have it become a checked goal handed to PathPlanner.

Two real questions: (1) is a typed, validated intent layer (declare goal + constraints, validate, consume the path) useful above PathPlanner? (2) Does URML's capability + safety-envelope model fit how an FRC robot's limits are described?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0567-pathplanner-outreach.md

Thanks for PathPlanner; it is a staple of FRC autonomous, and a typed front door above it could make the intent behind a routine clearer to a team.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0568: PhotonVision

**Post to (Issue):** https://github.com/PhotonVision/photonvision/issues/new
**Title:** URML (open robot intent language): consuming a PhotonVision estimate as a fact an intent conditions on (request for comment)

```
Hi PhotonVision maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML does not do vision; it consumes the estimate. A pose or target from PhotonVision is exactly the kind of fact a URML intent can condition on and validate against before acting. This is a consume-the-estimate note (cross-citation only, since PhotonVision is GPL-3.0).

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: PhotonVision delivers a pose or target estimate. URML treats that as an input fact -- an intent like "align to the tag, then place" can be expressed, validated against the robot's capabilities and a safety envelope, and conditioned on the estimate PhotonVision provides. URML stays out of perception entirely; given the GPL-3.0 license this proposes no shared code, only a clean boundary.

Two real questions: (1) is "PhotonVision produces the estimate, URML consumes it as a fact an intent conditions on" a sensible boundary? (2) Does a typed, validated intent layer that conditions on a vision estimate fit how teams use PhotonVision?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0568-photonvision-outreach.md

Thanks for PhotonVision; it does the hard perception work, and a clean line between the estimate and the intent that uses it seems worth drawing.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0569: Choreo

**Post to (Issue):** https://github.com/SleipnirGroup/Choreo/issues/new
**Title:** URML (open robot intent language): declare and validate, then consume the Choreo trajectory (request for comment)

```
Hi Choreo maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Choreo generates time-optimal trajectories for FRC subject to a robot's dynamic constraints, and URML sits above a trajectory tool like this at the intent layer.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: URML expresses the goal plus constraints, validates them against the robot's declared capabilities and an envelope, then consumes the trajectory Choreo optimizes. URML does not optimize trajectories; it declares, validates, and consumes. The contribution is a typed, checkable statement of what is allowed before the optimizer runs, not a competing optimizer.

Two real questions: (1) is a typed, validated intent layer (declare goal + constraints, validate admissibility, consume the optimized trajectory) useful above Choreo? (2) Does URML's capability + safety-envelope model align with the dynamic constraints Choreo already takes?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0569-choreo-outreach.md

Thanks for Choreo; time-optimal trajectory generation is exactly the kind of thing an intent layer should sit above and never try to replace.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0570: Road Runner

**Post to (Issue):** https://github.com/acmerobotics/road-runner/issues/new
**Title:** URML (open robot intent language): declare and validate, then consume the Road Runner trajectory (request for comment)

```
Hi Road Runner maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Road Runner plans motion for FTC robots, and URML sits above a motion-planning library at the intent layer.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: an autonomous routine is a goal plus constraints. URML expresses it, validates against the robot's declared capabilities and an envelope, then consumes the trajectory Road Runner produces. URML does not plan; it declares, validates, and consumes. And because URML's natural-language layer turns an instruction into validated intent, a student could state an autonomous routine in plain language and have it become a checked goal handed to Road Runner.

Two real questions: (1) is a typed, validated intent layer (declare goal + constraints, validate, consume the trajectory) useful above Road Runner? (2) Does URML's capability + safety-envelope model fit how an FTC robot's limits are described?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0570-road-runner-outreach.md

Thanks for Road Runner; it powers a lot of FTC autonomous, and a typed intent front door above it could help students reason about what their routine is really asking for.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0571: KIPR libwallaby

**Post to (Issue):** https://github.com/kipr/libwallaby/issues/new
**Title:** URML (open robot intent language): a typed, English-friendly intent layer above libwallaby (request for comment)

```
Hi KIPR maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction (including an English one) becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. libwallaby is the control library behind the Wombat/Wallaby controllers used in Botball, and URML is interesting as a teaching companion above it. This is a consume / front-door note (cross-citation only, since libwallaby is GPL-3.0).

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: students program against libwallaby. URML adds a small layer at the top -- a declared intent checked against the robot's declared capabilities before it runs, optionally starting from an English sentence. libwallaby stays the runtime; URML makes the intent and its validation explicit, which suits a teaching context. Given the GPL-3.0 license this proposes no shared code, only a boundary.

Two real questions: (1) is a typed, validated intent layer (declare intent, check against capabilities, optionally from English) a useful teaching companion above libwallaby? (2) Does URML's capability manifest map onto how a Wombat/Wallaby robot is configured?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0571-libwallaby-outreach.md

Thanks for libwallaby; Botball is a great on-ramp, and making intent explicit is the kind of thing that helps newcomers reason about their robot.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0572: GoPiGo3

**Post to (Issue):** https://github.com/DexterInd/GoPiGo3/issues/new
**Title:** URML (open robot intent language): an English-to-validated-intent front door for the GoPiGo3 (request for comment)

```
Hi GoPiGo3 maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an English instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. The GoPiGo3 is a lovely, clear beginner robot, and a simple well-defined platform is an ideal place to show the natural-language-to-validated-intent path end to end.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the GoPiGo3 has a small, clear set of capabilities (drive, turn, sensors). That maps cleanly onto a URML capability manifest, so "drive forward two metres, then stop if you see an obstacle" can become a typed, validated intent and then GoPiGo3 API calls. URML adds the typed validation and the English layer; the GoPiGo3 API stays the runtime. For a learner, seeing an instruction become a checked plan -- and seeing why an impossible instruction is rejected -- is exactly the kind of thing a small platform makes vivid.

Two real questions: (1) is an English-to-validated-intent front door useful for a beginner robot like the GoPiGo3? (2) Does the GoPiGo3's capability set map cleanly onto a URML capability manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0572-gopigo3-outreach.md

Thanks for the GoPiGo3; an approachable robot with a clean API is exactly where an English front door is easiest to make real.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0573: Raspberry Pi Foundation Blockly

**Post to (Issue):** https://github.com/RaspberryPiFoundation/blockly/issues/new
**Title:** URML (open robot intent language): a typed, validated compile target for a robotics block palette (request for comment)

```
Hi Raspberry Pi Foundation Blockly maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction (including an English one) becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Blockly and URML share a goal -- lower the barrier to telling a machine what to do -- and the boundary between block-based programming and a typed intent language is interesting. This is a conceptual-peer note, not an integration ask.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two ways to lower the barrier: Blockly lets a learner assemble a program from blocks. URML lets a learner (or an LLM) express a robot intent in a small typed language, optionally from English, and validates it against the robot's declared capabilities before it runs. For robotics specifically, a block palette could emit URML as its target representation, getting typed validation and a capability check for free -- the "is this actually possible on this robot, and why not" check, in typed form.

Two real questions: (1) for robotics use, is a typed, validated intent representation (with a capability check) a useful compile target for a block palette? (2) Is the block-based / typed-intent boundary an interesting comparison for learner-facing robotics tools?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0573-blockly-outreach.md

Thanks for your work on Blockly; block-based programming has opened robotics to a lot of learners, and the seam with a validated intent layer feels worth comparing notes on.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0574: Robocode Tank Royale

**Post to (Issue):** https://github.com/robocode-dev/tank-royale/issues/new
**Title:** URML (open robot intent language): declarative intent as a teaching on-ramp alongside imperative bots (request for comment)

```
Hi Tank Royale maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a goal becomes a typed primitive, validated against the actor's declared capabilities, then dispatched. Tank Royale is a programming game widely used to teach programming, and while a game bot is virtual, the shared idea is interesting: a declarative, checkable way to state what a bot should try to do. This is a conceptual note, not an integration ask.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The idea: a Tank Royale bot is written imperatively against an API. URML's angle is a declarative, typed intent layer that states a goal and is validated against the actor's declared capabilities. For a teaching game, an optional declarative-intent mode could be a gentle on-ramp before learners write full imperative bots, and it makes "what is this bot allowed to do" explicit. This is exploratory; a battle game is not a physical robot, and the value, if any, is pedagogical.

Two real questions: (1) is a declarative, typed intent layer an interesting on-ramp or teaching aid alongside imperative bot programming? (2) Does "declare what the bot should try to do, validated against its capabilities" map onto how Tank Royale bots are written?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0574-tank-royale-outreach.md

Thanks for Tank Royale; carrying the Robocode tradition forward is great, and the declarative-on-ramp idea felt worth floating with you.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0575: iRobot Create 3

**Post to (Issue):** https://github.com/iRobotEducation/create3_docs/issues/new
**Title:** URML (open robot intent language): an English front door over the Create 3 ROS 2 interface (request for comment)

```
Hi iRobot Education maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an English instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. The Create 3 is a clean, well-documented educational robot with a ROS 2 interface, which makes it an ideal place to show the natural-language-to-validated-intent path.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the Create 3 exposes a well-defined set of actions over ROS 2. That maps onto a URML capability manifest, so "drive a square, then dock" can become a typed, validated intent that dispatches through the Create 3's existing ROS 2 interface. URML adds the typed validation and the English layer; the Create 3 stays the runtime. As a teaching robot with strong docs, it is a natural place to make the intent-and-validation story visible to learners.

Two real questions: (1) is an English-to-validated-intent front door useful for the Create 3 in an educational setting? (2) Does the Create 3's ROS 2 action set map cleanly onto a URML capability manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0575-create3-docs-outreach.md

Thanks for the Create 3 docs; a well-documented ROS 2 teaching robot is exactly where an English front door can be both useful and honest about what it does.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
