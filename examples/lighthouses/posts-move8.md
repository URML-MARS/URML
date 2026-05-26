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

# Move #8 post bodies

Copy-paste-ready Issue / Discussion / Contact-form bodies for the Move #8 home-assistance outreach. Eight RFCs total: 5 Tier A vendor-style (iRobot Roomba, Husqvarna Automower, Bear Robotics, Maytronics Dolphin, ROBOTIS Dynamixel) and 3 Tier B research-collab + community (Luxonis OAK-D, Home Assistant, OpenVoiceOS).

Ledger state lives in [`outreach-move8.yaml`](outreach-move8.yaml). After posting, set `posted_url`, update `last_touch`, and update `next_action`.

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts (`reference/marine-runtime/`, `reference/edu-runtime/`, `reference/cobot-runtime/`, RFCs in `docs/rfcs/`) are fine to cite. Aggregate counts ("~100 RFCs sent across eight outreach moves; single-digit substantive responses") are fine. Naming the specific orgs that responded is not.

---

## RFC-0100: iRobot / Roomba

**Post to:** https://github.com/koalazak/dorita980/issues/new

**Title:**

```
Research-collab proposal: URML (substrate-neutral robot intent) for the Roomba LAN-control surface
```

**Body:**

```markdown
Hi Pablo + dorita980 community,

Posting this as a collaboration proposal to the dorita980 maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`, plus profile extensions for home / educational / research) sits one layer above ROS 2 / PX4 / vendor SDKs / LAN-control surfaces.

URML's value proposition for Roomba via dorita980: a homeowner writes "vacuum the kitchen, then dock" in URML's natural-language layer; URML compiles to `move_to(kitchen)` + `wait_for(cleaning_complete)` + `report(docked)`; a `RoombaAdapter` dispatches the primitives onto the local Roomba via dorita980's WebSocket+TLS surface. URML's substrate-neutral story means the same English-language program retargets to a different cleaning robot (or to an outdoor lawn robot, or to a pool cleaner) by manifest swap. iRobot itself does not publish a developer SDK; dorita980 is the documented engagement surface for substrate-neutral integrations.

URML proposes a new `reference/home-runtime/` package with `RoombaAdapter` as the first adapter in it, composing above dorita980 + ha-rest980-roomba without requiring upstream changes.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0100-irobot-roomba-outreach.md

This is proposal-only, part of URML's **Move #8** outreach (home-assistance robotics + parts). Eight targets in this wave (5 vendor-style + 3 research-collab + community), spanning consumer cleaning + outdoor + pool + servo + perception + Home Assistant + voice. URML has sent ~100 RFCs across eight outreach moves to date; single-digit substantive responses (the outreach is real, the language is early).

## Feedback we'd value

1. **Adapter home.** URML's `reference/home-runtime/src/home_runtime/irobot/` (URML-side), a dorita980 contributed example, or both?
2. **Authoritative manifest values.** Roomba model-specific mass, dimensions, sensor inventory (J7 / J9 / i7 etc.).
3. **Region-based mobility encoding.** Is `region_based` the right manifest term, or should URML extend its schema to model Roomba's "Spaces" semantics directly?
4. **Home-profile co-design.** Future `spec/profiles/home/` Layer-3 vocabulary (clean / vacuum / mop / scout / monitor) interest?
5. **iRobot developer-relations channel.** Known contact at iRobot to forward this RFC to as a courtesy, or is engagement with the maintainer community the canonical path?
6. **Conformance lane.** Open to a URML conformance line on the dorita980 README?
7. **Anything else.**

Thanks for the dorita980 project and the years of community maintenance keeping Roomba accessible to substrate-neutral integrators. URML's home-assistance story benefits from clean MIT-licensed substrate work like this.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0101: Husqvarna Automower

**Post to:** https://github.com/Thomas55555/aioautomower/issues/new

**Title:**

```
Research-collab proposal: URML (substrate-neutral robot intent) for Husqvarna Automower via Automower Connect
```

**Body:**

