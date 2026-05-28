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

# Move #14 post bodies — mobile manipulators + commercial humanoids (Theme B)

Copy-paste-ready Issue / Discussion bodies for the Move #14 outreach. **Wave shape**: 7 verified Theme B targets (4 Tier A + 3 Tier B), verified 2026-05-28. RFC numbers 0184-0190.

Ledger state: [`outreach-move14.yaml`](outreach-move14.yaml). Full research audit: [`move14-research-2026-05-28.md`](move14-research-2026-05-28.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("fourteen outreach waves to date") are fine. Naming the specific orgs that responded is not.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #14 post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Schema-extension flags.** Move #14 surfaces multiple v0.1 schema gaps that should be opened as Spec RFCs in parallel:

- **Mobile-manipulator topology declaration** (Hello Robot RFC-0184, Fetch RFC-0188, Toyota HSR RFC-0190 — composite mobility + actuators + cameras block).
- **Cobot-arm precision-class declaration** (Franka RFC-0185, Kinova RFC-0186).
- **Per-joint torque-sensing declaration** (Franka RFC-0185).
- **Humanoid platform refinement + wheeled-humanoid composite topology + NN-controller class + managed-program distribution-class** (1X RFC-0187).
- **Acquisition-era governance declaration** (Fetch RFC-0188; novel — first concrete case).
- **Multi-platform-org engagement + social-robot topology** (PAL RFC-0189).
- **Research-consortium-class platform + end-effector-mounted-camera (grip-camera) declaration** (Toyota HSR RFC-0190).
- **Telescoping-arm kinematics + pan-tilt-head perception** (Hello Robot RFC-0184).
- **Assistive-application-class declaration** (Kinova RFC-0186).

Each is a separate Spec RFC; URML's outreach RFCs ship with the v0.1 `custom` measurement_type / mobility-class escape-hatch and reference the queued Spec RFC.

**Three rows carry license-clarification asks** in their per-target question lists: RFC-0184 Hello Robot, RFC-0188 Fetch, RFC-0189 PAL TIAGo.

**Three rows carry canonical-engagement-surface asks**: RFC-0186 Kinova (ROS 2 successor question), RFC-0189 PAL (multi-platform org), RFC-0190 TRI (TRI vs Toyota-Japan).

**One fixture-refinement cross-link**: RFC-0187 1X Technologies refines URML's existing `neo_biped` fixture upstream.

---

## Tier A — 4 vendor-direct targets

### Mobile manipulators (3)

### RFC-0184: Hello Robot (Stretch)

**Post to:** https://github.com/hello-robot/stretch_ros2/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Stretch mobile manipulator — and a license-clarification ask
```

**Body:**

```markdown
Hi @hello-robot team,

Proposing a URML v0.1 capability-manifest mapping for the Stretch mobile manipulator over `hello-robot/stretch_ros2`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent: a typed primitive vocabulary plus a Layer-1 capability manifest and a validator that gates programs against the manifest before any actuator publishes.

Stretch is the mobile-manipulator class URML's manifest declares for indoor / home-assistance / research deployments. Mobile-base + telescoping-arm + pan-tilt-camera composition exercises URML's `mobility` + `actuators` + `cameras` blocks simultaneously — a cross-block boundary URML's existing cobot-only or mobile-base-only fixtures don't fully test. The MIT-spinoff posture aligns with URML's open-core stance. **License-clarification ask** is the gating fact: no SPDX visible upstream blocks Apache-2.0 downstream bundling; URML's adapter composes at the ROS 2 interface regardless.

This is **proposal-only**, posted as part of URML's Move #14 outreach (mobile manipulators + commercial humanoids, 7 engageable RFCs). No bridge in URML's repo yet; a bridge would ship engagement-driven.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0184-hello-robot-stretch-outreach.md

Questions worth `hello-robot` maintainer input on:

1. **License clarification.** Can `hello-robot/stretch_ros2` get an explicit OSI license declaration?
2. **Mobile-manipulator topology manifest fields.** URML's v0.1 has no `topology: mobile_base_plus_arm_plus_head` declaration. Spec RFC queued. Manifest field expectations from the Stretch perspective?
3. **Telescoping-arm kinematics.** Stretch's lift + telescope is a non-standard kinematic chain. Manifest field expectations?
4. **Pan-tilt-head perception declaration.** Should URML's manifest declare pan-tilt-mounted cameras as a distinct class vs fixed-mounted?
5. **Adapter home.** URML repo (`reference/mobile-manipulator-runtime/StretchAdapter`), Hello-Robot-maintained `hello-robot/stretch-urml-bridge`, or both?
6. **Conformance listing.** Would Hello Robot consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0185: Franka Robotics (Panda / FR3)

**Post to:** https://github.com/frankaemika/franka_ros2/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Franka Panda / FR3 — cobot-arm precision-class substrate
```

**Body:**

```markdown
Hi @frankaemika team,

Proposing a URML v0.1 capability-manifest mapping for the Franka Panda / FR3 cobot arm over `frankaemika/franka_ros2`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

Franka FR3 is the high-precision research-cobot reference URML's existing cobot-runtime fixtures imply support for. Manifest declares Franka as the actuator class; URML's existing `pick_from` / `place_at` / `swap_tool` primitives (RFC-0013 industrial profile) dispatch via `franka_ros2`. Franka's per-joint torque sensing is the distinguishing capability URML's v0.1 actuator manifest cannot today declare — a cobot-arm precision-class Spec RFC is queued (shared with sibling Move-14 Kinova RFC).

This is **proposal-only**, posted as part of URML's Move #14 outreach (7 engageable RFCs in this wave). Franka was deferred from URML's Move-13 actuator-vendors wave because cobot OEMs sit at the platform layer, not the actuator-controller layer — Move-14 is the correct placement.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0185-frankaemika-franka-ros2-outreach.md

Questions worth `frankaemika` maintainer input on:

1. **Cobot-arm precision-class manifest fields.** URML's v0.1 actuator manifest doesn't declare precision class (research-grade torque sensing per joint vs industrial-grade position-only). Spec RFC queued. Manifest field expectations from the Franka perspective?
2. **Per-joint torque-sensing declaration.** Franka's distinguishing capability — manifest field shape?
3. **CE / safety-certification declaration.** Should URML's manifest declare safety-certification class for cobot deployments alongside humans?
4. **Adapter home.** URML repo (`reference/cobot-runtime/FrankaAdapter`), Franka-maintained `frankaemika/franka-urml-bridge`, or both?
5. **Conformance listing.** Would Franka Robotics consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0186: Kinova Robotics (Jaco / Movo)

**Post to:** https://github.com/Kinovarobotics/kinova-ros/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Kinova Jaco / Movo — and a ROS 2 canonical-surface ask
```

**Body:**

```markdown
Hi @Kinovarobotics team,

Proposing a URML v0.1 capability-manifest mapping for the Kinova Jaco / Movo cobot arms over `Kinovarobotics/kinova-ros`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

URML's existing `kinova_cobot_cell` manifest fixture implies engagement with the Kinova surface; this RFC formalizes the upstream link. The 410-star adoption signal on this repo reflects substantial deployed-fleet presence, particularly in assistive-robotics applications (wheelchair-mounted, accessibility deployments). Kinova's distinguishing application class — assistive technology — is something URML's v0.1 manifest doesn't today declare.

Acknowledging the repo has been quiet on GitHub for >1.5 years. Engagement is partly a reactivating-nudge + partly a **canonical-engagement-surface ask**: is there a ROS 2 successor surface URML's adapter should target instead?

This is **proposal-only**, posted as part of URML's Move #14 outreach (7 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0186-kinovarobotics-kinova-ros-outreach.md

Questions worth `Kinovarobotics` maintainer input on:

1. **Canonical ROS 2 engagement surface.** Is `Kinovarobotics/kinova-ros` the active engagement surface, or has a `kinova-ros2` (or similar) successor moved elsewhere?
2. **Repository status.** Stale 654 days — actively maintained on slower cadence, dormant-but-supported, or has development moved to a successor?
3. **Assistive-application-class manifest fields.** URML's manifest doesn't today declare deployment-class. Manifest field expectations from the Kinova assistive perspective?
4. **Cobot-arm precision-class manifest fields.** Shared shared with sibling Move-14 Franka RFC.
5. **Adapter home.** URML repo (`reference/cobot-runtime/KinovaAdapter`), Kinova-maintained, or both?
6. **Conformance listing.** Would Kinova consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### Commercial humanoid (1)

### RFC-0187: 1X Technologies (EVE / NEO)

**Post to:** https://github.com/1x-technologies/eve-ros2-examples/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for 1X EVE / NEO — refining URML's existing neo_biped fixture upstream
```

**Body:**

```markdown
Hi @1x-technologies team,

Proposing a URML v0.1 capability-manifest mapping for the 1X EVE and NEO humanoid platforms over `1x-technologies/eve-ros2-examples`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

URML's existing `neo_biped` manifest fixture (per RFC-0009 mobility specialization) declares NEO as a bipedal humanoid class; this RFC closes the loop with the upstream surface. The fixture is URML-side declaration today; engagement validates / refines it with the vendor maintainer — same posture URML adopted with its `microbit_edu` fixture upstream in a prior wave.

**Important framing note for honesty.** URML's Move-14 research surveyed seven commercial humanoid OEM candidates (Apptronik, Sanctuary AI, Figure AI, Tesla Optimus, Agility Robotics, Boston Dynamics Atlas, 1X) — 1X is the only one with vendor-direct active public robot code. URML's existing humanoid fixtures (apollo_biped, digit_biped, figure_biped, neo_biped, optimus_biped) exist as URML-side declarations because the other upstream surfaces aren't engageable. That makes 1X's role in URML's humanoid story uncommonly load-bearing.

This is **proposal-only**, posted as part of URML's Move #14 outreach (7 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0187-1x-technologies-eve-outreach.md

Questions worth `1x-technologies` maintainer input on:

1. **Humanoid platform refinement.** URML's `neo_biped` fixture sketches the NEO manifest mapping. What fields would 1X refine / add (DoF inventory, sensor inventory)?
2. **EVE wheeled-humanoid topology.** Wheeled-base + humanoid-torso composite — manifest declaration shape?
3. **NN-controller class declaration.** Should URML's manifest declare which neural-network-trained controller class is active (similar to URML's VLA RFCs from a prior wave)?
4. **Managed-program distribution-class.** Should URML's manifest declare 1X's managed-program distribution model for downstream operator awareness?
5. **Adapter home.** URML repo (`reference/humanoid-runtime/OneXAdapter`), 1X-maintained `1x-technologies/eve-urml-bridge`, or both?
6. **Conformance listing.** Would 1X Technologies consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier B — 3 research-collab / cross-citation targets

