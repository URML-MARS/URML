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

# Move #7 post bodies

Copy-paste-ready Issue / Discussion / email / Discord-post bodies for the Move #7 agriculture-robotics outreach. Eight RFCs total: 3 Tier A vendor-style (Twisted Fields, Sentera, Burro) and 5 Tier B research-collab (UCLA AgriCruiser, INRAE Romea, EarthSense/TerraSentia, Cornell AgXRP, Wageningen FRE).

Ledger state lives in [`outreach-move7.yaml`](outreach-move7.yaml). After posting, set `posted_url`, update `last_touch`, and update `next_action`.

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly. Agriculture-vendor cadence varies; small DIY orgs may be slower than large commercial outfits.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to other engaged URML maintainers as social proof. URML's own shipped artifacts (`reference/marine-runtime/`, `reference/edu-runtime/`, `reference/cobot-runtime/`, RFCs in `docs/rfcs/`) are fine to cite. Aggregate counts ("~80 RFCs sent, single-digit substantive responses") are fine. Naming the specific orgs that responded is not.

---

## RFC-0092: Twisted Fields / Acorn

**Post to:** https://github.com/Twisted-Fields/acorn-precision-farming-rover/issues/new

**Title:**

```
Research-collab proposal: URML (substrate-neutral robot intent) for Acorn precision-farming rover
```

**Body:**

```markdown
Hi Twisted Fields team,

Posting this as a collaboration proposal to the Acorn maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`, plus profile extensions for agriculture / educational / research) sits one layer above ROS 2 / PX4 / vendor SDKs.

URML's value proposition for Acorn: a farmer or educator writes "drive the rover along row 3 and measure soil moisture every 2 meters" in URML's natural-language layer; URML compiles to `move_to(...)` + `measure(soil_moisture, ...)` + `wait_for(distance, 2m)`; an `AcornAdapter` dispatches the primitives onto Acorn's existing autonomous-navigation layer. The license fit is clean (Acorn is Apache-2.0, URML's `reference/` is Apache-2.0 too) and the audience is exactly the maker / farmer / educator who would benefit from URML's English-to-primitive path.

Cross-link to URML's first agriculture-vertical RFC ([RFC-0067 FarmBot](https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0067-farmbot-outreach.md)) and to URML's existing `reference/marine-runtime/` precedent for Apache-2.0 substrate adapters.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0092-twisted-fields-acorn-outreach.md

This is proposal-only, part of URML's **Move #7** outreach (agriculture-robotics second wave). Eight targets in this wave, mixing Tier A vendor-style and Tier B research-collab framing. URML has sent ~90 RFCs across seven outreach moves; single-digit substantive responses to date (the outreach is real but the language is early).

## Feedback we'd value

1. **Adapter home.** URML's `reference/agriculture-runtime/` (URML-side), Twisted-Fields contributed example, or both?
2. **Authoritative manifest values.** Mass, payload, sensor inventory, mobility (skid-steer vs differential).
3. **Repo cadence.** Is `acorn-precision-farming-rover` actively maintained, in maintenance mode, or paused?
4. **Solar-power / battery-aware execution.** Should URML's static verifier reason about battery state at validation time?
5. **Agriculture-profile co-design.** Future `spec/profiles/agriculture/` Layer-3 (plant / water / weed / scout) interest?
6. **Conformance lane.** Open to a URML conformance line on the rover README?
7. **Anything else.**

Thanks for the Acorn project and the open-source posture across the Twisted-Fields org. URML's substrate-neutral story benefits from clean Apache-2.0 ag-robotics work like Acorn.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0093: Sentera

**Post to:** https://github.com/SenteraLLC/py-radiometric-corrections/issues/new (or `py-image-registration` if maintainers prefer)

**Title:**

```
Research-collab proposal: URML (substrate-neutral robot intent) for Sentera multispectral payloads + MAVLink integration
```

**Body:**

