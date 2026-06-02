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

# Move #24 post bodies: simulation / digital-twin

Copy-paste-ready bodies for the 10 Tier-A targets. Folded siblings (o3de-extras,
habitat-lab, NVIDIA Warp, PettingZoo / Gymnasium-Robotics) and the Tier-B/C
research/closed/stale sims (SAPIEN/ManiSkill, robosuite, BEHAVIOR-1K, Cosys-AirSim,
ARGoS, DART, CoppeliaSim, PyBullet, Flightmare) are recorded in
[`outreach-move24.yaml`](outreach-move24.yaml), not posted.

Bodies follow the [AGENTS.md](../../AGENTS.md) outreach-post-structure rules:
concrete hook first, "nothing for you to maintain" up front, one or two real
questions, full RFC linked as optional depth, under a two-minute read, zero
em-dashes. The audience is a simulation maintainer, so the bodies speak in their
terms. The mandatory VIBE disclosure line goes last in every body.

All 10 repos have Issues enabled (verified 2026-06-02), so each is a single Issue.

**Posting status:** DRAFTED, not yet posted. Post under `idoco2003` only after
RFCs 0322-0331 land on `main`. Then fill `sent_at` / `posted_url` per row in
`outreach-move24.yaml` and refresh `outreach.db`.

**Routing summary**

| RFC | Target | Channel | Status |
|---|---|---|---|
| 0322 | Genesis | Issue on `Genesis-Embodied-AI/Genesis` | Drafted (post after merge) |
| 0323 | NVIDIA Isaac Sim | Issue on `isaac-sim/IsaacSim` | Drafted (post after merge) |
| 0324 | O3DE | Issue on `o3de/o3de` | Drafted (post after merge) |
| 0325 | CARLA | Issue on `carla-simulator/carla` | Drafted (post after merge) |
| 0326 | Unity Robotics Hub | Issue on `Unity-Technologies/Unity-Robotics-Hub` | Drafted (post after merge) |
| 0327 | Habitat | Issue on `facebookresearch/habitat-sim` | Drafted (post after merge) |
| 0328 | Project Chrono | Issue on `projectchrono/chrono` | Drafted (post after merge) |
| 0329 | Brax | Issue on `google/brax` | Drafted (post after merge) |
| 0330 | Eclipse Ditto | Issue on `eclipse-ditto/ditto` | Drafted (post after merge) |
| 0331 | Gymnasium | Issue on `Farama-Foundation/Gymnasium` | Drafted (post after merge) |

---

## RFC-0322: Genesis

**Post to:** https://github.com/Genesis-Embodied-AI/Genesis/issues/new
**Title:** URML (open robot intent language): Genesis as a hermetic NL-to-motion demo target, request for comment

```
Hi Genesis maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. A person writes an English sentence, URML translates it to a typed primitive, statically validates it against the robot's declared capabilities and a safety envelope, then dispatches. The most compelling place to show that loop is in simulation, with no hardware in the way, and Genesis is the most capable open sim to do it in: validated English -> URML primitive -> a robot entity in a Genesis scene -> motion.

Nothing here asks Genesis to change or maintain anything. This is a request for comment on whether the layers fit.

Two real questions. First, what is the cleanest boundary for "URML primitive -> Genesis entity command", the Python control API directly, or via an imported robot (URDF/MJCF) and its actuators? Second, would Genesis find value in being a documented hermetic-demo target for a natural-language front end, or does that overlap your own roadmap?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0322-genesis-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is Genesis Apache-2.0?

Thanks for how far Genesis has pushed open, fast robot simulation.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0323: NVIDIA Isaac Sim

**Post to:** https://github.com/isaac-sim/IsaacSim/issues/new
**Title:** URML (open robot intent language): validated-intent mapping onto Isaac Sim, request for comment

```
Hi Isaac Sim maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML composes above the simulator: validated intent -> a controller -> Isaac Sim via the ROS 2 bridge / Action Graph -> a simulated robot.

To be clear about scope: I have a separate, earlier thread with Isaac Lab (RFC-0050) about the RL training framework. This one is specifically about Isaac Sim as the simulator application, a distinct conversation, not a re-pitch of that relationship.

