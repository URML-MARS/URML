"""ConformanceRunner — exercise URMLRuntime against a set of fixtures.

The fixtures themselves are the durable artifact: they declare expected
outcomes that any URML-compatible runtime/adapter pair must reproduce.

By default, the runner uses ``MockROSAdapter`` — fully hermetic, no ROS 2
install required. A real adapter (``RclpyAdapter``, a PX4 adapter, a
vendor SDK adapter) can be plugged in via the ``adapter_factory`` hook
without changing the fixture set or the runner internals. Fixture-side
``adapter_overrides`` are only applied when the factory yields a
``MockROSAdapter``; real adapters get their behavior from the live
substrate.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from urml_ros2_runtime import MockROSAdapter, URMLRuntime
from urml_ros2_runtime.substrate.base import ROSAdapter
from urml_validator import validate

from urml_conformance.fixtures import (
    AdapterOverrides,
    FixtureCase,
    discover_fixtures,
    resolve_envelope,
    resolve_manifest,
    resolve_policy,
)
from urml_conformance.report import CaseResult, ConformanceReport

AdapterFactory = Callable[[], ROSAdapter]
"""Construct a fresh ROSAdapter per fixture case.

Use a factory rather than a single adapter instance so each case starts
with a clean call_log / clean topic subscriptions / clean action-client
state. The default factory returns ``MockROSAdapter()``.
"""

# ---------------------------------------------------------------------------
# Apply adapter overrides — small helper so the runner stays compact
# ---------------------------------------------------------------------------


def _apply_overrides(adapter: MockROSAdapter, overrides: AdapterOverrides | None) -> None:
    """Map AdapterOverrides fields onto MockROSAdapter's set_* methods."""
    if overrides is None:
        return
    if overrides.navigation is not None:
        adapter.set_navigation_result(overrides.navigation)
    if overrides.docking is not None:
        adapter.set_dock_result(overrides.docking)
    if overrides.manipulation is not None:
        adapter.set_manipulation_result(overrides.manipulation)
    if overrides.detection is not None:
        adapter.set_detection_result(overrides.detection)
    if overrides.scan is not None:
        adapter.set_scan_result(overrides.scan)
    if overrides.measurement is not None:
        adapter.set_measurement_result(overrides.measurement)
    if overrides.capture is not None:
        adapter.set_capture_result(overrides.capture)
    if overrides.wait_for is not None:
        adapter.set_wait_for_result(overrides.wait_for)
    if overrides.wait_passive is not None:
        adapter.set_wait_passive_result(overrides.wait_passive)
    if overrides.report is not None:
        adapter.set_report_result(overrides.report)
    if overrides.speech is not None:
        adapter.set_speech_result(overrides.speech)
    if overrides.listen is not None:
        adapter.set_listen_result(overrides.listen)


# ---------------------------------------------------------------------------
# Diagnostic helpers
# ---------------------------------------------------------------------------


def _diag_validation(case: FixtureCase, result: Any) -> list[str]:
    """Compare a validator's ValidationResult against the expected_validation."""
    expected = case.expected_validation
    diagnostics: list[str] = []
    if result.accepted != expected.accepted:
        diagnostics.append(
            f"validation accepted={result.accepted}, expected={expected.accepted}"
        )
    if not expected.accepted and expected.error_codes:
        emitted = {e.code.value for e in result.errors}
        missing = [c for c in expected.error_codes if c not in emitted]
        if missing:
            diagnostics.append(
                f"validation did not emit expected error codes: missing={missing!r}, "
                f"emitted={sorted(emitted)!r}"
            )
    return diagnostics


