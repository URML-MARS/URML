---
rfc: 0639
title: Parameterized, reusable behaviors — named arguments instead of N hand-written programs
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-26
updated: 2026-06-26
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

# RFC-0639: Parameterized, reusable behaviors

**Kind: Spec.** Touches Layer-3 behavior composition (the program/behavior schema
and the validator), so it is a genuine normative change, not a runtime contract
like RFC-0638. This RFC scopes the design and leaves open questions for the
maintainer; no code ships until it is accepted. Adding a parameter mechanism to
the composition layer is close to a one-way door, so the bar for accepting it is
high and the framing below is deliberately cautious.

## Summary

A URML behavior today is a concrete tree of primitives. There is no way to write
one behavior, name it, and invoke it with arguments: "navigate from A to B" for
any declared A and B. A user with a ten-stop tour either writes ten near-identical
programs, or generates them outside URML by templating dicts before validation.

This RFC scopes a **parameterized, reusable behavior**: a named behavior with a
small set of typed parameters, invoked with arguments that substitute into the
fields of its steps. It is the smallest thing that removes the
N-minus-1-combinations problem without turning URML into a general-purpose
programming language, which is the real risk and the reason this is an RFC.

**State: Draft.** Design proposal with open questions (see the end). Nothing is
implemented yet, and the central open question is whether to do this at all versus
leave instantiation to the autonomy layer.

## Motivation

