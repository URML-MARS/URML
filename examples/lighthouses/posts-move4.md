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

# Move #4 post bodies

Copy-paste-ready Issue / Discussion bodies for the Move #4 outreach RFCs in [`docs/rfcs/`](../../docs/rfcs/). Each section is one target.

Ledger state lives in [`outreach-move4.yaml`](outreach-move4.yaml). After posting, set `sent_at` and `last_touch` to today's date, append the URL to `posted_url`, and update `next_action`.

Voice: founder posts under his GitHub identity. The RFC author field already reads `Ido Yahalomi (greenvh@gmail.com)`. Posts sign as the URML maintainer; do not impersonate URML as an organization.

---

## RFC-0065: ROBOTIS

**Post to:** https://github.com/ROBOTIS-GIT/turtlebot3/issues/new
**Optional cross-reference:** https://github.com/ROBOTIS-GIT/dynamixel_sdk/issues/new (for the institutional servo-backbone surface)
**Label:** the closest `enhancement` equivalent the form offers
**Title:** `Proposal: RobotisAdapter family for URML's substrate-neutral robot-intent language (TurtleBot 3 + OP3 + OpenManipulator + Dynamixel SDK)`

**Body:**

```markdown
Proposing a `RobotisAdapter` family that targets four published ROBOTIS-GIT surfaces: `turtlebot3` (mobile base), `turtlebot3_manipulation`, the OP3 humanoid line (newly ROS 2 in 2025), and the `dynamixel_sdk` servo backbone. The adapter routes [URML](https://urml.dev) Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) onto your published ROS 2 topics and Dynamixel protocol calls without changes on your side.

URML is an Apache 2.0 specification for substrate-neutral robot intent. Its Layer-2 primitive vocabulary sits one layer above ROS 2 / PX4 / Isaac / MuJoCo / AUTOSAR Adaptive / OPC UA Robotics. A program written for a TurtleBot 3 retargets to an OP3 humanoid or an OpenManipulator-X arm by switching the manifest, with static validation at every step.

Cross-link worth flagging: URML's existing outreach to Trossen Robotics Interbotix (RFC-0064), Stanford ALOHA (RFC-0056), and Hugging Face LeRobot (RFC-0040) all transitively depend on Dynamixel servos. The ROBOTIS-side relationship has never been directly engaged; this RFC closes that loop.

This is proposal-only, posted as URML's first **Move #4** outreach (adjacent niches Moves #1, #2, and #3 did not touch). No adapter code in this PR. The TurtleBot 3 variant manifest split, the OP3 motion-surface choice, and the Dynamixel SDK cross-link are observable choices worth your input before shipping.

Full RFC with proposed package layout, per-primitive mapping, manifest sketches, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0065-robotis-outreach.md

## Feedback we'd value

1. **Adapter home.** URML repo (`reference/robotis-runtime/`), ROBOTIS-GIT contributed example, both?
2. **OP3 motion surface.** OP3 motion-module topic for URML's `move_to` dispatch, or a higher-level walk-engine interface?
3. **Dynamixel cross-link.** Interest in a documented `dynamixel_sdk` README note acknowledging the URML adapters that transitively depend on it?
4. **TurtleBot 3 variants.** Per-variant manifests (Burger / Waffle / Waffle Pi) or parametric?
5. **OpenCR firmware coverage.** Stock-only or document a custom-firmware path?
6. **Conformance lane.** Open to a URML conformance line on the `turtlebot3` README or in the OP3 emanual?

Thanks for the TurtleBot 3 / OP3 / Dynamixel ecosystem and for the OP3 2025 ROS 2 reboot. The institutional weight across global robotics education is exactly what URML's open-standard story needs.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0066: AgileX Robotics

**Post to:** https://github.com/agilexrobotics/scout_ros/issues/new (most-starred platform repo; pivot to `tracer_ros2` if maintainers prefer the Mobile-ALOHA-adjacent thread)
**Optional cross-reference:** https://github.com/agilexrobotics/ugv_sdk/issues/new (SDK-specific questions)
**Label:** the closest `enhancement` equivalent the form offers
**Title:** `Proposal: AgileXAdapter family for URML's substrate-neutral robot-intent language (six-platform catalog: Tracer / Limo / Scout / Hunter / Bunker / Ranger)`

