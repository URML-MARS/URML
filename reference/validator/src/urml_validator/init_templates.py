"""Starter-project templates for `urml init`.

Each helper returns a dict mapping a relative file path to the file's
content. The CLI writes every entry into the target directory.

Templates are inlined as Python strings rather than bundled YAML files
because (a) they're small, (b) keeping them in-source means they
version-lock with the validator, and (c) no extra hatch include logic.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Home profile
# ---------------------------------------------------------------------------


_HOME_MANIFEST = """\
# Capability manifest for a TurtleBot 4 configured for the home profile.
# Edit to match your robot. See spec/layer-1-hal/ for the field reference.

manifest_version: "0.1"
robot_id: turtlebot4_home
description: Indoor service robot with depth camera and a small gripper.

frames:
  - name: map
    parent: null
  - name: base_link
    parent: map

declared_locations:
  - name: kitchen
    pose: { x: 3.2, y: 1.0 }
    frame: map
  - name: user
    pose: { x: 0.5, y: 0.5 }
    frame: map
  - name: charging_dock
    pose: { x: 0.0, y: 0.0 }
    frame: map

declared_events:
  - user_present
  - emergency_stop

mobility:
  drive_type: differential
  max_velocity: 0.46
  station_keeping: true

manipulation:
  arm_count: 1
  grippers:
    - name: claw_demo
      kind: servo_electric
      force_min_n: 0.5
      force_max_n: 5.0
      accepted_classes: [mug, cup, small_object]
      movable: true
  reachable_workspace_m: 0.35

perception:
  cameras:
    - name: oakd_rgb
      movable: false
      supports_photo: true
      supports_video: true
      max_resolution: "1080p"
  sensors: []
  object_vocabulary:
    - mug
    - cup
    - person

docking_stations:
  - name: charging_dock
    pose: { x: 0.0, y: 0.0 }
    frame: map
    services: [park, charge]

outputs:
  named_endpoints: []

# Hardware provenance (RFC-0004). Optional: when present, the validator's
# Pass 5 checks the bundled US-federal compliance policy against this block.
# Pass `urml validate --no-policy` to skip the check, or `--policy <file>`
# to override with a deployment-specific rule set.
#
# TODO: fill in real provenance for your robot before any deployment that
# claims compliance. The placeholder values below illustrate the shape and
# are deliberately fictional ("example_*" vendor IDs); they are not a
# certification of any real product.
provenance:
  manifest_attestation: self_declared
  components:
    - id: drive_controller
      role: critical
      vendor: example_drive_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/drive_controller.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
    - id: depth_camera
      role: critical
      vendor: example_camera_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/depth_camera.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"

# Abstract connectivity (RFC-0006). Optional: declares the link roles this
# robot supports. Roles are abstract -- the transport medium (WiFi/5G/RF/...)
# is the substrate's concern, never URML's. The envelope's link_loss_policy
# governs what happens when a declared link is lost.
connectivity:
  links:
    - role: command_link
      required_for_operation: false   # a validated program runs offline
      autonomous_when_lost: false
      assurance_class: best_effort
"""


_HOME_ENVELOPE = """\
# Default home-profile safety envelope. Tightens manifest defaults.

envelope_version: "0.1"
deployment_id: home_demo
description: Default home-profile envelope.

max_velocity: 0.4
max_grip_force_n: 3.0

people_occupancy_zones: []
geofences: []

# RFC-0006: structured per-role link-loss policy. If the command link drops,
# the robot halts and reports rather than continuing blind.
link_loss_policy:
  - role: command_link
    action: halt_and_report
"""


_HOME_PROGRAM = """\
# URML program -- generated from the natural-language prompt below.
# This is the canonical red-mug example from MANIFESTO.md §A Concrete Example.

profile: home
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - move_to:
        location: kitchen
    - detect:
        object: mug
        attributes:
          color: red
        store_as: target_mug
    - grasp:
        target: $target_mug
        force: gentle
    - move_to:
        location: user
        carrying: $target_mug
    - release:
        mode: hand_to_user
"""


_HOME_PROMPT = "Bring me the red mug from the kitchen.\n"


_HOME_README = """\
# {project_name}

A starter URML project for the **home** profile.

## Files

- `manifest.yaml` -- the robot's capability declaration (edit to match your platform).
- `envelope.yaml` -- the deployment safety envelope (tightens manifest defaults).
- `program.urml.yaml` -- a sample URML program; the red-mug fetch example.
- `prompt.en.txt` -- the natural-language request that would produce that program.
- `Makefile` -- common URML commands.

