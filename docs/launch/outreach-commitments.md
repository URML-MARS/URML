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

# Outreach commitments (open promises)

URML's outreach ledgers under [`examples/lighthouses/`](../../examples/lighthouses/) are the source of truth for engagement state. This page is the **human-readable index of outstanding commitments URML has made publicly** to engaged maintainers — promises that need to be honored, with checkbox status.

It exists because nine outreach moves and ~100 RFCs produce engagement threads whose commitments accumulate, and the next-action field on a ledger row is verbose enough that the open-promise count is easy to lose. Per the [session retrospective's improvement #4](https://github.com/URML-MARS/URML/pull/157), this page is the visible-backlog mechanism.

**Maintenance**: this is currently human-edited. The source of truth is each ledger row's `next_action`; this page is a derivative view. A future script could regenerate it from the ledgers, but for now the discipline is: when URML makes a public commitment, add a checkbox here; when URML honors it, check the box and date the change.

**Scope**: every ledger row with `response: engaged`. Other states (`acked`, `declined`, `wontfix`, `none`) don't produce commitments URML needs to track.

---

## Ouster — RFC-0032 (engaged 2026-05-22)

- **Thread**: [ouster-lidar/ouster_example#711](https://github.com/ouster-lidar/ouster_example/issues/711)
- **Maintainer**: Samahu (Ussama Naal, Ouster Inc engineer)
- **Ledger row**: [outreach.yaml `ouster`](../../examples/lighthouses/outreach.yaml)

Open commitments:

- [ ] **v0.2 schema iteration: `beam_count`** (Samahu Q1).
- [ ] **v0.2 schema iteration: units-on-point-cloud** (Samahu Q2).
- [ ] **v0.2 schema iteration: `time_sync_methods` capability list** (Samahu Q4).
- [ ] **Post back on `ouster_example#711`** when the iteration lands.

Notes: Samahu's Q5 ("RFC-0020 lidar review — will try") is on his side; URML has nudged once and does not nudge again.

---

## Kawasaki — RFC-0029 (engaged 2026-05-26; first Tier-1 industrial OEM engaged)

- **Thread**: [Kawasaki-Robotics/khi_ros2#9](https://github.com/Kawasaki-Robotics/khi_ros2/issues/9)
- **Maintainer**: kurita-taisuke (Kawasaki-Robotics MEMBER)
- **Ledger row**: [outreach.yaml `kawasaki`](../../examples/lighthouses/outreach.yaml)
- **Reference memory**: [`project_first_tier1_oem_engaged_kawasaki.md`](../../../../.claude/projects/c--Users-Ido-URML/memory/project_first_tier1_oem_engaged_kawasaki.md) (Claude session memory)

Open commitments:

- [x] **RFC-0029 + `KawasakiAdapter` docstring correction** (E-series claim removed; AS-binding endorsement + Discussions enablement recorded). DONE 2026-05-26 (PR #147).
- [ ] **Advance `KawasakiAdapter` listing in `docs/compatible-runtimes.md`** (RFC-0014 self-reported tier). **BLOCKED** on the Phase 0 reference-runtime exclusion in [`reference/ros2-runtime/CONFORMANCE.md`](../../reference/ros2-runtime/CONFORMANCE.md). Lifts when at least one third-party runtime submission lands in the registry. URML's commitment is to advance the row in the same wave that admits the first third-party runtime; until then, the maintainer-blessed status is recorded in RFC-0029 and the ledger.
- [ ] **Cite this thread when RFC-0015 (`call_program`) advances Draft → Open** as the AS-language binding acknowledgement.

---

## Zivid — RFC-0035 (engaged 2026-05-27 via public + email)

- **Thread**: [zivid/zivid-ros#163](https://github.com/zivid/zivid-ros/issues/163) (public) + private email to `greenvh@gmail.com` (substance)
- **Maintainers**: holmbakk (public ack); Espen Holmbakken (Principal Engineering Manager, Zivid — substantive email)
- **Ledger row**: [outreach.yaml `zivid`](../../examples/lighthouses/outreach.yaml)

Open commitments:

- [x] **RFC-0035 "Maintainer engagement received (2026-05-27)" section** reflecting Espen's Q1–Q5 outcomes. DONE 2026-05-27 (PR #155).
- [x] **Manifest fixture `manifest_attestation: third_party_audited → self_declared`** in `zivid_two_cell.yaml`. DONE 2026-05-27 (PR #155, broadened to all fixtures in PR #157).
- [ ] **Future Spec RFC: 3D-camera schema extension** (color + per-point attributes parallel to RFC-0039 lidar). Not opened in this round; URML records this as a queued Spec RFC question.
- [ ] **Q4 hand-eye calibration declaration** — Espen did not address; remains a v0.1 manifest gap. URML notes it as deployment-side concern unless a future RFC says otherwise.

---

## Marty — RFC-0073 (engaged 2026-05-25 → 2026-05-27 across three rounds)

- **Thread**: [robotical/martypy#52](https://github.com/robotical/martypy/issues/52)
- **Maintainer**: NikTheGeek1 (Robotical CONTRIBUTOR on `martypy`)
- **Ledger row**: [outreach-move5.yaml `robotical-marty`](../../examples/lighthouses/outreach-move5.yaml)

Open commitments:

- [x] **Round-1 scaffold shipment**: `RoboticalMartyAdapter` + manifest fixture + conformance fixture. DONE 2026-05-25 (PR #137).
- [x] **Round-2 corrections**: BLE cleanup, `sit()` removal, `get_battery_voltage → get_battery_remaining`, tuple-handling, `third_party_audited → self_declared`. DONE 2026-05-27 (PR #152).
- [x] **Round-3 corrections**: accelerometer list-return, `ws://` cleanup, BLE in Summary/Motivation, authoritative skill catalog recorded, adapter-design scaffold-gap acknowledged. DONE 2026-05-27 (PR #156).
- [ ] **Production-graduation milestone**: richer arg-passing dispatch in `RoboticalMartyAdapter._send` + real-`martypy` CI workflow + claims-audit graduation update. **In flight** as PR C from the session retro (improvement #3).
- [ ] **Hardware-in-the-loop validation** by URML itself on real Marty hardware. Depends on hardware access (loan or community unit); separate future ticket.
- [ ] **Re-engage NikTheGeek1 to request the upstream `martypy` README/docs link** once hardware validation closes (per round-1 item 5).

---

## Spot — RFC-0043 (engaged 2026-05-26 on the rai-opensource side; BD-side still none)

- **Threads**: 
  - PRIMARY: [boston-dynamics/spot-cpp-sdk#14](https://github.com/boston-dynamics/spot-cpp-sdk/issues/14) — no response from BD maintainers yet.
  - PARALLEL: [rai-opensource/spot_ros2 Discussion #805](https://github.com/rai-opensource/spot_ros2/discussions/805) — engaged.
- **Maintainer**: Tim Perkins (`taughz`, rai-opensource COLLABORATOR, **explicitly not Boston Dynamics**)
- **Ledger row**: [outreach-move2.yaml `spot`](../../examples/lighthouses/outreach-move2.yaml)

Open commitments:

- [x] **Substrate-cut validation acknowledged**: URML's bosdyn-direct `SpotAdapter` (parallel to `PX4Adapter` for MAVLink) is the canonical cut. DONE 2026-05-27 (PR #150).
- [x] **"Not Boston Dynamics" Q4 redirect accepted**: BD-policy questions go to BD directly. DONE 2026-05-27 (PR #150).
- [ ] **Q2 capability-vocabulary nits**: frames (`site` + `body` vs `vision` / `odom` / `body`), `perception.cameras` (single aggregate vs five fisheye + arm), `mobility.station_keeping` for posture-hold. Surfaced for optional low-pressure engagement; no Tim-side commitment, but URML's open question.
- [ ] **Q3 Spot Arm extension**: minimum manifest fields + minimum `SpotAdapter` extension for grasp/release on Spot Arm deployments. Surfaced for optional low-pressure engagement.
- [ ] **BD-side primary thread** (`spot-cpp-sdk#14`): still `response: none`. No BD-side commitment; URML monitors for any future signal.

---

## Maytronics Dolphin — RFC-0103 (engaged 2026-05-26)

- **Thread**: [sh00t2kill/dolphin-robot#284](https://github.com/sh00t2kill/dolphin-robot/issues/284) (public) + Maytronics R&D relay (private, via elad-bar)
- **Maintainer**: elad-bar (sh00t2kill/dolphin-robot COLLABORATOR; community-maintained Home Assistant integration of Maytronics' WiFi API)
- **Ledger row**: [outreach-move8.yaml `maytronics-dolphin`](../../examples/lighthouses/outreach-move8.yaml)

Open commitments:

- [x] **R&D-readable distillation supplied** (2 paragraphs) for elad-bar to forward to Maytronics R&D. DONE 2026-05-27 (PR #148).
- [x] **Lower-bound mapping proposed**: only what `dolphin-robot` reliably surfaces today (region-based mobility, cycle status, scheduled-start trigger, `measure` / `report`). Higher-fidelity primitives return `not_supported_on_consumer_pool_robot` per RFC-0014. DONE 2026-05-27 (PR #148, RFC-0103).
- [ ] **Awaiting Maytronics-side response** via elad-bar's R&D relay. No URML-side action until the relay produces a signal.
- [ ] **Awaiting more specific signal on newer Maytronics products**: which models expose richer data envelopes, which capability categories. URML asked; not yet answered.
- [ ] **Unresolved questions Q1–Q4, Q6–Q7** (license posture, adapter home, manifest values, mobility encoding, home-profile co-design, conformance lane) remain open from RFC-0103's original ask.

---

## Clearpath — RFC-0072 (engaged 2026-05-26)

- **Thread**: [clearpathrobotics/cpr_gazebo#26](https://github.com/clearpathrobotics/cpr_gazebo/issues/26)
- **Maintainer**: nnarain-cpr (Clearpath contributor by handle suffix)
- **Ledger row**: [outreach-move5.yaml `clearpath`](../../examples/lighthouses/outreach-move5.yaml)

Open commitments:

- (Not handled in this session — the engagement predates the round of work that produced this page. Commitments need to be enumerated from the ledger row's `next_action` field in a future maintenance pass on this page. Listed here so the thread is not forgotten.)

---

## Closed / declined threads (no open commitments)

For history, threads URML has closed or that the maintainer declined are recorded in the ledgers but generate no commitments:

- **Festo (RFC-0034, declined 2026-05-26)** — venue rejection accepted; thread closed.
- **ArduPilot (RFC-0041, declined 2026-05-25)** — venue rejection accepted; thread closed.
- **OVOS (RFC-0107, closed wontfix 2026-05-26)** — AI-generated-flagging close; URML did not pursue.
- **JIYIUAV (out-of-repo decline, 2026-05-26)** — scope-mismatch decline via WhatsApp; no in-repo trace.

## Cross-references

- Per-thread engagement history lives in each RFC's "Engagement received" / "Maintainer engagement received" section, by round.
- The launch-claims dossier is [`claims-audit.md`](claims-audit.md); this page is the engagement-side complement.
- The "first engaged" milestone memories: [`project_first_engaged_outreach.md`](../../../../.claude/projects/c--Users-Ido-URML/memory/project_first_engaged_outreach.md) (Marty, first across the Move #2-#6 inbox) and [`project_first_tier1_oem_engaged_kawasaki.md`](../../../../.claude/projects/c--Users-Ido-URML/memory/project_first_tier1_oem_engaged_kawasaki.md) (Kawasaki, first Tier-1 OEM).