### RFC-0188: Fetch Robotics

**Post to:** https://github.com/fetchrobotics/fetch_ros/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for Fetch + Freight — license + post-acquisition-governance asks
```

**Body:**

```markdown
Hi @fetchrobotics maintainers (and Zebra Technologies, if reachable),

Proposing a URML v0.1 capability-manifest cross-citation for Fetch + Freight over `fetchrobotics/fetch_ros`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

Fetch / Freight are the mobile-manipulator + mobile-base lineage with substantial research-lab deployment in academic robotics. URML's manifest declares the mobile-manipulator topology — mobile base + arm + head as a single integrated platform — exercising the cross-block boundary URML's existing fixtures don't fully test.

Two open questions frame this RFC as cross-citation rather than full manifest mapping:

- **License clarification:** no SPDX visible upstream blocks Apache-2.0 downstream bundling.
- **Post-acquisition governance:** Fetch was acquired by Zebra Technologies in 2023; the GitHub presence has been stale 646 days since. Is the surface still community-supported, or has engagement migrated elsewhere?

This is **proposal-only**, posted as part of URML's Move #14 outreach (7 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0188-fetchrobotics-fetch-ros-outreach.md

Questions worth maintainer input on:

1. **License clarification.** Can `fetchrobotics/fetch_ros` get an explicit OSI license declaration?
2. **Post-acquisition governance.** Is the Fetch GitHub org actively maintained under Zebra, dormant-but-monitored, or has engagement moved to a successor surface entirely?
3. **Mobile-manipulator topology manifest fields.** Same shared question as URML's Hello Robot Stretch RFC.
4. **Acquisition-era governance manifest declaration.** Should URML's manifest declare acquisition-era platforms for downstream operator awareness? This is the first concrete case URML's outreach has encountered.
5. **Bridge home.** Cross-citation only (recommended pending license + governance), URML repo (`reference/mobile-manipulator-runtime/FetchAdapter`), or none?
6. **Conformance listing.** If the platform is still community-supported, would the maintainers consider a README link to URML's compatible-runtimes registry?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0189: PAL Robotics (TIAGo / TALOS / ARI)

