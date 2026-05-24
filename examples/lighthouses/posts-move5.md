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

# Move #5 post bodies

Copy-paste-ready Issue / Discussion bodies for the Move #5 outreach RFCs in [`docs/rfcs/`](../../docs/rfcs/). Nine RFCs split into **Tier A vendor-style (4): Robotnik, Clearpath, Robotical Marty, DEEP Robotics** and **Tier B research-collab (5): Stanford Pupper, Open Dynamic Robot Initiative, MIT CHAMP, Orca4 + ros-maritime, Open Bionics**.

Ledger state lives in [`outreach-move5.yaml`](outreach-move5.yaml). After posting, set `posted_url`, update `last_touch`, and update `next_action`.

Voice: founder posts under his GitHub identity. RFC author field already reads `Ido Yahalomi (greenvh@gmail.com)`. Posts sign as the URML maintainer; do not impersonate URML as an organization.

---

## RFC-0071: Robotnik Automation

**Post to:** https://github.com/RobotnikAutomation/agvs/issues/new (most-starred platform repo at 195 stars) or https://github.com/RobotnikAutomation/summit_xl_common/issues/new
**Title:** `Proposal: RobotnikAdapter family for URML's substrate-neutral robot-intent language (Summit XL / RB-1 / RB-VOGUI / AGVS / rbcar)`

**Body:**

```markdown
Proposing a `RobotnikAdapter` family that covers your published ROS 2 platforms under one URML adapter family: Summit XL / XL HL / X, RB-1, RB-VOGUI, AGVS, and rbcar. [URML](https://urml.dev) Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) plus the industrial-profile extensions (`pick_from`, `place_at`, `swap_tool`) map onto each platform's ROS 2 surface, with mounted-arm composition (Summit XL + UR5 or Franka) handled via URML's manifest composition pattern.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). Robotnik fills a distinctive niche in URML's outreach landscape between Move #4 PAL Robotics (Spanish commercial humanoid mobile manipulator) and Move #4 AgileX (Chinese research-grade mobile bases): commercial industrial mobile robotics with 456 public repos, 161 followers, and BSD-3-Clause predominant licensing.

This is proposal-only, posted as URML's first **Move #5** outreach (Tier 2 candidates promoted from URML's Move #4 adjacent-niches research pass). No adapter code in this PR. The canonical per-platform repos, the mounted-arm composition design, and the AGVS coordination with URML's RFC-0022 warehouse profile are observable choices worth your input before shipping.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0071-robotnik-outreach.md

## Feedback we'd value

1. **Adapter home.** URML repo (`reference/mobile-runtime/src/mobile_runtime/robotnik/`), RobotnikAutomation contributed example, both?
2. **Canonical per-platform repos.** Could you confirm the canonical first-class repos for Summit XL, RB-1, RB-VOGUI, AGVS, and rbcar in your 456-repo org?
3. **Mounted-arm composition.** What is your recommended approach to URML composing a Summit-XL-base manifest with a UR5-arm manifest at validation time?
4. **AGVS coordination.** Is there interest in coordinating with URML's RFC-0022 warehouse-profile draft on the AGVS use case?
5. **Per-platform variant manifests.** Per-variant manifests (Summit XL / XL HL / X) or parametric with a `variant:` field?
6. **Conformance lane.** Open to a URML conformance line on the platform-repo READMEs or at robotnik.eu?

Thanks for the breadth of the Robotnik ROS 2 catalog and the long-standing BSD-3-Clause posture. The European commercial industrial-mobile-robotics anchor is exactly what URML's outreach landscape needs.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0072: Clearpath Robotics

**Post to:** https://github.com/clearpathrobotics/cpr_gazebo/issues/new (most-active general repo at 233 stars) or https://github.com/clearpathrobotics/clearpath_common/issues/new
**Title:** `Proposal: ClearpathAdapter family for URML's substrate-neutral robot-intent language (TurtleBot 4 + Husky + Jackal + Dingo + Warthog)`

**Body:**

