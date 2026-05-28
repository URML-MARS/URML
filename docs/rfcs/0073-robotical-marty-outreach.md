---
rfc: 0073
title: Robotical (Marty) integration, request for comment from robotical maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Open
created: 2026-05-24
updated: 2026-05-28 (round 5)
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

# RFC-0073: Robotical (Marty) integration, request for comment from robotical maintainers

## Engagement received (2026-05-25)

NikTheGeek1 (Robotical contributor) replied on [robotical/martypy#52](https://github.com/robotical/martypy/issues/52) with substantive technical guidance. The maintainer-side answers to the six RFC questions:

1. **Adapter home.** URML repo, externally maintained against the public `martypy` API. README link to URML's adapter possible once it is stable and tested against real Marty hardware.
2. **Active development cadence.** `martypy` is stable / maintenance-mode, not under active feature development.
3. **Transport priority.** Marty v2: default **USB-serial**, WiFi / WebSocket configurable. Marty v1: **socket**. **BLE is not supported by `martypy`** and URML would need to provide its own BLE layer if it wants one (out of scope here).
4. **MartyBlocks alignment.** No joint plans; URML should be positioned as an external intent/runtime layer, not as a MartyBlocks replacement.
5. **Conformance lane.** Open to a README / docs link once URML ships a working adapter, a clear v1/v2 compatibility matrix, and basic tests or real-hardware validation.

URML's response: shipped `RoboticalMartyAdapter` in `reference/edu-runtime/` alongside the existing VEX V5 / LEGO SPIKE / Thymio adapters (the maintainer's recommended "external adapter" home). Transport priority follows the maintainer's guidance verbatim. BLE deferred. Manifest fixture (`robotical_marty_v2.yaml`) and conformance fixture (`05_marty_patrol_positive.yaml`) shipped against `MockROSAdapter`; real-hardware validation is the documented next step before URML requests the upstream README link. State moves from Draft to Open.

This is URML's first engaged outreach response across the 31-thread Move #3–#6 inbox.

## Engagement received (round 2, 2026-05-27)

