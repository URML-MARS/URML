---
rfc: 0006
title: Connectivity as an abstract capability and link-loss as a validated safety contract
author: Ido Yahalomi (ido@jacob-ai.com)
state: Accepted
created: 2026-05-16
updated: 2026-05-16
supersedes: —
superseded-by: —
---

# RFC-0006: Connectivity as an abstract capability and link-loss as a validated safety contract

## Summary

URML today has a connectivity placeholder that does nothing. `SafetyEnvelope.link_loss_policy`
is a free-form string the validator's five passes ignore entirely; the drone and home
profiles name values for it (`return_to_home`, `halt_and_report`, …) but no static check
verifies the named behavior is even achievable on the target robot. This RFC promotes
connectivity to a first-class, **substrate-neutral** Layer-1 capability and turns
link-loss into a **validated** safety contract. It adds an abstract `connectivity:` block
to the capability manifest declaring *link roles* (`command_link`, `telemetry_link`,
`peer_link`, `payload_link`) with abstract properties only — criticality, autonomy-on-loss,
declared outage tolerance, and an ordered `assurance_class`. It replaces the free-form
`link_loss_policy` with a structured, per-role rule list. It extends the validator's
existing Pass 2 and Pass 3 (no new pass) so that a policy referencing an undeclared link
role is rejected, and an incoherent policy — `return_to_home` with no declared `home`,
`continue_autonomous` on a link the robot says it cannot fly without — is rejected with a
stable error code. It names no transport medium anywhere: WiFi/5G/LTE/RF/fiber is Layer 0
and stays out of URML. It adds no new layer and no Layer-2 primitive.

## Motivation

The red-mug demo's home envelope declares `link_loss_policy: halt_and_report`. The drone
profile documents `link_loss_policy: return_to_home`. A reader reasonably assumes URML
*checks* these. It does not. The string is parsed, echoed into the LLM-bridge prompt, and
otherwise discarded. Concretely, today all of the following validate as **accepted**:

- An envelope that says `link_loss_policy: return_to_home` against a manifest with no
  declared `home` location. On real link loss the robot has nowhere to return to.
- An envelope that says `link_loss_policy: hover` against a ground robot with no
  station-keeping capability. The declared failsafe is physically impossible.
- An envelope that says `link_loss_policy: banana`. Free-form strings accept typos.

