---
rfc: NNNN
title: <Short, descriptive title>
author: <Your Name> (<email>)
state: Draft
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
supersedes: <RFC-NNNN, or "—">
superseded-by: <RFC-NNNN, or "—">
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

<!--
0000-template.md is a TEMPLATE, not an RFC. Do not modify this file when filing
a new RFC; copy it to `NNNN-short-kebab-name.md` first.

All sections below are REQUIRED. If a section is truly N/A, keep the heading
and write one sentence explaining why.
-->

# RFC-NNNN: <Title>

## Summary

<!-- One paragraph. If a reader stops here, they should know what this RFC proposes. -->

## Motivation

<!-- The problem. Why is the status quo insufficient? Use concrete examples. -->

## Detailed design

<!-- The proposal. Schemas, signatures, grammar productions, file layouts —
whatever is needed to implement this without further guessing. Be specific
about which spec documents change and how. -->

### Spec changes

<!-- Layer 1 / Layer 2 / Layer 3 / Layer 4 / profile — list each affected
document and summarize the change. -->

### Validator changes

<!-- New checks the validator must perform; existing checks that change. -->

### Reference runtime changes

<!-- What each reference runtime must implement to remain conformant. -->

### Conformance suite changes

<!-- New tests, modified tests, deprecated tests. -->

## Backward compatibility

<!-- Which prior URML versions does this break? If pre-v1.0, name what
breaks. If post-v1.0, this section had better say "fully compatible" or
explain why a breaking change is unavoidable. -->

## Drawbacks

<!-- Honest accounting of why this might be a bad idea. If you cannot
think of any, you have not thought hard enough — try again. -->

## Alternatives considered

<!-- At least one. "I considered none" is a sign the proposal is
under-cooked. Explain why each alternative was rejected. -->

## Prior art

<!-- Behavior trees, PDDL, AUTOSAR services, robotics-paper formulations,
vendor APIs, prior URML RFCs — anything the design draws from or deliberately
diverges from. -->

## Unresolved questions

<!-- Concrete things the author does not yet know. Each should be small
enough to be answered before this RFC moves from Open to Accepted. -->

## Implementation note

<!-- The plan for landing this. Order of changes, expected pull requests,
who is doing what, expected timeline. -->

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [ ] The Summary alone tells a reader what is being proposed.
- [ ] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [ ] The Detailed design names every affected spec document and reference component.
- [ ] At least one alternative is genuinely considered (not a strawman).
- [ ] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [ ] Backward compatibility is honest about what breaks.
- [ ] If this RFC adds a Layer-2 primitive, both ROS-2 and non-ROS implementation sketches are present (substrate-neutrality acid test).
- [ ] The implementation note explains how this lands, not just what.
- [ ] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
