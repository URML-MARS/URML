"""URML UR-3e Pick-Place — a FlexBE behavior driving a Universal Robots arm via URML.

A minimal HFSM that demonstrates the URML <-> FlexBE seam on the hardware David
Conner (CHRISLab, CNU) pointed at: CNURobotics/flexbe_ur_demo, a UR-3e driven
through flexbe_universal_robots + flexbe_moveit2 + the UR ROS 2 driver.

    [Approve Plan] --approved--> [Run URML Pick-Place] --done--> finished
         |                              |  \\--refused--> failed
         \\--rejected--> failed         \\--failed--> failed

The operator approves the plan (FlexBE collaborative autonomy — the human gate),
then ``ExecuteUrmlState`` dispatches a validated URML program through the
ExecuteURML action (URML's validate-before-actuate static gate). URML checks the
pick-and-place against the cell's capability manifest and safety envelope — the
gripper's force ceiling, the declared object vocabulary, the named stations,
the safety-door interlock — *before* MoveIt 2 plans a single motion. This is the
operator-approves-a-validated-capability shape of Fig. 5 in Conner et al.,
"Capability-based Robot Controller Synthesis," with URML supplying the typed,
admissible intent.

The program + manifest are inlined here so the behavior is self-contained; they
mirror ``examples/flexbe/ur3e-pick-place.urml.yaml`` and
``examples/flexbe/ur3e.manifest.yaml``. Run the hermetic check with:

    urml execute examples/flexbe/ur3e-pick-place.urml.yaml \\
      -m examples/flexbe/ur3e.manifest.yaml --profile industrial --adapter mock

Targets flexbe_behavior_engine on ROS 2 Jazzy / Kilted / Rolling.
"""

from flexbe_core import Autonomy, Behavior, OperatableStateMachine
from flexbe_states.operator_decision_state import OperatorDecisionState
from urml_flexbe_states.execute_urml_state import ExecuteUrmlState

# A Universal Robots UR-3e e-Series arm cell and a one-cycle red-widget
# pick-and-place. Compact mirrors of the canonical files under examples/flexbe/.
UR3E_MANIFEST = """
manifest_version: "0.1"
robot_id: ur3e_cell_1
description: A Universal Robots UR-3e e-Series arm cell for the URML FlexBE worked example.
frames:
  - { name: cell, parent: null }
  - { name: base_link, parent: cell }
declared_locations:
  - { name: pick_bin, pose: { x: 0.4, y: -0.3, z: 0.10 }, frame: cell }
  - { name: kitting_tray_red, pose: { x: -0.4, y: 0.2, z: 0.10 }, frame: cell }
  - { name: home_pose, pose: { x: 0.0, y: 0.0, z: 0.30 }, frame: cell }
declared_events: [safety_door_closed, line_ready, emergency_stop]
mobility:
  drive_type: manipulator_base
  max_velocity: 0.50
  station_keeping: true
manipulation:
  arm_count: 1
  grippers:
    - name: robotiq_2f85
      kind: servo_electric
      force_min_n: 1.0
      force_max_n: 235.0
      accepted_classes: [widget, widget_red, widget_blue, small_part]
      movable: true
  reachable_workspace_m: 0.85
perception:
  object_vocabulary: [widget, widget_red, widget_blue, small_part]
outputs:
  named_endpoints: [line_controller]
provenance:
  manifest_attestation: self_declared
  components:
    - id: ur_controller
      role: critical
      vendor: universal_robots
      country_of_origin: DK
      country_of_final_assembly: DK
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/ur_controller.cdx.json
        sha256: "2424242424242424242424242424242424242424242424242424242424242424"
"""

UR3E_PROGRAM = """
profile: industrial
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - wait_for: { condition: { event: safety_door_closed } }
    - pick_from:
        source: pick_bin
        object: widget_red
        attributes: { color: red }
        force: firm
        store_as: red_widget
    - place_at: { target: kitting_tray_red, held: $red_widget, mode: place }
    - move_to: { location: home_pose }
    - report:
        to: line_controller
        facts: { cycle: pick_red_to_tray, result: ok }
        status: success
"""


class URMLUr3ePickPlaceSM(Behavior):
    """Operator-approved URML pick-and-place over a Universal Robots UR-3e."""

    def __init__(self, node):
        super().__init__()
        self.name = "URML UR-3e Pick-Place"
        self.add_parameter("action_topic", "execute_urml")
        # FlexBE 4: hand the node to states that need ROS handles.
        ExecuteUrmlState.initialize_ros(node)
        OperatorDecisionState.initialize_ros(node)

    def create(self):
        action_topic = self.action_topic
        sm = OperatableStateMachine(outcomes=["finished", "failed"])

        with sm:
            OperatableStateMachine.add(
                "Approve Plan",
                OperatorDecisionState(
                    outcomes=["approved", "rejected"],
                    hint="Approve the URML UR-3e pick-and-place before it actuates?",
                    suggestion="approved",
                ),
                transitions={"approved": "Run URML Pick-Place", "rejected": "failed"},
                autonomy={"approved": Autonomy.Full, "rejected": Autonomy.Full},
            )

            OperatableStateMachine.add(
                "Run URML Pick-Place",
                ExecuteUrmlState(
                    manifest_yaml=UR3E_MANIFEST,
                    program_yaml=UR3E_PROGRAM,
                    profiles=["industrial"],
                    no_policy=False,
                    action_topic=action_topic,
                ),
                transitions={
                    "done": "finished",
                    "failed": "failed",
                    "refused": "failed",
                },
                autonomy={
                    "done": Autonomy.Off,
                    "failed": Autonomy.Off,
                    "refused": Autonomy.Off,
                },
            )

        return sm
