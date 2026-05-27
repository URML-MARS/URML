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

# URML RFCs

This directory is URML's decision history. Every change to the **specification** — adding or modifying a primitive, changing a schema, modifying behavior semantics, changing a profile, modifying the Core Commitment — happens here, not in a pull request.

The authoritative description of *how* RFCs work is [RFC-0001](0001-rfc-process.md). This file is just the index.

## Two kinds of RFC live here

The `docs/rfcs/` dir now holds two distinct kinds of document, marked by the
**Kind** column in the index below:

- **Spec** — changes URML's normative surface: Layer-1/2/3/4 schemas, new
  primitives, policy mechanism, profiles, the Core Commitment. These are
  RFCs in the canonical sense ([RFC-0001](0001-rfc-process.md) governs
  them) and going through Draft → Open → Accepted → Implemented is the
  way *the specification* changes. Numbered 0001–0022 at time of writing.
- **Outreach** — per-target request-for-comment documents. Each one
  explicitly states *"No spec change is proposed here"* and proposes a
  mapping from URML v0.1 to an existing target's adapter / manifest / API.
  They live in this directory for ergonomic discoverability (one place
  to find "URML's pitch to target X") and are tracked operationally in
  the outreach ledgers under [`examples/lighthouses/`](../../examples/lighthouses/).
  Eight outreach waves now exist: **Move #1** (RFCs 0023–0038, robot
  OEMs and component vendors, ledger
  [`outreach.yaml`](../../examples/lighthouses/outreach.yaml)),
  **Move #2** (RFCs 0040–0060, AI/ML-layer projects, ledger
  [`outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml)),
  **Move #3** (RFCs 0061–0064, affordable / desktop / educational
  robotics vendors, ledger
  [`outreach-move3.yaml`](../../examples/lighthouses/outreach-move3.yaml)),
  **Move #4** (RFCs 0065–0070, adjacent niches Moves #1–#3 did not touch,
  ledger
  [`outreach-move4.yaml`](../../examples/lighthouses/outreach-move4.yaml)),
  **Move #5** (RFCs 0071–0079, Tier 2 promoted candidates plus DEEP
  Robotics' Lynx S10 wheeled-legged-hybrid debut, ledger
  [`outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml)),
  **Move #6** (RFCs 0080–0091, US-friendly university robotics labs,
  ledger
  [`outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml)),
  **Move #7** (RFCs 0092–0099, agriculture-robotics second wave,
  ledger
  [`outreach-move7.yaml`](../../examples/lighthouses/outreach-move7.yaml)),
  **Move #8** (RFCs 0100–0107, home-assistance robotics + parts,
  ledger
  [`outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml)),
  and **Move #9** (RFC 0108 first, NASA robotics, ledger
  [`outreach-move9.yaml`](../../examples/lighthouses/outreach-move9.yaml)).
  Move #3 sits between the Tier-1 OEMs of Move #1 and the AI/ML targets
  of Move #2. Move #4 widens the substrate set into verticals and
  audiences URML's first three waves left untouched. Move #5 promotes
  the parked Tier 2 from the Move #4 research pass. Move #6 turns to
  university robotics labs (6 US, 4 EU+UK, 2 Asia-Pacific), all Tier B
  research-collab framing rather than vendor outreach. Move #7 widens
  the agriculture surface first opened by Move #4 RFC-0067 (FarmBot) to
  eight new targets across solar-powered rovers, ag-drones, commercial
  cobots, US + EU academic ag-robotics labs, off-GitHub educational
  platforms, and the European Field Robot Event competition (3 Tier A
  vendor-style + 5 Tier B research-collab). Move #8 opens the home-
  assistance vertical: eight new targets across consumer cleaning
  robots (Roomba), outdoor home robots (Husqvarna Automower), hospitality
  cobots (Bear Robotics), pool cleaning (Maytronics Dolphin), servo
  (ROBOTIS Dynamixel) + perception (Luxonis OAK-D) component vendors,
  the Home Assistant orchestration hub, and the OpenVoiceOS voice stack
  (5 Tier A vendor-style + 3 Tier B research-collab + community). Move #9
  opens URML's first dedicated NASA-robotics wave: three Tier A targets
  identified via a verified 2026-05-27 shortlist of JPL / Ames
  Apache-2.0 robotics projects (`nasa-jpl/rosa` NL-driven ROS agent,
  `nasa/fprime` flight-software framework with ROS 2 bridge,
  `nasa/astrobee` ISS free-flyer); sequencing leads with ROSA alone
  (RFC-0108, the closest single-repo semantic overlap with URML's reason
  for existing across nine outreach waves), with F Prime + Astrobee
  follow-ons once ROSA lands. Do not interpret outreach RFCs as a quiet
  expansion of URML's spec surface.

## Index

