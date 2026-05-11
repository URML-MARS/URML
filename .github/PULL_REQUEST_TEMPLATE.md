<!--
Thanks for contributing to URML.

Before opening this PR, please confirm the items in the checklist below.
Anything that changes specification semantics needs an accepted RFC first
(see docs/rfcs/) — PRs implement RFCs; they do not replace them.
-->

## What changed and why

<!-- One short paragraph. The "why" matters more than the "what" — the diff already shows the what. -->

## Linked RFC

- RFC: `docs/rfcs/NNNN-...md`  <!-- or: "Not required — this is implementation / docs / tests only, no spec change." -->

## How it was tested

<!-- Commands run, environments covered, fixtures added. If there is no test, justify why. -->

## Rollback plan

<!-- One line: how to back this out if it lands wrong. -->

## Checklist

- [ ] Commits are **DCO-signed** (`git commit -s`). See [`DCO`](../DCO) and [`CONTRIBUTING.md`](../CONTRIBUTING.md).
- [ ] Linked RFC is **Accepted** (or this PR does not change specification semantics).
- [ ] Tests added or updated for the change; existing tests pass.
- [ ] Conformance impact considered. If a primitive's contract changed, conformance tests are updated.
- [ ] Docs / READMEs / `CHANGELOG.md` updated.
- [ ] Substrate-neutrality acid test passes: anything touching Layer 2 can be cleanly implemented on a runtime with zero ROS dependencies.
- [ ] No content from outside the URML organization's canonical scope (civilian, consumer, educational, industrial, research) has been introduced.
