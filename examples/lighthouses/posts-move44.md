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

# Move #44 post bodies: the open robot-platforms wave

Ten targets (Source Robotics's two arms folded into one org-anchor post), all
GitHub Issues. Post under idoco2003. No license-ask anywhere (state the license
if relevant, never ask). AI-assisted-authoring disclosure up front. Titles carry
no em-dash.

Shared thesis: URML sits ABOVE the platform's own control stack as the
validated-intent gate. An intent becomes a typed primitive, validated against
the platform's declared capability manifest and a safety envelope, then
dispatched to the platform's existing API / ROS 2 stack. The platform stays the
thing that moves; URML adds the typed, checkable gate above it.

---

## RFC-0491: OpenArm (anchor)

**Post to (Issue):** https://github.com/enactic/openarm/issues/new
**Title:** URML (open robot intent language): a validated-intent layer + capability manifest for OpenArm (request for comment)

```
Hi OpenArm community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person (or a higher-level planner) expresses an intent, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches to the robot's own control stack. OpenArm is a clean, fully-open arm platform, and URML is interesting to it as the layer above the SDK -- not a replacement for it.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: OpenArm's joints, end-effector, reach, and payload become a URML capability manifest. A bimanual OpenArm declares its two arms (each with its gripper), so a command can address left / right / a named arm, and a coordinated two-arm intent uses URML's `bimanual` primitive; the single-arm config is the same manifest with one declared arm. `grasp`, `release`, and a bimanual lift are then validated against the declared arms, gripper force limits, and the active safety envelope before anything moves. Your SDK stays the execution layer.

Two real questions: (1) does mapping OpenArm's single- and dual-arm configs onto a URML manifest (per-arm declaration + a bimanual primitive) read right for how the arms are actually addressed? (2) Is a validated-intent gate above the OpenArm SDK interesting for contact-rich work -- and which is the cleaner first seam, the manifest mapping or the dispatch adapter?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0491-openarm-outreach.md

Thanks for OpenArm; an open bimanual platform is exactly where the dual-arm-intent question is worth asking.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0492: Upkie

**Post to (Issue):** https://github.com/upkie/upkie/issues/new
**Title:** URML (open robot intent language): a validated-intent layer above Upkie's balancing controller (request for comment)

```
Hi Upkie community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched to the robot's own controller. For a wheeled-biped balancer like Upkie, URML is interesting as the layer above the balancing loop: a high-level command ("go to the door", "turn around") is validated before it reaches the agent, while the balancing keeps running underneath.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: Upkie's wheeled-biped mobility and its balance envelope (the limits it must stay within to stay upright) map onto a URML manifest -- a `mobility` block plus a `whole_body` stability declaration (center-of-mass / support bounds). A locomotion intent is checked against those limits and the active safety envelope before it reaches the balancing agent. URML is the typed gate; Upkie's controller stays the thing that balances and drives.

Two real questions: (1) does declaring Upkie's mobility plus a `whole_body` balance envelope as a URML manifest read right for a wheeled biped? (2) Is a validated-intent gate above the balancing controller interesting -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0492-upkie-outreach.md

Thanks for Upkie; the balancing-controller-plus-high-level-intent split is exactly the seam this asks about.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0493: linorobot2

**Post to (Issue):** https://github.com/linorobot/linorobot2/issues/new
**Title:** URML (open robot intent language): an English front door above the linorobot2 nav stack (request for comment)

```
Hi linorobot2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: "go to the kitchen" becomes a typed `move_to`, validated against the robot's declared mobility and the map's declared locations, then dispatched to the existing navigation stack. For a build-your-own mobile base, URML is interesting as the natural-language front door above your ROS 2 nav pipeline -- it adds a capability/envelope gate and a typed intent record, it does not replace Nav2.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the base's drive type (differential / mecanum), velocity limits, and the deployment's named locations and frames become a URML manifest. A program's `move_to(location)` is validated against it -- the location resolves, the drive type supports the motion, the envelope permits it -- and then the goal is handed to linorobot2's navigation.

Two real questions: (1) does mapping a linorobot2 base (drive type, velocity limits, named locations) onto a URML manifest read right? (2) Is an English-to-validated-`move_to` front door above the nav stack interesting for the build-your-own audience -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0493-linorobot2-outreach.md

Thanks for linorobot2; "one English sentence makes the base move" is exactly the path a build-your-own platform shows off.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0494: BotBrain

**Post to (Issue):** https://github.com/botbotrobotics/BotBrain/issues/new
**Title:** URML (open robot intent language): a validated-intent layer above BotBrain (request for comment)

```
Hi BotBrain community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. BotBrain is a modular brain for legged robots (teleop, nav, mapping on ROS 2), and URML is interesting as the validated-intent layer that sits above it and routes into its existing modules.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the legged platform BotBrain drives declares its mobility (a legged drive type), its `whole_body` stability limits, and its named locations as a URML manifest. A high-level or natural-language command becomes a typed URML primitive, validated against that manifest, then routed to BotBrain's navigation or teleop path. URML is the typed gate and intent record; BotBrain stays the runtime that moves the legs.

Two real questions: (1) does a URML manifest for the legged platform (legged drive type + `whole_body` limits + locations) fit how BotBrain models its robot? (2) Is a validated-intent layer above the nav / teleop modules interesting, or already covered by something in the stack -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0494-botbrain-outreach.md

Thanks for BotBrain; a modular legged-robot brain is a natural place to ask where a validated-intent gate fits.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0495: Source Robotics (PAROL6 / Faze4)

**Post to (Issue):** https://github.com/Source-Robotics/PAROL-commander-software/issues/new
**Title:** URML (open robot intent language): a validated pick/place layer for PAROL6 and Faze4 (request for comment)

```
Hi Source Robotics community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: "pick that up and place it there" becomes a typed primitive, validated against the arm's declared reach, payload, and gripper, then dispatched to the arm's own controller. Your open desktop arms (PAROL6 via the PAROL commander, and the Faze4) are a great fit for a validated-intent layer above the controller. I'm sending one note for the org rather than separate posts.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the arm's joints, reach, payload, and end-effector become a URML capability manifest. `pick_from` / `place_at` / `grasp` are validated against that declared workspace and the gripper's force limits and the active safety envelope, then the motion is handed to the PAROL commander (or the Faze4 controller). This proposes no code reuse (the commander is GPL-3.0, the Faze4 hardware is CERN-OHL) -- only a capability-manifest mapping and an optional adapter.

Two real questions: (1) does mapping a PAROL6 / Faze4 arm (reach, payload, gripper) onto a URML manifest read right for a desktop arm? (2) Is a validated pick/place intent layer above the controller interesting -- and which platform (PAROL6 or Faze4) is the better place to start?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0495-source-robotics-outreach.md

Thanks for the PAROL6 and Faze4; widely-built open arms are exactly where this kind of typed-intent layer is worth trying.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0496: The BiMo Project

**Post to (Issue):** https://github.com/mekion/the-bimo-project/issues/new
**Title:** URML (open robot intent language): a validated-intent layer + sim2real envelope for BiMo (request for comment)

```
Hi BiMo community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. BiMo is an open biped with a clean Python API and an Isaac Lab sim-to-real workflow, and URML is interesting to it in two complementary ways.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

(1) Validated intent: the biped's kinematic structure and balance limits map onto a URML `whole_body` declaration plus a `mobility` block; a locomotion intent is validated against that envelope before it reaches the Python API. (2) Sim-to-real envelope: your Isaac Lab workflow trains policies in a simulated domain, and URML has a `LearnedPolicy` declaration that lets a trained policy carry the observation/action spaces and training-domain bounds it learned, so the validator can refuse to dispatch it outside the domain it trained for. That is the sim-to-real boundary made checkable.

Two real questions: (1) does a URML manifest for the biped (`whole_body` structure + balance envelope) read right, and does a validated-intent layer above the Python API fit? (2) Is a declared training envelope for the Isaac Lab side useful -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0496-the-bimo-project-outreach.md

Thanks for BiMo; the clean Python API plus the sim-to-real workflow are exactly what makes both seams concrete.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0497: Zeroth Bot

**Post to (Issue):** https://github.com/zeroth-robotics/zeroth-bot/issues/new
**Title:** URML (open robot intent language): a validated-intent layer + learned-policy envelope for Zeroth Bot (request for comment)

```
Hi Zeroth Bot community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Zeroth Bot is a low-cost open 3D-printed humanoid built for sim-to-real and RL, and URML is interesting to it both as a validated-intent layer above the control stack and as the place an RL policy declares the envelope it was trained in.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

(1) Validated intent: the humanoid's kinematic structure and stability limits map onto a URML `whole_body` declaration; a command is validated against that envelope before dispatch. (2) Learned-policy envelope: a trained policy can carry its observation/action spaces and training-domain bounds as a URML `LearnedPolicy` declaration, so the validator refuses to dispatch it outside the domain it learned -- the out-of-distribution action caught before it reaches a low-cost humanoid's joints.

Two real questions: (1) does a URML `whole_body` manifest for the humanoid read right? (2) For the RL / sim-to-real side, is a declared training envelope on a deployed policy useful -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0497-zeroth-bot-outreach.md

Thanks for Zeroth Bot; a low-cost RL humanoid is exactly where bounding a learned policy by its training envelope matters.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0498: quadruped_ros2_control

**Post to (Issue):** https://github.com/legubiao/quadruped_ros2_control/issues/new
**Title:** URML (open robot intent language): a validated-intent layer that emits goals onto quadruped ros2_control (request for comment)

```
Hi,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Your project provides ros2_control implementations for quadrupeds, and URML is interesting one layer above: a locomotion intent validated against the robot's declared structure, then emitted as goals onto the controllers you provide.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the quadruped's legged drive type and its `whole_body` stability limits (center-of-mass / support polygon) become a URML manifest; a locomotion intent is validated against that envelope before dispatch. URML already treats ros2_control as a Layer-1 hardware-abstraction seam, so this is a concrete quadruped instance of that mapping, not a new mechanism: URML validates and emits the goal, your controllers execute it.

Two real questions: (1) does a URML manifest for a quadruped (legged drive type + `whole_body` limits) read right for the robots this stack targets? (2) Is a validated-intent layer that emits goals onto the ros2_control controllers interesting -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0498-quadruped-ros2-control-outreach.md

Thanks for the project; a clean quadruped ros2_control stack is a natural execution layer for a validated-intent gate.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0499: hexapod-robot-simulator

**Post to (Issue):** https://github.com/mithi/hexapod-robot-simulator/issues/new
**Title:** URML (open robot intent language): a typed gait/pose intent layer for the hexapod (request for comment)

```
Hi Mithi,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared structure and a safety envelope, then dispatched to the kinematics engine. Your first-principles hexapod kinematics work (the simulator, and hexapod-irl for real hardware) is a clean place to try a typed-intent layer above the gait and pose control.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the hexapod's six legs and their degrees of freedom map onto a URML `whole_body` kinematic-structure declaration plus a legged drive type. A "walk forward" / "turn" / "strike this pose" intent is validated against that declared structure, then the kinematics engine executes the gait. URML is the typed gate and intent record; it does not re-implement the inverse kinematics.

Two real questions: (1) does mapping the six-leg structure onto a URML `whole_body` declaration read right? (2) Is a typed, validated gait/pose intent layer above the kinematics engine interesting -- for the simulator, or the hexapod-irl real-hardware path -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0499-hexapod-robot-simulator-outreach.md

Thanks for the hexapod work; the first-principles kinematics make the structure declaration unusually clean.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0500: magician_ros2 (Dobot Magician)

**Post to (Issue):** https://github.com/jkaniuka/magician_ros2/issues/new
**Title:** URML (open robot intent language): an English front door for the Dobot Magician (request for comment)

```
Hi,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: "pick up the block and place it on the stack" becomes a typed pick/place primitive, validated against the arm's declared reach and payload, then dispatched to the ROS 2 stack. Your magician_ros2 is a clean control stack for a common classroom manipulator, and the educational tier is exactly where the "one English sentence moves a real arm" path matters.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the Magician's reach, payload, and end-effector become a URML manifest under an educational profile. `pick_from` / `place_at` / `grasp` are validated against that workspace, then the motion is handed to magician_ros2. URML adds the capability/envelope gate and a typed intent record above the ROS 2 stack. (URML already ships an edu-runtime with adapters for several classroom platforms, so the Magician fits an established pattern.)

Two real questions: (1) does mapping the Dobot Magician (reach, payload, gripper) onto a URML educational-profile manifest read right? (2) Is an English-to-validated-pick/place front door above magician_ros2 interesting for classroom use -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0500-magician-ros2-outreach.md

Thanks for magician_ros2; a clean ROS 2 stack for a classroom arm is a great fit for the English-front-door path.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