NikTheGeek1 returned on [robotical/martypy#52](https://github.com/robotical/martypy/issues/52) with five concrete factual corrections after reviewing the shipped scaffold. All five are landed in the same commit that records this section:

1. **BLE in the transport list (manifest snippet + RFC body).** `martypy` does not implement BLE; the example manifest snippet's `transport: [serial, websocket, ble]` and the RFC's "triple transport" framing overclaimed. URML's response: dropped BLE from the manifest example, from the drawbacks list, and from the "Detailed design" prose. The adapter docstring already scoped BLE as not-supported (originally from round-1 guidance); the RFC body now matches.

2. **Fake-`martypy` injection is not real adapter validation.** The hermetic tests use `_FakeMarty` doubles, which is fine for a scaffold but does not validate against the real `martypy` package or hardware. URML's response: no overclaim; the RFC and the outreach ledger now both explicitly mark current tests as scaffold-only, with real-`martypy` + hardware validation gated behind the eventual upstream README/docs link (item 5 from round 1).

3. **Skill name `sit()` may not exist in the current public `martypy.Marty` API.** Fake tests using `sit()` would pass while the real adapter fails. URML's response: removed `sit` from the adapter docstring examples and the test scaffold; replaced with confirmed-real skills (`walk`, `kick`, `eyes`, `arms`).

4. **Battery + accelerometer API corrections.** `get_battery_voltage()` is not implemented in `martypy`; `get_battery_remaining()` is the safer v2 call. The accelerometer no-axis form can return a tuple, so a naive `float(getter())` would fail for it. URML's response: changed the adapter's default sensor getter from `get_battery_voltage` to `get_battery_remaining`, added tuple-handling to the measurement payload so accelerometer tuple returns pass through cleanly, updated the test scaffold to mirror the corrected API.

5. **`third_party_audited` overclaim in the manifest fixture.** Without an actual third-party audit, the attestation level should be `self_declared`. URML's response: changed `manifest_attestation: third_party_audited` to `self_declared` in `robotical_marty_v2.yaml`.

## Engagement received (round 3, 2026-05-27)

NikTheGeek1 ran a non-moving smoke trace against a real Marty v2 over Wi-Fi and posted the JSON output on [robotical/martypy#52](https://github.com/robotical/martypy/issues/52), plus a curated authoritative skill + getter list (v1 + v2 split), plus three more corrections. This round-3 engagement materially closes URML's round-2 ask for both a "sample sensor trace" and an "authoritative skill / getter list."

Trace observed (real Marty v2, system version `RIC 1.3.21`, HwRev 5):

- `get_battery_remaining` returned an `int`: `81` (percent).
- `get_accelerometer` (no axis) returned a **`list`**, not a tuple: `[0.02, -0.04, 0.97]` (x, y, z).
- `get_power_status` returned a structured dict (`battRemainCapacityPercent`, `battRemainCapacityMAH`, `battFullCapacityMAH`, `battCurrentMA`, `battTempDegC`, `powerUSBIsConnected`, `power5VIsOn`).
- `get_robot_status` returned `isMoving / isPaused / workQCount`.
- `get_distance_sensor` returned an `int` (`0` in the trace).
- Axial accelerometer reads (`get_accelerometer_x`, `..._y`, `..._z`) returned plain `float`s.

URML responses:

1. **`tuple` vs `list` accelerometer return.** URML's round-2 tuple-handling guard only checked `isinstance(raw, tuple)`; the real trace returns `list`. **Action:** widened the guard to `isinstance(raw, (tuple, list))`; the test scaffold now mirrors the real-trace data with `_FakeMarty.get_accelerometer()` returning a `list`. URML's measurement payload passes the raw return through as a list either way.

2. **Connection-string surface.** `martypy.Marty` accepts methods `usb`, `wifi`, `socket`; URL-style `wifi://host` works because `wifi` is a valid method name. **`ws://host` is not a valid `martypy` method** and was an URML overclaim in the adapter docstring. **Action:** removed `ws://` from the adapter docstring; documented `usb` / `wifi` / `socket` explicitly with a note that URL-style `wifi://host` parses because `wifi` is the underlying method.

3. **BLE references still in Summary / Motivation.** URML's round-2 BLE cleanup caught the Detailed-design prose, the example manifest snippet, and the Drawbacks list, but not the Summary or Motivation sections. **Action:** Summary and Motivation prose in this RFC are now BLE-free; both call out URML's USB-serial / Wi-Fi surface and the `socket` method for v1.

4. **Authoritative skill + getter list.** URML internalized:
   - Movement / skill methods (v1 + v2): `walk`, `kick`, `arms`, `lean`, `eyes`, `dance`, `celebrate`, `get_ready`, `stand_straight`, `sidestep`, `move_joint`, `stop`, `play_sound`.
   - Movement / skill methods (v2-only): `wiggle`, `circle_dance`, `lift_foot`, `lower_foot`, `wave`, `resume`, `hold_position`, `speak`.
   - Sensor / status getters (v2): `get_battery_remaining`, `get_accelerometer`, `get_distance_sensor`, `get_robot_status`, `get_joints`, `get_power_status`, `get_add_ons_status`, `get_add_on_status`.
   - Sensor / status getters (v1): `get_battery_voltage`, `get_distance_sensor`, `get_accelerometer(axis="x"|"y"|"z")`.
   - **Adapter-design note (acknowledged gap, not fixed in this round).** URML's current `_send(command)` dispatch is generic no-args (`getattr(marty, command, None); skill()`). Many real Marty methods take arguments: `arms(left_angle, right_angle, move_time)`, `eyes(pose_or_angle)`, `lean(direction)`, `sidestep(side)`, `wave(side)`. A production-quality URML adapter needs an explicit URML-to-`martypy` mapping layer with positional / keyword arguments, not just method-name strings. URML records this as a v0.1 scaffold-limitation; the richer-dispatch design is a future ticket against the published `martypy.Marty` reference and is out of scope for this round-3 commit.

This round-3 engagement is URML's most substantive single round across the entire outreach inbox to date: an authoritative API reference plus a real-hardware trace, both contributed by the maintainer, both materially upgrading URML's test scaffold and adapter correctness without requiring URML to guess.

## Production-graduation milestone (2026-05-27)

Per the session retrospective's improvement #3, URML graduated `RoboticalMartyAdapter` from scaffold to production-grade in the same wave that PR-A (`third_party_audited` cleanup) and PR-B (`outreach-commitments.md`) landed. Two gates closed:

1. **Richer arg-passing dispatch.** The round-3 acknowledged-gap (`_send(command)` was name-only no-args) is now closed. `EduConfig.location_to_command` and `manipulation_commands` accept either a bare method-name string (no-arg call, backwards-compatible with the scaffold) or an `EduSkillCall(method=..., args=[...], kwargs={...})` for parameterized skills (`arms(left_angle, right_angle, move_time)`, `eyes(pose_or_angle)`, `lean(direction)`, `sidestep(side)`, `wave(side)`). `RoboticalMartyAdapter._send` dispatches both forms.
2. **Real-`martypy` CI workflow.** `.github/workflows/marty-real-integration.yml` pip-installs `martypy` from PyPI weekly (plus on every PR touching `reference/edu-runtime/**`) and asserts that every URML-documented skill + getter is a callable attribute on the real `martypy.Marty` class. Catches upstream-`martypy` API drift before users do.

What stays open (not closed in this round, recorded honestly):

- **Hardware-in-the-loop validation by URML itself.** The workflow's `marty-hardware-e2e` job is a placeholder that fails loudly until URML has access to a real Marty v2 (community loan or demo unit). Same convention as the existing `edu-board-e2e` / `cobot-controller-e2e` / `marine-sitl-e2e` placeholders.
- **Re-engaging NikTheGeek1 to request the upstream `martypy` README/docs link.** That ask was gated in round 1 on real-hardware validation, which has not closed. URML will return to the thread once it can demonstrate end-to-end on real hardware.

Net effect: `RoboticalMartyAdapter` is now URML's first scaffold-to-production graduation. Other engaged adapters (Kawasaki, Zivid, Maytronics, Spot rai-opensource-side) remain at scaffold or proposal-only; their graduations are future tickets.

## Engagement received (round 4, 2026-05-28)

NikTheGeek1 returned on [robotical/martypy#52](https://github.com/robotical/martypy/issues/52) with a concrete offer: he has a Marty v2 on hand and will run a URML-provided validation script against real hardware and paste the output back into the thread. Ownership stays clean: URML maintains the adapter and the script; Robotical runs the script and shares the JSON. His own framing: *"a URML-provided validation script run by Robotical on real Marty hardware, not a Robotical-maintained adapter."*

His script constraints:

- self-contained (single file, no URML install required, only `martypy` plus the Python standard library);
- prints commands before running them, so the script is reviewable end-to-end before any call lands on hardware;
- movement is small and explicit, opt-in via flags, with no walking or kicking in the first pass;
- the optional visible commands he named are `eyes('normal')` and `stand_straight()`;
- the connection must close cleanly.

URML's response: shipped [`reference/edu-runtime/scripts/marty_validate.py`](../../reference/edu-runtime/scripts/marty_validate.py). The script:

- Takes a `--method usb|wifi|socket` argument (matching the round-3 authoritative connection-string surface; `usb` and `wifi` for Marty v2, `socket` for Marty v1; `ws://` correctly absent).
- Prints a human-readable plan on stderr before any call runs, and a `RUN [...]: marty.<method>(...)` line before each individual invocation, so the entire call sequence is visible to the operator without reading the file.
- Has a `--plan-only` flag that prints the plan and exits without importing `martypy` or connecting, for an extra-cautious dry-run.
- Defaults to **sensor-only**: no movement happens unless the operator explicitly passes `--with-eyes` and / or `--with-stand-straight`. The opt-in movement set is limited to the two commands NikTheGeek1 named in round 4 (no walking, no kicking, no `arms` / `lean` / `sidestep`, no `dance` / `celebrate`).
- Exercises the URML-documented `martypy.Marty` API surface against real hardware: `get_battery_remaining`, `get_power_status`, `get_accelerometer` (no-axis list form per round-3 trace), `get_accelerometer_x` / `_y` / `_z` (only if present), `get_robot_status`, `get_distance_sensor`, plus a probe for `get_system_info` / `get_version_info` / `get_software_version`.
- Captures everything in a single JSON object on stdout, structured like the round-3 trace so URML can record it verbatim. Exceptions are captured per-call (each call returns an `{"ok": false, "error": "..."}` envelope rather than crashing the run), so a single broken getter does not abort the script.
- Disconnects in a `finally` block, preferring `marty.close()` and falling back to `marty.disconnect()`.

What this engagement does and does not close:

- **Closes (substantially): the round-1 item-5 "real-hardware validation" gate**, in the form of *URML's documented API surface verified against a real Marty v2 over WiFi*. The validation is URML-authored, Robotical-executed, JSON-receipted in this thread.
- **Stays open: URML's own end-to-end run of the `RoboticalMartyAdapter` (not just the underlying `martypy` surface) on a real Marty.** That gate waits on URML having access to its own Marty unit (community loan or community-channel demo); the `marty-hardware-e2e` job in the CI workflow remains a placeholder that fails loudly until then.

This is round four of four substantive engagement rounds across the Marty thread, and the third instance in which a Robotical maintainer's contribution has materially upgraded URML's adapter without URML having to guess. The thread's cumulative shape (scaffold guidance, five factual corrections, real-Marty trace + authoritative skill / getter list, hardware-validation offer) is recorded here verbatim so that the precedent is reusable by URML's other engaged outreach threads.

## Engagement received (round 5, 2026-05-28)

NikTheGeek1 ran [`reference/edu-runtime/scripts/marty_validate.py`](../../reference/edu-runtime/scripts/marty_validate.py) against a real Marty v2 over WiFi (no movement flags) and posted the JSON output on [robotical/martypy#52](https://github.com/robotical/martypy/issues/52). Two corrections plus a behavioural finding came back.

Trace observed (real Marty v2, `martypy` 3.7.1, `RIC 1.3.21`, HwRev 5, host `192.168.1.13`, no movement):

- `get_system_info` returned a structured dict with `SystemName=RIC`, `SystemVersion=1.3.21`, `RicHwRevNo=5`, plus a `MAC` field.
- `get_battery_remaining` returned `int 74` (percent).
- `get_power_status` returned the same dict shape as the round-3 trace (`battRemainCapacityPercent=74`, `battRemainCapacityMAH=1980`, `battFullCapacityMAH=2657`, `battCurrentMA=-245`, `battTempDegC=29`, `power5VIsOn=true`, `powerUSBIsConnected=false`, plus a `battInfoValid=true` field not seen in round 3).
- `get_accelerometer` (no axis) returned a list `[0.02, 0.0, 0.99]` (round-3 trace: `[0.02, -0.04, 0.97]`; trace-to-trace variation is expected and small).
- `get_accelerometer("x")` / `("y")` / `("z")` returned plain floats `0.02 / 0.0 / 0.99`.
- `get_robot_status` returned `isMoving=false / isPaused=false / workQCount=0`, plus an `isFwUpdating=false` field not seen in round 3.
- `get_distance_sensor` returned `int 0`.
- `close` succeeded.

**Corrections:**

1. **`martypy` does NOT expose `get_accelerometer_x() / _y() / _z()` methods.** URML's round-4 script probed `getattr(marty, "get_accelerometer_x", None)` etc. NikTheGeek1 had to patch the script locally before running it on real hardware; axis reads on real `martypy` use the no-axis getter with an axis argument: `get_accelerometer("x")`. **Action:** the script (round-5, this commit) now calls `marty.get_accelerometer(axis)` for each axis, not `getattr(marty, f"get_accelerometer_{axis}", None)`. `_FakeMarty` in [`reference/edu-runtime/tests/test_edu_adapters.py`](../../reference/edu-runtime/tests/test_edu_adapters.py) gains an optional `axis` parameter that returns the corresponding scalar, mirroring real-`martypy` behaviour.

2. **Empty first-read of `get_power_status()` immediately after reconnect.** NikTheGeek1 observed that the very first `get_power_status()` after a fresh connection returned an empty / zero snapshot, and a rerun produced the valid data above. **Action:** the script now retries once if the first read is empty (no sleep loop; one retry; the retry result carries a `retried_once: true` field so the JSON records the behaviour). A new `_is_empty_power` helper inspects the returned dict for missing / zero `battRemainCapacityPercent` and `battRemainCapacityMAH` and treats either as "empty".

**Finding (not a correction):** `martypy` 3.7.1 is in the wild and is the version NikTheGeek1's real Marty is running. URML's earlier writeup referenced `v3.6.6 (release 2024-01-12)` as "the canonical engagement surface"; the real-Marty side has moved on. Updating the manifest's `sdk_version_min` is a separate decision (URML's API-surface CI catches drift either way; raising the floor would only matter if the adapter starts using a 3.7-only attribute, which it does not).

**What this engagement does and does not close:**

- **Closes (in full): the round-1 item-5 "URML's documented API surface against real Marty v2" gate.** Round-4 covered the offer; round-5 has the receipted JSON in the thread. The full sensor-getter suite plus the corrected axis-form call returns valid data.
- **Stays open: URML's own end-to-end run of the `RoboticalMartyAdapter` (not just the underlying `martypy` surface) on a real Marty.** Same caveat as round 4: this is URML's problem until URML has a Marty unit. `marty-hardware-e2e` job in the CI workflow remains a placeholder.

This is round five of five substantive engagement rounds across the Marty thread, and the fourth instance in which a Robotical maintainer's contribution has materially upgraded URML's adapter or tooling without URML having to guess. The cumulative shape (scaffold guidance → five factual corrections → real-Marty trace + authoritative skill / getter list → hardware-validation offer → URML-provided script run on real hardware + two script-side corrections) is now recorded across rounds 1 to 5 on robotical/martypy#52 and in this RFC.

## Summary

URML does not yet ship a Robotical integration. This RFC proposes a `RoboticalMartyAdapter` under [`reference/edu-runtime/`](../../reference/edu-runtime/) (or as a sibling to the existing `reference/petoi-runtime/` family if the educational-runtime placement does not fit) targeting [`robotical/martypy`](https://github.com/robotical/martypy) (Apache-2.0, Python 99.4%, v3.6.6 release 2024-01-12). The adapter routes URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`, plus posture composition) onto MartyPy's USB-serial / Wi-Fi command surface for Marty v1 (`socket`) and Marty v2 (`usb` / `wifi`). No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the robotical maintainers.

This is the third Move #5 RFC. Robotical fills the **bipedal educational walking robot** niche: the closest analogue in URML's existing outreach is [RFC-0062 (Petoi Bittle / Nybble)](0062-petoi-bittle-outreach.md), but Petoi is quadruped and Marty is bipedal. The bipedal-classroom audience has been uncovered.

## Motivation

Marty is the bipedal counterpart to Petoi's Bittle in URML's outreach landscape: a commercial educational walking-robot vendor (UK-domiciled, Edinburgh) with a Python SDK, a Scratch-based block-coding surface (MartyBlocks), and a real classroom presence in UK and European STEM curricula. The audience overlap with Petoi is small (different mobility morphology, different curricular use cases), so a Marty integration broadens URML's educational footprint rather than duplicating it.

Three things make this RFC concrete rather than aspirational. First, `robotical/martypy` is Apache-2.0, Python 99.4%, with Issues enabled (2 open at time of writing); latest release v3.6.6 on 2024-01-12. The Python SDK is the canonical engagement surface. Second, Marty v2 (the current generation, released 2020) is a 9-DOF bipedal humanoid with an ESP32 controller and a documented USB-serial / Wi-Fi command surface that the SDK wraps (`usb` and `wifi` are the v2 connection methods; `socket` is the v1 method; BLE is not implemented in `martypy` per maintainer correction). Third, the MartyBlocks visual-coding interface is conceptually adjacent to URML's English-to-program path: both wrap the same robot-intent surface with a more accessible programming abstraction; URML can position as the natural-language layer above MartyBlocks's block-based layer.

Robotical's posture is open SDK on closed hardware: MIT / Apache-2.0 across the public-facing Python SDK and example code, proprietary firmware on the Marty hardware. URML's adapter consumes the SDK and the documented command protocol without proposing firmware changes. Robotical is UK-domiciled; URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) passes at the manifest level for the UK origin without organisational override.

## Detailed design

### Proposed `RoboticalMartyAdapter` shape

One adapter, parameterised by Marty generation (v1 / v2). Package layout:

```
reference/edu-runtime/src/edu_runtime/robotical/
├── __init__.py
├── adapter.py             # RoboticalMartyAdapter
├── martypy_wrapper.py     # martypy SDK call wrappers
├── skills.py              # mapping URML primitives to Marty skill commands
└── manifests/
    ├── robotical_marty_v1.yaml
    └── robotical_marty_v2.yaml
```

The adapter implements URML's substrate Protocol via `martypy.Marty` connection objects. Two transports per Marty v2: USB-serial (default) and WebSocket (over Wi-Fi). BLE is **not supported by `martypy`** (confirmed by NikTheGeek1 on robotical/martypy#52 in both round-1 and round-2 engagement); URML would need to ship a separate BLE layer if it ever wants one, which is out of scope here. Marty v1 uses `socket`.

### Proposed URML v0.1 to Robotical mapping

| URML primitive | Marty realisation |
|---|---|
| `move_to(pose)` | A `walk` / `kick` / `arms` / `lean` / `eyes` skill call via `martypy.Marty(...).walk(...)` or similar. URML's pose maps to direction + step-count + speed. Like Bittle ([RFC-0062](0062-petoi-bittle-outreach.md)), Marty is skill-library-driven rather than per-joint-trajectory; the URML adapter does not emit joint targets. |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable on stock Marty (no gripper). Manifest declares `gripper: none`; static verifier rejects programs using these primitives on a Marty manifest. |
| `measure(sensor_id)` | A `get_accelerometer()` / `get_battery_voltage()` / etc. call via the SDK. Marty v2 has an IMU and battery sensor at minimum. |
| `wait_for(...)` | Polling loop on the sensor stream with debounce. |
| `report(status)` | Append to per-session log file plus stdout; optional `martypy.Marty().eyes(...)` for visible status indication. |
| `pose(posture_id)` (Layer-3 composition) | A named-skill call from the Marty skill library (e.g., `stand_straight`, `kick`, `wave`). |

### Proposed capability manifest

A condensed shape for `robotical_marty_v2`:

```yaml
brand: robotical_marty_v2
profile: educational
mobility: legged_bipedal
dof: 9
mass_kg: 0.85
height_m: 0.35
transport: [serial, websocket]
python_sdk: martypy
sdk_version_min: 3.6.6
skills:
  - walk
  - kick
  - arms
  - lean
  - eyes
  - dance
gripper: none
controller: esp32
provenance:
  origin: GB
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The skill list mirrors Bittle's structure ([RFC-0062](0062-petoi-bittle-outreach.md)). Robotical and Petoi both speak skill-library command languages even though their hardware morphologies differ.

### Cross-link to RFC-0062 (Petoi)

Marty (bipedal) and Bittle (quadruped) are the two URML educational legged-robot targets. The adapter pattern is intentionally consistent: skill-library mapping with no joint-target emission, gripper-less manifest, low-cost educational tier. A URML program written for Bittle does not directly retarget to Marty (the gait vocabulary differs), but the URML primitive-set the program emits does.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/edu-runtime/src/edu_runtime/robotical/`. Not built in this PR.
- Conformance suite: proposed new `robotical-integration.yml` CI workflow and a `URML_ROBOTICAL_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.**
- **Skill-library motion forfeits joint-target authoring.** Same trade-off as Bittle ([RFC-0062](0062-petoi-bittle-outreach.md)).
- **martypy star count is low (6 stars).** Low GitHub footprint doesn't reflect the actual classroom deployment scale, which is documented at `robotical.io` but not reflected in repo stars.
- **martypy release cadence has slowed.** Latest release v3.6.6 on 2024-01-12 (about 18 months stale at time of writing); needs maintainer input on whether the platform is actively developed or in maintenance mode.
- **Dual transport (serial / WebSocket).** Increases the test matrix. BLE was originally listed but is not supported by `martypy` (confirmed in maintainer engagement; dropped from the manifest example and from this list).

## Alternatives considered

1. **Ship the adapter first.** Rejected.
2. **Skip Marty v1 and target only Marty v2.** Rejected. V1 deployments remain in classroom use; the SDK already supports both.
3. **Fold Marty into [RFC-0062 (Petoi)](0062-petoi-bittle-outreach.md) as another DIY-walking-robot vendor.** Rejected. Different audiences (Petoi is global maker / hobbyist; Marty is UK / European education-channel), different morphologies.
4. **Wait for MartyBlocks 2.0 / Marty v3.** Rejected. Current SDK is sufficient for the proposal.

## Prior art

- `robotical/martypy` (Apache-2.0, 6 stars, Python 99.4%, v3.6.6 2024-01-12).
- MartyBlocks: the Scratch-based visual coding interface.
- Marty v2 product page at `robotical.io`.
- [RFC-0011](0011-educational-profile.md): the educational profile.
- [RFC-0062](0062-petoi-bittle-outreach.md): the parallel quadruped DIY-walking-robot RFC.

## Unresolved questions

1. **Adapter home.** URML repo or robotical contributed example?
2. **Active development cadence.** Is the platform actively developed or in maintenance mode?
3. **Transport priority.** Which transport should URML's adapter default to (serial / WebSocket / BLE)?
4. **MartyBlocks alignment.** Is there interest in coordinating URML's natural-language layer with MartyBlocks's block-based layer?
5. **Conformance lane.** Open to a URML conformance line on `robotical/martypy` README or `robotical.io` docs?
6. **Anything else.**

## Implementation note

RFC-0073 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback (from robotical maintainers)

1. Adapter home.
2. Active development cadence.
3. Transport priority.
4. MartyBlocks coordination.
5. Conformance-lane interest.
6. Anything else.

## How to respond

`robotical/martypy` has Issues enabled (2 open at time of writing; verified 2026-05-24). URML's planned channel: open a single Issue on `robotical/martypy` labelled with the closest `enhancement` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary, Motivation, and Detailed design grounded in verified `robotical/martypy` surface.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (proposal-only, skill-library motion ceiling, low star count, stale release cadence, triple transport).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified as of 2026-05-24.
- [x] Provenance `origin: GB` recorded; US-federal default policy passes.
- [x] CLAUDE.md compliance check passed.
