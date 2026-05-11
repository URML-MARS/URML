# URML Examples

Runnable demonstrations of URML, organized per profile. Examples are how new readers learn what URML *looks like* — keep them small, honest, and runnable.

## Layout

```
examples/
├── home/                  v1.0 profile — only profile with content in v0.1.
│   ├── red-mug.urml.yaml      # The structured program.
│   └── red-mug.en.txt         # The English natural-language prompt.
├── drone/                 Reserved — populated when drone L2 vocab is drafted.
└── industrial/            Reserved — populated when industrial L2 vocab is drafted.
```

## Pairing convention

Each scenario is a pair (or small group) of files sharing a base name:

- **`<scenario>.urml.yaml`** — the URML program. YAML is canonical. One program per file.
- **`<scenario>.<lang>.txt`** — the natural-language prompt that yields the program. `<lang>` is an ISO 639-1 code: `en` for English, `he` for Hebrew, `es` for Spanish, `ja` for Japanese, `zh` for Mandarin.

The reserved languages from [`CLAUDE.md`](../CLAUDE.md) §Strategic Posture (Hebrew, Spanish, Japanese, Mandarin) get slots reserved by file naming. **V0.1 coverage is English-only;** other slots will fill in as multilingual fixtures land in later versions.

A scenario may also include:

- **`<scenario>.manifest.yaml`** — a capability manifest the program is validated against, when no shared profile manifest fits.
- **`<scenario>.expected.json`** — the expected validator output (for testing).

These are added per-scenario only when needed. The minimum example is one `*.urml.yaml` plus one `*.en.txt`.

## How examples are used

1. **In documentation.** The `red-mug` example is the canonical instance referenced from [`MANIFESTO.md`](../MANIFESTO.md) §A Concrete Example.
2. **By the LLM bridge as few-shot fixtures.** Each `(natural_language, urml_program)` pair becomes a few-shot exemplar.
3. **By the conformance suite as end-to-end tests.** A conformant runtime, given the manifest and the program, must execute the scenario to completion (or fail in the documented way for negative tests).
4. **By new readers.** Every example should be readable in under thirty seconds. If a reader needs context to understand a `*.urml.yaml`, the scenario is too complex — split it.

## Status of each profile

| Profile | v0.1 content | Trigger to fill in |
|---|---|---|
| [`home/`](home/) | `red-mug` (the manifesto example). | Already populated. Additional home scenarios land alongside the home-profile spec. |
| [`drone/`](drone/) | None yet. | Populated when the drone-profile Layer-2 vocabulary is drafted (Phase 2). |
| [`industrial/`](industrial/) | None yet. | Populated when the industrial-profile Layer-2 vocabulary is drafted (Phase 3). |

## Adding a new example

Examples are PR-able (not RFC-able) when they exercise *already-Accepted* spec primitives. Open a PR with:

1. The `*.urml.yaml` and at least an `*.en.txt`.
2. A short note in the PR explaining what the example demonstrates and why it's worth including.
3. A passing `urml validate` against an appropriate manifest.

Examples that *propose* new behavior must wait for the corresponding RFC; an example is not a substitute for a specification change.

## Style

- One scenario per file pair. Two-paragraph natural-language prompts are usually too much.
- No editorial commentary inside the YAML — comments are allowed, but should explain non-obvious *why*, not narrate.
- Examples should look like what an LLM would emit, not what a hand-tuned author would emit. They are realistic, not idealized.
