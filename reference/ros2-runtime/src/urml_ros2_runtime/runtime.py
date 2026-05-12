"""URMLRuntime — the orchestrator.

```
   validated URML program          re-validate (defense-in-depth)
              |                                |
              v                                v
        URMLRuntime.execute(program, manifest, envelope?)
              |
              | walk behavior tree (Sequence only in this skeleton)
              |
              v
        per-step: PrimitiveExecutor -> ROSAdapter call -> outcome
              |
              | on_error: abort_and_report | continue | retry
              |
              v
        RuntimeResult(success, audit, bindings)
```

Scope of this skeleton:

- Sequence composition with `on_error: abort_and_report | continue`.
- All 12 primitives dispatch through the executors in `primitives.py`.
- Defense-in-depth: the runtime re-validates the program before executing.
  Bypassing the validator at runtime is prohibited per CLAUDE.md.

Not in this PR (separate milestones):

- `Branch`, `Parallel`, `Retry` execution (raises `UnsupportedCompositionError`
  with a clear message).
- Real `rclpy`-backed adapter.
- Variable-binding resolution into `$ref.field` accesses inside primitive
  arguments (the runtime forwards the literal `$ref` strings; the adapter
  is responsible). Tightens in a follow-up.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from urml_validator import ValidationResult, validate
from urml_validator.schemas.composition import Sequence, Step
from urml_validator.schemas.program import URMLProgram

from urml_ros2_runtime.errors import (
    PrimitiveExecutionError,
    UnsupportedCompositionError,
    ValidationRejectedError,
)
from urml_ros2_runtime.primitives import PrimitiveOutcome, execute_step
from urml_ros2_runtime.substrate.base import ROSAdapter


class RuntimeResult(BaseModel):
    """The return value of `URMLRuntime.execute()`.

    Carries enough information for the caller to know what happened: the
    success flag, the count of steps actually executed, the final variable
    bindings (useful for downstream consumers of the program's outputs),
    and the full audit log from the adapter."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    success: bool
    steps_executed: int = 0
    bindings: dict[str, Any] = Field(default_factory=dict)
    audit_log: list[dict[str, Any]] = Field(default_factory=list)
    last_outcome: PrimitiveOutcome | None = None


class URMLRuntime:
    """Executes a validated URML program against a substrate adapter."""

    def __init__(self, adapter: ROSAdapter, *, revalidate: bool = True) -> None:
        """Construct a runtime bound to a substrate adapter.

        Args:
            adapter:    The ``ROSAdapter`` to dispatch primitives through.
                        ``MockROSAdapter`` for tests; ``RclpyAdapter`` (future)
                        for real ROS 2.
            revalidate: When True (default), the runtime re-validates the
                        program against the manifest + envelope before
                        executing. Set to False *only* when the runtime is
                        being driven from already-validated input AND the
                        caller has explicit reason to trust upstream
                        (skipping the validator is a safety-boundary
                        violation per CLAUDE.md; the option exists for
                        deterministic test harnesses).
        """
        self._adapter = adapter
        self._revalidate = revalidate

    def execute(
        self,
        program: dict[str, Any] | URMLProgram,
        manifest: dict[str, Any],
        envelope: dict[str, Any] | None = None,
        profiles: tuple[str, ...] = (),
    ) -> RuntimeResult:
        """Execute a URML program against the runtime's adapter.

        Returns a RuntimeResult. Raises ``ValidationRejectedError`` if the
        program fails defense-in-depth re-validation, or
        ``UnsupportedCompositionError`` if the program contains a
        composition node this skeleton does not yet implement.
        """
        # Defense-in-depth re-validation.
        if self._revalidate:
            result: ValidationResult = validate(program, manifest, envelope, profiles=profiles)
            if not result.accepted:
                raise ValidationRejectedError(
                    "runtime defense-in-depth re-validation rejected the program; "
                    "see validation_result.errors for the structured cause.",
                    validation_result=result,
                )

        # Normalize to a URMLProgram model.
        program_model: URMLProgram
        if isinstance(program, URMLProgram):
            program_model = program
        else:
            program_model = URMLProgram.model_validate(program)

        # Execute the root behavior.
        bindings: dict[str, Any] = {}
        steps_executed = 0
        last_outcome: PrimitiveOutcome | None = None

        try:
            steps_executed, last_outcome = self._exec_behavior(
                program_model.behavior,
                path=["behavior"],
                bindings=bindings,
                steps_executed=steps_executed,
            )
        except _ExecutionHalt as halt:
            return RuntimeResult(
                success=False,
                steps_executed=halt.steps_executed,
                bindings=bindings,
                audit_log=self._audit_snapshot(),
                last_outcome=halt.last_outcome,
            )

        return RuntimeResult(
            success=True,
            steps_executed=steps_executed,
            bindings=bindings,
            audit_log=self._audit_snapshot(),
            last_outcome=last_outcome,
        )

    # ----- Internal -----

    def _exec_behavior(
        self,
        node: Any,
        *,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        if isinstance(node, Step):
            return self._exec_step(node, path=path, bindings=bindings, steps_executed=steps_executed)
        if isinstance(node, Sequence):
            return self._exec_sequence(node, path=path, bindings=bindings, steps_executed=steps_executed)
        # Branch / Parallel / Retry land in a follow-up PR. Until then we
        # surface an unambiguous error so programs can adjust.
        cls_name = type(node).__name__
        raise UnsupportedCompositionError(
            f"runtime skeleton does not yet implement composition node {cls_name!r}. "
            "Sequence is supported; Branch / Parallel / Retry land in a follow-up release."
        )

    def _exec_sequence(
        self,
        node: Sequence,
        *,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        last_outcome: PrimitiveOutcome | None = None
        for idx, sub in enumerate(node.steps):
            sub_path = [*path, "steps", str(idx)]
            steps_executed, last_outcome = self._exec_behavior(
                sub,
                path=sub_path,
                bindings=bindings,
                steps_executed=steps_executed,
            )
            # If a step (or nested behavior) failed, honor this sequence's
            # on_error policy. Default (None) behaves like abort_and_report.
            if last_outcome is not None and not last_outcome.success:
                if node.on_error == "continue":
                    continue
                raise _ExecutionHalt(
                    steps_executed=steps_executed,
                    last_outcome=last_outcome,
                    primitive="sequence",
                    path=sub_path,
                )
        return steps_executed, last_outcome

    def _exec_step(
        self,
        step: Step,
        *,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome]:
        outcome = execute_step(step, self._adapter)
        steps_executed += 1
        # Merge any new bindings the step produced into the runtime scope.
        bindings.update(outcome.bindings)
        return steps_executed, outcome

    def _audit_snapshot(self) -> list[dict[str, Any]]:
        """Snapshot of the adapter's call log, if it exposes one."""
        log = getattr(self._adapter, "call_log", None)
        if log is None:
            return []
        return list(log)


# ---------------------------------------------------------------------------
# Internal flow-control exception
# ---------------------------------------------------------------------------


class _ExecutionHalt(Exception):  # noqa: N818 -- "Halt" reads better than "HaltError" for an internal flow-control signal.
    """Raised when a primitive returns ``success=False`` and the surrounding
    composition's on_error policy is to abort."""

    def __init__(
        self,
        *,
        steps_executed: int,
        last_outcome: PrimitiveOutcome,
        primitive: str,
        path: list[str],
    ) -> None:
        super().__init__(f"{primitive} at {'/'.join(path)} returned success=False")
        self.steps_executed = steps_executed
        self.last_outcome = last_outcome
        self.primitive = primitive
        self.path = path


# Re-export PrimitiveExecutionError for callers that want to surface a
# typed error rather than a RuntimeResult.success=False.
__all__ = [
    "PrimitiveExecutionError",
    "RuntimeResult",
    "URMLRuntime",
    "UnsupportedCompositionError",
    "ValidationRejectedError",
]
