"""urml_conformance — conformance test suite for URML runtimes.

Public API:

    from urml_conformance import ConformanceRunner

    runner = ConformanceRunner()
    report = runner.run()
    assert report.all_passed, report.render()

The suite ships a set of declarative fixture cases under
``conformance/fixtures/`` that any URML-compatible runtime must satisfy.
The runner defaults to ``URMLRuntime`` + ``MockROSAdapter`` for a
hermetic self-test, and accepts an ``adapter_factory=`` so real adapters
(``rclpy``, PX4, vendor SDKs) run through the same suite. The
bring-your-own-adapter entrypoint wraps this:
``python -m urml_conformance --adapter your_pkg:YourAdapter`` (see
``conformance/CONFORMANCE_KIT.md``).

The goal-line lane (``run_goal_line``, ``python -m urml_conformance
--goal-line``) hands every rejected fixture to the runtime itself and
requires a refusal with the expected codes and zero adapter calls.

``run_suite`` runs the published fixture set against an adapter spec and
returns a ``urml.conformance-report/1`` report that names the adapter, the
versions and the fixture set; ``urml conformance run --output`` and
``python -m urml_conformance --report`` write it as JSON.

The fixtures themselves are Apache 2.0 and part of the URML Core
Commitment — they're the contract a runtime claims compatibility with.
"""

from __future__ import annotations

from urml_conformance._version import __version__
from urml_conformance.fixtures import (
    ENVELOPE_REGISTRY,
    MANIFEST_REGISTRY,
    RULEBOOK_REGISTRY,
    AdapterOverrides,
    ExpectedExecution,
    ExpectedValidation,
    FixtureCase,
    discover_fixtures,
    fixture_paths,
    fixtures_root,
    fixtures_sha256,
    load_fixture,
    resolve_envelope,
    resolve_manifest,
    resolve_rulebook,
)
from urml_conformance.goal_line import RecordedCall, RecordingAdapter, run_goal_line
from urml_conformance.report import DEFAULT_ADAPTER, REPORT_FORMAT, CaseResult, ConformanceReport
from urml_conformance.runner import (
    AdapterSpecError,
    ConformanceRunner,
    load_adapter_factory,
    load_factory,
    run_suite,
)

__all__ = [
    "DEFAULT_ADAPTER",
    "ENVELOPE_REGISTRY",
    "MANIFEST_REGISTRY",
    "REPORT_FORMAT",
    "RULEBOOK_REGISTRY",
    "AdapterOverrides",
    "AdapterSpecError",
    "CaseResult",
    "ConformanceReport",
    "ConformanceRunner",
    "ExpectedExecution",
    "ExpectedValidation",
    "FixtureCase",
    "RecordedCall",
    "RecordingAdapter",
    "__version__",
    "discover_fixtures",
    "fixture_paths",
    "fixtures_root",
    "fixtures_sha256",
    "load_adapter_factory",
    "load_factory",
    "load_fixture",
    "resolve_envelope",
    "resolve_manifest",
    "resolve_rulebook",
    "run_goal_line",
    "run_suite",
]
