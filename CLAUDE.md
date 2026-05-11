# CLAUDE.md

> Project context for AI-assisted development sessions (Claude Code, Claude chat, IDE integrations).  
> Loaded automatically by Claude Code at the start of every session in this repository.  
> Last updated: [fill in]

---

## What This Project Is

URML (Universal Robot Language) is an open specification for describing robot intent — a small, opinionated, human-readable language that sits above existing robot operating systems (ROS 2, PX4, AUTOSAR, OPC UA Robotics) and compiles down to whatever runtime lives below. The full vision is in `MANIFESTO.md`. Read it before any non-trivial work.

The repository contains:

- The specification documents (Layers 1–4 plus domain profiles)
- Reference runtimes that translate URML programs into substrate-specific commands
- A conformance test suite that determines whether a runtime is URML-compatible
- An LLM bridge: prompt contracts, validators, and examples that let language models reliably emit valid URML

Phase 0 is the current phase. The founder is the sole contributor. Conventions documented here are designed to scale from one person to a real engineering organization without rewrites.

## Strategic Posture

The long-term goal is a **venture-scale company**. This is not incidental — it shapes technical decisions. Encode the following in any architectural choice:

**The standard is the moat.** The spec, reference runtimes, and conformance suite are Apache 2.0 forever. They are the loss-leader that builds adoption, and adoption is what makes the trademark and certification program valuable downstream. Resist any urge to keep "the good parts" closed — the good parts are precisely what attract the engineering community whose presence makes this company defensible.

**Commercial value lives in the surround, not in this repository.** Eventual revenue comes from: a paid certification/conformance program (the trademark *URML-Certified*), premium tooling on top of the open core (fleet management, hosted simulation, observability), managed cloud services (URML-as-a-service, hosted LLM bridges), training, and certification for individuals. These commercial surfaces are not part of this repository. Keep them mentally separate, but design so they remain *possible* later: clean APIs, well-defined extension points, no architectural choices that would make a hosted product harder to build.

**The Core Commitment, in writing.** What will always be Apache 2.0 and never move behind a paywall: the specification documents, the conformance test suite, the ROS 2 and PX4 reference runtimes, the validator, and the prompt contract for LLM integration. This commitment lives in `CORE_COMMITMENT.md` (to be created before any commercial entity is incorporated). It is non-negotiable. The open-core re-licensing controversies of the last decade (Elastic, MongoDB, HashiCorp, Redis) show what happens when the line is drawn after adoption rather than before.

**Optimize for inevitability, not features.** A venture-scale outcome requires URML to become *the obvious choice* for natural-language robot control, not one of several. That means ruthless simplicity in the core vocabulary, exceptional documentation, demos that travel virally, and a deliberate community strategy. Every architectural decision should ask: does this make URML easier or harder to adopt at scale?

**Don't lock to one substrate.** ROS 2 is the first reference runtime because its community is largest. But a venture-scale outcome means URML works *everywhere* — PX4, AUTOSAR Adaptive, Autoware, OPC UA Robotics, vendor SDKs, future runtimes that don't exist yet. Architectural decisions that implicitly assume ROS 2 are bugs. The acid test for any primitive: can it be cleanly implemented on a runtime with zero ROS dependencies?

**Geographic neutrality matters.** The author is in Israel; the target market is global. Avoid choices that would make the project read as a national project. Documentation is English-first; examples deliberately include diverse languages (Hebrew, Spanish, Japanese, Mandarin) from v0.1; license and governance follow international open-source conventions; the eventual foundation is intended to be jurisdictionally neutral.

**Structural separation is coming.** A venture-scale outcome typically ends with two entities: a non-profit foundation owning the standard (the moat) and a for-profit company selling adjacent products (the revenue). This separation does not need to exist on day one but should not be made structurally harder by today's decisions. Specifically: trademarks are filed in the founder's name initially and assignable; code is contributed under DCO sign-off (not CLA) so future re-organization is clean; no commercial features are merged into this repository.

## Architecture: Quick Reference

URML is five layers. Code and specs are organized to mirror them.

```
Layer 4 — Natural Language Interface     /spec/layer-4-nl    /reference/llm-bridge
Layer 3 — Behavior Composition           /spec/layer-3       /reference/validator
Layer 2 — Intent Primitives              /spec/layer-2       /reference/primitives
Layer 1 — Hardware Abstraction           /spec/layer-1
Layer 0 — Substrate (not part of URML)   targeted, not defined: ROS 2, PX4, ...
Profiles                                 /spec/profiles/{home, drone, industrial, ...}
```

A change that touches multiple layers is suspect — the layers are designed to evolve independently. If a feature requires coordinated changes across three layers, that is an RFC, not a PR.

## Repository Structure

```
/spec               Versioned specification documents (semver per spec)
  /layer-1-hal
  /layer-2-primitives
  /layer-3-behavior
  /layer-4-nl-grammar
  /profiles
/reference          Reference implementations
  /ros2-runtime
  /px4-runtime
  /validator
  /llm-bridge
/tools              CLI, linter, simulator hooks
/examples           Runnable demos per profile
/conformance        Conformance test suite
/docs               Website source, tutorials, glossary
  /rfcs             Numbered RFC documents
/governance         Charter, decision log, working group docs (when they exist)
/.github            CI, issue templates, PR templates
MANIFESTO.md
CLAUDE.md           This file
README.md
LICENSE             Apache 2.0
CONTRIBUTING.md
GOVERNANCE.md
CORE_COMMITMENT.md  (to be created before commercial work begins)
```

Not all directories exist yet. Create them as needed; do not create empty directories speculatively.

## Working Conventions

### Documentation