```markdown
Proposing a `ClearpathAdapter` family targeting your TurtleBot 4, Husky, Jackal, Dingo, and Warthog platforms via your published ROS 2 packages. [URML](https://urml.dev) Layer-2 primitives map onto each platform's `/cmd_vel` and Nav2 goal-pose surfaces, with per-platform kinematic constraints enforced by URML's static verifier from the manifest.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). Clearpath complements URML's existing institutional outreach in the mobile-platform tier: ROBOTIS (RFC-0065 TurtleBot 3, Korean DIY-kit), AgileX (RFC-0066 research-grade Chinese mobile bases), PAL (RFC-0068 Spanish commercial humanoid mobile manipulator), Robotnik (RFC-0071 Spanish commercial industrial). Clearpath is the Canadian Western-channel anchor with mature ROS 2 ecosystem and the post-Rockwell industrial-automation context.

**TurtleBot 4 vs TurtleBot 3 disambiguation.** URML treats your TurtleBot 4 (Create-3-based, pre-configured for ROS 2 out-of-box) and ROBOTIS' TurtleBot 3 (DIY OpenCR + Dynamixel kit) as distinct first-class adapter targets. Same TurtleBot trademark, different hardware lineage, different audiences. The URML manifest namespacing (`clearpath_turtlebot4_standard` vs `robotis_turtlebot3_burger`) keeps them disambiguated.

This is proposal-only, posted as part of URML's **Move #5** outreach. No adapter code in this PR. The canonical per-platform repos, the Dingo D/O variant manifests, the post-Rockwell maintenance posture, and the TurtleBot 4 / TurtleBot 3 cross-coordination are observable choices worth your input before shipping.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0072-clearpath-robotics-outreach.md

## Feedback we'd value

1. **Adapter home.** URML repo, Clearpath contributed example, both?
2. **Canonical per-platform repos.** Could you confirm the canonical first-class repos for TurtleBot 4 / Husky / Jackal / Dingo / Warthog in your 314-repo org?
3. **TurtleBot 4 cross-coordination.** Interest in coordinating with URML's open RFC-0065 (ROBOTIS) outreach so URML's TurtleBot 3 and TurtleBot 4 manifests stay consistent at the program-portability layer?
4. **Dingo variant manifests.** Per-variant (D differential / O omnidirectional) or parametric?
5. **Post-Rockwell maintenance posture.** Has the GitHub maintenance and release cadence stabilised post-acquisition?
6. **Conformance lane.** Open to a URML conformance line on the TurtleBot 4 README or clearpathrobotics.com documentation?

Thanks for the catalog breadth, the long-standing ROS contribution record (`cpr_gazebo`, `robot_upstart`, `LMS1xx`), and the ROSCon 2024 workshop. The Canadian Western-channel positioning is exactly what URML needs alongside the Asian and European mobile-platform anchors.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0073: Robotical (Marty)

**Post to:** https://github.com/robotical/martypy/issues/new
**Title:** `Proposal: RoboticalMartyAdapter for URML's substrate-neutral robot-intent language (Marty v1 / v2 via martypy)`

**Body:**

```markdown
Proposing a `RoboticalMartyAdapter` that wraps `martypy` to translate [URML](https://urml.dev) Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`, plus posture composition) onto Marty's skill-library command surface for v1 and v2. The mapping mirrors URML's existing Petoi Bittle adapter (RFC-0062, quadruped at similar price tier): skill-library calls (`walk`, `kick`, `arms`, `lean`, `eyes`, `dance`) instead of per-joint targets.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). Marty fills the bipedal educational walking robot niche in URML's outreach landscape — Petoi Bittle's quadruped counterpart at the same audience tier.

This is proposal-only, posted as part of URML's **Move #5** outreach. No adapter code in this PR. The triple-transport priority (serial / WebSocket / BLE), the active-development cadence question (latest release v3.6.6 on 2024-01-12 — is the platform actively developed or in maintenance mode?), and the MartyBlocks-vs-URML positioning are observable choices worth your input before shipping.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0073-robotical-marty-outreach.md

## Feedback we'd value

1. **Adapter home.** URML repo (`reference/edu-runtime/src/edu_runtime/robotical/`), robotical contributed example, both?
2. **Active development cadence.** Is the platform actively developed or in maintenance mode?
3. **Transport priority.** Which transport should URML's adapter default to (serial / WebSocket / BLE)?
4. **MartyBlocks alignment.** Interest in coordinating URML's natural-language layer with MartyBlocks' block-based layer?
5. **Conformance lane.** Open to a URML conformance line on robotical/martypy README or robotical.io docs?

