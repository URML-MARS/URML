"""FleetRuntime — execute a multi-robot URML program (RFC-0286).

`FleetRuntime` is the inter-robot analogue of `URMLRuntime`. Where `URMLRuntime`
dispatches one program's primitives to one adapter, `FleetRuntime` holds a
``{member -> ROSAdapter}`` map and dispatches each `on:`-scoped subtree to that
member's adapter. The two compose: a member's adapter could itself be a
`CompositeAdapter` (the intra-robot split from the PX4 runtime).

Execution model (v0.1): deterministic and sequential, matching the single-robot
runtime — which also executes `parallel` branches sequentially and treats real
concurrency as a substrate-level concern. A `barrier` is therefore a rendezvous
marker (a no-op join point) under sequential execution; its teeth are in the
*validator* (`fleet.barrier_missing_peer_link` and the cross-robot workspace
check), which runs before anything actuates. Each member owns its own adapter, so
``adapter.call_log`` is the member's audit trail, kept clean and assertable.

Hermetic path: give each member a `MockROSAdapter()` and the whole fleet runs
offline, on any host, with no ROS and no cloud — the same posture as the
single-robot reference path.

Defense-in-depth: `execute` re-validates via `validate_fleet` before dispatching.
Bypassing the validator is prohibited (CLAUDE.md safety boundary).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from urml_validator import Policy, ValidationResult, validate_fleet
from urml_validator.schemas.composition import (
    Barrier,
    Branch,
    OnMember,
    Parallel,
    Retry,
    Sequence,
    Step,
)
from urml_validator.schemas.program import URMLProgram

from urml_ros2_runtime.conditions import evaluate as _eval_condition
from urml_ros2_runtime.errors import (
    UnsupportedCompositionError,
    ValidationRejectedError,
)
from urml_ros2_runtime.primitives import PrimitiveOutcome, execute_step
from urml_ros2_runtime.substrate.base import ROSAdapter


class FleetRuntimeResult(BaseModel):
    """The return value of `FleetRuntime.execute()`.

    ``per_member_audit`` is the multi-robot analogue of `RuntimeResult.audit_log`:
    one adapter call-log per fleet member, keyed by member handle.
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    success: bool
    steps_executed: int = 0
    bindings: dict[str, Any] = Field(default_factory=dict)
    per_member_audit: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    last_outcome: PrimitiveOutcome | None = None


