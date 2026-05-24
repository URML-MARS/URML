---
rfc: 0067
title: FarmBot integration, request for comment from FarmBot maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-24
updated: 2026-05-24
supersedes: —
superseded-by: —
---

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

# RFC-0067: FarmBot integration, request for comment from FarmBot maintainers

## Summary

URML does not yet ship a FarmBot integration. This RFC proposes a `FarmBotAdapter` under a new `reference/agriculture-runtime/` (or as a sub-package under the existing mobile-runtime tree) targeting FarmBot's [public REST API](https://developer.farm.bot/docs/api-docs) and the `farmbot` GitHub org's open-source Cartesian gantry stack. The adapter routes URML Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) onto FarmBot's sequence / regimen / coordinate-target vocabulary, treating each FarmBot tool (seeder, watering nozzle, weeder, soil sensor) as a URML-named effector. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the FarmBot maintainers.

This is the third Move #4 RFC and **URML's first outreach into the agricultural vertical**. Moves #1, #2, and #3 never touched agriculture. FarmBot is the open-source flagship for small-plot autonomous farming, with public REST API, MQTT pub/sub, and an existing abstraction layer (sequences, regimens, peripherals) that maps almost one-to-one onto URML's primitive vocabulary.

## Motivation

The intent vocabulary URML proposes for agriculture lands more naturally on FarmBot than on any other agricultural target. Closed agricultural vendors (Naïo Technologies, Carbon Robotics) sell hardware-as-service with no public API; large equipment vendors (John Deere AutoTrac, AGCO Fendt) offer enterprise integrations behind sales engagements. FarmBot is the one open-source small-plot farming robot with a Python-friendly developer surface and a community oriented toward customisation.

Three things make this RFC concrete rather than aspirational. First, `FarmBot/Farmbot-Web-App` (967 stars, MIT-licensed, Issues enabled with 38 open) ships a documented REST API and an MQTT pub/sub interface; the `farmbot` GitHub org also hosts the Arduino firmware (`FarmBot-Arduino-Firmware`) and the FarmBot OS (`farmbot_os`). Second, FarmBot's domain vocabulary (sequences = ordered command lists; regimens = scheduled sequences; peripherals = controllable outputs; tools = mounted effectors) is itself a robotics-intent abstraction that URML can compile down to. Third, the audience overlap is exact: FarmBot users are makers, educators, and small-farm operators who would benefit from URML's English-to-program path more than any URML target so far. A sentence like "plant a row of lettuce two centimeters apart along the back bed" is the canonical FarmBot use case.

FarmBot's posture is fully open-source: MIT license on the web app, open hardware files, English-first community, public Forum at `forum.farmbot.org`, US-based (Berkeley). URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation. FarmBot does not compete with URML for the substrate-neutral vocabulary role. FarmBot is the hardware plus the domain-specific abstraction. URML is the spec the program above FarmBot's abstraction can target, and the path that lets a FarmBot sequence retarget to a future agricultural cobot, drone-mounted sprayer, or research-grade gantry without source changes.

## Detailed design

URML's existing artifacts that feed into a FarmBot adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- A future `spec/profiles/agriculture/` profile, raised as an open question for the manifesto-stretch agricultural vertical noted in `MANIFESTO.md`. This RFC does **not** propose the profile; that is a separate spec RFC. The FarmBot adapter sits under the existing educational and research profiles until the agricultural profile lands.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference. The FarmBot use case ("plant a row of lettuce") leans on this heavily.
- A new `reference/agriculture-runtime/` (proposed) or a sub-package under an existing runtime; placement is open.

### Proposed `FarmBotAdapter` shape

One adapter, parameterised by FarmBot generation (Genesis v1.7, Genesis XL, Express, Express XL). Package layout:

