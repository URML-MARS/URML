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

# Move #6 post bodies

Copy-paste-ready Issue / Discussion / email bodies for the Move #6 university-robotics-lab outreach. Twelve RFCs, all Tier B research-collab framing. Geographic spread: 6 US, 4 EU+UK, 2 Asia-Pacific.

Ledger state lives in [`outreach-move6.yaml`](outreach-move6.yaml). After posting, set `posted_url`, update `last_touch`, and update `next_action`.

Voice: founder posts under his GitHub identity. Each post opens with "Hi <lab>" and addresses the PI(s) directly. Academic-calendar cadence means polite follow-up at +30d is reasonable.

---

## RFC-0080: UC Berkeley AUTOLAB

**Post to:** https://github.com/BerkeleyAutomation/autolab_core/issues/new
**Title:** `Research-collab proposal: URML (substrate-neutral robot intent) for AUTOLAB`

**Body:**

```markdown
Hi AUTOLAB,

Posting this as a research-collaboration proposal to Prof. Ken Goldberg and the AUTOLAB team. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`, plus profile extensions for industrial / educational / research) sits one layer above ROS 2 / Isaac / MuJoCo / AUTOSAR Adaptive / OPC UA Robotics.

URML proposes alignment with AUTOLAB on three vectors: (a) URML primitive vocabulary as a teaching artifact in EECS 206A/B coursework; (b) a documented mapping from gqcnn grasp output to URML `grasp` primitive emission so policies trained against dex-net retarget across substrates; (c) cross-citation between URML's manifest schema and `autolab_core` utilities. No URML adapter against AUTOLAB-specific code in this RFC.

This is proposal-only, part of URML's **Move #6** outreach (US-friendly university robotics labs). Twelve labs in this wave, all research-collab framing.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0080-uc-berkeley-autolab-outreach.md

## Feedback we'd value

1. **Coursework integration.** Is EECS 206A/B (or successor) a candidate for a URML primitive-vocabulary lecture + lab?
2. **dex-net / gqcnn mapping.** Interest in a documented mapping from gqcnn grasp output to URML `grasp` primitive emission?
3. **autolab_core cross-link.** Open to a documented README note on URML as a complementary primitive-layer?
4. **Conformance lane on AUTOLAB docs?**
5. **Anything else.**

Thanks for AUTOLAB and the global research impact of dex-net + gqcnn. URML's substrate-neutral story benefits from the manipulation-research foundation AUTOLAB built.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0081: Caltech AMBER Lab

**Post to:** https://github.com/Caltech-AMBER/obelisk/issues/new
**Title:** `Research-collab proposal: URML formal-methods alignment with AMBER Lab + obelisk composition`

**Body:**

```markdown
Hi AMBER Lab,

Posting this as a research-collaboration proposal to Prof. Aaron Ames and the AMBER team. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

AMBER's nonlinear control + hybrid-systems + bipedal-locomotion + prosthetics research is the strongest formal-methods alignment URML has encountered across six outreach moves. URML's capability manifest schema can encode joint limits, contact constraints, hybrid-systems mode-switch boundaries — exactly the formal surfaces AMBER's papers reason over. URML's static-verification path ([RFC-0014 Draft](https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0014-substrate-conformance.md)) sits one layer above that.

`obelisk` is interesting: it's "a stable generic robot control interface" with explicit overlap to URML's substrate-Protocol abstraction. The two should compose, not compete. URML's RFC asks whether obelisk + URML composition is the right shape.

This is proposal-only, part of URML's **Move #6** outreach (US-friendly university robotics labs). No URML adapter against AMBER code in this RFC.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0081-caltech-amber-outreach.md

## Feedback we'd value

1. **obelisk + URML composition.** Is `obelisk` a substrate-Protocol target for URML, or is URML's primitive layer better composed above obelisk at a different level?
2. **Formal-methods integration.** Is there an AMBER publication whose controller would be a useful pilot for URML manifest encoding?
3. **Coursework integration.** Caltech Robotics Minor or ME 11 as candidate for URML primitive vocabulary?
4. **Prosthetics research-side complement.** URML's RFC-0079 opened accessibility as a documented identity (academic + commercial-courtesy). Interest in a documented bridge between AMBER's prosthetics work and URML's accessibility identity?
5. **Conformance lane on obelisk README or bipedalrobotics.com?**
6. **Anything else.**

Thanks for AMBER's open-source posture across `obelisk`, `ambersim`, and the broader Caltech-AMBER repos. The formal-methods alignment with URML is the strongest of any Move #6 lab.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0082: UPenn GRASP Lab

**Post to:** https://github.com/KumarRobotics/kr_autonomous_flight/issues/new (or KumarRobotics/MOCHA)
**Title:** `Research-collab proposal: URML substrate-neutral intent layer above GRASP swarm + heterogeneous fleet research`

**Body:**

```markdown
Hi GRASP,