- Markdown is canonical for everything human-readable. No reStructuredText, no AsciiDoc.
- Specs use semantic versioning. v0.x.y is pre-stable; breaking changes are allowed. v1.0.0 is the first stability commitment.
- All examples in spec documents must be runnable against the current reference runtime. A broken example is fixed or removed in the same commit — never left dangling.
- One thought per paragraph. Bullets only when the items are genuinely parallel and discrete.

### Code

- Languages, in order of preference: **Python** (specifications, validators, tooling, LLM bridge), **C++17** (ROS 2 nodes that need to be performant), **Rust** (long-running infrastructure: validator service, conformance harness). Avoid TypeScript/JavaScript in the core repo; web tooling lives in a separate repository when it is needed.
- Every public API is type-annotated. Python: full PEP 484, `mypy --strict`. C++: concepts where reasonable. Rust: the type system enforces this for free.
- Tests are not optional. New code lands with tests. Bug fixes land with a regression test that fails before the fix and passes after.
- No primitive enters Layer 2 without: a spec document section, a JSON Schema, a reference implementation in at least one runtime, conformance tests, and a runnable example. This is the bar.

### Commits and PRs

- **DCO sign-off** on every commit (`git commit -s`). No exceptions. This is the venture-scale safeguard: it keeps future re-organization (foundation creation, entity splits, acquisitions) legally clean.
- Commit messages: imperative subject under 72 chars, blank line, body explaining *why* not *what*. Reference RFC numbers and issue numbers where relevant.
- PRs include: what changed, why, how it was tested, what the rollback plan is if it lands wrong.
- Squash-merge to `main`. The PR description becomes the commit message.

### RFCs

- Any change to the specification — adding a primitive, changing a schema, modifying behavior semantics — is an RFC, not a PR.
- RFCs live in `/docs/rfcs/NNNN-short-name.md`, numbered sequentially.
- Each RFC contains: problem statement, proposal, alternatives considered, prior art, implementation plan, open questions.
- During Phase 0 (solo), RFCs are still written and merged. The author reviews their own work against a documented self-review checklist. Future contributors will inherit a real decision history rather than a folkloric one.

## What Claude Should Do By Default

- Read `MANIFESTO.md` and the relevant Layer specification before making non-trivial changes. The manifesto is the constitution; the layer specs are the laws.
- Prefer fewer primitives over more. Adding a primitive is a one-way door; removing one breaks every downstream user. If a behavior can be composed from existing primitives, it should be.
- When extending an existing primitive vs. adding a new one is unclear, ask the founder. Do not silently choose.
- Treat the Core Commitment as architectural. Never propose moving anything listed there behind a paywall, conditional license, or "enterprise edition." If a contribution conflicts with the Commitment, refuse the change and explain why.
- Test *spec-level* behavior, not implementation details. A good conformance test passes on any URML-compatible runtime, not just this one.
- When writing prose for users (READMEs, error messages, docs), write for a smart non-expert. The audience is the roboticist who has never seen URML before, not the URML core team.
- Default to opinionated decisions documented in writing, rather than configurable options. Every configuration knob is technical debt and a tax on adoption.

## What Claude Should Never Do

- Implement, accept contributions for, or document profiles or primitives outside the URML organization's canonical scope (civilian, consumer, educational, industrial, research). The Apache 2.0 license permits external parties to build other extensions on top of URML; this repository does not host them.
- Bypass the validator at runtime. URML programs are executed *only* after static verification against the target's capability manifest and active safety envelope. Any "fast path" that skips verification is rejected on review. This is a safety boundary and a liability boundary; do not weaken it.
- Introduce dependencies on cloud services in the reference runtimes. URML programs must execute fully offline once validated. Hosted services are a separate, commercial concern that lives outside this repository.
- Embed a specific LLM provider. The LLM bridge is provider-agnostic — Anthropic, OpenAI, open-weights models, on-device models must all be first-class. Vendor lock-in here would forfeit the standard's neutrality and kill the venture story.
- Couple a primitive to a specific substrate. If a primitive's specification is unimplementable on a substrate that doesn't use ROS, it is a leaky primitive and needs rework.
- Accept or write code that gathers user data, telemetry, or identifiers without an explicit, opt-in, documented purpose. Trust is the most valuable asset this project has and the easiest to lose.
- Suggest a CLA (Contributor License Agreement) over a DCO. CLAs concentrate copyright in one party and are read by the open-source community as a signal of intent to re-license later. DCO is the venture-scale-friendly choice precisely because it preserves trust.

## Communication Style

The founder prefers direct, opinionated engagement. Specifically:

- Disagreement is welcome and expected. If a design seems wrong, say so with reasons.
- Honesty over reassurance. Bad news early is better than bad news late.
- Pragmatism over purity. "This is what most projects do" is rarely a good reason; "this is what works for our specific situation, for these reasons" is.
- Concision in chat; thoroughness in written artifacts (specs, docs, RFCs).
- No corporate-AI hedging. If you are 80% confident, say "I think" and proceed; do not bury the answer under qualifications.

## Reference Documents

- `MANIFESTO.md` — Project vision, scope, principles, roadmap. The constitution.
- `GOVERNANCE.md` — How decisions are made (to be created).
- `CONTRIBUTING.md` — How to contribute (to be created when external contributions open in Phase 1).
- `CORE_COMMITMENT.md` — What will always be Apache 2.0 and never move (to be created before any commercial work begins).
- `/docs/rfcs/` — Numbered RFC documents; the decision history.
- `LICENSE` — Apache License 2.0.

**Precedence order**, when in doubt about a decision in this repository:

1. Manifesto
2. Core Commitment
3. Layer specifications
4. Accepted RFCs
5. This file (`CLAUDE.md`)
6. The founder's stated preference in chat
7. Claude's judgment

---

*This file is checked into version control and updated as conventions evolve. Substantive changes to it require an RFC.*