```
reference/agriculture-runtime/src/agriculture_runtime/farmbot/
├── __init__.py
├── adapter.py             # FarmBotAdapter
├── rest_client.py         # FarmBot REST API wrapper (developer.farm.bot)
├── mqtt_client.py         # FarmBot MQTT pub/sub wrapper
├── sequences.py           # mapping URML primitives to FarmBot sequences
├── peripherals.py         # mapping URML effectors to FarmBot peripherals / tools
└── manifests/
    ├── farmbot_genesis_v17.yaml
    ├── farmbot_genesis_xl_v17.yaml
    ├── farmbot_express_v10.yaml
    └── farmbot_express_xl_v10.yaml
```

The adapter implements URML's substrate Protocol. The primary transport is FarmBot's REST API for command dispatch and MQTT for telemetry; the FarmBot device runs FarmBot OS on a Raspberry Pi connected to the gantry's Arduino-firmware-driven microcontroller.

### Proposed URML v0.1 to FarmBot mapping

| URML primitive | FarmBot realisation |
|---|---|
| `move_to(pose)` | A FarmBot `move_absolute` or `move_relative` to the (x, y, z) coordinate, dispatched via the REST API's sequence-execute endpoint. URML's pose maps to FarmBot's (x, y, z) plus speed parameter. |
| `grasp(gripper_id)` | A `tool_mount` command for the named tool, or a `peripheral_on` for the named output (vacuum, soil-probe deployment). FarmBot's tool-mount mechanism is a magnetic mount; "grasp" semantics are tool-specific. |
| `release(gripper_id)` | A `tool_dismount` command, or `peripheral_off` for the named output. |
| `measure(sensor_id)` | A `read_sensor` command on the named sensor (soil sensor, weather sensor, camera capture). FarmBot's photo-capture endpoint covers the visual-measure case. |
| `wait_for(event \| threshold \| signal)` | A FarmBot `wait` (duration), or a polling loop on the read-sensor endpoint with a threshold check, or an MQTT subscriber on the event topic. |
| `report(status)` | Append to FarmBot's log via the `send_message` REST endpoint, with URML status tokens. The FarmBot Web App's log surface is what FarmBot users already read. |
| `plant`, `water`, `weed` (Layer-3 compositions, agriculture-profile candidates) | Composed Layer-3 sequences over `move_to` plus `tool_mount` plus `peripheral_on`, no new Protocol method. These are candidates for a future `spec/profiles/agriculture/` profile but are NOT proposed in this RFC. |

### Proposed capability manifest

The manifests live under `reference/agriculture-runtime/src/agriculture_runtime/farmbot/manifests/`. A condensed shape for `farmbot_genesis_v17`:

```yaml
brand: farmbot_genesis_v17
profile: educational
mobility: cartesian_gantry
workspace_m: [3.0, 1.5, 0.5]
mass_kg: 35.0
payload_kg: 0.5
transport: rest_plus_mqtt
rest:
  base_url: https://my.farm.bot/api
  spec_url: https://developer.farm.bot/docs/api-docs
mqtt:
  broker: configurable (typically clever-octopus.rmq.cloudamqp.com)
tools:
  - seeder
  - watering_nozzle
  - weeder
  - soil_sensor
peripherals:
  - vacuum_pump
  - water_solenoid
  - lighting
sensors:
  - soil_moisture
  - weather_optional
  - camera
controller: raspberry_pi_plus_farmduino
provenance:
  origin: US
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The `provenance.origin: US` row passes URML's US-federal default policy at [RFC-0003](0003-us-alignment.md) without organisational override. FarmBot is US-based (Berkeley, California).

### Proposed conformance integration

A `URML_FARMBOT_INTEGRATION=1` env-gated CI workflow installs a `farmbot-py` (or equivalent) client, runs `FarmBotAdapter` against a hermetic mock that replays REST and MQTT responses, and asserts that the emitted command sequences match recorded golden traces against the FarmBot API spec. The in-tree conformance suite continues to use `MockROSAdapter`. Hardware-in-the-loop against a real FarmBot is out of scope for this RFC.

### Future agriculture profile (open spec question, not in this RFC)

The natural Layer-3 compositions for agriculture (`plant(crop, location)`, `water(zone, volume)`, `weed(zone)`) are visible from this adapter design but the spec decision belongs in a future RFC. This RFC observes the alignment and leaves the profile-spec direction to a separate process. URML's posture on profiles (per `MANIFESTO.md`) is that profiles are added when the primitive sequences compose stably across at least two independent target deployments. FarmBot is one; a second agricultural target (a future cobot-mounted spray system, a programmable greenhouse) is the precondition for the profile spec.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC.
- Reference runtime: proposed new package `reference/agriculture-runtime/`. Not built in this PR. The RFC requests FarmBot maintainer feedback first.
- Conformance suite: proposed new `farmbot-integration.yml` CI workflow and a `URML_FARMBOT_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. FarmBot gains nothing yet; the adapter consumes the published REST API and MQTT surface without proposing changes to them.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** The honest framing: URML wants FarmBot input on the URML-primitive-to-FarmBot-sequence mapping before shipping, because the agricultural semantics (what does `move_to` mean over a planting bed?) are choices the REST API does not pin down.
- **The natural compositions are agriculture-profile primitives URML does not yet ship.** `plant`, `water`, `weed` belong in a future `spec/profiles/agriculture/` profile. Without that profile, URML programs for FarmBot remain at the lower-level `move_to + tool_mount + peripheral_on` Layer-2 surface, which is less ergonomic than the FarmBot Web App's native sequence editor.
- **Cartesian gantry is unique among URML manifests.** No prior URML manifest declares a Cartesian-gantry mobility surface. The workspace declaration (`workspace_m`) is the right shape but the rest of URML's mobility vocabulary (legged, wheeled, aerial) does not directly apply.
- **MQTT broker dependency.** FarmBot relies on a cloud-hosted MQTT broker (typically CloudAMQP-backed) for the standard deployment. URML's "validated programs run offline" rule (per [`CLAUDE.md`](../../CLAUDE.md)) requires the adapter to support a local broker mode; the FarmBot OS supports this, but the RFC needs to document the offline path explicitly.

## Alternatives considered

1. **Ship the adapter first, ask FarmBot maintainers later.** Rejected. The mapping from URML primitives to FarmBot sequences is a design choice with grower-visible consequences; a pre-RFC saves rework.
2. **Wait for the agriculture profile RFC before opening FarmBot outreach.** Rejected. The Layer-2 surface is sufficient for a first integration. The profile RFC depends on having at least one shipping adapter to ground its primitives, and FarmBot is that adapter.
3. **Target only the REST API; skip MQTT.** Rejected. MQTT is FarmBot's telemetry surface; without it, `wait_for` and `report` cannot reach real-time events.
4. **Fold FarmBot into [RFC-0063 (Hiwonder)](0063-hiwonder-outreach.md) or [RFC-0061 (WLKATA)](0061-wlkata-outreach.md) as a Cartesian-gantry extension.** Rejected. Hiwonder and WLKATA are makers of robot arms / mobile bases / hobby quadrupeds; FarmBot is an agricultural robot. The vertical is different and the user audience is different.

## Prior art

- `FarmBot/Farmbot-Web-App`: the upstream web application (967 stars, MIT-licensed, TypeScript / Ruby / SCSS, Issues enabled, 38 open, CONTRIBUTING.md present, REST + MQTT documented).
- `FarmBot/Farmbot-Arduino-Firmware`: the gantry firmware.
- `FarmBot/farmbot_os`: the Raspberry-Pi-side OS.
- FarmBot API documentation at `developer.farm.bot/docs/api-docs`: the canonical API reference.
- FarmBot Forum at `forum.farmbot.org`: the community surface.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): the URML profiles the FarmBot manifests target (until an agriculture-profile RFC lands).
- [RFC-0013](0013-industrial-layer2-primitives.md): the industrial-profile primitives (`pick_from`, `place_at`, `swap_tool`) that compose onto a tool-mount surface analogous to FarmBot's.
- [`MANIFESTO.md`](../../MANIFESTO.md): the stretch-goal mention of agricultural verticals.