```markdown
Hi Thomas + aioautomower community,

Posting this as a collaboration proposal to the aioautomower maintainer. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary sits one layer above ROS 2 / PX4 / vendor APIs.

URML's value proposition for Husqvarna Automower: a homeowner writes "mow the back lawn between 10 AM and 2 PM, but skip if it rains" in URML's natural-language layer; URML compiles to `move_to(back_lawn)` + `wait_for(time, 10:00)` + `wait_for(weather, not_raining)` + `report(mowing_complete)`; a `HusqvarnaAutomowerAdapter` dispatches via the Automower Connect API. Husqvarna's first-class developer portal (OpenAPI 3.0 + OAuth 2.0) plus your aioautomower async Python wrapper is the cleanest engagement surface in URML's Move #8 wave; URML's adapter composes above the existing async Python without re-implementing OAuth or REST.

URML proposes the `HusqvarnaAutomowerAdapter` in a new `reference/home-runtime/` package (sibling to the indoor-floor adapter for Roomba and the aquatic adapter for pool cleaners). Same English-language URML program retargets across indoor + outdoor + pool by manifest swap.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0101-husqvarna-automower-outreach.md

This is proposal-only, part of URML's **Move #8** outreach (home-assistance robotics + parts). Eight targets in this wave. URML has sent ~100 RFCs across eight outreach moves to date; single-digit substantive responses (the outreach is real, the language is early).

## Feedback we'd value

1. **Adapter home.** URML's `reference/home-runtime/src/home_runtime/husqvarna/` (URML-side), an aioautomower contributed example, both?
2. **Authoritative manifest values.** Model-specific mass, dimensions, sensor inventory across the Automower line (315X, 430X, 535 AWD, etc.).
3. **Zone-based mobility encoding.** Is `zone_based` the right manifest term for URML's mobility schema, or should URML extend the schema to model Automower's geofence semantics directly?
4. **Husqvarna developer-relations channel.** Known contact at Husqvarna for a courtesy notification, or is engagement with aioautomower + Home Assistant community the canonical path?
5. **Home-profile co-design.** Future `spec/profiles/home/` Layer-3 vocabulary (mow / vacuum / clean / scout) interest?
6. **Conformance lane.** Open to a URML conformance line on the aioautomower README?
7. **Anything else.**

Thanks for the aioautomower project; it's the cleanest first-class-vendor-API substrate surface URML's Move #8 reaches.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0102: Bear Robotics (Servi)

**Channel:** Bear Cloud API developer portal Contact form at https://cloud.api.bearrobotics.ai (no customer-facing GitHub Issue surface on the bearrobotics org; off-GitHub courtesy)

**Subject line:**

```
URML (substrate-neutral robot intent); research-collab proposal for Servi fleet API
```

**Body:**

```markdown
Hi Bear Robotics developer-relations team,

Sending this via the Bear Cloud developer portal since the bearrobotics GitHub org doesn't surface a customer-facing product repo with Issues enabled (the org has 25 repos, all infrastructure forks). I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent.

URML's value proposition for Bear / Servi: a customer running a mixed-vendor robot fleet in a senior-living facility or hospitality venue writes "deliver dish to table 12 and return to staging" in URML's natural-language layer; URML compiles to `move_to(table_12)` + `release(dish)` + `move_to(staging)` + `report(complete)`; a `BearAdapter` dispatches via the Bear Cloud API's documented gRPC / REST endpoints. The cross-vendor substrate-neutral story is the natural value proposition for a customer who runs Servi alongside other delivery robots and wants one programming model.

The integration is at the API level. URML's substrate-Protocol sits at the intent layer above Bear Cloud, not inside Servi's proprietary core. URML's Move #8 home-assistance framing includes Servi specifically for the senior-living + assisted-living adjacency (home-assistance continuum).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0102-bear-robotics-servi-outreach.md

This is proposal-only, part of URML's **Move #8** outreach (home-assistance robotics + parts). Eight targets in this wave. URML has sent ~100 RFCs across eight outreach moves to date; single-digit substantive responses.

## Feedback we'd value

1. **API access posture.** Is the Bear Cloud API available to integration partners on request, or does substantive integration require a commercial partnership?
2. **Engagement surface.** Is the developer-portal Contact form the right channel, a specific dev-relations email, or a different surface?
3. **Adapter home.** If URML ships a `BearAdapter`, would `reference/home-runtime/` (URML-side) be appropriate, or would Bear prefer a contributed example in a Bear-operated repo?
4. **Senior-living + care-home framing.** Is URML's home-assistance framing for Servi (as a care-home delivery cobot) consistent with Bear's product positioning?
5. **Multi-vendor fleet orchestration.** Is URML's substrate-neutral programming model interesting to Bear's product / engineering side?
6. **Conformance lane.** Open to a URML conformance line in Bear's developer portal documentation?
7. **Anything else.**