Thanks for `martypy`, MartyBlocks, and the UK education-channel reach. Bipedal walking education is a niche URML's existing outreach lacked.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0074: DEEP Robotics

**Post to:** https://github.com/DeepRoboticsLab/Lite3_MotionSDK/issues/new (the top-starred `rl_training` has Issues DISABLED; pivot to a sibling SDK repo with Issues enabled)
**Optional cross-reference:** https://github.com/DeepRoboticsLab/Lite3_rl_deploy/issues/new
**Title:** `Proposal: DeepRoboticsAdapter family for URML's substrate-neutral robot-intent language (Lite3 / M20 today, Lynx S10 forward-declared)`

**Body:**

```markdown
Proposing a `DeepRoboticsAdapter` family targeting your published `Lite3_MotionSDK`, `sdk_deploy` ROS 2, and Lite3 / M20 stack today, with the **Lynx S10** (launched 2026-05-22) as a forward target pending SDK publication. [URML](https://urml.dev) Layer-2 primitives map onto your motion-command surfaces and ROS 2 topics without changes upstream.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). DEEP Robotics introduces a **mobility class URML has not previously declared**: wheeled-legged hybrid. The Lynx S10 (16 joints, sub-20kg, 8 m/s, IP66) is the first URML outreach target with this morphology. The RFC flags the new mobility-class vocabulary as an **open question for a future URML Spec RFC** rather than proposing the Layer-1 schema change inline.

This is proposal-only, posted as part of URML's **Move #5** outreach. No adapter code in this PR. The Lynx S10 portion is forward-declared (SDK pending publication). Beyond Lynx, the adapter family also covers Lite3 (the existing flagship quadruped) and M20 (industrial quadruped).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0074-deep-robotics-outreach.md

## Feedback we'd value

1. **Lynx S10 SDK timeline.** When is the published SDK expected?
2. **Adapter home.** URML repo, DeepRoboticsLab contributed example, both?
3. **Best Issue surface.** `rl_training` has Issues disabled; is `Lite3_MotionSDK` the right place to file substantive integration discussion, or do you prefer `sdk_deploy` / a different repo?
4. **Wheeled-legged mobility-class vocabulary.** Recommendation for URML's manifest schema?
5. **Isaac Lab cross-link.** `rl_training` is Isaac Lab-based; interest in coordinating with URML's open RFC-0050 (NVIDIA Isaac Lab) outreach?
6. **Conformance lane.** Open to a URML conformance line on `Lite3_MotionSDK` README or DEEP Robotics product documentation?

Thanks for the Lite3 ecosystem (Lite3_MotionSDK, Lite3_rl_deploy, sdk_deploy ROS 2) and for the Lynx S10 launch. The wheeled-legged class is the most distinctive integration shape URML has encountered, and your existing SDKs make this proposal a lot more concrete than it otherwise would have been.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0075: Stanford Pupper

**Post to:** https://github.com/stanfordroboticsclub/StanfordQuadruped/issues/new
**Title:** `Research-collab proposal: StanfordPupperAdapter for URML's substrate-neutral robot-intent language (v1/v2 + Pupper v3)`

**Body:**

