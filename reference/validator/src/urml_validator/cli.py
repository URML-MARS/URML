"""`urml` command-line interface.

Subcommands:

  urml validate PROGRAM --manifest MANIFEST [--envelope ENVELOPE] [--profile NAME]... [--json]

Exit codes:

  0   validation accepted (no errors; warnings are still printed)
  1   validation failed (one or more error-severity errors)
  2   usage error (missing files, bad YAML, bad arguments)
  64  internal error (an unhandled exception bubbled out of validate())

The CLI is a thin wrapper around `urml_validator.validate()`. All semantics
live in the validator; this module's job is argument parsing, I/O, and output
formatting. The `--json` flag emits the raw `ValidationResult` so other tools
(the LLM bridge revision flow, CI checks) can consume the structured output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from urml_validator import validate
from urml_validator._version import __version__
from urml_validator.errors import ValidationError, ValidationResult
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
    p_validate.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit the ValidationResult as JSON on stdout instead of pretty text.",
    )
    p_validate.set_defaults(func=cmd_validate)

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
    except _CLILoadError as exc:
        print(f"urml: {exc}", file=sys.stderr)
        return 2

    result = validate(program, manifest, envelope, profiles=tuple(args.profile))

    if args.as_json:
        _emit_json(result)
    else:
        _emit_pretty(result, program_path=args.program)

    return 0 if result.accepted else 1


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
    print(f"  {severity_label} [{issue.code.value}] {location}", file=stream)
    if issue.field:
        print(f"    field: {issue.field}", file=stream)
    print(f"    {issue.message}", file=stream)
    if issue.suggestion:
        print(f"    suggestion: {issue.suggestion}", file=stream)


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
