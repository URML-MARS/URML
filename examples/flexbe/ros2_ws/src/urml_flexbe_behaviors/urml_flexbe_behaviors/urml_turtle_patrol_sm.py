"""URML Turtle Patrol — a FlexBE behavior driving turtlesim via URML.

A minimal HFSM that demonstrates the URML <-> FlexBE seam end to end:

    [Approve Plan] --approved--> [Run URML Patrol] --done--> finished
         |                              |  \\--refused--> failed
         \\--rejected--> failed         \\--failed--> failed

The operator approves the plan (FlexBE collaborative autonomy — the human gate),
then ``ExecuteUrmlState`` dispatches a validated URML program through the
ExecuteURML action (URML's validate-before-actuate static gate). This mirrors
Fig. 5 of Conner et al., "Capability-based Robot Controller Synthesis" — an
operator approving a plan before actuation — with URML supplying the validated,
typed intent.

The program + manifest are inlined here so the behavior is self-contained; they
mirror ``examples/flexbe/turtle-patrol.urml.yaml`` and
``examples/flexbe/turtle.manifest.yaml``. Run the hermetic check with:

    urml execute examples/flexbe/turtle-patrol.urml.yaml \\
      -m examples/flexbe/turtle.manifest.yaml --profile home --no-policy --adapter mock

Targets flexbe_behavior_engine on ROS 2 Jazzy / Kilted / Rolling.
"""

from flexbe_core import Autonomy, Behavior, OperatableStateMachine
from flexbe_states.operator_decision_state import OperatorDecisionState
from urml_flexbe_states.execute_urml_state import ExecuteUrmlState

# A 2D mobile base ("the turtle") and a two-waypoint patrol. Compact mirrors of
# the canonical files under examples/flexbe/.
TURTLE_MANIFEST = """
manifest_version: "0.1"
robot_id: turtlesim_1
description: A turtlesim 2D mobile base for the URML FlexBE worked example.
frames:
  - { name: site, parent: null }
  - { name: base_link, parent: site }
declared_locations:
  - { name: waypoint_a, pose: { x: 8.0, y: 3.0, z: 0.0 }, frame: site }
  - { name: waypoint_b, pose: { x: 3.0, y: 8.0, z: 0.0 }, frame: site }
  - { name: home, pose: { x: 5.5, y: 5.5, z: 0.0 }, frame: site }
mobility:
  drive_type: differential
  max_velocity: 1.0
  station_keeping: false
provenance:
  manifest_attestation: self_declared
  components:
    - id: turtlesim_base
      role: critical
      vendor: open_robotics
      country_of_origin: US
      country_of_final_assembly: US
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/turtlesim_base.cdx.json
        sha256: "5555555555555555555555555555555555555555555555555555555555555555"
"""

TURTLE_PROGRAM = """
profile: home
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - move_to: { location: waypoint_a }
    - move_to: { location: waypoint_b }
    - move_to: { location: home }
"""


class URMLTurtlePatrolSM(Behavior):
    """Operator-approved URML patrol over turtlesim."""

    def __init__(self, node):
        super().__init__()
        self.name = "URML Turtle Patrol"
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
                    hint="Approve the URML turtle patrol before it actuates?",
                    suggestion="approved",
                ),
                transitions={"approved": "Run URML Patrol", "rejected": "failed"},
                autonomy={"approved": Autonomy.Full, "rejected": Autonomy.Full},
            )

            OperatableStateMachine.add(
                "Run URML Patrol",
                ExecuteUrmlState(
                    manifest_yaml=TURTLE_MANIFEST,
                    program_yaml=TURTLE_PROGRAM,
                    profiles=["home"],
                    no_policy=True,
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