```markdown
Hi Stanford Robotics Club,

Posting this as a research-collaboration proposal. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. Proposing a `StanfordPupperAdapter` that wraps your Python control surface (`run_robot.py` and the joystick + hardware-control modules) to translate URML Layer-2 primitives onto Pupper gait / posture calls. Like URML's Petoi Bittle adapter (RFC-0062, similar tier), the mapping is skill-library-driven rather than joint-target-driven.

URML is targeting Pupper because the platform represents the **build-it-yourself** education tier between hobby-servo quadrupeds (Bittle) and torque-controlled research quadrupeds (Solo, MIT Cheetah). Students who build their own quadruped from your published BOM and want a substrate-neutral programming abstraction would benefit from URML's English-to-program layer.

This is proposal-only, posted as part of URML's **Move #5** outreach (Tier B research-collab). No adapter code in this PR.

Two open questions stand out: (a) the canonical Pupper v3 repo location (the StanfordQuadruped README notes v3 development is happening elsewhere), and (b) authoritative v3 manifest values (DOF, mass, height pending confirmation).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0075-stanford-pupper-outreach.md

## Feedback we'd value

1. **Canonical Pupper v3 repo.** Where does v3 live on GitHub?
2. **Authoritative v3 manifest values.** DOF, mass, height, sensor inventory pending confirmation.
3. **Adapter home.** URML repo, contributed example under stanfordroboticsclub, both?
4. **Coursework integration.** Interest in including URML primitive emission in CS-225a or related Pupper-using courses?
5. **v1/v2 vs v3 priority.** Should URML's adapter prioritise the v3 line, the legacy surface, or both equally?
6. **Conformance lane.** Open to a URML conformance line in the Pupper README or course materials?

Thanks for Stanford Pupper and the open-hardware build-it-yourself posture. The education-via-construction audience is exactly the one URML's substrate-neutral story is designed for.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0076: Open Dynamic Robot Initiative (Solo)

**Post to:** https://github.com/open-dynamic-robot-initiative/master-board/issues/new
**Title:** `Research-collab proposal: SoloAdapter for URML's substrate-neutral robot-intent language (Solo 8 / Solo 12 torque-controlled)`

**Body:**

```markdown
Hi ODRI maintainers,

Posting this as a research-collaboration proposal. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. Proposing a `SoloAdapter` that wraps the `master-board` firmware interface to translate URML Layer-2 primitives onto Solo 8 / Solo 12's torque-controlled actuators.

URML is targeting Solo because it represents a control-mode URML has not directly engaged with: **torque-controlled** quadrupeds. Where Stanford Pupper (parallel RFC-0075) is hobby-servo and MIT CHAMP (parallel RFC-0077) is a position-level controller framework, Solo is the canonical European torque-controlled research quadruped, ERC-funded, open-hardware across MPI Tübingen / NYU / ETH Zürich.

The key open question this RFC raises: **`move_to` semantics on torque-controlled hardware**. URML's `move_to` has not previously targeted a pure-torque-controlled substrate. Should `move_to` target the position-level high-level controller (the policy or planner above the torque loop), or the torque-level interface directly? This is the design choice the ODRI consortium's input would shape.

This is proposal-only, posted as part of URML's **Move #5** outreach (Tier B research-collab). No adapter code in this PR.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0076-open-dynamic-robot-initiative-outreach.md

## Feedback we'd value

1. **`move_to` semantics on torque-controlled hardware.** Target the high-level controller above the torque loop, or the torque interface directly?
2. **Adapter home.** URML repo, ODRI contributed example, both?
3. **Authoritative Solo 8 / Solo 12 manifest values.** DOF, mass, dimensions, BOM cost pending consortium confirmation.
4. **Cross-institution coordination.** Best contact thread across MPI / NYU / ETH for substantive design discussion?
5. **Research-publication alignment.** Interest in coordinating a URML conformance lane with an ODRI publication?
6. **Conformance lane.** Open to a URML conformance line on `master-board` README or ODRI documentation?

Thanks for `open_robot_actuator_hardware`, `master-board`, `open-motor-driver-initiative`, and the ERC-funded open-science posture across the ODRI consortium. The torque-controlled research-quadruped class is exactly what URML's manifest schema's `control_mode: torque` field was designed for.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0077: MIT CHAMP

**Post to:** https://github.com/chvmp/champ/discussions/new (Discussions enabled; or labelled Issue if maintainer prefers)
**Title:** `Research-collab proposal: ChampAdapter for URML's substrate-neutral robot-intent language (control-framework adapter consuming CHAMP)`

**Body:**