```markdown
Hi Sentera team,

Posting this as a collaboration proposal to the SenteraLLC maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary sits one layer above ROS 2 / PX4 / MAVLink / vendor SDKs.

URML's value proposition for Sentera: an agronomist writes "photograph the field on a 10-meter grid and record the multispectral signature at each waypoint" in URML's natural-language layer; URML compiles to `move_to(...)` + `measure(multispectral, ...)` per waypoint; a `SenteraAdapter` (extending URML's existing `reference/px4-runtime/`) dispatches the primitives onto Sentera's MAVLink-integrated Double 4K or 6X payload. Programs written against one payload retarget to the other by manifest swap; programs written against an ag-drone retarget to an ag-rover by manifest swap. The substrate-neutral story is exactly the value proposition for ag-imagery research and operations.

URML's `reference/px4-runtime/` already targets the MAVLink ecosystem; Sentera's MAVSDK / MAVSDK-Swift forks plus the documented MAVLink integration on `support.sentera.com` compose directly. The `measure` primitive with a typed `payload:` field abstracts radiometric / multispectral / NDVI readings as substrate-neutral observations.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0093-sentera-outreach.md

This is proposal-only, part of URML's **Move #7** outreach (agriculture-robotics second wave). Eight targets in this wave. URML has sent ~90 RFCs across seven outreach moves; single-digit substantive responses to date.

## Feedback we'd value

1. **Adapter home.** URML's `reference/px4-runtime/sentera/` (URML-side), a SenteraLLC contributed example, or both?
2. **MAVLink command surface.** Which MAVLink command IDs are the canonical hooks for triggering Double 4K / 6X captures from a URML-compiled mission?
3. **`py-radiometric-corrections` cross-link.** Documented mapping from URML's `measure(payload=multispectral)` to Sentera's radiometric output streams?
4. **PHX-platform manifest.** Authoritative airframe / payload / endurance values for URML's capability manifest?
5. **Agriculture-profile co-design.** Future `spec/profiles/agriculture/` Layer-3 interest?
6. **Conformance lane.** Open to a URML conformance line on a Sentera repo README or support.sentera.com?
7. **Anything else.**

Thanks for the SenteraLLC public-Python posture and the documented MAVLink integration. URML's first ag-drone RFC benefits from the existing engineering substrate.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0094: Burro Robotics

**Post to:** https://github.com/burro-robotics/burro-sdk/issues/new

**Title:**

```
Research-collab proposal: URML (substrate-neutral robot intent) above BOSS Cloud for cross-vendor fleet orchestration
```

**Body:**

```markdown
Hi Burro Robotics team,

Posting this as a collaboration proposal to the burro-robotics maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary sits one layer above ROS 2 / PX4 / vendor cloud APIs.

URML's value proposition for Burro: a customer running mixed-vendor agriculture operations writes "send the next available Burro to picking station 5 and report when arrived" in URML's natural-language layer; URML compiles to `move_to(picking_station_5)` + `report(arrival, fleet_log)`; a `BurroAdapter` dispatches the primitives onto BOSS Cloud's documented fleet API. The same URML program retargets to an open-source-rover fleet or to a research-grade ag rover by manifest swap. The cross-vendor substrate-neutral story is the natural value proposition for a customer who does not want to lock into one vendor's stack.

The integration is BOSS-API-level (URML's substrate-Protocol sits at the intent layer above BOSS Cloud, not inside Burro's proprietary core).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0094-burro-robotics-outreach.md

This is proposal-only, part of URML's **Move #7** outreach (agriculture-robotics second wave). Eight targets in this wave. URML has sent ~90 RFCs across seven outreach moves; single-digit substantive responses to date.

## Feedback we'd value

1. **BOSS Cloud API access.** Is the BOSS API publicly documented, or available to integration partners on request?
2. **Adapter home.** URML's `reference/agriculture-runtime/burro/` (URML-side), a burro-robotics contributed example, or both?
3. **Multi-vendor fleet orchestration.** Is URML's substrate-neutral programming model interesting to Burro's product / engineering side?
4. **`burro-sdk` cross-link.** Documented README note on URML as a complementary intent layer?
5. **Authoritative manifest values.** Burro chassis dimensions, payload, sensor inventory.
6. **Agriculture-profile co-design.** Future `spec/profiles/agriculture/` Layer-3 interest?
7. **Conformance lane.** Open to a URML conformance line on a burro-robotics repo README?
8. **Anything else.**

