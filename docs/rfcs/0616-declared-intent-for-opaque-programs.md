---
rfc: 0616
title: Declared intent for opaque programs (best-effort, attested)
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-06-15
updated: 2026-06-15
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

# RFC-0616: Declared intent for opaque programs (best-effort, attested)

## Summary

URML's static-validation posture assumes it can see the intent before it runs. A `call_program` (RFC-0015) breaks that assumption on purpose: the program body is opaque, a substrate-defined routine URML invokes by name. The validator still gates it (the name must be declared in `programs:`), but it cannot check what the routine *does*. For a simple commissioned routine that is fine. For a sufficiently general program, a coroutine-style plan that runs arbitrary code, or a learned-policy rollout, it is not just hard but impossible: deciding what the program will do is the halting problem.

This RFC adds an optional `declared_intent` to a `Program`: a best-effort, attested declaration of the primitives the opaque body exercises, validated as a **claim** against the manifest rather than as a proof of the body. It is not a new primitive and not a change to `call_program`; it is an optional, additive manifest field.

**State: Implemented** (2026-06-15). Ships the schema (`DeclaredIntent` + `Program.declared_intent`), a Pass-2 check with three codes, three conformance fixtures, a runnable example, unit tests, and the spec text. Additive end to end: a program without `declared_intent` is unaffected; `manifest_version` stays `"0.1"`.

## Motivation

The gap was surfaced by real engagement. URML reached the [bluesky](https://github.com/bluesky/bluesky) maintainers (RFC-0590), whose run-engine executes experiment "plans." Their lead, Thomas Caswell, corrected a premise URML had led with:

> bluesky plans are not declarative, they are generator co-routines ... inside of a plan you can do arbitrary Python in response to the results of previous messages. ... we can't tell if the plan provided bad info upfront until we actually run it (and trying to introspect the code before we run it turns into the halting problem).

He also pointed at the honest middle ground:

> We do already wrap the generator in a class so that we can warn if things are not actually yielded from, so extending that for an opt-in check so the plan can report what it intends to do, but it would have to be best effort/made correct by hand.

That is exactly the design here. URML cannot verify an opaque or Turing-complete program. But the program can *opt in* to declaring what it intends to do, and URML can check that declaration against the manifest. The declaration is a claim, made-correct-by-hand, not a proof, and the validator says so.

## Proposal

### Schema (Layer 1)

`Program` gains an optional `declared_intent` block:

```yaml
programs:
  - name: pick_place_cycle
    description: Commissioned AS-language pick-and-place cycle.
    declared_intent:
      primitives: [move_to, grasp, place_at]   # non-empty; URML primitives the body exercises
      attestation: asserted                    # asserted (default, best-effort) | verified
      max_force_n: 20.0                         # optional; claimed peak grasp force
      note: Best-effort declaration, made correct by hand.
```

`attestation` records the strength of the claim:

- **`asserted`** (default): hand-maintained, made-correct-by-hand. Validated as a claim and flagged with a best-effort advisory so no one mistakes it for a proof.
- **`verified`**: the substrate can prove the body matches the declaration. No advisory.

This mirrors URML's provenance attestation ladder (self-declared vs third-party-audited): a checkable claim is worth more than nothing and less than a proof, and the manifest is honest about which it is.

### Validation (Pass 2, capability)

For each program with a `declared_intent`:

- Every `primitives` entry must be a URML primitive (`capability.declared_intent_primitive_unknown`).
- Each claimed primitive's capability must be present in the manifest (`capability.declared_intent_unsupported`) using a coarse, capability-presence map (`grasp` needs `manipulation`, `move_to` needs `mobility`, `detect` needs `perception`, and so on). The check is deliberately coarse: a declaration is a claim, not the per-argument validation a real step gets.
- A `max_force_n` must fit the strongest declared gripper, else `capability.declared_intent_unsupported`.
- An `asserted` attestation raises `capability.declared_intent_asserted`, a **warning** (it does not reject), so a reader knows the check covered the declaration, not the opaque body.

## Alternatives considered

- **Try to statically analyze the program body.** Rejected: it is the halting problem for a general program, exactly the point the bluesky maintainers made. URML does not pretend to solve it.
- **A new primitive (e.g. `call_program_with_intent`).** Rejected per the fewer-primitives doctrine: this is metadata on the existing `Program`, not a new behavior.
- **A free-form intent string.** Rejected: a typed `primitives` list against the vocabulary lets the validator actually check the claim; free text could not be checked.
- **Reject opaque programs that lack a declaration.** Rejected: `declared_intent` is opt-in. RFC-0015's name-declaration gate is the floor; this is an optional, stronger, still-best-effort layer above it. Making it mandatory would break every existing `call_program`.

## Prior art

URML's provenance attestation ladder (RFC-0004: self_declared vs third_party_audited) is the direct model for `attestation`. The "validate the claim, flag that it is a claim" pattern matches how the default policy treats self-declared provenance (accepted but warned). The opaque-program gate is RFC-0015; the optional-binding precedent on `Program` is RFC-0019 (`ara_com`).

## Implementation plan

Shipped in one slice:

- Schema: `DeclaredIntent` model + `Program.declared_intent` (`manifest.py`).
- Validator: `_check_declared_intent` + the `_DECLARED_INTENT_REQUIRES` primitive→capability map; three `ErrorCode`s (two errors + the asserted warning); wired into `validate()` with severity routing.
- Conformance: `declared_intent_cell` / `_unsupported` / `_unknown` manifests + three `programs/` fixtures (asserted positive, unsupported negative, unknown-primitive negative).
- Example: `examples/industrial/declared-intent-cycle` (validates under the default policy with the asserted advisory; executes hermetically via `call_named_program`).
- Spec: Layer-1 §2.8a (programs). Tests: `reference/validator/tests/test_declared_intent.py` (7 cases).

## Open questions (deferred, not blocking)

- **A richer envelope claim.** v0.1 ships `max_force_n` only. Claimed speed/geometry bounds, checked against the active safety envelope, are an additive extension.
- **What `verified` requires.** The mechanism by which a substrate proves a body matches its declaration (a typed plan IR, a sandbox, a signed attestation) is substrate-specific and left open; `verified` is the schema slot for it.
- **Per-argument claims.** The declaration lists primitives, not their arguments. A future version could let a program declare argument bounds, at the cost of duplicating the per-primitive arg models.