Thanks for the public Bear Cloud documentation and the documented gRPC + REST APIs. URML's hospitality + senior-living engagement benefits from the engineering work behind those surfaces.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0103: Maytronics Dolphin

**Post to:** https://github.com/sh00t2kill/dolphin-robot/issues/new

**Title:**

```
Research-collab proposal: URML (substrate-neutral robot intent) for Maytronics Dolphin via dolphin-robot
```

**Body:**

```markdown
Hi sh00t2kill + dolphin-robot community,

Posting this as a collaboration proposal to the dolphin-robot maintainer. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary sits one layer above ROS 2 / PX4 / vendor APIs / Home Assistant integrations.

URML's value proposition for Maytronics Dolphin via dolphin-robot: a homeowner writes "clean the pool floor and walls, then idle" in URML's natural-language layer; URML compiles to `move_to(pool_floor)` + `move_to(pool_walls)` + `wait_for(cycle_complete)` + `report(idle)`; a `MaytronicsDolphinAdapter` dispatches via the dolphin-robot integration's WiFi-API surface. The substrate-neutral story is exactly URML's value proposition: the same URML program retargets across indoor floor (Roomba) + outdoor lawn (Automower) + aquatic pool (Dolphin) by manifest swap. Pool cleaning broadens URML's substrate-neutral claim across operating environments.

URML proposes the `MaytronicsDolphinAdapter` in a new `reference/home-runtime/` package as the third adapter (after RoombaAdapter and HusqvarnaAutomowerAdapter).

License note: GitHub's API does not surface an SPDX license identifier on the dolphin-robot repo at verification time. URML's RFC asks the maintainer to clarify the license posture before any adapter code reuse.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0103-maytronics-dolphin-outreach.md

This is proposal-only, part of URML's **Move #8** outreach (home-assistance robotics + parts). Eight targets in this wave. URML has sent ~100 RFCs across eight outreach moves to date; single-digit substantive responses.

## Feedback we'd value

1. **License posture.** Could you clarify the license on the dolphin-robot integration? GitHub's API did not surface an SPDX identifier at verification time.
2. **Adapter home.** URML repo (`reference/home-runtime/src/home_runtime/maytronics/`), `dolphin-robot` contributed example, both?
3. **Authoritative manifest values.** Model-specific mass, dimensions, sensor inventory (M700 / M600 / M400 / Premier).
4. **Region-based mobility encoding.** Is `region_based` the right manifest term, or should URML extend its schema to model the Dolphin's floor / walls / waterline / steps semantics directly?
5. **Maytronics developer-relations channel.** Known contact for a courtesy notification, or is the community surface the canonical engagement path?
6. **Home-profile co-design.** Future `spec/profiles/home/` Layer-3 vocabulary interest?
7. **Conformance lane.** Open to a URML conformance line on the dolphin-robot README?
8. **Anything else.**

Thanks for the dolphin-robot project; pool cleaning is the smallest-installed-base niche in URML's Move #8 wave but the substrate-neutral story benefits from explicit aquatic-subsystem coverage.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0104: ROBOTIS Dynamixel

**Post to:** https://github.com/ROBOTIS-GIT/DynamixelSDK/issues/new

**Title:**

```
Research-collab proposal: URML cross-citation of Dynamixel as canonical actuator substrate for home-scale robotics
```

**Body:**

```markdown
Hi ROBOTIS team,

Posting this as a collaboration proposal to the ROBOTIS-GIT maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) sits one layer above ROS 2 / PX4 / vendor SDKs.

URML's value proposition for ROBOTIS: a documented cross-citation between URML's primitive vocabulary and Dynamixel as the canonical actuator substrate for affordable home / educational / quadruped / arm robotics. URML's `move_to(joint_pose)` decomposes to per-servo position commands dispatched via the DynamixelSDK; the composition is well-defined (URML at the intent layer, Dynamixel at the actuator layer, ROS 2 as the canonical intermediate substrate). URML's existing `reference/edu-runtime/` already implicitly depends on Dynamixel for several educational platforms; surfacing the relationship explicitly broadens URML's home-scale + educational + research story.