Thanks for the public burro-robotics GitHub org and the documented BOSS Cloud API. URML's first commercial ag-cobot RFC benefits from the real engineering surface.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0095: UCLA AgriCruiser

**Post to:** https://github.com/agri-cruiser/agri-cruiser/issues/new

**Title:**

```
Research-collab proposal: URML primitive vocabulary as a teaching artifact above AgriCruiser
```

**Body:**

```markdown
Hi AgriCruiser team,

Posting this as a research-collaboration proposal to the agri-cruiser maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary sits one layer above C++ controller code.

URML's value proposition for AgriCruiser: students using AgriCruiser for over-the-row navigation experiments could write URML programs in URML's natural-language layer; URML compiles to primitives (`move_to`, `measure`, `wait_for`, `report`) that an AgriCruiser controller dispatches. The teaching value is the abstraction level above C++ control code; a pedagogical ladder from English-language intent down to substrate-specific implementation. The substrate-neutral story is exactly what coursework benefits from: programs from one ag platform port to another by manifest swap.

License-fit note: AgriCruiser is GPL-3.0; URML's `reference/` is Apache-2.0. URML's proposal here is **documented mapping + cross-citation**, not adapter code reuse. The integration lives in URML's `reference/agriculture-runtime/README.md` as a documented mapping; AgriCruiser code stays in `agri-cruiser/agri-cruiser` unmodified.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0095-ucla-agricruiser-outreach.md

This is proposal-only, part of URML's **Move #7** outreach (agriculture-robotics second wave). Eight targets in this wave. URML has sent ~90 RFCs across seven outreach moves; single-digit substantive responses to date.

## Feedback we'd value

1. **PI / lab affiliation.** Could you confirm the lab + PI behind `agri-cruiser/agri-cruiser`? UCLA agricultural-engineering or different department?
2. **License-fit posture.** AgriCruiser is GPL-3.0; URML is Apache-2.0. Cross-citation is URML's proposal; any concerns?
3. **Coursework integration.** Is AgriCruiser used in a specific UCLA (or other institution) course where URML primitive vocabulary would be a useful teaching artifact?
4. **Agriculture-profile co-design.** Future `spec/profiles/agriculture/` Layer-3 (plant / water / weed / scout) interest?
5. **Conformance lane.** Open to a URML conformance line on the `agri-cruiser/agri-cruiser` README?
6. **Anything else.**

Thanks for the USDA-funded open-source posture (NIFA grants 2024-67021-42528, 2022-67022-37021, 2021-67022-34200). URML's research-collab framing aims to complement, not interfere with, AgriCruiser's existing coursework and research.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0096: INRAE Romea

**Post to:** https://github.com/Romea/cropcraft/issues/new (or `Romea/romea-ros2-mobile-base` if maintainers prefer)

**Title:**

```
Research-collab proposal: URML (substrate-neutral robot intent) above Romea's ROS 2 ag-robotics stack
```

**Body:**

```markdown
Hi INRAE Romea team,

Posting this as a research-collaboration proposal to the Romea maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) sits one layer above ROS 2 / PX4 / vendor SDKs.

URML's value proposition for Romea: a documented mapping between URML's primitive vocabulary and Romea's ROS 2-native agriculture-robotics stack (`romea-ros2`, `romea-ros2-mobile-base`, `four_wheel_steering_tools`). URML's `move_to` primitive dispatches via Romea's published ROS 2 topics; URML's `measure` primitive abstracts crop / soil / environmental sensors as substrate-neutral observations. Cropcraft's procedural ag-sim world generator is a candidate complement for URML's hermetic conformance-test fixtures for the future `reference/agriculture-runtime/`. License alignment is clean: both Romea and URML are Apache-2.0 predominant.

Romea is the strongest EU-academic ag-robotics surface URML has surfaced. 79 public repos, ROS 2 native, Apache-2.0, active maintenance (the most recent commit on `romea-ros2-joy` was four days before this RFC drafted).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0096-inrae-romea-outreach.md

