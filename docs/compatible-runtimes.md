# Compatible Runtimes

Runtimes listed here have self-reported that they pass the public [URML conformance suite](../conformance/) against the spec versions they declare.

This is a **self-reported** registry. URML does not certify, audit, or endorse listed runtimes. Listing reflects only that the maintainer ran the conformance suite and submitted the result. See [TRADEMARK.md](../TRADEMARK.md) for what listing does and does not grant.

The URML-Certified conformance mark is a separate, future program (Phase 4). It is not in use today, and nothing on this page should be read as a certification claim.

This registry is for **runtime authors** (projects that translate URML down to a substrate). If you make **robots or parts** rather than runtimes, the parallel surface is the [Manufacturer & Product Directory](manufacturers/directory.md).

## How to submit

Open a PR following [docs/registry/SUBMISSION.md](registry/SUBMISSION.md). It takes five steps and one PR.

## Current entries

No entries yet. Be the first by following [SUBMISSION.md](registry/SUBMISSION.md).

<!-- Add new entries below this comment, one row per runtime. -->

| Runtime | Maintainer | Substrate | Spec versions | Conformance report | License | Last-verified commit |
| ------- | ---------- | --------- | ------------- | ------------------ | ------- | -------------------- |

## How to read this table

- **Runtime**: the project name, linked to its repository.
- **Maintainer**: the org or person who submitted and maintains the listing.
- **Substrate**: what URML compiles down to in this runtime (ROS 2, PX4, vendor SDK, etc.).
- **Spec versions**: declared coverage. Per-layer semver, e.g. `layer-2: 0.1.0, layer-3: 0.1.0, profiles: home/0.1.0`.
- **Conformance report**: link to the JSON report produced by `urml conformance run --output`, hosted in the runtime's own repository at a pinned commit.
- **License**: the runtime's license. URML is Apache 2.0; listed runtimes may use any OSI-approved license.
- **Last-verified commit**: the runtime commit hash at which the report was produced.

## Delisting

A runtime is delisted if any of the following happens:

- The maintainer requests removal (open a PR removing the row).
- A bumped version of the spec invalidates the prior report and no updated report is filed within 90 days.
- The trademark policy in [TRADEMARK.md](../TRADEMARK.md) is materially violated by the maintainer.

Delisting is recorded in the PR removing the row, so the history is auditable in git.