Posting this as a research-collaboration proposal to Prof. Vijay Kumar and the GRASP Lab team. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

GRASP fills a niche URML's prior outreach has not covered: multi-agent + aerial-ground heterogeneous fleet coordination. URML's Move #1 covered ground industrial OEMs, Move #2 covered AI/ML, Moves #3-#5 covered hardware + Tier 2 promotions. None touched the swarm + heterogeneous-fleet research where GRASP is a global leader. URML proposes its substrate-neutral primitive vocabulary as the missing intent layer above MOCHA (multi-robot communication), SLIDE_SLAM (decentralized SLAM), and HALO (language-conditioned aerial exploration).

The unresolved URML question this RFC surfaces: **multi-agent coordination primitive**. URML's Layer-2 vocabulary has no explicit `coordinate(...)` primitive. GRASP's research is the strongest case yet for a future URML Spec RFC adding multi-agent coordination semantics.

This is proposal-only, part of URML's **Move #6** outreach. No URML adapter against GRASP code in this RFC.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0082-upenn-grasp-outreach.md

## Feedback we'd value

1. **MOCHA composition.** Is MOCHA an explicit composition target for URML primitive decomposition?
2. **HALO + URML language-conditioned exploration.** Interest in a documented mapping?
3. **Multi-agent primitive.** Is there a coordination primitive GRASP's research suggests URML should adopt at the spec level?
4. **Coursework integration.** CIS 3960X / MEAM 5100 as candidate course?
5. **Open-RMF coordination.** URML's open RFC-0053 thread (Open-RMF multi-robot framework) is research-grade adjacent.
6. **Conformance lane?**
7. **Anything else.**

Thanks for kr_autonomous_flight, MOCHA, SLIDE_SLAM, HALO — the GRASP open-source surface is the most concrete swarm-coordination research surface URML can point at.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0083: UW Personal Robotics Lab

**Post to:** https://github.com/personalrobotics/aikido/issues/new
**Title:** `Research-collab proposal: URML primitive vocabulary for ADA / HERB / aikido (composition, not adapter)`

**Body:**

```markdown
Hi UW Personal Robotics Lab,

Posting this as a research-collaboration proposal to Prof. Siddhartha Srinivasa and the PRL team. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

UW PRL is one of URML's most natural alignment targets: assistive robotics under clutter, learning from demonstration, HRI are exactly the domain where URML's English-to-primitive translation path lands hardest. The ADA assistive-feeding use case is the canonical example: a user instruction like "give me a bite of broccoli" decomposes into URML primitives (`measure(bowl_location)`, `move_to(broccoli_pose)`, `grasp(food_item)`, `move_to(user_mouth_pose)`, `release(food_item)`) that the substrate executes with `aikido`'s kinematics-and-dynamics underneath.

Name disambiguation worth flagging: URML's outreach addresses the UW Personal Robotics Lab (Srinivasa, Seattle) and Imperial College London's Personal Robotics Lab (Demiris, London) as two distinct labs. Same lab name, different country, different PI. URML's manifest namespacing keeps them disambiguated. URML's parallel RFC-0088 covers Imperial PRL.

This is proposal-only, part of URML's **Move #6** outreach. No URML adapter against UW PRL code in this RFC.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0083-uw-personal-robotics-outreach.md

## Feedback we'd value

1. **aikido + URML composition.** Is aikido the right composition target for URML's substrate-Protocol implementation, or at a different level (e.g., prpy)?
2. **ADA assistive-feeding pilot.** Interest in a documented mapping from URML primitives to ADA's task surface?
3. **Coursework integration.** CSE 490R as candidate course for URML primitive vocabulary?
4. **Name-collision disambiguation with Imperial PRL.** Maintainer concerns?
5. **Conformance lane on aikido README or PRL website?**
6. **Anything else.**

Thanks for aikido, ADA, HERB, and 15+ years of clutter-manipulation research. URML's English-to-primitive path benefits from the assistive-robotics foundation UW PRL has built.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0084: UMich Robotics

**Post to:** https://github.com/UMich-CURLY/drift/issues/new
**Title:** `Research-collab proposal: URML substrate-neutral intent for UMich Robotics + ROB 101 / 102 coursework integration`

**Body:**

```markdown
Hi UMich Robotics,

