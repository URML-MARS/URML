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

# Move #54 post bodies: the lab-automation / scientific-robotics wave

Nine targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(MIT/BSD: state it, never ask; nimsos has no license file: say so, no ask).
AI-assisted-authoring disclosure up front. Titles carry no em-dash. AD-SDL
WEI + MADSci are one post (on MADSci, referencing WEI). Honest framing: URML's
MODEL transfers to lab automation (workcell/deck/labware as the capability
manifest); the posts ask whether it maps, they do not claim URML already does
lab automation. Bodies are varied per target.

---

## RFC-0587: PyLabRobot (anchor)

**Post to (Issue):** https://github.com/PyLabRobot/pylabrobot/issues/new
**Title:** URML (open robot intent language): is a deck/labware model a capability manifest? (request for comment)

```
Hi PyLabRobot maintainers,

I lead a small Apache-2.0 project, URML (urml.dev), that describes robot intent: an instruction becomes a typed primitive, validated against a declared capability manifest and a safety envelope, then dispatched to whatever executes it. PyLabRobot caught my attention because it is built on the same instinct from the other end: one hardware-agnostic command set over many instruments, against a structured model of the deck and labware. The overlap is close enough that I wanted to ask directly.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The specific question is structural. PyLabRobot abstracts instruments behind a universal command set plus a deck/labware model; URML abstracts robots behind typed primitives plus a capability manifest. Is your deck/labware description, in effect, the lab-automation form of a capability manifest, such that a high-level protocol could be checked against what the configured deck can actually do before any command is issued? If so, the only thing URML would add is that pre-dispatch validation gate (optionally fed by a natural-language instruction); the drivers and the command set would stay entirely yours. If your command set already carries those guarantees, that is a useful answer too.

Two real questions: (1) is the deck/labware model close enough to a capability manifest that validating a protocol against it before dispatch would be meaningful? (2) Is a typed, statically-validated intent layer above the universal command set useful, or redundant with what PyLabRobot already checks?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0587-pylabrobot-outreach.md

Thanks for PyLabRobot; a genuinely hardware-agnostic lab SDK is rare, and it is the closest structural cousin to URML I have come across.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0588: AD-SDL (MADSci / WEI)

**Post to (Issue):** https://github.com/AD-SDL/MADSci/issues/new
**Title:** URML (open robot intent language): a per-node validation step under a workcell scheduler (request for comment)

```
Hi AD-SDL maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a typed action, validated against a declared capability manifest and a safety envelope, then dispatched. MADSci (and WEI before it) orchestrate workflows across the instruments of a workcell, which is a layer above where URML sits. This is a request for comment about where the two meet.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: MADSci/WEI schedule a workflow across nodes; each node advertises what it can do. URML's candidate contribution is the typed, pre-dispatch validation of each per-node step, checked against that node's advertised capabilities and limits before the scheduler issues it. The scheduling, recovery, and campaign logic stay entirely with MADSci/WEI; URML would only be the gate on each step. Two pieces line up especially well: a node's capability advertisement maps toward a URML capability manifest, and a workcell of many nodes maps onto URML's multi-robot roster.

Two real questions: (1) does a typed per-node validation step fit how MADSci/WEI dispatch a workflow, or is node-level checking already handled? (2) Does a node's capability advertisement map cleanly toward a capability manifest, and a workcell onto a fleet roster?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0588-ad-sdl-outreach.md

Thanks for the AD-SDL stack; an open, national-lab workcell-orchestration layer is exactly the kind of peer a per-node intent gate wants to understand its boundary with.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0589: Aquarium

**Post to (Issue):** https://github.com/aquariumbio/aquarium/issues/new
**Title:** URML (open robot intent language): comparing two notions of a typed operation (request for comment)

