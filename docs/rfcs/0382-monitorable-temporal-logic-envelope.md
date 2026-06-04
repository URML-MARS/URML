---
rfc: 0382
title: Monitorable properties, a temporal-logic specification attached to the safety envelope
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-04
updated: 2026-06-04
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

# RFC-0382: Monitorable properties on the safety envelope

## Summary

URML's safety envelope declares static limits (velocity caps, geofences, occupancy zones) that the validator checks once, before dispatch. It cannot declare a property that must hold *over time during execution*, for example "speed stays under 1 m/s whenever a person is within 2 m" or "after a stop request, the robot halts within 500 ms." Those are runtime-monitorable temporal properties, and a whole ecosystem of runtime verification tools exists to enforce them (RTAMT, Reelay, Copilot, MoonLight). This RFC adds an optional `monitorable_properties` list to the safety envelope. Each entry names a property and expresses it in a small, closed temporal-logic core over signals the manifest and envelope already declare. URML stays declarative: it validates that each property is well-formed and references real signals, and it compiles the property to a target monitor dialect (STL, STREL, or a Copilot/Ogma pipeline). URML does not run the monitor. No primitive changes. Backward compatible (additive optional field).

The surface that demanded this RFC is the Move #28 safety / runtime-verification wave, whose index entry names it directly: "the load-bearing queued Spec RFC: a monitorable-property / temporal-logic specification attached to the safety envelope."

## Motivation

URML's pitch is that the validator is a static gate: it rejects inadmissible intent before the robot moves. That is exactly half of the safety lifecycle. The other half is runtime: some properties are not decidable statically because they depend on values that only exist while the robot runs (a person's distance, the time since an event, a sensor reading). The Move #28 ecosystem operates precisely there.

URML's safety envelope today can say "max_velocity: 1.0." It cannot say "max_velocity is 0.3 whenever `person_distance` is below 2.0," because that is a conditional, time-varying property over a runtime signal. It cannot say "the robot reaches a full stop within 500 ms of a `stop_requested` event," because that is a bounded-response temporal property. These are the bread and butter of signal temporal logic (STL) and its spatial extension (STREL).

Three concrete consequences of the gap:

1. **The envelope under-specifies safety.** A deployment that genuinely needs "slow near people" has to encode it out of band, in substrate code, where URML cannot see or check it. The static gate is blind to the property that matters most.
2. **The Move #28 engagements have no anchor.** RTAMT (RFC-0362), Reelay (RFC-0363), Copilot (RFC-0364), Ogma (RFC-0365), and MoonLight (RFC-0371) are all monitor backends. URML's pitch to them is "your monitor enforces a property URML declared." That pitch is empty until URML can declare the property. This RFC is the declaration those engagements assume.
3. **"Validate then monitor" is the whole story.** URML rejects inadmissible intent before dispatch; a runtime monitor enforces the temporal properties during execution. The two cover the lifecycle. Without this RFC, URML only tells half of it.

## Detailed design

URML does not become a runtime monitor and does not invent a new logic. It declares properties in a small named core and compiles them to existing monitor dialects. The design has three parts: the envelope field, the property core, and the compile targets.

### Field shape

Add an optional `monitorable_properties` list to `SafetyEnvelope` (`reference/validator/src/urml_validator/schemas/envelope.py`).

```yaml
monitorable_properties:
  - name: slow_near_people
    severity: critical
    dialect: stl
    expression: "always (person_distance < 2.0 implies speed <= 0.3)"
  - name: bounded_stop
    severity: critical
    dialect: stl
    expression: "always (stop_requested implies eventually[0, 0.5] (speed == 0))"
```

`monitorable_properties` is **optional**; an envelope that omits it validates exactly as today.

Each `MonitorableProperty` has:

| Field | Type | Meaning |
|---|---|---|
| `name` | identifier | Stable handle for the property (used in reports and monitor output) |
| `severity` | `info` / `warning` / `critical` | How a violation is treated by a downstream monitor; advisory to URML |
| `dialect` | `stl` / `stl_strel` / `custom` | Which temporal-logic dialect the expression is written in |
| `expression` | string | The property, in the declared dialect |
| `signals` | list of identifiers (optional) | Declared signals the expression references; if omitted, the validator infers them from the expression |

### The property core

URML defines a **small, closed temporal-logic core** rather than adopting a full STL grammar wholesale (that would be a large one-way door). The core covers the operators the Move #28 backends share and the properties real deployments need:

- **Atoms.** Comparisons (`<`, `<=`, `==`, `>=`, `>`) between a declared signal and a literal, or between two declared signals.
- **Boolean.** `and`, `or`, `not`, `implies`.
- **Temporal.** `always`, `eventually`, `until`, each optionally bounded by a time interval `[a, b]` in seconds (`always[0, 5] phi`).
- **Spatial (dialect `stl_strel` only).** `somewhere`, `everywhere`, `surround`, over a declared spatial relation, for spatio-temporal properties (geofence-over-time, fleet separation). This is the MoonLight/STREL surface and ties to RFC-0291 deconfliction volumes.

`dialect: custom` is an escape hatch: the expression is carried verbatim and validated only for signal references, for a deployment that needs an operator outside the core. Like RFC-0250's `custom`, it weakens the guarantee and is documented as such.

**Signals** referenced by an expression must resolve to something URML already declares: a manifest sensor (`perception.sensors[].name`), an envelope quantity (`speed`, `altitude`, `person_distance` from an occupancy zone), or a declared event (`declared_events`). The validator rejects a property that references an undeclared signal. This is what keeps the property honest: you cannot monitor what the manifest never said the robot can sense.

### Compile targets

URML compiles a core property to a monitor dialect for the chosen backend. The compilation is a documented mapping, not a runtime:

| URML core | STL (RTAMT, Reelay) | STREL (MoonLight) | Copilot (via Ogma) |
|---|---|---|---|
| `always[a,b] phi` | `G[a,b] phi` | `G[a,b] phi` | a Copilot stream that holds over the window |
| `eventually[a,b] phi` | `F[a,b] phi` | `F[a,b] phi` | a bounded Copilot trigger |
| `phi until psi` | `phi U psi` | `phi U psi` | a Copilot until-pattern |
| spatial ops | n/a | `somewhere` / `surround` | n/a |

The validator emits the compiled form into the `--json` report so a deployment can hand it to the chosen monitor. URML ships the STL mapping first (the RTAMT/Reelay path); STREL and Copilot mappings are noted as follow-on once the STL path is exercised.

### Validator behavior

`urml validate` adds:

1. **Parse.** Each `expression` is parsed against its declared `dialect`'s grammar. A parse failure is a clear validator error pointing to this RFC.
2. **Signal resolution.** Every signal in the expression must resolve to a declared sensor, envelope quantity, or event. Unresolved signals fail validation.
3. **Compile.** The property is compiled to the STL form (for `stl`) and surfaced in the report. `stl_strel` and `custom` are parsed and signal-checked but compiled only where a mapping exists.

The validator does **not** evaluate the property (it has no runtime trace) and does not gate dispatch on it. A monitorable property is, by definition, enforced at runtime by a monitor, not statically. URML's contribution is that the property is well-formed, references real signals, and is expressed once in a form every backend can consume.

### Reference runtime changes

No reference runtime is required to run a monitor to stay conformant (URML does not mandate runtime monitoring). A runtime *may* consume the compiled property and wire it to a monitor backend; that integration is the subject of the Move #28 engagements (Ogma emitting Copilot, RTAMT online monitoring) and is out of scope for this Spec RFC, which defines the declaration and the static checks.

### Conformance suite changes

`conformance/tests/test_envelope_monitorable_properties.py` adds:

1. A well-formed `slow_near_people` STL property over a declared `person_distance` signal passes and the compiled STL appears in the report.
2. A property referencing an undeclared signal (`battery_temp` with no such sensor) fails with the RFC-0382 error.
3. A property with a malformed expression (`always (` unterminated) fails parse.
4. An envelope omitting `monitorable_properties` validates unchanged.

## Backward compatibility

Pre-v1.0. Additive: `monitorable_properties` is optional, every existing envelope validates unchanged, and no Layer-2 program or reference runtime must change to stay conformant.

## Drawbacks

- **A grammar is a real commitment.** Even a small temporal-logic core is a surface URML now has to maintain and version. The mitigation is deliberate smallness (the operators the backends share) plus the `custom` escape hatch, and the precedent that the core grows only by RFC.
- **Declared, not enforced.** URML validates and compiles a property; it does not guarantee a monitor runs. A deployment could declare `slow_near_people` and never wire a monitor. This is the same shape as the static/runtime split generally, and the honest framing is "URML makes the property precise and portable; running it is the runtime's job."
- **Signal vocabulary is the hard part.** Binding `person_distance` to an occupancy-zone concept, or `speed` to a runtime quantity, requires URML to name runtime signals it has so far only reasoned about statically. This RFC scopes signals to what is already declared; a richer runtime-signal vocabulary may be a follow-on.
- **Dialect drift.** STL, MTL, and STREL differ in subtle semantics (strict vs non-strict until, interval inclusivity). URML's core has to pin one semantics and document divergences from each backend. That is real work and a source of subtle bugs.