Posting this as a research-collaboration proposal to Prof. Maani Ghaffari + Prof. Jessy Grizzle and the UMich Robotics Department leadership. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

UMich Robotics is the most teaching-pipeline-ready URML target in Move #6. ROB 101 (Computational Linear Algebra for Robotics) and ROB 102 (Intro to AI and Programming for Robotics), launched 2023 as part of the new undergraduate robotics major, are robot-agnostic by design — exactly the audience URML's substrate-neutral primitive vocabulary serves.

CURLY (Computational Autonomy and Robotics Laboratory, Ghaffari) is the lab-level surface URML's `measure` primitive can compose with: `drift` (state estimation), `unified_cvo` (GPU point-cloud registration), `3DMapping`, `deep-contact-estimator` — all sit below URML's intent layer. Cassie / Digit bipedal-locomotion work (Grizzle) is a candidate URML manifest reference geometry.

This is proposal-only, part of URML's **Move #6** outreach. No URML adapter against UMich Robotics code in this RFC.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0084-umich-robotics-outreach.md

## Feedback we'd value

1. **ROB 101 / ROB 102 coursework integration.** Candidates for URML primitive vocabulary as teaching artifact?
2. **CURLY + URML composition.** Documented note that URML's `measure` consumes CURLY state-estimation outputs — useful?
3. **Bipedal-locomotion cross-link.** Cassie / Digit URDFs as URML manifest reference geometries?
4. **Isaac Lab coordination.** URML's open RFC-0050 (NVIDIA Isaac Lab) is adjacent; coordinate?
5. **Other UMich Robotics labs.** Who else (ROAHM, Bezzo, ...) is worth a separate URML outreach in a future Move #7?
6. **Conformance lane on CURLY README or robotics.umich.edu?**
7. **Anything else.**

Thanks for the ROB 101 / 102 / 401 robot-agnostic undergraduate curriculum, the CURLY state-estimation work, and the Cassie / Digit bipedal-research lineage. UMich Robotics is the most teaching-pipeline-aligned URML target in this Move.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0085: Northwestern CRB

**Post to:** https://github.com/MurpheyLab/MaxDiffRL/issues/new (or ergodic-control-sandbox)
**Title:** `Research-collab proposal: URML primitive vocabulary for Northwestern CRB + HAND ERC`

**Body:**

```markdown
Hi Northwestern CRB,

Posting this as a research-collaboration proposal to Prof. Todd Murphey, Prof. Ed Colgate, and Prof. Kevin Lynch. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

Northwestern CRB anchors dexterous manipulation across medical, soft, and industrial robotics at URML's Move #6 wave. The HAND Engineering Research Center ($52M / 10y NSF) is the largest-budget academic research surface URML has engaged. URML proposes alignment on three vectors:

(a) **ergodic-control + URML composition**: Murphey's ergodic exploration policies generate state coverage; URML's `measure` + `wait_for(threshold)` + LLM-bridge are the user-facing layer above ergodic-policy execution.
(b) **HAND ERC outreach mention** (where ERC communications team decides).
(c) **Lynch textbook (speculative)**: *Modern Robotics: Mechanics, Planning, and Control* is the global standard. A speculative ask: would a future edition or workshop consider a URML primitive-vocabulary appendix or worked example? URML expects this is below the base case but documents the ask.

License note: MurpheyLab is GPL-3.0 predominant; URML reference/ is Apache-2.0. The integration is documentation and cross-citation, not adapter code.

This is proposal-only, part of URML's **Move #6** outreach.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0085-northwestern-crb-outreach.md

## Feedback we'd value

1. **Ergodic-control + URML composition.** Useful direction?
2. **Coursework integration.** ME 495 as candidate for URML primitive vocabulary?
3. **HAND ERC outreach.** Interest in mentioning URML in HAND ERC developer outreach (ERC leadership decides)?
4. **License-fit.** GPL-3.0 on MurpheyLab vs Apache-2.0 on URML. Cross-citation arrangements?
5. **Lynch textbook (speculative).** Would *Modern Robotics* consider a URML appendix or worked example in a future edition?
6. **Conformance lane?**
7. **Anything else.**

Thanks for MurpheyLab's open-source posture across ergodic-control + max-diffusion-RL + brne + DPGO, the HAND ERC's scale, and Lynch's textbook lineage. URML's research-side outreach benefits from CRB's institutional depth.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0086: ETH Zurich ASL

**Post to:** https://github.com/ethz-asl/maplab/issues/new (or ethzasl_msf)
**Title:** `Research-collab proposal: URML substrate-neutral intent for ETH ASL (ground / aerial / aquatic)`

**Body:**

```markdown
Hi ETH ASL,

