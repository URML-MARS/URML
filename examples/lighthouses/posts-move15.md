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

# Move #15 post bodies — niche verticals (surgical, construction, delivery, warehouse) (Theme D)

Copy-paste-ready Issue bodies for the Move #15 outreach. **Wave shape**: 5 verified Theme D targets (3 Tier A + 2 Tier B), verified 2026-05-28. RFC numbers 0191-0195. **The smallest URML wave so far** — reflects the closed-vertical market reality (18 Tier C exclusions documented).

Ledger state: [`outreach-move15.yaml`](outreach-move15.yaml). Full research audit: [`move15-research-2026-05-28.md`](move15-research-2026-05-28.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("fifteen outreach waves to date") are fine.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #15 post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/VIBE.md)). Human-only correspondence available on request.*
```

**Vertical-firsts:**
- **RFC-0191 JHU dVRK** opens URML's surgical / medical class — first surgical engagement.
- **RFC-0193 Starship Technologies** opens URML's delivery-robot class — first delivery engagement.

**Schema-extension flags:**
- Surgical-class platform + telesurgery topology + surgical-instrument-class + regulatory-class (RFC-0191).
- Assistive / prosthetic / rehabilitation application-class (RFC-0192; shared with Move-14 RFC-0186 Kinova).
- Sidewalk-delivery platform-class + urban-public-space deployment-context + closed-stack engagement-layer (RFC-0193).
- Alternate-substrate middleware + LGPL substrate-license-class + YARP↔ROS-2 bridging (RFC-0194).
- Engagement-surface-quality declaration (RFC-0195; novel).

**One license-clarification ask:** RFC-0191 JHU dVRK (CISST custom permissive → explicit OSI declaration).

---

## Tier A — 3 research-lab-direct / vendor-direct targets

### RFC-0191: JHU dVRK (Da Vinci Research Kit)

**Post to:** https://github.com/jhu-dvrk/sawIntuitiveResearchKit/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for the Da Vinci Research Kit — URML's first surgical / medical RFC, with a CISST license-clarification ask
```

**Body:**

```markdown
Hi @jhu-dvrk team,

Proposing a URML v0.1 capability-manifest mapping for the Da Vinci Research Kit over `jhu-dvrk/sawIntuitiveResearchKit`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent: a typed primitive vocabulary plus a Layer-1 capability manifest and a validator that gates programs against the manifest before any actuator publishes.

**This is URML's first surgical / medical-robotics RFC.** Surgical / medical robotics is a structural URML manifest gap — URML's v0.1 has no surgical-class platform declaration, no telesurgery master-slave topology field, no surgical-instrument-class declaration, and no regulatory-class declaration. The dVRK is the research-lab-direct surface where this conversation can happen at all (commercial da Vinci, Auris/J&J, CMR Surgical, Stryker Mako are all closed). JHU is the proper layer for the manifest-mapping discussion.

The CISST custom permissive license is functionally Apache-2.0-friendly but isn't SPDX-recognized; URML's adapter-grade downstream bundling needs an explicit OSI clarification.

This is **proposal-only**, posted as part of URML's Move #15 outreach (niche verticals, 5 engageable RFCs). No bridge in URML's repo yet; a bridge would ship engagement-driven.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0191-jhu-dvrk-outreach.md

Questions worth `jhu-dvrk` maintainer input on:

1. **CISST license clarification.** Can the repo get an explicit OSI-recognized license declaration (or clarification that CISST is Apache-2.0-style equivalent for downstream-bundling purposes)?
2. **Surgical-class platform manifest fields.** URML's v0.1 has no surgical-class declaration. Spec RFC queued. What manifest fields would a dVRK deployment expect (master-slave topology, instrument-class declaration, force/position constraints)?
3. **Regulatory-class declaration.** Should URML's manifest declare research-use-only vs FDA-cleared status as a first-class field?
4. **Telesurgery control-loop declaration.** Master-MTM + patient-PSM coupling has specific safety-and-latency constraints; manifest field shape?
5. **Adapter home.** URML repo (`reference/surgical-runtime/DvrkAdapter`), JHU-maintained `jhu-dvrk/dvrk-urml-bridge`, or both?
6. **Conformance listing.** Would the dVRK maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0192: IIT iCub

**Post to:** https://github.com/robotology/icub-main/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for iCub — medical-research humanoid
```

**Body:**

```markdown
Hi @robotology team,

Proposing a URML v0.1 capability-manifest mapping for the iCub humanoid platform over `robotology/icub-main`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

This is URML's first medical-research-humanoid engagement. URML's prior humanoid coverage targets commercial OEM platforms (apollo_biped, digit_biped, figure_biped, neo_biped, optimus_biped fixtures); iCub is the research-lab-direct sibling at the medical-relevant layer with cognitive-research + assistive-technology + prosthetic-interface + rehabilitation focus. URML's manifest declares iCub's 53-DoF full-body articulation plus the YARP-middleware substrate (engaged separately via a sibling RFC at the substrate layer).

This is **proposal-only**, posted as part of URML's Move #15 outreach (5 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0192-iit-icub-main-outreach.md

Questions worth `robotology` iCub maintainer input on:

1. **Assistive / prosthetic / rehabilitation application-class manifest fields.** URML's v0.1 has no application-class declaration. Spec RFC queued (shared with URML's prior assistive cobot engagement). Manifest field expectations from the iCub perspective?
2. **YARP middleware substrate manifest declaration.** Should URML's manifest declare YARP as an alternate substrate to ROS 2, or treat iCub-via-yarp as a single composed declaration?
3. **Research-platform-class declaration.** Should URML's manifest declare institutional research-platform distribution model (vs vendor-OEM commercial)?
4. **53-DoF articulation declaration.** What manifest field granularity makes sense for iCub's full-body DoF inventory?
5. **Adapter home.** URML repo (`reference/humanoid-runtime/IcubAdapter`), IIT-maintained `robotology/icub-urml-bridge`, or both?
6. **Conformance listing.** Would IIT consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0193: Starship Technologies

**Post to:** https://github.com/starship-technologies/bag_rdr/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for sidewalk delivery — engagement at the bag_rdr infrastructure layer
```

**Body:**

```markdown
Hi @starship-technologies team,

Proposing a URML v0.1 capability-manifest mapping for the sidewalk-delivery class over `starship-technologies/bag_rdr`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

**This is URML's first delivery-robot RFC.** The engagement enters at the ROS-bag-reader infrastructure layer because URML's research surfaced that the actual sidewalk-delivery robot stack is closed; the bag-reader + companion ROS-bag infrastructure repos (`bag_rdr`, `common_cxx`, `gobag`, `bagrec`) are the engageable public surface. URML-fit is via perception-replay / logging-format manifest declarations + a structural sidewalk-delivery class declaration that doesn't exist in URML's v0.1.

This is **proposal-only**, posted as part of URML's Move #15 outreach (5 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0193-starship-technologies-outreach.md

Questions worth `starship-technologies` maintainer input on:

1. **Sidewalk-delivery platform-class manifest fields.** URML's v0.1 has no platform-class for delivery robots. Spec RFC queued. Manifest field expectations from the Starship perspective?
2. **Urban-public-space deployment-context declaration.** Manifest field for pedestrian-aware navigation + public-street operation + weather constraints?
3. **Bag-reader infrastructure scope.** Is `bag_rdr` the right URML engagement entry, or is there a different infrastructure-layer surface URML should target?
4. **Closed-stack engagement-layer declaration.** Should URML's manifest declare that the engagement is data/infrastructure-only (vs full-stack adapter)?
5. **Bridge home.** URML repo (`reference/delivery-runtime/StarshipBagReaderAdapter`), Starship-maintained, or external?
6. **Conformance listing.** Would Starship Technologies consider a README link to URML's compatible-runtimes registry once a working bridge ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier B — 2 research-collab / cross-citation targets

### RFC-0194: IIT YARP middleware

**Post to:** https://github.com/robotology/yarp/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for YARP — alternate-substrate middleware sibling to URML's ros2-runtime
```

**Body:**

```markdown
Hi @robotology YARP team,

Proposing a URML v0.1 capability-manifest cross-citation for YARP over `robotology/yarp`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

URML's substrate-neutral claim depends on declaring more than one substrate. URML's existing `reference/ros2-runtime/` targets ROS 2; YARP is the sibling middleware that makes URML's substrate-neutrality concrete in the manifest. Medical-research / European-research deployments (including iCub, engaged separately) often use YARP rather than ROS 2; URML's manifest needs to declare these substrates cleanly.

**LGPL** is the gating fact for adapter shape — URML's Apache-2.0 adapter pattern composes with LGPL middleware at the API boundary without modifying YARP, which is LGPL-compatible posture. Cross-citation framing recommended pending substrate-license-class Spec RFC.

This is **proposal-only**, posted as part of URML's Move #15 outreach (5 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0194-iit-yarp-outreach.md

Questions worth `robotology` YARP maintainer input on:

1. **Alternate-substrate middleware manifest declaration.** URML's v0.1 has no `substrate.middleware: yarp` declaration. Spec RFC queued. Manifest field expectations from the YARP perspective (version, transport class, port naming convention)?
2. **LGPL substrate license-class declaration.** Should URML's manifest declare LGPL-linkable substrate as a first-class field for downstream operator awareness?
3. **YARP↔ROS-2 bridging declaration.** Some deployments bridge between YARP and ROS 2; manifest field for declaring bridging topology?
4. **Bridge home.** Cross-citation only (recommended pending LGPL framing), URML repo (`reference/yarp-runtime/`), or IIT-maintained `robotology/yarp-urml-bridge`?
5. **Conformance listing.** Would IIT consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0195: Serve Robotics

**Post to:** https://github.com/serve-robotics/Model-Optimizer/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for Serve Robotics — sidewalk-delivery sibling
```

**Body:**

```markdown
Hi @serve-robotics team,

Proposing a URML v0.1 capability-manifest cross-citation for Serve Robotics over `serve-robotics/Model-Optimizer`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

URML's manifest needs to declare the sidewalk-delivery class (Spec RFC shared with a sibling Move-15 engagement). Serve Robotics is the Uber-spinoff sidewalk-delivery sibling; URML-fit acknowledges that Serve's public GitHub surface is predominantly forks (Model-Optimizer, horde, libOpenDRIVE, unreal-mcp, xviz, etc.) with minimal vendor-original engageable code. Engagement is light-touch and partly asks where vendor-original surface lives.

This is **proposal-only**, posted as part of URML's Move #15 outreach (5 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0195-serve-robotics-outreach.md

Questions worth `serve-robotics` maintainer input on:

1. **Vendor-original engagement surface.** Where does Serve's vendor-original code (vs forks) live? Off-GitHub developer portal, private repos, or fork-heavy posture is intentional?
2. **Sidewalk-delivery platform-class manifest fields.** Shared Spec RFC with the sibling Move-15 sidewalk-delivery engagement. Manifest field expectations?
3. **Engagement-surface-quality declaration.** Should URML's manifest declare the engagement-surface quality (vendor-original vs fork-heavy vs closed-stack) for downstream operator awareness?
4. **Bridge home.** Cross-citation only (recommended given fork-heavy surface), URML repo, or external?
5. **Conformance listing.** If vendor-original surface emerges, would Serve Robotics consider a README link to URML's compatible-runtimes registry?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier C (18) — recorded in research file, NOT engaged

See [`move15-research-2026-05-28.md`](move15-research-2026-05-28.md) for the full Tier-C list documenting the closed-vertical market reality:

- **Surgical OEMs × 4:** Intuitive Surgical, Auris Health / J&J, CMR Surgical, Stryker Mako — all closed.
- **Construction OEMs × 5:** Built Robotics, Dusty Robotics, Canvas Construction, Civ Robotics, Hilti — **ZERO engageable construction candidates.**
- **Delivery OEMs × 3:** Nuro, Kiwibot, Cartken — no public GitHub.
- **Warehouse AMR × 6:** Fetch Robotics (already engaged Move-14 RFC-0188), Clearpath Robotics (already engaged Move-5 RFC-0072), Open-RMF (already engaged Move-2 RFC-0053), MiR / Locus / Vecna / Symbotic / OTTO Motors / 6 River Systems (all closed), Greyorange (Erlang ops only), Geek+ (PRC-excluded).
