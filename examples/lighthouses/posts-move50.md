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

# Move #50 post bodies: the HRI / conversational / robot-data wave

Nine targets, all GitHub Issues. Post under idoco2003. No license-ask
anywhere (state each repo's actual license, never ask; ROSGPT has no license
file, so say nothing about licensing; vhtoolkit is a custom USC license, no
code reuse). AI-assisted-authoring disclosure up front. Titles carry no
em-dash. Two sub-clusters: conversational NL-to-robot peers (ROSGPT anchor,
DialoStack, retico-core, Furhat, vhtoolkit) and robot-data / audit-trail
(ReductStore, Forge, ARES, rosbag2_composable_recorder).

---

## RFC-0549: ROSGPT (anchor)

**Post to (Issue):** https://github.com/aniskoubaa/rosgpt/issues/new
**Title:** URML (open robot intent language): a typed, validated layer between an LLM and ROS (request for comment)

```
Hi Anis,

ROSGPT is one of the clearest demonstrations that natural language can drive a robot, and it is the project URML (urml.dev) most resembles in spirit. URML is a small, Apache-2.0 language for robot intent: a natural-language instruction becomes a typed primitive, validated against the robot's declared capabilities and an active safety envelope, then dispatched. This is a language-to-language note about where the two meet.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The same seam, with a gate: ROSGPT turns language into ROS commands. URML turns language into a typed primitive and runs five validation passes (argument typing, capability check against a manifest, safety-envelope check, variable bindings, compliance policy) before anything is dispatched. One natural composition: an LLM proposes intent (ROSGPT-style), URML is the intermediate representation that is statically checked before it reaches ROS. The LLM stays free to be creative; the validator refuses anything the robot cannot safely do. And because URML validates against a capability manifest rather than ROS specifics, the same validated intent can target PX4, a vendor SDK, or a non-ROS substrate.

Two real questions: (1) is a typed, statically-validated intermediate representation a useful layer between an LLM and ROS? (2) Does five-pass validation against a manifest + safety envelope address the "the LLM emitted an unsafe or unsupported command" failure mode that any language-to-ROS bridge has to handle somewhere?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0549-rosgpt-outreach.md

Thanks for ROSGPT; it made the natural-language-to-robot case early and well, and the validation seam is exactly the part worth comparing notes on.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0550: DialoStack

**Post to (Issue):** https://github.com/aquintan4/DialoStack/issues/new
**Title:** URML (open robot intent language): a validated intent target for an LLM dialogue layer (request for comment)

```
Hi DialoStack maintainer,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. DialoStack connects an LLM dialogue layer to ROS 2, turning a conversation into robot actions; URML sits right at that handoff.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: DialoStack turns a conversation into ROS 2 actions. URML is the intermediate, statically-checkable representation between dialogue and execution -- the dialogue layer emits URML intent, the validator checks it (argument typing, capability, safety envelope, bindings, policy), then it dispatches. The dialogue stays the creative part; the validator is the gate. Because URML validates against a capability manifest rather than ROS specifics, the same dialogue front end can also drive non-ROS substrates.

Two real questions: (1) is a typed, validated intent representation a useful target for an LLM dialogue layer that drives ROS 2? (2) Does capability + safety-envelope validation address the "the dialogue produced an action the robot can't safely do" case?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0550-dialostack-outreach.md

Thanks for DialoStack; the dialogue-to-ROS2 handoff is exactly where a validated intent representation earns its place.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0551: retico-core

**Post to (Issue):** https://github.com/retico-team/retico-core/issues/new
**Title:** URML (open robot intent language): the validated intent an incremental dialogue commits to (request for comment)

```
Hi retico-core maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. retico-core processes spoken dialogue incrementally, recognizing intent as it forms; URML is a peer at the next layer down.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The layering: retico recognizes intent incrementally and responsively. URML is what a recognized intent commits to -- a typed primitive checked against a capability manifest + safety envelope before it reaches the robot. The incremental layer stays fast; the commit is statically validated. retico-core is about understanding language in real time; URML is about turning a recognized intent into something safe and runnable.

Two real questions: (1) is "retico recognizes the intent incrementally, URML is the validated representation it commits to" a sensible layering for a dialogue-driven robot? (2) Does capability + safety-envelope validation fit where an incremental dialogue system hands off to actuation?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0551-retico-core-outreach.md

Thanks for retico-core; incremental dialogue is a genuinely hard problem done well, and the commit-to-actuation seam is the interesting boundary with a validated intent layer.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0552: Furhat skills

**Post to (Issue):** https://github.com/FurhatRobotics/example-skills/issues/new
**Title:** URML (open robot intent language): a validated bridge when a Furhat skill drives a physical robot (request for comment)

```
Hi Furhat maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Furhat is a social conversational robot, and URML is the validated-intent layer for physical robot action -- so this is a narrow, honest note about one possible seam.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The seam: a Furhat skill owns the social interaction. If a skill ever triggers a physical action on a connected robot (a mobile base, an arm, a device), URML is the typed, validated representation of that action -- checked against the robot's capabilities and a safety envelope before it runs. Furhat stays the conversational brain; URML is the gate on the physical limb. If Furhat skills never drive an external physical robot, then the seam is empty and this is just a friendly hello -- which is why the first question is genuine.

Two real questions: (1) do Furhat skills ever drive an external physical robot as part of an interaction? (2) If so, is a typed, validated intent layer between a skill and that physical robot useful?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0552-furhat-example-skills-outreach.md

