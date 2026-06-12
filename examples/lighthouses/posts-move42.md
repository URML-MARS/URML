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

# Move #42 post bodies: the teleoperation / data-collection wave

Six targets, all GitHub Issues (none of these repos have Discussions). Post
under idoco2003. No license-ask (all permissive). AI-assisted-authoring
disclosure up front.

---

## RFC-0479: GELLO

**Post to (Issue):** https://github.com/wuphilipp/gello_software/issues/new
**Title:** URML (open robot intent language): a validated shared-autonomy / typed-intent layer for GELLO — request for comment

```
Hi GELLO community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person expresses an intent, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. GELLO is a default way to teleoperate and collect demonstrations, and URML is interesting to a teleop / data-collection rig in two ways that don't compete with manual control.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams: (1) shared-autonomy handoff -- the operator stays in control by default, and when they issue a high-level command ("pick that up", "move to the bin") URML validates it against the robot's capabilities + envelope and dispatches, with teleop as the correction path; URML adds a capability/envelope gate a raw teleop stream doesn't have. (2) typed-intent annotation -- each demonstration segment is labelled with the URML primitive it represents (grasp($obj), move_to(bin)), so a recorded demo carries a typed, validatable intent next to the trajectory: structured supervision a downstream policy can learn from, and a record the validator can check against the manifest.

Two real questions: (1) Is a validated shared-autonomy handoff interesting on a GELLO rig? (2) Is labelling demonstration segments with a typed URML primitive useful for the data you collect -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0479-gello-outreach.md

Thanks for GELLO; a low-cost, widely-used teleop rig is exactly where this kind of validated-handoff / typed-demo question should be asked.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0480: oculus_reader

**Post to (Issue):** https://github.com/rail-berkeley/oculus_reader/issues/new
**Title:** URML (open robot intent language): mapping a controller action to a validated intent — request for comment

```
Hi oculus_reader community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. oculus_reader is the VR input front-end many manipulation teleop rigs build on, and URML is interesting to it as the validated layer a button-press can trigger.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The idea: a mapped controller action ("grip -> grasp the detected object", "A -> return home") becomes a high-level URML primitive that is validated against the robot's declared capabilities and safety envelope before it actuates. Continuous pose teleop stays the direct path; the buttons gain validated, named intents. And the recorded session can carry the typed intent each button triggered, so a VR-collected demonstration is labelled with validatable URML primitives next to the pose stream.

Two real questions: (1) Is mapping a controller action to a validated URML intent (vs raw pose streaming) interesting for VR teleop built on oculus_reader? (2) Is recording the typed intent per button useful for the demonstrations collected through it?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0480-oculus-reader-outreach.md

Thanks for oculus_reader; a clean Quest input bridge is a natural place to attach validated, named intents to controller actions.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0481: dex-retargeting

**Post to (Issue):** https://github.com/dexsuite/dex-retargeting/issues/new
**Title:** URML (open robot intent language): wrapping retargeted hand intent in a capability/envelope check — request for comment

```
Hi dex-retargeting community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. dex-retargeting is the human->robot hand retargeting layer behind AnyTeleop, used by many VR/vision teleop rigs, and URML is interesting to it as the validated bound around the retargeted output.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment, and a design question.

A retargeted grasp still has to be something the declared hand can actually do -- DOF, joint limits, the object's graspable class -- and that's exactly URML's capability/envelope check. So a retargeting result becomes (or is paired with) a URML manipulation intent that is validated against the declared dexterous-hand manifest before it's sent to hardware. This connects to dexterous-hand manifest questions URML has been asking elsewhere (LEAP / Shadow): what a multi-DoF hand must declare so a retargeted grasp can be capability-checked.

Two real questions: (1) Is wrapping a retargeted hand pose in a validated manipulation intent (capability + envelope check before hardware) interesting for AnyTeleop-style rigs? (2) What should a URML capability manifest declare to describe a dexterous hand honestly so a retargeted grasp can be checked (DOF, joint limits, graspable classes)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0481-dex-retargeting-outreach.md

Thanks for dex-retargeting; the retargeting layer most VR teleop rigs depend on is the right place to think about a validated bound on the result.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0482: Open-TeleVision

**Post to (Issue):** https://github.com/OpenTeleVision/TeleVision/issues/new
**Title:** URML (open robot intent language): a validated handoff / typed-demo layer for Open-TeleVision — request for comment

```
Hi Open-TeleVision community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. Open-TeleVision is a leading immersive VR teleop system for bimanual and humanoid demonstration collection, and URML is interesting to it in two ways that don't compete with immersive control.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams: (1) shared-autonomy handoff -- inside the immersive session the operator can issue a high-level command; URML validates it against the robot's capabilities + envelope and dispatches, with full teleop as the correction path. (2) typed-intent annotation -- a demonstration is labelled with the URML primitives it realizes, so an immersive bimanual demo carries validatable typed intent next to the video. URML already models bimanual manipulation (an arm selector + a bimanual primitive), so a two-arm demo maps cleanly.