Nothing here asks Isaac Sim to change or maintain anything. Two real questions. First, is the ROS 2 bridge the right boundary for "URML primitive -> Isaac Sim", or is there a more idiomatic Action Graph entry point? Second, URML's capability manifest needs to align with a robot description; for Isaac Sim that is USD. What grain of USD robot-description alignment would be most useful from your side?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0323-nvidia-isaac-sim-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. What is the current license?

Thanks for open-sourcing Isaac Sim. It changes what an open NL-to-sim demo can look like.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0324: O3DE

**Post to:** https://github.com/o3de/o3de/issues/new
**Title:** URML (open robot intent language): mapping onto the O3DE ROS 2 Robotics Gem, request for comment

```
Hi O3DE maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML composes above the simulator: validated intent -> a controller -> the O3DE ROS 2 Robotics Gem -> a simulated robot.

Nothing here asks O3DE to change or maintain anything. This is a request for comment on whether the layers fit, and where the boundary sits.

Two real questions. First, is the ROS 2 Robotics Gem (in o3de-extras) the right integration surface for "URML primitive -> O3DE simulated robot", and should the Gem-specific follow-up live on o3de-extras rather than here? Second, URML's capability manifest needs to align with an imported robot (URDF) and its spawnable; what grain of alignment would be most useful?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0324-o3de-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is O3DE Apache-2.0 / MIT dual-licensed?

Thanks for keeping a fully open, LF-governed engine in the robotics-sim conversation.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0325: CARLA

**Post to:** https://github.com/carla-simulator/carla/issues/new
**Title:** URML (open robot intent language): mapping a validated-intent layer onto CARLA, request for comment

```
Hi CARLA maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML's mobility vocabulary (ackermann steering, max velocity) and its perception manifest (cameras, lidar, radar, GNSS, IMU) line up closely with a CARLA vehicle actor and its sensor suite.

To be honest about scope: CARLA is autonomous-driving, which is a subset of what URML targets, and URML does not yet have a full driving profile. So this is a request for comment on the fit, not a finished mapping.

Two real questions. First, what is the cleaner boundary for "URML intent -> CARLA actor", the Python API directly or the ROS bridge? Second, would a documented mapping from a small URML mobility/perception subset onto a CARLA vehicle be interesting to you, and is a driving profile something worth URML defining?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0325-carla-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is CARLA MIT-licensed?

Thanks for the work that made open AV simulation a real thing.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0326: Unity Robotics Hub

**Post to:** https://github.com/Unity-Technologies/Unity-Robotics-Hub/issues/new
**Title:** URML (open robot intent language): Unity Robotics Hub mapping, plus a maintenance-status check

```
Hi Unity Robotics team,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML composes above the simulator: validated intent -> ROS-TCP-Connector -> a Unity-simulated robot, with the URDF Importer aligning the robot model to URML's capability manifest.

Before anything else, an honest question: the repo's last push is from late 2024, so I want to check whether Unity Robotics Hub is still maintained and whether this is the right venue, or whether the project has moved. A clear "unmaintained" is a useful answer too.

If it is live: nothing here asks you to change or maintain anything. The one real mapping question is whether ROS-TCP-Connector is the boundary you would expect for "URML primitive -> Unity robot", and at what grain the URDF Importer's output should align with a capability manifest.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0326-unity-robotics-hub-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. What is the current license?

Thanks for the ROS-TCP and URDF Importer tooling; it shaped how a lot of people bridge Unity and ROS.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0327: Habitat

**Post to:** https://github.com/facebookresearch/habitat-sim/issues/new
**Title:** URML (open robot intent language): validated-intent mapping onto a Habitat agent, request for comment

```
Hi Habitat maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. For an embodied agent, URML's navigation and perception subset (move to, scan, detect, measure, report) maps onto a Habitat agent's actions.

To be honest about the fit: a Habitat agent is navigation-and-perception-first, not a full manipulator, so URML would declare a lower-bound capability subset for it. URML is comfortable declaring exactly what a substrate can and cannot do; that honesty is part of the design.

