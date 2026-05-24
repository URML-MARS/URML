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

# Move #3 post bodies

Copy-paste-ready Issue / Discussion bodies for the Move #3 outreach RFCs in [`docs/rfcs/`](../../docs/rfcs/). Each section is one target.

Ledger state lives in [`outreach-move3.yaml`](outreach-move3.yaml). After posting, set `sent_at` and `last_touch` to today's date, append the URL to `posted_url`, and update `next_action`.

Voice: founder posts under his GitHub identity. The RFC author field already reads `Ido Yahalomi (greenvh@gmail.com)`. Posts sign as the URML maintainer; do not impersonate URML as an organization.

---

## RFC-0061: WLKATA

**Post to:** https://github.com/wlkata/ROS2_WLKATA/issues/new (umbrella ROS 2 package set; the broadest surface across the WLKATA arm line)
**Optional cross-reference Discussion:** https://github.com/wlkata/WLKATA-Python-SDK-wlkatapython/discussions/new
**Label:** the closest `enhancement` or `feature` equivalent the form offers
**Title:** `Proposal: WlkataAdapter family for URML's substrate-neutral robot-intent language (cross-product, ROS 2 + serial)`

**Body:**

```markdown
Proposing a `WlkataAdapter` family that targets the four WLKATA ROS 2 packages (`Wlkata_Mirobot_Ros2`, `Wlkata_MT4_ROS2`, `Wlkata_Haro380_Ros2`, and the umbrella `ROS2_WLKATA`) plus the `wlkatapython` Python SDK over G-code-on-USB-serial for deployments without ROS. The adapter routes [URML](https://urml.dev) Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) and the industrial-profile extensions (`pick_from`, `place_at`, `swap_tool`) onto WLKATA's published surfaces without changes on your side.

URML is an Apache 2.0 specification for substrate-neutral robot intent. Its Layer-2 primitive vocabulary sits one layer above ROS 2 / PX4 / Isaac / MuJoCo / AUTOSAR Adaptive / OPC UA Robotics. A program written for a Mirobot retargets to an MT4 or Haro380 by switching the manifest, with static validation at every step.

This is proposal-only, posted as URML's first **Move #3** outreach (the affordable / desktop / educational tier between Move #1 industrial OEMs and Move #2 AI/ML projects). No adapter code in this PR. The per-product manifest split and the ROS 2-vs-serial transport selection are observable choices the published surface does not pin down, and your input shapes them before shipping.

Full RFC with proposed package layout, per-primitive mapping, manifest sketches, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0061-wlkata-outreach.md

## Feedback we'd value

1. **Adapter home.** URML repo (`reference/cobot-runtime/`), wlkata-org contributed example, both?
2. **Manifest granularity.** Per-product (Mirobot, MT4, Haro380), per-family, or parametric?
3. **Transport selection.** Single manifest with a `transport:` list (ROS 2 + serial), or two manifests per product?
4. **G-code reference.** Is `WLKATA-Python-SDK-wlkatapython` the canonical surface, or does the Haro380 expose additional commands the SDK does not yet wrap?
5. **BRAVE alignment.** Interest in a URML-aware BRAVE branch where policies train against URML-primitive emissions?
6. **Conformance lane.** Open to a URML conformance line on the product model cards?

Thanks for the open SDKs across the WLKATA line and for `ROS2_WLKATA`. The cross-product coverage made this RFC a lot more concrete than it otherwise would have been.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0062: Petoi (Bittle / Nybble)

**Post to:** https://github.com/PetoiCamp/OpenCat/issues/new/choose
**Label:** the closest `enhancement` or `feature` equivalent the form offers
**Title:** `Proposal: PetoiAdapter for URML's substrate-neutral robot-intent language (skill-library mapping on Bittle X / Bittle / Nybble Q)`

**Body:**

```markdown
Proposing a `PetoiAdapter` that wraps the OpenCat firmware on Bittle X, the original Bittle, and Nybble Q. The adapter speaks OpenCat's documented single-letter serial command protocol via `PetoiCamp/Petoi_MindPlusLib` (Python) and translates [URML](https://urml.dev) Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`, plus posture composition) onto OpenCat's SkillLibrary (`walk`, `trot`, `bound`, `sit`, `rest`, `stretch`, `push_up`, `balance`). No firmware changes on your side.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). On a Petoi, URML's distinctive contribution is the English-to-skill path with static validation: a one-sentence English instruction ("walk forward two steps and sit") compiles to a validated URML program that the OpenCat firmware executes via its existing skill library.