class FleetRuntime:
    """Executes a validated multi-robot URML program across member adapters."""

    def __init__(
        self,
        adapters: dict[str, ROSAdapter],
        *,
        revalidate: bool = True,
        sequential: bool = False,
    ) -> None:
        """Construct a fleet runtime bound to one adapter per member.

        Args:
            adapters:   ``{member_handle -> ROSAdapter}``. Hermetic deployments
                        pass one ``MockROSAdapter`` per member.
            revalidate: When True (default), `execute` re-validates the program
                        via `validate_fleet` before dispatching (defense-in-depth;
                        see CLAUDE.md). Set False only for already-validated input
                        in a deterministic test harness.
            sequential: When True, `parallel` branches run one after another
                        (fully deterministic — used by conformance for byte-stable
                        audits). When False (default), branches run CONCURRENTLY on
                        a thread pool: members dispatch to their adapters at the
                        same time, which is what makes "the robots move together"
                        real. Per-member audit stays deterministic regardless —
                        each member owns its adapter, so its call-log is ordered;
                        only the cross-member interleaving differs.
        """
        self._adapters = dict(adapters)
        self._revalidate = revalidate
        self._sequential = sequential

    def execute(
        self,
        roster: dict[str, Any],
        member_manifests: dict[str, dict[str, Any]],
        program: dict[str, Any] | URMLProgram,
        member_envelopes: dict[str, dict[str, Any]] | None = None,
        profiles: tuple[str, ...] = (),
        policy: dict[str, Any] | Policy | None | Literal["DEFAULT"] = "DEFAULT",
    ) -> FleetRuntimeResult:
        """Execute a fleet program against the runtime's member adapters.

        ``policy`` is forwarded to the defense-in-depth re-validation, so a
        deployment can run ``--no-policy`` (``policy=None``) exactly as the
        validator does — the no-bypass rule is about skipping validation, not
        about the optional compliance pass.

        Raises ``ValidationRejectedError`` if defense-in-depth re-validation
        rejects the program, or ``UnsupportedCompositionError`` for a node this
        runtime does not implement.
        """
        if self._revalidate:
            result: ValidationResult = validate_fleet(
                roster, member_manifests, program, member_envelopes,
                profiles=profiles, policy=policy,
            )
            if not result.accepted:
                raise ValidationRejectedError(
                    "fleet runtime defense-in-depth re-validation rejected the program; "
                    "see validation_result.errors for the structured cause.",
                    validation_result=result,
                )

        program_model = (
            program if isinstance(program, URMLProgram) else URMLProgram.model_validate(program)
        )

        # A fleet of one resolves an unaddressed root to the sole member; a
        # multi-member fleet always enters through an `on:` node (the validator
        # has already rejected an unaddressed step otherwise).
        root_adapter: ROSAdapter | None = (
            next(iter(self._adapters.values())) if len(self._adapters) == 1 else None
        )

        bindings: dict[str, Any] = {}
        steps_executed, last_outcome = self._exec(
            program_model.behavior,
            adapter=root_adapter,
            path=["behavior"],
            bindings=bindings,
            steps_executed=0,
        )

        overall_success = last_outcome is None or last_outcome.success
        return FleetRuntimeResult(
            success=overall_success,
            steps_executed=steps_executed,
            bindings=bindings,
            per_member_audit=self._audit_snapshot(),
            last_outcome=last_outcome,
        )

    # ----- Internal -----

    def _exec(
        self,
        node: Any,
        *,
        adapter: ROSAdapter | None,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        if isinstance(node, OnMember):
            member_adapter = self._adapters.get(node.member)
            if member_adapter is None:
                raise UnsupportedCompositionError(
                    f"fleet runtime has no adapter for member {node.member!r}; "
                    f"known members: {sorted(self._adapters)!r}."
                )
            return self._exec(
                node.body,
                adapter=member_adapter,
                path=[*path, "body"],
                bindings=bindings,
                steps_executed=steps_executed,
            )
        if isinstance(node, Barrier):
            # Sequential execution: every prior member subtree has already run,
            # so the rendezvous is implicit. Record a success marker.
            return steps_executed, PrimitiveOutcome(
                success=True, reason=f"barrier:{','.join(node.members)}"
            )
        if isinstance(node, Step):
            if adapter is None:
                raise UnsupportedCompositionError(
                    "fleet runtime reached an unaddressed step (no enclosing `on:` "
                    "member). The validator should have rejected this; pass a "
                    "validated program."
                )
            outcome = execute_step(node, adapter, bindings)
            bindings.update(outcome.bindings)
            return steps_executed + 1, outcome
        if isinstance(node, Sequence):
            return self._exec_sequence(
                node, adapter=adapter, path=path, bindings=bindings, steps_executed=steps_executed
            )
        if isinstance(node, Branch):
            condition_true = _eval_condition(node.condition, bindings)
            chosen = node.if_true if condition_true else node.if_false
            if chosen is None:
                return steps_executed, PrimitiveOutcome(success=True, reason="branch_skipped")
            return self._exec(
                chosen,
                adapter=adapter,
                path=[*path, "if_true" if condition_true else "if_false"],
                bindings=bindings,
                steps_executed=steps_executed,
            )
        if isinstance(node, Parallel):
            return self._exec_parallel(
                node, adapter=adapter, path=path, bindings=bindings, steps_executed=steps_executed
            )
        if isinstance(node, Retry):
            return self._exec_retry(
                node, adapter=adapter, path=path, bindings=bindings, steps_executed=steps_executed
            )
        raise UnsupportedCompositionError(
            f"fleet runtime does not implement composition node {type(node).__name__!r}."
        )

    def _exec_sequence(
        self,
        node: Sequence,
        *,
        adapter: ROSAdapter | None,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        last_outcome: PrimitiveOutcome | None = None
        for idx, sub in enumerate(node.steps):
            steps_executed, last_outcome = self._exec(
                sub,
                adapter=adapter,
                path=[*path, "steps", str(idx)],
                bindings=bindings,
                steps_executed=steps_executed,
            )
            if last_outcome is not None and not last_outcome.success:
                if node.on_error == "continue":
                    continue
                return steps_executed, last_outcome
        return steps_executed, last_outcome

    def _exec_parallel(
        self,
        node: Parallel,
        *,
        adapter: ROSAdapter | None,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        """Execute `parallel` branches concurrently (default) or sequentially.

        Branches may each dispatch to a different member's adapter via an inner
        `on:` node. The default concurrent path is what makes the members move
        *at the same time*; `sequential=True` runs them in order for byte-stable
        determinism. Aggregation is identical: ``all`` fails on any branch
        failure, ``any`` needs one success, ``first_to_succeed`` selects the
        first successful branch in declaration order.
        """
        if self._sequential:
            return self._exec_parallel_sequential(
                node, adapter=adapter, path=path, bindings=bindings, steps_executed=steps_executed
            )
        return self._exec_parallel_concurrent(
            node, adapter=adapter, path=path, bindings=bindings, steps_executed=steps_executed
        )

    def _exec_parallel_sequential(
        self,
        node: Parallel,
        *,
        adapter: ROSAdapter | None,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        """Run branches one after another (deterministic; short-circuits)."""
        succeeded = 0
        last_outcome: PrimitiveOutcome | None = None
        for idx, sub in enumerate(node.branches):
            steps_executed, last_outcome = self._exec(
                sub,
                adapter=adapter,
                path=[*path, "branches", str(idx)],
                bindings=bindings,
                steps_executed=steps_executed,
            )
            sub_success = last_outcome is None or last_outcome.success
            if sub_success:
                succeeded += 1
                if node.complete_when == "first_to_succeed":
                    break
            elif node.complete_when == "all":
                return steps_executed, last_outcome

        if node.complete_when == "all":
            return steps_executed, last_outcome
        if node.complete_when == "any":
            if succeeded >= 1:
                return steps_executed, PrimitiveOutcome(
                    success=True, reason=f"parallel.any:{succeeded}"
                )
            return steps_executed, PrimitiveOutcome(
                success=False, reason="parallel.any: every branch failed"
            )
        if node.complete_when == "first_to_succeed":
            if succeeded >= 1:
                return steps_executed, last_outcome
            return steps_executed, PrimitiveOutcome(
                success=False, reason="parallel.first_to_succeed: no branch succeeded"
            )
        raise UnsupportedCompositionError(
            f"unknown parallel.complete_when: {node.complete_when!r}"
        )

    def _exec_parallel_concurrent(
        self,
        node: Parallel,
        *,
        adapter: ROSAdapter | None,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        """Run branches concurrently on a thread pool, then aggregate.

        Each branch gets its own copy of the bindings (thread-safe — no shared
        mutation mid-flight; a cross-branch ``$ref`` dependency is a hazard the
        validator already discourages). All branches run to completion, then the
        results are aggregated in declaration order and their bindings merged.
        """

        def run_branch(
            idx: int, sub: Any
        ) -> tuple[int, int, PrimitiveOutcome | None, dict[str, Any]]:
            branch_bindings = dict(bindings)
            steps, outcome = self._exec(
                sub,
                adapter=adapter,
                path=[*path, "branches", str(idx)],
                bindings=branch_bindings,
                steps_executed=0,
            )
            return idx, steps, outcome, branch_bindings

        results_by_idx: dict[int, tuple[int, PrimitiveOutcome | None, dict[str, Any]]] = {}
        with ThreadPoolExecutor(max_workers=len(node.branches)) as pool:
            futures = [pool.submit(run_branch, idx, sub) for idx, sub in enumerate(node.branches)]
            for fut in as_completed(futures):
                idx, steps, outcome, branch_bindings = fut.result()
                results_by_idx[idx] = (steps, outcome, branch_bindings)
        ordered = [results_by_idx[i] for i in range(len(node.branches))]

        total = steps_executed
        succeeded = 0
        first_failure: PrimitiveOutcome | None = None
        last_outcome: PrimitiveOutcome | None = None
        for steps, outcome, branch_bindings in ordered:
            total += steps
            bindings.update(branch_bindings)
            last_outcome = outcome
            if outcome is None or outcome.success:
                succeeded += 1
            elif first_failure is None:
                first_failure = outcome

        if node.complete_when == "all":
            return total, (first_failure if first_failure is not None else last_outcome)
        if node.complete_when == "any":
            if succeeded >= 1:
                return total, PrimitiveOutcome(success=True, reason=f"parallel.any:{succeeded}")
            return total, PrimitiveOutcome(
                success=False, reason="parallel.any: every branch failed"
            )
        if node.complete_when == "first_to_succeed":
            for steps, outcome, branch_bindings in ordered:
                if outcome is None or outcome.success:
                    return total, outcome
            return total, PrimitiveOutcome(
                success=False, reason="parallel.first_to_succeed: no branch succeeded"
            )
        raise UnsupportedCompositionError(
            f"unknown parallel.complete_when: {node.complete_when!r}"
        )

    def _exec_retry(
        self,
        node: Retry,
        *,
        adapter: ROSAdapter | None,
        path: list[str],
        bindings: dict[str, Any],
        steps_executed: int,
    ) -> tuple[int, PrimitiveOutcome | None]:
        last_outcome: PrimitiveOutcome | None = None
        for attempt_idx in range(node.max_attempts):
            steps_executed, last_outcome = self._exec(
                node.behavior,
                adapter=adapter,
                path=[*path, "attempt", str(attempt_idx)],
                bindings=bindings,
                steps_executed=steps_executed,
            )
            if node.until is not None:
                if _eval_condition(node.until, bindings):
                    return steps_executed, last_outcome
            elif last_outcome is None or last_outcome.success:
                return steps_executed, last_outcome
        if last_outcome is None:
            last_outcome = PrimitiveOutcome(success=False, reason="retry.max_attempts_exhausted")
        elif last_outcome.success and node.until is not None:
            last_outcome = PrimitiveOutcome(
                success=False, reason="retry.until_unsatisfied_after_max_attempts"
            )
        return steps_executed, last_outcome

    def _audit_snapshot(self) -> dict[str, list[dict[str, Any]]]:
        """One adapter call-log per member, keyed by member handle."""
        out: dict[str, list[dict[str, Any]]] = {}
        for member, adapter in self._adapters.items():
            log = getattr(adapter, "call_log", None)
            out[member] = list(log) if log is not None else []
        return out


__all__ = ["FleetRuntime", "FleetRuntimeResult"]