Thanks for the Furhat skills; social robotics is a different world from actuation, and I am genuinely curious whether the two ever touch in your deployments.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0553: USC-ICT Virtual Human Toolkit

**Post to (Issue):** https://github.com/USC-ICT/vhtoolkit/issues/new
**Title:** URML (open robot intent language): comparing embodied-agent intent representations (request for comment)

```
Hi Virtual Human Toolkit maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against a declared capability set and a safety envelope, then dispatched. The Virtual Human Toolkit builds embodied conversational virtual humans. URML represents intent for physical embodied agents, and the shared question is interesting enough to ask about. This is a conceptual-peer note, with no code reuse (the toolkit is under a custom USC license).

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two embodiments, one intent question: virtual humans and physical robots both turn understanding into embodied action. URML's contribution is a typed intent representation validated against a declared capability set before action. For a virtual human the "capabilities" are different, but the idea of a checkable intent representation may transfer. This is research-scope; I am not claiming URML drives a virtual human today.

Two real questions: (1) does a typed, validatable intent representation map onto how the toolkit drives a virtual human's embodied behavior? (2) Is the physical-robot / virtual-human intent boundary an interesting comparison?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0553-vhtoolkit-outreach.md

Thanks for the Virtual Human Toolkit; the intent-representation question sits right between your world and the physical-robot one, which is why I wanted to compare notes.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0554: ReductStore

**Post to (Issue):** https://github.com/reductstore/reductstore/issues/new
**Title:** URML (open robot intent language): validated-intent audit records as a robotics time series (request for comment)

```
Hi ReductStore maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Every validated dispatch emits a structured audit record, and that record is a natural data source for a robotics time-series store like ReductStore.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: URML validates intent before dispatch and records what was validated and why -- the intent, the resolved arguments, the verdict, the safety envelope it was checked against, all timestamped and typed. That stream is exactly the kind of robotics time series ReductStore stores, and putting it next to sensor and telemetry data gives a queryable record of intent, not just outcome. Because the records are typed and carry the verdict, retention and labeling can key on intent (every grasp, every envelope rejection), which is hard to recover from raw telemetry alone.

Two real questions: (1) is a typed validated-intent audit record a useful first-class time series alongside sensor/telemetry data? (2) Does intent-keyed retention/labeling fit ReductStore's model?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0554-reductstore-outreach.md

Thanks for ReductStore; a store built for unstructured robotics data is exactly where an intent record wants to live next to the signals it explains.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0555: Forge

**Post to (Issue):** https://github.com/arpitg1304/forge/issues/new
**Title:** URML (open robot intent language): validated-intent records as a dataset annotation channel (request for comment)

```
Hi Forge maintainer,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Forge converts between robot-learning data formats (RLDS, LeRobot, rosbag), and URML is interesting as an annotation source for those datasets.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a robot-learning episode records what happened. URML's audit trail records the typed intent that drove it and the validation verdict. Aligning the two gives episodes a structured intent label without hand-annotation -- exactly the kind of label robot-learning datasets are usually missing. Forge already moves between formats; URML intent records could ride along as an annotation channel. The intent vocabulary is small and typed, so the annotation stays compact and consistent across robots and substrates.

Two real questions: (1) is a typed validated-intent record a useful annotation channel when converting robot-learning datasets? (2) Does aligning intent records to RLDS/LeRobot/rosbag episodes fit Forge's model?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0555-forge-outreach.md

Thanks for Forge; format conversion is the natural place to thread a consistent intent annotation through the robot-learning data world.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0556: ARES

**Post to (Issue):** https://github.com/jacobphillips99/ares/issues/new
**Title:** URML (open robot intent language): structured intent-and-verdict annotation over robot episodes (request for comment)

```
Hi ARES maintainer,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. ARES ingests, annotates, and analyzes robot-episode data, and URML is the closest intent peer to that work.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: ARES ingests and annotates robot episodes. URML's audit trail is a typed record of the intent behind each episode plus the validation verdict (admissible, rejected, why). As an annotation layer it turns "what the robot did" into "what it was asked to do and whether that was allowed" -- the harder half to recover after the fact. Because the records are typed and tied to a capability manifest + safety envelope, episodes become queryable by intent and by rejection reason, not just by raw signal.

Two real questions: (1) is a typed validated-intent record a useful structured annotation layer over ingested robot episodes? (2) Does intent-and-verdict annotation fit how ARES models episode metadata?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0556-ares-outreach.md

Thanks for ARES; an episode-analysis platform is exactly where a typed intent-and-verdict layer makes the data answer questions it otherwise can't.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0557: rosbag2_composable_recorder

**Post to (Issue):** https://github.com/berndpfrommer/rosbag2_composable_recorder/issues/new
**Title:** URML (open robot intent language): a validated-intent companion channel to a rosbag2 recording (request for comment)

```
Hi Bernd,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Your composable rosbag2 recorder captures the signals; URML's validated-intent audit trail is a natural companion to that recording.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a rosbag2 recording captures topics over time. A URML audit record captures the validated intent that produced that window of behavior -- typed, with the verdict. Recorded together (the record referencing the bag, or rolled into a companion stream), a bag becomes self-describing about intent, not just signal. A composable recorder is the right place to add an optional intent-record channel without coupling it to any specific stack.

Two real questions: (1) is a typed validated-intent record a useful companion channel to a rosbag2 recording? (2) Does adding an optional intent-record stream fit a composable recorder's design?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0557-rosbag2-composable-recorder-outreach.md

Thanks for the composable recorder; the composability is exactly what makes an optional intent channel feasible without forcing it on anyone.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