## What you can run today

```bash
# Validate the sample program against the manifest + envelope:
urml validate program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile home

# See the system prompt the LLM bridge would send for this robot
# (no API key required):
urml emit-prompt --manifest manifest.yaml --envelope envelope.yaml --profile home

# Translate a natural-language request through an LLM (requires urml-llm-bridge
# and an API key):
urml translate "Bring me the red mug from the kitchen." \\
    --manifest manifest.yaml --envelope envelope.yaml --profile home \\
    --provider anthropic
```

## What to edit first

1. **`manifest.yaml`** -- replace `turtlebot4_home` with your robot's identifier;
   add any locations, objects, or sensors your robot actually has.
2. **`envelope.yaml`** -- tighten or relax the caps for your deployment.
3. **`prompt.en.txt`** -- the natural-language request you want the LLM to translate.

See the spec for field references:

- Layer 1 (manifest): https://github.com/URML-MARS/URML/tree/main/spec/layer-1-hal
- Layer 2 (primitives): https://github.com/URML-MARS/URML/tree/main/spec/layer-2-primitives
- Layer 3 (composition): https://github.com/URML-MARS/URML/tree/main/spec/layer-3-behavior
"""


_HOME_MAKEFILE = """\
# Convenience targets. Run `make help` for the list.

.PHONY: help validate emit-prompt translate clean

help:
\t@echo "validate        Validate program.urml.yaml against manifest + envelope."
\t@echo "emit-prompt     Print the system prompt the bridge would send to an LLM."
\t@echo "translate       Translate prompt.en.txt via Anthropic (requires ANTHROPIC_API_KEY)."

validate:
\turml validate program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile home

emit-prompt:
\turml emit-prompt --manifest manifest.yaml --envelope envelope.yaml --profile home

translate:
\turml translate "$$(cat prompt.en.txt)" \\
\t    --manifest manifest.yaml --envelope envelope.yaml --profile home \\
\t    --provider anthropic
"""


def home_project(project_name: str) -> dict[str, str]:
    """Return the starter file set for a home-profile project."""
    return {
        "manifest.yaml": _HOME_MANIFEST,
        "envelope.yaml": _HOME_ENVELOPE,
        "program.urml.yaml": _HOME_PROGRAM,
        "prompt.en.txt": _HOME_PROMPT,
        "README.md": _HOME_README.format(project_name=project_name),
        "Makefile": _HOME_MAKEFILE,
    }


# ---------------------------------------------------------------------------
# Industrial profile
# ---------------------------------------------------------------------------


_INDUSTRIAL_MANIFEST = """\
# Capability manifest for a single-arm pick-and-place cell.
# Edit to match your cell. See spec/layer-1-hal/ for the field reference.

manifest_version: "0.1"
robot_id: cell_a1
description: Single-arm pick-and-place cell with a wrist RGB camera.

frames:
  - name: cell
    parent: null
  - name: base_link
    parent: cell

declared_locations:
  - name: pick_bin
    pose: { x: 0.4, y: -0.3, z: 0.10 }
    frame: cell
  - name: kitting_tray_red
    pose: { x: -0.4, y: 0.2, z: 0.10 }
    frame: cell
  - name: kitting_tray_blue
    pose: { x: -0.4, y: -0.2, z: 0.10 }
    frame: cell
  - name: home_pose
    pose: { x: 0.0, y: 0.0, z: 0.30 }
    frame: cell

declared_events:
  - safety_door_closed
  - line_ready
  - emergency_stop

mobility:
  drive_type: manipulator_base
  max_velocity: 0.50
  station_keeping: true

manipulation:
  arm_count: 1
  grippers:
    - name: pneumatic_2_finger
      kind: pneumatic
      force_min_n: 1.0
      force_max_n: 25.0
      accepted_classes: [widget, widget_red, widget_blue, small_part]
      movable: true
  reachable_workspace_m: 0.85

perception:
  cameras:
    - name: wrist_rgb
      movable: true
      supports_photo: true
      supports_video: false
      max_resolution: "1080p"
  sensors:
    - name: tcp_force
      measurement_type: pressure
      range_min: 0.0
      range_max: 50.0
      units: N
  object_vocabulary:
    - widget
    - widget_red
    - widget_blue
    - small_part

docking_stations: []

outputs:
  named_endpoints:
    - line_controller