Two real questions. First, what is the right integration surface, habitat-sim's agent-action API directly, or habitat-lab's task layer? Second, how should a URML capability manifest align with a scene / episode dataset, if at all?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0327-habitat-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is Habitat MIT-licensed?

Thanks for Habitat; it set a bar for fast, photorealistic embodied-AI simulation.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0328: Project Chrono

**Post to:** https://github.com/projectchrono/chrono/issues/new
**Title:** URML (open robot intent language): high-fidelity validation via Project Chrono, request for comment

```
Hi Project Chrono maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. Most simulators are fine for showing the loop, but Chrono is where it could be validated for real: high-fidelity multibody dynamics, terramechanics for deformable terrain, and Chrono::Sensor. The use case is pre-deployment validation, checking validated intent against rough-terrain or vehicle dynamics before a real robot moves.

Nothing here asks Chrono to change or maintain anything. Two real questions. First, is PyChrono the boundary you would expect for "URML primitive -> Chrono model", or is there a ROS path you would point me at? Second, at what grain should a URML capability manifest align with a Chrono vehicle / robot model?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0328-project-chrono-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is Chrono BSD-3-Clause?

Thanks for the fidelity Chrono brings to open robotics simulation.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0329: Brax

**Post to:** https://github.com/google/brax/issues/new
**Title:** URML (open robot intent language): intent as a bound on a Brax-trained policy, request for comment

```
Hi Brax maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. Brax is interesting to URML from a different angle than a classic simulator: a policy trained in Brax becomes a controller that URML dispatches to, and URML's capability manifest plus envelope statically bound what that learned controller is allowed to attempt.

I will be honest that "learned controller as a URML substrate" is newer ground for the project, so this is genuinely a request for comment.

Two real questions. First, what is the natural boundary between a URML primitive and a Brax environment's action and observation spaces? Second, given Brax's MJX lineage, how do you see the relationship to MuJoCo (we have a separate MuJoCo thread), and does a thin intent/spec layer above a trained policy resonate or seem out of place?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0329-brax-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is Brax Apache-2.0?

Thanks for Brax and for making large-scale differentiable physics approachable.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0330: Eclipse Ditto

**Post to:** https://github.com/eclipse-ditto/ditto/issues/new
**Title:** URML (open robot intent language): a capability manifest as a robot's digital twin, request for comment

```
Hi Eclipse Ditto maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. That capability manifest is, in effect, a robot's capability twin: what it can do, what it carries, what it is allowed to do. Ditto manages digital twins via a Thing / Feature model, which is a striking overlap. URML validates intent against the declared twin before dispatch; Ditto reflects live state. The two compose. (URML has engaged sibling Eclipse projects before, iceoryx and Zenoh, so the foundation has seen us around.)

Nothing here asks Ditto to change or maintain anything. Two real questions. First, at what grain should a URML capability manifest align with a Ditto Thing and its Features, capability blocks as Features, declared state as Feature properties? Second, Ditto aligns with the W3C Web of Things Thing Description; should URML's manifest align with WoT TD rather than invent its own shape?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0330-eclipse-ditto-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is Ditto EPL-2.0? To be clear, the fit is cross-citation, not vendoring code in either direction.

Thanks for Ditto, and for keeping open digital twins a real option.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0331: Gymnasium

**Post to:** https://github.com/Farama-Foundation/Gymnasium/issues/new
**Title:** URML (open robot intent language): an intent layer alongside the Gymnasium env API, request for comment

```
Hi Farama maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. Gymnasium is the de-facto RL environment API. URML is not an RL environment, so I want to be upfront that this is a conceptual-peer conversation, not a substrate mapping, and the fit is exploratory.

Two directions seem worth your read. First, a URML-validated policy could expose a Gymnasium environment, so a declared capability manifest bounds the action space a learned agent is allowed to explore. Second, PettingZoo's multi-agent API lines up with URML's multi-robot fleet work, where intent is validated across robots before any of them act.

Nothing here asks Gymnasium to change or maintain anything. The real question: does a thin intent/spec layer above the env API seem useful to you, or firmly out of scope for what Gymnasium is?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0331-gymnasium-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is Gymnasium MIT-licensed?

Thanks for stewarding the RL environment API the whole field leans on.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
