"""RFC-0668: the rehearsal gate — roll a validated program out in simulation
and evaluate the recorded trace against the envelope before any real robot moves.

```
validated program --> sim adapter (records a trace) --> monitor evaluation
                                                              |
                                            critical violation? --> gate FAILS,
                                                                    real execution blocked
```

The gate is substrate-neutral: any adapter that satisfies the frozen
`ROSAdapter` Protocol and exposes recorded samples (`TraceRecorder`)
qualifies as a rehearsal backend. Two reference backends exist:

- `KinematicRehearsalAdapter` (here) — hermetic, zero dependencies. It
  synthesizes a *declared, synthetic* motion profile (cruise speed, climb
  rate) rather than simulating physics. It exists so the gate runs in CI
  and on machines without a simulator, and so rehearsal has a floor that
  never depends on an optional extra.
- `RecordingMujocoAdapter` (`urml_mujoco_runtime.recording`) — real
  physics, per-tick sampling, optional `[sim]` extra.

A passed rehearsal is evidence, not a guarantee: the gate proves the
program's *simulated* trace keeps the envelope, under whichever motion
model the backend implements. The CLI banner says which model that was.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field
from urml_validator.monitor import (
    OnlineMonitor,
    Sample,
    Violation,
    compile_envelope_monitors,
)
from urml_validator.schemas.program import URMLProgram

from urml_ros2_runtime.runtime import URMLRuntime
from urml_ros2_runtime.substrate.mock import MockROSAdapter

__all__ = [
    "KinematicProfile",
    "KinematicRehearsalAdapter",
    "RehearsalReport",
    "TraceRecorder",
    "rehearse",
]


@runtime_checkable
class TraceRecorder(Protocol):
    """Anything that recorded a signal trace during a rehearsal run."""

    def samples(self) -> tuple[Sample, ...]:
        """The recorded trace, in observation order."""
        ...


@dataclass(frozen=True)
class RehearsalReport:
    """The outcome of one rehearsal run.

    `passed` is the gate: the simulated execution succeeded AND no critical
    envelope property was violated on the recorded trace. Warning and info
    violations are reported but do not fail the gate, mirroring the
    RFC-0667 severity mapping.
    """

    passed: bool
    sim_success: bool
    steps_executed: int
    trace_len: int
    properties_checked: int
    violations: tuple[Violation, ...] = ()
    notes: tuple[str, ...] = ()

    def critical_violations(self) -> tuple[Violation, ...]:
        return tuple(v for v in self.violations if v.severity == "critical")

    def to_payload(self) -> dict[str, Any]:
        """JSON-serializable form for CLI `--json` output."""
        return {
            "passed": self.passed,
            "sim_success": self.sim_success,
            "steps_executed": self.steps_executed,
            "trace_len": self.trace_len,
            "properties_checked": self.properties_checked,
            "violations": [
                {
                    "property": v.name,
                    "severity": v.severity,
                    "expression": v.expression,
                    "at_time": v.at_time,
                }
                for v in self.violations
            ],
            "notes": list(self.notes),
        }


def rehearse(
    program: dict[str, Any] | URMLProgram,
    manifest: dict[str, Any],
    envelope: dict[str, Any] | None = None,
    *,
    adapter: Any,
    recorder: TraceRecorder | None = None,
    profiles: tuple[str, ...] = (),
    revalidate: bool = True,
) -> RehearsalReport:
    """Roll the program out on a simulation adapter and evaluate the trace.

    Args:
        program:    The URML program. Must already be validator-accepted;
                    with `revalidate=True` (default) the runtime checks
                    again (defense-in-depth). The CLI passes False because
                    it validates explicitly with the caller's chosen policy.
        manifest:   The robot's capability manifest.
        envelope:   The deployment safety envelope; its monitorable
                    properties and static caps are what the gate checks.
        adapter:    The rehearsal backend (a `ROSAdapter` implementation).
        recorder:   Where the trace comes from. Defaults to the adapter
                    itself when it satisfies `TraceRecorder`.
        profiles:   Active URML profiles.
        revalidate: Forwarded to `URMLRuntime`.

    An envelope with no compilable properties yields a gate that passes on
    simulated execution success alone, with a note saying nothing was
    checked. An envelope *with* properties but an empty recorded trace
    fails the gate: no evidence is not passing evidence.
    """
    if recorder is None:
        if not isinstance(adapter, TraceRecorder):
            raise TypeError(
                "rehearse() needs a trace: pass a recorder, or use an adapter "
                "that satisfies TraceRecorder (KinematicRehearsalAdapter, "
                "RecordingMujocoAdapter)."
            )
        recorder = adapter

    runtime = URMLRuntime(adapter, revalidate=revalidate)
    result = runtime.execute(program, manifest, envelope, profiles=profiles)

    properties = compile_envelope_monitors(envelope)
    notes: list[str] = []
    if not properties:
        notes.append("envelope declares no monitorable properties or static caps; the gate checked execution only")
        return RehearsalReport(
            passed=result.success,
            sim_success=result.success,
            steps_executed=result.steps_executed,
            trace_len=len(recorder.samples()),
            properties_checked=0,
            notes=tuple(notes),
        )

    trace = recorder.samples()
    if not trace:
        notes.append("the rehearsal backend recorded no samples; cannot certify the envelope held")
        return RehearsalReport(
            passed=False,
            sim_success=result.success,
            steps_executed=result.steps_executed,
            trace_len=0,
            properties_checked=len(properties),
            notes=tuple(notes),
        )

    monitor = OnlineMonitor(properties)
    for sample in trace:
        monitor.observe(sample)
    monitor.finalize()
    violations = tuple(monitor.violations())
    critical = [v for v in violations if v.severity == "critical"]

    return RehearsalReport(
        passed=result.success and not critical,
        sim_success=result.success,
        steps_executed=result.steps_executed,
        trace_len=len(trace),
        properties_checked=len(properties),
        violations=violations,
        notes=tuple(notes),
    )


# ---------------------------------------------------------------------------
# Hermetic kinematic backend
# ---------------------------------------------------------------------------


class KinematicProfile(BaseModel):
    """The declared synthetic motion profile the kinematic backend renders.

    These numbers are the rehearsal's *assumptions about the robot*, not
    measurements. Set them to the deployment's real expected values (the
    manifest's cruise speed, the platform's climb rate) or the gate checks
    a fiction.
    """

    model_config = ConfigDict(extra="forbid")

    dt: float = Field(0.5, gt=0, description="Sample period, seconds.")
    cruise_speed: float = Field(0.5, ge=0, description="Assumed translation speed, m/s.")
    turn_speed: float = Field(0.1, ge=0, description="Assumed effective speed while turning in place, m/s.")
    climb_rate: float = Field(2.0, ge=0, description="Assumed vertical rate for take_off/land, m/s.")
    move_duration: float = Field(2.0, gt=0, description="Assumed duration of one navigation command, seconds.")


class KinematicRehearsalAdapter(MockROSAdapter):
    """Hermetic rehearsal backend: MockROSAdapter plus a synthetic signal trace.

    Every motion-shaped command appends samples rendered from the declared
    `KinematicProfile` (translation at `cruise_speed`, vertical motion at
    `climb_rate`, `person_distance` fixed far). Non-motion commands append
    one at-rest sample so the trace covers the whole program.
    """

    def __init__(self, profile: KinematicProfile | None = None) -> None:
        super().__init__()
        self._profile = profile or KinematicProfile()
        self._trace: list[Sample] = []
        self._t = 0.0
        self._alt = 0.0
        self._grip = 0.0

    def samples(self) -> tuple[Sample, ...]:
        return tuple(self._trace)

    # ----- trace synthesis -----

    def _emit(self, *, duration: float, speed: float, alt_target: float | None = None) -> None:
        prof = self._profile
        steps = max(1, round(duration / prof.dt))
        alt_start = self._alt
        for i in range(1, steps + 1):
            self._t += prof.dt
            if alt_target is not None:
                self._alt = alt_start + (alt_target - alt_start) * (i / steps)
            self._trace.append(
                Sample(
                    t=self._t,
                    signals={
                        "speed": speed,
                        "altitude": self._alt,
                        "payload": 0.0,
                        "grip_force": self._grip,
                        "person_distance": 100.0,
                    },
                )
            )
        # Command boundary: one at-rest sample so `speed` returns to zero.
        self._t += prof.dt
        self._trace.append(
            Sample(
                t=self._t,
                signals={
                    "speed": 0.0,
                    "altitude": self._alt,
                    "payload": 0.0,
                    "grip_force": self._grip,
                    "person_distance": 100.0,
                },
            )
        )

    def _emit_idle(self) -> None:
        self._emit(duration=self._profile.dt, speed=0.0)

    # ----- motion-shaped commands (delegate to the mock after tracing) -----

    def send_navigation_goal(self, **kwargs: Any) -> Any:
        speed = kwargs.get("speed") or self._profile.cruise_speed
        self._emit(duration=self._profile.move_duration, speed=float(speed))
        return super().send_navigation_goal(**kwargs)

    def send_docking_goal(self, **kwargs: Any) -> Any:
        self._emit(duration=self._profile.move_duration, speed=self._profile.cruise_speed)
        return super().send_docking_goal(**kwargs)

    def send_takeoff_goal(self, **kwargs: Any) -> Any:
        altitude = float(kwargs.get("altitude") or 0.0)
        rate = float(kwargs.get("climb_rate") or self._profile.climb_rate)
        duration = abs(altitude - self._alt) / rate if rate > 0 else self._profile.move_duration
        self._emit(duration=max(duration, self._profile.dt), speed=rate, alt_target=altitude)
        return super().send_takeoff_goal(**kwargs)

    def send_land_goal(self, **kwargs: Any) -> Any:
        rate = self._profile.climb_rate
        duration = self._alt / rate if rate > 0 else self._profile.move_duration
        self._emit(duration=max(duration, self._profile.dt), speed=rate, alt_target=0.0)
        return super().send_land_goal(**kwargs)

    def send_return_to_home_goal(self, **kwargs: Any) -> Any:
        speed = kwargs.get("speed") or self._profile.cruise_speed
        self._emit(duration=self._profile.move_duration, speed=float(speed))
        return super().send_return_to_home_goal(**kwargs)

    def drive_by(self, **kwargs: Any) -> Any:
        distance = abs(float(kwargs.get("distance") or 0.0))
        speed = float(kwargs.get("speed") or self._profile.cruise_speed)
        duration = distance / speed if speed > 0 else self._profile.dt
        self._emit(duration=max(duration, self._profile.dt), speed=speed)
        return super().drive_by(**kwargs)

    def turn_by(self, **kwargs: Any) -> Any:
        self._emit(duration=self._profile.dt, speed=self._profile.turn_speed)
        return super().turn_by(**kwargs)

    def follow_trajectory_goal(self, **kwargs: Any) -> Any:
        speed = kwargs.get("max_velocity_mps") or self._profile.cruise_speed
        self._emit(duration=self._profile.move_duration, speed=float(speed))
        return super().follow_trajectory_goal(**kwargs)

    def send_manipulation_goal(self, **kwargs: Any) -> Any:
        force = kwargs.get("force_n")
        self._grip = float(force) if force is not None else self._grip
        self._emit_idle()
        result = super().send_manipulation_goal(**kwargs)
        if kwargs.get("action") == "release":
            self._grip = 0.0
        return result

    # ----- non-motion commands: one at-rest sample each -----

    def query_detection(self, **kwargs: Any) -> Any:
        self._emit_idle()
        return super().query_detection(**kwargs)

    def run_scan(self, **kwargs: Any) -> Any:
        self._emit(duration=self._profile.move_duration, speed=self._profile.cruise_speed)
        return super().run_scan(**kwargs)

    def take_measurement(self, **kwargs: Any) -> Any:
        self._emit_idle()
        return super().take_measurement(**kwargs)

    def capture_media(self, **kwargs: Any) -> Any:
        self._emit_idle()
        return super().capture_media(**kwargs)

    def wait_for_condition(self, **kwargs: Any) -> Any:
        self._emit_idle()
        return super().wait_for_condition(**kwargs)

    def wait_passively(self, **kwargs: Any) -> Any:
        duration = float(kwargs.get("duration_seconds") or self._profile.dt)
        self._emit(duration=duration, speed=0.0)
        return super().wait_passively(**kwargs)

    def emit_report(self, **kwargs: Any) -> Any:
        self._emit_idle()
        return super().emit_report(**kwargs)

    def emit_speech(self, **kwargs: Any) -> Any:
        self._emit_idle()
        return super().emit_speech(**kwargs)

    def acquire_speech(self, **kwargs: Any) -> Any:
        self._emit_idle()
        return super().acquire_speech(**kwargs)

    def call_named_program(self, **kwargs: Any) -> Any:
        self._emit_idle()
        return super().call_named_program(**kwargs)

    def set_output_line(self, **kwargs: Any) -> Any:
        self._emit_idle()
        return super().set_output_line(**kwargs)