**Body:**

```markdown
Proposing an `AgileXAdapter` family that covers your six published mobile-base ROS 2 packages under one URML adapter family: `tracer_ros2` (Mobile ALOHA chassis), `limo_ros2` (multi-mode configurable: differential / Mecanum / Ackermann / tracked), `scout_ros2`, `hunter_ros2`, `bunker_ros2`, `ranger_ros2`. [URML](https://urml.dev) Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`) map onto each base's `geometry_msgs/Twist` topic and Nav2 surface, with per-chassis kinematic constraints enforced by URML's static verifier from the manifest.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). The catalog-breadth angle is what makes AgileX distinctive for URML: a teacher who buys a Limo for an undergraduate course can later add a Scout Mini or a Hunter and keep using the same URML programs across the additions.

Cross-link worth flagging: URML's existing Stanford ALOHA RFC-0056 names the AgileX Tracer as Mobile ALOHA's chassis. The AgileX-side institutional outreach has never directly happened. This RFC closes that loop and extends to your full catalog. URML's LeRobot RFC-0040 outreach is also adjacent given the AgileX-LeRobot ecosystem alignment.

This is proposal-only, posted as part of URML's **Move #4** outreach (adjacent niches). No adapter code in this PR. The Limo per-mode manifest split, the `ugv_sdk` direct-call path, and the Mobile ALOHA cross-link note are observable choices worth your input before shipping.

Full RFC with proposed per-platform mapping, manifest sketches, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0066-agilex-outreach.md

## Feedback we'd value

1. **License confirmation.** Could you confirm the licenses on `tracer_ros2`, `limo_ros2`, `scout_ros2`, `hunter_ros2`, `bunker_ros2`, `ranger_ros2`, and `ugv_sdk`?
2. **Adapter home.** URML repo (`reference/mobile-runtime/src/mobile_runtime/agilex/`), agilexrobotics org as a contributed example, both?
3. **Limo manifest granularity.** Per-mode manifests (Mecanum / differential / Ackermann / tracked) or a single parametric manifest with a `chassis_mode:` field?
4. **`ugv_sdk` direct path.** Is the C++ SDK URML's recommended no-ROS path, or do you recommend the ROS 2 driver even there?
5. **Mobile ALOHA cross-link.** Interest in a documented `tracer_ros2` README note acknowledging the Mobile ALOHA chassis use case via URML?
6. **LeRobot ecosystem coordination.** Interest in coordinating with the existing AgileX-LeRobot alignment via URML?
7. **Conformance lane.** Open to a URML conformance line on the platform-repo READMEs?

Thanks for the breadth of the AgileX ROS 2 catalog and for `ugv_sdk`. The cross-platform coverage under one institutional contact is the most distinctive thing URML can offer at this tier.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0067: FarmBot

**Post to:** https://github.com/FarmBot/Farmbot-Web-App/issues/new
**Optional cross-post:** forum.farmbot.org (if maintainers prefer the design conversation there)
**Label:** the closest `enhancement` equivalent the form offers
**Title:** `Proposal: FarmBotAdapter for URML's substrate-neutral robot-intent language (Layer-2 primitives onto sequences / regimens / peripherals)`

**Body:**