**Post to:** https://github.com/pal-robotics/tiago_tutorials/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for PAL Robotics platforms — canonical-engagement-surface + license-clarification asks
```

**Body:**

```markdown
Hi @pal-robotics team,

Proposing a URML v0.1 capability-manifest cross-citation for PAL Robotics' TIAGo (mobile manipulator), TALOS (humanoid), and ARI (social robot) over `pal-robotics/tiago_tutorials`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

PAL Robotics is one of Europe's most established robotics OEMs — TIAGo / TALOS / ARI span three distinct platform topology classes URML's manifest would benefit from declaring cleanly. Two engagement asks frame this RFC as cross-citation pending clarifications:

- **Canonical-engagement-surface ask.** PAL has multiple repos at `pal-robotics`; `tiago_tutorials` is one of many and the most-stale of the visible ones (>2 years). Which repo — or off-GitHub channel — is the canonical engagement surface in 2026?
- **License-clarification ask.** No SPDX visible on the tutorials repo; URML's adapter-grade reuse depends on per-surface clarity across the PAL repo catalog.

This is **proposal-only**, posted as part of URML's Move #14 outreach (7 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0189-pal-robotics-tiago-outreach.md

Questions worth `pal-robotics` maintainer input on:

1. **Canonical engagement surface.** Which PAL repo (or off-GitHub channel) is the canonical engagement surface in 2026?
2. **License clarification.** Can the active engagement-surface repo get an explicit OSI license declaration?
3. **Multi-platform-org engagement scope.** Should URML engage per-platform (separate RFCs for TIAGo / TALOS / ARI), or per-org with manifest-side platform identifiers?
4. **Mobile-manipulator + humanoid + social-robot topology manifest fields.** Three distinct topology classes; Spec RFCs queued. Manifest field expectations from the PAL perspective?
5. **Adapter home.** Cross-citation only (recommended pending clarifications), URML repo, or PAL-maintained?
6. **Conformance listing.** Would PAL Robotics consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0190: Toyota Research HSR

