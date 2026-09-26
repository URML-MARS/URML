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

The program is inlined here so the behavior is self-contained; it mirrors
``examples/flexbe/turtle-patrol.urml.yaml``. The goal does not carry the
manifest or envelope: the action server pins ``examples/flexbe/turtle.manifest.yaml``
and ``examples/flexbe/turtle.envelope.yaml`` at start (launch arguments
``manifest_path`` and ``envelope_path``), so a goal cannot choose its own
limits. Run the hermetic check with:

    urml execute examples/flexbe/turtle-patrol.urml.yaml \\
      -m examples/flexbe/turtle.manifest.yaml -e examples/flexbe/turtle.envelope.yaml \\
      --profile home --adapter mock

Targets flexbe_behavior_engine on ROS 2 Jazzy / Kilted / Rolling.
"""

from flexbe_core import Autonomy, Behavior, OperatableStateMachine
from flexbe_states.operator_decision_state import OperatorDecisionState
from urml_flexbe_states.execute_urml_state import ExecuteUrmlState

# A two-waypoint patrol for the turtle (a 2D mobile base). Compact mirror of
# the canonical program under examples/flexbe/.
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
                    program_yaml=TURTLE_PROGRAM,
                    profiles=["home"],
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