```
Hi Aquarium maintainers,

What brought me here is the typed unit operation. URML (urml.dev, a small Apache-2.0 robot-intent language) represents what a robot should do as a small set of typed operations with declared, checkable arguments; Aquarium represents a protocol as typed unit operations with declared inputs and outputs over samples and labware. Two domains, the same instinct that operations should be typed. This is a request for comment, not an integration ask.

Nothing here asks the project to adopt, host, or maintain anything.

Where the two might meet is narrow and specific: on the steps that touch a physical instrument or robot, URML's per-step check (does the configured equipment support this operation, within these limits) could complement Aquarium's typed-IO model. Aquarium would keep the protocol, the sample tracking, and the workflow; the only candidate addition is a pre-dispatch capability check on equipment-facing steps. It is entirely possible Aquarium's own typing already covers that, which is part of what I am asking.

Two real questions: (1) do Aquarium's typed unit operations and URML's typed primitives describe the same kind of thing closely enough that a shared capability check on equipment-facing steps would help? (2) Is a pre-dispatch validation against declared equipment capabilities meaningful in Aquarium's model, or already covered?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0589-aquarium-outreach.md

Thanks for Aquarium; a lab OS built around typed protocols is a thoughtful design, and the typed-operation parallel felt worth comparing notes on.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0590: Bluesky

**Post to (Issue):** https://github.com/bluesky/bluesky/issues/new
**Title:** URML (open robot intent language): two declare-then-execute loops, one validation question (request for comment)

```
Hi Bluesky maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent, and the reason I am writing to Bluesky specifically is that we share a shape. A Bluesky plan declares what an experiment should do, and the run engine executes it against hardware. A URML program declares what a robot should do, the validator checks it, and the runtime dispatches it. Same declare-then-execute loop, different domain. This is a request for comment about the one place they differ.

Nothing here asks the project to adopt, host, or maintain anything.

The difference URML leans on is an explicit pre-dispatch validation pass: before a plan runs, it is checked against a declared device capability manifest and operating envelope. Bluesky already owns experiment specification and execution at beamlines and labs, and does it well, so I am not proposing to replace the run engine. The honest question is only whether a typed capability/envelope check ahead of a plan is meaningful for instrument admissibility and safety, or whether Bluesky's design already places that responsibility elsewhere.

Two real questions: (1) is a pre-dispatch validation pass (a plan checked against declared instrument capabilities and limits) a meaningful addition to the plan/run-engine model? (2) Do Bluesky's device abstractions map toward a capability manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0590-bluesky-outreach.md

Thanks for Bluesky; the declarative-plan design is exactly the kind of thing that made me think the validation question was worth asking the people who built it.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0591: AlabOS

**Post to (Issue):** https://github.com/CederGroupHub/alabos/issues/new
**Title:** URML (open robot intent language): a typed per-task check under the A-Lab scheduler (request for comment)

```
Hi AlabOS maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a typed action validated against a declared capability manifest and a safety envelope, then dispatched. AlabOS maps task graphs onto the A-Lab's devices and runs synthesis-and-characterization campaigns end to end, which sits a layer above URML. This is a request for comment about the seam.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: AlabOS schedules a task graph across devices. URML's candidate role is the typed, pre-dispatch validation of each device-facing task, checked against that device's declared capabilities and limits before AlabOS sends it. The orchestration, recovery, and campaign logic stay with AlabOS; the only addition is the per-task gate. AlabOS already describes its devices and their tasks, and that description maps toward a URML capability manifest, which is what a per-task check would validate against.

Two real questions: (1) is a typed per-task validation step useful in the AlabOS scheduling model, or is device-level checking already handled? (2) Do AlabOS device/task definitions map toward a capability manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0591-alabos-outreach.md

Thanks for AlabOS; a real autonomous-materials lab running end to end is exactly where a per-task admissibility check earns or fails to earn its place, and you would know which.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0592: PyHamilton

**Post to (Issue):** https://github.com/dgretton/pyhamilton/issues/new
**Title:** URML (open robot intent language): a typed intent layer above PyHamilton (request for comment)

```
Hi PyHamilton maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against a declared capability manifest and a safety envelope, then dispatched to whatever executes it. PyHamilton is exactly the kind of concrete executor URML is designed to dispatch to: a real interface to Hamilton liquid handlers that people write real protocols against. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: a protocol step, once checked against the configured deck's capabilities and limits, becomes PyHamilton calls. URML would add the typed pre-dispatch check and, through its natural-language layer, an optional plain-language front door; PyHamilton stays the Hamilton interface. A PyHamilton script already assumes a particular deck layout and labware, which is the lab-automation analogue of the capability manifest a step would be validated against.