# Hardware provenance (RFC-0004). Optional: when present, the validator's
# Pass 5 checks the bundled US-federal compliance policy against this block.
# Industrial cells commonly contract for NDAA-compliant procurement; the
# provenance block lets URML enforce that statically before any program runs.
#
# TODO: fill in real provenance before any deployment that claims compliance.
# The placeholder values below are illustrative; they are not a certification
# of any real product.
provenance:
  manifest_attestation: self_declared
  components:
    - id: arm_controller
      role: critical
      vendor: example_arm_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/arm_controller.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
    - id: gripper_pneumatic
      role: critical
      vendor: example_gripper_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/gripper.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
    - id: wrist_camera
      role: critical
      vendor: example_camera_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/wrist_camera.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
"""


_INDUSTRIAL_PROGRAM = """\
# URML program -- generated from the natural-language prompt below.
# Pick-and-place cycle: detect a red widget, place it in the red tray.

profile: industrial
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - move_to:
        location: pick_bin
    - detect:
        object: widget_red
        where:
          near: pick_bin
        store_as: red_widget
    - grasp:
        target: $red_widget
        force: firm
    - move_to:
        location: kitting_tray_red
        carrying: $red_widget
    - release:
        mode: place
        at: kitting_tray_red
    - move_to:
        location: home_pose
    - report:
        to: line_controller
        facts:
          cycle: pick_red_to_tray
          result: ok
        status: success
"""


_INDUSTRIAL_PROMPT = "Pick a red widget from the bin and place it in the red kitting tray.\n"


_INDUSTRIAL_README = """\
# {project_name}

A starter URML project for the **industrial** profile.

## Files

- `manifest.yaml` -- the cell's capability declaration (edit to match your hardware).
- `program.urml.yaml` -- a sample URML program; the pick-red pick-and-place cycle.
- `prompt.en.txt` -- the natural-language request that would produce that program.
- `Makefile` -- common URML commands.

## What you can run today

```bash
# Validate the sample program against the manifest:
urml validate program.urml.yaml --manifest manifest.yaml --profile industrial

# See the system prompt the LLM bridge would send (no API key required):
urml emit-prompt --manifest manifest.yaml --profile industrial

# Translate a natural-language request through an LLM (requires urml-llm-bridge
# and an API key):
urml translate "Pick a red widget from the bin and place it in the red kitting tray." \\
    --manifest manifest.yaml --profile industrial \\
    --provider anthropic
```

## What to edit first

1. **`manifest.yaml`** -- replace `cell_a1` with your cell's identifier; add the
   real declared locations, object vocabulary, and gripper details.
2. **`prompt.en.txt`** -- the natural-language request you want translated.

See the spec for field references:

- Layer 1 (manifest): https://github.com/URML-MARS/URML/tree/main/spec/layer-1-hal
- Layer 2 (primitives): https://github.com/URML-MARS/URML/tree/main/spec/layer-2-primitives
- Layer 3 (composition): https://github.com/URML-MARS/URML/tree/main/spec/layer-3-behavior
"""


_INDUSTRIAL_MAKEFILE = """\
# Convenience targets. Run `make help` for the list.

.PHONY: help validate emit-prompt translate clean

help:
\t@echo "validate        Validate program.urml.yaml against the manifest."
\t@echo "emit-prompt     Print the system prompt the bridge would send to an LLM."
\t@echo "translate       Translate prompt.en.txt via Anthropic (requires ANTHROPIC_API_KEY)."

validate:
\turml validate program.urml.yaml --manifest manifest.yaml --profile industrial

emit-prompt:
\turml emit-prompt --manifest manifest.yaml --profile industrial

translate:
\turml translate "$$(cat prompt.en.txt)" \\
\t    --manifest manifest.yaml --profile industrial \\
\t    --provider anthropic
"""


def industrial_project(project_name: str) -> dict[str, str]:
    """Return the starter file set for an industrial-profile project."""
    return {
        "manifest.yaml": _INDUSTRIAL_MANIFEST,
        "program.urml.yaml": _INDUSTRIAL_PROGRAM,
        "prompt.en.txt": _INDUSTRIAL_PROMPT,
        "README.md": _INDUSTRIAL_README.format(project_name=project_name),
        "Makefile": _INDUSTRIAL_MAKEFILE,
    }


# ---------------------------------------------------------------------------
# Drone profile
# ---------------------------------------------------------------------------


_DRONE_MANIFEST = """\
# Capability manifest for a civilian multirotor configured for the drone profile.
# Edit to match your aircraft. See spec/layer-1-hal/ for the field reference.