This is proposal-only, part of URML's **Move #7** outreach (agriculture-robotics second wave). Eight targets in this wave. URML has sent ~90 RFCs across seven outreach moves; single-digit substantive responses to date.

## Feedback we'd value

1. **Canonical first-class repos.** Of the 79 repos in the Romea org, which are the canonical first-class entry points for URML's substrate-neutral story?
2. **`romea_controllers` + `four_wheel_steering_tools` archive status.** Replaced by the `romea-ros2-*` family, or different reason?
3. **`cropcraft` conformance-fixture composition.** Interest in URML documenting `cropcraft` worlds as conformance-test fixtures for `reference/agriculture-runtime/`?
4. **Cross-link to other Move #7 targets.** Interest in coordinating across the ag-robotics research community URML's Move #7 reaches?
5. **Agriculture-profile co-design.** Future `spec/profiles/agriculture/` Layer-3 interest?
6. **Language fluency.** English or French for substantive technical discussion?
7. **Conformance lane.** Open to a URML conformance line on the `cropcraft` or `romea-ros2-mobile-base` README?
8. **Anything else.**

Thanks for the Romea org's ROS 2 + Apache-2.0 posture. URML's strongest EU-academic Move #7 engagement benefits from the institutional research surface INRAE maintains.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0097: EarthSense / TerraSentia

**Post to:** https://github.com/TerraSentia/livox_ros_driver2/issues/new (the most-recently-updated repo, last commit 2026-05-06)

**Title:**

```
Research-collab proposal: URML measure primitive as substrate-neutral intent above TerraSentia phenotyping
```

**Body:**

```markdown
Hi TerraSentia / EarthSense team,

Posting this as a research-collaboration proposal to the TerraSentia maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) sits one layer above ROS 2 / PX4 / vendor SDKs.

URML's value proposition for TerraSentia: a URML program describing "scout the maize trial plot and record stand-count + plant-height every 10cm" decomposes into `move_to(...)` + `measure(stand_count, ...)` + `wait_for(distance, 10cm)`. The TerraSentia ROS drivers (`livox_ros_driver2`, `FAST-LIO-SAM`, `terra-lidar-imu-init`) consume those primitives at the substrate layer. A URML phenotyping program written for TerraSentia retargets to a future agricultural drone or to a four-wheel-steering platform by manifest swap. Cross-trial phenotyping research benefits from substrate-neutrality.

License-fit note: `terra-lidar-imu-init` is GPL-2.0; other repos do not surface a license. URML's proposal here is **documented cross-citation**, not adapter code in URML's `reference/`. Adapter code follows license clarity.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0097-earthsense-terrasentia-outreach.md

This is proposal-only, part of URML's **Move #7** outreach (agriculture-robotics second wave). Eight targets in this wave. URML has sent ~90 RFCs across seven outreach moves; single-digit substantive responses to date.

## Feedback we'd value

1. **License posture.** Could you confirm the license on `livox_ros_driver2`, `FAST-LIO-SAM`, `ES-ESC-FW`, `ES-ESC-HW`?
2. **Engagement surface.** Which surface is the right one for substantive URML cross-citation: a specific repo's Issues, an academic UIUC contact channel, or the EarthSense Inc. developer-relations team?
3. **Nature Communications 2025 datasets.** Are the trial datasets open or proprietary?
4. **Cross-platform retargetability.** Is there interest in documenting URML's substrate-neutral phenotyping path across TerraSentia + ag-drones + ag-rovers?
5. **Agriculture-profile co-design.** Future `spec/profiles/agriculture/` Layer-3 interest?
6. **Conformance lane.** Open to a URML conformance line on the `livox_ros_driver2` README or earthsense.co?
7. **Anything else.**

Thanks for the TerraSentia public ROS work and the published 2025 validation at scale. URML's research-collab framing aims to complement the existing phenotyping pipeline.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0098: Cornell AgXRP

**Post to:** Contact form at https://www.experiential.bot/agxrp (off-GitHub courtesy email; no verified GitHub repo or org).

**Title:**

```
URML research-collab proposal for AgXRP; substrate-neutral robot intent for STEM agriculture
```

**Body:**

```markdown
Hi Jonathan,

