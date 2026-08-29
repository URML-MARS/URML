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

# Sentence to Pixhawk: URML on a real ArduPilot board

[sentence-to-flight.md](sentence-to-flight.md) flies a simulated PX4. This
page puts URML on a physical flight controller: a Pixhawk-class board running
ArduCopter, plugged into a laptop over USB. Three scenes on the bench, then
two flight-test runbooks gated behind a simulator pass.

The bench scenes were run against real hardware while this page was written
(ArduCopter 4.6.3, MAVLink system id 10, USB, propellers off). The flight
tests have not been flown. Nothing on this page claims a physical flight.

## Prerequisites

- URML from a checkout per [Tutorial 1](../tutorials/01-getting-started.md).
- The ArduPilot transport: `pip install -e reference/ardupilot-runtime[ardupilot]`
  (pulls `pymavlink` and `pyserial`).
- A Pixhawk-class board running ArduCopter on USB. Windows shows it as
  `COM<n>` (Device Manager, "USB Serial Device"); Linux as `/dev/ttyACM0`.
  Edit `connection_url` in
  [`examples/drone/pixhawk-ardupilot.adapter.yaml`](../../examples/drone/pixhawk-ardupilot.adapter.yaml)
  if yours differs.
- **Propellers off** for every bench scene. Scene 3 asks the autopilot to
  arm. It should refuse; do not rely on that.

## Scene 1: the board says who it is

Read-only. Sends a version request and listens.

```bash
python -m urml_ardupilot_runtime.probe COM5
```

Observed on the bench (2026-08-29):

```
connection_url: COM5,115200
autopilot: ArduPilot
mav_type: 2
system_id: 10
component_id: 1
armed: False
mode: STABILIZE
firmware: 4.6.3
battery_v: 0.01
gps_fix: None
statustext:
  - PreArm: Compass not calibrated
  - PreArm: Battery 1 low voltage failsafe
```

`mav_type: 2` is a quadrotor. `battery_v: 0.01` is a board on USB with no
flight battery. The `PreArm:` lines are the autopilot talking; they are what
Scene 3 will surface as a reason.

## Scene 2: a sentence reads the battery

The sentence is in
[`examples/drone/bench-battery.en.txt`](../../examples/drone/bench-battery.en.txt):

```
Read the battery voltage and report it.
```

The program is
[`examples/drone/bench-battery.urml.yaml`](../../examples/drone/bench-battery.urml.yaml):
one `measure`, one `report`. The validator clears it first:

```bash
urml validate examples/drone/bench-battery.urml.yaml \
    -m examples/drone/pixhawk-ardupilot.manifest.yaml \
    --profile drone --no-policy
```

Then it runs on the board:

```bash
urml execute examples/drone/bench-battery.urml.yaml \
    -m examples/drone/pixhawk-ardupilot.manifest.yaml \
    --profile drone --no-policy \
    --adapter ardupilot \
    --adapter-config examples/drone/pixhawk-ardupilot.adapter.yaml
```

Expected:

```
URML execute: examples/drone/bench-battery.urml.yaml
  adapter:   ardupilot
  substrate: ArduPilot / MAVLink. Primitives dispatched to the connected ArduCopter (SITL or hardware). ...
  re-validation: passed (executed only after the validator accepted it)

  trace (2 step(s) executed, 0 adapter call(s)):
    (2 step(s) dispatched; this adapter keeps no call log, so there is no per-step trace. See RESULT below.)

  bindings:
    battery = {'value': 0.008, 'unit': 'V', 'timestamp': 0.0}

  RESULT: SUCCESS (2 step(s) executed)
```

`measure` read `BATTERY_STATUS` over MAVLink; `report` sent a `STATUSTEXT`
back to the autopilot's log. Nothing armed, no mode changed.

## Scene 3: the autopilot says no

A four-step flight program,
[`examples/drone/bench-hop.urml.yaml`](../../examples/drone/bench-hop.urml.yaml):
`take_off` to 3 m, `move_to` five metres north, `return_to_home`, `land`.