| # | Kind | Title | State | Last updated |
|---|---|---|---|---|
| [0000](0000-template.md) | — | RFC template | Template (not an RFC) | — |
| [0001](0001-rfc-process.md) | Spec | RFC process | Accepted | Phase 0 |
| [0002](0002-initial-primitive-vocabulary.md) | Spec | Initial Layer-2 primitive vocabulary | Implemented | 2026-05-17 |
| [0003](0003-us-alignment.md) | Spec | Strategic realignment — URML aligns with US federal robotics regulation | Accepted | 2026-05-13 |
| [0004](0004-compliance-policy.md) | Spec | Compliance policy enforcement | Accepted | 2026-05-13 |
| [0005](0005-hbom-parsing.md) | Spec | Structured HBOM parsing for Pass 5 | Draft | 2026-05-13 |
| [0006](0006-connectivity-and-link-loss.md) | Spec | Connectivity as an abstract capability and link-loss as a validated safety contract | Implemented | 2026-05-16 |
| [0007](0007-manufacturer-go-to-market.md) | Spec | Manufacturer go-to-market: URML as an opportunity and a channel for robot OEMs and component makers | Implemented | 2026-05-16 |
| [0008](0008-community-discussions.md) | Spec | Community Discussions: a public Q&A and feedback channel brought forward into Phase 0 | Implemented | 2026-05-16 |
| [0009](0009-legged-humanoid-mobility.md) | Spec | Legged and humanoid mobility in the capability manifest | Implemented | 2026-05-19 |
| [0010](0010-whole-body-bimanual-manipulation.md) | Spec | Whole-body and bimanual manipulation | Draft | 2026-05-17 |
| [0011](0011-educational-profile.md) | Spec | Educational profile | Accepted | 2026-05-19 |
| [0012](0012-research-profile.md) | Spec | Research profile | Accepted | 2026-05-19 |
| [0013](0013-industrial-layer2-primitives.md) | Spec | Industrial-profile Layer-2 primitives — pick_from, place_at, swap_tool | Implemented | 2026-05-19 |
| [0014](0014-substrate-conformance.md) | Spec | Substrate conformance — what makes a runtime URML-compatible | Draft | 2026-05-19 |
| [0015](0015-control-program-invocation.md) | Spec | Control-program invocation — calling a named substrate program | Draft | 2026-05-19 |
| [0016](0016-realtime-cyclic-manifest-block.md) | Spec | Real-time / cyclic timing declaration in the capability manifest | Draft | 2026-05-19 |
| [0017](0017-digital-io-actuation.md) | Spec | Digital-I/O actuation — driving a named substrate output | Draft | 2026-05-19 |
| [0018](0018-minimal-mcu-capability-subset.md) | Spec | Minimal-MCU capability subset in the manifest | Draft | 2026-05-19 |
| [0019](0019-autosar-adaptive-substrate.md) | Spec | AUTOSAR Adaptive substrate — binding ara::com to URML | Draft | 2026-05-20 |
| [0020](0020-autoware-av-substrate.md) | Spec | Autoware AV substrate — research-grade autonomous-vehicle profile | Draft | 2026-05-20 |
| [0021](0021-on-device-llm-bridge.md) | Spec | On-device LLM bridge — schema-derived GBNF, GGUF model contract, per-model conformance | Draft | 2026-05-21 |
| [0022](0022-warehouse-domain-profile.md) | Spec | Warehouse domain profile — mixed-traffic AMR aisles, zero new primitives | Draft | 2026-05-21 |
| [0023](0023-yaskawa-motoros2-integration.md) | Outreach | Yaskawa / MotoROS2 integration — request for comment from Yaskawa-Global maintainers | Draft | 2026-05-22 |
| [0024](0024-universal-robots-integration.md) | Outreach | Universal Robots integration — same robot, two URML adapters; request for comment from UniversalRobots maintainers | Draft | 2026-05-22 |
| [0025](0025-kuka-integration.md) | Outreach | KUKA integration — request for comment from kroshu/kuka_drivers maintainers | Draft | 2026-05-22 |
| [0026](0026-staubli-integration.md) | Outreach | Stäubli integration — request for comment from ros-industrial/staubli_val3_driver maintainers | Draft | 2026-05-22 |
| [0027](0027-mitsubishi-melfa-integration.md) | Outreach | Mitsubishi MELFA integration — request for comment from Mitsubishi-Electric-Asia maintainers | Draft | 2026-05-22 |
| [0028](0028-fanuc-integration.md) | Outreach | FANUC integration — request for comment from FANUC-CORPORATION/fanuc_driver maintainers | Draft | 2026-05-22 |
| [0029](0029-kawasaki-integration.md) | Outreach | Kawasaki integration — request for comment from Kawasaki-Robotics/khi_ros2 maintainers | Draft | 2026-05-22 |
| [0030](0030-denso-integration.md) | Outreach | Denso integration — request for comment from DENSORobot/denso_robot_ros2 maintainers | Draft | 2026-05-22 |
| [0031](0031-schunk-integration.md) | Outreach | SCHUNK integration — request for comment from SCHUNK-SE-Co-KG maintainers | Draft | 2026-05-22 |
| [0032](0032-ouster-integration.md) | Outreach | Ouster integration — request for comment from ouster-lidar/ouster-sdk maintainers | Draft | 2026-05-22 |
| [0033](0033-sick-integration.md) | Outreach | SICK integration — request for comment from SICKAG/sick_safetyscanners2 maintainers | Draft | 2026-05-22 |
| [0034](0034-festo-integration.md) | Outreach | Festo integration — request for comment from Festo-se maintainers | Draft | 2026-05-22 |
| [0035](0035-zivid-integration.md) | Outreach | Zivid integration — request for comment from zivid/zivid-python maintainers | Draft | 2026-05-22 |
| [0036](0036-hokuyo-integration.md) | Outreach | Hokuyo integration — request for comment from Hokuyo-aut/urg_node2 maintainers | Draft | 2026-05-22 |
| [0037](0037-osrf-gazebo-integration.md) | Outreach | OSRF / Gazebo Sim integration — proposal-only RFC; request for comment from gazebosim maintainers | Draft | 2026-05-22 |
| [0038](0038-ros-industrial-consortium.md) | Outreach | ROS-Industrial Consortium alignment — institutional umbrella RFC; closes the Move #1 16-vendor lighthouse program | Draft | 2026-05-22 |
| [0039](0039-sensor-schema-v0-2-iteration.md) | Spec | Sensor schema v0.2 iteration — point-cloud type, beam_count, channels, time_sync_methods, rate_hz_max (from Ouster maintainer feedback) | Draft | 2026-05-22 |
| [0040](0040-hugging-face-lerobot.md) | Outreach | Hugging Face LeRobot integration — first Move #2 RFC; proposal-only bridge; request for comment from huggingface/lerobot maintainers | Draft | 2026-05-23 |
| [0041](0041-ardupilot-integration.md) | Outreach | ArduPilot integration; Move #1 follow-on; proposal-only bridge; request for comment from ArduPilot/ardupilot maintainers | Draft | 2026-05-23 |
| [0042](0042-waymo-open-dataset.md) | Outreach | Waymo Open Dataset conformance demonstration; proposal-only; request for comment from waymo-research maintainers | Draft | 2026-05-23 |
| [0043](0043-boston-dynamics-spot-integration.md) | Outreach | Boston Dynamics Spot integration; Move #1 follow-on; shipping `SpotAdapter`; request for comment from boston-dynamics SDK maintainers | Draft | 2026-05-23 |
| [0044](0044-aws-robotics-sim-worlds.md) | Outreach | AWS Robotics simulation worlds conformance lane; proposal-only; request for comment from aws-robotics maintainers | Draft | 2026-05-23 |
| [0045](0045-physical-intelligence-openpi.md) | Outreach | Physical Intelligence (openpi) integration; Move #2 RFC; proposal-only bridge via the Inputs / Outputs extension pattern; request for comment from Physical-Intelligence/openpi maintainers | Draft | 2026-05-23 |
| [0046](0046-open-x-embodiment.md) | Outreach | Open X-Embodiment integration; Move #2 RFC; proposal-only URML annotation schema for OXE trajectories; primary public touch with Google DeepMind; request for comment from OXE governance | Draft | 2026-05-23 |
| [0047](0047-allen-institute-molmoact.md) | Outreach | Allen Institute MolmoAct integration; Move #2 RFC; proposal-only bridge with preview-and-correct loop; request for comment from Ai2 Embodied AI initiative | Draft | 2026-05-23 |
| [0048](0048-anthropic-mcp-and-agent-skills.md) | Outreach | Anthropic integration via MCP and Agent Skills; Move #2 RFC; proposal-only (URML as MCP server + URML as Agent Skill); request for comment from Anthropic | Draft | 2026-05-23 |
| [0049](0049-anybotics-anymal-integration.md) | Outreach | ANYbotics ANYmal integration; Move #1 follow-on; shipping `AnymalAdapter`; closes the legged-quadruped pair with RFC-0043; request for comment from ANYbotics maintainers | Draft | 2026-05-23 |
| [0050](0050-nvidia-isaac-lab-integration.md) | Outreach | NVIDIA Isaac integration (Isaac Lab + Isaac-GR00T); proposal-only two-vector `urml-isaac-bridge`; URML as substrate-neutral vocabulary above NVIDIA's stack; request for comment from isaac-sim and NVIDIA Isaac-GR00T maintainers | Draft | 2026-05-23 |
| [0051](0051-carla-simulator-integration.md) | Outreach | CARLA simulator integration; proposal-only `reference/carla-runtime/` and conformance lane; AV triangle with RFC-0020 (Autoware) and RFC-0042 (Waymo); request for comment from carla-simulator maintainers | Draft | 2026-05-23 |
| [0052](0052-meta-fair-vjepa2.md) | Outreach | Meta FAIR V-JEPA 2 integration; Move #2 RFC; proposal-only `urml-vjepa2-bridge` with two vectors (URML primitives as V-JEPA 2-AC action conditioning + V-JEPA 2 predictions as URML predictive-safety lane); world-model angle is unique among Move #2 targets; request for comment from facebookresearch/vjepa2 maintainers | Draft | 2026-05-23 |
| [0053](0053-open-rmf-multirobot-integration.md) | Outreach | Open-RMF multi-robot integration; proposal-only two-vector `urml-rmf-bridge` (task-source + fleet-adapter); closes the multi-robot coordination gap adjacent to RFC-0022 warehouse profile; request for comment from open-rmf maintainers | Draft | 2026-05-23 |
| [0054](0054-tri-large-behavior-models.md) | Outreach | TRI Large Behavior Models integration; Move #2 RFC; proposal-only `urml-tri-lbm-bridge` plugging into vla_foundry's `@register_model_params` and `DataParams` extension pattern; LBM-on-Atlas path via the TRI + Boston Dynamics partnership; request for comment from TRI-ML/vla_foundry maintainers | Draft | 2026-05-23 |
| [0055](0055-nvidia-cosmos-reason.md) | Outreach | NVIDIA Cosmos-Reason1 integration; Move #2 RFC; proposal-only `urml-cosmos-bridge` as a constrained-decoding wrapper over Cosmos-Reason1's reasoning VLM; reasoner emits URML primitive programs instead of free-form text; third Move #2 integration shape (reasoner, not policy or world model); request for comment from nvidia-cosmos/cosmos-reason1 maintainers | Draft | 2026-05-23 |
| [0056](0056-stanford-aloha.md) | Outreach | Stanford ALOHA and Mobile ALOHA integration; Move #2 RFC; proposal-only `urml-aloha-bridge` at the data layer (record_episodes.py extension + post-hoc annotation); reinforces RFC-0046 (OXE) at the upstream recording layer; research-collaboration shape; request for comment from MarkFzp/mobile-aloha and tonyzhaozh/aloha maintainers | Draft | 2026-05-23 |
| [0057](0057-nvidia-cosmos-predict.md) | Outreach | NVIDIA Cosmos-Predict2.5 integration; Move #2 RFC; proposal-only `urml-cosmos-predict-bridge` wiring the world model into URML's predictive-safety lane; NVIDIA-side parallel of RFC-0052 (V-JEPA 2 Vector B); composes with RFC-0055 (Cosmos-Reason1) into a closed loop; request for comment from nvidia-cosmos/cosmos-predict2.5 maintainers | Draft | 2026-05-23 |
| [0058](0058-openai-robotics.md) | Outreach | OpenAI robotics integration; Move #2 RFC; deliberate cold knock (OpenAI has not published a public robotics surface as of 2026-05-23); files for symmetry across Move #2 AI-lab coverage and to put URML on OpenAI's radar when their robotics work goes public; request for comment from OpenAI | Draft | 2026-05-23 |
| [0059](0059-drake-model-based-robotics.md) | Outreach | Drake model-based robotics integration; Move #2 RFC; proposal-only `urml-drake-bridge` with two vectors (`DrakeAdapter` substrate + analytical safety lane backed by Drake's solvers); fills the model-based-verification niche complementary to the learned-world-model lanes in RFC-0052 / RFC-0057; request for comment from RobotLocomotion/drake maintainers | Draft | 2026-05-23 |
| [0060](0060-mujoco-integration.md) | Outreach | MuJoCo physics-engine integration; Move #2 RFC; formalizes URML's existing `reference/mujoco-runtime/` stub into a full `MuJoCoAdapter` plus optional `urml_envelope_plugin`; closes the "URML supports MuJoCo" overclaim; request for comment from google-deepmind/mujoco maintainers | Draft | 2026-05-23 |
| [0061](0061-wlkata-outreach.md) | Outreach | WLKATA integration; first Move #3 RFC; proposal-only `WlkataAdapter` family targeting per-product ROS 2 packages (Mirobot / MT4 / Haro380) plus `wlkatapython` G-code-on-serial; cross-link to BRAVE simulation suite (Gazebo, MuJoCo, Isaac Lab); request for comment from wlkata maintainers | Draft | 2026-05-24 |
| [0062](0062-petoi-bittle-outreach.md) | Outreach | Petoi (Bittle / Nybble) integration; Move #3 RFC; proposal-only `PetoiAdapter` over the OpenCat serial protocol; skill-library mapping from URML primitives to OpenCat gaits; the $299 hobby-quadruped hero-demo target for Move #3; request for comment from PetoiCamp maintainers | Draft | 2026-05-24 |
| [0063](0063-hiwonder-outreach.md) | Outreach | Hiwonder integration; Move #3 RFC; proposal-only `HiwonderAdapter` family spanning MentorPi (Mecanum/Ackermann/tank), PuppyPi (quadruped), JetRover (Jetson rover), ROSPider (hexapod), JetMax (arm); catalog-breadth substrate-fungibility story; request for comment from Hiwonder maintainers | Draft | 2026-05-24 |
| [0064](0064-trossen-interbotix-outreach.md) | Outreach | Trossen Robotics Interbotix integration; Move #3 RFC; proposal-only `InterbotixAdapter` over `interbotix_ros_manipulators` (BSD-3-Clause, ROS 2 Humble + Rolling + ROS 1 Noetic legacy); US-domiciled provenance anchor for Move #3; cross-links to RFC-0040 LeRobot and RFC-0056 Stanford ALOHA; request for comment from Interbotix maintainers | Draft | 2026-05-24 |
| [0065](0065-robotis-outreach.md) | Outreach | ROBOTIS integration; first Move #4 RFC; proposal-only `RobotisAdapter` family across TurtleBot 3 + OP3 humanoid + OpenManipulator + `dynamixel_sdk`; closes the institutional loop with three existing URML outreach RFCs (RFC-0040 LeRobot, RFC-0056 Stanford ALOHA, RFC-0064 Trossen Interbotix) that transitively depend on Dynamixel; request for comment from ROBOTIS-GIT maintainers | Draft | 2026-05-24 |
| [0066](0066-agilex-outreach.md) | Outreach | AgileX Robotics integration; Move #4 RFC; proposal-only `AgileXAdapter` family across Tracer / Limo / Scout / Hunter / Bunker / Ranger mobile bases; closes the Mobile-ALOHA chassis loop (cross-link to RFC-0056) and the AgileX-LeRobot ecosystem alignment (cross-link to RFC-0040); request for comment from agilexrobotics maintainers | Draft | 2026-05-24 |
| [0067](0067-farmbot-outreach.md) | Outreach | FarmBot integration; Move #4 RFC; proposal-only `FarmBotAdapter` over the public REST + MQTT API; **URML's first outreach into the agricultural vertical**; raises a future `spec/profiles/agriculture/` profile as an open question (not proposed in this RFC); request for comment from FarmBot maintainers | Draft | 2026-05-24 |
| [0068](0068-pal-robotics-outreach.md) | Outreach | PAL Robotics integration; Move #4 RFC; proposal-only `PalAdapter` family across PMB2 / TIAGo / TIAGo Pro; the commercial mobile-manipulator niche between Move #1 stationary OEMs and Move #2's research humanoids; raises bimanual-coordination primitive question alongside RFC-0010 Draft, RFC-0047, RFC-0056; request for comment from pal-robotics maintainers | Draft | 2026-05-24 |
| [0069](0069-berkeley-humanoid-lite-outreach.md) | Outreach | Berkeley Humanoid Lite integration; Move #4 RFC; proposal-only `BerkeleyHumanoidLiteAdapter` covering sim (Isaac Lab) and real-hardware paths for the sub-$5k open-hardware humanoid from UC Berkeley Hybrid Robotics Lab; cross-link to RFC-0050 NVIDIA Isaac Lab; request for comment from HybridRobotics maintainers | Draft | 2026-05-24 |
| [0070](0070-hebi-robotics-outreach.md) | Outreach | HEBI Robotics integration; Move #4 RFC; proposal-only `HebiAdapter` for modular Series Elastic Actuator configurations; first URML deployment to fully populate the manifest's `kinematic_chain` field; CMU-rooted, US-domiciled, Apache-2.0 predominant; closes the Move #4 pilot batch; request for comment from HebiRobotics maintainers | Draft | 2026-05-24 |
| [0071](0071-robotnik-outreach.md) | Outreach | Robotnik Automation integration; first Move #5 RFC, Tier A vendor-style; proposal-only `RobotnikAdapter` family across Summit XL + RB-1 + RB-VOGUI + AGVS + rbcar; Spanish commercial industrial mobile-robotics; BSD-3-Clause predominant; cross-link to RFC-0022 warehouse profile (AGVS) and RFC-0068 PAL (Spanish); request for comment from RobotnikAutomation maintainers | Draft | 2026-05-24 |
| [0072](0072-clearpath-robotics-outreach.md) | Outreach | Clearpath Robotics integration; Move #5 RFC, Tier A vendor-style; proposal-only `ClearpathAdapter` family across TurtleBot 4 + Husky + Jackal + Dingo + Warthog; Canadian; explicit TurtleBot-4-vs-TurtleBot-3 disambiguation with RFC-0065 ROBOTIS; post-Rockwell-acquisition context noted; request for comment from clearpathrobotics maintainers | Draft | 2026-05-24 |
| [0073](0073-robotical-marty-outreach.md) | Outreach | Robotical (Marty) integration; Move #5 RFC, Tier A vendor-style; proposal-only `RoboticalMartyAdapter` over `martypy` for Marty v1 / v2 bipedal educational walking robot; UK; the bipedal counterpart to RFC-0062 Petoi Bittle quadruped; request for comment from robotical maintainers | Draft | 2026-05-24 |
| [0074](0074-deep-robotics-outreach.md) | Outreach | DEEP Robotics integration; Move #5 RFC, Tier A vendor-style; proposal-only `DeepRoboticsAdapter` family across Lite3 + M20 today and Lynx S10 (wheeled-legged hybrid, launched 2026-05-22, SDK pending) forward-declared; introduces wheeled-legged mobility class flagged for future Spec RFC; Chinese; request for comment from DeepRoboticsLab maintainers | Draft | 2026-05-24 |
| [0075](0075-stanford-pupper-outreach.md) | Outreach | Stanford Pupper integration; Move #5 RFC, first Tier B research-collab; proposal-only `StanfordPupperAdapter` for v1 / v2 (StanfordQuadruped, 1.7k stars MIT) plus Pupper v3 (Raspberry Pi 5 + 400W brushless + Luxonis SR); Stanford Robotics Club student-led; research-collab framing; request for comment from stanfordroboticsclub maintainers | Draft | 2026-05-24 |
| [0076](0076-open-dynamic-robot-initiative-outreach.md) | Outreach | Open Dynamic Robot Initiative (Solo 8 / Solo 12) integration; Move #5 RFC, Tier B research-collab; proposal-only `SoloAdapter` for torque-controlled open quadruped; first URML deployment to explicitly target `control_mode: torque`; multi-institution academic consortium (MPI Tübingen + NYU + ETH); research-collab framing; request for comment from open-dynamic-robot-initiative maintainers | Draft | 2026-05-24 |
| [0077](0077-mit-champ-outreach.md) | Outreach | MIT CHAMP integration; Move #5 RFC, Tier B research-collab; proposal-only `ChampAdapter` as control-framework target (not hardware); consumes CHAMP's URDF-parameterised whole-body controller for MIT Mini Cheetah / ANYmal / Spot / LittleDog / SpotMicroAI / OpenQuadruped; mirrors RFC-0070 HEBI per-customer-geometry pattern; ROS 1 only; cross-link to RFC-0043 Spot and RFC-0049 ANYmal; request for comment from chvmp maintainers | Draft | 2026-05-24 |
| [0078](0078-orca4-ros-maritime-outreach.md) | Outreach | Orca4 / ros-maritime integration; Move #5 RFC, Tier B research-collab; alignment + documentation (not new adapter) layering URML's existing `marine-runtime` BlueRovAdapter with the community Orca4 ROS 2 stack on top of BlueROV2; cross-link to RFC-0041 ArduPilot; request for comment from clydemcqueen and ros-maritime working group | Draft | 2026-05-24 |
| [0079](0079-open-bionics-outreach.md) | Outreach | Open Bionics integration; Move #5 RFC, Tier B research-collab + commercial courtesy; URML's first accessibility-identity outreach; two-surface engagement (academic OpenBionics GitHub org, dormant, last commits 2018–2020 / commercial Open Bionics Ltd, no GitHub Issue surface); no spec or profile commitment; lightest engagement payload in Move #5; request for comment from OpenBionics maintainers (if reachable) + courtesy outreach to Open Bionics Ltd | Draft | 2026-05-24 |
| [0080](0080-uc-berkeley-autolab-outreach.md) | Outreach | UC Berkeley AUTOLAB integration; first Move #6 RFC, Tier B research-collab; PI Ken Goldberg (distinct from RAIL/Abbeel and Hybrid Robotics Lab/RFC-0069); dex-net + gqcnn + autolab_core engagement; EECS 206A/B coursework integration; request for comment from BerkeleyAutomation maintainers | Draft | 2026-05-25 |
| [0081](0081-caltech-amber-outreach.md) | Outreach | Caltech AMBER Lab integration; Move #6 RFC, Tier B research-collab; PI Aaron Ames; strongest formal-methods alignment with URML's static-verification story in any outreach wave; `obelisk` composition + prosthetics complement to RFC-0079; request for comment from Caltech-AMBER maintainers | Draft | 2026-05-25 |
| [0082](0082-upenn-grasp-outreach.md) | Outreach | UPenn GRASP Lab integration; Move #6 RFC, Tier B research-collab; PI Vijay Kumar; KumarRobotics 93 repos with msckf_vio 1.9k + kr_autonomous_flight 771; multi-agent + aerial + ground-aerial heterogeneous fleet research; surfaces multi-agent coordination primitive question for future Spec RFC; request for comment from KumarRobotics maintainers | Draft | 2026-05-25 |
| [0083](0083-uw-personal-robotics-outreach.md) | Outreach | UW Personal Robotics Lab integration; Move #6 RFC, Tier B research-collab; PI Siddhartha Srinivasa (distinct from Imperial PRL/Demiris per RFC-0088); ADA + HERB + aikido composition; CSE 490R coursework; request for comment from personalrobotics maintainers | Draft | 2026-05-25 |
| [0084](0084-umich-robotics-outreach.md) | Outreach | UMich Robotics Department + CURLY lab integration; Move #6 RFC, Tier B research-collab; PIs Maani Ghaffari + Jessy Grizzle; ROB 101 / ROB 102 / ROB 401 robot-agnostic undergraduate curriculum (most teaching-pipeline-ready URML target in Move #6); request for comment from UMich-CURLY + department leadership | Draft | 2026-05-25 |
| [0085](0085-northwestern-crb-outreach.md) | Outreach | Northwestern Center for Robotics and Biosystems (CRB) integration; Move #6 RFC, Tier B research-collab; PIs Todd Murphey + Ed Colgate + Kevin Lynch; ergodic-control + HAND ERC ($52M/10y) + speculative Lynch textbook ask; GPL-3.0 license-fit note for URML Apache-2.0 reference/; request for comment from MurpheyLab + CRB faculty | Draft | 2026-05-25 |
| [0086](0086-eth-asl-outreach.md) | Outreach | ETH Zurich Autonomous Systems Lab (ASL) integration; Move #6 RFC, Tier B research-collab; PI Roland Siegwart; largest GitHub footprint in Move #6 (458 repos, 2.3k followers, maplab 2.8k stars); distinct from ETH RSL (Hutter, covered indirectly via RFC-0049 ANYmal); request for comment from ethz-asl maintainers | Draft | 2026-05-25 |
| [0087](0087-tu-delft-cognitive-robotics-outreach.md) | Outreach | TU Delft Cognitive Robotics integration; Move #6 RFC, Tier B research-collab; PI Martijn Wisse; bio-inspired locomotion + Mobile Robotics course + CoppeliaSim Spec RFC question; request for comment from tud-cor maintainers | Draft | 2026-05-25 |
| [0088](0088-imperial-personal-robotics-outreach.md) | Outreach | Imperial College London Personal Robotics Lab integration; Move #6 RFC, Tier B research-collab + off-GitHub courtesy; PI Yiannis Demiris (distinct from UW PRL/Srinivasa per RFC-0083); no verified standalone GitHub Issue surface — engagement via courtesy email to y.demiris@imperial.ac.uk; request for comment from Imperial PRL | Draft | 2026-05-25 |
| [0089](0089-oxford-ori-outreach.md) | Outreach | Oxford Robotics Institute (ORI) integration; Move #6 RFC, Tier B research-collab; PI Paul Newman; thin GitHub presence (only 2 public repos in oxford-robotics-institute); cross-link to RFC-0042 (Waymo) for Radar RobotCar Dataset annotation + RFC-0020 (Autoware) for AV research; request for comment from ORI maintainers | Draft | 2026-05-25 |
| [0090](0090-utokyo-jsk-outreach.md) | Outreach | University of Tokyo JSK Robotics Lab integration; Move #6 RFC, Tier B research-collab; PIs Masayuki Inaba + Kei Okada; most mature Asian academic ROS surface (20+ years); jsk_recognition + jsk_visualization composition + EusLisp / roseus + jsk_aerial_robot; request for comment from jsk-ros-pkg maintainers | Draft | 2026-05-25 |
| [0091](0091-qut-centre-for-robotics-outreach.md) | Outreach | QUT Centre for Robotics (Peter Corke) integration; Move #6 RFC, Tier B research-collab; twelfth and final Move #6 RFC; PI Peter Corke; personal handle (`petercorke`) plus institutional QUT Centre; robotics-toolbox-python global teaching standard + RVC3 textbook (speculative URML-appendix ask) + AuSRoS 2025+ ROS 2 labs + ARC Centre of Excellence; request for comment from Peter Corke | Draft | 2026-05-25 |
| [0092](0092-twisted-fields-acorn-outreach.md) | Outreach | Twisted Fields / Acorn integration; first Move #7 RFC, Tier A vendor-style; agriculture-vertical second wave (after RFC-0067 FarmBot); Apache-2.0 upstream (clean license fit); solar-powered modular precision-farming rover; `acorn-precision-farming-rover` 275 stars + KiCAD electronics + mechanical CAD; AcornAdapter proposed in `reference/agriculture-runtime/`; request for comment from Twisted-Fields maintainers | Draft | 2026-05-26 |
| [0093](0093-sentera-outreach.md) | Outreach | Sentera integration; Move #7 RFC, Tier A vendor-style; first URML ag-drone RFC; SenteraLLC org 63 public repos with `py-radiometric-corrections` Apache-2.0 + MAVSDK forks; documented MAVLink integration for Double 4K / 6X multispectral payloads; SenteraAdapter proposed in `reference/px4-runtime/sentera/`; request for comment from SenteraLLC maintainers | Draft | 2026-05-26 |
| [0094](0094-burro-robotics-outreach.md) | Outreach | Burro Robotics integration; Move #7 RFC, Tier A vendor-style; first commercial ag-cobot RFC; 300+ units deployed across 40+ customers in 6 countries with $24M Series B 2024; burro-robotics org 34 public repos + documented BOSS Cloud API for fleet telemetry + WMS; BurroAdapter proposed in `reference/agriculture-runtime/`; cross-link to RFC-0053 Open-RMF; request for comment from burro-robotics maintainers | Draft | 2026-05-26 |
| [0095](0095-ucla-agricruiser-outreach.md) | Outreach | UCLA AgriCruiser integration; Move #7 RFC, Tier B research-collab; USDA NIFA-funded (grants 2024-67021-42528, 2022-67022-37021, 2021-67022-34200) over-the-row platform; `agri-cruiser/agri-cruiser` 15 stars C++ GPL-3.0; license-fit note for URML Apache-2.0 reference/ (cross-citation only, RFC-0085 precedent); request for comment from agri-cruiser maintainers | Draft | 2026-05-26 |
| [0096](0096-inrae-romea-outreach.md) | Outreach | INRAE Romea integration; Move #7 RFC, Tier B research-collab; strongest EU-academic ag-robotics surface; Romea org 79 public repos ROS 2 native Apache-2.0 predominant; `cropcraft` 105 stars procedural ag-sim world generator + `romea-ros2-mobile-base` four-wheel-steering platforms; cross-link to RFC-0086 ETH ASL large-ROS-2-org template + RFC-0095 US counterpart; request for comment from Romea maintainers | Draft | 2026-05-26 |
| [0097](0097-earthsense-terrasentia-outreach.md) | Outreach | EarthSense / TerraSentia integration; Move #7 RFC, Tier B research-collab; hybrid academic UIUC + commercial spin-out structure; TerraSentia org 7 public repos including `livox_ros_driver2` + `FAST-LIO-SAM` + `terra-lidar-imu-init` GPL-2.0; under-canopy crop phenotyping (<15 lbs, 11" width); Nature Communications 2025 142-field validation; license-clarity gate before adapter; cross-link to RFC-0088 hybrid + RFC-0089 thin-GitHub precedents; request for comment from TerraSentia + EarthSense | Draft | 2026-05-26 |
| [0098](0098-cornell-agxrp-outreach.md) | Outreach | Cornell AgXRP integration; Move #7 RFC, Tier B research-collab + off-GitHub courtesy; PI Jonathan Jaramillo; partnerships Cornell + University of Idaho + 4-H + Agriculture in the Classroom + community colleges; affordable open-source ag-robotics for K-12 STEM; NO verified GitHub repo or org (off-GitHub courtesy email to experiential.bot/agxrp Contact form); precedent RFC-0088 Imperial PRL off-GitHub framing; request for comment from AgXRP team | Draft | 2026-05-26 |
| [0099](0099-wageningen-field-robot-event-outreach.md) | Outreach | Wageningen Field Robot Event 2026 integration; eighth and final Move #7 RFC, Tier B research-collab + community-channel framing (closes the agriculture wave); FRE 2026 June 16-18 2026 at International DLG Crop Production Centre Bernburg Germany; annual European ag-robotics competition; community engagement via FRE Discord (linked from fieldrobotevent.eu); URML primitive vocabulary as candidate teaching artifact for entrants; request for comment from FRE 2026 organising committee | Draft | 2026-05-26 |
| [0100](0100-irobot-roomba-outreach.md) | Outreach | iRobot Roomba integration; first Move #8 RFC, Tier A vendor-style; opens the home-assistance wave; community LAN-control SDK (`koalazak/dorita980` MIT 1.1k stars + `jeremywillans/ha-rest980-roomba` + Home Assistant `roomba`) — iRobot itself has no public developer SDK; proposes new `reference/home-runtime/` package with `RoombaAdapter` as first adapter; region-based mobility (mapped rooms / Spaces, not free coordinates); request for comment from dorita980 + ha-rest980-roomba maintainers | Draft | 2026-05-26 |
| [0101](0101-husqvarna-automower-outreach.md) | Outreach | Husqvarna Automower integration; Move #8 RFC, Tier A vendor-style; cleanest first-class-vendor-API surface in Move #8; official Automower Connect API (OpenAPI 3.0 + OAuth 2.0) at `developer.husqvarnagroup.cloud` + `Thomas55555/aioautomower` MIT Python wrapper; `HusqvarnaAutomowerAdapter` proposed in `reference/home-runtime/`; zone-based mobility (geofence zones); cloud-only API; request for comment from aioautomower maintainer | Draft | 2026-05-26 |
| [0102](0102-bear-robotics-servi-outreach.md) | Outreach | Bear Robotics / Servi integration; Move #8 RFC, Tier A vendor-style but **off-GitHub courtesy** (no customer-facing GitHub Issue surface on bearrobotics org — 25 repos, all infrastructure forks); documented Bear Cloud API (gRPC + REST) at `cloud.api.bearrobotics.ai`; senior-living + care-home adjacency framing for home-assistance continuum; cross-link to RFC-0094 (Burro Robotics commercial-cobot-fleet precedent); engagement via Bear Cloud developer portal Contact form; RFC-0088 / RFC-0098 off-GitHub precedents | Draft | 2026-05-26 |
| [0103](0103-maytronics-dolphin-outreach.md) | Outreach | Maytronics Dolphin integration; Move #8 RFC, Tier A vendor-style; aquatic-subsystem niche broadens URML's substrate-neutral claim across indoor floor + outdoor lawn + pool home-assistance continuum; community surface `sh00t2kill/dolphin-robot` (Python, 75 stars, license-unset — clarification gate before adapter code); reverse-engineered Maytronics WiFi API; `MaytronicsDolphinAdapter` proposed in `reference/home-runtime/`; region-based mobility (floor / walls / waterline / steps); request for comment from dolphin-robot maintainer | Draft | 2026-05-26 |
| [0104](0104-robotis-dynamixel-outreach.md) | Outreach | ROBOTIS Dynamixel integration; Move #8 RFC, Tier A vendor-style; first servo-vendor RFC in URML's outreach landscape; ROBOTIS-GIT org (80+ repos, Apache-2.0 predominant, ROS 2 native); `DynamixelSDK` 587 stars + `dynamixel_hardware_interface` 34 stars; documented cross-citation (NOT stand-alone adapter — Dynamixel is actuator-substrate, not platform-substrate); home-scale / educational / research counterpart to Move #1 industrial-component-vendor RFCs (RFC-0031-0034); request for comment from ROBOTIS-GIT maintainers | Draft | 2026-05-26 |
| [0105](0105-luxonis-oak-d-outreach.md) | Outreach | Luxonis OAK-D / DepthAI integration; Move #8 RFC, Tier B research-collab; de facto affordable 3D-perception module for home / educational / research robotics; `luxonis/depthai-python` (MIT, 429 stars, Discussions enabled — preferred surface) + `luxonis/depthai-ros` (MIT, 346 stars); documented cross-citation (perception substrate, like Dynamixel for actuators); home-scale counterpart to Move #1 industrial-perception-vendor RFCs (RFC-0032 Ouster, RFC-0033 SICK); request for comment from luxonis maintainers | Draft | 2026-05-26 |
| [0106](0106-home-assistant-outreach.md) | Outreach | Home Assistant integration; Move #8 RFC, Tier B research-collab + community; **strategic anchor for the home-assistance wave** (every Move #8 vendor target already lives as an HA integration); `home-assistant/core` Apache-2.0 87.3k stars under Open Home Foundation (2024+); URML primitives compile into HA automation YAML; candidate `urml` HACS integration prototype; cross-link to RFC-0100 / 0101 / 0103 (Move #8 vendor dependents), RFC-0021 (NL layer), RFC-0014 (conformance); request for comment from home-assistant/core maintainers | Draft | 2026-05-26 |
| [0107](0107-openvoiceos-outreach.md) | Outreach | OpenVoiceOS integration; eighth and final Move #8 RFC, Tier B research-collab + community (closes the home-assistance wave); pivoted from `rhasspy/rhasspy3` (archived shortly before this RFC drafted) to `OpenVoiceOS/ovos-core` (Apache-2.0, 275 stars, NGI Zero Commons Fund grant Oct 2025); post-Mycroft independent voice-stack trajectory (distinct from HA / Open Home Foundation umbrella covered indirectly via RFC-0106); composition direction voice -> OVOS intent -> URML primitive -> substrate; request for comment from OpenVoiceOS maintainers | Draft | 2026-05-26 |
| [0108](0108-nasa-jpl-rosa-outreach.md) | Outreach | NASA-JPL ROSA integration; **first Move #9 RFC**, Tier A vendor-style; proposal-only URML Langchain tool that ROSA's agent registers, emitting validated URML programs in place of raw `rospy` / `rclpy` calls with URML's manifest-gated validator as a static safety check before any topic publishes; `nasa-jpl/rosa` Apache-2.0 1.5k stars Langchain-based ROS 1/2 agent (`jpl-rosa` on PyPI); closest single-repo semantic overlap with URML's reason for existing across nine outreach waves; cross-link to RFC-0040 (LeRobot bridge precedent), RFC-0073 (Robotical Marty engagement-driven adapter pattern), `reference/llm-bridge/` + `reference/ros2-runtime/` + `reference/isaac-runtime/`; request for comment from `nasa-jpl/rosa` maintainers (@RobRoyce, JPL AI Group) | Draft | 2026-05-27 |