manifest_version: "0.1"
robot_id: civilian_inspector
description: Civilian multirotor for roof / tower inspection.

frames:
  - name: wgs84
    parent: null
  - name: agl
    parent: wgs84

declared_locations:
  - name: home
    pose: { x: 0.0, y: 0.0, z: 0.0 }
    frame: agl
    description: Takeoff / landing position.
  - name: roof_north
    pose: { x: 10.0, y: 5.0, z: 30.0 }
    frame: agl

declared_events:
  - emergency_stop
  - low_battery

mobility:
  drive_type: multirotor
  max_velocity: 15.0
  station_keeping: true
  service_ceiling: 120.0
  max_payload: 0.5

perception:
  cameras:
    - name: downward
      movable: false
      supports_photo: true
      supports_video: true
      max_resolution: "4k"
  sensors:
    - name: rangefinder
      measurement_type: distance
      range_min: 0.5
      range_max: 50.0
      units: m
  object_vocabulary:
    - person
    - vehicle

outputs:
  named_endpoints: []

# Hardware provenance (RFC-0004). Optional: when present, the validator's
# Pass 5 checks the bundled US-federal compliance policy against this block.
# Civilian drones are explicitly covered by FCC entity-list rules and NDAA
# §889 procurement restrictions; the provenance block lets URML enforce
# that statically before any flight.
#
# TODO: fill in real provenance before any deployment that claims compliance.
# The placeholder values below are illustrative; they are not a certification
# of any real product.
provenance:
  manifest_attestation: self_declared
  components:
    - id: flight_controller
      role: critical
      vendor: example_fc_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/flight_controller.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
    - id: imaging_camera
      role: critical
      vendor: example_camera_vendor
      country_of_origin: JP
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/imaging_camera.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
    - id: rangefinder_module
      role: critical
      vendor: example_sensor_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/rangefinder.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
"""


_DRONE_ENVELOPE = """\
# Default drone-profile safety envelope. FAA Part 107-aligned defaults.

envelope_version: "0.1"
deployment_id: drone_demo
description: Default civilian drone envelope.

max_velocity: 10.0      # m/s
max_altitude: 120.0     # m AGL; FAA Part 107 default for uncertified small drones

# Spatial / behavioral defaults (geofence polygons, weather thresholds,
# people-occupancy zones) are not statically enforced in v0.1; they live
# in the substrate runtime contract.
"""


_DRONE_PROGRAM = """\
# URML program -- generated from the natural-language prompt below.
# Citizen-inspector flight: take off, fly to the north roof, capture a photo,
# return home, land.

profile: drone
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - take_off:
        altitude: 30.0
    - move_to:
        location: roof_north
    - capture:
        media: photo
        store_as: north_photo
    - return_to_home: {}
    - land: {}
"""


_DRONE_PROMPT = "Inspect the north roof for damage and bring me photos.\n"


_DRONE_README = """\
# {project_name}

A starter URML project for the **drone** profile.

## Files

- `manifest.yaml` -- the aircraft's capability declaration (edit to match your platform).
- `envelope.yaml` -- the deployment safety envelope (altitude cap, velocity cap, etc.).
- `program.urml.yaml` -- a sample URML program; the roof-inspection flight.
- `prompt.en.txt` -- the natural-language request that would produce that program.
- `Makefile` -- common URML commands.

## What you can run today

```bash
# Validate the sample program against the manifest + envelope:
urml validate program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile drone

# See the system prompt the LLM bridge would send for this aircraft
# (no API key required):
urml emit-prompt --manifest manifest.yaml --envelope envelope.yaml --profile drone

# Translate a natural-language request through an LLM (requires urml-llm-bridge
# and an API key):
urml translate "Inspect the north roof for damage and bring me photos." \\
    --manifest manifest.yaml --envelope envelope.yaml --profile drone \\
    --provider anthropic
```

## What to edit first

1. **`manifest.yaml`** -- replace `civilian_inspector` with your aircraft's identifier;
   add the real declared locations and sensor list.
2. **`envelope.yaml`** -- tighten the altitude or velocity caps for your deployment.
3. **`prompt.en.txt`** -- the natural-language request you want translated.

See the spec for field references:

- Layer 1 (manifest): https://github.com/URML-MARS/URML/tree/main/spec/layer-1-hal
- Layer 2 (primitives): https://github.com/URML-MARS/URML/tree/main/spec/layer-2-primitives
- Layer 3 (composition): https://github.com/URML-MARS/URML/tree/main/spec/layer-3-behavior
- Drone profile: https://github.com/URML-MARS/URML/tree/main/spec/profiles/drone
"""


_DRONE_MAKEFILE = """\
# Convenience targets. Run `make help` for the list.

.PHONY: help validate emit-prompt translate clean

help:
\t@echo "validate        Validate program.urml.yaml against manifest + envelope."
\t@echo "emit-prompt     Print the system prompt the bridge would send to an LLM."
\t@echo "translate       Translate prompt.en.txt via Anthropic (requires ANTHROPIC_API_KEY)."

validate:
\turml validate program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile drone

emit-prompt:
\turml emit-prompt --manifest manifest.yaml --envelope envelope.yaml --profile drone

translate:
\turml translate "$$(cat prompt.en.txt)" \\
\t    --manifest manifest.yaml --envelope envelope.yaml --profile drone \\
\t    --provider anthropic
"""


def drone_project(project_name: str) -> dict[str, str]:
    """Return the starter file set for a drone-profile project."""
    return {
        "manifest.yaml": _DRONE_MANIFEST,
        "envelope.yaml": _DRONE_ENVELOPE,
        "program.urml.yaml": _DRONE_PROGRAM,
        "prompt.en.txt": _DRONE_PROMPT,
        "README.md": _DRONE_README.format(project_name=project_name),
        "Makefile": _DRONE_MAKEFILE,
    }


# ---------------------------------------------------------------------------
# Warehouse profile
# ---------------------------------------------------------------------------


_WAREHOUSE_MANIFEST = """\
# Capability manifest for a warehouse-profile mobile manipulator AMR.
# Edit the declared locations, events, gripper, and provenance to match
# your actual deployment before validating against the bundled US-federal
# policy.

manifest_version: "0.1"
robot_id: warehouse_amr_a1
description: Mobile manipulator AMR for mixed-traffic warehouse aisles.

frames:
  - name: site
    parent: null
  - name: base_link
    parent: site

declared_locations:
  - name: shelf_a3
    pose: { x: 6.0, y: -2.0, z: 0.50 }
    frame: site
  - name: conveyor_a
    pose: { x: 0.0, y: 4.0, z: 0.40 }
    frame: site
  - name: charge_dock_1
    pose: { x: -4.0, y: 0.0, z: 0.0 }
    frame: site

declared_events:
  - partner_ready
  - partner_unavailable
  - obstacle_detected
  - path_clear
  - dock_acquired
  - emergency_stop

mobility:
  drive_type: differential
  max_velocity: 1.5
  station_keeping: false

manipulation:
  arm_count: 1
  grippers:
    - name: gripper_2_finger
      kind: servo_electric
      force_min_n: 1.0
      force_max_n: 235.0
      accepted_classes: [tote, parcel, small_part]
      movable: true
  reachable_workspace_m: 0.85

perception:
  cameras:
    - name: front_rgbd
      movable: false
      supports_photo: true
      supports_video: true
      supports_stream: false
      max_resolution: "1080p"
  sensors:
    - name: front_lidar
      measurement_type: distance
      range_min: 0.05
      range_max: 100.0
      units: m
    - name: battery
      measurement_type: voltage
      range_min: 0.0
      range_max: 100.0
      units: percent
  object_vocabulary:
    - tote
    - parcel
    - small_part

docking_stations:
  - name: charge_dock_1
    pose: { x: -4.0, y: 0.0, z: 0.0 }
    frame: site
    services: [dock, park]
  - name: conveyor_a
    pose: { x: 0.0, y: 4.0, z: 0.40 }
    frame: site
    services: [dock]

outputs:
  named_endpoints:
    - fleet_manager

# Hardware provenance (RFC-0004). The bundled default US-federal policy
# checks this block in Pass 5. Replace the placeholder values with real
# component data before any deployment that claims compliance.
provenance:
  manifest_attestation: self_declared
  components:
    - id: amr_base
      role: critical
      vendor: example_amr_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/amr_base.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
    - id: arm_controller
      role: critical
      vendor: example_arm_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/arm_controller.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
    - id: front_lidar
      role: critical
      vendor: example_lidar_vendor
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/front_lidar.cdx.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
"""


_WAREHOUSE_ENVELOPE = """\
# Default safety envelope for a warehouse deployment. Edit to set the
# aisle speed cap, people-occupancy zones, and any link-loss policy your
# deployment requires.