```bash
urml execute examples/drone/bench-hop.urml.yaml \
    -m examples/drone/pixhawk-ardupilot.manifest.yaml \
    --profile drone --no-policy \
    --adapter ardupilot \
    --adapter-config examples/drone/pixhawk-ardupilot.adapter.yaml
```

Observed on the bench (2026-08-29), trimmed:

```
  RESULT: FAILURE (1 step(s) executed)
    last outcome: PrimitiveOutcome(success=False, reason='arm_rejected: mav_result_failed;
      Arm: Compass not calibrated; Arm: GPS 1: Bad fix; Arm: Battery 1 low voltage failsafe;
      PreArm: Compass not calibrated; PreArm: GPS 1: Bad fix; PreArm: Battery 1 low voltage
      failsafe; PreArm: Logging failed', ...)
```

"1 step executed" is `take_off` being dispatched and refused; the remaining
three steps never ran. On a board whose EKF refuses GUIDED before arming is
attempted, the reason starts with `mode_rejected: GUIDED` instead. ArduCopter
accepted the GUIDED mode change while disarmed, so the board is left in
GUIDED; that is the autopilot's normal behaviour, not something URML set
without asking.

This is the demo. The validator accepted the program, the adapter entered
the arming sequence exactly as it would in the field, and the autopilot's
own pre-arm checks refused. URML reported the autopilot's words and stopped.
No `ARMING_CHECK` was touched. Re-run Scene 1 afterwards: `armed: False`, `mode: GUIDED`.

The same three scenes are a gated test:

```bash
URML_ARDUPILOT_BENCH=COM5 pytest reference/ardupilot-runtime/tests/integration/test_arducopter_bench.py -q
```

## What this is NOT

A bench is a bench. These scenes prove the URML pipeline reaches a physical
ArduPilot autopilot over MAVLink, reads real telemetry from it, and is
refused by its real safety checks. They do not prove an aircraft flew. A
flight needs an airframe, a GPS fix, a legal site, a licensed operator, and
the checklists below.

## Flight test runbooks

Two outdoor tests are queued. Both are gated on a green ArduCopter SITL run
first; the field run is the operator's call and is not claimed here.

### SITL gate

ArduCopter SITL runs on Linux (WSL on Windows). From an ArduPilot checkout:

```bash
Tools/autotest/sim_vehicle.py -v ArduCopter --console --map \
    --out udp:<windows-host-ip>:14550
```

Set these SITL parameters once so camera, gripper, and winch commands are
acknowledged: `CAM1_TYPE 1`, `GRIP_ENABLE 1`, `GRIP_TYPE 1`, `WINCH_TYPE 1`
(PWM), with a servo function assigned to each (`SERVO9_FUNCTION 10` camera
trigger, `SERVO10_FUNCTION 28` gripper, `SERVO11_FUNCTION 88` winch). Then:

```bash
URML_ARDUPILOT_SITL=1 URML_ARDUPILOT_SITL_URL=udp:0.0.0.0:14550 \
    pytest reference/ardupilot-runtime/tests/integration/test_arducopter_sitl_e2e.py -q
```

That flies the `drone/flight_only_positive` conformance fixture and the two
example programs below against the simulator. First calibration run:
2026-08-29, SITL built from `Copter-4.6.3` in WSL2, home at the example
coordinates, all three green in one uninterrupted run. (Direct binary used
instead of `sim_vehicle.py`, which needs MAVProxy for `--out`:
`build/sitl/bin/arducopter --model + --speedup 4 -w --home 32.0853,34.7818,50,0
--defaults Tools/autotest/default_params/copter.parm,urml_sitl.parm
--serial0 udpclient:<windows-host-ip>:14550`.) The same job exists as
`ardupilot-sitl-e2e` in
[`.github/workflows/ardupilot-integration.yml`](../../.github/workflows/ardupilot-integration.yml),
manual-trigger only, not yet run in CI.

