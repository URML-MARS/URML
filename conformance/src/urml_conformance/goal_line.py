"""The goal-line lane: a program the validator rejects sends zero commands.

The main conformance run stops a rejected fixture at the validator, so it
never shows what a runtime does with one. This lane hands every rejected
fixture (``expected_validation.accepted: false``, single-robot and fleet) to
the runtime itself, with the fixture's manifest, envelope, profiles, policy
and manifest directory, through an adapter that records every method call.
A case passes only when:

1. the runtime refuses: ``execute`` raises an exception that carries the
   validator's result as ``validation_result`` (``ValidationRejectedError``
   in the reference runtimes; a third-party runtime may raise its own type
   with the same attribute);
2. the refusal carries every error code the fixture expects; and
3. the adapter saw zero method calls.

Run it with ``python -m urml_conformance --goal-line``. A third-party runtime
plugs in through ``runtime_factory`` (``--runtime module:attr``): a callable
that takes one adapter and returns an object whose
``execute(program, manifest, envelope, profiles, *, policy,
manifest_base_dir)`` matches ``URMLRuntime.execute``. Fleet fixtures run
through ``fleet_runtime_factory``, the reference ``FleetRuntime`` by default.

A fixture that sets rulebooks (RFC-0702, Draft) also passes ``rulebooks``,
``default_rulebooks`` and ``as_of`` to ``execute``, as ``URMLRuntime`` and
``FleetRuntime`` accept them; a runtime that drops them fails those
fixtures, because the program it accepts must be refused.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from urml_ros2_runtime import FleetRuntime, MockROSAdapter, URMLRuntime

from urml_conformance.fixtures import (
    FixtureCase,
    discover_fixtures,
    manifest_base_dir,
    resolve_envelope,
    resolve_manifest,
    resolve_policy,
    rulebook_kwargs,
)
from urml_conformance.report import CaseResult, ConformanceReport
from urml_conformance.runner import fleet_inputs

AdapterFactory = Callable[[], Any]
"""Build a fresh adapter per case (the lane wraps it in a RecordingAdapter)."""

RuntimeFactory = Callable[[Any], Any]
"""Build a single-robot runtime around one adapter."""

FleetRuntimeFactory = Callable[[dict[str, Any]], Any]
"""Build a fleet runtime around ``{member: adapter}``."""


@dataclass(frozen=True)
class RecordedCall:
    """One method call a runtime made on an adapter."""

    method: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)


class RecordingAdapter:
    """Wrap any adapter object and record every method call before forwarding it.

    Works for any adapter shape. Reading a plain attribute (``call_log``, a
    config value) is passed through and not recorded; calling anything is
    recorded, then forwarded to the wrapped adapter.

    The wrapped adapter's public methods are bound on the proxy up front.
    The runtime checks optional capabilities with ``isinstance`` against
    runtime-checkable Protocols, and Python 3.12+ looks those attributes up
    with ``inspect.getattr_static``, which skips ``__getattr__``. Binding
    them up front makes the proxy answer the checks the way the wrapped
    adapter does on every Python version.
    """

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.calls: list[RecordedCall] = []
        for name in dir(type(inner)):
            if name.startswith("_"):
                continue
            # Static lookup: no property or descriptor on the adapter runs here.
            static = inspect.getattr_static(inner, name, None)
            if inspect.isfunction(static) or isinstance(static, (staticmethod, classmethod)):
                setattr(self, name, self._recording(name, getattr(inner, name)))

    def _recording(self, name: str, method: Callable[..., Any]) -> Callable[..., Any]:
        def recorded(*args: Any, **kwargs: Any) -> Any:
            self.calls.append(RecordedCall(name, args, dict(kwargs)))
            return method(*args, **kwargs)

        return recorded

    def __getattr__(self, name: str) -> Any:
        # Only reached for names not bound above: plain attributes, and
        # callables the adapter sets on its instance.
        if name in {"_inner", "calls"}:  # not set yet (copy, pickle): no recursion
            raise AttributeError(name)
        attr = getattr(self._inner, name)
        return self._recording(name, attr) if callable(attr) else attr


def rejected_cases(cases: list[FixtureCase]) -> list[FixtureCase]:
    """The fixtures the validator must reject: the goal line's input."""
    return [c for c in cases if not c.expected_validation.accepted]


