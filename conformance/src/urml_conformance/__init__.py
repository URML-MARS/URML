"""urml_conformance — conformance test suite for URML runtimes.

Public API:

    from urml_conformance import ConformanceRunner

    runner = ConformanceRunner()
    report = runner.run()
    assert report.all_passed, report.render()

The suite ships a set of declarative fixture cases under
``conformance/fixtures/`` that any URML-compatible runtime must satisfy.
For v0.1, the runner targets ``URMLRuntime`` + ``MockROSAdapter``; a v1.0
runner will accept a substrate-adapter factory so real adapters
(``rclpy``, PX4, vendor SDKs) can be exercised through the same suite.

The fixtures themselves are Apache 2.0 and part of the URML Core
Commitment — they're the contract a runtime claims compatibility with.
"""

from __future__ import annotations

from urml_conformance._version import __version__
from urml_conformance.fixtures import (
    ENVELOPE_REGISTRY,
    MANIFEST_REGISTRY,
    AdapterOverrides,
    ExpectedExecution,
    ExpectedValidation,
    FixtureCase,
    discover_fixtures,
    fixtures_root,
    load_fixture,
    resolve_envelope,
    resolve_manifest,
)
from urml_conformance.report import CaseResult, ConformanceReport
from urml_conformance.runner import ConformanceRunner

__all__ = [
    "ENVELOPE_REGISTRY",
    "MANIFEST_REGISTRY",
    "AdapterOverrides",
    "CaseResult",
    "ConformanceReport",
    "ConformanceRunner",
    "ExpectedExecution",
    "ExpectedValidation",
    "FixtureCase",
    "__version__",
    "discover_fixtures",
    "fixtures_root",
    "load_fixture",
    "resolve_envelope",
    "resolve_manifest",
]