## Alternatives considered

1. **Adopt STL wholesale as the expression language, no URML core.** Rejected. A full STL/STREL grammar is a large one-way door, and the backends disagree on dialect details. A small closed core URML controls, compiled to each backend, keeps URML opinionated and portable. The `custom` hatch covers the deployment that genuinely needs full STL.
2. **A separate top-level `monitors` document instead of an envelope field.** Rejected as the primary home. The properties are deployment-time safety constraints; the envelope is the deployment-time safety artifact. Putting them anywhere else fragments "the safety a deployment imposes" across two files.
3. **Free-text property strings, validated only for parse.** Rejected for the signal-resolution reason: a property that references a signal the robot cannot sense is not monitorable, and only signal resolution against the manifest catches that. Free text cannot.
4. **Do nothing; leave temporal properties to substrate monitors.** Rejected. That is the status quo and it is why the Move #28 engagements have no anchor and why the envelope under-specifies safety.

## Prior art

- Signal Temporal Logic (Maler & Nickovic) and MTL; STREL (Bartocci et al.) for the spatial extension.
- [RFC-0362 (RTAMT)](0362-rtamt-outreach.md), [RFC-0363 (Reelay)](0363-reelay-outreach.md), [RFC-0364 (Copilot)](0364-copilot-rv-outreach.md), [RFC-0365 (Ogma)](0365-ogma-outreach.md), [RFC-0371 (MoonLight)](0371-moonlight-outreach.md), the Move #28 monitor backends this declaration targets.
- [RFC-0006 (link-loss policy)](0006-link-loss-policy.md), the existing structured-envelope precedent (replacing a free-form string with a validated list), the same move this RFC makes for temporal properties.
- [RFC-0291 (operational-clearance volumes)](0291-operational-clearance-volumes.md), the spatial concept STREL properties would reference for fleet separation.
- [RFC-0004 (compliance policy)](0004-compliance-policy.md), the other "declared, checked, pluggable" mechanism in URML; this RFC mirrors its posture.

## Unresolved questions

1. **STL semantics pin.** Which exact semantics does the core adopt (interval inclusivity, strict vs non-strict until)? The lean is to match RTAMT's defaults since it is the anchor engagement, and document divergences. To be settled before Open.
2. **Runtime-signal vocabulary.** This RFC scopes signals to declared sensors, events, and envelope quantities. Is that enough for real properties, or does URML need a small explicit runtime-signal declaration (a named, typed signal list)? Possibly a follow-on RFC.
3. **Compile-target scope for v1.** Ship only the STL mapping, or STL + STREL together? STREL pulls in RFC-0291 spatial relations. The lean is STL first, STREL as a fast follow.
4. **Severity semantics.** `severity` is advisory to URML and consumed by the monitor. Should the validator do anything with it (for example, refuse a program if a `critical` property references a signal the manifest marks unreliable)? Deferred.

## Implementation plan

1. Land the `MonitorableProperty` model and `monitorable_properties` field in `reference/validator/src/urml_validator/schemas/envelope.py`.
2. Land the core grammar parser and the signal-resolution check in `reference/validator/` (Pass 3 extension).
3. Land the STL compile mapping and report surfacing.
4. Land the conformance tests in `conformance/tests/`.
5. Update the Layer-3 / envelope spec doc to document the field and the core.

The STL path lands first in a single PR; STREL and Copilot mappings are separate follow-on PRs once STL is exercised against RTAMT.

## How to respond

This is a Spec RFC. Comments belong in the RFC's PR thread on `URML-MARS/URML`.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is proposed.
- [x] Motivation grounded in concrete properties (slow-near-people, bounded-stop) and a concrete gap (Move #28 has no anchor).
- [x] Detailed design names every affected component and pins the core grammar and compile targets.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (grammar commitment, declared-not-enforced, signal vocabulary, dialect drift).
- [x] Backward compatibility honest (additive, optional).
- [x] No Layer-2 primitive added; the declaration is substrate-neutral (compiles to multiple monitor backends, none assumed).
- [x] Implementation note explains how it lands (STL first, STREL/Copilot follow-on).
- [x] Re-read CLAUDE.md §What Claude Should Never Do; the core is closed and RFC-gated, no backend is embedded, no cloud dependency.
