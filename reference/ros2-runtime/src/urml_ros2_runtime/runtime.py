"""URMLRuntime — the orchestrator.

```
   validated URML program          re-validate (defense-in-depth)
              |                                |
              v                                v
        URMLRuntime.execute(program, manifest, envelope?)
              |
              | walk the full behavior tree (Layer-3 v0.1.0)
              |
              v
        per-step: PrimitiveExecutor -> ROSAdapter call -> outcome
              |
              | on_error: abort_and_report | continue | retry
              |
              v
        RuntimeResult(success, audit, bindings)
```

Scope (Layer-3 v0.1.0 — see spec/layer-3-behavior/v0.1.0.md):

- All four composition operators execute: `Sequence`, `Branch`, `Parallel`
  (`all` / `any` / `first_to_succeed`), and `Retry`, plus the `on_error`
  model (`abort_and_report` | `continue` | `retry`).
- All 17 primitives (12 core + 5 profile-scoped) dispatch through the
  executors in `primitives.py`.
- Defense-in-depth: the runtime re-validates the program before executing.
  Bypassing the validator at runtime is prohibited per CLAUDE.md.

Substrate: the real `rclpy`-backed adapter ships alongside `MockROSAdapter`;
both satisfy the substrate-neutral `ROSAdapter` Protocol. Variable bindings
(`$ref` / `$ref.field`) resolve via `bindings.py` before the adapter call.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from urml_validator import ValidationResult, validate
from urml_validator.schemas.composition import Branch, Parallel, Retry, Sequence, Step
from urml_validator.schemas.program import URMLProgram

from urml_ros2_runtime.conditions import evaluate as _eval_condition
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

        # The composition executors (Branch / Parallel / Retry) may return a
        # failing outcome without raising — the runtime treats a non-success
        # outcome at the root as overall failure. Sequence still raises
        # `_ExecutionHalt` (handled above) when its `on_error` policy aborts.
        overall_success = last_outcome is None or last_outcome.success
        return RuntimeResult(
            success=overall_success,
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
        if isinstance(node, Branch):
            return self._exec_branch(node, path=path, bindings=bindings, steps_executed=steps_executed)
        if isinstance(node, Parallel):
            return self._exec_parallel(node, path=path, bindings=bindings, steps_executed=steps_executed)
        if isinstance(node, Retry):
            return self._exec_retry(node, path=path, bindings=bindings, steps_executed=steps_executed)
        cls_name = type(node).__name__
        raise UnsupportedCompositionError(
            f"runtime does not implement composition node {cls_name!r}. "
            "Supported: Sequence, Branch, Parallel, Retry, Step."
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
        outcome = execute_step(step, self._adapter, bindings)
        steps_executed += 1
        # Merge any new bindings the step produced into the runtime scope.
        bindings.update(outcome.bindings)
        return steps_executed, outcome

    def _exec_branch(
        self,
        node: Branch,
        *,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        condition_true = _eval_condition(node.condition, bindings)
        chosen = node.if_true if condition_true else node.if_false
        if chosen is None:
            # Branch with condition=False and no `if_false`: treat as a no-op that
            # succeeds. Synthesize a success outcome so the caller's
            # success-tracking stays consistent.
            return steps_executed, PrimitiveOutcome(success=True, reason="branch_skipped")
        sub_path = [*path, "if_true" if condition_true else "if_false"]
        return self._exec_behavior(
            chosen, path=sub_path, bindings=bindings, steps_executed=steps_executed
        )

    def _exec_parallel(
        self,
        node: Parallel,
        *,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        """Execute branches and aggregate per `complete_when`.

        This skeleton executes branches **sequentially**. Real concurrent
        execution is a substrate-level concern (the adapter decides whether
        to coordinate via threads, asyncio, or substrate-native parallelism).
        Aggregation semantics are honored either way:

          - ``all``               -> every branch must succeed; first failure halts.
          - ``any``               -> at least one branch must succeed; failures
                                     don't halt the loop, but a final all-fail
                                     overall outcome is failure.
          - ``first_to_succeed``  -> short-circuit on the first success.
        """
        branch_bindings = dict(bindings)
        succeeded = 0
        last_outcome: PrimitiveOutcome | None = None

        for idx, sub in enumerate(node.branches):
            sub_path = [*path, "branches", str(idx)]
            steps_executed, last_outcome = self._exec_behavior(
                sub,
                path=sub_path,
                bindings=branch_bindings,
                steps_executed=steps_executed,
            )
            sub_success = last_outcome is None or last_outcome.success
            if sub_success:
                succeeded += 1
                if node.complete_when == "first_to_succeed":
                    break
            elif node.complete_when == "all":
                # Halt the parallel block; surface the failing outcome.
                bindings.update(branch_bindings)
                return steps_executed, last_outcome

        # Merge the branches' bindings back into the parent scope.
        bindings.update(branch_bindings)

        if node.complete_when == "all":
            return steps_executed, last_outcome  # all succeeded (we'd have returned above otherwise)
        if node.complete_when == "any":
            if succeeded >= 1:
                # Synthesize a success outcome since multiple branches contributed.
                return steps_executed, PrimitiveOutcome(success=True, reason=f"parallel.any:{succeeded}")
            return steps_executed, PrimitiveOutcome(
                success=False, reason="parallel.any: every branch failed"
            )
        if node.complete_when == "first_to_succeed":
            if succeeded >= 1:
                return steps_executed, last_outcome  # the one that succeeded
            return steps_executed, PrimitiveOutcome(
                success=False, reason="parallel.first_to_succeed: no branch succeeded"
            )
        # Unreachable per the pydantic Literal type, but kept for safety.
        raise UnsupportedCompositionError(
            f"unknown parallel.complete_when: {node.complete_when!r}"
        )

    def _exec_retry(
        self,
        node: Retry,
        *,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        """Retry the inner behavior up to ``max_attempts`` times.

        Semantics:

          - No ``until``: retry until the inner behavior succeeds, or
            ``max_attempts`` is exhausted.
          - With ``until``: retry until the ``until`` expression evaluates
            to true *or* ``max_attempts`` is exhausted. Inner-behavior
            failures do NOT short-circuit when ``until`` is set — the
            condition is the source of truth.

        Bindings produced by failed attempts are kept (they describe the
        state of the world when the attempt ran; the next attempt sees
        them). Authors who want fresh state per attempt should structure
        their program so each attempt rebinds.
        """
        last_outcome: PrimitiveOutcome | None = None
        for attempt_idx in range(node.max_attempts):
            sub_path = [*path, "attempt", str(attempt_idx)]
            steps_executed, last_outcome = self._exec_behavior(
                node.behavior,
                path=sub_path,
                bindings=bindings,
                steps_executed=steps_executed,
            )
            if node.until is not None:
                if _eval_condition(node.until, bindings):
                    return steps_executed, last_outcome
            else:
                # No `until`: success-on-attempt halts the retry.
                if last_outcome is None or last_outcome.success:
                    return steps_executed, last_outcome
        # Exhausted attempts.
        if last_outcome is None:
            last_outcome = PrimitiveOutcome(success=False, reason="retry.max_attempts_exhausted")
        elif last_outcome.success and node.until is not None:
            # Inner kept succeeding but `until` never matched -> overall failure.
            last_outcome = PrimitiveOutcome(
                success=False,
                reason="retry.until_unsatisfied_after_max_attempts",
            )
        elif not last_outcome.success:
            # Last attempt failed; surface that outcome as-is.
            pass
        return steps_executed, last_outcome

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