```markdown
Hi chvmp,

Posting this as a research-collaboration proposal. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. Proposing a `ChampAdapter` that consumes CHAMP as a control-framework target (not a hardware target), routing URML programs onto any CHAMP-supported URDF (MIT Mini Cheetah, ANYmal, Spot, LittleDog, SpotMicroAI, OpenQuadruped).

URML's adapter pattern usually targets hardware (Spot via Boston Dynamics SDK, ANYmal via ANYbotics SDK). CHAMP is a different shape: a whole-body controller framework that abstracts the hardware geometry via URDF. A URML CHAMP adapter is **the second path to the same hardware**. URML's existing `SpotAdapter` (RFC-0043) and `AnymalAdapter` (RFC-0049) dispatch through proprietary SDKs; `ChampAdapter` dispatches through the open-source CHAMP controller on the same hardware. URML's user picks based on whether they need the proprietary SDK's full-feature surface or the open controller's customisability (gait research, sim-to-real).

This is proposal-only, posted as part of URML's **Move #5** outreach (Tier B research-collab). No adapter code in this PR.

Two open questions stand out: (a) ROS 2 timeline (CHAMP is currently ROS 1 only — Kinetic / Melodic / Noetic), and (b) the per-customer-URDF manifest pattern (URML would ship example manifests covering CHAMP's supported URDFs; the deploying user adapts per their setup, mirroring URML's RFC-0070 HEBI per-customer-geometry approach).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0077-mit-champ-outreach.md

## Feedback we'd value

1. **ROS 2 timeline.** Is CHAMP ROS 2 support planned?
2. **Per-platform vs platform-agnostic manifests.** Per-URDF example manifests or a single parametric `champ_*` manifest?
3. **Adapter home.** URML repo, chvmp contributed example, both?
4. **SpotAdapter / ChampAdapter coexistence.** Documented user guidance for picking between proprietary-SDK and CHAMP paths on the same hardware?
5. **ANYmal cross-coordination.** Should URML coordinate with the open RFC-0049 (ANYmal) thread on CHAMP coexistence?
6. **Conformance lane.** Open to a URML conformance line on `chvmp/champ` README or in Discussions?

Thanks for CHAMP. The whole-body controller framework + URDF-parameterised approach is one of the cleanest abstraction shapes URML has encountered, and the MIT lineage gives it the institutional credibility URML's research-tier story needs.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0078: Orca4 / ros-maritime

**Post to:** https://github.com/clydemcqueen/orca4/issues/new
**Optional cross-reference:** `ros-maritime` working-group canonical surface (pending verification)
**Title:** `Research-collab proposal: align URML's marine-runtime with Orca4 (ROS 2 dispatch path alongside existing MAVLink-direct BlueRovAdapter)`

**Body:**

```markdown
Hi clydemcqueen,

Posting this as a research-collaboration proposal. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML already ships a `BlueRovAdapter` in `reference/marine-runtime/` (speaks MAVLink to ArduSub on BlueROV2 hardware). This RFC does **not** propose a new adapter — it proposes alignment between URML's existing marine-runtime and your Orca4 ROS 2 stack.

URML's adapter and Orca4 are complementary: URML emits substrate-neutral primitives, Orca4 provides the ROS 2 Humble dispatch surface on BlueROV2 (ArduSub + mavros + ORB_SLAM2). The ask is twofold:
1. Document the Orca4 ROS 2 surface as a supported dispatch path inside URML's marine-runtime, alongside the direct-MAVLink path that ships today.
2. Coordinate the URML manifest schema's marine entries with any conventions Orca4 / `ros-maritime` expects.

The `ros-maritime` working-group canonical contact surface is an open question — the RFC notes this honestly.

This is proposal-only, posted as part of URML's **Move #5** outreach (Tier B research-collab). No adapter code in this PR; the actual `reference/marine-runtime/README.md` documentation update follows in a later PR after community feedback.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0078-orca4-ros-maritime-outreach.md

## Feedback we'd value

1. **Canonical community contact.** Where is the `ros-maritime` working group's primary discussion surface, and is there a maintainer-of-record for outreach?
2. **Sensor naming / frame conventions.** Documented conventions URML manifests should align with?
3. **Orca4 ROS 2 distro plans.** Planning to support Jazzy and Rolling alongside Humble?
4. **README cross-reference willingness.** Open to a brief Orca4 README mention of URML's marine-runtime as a complementary primitive-layer?
5. **`awesome-maritime-robotics` inclusion path.** Appropriate venue for URML's marine-runtime?
6. **Conformance lane.** Open to a URML conformance line on `clydemcqueen/orca4` README?

Thanks for Orca4 and for the ROS 2 Humble + ORB_SLAM2 integration work. The community AUV stack is exactly the layer URML's marine-runtime should compose with.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0079: Open Bionics (academic + commercial courtesy)

Two-surface engagement; the academic post is substantive, the commercial post is courtesy.

### Academic OpenBionics Issue

**Post to:** https://github.com/OpenBionics/Prosthetic-Hands/issues/new (the org appears dormant — last commits 2018-2020; the Issue acknowledges that directly)
**Title:** `Research-collab proposal: URML accessibility identity + OpenBionics designs as reference geometries (dormancy acknowledged)`

**Body:**

```markdown
Hi OpenBionics maintainers,

