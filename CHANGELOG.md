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

# Changelog

All notable changes to URML are recorded in this file.

The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), and URML versioning is per-artifact semantic versioning (see [`MANIFESTO.md`](MANIFESTO.md) §License Direction and [`CONTRIBUTING.md`](CONTRIBUTING.md) — each spec layer, profile, and reference implementation versions independently; this top-level changelog records *project-level* milestones).

## [Unreleased]

### Added

- Phase 0 repository scaffold: governance and policy files, RFC process, layer/profile stubs, reference-implementation stubs, the first runnable example (`examples/home/red-mug.*`), and the conformance test suite placeholder.
- [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) — the list of components that will always remain Apache 2.0.
- [`docs/rfcs/0001-rfc-process.md`](docs/rfcs/0001-rfc-process.md) — the meta-RFC documenting how RFCs work.
- `urml-validator` Python package skeleton at [`reference/validator/`](reference/validator/) (pre-alpha v0.1.0a0). Includes pydantic v2 schemas for Layer-1 (capability manifest), Layer-2 (all 12 RFC-0002 primitives), Layer-3 (Sequence, Branch, Parallel, Retry, on-error), the safety envelope, and the top-level `URMLProgram`. Tested with 22 schema-parse cases including the `red-mug` example.
- Four-pass validator at `urml_validator.validate(program, manifest, envelope, profiles)` (pre-alpha v0.1.0a1). Argument, capability, safety-envelope, and binding-name passes; structured `ValidationError` with stable namespaced error codes (`argument.*`, `capability.*`, `envelope.*`, `binding.*`) consumable by the future LLM bridge. The `red-mug` example now validates end-to-end against the TurtleBot fixture; 22 additional behavior tests cover every error code.
- `urml` command-line interface, installed as a console script via the package's `[project.scripts]` entry point. Subcommand `urml validate <program> --manifest <path> [--envelope <path>] [--profile <name>] [--json]`. Pretty human-readable output by default; structured JSON output behind `--json` for tooling. Exit codes: 0 accepted, 1 validation failed, 2 usage error, 64 internal error. 13 CLI tests covering happy path, file-not-found, bad YAML, validation failure, JSON output, and argparse behaviours.
- JSON Schema export at `urml_validator.export_schema(name)` / `export_all_schemas()` / `write_schemas(dir)`, plus a new `urml schema [--name NAME | --all --out-dir DIR]` CLI subcommand. Emits Draft 2020-12 schemas for `URMLProgram`, `CapabilityManifest`, and `SafetyEnvelope` — the contract the LLM bridge will consume for structured-output prompting (Anthropic tool use, OpenAI JSON mode, open-weights structured output). Stable `$id`, `$schema`, and `$comment`-encoded provenance per artifact. 12 new tests cover registry coverage, write-to-disk, format stability, and primitive-name regression.
- `urml-llm-bridge` Python package skeleton at [`reference/llm-bridge/`](reference/llm-bridge/) (pre-alpha v0.1.0a0). Provider-agnostic adapter pattern (`LLMProvider` Protocol), hermetic `EchoProvider` for tests, `Bridge.translate(user_request)` with a validator-feedback revision loop, system-prompt builder that inlines the JSON Schema + manifest summary + envelope + few-shot examples, built-in `red-mug` few-shot fixture, and bridge-specific errors (`BridgeRevisionExhausted`, `ProviderError`). 15 tests cover happy path, revision-then-accept, revision-exhausted, provider misbehaviour (non-JSON, empty, non-object, raise), and prompt-builder output.
- Real provider adapters for the LLM bridge: `urml_llm_bridge.providers.anthropic.AnthropicProvider` (uses Anthropic tool use with an `emit_urml` tool whose `input_schema` is the URML program schema; default model `claude-sonnet-4-6`) and `urml_llm_bridge.providers.openai.OpenAIProvider` (uses `response_format={"type": "json_object"}` and conveys the schema via the system prompt; default model `gpt-4o`). Both are opt-in extras (`pip install urml-llm-bridge[anthropic]` / `[openai]`); the SDK imports are lazy so importing the bridge package never requires either SDK be installed. 9 adapter tests with mocked clients cover request payload shape, response parsing, error paths, and `max_tokens` plumbing.
- `py.typed` marker added to `urml-validator` (and the new bridge package) so downstream consumers' type checkers see the inline type hints.

### Changed

- Nothing released yet.

### Deprecated

- Nothing released yet.

### Removed

- Nothing released yet.

### Fixed

- Nothing released yet.

### Security

- Nothing released yet.

---

*Released versions will be appended above this line as `[X.Y.Z] — YYYY-MM-DD` sections. The first release is targeted in Phase 1 (Manifesto roadmap, months 2–6).*
