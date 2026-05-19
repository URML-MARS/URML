<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# URML Tools

**Status:** Pre-implementation. Phase 1 target.

Developer-facing tools for working with URML: a CLI, a linter for spec documents, and integration hooks for simulators. Each tool becomes its own subdirectory when implementation begins; for now this README enumerates the planned set and the bar each must clear before merging.

## Planned tools

### `urml` CLI

The single command-line entry point. Subcommands (planned):

- `urml validate <program.urml.yaml> --manifest=<manifest> [--profile=...]` — run the validator against a program; print a structured pass/fail report.
- `urml format <file>` — canonicalize a URML program's YAML formatting (preserve semantics, normalize indentation, sort keys consistently).
- `urml schema <layer>` — print the JSON Schema for a given layer.
- `urml example <profile> <name>` — print a runnable example.
- `urml compile <program.urml.yaml> --runtime=ros2 --dry-run` — show the substrate-level commands a runtime would produce (without executing).

Language: **Python**. `mypy --strict`. Single dependency-light executable; installable via `pip install urml` and via standalone binary releases.

### Spec linter

A small linter that runs over `/spec/**/*.md` and checks the conventions in [`CLAUDE.md`](../CLAUDE.md) §Documentation: Markdown only, frontmatter present where required, no broken internal links, no leftover RFC `<!--` template comments, no stale `[Unreleased]` references after a release.

Useful as a pre-commit hook and as a CI step (CI wired up in Phase 1).

### Simulator hooks

Adapters that connect URML to common simulators so end-to-end examples run without physical hardware:

- **Gazebo** (paired with the ROS 2 reference runtime).
- **jMAVSim / Gazebo + PX4 SITL** (paired with the PX4 reference runtime).
- **Webots** (for the educational profile, when that lands).

These are thin: the bulk of "running URML in a simulator" is the runtime itself; the hook is configuration and a small launch script per platform.

## What goes here vs. elsewhere

**Goes here:**

- Tools that operate *on URML programs* (validate, format, compile).
- Tools that operate *on the spec* (linter).
- Tools that wire URML into common developer environments (simulator hooks).

**Does not go here:**

- The validator itself — that's [`/reference/validator/`](../reference/validator/) (the library); `urml validate` is a thin CLI front-end to it.
- The reference runtimes — those are [`/reference/<runtime>/`](../reference/).
- Web tooling — explicitly out of repo per [`CLAUDE.md`](../CLAUDE.md) §Working Conventions: TypeScript / JavaScript and web tooling live in a separate repository when they exist.
- Hosted services, observability dashboards, fleet management — those are commercial concerns outside the URML organization's open repository.

## Conventions

- Every tool ships with `--help`, exits with a documented nonzero code on failure, and uses structured (JSON-Lines) output behind a `--json` flag.
- No tool collects telemetry. Per [`CLAUDE.md`](../CLAUDE.md): *no code that gathers user data, telemetry, or identifiers without an explicit, opt-in, documented purpose.* Tools fail-closed on this — there is no opt-out flag because there is no telemetry to opt out of.
- Tools that need a network do not require one for their *core* functionality. `urml validate` runs offline. `urml example` may fetch a remote example library in a future release; the local cache works offline.
