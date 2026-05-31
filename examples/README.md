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

# URML Examples

Runnable demonstrations of URML, organized per profile. Examples are how new readers learn what URML *looks like* — keep them small, honest, and runnable.

New here? Start with [`WALKTHROUGH.md`](WALKTHROUGH.md): the full path from a natural-language sentence to a verified robot action, reproducible on any machine in under a minute, no robot or install beyond the open packages.

## Layout

```
examples/
├── home/                       v1.0 profile.
│   ├── red-mug.*                   # The manifesto example (move/detect/grasp/release).
│   ├── evening-routine.*           # Conversational routine (speak/listen/wait_for/dock/wait).
│   └── patient-fetch.*             # Layer-3: retry + branch + variables.
├── educational/                educational-profile programs (RFC-0011; classroom buggy, zero ROS).
│   ├── hello-square.*               # The "hello world" of motion: drive four corners and home.
│   ├── classroom-patrol.*           # start → checkpoint → base (teachable twin of the conformance patrol).
│   └── fetch-the-block.*            # gentle grasp + fail-closed detect (the profile's safety rules).
├── drone/                      drone-profile programs (v0.1).
│   ├── roof-inspection.*           # Citizen-inspector roof scan (take_off/capture/RTH/land).
│   ├── bridge-survey.*             # Structure survey (scan/hover/measure).
│   ├── parallel-watch.*            # Layer-3: parallel (first_to_succeed) + wait_for.
│   └── link-aware-patrol.*         # Layer-1: connectivity block + link-loss envelope.
├── industrial/                 industrial-profile programs (v0.1).
│   └── simple-pick-and-place.*     # MVP pick-place cycle.
├── legged/                     legged programs (home profile; RFC-0009 quadruped).
│   └── spot-patrol.*               # MVP nav-only quadruped patrol.
├── humanoid/                   humanoid programs (home profile; RFC-0009 biped, locomotion subset).
│   └── digit-patrol.*              # MVP nav-only biped patrol.
├── mobile/                     wheeled-AMR programs (home profile).
│   └── husky-patrol.*              # MVP nav-only AMR patrol.
└── marine/                     underwater programs (home profile; MAVLink, zero ROS).
    └── reef-survey.*               # MVP nav-only underwater survey.
```

## Pairing convention

Each scenario is a pair (or small group) of files sharing a base name:

- **`<scenario>.urml.yaml`** — the URML program. YAML is canonical. One program per file.
- **`<scenario>.<lang>.txt`** — the natural-language prompt that yields the program. `<lang>` is an ISO 639-1 code: `en` for English, `he` for Hebrew, `es` for Spanish, `ja` for Japanese, `zh` for Mandarin.

The reserved languages from [`CLAUDE.md`](../CLAUDE.md) §Strategic Posture (Hebrew, Spanish, Japanese, Mandarin) get slots reserved by file naming. The canonical `home/red-mug` example leads: it ships all five (`en`, `es`, `ja`, `zh`, `he`). Other scenarios remain English-only for now and fill their slots as multilingual fixtures land.

A scenario may also include:

- **`<scenario>.manifest.yaml`** — a capability manifest the program is validated against, when no shared profile manifest fits.
- **`<scenario>.envelope.yaml`** — a deployment safety envelope, when the scenario exercises an envelope constraint the profile default does not (e.g. an RFC-0006 link-loss policy). Pass it with `--envelope`.
- **`<scenario>.expected.json`** — the expected validator output (for testing).

These are added per-scenario only when needed. The minimum example is one `*.urml.yaml` plus one `*.en.txt`.

## How examples are used

1. **In documentation.** The `red-mug` example is the canonical instance referenced from [`MANIFESTO.md`](../MANIFESTO.md) §A Concrete Example.
2. **By the LLM bridge as few-shot fixtures.** Each `(natural_language, urml_program)` pair becomes a few-shot exemplar.
3. **By the conformance suite as end-to-end tests.** A conformant runtime, given the manifest and the program, must execute the scenario to completion (or fail in the documented way for negative tests).
4. **By new readers.** Every example should be readable in under thirty seconds. If a reader needs context to understand a `*.urml.yaml`, the scenario is too complex — split it.

## Status of each profile

| Profile | v0.1 content | How it grows |
|---|---|---|
| [`home/`](home/) | `red-mug` (the manifesto example); `evening-routine` (speech + dock); `patient-fetch` (retry/branch). | Additional home scenarios land alongside the home-profile spec. |
| [`educational/`](educational/) | `hello-square` (nav-only "hello world"); `classroom-patrol` (start/checkpoint/base); `fetch-the-block` (gentle grasp + fail-closed detect). See [Tutorial 5](../docs/tutorials/05-teaching-urml.md). | Additional classroom scenarios land alongside the educational profile (RFC-0011). |
| [`drone/`](drone/) | `roof-inspection` (citizen-inspector); `bridge-survey` (scan/hover/measure); `parallel-watch` (parallel); `link-aware-patrol` (connectivity + link-loss). | Additional drone scenarios land alongside the drone-profile spec. |
| [`industrial/`](industrial/) | `simple-pick-and-place` (MVP integrator example). | Additional industrial scenarios land alongside the industrial-profile spec. |
| [`legged/`](legged/) | `spot-patrol` (nav-only quadruped patrol; RFC-0009). | Additional legged scenarios land alongside the legged runtime. |
| [`humanoid/`](humanoid/) | `digit-patrol` (nav-only biped patrol; RFC-0009 locomotion subset). | Manipulation scenarios land with the RFC-0010 whole-body work. |
| [`mobile/`](mobile/) | `husky-patrol` (nav-only AMR patrol, compliant declared parts). | Additional mobile scenarios land alongside the mobile runtime. |
| [`marine/`](marine/) | `reef-survey` (nav-only underwater survey; MAVLink, zero ROS). | Additional marine scenarios land alongside the marine runtime. |

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