From the same live design conversation that produced RFC-0638
([Discussion #526](https://github.com/URML-MARS/URML/discussions/526)), an active
user building a real TurtleBot4-clone patrol described his tour and then asked,
in his words:

> Pass the current location name and goal location name into a parameterized URML
> program?

> Note use of a parameterized "Navigate from {valid named location} to {valid
> named location}" to eliminate need for N-minus-1-combinations of
> [from-to-named-location, ...]

He is right that hand-writing one program per leg of a tour does not scale, and he
is right that the body of each leg is identical up to two named locations: announce
the move, wait, `move_to` the goal, branch on the result to announce success or
failure, return. Only the two location names change.

This is a recurring shape, not one user's quirk. A warehouse pick tour, a home
cleaning route, an inspection circuit: all are "the same validated behavior, run
with different declared arguments." URML has no first-class way to express that.

## Why not the existing surface

**`$var` bindings (`store_as`).** A binding names a value *produced at runtime* by a
prior primitive, for a later primitive to consume (the decide/do split of RFC-0002,
`detect -> grasp($target)`). It flows forward from execution. It is not a
*caller-supplied parameter* chosen before the behavior runs. The two are different:
one is a runtime result, the other is an invocation argument.

**`call_program` (RFC-0015).** It invokes a *substrate*-declared program (a Kawasaki
AS job, an OPC UA method) by name, with `args`. It is opaque by design: URML does
not model the body, cannot validate it beyond a signature, and the body lives on
the substrate, not in URML. That is the wrong tool for "a reusable *URML* behavior,
validated like any other URML behavior." Reaching for it here would push portable
intent down into substrate-specific programs, the opposite of the goal.

**Templating outside URML (the status quo).** An autonomy layer can build a fresh
concrete program per leg by substituting two strings into a dict, then validating
that. This works today and is not wrong. Its cost is that the reusable unit is
invisible to URML: there is no named, validatable "navigate(from, to)" artifact,
each leg is validated from scratch, and the parameter contract (these two fields
are locations, and must be declared) is enforced by the autonomy author, not by
URML. This RFC asks whether that contract is worth making first-class.

## Proposal (sketch)

A **parameterized behavior**: a named behavior declaring typed parameters, plus an
**invoke** step that calls it with arguments.

```yaml
behaviors:
  navigate_leg:
    params:
      from:  { type: location }
      to:    { type: location }
    behavior:
      type: sequence
      on_error: continue
      steps:
        - announce: { text: "Navigating from $from to $to" }
        - wait:     { seconds: 5 }
        - move_to:  { location: $to }
        - report:   { to: run_log, facts: { arrived: $to } }

# ... a tour, run by the mastermind, one invoke per leg:
behavior:
  type: sequence
  steps:
    - invoke: { behavior: navigate_leg, args: { from: dock,    to: kitchen } }
    - invoke: { behavior: navigate_leg, args: { from: kitchen, to: patio   } }
```

The defining constraints, all chosen to keep URML declarative and statically
checkable:

1. **Parameters are typed values, not expressions.** A parameter is a `location`,
   a scalar, an enum, a duration. There is no arithmetic, no concatenation beyond
   simple field substitution, no computed parameter. A parameter named `to` of type
   `location` must be bound to a manifest-declared location, and the validator
   checks that at the call site.

2. **Substitution is field-level only.** `$to` may appear where a value of its type
   is legal (the `location` field of `move_to`, a `$to` token inside an `announce`
   text). It cannot synthesize structure, choose a primitive, or alter control flow.

3. **No new control flow.** `invoke` is a step like any other. It does not add
   loops or conditionals. The tour's *iteration* stays where it belongs: in the
   autonomy layer (the mastermind of RFC-0010), which decides the order of legs
   and emits one `invoke` per leg. URML gains a reusable unit, not a `for` loop.

4. **Statically validatable.** A parameterized behavior is checked once against the
   manifest and envelope for its parameter types; each `invoke` is checked for
   argument arity, types, and (for `location` and similar) declared-ness. An
   undeclared goal, a missing argument, or a type mismatch is a validation error
   before anything runs, exactly like every other URML check.

### The line this must not cross

The danger is obvious and worth naming. Parameters, then defaults, then conditional
substitution, then expressions, then a scripting language. URML's entire value is
that a program is a flat, statically verifiable artifact a validator can reason
about completely. If parameterization quietly reintroduces general computation, the
"validate before actuate" guarantee weakens, because you can no longer see the whole
behavior without running it. So the constraints above are not stylistic; they are
the safety boundary. If this RFC cannot stay inside them, the right answer is to not
do it and to leave instantiation in the autonomy layer.

## Alternatives considered

- **Do nothing; keep templating in autonomy.** Lowest risk, zero new surface. The
  autonomy layer stamps out a concrete program per leg and validates it. The user's
  N-minus-1 pain stays, but in code he already writes. This is the honest default
  and the bar the proposal must clear.
- **Lean on `call_program`.** Rejected: it is substrate-specific and opaque, the
  wrong home for portable URML intent (see above).
- **Macro expansion at parse time.** A parameterized behavior could be pure
  syntactic sugar: expand each `invoke` into its concrete subtree before validation,
  so the validator never sees parameters. Attractive because it adds no runtime
  concept and keeps the validated artifact concrete. Open question 3 asks whether
  this is the whole feature.

## Prior art / context

- RFC-0002 (decide/do, `$var` bindings) — the existing, different, runtime-binding
  mechanism this is often confused with.
- RFC-0015 (`call_program`) — the substrate escape hatch this deliberately is not.
- RFC-0010 (the mastermind / URML line) — iteration and ordering stay above URML;
  this only gives the mastermind a reusable unit to invoke.
- RFC-0638 (run report) — a tour's per-leg results ride the run report; the two
  RFCs compose (parameterized legs that each return structured telemetry).
- Subroutines with typed parameters and no closures are the conservative prior art
  (think a typed, side-effecting procedure call, not a lambda).

## Implementation plan (only after acceptance)

1. A `behaviors:` block (named parameterized behaviors) and an `invoke` step in the
   Layer-3 schema, with parameter type declarations.
2. Validator support: parameter typing, `invoke` arity/type/declared-ness checks,
   and substitution. Decide (open question 3) whether substitution is parse-time
   macro expansion or a runtime concept.
3. Conformance fixtures: a parameterized behavior invoked with valid and invalid
   arguments (undeclared location, missing arg, wrong type), each with its expected
   verdict.
4. A worked example: the #526 tour, a `navigate_leg(from, to)` behavior invoked
   across a multi-stop route by a plain-Python mastermind, validated and run on the
   mock substrate.
5. Layer-4 note: how the natural-language layer would or would not surface
   parameterized behaviors (likely it keeps emitting concrete `invoke`s).

## Open questions (for the maintainer)

1. **Do this at all?** Is the N-minus-1 pain worth a Layer-3 surface change, or is
   templating-in-autonomy the right, smaller answer? This is the real decision; the
   rest is detail.
2. **Parameter types.** Start with `location` only (the motivating and safest case),
   or a small fixed set (location, scalar, duration, enum) from the start?
3. **Macro expansion vs runtime concept.** Is a parameterized behavior pure
   parse-time sugar that expands to concrete subtrees before validation (so the
   validated artifact stays fully concrete, the strongest safety story), or a
   first-class runtime concept the report and progress events can name?
4. **Where behaviors are defined.** Inline in the program (as sketched), in a
   separate reusable library file, or both? A library raises versioning and trust
   questions a single program does not.
5. **Layer-4 surface.** Does the NL layer ever emit a parameterized behavior, or
   does it only ever emit concrete `invoke`s that a human or a mastermind wrote the
   behavior for? Keeping NL on concrete `invoke`s only is the conservative choice.
6. **Recursion and nesting.** Forbid a behavior invoking itself (and bound nesting
   depth) to preserve static checkability and termination? The cautious answer is
   yes: no recursion, shallow nesting only.