Posting this acknowledging that the academic OpenBionics GitHub org appears dormant (last commits in `Prosthetic-Hands` 2018-02, `Robot-Hands` 2015, `Anthropomorphic-Robot-Hands` 2020). I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

URML is opening its accessibility identity. URML's first four outreach waves (Moves #1–#4, 64 RFCs) covered industrial, AI/ML, affordable-educational, and adjacent-niche verticals. Prosthetics has been deliberately uncovered. This RFC proposes documenting the OpenBionics academic Prosthetic-Hand and Robot-Hand designs as reference geometries for a future open-prosthetic research adapter, **not** as a partnership with the commercial Open Bionics Ltd (which is a distinct entity sharing the name).

This is proposal-only, posted as part of URML's **Move #5** outreach (Tier B research-collab). Light engagement payload — no new adapter ships; the documentation work happens only if the academic side signals interest.

Honest about scope: URML's adapter against a research-grade prosthetic-hand design has no regulatory standing for clinical deployment. URML's posture is education and research, not medical-device certification.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0079-open-bionics-outreach.md

## Feedback we'd value (if reachable given dormancy)

1. **Project status.** Active, in maintenance, or fully archived?
2. **Canonical files.** Which repos / files are the canonical reference for a research adapter?
3. **Citation form.** How should URML cite the project?
4. **Engagement willingness.** Interest in a documented URML cross-reference?

Thanks for the published Prosthetic-Hand and Robot-Hand designs. The open-hardware research foundation matters even when the project is in archive mode.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

### Commercial Open Bionics Ltd courtesy outreach (off-GitHub)

**Send to:** info@openbionics.com (or LinkedIn outreach to Open Bionics Ltd product team)
**Subject:** `URML accessibility identity overlap notice (courtesy outreach, no specific ask)`

**Body:**

```text
Hi Open Bionics Ltd team,

I'm Ido Yahalomi, the maintainer of URML (Universal Robot Language), an Apache 2.0 open specification for substrate-neutral robot intent at urml.dev. URML's outreach program has just opened a Move #5 wave (nine RFCs across robotics verticals) that includes accessibility as a documented identity for the first time.

I'm sending this as a courtesy notice rather than a formal proposal. URML does not have a Hero Arm adapter and would not propose one without your collaboration; the Hero Arm is a regulated medical device and URML's authority is open-spec, not clinical deployment. I wanted you to know URML's identity overlap exists.

The full RFC documenting URML's accessibility identity placement is on URML's repo:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0079-open-bionics-outreach.md

If a future conversation about URML's accessibility identity is of interest to your team — at any pace — my contact is in the RFC. No specific ask; this is institutional acknowledgement.

Thanks for the Hero Arm work and the visibility you've brought to open prosthetics globally.

— Ido Yahalomi (URML maintainer, greenvh@gmail.com, urml.dev)
```

---

## Workflow for posting

For each target (in any order, but recommended to start with DEEP Robotics for the wheeled-legged-class novelty, then the academic OpenBionics outreach because the dormancy may need re-routing, then the remaining seven):

1. Open the target's new-Issue / new-Discussion URL (above each section).
2. Paste the title.
3. Paste the body (the contents inside the ```markdown or ```text fence, NOT the fence markers themselves).
4. Apply the recommended label if the form requires one. If no obvious match, leave unlabelled and let the maintainers triage.
5. Submit.
6. Copy the resulting Issue / Discussion URL.
7. Update [`outreach-move5.yaml`](outreach-move5.yaml) for that slug.
8. Continue.

The commercial Open Bionics Ltd courtesy outreach is off-GitHub (email or LinkedIn); record any reply or non-reply in the `notes` field of the `open-bionics` row.

After all posts are sent, the ledger reflects the truth and `make audit` re-measures cleanly.