```markdown
Proposing a `FarmBotAdapter` that targets FarmBot's [public REST API](https://developer.farm.bot/docs/api-docs) and MQTT pub/sub surface. The adapter routes [URML](https://urml.dev) Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) onto FarmBot's existing sequence / regimen / peripheral / tool vocabulary. Each FarmBot tool (seeder, watering nozzle, weeder, soil sensor) becomes a URML-named effector.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). FarmBot is **URML's first outreach into the agricultural vertical** — Moves #1, #2, and #3 did not touch agriculture. The natural reason FarmBot is first: it is the one open-source small-plot farming robot with a Python-friendly developer surface, REST API, and a community oriented toward customisation. Closed agricultural vendors (Naïo, Carbon Robotics) sell hardware-as-service with no public API.

The English-to-program use case lands more naturally on FarmBot than on any URML target so far. A sentence like "plant a row of lettuce two centimeters apart along the back bed" is the canonical FarmBot use case.

This is proposal-only, posted as part of URML's **Move #4** outreach (adjacent niches). No adapter code in this PR. The primitive-to-sequence mapping, the agriculture-profile primitive question (`plant` / `water` / `weed` as future Layer-3 vocabulary), and the local-MQTT-broker path for URML's offline-execution rule are observable choices worth your input before shipping.

Full RFC with proposed package layout, per-primitive mapping, manifest sketches, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0067-farmbot-outreach.md

## Feedback we'd value

1. **Adapter home.** URML repo (`reference/agriculture-runtime/`), FarmBot contributed example, both?
2. **Primitive-to-sequence mapping.** Is the `move_to + tool_mount + peripheral_on` decomposition the right way to ground URML primitives in FarmBot's sequence vocabulary, or would you prefer URML primitives map to CeleryScript directly?
3. **Agriculture-profile primitives.** Appetite for a co-designed `plant` / `water` / `weed` Layer-3 vocabulary in a future RFC, with FarmBot as the first adapter?
4. **Local MQTT broker.** What is the documented path for running FarmBot's MQTT broker locally for URML's offline-execution requirement?
5. **Generation-specific manifests.** Per-generation manifests (Genesis v1.7 / Genesis XL / Express / Express XL) or parametric?
6. **Conformance lane.** Open to a URML conformance line on developer.farm.bot or in the Web App README?

Thanks for FarmBot. The sequence / regimen / peripheral abstraction is exactly the right shape for the audience URML is trying to reach, and this is URML's first outreach into the agricultural vertical because FarmBot makes it the most concrete.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0068: PAL Robotics

**Post to:** https://github.com/pal-robotics/tiago_simulation/issues/new (or whichever TIAGo Pro repo PAL maintainers prefer)
**Label:** the closest `enhancement` equivalent the form offers
**Title:** `Proposal: PalAdapter family for URML's substrate-neutral robot-intent language (TIAGo / TIAGo Pro / PMB2)`

**Body:**

```markdown
Proposing a `PalAdapter` family targeting your published ROS 2 packages for PMB2 (mobile base), TIAGo (single-arm mobile manipulator), and TIAGo Pro (dual-arm + head). [URML](https://urml.dev) Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) plus the industrial-profile extensions (`pick_from`, `place_at`, `swap_tool`) map onto your published joint-trajectory action servers, gripper services, and Nav2-compatible base topics without changes on your side.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). PAL fills a distinctive niche in URML's outreach landscape: a commercial mobile-manipulator vendor with a mature ROS 2 ecosystem. URML's prior Move #1 industrial OEMs (Yaskawa, FANUC, UR, etc.) are stationary arms. Move #3's Trossen Interbotix is stationary research arms. Move #1's Boston Dynamics Spot and Move #2's ANYmal are legged platforms without arms. AgileX's mobile bases (parallel RFC-0066) have no arms. PAL's TIAGo and TIAGo Pro are the missing combination: a wheeled mobile base with a torque-controlled manipulator, sold commercially, with full ROS 2 support.

This is proposal-only, posted as part of URML's **Move #4** outreach. No adapter code in this PR. The TIAGo variant manifest split (Steel / Iron / Titanium / OMNI / Pro / Pro Head), the safety-field schema (`brake_rated`, `iso_collaborative`), and the bimanual-coordination primitive question are observable choices worth your input before shipping.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0068-pal-robotics-outreach.md

## Feedback we'd value

1. **Adapter home.** URML repo (`reference/pal-runtime/`), pal-robotics contributed example, both?
2. **Variant manifest granularity.** Per-variant manifests (Steel / Iron / Titanium / OMNI / Pro / Pro Head) or a parametric `tiago` manifest with `variant:` field?
3. **Safety-field schema.** Right declarative shape for `safety.brake_rated`, `safety.iso_collaborative`, and how to distinguish per-platform capability from per-deployment certification?
4. **Bimanual coordination at the ROS 2 layer.** Path for a `coordinate(arm_left, arm_right, ...)` Layer-2 primitive that targets TIAGo Pro's whole-body controller, or stay at the policy / behaviour-tree layer above URML?
5. **Whole-body controller cross-link.** Interest in coordinating with URML's RFC-0010 spec work on whole-body and bimanual manipulation?
6. **Conformance lane.** Open to a URML conformance line in TIAGo simulation README or PAL product documentation?

Thanks for the TIAGo / TIAGo Pro / PMB2 ROS 2 stack and for the long-running ecosystem commitment. The safety-rated mobile-manipulator surface is exactly what URML's commercial-research story needs.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0069: Berkeley Humanoid Lite

**Post to:** https://github.com/HybridRobotics/Berkeley-Humanoid-Lite/issues/new
**Label:** the closest `enhancement` equivalent the form offers
**Title:** `Proposal: BerkeleyHumanoidLiteAdapter for URML's substrate-neutral robot-intent language (sim via Isaac Lab + real hardware via published Python interface)`