## Unresolved questions

Provisional pending FarmBot maintainer feedback:

1. **Adapter home.** Should URML host the adapter under `reference/agriculture-runtime/` (URML-side), under a new repo in the `FarmBot` GitHub org as a contributed example, or both?
2. **Primitive-to-sequence mapping.** Is the `move_to + tool_mount + peripheral_on` decomposition the right way to ground URML primitives in FarmBot's sequence vocabulary, or would FarmBot recommend a different shape (e.g., URML primitives map to FarmBot CeleryScript directly)?
3. **Agriculture-profile primitives.** Is there appetite for a co-designed `plant` / `water` / `weed` Layer-3 vocabulary in a future RFC, with FarmBot as the first adapter?
4. **Local MQTT broker.** What is the documented path for running FarmBot's MQTT broker locally for URML's offline-execution requirement?
5. **Generation-specific manifests.** Per-generation manifests (Genesis v1.7 / Genesis XL / Express / Express XL) versus a single parametric `farmbot` manifest with a `workspace_m:` field?
6. **Conformance lane.** Open to a URML conformance line on FarmBot's developer documentation site or the Web App README?
7. **Anything else.**

## Implementation note

RFC-0067 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/agriculture-runtime/` package follows in a later session, gated on FarmBot maintainer feedback. Draft state. Third Move #4 RFC. First URML outreach to the agricultural vertical. Ledger entry in [`examples/lighthouses/outreach-move4.yaml`](../../examples/lighthouses/outreach-move4.yaml).

## Requested feedback (from FarmBot maintainers)

1. Adapter home (URML repo, FarmBot contributed example, both).
2. Primitive-to-sequence mapping.
3. Agriculture-profile co-design interest.
4. Local MQTT broker path.
5. Generation-specific manifest granularity.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`FarmBot/Farmbot-Web-App` has Issues enabled with 38 open at time of writing; CONTRIBUTING.md is present (verified 2026-05-24). The FarmBot Forum at `forum.farmbot.org` is the community-discussion surface, but a labelled Issue on the Web App repo is the documented contribution path for proposals. URML's planned channel: open a single Issue on `FarmBot/Farmbot-Web-App` labelled with the closest `enhancement` equivalent, pointing to this RFC, with optional cross-post on the FarmBot Forum if maintainers prefer the design conversation there.

URML's own public Discussions for the broader Move #4 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the third Move #4 RFC and URML's first agriculture outreach).
- [x] Motivation grounded in verified technical alignment (FarmBot Web App at 967 stars MIT, REST API documented at developer.farm.bot, MQTT pub/sub, Arduino firmware, FarmBot OS) plus the agricultural-vertical positioning.
- [x] Detailed design uses verified repo names (`FarmBot/Farmbot-Web-App`, `FarmBot/Farmbot-Arduino-Firmware`, `FarmBot/farmbot_os`).
- [x] At least one alternative considered (four are: ship-first, wait-for-agriculture-profile, REST-only, fold-into-WLKATA-or-Hiwonder).
- [x] Drawbacks are real (proposal-only, missing agriculture-profile primitives, Cartesian gantry uniqueness, MQTT broker dependency).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The mapping uses the existing vocabulary. The agriculture-profile primitives are flagged as a future RFC, not proposed here.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of `FarmBot/Farmbot-Web-App` as of 2026-05-24.
- [x] Provenance row (`origin: US`) recorded; US-federal default policy passes without override.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. The MQTT-broker offline-mode requirement is documented as a real cloud-dependency surface that must be solved by the adapter, not papered over.
