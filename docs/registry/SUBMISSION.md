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

# Submitting a Runtime to the Compatible Runtimes Registry

This page is for runtime authors who want their project listed in [docs/compatible-runtimes.md](../compatible-runtimes.md).

The registry is self-reported. You run the public conformance suite against your runtime, publish the report from your own repo, and open a PR adding a row. The maintainer reviews the PR for completeness and merges it.

Before you start, read [TRADEMARK.md](../../TRADEMARK.md). The short version: listing does not grant a license to the URML or URML-Certified marks. Calling yourself "URML-compatible" is fine if you pass the suite. Calling yourself "URML-Certified" is not, and won't be until the Phase 4 certification program launches.

## The five steps

### 1. Install the conformance suite

```bash
pip install urml-conformance
```

This pulls `urml-validator` and `urml-ros2-runtime` as dependencies. See the [conformance README](../../conformance/README.md) for setup detail and the editable-install path for development.

### 2. Add CONFORMANCE.md to your runtime repo

Drop a file at the root of your runtime repository declaring which URML spec versions you claim to support. The format follows the convention in [conformance/README.md](../../conformance/README.md):

```yaml
declares:
  layer-1-hal: 0.1.0
  layer-2-primitives: 0.1.0
  layer-3-behavior: 0.1.0
  layer-4-nl-grammar: 0.1.0
  profiles:
    home: 0.1.0
```

Only declare the versions you actually pass. A partial claim is fine ("Layer 2 only, no profile coverage yet"). An overclaim that fails the suite gets rejected during review.

### 3. Run the conformance suite

```bash
urml conformance run --output conformance-report.json
```

Exit code 0 means every fixture passed against the layers and profiles you declared. Exit code 1 means at least one fixture failed; the JSON report lists which ones. Do not submit a report with `all_passed: false`.

### 4. Commit and tag

Commit both `CONFORMANCE.md` and `conformance-report.json` to your runtime repository at a tagged release (or at minimum a stable commit hash). The registry entry links to the report at that pinned commit, not to a moving `main` branch, so reviewers can verify the claim later.

### 5. Open a PR against this repo

Open a PR against `URML-MARS/URML` that adds one row to [docs/compatible-runtimes.md](../compatible-runtimes.md). Use the registry-submission PR template (it auto-loads if you append `?template=registry-submission.md` to the New Pull Request URL).

The row needs:

- **Runtime**: name of your project, linked to its repository.
- **Maintainer**: org or person.
- **Substrate**: ROS 2, PX4, vendor SDK, etc.
- **Spec versions**: from your `CONFORMANCE.md`, comma-separated.
- **Conformance report**: raw URL to `conformance-report.json` at the pinned commit.
- **License**: your runtime's license (any OSI-approved license is acceptable).
- **Last-verified commit**: the seven-character short hash of the commit where the report lives.

The PR template includes a trademark-acknowledgement checkbox. Tick it before requesting review.

## What the maintainer checks

Five quick things:

1. The JSON report parses as a valid `ConformanceReport`.
2. `all_passed` is true.
3. The declared spec versions match the versions tested in the report.
4. The link to the report resolves at the pinned commit.
5. The trademark-acknowledgement checkbox is ticked.

That's it. The maintainer does not audit your code, run your tests independently, or assess fitness for any particular purpose. The registry trusts the report; readers who want stronger guarantees can re-run the suite against your runtime themselves.

## Keeping your listing current

When URML ships a new spec version that affects your declared coverage:

- Re-run the suite against your runtime.
- Update `CONFORMANCE.md` and `conformance-report.json` in your repo.
- Open a PR updating the registry row.

You have 90 days from a relevant spec bump to file an updated report before the listing is removed for staleness. The 90-day window is generous; nobody wants outdated claims sitting on the registry.

## Withdrawing a listing

Open a PR removing your row. No questions asked. Delisting is recorded in git, so the history is auditable.

## If something goes wrong

Open an issue describing the problem. The maintainer commits to responding within 30 days during Phase 0. The conformance suite itself is Apache 2.0 and freely runnable, so disputes about whether your runtime passes are resolvable independently by anyone.

## What this is not

This registry is not a certification, an audit, or an endorsement. It is a public record that the maintainer of a runtime ran the public suite, got a passing report, and submitted the result. The URML-Certified program (Phase 4) is the certification surface and does not exist yet. See [TRADEMARK.md](../../TRADEMARK.md).