## Lifecycle states

Per RFC-0001:

- **Draft** — Author working on it. Not yet open for review.
- **Open** — Open for review; the comment window is active.
- **Accepted** — Approved by the governance body (Phase 0: sole maintainer; Phase 1+: steering committee). Authoritative; implementation may begin.
- **Implemented** — The RFC's normative changes have landed in the spec and at least the reference implementations required for conformance.
- **Rejected** — Considered and not adopted. Stays in the directory as historical record; the RFC body documents the reasoning.
- **Superseded** — Replaced by a later RFC. Header links to the successor.
- **Withdrawn** — Author withdrew before the decision. Stays as historical record.

State changes are recorded in the RFC's own header, not here; this table reflects the current state at index update.

## How to file an RFC

1. Copy [`0000-template.md`](0000-template.md) to `NNNN-short-kebab-name.md`, where `NNNN` is the next unused number (zero-padded to four digits).
2. Fill in the template. The required sections are non-negotiable; saying "N/A" in one is fine if it's truly N/A and you explain why.
3. Open a PR titled `RFC-NNNN: <short title>`. The PR is the comment window.
4. The maintainer (Phase 0) or a steering-committee reviewer (Phase 1+) advances the state header.

A Phase 0 RFC may be authored, reviewed, and merged by the same person. The author reviews their own work against the self-review checklist in RFC-0001 §Self-review. The discipline matters: future contributors inherit a real decision trail rather than a folkloric one.
