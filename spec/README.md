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

# URML Specification

This directory holds the **normative** specification documents. Everything outside `/spec/` is supporting material — narrative docs (`/docs/`), reference implementations (`/reference/`), tools, examples, and the conformance suite. When in doubt, the spec wins.

## Layout

```
spec/
├── layer-1-hal/              Hardware abstraction. Capability manifests, frames, limits, safety-envelope schemas.
├── layer-2-primitives/       The atomic intent vocabulary. Verbs: move_to, grasp, hover, scan, detect, ...
├── layer-3-behavior/         Composition: sequence, branch, parallel, retry, error handling, variables.
├── layer-4-nl-grammar/       Natural-language interface. The LLM prompt contract, schemas, examples.
└── profiles/                 Domain-specific extensions: home, drone, industrial, ...
```

Layer 0 (substrate) is named in the Manifesto and the architecture document, but is **not** specified here — ROS 2, PX4, AUTOSAR, OPC UA and others are *targeted*, not defined.

## Versioning

Each spec layer and each profile **versions independently** under semantic versioning. The Manifesto's stability commitment (v1.0.0) applies per-artifact: Layer-1 v1.0.0 is a different stability commitment from Layer-3 v1.0.0, and they can be reached at different times.

A spec document's version is declared at the top of the document, in the same YAML frontmatter style RFCs use:

```yaml
---
spec: layer-2-primitives
version: 0.1.0
state: Draft
---
```

States mirror the RFC states: Draft → Open → Accepted → Implemented → (Rejected | Superseded | Withdrawn). A spec at Accepted is the authoritative version; a spec at Implemented is reflected in at least the reference runtimes required for conformance.

## How to change a spec

Any change to a spec document is an **RFC**, not a pull request. See [`/docs/rfcs/0001-rfc-process.md`](../docs/rfcs/0001-rfc-process.md). The RFC is the deliberation; the PR is the implementation. PRs that change spec semantics without a linked Accepted RFC are sent back.

## What goes here, what does not

**Goes here:** normative documents, JSON Schemas referenced from those documents, semantic definitions, conformance points (the parts of a spec the conformance suite tests against).

**Does not go here:** runnable code (in `/reference/`), examples (in `/examples/`), narrative documentation (in `/docs/`), open-ended design notes (in `/docs/rfcs/` if they're decision-making, otherwise in `/docs/`).

## Status

Phase 0. The layer and profile directories are stubs — each holds a `README.md` describing what the document will contain when it is drafted. The substantive specification work begins in Phase 1.