License alignment is clean (both Apache-2.0). The proposal is documented cross-citation + a hermetic Dynamixel-conformance test fixture in URML's `conformance/` suite. NOT a stand-alone `DynamixelAdapter` (Dynamixel is actuator-substrate, not platform-substrate; URML's per-platform adapters compose with Dynamixel internally).

ROBOTIS Dynamixel is the first servo-vendor RFC in URML's outreach landscape. URML's prior Move #1 touched industrial-component vendors (LiDAR, safety scanners, pneumatics, grippers); ROBOTIS Dynamixel is the home-scale / educational / research counterpart.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0104-robotis-dynamixel-outreach.md

This is proposal-only, part of URML's **Move #8** outreach (home-assistance robotics + parts). Eight targets in this wave. URML has sent ~100 RFCs across eight outreach moves to date; single-digit substantive responses.

## Feedback we'd value

1. **Cross-citation appetite.** Is ROBOTIS open to a documented cross-citation in URML's `reference/edu-runtime/README.md` and conformance suite, naming Dynamixel as the canonical actuator substrate for affordable humanoid / arm / quadruped robotics?
2. **Conformance lane.** Open to a URML conformance line on `DynamixelSDK` or `dynamixel_hardware_interface` README?
3. **Adapter-layering question.** Does ROBOTIS prefer URML's adapters to invoke Dynamixel via the SDK directly, or via the ROS 2 `dynamixel_hardware_interface`?
4. **Educational-profile co-design.** URML's RFC-0011 educational profile would benefit from a ROBOTIS perspective on the right Layer-3 vocabulary for Dynamixel-driven platforms.
5. **OpenManipulator + TurtleBot3 specific manifests.** URML's manifest schema would benefit from authoritative mass / DOF / payload values for ROBOTIS's flagship open platforms.
6. **Korean-language follow-up.** Is English sufficient, or would Korean follow-up be preferred?
7. **Anything else.**

Thanks for the ROBOTIS-GIT open-source posture and the Apache-2.0 license across DynamixelSDK + dynamixel_hardware_interface + OpenManipulator + TurtleBot3. URML's home-scale + educational story benefits directly from the substrate work ROBOTIS has done.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0105: Luxonis OAK-D / DepthAI

**Post to:** https://github.com/luxonis/depthai-python/discussions/new (Discussions surface; Luxonis has Discussions enabled and the research-collab framing fits better there than Issues)

**Title:**

```
Research-collab proposal: URML cross-citation of OAK-D / DepthAI as candidate perception substrate
```

**Body:**

```markdown
Hi Luxonis team,

Posting this on Discussions (rather than Issues) since the framing is research-collab + composition rather than a bug or feature request. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary sits one layer above ROS 2 / PX4 / vendor SDKs.

URML's value proposition for Luxonis: a documented cross-citation between URML's `measure` + `wait_for` primitives and DepthAI's perception streams. URML's `measure(depth)` + `measure(orientation)` + `wait_for(object_detected)` compose directly with OAK-D streams (stereo depth + IMU + on-device AI inference). The substrate-neutral story: a URML program written against OAK-D retargets to a different perception module by manifest swap. URML's value-add is the intent-validation + cross-substrate layer above DepthAI.

OAK-D is the de facto affordable 3D-perception module for home / educational / research robotics. The audience overlaps with URML's educational + research + home-assistance waves directly.

License alignment: MIT on depthai-ros + depthai-python composes cleanly with URML's Apache-2.0 `reference/`. The proposal is documented cross-citation + a hermetic DepthAI-conformance test fixture in URML's `conformance/` suite. NOT a stand-alone Luxonis adapter (perception modules sit inside platform adapters, not alongside them).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0105-luxonis-oak-d-outreach.md

This is proposal-only, part of URML's **Move #8** outreach (home-assistance robotics + parts). Eight targets in this wave. URML has sent ~100 RFCs across eight outreach moves to date; single-digit substantive responses.

## Feedback we'd value

1. **Cross-citation appetite.** Is Luxonis open to a documented cross-citation in URML's `reference/` runtimes + conformance suite, naming OAK-D as a candidate perception substrate?
2. **Primary-variant manifest.** Which OAK-D variant (OAK-D S2, OAK-D Pro, OAK-4) is the right primary target for URML's documented mapping?
3. **DepthAI v3 trajectory.** Is DepthAI v3 the right substrate target, or should URML's cross-citation target v2 for stability?
4. **Conformance lane.** Open to a URML conformance line on depthai-ros or depthai-python README?
5. **Educational + research profile co-design.** URML's RFC-0011 / RFC-0012 raised the broader profile-design question; Luxonis's perspective from the affordable-perception side would inform the future Spec RFC.
6. **GitHub Discussions vs Issues.** I posted on Discussions; if Luxonis prefers Issues for this kind of RFC, happy to mirror.
7. **Anything else.**

Thanks for the open-source posture across depthai-python + depthai-ros + oak-hardware. URML's substrate-neutral story is much cleaner with an active, MIT-licensed perception substrate like OAK-D.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0106: Home Assistant

**Post to:** https://github.com/home-assistant/core/issues/new

**Title:**

```
Research-collab proposal: URML (substrate-neutral robot intent) as a compilation target for Home Assistant automations
```

**Body:**

```markdown
Hi Home Assistant team,

