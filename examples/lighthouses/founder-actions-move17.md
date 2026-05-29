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

# Move #17 founder-action artifacts: Sub-wave B (13 targets)

13 Move-17 targets that need to be sent through non-GitHub channels: email, membership forms, formal consultation portals, working-group sign-ups. Drafts below. Refine the voice as fits before sending; everything goes out under the maintainer identity (Ido Yahalomi, URML maintainer, urml.dev, greenvh@gmail.com).

10 targets reference a public URML RFC on `main` (RFCs 0217-0226). 3 are membership-only and don't need an RFC; the URML repo is the citation.

Sub-wave A (5 GitHub-Issue targets: Eclipse SDV, ELISA, OPC, SLSA, Scorecard) is in [`posts-move17.md`](posts-move17.md). Sub-wave C (4 federal-docket-watch) and 15 Tier B candidates are deferred in [`outreach-move17.yaml`](outreach-move17.yaml). Research audit in [`move17-research-2026-05-29.md`](move17-research-2026-05-29.md).

**Confidentiality.** Drafts don't name previously engaged URML maintainers. URML's own repo and RFCs are fine to cite. Aggregate counts ("seventeen outreach waves to date") are fine.

**Authoring disclosure.** Each email-shaped artifact ends with the same one-line note:

```
*AI-assisted prose, maintainer-reviewed before sending (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

For application-form fills (IIA, ASTM, euRobotics, ADRA), the disclosure goes in the cover letter or project-description field, not in structured-data fields.

---

## Sub-wave B with RFCs (10)

---

### RFC-0217: OSRA membership inquiry

**Send to:** Open Source Robotics Alliance contact form on [osralliance.org](https://osralliance.org/). If the form is not the right channel, the OSRF executive contact at openrobotics.org is the alternative.

**Channel:** Alliance contact form, follow-up email if needed.

**Subject:** URML (substrate-neutral robot intent language): orientation inquiry for OSRA

**Body:**

Hi OSRA team,

I'm Ido Yahalomi, maintainer of URML (urml.dev). URML is a small, substrate-neutral language for describing robot intent. The Apache-2.0 spec, the ROS 2 reference runtime, the validator, the conformance suite, and the LLM bridge are all open under URML's Core Commitment, which is documented in the repo and not going to move.

URML's plan over time is a structural separation: a non-profit foundation owns the standard, and any commercial surround stays outside the repo. OSRA is the closest existing robotics-native option for that foundation, so I'm writing as orientation, not as a formal candidacy. Background: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0217-osra-foundation-home-outreach.md

A few things I want to ask:

1. Does OSRA's charter have room for a sponsored-project candidacy where the project is substrate-neutral (URML composes onto ROS 2 first, but also PX4, OPC UA Robotics, and other substrates), or is OSRA explicitly ROS-aligned at the charter level?
2. What does the typical project-maturity threshold look like before a candidacy makes sense (community size, adoption signals, time since v1.0, US-domiciled co-sponsor)?
3. What membership tier is realistic as a first engagement for a single-maintainer Phase-1 project, with fees and obligations?
4. URML's trademark is in my name and assignable. How does OSRA handle trademark and IP assignment for sponsored projects?

I'm also engaging the Joint Development Foundation (JDF) at the same orientation level, because they're the neutral / multi-domain version of the same conversation. I don't want to be cute about it: I want to understand both before committing to either.

Thanks. ROS, Gazebo, and Open-RMF are part of why URML can exist at all.

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

*AI-assisted prose, maintainer-reviewed before sending (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0218: JDF formation inquiry

**Send to:** Joint Development Foundation. `jdfsupport@linuxfoundation.org` is the contact on jointdevelopment.org. Confirm at send time. Linux Foundation member services is the alternative.

**Channel:** Email.

**Subject:** URML (substrate-neutral robot intent language): orientation inquiry for JDF Projects affiliate path

**Body:**

Hi JDF team,

I'm Ido Yahalomi, maintainer of URML (urml.dev). URML is a substrate-neutral language for describing robot intent. The repo's shape is set up the way JDF Projects affiliates look before they form: Apache-2.0 spec under URML's Core Commitment, DCO sign-off on contributions instead of a CLA, trademark in my name and assignable.

URML's roadmap includes a structural separation: a non-profit foundation owns the standard, and the commercial surround stays separate. JDF is the cleanest neutral path I can find. The recent OpenUSD work and OpenChain's ISO/IEC submission via JDF are basically the arc URML eventually wants to walk. Background: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0218-jdf-foundation-home-outreach.md

Questions:

1. What does the project-formation threshold look like for a JDF Projects affiliate (community size, governance maturity, time since v1.0, US-domiciled co-sponsor expectation)?
2. Are there JDF charter templates an affiliate adopts with a project-specific overlay, or does each affiliate write its own from scratch?
3. What's the typical timeline and project-maturity threshold for a JDF affiliate to submit a standard downstream into ISO/IEC JTC 1 PAS?
4. IP and trademark assignment expectations for affiliates?
5. I'm Israel-domiciled. URML's user base is multi-national. Are there domicile constraints on affiliate maintainers, or is it project-org-level?

I'm engaging OSRA at the same orientation level. They're the robotics-native option; you're the neutral standards-track option. I want to understand both shapes before committing.

Thanks for the work that makes this path real and not a wish.

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

*AI-assisted prose, maintainer-reviewed before sending (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0219: IEEE P1872.2 WG sign-up and RAS-SCSA email

**Send to:** Two steps.

1. IEEE-SA Working Group sign-up at [sagroups.ieee.org/1872-2](https://sagroups.ieee.org/1872-2/). Affiliation: "URML (urml.dev), open-source robotics-intent language." Interest: ontology and structured-intent vocabulary. Country: Israel.
2. Once the sign-up confirms, follow up with the IEEE-RAS Standing Committee for Standards (sagroups.ieee.org/ras-sc).

**Follow-up email to IEEE-RAS Standing Committee:**

**Subject:** URML: maintainer joining P1872.2, possible AuR ontology cross-citation

Hi IEEE-RAS Standing Committee for Standards,

I've signed up for the P1872.2 Autonomous Robotics Ontology Working Group at sagroups.ieee.org/1872-2. I'm Ido Yahalomi, maintainer of URML (urml.dev), a substrate-neutral robotics-intent language. URML's Layer-2 primitives (`move_to`, `pick_from`, `place_at`, `grasp`, `release`, `swap_tool`, `scan_area`, `query_detection`) and Layer-3 behavior composition map onto IEEE 1872-2015 Core Ontology terms and the P1872.2 AuR extension naturally. I want to monitor the WG and contribute observations where cross-mapping is useful. Background: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0219-ieee-1872-2-wg-outreach.md

Questions:

1. What's the preferred format for URML primitive to IEEE 1872 / P1872.2 vocabulary mapping (inline citation in URML spec docs, separate cross-reference table, both)?
2. Are non-member observers welcome at P1872.2 WG calls?
3. Is there interest in jointly scoping a URML-to-IEEE-1872 mapping table as collaborative WG work, or should I draft a proposal independently and submit it for WG review?
4. URML's multi-robot direction (RFC-0006) is future work. Would the same observer status extend to the P1872.3 sister WG when that work moves forward?

Thanks for the ontology work. IEEE 1872 is exactly the kind of standards-side recognized vocabulary URML benefits from citing rather than reinventing.

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

*AI-assisted prose, maintainer-reviewed before sending (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0220: NIST EL Intelligent Systems Division feedback memo

**Send to:** `craig.schlenoff@nist.gov` (NIST EL Intelligent Systems Division program manager). CC: `RobotTestMethods@nist.gov`.

**Channel:** Single email with the memo attached.

**Subject:** URML: substrate-neutral robotics-intent language, measurement-science feedback for NIST EL ISD

**Cover email:**

Dr. Schlenoff,

I'm using the NIST EL ISD Robotics Community Feedback channel. Attached is a short memo (about 1.5 pages) on URML (urml.dev). URML is a substrate-neutral robotics-intent language with a manifest-validated dispatch model and a static validator. The memo maps URML's primitive set and capability-manifest model onto NIST EL ISD's published performance categories (agility, manipulation, mobility, perception) and asks three concrete questions about possible alignment, MORT composability, and ARIAC scenario expression in URML language.

Background RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0220-nist-el-isd-feedback-outreach.md

Best,
Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

*AI-assisted prose, maintainer-reviewed before sending (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

**Attached memo:**

**URML: Measurement-Science Feedback for NIST EL Intelligent Systems Division**

*Ido Yahalomi, URML maintainer · 2026-05-29*

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent. It sits above existing robot operating systems and compiles down to whatever runtime lives below. The v0.1.0 release shipped on 2026-05-22 with:

- A spec in four layers: a Hardware Abstraction capability manifest (Layer 1), typed intent primitives (Layer 2), behavior composition (Layer 3), and a multilingual natural-language grammar (Layer 4).
- A ROS 2 reference runtime.
- A static validator (`urml validate --policy`).
- A conformance test suite that any URML-compatible runtime must pass.
- A US-federal-aligned default policy file (NDAA Section 889, EO 14307, FCC Covered List) for procurement-gated deployments.
- An LLM bridge with prompt contracts that let language models reliably emit valid URML, with the validator as the integrity boundary.

**Measurement-science fit.** URML's manifest, validator, and conformance suite map onto NIST EL ISD's published performance categories:

| URML surface | NIST EL ISD performance category |
|---|---|
| `move_to`, `dock`, `scan_area` primitives plus the manifest mobility class | Mobility, agility |
| `pick_from`, `place_at`, `grasp`, `release`, `swap_tool` plus manipulator declaration | Manipulation, agility |
| Sensor manifest (lidar, camera, radar, sonar) plus perception primitives | Perception |
| `safety_envelope` manifest field plus validator gate | Safety |

Two concrete intersection opportunities:

1. **MORT composability.** URML's `reference/ros2-runtime/` could be exercised against NIST's Modular Open-Source Robotics Testbed. The measurement-science question worth testing is whether URML's static manifest validation correlates with measured runtime agility and safety scores. URML alone can't test that; MORT is purpose-built to.

2. **ARIAC scenario expression.** URML's industrial profile (RFC-0013) defines `pick_from`, `place_at`, and `swap_tool` against an industrial-arm manifest. A handful of ARIAC scenarios are expressible verbatim in URML language. Doing so would give URML a published-scenario corpus for conformance work, and would give the ARIAC community a candidate human-readable scenario notation as related art.

**Structural separation.** The URML spec, conformance suite, validator, ROS 2 and PX4 reference runtimes, LLM bridge prompt contract, and US-federal default policy file are Apache-2.0 forever per URML's Core Commitment. Over time the standard belongs in a non-profit foundation, separate from any commercial surround. The realistic target is US-domiciled and US-aligned (a 501(c)(6) industry association, an SDO with strong US ties, or a sponsored project under an existing US-domiciled foundation). I'm currently in orientation conversations with OSRA and JDF on that. Warming a NIST EL ISD relationship in parallel is a natural part of that arc.

**Asks:**

1. Does URML's manifest, validator, and conformance-suite framing map usefully onto NIST EL ISD's performance categories, or does the framing need adjustment to be useful at the measurement-science layer?
2. Is there a NIST EL ISD path for an external project to compose reference runtimes against MORT and contribute measurement scenarios?
3. Would expressing ARIAC scenarios in URML as related art be of interest, or is that out of scope for the competition format?

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

---

### RFC-0221: ASTM F45.04 position paper

**Send to:** Two steps.

1. ASTM individual membership at [astm.org/membership-participation/membership-options](https://www.astm.org/membership-participation/membership-options). There's an annual fee. Confirm current fee at sign-up time.
2. F45.04 subcommittee chair contact, obtained after F45 membership confirms. Submit the position paper as an F45.04 working-document contribution.

**ASTM membership-application supporting statement (form field):**

I maintain URML (urml.dev), an Apache-2.0 substrate-neutral robotics-intent language. URML ships a ROS 2 reference runtime, a conformance suite, a validator, and a US-federal-aligned default policy file. URML's interoperability scope (declaring what a robot can do at the manifest layer and what the operator wants done at the intent layer, in a way that's portable across substrates) aligns directly with F45.04's System Communication and Interoperability mandate. I'm joining F45.04 to participate in the subcommittee and offer URML's manifest and primitive schema as a candidate interoperability layer for committee review.

**Position paper to F45.04:**

**URML: A Candidate Interoperability Layer for ASTM F45.04**

*Position paper to ASTM Committee F45, Subcommittee F45.04 (System Communication and Interoperability)*

*Ido Yahalomi, URML maintainer · 2026-05-29*

**Abstract.** URML (Universal Robot Language, urml.dev) is a substrate-neutral, declarative, human-readable language for robot intent. URML's Layer-1 Hardware Abstraction capability manifest declares what a robot can do. Its Layer-2 intent primitives declare what the operator wants done. A static validator (`urml validate --policy`) enforces a static check between the two before execution. This position paper proposes URML's manifest and primitive schema as a candidate interoperability layer for F45.04 consideration, between substrate-side hardware abstractions (the OEM's SDK, ROS 2 messages, OPC UA Robotics NodeSet) and operator-side intent declaration (mission planners, NL interfaces, supervisory controllers). The paper outlines the interoperability problem URML targets, the schema URML proposes, mapping notes to adjacent F45 subcommittees, and three asks for F45.04 subcommittee orientation.

**1. The interoperability problem.** Production robotics deployments compose multiple runtime substrates at once: ROS 2 for mobile-base coordination, PX4 for drone autopilots, MoveIt 2 for manipulation planning, DDS or Zenoh for transport, OPC UA Robotics for industrial-cell integration. Each substrate has its own capability declaration form, or none. An interoperability standard at the manifest and intent layer, declaring once what the robot can do and what the operator wants, in a substrate-neutral notation, is the natural interoperability target above the OEM SDK boundary and below the operator interface.

**2. URML's interoperability proposal.** URML is layered:

- **Layer 1 (Hardware Abstraction, capability manifest):** a YAML schema declaring the robot's mobility class (mobile-base, drone, fixed-arm, legged), manipulator topology, sensor set, safety envelope, substrate class (ros2, px4, opc_ua_robotics), and policy posture.
- **Layer 2 (Intent Primitives):** a small set of verbs with typed arguments and static preconditions. `move_to`, `dock`, `scan_area`, `pick_from`, `place_at`, `grasp`, `release`, `swap_tool`, `query_detection`.
- **Layer 3 (Behavior Composition):** sequences, branches, recoveries, timing modifiers.
- **Layer 4 (Natural Language Interface):** a formal grammar that compiles an English sentence (with additional grammars shipping for Spanish, Japanese, and Mandarin in v0.1) to a validated Layer-2 program.

The interoperability boundary URML proposes for F45.04 standardization is at Layer 1 to Layer 2. The manifest declares the capability surface in a substrate-neutral form. The intent program references only primitives that the manifest declares the robot supports. The validator enforces this statically before dispatch.

URML is Apache-2.0 forever per its Core Commitment: the spec, conformance suite, validator, ROS 2 and PX4 reference runtimes, LLM bridge prompt contract, and US-federal-aligned default policy file remain open-source under that license. Bringing URML's schema into ASTM F45.04 would let the committee standardize the manifest and primitive boundary as a recognized interoperability layer, with URML's existing schema as a candidate starting point the committee can adopt, modify, or reject on its merits.

**3. Mapping to adjacent F45 subcommittees.**

- **F45.02 (A-UGV Docking and Navigation):** URML's `move_to`, `dock`, `scan_area` primitives plus the manifest mobility-class declaration align with F45.02's navigation performance work. URML's manifest could declare F45.02-conformant navigation as a substrate capability.
- **F45.05 (Grasping and Manipulation):** URML's `pick_from`, `place_at`, `grasp`, `release`, `swap_tool` primitives align with F45.05's manipulation performance work. URML's industrial profile (RFC-0013) ships these primitives for industrial-arm deployments.
- **F45.06 (Legged Robot Systems):** URML's manifest mobility-class declaration includes `legged` as a value. The legged-specific primitive set is future work where F45.06 review would help.

Natural cross-reference shape: F45.04 standardizes the manifest and intent boundary. F45.02, F45.05, and F45.06 standardize the substrate capability classes that the manifest declares. URML's schema is candidate raw material for F45.04 specifically.

**4. Composability with existing standards.** URML composes against ROS 2 (the primary reference runtime, OSRA/OSRF governance), PX4/MAVLink/MAVSDK (drone substrate, Linux Foundation Dronecode governance), OPC UA Robotics Companion Specification (industrial-cell substrate, OPC Foundation governance), MoveIt 2 (manipulation dispatcher, MoveIt Working Group), Nav2 (navigation dispatcher, ROS 2 Navigation Working Group), and Fast DDS / Cyclone DDS (transport, eProsima + Eclipse Foundation governance). URML's outreach to each is documented in [`docs/rfcs/`](https://github.com/URML-MARS/URML/tree/main/docs/rfcs). The substrate-spine wave (RFCs 0196-0211) engaged the substrate maintainers explicitly to make URML's substrate-neutrality concrete and not rhetorical.

**5. Asks for F45.04.**

1. Does URML's substrate-neutral manifest and Layer-1-to-Layer-2 boundary match F45.04's interoperability mandate, or is the scope different in ways URML should adjust framing to address?
2. What's the typical channel for an individual ASTM member to contribute a position paper and propose collaborative document development at F45.04?
3. Is F45.04 interested in scoping a URML-position-paper-driven standards-track document, or does the subcommittee prefer URML contribute to existing F45.04 documents?
4. What's the typical ASTM-to-ANSI-to-ISO PAS pickup path for F45 standards? URML's planned structural-separation arc would benefit from downstream pickup orientation.

**Background.** Full URML RFC for this submission: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0221-astm-f45-04-outreach.md. URML repo: https://github.com/URML-MARS/URML. The sibling outreach to NIST EL Intelligent Systems Division (RFC-0220) is in flight. The NIST EL ISD plus ASTM F45 engagement pair is the strategic shape: NIST informs the measurement science, ASTM F45 standardizes the outputs.

*AI-assisted prose, maintainer-reviewed before submission (see VIBE.md in the URML repo). Human-only correspondence available on request.*

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

---

### RFC-0222: CEN-CENELEC JTC 21 public-enquiry submission

**Send to:** CEN-CENELEC public-enquiry portal when the next URML-relevant prEN window opens. Parallel routing via SII (Standards Institution of Israel) for the future TC seat is Phase 2.

**Channel:** cencenelec.eu public-enquiry comment form. Window-dependent.

**Submission shell. Sections 3 and 4 fill at send time based on the specific prEN draft under enquiry.**

**URML: Public-Enquiry Comment on [prEN reference, target window]**

*Submitted by Ido Yahalomi, URML maintainer*

*Affiliation: URML (urml.dev), an open-source robotics-intent-language project. Israel-domiciled maintainer. This submission is a related-art reference, not a compliance claim.*

**1. Introduction.** URML (urml.dev) is a substrate-neutral, declarative, human-readable language for robot intent. The language ships an Apache-2.0 spec, a ROS 2 reference runtime, a conformance test suite, and a static validator (`urml validate --policy`). This comment offers URML as a related-art reference for [the prEN draft under enquiry], specifically for the AI-on-systems framing where structured intent and validator-gated execution intersect with the draft's scope.

**2. Structured intent and validator-gated execution.** URML's design separates three concerns. *Capability declaration* (Layer 1) is a YAML manifest declaring what a robot can do: mobility class, sensors, manipulators, safety envelope, substrate class. *Intent declaration* (Layer 2) is a small set of typed primitives (`move_to`, `pick_from`, `scan_area`, others) declaring what the operator wants done. *Static validation* checks every intent program against its target's capability manifest plus the active safety envelope before dispatch. Programs that don't validate don't execute.

For AI-on-systems scope: URML's Layer-4 natural-language interface lets a sentence in English (or Spanish, Japanese, Mandarin) compile to Layer-2 programs. The output goes through the same Layer-1 validator gate as any other Layer-2 program. The LLM is constrained by the structured grammar and the manifest is the contract.

**3. Why this is related art for the prEN draft.** [Fill at submission time with specific clause references based on the prEN content.] URML's pattern is one concrete instance of structured intent plus static verification applied to AI-on-systems. URML doesn't claim to be a safety standard or an AI Act compliance product. It claims to be a real-world example of a design pattern that the draft may want to reference, accommodate, or otherwise consider.

**4. Concrete observations and suggestions.** [Fill at submission time. Likely areas: the structured-intent boundary, the validator-vs-runtime-check distinction, capability-declaration semantics, multi-language NL grammar concerns.]

**5. Asks.**

1. Is URML's structured-intent and validator-gated-execution framing acceptable as related-art reference in JTC 21 public enquiries, or does the committee expect submissions to be standard-conformance claims?
2. For the next URML-relevant public-enquiry calendar (2026 robotics-AI prEN drafts), is the cencenelec.eu portal the canonical submission channel, or are there national-mirror routing recommendations?
3. URML's maintainer is Israel-domiciled. SII national-mirror routing is the natural Phase 2 path for an active TC seat. What's the orientation for non-EU non-mirror submitters on the public-enquiry side?

Full URML RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0222-cen-cenelec-jtc-21-outreach.md. URML repo: https://github.com/URML-MARS/URML.

*AI-assisted prose, maintainer-reviewed before submission (see VIBE.md in the URML repo). Human-only correspondence available on request.*

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

**Note for the founder:** Window-dependent. The draft above is reusable as a shell. Sections 3 and 4 need filling at submission time based on the specific prEN draft under enquiry. Monitor cencenelec.eu and jtc21.eu for the next URML-relevant window (likely a 2026 robotics-AI prEN).

---

### RFC-0223: DIN/DKE German AI Standardization Roadmap contribution

**Send to:** DIN/DKE roadmap participation channel at [din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap](https://www.din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap). Verify exact contribution-submission email or portal at send time.

**Channel:** Roadmap participation portal plus DIN/DKE contact email.

**Subject:** URML: robotics-intent language contribution to DIN/DKE German AI Standardization Roadmap

**Body:**

Dear DIN/DKE AI Standardization Roadmap coordinators,

I'm writing under the roadmap's civil-society invitation. I'm Ido Yahalomi, maintainer of URML (urml.dev), an Apache-2.0 substrate-neutral robotics-intent language with a ROS 2 reference runtime, a validator, a conformance suite, and a US-federal-aligned default policy file. I want to offer URML's structured-AI-intent pattern as a concrete instance of the roadmap's structured-AI catalogue, for the German national position into CEN-CENELEC JTC 21 and ISO/IEC JTC 1/SC 42.

**URML's structured-AI-intent pattern.** URML separates capability declaration (Layer 1 manifest), intent declaration (Layer 2 primitives), and natural-language translation (Layer 4) so that AI-derived intent passes through the same Layer-1 capability-manifest validator as any other intent program. The LLM is constrained by structured grammar and the manifest is the contract. Programs that don't validate against the manifest and safety envelope don't execute. This is one concrete pattern for safe AI-on-systems integration the German roadmap may benefit from referencing as related art.

**URML is multilingual.** The Layer-4 natural-language interface ships English, Spanish, Japanese, and Mandarin grammars in v0.1. A German grammar is future work but architecturally aligned. The German roadmap's multilingual orientation is a structural fit.

**URML's standards-track posture.** Concurrent engagements: sibling AFNOR Grand Défi AI consultation (FR national position into JTC 21), CEN-CENELEC JTC 21 directly (window-dependent), BSI AI Standards Hub (UK side, international remit), OECD AI Policy Observatory (international norms), NIST EL Intelligent Systems Division and ASTM F45.04 (US side). The cross-national footprint is intentional: URML's structural-separation roadmap targets a foundation home with broad standards-body recognition.

**Asks:**

1. Is URML's structured-AI-intent pattern an acceptable fit for the AI Standardization Roadmap catalogue, or does the catalogue expect German-domiciled contributors?
2. Beyond the roadmap, what's the channel for an external project to feed into the DE national-position file for JTC 21 and ISO/IEC JTC 1/SC 42?
3. Is the Indo-German bilateral surface a relevant channel, or is roadmap-direct the right entry?
4. What's the path for an external project to participate in DIN robotics-related committees? Orientation only; URML at Phase 1 is roadmap-contribution-only.

Full URML RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0223-din-dke-ai-roadmap-outreach.md. URML repo: https://github.com/URML-MARS/URML.

Thank you for the roadmap and the civil-society invitation.

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

*AI-assisted prose, maintainer-reviewed before sending (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0224: AFNOR Grand Défi AI consultation submission

**Send to:** AFNOR Grand Défi AI consultation platform at [afnor.org/en/news/shaping-european-ai-leadership/](https://www.afnor.org/en/news/shaping-european-ai-leadership/). Find the exact consultation submission form at send time.

**Channel:** AFNOR consultation-platform submission.

**Submission (mirrors the DIN/DKE structure with FR-specific framing):**

**URML: Robotics-Intent Language Contribution to AFNOR Grand Défi AI**

*Submitted by Ido Yahalomi, URML maintainer · urml.dev · greenvh@gmail.com*

I'm using the Grand Défi AI consultation platform's international-participation invitation. URML (urml.dev) is an Apache-2.0 substrate-neutral robotics-intent language with a ROS 2 reference runtime, a validator, a conformance suite, and a US-federal-aligned default policy file. I'm offering URML's structured-AI-intent pattern for the French national position into CEN-CENELEC JTC 21.

**Structured-AI-intent pattern.** URML's Layer-1 capability manifest declares what the robot can do. Layer-2 typed primitives declare what should be done. A static validator (`urml validate --policy`) gates execution against both plus the active safety envelope. URML's Layer-4 natural-language interface compiles human-language input to Layer-2 programs that go through the same Layer-1 validator. The LLM is constrained by the structured grammar; the manifest is the contract.

**Cross-national positioning.** Concurrent submissions to DIN/DKE (DE) and direct engagements with JTC 21, BSI AI Standards Hub (UK), OECD AI Policy Observatory, NIST EL, and ASTM F45.04 (US). The Grand Défi AI consultation is the natural FR-side channel for the same contribution shape DIN/DKE receives from the DE side.

**Multilingual orientation.** URML's natural-language layer ships five grammars in v0.1. A French grammar is architecturally aligned future work. Grand Défi AI's openness to international participants is a structural fit.

**Asks:**

1. Is URML's structured-AI-intent pattern an acceptable Grand Défi AI consultation contribution, or does the platform prefer French-domiciled contributors?
2. Beyond Grand Défi AI consultation, what's the channel for an external project to feed into the FR national position for JTC 21?
3. What's the path for an external project to participate in AFNOR robotics-AI committees? Phase 2 orientation question.

Full URML RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0224-afnor-grand-defi-ai-outreach.md. URML repo: https://github.com/URML-MARS/URML.

Thank you for the consultation work.

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

*AI-assisted prose, maintainer-reviewed before sending (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0225: BSI AI Standards Hub engagement

**Send to:** BSI AI Standards Hub at [aistandardshub.org](https://aistandardshub.org/). Hub maintainer registration plus engagement-note submission.

**Channel:** Hub registration portal plus engagement-note via Hub contact.

**Hub registration form fields:** Affiliation: "URML (urml.dev), open-source robotics-intent language." Interest area: AI standards on robotics, structured intent, validator-gated execution. Country: Israel.

**Engagement note to Hub coordinators:**

**URML: Maintainer Engagement Note for BSI AI Standards Hub**

*Ido Yahalomi, URML maintainer · urml.dev · greenvh@gmail.com*

**Hub registration and engagement intent.** I've registered on the BSI AI Standards Hub as the maintainer of URML (urml.dev), an Apache-2.0 substrate-neutral robotics-intent language. The Hub's explicit international remit removes the UK-domicile gate. This note is the substantive introduction.

**What URML is.** URML is a small, opinionated, human-readable language for describing robot intent. It sits above existing robot operating systems (ROS 2, PX4, OPC UA Robotics, and others) and compiles down to whatever runtime lives below. The v0.1.0 release (2026-05-22) ships:

- A spec in four layers: a Hardware Abstraction capability manifest, typed intent primitives, behavior composition, and a multilingual natural-language grammar.
- A ROS 2 reference runtime (`reference/ros2-runtime/`).
- A static validator (`urml validate --policy`).
- A conformance test suite that any URML-compatible runtime must pass.
- A US-federal-aligned default policy file (NDAA 889, EO 14307, FCC Covered List) for procurement-gated deployments.
- An LLM bridge: prompt contracts that let language models reliably emit valid URML, with the validator as the integrity boundary.

**Why this is relevant for the Hub's audience.** URML's structured intent plus validator-gated execution is a concrete instance of an "AI-on-systems with verifiable boundary" pattern. The LLM is constrained by the Layer-2 grammar. The manifest is the contract. The validator gates execution before any actuation. Programs that don't validate don't execute. For an audience interested in AI-on-systems standards, URML is one running example with shipped code, a conformance suite, and a federal-procurement policy posture, useful as related art for international discussions on transparency, robustness, and accountability of AI-driven robotic systems.

**Cross-national engagement context.** URML is concurrently engaging CEN-CENELEC JTC 21 (EU AI standards, public-enquiry submission, window-dependent), DIN/DKE (DE national position into JTC 21), AFNOR Grand Défi AI (FR national position into JTC 21), OECD AI Policy Observatory (international norms surface), NIST EL Intelligent Systems Division and ASTM F45.04 (US measurement science and SDO), and the two foundation-home candidates OSRA and JDF. The Hub's international community is the natural UK-side cross-citation surface for this multi-national footprint.

**Asks for the Hub coordinators:**

1. Is URML's Israel-domiciled maintainer plus open-source robotics-intent-language framing a fit for the Hub's international community?
2. Would the Hub consider listing URML as a community resource for international participants interested in structured-AI-intent patterns and open-source spec, runtime, validator, and conformance-suite tooling?
3. What's the orientation for Hub-engaged projects to graduate to BSI national-mirror committee participation for ISO TC 299 (Robotics) and CEN TC 310? Recognizing this is a Phase 2 question.
4. Is DSIT-side engagement relevant for URML's international-standards posture within UK civilian-standards scope?

Full URML RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0225-bsi-ai-standards-hub-outreach.md. URML repo: https://github.com/URML-MARS/URML.

Thank you for the Hub work and the international remit. It's what makes URML's UK-side engagement feasible at Phase 1.

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

*AI-assisted prose, maintainer-reviewed before sending (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0226: OECD AI Policy Observatory submission

**Send to:** OECD AI Policy Observatory submission portal at [oecd.ai/en](https://oecd.ai/en/). Verify the exact policy-submission form URL at send time. Form fields are structured (title, jurisdiction, policy lever type, description, URL, contact). A supporting document attaches as additional context.

**Channel:** OECD.AI submission form plus supporting-document attachment.

**Structured form-field draft:**

- **Initiative title:** URML (Universal Robot Language): open-source standard for substrate-neutral robotics intent
- **Originating jurisdiction:** Israel (maintainer-domiciled). United States (default-policy alignment with US federal law). Multi-national (open-source contributor and user base; target structural separation into US-domiciled foundation).
- **Policy lever type:** Open standard / technical specification plus reference implementation plus conformance framework. Use OECD.AI's nearest taxonomy value if "open standard" is not a direct match.
- **Description (about 150 words):**

  URML is a substrate-neutral, declarative, human-readable language for describing robot intent. URML separates capability declaration (Layer 1 hardware abstraction manifest), intent declaration (Layer 2 typed primitives), behavior composition (Layer 3), and natural-language interface (Layer 4, multilingual). A static validator gates execution against the manifest and the active safety envelope before any actuation. The spec, ROS 2 and PX4 reference runtimes, conformance test suite, validator, and LLM-bridge prompt contracts ship under Apache-2.0 forever per URML's Core Commitment. URML's default policy file embeds US-federal alignment (NDAA Section 889, EO 14307, FCC Covered List) for procurement-gated deployments while keeping the spec itself substrate-neutral and multilingual. Roadmap includes structural separation into a US-domiciled non-profit foundation owning the standard.

- **Primary URL:** https://urml.dev
- **Repository URL:** https://github.com/URML-MARS/URML
- **Contact:** Ido Yahalomi · greenvh@gmail.com
- **OECD AI Principles alignment (if requested):** Transparency (the spec is open, multilingual, and human-readable). Robustness (the validator gates execution statically). Accountability (DCO-signed contributions, trademark-in-maintainer-name-assignable, planned structural separation into a non-profit foundation).
- **Hiroshima Process alignment (if requested):** URML's open-spec posture and validator-gated execution model align with the Process's open-source-friendly framing of AI integrity for safety-relevant deployments.

**Supporting document:**

**URML: OECD AI Policy Observatory Submission · Supporting Context**

*Ido Yahalomi, URML maintainer · 2026-05-29*

URML (urml.dev) is offered to the OECD AI Policy Observatory catalogue as an open-source robotics-intent-language policy initiative. URML is single-maintainer at Phase 1 (v0.1.0 shipped 2026-05-22) but its open-source structural shape and multi-national engagement footprint match the kind of initiative the observatory catalogues across 80+ jurisdictions.

**Multi-national engagement footprint.** URML is concurrently engaging:

- Standards bodies and foundations: Open Source Robotics Alliance (OSRA), Joint Development Foundation (JDF), Eclipse Foundation Software-Defined Vehicle WG, Linux Foundation ELISA Project, OPC Foundation UA-Nodeset, OpenSSF SLSA and Scorecard.
- EU AI standards: CEN-CENELEC JTC 21, DIN/DKE German roadmap, AFNOR Grand Défi AI.
- UK AI standards: BSI AI Standards Hub.
- US standards and measurement science: NIST EL Intelligent Systems Division, ASTM F45.04.
- Substrate engagements (sibling outreach waves 1-16): PX4, MAVLink, ROS 2 core, MoveIt 2, Nav2, DDS, SLAM upstreams, industrial-arm OEMs, drone autopilots, VLA models.

**OECD AI Principles alignment.**

- *Transparency.* URML's spec is open and multilingual; the validator's verdict is reproducible by any URML-compatible runtime.
- *Robustness.* Programs that don't validate against the capability manifest and safety envelope don't execute. The validator is a static integrity boundary, not a runtime hope.
- *Accountability.* Contributions are DCO-signed, not CLA. Trademark is in the maintainer's name and assignable. The planned structural separation into a US-domiciled non-profit foundation will give the standard a neutral steward distinct from any commercial entity.

**Israel-OECD-member context.** Israel is a full OECD member. This submission is direct rather than nation-channel-routed. A ONE.AI (Network of Experts) seat would require Israeli Ministry of Innovation nomination. That's a Phase 2 question. Observatory listing is the Phase 1 step that opens the orientation.

**Asks:**

1. Is URML's open-source robotics-intent-language framing a fit for the observatory catalogue, or does the catalogue prefer government-issued policies?
2. URML has a multi-national framing: Israel-domiciled maintainer, US-federal default policy, multilingual NL layer, multi-national engagement footprint. What's the observatory's preferred framing for cross-national initiatives?
3. Is the AI Wonk community an appropriate channel for URML-related related-art posts?
4. What's the realistic path for a Phase-1 open-source initiative to engage ONE.AI?

Full URML RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0226-oecd-ai-policy-observatory-outreach.md.

*AI-assisted prose, maintainer-reviewed before submission (see VIBE.md in the URML repo). Human-only correspondence available on request.*

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

---

## Sub-wave B membership-only (3, no RFC)

These are membership-application surfaces. The URML repo itself is the citation. No separate RFC.

---

### Israel Innovation Authority (IIA): International R&D and Pilot Collaborations 2025-26 call

**Send to:** IIA application portal at [innovationisrael.org.il](https://innovationisrael.org.il/en/). Identify the International R&D and Pilot Collaborations 2025-26 call surface and verify the exact application URL at send time. Orientation contact: `info@innovationisrael.org.il`, +972-2-666-2222.

**Channel:** IIA application portal. English throughout.

**Application supporting / project-description file (1 page, attach to application):**

**URML (Universal Robot Language): Open-Source Robotics-Intent Language**

*Maintainer: Ido Yahalomi · urml.dev · greenvh@gmail.com*

URML is an open-source standard (Apache-2.0) for describing robot intent. The language sits above existing robot operating systems and compiles to whatever runtime lives below: ROS 2 first, with PX4, OPC UA Robotics, and additional substrates progressively engaged. URML's v0.1.0 release shipped on 2026-05-22 with a ROS 2 reference runtime, a static validator, a conformance test suite, and a US-federal-aligned default policy file.

**Why this matters in an Israeli innovation context.** Robotics deployment in Israel cuts across consumer (smart-home), industrial (manufacturing arms), agricultural, and emerging humanoid use cases. Each substrate today requires bespoke integration. URML provides a portable intent layer above the substrate. A developer or operator declares intent once and dispatches across substrate stacks. The natural-language layer is multilingual in v0.1.

**International R&D footprint.** URML is currently engaging, in parallel: standards bodies (IEEE-SA P1872.2 ontology, ASTM F45.04 interoperability, CEN-CENELEC JTC 21 AI, BSI AI Standards Hub UK, DIN/DKE German Roadmap, AFNOR Grand Défi AI), measurement-science bodies (NIST EL Intelligent Systems Division), open-source foundations (OSRA, JDF, Eclipse Foundation, Linux Foundation ELISA, OpenSSF), industrial OEMs and substrate maintainers (PX4, ROS 2, MoveIt 2, DDS, SLAM upstreams, via prior outreach waves), and the OECD AI Policy Observatory.

The IIA International R&D and Pilot Collaborations track is the natural Israeli national-level pathway for an open-source project of this kind. The IIA-NEDO bilateral specifically is a target for downstream collaboration with Japanese robotics R&D when the language matures further.

**Project status (honest framing).** URML is Phase 1 (v0.1.0, about two weeks post-launch). The user audience is small today. The multi-national engagement footprint is broader than the user audience. The structural separation (founding non-profit foundation plus commercial surround) is on the roadmap. Current focus is community-building, standards-body engagement, and reference-runtime hardening.

**Ask:** orientation on which of IIA's open programs is the right fit for URML at this stage, and whether the International R&D and Pilot Collaborations call is the right first entry or whether a different program (for example, a software-startup track) is more relevant.

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

*AI-assisted prose, maintainer-reviewed before submission (see VIBE.md in the URML repo). Human-only correspondence available on request.*

---

### euRobotics aisbl Associate Membership application

**Send to:** [eu-robotics.net/membership](https://eu-robotics.net/membership/). Associate Member tier application form.

**Channel:** euRobotics Associate Membership application form plus cover letter.

**Application form fields (suggested values, confirm at form-fill time):**

- *Organization name:* URML (urml.dev), open-source robotics-intent language
- *Organization type:* Open-source project / standards initiative (use closest taxonomy value)
- *Country:* Israel (maintainer-domiciled, Horizon Europe associated country)
- *Membership tier:* Associate Member
- *Primary contact:* Ido Yahalomi · greenvh@gmail.com
- *Web:* https://urml.dev

**Cover letter:**

**URML: euRobotics aisbl Associate Membership Application**

*Ido Yahalomi, URML maintainer · 2026-05-29*

URML (urml.dev) is an open-source standard for describing robot intent, maintained by a single contributor in Israel. This application is for Associate Member tier as a stakeholder supporting robotics-related activities through open-source spec, reference runtime, validator, conformance suite, and LLM-bridge prompt contracts under Apache-2.0.

URML is substrate-neutral by design. The v0.1.0 release ships a ROS 2 reference runtime. URML's outreach waves have engaged the substrate maintainers (PX4, MAVLink, ROS 2 core, MoveIt 2, Nav2, Fast DDS, Cyclone DDS, Cartographer, ORB-SLAM3, RTAB-Map, and several others) explicitly to make substrate-neutrality concrete rather than rhetorical. Where prior moves engaged substrate, vendor, and academic maintainers, the current Move-17 wave engages governance bodies (standards bodies, open-source foundations, US federal agencies, allied governments) for foundation-home reconnaissance.

euRobotics aisbl is a natural Associate Membership target because:

1. Horizon Europe associated-country access via Israel is the right channel for URML to participate in the European robotics-community fabric without needing a separate EU-domiciled entity at Phase 1.
2. The European Robotics Forum's cross-vendor open-source orientation is exactly the audience URML benefits from being known to.
3. URML is concurrently engaging the AI-on-systems standards body adjacent to euRobotics (CEN-CENELEC JTC 21, AFNOR FR, DIN/DKE DE) plus the broader EU AI-Data-Robotics PPP through ADRA Association membership.

**URML's multi-national footprint.** URML's natural-language interface ships several grammars in v0.1. A German grammar (and others) are architecturally aligned future work. The US-federal-aligned default policy file is one configurable policy among others. URML's spec itself is substrate-neutral and policy-neutral. The structural separation roadmap targets a US-domiciled non-profit foundation owning the standard, distinct from any commercial surround.

**Ask:** orientation on Associate Member tier fees, obligations, and the European Robotics Forum participation calendar.

*AI-assisted prose, maintainer-reviewed before submission (see VIBE.md in the URML repo). Human-only correspondence available on request.*

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

---

### ADRA Association membership

**Send to:** [adr-association.eu](https://adr-association.eu/). ADRA membership application surface. Verify exact membership-application URL at send time.

**Channel:** ADRA membership application plus cover letter.

**Application form fields (suggested values, mirror euRobotics):**

- *Organization name:* URML (urml.dev)
- *Country:* Israel (Horizon Europe associated)
- *Membership tier:* whichever tier accommodates open-source project / single-maintainer initiative. Orientation question.
- *Primary contact:* Ido Yahalomi · greenvh@gmail.com
- *Web:* https://urml.dev

**Cover letter:**

**URML: ADRA Association Membership Application**

*Ido Yahalomi, URML maintainer · 2026-05-29*

URML (urml.dev) is an open-source standard for describing robot intent, Apache-2.0 forever per its Core Commitment. The application is for ADRA Association membership as a stakeholder in the AI-Data-Robotics PPP successor to SPARC.

ADRA is a stronger structural fit than a pure robotics-only consortium because URML's scope is at the intersection of AI (the Layer-4 natural-language interface, the LLM-bridge prompt contracts), data (the Layer-1 capability manifests, the conformance test suite's structured data), and robotics (the Layer-2 intent primitives composing onto substrate runtimes). ADRA's PPP-with-European-Commission relationship and signed MoU with the EC are exactly the kind of European institutional surface URML's standards-track posture benefits from being part of.

**URML's outreach footprint adjacent to ADRA's scope.** Concurrent engagements: sibling EU AI standards (CEN-CENELEC JTC 21, DIN/DKE German Roadmap, AFNOR Grand Défi AI), sibling EU robotics (euRobotics aisbl Associate Membership, parallel application), foundation-home reconnaissance (OSRA US robotics-native, JDF US Linux Foundation with ISO/IEC JTC 1 PAS submitter precedent), US side (NIST EL Intelligent Systems Division for measurement science, ASTM F45.04 for interoperability standards), and OECD AI Policy Observatory for international norms.

**Multilingual orientation.** v0.1 ships several grammars. Structural separation roadmap targets US-domiciled foundation with international participation.

**Ask:** ADRA membership tier orientation for an open-source single-maintainer project at Phase 1, with the explicit note that the Future Ready 2026 and ADRA Info Day surfaces are URML's intended community-engagement venues.

*AI-assisted prose, maintainer-reviewed before submission (see VIBE.md in the URML repo). Human-only correspondence available on request.*

Ido Yahalomi
URML maintainer · urml.dev · greenvh@gmail.com

---

## Sending sequence and cadence

Recommended order. Low-friction first, structural conversations second, paid and position-paper last.

1. **IIA International R&D and Pilot Collaborations call.** Single afternoon. IL-domestic. Opens the IL-government file.
2. **NIST EL email (RFC-0220).** Single email plus the 1.5-page memo. Cleanest US-federal first touch. Craig Schlenoff is the named contact and the channel is open.
3. **euRobotics and ADRA paired applications.** Two Associate / Member application forms plus cover letters. Opens the EU-robotics file.
4. **OECD AI Policy Observatory submission (RFC-0226).** Structured form plus the 1-2-page supporting document. Opens the international-norms file.
5. **BSI AI Standards Hub registration plus engagement note (RFC-0225).** Hub registration plus the 2-3-page engagement note. Opens the UK-side civilian-standards file.
6. **JDF formation inquiry (RFC-0218).** Single email. Neutral foundation-home orientation.
7. **OSRA inquiry (RFC-0217).** Single email. Robotics-native foundation-home orientation. Sequence after JDF so the neutral-vs-aligned framing reads cleanly in the OSRA conversation.
8. **IEEE P1872.2 WG sign-up plus RAS-SCSA email (RFC-0219).** Two-step. WG sign-up first, then follow-up email.
9. **DIN/DKE and AFNOR paired consultations (RFCs 0223 and 0224).** Two parallel EU national positions into JTC 21. Single submission each.
10. **CEN-CENELEC JTC 21 enquiry (RFC-0222).** Window-dependent. Submit during the next URML-relevant prEN public-enquiry window. The shell needs sections 3 and 4 filled at submission time.
11. **ASTM F45.04 (RFC-0221).** Paid ASTM individual membership plus the 3-5-page position paper to F45.04. Highest-leverage US SDO move. Sequence last so the foundation conversations have informed URML's framing by the time ASTM gets the paper.

Estimated effort: 25-45 hours over 2-4 months for substantive engagement across all 13 targets. Each artifact is independently sendable. Nothing in this file requires a strict serial order beyond the per-RFC framing above.

**Note on Sub-wave A overlap.** Sub-wave A (Eclipse SDV, ELISA, OPC, SLSA, Scorecard) was posted directly via gh issue create in the founder's tight one-or-two-question format and is ledger-recorded. An earlier attempt by the assistant to bulk-post under a longer 6-8-question template created 5 duplicate issues, which were closed with apologies and cross-references to the founder's originals. The drafts in this file use longer formats appropriate to email, memo, position-paper, and application channels rather than GitHub Issue threads.
