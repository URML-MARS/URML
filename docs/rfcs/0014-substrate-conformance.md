---
rfc: 0014
title: Substrate conformance — what makes a runtime URML-compatible
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-19
updated: 2026-06-06
supersedes: —
superseded-by: —
---

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

# RFC-0014: Substrate conformance — what makes a runtime URML-compatible

## Summary

URML's value proposition is that one sentence runs on any substrate, but the
repository has never defined, normatively, what "runs on URML" means for a
runtime. "URML-compatible" is currently folklore: a runtime is compatible if it
"feels like" the ROS 2 reference runtime. This RFC defines a runtime's
conformance obligations as a small, testable contract — accept a Layer-1
manifest, implement the frozen substrate Protocol, validate before it actuates,
need no cloud, and pass the conformance suite — and defines two honest
conformance tiers (self-reported and, later, certified). It adds no primitive
and changes no existing schema; it writes down a boundary that already exists
implicitly, so that the universality claim is provable rather than asserted, and
so that the eventual *URML-Certified* trademark program has a specification to
certify against.

**State: Implemented** (2026-06-06). The contract ships as the versioned
[`spec/conformance/v0.1.0.md`](../../spec/conformance/v0.1.0.md). No code,
schema, or fixture changes: every reference runtime already satisfies the six
clauses, and the conformance suite is already the contract's executable form.

## Motivation

The standard is the moat (CLAUDE.md §Strategic Posture). A moat made of "works
everywhere" is worth nothing if "works" is undefined: two vendors can both claim
URML support, ship incompatible behavior, and the project has no document to
point at. The reference runtimes (ROS 2, PX4, and the growing set of zero-ROS
adapters) already share a precise contract — the substrate Protocol in
`reference/ros2-runtime/src/urml_ros2_runtime/substrate/base.py` and the
five-pass validate-before-execute discipline — but that contract is expressed
only as code and prose scattered across `conformance/README.md`, `CLAUDE.md`,
and the Layer-1 spec. Three concrete problems follow:

1. A new substrate author (the OPC UA, cobot, MuJoCo, and embedded runtimes
   under active development are the immediate examples) has no single document
   stating what they must satisfy to call the result URML-compatible. They
   reverse-engineer it from the ROS 2 runtime, which silently re-couples the
   ecosystem to ROS-shaped assumptions — the exact failure CLAUDE.md's acid test
   exists to prevent.

2. There is no defined, repeatable answer to "this substrate cannot express X —
   now what?" Without a written loop, the pressure is to bend a primitive or
   widen a schema quietly to make a substrate work. That is a one-way door taken
   in the dark.

3. The commercial surround named in CLAUDE.md — a paid certification program and
   the *URML-Certified* trademark — cannot exist without a specification of what
   is being certified. The specification must be in the open core (it is part of
   what makes the standard adoptable); only the certification *service* is
   commercial. This RFC is the missing open-core artifact.

## Detailed design

A runtime is **URML-compatible** if and only if it satisfies all of the
following. Each clause is already true of every reference runtime; this RFC only
names them.

1. **Manifest intake.** It accepts a valid Layer-1 capability manifest
   (`manifest_version: "0.1"`, `extra: forbid`) and refuses to execute a program
   that is not expressible under that manifest. It does not require any manifest
   field beyond the published Layer-1 schema.

2. **Frozen substrate Protocol.** It provides an adapter implementing the
   substrate Protocol (`reference/ros2-runtime/src/urml_ros2_runtime/substrate/base.py`)
   — every method, returning the published `SubstrateResult` subtypes, failures
   returned not raised. A primitive the substrate genuinely cannot perform
   returns an unsuccessful `SubstrateResult` with a clear reason; it does not
   crash and does not silently no-op.

3. **Validate-before-actuate.** It runs the full validator pass set (argument
   typing → capability → safety envelope → variable bindings → compliance
   policy) before a single actuator command is issued. A runtime that exposes a
   path which actuates without validation is not URML-compatible at any tier.
   This is a safety and liability boundary, not a performance tunable.

4. **Offline.** Once a program is validated, execution completes with no
   mandatory network or cloud dependency. Optional telemetry is opt-in and
   documented (CLAUDE.md). A runtime that cannot run a validated program
   air-gapped is not URML-compatible.

