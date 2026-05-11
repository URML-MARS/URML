# URML Documentation

This directory holds documentation that supports — but is not part of — the formal specification. The spec itself lives in [`/spec`](../spec/). The decision history lives in [`rfcs/`](rfcs/). Reference implementations document themselves in [`/reference`](../reference/).

## Map

| Document | Purpose |
|---|---|
| [`architecture.md`](architecture.md) | The layered stack, expanded from the Manifesto. One section per layer: *what goes here*, *what does NOT go here*, *open questions*. Read this before proposing changes that cross layer boundaries. |
| [`glossary.md`](glossary.md) | Terms used across the spec, with one-line definitions. Extends `MANIFESTO.md` Appendix A. |
| [`open-questions.md`](open-questions.md) | Working list of decisions that are still open. Extends `MANIFESTO.md` Appendix B. Items move out of this file when an RFC resolves them. |
| [`rfcs/`](rfcs/) | The decision history. Numbered RFCs, the RFC process itself, and the template. |

## What goes here, what does not

**Goes here:** narrative documentation, tutorials (when they exist), the architecture overview, the glossary, working-out-loud notes that don't change spec semantics.

**Does not go here:** the specification documents themselves (they live in `/spec`), runtime documentation (lives in `/reference/<runtime>/README.md`), and anything that should be runnable code (examples live in `/examples`, tools in `/tools`).

If a doc here ever contradicts a spec document, the spec wins (per the precedence order in [`CLAUDE.md`](../CLAUDE.md) §Reference Documents).

## Style

- Markdown only. No reStructuredText, no AsciiDoc.
- One thought per paragraph. Bullets only when items are genuinely parallel and discrete.
- Write for a smart non-expert: the roboticist who has not seen URML before, not the URML core team.

Per [`CONTRIBUTING.md`](../CONTRIBUTING.md): a doc change that fixes a typo or clarifies wording is a normal PR. A doc change that documents a *new* behavior or contradicts the spec is an RFC.
