"""`urml` command-line interface.

Subcommands:

  urml validate PROGRAM --manifest MANIFEST [--envelope ENVELOPE] [--profile NAME]... [--json]
  urml execute PROGRAM --manifest MANIFEST [--adapter mock|ros2|px4] [...]
  urml schema --name NAME | --all --out-dir DIR
  urml translate REQUEST --manifest MANIFEST [...]
  urml emit-prompt --manifest MANIFEST [...]
  urml init DIRECTORY [--profile NAME] [--force]
  urml conformance run [--output PATH]

Exit codes:

  0   command succeeded (validation accepted, execution succeeded, all-passed)
  1   command failed at the spec level (validation errors, conformance
      failures, a primitive failed at runtime)
  2   usage error (missing files, bad YAML, bad arguments, optional dep missing)
  64  internal error (an unhandled exception bubbled out of validate())

The CLI is a thin wrapper around `urml_validator.validate()`. All semantics
live in the validator; this module's job is argument parsing, I/O, and output
formatting. The `--json` flag emits the raw `ValidationResult` so other tools
(the LLM bridge revision flow, CI checks) can consume the structured output.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

from urml_validator import validate
from urml_validator._version import __version__
from urml_validator.errors import ValidationError, ValidationResult
from urml_validator.init_templates import PROJECT_TEMPLATES
from urml_validator.schema_export import SCHEMA_REGISTRY, export_schema, write_schemas

_SCHEMA_NAMES = frozenset(SCHEMA_REGISTRY.keys())

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argparse parser. Exposed for test introspection."""
    parser = argparse.ArgumentParser(
        prog="urml",
        description="URML — Universal Robot Language: validator CLI.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"urml-validator {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    p_validate = subparsers.add_parser(
        "validate",
        help="Validate a URML program against a capability manifest.",
        description=(
            "Run the four-pass validator on a URML program. Returns exit 0 if "
            "the program is accepted, exit 1 if any error-severity errors fire."
        ),
    )
    p_validate.add_argument(
        "program",
        type=Path,
        metavar="PROGRAM",
        help="Path to a URML program file (YAML).",
    )
    p_validate.add_argument(
        "--manifest",
        "-m",
        type=Path,
        required=True,
        metavar="PATH",
        help="Path to the target robot's capability manifest (YAML).",
    )
    p_validate.add_argument(
        "--envelope",
        "-e",
        type=Path,
        default=None,
        metavar="PATH",
        help="Optional path to a deployment safety envelope (YAML).",
    )
    p_validate.add_argument(
        "--profile",
        "-p",
        action="append",
        default=[],
        metavar="NAME",
        help="Profile(s) the program targets (repeatable). Currently informational.",
    )
    p_validate_policy = p_validate.add_mutually_exclusive_group()
    p_validate_policy.add_argument(
        "--policy",
        "-P",
        dest="policy_path",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Path to a compliance policy file (YAML). If omitted, the bundled "
            "default US-federal policy is loaded automatically. See RFC-0004."
        ),
    )
    p_validate_policy.add_argument(
        "--no-policy",
        dest="no_policy",
        action="store_true",
        help="Skip Pass 5 (compliance policy) entirely.",
    )
    p_validate.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit the ValidationResult as JSON on stdout instead of pretty text.",
    )
    p_validate.set_defaults(func=cmd_validate)

    # ---- urml execute ----
    p_execute = subparsers.add_parser(
        "execute",
        help="Validate a URML program and then run it against a substrate adapter.",
        description=(
            "Re-validate a URML program (defense-in-depth) and execute it "
            "step by step through a substrate adapter, printing the audit "
            "trace. The default `mock` adapter is a hermetic, zero-dependency "
            "simulation: it proves the URML language and execution pipeline "
            "without touching any robot. `ros2` and `px4` dispatch to a real "
            "(or simulated) substrate and require their optional runtime "
            "package. Requires urml-ros2-runtime (always installed in the "
            "bootstrap venv); the px4 adapter additionally needs "
            "urml-px4-runtime."
        ),
    )
    p_execute.add_argument(
        "program",
        type=Path,
        metavar="PROGRAM",
        help="Path to a URML program file (YAML).",
    )
    p_execute.add_argument(
        "--manifest",
        "-m",
        type=Path,
        required=True,
        metavar="PATH",
        help="Path to the target robot's capability manifest (YAML).",
    )
    p_execute.add_argument(
        "--envelope",
        "-e",
        type=Path,
        default=None,
        metavar="PATH",
        help="Optional path to a deployment safety envelope (YAML).",
    )
    p_execute.add_argument(
        "--profile",
        "-p",
        action="append",
        default=[],
        metavar="NAME",
        help="Profile(s) the program targets (repeatable).",
    )
    p_execute.add_argument(
        "--adapter",
        choices=("mock", "ros2", "px4"),
        default="mock",
        metavar="NAME",
        help=(
            "Substrate adapter to execute through. `mock` (default) is a "
            "hermetic simulation that moves nothing. `ros2` dispatches to a "
            "live ROS 2 graph; `px4` to a connected PX4 autopilot (SITL or "
            "hardware)."
        ),
    )
    p_execute.add_argument(
        "--adapter-config",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Adapter configuration file (YAML). Used by the ros2 and px4 "
            "adapters for connection/topic settings; ignored by mock."
        ),
    )
    p_execute_policy = p_execute.add_mutually_exclusive_group()
    p_execute_policy.add_argument(
        "--policy",
        "-P",
        dest="policy_path",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Path to a compliance policy file (YAML). If omitted, the bundled "
            "default US-federal policy is loaded automatically. See RFC-0004."
        ),
    )
    p_execute_policy.add_argument(
        "--no-policy",
        dest="no_policy",
        action="store_true",
        help="Skip Pass 5 (compliance policy) when re-validating before execution.",
    )
    p_execute.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit the run result as JSON on stdout instead of a pretty trace.",
    )
    p_execute.set_defaults(func=cmd_execute)

    # ---- urml schema ----
    p_schema = subparsers.add_parser(
        "schema",
        help="Export URML JSON Schemas (program, manifest, envelope).",
        description=(
            "Print or write the JSON Schema definitions for URML artifacts. "
            "Used by the LLM bridge as the structured-output contract; also "
            "useful for robot makers writing manifests by hand."
        ),
    )
    schema_excl = p_schema.add_mutually_exclusive_group(required=True)
    schema_excl.add_argument(
        "--name",
        choices=sorted(_SCHEMA_NAMES),
        metavar="NAME",
        help="Print the named schema to stdout. One of: program, manifest, envelope.",
    )
    schema_excl.add_argument(
        "--all",
        dest="all_schemas",
        action="store_true",
        help="Write every schema to --out-dir.",
    )
    p_schema.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="Output directory for --all. Required when --all is used.",
    )
    p_schema.set_defaults(func=cmd_schema)

    # ---- urml translate ----
    p_translate = subparsers.add_parser(
        "translate",
        help="Translate a natural-language request into a validated URML program.",
        description=(
            "Send a natural-language request to an LLM via the URML bridge, "
            "validate the emission against a capability manifest, and print "
            "the accepted URML program. Requires the urml-llm-bridge package "
            "(install with: pip install urml-llm-bridge[anthropic] OR [openai])."
        ),
    )
    p_translate.add_argument(
        "request",
        metavar="REQUEST",
        help="The user's natural-language request, in quotes.",
    )
    p_translate.add_argument(
        "--manifest",
        "-m",
        type=Path,
        required=True,
        metavar="PATH",
        help="Path to the target robot's capability manifest (YAML).",
    )
    p_translate.add_argument(
        "--envelope",
        "-e",
        type=Path,
        default=None,
        metavar="PATH",
        help="Optional path to a deployment safety envelope (YAML).",
    )
    p_translate.add_argument(
        "--profile",
        "-p",
        action="append",
        default=[],
        metavar="NAME",
        help="Profile(s) the request targets (repeatable).",
    )
    p_translate_policy = p_translate.add_mutually_exclusive_group()
    p_translate_policy.add_argument(
        "--policy",
        "-P",
        dest="policy_path",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Path to a compliance policy file (YAML). If omitted, the bundled "
            "default US-federal policy is loaded automatically."
        ),
    )
    p_translate_policy.add_argument(
        "--no-policy",
        dest="no_policy",
        action="store_true",
        help="Skip Pass 5 (compliance policy) when validating LLM emissions.",
    )
    p_translate.add_argument(
        "--provider",
        choices=("anthropic", "openai", "echo"),
        default="anthropic",
        metavar="NAME",
        help="LLM provider to use. Default: anthropic. `echo` is a hermetic "
        "test provider requiring --echo-response-file.",
    )
    p_translate.add_argument(
        "--model",
        default=None,
        metavar="MODEL",
        help="Override the provider's default model.",
    )
    p_translate.add_argument(
        "--max-revisions",
        type=int,
        default=3,
        metavar="N",
        help="Maximum number of validator-feedback revision attempts. Default: 3.",
    )
    p_translate.add_argument(
        "--echo-response-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="Path to a YAML/JSON file with the canned response, used only with --provider echo.",
    )
    p_translate.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit the accepted program as JSON on stdout (default: YAML).",
    )
    p_translate.add_argument(
        "--out",
        type=Path,
        default=None,
        metavar="PATH",
        help="Write the accepted program to PATH instead of stdout.",
    )
    p_translate.set_defaults(func=cmd_translate)

    # ---- urml emit-prompt ----
    p_emit = subparsers.add_parser(
        "emit-prompt",
        help="Print the system prompt the LLM bridge would build for a given manifest/envelope.",
        description=(
            "Assemble and emit the system prompt the URML bridge would send to "
            "an LLM for the given manifest + envelope + profile set. Useful for "
            "debugging, transparency, and offline review without needing an API key."
        ),
    )
    p_emit.add_argument(
        "--manifest",
        "-m",
        type=Path,
        required=True,
        metavar="PATH",
        help="Path to the target robot's capability manifest (YAML).",
    )
    p_emit.add_argument(
        "--envelope",
        "-e",
        type=Path,
        default=None,
        metavar="PATH",
        help="Optional path to a deployment safety envelope (YAML).",
    )
    p_emit.add_argument(
        "--profile",
        "-p",
        action="append",
        default=[],
        metavar="NAME",
        help="Profile(s) the prompt should target (repeatable).",
    )
    p_emit.add_argument(
        "--no-few-shots",
        dest="include_few_shots",
        action="store_false",
        default=True,
        help="Omit the few-shot examples block from the prompt.",
    )
    p_emit.add_argument(
        "--out",
        type=Path,
        default=None,
        metavar="PATH",
        help="Write the prompt to PATH instead of stdout.",
    )
    p_emit.set_defaults(func=cmd_emit_prompt)

    # ---- urml init ----
    p_init = subparsers.add_parser(
        "init",
        help="Scaffold a starter URML project (manifest, envelope, sample program, Makefile).",
        description=(
            "Create a new directory with a minimal but runnable URML project: "
            "a capability manifest, an optional envelope, a sample program "
            "with its natural-language prompt, a README, and a Makefile. "
            "Pick `--profile home`, `--profile industrial`, or `--profile drone`; "
            "defaults to home."
        ),
    )
    p_init.add_argument(
        "directory",
        type=Path,
        metavar="DIRECTORY",
        help="Where to write the project. Must be empty (or use --force).",
    )
    p_init.add_argument(
        "--profile",
        "-p",
        choices=sorted(PROJECT_TEMPLATES.keys()),
        default="home",
        metavar="NAME",
        help="Profile to scaffold. Default: home.",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Allow writing into a non-empty directory; existing files are overwritten.",
    )
    p_init.set_defaults(func=cmd_init)

    # ---- urml conformance ----
    p_conformance = subparsers.add_parser(
        "conformance",
        help="Run the URML conformance suite against a runtime.",
        description=(
            "Run the public URML conformance suite and emit a structured report. "
            "Used by runtime authors to produce the JSON artifact required for "
            "the Compatible Runtimes registry. Requires the urml-conformance "
            "package (install with: pip install urml-conformance)."
        ),
    )
    p_conformance_sub = p_conformance.add_subparsers(
        dest="conformance_command", required=True, metavar="SUBCOMMAND"
    )
    p_conformance_run = p_conformance_sub.add_parser(
        "run",
        help="Run every fixture in the bundled suite and emit a report.",
        description=(
            "Run every fixture against the default hermetic adapter and emit a "
            "ConformanceReport. Exit 0 if all fixtures pass, 1 if any fail."
        ),
    )
    p_conformance_run.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        metavar="PATH",
        help="Write the JSON report to PATH (creates parents as needed).",
    )
    p_conformance_run.set_defaults(func=cmd_conformance_run)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Run the `urml` CLI.

    Args:
        argv: Argument vector excluding the program name. Defaults to sys.argv[1:].

    Returns:
        Exit code (see module docstring for the contract).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        rc: int = args.func(args)
        return rc
    except SystemExit:
        raise
    except Exception as exc:
        print(f"urml: internal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 64


# ---------------------------------------------------------------------------
# `urml validate`
# ---------------------------------------------------------------------------


def cmd_validate(args: argparse.Namespace) -> int:
    """Implement the `urml validate` subcommand."""
    try:
        program = _load_yaml(args.program, kind="program")
        manifest = _load_yaml(args.manifest, kind="manifest")
        envelope: dict[str, Any] | None = (
            _load_yaml(args.envelope, kind="envelope") if args.envelope is not None else None
        )
        policy_arg = _resolve_policy_arg(args)
    except _CLILoadError as exc:
        print(f"urml: {exc}", file=sys.stderr)
        return 2

    result = validate(
        program,
        manifest,
        envelope,
        profiles=tuple(args.profile),
        policy=policy_arg,
    )

    if args.as_json:
        _emit_json(result)
    else:
        _emit_pretty(result, program_path=args.program)

    return 0 if result.accepted else 1


def _resolve_policy_arg(args: argparse.Namespace) -> Any:
    """Map the CLI policy flags to the `policy` parameter of validate().

    Returns:
      - None if --no-policy was passed.
      - The parsed policy dict if --policy PATH was passed.
      - The "DEFAULT" sentinel string otherwise.
    """
    if getattr(args, "no_policy", False):
        return None
    policy_path: Path | None = getattr(args, "policy_path", None)
    if policy_path is None:
        return "DEFAULT"
    return _load_yaml(policy_path, kind="policy")


# ---------------------------------------------------------------------------
# `urml execute`
# ---------------------------------------------------------------------------

# Per-adapter substrate honesty banner. The mock line is deliberately blunt:
# calling a mock run "a robot moved" is exactly the overclaiming the demo
# path exists to avoid.
_SUBSTRATE_NOTE = {
    "mock": (
        "HERMETIC MOCK. No physical or simulated robot, no actuator moved. "
        "This proves the URML language, validation, and execution pipeline "
        "end to end. For a real simulated autopilot, run --adapter px4 "
        "against PX4 SITL (see docs/demos/sentence-to-flight.md)."
    ),
    "ros2": (
        "REAL ROS 2. Primitives dispatched to the live ROS 2 graph via "
        "rclpy. Whatever is listening on that graph will act."
    ),
    "px4": (
        "PX4 / MAVLink. Primitives dispatched to the connected autopilot "
        "(PX4 SITL or hardware). The vehicle will act."
    ),
}


def cmd_execute(args: argparse.Namespace) -> int:
    """Implement the `urml execute` subcommand.

    Re-validates the program with the caller's chosen policy (honoring
    ``--no-policy`` / ``--policy``), then runs it through the selected
    substrate adapter and prints the audit trace.

    The runtime (``urml_ros2_runtime``) is an optional dependency of the
    validator; the import is lazy so ``urml validate`` works without it.
    Because this command validates explicitly with the requested policy, the
    runtime is constructed with ``revalidate=False`` — re-running the
    runtime's own default-policy re-validation would silently defeat
    ``--no-policy`` / ``--policy``. Skipping the validator entirely is still
    prohibited (CLAUDE.md); the validation happens here instead.
    """
    try:
        from urml_ros2_runtime import (  # type: ignore[import-not-found,unused-ignore]
            URMLRuntime,
        )
        from urml_ros2_runtime import (
            PrimitiveExecutionError,
            UnsupportedCompositionError,
            ValidationRejectedError,
        )
    except ImportError:
        print(
            "urml: error: `execute` requires urml-ros2-runtime.\n"
            "  Install with: pip install urml-ros2-runtime",
            file=sys.stderr,
        )
        return 2

    # ----- Load inputs -----
    try:
        program = _load_yaml(args.program, kind="program")
        manifest = _load_yaml(args.manifest, kind="manifest")
        envelope: dict[str, Any] | None = (
            _load_yaml(args.envelope, kind="envelope") if args.envelope is not None else None
        )
        policy_arg = _resolve_policy_arg(args)
    except _CLILoadError as exc:
        print(f"urml: {exc}", file=sys.stderr)
        return 2

    profiles = tuple(args.profile)

    # ----- Defense-in-depth validation (surfaced, with the chosen policy) -----
    result = validate(program, manifest, envelope, profiles=profiles, policy=policy_arg)
    if not result.accepted:
        if args.as_json:
            _emit_json(result)
        else:
            print(
                "urml: execution refused: the program failed re-validation. "
                "URML executes only validated programs (CLAUDE.md safety boundary).",
                file=sys.stderr,
            )
            _emit_pretty(result, program_path=args.program)
        return 1

    # ----- Build the substrate adapter -----
    cleanup: list[Any] = []
    try:
        adapter = _build_execute_adapter(args, cleanup)
    except _CLILoadError as exc:
        print(f"urml: {exc}", file=sys.stderr)
        return 2

    # ----- Execute -----
    try:
        runtime = URMLRuntime(adapter, revalidate=False)
        try:
            rr = runtime.execute(program, manifest, envelope, profiles=profiles)
        except ValidationRejectedError as exc:
            # Should not happen (revalidate=False) — surface defensively.
            print(f"urml: internal error: runtime rejected a pre-validated program: {exc}", file=sys.stderr)
            return 64
        except UnsupportedCompositionError as exc:
            print(f"urml: execution error: {exc}", file=sys.stderr)
            return 1
        except PrimitiveExecutionError as exc:
            print(f"urml: execution error: a primitive failed: {exc}", file=sys.stderr)
            return 1
    finally:
        for close in cleanup:
            try:
                close()
            except Exception:  # noqa: BLE001 — best-effort teardown, never mask the result
                pass

    if args.as_json:
        _emit_execute_json(rr, args.adapter)
    else:
        _emit_execute_pretty(rr, args.adapter, program_path=args.program)

    return 0 if rr.success else 1


def _build_execute_adapter(args: argparse.Namespace, cleanup: list[Any]) -> Any:
    """Construct the chosen substrate adapter.

    Appends teardown callables to ``cleanup`` (called in cmd_execute's
    finally). Raises ``_CLILoadError`` for usage problems (missing optional
    dep, missing config) so the caller maps them to exit code 2 — never a
    traceback.
    """
    adapter_name = args.adapter

    if adapter_name == "mock":
        from urml_ros2_runtime import MockROSAdapter  # type: ignore[import-not-found,unused-ignore]

        return MockROSAdapter()

    if adapter_name == "ros2":
        try:
            import rclpy  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise _CLILoadError(
                "the ros2 adapter requires a ROS 2 environment (rclpy is not "
                "importable). Source a ROS 2 install, or use --adapter mock "
                "for a hermetic run."
            ) from exc
        from urml_ros2_runtime import (  # type: ignore[import-not-found,unused-ignore]
            RclpyAdapter,
            load_adapter_config,
        )

        config = None
        if args.adapter_config is not None:
            if not args.adapter_config.is_file():
                raise _CLILoadError(f"adapter-config file not found: {args.adapter_config}")
            config = load_adapter_config(args.adapter_config)
        rclpy.init()
        cleanup.append(rclpy.shutdown)
        adapter = RclpyAdapter(config)
        cleanup.append(adapter.close)
        return adapter

    if adapter_name == "px4":
        try:
            from urml_px4_runtime import (  # type: ignore[import-not-found,unused-ignore]
                PX4Adapter,
                load_px4_config,
            )
        except ImportError as exc:
            raise _CLILoadError(
                "the px4 adapter requires urml-px4-runtime. Install with: "
                "pip install urml-px4-runtime (or use --adapter mock)."
            ) from exc

        config = None
        if args.adapter_config is not None:
            if not args.adapter_config.is_file():
                raise _CLILoadError(f"adapter-config file not found: {args.adapter_config}")
            config = load_px4_config(args.adapter_config)
        try:
            adapter = PX4Adapter(config)
        except Exception as exc:  # noqa: BLE001 — surface pymavlink-missing etc. as usage error
            raise _CLILoadError(
                f"could not construct the px4 adapter: {exc} "
                f"(a reachable PX4 SITL/autopilot is also required to execute)."
            ) from exc
        close = getattr(adapter, "close", None)
        if callable(close):
            cleanup.append(close)
        return adapter

    raise _CLILoadError(f"unknown adapter: {adapter_name!r}")


def _format_audit_entry(index: int, entry: dict[str, Any]) -> str:
    """One audit-log line: `  N. method   key=val key=val`."""
    method = entry.get("method", "<unknown>")
    parts = []
    for key, value in entry.items():
        if key == "method" or value is None:
            continue
        text = repr(value) if not isinstance(value, str) else value
        if len(text) > 60:
            text = text[:57] + "..."
        parts.append(f"{key}={text}")
    tail = ("  " + " ".join(parts)) if parts else ""
    return f"  {index:>2}. {method}{tail}"


def _emit_execute_pretty(rr: Any, adapter_name: str, *, program_path: Path) -> None:
    """Human-readable rendering of a RuntimeResult + the honest substrate note."""
    out = sys.stdout
    print(f"URML execute: {program_path}", file=out)
    print(f"  adapter:   {adapter_name}", file=out)
    print(f"  substrate: {_SUBSTRATE_NOTE.get(adapter_name, 'unknown')}", file=out)
    print("  re-validation: passed (executed only after the validator accepted it)", file=out)

    audit = list(rr.audit_log)
    print(f"\n  trace ({rr.steps_executed} step(s) executed, {len(audit)} adapter call(s)):", file=out)
    if audit:
        for i, entry in enumerate(audit, start=1):
            print(_format_audit_entry(i, entry), file=out)
    elif rr.steps_executed > 0:
        # Steps ran but the adapter records no call log. This is true of
        # PX4Adapter, whose effects are MAVLink commands to an autopilot,
        # not recordable mock calls. Do not imply nothing happened.
        print(
            f"    ({rr.steps_executed} step(s) dispatched; this adapter keeps "
            "no call log, so there is no per-step trace. See RESULT below.)",
            file=out,
        )
    else:
        print("    (no steps executed; the program's behavior tree was empty)", file=out)

    if rr.bindings:
        print("\n  bindings:", file=out)
        for name, value in rr.bindings.items():
            text = repr(value)
            if len(text) > 72:
                text = text[:69] + "..."
            print(f"    {name} = {text}", file=out)

    status = "SUCCESS" if rr.success else "FAILURE"
    print(f"\n  RESULT: {status} ({rr.steps_executed} step(s) executed)", file=out)
    if not rr.success and rr.last_outcome is not None:
        print(f"    last outcome: {rr.last_outcome!r}", file=out)


def _emit_execute_json(rr: Any, adapter_name: str) -> None:
    """JSON rendering for machine consumers."""
    payload = {
        "adapter": adapter_name,
        "substrate_is_mock": adapter_name == "mock",
        "revalidated": True,
        "result": rr.model_dump(mode="json"),
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, default=str)
    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def _emit_pretty(result: ValidationResult, program_path: Path) -> None:
    """Human-readable rendering of a ValidationResult."""
    out = sys.stdout
    err = sys.stderr
    if result.accepted:
        print(f"Validation passed: {program_path}", file=out)
        if result.warnings:
            print(f"  ({len(result.warnings)} warning(s))", file=out)
            for w in result.warnings:
                _render_issue(w, stream=out, severity_label="WARN ")
        return

    print(
        f"Validation failed: {program_path} ({len(result.errors)} error(s)"
        f"{', ' + str(len(result.warnings)) + ' warning(s)' if result.warnings else ''})",
        file=err,
    )
    for e in result.errors:
        _render_issue(e, stream=err, severity_label="ERROR")
    for w in result.warnings:
        _render_issue(w, stream=err, severity_label="WARN ")


def _render_issue(
    issue: ValidationError,
    *,
    stream: Any,
    severity_label: str,
) -> None:
    """Render one ValidationError as 3-4 lines on the given stream."""
    location = "/".join(issue.path) if issue.path else "<program>"
    print(file=stream)
    print(f"  {severity_label} [{issue.code_str}] {location}", file=stream)
    if issue.field:
        print(f"    field: {issue.field}", file=stream)
    print(f"    {issue.message}", file=stream)
    if issue.suggestion:
        print(f"    suggestion: {issue.suggestion}", file=stream)
    if issue.detail:
        # Render policy-error detail in a stable, scannable shape.
        for key, value in issue.detail.items():
            print(f"    {key}: {value}", file=stream)


def _emit_json(result: ValidationResult) -> None:
    """JSON rendering for machine consumers (LLM bridge, CI checks)."""
    payload = result.model_dump(mode="json")
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
# `urml schema`
# ---------------------------------------------------------------------------


def cmd_schema(args: argparse.Namespace) -> int:
    """Implement the `urml schema` subcommand."""
    if args.all_schemas:
        if args.out_dir is None:
            print("urml: error: --all requires --out-dir DIR.", file=sys.stderr)
            return 2
        written = write_schemas(args.out_dir)
        for path in written:
            print(f"wrote {path}", file=sys.stderr)
        return 0

    # Single-schema mode: print to stdout.
    schema = export_schema(args.name)
    json.dump(schema, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


# ---------------------------------------------------------------------------
# `urml translate`
# ---------------------------------------------------------------------------


def cmd_translate(args: argparse.Namespace) -> int:
    """Implement the `urml translate` subcommand.

    This subcommand requires the `urml-llm-bridge` package, which is not a
    hard dependency of `urml-validator`. The import is lazy so `urml validate`
    and `urml schema` work even when the bridge isn't installed.
    """
    try:
        from urml_llm_bridge import (  # type: ignore[import-not-found,unused-ignore]
            Bridge,
            BridgePolicyViolation,
            BridgeRevisionExhausted,
            ProviderError,
        )
    except ImportError:
        print(
            "urml: error: `translate` requires urml-llm-bridge.\n"
            "  Install with: pip install urml-llm-bridge[anthropic]\n"
            "  Or:           pip install urml-llm-bridge[openai]",
            file=sys.stderr,
        )
        return 2

    # ----- Load fixtures -----
    try:
        manifest = _load_yaml(args.manifest, kind="manifest")
        envelope: dict[str, Any] | None = (
            _load_yaml(args.envelope, kind="envelope") if args.envelope is not None else None
        )
        policy_arg = _resolve_policy_arg(args)
    except _CLILoadError as exc:
        print(f"urml: {exc}", file=sys.stderr)
        return 2

    # ----- Construct provider -----
    try:
        provider = _build_provider(args)
    except _CLILoadError as exc:
        print(f"urml: {exc}", file=sys.stderr)
        return 2

    bridge = Bridge(
        provider=provider,
        manifest=manifest,
        envelope=envelope,
        profiles=tuple(args.profile),
        max_revisions=args.max_revisions,
        policy=policy_arg,
    )

    # ----- Translate -----
    try:
        result = bridge.translate(args.request)
    except ProviderError as exc:
        print(f"urml: provider error: {exc}", file=sys.stderr)
        return 1
    except BridgePolicyViolation as exc:
        print(
            f"urml: translation aborted: compliance policy rejected the target "
            f"robot after {exc.attempts} attempt(s). Policy errors cannot be "
            f"fixed by editing the URML program.",
            file=sys.stderr,
        )
        last = exc.last_result
        for issue in getattr(last, "errors", []) or []:
            _render_issue(issue, stream=sys.stderr, severity_label="ERROR")
        return 1
    except BridgeRevisionExhausted as exc:
        print(
            f"urml: translation failed: validator rejected the LLM's emission in all {exc.attempts} attempt(s).",
            file=sys.stderr,
        )
        last = exc.last_result
        for issue in getattr(last, "errors", []) or []:
            _render_issue(issue, stream=sys.stderr, severity_label="ERROR")
        return 1

    # ----- Emit accepted program -----
    if result.program is None:
        print("urml: internal error: bridge returned no program despite accepting.", file=sys.stderr)
        return 64

    text = _render_program(result.program, as_json=args.as_json)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")

    print(
        f"Translation accepted after {result.revision_count} revision(s); "
        f"profile(s)={','.join(args.profile) or '(none)'}",
        file=sys.stderr,
    )
    return 0


def _build_provider(args: argparse.Namespace) -> Any:
    """Construct the right provider based on the CLI args.

    Return type is intentionally `Any` (rather than the bridge's `LLMProvider`)
    because `urml-llm-bridge` is an optional dependency of `urml-validator` —
    importing it at the module top level would break installs that don't
    include the bridge.

    Raises `_CLILoadError` for usage problems (missing API key, missing echo
    response file, etc.) so the caller can map them to exit code 2.
    """
    if args.provider == "echo":
        return _build_echo_provider(args)
    if args.provider == "anthropic":
        return _build_anthropic_provider(args)
    if args.provider == "openai":
        return _build_openai_provider(args)
    raise _CLILoadError(f"unknown provider: {args.provider!r}")


def _build_echo_provider(args: argparse.Namespace) -> Any:
    from urml_llm_bridge import EchoProvider

    if args.echo_response_file is None:
        raise _CLILoadError("--provider echo requires --echo-response-file PATH.")
    if not args.echo_response_file.is_file():
        raise _CLILoadError(f"echo-response file not found: {args.echo_response_file}")
    raw = args.echo_response_file.read_text(encoding="utf-8")
    # Accept either a JSON object (passed through verbatim) or a YAML mapping
    # (re-serialized as JSON for the EchoProvider, which expects the raw
    # response string a real LLM would emit).
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        try:
            parsed = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise _CLILoadError(f"echo-response file is neither valid JSON nor YAML: {exc}") from exc
    if not isinstance(parsed, dict):
        raise _CLILoadError(
            f"echo-response file did not contain a top-level mapping: {args.echo_response_file}"
        )
    return EchoProvider(scripted=[json.dumps(parsed)])


def _build_anthropic_provider(args: argparse.Namespace) -> Any:
    try:
        # type: ignore[import-not-found,unused-ignore]
        from urml_llm_bridge.providers.anthropic import (  # type: ignore[import-not-found,unused-ignore]
            AnthropicProvider,
        )
    except ImportError as exc:
        raise _CLILoadError(
            "anthropic SDK not installed. Install with: pip install urml-llm-bridge[anthropic]"
        ) from exc
    if "ANTHROPIC_API_KEY" not in os.environ:
        raise _CLILoadError(
            "ANTHROPIC_API_KEY environment variable is not set. Set it or pick a different --provider."
        )
    kwargs: dict[str, Any] = {}
    if args.model is not None:
        kwargs["model"] = args.model
    return AnthropicProvider(**kwargs)


def _build_openai_provider(args: argparse.Namespace) -> Any:
    try:
        from urml_llm_bridge.providers.openai import OpenAIProvider  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise _CLILoadError(
            "openai SDK not installed. Install with: pip install urml-llm-bridge[openai]"
        ) from exc
    if "OPENAI_API_KEY" not in os.environ:
        raise _CLILoadError(
            "OPENAI_API_KEY environment variable is not set. Set it or pick a different --provider."
        )
    kwargs: dict[str, Any] = {}
    if args.model is not None:
        kwargs["model"] = args.model
    return OpenAIProvider(**kwargs)


def _render_program(program: dict[str, Any], *, as_json: bool) -> str:
    """Render an accepted URML program in the chosen surface format."""
    if as_json:
        return json.dumps(program, indent=2, sort_keys=True)
    return yaml.safe_dump(program, sort_keys=False, default_flow_style=False)


# ---------------------------------------------------------------------------
# `urml init`
# ---------------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    """Implement the `urml init` subcommand.

    Writes a starter project into ``args.directory``. Refuses to write into
    a non-empty directory unless ``--force`` is passed. The set of files
    landed depends on ``--profile``; see ``init_templates.PROJECT_TEMPLATES``.
    """
    target: Path = args.directory
    factory = PROJECT_TEMPLATES[args.profile]
    files = factory(target.name or args.profile)

    # Pre-flight: refuse to clobber a non-empty directory without --force.
    if target.exists():
        if not target.is_dir():
            print(f"urml: error: {target} exists and is not a directory.", file=sys.stderr)
            return 2
        contents = list(target.iterdir())
        if contents and not args.force:
            print(
                f"urml: error: {target} is not empty (use --force to overwrite).",
                file=sys.stderr,
            )
            return 2
    else:
        target.mkdir(parents=True, exist_ok=True)

    # Write every file.
    written: list[Path] = []
    for relative_path, content in files.items():
        path = target / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)

    print(f"Initialized {args.profile} project at {target}", file=sys.stderr)
    for path in sorted(written):
        print(f"  wrote {path.relative_to(target)}", file=sys.stderr)
    print(
        "\nNext steps:\n"
        f"  cd {target}\n"
        "  urml validate program.urml.yaml --manifest manifest.yaml"
        + (" --envelope envelope.yaml" if "envelope.yaml" in files else "")
        + f" --profile {args.profile}",
        file=sys.stderr,
    )
    return 0


# ---------------------------------------------------------------------------
# `urml conformance run`
# ---------------------------------------------------------------------------


def cmd_conformance_run(args: argparse.Namespace) -> int:
    """Implement the `urml conformance run` subcommand.

    The `urml-conformance` package is an optional dependency of `urml-validator`
    (it depends on the validator, so installing it pulls validator in but not
    vice versa). The import is lazy so `urml validate` and `urml schema` work
    even when the conformance suite isn't installed.
    """
    try:
        from urml_conformance import ConformanceRunner  # type: ignore[import-not-found,unused-ignore]
    except ImportError:
        print(
            "urml: error: `conformance` requires urml-conformance.\n"
            "  Install with: pip install urml-conformance",
            file=sys.stderr,
        )
        return 2

    report = ConformanceRunner().run()

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)

    print(report.render(), file=sys.stderr)
    return 0 if report.all_passed else 1


# ---------------------------------------------------------------------------
# `urml emit-prompt`
# ---------------------------------------------------------------------------


def cmd_emit_prompt(args: argparse.Namespace) -> int:
    """Implement the `urml emit-prompt` subcommand.

    Prints the system prompt the LLM bridge would assemble for the given
    manifest / envelope / profile set. Useful for debugging the prompt,
    reviewing what gets sent to the LLM, and inspecting few-shot examples
    without requiring an API key.

    Requires the `urml-llm-bridge` package; the import is lazy.
    """
    try:
        from urml_llm_bridge import build_system_prompt, few_shots_for  # type: ignore[import-not-found,unused-ignore]
    except ImportError:
        print(
            "urml: error: `emit-prompt` requires urml-llm-bridge.\n"
            "  Install with: pip install urml-llm-bridge",
            file=sys.stderr,
        )
        return 2

    try:
        manifest = _load_yaml(args.manifest, kind="manifest")
        envelope: dict[str, Any] | None = (
            _load_yaml(args.envelope, kind="envelope") if args.envelope is not None else None
        )
    except _CLILoadError as exc:
        print(f"urml: {exc}", file=sys.stderr)
        return 2

    profiles = tuple(args.profile)
    few_shots = list(few_shots_for(profiles)) if args.include_few_shots else []
    schema = export_schema("program")
    prompt = build_system_prompt(
        schema=schema,
        manifest=manifest,
        envelope=envelope,
        profiles=profiles,
        few_shots=few_shots,
    )

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(prompt + ("" if prompt.endswith("\n") else "\n"), encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(prompt)
        if not prompt.endswith("\n"):
            sys.stdout.write("\n")

    return 0


# ---------------------------------------------------------------------------
# YAML loader helper
# ---------------------------------------------------------------------------


class _CLILoadError(Exception):
    """Internal: any file/YAML error during input loading."""


def _load_yaml(path: Path, *, kind: str) -> dict[str, Any]:
    if not path.is_file():
        raise _CLILoadError(f"{kind} file not found: {path}")
    try:
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise _CLILoadError(f"{kind} YAML parse error in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise _CLILoadError(f"{kind} file {path} did not contain a YAML mapping at the top level.")
    return data


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