Two real questions: (1) is a typed, validated intent layer (a step checked against the configured deck before it becomes PyHamilton calls) useful above PyHamilton? (2) Could a deck/labware configuration serve as the capability manifest the validation checks against?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0592-pyhamilton-outreach.md

Thanks for PyHamilton; a widely-used, no-nonsense interface to real liquid handlers is a good honest test of whether a typed intent layer above it pulls its weight.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0593: Pycro-Manager

**Post to (Issue):** https://github.com/micro-manager/pycro-manager/issues/new
**Title:** URML (open robot intent language): a validated acquisition instruction for a microscope (request for comment)

```
Hi Pycro-Manager maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a typed instruction validated against a declared capability manifest and a safety envelope, then dispatched. A microscope is an instrument with a well-defined set of capabilities and limits, which is the kind of thing a capability manifest describes, so Pycro-Manager seemed worth asking about. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: an acquisition is a declared intent (image this region, at these channels, within these stage and exposure limits). URML could express that as a typed instruction, validate it against the scope's declared capabilities and limits, then dispatch it through Pycro-Manager. Pycro-Manager stays the microscope interface; URML adds the typed pre-dispatch check and an optional natural-language path. The scope's available channels, stage travel, and objectives form the capability set an instruction would be checked against.

Two real questions: (1) is a typed, validated instruction layer (an acquisition checked against the scope's declared capabilities before dispatch) useful above Pycro-Manager? (2) Does a microscope's configuration map onto a capability manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0593-pycro-manager-outreach.md

Thanks for Pycro-Manager; reproducible scripted acquisition is exactly the setting where stating an instruction's limits up front and checking them might be worth something.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0594: Self-Driving Lab Demo

**Post to (Issue):** https://github.com/sparks-baird/self-driving-lab-demo/issues/new
**Title:** URML (open robot intent language): making the validated-intent step visible in a teaching SDL (request for comment)

```
Hi Self-Driving Lab Demo maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction (including a plain-language one) becomes a typed primitive, validated against a declared capability manifest and a safety envelope, then dispatched. Because your project exists to teach the self-driving-lab loop accessibly, it seemed like a good place to ask whether making the validated-intent step explicit helps learners. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The angle is the "run it on hardware" step of the loop. URML would declare that action as typed intent, validate it against the demo rig's declared capabilities and limits, then dispatch. For a learner, seeing why an out-of-range action is refused is exactly the kind of thing a teaching framework can make vivid, and URML's natural-language layer lets a demo start from a plain instruction and show how it becomes a checked, runnable action.

Two real questions: (1) is a typed, validated intent step (the actuation checked against the rig's declared capabilities) a useful thing to make explicit in a teaching SDL loop? (2) Does showing the natural-language to validated-intent path add pedagogical value here?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0594-self-driving-lab-demo-outreach.md

Thanks for the demo; lowering the barrier to the self-driving-lab loop is genuinely valuable, and making the intent-and-validation step legible feels like it fits that goal.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0595: NIMS-OS

**Post to (Issue):** https://github.com/nimsos-dev/nimsos/issues/new
**Title:** URML (open robot intent language): a neutral typed action at the instrument boundary (request for comment)

```
Hi NIMS-OS maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a typed action validated against a declared capability manifest and a safety envelope, then dispatched. NIMS-OS closes the loop between an AI decision layer and robotic experimental equipment, and one detail stood out: the file-exchange path that lets non-Python instruments participate. That boundary is exactly where a small, neutral, typed action representation tends to earn its keep. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: NIMS-OS decides the next experiment and drives the equipment. URML's candidate role is the typed, pre-dispatch validation of the equipment-facing action, checked against that equipment's declared capabilities and limits before NIMS-OS issues it; the AI loop and the experiment design stay with NIMS-OS. And because NIMS-OS already crosses into non-Python instruments via file exchange, a small typed runtime-neutral action representation is a natural candidate for what travels across that boundary, with a capability manifest as what it is checked against.

Two real questions: (1) is a typed, validated device action useful in the NIMS-OS loop, or is equipment-level checking already handled? (2) Could a runtime-neutral typed action representation help at the file-exchange boundary to non-Python instruments?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0595-nimsos-outreach.md

Thanks for NIMS-OS; an autonomous-experiment loop that deliberately reaches non-Python instruments is exactly where a neutral typed action representation is most interesting to think about.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