Sending this off-GitHub since URML's verification on 2026-05-26 did not surface a public GitHub repo or org for AgXRP (the project page mentions "open-source software library" without a specific URL). I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

URML fills a specific niche that maps closely to AgXRP's audience: **affordable open-source agriculture-robotics platforms for K-12 / 4-H / community-college STEM**. A student writes "drive the robot to the soil plot and measure soil moisture" in URML's natural-language layer; URML compiles to `move_to(...)` + `measure(soil_moisture, ...)`; an AgXRP-side controller dispatches the primitives. The pedagogical ladder URML offers; from natural-language English to validated robot programs; is the strongest match for the AgXRP audience. URML's `reference/edu-runtime/` already ships several educational adapters; an `AgXRPAdapter` would be a natural fifth, if the AgXRP maintainers want a URML-side home for it.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0098-cornell-agxrp-outreach.md

This is proposal-only, part of URML's **Move #7** outreach (agriculture-robotics second wave). Eight targets in this wave. URML has sent ~90 RFCs across seven outreach moves; single-digit substantive responses to date. If the substantive surface is the Cornell academic side, or the University of Idaho partnership, or 4-H, URML's outreach pivots accordingly.

## Feedback we'd value

1. **Public GitHub URL.** Is there a GitHub repository or org for the AgXRP open-source software library?
2. **License posture.** Specific license on the software library + 3D-printable files?
3. **Curriculum + software release timeline.** When is the curriculum (marked "Coming Soon") expected to publish?
4. **Coursework integration.** Is URML primitive vocabulary a candidate teaching artifact for the AgXRP curriculum or Cornell / University of Idaho coursework?
5. **AgXRPAdapter home.** If URML ships an adapter, `reference/edu-runtime/` (URML-side), or a contributed example in your own repo when published?
6. **Cross-link to K-12 + 4-H audience.** Interest in coordinating across the broader ag-STEM educational ecosystem?
7. **Anything else.**

Thanks for the AgXRP project's accessible-price-point ag-robotics work for the K-12 / 4-H / community-college audience. URML's research-collab framing aims to complement the curriculum direction you're publishing.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0099: Wageningen Field Robot Event 2026