def run_goal_line(
    cases: list[FixtureCase] | None = None,
    adapter_factory: AdapterFactory | None = None,
    runtime_factory: RuntimeFactory | None = None,
    *,
    fleet_runtime_factory: FleetRuntimeFactory | None = None,
) -> ConformanceReport:
    """Run every rejected fixture through the runtime; see the module docstring.

    Accepted fixtures in ``cases`` are skipped. Defaults: the shipped fixtures,
    ``MockROSAdapter``, the reference ``URMLRuntime``, and a sequential
    reference ``FleetRuntime``.
    """
    make_adapter: AdapterFactory = adapter_factory or MockROSAdapter
    make_runtime: RuntimeFactory = runtime_factory or URMLRuntime
    make_fleet: FleetRuntimeFactory = fleet_runtime_factory or (
        lambda adapters: FleetRuntime(adapters, sequential=True)
    )
    results: list[CaseResult] = []
    for case in rejected_cases(cases if cases is not None else discover_fixtures()):
        if case.roster is not None:
            results.append(_run_fleet_case(case, make_adapter, make_fleet))
        else:
            results.append(_run_single_case(case, make_adapter, make_runtime))
    return ConformanceReport(results=results)


def _run_single_case(
    case: FixtureCase, make_adapter: AdapterFactory, make_runtime: RuntimeFactory
) -> CaseResult:
    try:
        assert case.manifest is not None  # the FixtureCase validator ensures this
        manifest = resolve_manifest(case.manifest)
        envelope = resolve_envelope(case.envelope) if case.envelope else None
        policy = resolve_policy(case.policy)
        base_dir = manifest_base_dir(case.manifest)
        extra = rulebook_kwargs(case) if case.uses_rulebook_fields else {}
    except (KeyError, ValueError) as exc:
        return CaseResult(name=case.name, passed=False, diagnostics=[f"fixture-load error: {exc}"])

    recorder = RecordingAdapter(make_adapter())
    runtime = make_runtime(recorder)

    def run() -> Any:
        return runtime.execute(
            case.program,
            manifest,
            envelope,
            tuple(case.profiles),
            policy=policy,
            manifest_base_dir=base_dir,
            **extra,
        )

    diagnostics = _judge(case, run, [recorder])
    return CaseResult(name=case.name, passed=not diagnostics, diagnostics=diagnostics)


def _run_fleet_case(
    case: FixtureCase, make_adapter: AdapterFactory, make_fleet: FleetRuntimeFactory
) -> CaseResult:
    try:
        roster, members, member_envelopes = fleet_inputs(case)
        policy = resolve_policy(case.policy)
        extra = rulebook_kwargs(case) if case.uses_rulebook_fields else {}
    except (KeyError, ValueError) as exc:
        return CaseResult(name=case.name, passed=False, diagnostics=[f"fixture-load error: {exc}"])

    recorders = {name: RecordingAdapter(make_adapter()) for name in members}
    runtime = make_fleet(dict(recorders))

    def run() -> Any:
        return runtime.execute(
            roster,
            members,
            case.program,
            member_envelopes,
            profiles=tuple(case.profiles),
            policy=policy,
            **extra,
        )

    diagnostics = _judge(case, run, list(recorders.values()))
    return CaseResult(name=case.name, passed=not diagnostics, diagnostics=diagnostics)


def _code(error: Any) -> str:
    code = getattr(error, "code", error)
    return str(getattr(code, "value", code))


def _judge(case: FixtureCase, run: Callable[[], Any], recorders: list[RecordingAdapter]) -> list[str]:
    """Apply the three goal-line requirements to one runtime call."""
    diagnostics: list[str] = []
    try:
        outcome = run()
    except Exception as exc:  # noqa: BLE001 - any exception type is judged below
        verdict = getattr(exc, "validation_result", None)
        if verdict is None:
            diagnostics.append(
                f"runtime raised {type(exc).__name__} instead of a validation refusal: {exc}"
            )
        else:
            emitted = {_code(e) for e in getattr(verdict, "errors", [])}
            missing = [c for c in case.expected_validation.error_codes if c not in emitted]
            if missing:
                diagnostics.append(
                    f"the refusal did not carry the expected error codes: missing={missing!r}, "
                    f"emitted={sorted(emitted)!r}"
                )
    else:
        diagnostics.append(
            "runtime did not refuse the program: execute returned "
            f"{type(outcome).__name__} (success={getattr(outcome, 'success', None)!r})"
        )
    calls = [call.method for recorder in recorders for call in recorder.calls]
    if calls:
        diagnostics.append(f"{len(calls)} adapter call(s) for a rejected program: {calls!r}")
    return diagnostics


__all__ = [
    "AdapterFactory",
    "FleetRuntimeFactory",
    "RecordedCall",
    "RecordingAdapter",
    "RuntimeFactory",
    "rejected_cases",
    "run_goal_line",
]
