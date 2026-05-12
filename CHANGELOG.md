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
