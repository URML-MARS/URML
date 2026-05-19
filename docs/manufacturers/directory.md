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

# Manufacturer & Product Directory

Robots and products listed here have been self-reported by their manufacturer as having a capability manifest that validates under the [URML validator](../../reference/validator/) for the spec versions and profile declared, optionally with a published federal-validation self-report.

This is a **self-reported** directory. URML does not certify, audit, or endorse listed products. Listing reflects only that the manufacturer submitted the entry. See [TRADEMARK.md](../../TRADEMARK.md) for what listing does and does not grant.

The `URML-Certified` conformance mark is a separate, future program (Phase 4). It is not in use today, and nothing on this page should be read as a certification claim. A federal-validation self-report, where present, is a factual reproducible statement, not a compliance determination; see [FEDERAL-VALIDATION-SELF-REPORT.md](FEDERAL-VALIDATION-SELF-REPORT.md).

## Relationship to the Compatible Runtimes registry

This directory is for companies that ship **robots and products**. The [Compatible Runtimes registry](../compatible-runtimes.md) is for companies that ship **runtimes** that translate URML down to a substrate (ROS 2, PX4, vendor SDK). Different audience, different claim. A product here declares that its manifest validates; a runtime there declares that it passes the conformance suite. If you do both, you may list in both, separately.

## How to submit

Open a PR following [SUBMISSION.md](SUBMISSION.md). It takes five steps and one PR.

## Current entries

No entries yet. Be the first by following [SUBMISSION.md](SUBMISSION.md).

<!-- Add new entries below this comment, one row per product. -->

| Manufacturer | Product / Robot | Profile(s) | Spec versions validated | Federal-validation self-report | Manifest source | Last-verified commit |
| ------------ | --------------- | ---------- | ----------------------- | ------------------------------ | --------------- | -------------------- |

## How to read this table

- **Manufacturer**: the org, linked to its site or repository.
- **Product / Robot**: the model name.
- **Profile(s)**: home, drone, industrial, or a combination.
- **Spec versions validated**: declared coverage. Per-layer semver, e.g. `layer-1: 0.1.0, layer-2: 0.1.0, profiles: home/0.1.0`.
- **Federal-validation self-report**: optional. Raw URL to the manufacturer's own `URML-FEDERAL-VALIDATION.md` at a pinned commit. Blank means the manufacturer listed for integration reasons without publishing the federal wedge. A present link is a factual self-report only, governed by [FEDERAL-VALIDATION-SELF-REPORT.md](FEDERAL-VALIDATION-SELF-REPORT.md).
- **Manifest source**: link to the capability manifest the claim is about, in the manufacturer's repository at the pinned commit.
- **Last-verified commit**: the seven-character short hash of the commit where the manifest and any self-report live.

## Early adopters

A short, optional note for the first manufacturers to list during Phase 0. This is recognition only. It carries no mark, no priority, and no commercial commitment (see [README.md](README.md) §"Launch partners (Phase 0)").

## Delisting

A product is delisted if any of the following happens:

- The manufacturer requests removal (open a PR removing the row).
- A bumped version of the spec invalidates the prior declared coverage and no updated entry is filed within 90 days.
- The trademark policy in [TRADEMARK.md](../../TRADEMARK.md) is materially violated, including a linked federal-validation self-report that breaks the phrasing rules in [FEDERAL-VALIDATION-SELF-REPORT.md](FEDERAL-VALIDATION-SELF-REPORT.md).

Delisting is recorded in the PR removing the row, so the history is auditable in git.