def _diag_execution(case: FixtureCase, result: Any, audit_log: list[dict[str, Any]]) -> list[str]:
    """Compare RuntimeResult against expected_execution."""
    expected = case.expected_execution
    if expected is None:
        return []
    diagnostics: list[str] = []
    if result.success != expected.success:
        diagnostics.append(f"execution success={result.success}, expected={expected.success}")
    if expected.steps_executed is not None and result.steps_executed != expected.steps_executed:
        diagnostics.append(
            f"steps_executed={result.steps_executed}, expected={expected.steps_executed}"
        )
    if expected.audit_methods is not None:
        actual = [entry["method"] for entry in audit_log]
        if actual != expected.audit_methods:
            diagnostics.append(
                f"audit methods do not match: actual={actual!r}, "
                f"expected={expected.audit_methods!r}"
            )
    if expected.bindings_contains is not None:
        for key, expected_subset in expected.bindings_contains.items():
            if key not in result.bindings:
                diagnostics.append(f"binding {key!r} missing from result.bindings")
                continue
            bound = result.bindings[key]
            if isinstance(expected_subset, dict):
                for sub_key, sub_val in expected_subset.items():
                    if not isinstance(bound, dict) or bound.get(sub_key) != sub_val:
                        actual_field: Any = (
                            bound.get(sub_key) if isinstance(bound, dict) else bound
                        )
                        diagnostics.append(
                            f"binding {key!r}.{sub_key!r}={actual_field!r}, expected {sub_val!r}"
                        )
    if expected.last_reason is not None:
        actual_reason = getattr(result.last_outcome, "reason", None) if result.last_outcome else None
        if actual_reason != expected.last_reason:
            diagnostics.append(
                f"last_outcome.reason={actual_reason!r}, expected {expected.last_reason!r}"
            )
    return diagnostics


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


class ConformanceRunner:
    """Run a set of fixture cases against URMLRuntime + a configurable adapter.

    By default uses ``MockROSAdapter`` for fully hermetic, OS-independent
    execution. Pass ``adapter_factory=`` to plug in a real adapter (e.g.,
    ``RclpyAdapter``) for integration testing against a live substrate.
    """

    def __init__(
        self,
        cases: list[FixtureCase] | None = None,
        *,
        adapter_factory: AdapterFactory | None = None,
    ) -> None:
        self._cases: list[FixtureCase] = cases if cases is not None else discover_fixtures()
        # Default factory: hermetic mock. The factory pattern (callable, not
        # instance) gives each case a fresh adapter — important for real
        # adapters that accumulate state across calls.
        self._adapter_factory: AdapterFactory = adapter_factory or (lambda: MockROSAdapter())

    @property
    def cases(self) -> list[FixtureCase]:
        return list(self._cases)

    def run(self) -> ConformanceReport:
        """Execute every fixture; return an aggregated report."""
        results = [self._run_case(case) for case in self._cases]
        return ConformanceReport(results=results)

    def _run_case(self, case: FixtureCase) -> CaseResult:
        try:
            manifest = resolve_manifest(case.manifest)
            envelope = resolve_envelope(case.envelope) if case.envelope else None
            policy = resolve_policy(case.policy)
        except (KeyError, ValueError) as exc:
            return CaseResult(name=case.name, passed=False, diagnostics=[f"fixture-load error: {exc}"])

        diagnostics: list[str] = []

        # ----- Validation pass (always runs) -----
        validation = validate(
            case.program,
            manifest,
            envelope,
            profiles=tuple(case.profiles),
            policy=policy,
        )
        diagnostics.extend(_diag_validation(case, validation))

        # If we don't expect to execute (validator-only case) or validation
        # didn't accept, we stop here.
        if case.expected_execution is None or not validation.accepted:
            passed = not diagnostics
            return CaseResult(name=case.name, passed=passed, diagnostics=diagnostics)

        # ----- Execution pass -----
        adapter = self._adapter_factory()
        # Fixture-declared overrides only make sense against the mock; real
        # adapters get their behavior from the live substrate.
        if isinstance(adapter, MockROSAdapter):
            _apply_overrides(adapter, case.adapter_overrides)
        runtime = URMLRuntime(adapter)
        try:
            runtime_result = runtime.execute(
                case.program,
                manifest,
                envelope,
                profiles=tuple(case.profiles),
            )
        except Exception as exc:
            diagnostics.append(f"runtime raised: {type(exc).__name__}: {exc}")
            return CaseResult(name=case.name, passed=False, diagnostics=diagnostics)

        # Audit-log assertions only run against the mock (real adapters
        # don't expose a call_log surface).
        call_log = getattr(adapter, "call_log", [])
        diagnostics.extend(_diag_execution(case, runtime_result, call_log))

        return CaseResult(
            name=case.name,
            passed=not diagnostics,
            diagnostics=diagnostics,
        )