**Body:**

```markdown
Hi Hybrid Robotics Lab,

Proposing a `BerkeleyHumanoidLiteAdapter` targeting both the sim path (Isaac Lab tasks) and the real-hardware path (the published Python control interface) for the Berkeley Humanoid Lite platform. [URML](https://urml.dev) Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`) map onto Isaac Lab task vectors and whole-body controller setpoints respectively.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). Berkeley Humanoid Lite is the most distinctive open-hardware humanoid target available right now: genuinely open (MIT code + CC-BY-SA 4.0 assets), affordable (sub-$5k BOM), research-fresh (2025 release, arXiv 2504.17249), and sim-friendly (Isaac Lab tasks ship in-repo).

The cross-link worth flagging: URML's existing RFC-0050 outreach to NVIDIA Isaac Lab + Isaac-GR00T composes with this proposal directly. A URML-aware Berkeley Humanoid Lite branch where Isaac Lab tasks consume URML primitive sequences closes the loop: train in URML-aware sim, deploy on real hardware via the same adapter family.

This is proposal-only, posted as part of URML's **Move #4** outreach. No adapter code in this PR. The sim-vs-real adapter split, the policy-trained-motion primitive mapping (a `move_to`-to-gait/posture rule similar to URML's existing Petoi RFC-0062), and the authoritative manifest values (DOF / mass / height) are observable choices worth your input before shipping.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0069-berkeley-humanoid-lite-outreach.md

## Feedback we'd value

1. **Adapter home.** URML repo (`reference/humanoid-runtime/src/humanoid_runtime/berkeley_humanoid_lite/`), HybridRobotics contributed example, both?
2. **Sim-vs-real adapter split.** Two adapters (one per substrate) or one adapter with a `mode:` parameter?
3. **Authoritative manifest values.** Could you confirm the DOF, mass, height, and control-loop frequency for the production design so URML's manifest reflects ground truth?
4. **Policy-trained-motion primitive mapping.** Is the `move_to` → whole-body-setpoint mapping the right shape, or would HybridRobotics recommend a more explicit `posture()` / `gait()` Layer-3 vocabulary?
5. **Isaac Lab cross-coordination.** Interest in coordinating with URML's open RFC-0050 outreach to the NVIDIA Isaac team, given your platform's Isaac Lab task ecosystem?
6. **Hardware-in-the-loop conformance path.** What is the documented path for a URML conformance run on real hardware?
7. **Conformance lane on the README.** Open to a URML conformance line on the Berkeley Humanoid Lite README?

Thanks for Berkeley Humanoid Lite and for the genuinely open-hardware posture. The sub-$5k BOM plus Isaac Lab task ecosystem is exactly the substrate-fungible target URML's outreach landscape was missing.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0070: HEBI Robotics

