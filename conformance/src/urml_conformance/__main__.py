"""``python -m urml_conformance`` — run the URML conformance suite.

This is the bring-your-own-adapter entrypoint. Any runtime that
implements the substrate-neutral ``ROSAdapter`` Protocol can be checked
against the same Apache-2.0 fixture contract every reference runtime
passes:

    # Hermetic self-test (default: MockROSAdapter):
    python -m urml_conformance

    # Against your own runtime's adapter:
    python -m urml_conformance --adapter my_pkg.substrate:MyAdapter

    # Just the quadruped fixtures, verbose:
    python -m urml_conformance --filter quadruped -v

    # Write the JSON report (urml.conformance-report/1) a registry entry links:
    python -m urml_conformance --adapter my_pkg.substrate:MyAdapter --report report.json

    # The goal line: every rejected fixture, handed to the runtime itself,
    # must be refused with the expected codes and zero adapter calls:
    python -m urml_conformance --goal-line
    python -m urml_conformance --goal-line --runtime my_pkg.runtime:make_runtime

``--adapter`` takes a ``module:attribute`` spec. The attribute must be
callable with no arguments and return a fresh adapter instance — a
class (``my_pkg:MyAdapter``) or a factory function
(``my_pkg:make_adapter``) both work; the runner calls it once per
fixture so stateful adapters get a clean instance each time.

``--runtime`` (with ``--goal-line`` only) takes the same spec form. The
attribute must be callable with one adapter and return a runtime whose
``execute`` matches ``URMLRuntime.execute``. Fleet fixtures run through
the reference ``FleetRuntime``.

Exit code is 0 only if every selected fixture passes, so this drops
straight into CI. See ``conformance/CONFORMANCE_KIT.md`` for the full
guide. No telemetry: nothing is sent anywhere; the suite runs and
prints locally.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from urml_conformance.fixtures import FixtureCase, discover_fixtures
from urml_conformance.goal_line import rejected_cases, run_goal_line
from urml_conformance.runner import AdapterSpecError, load_factory, run_suite


def _load_factory(spec: str, flag: str, example: str) -> Callable[..., Any]:
    """Resolve a ``module:attribute`` spec to a callable factory, or exit with the reason."""
    try:
        return load_factory(spec, flag, example)
    except AdapterSpecError as exc:
        raise SystemExit(str(exc)) from exc


def _load_adapter_factory(spec: str) -> Callable[[], Any]:
    """Resolve a ``module:attribute`` spec to a zero-arg adapter factory."""
    return _load_factory(spec, "--adapter", "my_pkg.substrate:MyAdapter")


def _load_runtime_factory(spec: str) -> Callable[[Any], Any]:
    """Resolve a ``module:attribute`` spec to a one-adapter runtime factory."""
    return _load_factory(spec, "--runtime", "my_pkg.runtime:make_runtime")


def _run_goal_line(
    cases: list[FixtureCase],
    adapter_factory: Callable[[], Any] | None,
    runtime_spec: str | None,
    adapter_label: str,
    verbose: bool,
) -> int:
    runtime_factory = _load_runtime_factory(runtime_spec) if runtime_spec else None
    report = run_goal_line(cases, adapter_factory, runtime_factory)
    runtime_label = runtime_spec or "URMLRuntime (reference)"
    passed = report.passed_count
    print(f"URML goal line - adapter: {adapter_label}, runtime: {runtime_label}")
    print(
        f"{passed}/{len(report.results)} rejected fixtures refused, "
        "with the expected codes and zero adapter calls"
    )
    if verbose or not report.all_passed:
        print(report.render())
    return 0 if report.all_passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m urml_conformance",
        description="Run the URML conformance suite against a runtime adapter.",
    )
    parser.add_argument(
        "--adapter",
        metavar="MODULE:ATTR",
        default=None,
        help="Adapter factory spec. Omit to self-test with the hermetic MockROSAdapter.",
    )
    parser.add_argument(
        "--filter",
        metavar="SUBSTR",
        default=None,
        help="Only run fixtures whose name contains SUBSTR (e.g. 'quadruped').",
    )
    parser.add_argument(
        "--profile",
        dest="profiles",
        action="append",
        default=None,
        metavar="NAME",
        help=(
            "Only run fixtures that list this profile (repeatable). A registry "
            "compatibility claim for a profile needs every one of them to pass."
        ),
    )
    parser.add_argument(
        "--goal-line",
        action="store_true",
        help="Run the goal-line lane instead: hand every rejected fixture to the "
        "runtime and require a refusal with the expected codes and zero adapter calls.",
    )
    parser.add_argument(
        "--runtime",
        metavar="MODULE:ATTR",
        default=None,
        help="With --goal-line: runtime factory spec, called with one adapter. "
        "Omit to use the reference URMLRuntime.",
    )
    parser.add_argument(
        "--report",
        metavar="PATH",
        type=Path,
        default=None,
        help="Write the JSON report (urml.conformance-report/1) to PATH. Main run only.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Print the full per-case report.")
    args = parser.parse_args(argv)
    if args.runtime and not args.goal_line:
        parser.error("--runtime applies only with --goal-line")
    if args.report and args.goal_line:
        parser.error("--report applies to the main run, not to --goal-line")

    target = args.adapter or "MockROSAdapter (hermetic self-test)"

    if args.goal_line:
        cases = discover_fixtures()
        if args.filter:
            cases = [c for c in cases if args.filter in c.name]
            if not cases:
                print(f"no fixtures match --filter {args.filter!r}", file=sys.stderr)
                return 2
        factory = _load_adapter_factory(args.adapter) if args.adapter else None
        if not rejected_cases(cases):
            print(f"no rejected fixtures match --filter {args.filter!r}", file=sys.stderr)
            return 2
        return _run_goal_line(cases, factory, args.runtime, target, args.verbose)

    try:
        report = run_suite(args.adapter, filter=args.filter, profiles=args.profiles)
    except AdapterSpecError as exc:
        raise SystemExit(str(exc)) from exc
    if not report.results:
        found = (
            f"no fixtures match --filter {args.filter!r}"
            if args.filter
            else f"no fixtures list --profile {args.profiles!r}"
            if args.profiles
            else "no fixtures found"
        )
        print(found, file=sys.stderr)
        return 2

    print(f"URML conformance - adapter: {target}")
    print(f"{report.passed}/{len(report.results)} fixtures passed")
    if args.verbose or not report.all_passed:
        print(report.render())
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        # LF on every platform, so the file's sha256 is the same wherever it is read.
        args.report.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {args.report}")
    return 0 if report.all_passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
