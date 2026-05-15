# URML Trademark Policy (Stub)

Status: stub, non-binding interim statement of intent.
Established: Phase 0.
Authority: refines [GOVERNANCE.md §Trademark Policy](GOVERNANCE.md#trademark-policy). Does not modify the [CORE_COMMITMENT.md](CORE_COMMITMENT.md), which controls.

## What this is

A stub trademark policy, just enough for Phase 0. It exists so that public-facing surfaces of URML (the [Compatible Runtimes registry](docs/compatible-runtimes.md), the README, outbound communications) have a written boundary to point at.

The full policy, with formal definitions, dispute procedures, and revocation mechanics, ships in Phase 4 alongside the URML-Certified conformance program (see [MANIFESTO.md](MANIFESTO.md) phase roadmap).

## The marks

URML maintains two marks.

The word mark **URML** identifies the open specification and its reference implementations.

The conformance mark **URML-Certified** is reserved for the future Phase 4 certification program. It is not in use yet, and no party may claim it during Phase 0.

## Ownership

Both marks are filed in the founder's name during Phase 0. They are assignable to the URML Foundation once that entity exists (Phase 3+). The maintainer commits to not making decisions during Phase 0 that would block this assignment.

## What anyone can do

Use the word "URML" as a factual descriptor. Statements like "this library implements the URML specification" or "URML is an open standard for natural-language robot control" are fine. You don't need permission.

Describe a runtime, library, or tool as "URML-compatible" if it passes the public [conformance test suite](conformance/) against the URML spec versions it claims to support.

Submit your runtime for listing in the Compatible Runtimes registry by following [docs/registry/SUBMISSION.md](docs/registry/SUBMISSION.md). Listing reflects a factual record of submission, not an endorsement.

## What is off limits

Using the term "URML-Certified" in any form. Reserved until the Phase 4 program launches.

Implying URML endorsement, sponsorship, or affiliation when none exists. Being listed in the registry does not grant a license to imply URML has audited, endorsed, or sponsored the listed runtime.

Using the URML name in a product name that suggests official status (e.g., "URML Pro", "URML Cloud", "URML Enterprise") without written permission. Product names that make the relationship factual (e.g., "Foo Robotics URML Adapter") are fine.

Modifying the URML conformance suite and continuing to claim conformance against the modified suite. "URML-compatible" means passing the unmodified, current-version public suite.

## What listing in the registry does not grant

Listing in [docs/compatible-runtimes.md](docs/compatible-runtimes.md) does not grant any license to use the URML or URML-Certified marks beyond the factual descriptor use above. It does not indicate URML has audited, endorsed, sponsored, or assumed responsibility for the listed runtime. It does not indicate the listed runtime is fit for production, safety-critical, or regulated deployment. The conformance suite tests specification conformance, not fitness for any particular purpose. If a listing is later removed (failed update, withdrawal, delisting), no rights persist.

## Phase 4: the full policy

When the URML-Certified program launches, this stub will be replaced by a full TRADEMARK.md covering:

- Formal definitions of mark categories
- The URML-Certified policy: who can apply, what audit confirms it, how often re-certification is required, fees if any
- A dispute-resolution procedure for trademark misuse
- A revocation procedure for the URML-Certified mark
- Foundation-level governance of the marks (assumes the Phase 3+ foundation exists)

Until then, this stub is the operative public statement.

## Reporting trademark concerns

During Phase 0, open an issue in the URML repository or contact the maintainer per [CONTRIBUTING.md](CONTRIBUTING.md). The maintainer commits to responding within 30 days.

## Changing this document

Material changes follow the RFC process in [docs/rfcs/0001-rfc-process.md](docs/rfcs/0001-rfc-process.md). Typo and clarification fixes go through ordinary PRs. The full Phase 4 trademark policy will land as its own RFC and replace this document at that time.