### Flight test 1: five photos at 100 m around an address

Sentence: *Fly 100 metres above the site and take five pictures around it
for a 3D model.*

Files: [`site-photogrammetry.urml.yaml`](../../examples/drone/site-photogrammetry.urml.yaml),
[`.manifest.yaml`](../../examples/drone/site-photogrammetry.manifest.yaml),
[`.envelope.yaml`](../../examples/drone/site-photogrammetry.envelope.yaml),
[`.adapter.yaml`](../../examples/drone/site-photogrammetry.adapter.yaml).

1. **Address to coordinates, once, offline from the runtime.** Put the launch
   point and the site address in a copy of
   [`addresses.example.yaml`](../../examples/drone/addresses.example.yaml), then:

   ```bash
   python tools/scripts/geocode_locations.py my-addresses.yaml \
       --out examples/drone/site-photogrammetry.adapter.yaml \
       --alt-agl 100 --orbit site --radius-m 40 --points 5 --look-at site
   ```

   It writes `location_to_global` (five orbit stations, each yawing toward
   the site) into the adapter config and prints the matching
   `declared_locations` block; paste that into the manifest so the validator
   has metres to check against the geofence. The committed example is Times
   Square, New York (geocoded via Nominatim on 2026-08-29, then pinned with
   `--fix` so it regenerates offline); see step 5 for why that site is a
   legal case study rather than a flight plan.
2. **Camera.** `camera.kind: digicam` in the adapter config sends
   `MAV_CMD_DO_DIGICAM_CONTROL`; set `CAM_TRIGG_TYPE` on the board to match
   your shutter wiring, or use `kind: servo` with the AUX `channel`. Images
   stay on the camera; URML records `camera://shot/N` plus the autopilot
   position at trigger time.
3. **Validate**, then **SITL**, then field.
4. **Reconstruction.** Hand the five files and `urml execute --json` output to
   OpenDroneMap / WebODM or COLMAP. Five frames make a coarse model; 20 to 40
   frames with 70 % overlap is the usual photogrammetry input
   (`--points 20`). URML does not run reconstruction; see RFC-0519 / 0520.
