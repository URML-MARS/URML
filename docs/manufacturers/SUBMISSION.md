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

# Submitting a Product to the Manufacturer & Product Directory

This page is for robot and product manufacturers who want a product listed in [docs/manufacturers/directory.md](directory.md).

The directory is self-reported. You validate your product's capability manifest with the open URML validator, optionally publish a federal-validation self-report from your own repo, and open a PR adding a row. The maintainer reviews the PR for completeness and merges it.

Before you start, read [TRADEMARK.md](../../TRADEMARK.md) and [FEDERAL-VALIDATION-SELF-REPORT.md](FEDERAL-VALIDATION-SELF-REPORT.md). The short version: listing does not grant a license to the URML or `URML-Certified` marks. Saying your manifest "validates under URML" is fine if it does. Saying your product is "URML-Certified" or "NDAA compliant by URML" is not, and will not be until the Phase 4 program launches.

## The five steps

### 1. Author your capability manifest with provenance

Write your manifest following [Tutorial 4: Writing your own manifest](../tutorials/04-writing-your-own-manifest.md), and complete its provenance exercise so the manifest carries a `provenance:` block declaring per-component country of origin, vendor, and role. Pass 5 (compliance policy) checks that block.

### 2. Validate against the bundled default policy

```bash
urml validate program.urml.yaml \
    --manifest manifest.yaml --envelope envelope.yaml --profile home
```

Run at a pinned URML commit, with no `--policy` and no `--no-policy`, so the bundled `us_federal_default.yaml` is in effect. Exit code 0 with `Validation passed` means every pass, including compliance, succeeded. Do not submit if validation fails.

### 3. Add `URML-FEDERAL-VALIDATION.md` to your product repo (optional)

If you want the federal-readiness wedge, drop a `URML-FEDERAL-VALIDATION.md` at the root of your repository using the exact template and phrasing rules in [FEDERAL-VALIDATION-SELF-REPORT.md](FEDERAL-VALIDATION-SELF-REPORT.md). If you are listing for integration reasons only, skip this step and leave the column blank.

### 4. Commit and pin

Commit your manifest and any `URML-FEDERAL-VALIDATION.md` to your product repository at a tagged release or a stable commit hash. The directory entry links to those files at the pinned commit, not to a moving `main`, so reviewers and buyers can verify the claim later.

### 5. Open a PR against this repo

Open a PR against `URML-MARS/URML` that adds one row to [docs/manufacturers/directory.md](directory.md). Use the manufacturer-listing PR template (it auto-loads if you append `?template=manufacturer-listing.md` to the New Pull Request URL).

The row needs:

- **Manufacturer**: org or person, linked to its site or repository.
- **Product / Robot**: the model name.
- **Profile(s)**: home, drone, industrial, or a combination.
- **Spec versions validated**: per-layer semver, comma-separated.
- **Federal-validation self-report**: raw URL to `URML-FEDERAL-VALIDATION.md` at the pinned commit, or left blank.
- **Manifest source**: raw URL to the manifest at the pinned commit.
- **Last-verified commit**: the seven-character short hash where those files live.

The PR template includes a trademark-and-phrasing acknowledgement checkbox. Tick it before requesting review.

## What the maintainer checks

Five quick things:

1. The row is complete and the manifest link resolves at the pinned commit.
2. If a federal-validation self-report is linked, it resolves at the pinned commit and uses only the factual phrasing in [FEDERAL-VALIDATION-SELF-REPORT.md](FEDERAL-VALIDATION-SELF-REPORT.md), including the mandatory disclaimer block.
3. The declared spec versions are well-formed per-layer semver.
4. No row text uses "URML-Certified", "NDAA compliant by URML", or any phrasing forbidden by the trademark and self-report rules.
5. The trademark-and-phrasing acknowledgement checkbox is ticked.

That is it. The maintainer does not audit your product, run your validation independently, or assess fitness for any particular purpose. The directory trusts the submission; readers who want stronger guarantees can re-run the open validator against your manifest themselves.

## Keeping your listing current

When URML ships a new spec version or a default-policy update that affects your declared coverage:

- Re-validate against your manifest at the new pinned commit.
- Update your manifest and any `URML-FEDERAL-VALIDATION.md` in your repo.
- Open a PR updating the directory row.

You have 90 days from a relevant spec bump to file an updated entry before the listing is removed for staleness. Nobody benefits from outdated claims sitting on the directory.

## Withdrawing a listing

Open a PR removing your row. No questions asked. Delisting is recorded in git, so the history is auditable.

## If something goes wrong

Open an issue describing the problem. The maintainer commits to responding within 30 days during Phase 0. The validator is Apache 2.0 and freely runnable, so disputes about whether a manifest validates are resolvable independently by anyone.

## What this is not

This directory is not a certification, an audit, or an endorsement. It is a public record that a manufacturer self-reported a validating manifest and, optionally, a reproducible federal-validation result. The `URML-Certified` program (Phase 4) is the certification surface and does not exist yet. See [TRADEMARK.md](../../TRADEMARK.md) and [CORE_COMMITMENT.md](../../CORE_COMMITMENT.md).
