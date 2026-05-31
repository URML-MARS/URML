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

# CLAUDE.md

> Project context for AI-assisted development sessions (Claude Code, Claude chat, IDE integrations).
> Loaded automatically by Claude Code at the start of every session in this repository.
> See [`AGENTS.md`](AGENTS.md) for the operational handbook (writing style, chat style, tactical workflow rules).
> Last updated: 2026-05-23

---

## What this project is

URML (Universal Robot Language) is an open specification for describing robot intent. It is a small, opinionated, human-readable language that sits above existing robot operating systems (ROS 2, PX4, AUTOSAR Adaptive, OPC UA Robotics) and compiles down to whatever runtime lives below. The full vision is in [`MANIFESTO.md`](MANIFESTO.md). Read it before any non-trivial work.

The repository contains:

- The specification documents (Layers 1 through 4 plus domain profiles).
- Reference runtimes that translate URML programs into substrate-specific commands.
- A conformance test suite that determines whether a runtime is URML-compatible.
- An LLM bridge: prompt contracts, validators, and examples that let language models reliably emit valid URML.

Phase 1 is the current phase as of v0.1.0 (2026-05-22, PR #126). `pip install urml-validator` ships. External contributions are open per [`CONTRIBUTING.md`](CONTRIBUTING.md). The founder remains the sole maintainer. The phase flip opened the door, not the headcount. Conventions documented here are designed to scale from one person to a real engineering organization without rewrites.

## Strategic posture

The long-term goal is a **venture-scale company**. This is not incidental. It shapes technical decisions. Encode the following in any architectural choice.

**The standard is the moat.** The spec, reference runtimes, and conformance suite are Apache 2.0 forever. They are the loss-leader that builds adoption, and adoption is what makes the trademark and certification program valuable downstream. Resist any urge to keep "the good parts" closed. The good parts are precisely what attract the engineering community whose presence makes this company defensible.

**Commercial value lives in the surround, not in this repository.** Eventual revenue comes from: a paid certification and conformance program (the trademark *URML-Certified*), premium tooling on top of the open core (fleet management, hosted simulation, observability), managed cloud services (URML-as-a-service, hosted LLM bridges), training, and certification for individuals. These commercial surfaces are not part of this repository. Keep them mentally separate, but design so they remain *possible* later: clean APIs, well-defined extension points, no architectural choices that would make a hosted product harder to build.

**The Core Commitment, in writing.** What will always be Apache 2.0 and never move behind a paywall: the specification documents, the conformance test suite, the ROS 2 and PX4 reference runtimes, the validator, the prompt contract for LLM integration, and (per RFC-0003) the default US-federal compliance policy file. This commitment lives in [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md). It is non-negotiable. The open-core re-licensing controversies of the last decade (Elastic, MongoDB, HashiCorp, Redis) show what happens when the line is drawn after adoption rather than before.

**Identity: URML is a universal robot language.** Compliance is one feature, not the identity. The headline path is "one English sentence makes a robot move," reproducible by a developer. Demos and headline paths use `--no-policy` so the language is on stage with compliance one flag away. Do not bury the language under the NDAA gate. Compliance stays default-on for `urml validate`, but it is not the front-page story. Decided 2026-05-16 after an honest user-eye review found every "shipped" claim was a unit test or a gated CI job; the gap was operational glue, not architecture.

**Optimize for inevitability, not features.** A venture-scale outcome requires URML to become *the obvious choice* for natural-language robot control, not one of several. That means ruthless simplicity in the core vocabulary, exceptional documentation, demos that travel virally, and a deliberate community strategy. Every architectural decision should ask: does this make URML easier or harder to adopt at scale?

**Do not lock to one substrate.** ROS 2 is the first reference runtime because its community is largest. But a venture-scale outcome means URML works *everywhere*: PX4, AUTOSAR Adaptive, Autoware, OPC UA Robotics, vendor SDKs, future runtimes that do not exist yet. Architectural decisions that implicitly assume ROS 2 are bugs. The acid test for any primitive: can it be cleanly implemented on a runtime with zero ROS dependencies?

**Regulatory alignment is US-federal.** Default provenance and procurement rules embedded in the standard reflect United States statutory and executive frameworks: NDAA Section 889 / FY26, the FCC Covered List, Executive Order 14307, and the American Security Robotics Act once enacted. Documentation remains English-first, and the natural-language layer remains multilingual (examples in Hebrew, Spanish, Japanese, Mandarin from v0.1), because end users speak many languages even when the regulatory frame is one country's. Avoid choices that would *further* couple URML to a single US vendor, a single US agency, or a single US administration's policy interpretation; the alignment is to enacted law, not to politics. The strategic rationale and trade-offs are in [RFC-0003](docs/rfcs/0003-us-alignment.md).

**Structural separation is coming.** A venture-scale outcome typically ends with two entities: a non-profit foundation owning the standard (the moat) and a for-profit company selling adjacent products (the revenue). The realistic foundation target is US-domiciled and aligned with US federal law: a 501(c)(6) industry association, an SDO with strong US ties (IEEE-SA, INCITS), or a sponsored project under an existing US-domiciled foundation (Open Source Security Foundation, Cloud Native Computing Foundation). This separation does not need to exist on day one but should not be made structurally harder by today's decisions. Specifically: trademarks are filed in the founder's name initially and assignable, code is contributed under DCO sign-off (not CLA) so future re-organization is clean, and no commercial features are merged into this repository.

**Branding posture (Phase 0 into Phase 1).** URML is the face. MARS is acknowledged only as a small, reversible footer credit. The live site footer reads: "URML is an open specification under Apache 2.0. Stewarded by MARS during Phase 0." Never elevate MARS to a parent brand. Do not surface MARS as a product brand, do not add a MARS logo or header presence, do not write "A MARS product". The word "stewarded" and the "during Phase 0" time-bound are deliberate. They preserve the planned Phase 3+ structural split and keep it from reading as a bait-and-switch. `URML-MARS` as the GitHub org name is incidental plumbing, not a branding statement. This is a strategic meta-decision: refine within it, do not re-argue it.

**Traffic reality.** Phase 1 just opened. The repo's real audience is small (measured 2026-05-19: 4 human uniques, 0 stars, 0 watchers, 0 forks over 14 days). The thousand-plus clones reported in the GitHub traffic API are CI runners and crawlers, not interest. Do not tune the repo for phantom traffic. Do not derive engagement claims from clone counts. Optimize for the right reader (a roboticist who has never seen URML before), not for vanity numbers.

## Architecture: quick reference

URML is five layers. Code and specs are organized to mirror them.

```
Layer 4: Natural Language Interface     /spec/layer-4-nl-grammar     /reference/llm-bridge
Layer 3: Behavior Composition           /spec/layer-3-behavior       /reference/validator
Layer 2: Intent Primitives              /spec/layer-2-primitives     /reference/primitives
Layer 1: Hardware Abstraction           /spec/layer-1-hal
Layer 0: Substrate (not part of URML)   targeted, not defined: ROS 2, PX4, ...
Profiles                                /spec/profiles/{home, drone, industrial, ...}
```

A change that touches multiple layers is suspect. The layers are designed to evolve independently. If a feature requires coordinated changes across three layers, that is an RFC, not a PR.

## Repository structure

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
  /cobot-runtime, /industrial-arm-runtime, /humanoid-runtime, ...
/tools              CLI, linter, simulator hooks
/examples           Runnable demos per profile, plus the outreach ledgers
  /lighthouses      Move #1 and Move #2 outreach state
/conformance        Conformance test suite
/docs               Website source, tutorials, glossary
  /rfcs             Numbered RFC documents (Spec and Outreach kinds, see below)
/governance         Charter, decision log, working group docs (when they exist)
/.github            CI, issue templates, PR templates
MANIFESTO.md
CLAUDE.md           This file (project bible)
AGENTS.md           Operational handbook for AI assistants
README.md
LICENSE             Apache 2.0
CONTRIBUTING.md
GOVERNANCE.md
CORE_COMMITMENT.md
```

Not all directories exist yet. Create them as needed; do not create empty directories speculatively.

## Working conventions

### Documentation

- Markdown is canonical for everything human-readable. No reStructuredText, no AsciiDoc.
- Specs use semantic versioning. v0.x.y is pre-stable; breaking changes are allowed. v1.0.0 is the first stability commitment.
- All examples in spec documents must be runnable against the current reference runtime. A broken example is fixed or removed in the same commit, never left dangling.
- One thought per paragraph. Bullets only when the items are genuinely parallel and discrete.
- Writing style rules (no em-dashes, no hedging adverbs, no empty intensifiers, no LLM-tells) are in [`AGENTS.md`](AGENTS.md). They apply to every artifact a human will see, including this file.

### Code

- Languages, in order of preference: **Python** (specifications, validators, tooling, LLM bridge), **C++17** (ROS 2 nodes that need to be performant), **Rust** (long-running infrastructure: validator service, conformance harness). Avoid TypeScript / JavaScript in the core repo; web tooling lives in a separate repository when it is needed.
- Every public API is type-annotated. Python: full PEP 484, `mypy --strict`. C++: concepts where reasonable. Rust: the type system enforces this for free.
- Tests are not optional. New code lands with tests. Bug fixes land with a regression test that fails before the fix and passes after.
- No primitive enters Layer 2 without: a spec document section, a JSON Schema, a reference implementation in at least one runtime, conformance tests, and a runnable example. This is the bar.

### Commits and PRs

- DCO sign-off on every commit (`git commit -s`). No exceptions. This is the venture-scale safeguard: it keeps future re-organization (foundation creation, entity splits, acquisitions) legally clean.
- Commit messages: imperative subject under 72 chars, blank line, body explaining *why* not *what*. Reference RFC numbers and issue numbers where relevant.
- PRs include: what changed, why, how it was tested, what the rollback plan is if it lands wrong.
- **Merge commit to `main`, never squash.** Preserve all commits so the per-PR decision trail and RFC history stay on `main`. The repo allows both merge and squash, but the founder's standing preference is merge commit.
- Solo-maintainer branch protection requires `--admin` bypass to land a PR (the sole maintainer cannot approve their own review). The founder runs the final merge command. AI assistants prepare the PR, hand the commands over, and wait. See [`AGENTS.md`](AGENTS.md) for the operational details (which `gh` flags, how to verify a merge landed on `origin/main`, the Bash-tool quirk on Windows).

### RFCs

- Any change to the specification (adding a primitive, changing a schema, modifying behavior semantics) is an RFC, not a PR.
- RFCs live in `/docs/rfcs/NNNN-short-name.md`, numbered sequentially.
- Each RFC contains: problem statement, proposal, alternatives considered, prior art, implementation plan, open questions.
- During Phase 0 the founder authored, reviewed, and merged their own RFCs against a documented self-review checklist. The discipline survives into Phase 1: future contributors inherit a real decision history rather than a folkloric one.

**Two kinds of RFC live in `docs/rfcs/`.** A `Kind` column in [`docs/rfcs/README.md`](docs/rfcs/README.md) distinguishes them:

- **Spec RFCs** (currently 0001 through 0022, plus 0039): changes to URML's normative surface (Layer-1 through Layer-4 schemas, new primitives, the policy mechanism, profiles, the Core Commitment).
- **Outreach RFCs** (currently 0023 through 0038, plus 0040 onward): per-target request-for-comment documents. Each one explicitly states "No spec change is proposed here" and proposes a mapping from URML v0.1 to an existing target's adapter, manifest, or API. They live in the RFC directory for ergonomic discoverability and are tracked operationally in the ledgers under [`examples/lighthouses/`](examples/lighthouses/).

Outreach RFCs are not a quiet expansion of URML's spec surface. A reader scanning the index can tell them apart at a glance.

### Outreach ledgers and the listening side

Two ledger files under [`examples/lighthouses/`](examples/lighthouses/):

- `outreach.yaml` (Move #1, RFCs 0023 through 0038): the 16 Tier-1 robot OEMs and component vendors. Parity-locked to `examples/lighthouses/demo.py::LIGHTHOUSES` by `conformance/tests/test_outreach_ledger.py`. Do not add a row without updating both, or the test fails.
- `outreach-move2.yaml` (Move #2 onward, RFC 0040+): the AI / ML layer and substrate follow-ons. Mirroring schema, no parity test (different audience, not every target has an in-repo manifest).

Response enum: `none | acked | engaged | declined | wontfix`. Default state for fresh outreach is `none` with `last_touch == sent_at`. Do not massage state to look more engaged than reality. When state changes, edit the ledger first; everything else (the demo runner, the outreach dashboard, the claims-audit) reads from it.

The outreach dashboard (RFC-0275) reads a SQLite mirror at `tools/outreach.db`, not the YAML directly. The mirror is a derived view: regenerated on demand by `python tools/scripts/refresh_outreach_db.py`, deterministic, and never committed. Do not hand-edit the `.db`, and keep it out of git. YAML stays the single source of truth. **Always refresh the mirror after any ledger change** (a post, a response, a deferral) so the dashboard reflects reality. The rebuild deletes and rewrites the file, so it fails while a dashboard process holds it open; stop the dashboard first, then refresh.

### Public commitments are deferred until measured

Do not publish SLA matrices, formal response-time promises, or support guarantees on the URML project until: (a) the repo is fully public, AND (b) at least 1 to 2 months of measured response-time data shows the numbers are hittable. Build the private measurement first, calibrate against reality, then publish numbers anchored in data. Publishing a promise you might miss is worse than not publishing one.

Visible behavior beats written commitments in Phase 0 and early Phase 1: RFC cadence, commit visibility, monthly metrics notes once public, fast first-issue responses. The formal SLA matrix gets reintroduced at the public-launch RFC, with numbers grounded in measured response times.

### Audit discipline

`make audit` (= `python tools/scripts/refresh_audit.py`) is a read-only re-measurer. It runs every package's pytest, counts conformance fixtures from disk, and prints a paste-ready markdown block plus a diff against the current audit table. **It does not auto-edit any file.** The maintainer reads, sanity-checks, and transcribes to `docs/launch/claims-audit.md` and the README front-page cell in lockstep.

Report drift, do not silently rewrite. Mark unmeasurable rows (missing optional extras on the host) as `n/a` and carry forward the prior number with an explicit caveat. Never fabricate 0.

### README hero and demo discipline

The README hero SVG (`docs/assets/sentence-to-motion.svg`) is generated by `tools/scripts/gen_demo_svg.py`. Pure Python stdlib, deterministic, any-OS including Windows. Not asciinema, not vhs, not termtosvg, not ffmpeg, not Node. If asked to "use a real recorder," push back: pure Python is the on-ethos choice and matches the MockROSAdapter and bootstrap hermetic posture (zero external runtime dependency).

`reference/validator/tests/test_demo_svg.py` is the guard. It asserts that the committed SVG equals the generator output (stale asset means red CI) and that every line the hero shows is emitted verbatim by a live hermetic `translate -> validate -> execute` run. The hero cannot drift from or lie about the tool. If you change the demo output, regenerate (`make demo-record`) or CI fails.

## What Claude should do by default

- Read [`MANIFESTO.md`](MANIFESTO.md) and the relevant Layer specification before making non-trivial changes. The manifesto is the constitution; the layer specs are the laws.
- Prefer fewer primitives over more. Adding a primitive is a one-way door; removing one breaks every downstream user. If a behavior can be composed from existing primitives, it should be.
- When extending an existing primitive vs. adding a new one is unclear, ask the founder. Do not silently choose.
- Treat the Core Commitment as architectural. Never propose moving anything listed there behind a paywall, a conditional license, or an "enterprise edition". If a contribution conflicts with the Commitment, refuse the change and explain why.
- Test *spec-level* behavior, not implementation details. A good conformance test passes on any URML-compatible runtime, not just this one.
- When writing prose for users (READMEs, error messages, docs), write for a smart non-expert. The audience is the roboticist who has never seen URML before, not the URML core team.
- Default to opinionated decisions documented in writing, rather than configurable options. Every configuration knob is technical debt and a tax on adoption.

## What Claude should never do

- Implement, accept contributions for, or document profiles or primitives outside the URML organization's canonical scope (civilian, consumer, educational, industrial, research). The Apache 2.0 license permits external parties to build other extensions on top of URML; this repository does not host them.
- Bypass the validator at runtime. URML programs are executed *only* after static verification against the target's capability manifest and active safety envelope. Any "fast path" that skips verification is rejected on review. This is a safety boundary and a liability boundary; do not weaken it.
- Introduce dependencies on cloud services in the reference runtimes. URML programs must execute fully offline once validated. Hosted services are a separate, commercial concern that lives outside this repository.
- Embed a specific LLM provider. The LLM bridge is provider-agnostic: Anthropic, OpenAI, open-weights models, on-device models must all be first-class. Vendor lock-in here would forfeit the standard's neutrality and kill the venture story.
- Couple a primitive to a specific substrate. If a primitive's specification is unimplementable on a substrate that does not use ROS, it is a leaky primitive and needs rework.
- Accept or write code that gathers user data, telemetry, or identifiers without an explicit, opt-in, documented purpose. Trust is the most valuable asset this project has and the easiest to lose.
- Suggest a CLA (Contributor License Agreement) over a DCO. CLAs concentrate copyright in one party and are read by the open-source community as a signal of intent to re-license later. DCO is the venture-scale-friendly choice precisely because it preserves trust.
- Embed a specific US administration's executive-order interpretation in default rules. Track enacted statutes, final FCC Covered List entries, and final DoD rules. Not draft guidance, not pending bills, not interpretive memos that can be withdrawn by a successor. The default policy file's stability depends on this discipline.

## Communication style

The founder prefers direct, opinionated engagement. The detailed rules (terse prompts, full delegation, when to use AskUserQuestion, the protected-action exception) are in [`AGENTS.md`](AGENTS.md). The short version:

- Disagreement is welcome and expected. If a design seems wrong, say so with reasons.
- Honesty over reassurance. Bad news early is better than bad news late.
- Pragmatism over purity. "This is what most projects do" is rarely a good reason; "this is what works for our specific situation, for these reasons" is.
- Concision in chat, thoroughness in written artifacts (specs, docs, RFCs).
- No corporate hedging. If you are 80% confident, say "I think" and proceed; do not bury the answer under qualifications.

## Reference documents

- [`MANIFESTO.md`](MANIFESTO.md): project vision, scope, principles, roadmap. The constitution.
- [`AGENTS.md`](AGENTS.md): operational handbook for AI assistants (writing style, chat style, outreach verification, ledger discipline, merge specifics, audit and hero discipline).
- [`VIBE.md`](VIBE.md): authoring posture. URML is the invention of Ido Yahalomi; the prose is AI-assisted (vibe-coded), under the maintainer's direction and review. Not hidden, not transitional.
- [`GOVERNANCE.md`](GOVERNANCE.md): how decisions are made.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): how to contribute (Phase 1, open).
- [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md): what will always be Apache 2.0 and never move.
- [`docs/rfcs/`](docs/rfcs/): numbered RFC documents, the decision history.
- [`examples/lighthouses/`](examples/lighthouses/): outreach ledgers (Move #1 and Move #2).
- [`LICENSE`](LICENSE): Apache License 2.0.

**Precedence order**, when in doubt about a decision in this repository:

1. Manifesto.
2. Core Commitment.
3. Layer specifications.
4. Accepted RFCs.
5. This file (`CLAUDE.md`).
6. `AGENTS.md`.
7. The founder's stated preference in chat.
8. Claude's judgment.

If a Claude memory file disagrees with a checked-in document, the checked-in document wins.

---

*This file is checked into version control and updated as conventions evolve. Substantive changes to it require an RFC.*