**Post to:** FRE 2026 Discord (the community channel linked from [`fieldrobotevent.eu`](https://fieldrobotevent.eu); no verified GitHub Issue surface for FRE itself).

**Title:**

```
URML (substrate-neutral robot intent); community introduction for FRE 2026 participants
```

**Body:**

```markdown
Hi FRE 2026 community,

Joining the FRE Discord and posting this introduction. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`, plus profile extensions for educational / research) sits one layer above ROS 2 / PX4 / vendor SDKs.

URML's relevance to FRE 2026: the competition draws teams from universities across Europe, each bringing different robot platforms to the same maize/sorghum row-following + scouting tasks. URML's substrate-neutral primitive vocabulary is a candidate teaching artifact for the participating teams; a URML program written against one team's robot retargets to another's by manifest swap. The competition's heterogeneity is exactly URML's value proposition.

For teams that have not yet built deep ROS expertise, URML's natural-language layer offers a pedagogical ladder: students begin by writing English-language URML programs and progressively descend into ROS as needed. URML's existing `examples/` directory provides starting code; participating labs own the pedagogical integration.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0099-wageningen-field-robot-event-outreach.md

This is proposal-only, part of URML's **Move #7** outreach (agriculture-robotics second wave). Eight targets in this wave. URML has sent ~90 RFCs across seven outreach moves; single-digit substantive responses to date.

## Feedback we'd value

1. **Maintainer of record.** Who is the lead PI / committee chair for FRE 2026?
2. **Simulation stack.** What ROS / Gazebo / other simulation environment does FRE 2026 expect entrants to use?
3. **ReFiBot platform.** Is the Arduino-based open-source FRE platform still part of the 2026 edition?
4. **Public mailing list or forum.** Is Discord the primary community channel, or is there a separate technical mailing list?
5. **URML primitive-vocabulary integration.** Is there interest in URML primitive vocabulary as a candidate teaching artifact for FRE entrants?
6. **Conformance lane.** Open to a URML conformance line in FRE 2026's published technical materials or on `fieldrobotevent.eu`?
7. **Anything else.**

Thanks for the FRE community's annual European ag-robotics competition. URML's research-collab framing aims to support entrants who want to integrate URML before Bernburg in June.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## Operational notes

- **Sequencing.** Recommended first post: **RFC-0092 Twisted Fields / Acorn**. Clean Apache-2.0 license, active US 501(c)(3) maintainer, smallest blast radius for the first agriculture-wave conversation. Then RFC-0093 (Sentera) and RFC-0094 (Burro) in either order. The five Tier B (0095-0099) can ship in parallel after the Tier A engagement opens.
- **Cadence.** Agriculture-vendor cadence varies. Small DIY orgs are slower than commercial outfits; academic ag labs run on the US / EU semester calendar (summer break May-August affects EU + US lab cadence). Polite follow-up at +30d is reasonable for academic targets; +14d for commercial.
- **Channel pivot.** RFC-0098 (AgXRP) opens off-GitHub by courtesy email. If the maintainer responds with a public GitHub URL, URML pivots to standard Issue-thread engagement. RFC-0099 (FRE) opens on Discord. If the organising committee prefers a different surface (email, separate forum, GitHub org), URML's outreach pivots accordingly.
- **Confidentiality.** Per the outreach-confidentiality rule, no other engaged URML maintainer or org is named in any post body above. URML's own shipped reference runtimes and aggregate outreach counts are fine to cite; specific responder identities are not.

---

## RFC-0099 addendum (2026-05-30): surface recovered, posted to GitHub

RFC-0099 was deferred at posting time 2026-05-26 because the only documented FRE community channel was Discord (declined). A 2026-05-30 re-check found `github.com/FieldRobotEvent` **does** exist, with Issues enabled on `competition_environment`, `virtual_maize_field`, and `example_ws`. The May surface check missed it. Posted to [competition_environment#25](https://github.com/FieldRobotEvent/competition_environment/issues/25), with the Discord acknowledged. Body below uses the current authoring-disclosure convention (the body above predates it).

**Posted to:** https://github.com/FieldRobotEvent/competition_environment/issues/25

**Title:** URML (substrate-neutral robot intent language) — research-collab RFC for FRE 2026 entrants

**Body:**

Hi Field Robot Event organisers and maintainers,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. It lets someone write what a robot should do as a sentence and compiles it into a validated, runnable program above whatever runtime runs below (ROS 2, a microcontroller, a vendor SDK). I am reaching out because the Field Robot Event gathers exactly the audience URML is built for: students authoring robot programs against heterogeneous ag-robotics platforms, where one program retargeting to another team's robot by a manifest swap is the whole point.

This is **proposal-only**, research-collab framing — no spec change, nothing to merge. The offer is to support FRE entrants who want to try URML's primitive vocabulary as a teaching layer above their ROS / control code. Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0099-wageningen-field-robot-event-outreach.md

I originally found only the Discord as a community channel and held off, since URML's outreach prefers durable, public surfaces. Finding this GitHub org is why I am posting here instead. If an Issue is the wrong venue and you would rather take this on Discord or by email, just say so.

A few questions for the organising committee:

1. **Maintainer of record.** Who is the lead PI / committee chair for FRE 2026, so the conversation has a contact?
2. **Simulation stack.** What ROS / Gazebo / other simulation environment does FRE 2026 expect entrants to use? (`virtual_maize_field` looks like the answer — confirming.)
3. **ReFiBot platform.** Is the Arduino-based open-source FRE platform still part of the 2026 edition?
4. **URML primitive-vocabulary integration.** Is there interest in URML's primitive vocabulary as a candidate teaching artifact for entrants?
5. **Conformance lane.** Open to a URML conformance line in FRE 2026's published technical materials once a mapping stabilizes? (Self-reported, no continuous obligation.)
6. **Anything else.**

Happy to scope down or shelve as fits. Thanks for running the annual proving ground for European ag-robotics — see you near Bernburg in June, if only in spirit.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