**Post to:** https://github.com/ToyotaResearchInstitute/hsr_description/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for Toyota HSR — canonical-engagement-surface ask (TRI vs Toyota-Japan)
```

**Body:**

```markdown
Hi @ToyotaResearchInstitute maintainers (and Toyota Japan, if reachable),

Proposing a URML v0.1 capability-manifest cross-citation for the Toyota HSR (Human Support Robot) over `ToyotaResearchInstitute/hsr_description`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

HSR is a research-grade mobile manipulator widely used in robotics-competition contexts (RoboCup@Home, World Robot Summit) and assistive-robotics research. URML's mobile-manipulator class declaration applies cleanly to HSR's mobile-base + arm + display-head composition; HSR's grip-camera (end-effector-mounted camera) is a distinguishing perception feature URML's `cameras` block doesn't today declare.

The public repo is URDF/mesh-asset-only; the primary HSR robot stack is closed. **Canonical-engagement-surface ask** is the primary item: TRI is Toyota's US research-direct surface, but Toyota Japan owns HSR's primary engineering. Where does active engagement happen in 2026 — TRI-side, Toyota-Japan-side, or via a research consortium?

This is **proposal-only**, posted as part of URML's Move #14 outreach (7 engageable RFCs in this wave; completes the Move).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0190-toyota-research-hsr-outreach.md

Questions worth maintainer input on:

1. **Canonical engagement surface.** Is TRI the canonical engagement surface for HSR research, or does Toyota Japan own the primary engineering?
2. **Repository status.** Stale 753 days — actively maintained on slower cadence, dormant-but-supported, or has the engagement moved to a research-consortium channel?
3. **Mobile-manipulator topology manifest fields.** Same shared question as URML's Hello Robot Stretch + Fetch Robotics RFCs.
4. **Research-consortium-class platform declaration.** Should URML's manifest declare research-program-only distribution for downstream operator awareness?
5. **Grip-camera declaration.** Manifest field for end-effector-mounted cameras?
6. **Bridge home.** Cross-citation only (recommended given URDF-only public scope), URML repo, or TRI-maintained?
7. **Conformance listing.** Would TRI consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
8. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier C (6) — recorded in research file, NOT engaged

See [`move14-research-2026-05-28.md`](move14-research-2026-05-28.md) for the full Tier-C list with exclusion causes:

- **0 public repos × 2:** Apptronik (Apollo humanoid closed), Sanctuary AI (Phoenix humanoid closed).
- **No humanoid robot code × 2:** Figure AI (55 build-tools repos only), Tesla Optimus (legacy Maven repos only).
- **Archived primary surface × 1:** Agility Robotics (cassie-doc archived).
- **Already engaged × 1:** Boston Dynamics Atlas (no separate repo; Spot engaged via Move-2 RFC-0043).

URML's existing humanoid manifest fixtures (apollo_biped, digit_biped, figure_biped, neo_biped, optimus_biped) exist as URML-side declarations because the upstream surfaces aren't engageable; private-channel engagement is outside URML's outreach pattern. The Tier C list is URML's honest record of this market-shape reality.