**Post to:** https://github.com/HebiRobotics/hebi-python-examples/issues/new (or https://github.com/HebiRobotics/hebi_ros2_examples/issues/new — pivot to whichever maintainers prefer)
**Label:** the closest `enhancement` equivalent the form offers
**Title:** `Proposal: HebiAdapter for URML's substrate-neutral robot-intent language (modular Series Elastic Actuator configurations via the HEBI API)`

**Body:**

```markdown
Proposing a `HebiAdapter` that targets your published Python / C++ API surface (`hebi-python-examples`, `hebi-cpp-examples`, `hebi_ros2_examples`, `hebi_description`, `hebi_msgs`, `hebi_cpp_api_ros`). [URML](https://urml.dev) Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) plus the industrial-profile extensions (`pick_from`, `place_at`, `swap_tool`) map onto HEBI's `Group.send_command()` and `Group.get_feedback()` calls, parameterised by the customer-declared kinematic chain.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). HEBI's distinctive value proposition for URML is **per-deployment kinematic modularity**. A HEBI customer at a research lab assembles actuators into a custom geometry — a five-DOF arm for one experiment, a seven-DOF arm for another, a quadruped for a third — and the same URML adapter drives all configurations. URML's capability manifest's `kinematic_chain` declaration is the natural vocabulary for the declared geometry; HEBI is the first URML target where every customer writes their own. The static verifier reasons against the declared chain before any motion executes.

This is proposal-only, posted as part of URML's **Move #4** outreach (adjacent niches). No adapter code in this PR. The kinematic-chain manifest shape, the example manifest set, the ROS 2 vs direct-API default, and the MATLAB-surface scope are observable choices worth your input before shipping.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0070-hebi-robotics-outreach.md

## Feedback we'd value

1. **Adapter home.** URML repo (`reference/cobot-runtime/src/cobot_runtime/hebi/`), HebiRobotics contributed example, both?
2. **Kinematic-chain manifest shape.** Is URML's `kinematic_chain` declaration the right shape for per-customer configurations, or would HEBI recommend a different vocabulary (URDF reference, MoveIt config import)?
3. **Example manifests.** Are the proposed examples (5-DoF X-Series arm, 7-DoF X-Series arm, Igor balancing kit, Rosie double-shoulder) the right starting set?
4. **ROS 2 vs direct-API default.** Should URML's adapter default to direct HEBI API calls or to the ROS 2 bridge?
5. **MATLAB surface.** Is the MATLAB-only deployment population large enough that URML should expose a MATLAB-facing adapter, or is Python sufficient?
6. **Robotarium cross-link.** Interest in coordinating with Robotarium @ Georgia Tech for a documented URML conformance deployment?
7. **Conformance lane.** Open to a URML conformance line in the HEBI documentation site or in `hebi_ros2_examples` README?

Thanks for the HEBI ecosystem and for the modular Series Elastic Actuator design. The per-customer-geometry story is the most distinctive integration shape URML has encountered across four outreach waves, and HEBI is the natural first deployment for URML's `kinematic_chain` manifest field.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## Workflow for posting

For each target (in any order, but recommended to start with `FarmBot/Farmbot-Web-App` as the most distinctive vertical opening, then `HybridRobotics/Berkeley-Humanoid-Lite` for the frontier-open hardware story, then the remaining four):

1. Open the target's new-Issue URL (above each section).
2. Paste the title.
3. Paste the body (the contents inside the ```markdown fence, NOT the fence markers themselves).
4. Apply the recommended label if the form requires one. If no obvious match, leave unlabelled.
5. Submit.
6. Copy the resulting Issue URL.
7. Update [`outreach-move4.yaml`](outreach-move4.yaml) for that slug:
   - Set `posted_url` to the URL.
   - Set `last_touch` to today.
   - Append a verified-surface dated note to `notes`.
   - Update `next_action` to the chosen wait window (Moves #1, #2, #3 used "wait 14 d").
8. Continue.

After all posts are sent, the ledger reflects the truth and `make audit` re-measures cleanly.
