---
rfc: 0636
title: Lang2LTL (h2r/Lang2LTL) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-25
updated: 2026-06-25
supersedes: —
superseded-by: —
---

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

# RFC-0636: Lang2LTL (h2r/Lang2LTL) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #61 (university lane).

## Summary

[`h2r/Lang2LTL`](https://github.com/h2r/Lang2LTL) (Humans to Robots Lab, Brown University; Prof. Stefanie Tellex) grounds a free-form natural-language command into an LTL task specification that then drives a real robot. That natural-language-to-executable-spec path is exactly where URML's validate-before-actuate gate sits one step below: where Lang2LTL produces the formal task spec, URML validates each concrete action the spec dispatches against a declared capability manifest and a safety envelope before it executes. This is a request for comment.

## The relationship (URML beneath Lang2LTL)

- **Two complementary questions.** The LTL spec answers *what to achieve*; URML's capability check answers *whether this robot can admissibly do each step*. The formal spec says the task is well-formed; the manifest check says the step is within the robot's declared reach, force, mobility, and the safety envelope before it actuates.
- **At dispatch, not at grounding.** URML does not touch the language grounding or the temporal logic; it sits at the action-dispatch boundary, the last checkable point before motion.

## What is asked

1. Is a declared-capability layer beneath the LTL spec useful for deployment on a platform like Spot, or does the grounding already cover it?
2. Would a small worked example mapping a Lang2LTL-dispatched action onto a URML manifest (validated, no execution) help the conversation?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, the validate-before-actuate gate, beneath a natural-language-to-formal-spec pipeline. Part of Move #61 (university lane); US, Brown h2r.

## Implementation note

Outreach only. The post is a GitHub Issue on `h2r/Lang2LTL` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