This is proposal-only, posted as part of URML's **Move #3** outreach (the affordable / desktop / educational tier). No adapter code in this PR. The `move_to`-to-gait selection rule and the skill-library mapping are design choices the OpenCat protocol does not pin down, and your input shapes them before shipping.

Why Petoi specifically: Bittle X at $299 is the smallest-scale, most-shareable legged-robot target in URML's outreach landscape. The hero demo URML wants is a Bittle X on a desk acting out an English sentence, and the open OpenCat firmware (4.8k stars, MIT) makes it possible.

Full RFC with proposed package layout, primitive-to-skill mapping, manifest sketches, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0062-petoi-bittle-outreach.md

## Feedback we'd value

1. **Skill-library mapping.** Implicit `move_to`-to-gait selection (direction and magnitude pick the gait token; duration scales playback), or an explicit `gait()` primitive at URML's Layer-3?
2. **Adapter home.** URML repo (`reference/petoi-runtime/`), `PetoiCamp` org as a contributed example, both?
3. **Manifest granularity.** One manifest per product (Bittle X, Bittle, Nybble Q), or a single parametric `petoi` manifest with a variant field?
4. **`ros_opencat` alignment.** Should URML's adapter delegate to `PetoiCamp/ros_opencat` where ROS is present, or speak OpenCat serial directly even in ROS deployments?
5. **Add-ons.** Bittle has add-ons (gripper, claw, sensors). Worth modelling now, or deferred?
6. **Conformance lane.** Open to a URML conformance line on `OpenCat`'s README or release notes?

Thanks for OpenCat, for the SkillLibrary, and for the open-hardware posture across Bittle and Nybble. The skill-library design is exactly the right shape for URML's audience at this tier.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0063: Hiwonder

**Post to:** https://github.com/Hiwonder/MentorPi/issues/new (the most-pinned Hiwonder platform repo)
**Optional cross-reference:** the maintainers' preferred surface if MentorPi is not the right home
**Label:** the closest `enhancement` or `feature` equivalent the form offers
**Title:** `Proposal: HiwonderAdapter family for URML's substrate-neutral robot-intent language (cross-platform: arm, quadruped, mobile, hexapod)`

**Body:**

```markdown
Proposing a `HiwonderAdapter` family that covers your published ROS 2 platforms under one URML adapter family: `MentorPi` (Mecanum / Ackermann / tank mobile base), `PuppyPi` (quadruped), `JetRover` (Jetson rover), `ROSPider` (hexapod), and the JetMax / DOFBOT educational arms. [URML](https://urml.dev) Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) plus the industrial-profile extensions (`pick_from`, `place_at`, `swap_tool`) map onto each platform's ROS 2 topics and services without changes on your side.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). The catalog-breadth angle is what makes Hiwonder distinctive for URML: a teacher who buys a PuppyPi for a robotics elective can later add a JetMax or a MentorPi and keep using the same URML primitives across the additions. URML's value-add is the substrate-neutral vocabulary and validation across the platforms you already ship.

This is proposal-only, posted as part of URML's **Move #3** outreach (the affordable / desktop / educational tier). No adapter code in this PR. The platform-priority question (which one to integrate first), the per-chassis manifest split on MentorPi (Mecanum vs Ackermann vs tank), and the alignment with your `Hiwonder/LeRobot` fork are observable choices worth your input before shipping.

Full RFC with proposed per-platform mapping, manifest sketches, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0063-hiwonder-outreach.md

## Feedback we'd value

1. **Platform priority.** Best first integration target from your perspective: MentorPi, PuppyPi, JetMax, JetRover, ROSPider, other?
2. **Adapter home.** URML repo (`reference/hiwonder-runtime/`), Hiwonder org as a contributed example, both?
3. **License confirmation.** Could you confirm the licenses on `MentorPi`, `PuppyPi`, `JetRover`, `ROSPider`, and `JetMax`?
4. **MentorPi chassis manifests.** Per-chassis (Mecanum / Ackermann / tank) or parametric?
5. **`Hiwonder/LeRobot` cross-link.** Interest in coordinating with our open RFC-0040 outreach to upstream LeRobot?
6. **Conformance lane.** Open to a URML conformance line on `docs.hiwonder.com` or in platform-repo READMEs?

Thanks for the breadth of the Hiwonder ROS 2 catalog and for the English-first documentation at `docs.hiwonder.com`. The cross-platform substrate-fungibility story is the most distinctive thing URML can offer at this tier, and it lands almost exclusively on you.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0064: Trossen Robotics Interbotix

**Post to:** https://github.com/Interbotix/interbotix_ros_manipulators/issues/new (the primary X-Series manipulator package)
**Optional cross-reference:** `Interbotix/interbotix_ros_core` or `Interbotix/interbotix_ros_toolboxes` if maintainers prefer to thread there
**Label:** the closest `enhancement` or `feature` equivalent the form offers
**Title:** `Proposal: InterbotixAdapter for URML's substrate-neutral robot-intent language (X-Series, ROS 2 + legacy ROS 1)`

