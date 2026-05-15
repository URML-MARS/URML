<!--
Thanks for submitting your runtime to the URML Compatible Runtimes registry.

This template is for registry submissions only. For code or spec PRs, use the
default template. See docs/registry/SUBMISSION.md for the full submission flow
and TRADEMARK.md for what listing does and does not grant.
-->

## Registry entry

Fill in each field. The values below populate the row added in `docs/compatible-runtimes.md`.

- **Runtime name**:
- **Runtime repository URL**:
- **Maintainer (org or person)**:
- **Substrate (ROS 2 / PX4 / vendor SDK / other)**:
- **Declared spec versions** (from your `CONFORMANCE.md`):
  - layer-1-hal:
  - layer-2-primitives:
  - layer-3-behavior:
  - layer-4-nl-grammar:
  - profiles:
- **Conformance report URL** (raw `conformance-report.json` at a pinned commit):
- **License of the runtime**:
- **Last-verified commit (7-char short hash)**:

## Pre-submit checks

- [ ] `urml conformance run` against my runtime produced a report with `all_passed: true`.
- [ ] The report covers exactly the spec versions declared above. No overclaim.
- [ ] `CONFORMANCE.md` and `conformance-report.json` are committed at the pinned commit, not floating on `main`.
- [ ] The conformance report URL above resolves and returns valid JSON.
- [ ] I have read [TRADEMARK.md](../TRADEMARK.md).

## Trademark acknowledgement

- [ ] I understand that being listed in the Compatible Runtimes registry does not grant me a license to use the URML or URML-Certified trademarks beyond the factual descriptor use described in [TRADEMARK.md](../TRADEMARK.md). I will not describe my runtime as "URML-Certified". I will not imply URML endorsement, sponsorship, or affiliation.

## Maintenance commitment

- [ ] I will re-run the conformance suite against my runtime when URML ships a spec version that affects my declared coverage, and update my listing within 90 days of that spec version's release.
- [ ] I will open a PR removing my listing if my runtime stops passing the suite or if I no longer want it listed.

## Anything else the reviewer should know

<!-- Optional. Most submissions need nothing here. -->