5. **Zero-ROS acid test.** The substrate Protocol contains no ROS type and no
   ROS assumption; a URML-compatible runtime may use ROS internally but MUST NOT
   require the URML layer above it to. This clause makes CLAUDE.md's existing
   acid test ("can it be cleanly implemented on a runtime with zero ROS
   dependencies?") a normative gate, not a code-review reminder. The PX4,
   marine, and the in-flight OPC UA / cobot / MuJoCo / embedded runtimes are the
   standing evidence that the test is satisfiable.

6. **Conformance suite.** It passes the conformance suite (`conformance/`) for
   the profiles it claims, run through `ConformanceRunner` with the runtime's
   own adapter via the existing `adapter_factory` hook. The suite is the
   executable embodiment of this RFC; this document is its rationale and its
   human-readable contract.

### Conformance tiers

Two tiers, deliberately only two, mirroring the honest split already described
in `conformance/README.md`:

- **Self-reported URML-compatible.** The runtime's authors run the conformance
  suite and publish the result. No third party is involved. This tier is free,
  requires no trademark, and is the only tier that exists in Phase 0. It is a
  factual claim ("the suite passes for profiles A, B"), not an endorsement.

- **URML-Certified.** A future, separately-operated program (outside this
  repository, per CLAUDE.md's commercial-surround separation) attests a runtime
  against this specification and licenses the *URML-Certified* trademark. This
  RFC defines only the *bar*; it does not create the program, set a price, or
  bless any vendor. Naming the tier here is what makes the later program
  possible without re-litigating the technical contract.

No numeric levels, scores, or star ratings: a runtime is compatible for the
profiles whose conformance fixtures it passes, and not for the others. Inventing
a richer grading scheme before there is a single external runtime to grade would
be premature taxonomy.

### The spec-gap loop (normative)

When a substrate genuinely cannot express something with the existing primitives
and the published manifest schema, the runtime author MUST NOT add a primitive,
widen a schema, or change a primitive's semantics to make it fit. The required
sequence is:

1. Record the need in the runtime package's `SPEC-GAPS.md`, stating whether it
   is *composable* from existing primitives (then document the composition — it
   is not a gap) or *genuinely inexpressible*.
2. For a genuinely inexpressible need, file an RFC **Draft** describing it. The
   substrate ships against the frozen Protocol with that capability returning an
   unsuccessful `SubstrateResult` until the RFC is accepted.
3. The maintainer (Phase 0) decides the RFC on its own merits. A primitive is a
   one-way door (RFC-0002, CLAUDE.md §What Claude Should Never Do); the gap loop
   exists so that door is only ever opened deliberately and in writing.

This formalizes, as project doctrine, the rule that integration work surfaces
spec gaps as proposals, never as silent expansion.

### Spec changes

This RFC is a normative definition; it adds no primitive, no manifest field, no
behavior semantics, and no profile.

The normative text of clauses 1–6, the tiers, and the gap loop lives as a
versioned specification document so it has parity with the layer specs and a
semver of its own. **Resolved (2026-06-06): option (a)** — the contract ships as
[`spec/conformance/v0.1.0.md`](../../spec/conformance/v0.1.0.md), giving
substrate conformance the same versioned, citable status as Layers 1–4 and the
profiles, with an orientation `spec/conformance/README.md`. Option (b)
(elevating `conformance/README.md` in place) was rejected because it would not
carry an independent semver.

Layer 1 / Layer 2 / Layer 3 / Layer 4 / profile specs: unchanged. This RFC cites
and must not contradict CLAUDE.md (the acid test and the Core Commitment),
`CORE_COMMITMENT.md` (the conformance suite is Apache-2.0 forever — so is this
specification; only the certification service is commercial), `conformance/README.md`
(the self-reported-vs-certified split this RFC formalizes), and the Layer-1 HAL
spec (substrate-neutral manifest intake).

### Validator changes

None. The validator already enforces validate-before-actuate; this RFC names
that enforcement as a conformance obligation rather than introducing a new check.

### Reference runtime changes

None. Every reference runtime already satisfies clauses 1–6; this RFC is written
*from* their shared contract. New runtimes must satisfy it from the start, which
they already do by mirroring the zero-ROS sibling-package template.

### Conformance suite changes

None required by this RFC. The suite is the contract's executable form; this
document is its written form. A later, separate PR may add a `SPEC-GAPS.md`
presence check or a conformance self-report manifest, but neither is normative
in v0.1 and neither blocks this RFC.

## Backward compatibility

Fully compatible. This RFC describes the contract every existing reference
runtime already meets and the validator already enforces. No program, manifest,
runtime, or fixture changes behavior. It is additive and pre-v1.0.

## Drawbacks

- **A written bar can read as exclusionary.** A partial runtime (say, navigation
  only) is "URML-compatible for the home profile's nav subset" — which is honest
  but less marketable than an unqualified "URML-compatible." Mitigation: tiers
  and per-profile scoping make partial conformance a precise, publishable claim
  rather than a disqualification, but the precision has a marketing cost and that
  cost is real.

- **Self-reported conformance can be gamed.** Until the certification program
  exists, a vendor can claim the suite passes without proof. This RFC does not
  fully solve that — only the trademark program does. It does, however, give the
  project a specific document to measure a disputed claim against, which is
  strictly better than the status quo of having none.

- **Naming a future certified tier risks looking like premature commercialization.**
  Mitigation: the RFC defines only the open-core bar and explicitly places the
  program and its economics outside this repository, consistent with the
  structural-separation posture in CLAUDE.md. The risk is presentational, not
  structural, but it is worth stating plainly.

## Alternatives considered

- **Leave it implicit (status quo).** Rejected: it re-couples every new
  substrate to ROS-shaped folklore and leaves the universality claim
  unfalsifiable — the precise failure mode this RFC exists to close.

- **A marketing badge with no normative text.** Rejected: a badge with nothing
  behind it is the open-core anti-pattern (claim without contract) and would
  make the eventual trademark indefensible.

- **Define a full multi-level certification scheme now.** Rejected as premature
  taxonomy: there is not yet one external runtime to grade. Two honest tiers and
  per-profile scoping carry all the weight v0.1 needs; a richer scheme can be a
  post-v1.0 RFC if real demand appears.

- **Put the normative text only in `CLAUDE.md`.** Rejected: `CLAUDE.md` is
  AI-session context, not a versioned public specification a third party can
  cite or certify against.

## Prior art

Conformance-suite-defined compatibility is well-trodden: the W3C test suites,
the SQL standard's conformance levels, the OCI image/runtime specs, and CNCF's
*Certified Kubernetes* (an open conformance suite plus a separately-run
trademark program) — the last is the closest structural analogue and an explicit
model for the open-spec / commercial-attestation split CLAUDE.md describes.
URML-internal prior art: RFC-0002 (primitive economy — why the gap loop guards a
one-way door), RFC-0007 (the manufacturer go-to-market this conformance bar
underwrites), and `conformance/README.md` (the self-reported-vs-certified split
this RFC promotes to normative).

## Unresolved questions

- **Document placement.** *Resolved (2026-06-06): option (a).* The normative
  contract lives at [`spec/conformance/v0.1.0.md`](../../spec/conformance/v0.1.0.md),
  versioned independently like the layer specs, with an orientation
  `spec/conformance/README.md`. `conformance/README.md` now points to it as the
  written form of the suite. Elevating `conformance/README.md` in place (option b)
  was rejected: it would not have given the contract its own semver.
- **Self-report artifact.** Whether a machine-readable conformance self-report
  (profiles claimed, suite version, commit) should be standardized later. Out of
  scope for v0.1; noted so it is not silently invented.

## Implementation note

Shipped as one documentation slice: this RFC advanced to `state: Implemented`,
plus the normative [`spec/conformance/v0.1.0.md`](../../spec/conformance/v0.1.0.md)
(clauses 1-6, the two tiers, the gap loop) and its `README.md`, the
`spec/README.md` layout entry, and a pointer from `conformance/README.md`. No
code, schema, or fixture: the conformance suite already exists as the contract's
executable form, and every reference runtime already satisfies clauses 1-6, so
there is nothing to implement to make the definition true. The in-flight
substrate PRs (OPC UA, cobot, MuJoCo, embedded) cite this contract and carry
their own `SPEC-GAPS.md` per the gap loop above.

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks.
- [x] If this RFC adds a Layer-2 primitive, both ROS-2 and non-ROS implementation sketches are present (substrate-neutrality acid test). — N/A: this RFC adds no primitive; it instead promotes the acid test itself to a normative conformance gate.
- [x] The implementation note explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
