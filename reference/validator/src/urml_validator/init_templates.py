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

link_loss_policy: halt_and_report
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
# Profile registry
# ---------------------------------------------------------------------------


PROJECT_TEMPLATES = {
    "home": home_project,
    "industrial": industrial_project,
}
