# Contributing to URML

Thank you for your interest in URML. This document describes how to engage during Phase 0 and how to contribute from Phase 1 on.

> **Phase 0 status (current).** URML is a solo project working in public. The artifact under review is the manifesto itself. The author welcomes critique, prior-art pointers, and use-case descriptions; **direct code contributions open in Phase 1.** This document is in force now so the contribution process is understood before contributions arrive.

---

## Ways to Engage Today (Phase 0)

The author welcomes:

- **Critique of [`MANIFESTO.md`](MANIFESTO.md)** — especially of the layer boundaries, the substrate-neutrality acid test, and the (not-yet-drafted) primitive vocabulary.
- **Pointers to prior art** that should be acknowledged or built upon — behavior trees, PDDL, AUTOSAR Adaptive, Skiros, BehaviorTree.CPP, OpenRAVE intent layers, and others.
- **Use cases that strain the current architecture** — scenarios the manifesto's three motivating examples (home, drone, industrial) do not cover.
- **Naming suggestions** if "URML" proves unsuitable. See `MANIFESTO.md` Appendix B, Question 1.

URML uses [GitHub Discussions](https://github.com/URML-MARS/URML/discussions), open now in Phase 0 ([RFC-0008](docs/rfcs/0008-community-discussions.md)). Where things go:

- **Questions** (writing a manifest, running the validator, integrating a runtime): Discussions [Q&A](https://github.com/URML-MARS/URML/discussions/categories/q-a).
- **Ideas** for a primitive, profile, or tooling: Discussions [Ideas](https://github.com/URML-MARS/URML/discussions/categories/ideas). One that holds up graduates to the [primitive proposal issue](.github/ISSUE_TEMPLATE/primitive_proposal.md) and then an RFC.
- **Complaints, feedback, posture critique**: Discussions [General](https://github.com/URML-MARS/URML/discussions/categories/general).
- **Runtime author or manufacturer topics**: Discussions [Builders & Makers](https://github.com/URML-MARS/URML/discussions/categories/builders-makers).
- **Reproducible reference-runtime bugs**: an [issue](.github/ISSUE_TEMPLATE/bug_report.md).
- **Security or conduct concerns**: the private process in [`SECURITY.md`](SECURITY.md), never a public thread.

A contributor mailing list will be set up when the project moves under its permanent GitHub organization.

## What Changes Today

When Phase 1 opens, this section is updated. Three things happen at that boundary:

1. The repository moves under a permanent GitHub organization.
2. CI is wired up: DCO enforcement, linting, conformance test execution.
3. This document is updated to describe pull-request mechanics, review SLAs, and merge authority.

## Developer Certificate of Origin (DCO)

URML uses **DCO sign-off**, not a Contributor License Agreement. The strategic reasoning is in [`CLAUDE.md`](CLAUDE.md) §What Claude Should Never Do (final bullet). The short version: a CLA concentrates copyright in one party and reads as a signal that re-licensing may be coming. DCO does neither.

The full DCO text is in [`DCO`](DCO).

**To sign off a commit, add `-s` to `git commit`:**

```bash
git commit -s -m "Subject line under 72 chars"
```

This appends a `Signed-off-by: Your Name <your@email>` line to the commit message. By doing so, you assert that you have the right to submit the work under the project's license, per the DCO.

DCO enforcement is wired into CI from Phase 1. Commits without sign-off are rejected; squashing or amending to add `-s` is the normal fix.

## Specification Changes Are RFCs

The single most important rule:

> Any change to the **specification** — adding a primitive, changing a schema, modifying behavior semantics, changing a profile, modifying the Core Commitment — is an **RFC**, not a pull request.

RFCs live in [`docs/rfcs/`](docs/rfcs/). The process is documented in [`docs/rfcs/0001-rfc-process.md`](docs/rfcs/0001-rfc-process.md). The template is [`docs/rfcs/0000-template.md`](docs/rfcs/0000-template.md). The index of all RFCs is in [`docs/rfcs/README.md`](docs/rfcs/README.md).

Pull requests handle *implementation* of accepted RFCs and routine maintenance — tests, documentation fixes, dependency bumps, refactoring without behavior change. If you cannot tell whether your change needs an RFC, file an issue and ask.

## Proposing a Layer 2 Primitive

A new primitive is a one-way door — once shipped, removing it breaks every downstream user. URML's bar is correspondingly high:

A new primitive enters Layer 2 only with **all** of the following:

1. A specification document section in the relevant [`spec/layer-2-primitives/`](spec/layer-2-primitives/) document.
2. A JSON Schema in the spec source.
3. A reference implementation in **at least one** runtime.
4. Conformance tests.
5. A runnable example.

Before doing that work, file the [primitive proposal issue](.github/ISSUE_TEMPLATE/primitive_proposal.md) so it can be evaluated against the existing vocabulary and the substrate-neutrality acid test (per [`CLAUDE.md`](CLAUDE.md): can it be cleanly implemented on a runtime with zero ROS dependencies?). If a behavior can be composed from existing primitives, it should be.

### Core vs. profile-specific primitives

The bar above is for the **core twelve** ([RFC-0002](docs/rfcs/0002-initial-primitive-vocabulary.md)) — primitives meaningful across multiple profiles. **Profile-specific primitives** (`speak`/`listen` in the home profile; `take_off`/`land`/`return_to_home` in the drone profile) follow the same five-point bar with one substitution: the specification document lives in the **profile's** spec directory ([`spec/profiles/<name>/`](spec/profiles/)), not in the core primitive doc.

Authorizing a profile-specific primitive does not require a dedicated RFC if the profile spec is already in **Draft** state and the primitive is named in that spec; the spec itself is the authorization. Primitives outside that scope (e.g., a new home-profile primitive a future contributor wants to add) require an RFC that amends the relevant profile spec first.

## Proposing a Profile

A new profile is a smaller commitment than a core primitive but still a commitment. The current profile set (home / drone / industrial) plus the stretch list (agricultural, AV, healthcare, SAR, education, underwater) in [`MANIFESTO.md`](MANIFESTO.md) §Scope is the canonical maintenance scope. The Apache 2.0 license permits external parties to build any profile on top of URML; the canonical URML organization maintains only the scoped set.

To propose a new canonical profile:

1. File a [feature request](.github/ISSUE_TEMPLATE/feature_request.md) describing the domain, the v1.0 use cases, and the safety-envelope class. The maintainer routes it.
2. If routed forward, file an RFC under [`docs/rfcs/`](docs/rfcs/) that defines the profile's added primitives, constrained core primitives, manifest fields, default safety envelope, and compliance-policy alignment.
3. On Accepted, draft the profile spec document under `spec/profiles/<name>/`, write reference examples under `examples/<name>/`, and write conformance fixtures under `conformance/fixtures/<name>/`. The profile reaches **Implemented** only when all four exist and the reference runtime supports the profile's added primitives.

See [`spec/profiles/home/`](spec/profiles/home/) and [`spec/profiles/drone/`](spec/profiles/drone/) for v0.1 Draft profiles as templates.

## Code Conventions

From [`CLAUDE.md`](CLAUDE.md) §Working Conventions:

- **Languages, in order of preference:** Python (specifications, validators, tooling, LLM bridge), C++17 (ROS 2 nodes that need to be performant), Rust (long-running infrastructure: validator service, conformance harness). TypeScript/JavaScript is avoided in the core repo; web tooling lives in a separate repository.
- **Public APIs are fully type-annotated.** Python: full PEP 484, `mypy --strict`. C++: concepts where reasonable.
- **Tests are not optional.** New code lands with tests. Bug fixes land with a regression test that fails before the fix and passes after.

## Documentation Conventions

- Markdown is canonical for everything human-readable. No reStructuredText, no AsciiDoc.
- All examples in spec documents must be runnable against the current reference runtime. A broken example is fixed or removed in the same commit — never left dangling.
- One thought per paragraph. Bullets only when the items are genuinely parallel and discrete.

## Listing a Runtime in the Compatible Runtimes Registry

Runtime authors (third parties or the URML organization itself) who want their runtime listed in [`docs/compatible-runtimes.md`](docs/compatible-runtimes.md) follow a separate flow from code or spec contributions. The flow is documented in [`docs/registry/SUBMISSION.md`](docs/registry/SUBMISSION.md). At a glance: run the conformance suite against your runtime, commit the report at a pinned commit in your repo, open a PR adding a row.

How to run it against your own runtime, including the bring-your-own-adapter one-liner (`python -m urml_conformance --adapter your_pkg:YourAdapter`), is documented in [`conformance/CONFORMANCE_KIT.md`](conformance/CONFORMANCE_KIT.md). You implement one substrate-neutral Protocol; no reference runtime, robot, or ROS is required.

The registry is self-reported. The maintainer reviews PRs for completeness, not for code or fitness. The URML-Certified mark, the future paid certification program, is reserved for Phase 4 and is not part of the registry. See [`TRADEMARK.md`](TRADEMARK.md) for the boundary.

Registry submissions use a dedicated PR template (`?template=registry-submission.md`) so the row data and the trademark-acknowledgement checkbox land in one place.

## Code of Conduct

This project follows the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md). All contributors and engagement participants — including during Phase 0 — are expected to follow it.

## Security

If you find a safety issue in the specification (a primitive that admits unsafe interpretations), file an RFC. If you find an implementation vulnerability in a reference runtime, follow the disclosure process in [`SECURITY.md`](SECURITY.md).

## Questions

If anything in this document is unclear, ambiguous, or contradicts other documents, that is a bug. Open an issue; documentation bugs are real bugs. For "how do I" questions rather than documentation defects, use Discussions [Q&A](https://github.com/URML-MARS/URML/discussions/categories/q-a).