Posting this as a research-collaboration proposal to Prof. Roland Siegwart and the ASL team. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

ETH ASL has one of the largest academic-robotics GitHub footprints in the world: 458 public repos, 2.3k followers, with maplab (2.8k stars), ethzasl_msf (1091 stars), and wavemap (559 stars) as foundational dependencies for hundreds of academic and industrial robotics deployments. URML proposes composition: URML's `measure` primitive can dispatch to ASL state-estimation outputs (maplab, wavemap, ethzasl_msf), and URML's manifest sensor declarations align with `ethzasl_msf`'s sensor-state interface. The cross-substrate research (ground / aerial / aquatic) is exactly URML's substrate-neutral value proposition made concrete.

Disambiguation: ETH ASL (Siegwart) is distinct from ETH RSL (Marco Hutter, ANYmal upstream, covered indirectly by URML's RFC-0049). The two labs are separate; URML's outreach to ASL does not duplicate ANYmal work.

This is proposal-only, part of URML's **Move #6** outreach.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0086-eth-asl-outreach.md

## Feedback we'd value

1. **maplab / wavemap / ethzasl_msf composition.** Useful direction?
2. **Multi-sensor-fusion manifest alignment.** URML manifest declarations + ethzasl_msf sensor-state interface mapping?
3. **Coursework integration.** ETH master's robotics courses as candidates?
4. **ASL / RSL coordination.** Both ETH labs in URML's outreach landscape — any ETH-internal coordination URML should be aware of?
5. **Conformance lane on maplab README or asl.ethz.ch?**
6. **Anything else.**

Thanks for the maplab + wavemap + ethzasl_msf lineage. URML's substrate-neutral story across ground / aerial / aquatic depends on the kind of perception foundation ASL has built.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0087: TU Delft Cognitive Robotics

**Post to:** https://github.com/tud-cor/FS19_modROS/issues/new (or another tud-cor repo per maintainer preference)
**Title:** `Research-collab proposal: URML primitive vocabulary for TU Delft CoR + bio-inspired locomotion alignment`

**Body:**

```markdown
Hi TU Delft Cognitive Robotics,

Posting this as a research-collaboration proposal to Prof. Martijn Wisse and the CoR team. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

TU Delft CoR anchors bio-inspired locomotion + energy-efficient design + dexterous manipulation at URML's Move #6 wave. The Mobile Robotics + Robotics fundamentals courses are exactly the audience URML's primitive vocabulary serves. URML proposes alignment on three vectors: (a) coursework integration as a teaching artifact; (b) cross-link of Wisse's bipedal-walker research with URML's RFC-0009 legged-mobility schema; (c) a Spec-RFC question: should CoppeliaSim be a future URML substrate (TU Delft's coppeliasim_ros_control is the most-cited academic ROS / CoppeliaSim integration)?

This is proposal-only, part of URML's **Move #6** outreach.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0087-tu-delft-cognitive-robotics-outreach.md

## Feedback we'd value

1. **Canonical repos.** Which tud-cor repos are the first-class URML integration candidates today?
2. **Coursework integration.** Mobile Robotics or Robotics fundamentals as candidate course for URML primitive vocabulary?
3. **Bio-inspired locomotion cross-link.** Documented mapping from Wisse's bipedal-walker controllers to URML manifest entries?
4. **CoppeliaSim Spec RFC.** Is CoppeliaSim worth a future URML Spec RFC as a simulation target?
5. **Conformance lane?**
6. **Anything else.**

Thanks for the TU Delft Cognitive Robotics group's open-source posture and the established teaching pipeline. URML's bio-inspired locomotion alignment benefits from Wisse's research lineage.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0088: Imperial College London Personal Robotics Lab (off-GitHub)

**Send to:** y.demiris@imperial.ac.uk (via imperial.ac.uk/personal-robotics)
**Subject:** `URML (substrate-neutral robot intent) research-collaboration proposal — Move #6 university outreach`

**Body:**

```text
Hi Prof. Demiris,

I'm Ido Yahalomi, the maintainer of URML (Universal Robot Language), an Apache 2.0 open specification for substrate-neutral robot intent at urml.dev. URML's outreach program just opened Move #6 — twelve university robotics labs across the US, UK, EU, and Asia-Pacific. Imperial's Personal Robotics Lab is one of those twelve, and your research focus (human-centred robotics, learning from demonstration, assistive systems, HRI) is a near-direct semantic match for URML's English-to-primitive translation path.

The engagement is off-GitHub by design: URML's verification did not find a standalone public GitHub Issue surface for Imperial PRL. If you maintain a different surface (a private GitHub org, a lab mailing list, the Imperial robotics workshop circuit), I'd welcome a pointer.

A few things URML would value your input on:

1. Whether Imperial's Human-Centred Robotics course (4th year / master) is a candidate for URML primitive vocabulary as a teaching artifact.
2. Whether the lab maintains LLM-to-robot-action work that URML's reference/llm-bridge/ should cite or coordinate with.
3. Name-collision disambiguation with the UW Personal Robotics Lab (Sidd Srinivasa). URML's manifest namespacing keeps the two PRLs distinct, but a courtesy note is worth flagging.

The full RFC is on URML's repo:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0088-imperial-personal-robotics-outreach.md

No specific ask in this email; the RFC is the substantive document. If a future conversation about URML's accessibility / HRI identity is of interest to your team, my contact is in the RFC.

Thanks for the Human-Centred Robotics work and for the visibility you've brought to assistive robotics globally.

— Ido Yahalomi (URML maintainer, greenvh@gmail.com, urml.dev)
```

---

## RFC-0089: Oxford Robotics Institute

**Post to:** https://github.com/oxford-robotics-institute/radar-robotcar-dataset-sdk/issues/new
**Title:** `Research-collab proposal: URML primitive vocabulary + RobotCar Dataset annotation cross-link with RFC-0042 (Waymo)`

**Body:**

```markdown
Hi Oxford ORI,

Posting this as a research-collaboration proposal to Prof. Paul Newman and the Oxford Robotics Institute team. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

URML's Move #6 outreach includes Oxford ORI for two reasons: (a) the Radar RobotCar Dataset annotation cross-link — URML's existing RFC-0042 (Waymo Open Dataset) outreach proposed an annotation pattern for dataset trajectories; the same pattern likely applies to the Oxford Radar RobotCar Dataset. (b) Oxford ORI's autonomous-driving research is institutionally adjacent to URML's RFC-0020 (Autoware AV substrate) Draft.

Honest note on surface: URML's verification found only 2 public repos in `oxford-robotics-institute` (radar-robotcar-dataset-sdk, oord-dataset). If you maintain a different engagement surface — `ori-drs`, `ori-systems`, an internal mailing list, the ORI website's contact form — I'd welcome a pointer; URML's outreach pivots accordingly.

This is proposal-only, part of URML's **Move #6** outreach.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0089-oxford-ori-outreach.md

## Feedback we'd value

1. **Engagement surface.** Maintainer-preferred surface for substantive engagement?
2. **Radar RobotCar Dataset annotation.** URML's annotation pattern from RFC-0042 (Waymo) applicable here?
3. **Coursework integration.** Engineering Science robotics curriculum as candidate?
4. **Autonomous-driving cross-link.** URML's open RFC-0020 (Autoware) Draft coordination with ORI's research?
5. **`ori-drs` and `ori-systems` clarification.** Public GitHub orgs URML did not verify, or private surfaces?
6. **Conformance lane?**
7. **Anything else.**

Thanks for the Radar RobotCar Dataset, the autonomous-driving research at Oxford, and the ORI's long-running role in UK mobile robotics. URML's substrate-neutral story benefits from the perception-and-mapping foundation Oxford ORI has built.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0090: University of Tokyo JSK Robotics Lab

**Post to:** https://github.com/jsk-ros-pkg/jsk_recognition/issues/new (or jsk_visualization)
**Title:** `Research-collab proposal: URML substrate-neutral intent above JSK ROS packages + EusLisp composition`

**Body:**

```markdown
Hi JSK,

Posting this as a research-collaboration proposal to Prof. Masayuki Inaba, Prof. Kei Okada, and the JSK Robotics Lab team. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

JSK is **the** longest-running academic ROS contributor in Asia: `jsk_recognition`, `jsk_visualization`, `jsk_aerial_robot`, `jsk_robot` are foundational dependencies for hundreds of robotics deployments globally. URML proposes alignment on four vectors:

(a) **jsk_recognition + URML composition**: URML's `measure` primitive consumes JSK perception outputs at the intent layer.
(b) **EusLisp / roseus + URML composition**: JSK Lab famously uses Common Lisp at the planning layer; URML's primitive vocabulary at the intent layer composes with EusLisp's symbolic reasoning. A documented example is paper-worthy.
(c) **jsk_aerial_robot cross-link**: URML's aerial-substrate path (via RFC-0041 ArduPilot) can target jsk_aerial_robot-class platforms.
(d) **Coursework integration**: URML primitive vocabulary as a teaching artifact in UTokyo robotics practicum.

This is proposal-only, part of URML's **Move #6** outreach.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0090-utokyo-jsk-outreach.md

Note on language: URML's RFC body is English. Substantive technical discussion is welcome in Japanese or English — whichever the JSK team prefers.

## Feedback we'd value

1. **jsk_recognition + URML composition.** Useful direction?
2. **EusLisp + URML composition.** Documented example interest?
3. **jsk_aerial_robot cross-link.** Candidate URML substrate target via RFC-0041 (ArduPilot) bridge?
4. **Coursework integration.** JSK Lab practicum as candidate course?
5. **Language fluency.** Japanese or English for substantive discussion?
6. **Conformance lane on jsk_recognition README or jsk.t.u-tokyo.ac.jp?**
7. **Anything else.**

Thanks for 20+ years of foundational ROS package development. URML's substrate-neutral story across global academic ROS deployments depends on the kind of ecosystem JSK built.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0091: QUT Centre for Robotics (Peter Corke)

**Post to:** https://github.com/petercorke/robotics-toolbox-python/issues/new
**Title:** `Research-collab proposal: URML primitive vocabulary above Robotics Toolbox + QUT Centre for Robotics`

**Body:**

```markdown
Hi Prof. Corke,

Posting this as a research-collaboration proposal. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

`robotics-toolbox-python` is the global standard educational robotics teaching codebase. URML proposes a complementary surface: URML primitive vocabulary at the intent layer composed above the Toolbox's kinematics-and-dynamics math layer. Programs written against the Toolbox in a course or RVC3 example chapter can compile to URML primitives, then retarget to ROS 2 / Isaac / MuJoCo substrates without re-teaching the underlying math.

A speculative ask: would a future edition of *Robotics, Vision and Control* consider a URML primitive-vocabulary appendix or worked example? URML expects this is below the base case but documents the ask honestly. The more realistic asks are (a) a documented cross-citation in the Toolbox README, (b) URML primitive vocabulary as a module in QUT's AuSRoS 2025+ ROS 2 labs, (c) URML mention in ARC Centre of Excellence outreach materials (where Centre leadership decides).

This is proposal-only, part of URML's **Move #6** outreach (US-friendly university robotics labs). Twelfth and final RFC; closes the wave.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0091-qut-centre-for-robotics-outreach.md

## Feedback we'd value

1. **robotics-toolbox-python cross-link.** Documented cross-citation in URML's reference/cobot-runtime/ README welcome (vice versa, would the Toolbox mention URML)?
2. **RVC3 chapter (speculative).** Future edition or workshop URML primitive-vocabulary content?
3. **AuSRoS 2025+ teaching integration.** Candidate teaching module in QUT's annual ROS 2 labs?
4. **Centre for Robotics outreach materials.** URML mention in ARC Centre outreach (where Centre leadership decides)?
5. **Personal handle vs institutional org.** Is petercorke/* the right URML engagement surface, or a separate Centre-level GitHub?
6. **Conformance lane?**
7. **Anything else.**

Thanks for the Robotics Toolbox lineage (MATLAB → Python → ROS 2), RVC3, and the QUT Centre's institutional role in Australian robotics. URML's teaching-artifact story benefits enormously from the foundation the Toolbox built.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## Workflow for posting

For each target (in any order, but recommended to start with UMich Robotics — the most teaching-pipeline-ready of the wave per the plan — and then proceed through the rest):

1. Open the target's new-Issue URL or email surface (above each section).
2. Paste the title.
3. Paste the body (the contents inside the ```markdown or ```text fence).
4. Apply the recommended label if the form requires one.
5. Submit (or send email).
6. Copy the resulting URL (or note "sent" for email).
7. Update [`outreach-move6.yaml`](outreach-move6.yaml) for that slug.
8. Continue.

RFC-0088 (Imperial PRL) is off-GitHub email; the other eleven are GitHub Issues. Academic-calendar cadence means polite follow-up at +30d is reasonable rather than the +14d URML uses for vendor RFCs.

After all posts are sent, the ledger reflects the truth and `make audit` re-measures cleanly.
