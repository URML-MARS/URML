# Federal-Validation Self-Report

This page defines a `URML-FEDERAL-VALIDATION.md` file that a manufacturer puts at the root of its own product repository. It mirrors the runtime-author `CONFORMANCE.md` convention: you generate a factual result with the open tooling, commit it at a pinned commit, and link to it. URML hosts nothing on your behalf.

Read this whole page before you publish anything. The phrasing rules are not optional and the boundary is narrow on purpose.

## What this is

A factual, reproducible statement that a specific capability manifest validates clean under URML's bundled US-federal default compliance policy, at a pinned URML commit, with no policy override. Anyone can re-run it, because [`us_federal_default.yaml`](../../reference/validator/src/urml_validator/policies/us_federal_default.yaml) is Apache 2.0 and public ([CORE_COMMITMENT.md](../../CORE_COMMITMENT.md) item 7).

## What this is NOT

It is not a certification, an audit, an endorsement, a compliance determination, or legal advice. Reusing the language from the bundled policy's own header:

> THIS IS NOT LEGAL ADVICE. A policy file passing the validator is not a legal compliance determination. Deployers must consult counsel for any binding compliance determination. Audited and certified policy files carrying third-party legal attestation are a separate commercial surface (see CORE_COMMITMENT.md, "What This Commitment Does Not Cover").

RFC-0004 §Unresolved questions item 6 is explicit: a robot whose validation passes under `us_federal_default.yaml` is not automatically "URML-Certified" or "NDAA compliant." Certification is a separate, future, paid program.

## Generating the result

From a clone of `URML-MARS/URML` at a commit you will pin, run the validator against your program and manifest with the bundled default policy. Do not pass `--policy` and do not pass `--no-policy`; the default policy must be the one in effect.

```bash
urml validate program.urml.yaml \
    --manifest manifest.yaml --envelope envelope.yaml --profile home
```

Exit code 0 with `Validation passed` means all five passes, including Pass 5 (compliance policy), succeeded against the bundled default. Record the URML commit hash you ran against: `git -C /path/to/URML rev-parse --short HEAD`. That hash is mandatory in the report; the policy changes over time as US federal regulation changes, so a result is only meaningful pinned to a policy version.

## The `URML-FEDERAL-VALIDATION.md` file

Put this at the root of your product repository, filled in, at a tagged release or stable commit:

```markdown
# URML Federal-Validation Self-Report

- Product: <model name>
- Manifest: <path in this repo>
- URML profile: <home | drone | industrial>
- URML commit validated against: <7-char short hash>
- URML spec versions: layer-1-hal: 0.1.0, layer-2-primitives: 0.1.0, ...
- Command: urml validate <program> --manifest <manifest> --envelope <envelope> --profile <p>
- Result: Validation passed (exit 0), Pass 5 compliance policy clean under the
  bundled us_federal_default.yaml, no --policy override
- Date: <YYYY-MM-DD>

This is a factual self-report. The manifest above validates clean under URML's
open US-federal default compliance policy at the pinned URML commit. This is
NOT a certification, an audit, an endorsement, or a legal compliance
determination, and is not legal advice. The default policy is Apache 2.0 and
public; anyone can reproduce this result. See CORE_COMMITMENT.md and
docs/manufacturers/FEDERAL-VALIDATION-SELF-REPORT.md.
```

## Phrasing: what you may and may not say

You **may** say, in marketing and procurement materials, statements of this exact factual shape:

- "Manifest `<name>` validates clean under URML's open US-federal default compliance policy (`us_federal_default.yaml`) at URML commit `<hash>`, run `<date>`, with no policy override."
- "We publish a reproducible URML federal-validation self-report."

You **must not** say, in any form:

- "URML-Certified" or "URML Certified" anything.
- "NDAA compliant by URML", "URML-verified NDAA compliant", or any phrasing that attributes a compliance determination to URML.
- "Certified", "audited", "approved", or "cleared" for federal procurement on the basis of this result.
- "URML-endorsed", "URML-approved", or anything implying URML sponsorship, affiliation, or assumed responsibility.
- Any statement that drops the pinned commit, drops "self-report", or rounds "validates clean" up to a compliance claim.

If you cannot make the statement factual, reproducible, and pinned, do not make it. The directory submission requires you to acknowledge these rules; a listing whose linked self-report breaks them is removed.
