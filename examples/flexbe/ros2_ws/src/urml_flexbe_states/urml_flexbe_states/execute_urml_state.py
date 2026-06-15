"""ExecuteUrmlState — a FlexBE state that dispatches a validated URML program.

This realizes the RFC-0474 seam David Conner picked: a FlexBE state calls the
URML ``ExecuteURML`` ROS 2 action, which validates the program against the
robot's capability manifest + safety envelope *before* actuating, and surfaces
the verdict. The operator-in-the-loop engine therefore gets URML's
validate-before-actuate gate per state — a static gate behind FlexBE's human
gate.

Outcomes:
    done     — the URML program executed successfully.
    failed   — a primitive failed during execution (substrate-side).
    refused  — the validator rejected the program (no actuation happened);
               ``userdata.urml_verdict`` carries the rendered reason so the
               operator UI can show why.

The state is parameterized so a behavior can either ship a fixed program
(``program_yaml``) or a natural-language sentence (``sentence``, translated by
the server's configured provider). The manifest is required.
"""

from __future__ import annotations

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyActionClient
from urml_ros2_msgs.action import ExecuteURML


class ExecuteUrmlState(EventState):
    """Send one URML goal to the ExecuteURML action server and map its result.

    Parameters:
        manifest_yaml  The robot's capability manifest (YAML/JSON string). Required.
        program_yaml   A URML program (YAML/JSON string). Use this OR ``sentence``.
        sentence       A natural-language request (translated server-side).
        envelope_yaml  Optional safety envelope (YAML/JSON string).
        profiles       List of active URML profiles, e.g. ["home"].
        no_policy      Skip the compliance-policy pass (hero-demo path).
        action_topic   The ExecuteURML action name (default "execute_urml").
    """

    def __init__(
        self,
        manifest_yaml,
        program_yaml="",
        sentence="",
        envelope_yaml="",
        profiles=None,
        no_policy=False,
        action_topic="execute_urml",
    ):
        super().__init__(
            outcomes=["done", "failed", "refused"],
            output_keys=["urml_verdict", "urml_audit_log"],
        )
        self._manifest_yaml = manifest_yaml
        self._program_yaml = program_yaml
        self._sentence = sentence
        self._envelope_yaml = envelope_yaml
        self._profiles = list(profiles) if profiles else []
        self._no_policy = bool(no_policy)
        self._topic = action_topic
        self._client = ProxyActionClient({self._topic: ExecuteURML})
        self._return = None  # latched outcome across execute() calls

    def execute(self, userdata):
        # Latch: once we have an outcome, keep returning it (FlexBE re-invokes
        # execute() until a non-None outcome is returned).
        if self._return is not None:
            return self._return

        if not self._client.has_result(self._topic):
            return None

        result = self._client.get_result(self._topic)
        userdata.urml_verdict = result.reason
        userdata.urml_audit_log = result.audit_log_json

        if result.refused:
            Logger.logwarn(f"URML refused the program: {result.reason}")
            self._return = "refused"
        elif result.success:
            Logger.loginfo(f"URML executed {result.steps_executed} step(s) successfully.")
            self._return = "done"
        else:
            Logger.logwarn(f"URML execution failed: {result.reason}")
            self._return = "failed"
        return self._return

    def on_enter(self, userdata):
        self._return = None
        goal = ExecuteURML.Goal()
        goal.program_yaml = self._program_yaml
        goal.sentence = self._sentence
        goal.manifest_yaml = self._manifest_yaml
        goal.envelope_yaml = self._envelope_yaml
        goal.profiles = self._profiles
        goal.no_policy = self._no_policy
        try:
            self._client.send_goal(self._topic, goal)
        except Exception as exc:  # noqa: BLE001 — surface as a clean failure
            Logger.logerr(f"Failed to send ExecuteURML goal: {exc}")
            self._return = "failed"

    def on_exit(self, userdata):
        # Cancel an in-flight goal if the state is preempted by the operator.
        if not self._client.has_result(self._topic) and self._client.is_active(self._topic):
            self._client.cancel(self._topic)
            Logger.loginfo("Cancelled in-flight URML goal on state exit.")

    def on_stop(self):
        pass