Posting this as a research-collab proposal to the home-assistant/core maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`, plus profile extensions for home / educational / research) sits one layer above ROS 2 / PX4 / vendor SDKs / Home Assistant entities.

URML's value proposition for Home Assistant: URML primitives compile into Home Assistant automation YAML, with HA entities as the substrate-neutral execution surface. A user writes "vacuum the kitchen at 7 AM unless someone is home" in URML; URML compiles to an HA automation calling `vacuum.start` on `vacuum.kitchen_roomba` with a person-tracker gate. The composition: URML at the intent + validation layer, HA at the orchestration + execution layer. URML composes with HA, not against it.

Home Assistant is the strategic anchor for URML's Move #8 home-assistance wave specifically because every vendor target in the wave (vacuum, lawn mower, pool cleaner, servo-driven home platform) already lives as a first-class HA integration. URML's value-add is the natural-language layer + formal verification + cross-substrate retargetability above the HA entity model.

A candidate `urml` HACS integration prototype would expose URML compilation as a HA service; documentation lives in URML's `reference/home-runtime/README.md` mapping URML primitives to HA entity actions.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0106-home-assistant-outreach.md

This is proposal-only, part of URML's **Move #8** outreach (home-assistance robotics + parts). Eight targets in this wave. URML has sent ~100 RFCs across eight outreach moves to date; single-digit substantive responses. The engagement payload here is intentionally light given the HA maintainer-community scale.

## Feedback we'd value

1. **Engagement-channel preference.** Is `home-assistant/core` Issues the right surface, or would HA prefer GitHub Discussions / `architecture` / the community forum?
2. **`urml` integration prototype.** Would HA welcome a community-maintained `urml` HACS integration, or would the maintainer community prefer URML's compilation surface to live entirely externally?
3. **Voice-stack composition.** How does URML's natural-language layer compose with HA's existing `assist_pipeline` + OHF-Voice / OpenVoiceOS without overlap?
4. **Blueprint format.** Could URML compile to HA Blueprint YAML as well as / instead of automation YAML?
5. **Formal-verification angle.** URML's static-verification path could check user-automation safety against entity manifests. Is there appetite from the HA community for that surface?
6. **Cross-vendor entity-model normalisation.** Are there gaps URML's substrate-neutral story could surface back to the HA maintainer community?
7. **Conformance lane.** Open to a URML conformance line on the home-assistant/core README or in HA's developer docs?
8. **Anything else.**

Thanks for the home-assistant/core community and the Open Home Foundation work. URML's home-assistance Move #8 wave is genuinely anchored in HA; every other Move #8 vendor already integrates with HA, and URML's value is most coherent when paired with HA as the orchestration layer.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0107: OpenVoiceOS

**Post to:** https://github.com/OpenVoiceOS/ovos-core/issues/new

**Title:**

```
Research-collab proposal: URML primitive vocabulary as substrate-neutral intent target for OVOS skills
```

**Body:**

```markdown
Hi OpenVoiceOS team,

