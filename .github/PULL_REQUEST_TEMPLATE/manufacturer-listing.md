<!--
Thanks for submitting a product to the URML Manufacturer & Product Directory.

This template is for manufacturer-directory submissions only. For code or spec
PRs, use the default template. For runtime submissions, use
?template=registry-submission.md instead. See
docs/manufacturers/SUBMISSION.md for the full submission flow,
docs/manufacturers/FEDERAL-VALIDATION-SELF-REPORT.md for the self-report rules,
and TRADEMARK.md for what listing does and does not grant.
-->

## Directory entry

Fill in each field. The values below populate the row added in `docs/manufacturers/directory.md`.

- **Manufacturer (org or person)**:
- **Manufacturer URL (site or repository)**:
- **Product / Robot (model name)**:
- **Profile(s) (home / drone / industrial / combination)**:
- **Spec versions validated**:
  - layer-1-hal:
  - layer-2-primitives:
  - layer-3-behavior:
  - layer-4-nl-grammar:
  - profiles:
- **Manifest source URL** (raw manifest at a pinned commit):
- **Federal-validation self-report URL** (raw `URML-FEDERAL-VALIDATION.md` at a pinned commit, or write `none`):
- **Last-verified commit (7-char short hash)**:

## Pre-submit checks

- [ ] `urml validate` against my manifest passed (exit 0, `Validation passed`) at the pinned commit, with no `--policy` and no `--no-policy` override.
- [ ] The declared spec versions match what I actually validated. No overclaim.
- [ ] My manifest, and my `URML-FEDERAL-VALIDATION.md` if I published one, are committed at the pinned commit, not floating on `main`.
- [ ] Every URL above resolves at the pinned commit.
- [ ] I have read [TRADEMARK.md](https://github.com/URML-MARS/URML/blob/main/TRADEMARK.md) and [docs/manufacturers/FEDERAL-VALIDATION-SELF-REPORT.md](https://github.com/URML-MARS/URML/blob/main/docs/manufacturers/FEDERAL-VALIDATION-SELF-REPORT.md).

## Trademark and phrasing acknowledgement

- [ ] I understand that being listed in the Manufacturer & Product Directory does not grant me a license to use the URML or `URML-Certified` trademarks beyond the factual descriptor use described in [TRADEMARK.md](https://github.com/URML-MARS/URML/blob/main/TRADEMARK.md). I will not describe my product as "URML-Certified" or "NDAA compliant by URML". I will not imply URML endorsement, sponsorship, affiliation, or a compliance determination.
- [ ] If I published a federal-validation self-report, it uses only the factual phrasing permitted in [docs/manufacturers/FEDERAL-VALIDATION-SELF-REPORT.md](https://github.com/URML-MARS/URML/blob/main/docs/manufacturers/FEDERAL-VALIDATION-SELF-REPORT.md), is pinned to a URML commit, and includes the mandatory "not a certification / not legal advice" disclaimer block.

## Maintenance commitment

- [ ] I will re-validate and update my listing within 90 days of a URML spec version or default-policy change that affects my declared coverage.
- [ ] I will open a PR removing my listing if my manifest stops validating or if I no longer want it listed.

## Anything else the reviewer should know

<!-- Optional. Most submissions need nothing here. -->