**Body:**

```markdown
Proposing an `InterbotixAdapter` under URML's [`reference/cobot-runtime/`](https://github.com/URML-MARS/URML/tree/main/reference/cobot-runtime) targeting `interbotix_ros_manipulators` plus the sibling `interbotix_ros_core` and `interbotix_ros_toolboxes`. The adapter routes [URML](https://urml.dev) Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) and the industrial-profile extensions (`pick_from`, `place_at`, `swap_tool`) onto the X-Series joint-trajectory action goals and gripper services across ROS 2 Humble, ROS 2 Rolling, and (optionally) ROS 1 Noetic for the legacy lane.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). Interbotix sits where URML's educational, research, and US-federal-compliant lanes converge: the X-Series is de-facto research-arm hardware in US curricula (Stanford, CMU, MIT, Berkeley) and powers Mobile ALOHA's four-arm bimanual rig via four VX300S units. URML's value-add is the substrate-neutral vocabulary that lets a program written against an Interbotix arm retarget to a UR3, a Franka, or a WLKATA Haro380 without source changes, with static validation as the safety boundary.

This is proposal-only, posted as part of URML's **Move #3** outreach (the affordable / desktop / educational tier). No adapter code in this PR. The per-arm manifest split across the X-Series (PX100 / PX150 / RX150 / RX200 / WX200 / WX250 / WX250S / VX250 / VX300 / VX300S), the gripper-variant schema, and the ROS 1 Noetic legacy-lane coverage are observable choices worth your input before shipping.

This RFC also cross-links to two of URML's Move #2 outreach RFCs: RFC-0040 (Hugging Face LeRobot) covers the policy library distributed in part on Interbotix hardware, and RFC-0056 (Stanford ALOHA) covers the Mobile ALOHA recording pipeline that runs on Interbotix arms. The two cross-links are observed in the RFC; no joint action proposed.

Full RFC with proposed package layout, per-arm manifest sketches, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0064-trossen-interbotix-outreach.md

## Feedback we'd value

1. **Manifest granularity.** One manifest per X-Series arm, or a single parametric `interbotix_x_series` manifest with a `model:` field?
2. **ROS 1 Noetic legacy lane.** Should URML's adapter cover ROS 1 Noetic, or target ROS 2 only?
3. **Gripper-variant surface.** Is the `gripper:` field's single-value design sufficient, or do you recommend a richer schema for finger-position vs. custom end-effectors?
4. **Adapter home.** URML repo (`reference/cobot-runtime/`), Interbotix org as a contributed example, both?
5. **Bimanual coordination.** Mobile ALOHA coordinates four VX300S arms via ALOHA's recording stack. Path for a `coordinate(arm0, arm1, ...)` Layer-2 primitive at the ROS 2 layer, or stays at the recording / policy layer?
6. **Conformance lane.** Open to a URML conformance line on the package README or in the X-Series documentation?

Thanks for the Interbotix ROS 2 packages and for the cross-ROS-version build matrix. The US-domiciled provenance plus the academic-curriculum reach is exactly what URML's open-standard story needs at the research tier of Move #3.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## Workflow for posting

For each target (in any order, but recommended to start with `PetoiCamp/OpenCat` for the most public-facing, hero-demo-aligned thread):

1. Open the target's new-Issue URL (above each section).
2. Paste the title.
3. Paste the body (the contents inside the ```markdown fence, NOT the fence markers themselves).
4. Apply the recommended label if the form requires one. If no obvious match, leave unlabelled and let the maintainers triage.
5. Submit.
6. Copy the resulting Issue URL.
7. Update [`outreach-move3.yaml`](outreach-move3.yaml) for that slug:
   - Set `posted_url` to the URL.
   - Set `sent_at` to today (if not already 2026-05-24).
   - Set `last_touch` to today.
   - Append a verified-surface dated note to `notes`.
   - Update `next_action` to the chosen wait window (Move #1 and Move #2 used "wait 14 d").
8. Continue.

After all posts are sent, the ledger reflects the truth and `make audit` re-measures cleanly.
