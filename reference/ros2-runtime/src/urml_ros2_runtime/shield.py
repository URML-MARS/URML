"""RFC-0667: the envelope shield — runtime enforcement of monitorable properties.

The validator proves a program *may* run; the shield keeps the envelope
true *while* it runs. Two enforcement surfaces share one `Shield`:

- `URMLRuntime(..., shield=...)` hooks the shield into the per-step
  dispatch loop: gate before each primitive, sample telemetry after it,
  halt on a critical violation.
- `ShieldedAdapter` interposes on a raw adapter, so ANY driver — a VLA
  policy, an external agent, hand-written code — passes through the same
  envelope checks without involving `URMLRuntime` at all. This is the
  policy-agnostic form: URML does not need to be the planner to be the
  safety boundary.

Severity mapping (normative, RFC-0667): `info` violations are recorded;
`warning` violations are recorded and surfaced in the audit trail;
`critical` violations veto further actuation (`ShieldViolationError` from
the gate) and halt a running program.

The shield never reads a clock; timestamps come from the adapter's samples
(`TelemetryAdapter`), which keeps every run reproducible. Without a
telemetry surface the shield degrades to gate-only enforcement: it can
still block dispatch after an externally pushed violation, but it cannot
see state on its own. Step-boundary sampling is honest but coarse — a
spike inside one long blocking command is invisible until the command
returns; substrates with an internal control loop should push samples at
their native cadence via `observe()`.
"""

from __future__ import annotations

from typing import Any

from urml_validator.monitor import (
    CompiledProperty,
    OnlineMonitor,
    PropertyVerdict,
    Sample,
    Violation,
    compile_envelope_monitors,
)

from urml_ros2_runtime.substrate.base import TelemetryAdapter

__all__ = ["Shield", "ShieldViolationError", "ShieldedAdapter"]


class ShieldViolationError(RuntimeError):
    """A critical envelope property is violated; further actuation is vetoed."""

    def __init__(self, message: str, *, violations: list[Violation]) -> None:
        super().__init__(message)
        self.violations = violations


class Shield:
    """One deployment's envelope, armed: compiled properties plus their monitor."""

    def __init__(
        self,
        envelope: dict[str, Any] | None,
        *,
        properties: list[CompiledProperty] | None = None,
    ) -> None:
        """Arm a shield for an envelope.

        Args:
            envelope:   The deployment's safety envelope (raw dict form).
                        Declared monitorable properties and static numeric
                        caps compile per `compile_envelope_monitors`.
            properties: Pre-compiled properties to monitor instead; when
                        given, `envelope` is not compiled (callers that
                        already ran the compiler, or tests).
        """
        self._properties = properties if properties is not None else compile_envelope_monitors(envelope)
        self._monitor = OnlineMonitor(self._properties)
        self._observed_any = False

    @property
    def properties(self) -> list[CompiledProperty]:
        return list(self._properties)

    def observe(self, sample: Sample) -> list[Violation]:
        """Feed one telemetry sample; returns every violation now standing."""
        self._observed_any = True
        self._monitor.observe(sample)
        return self._monitor.violations()

    def verdicts(self) -> tuple[PropertyVerdict, ...]:
        return self._monitor.verdicts()

    def violations(self) -> list[Violation]:
        return self._monitor.violations()

    def critical_violations(self) -> list[Violation]:
        return [v for v in self._monitor.violations() if v.severity == "critical"]

    def gate(self, primitive: str, arguments: dict[str, Any] | None = None) -> None:
        """Refuse dispatch while any critical property stands violated.

        Called immediately before every primitive dispatch. `info` and
        `warning` violations never block; they are in `violations()` and the
        runtime's audit trail.
        """
        critical = self.critical_violations()
        if critical:
            names = ", ".join(v.name for v in critical)
            raise ShieldViolationError(
                f"envelope shield vetoes {primitive!r}: critical property violated ({names})",
                violations=critical,
            )

    def audit_entries(self) -> list[dict[str, Any]]:
        """Violations in the runtime audit-log dict shape."""
        return [
            {
                "method": "shield.violation",
                "property": v.name,
                "severity": v.severity,
                "expression": v.expression,
                "at_time": v.at_time,
            }
            for v in self._monitor.violations()
        ]


#: Adapter method names the shield gates. The frozen ROSAdapter surface
#: (RFC-0014) plus the optional side-protocol actuation verbs. Read-only
#: verbs (detection, measurement, capture, report, speech) are gated too:
#: after a critical violation the robot's job is to stop acting, not to
#: keep working through the rest of its repertoire.
_GUARDED_METHODS = frozenset(
    {
        "send_navigation_goal",
        "send_docking_goal",
        "send_manipulation_goal",
        "query_detection",
        "run_scan",
        "take_measurement",
        "capture_media",
        "wait_for_condition",
        "wait_passively",
        "emit_report",
        "emit_speech",
        "acquire_speech",
        "call_named_program",
        "send_takeoff_goal",
        "send_land_goal",
        "send_return_to_home_goal",
        # Optional side-protocols (RFC-0020 / RFC-0630 / RFC-0017).
        "plan_trajectory",
        "follow_trajectory_goal",
        "drive_by",
        "turn_by",
        "set_output_line",
    }
)


class ShieldedAdapter:
    """Wrap any adapter so every call passes through the envelope shield.

    Attribute access delegates to the wrapped adapter, so the wrapper
    exposes exactly the capability surface the inner adapter has (an inner
    without `drive_by` still fails `isinstance(..., RelativeMotionAdapter)`
    through the wrapper). Guarded methods are gated before the call and,
    when the inner adapter is a `TelemetryAdapter`, followed by a telemetry
    sample; a fresh critical violation raises `ShieldViolationError` before
    the *next* action can begin.

    This is the VLA-shield shape: the driver on top can be anything that
    calls adapter methods. URML validates programs it is given; the shield
    guards even the actuation URML never saw as a program.
    """

    def __init__(self, inner: object, shield: Shield) -> None:
        # object.__setattr__-free plain init; the wrapper holds exactly two slots.
        self._inner = inner
        self._shield = shield

    @property
    def shield(self) -> Shield:
        return self._shield

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._inner, name)  # AttributeError propagates: surface mirrors inner
        if name not in _GUARDED_METHODS or not callable(attr):
            return attr

        def _guarded(*args: Any, **kwargs: Any) -> Any:
            self._shield.gate(name, kwargs or None)
            result = attr(*args, **kwargs)
            if isinstance(self._inner, TelemetryAdapter):
                fresh = self._shield.observe(self._inner.sample_signals())
                critical = [v for v in fresh if v.severity == "critical"]
                if critical:
                    names = ", ".join(v.name for v in critical)
                    raise ShieldViolationError(
                        f"envelope shield halted after {name!r}: critical property violated ({names})",
                        violations=critical,
                    )
            return result

        return _guarded