envelope_version: "0.1"
deployment_id: warehouse_demo
description: Default warehouse envelope.

max_velocity: 1.2
max_grip_force_n: 50.0

people_occupancy_zones: []
geofences: []

link_loss_policy: []
"""


_WAREHOUSE_PROGRAM = """\
# URML program -- generated from the natural-language prompt below.
# Pick a tote from the shelf, place it on the outbound conveyor, report.

profile: warehouse
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - pick_from:
        source: shelf_a3
        object: tote
        force: gentle
        store_as: shelf_tote
    - place_at:
        target: conveyor_a
        held: $shelf_tote
        mode: place
    - report:
        to: fleet_manager
        facts:
          cycle: shelf_to_conveyor
          result: ok
        status: success
"""


_WAREHOUSE_PROMPT = "Pick a tote from shelf A3 and place it on the outbound conveyor.\\n"


_WAREHOUSE_README = """\
# {project_name}

A starter URML project for the **warehouse** profile.

## Files

- `manifest.yaml` -- the AMR's capability declaration (edit to match your hardware).
- `envelope.yaml` -- safety envelope (aisle speed cap, people-occupancy zones).
- `program.urml.yaml` -- a sample URML program; pick-to-conveyor cycle.
- `prompt.en.txt` -- the natural-language request that would produce that program.
- `Makefile` -- common URML commands.

## What you can run today

```bash
# Validate the sample program against the manifest and envelope:
urml validate program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile warehouse

# See the system prompt the LLM bridge would send (no API key required):
urml emit-prompt --manifest manifest.yaml --profile warehouse

# Translate a natural-language request through an LLM (requires urml-llm-bridge
# and an API key):
urml translate "Pick a tote from shelf A3 and place it on the outbound conveyor." \\\\
    --manifest manifest.yaml --envelope envelope.yaml --profile warehouse \\\\
    --provider anthropic
```

## What to edit first

1. **`manifest.yaml`** -- replace `warehouse_amr_a1` with your AMR's identifier; add
   the real declared locations (aisles, shelves, handoff docks, conveyor stations),
   declared events, gripper details, and per-component provenance.
2. **`envelope.yaml`** -- add `people_occupancy_zones` for any floor area where
   operators or other traffic may share space with the AMR. The warehouse profile
   spec elevates this from optional to required for mixed-traffic deployments.
3. **`prompt.en.txt`** -- the natural-language request you want translated.

See the spec for field references:

- Layer 1 (manifest): https://github.com/URML-MARS/URML/tree/main/spec/layer-1-hal
- Layer 2 (primitives): https://github.com/URML-MARS/URML/tree/main/spec/layer-2-primitives
- Layer 3 (composition): https://github.com/URML-MARS/URML/tree/main/spec/layer-3-behavior
- Warehouse profile: https://github.com/URML-MARS/URML/tree/main/spec/profiles/warehouse
"""


_WAREHOUSE_MAKEFILE = """\
# Convenience targets. Run `make help` for the list.

.PHONY: help validate emit-prompt translate clean

help:
\\t@echo "validate        Validate program.urml.yaml against the manifest and envelope."
\\t@echo "emit-prompt     Print the system prompt the bridge would send to an LLM."
\\t@echo "translate       Translate prompt.en.txt via Anthropic (requires ANTHROPIC_API_KEY)."

validate:
\\turml validate program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile warehouse

emit-prompt:
\\turml emit-prompt --manifest manifest.yaml --profile warehouse

translate:
\\turml translate "$$(cat prompt.en.txt)" \\\\
\\t    --manifest manifest.yaml --envelope envelope.yaml --profile warehouse \\\\
\\t    --provider anthropic
"""


def warehouse_project(project_name: str) -> dict[str, str]:
    """Return the starter file set for a warehouse-profile project."""
    return {
        "manifest.yaml": _WAREHOUSE_MANIFEST,
        "envelope.yaml": _WAREHOUSE_ENVELOPE,
        "program.urml.yaml": _WAREHOUSE_PROGRAM,
        "prompt.en.txt": _WAREHOUSE_PROMPT,
        "README.md": _WAREHOUSE_README.format(project_name=project_name),
        "Makefile": _WAREHOUSE_MAKEFILE,
    }


# ---------------------------------------------------------------------------
# Profile registry
# ---------------------------------------------------------------------------


PROJECT_TEMPLATES = {
    "home": home_project,
    "industrial": industrial_project,
    "drone": drone_project,
    "warehouse": warehouse_project,
}
