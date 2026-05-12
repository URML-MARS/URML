"""Runtime-specific exception types.

The validator raises `ValidationResult.errors` (which are *static* problems
caught before execution begins). The runtime raises these (which are
*dynamic* problems that surfaced during execution).
"""

from __future__ import annotations


class RuntimeError(Exception):
    """Base class for runtime-side failures."""


class PrimitiveExecutionError(RuntimeError):
    """A specific primitive could not execute.

    Carries enough information for the caller (typically the LLM bridge or
    a higher-level orchestrator) to decide whether to retry, escalate, or
    surface to a human.
    """

    def __init__(
        self,
        message: str,
        *,
        primitive: str,
        path: list[str],
        reason: str | None = None,
    ) -> None:
        super().__init__(message)
        self.primitive = primitive
        self.path = path
        self.reason = reason


class UnsupportedCompositionError(RuntimeError):
    """The runtime saw a composition node it doesn't yet implement.

    This skeleton implements `Sequence` only. `Branch`, `Parallel`, and
    `Retry` raise this until their executors land in follow-up PRs. The
    error message names the unsupported type so authors get a clear
    upgrade path.
    """


class ConditionEvalError(RuntimeError):
    """The runtime could not evaluate a Branch.condition or Retry.until expression.

    Surfaces from `urml_ros2_runtime.conditions.evaluate` when the expression
    is syntactically invalid or uses an unsupported construct.
    """


class ValidationRejectedError(RuntimeError):
    """The runtime's defense-in-depth re-validation rejected the program.

    Raised when a caller hands the runtime a program that the validator
    rejects. Carries the structured `ValidationResult` for diagnostics.
    """

    def __init__(self, message: str, *, validation_result: object) -> None:
        super().__init__(message)
        self.validation_result = validation_result