This is precisely the class of error the project's value proposition rests on catching
*statically, before execution*. The geofence work (RFC-era PR #36/#38) established the
pattern: a constraint declared in the envelope, checked against the manifest, rejected
with a stable, LLM-consumable error code. Link-loss behavior is structurally identical and
is a safety/liability boundary — `CLAUDE.md` is explicit that the validator's safety
boundary must never be weakened, and an unenforced safety field is a weak boundary wearing
a strong field's name.

Separately, adopters increasingly ask URML to express that a mission *depends on*
connectivity (a supervised inspection that may not proceed without an operator command
link; a future fleet task that needs a peer link). That is intent, and URML cannot say it
today. The medium that carries the link (WiFi vs. 5G vs. a 900 MHz datalink) is *not*
intent — it is substrate, and naming it would fail the manifesto's substrate-neutrality
acid test. The reconciliation is to express the link's *assurance* abstractly and let the
substrate runtime bind an abstract role to a concrete radio.

## Detailed design

### Spec changes

**Layer 1 (`spec/layer-1-hal/README.md`).** New normative "Connectivity" subsection,
parallel to "Provenance and Compliance": a manifest MAY declare a `connectivity:` block
listing the abstract link roles the robot supports and, per role, whether the role is
required for operation, whether the robot can continue autonomously without it, a declared
maximum outage tolerance, and an abstract assurance class. The subsection states
explicitly that link *role* is abstract and the transport medium is Layer 0 and
deliberately out of scope.

**Layer 3 (`spec/layer-3-behavior/README.md`).** Note (not new schema): a behavior's
dependence on a link is expressed by the deployment declaring a link-loss rule governing
that role; the reactive handling composes from the existing `on_error` machinery (and the
already-sketched `on_error: substitute(...)`). No new composition operator.

**Profiles.** `drone`, `home`, and `industrial` READMEs migrate from the scalar
`link_loss_policy` to the structured form and each states a default connectivity posture
(see §Backward compatibility for the exact mapping).

### Validator changes

Two schema modules and the validator core change. No new pass; two whole-program checks
are appended to the existing Pass 2 and Pass 3 loops.

New schema module `reference/validator/src/urml_validator/schemas/connectivity.py`
(symmetry with how RFC-0004 added `policy.py`):

- `LinkRole` — closed enum: `command_link | telemetry_link | peer_link | payload_link`.
- `AssuranceClass` — closed, **ordered** enum (low→high):
  `best_effort | monitored | assured | safety_critical`. Ordering is deliberate so a
  future RFC can express "require ≥ assured" additively without a breaking enum change.
  This is the reconciliation of "transport media as intent": an *assurance* abstraction,
  never a medium.
- `DeclaredLink` (`extra="forbid"`): `role: LinkRole`,
  `required_for_operation: bool = False`, `autonomous_when_lost: bool = False`,
  `max_outage_seconds: float | None` (`ge=0`),
  `assurance_class: AssuranceClass = best_effort`, `description: str | None`.
- `Connectivity` (`extra="forbid"`): `links: list[DeclaredLink]`, with an after-model
  validator rejecting duplicate `role` values (surfaces as a Pass-1
  `argument.constraint_violation`, matching how `Step` enforces exactly-one-primitive).
- `LinkLossAction` — closed enum:
  `return_to_home | hover | land_now | halt_and_report | continue_autonomous`. This is
  the union of every value the three profiles already name, plus `continue_autonomous`
  (the "keep flying the mission" case, only coherent when the governed link is declared
  `autonomous_when_lost`).
- `LinkLossRule` (`extra="forbid"`): `role: LinkRole`, `action: LinkLossAction`,
  `max_outage_seconds: float | None` (`ge=0`).

`CapabilityManifest` gains one optional sibling of `provenance`:
`connectivity: Connectivity | None = None`.

`SafetyEnvelope.link_loss_policy` changes type from `str | None` to
`list[LinkLossRule]` (default empty). The field name is kept (the type changes) to
maximize continuity in profile docs and the LLM prompt.

New `ErrorCode` members (additive; `capability.*` / `envelope.*` namespaces):

| Code | Pass | Fires when |
|---|---|---|
| `capability.missing_link_role` | 2 | A link-loss rule governs a role but the manifest declares **no `connectivity` block at all**. |
| `envelope.link_loss_undeclared_role` | 3 | The manifest **has** a `connectivity` block but it omits the specific role a link-loss rule governs. |
| `envelope.link_loss_incoherent` | 3 | A rule's action is not satisfiable given the manifest (e.g. `return_to_home` with no declared `home`; `continue_autonomous` on a link with `autonomous_when_lost: false`). |
| `envelope.link_outage_exceeds_declared` | 3 | A rule's `max_outage_seconds` is *looser* than the manifest's declared tolerance for that role (envelope may only tighten — the invariant the whole envelope module exists to enforce). |

Pass 2 — `_check_connectivity_caps(manifest, envelope)`: collect the set of roles
governed by any `link_loss_policy` rule; for each, if `manifest.connectivity` is absent
or does not declare that role, emit `capability.missing_link_role`. No-op when no rules
exist (opt-in, exactly like Pass 5 with absent `provenance`).

Pass 3 — `_check_link_loss_coherence(manifest, envelope)`, per rule, reusing existing
predicates (`_AERIAL_DRIVE_TYPES`, the `home`-location check, `mobility.station_keeping`):

- role-existence is split so the two codes are **mutually exclusive by construction**
  (no dedup rule, no suppression logic): Pass 2 owns the "manifest declares no
  `connectivity` block at all" case (`capability.missing_link_role`); Pass 3 owns the
  "block exists but omits this role" case (`envelope.link_loss_undeclared_role`) and
  skips the rest of a rule whose role is undeclared. A single root cause therefore
  never produces two reports — the structural resolution of Drawback 2.
- `return_to_home` → requires a declared `home` location **and** an aerial `drive_type`.
- `land_now` → requires an aerial `drive_type`.
- `hover` → requires `mobility.station_keeping: true`.
- `halt_and_report` → requires `mobility` present (deliberately weak; documented).
- `continue_autonomous` → requires the matching `DeclaredLink.autonomous_when_lost`.
- `max_outage_seconds` looser than the manifest's → `envelope.link_outage_exceeds_declared`.

All emissions reuse the existing error shape so the LLM-bridge revision contract is
unchanged in shape.

### Reference runtime changes

Documented as a runtime contract, not a spec coupling:

- **PX4 runtime.** PX4 has native datalink-loss failsafe (`COM_DL_*`) and already
  establishes a heartbeat; it already maps `return_to_home` to
  `MAV_CMD_NAV_RETURN_TO_LAUNCH`. A conformant PX4 deployment configures the autopilot's
  datalink-loss failsafe to honor the declared rule. URML expresses intent; the autopilot
  enforces.
- **ROS 2 runtime.** No native datalink-loss failsafe. A conformant ROS 2 runtime must
  implement a link-loss monitor that triggers the declared action.

v0.1 conformance verifies the **validator statically rejects incoherent policies**. It
does **not** execute a simulated link drop; runtime honoring is a runtime contract (this
is the existing stance the drone profile already documents). Tightening to an executed
conformance scenario is named in Unresolved questions.

### Conformance suite changes

New substrate-agnostic, validator-only fixtures (no `expected_execution`), shaped like
the existing geofence-violation fixture:

- `drone/10_link_role_undeclared_rejected` → `capability.missing_link_role`
- `drone/11_link_loss_no_home_rejected` → `envelope.link_loss_incoherent`
- `drone/12_continue_autonomous_incoherent_rejected` → `envelope.link_loss_incoherent`
- `home/14_link_loss_hover_no_station_keeping_rejected` → `envelope.link_loss_incoherent`
- `industrial/03_link_outage_relaxed_rejected` → `envelope.link_outage_exceeds_declared`
- `drone/13_link_loss_rth_positive` → accepted
- `home/15_link_loss_halt_positive` → accepted

Every existing fixture envelope carrying a scalar `link_loss_policy` is migrated (only
`reference/validator/tests/fixtures/envelopes/home_default.yaml` carries one today).

## Backward compatibility

URML is pre-1.0; breaking changes are permitted (RFC-0002 §Backward compatibility,
RFC-0004 precedent). This RFC contains exactly one hard break: any envelope that set
`link_loss_policy` to a scalar string now fails Pass 1 with `argument.type`. This is the
correct failure (loud, at parse time, with a stable code) rather than the silent
acceptance it replaces. Migration is mechanical:

| Artifact | Old | New |
|---|---|---|
| `home_default.yaml` (test fixture) | `link_loss_policy: halt_and_report` | empty list in PR-1; structured rule + manifest connectivity in PR-2 |
| `spec/profiles/drone` | `link_loss_policy: return_to_home` | `[{role: command_link, action: return_to_home}]` |
| `spec/profiles/home` | `link_loss_policy: halt_and_report` | `[{role: command_link, action: halt_and_report}]` |
| `spec/profiles/industrial` | (silent) | `[{role: command_link, action: halt_and_report}]` (net-new normative posture: industrial cells stop on supervisory-link loss) |

`manifest_version` / `envelope_version` stay `"0.1"`. The `connectivity:` block is
optional; manifests without it and envelopes without link-loss rules behave exactly as
before (the feature is opt-in at both ends, like `provenance`/Pass 5).

## Drawbacks

1. **A real breaking change.** Every scalar `link_loss_policy` — including the drone
   profile's own documented default — breaks at Pass 1. Mitigated by the enumerated
   migration table and pre-1.0 status, but it is a genuine break, not a humblebrag.
2. **Two codes describe adjacent failures.** `capability.missing_link_role` (Pass 2)
   and `envelope.link_loss_undeclared_role` (Pass 3) both concern an absent link role.
   The implementation removes the double-report risk structurally — the two are
   mutually exclusive by construction (no `connectivity` block at all vs. a block that
   omits the role), so no fragile dedup rule is needed. The residual concern is
   real but narrower: both codes' `suggestion` text must point the LLM bridge at the
   *manifest*, not the program, or the bridge may "fix" the program when the manifest
   is the problem (the failure mode RFC-0004 calls out for policy errors). The shipped
   `suggestion` strings do this.
3. **Coherence is shallow in v0.1.** `halt_and_report` coherence reduces to "mobility
   present." The validator cannot prove the runtime actually halts. This RFC delivers a
   *static-coherence* contract, not a behavioral guarantee, and must not be oversold as
   one. This is the same honest limit the drone profile already states.
4. **`assurance_class` invites scope creep.** Reviewers will push for `min_bandwidth`,
   `max_latency_ms`, medium hints. Each is a step toward the transport catalog this RFC
   exists to avoid. The abstract-only line must be defended on every future PR.
5. **`peer_link` ships without semantics.** Declaring a role the spec cannot yet act on
   is a partially-empty abstraction. Justified because the enum is closed (a one-way
   door): fixing `peer_link` now makes the future multi-robot RFC additive rather than a
   breaking enum change — the same argument RFC-0002 makes for shipping a closed
   primitive set early.

## Alternatives considered

**Add a Layer-2 `require_link` / `check_link_health` primitive.** Rejected.
(a) One-way door: RFC-0002's central principle is composition over expansion, and
link-loss handling composes from the envelope contract plus the existing `on_error` /
sketched `substitute` with zero new vocabulary. (b) It places a sensing/assertion verb in
Layer 2, which RFC-0002 already rejected for `assert` ("invites authors to do logic in
Layer 2 that belongs at Layer 3 or in the validator's static checks"). (c) Weaker
substrate-neutrality acid test: a link-health primitive begs for medium-specific quality
metrics — exactly the transport catalog reconciled away. The chosen design passes the
acid test trivially: an envelope rule plus a declared `home` location are pure
declarations, implementable on a zero-ROS runtime (PX4 maps the consequence to
`MAV_CMD_NAV_RETURN_TO_LAUNCH`).

**A program-level `requires_link:` declarative field.** Rejected. The envelope rule
already carries the dependency; a parallel program-side declaration creates two sources of
truth Pass 2 would have to reconcile, and pushes a deployment concern into the program
(RFC-0004 ruled robot-vs-deployment acceptability belongs in the envelope/policy, not the
program).

**A new "Layer 0.5 / communications" layer.** Rejected. URML is constitutionally five
layers; Layer 0 is explicitly substrate and not part of URML. A communications layer
would either catalog transport media (substrate coupling, manifesto violation) or
duplicate what an abstract capability + envelope contract already expresses. Adding a
layer is the most invasive possible change and is unjustified when two optional schema
blocks suffice.

**Keep `link_loss_policy` free-form, validate by convention.** Rejected. An unenforced
safety field is the status quo this RFC exists to end.

## Prior art

- **PX4 / MAVLink datalink-loss failsafe** (`COM_DL_*`, `NAV_RCL_ACT`): the canonical
  prior art for "lose the link → take a declared safe action." URML abstracts the
  *intent*; PX4 is one conformant enforcement.
- **MAVLink heartbeat**: the substrate-level liveness mechanism URML deliberately does
  *not* specify (it is Layer 0); the abstract `max_outage_seconds` is the intent-level
  shadow of it.
- **AUTOSAR Adaptive `ara::com` service availability / E2E**: prior art for treating a
  communication link as a declared, monitored capability rather than an assumed constant.
- **Behavior trees / PDDL preconditions**: the "a declared condition must hold or a safe
  branch triggers" structure; URML keeps the check static, as RFC-0002 established.
- **Prior URML RFCs**: RFC-0002 (closed-vocabulary discipline, substrate-neutrality acid
  test), RFC-0004 (optional-block opt-in pattern, additive error codes, envelope-vs-program
  separation), the geofence PRs (#36/#38: the condition→static-check→stable-code pattern
  this RFC mirrors).

## Unresolved questions

1. **Executed link-drop conformance.** v0.1 verifies static rejection only. A future
   minor should add an executed conformance scenario (simulator drops the link; runtime
   must perform the declared action). What is the substrate-agnostic shape of that test?
2. **US-federal assurance hook.** `assurance_class` is ordered so a future Pass-5-style
   rule could require `≥ assured` for BVLOS command-and-control contexts. No such rule
   ships here: FAA BVLOS rulemaking is not final, and `CLAUDE.md` requires the default
   policy track enacted law only. This stays a hook, not a feature, until the law is final.
3. **`telemetry_link` / `payload_link` coherence.** This RFC's coherence checks are
   meaningful mainly for `command_link`. Do `telemetry`/`payload` losses warrant
   distinct actions beyond the shared enum, or is the shared `LinkLossAction` enough?
4. **Dedup direction — RESOLVED during implementation.** The draft asked whether to
   suppress one of the two role-absence codes. The shipped design makes the question
   moot: rather than emit-both-then-suppress, Pass 2 and Pass 3 partition the failure
   space so the codes are mutually exclusive by construction —
   `capability.missing_link_role` only when there is no `connectivity` block at all,
   `envelope.link_loss_undeclared_role` only when a block exists but omits the role.
   No dedup rule exists to get wrong, and each code carries a distinct, actionable
   `suggestion` (add a block vs. add a role to the existing block). See Detailed
   design §Validator changes and Drawback 2.

## Implementation note

The RFC authorizes six PRs. PR-1 is the load-bearing one and blocks the rest; docs land
in parallel at the end. Every commit is DCO-signed.

1. **PR-1 — schema + validator (the teeth).** `connectivity.py` (new),
   `manifest.py`, `envelope.py`, `errors.py`, `validator.py`, `schemas/__init__.py`;
   full Pass-2/Pass-3 unit tests; migrate `home_default.yaml` to an empty list so the
   existing suite proves the break is contained. The breaking type change lands here,
   behind this RFC. **Blocks PR-2…5.**
2. **PR-2 — conformance fixtures** + registry + migration to the structured form.
3. **PR-3 — LLM bridge** prompt summary (structured; empty when absent).
4. **PR-4 — profile READMEs** (drone / home / industrial).
5. **PR-5 — Layer-1 / Layer-3 spec READMEs.**
6. **PR-6 — JSON-Schema export verification** + regression test.

Order: PR-1 → (PR-2, PR-3 parallel) → (PR-4, PR-5, PR-6 parallel). The RFC stays
**Accepted** until all land, then advances to **Implemented** (RFC-0004 precedent).
Author and reviewer are the same person in Phase 0; the self-review checklist below is
the gate.

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs (three
      currently-accepted-but-wrong envelopes).
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (the rejected Layer-2 primitive,
      with the one-way-door reasoning and the acid test applied).
- [x] Drawbacks are listed; at least one is a real downside (the hard breaking change;
      the two-codes-one-cause overlap).
- [x] Backward compatibility is honest about what breaks (the scalar→list type change).
- [x] This RFC adds no Layer-2 primitive, so the ROS-2/non-ROS sketch requirement is
      N/A; the substrate-neutrality acid test is nonetheless applied in Alternatives.
- [x] The implementation note explains how this lands (six sequenced PRs, PR-1 blocking).
- [x] The author has re-read `CLAUDE.md` §What Claude Should Never Do and confirms this
      proposal does not violate it: no substrate coupling (no medium named, acid test
      applied), the safety boundary is strengthened not weakened, no cloud dependency,
      no LLM-provider coupling, scope stays civilian/industrial, US-federal alignment is
      a hook tracking enacted-law-only and ships zero new policy.