Posting this as a research-collab proposal to the OVOS maintainers. I'm Ido Yahalomi, maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. URML's Layer-2 primitive vocabulary sits one layer above ROS 2 / PX4 / vendor SDKs.

URML's value proposition for OVOS: substrate-neutral intent target for voice skills addressing home-robot tasks. A user says "vacuum the kitchen and then dock"; OVOS's intent layer maps the utterance to a URML primitive sequence; URML compiles + validates + dispatches to whichever home-robot substrate is configured (Roomba / open-source vacuum / future home-runtime adapter). The composition direction is voice → OVOS intent → URML primitive → substrate. URML at the intent-validation + cross-substrate layer above OVOS's intent + dialogue layer.

A candidate `ovos-urml-skill` prototype (Apache-2.0, independently-maintained) would map OVOS intents addressing home-robot tasks into URML primitive sequences. Documentation lives in URML's `reference/home-runtime/README.md` mapping OVOS intent classes to URML primitive emission.

License alignment is clean (both Apache-2.0). URML's RFC-0021 on-device LLM bridge is the closest URML-side architecture to OVOS's local-first voice-stack target; both are on-device-first.

This RFC pivoted to OVOS at verification time: the original Move #8 plan named rhasspy3, but rhasspy3 was archived shortly before this RFC drafted. OVOS is the active independent voice-stack trajectory.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0107-openvoiceos-outreach.md

This is proposal-only, part of URML's **Move #8** outreach (home-assistance robotics + parts). Eight targets in this wave (closes the wave). URML has sent ~100 RFCs across eight outreach moves to date; single-digit substantive responses.

## Feedback we'd value

1. **Composition appetite.** Is OVOS open to a documented composition between OVOS intents and URML primitives, with a candidate `ovos-urml-skill` prototype as an independently-maintained skill?
2. **Skill format alignment.** Which OVOS skill API version is the right composition target?
3. **Cross-link with HA's voice stack.** Does OVOS's relationship with HA's `assist_pipeline` + OHF-Voice align with URML's "compose with both" framing, or does OVOS prefer a clearer separation?
4. **On-device LLM bridge composition.** URML's RFC-0021 on-device LLM bridge is the closest URML-side architecture to OVOS's local-first target. Interest in exploring shared infrastructure?
5. **Skill ecosystem governance.** How does OVOS govern third-party skills (review, signing, conformance)? URML's substrate-conformance discipline may inform that conversation.
6. **Conformance lane.** Open to a URML conformance line on ovos-core README or the OpenVoiceOS website?
7. **Anything else.**

Thanks for the OVOS post-Mycroft community trajectory and the on-device-first stewardship. URML's home-assistance Move #8 wave closes with OVOS as the independent voice-stack engagement; distinct from the HA-umbrella voice stack covered by the parallel HA engagement.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## Operational notes

- **Sequencing.** Recommended first post: **RFC-0101 Husqvarna Automower** (cleanest first-class-vendor-API surface in the wave; official OpenAPI 3.0 + community Python wrapper; lowest engagement friction). Then RFC-0100 (iRobot Roomba) and RFC-0104 (ROBOTIS Dynamixel). The remaining five can ship in parallel.
- **Cadence.** Community-maintainer cadence varies (dorita980, aioautomower, dolphin-robot are single-maintainer projects; HA + OVOS run on a foundation cadence). Polite follow-up at +14d for vendor APIs, +30d for community projects.
- **Channel pivot.** RFC-0102 (Bear Robotics) is off-GitHub by design (bearrobotics org has no customer-facing product surface). If Bear redirects to a private GitHub Issue surface or a dev-relations email, URML pivots accordingly. RFC-0105 (Luxonis) is posted on Discussions; if Luxonis prefers Issues, URML mirrors.
- **Confidentiality.** Per the outreach-confidentiality rule, no other engaged URML maintainer or org is named in any post body above. URML's own shipped reference runtimes (`reference/marine-runtime/`, `reference/edu-runtime/`, `reference/cobot-runtime/`) and aggregate outreach counts ("~100 RFCs across eight moves") are fine to cite; specific responder identities are not.