Two real questions: (1) Is a validated shared-autonomy handoff interesting inside an immersive teleop session? (2) Is labelling demonstrations with typed URML intent (including bimanual) useful for the data collected -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0482-televison-outreach.md

Thanks for Open-TeleVision; an immersive bimanual teleop system is a great place to think about validated handoffs and typed demonstrations.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0483: Universal Manipulation Interface (UMI)

**Post to (Issue):** https://github.com/real-stanford/universal_manipulation_interface/issues/new
**Title:** URML (open robot intent language): typed, manifest-checkable labels on UMI demonstrations — request for comment

```
Hi UMI community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. UMI's handheld-gripper, in-the-wild data collection is interesting to URML as a place to attach a typed schema for the intent of each captured demonstration. (For context: URML engaged the sibling diffusion_policy earlier; this is a separate thought on UMI's data-collection side, not a repeat.)

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two ideas: (1) each UMI demonstration is labelled with the URML primitive(s) it realizes (grasp($obj), place_at(...)); the label is a typed, validatable intent -- structured supervision for a downstream policy, and a record checkable against a target robot's manifest (is this demonstrated grasp something this robot could do?). (2) at deployment, a policy trained on UMI data is wrapped in URML's validate-before-actuate envelope -- the decide-then-do split applied to learning -- so in-the-wild-collected behavior is capability- and envelope-checked before it runs on hardware.

Two real questions: (1) Is labelling UMI demonstrations with a typed URML primitive useful, as structured supervision and as a manifest-checkable record? (2) Is wrapping a UMI-trained policy in a validated intent + envelope at deployment interesting -- and where's the cleaner seam, annotation at collection or a wrapper at deployment?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0483-umi-outreach.md

Thanks for UMI; an in-the-wild handheld data-collection interface is a great place to think about typed, checkable demonstration intent.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0484: DexCap

**Post to (Issue):** https://github.com/j96w/DexCap/issues/new
**Title:** URML (open robot intent language): typed, manifest-checkable labels on DexCap demonstrations — request for comment

```
Hi DexCap community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. DexCap's portable hand-motion-capture data collection is interesting to URML as a place to attach a typed schema for the captured intent.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two ideas: (1) each DexCap demonstration is labelled with the URML primitive(s) it realizes (grasp with the addressed hand + dexterous-hand parameters); the label is typed and checkable against a target dexterous-hand manifest (DOF, joint limits, graspable classes). (2) a policy trained on DexCap data is wrapped in URML's validate-before-actuate envelope at deployment (the decide-then-do split applied to learning), so the captured dexterous behavior is capability- and envelope-checked before it runs.

Two real questions: (1) Is labelling DexCap demonstrations with a typed URML primitive useful as structured, manifest-checkable supervision? (2) What should a URML capability manifest declare to describe the target dexterous hand so a captured grasp can be checked?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0484-dexcap-outreach.md

Thanks for DexCap; a portable in-the-wild dexterous-mocap rig is a great place to think about typed, checkable demonstration intent.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