5. **Altitude and law, for the committed example (Times Square, New York).**
   The example addresses were geocoded on 2026-08-29 (home: Times Square;
   site: One Times Square; drop-off: Duffy Square). What the rules say about
   flying there, checked the same day:
   - **FAA.** Times Square sits in LaGuardia's Class B airspace. The FAA UAS
     Facility Map grid at 40.754 N, 73.988 W shows a **400 ft LAANC
     ceiling** (map effective 2026-08-06), so 100 m AGL (328 ft) is inside
     what LAANC can auto-authorize for a Part 107 pilot. Class B still means
     an authorization is mandatory before every flight, and a night flight or
     anything above the grid ceiling needs a waiver through FAADroneZone.
     Five photos of a building with a crowd underneath is also an operation
     over people: Part 107 Subpart D category rules apply to the aircraft.
   - **New York City.** NYC Admin Code 10-126(c) and 38 RCNY Ch. 24 forbid
     any drone take-off or landing in the five boroughs without an **NYPD
     permit**: application 30 days ahead at the NYPD Unmanned Aircraft portal,
     USD 150 fee, Part 107 certificate, general-liability insurance naming the
     City, and an operations plan with the take-off site, path, altitude, and
     window. Fines up to USD 1,000 per violation and equipment seizure. The
     only permit-free sites are three model-aircraft fields in Queens, Staten
     Island, and Brooklyn.
   - **Net.** The committed Times Square bundle is a real geocoding example
     and a real validator exercise; it is not a flight plan. Fly it only with
     an approved NYPD permit and a LAANC authorization in hand, or re-geocode
     to a site where you can. URML encodes the envelope you give it, not the
     law.

   Sources: [flyusi.org New York drone laws](https://www.flyusi.org/guides/drone-laws/new-york),
   [drone-laws.com NYC](https://drone-laws.com/drone-laws-in-nyc/),
   [FAA UAS Facility Maps](https://www.faa.gov/uas/commercial_operators/uas_facility_maps),
   [FAA UASFM FAQ](https://www.faa.gov/uas/commercial_operators/uas_facility_maps/faq),
   FAA UASFM ArcGIS feature service (queried at the Times Square point).

### Flight test 2: parcel delivery

Sentence: *Deliver the parcel to the drop-off point and come back.*

Files: [`parcel-delivery.urml.yaml`](../../examples/drone/parcel-delivery.urml.yaml)
(winch and latch), [`parcel-delivery-servo.urml.yaml`](../../examples/drone/parcel-delivery-servo.urml.yaml)
(latch only, low drop), shared
[`.manifest.yaml`](../../examples/drone/parcel-delivery.manifest.yaml),
[`.envelope.yaml`](../../examples/drone/parcel-delivery.envelope.yaml),
[`.adapter.yaml`](../../examples/drone/parcel-delivery.adapter.yaml).

1. The mechanisms are manifest `outputs.lines` driven by `set_output`
   (RFC-0017), bound in the adapter config to ArduPilot's gripper
   (`MAV_CMD_DO_GRIPPER`), winch (`MAV_CMD_DO_WINCH`, relative-length control;
   ArduCopter 4.6 rejects the deliver / retract actions), or a servo. The drone
   profile keeps `manipulation` off aerial manifests, so `release` is not the
   verb; a follow-up RFC proposes an aerial-delivery extension.
2. ArduPilot acknowledges a winch command when it accepts it, not when the
   line reaches the ground. The program brackets the winch with `hover`
   pauses sized from `deliver_length_m / rate_m_s` plus margin; edit both
   the program and the adapter config together.
3. Validator blind spot, stated rather than hidden: `set_output` and a
   `hover` without `over` add no spatial target, so the drop point is checked
   against the geofence only through the `move_to` before it.
4. Board parameters: `GRIP_ENABLE 1`, `GRIP_TYPE` per hardware,
   `WINCH_TYPE 1`, plus the servo function assignments for each.
5. **Validate**, then **SITL**, then field. Never with people under the drop
   point; the example envelope puts a people-occupancy zone beside it for
   exactly that reason.

### Field checklist (both tests)

Props on only after the SITL pass is green. GPS 3D fix and `PreArm` clear on
a ground station before running URML. A second link (radio or GCS) with RTL
on a switch. A spotter. Battery for the mission plus a return margin.
`urml execute` with the field adapter config; RTL from the switch overrides
anything URML sends. Afterwards, transcribe date, board, firmware string, and
outcome into `docs/launch/claims-audit.md`.

## Files used in this walkthrough

- [`examples/drone/pixhawk-ardupilot.manifest.yaml`](../../examples/drone/pixhawk-ardupilot.manifest.yaml),
  [`pixhawk-ardupilot.adapter.yaml`](../../examples/drone/pixhawk-ardupilot.adapter.yaml):
  the bare-autopilot manifest and the USB adapter config.
- [`examples/drone/bench-battery.urml.yaml`](../../examples/drone/bench-battery.urml.yaml):
  the read-only bench program.
- [`examples/drone/bench-hop.urml.yaml`](../../examples/drone/bench-hop.urml.yaml):
  the flight program the autopilot refuses on the bench.
- [`reference/ardupilot-runtime/`](../../reference/ardupilot-runtime/):
  the adapter, its README, and the three gated test tiers.
- [`tools/scripts/geocode_locations.py`](../../tools/scripts/geocode_locations.py):
  the configuration-time address resolver.

## Related reading

- [sentence-to-flight.md](sentence-to-flight.md): the PX4 SITL version.
- [RFC-0041](../rfcs/0041-ardupilot-integration.md): the ArduPilot runtime proposal this page implements.
- [RFC-0250](../rfcs/0250-substrate-autopilot-class.md): why drone manifests declare `substrate.autopilot_class`.
