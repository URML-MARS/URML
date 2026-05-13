# Security Policy

URML draws a hard line between two kinds of safety/security issues, because they need very different responses.

## 1. Specification safety issues

A *specification* safety issue is a flaw in URML itself: a primitive whose contract admits an unsafe interpretation, a behavior-composition rule that can produce undefined execution order, a profile that under-specifies its safety envelope, or any case where a valid URML program could direct a conformant runtime to do something dangerous.

**Report path:** file an [RFC](docs/rfcs/) describing the issue and the proposed fix. Spec safety lives in the open because every URML runtime needs to see the fix at the same time — there is no "vendor patch" for a specification.

If you are uncertain whether a problem is spec-level or implementation-level, open an issue first and the maintainer will route it.

## 2. Implementation vulnerabilities

An *implementation* vulnerability is a flaw in a reference runtime (`reference/ros2-runtime/`, `reference/px4-runtime/`, `reference/validator/`, `reference/llm-bridge/`) or in tools (`tools/`) where the bug is in URML's own code, not in the specification. Examples: a validator that fails to reject an out-of-envelope program, an LLM-bridge prompt that allows injection, a runtime that doesn't honor a primitive's declared limits, the compliance-policy engine (RFC-0004) failing to apply a denylist rule, or the bundled default policy file having syntactically valid but semantically broken rules that accept manifests the rules should reject.

**Report path:** email `security@urml.example` <!-- TODO: fill in real address after GitHub org setup -->. Please include:

- A description of the issue, including which component is affected.
- Steps to reproduce, or a minimal proof of concept.
- The impact you believe the issue has.
- Whether you have already disclosed this publicly.

**What to expect:**

- Acknowledgement within **seven days** during Phase 0; we aim to tighten this SLA as the project scales (see [`GOVERNANCE.md`](GOVERNANCE.md)).
- A coordinated disclosure window of up to **90 days** by default. We will discuss and adjust this with the reporter based on severity and how widely the affected code is in use.
- Credit in the fix's release notes, unless the reporter prefers to remain anonymous.

Please do **not** open a public issue for an implementation vulnerability until a fix is available and we have agreed on a disclosure date.

## Conduct concerns

For reports related to the [Code of Conduct](CODE_OF_CONDUCT.md), email `conduct@urml.example` <!-- TODO: fill in real address after GitHub org setup -->. Reports are handled confidentially by the maintainer (Phase 0) or the enforcement committee (Phase 1+).

## Compliance-data updates

URML's bundled default compliance policy (`reference/validator/src/urml_validator/policies/us_federal_default.yaml`, per [RFC-0004](docs/rfcs/0004-compliance-policy.md)) tracks enacted US federal regulation. When statute or final agency lists change (a new entry on the FCC Covered List; an updated DoD Chinese Military Companies designation; an NDAA amendment), the report path is **a normal pull request**, not a security disclosure. See [`GOVERNANCE.md`](GOVERNANCE.md) §Default Compliance Policy Maintenance for the cadence and the sources the bundled policy tracks.

If the bundled policy is *missing* a covered entity such that a real federal-procurement deployment would incorrectly pass URML validation — that *is* a security-relevant issue, and the implementation-vulnerability path above applies.

## Out of scope

- **Substrate vulnerabilities** (ROS 2, PX4, AUTOSAR, OPC UA, vendor SDKs). Please report those to the substrate's own security process. URML cannot fix bugs in code it does not maintain.
- **Vulnerabilities in third-party runtimes, profiles, or tools** that are not part of this repository. Contact the maintainer of that project directly.
- **Third-party compliance policy files.** URML supplies the mechanism and a bundled US-federal default. Other policy files (community-maintained or commercial; see [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) §What This Commitment Does Not Cover for the audited/certified commercial surface) are the responsibility of their authors. URML vulnerabilities in the *engine* that evaluates policies are in scope; flaws in *third-party rules* are not.

## Public security log

Once the first fix lands, a per-version `SECURITY-ADVISORIES.md` is added under `docs/` enumerating fixed issues, severities, and affected versions. Until then, this file is the canonical entry point.
