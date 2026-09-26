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

# Rulebooks: Normative Specification

This document is a Draft, proposed by [RFC-0702](../../docs/rfcs/0702-rulebooks.md). It becomes normative when RFC-0702 is accepted. The reference validator implements it, and the format stays Draft until then.

The decision history is in [RFC-0702](../../docs/rfcs/0702-rulebooks.md). The regulatory frame is [RFC-0003](../../docs/rfcs/0003-us-alignment.md). The model this document mirrors is the compliance policy, [`policy.md`](policy.md).

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are to be interpreted as in RFC 2119.

---

## Purpose

A **rulebook** is a YAML document that states what law or an organization allows a robot to do. The validator checks every program against the rulebooks that apply to it, in a pass that runs after the safety-envelope pass, and cites the rule when it refuses a program.

The validator reads four deployment-time files. Each has one owner.

| File | Says | Owner |
|---|---|---|
| Manifest | what the robot can do | the robot's maker or integrator |
| Safety envelope | what this site allows physically | the site operator |
| Rulebook | what law and company policy allow | a regulator or an organization; the operator, for declarations and exceptions |
| Compliance policy | what the robot may be made of | procurement |

A rulebook names places but never defines their geometry, and it never describes hardware. Geometry lives in the manifest's declared areas and the envelope's zones; hardware lives in the manifest.

## Disclaimer

**A program passing a rulebook is not a legal compliance determination.** This specification defines a mechanism. Whether a rulebook correctly encodes a law or a company's rules, and whether an operation that passes it is lawful, is a matter for counsel and for the people who run the operation, not for URML. URML records what the rulebook's author and the operator declare. It does not certify, and it does not verify declarations or waivers.

A rulebook checks the statically checkable subset of the rules it encodes. The rest are listed as obligations, and the operator remains responsible for every one of them. Every bundled government rulebook carries a `reviewed` date: the day its text was last checked against its sources. Deployers MUST verify a bundled rulebook against current law before relying on it.

## File format

A rulebook is a YAML mapping:

```yaml
rulebook_version: "0.1"            # required, literal "0.1"
rulebook_id: <identifier>          # required; unique among the rulebooks loaded together
title: <string>                    # required
issuer:                            # required
  kind: government | organization | deployment
  name: <string>                   # required
  jurisdiction: <string>           # required for government; optional otherwise (e.g. "US")
maintained_by: <string>            # optional; who wrote and maintains this file
source_status: final_rule | enacted_statute | organization_policy | deployment_declaration
effective: <ISO-8601 date>         # optional, informational; quote it
reviewed: <ISO-8601 date>          # required for government rulebooks; quote it
description: <string>              # optional

applies_to:                        # optional; not allowed on a deployment rulebook
  profiles: [<profile>, ...]
  drive_types: [<drive_type>, ...]
  unless_declared:
    - key: <identifier>
      allowed: [<scalar>, ...]
      cite: {text: <string>, url: <string>}   # optional

rules: [<rule>, ...]               # optional; not allowed on a deployment rulebook
obligations: [<obligation>, ...]   # optional; not allowed on a deployment rulebook

declarations: {<key>: <scalar>}    # deployment rulebooks only
exceptions: [<exception>, ...]     # deployment rulebooks only
```

An `<identifier>` matches `^[a-z][a-z0-9_]*$` and is at most 64 characters, the same rule as every other URML name. A `<scalar>` is a string, an integer or a boolean. Dates are ISO-8601 calendar dates written as quoted strings, so YAML does not turn them into date objects.

The following constraints are **normative**:

1. **No expression language.** A rule is one of the six fixed kinds below, with flat keys. There are no conditions, functions, regular expressions or arithmetic beyond what a kind defines.
2. **Unknown keys are rejected**, at every level of the document.
3. **Issuer and source status agree.** A `government` rulebook has `source_status` `final_rule` or `enacted_statute`. An `organization` rulebook has `organization_policy`. A `deployment` rulebook has `deployment_declaration`. There is no status for a proposed rule, so no government rulebook can encode one.
4. **A deployment rulebook carries declarations and exceptions only.** It MUST NOT carry `applies_to`, `rules` or `obligations`. Other rulebooks MUST NOT carry `declarations` or `exceptions`.
5. **Government rulebooks cite.** Every rule and obligation of a `government` rulebook carries `cite` with both `text` and `url`, and the rulebook carries `reviewed`.
6. **Ids are unique.** Rule ids and obligation ids share one namespace and are unique within a rulebook. A rule is referenced from outside its file as `<rulebook_id>/<rule_id>`.
7. **`rule.*` is a reserved namespace.** Rulebook authors do not choose error codes. Each rule kind emits the code this document assigns to it.

A file that breaks any constraint is invalid. The validator reports `rule.rulebook_invalid` (an error, so the program is refused) and does not apply that file.

### Applicability

A rulebook without `applies_to` applies to every validation it is loaded into.

A rulebook with `applies_to` is **in scope** for a validation when either list matches: the program declares one of `profiles` (in its `profile` field, or among the profiles the caller passes to the validator), or the robot's manifest declares one of `drive_types` as `mobility.drive_type` (for a fleet program, any member's manifest). When both lists are absent, the rulebook is in scope for every validation.

The match is a union on purpose. A program's `profile` is written by whoever wrote the program, possibly a language model, while the manifest is fixed by the operator. A rulebook that lists `drive_types` follows the robot, whatever profile a program names.

An in-scope rulebook is **switched off** when any `unless_declared` condition holds. A condition holds when a loaded deployment rulebook declares `key` with a value in `allowed`. A switched-off rulebook applies no rules, and the report lists it with the condition as the reason.

A rulebook that is in scope and not switched off is **applied**.

## Rules

Every rule has these fields:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | an identifier, unique within the rulebook |
| `title` | yes | a short statement of the rule; messages quote it |
| `cite` | government rulebooks | `{text, url}`: the source the rule encodes, such as `14 CFR 107.51(b)` |
| `exceptable` | no (default `false`) | whether a deployment rulebook may declare an exception to this rule |
| `note` | no | informational: how a number was derived, what the rule cannot see |
| one kind key | yes | exactly one of `cap`, `forbid_primitive`, `forbid_zone_entry`, `forbid_over_people`, `require_declared`, `max_concurrent_aircraft` |

### `cap`

```yaml
cap:
  quantity: altitude_agl_m | speed_m_per_s | grip_force_n
  max: <number, 0 or more>
```

A value the program states that is above `max` violates the rule: `rule.cap_exceeded`. The unit is part of the quantity's name, so a rulebook never converts units at run time.

| Quantity | The values judged |
|---|---|
| `altitude_agl_m` | `take_off.altitude`; `return_to_home.altitude` and `scan.altitude` when given; `move_to.pose.z` when given; and the declared altitude (`pose.z`) of the named place a step targets, for `move_to.location`, `hover.over`, `pick_from.source`, `place_at.target` and `dock` (the named or default station) |
| `speed_m_per_s` | `move_to.speed`, `drive.speed` and `return_to_home.speed` when given, and `follow_trajectory.speed_envelope.max_velocity_mps`. A speed given as a fraction is the fraction times the manifest's `mobility.max_velocity` (Layer-2 §1.1). A fraction on a robot with no `mobility` block is not judged here; Pass 2 already refuses the step |
| `grip_force_n` | `grasp.force`, `pick_from.force`, and the force of each grasp side of `bimanual`. `gentle` and `firm` resolve to the same newton values the envelope pass uses |

These are the same altitude values the safety-envelope pass compares with `max_altitude`, so the two passes never disagree about which numbers are altitudes. The validator reads them as heights above ground level, as the drone profile's envelope does. An altitude stated in another frame, such as a WGS-84 altitude above mean sea level, is judged as stated; a program that states heights that way needs an above-ground frame. `take_off.climb_rate` is a vertical rate and is not a speed for this rule. A landing place's altitude and a search region's altitude are not judged, because a landing ends on the ground and a search region is not a place the robot goes to.

Caps compose with the manifest and the envelope: the strictest limit wins. Each file reports its own violation with its own code. A value above both the envelope's `max_altitude` and a rulebook cap draws `envelope.altitude_exceeded` and `rule.cap_exceeded`.

### `forbid_primitive`

```yaml
forbid_primitive:
  primitives: [<primitive>, ...]    # required, non-empty: Layer-2 primitive names
  in_zones: [<zone>, ...]           # optional
  names: [<identifier>, ...]        # optional; not with except_names
  except_names: [<identifier>, ...] # optional; not with names
```

A step violates the rule, `rule.primitive_forbidden`, when all of these hold:

- it uses a listed primitive, directly or through a composite use (below);
- with `names`, the step's name for that primitive is listed; with `except_names`, it is not listed (an allowlist);
- with `in_zones`, the step happens in one of the listed zones (see *Places and zones*).

`names` and `except_names` are allowed only when every listed primitive has a name argument: `call_program` (its `name`), `set_output` (its `output`) and `gesture` (its `name`). Both lists are non-empty when present.

A step counts as a use of every primitive it composes, so a rule cannot be evaded by a synonym:

| Step | Also counts as a use of |
|---|---|
| `pick_from` | `move_to`, `detect`, `grasp` |
| `place_at` | `move_to`, `release` |
| `bimanual` | `grasp` or `release`, per side |
| `scan` with `media: photo` or `media: video` (the default is `photo`) | `capture` |
| `listen` with a `prompt` | `speak` |

### `forbid_zone_entry`

```yaml
forbid_zone_entry:
  zones: [<zone>, ...]   # required, non-empty
```

A step that names a target in one of the zones violates the rule: `rule.zone_forbidden`. A point target violates when it lies in the zone. An area target violates when it shares any point with the zone. Targets are defined under *Places and zones*.

### `forbid_over_people`

```yaml
forbid_over_people:
  unless_declared:                         # optional
    - key: <identifier>
      allowed: [<scalar>, ...]
      cite: {text: <string>, url: <string>}   # optional
```

The rule judges steps executed by an aircraft: a robot whose manifest declares `mobility.drive_type` `multirotor`, `fixed_wing` or `vtol`. Every target such a step names is judged against every people-occupancy zone the robot's envelope declares, including the zones the envelope marks with `allow_override: true`. An operator's override accepts a physical risk; it does not change the law. A point target in a zone, or an area target that shares any point with one, violates the rule: `rule.over_people`.

When any `unless_declared` condition holds, the rule is satisfied and judges nothing. The bundled FAA rulebook uses this for the operations-over-people categories of 14 CFR Part 107 Subpart D.

The rule sees only the zones the envelope declares. With no envelope, or an envelope with no people-occupancy zones, it has nothing to judge.

### `require_declared`

```yaml
require_declared:
  key: <identifier>           # required
  allowed: [<scalar>, ...]    # optional
```

The rule is judged once per validation. It is satisfied when a loaded deployment rulebook declares `key` and, when `allowed` is given, declares one of the allowed values. Otherwise it is violated: `rule.declaration_missing`.

Severity depends on whether the operator has declared a deployment at all:

- With at least one deployment rulebook loaded, a violation is an **error**.
- With none loaded, the validator knows nothing about the operation, and a violation is a **warning**. The program is not refused for a declaration no one has been asked to file, and the report says what the deployment must declare.

### `max_concurrent_aircraft`

```yaml
max_concurrent_aircraft:
  max: <integer, 1 or more>                    # exactly one of these two
  max_per_remote_pilot: <integer, 1 or more>
```

The rule limits how many aircraft are airborne at the same time in a fleet program. A single-robot validation has at most one aircraft and never violates it.

The limit is `max`, or `max_per_remote_pilot` times the number of remote pilots in command. That number is the deployment declaration `remote_pilots_in_command`, a positive integer; when no deployment rulebook declares it, it is 1.

An aircraft is a fleet member whose manifest declares `mobility.drive_type` `multirotor`, `fixed_wing` or `vtol`. The validator tracks which aircraft are airborne:

- `take_off` makes the member airborne. `land` and `return_to_home` make it grounded once the step completes.
- A member whose first flight step, in the program's execution order (depth first, with the arms of a `branch` or a `parallel` in declaration order), is anything other than `take_off` is airborne from the start of the program: it may already be flying. The flight steps are `take_off`, `move_to`, `hover`, `scan`, `land`, `return_to_home` and `follow_trajectory`.
- A `sequence` runs its children in order.
- The arms of a `parallel` run at the same time. Every member airborne at any point in any arm counts as airborne for the whole node, together with every member airborne when the node starts.
- The arms of a `branch` are alternatives. The count inside the branch is the larger of the arms' counts. After it, a member is airborne if it is airborne at the end of any arm.
- A `retry` body is judged as written. After it, a member is airborne if it was airborne before the retry or at the end of the body.

The rule is violated when the number of airborne aircraft can exceed the limit at any point: `rule.concurrency_exceeded`, reported once per program with the aircraft involved.

## Obligations

```yaml
obligations:
  - id: <identifier>
    title: <string>
    text: <string>                          # optional
    cite: {text: <string>, url: <string>}   # required, with url, in government rulebooks
```

An obligation is a rule a static check cannot judge: visual line of sight, night lighting, weather, a pilot's certificate. The validator does not check obligations. It lists the obligations of every applied rulebook in the report of every validation, accepted or refused.

## Deployment rulebooks

A deployment rulebook is the operator's record of the facts a rule depends on. It has two parts.

### Declarations

```yaml
declarations:
  <key>: <string | integer | boolean>
```

A declaration is a fact about the operation that the operator asserts: the Remote ID method, an operations-over-people category, the number of remote pilots, whether the flight is indoors. Rules and rulebooks read declarations through `require_declared`, `unless_declared` and `max_concurrent_aircraft`. Keys are identifiers. Quote string values that YAML would read as booleans (`yes`, `no`, `on`, `off`).

When several deployment rulebooks are loaded, their declarations merge. Two deployment rulebooks that declare the same key with different values make the set invalid: `rule.rulebook_invalid`.

The bundled rulebook reads four keys:

| Key | Values | Read by |
|---|---|---|
| `remote_id` | `standard_remote_id`, `broadcast_module`, `faa_recognized_identification_area` | `us_faa_part107/remote_identification` |
| `operations_over_people_category` | `category_1`, `category_2`, `category_3`, `category_4` | `us_faa_part107/over_human_beings` |
| `remote_pilots_in_command` | a positive integer | `us_faa_part107/one_aircraft_per_pilot` |
| `indoor` | `true` | `us_faa_part107` `applies_to` (the rulebook is switched off) |

### Exceptions

```yaml
exceptions:
  - rule: <rulebook_id>/<rule_id>   # required
    basis: <string>                 # required, non-empty: the legal or organizational basis
    limit: <number>                 # required for cap and max_concurrent_aircraft rules; not allowed otherwise
    expires: <ISO-8601 date>        # optional; quote it
```

An exception narrows one rule for this deployment. Its `basis` names why, in terms an auditor can check: a certificate of waiver number, a regulation's own allowance, a company approval.

1. The named rule MUST be marked `exceptable: true`. An exception to a rule that is not exceptable, or to a rule id that the named rulebook, when loaded, does not have, makes the set invalid: `rule.rulebook_invalid`.
2. An exception to a rulebook that is not loaded, or not applied, has no effect.
3. A rule has at most one exception across all loaded deployment rulebooks. More than one makes the set invalid.
4. An exception to a `cap` rule states `limit` in the cap's unit. An exception to a `max_concurrent_aircraft` rule states `limit` as an integer, which replaces the computed limit. Exceptions to other kinds MUST NOT state `limit`.
5. When a rule is violated and an exception to it applies, the validator compares the validation date with `expires` and the value with `limit`. If the exception has not expired and the value is within the limit, the violation is reported as a **warning** with the same code, and `detail.exception` holds the exception. Otherwise the violation stays an error, and `detail.exception` says it expired or that the value exceeds the exception's limit.
6. The validation date is the date the caller passes (`as_of`), or today's date in UTC.

An exception never widens a rule for other deployments, and a program can never declare one: the program has no field for it.

## Places and zones

### Zones

A rule names zones. A zone name resolves, in this order, against:

1. the manifest's `declared_areas` (RFC-0615);
2. the envelope's `people_occupancy_zones`;
3. the envelope's `geofences`.

The first match is the zone. In a fleet program, the manifest and envelope are those of the robot executing the step. A name that resolves nowhere cannot be judged: the validator emits `rule.zone_undeclared` (a warning) once per rule, zone and robot, and judges the rule's other zones.

### Targets

The targets of a step are the places it sends the robot to:

| Step | Targets |
|---|---|
| `move_to` | the pose in its frame, or the named location or area |
| `pick_from` | `source` |
| `place_at` | `target` |
| `dock` | `at`, or the manifest's first docking station when `at` is omitted |
| `swap_tool` | `at` (a docking station) |
| `hover` | `over`, when given |
| `land` | `at`, when given |
| `return_to_home` | the declared location `home` |
| `scan` | the scan area: a named region, a polygon or a bounding box |

A declared location, a docking station and a pose are **point** targets. A declared area and a scan area are **area** targets. A `$reference` target is a runtime binding: it is named, but it has no place until the program runs.

### Where a step happens

A zone-scoped `forbid_primitive` rule needs to know where a step happens. It asks only for the steps that match its primitives and names:

- a step with targets happens at each target;
- `scan` happens over its area;
- `capture` happens at the robot's current place, and also at its `target` when the target names a declared place;
- every other step happens at the robot's current place.

The validator tracks each robot's **current place** as it walks the program in execution order. In a fleet program each member has its own.

- The current place starts unknown.
- After a step with a single resolved target, the current place is that target. After `scan`, it is the scan area.
- After `drive`, `turn`, `follow_trajectory` or `call_program`, or a step whose target is a `$reference`, it is unknown: relative motion, a trajectory and an opaque program end at places the validator cannot see.
- Every other step leaves it unchanged.
- The arms of a `branch` each start from the current place before the branch. After the branch, the current place is the arms' common end place, or unknown when they differ. A missing `if_false` arm counts as an arm that leaves the place unchanged.
- The arms of a `parallel` start from the current place before the node, except that when any arm moves the robot, the robot's place in every other arm is unknown. After the node, the current place is the arms' common end place, or unknown.
- A `retry` body that moves the robot starts from an unknown place, because a second attempt starts wherever the first one stopped. After the retry, the current place is the body's end place.

An arm or a body moves the robot when it contains a step that changes the robot's current place.

### Judging a place against a zone

A point is in a zone when it lies inside the zone's polygon; the boundary counts as inside. An area is in a zone when the two polygons share any point. A current place set by `scan` is an area.

A place and a zone in different frames are compared after the place is expressed in the zone's frame through the manifest's frame graph (RFC-0290). A scan polygon or bounding box has no frame of its own and is read in the zone's frame.

Zone rules fail closed. A rule refuses a step with `rule.place_unknown` when it must judge the step against a zone it resolved and cannot:

- a zone-scoped `forbid_primitive` rule, for a matching step that happens at an unknown place: an unknown current place, or a `$reference` target;
- `forbid_zone_entry` and `forbid_over_people`, for a `$reference` target;
- any zone rule, for a place that cannot be expressed in the zone's frame.

A rule with no resolved zone judges nothing and never reports `rule.place_unknown`. (The envelope pass abstains when frames do not connect, as RFC-0290 specifies today. A rule that cannot see a place cannot say the step is allowed.)

## Evaluation semantics

1. **Loading.** The validator loads the bundled rulebooks (unless defaults are disabled), then the caller's rulebooks in the order given. A file that fails the format is reported as `rule.rulebook_invalid` and not applied. When two loaded rulebooks share a `rulebook_id`, the set is invalid and the later one is not applied.
2. **Applicability.** Each loaded rulebook is in scope, switched off, or out of scope, as defined under *Applicability*. Deployment rulebooks are always loaded as data and never out of scope.
3. **Position.** The rulebook pass runs after the safety-envelope pass (Pass 3) and before the variable-binding pass (Pass 4). It runs whenever Pass 1 succeeds. It does not depend on the compliance policy: `policy=None` and `--no-policy` never skip it.
4. **Order.** Rulebooks are judged in load order, rules in document order, steps in execution order. Each violation is reported once per rule, step and zone or value.
5. **Conjunction.** Every rule of every applied rulebook is judged. Rules only restrict. No rule relaxes another; the only narrowing is by an exception or a declaration, as specified above.
6. **Severity.** Every violation is an error except where this document says otherwise: `require_declared` with no deployment rulebook, a violation within an applying exception, `rule.zone_undeclared` and `rule.defaults_disabled`.
7. **Result.** Errors and warnings merge into the validation result with every other pass. The program is accepted only when no pass reports an error.

## Error codes

| Code | Severity | Raised when |
|---|---|---|
| `rule.cap_exceeded` | error | a value is above a `cap` |
| `rule.primitive_forbidden` | error | a step uses a forbidden primitive |
| `rule.zone_forbidden` | error | a step's target is in a zone of a `forbid_zone_entry` rule |
| `rule.over_people` | error | an aircraft's target is in a declared people-occupancy zone |
| `rule.declaration_missing` | error; a warning when no deployment rulebook is loaded | a `require_declared` rule is not satisfied |
| `rule.concurrency_exceeded` | error | more aircraft can be airborne at once than the limit |
| `rule.place_unknown` | error | a zone rule cannot place a step it must judge |
| `rule.zone_undeclared` | warning | a rule names a zone that resolves nowhere |
| `rule.rulebook_invalid` | error | a rulebook file, or the set of loaded rulebooks, breaks this specification |
| `rule.defaults_disabled` | warning | a bundled rulebook that would apply was switched off by the caller |

A violation within an applying exception keeps its code and becomes a warning.

### Error payload

Every `rule.*` issue populates `ValidationError.detail`:

```python
{
  "rulebook_id": "us_faa_part107",
  "rule_id": "altitude_400ft_agl",        # absent for rule.rulebook_invalid and rule.defaults_disabled
  "rule_kind": "cap",
  "cite": {"text": "14 CFR 107.51(b)", "url": "https://www.ecfr.gov/..."},
  "issuer": {"kind": "government", "name": "Federal Aviation Administration", "jurisdiction": "US"},
  "exception": None,                       # or the applying exception, below
  "remediation_hint": "revise_program",    # or "fix_deployment"
  # kind-specific fields:
  "quantity": "altitude_agl_m", "value": 137.16, "limit": 121.92,
}
```

- `exception`, when an exception exists for the rule: `{"rulebook_id", "basis", "limit", "expires", "expired", "exceeds_limit"}`, where `rulebook_id` names the deployment rulebook that declared it.
- `remediation_hint` is `revise_program` when editing the program can resolve the issue, and `fix_deployment` when it cannot (`rule.declaration_missing`, `rule.rulebook_invalid`). The LLM bridge sends the first kind back to the model and stops on the second.
- Kind-specific fields: `quantity`, `value`, `limit` for caps; `primitive`, `used_by` (the step's own primitive when it differs), `name` and `zone` as they apply, for `forbid_primitive`; `zone` and `target` for zone entry and people zones; `key`, `declared_value`, `allowed_values` for declarations; `count`, `limit`, `aircraft`, `remote_pilots_in_command` for concurrency; `reason` for `rule.place_unknown`; `zone` for `rule.zone_undeclared`; `source` (the file, or the rulebook id when the file parsed) and `problems` (what is wrong) for `rule.rulebook_invalid`.
- In a fleet validation, `member` names the robot, as it does for other passes.

A step-level issue sets `primitive`, `path` and `field` the way envelope issues do. A program-level issue (`rule.declaration_missing`, `rule.concurrency_exceeded`, `rule.rulebook_invalid`, `rule.defaults_disabled`) has `primitive` null and a path of `["<rulebook>", <rulebook_id or file>]`.

The message starts with the citation text, names the value or the step, and names the limit. A warning under an exception also names the exception's basis. For example:

```text
14 CFR 107.51(b): maximum altitude 400 feet (121.92 m) above ground level. take_off.altitude is 137.16 m; the limit is 121.92 m.
14 CFR 107.51(b): maximum altitude 400 feet (121.92 m) above ground level. take_off.altitude is 137.16 m; allowed by exception: Certificate of waiver 107W-EXAMPLE-0001 (limit 152.4 m, expires 2027-03-31).
```

## The validation report

`ValidationResult` gains a `rulebooks` list, one entry for each loaded rulebook that is in scope (applied or switched off) and for each loaded deployment rulebook, in load order:

```python
{
  "rulebook_id": "us_faa_part107",
  "title": "14 CFR Part 107 and Part 89, statically checkable subset",
  "issuer": {"kind": "government", "name": "Federal Aviation Administration", "jurisdiction": "US"},
  "source_status": "final_rule",
  "effective": None,
  "reviewed": "2026-09-26",
  "bundled": True,
  "applied": True,
  "reason": None,                 # why a rulebook was switched off
  "obligations": [{"id": "visual_line_of_sight", "title": "...", "text": "...", "cite": {...}}],
  "declarations": None,           # the declarations, for a deployment rulebook
  "exceptions": None,             # the exceptions, for a deployment rulebook
}
```

Every surface that shows a validation result (the CLI's text and JSON output, the MCP tools, the ROS action server's result) SHOULD show the applied rulebooks and their obligations. A result with no applicable rulebook SHOULD serialize without the key, so its JSON is unchanged from before this specification.

## Loading and defaults

### Python API

```python
validate(program, manifest, envelope=None, profiles=(), policy="DEFAULT", *,
         manifest_base_dir=None,
         rulebooks=(),            # dicts or Rulebook models, applied in order
         default_rulebooks=True,  # False disables only the bundled rulebooks
         as_of=None)              # a datetime.date; None means today in UTC
```

`validate_fleet` takes the same three keywords.

### CLI

- `--rulebook PATH`, repeatable, on `urml validate`, `execute`, `run`, `translate` and `bench`.
- `--no-default-rulebooks` disables only the bundled rulebooks. The CLI prints a warning on stderr, and the result carries `rule.defaults_disabled` for each bundled rulebook that would have applied and that no loaded rulebook replaces under the same `rulebook_id`.
- `--no-policy` and `--policy` do not affect rulebooks.
- `urml schema --name rulebook` prints the JSON Schema of the format.

### Agent-facing surfaces

A surface that takes programs from a language model (the MCP server, the ROS action server, the LLM bridge) MUST take rulebooks and the default switch from operator configuration only, never from the agent's request. A deployment rulebook can carry exceptions, so an agent that could supply one could grant itself a waiver. The reference MCP server reads `URML_MCP_RULEBOOKS` (paths) and `URML_MCP_DEFAULT_RULEBOOKS` (`on` or `off`); the ROS action server reads the matching node parameters. A runtime that re-validates a program before execution MUST use the same rulebooks the first validation used.

### Bundled rulebooks

The reference validator bundles rulebooks in `urml_validator/rulebooks/`. Every bundled rulebook:

- is a `government` rulebook whose `source_status` is `final_rule` or `enacted_statute`;
- carries `reviewed`, and a `cite` with a `url` on every rule and obligation;
- carries `applies_to`, so it is in scope only for the programs and robots it names.

Bundled rulebooks track final rules and enacted statutes only. A proposed rule joins by RFC after it is published as final.

| Rulebook | Encodes | In scope for |
|---|---|---|
| `us_faa_part107` | the statically checkable subset of 14 CFR Part 107 and Part 89 (Remote ID); see the file for each rule's eCFR citation | drone-profile programs, and robots with an aircraft drive type; switched off by `indoor: true` |

## What the rulebook pass cannot see

The pass judges the program a validator is given, before it runs. It does not see:

- the path between two targets, or the robot's position at the start of the program;
- where relative motion, a trajectory or a `call_program` body takes the robot;
- people, places or hazards the manifest and envelope do not declare;
- time of day, weather, visibility, or the class of airspace;
- whether a declaration or an exception is true;
- the speed the robot reaches, as opposed to the speed the program commands.

Those are obligations, runtime checks, or the operator's responsibility.

## Conformance

A URML-compatible validator that implements rulebooks MUST:

1. Parse rulebook files that conform to *File format*, and report `rule.rulebook_invalid`, refusing the program, for any file or set of files that breaks a normative constraint.
2. Decide applicability exactly as *Applicability* specifies, including the union of `profiles` and `drive_types` and the `unless_declared` switch.
3. Implement each rule kind, the composite uses, the targets, the current-place tracking and the fail-closed zone checks exactly as specified.
4. Apply exceptions and declarations exactly as *Deployment rulebooks* specifies, and nothing else.
5. Emit the `rule.*` codes with the severities and `detail` payload in *Error codes*.
6. Report every in-scope rulebook and its obligations in every validation result.
7. Apply the rulebooks bundled with the reference validator by default, and disable only them when the caller passes `default_rulebooks=False` or `--no-default-rulebooks`, reporting `rule.defaults_disabled`.
8. Run the rulebook pass regardless of the compliance-policy argument.
9. Take rulebooks from operator configuration only on any agent-facing surface.

The conformance fixtures under `conformance/fixtures/rulebook/` exercise points 2, 3, 4, 7 and 8, and the codes of point 5, against the reference validator. The validator's unit tests exercise point 1, point 6 and the `detail` payload of point 5, and the MCP server and ROS 2 action server tests exercise point 9.

## Future work

The open questions of [RFC-0702](../../docs/rfcs/0702-rulebooks.md) are the follow-ups: whether the bundled rulebooks join the Core Commitment, structured waivers, state-level and non-US rulebooks, a rulebook summary in the Layer-4 prompt, time-of-day and weather rules as runtime monitors (RFC-0382), zone-scoped caps, and a rulebook for recreational flight under 49 U.S.C. 44809.

## Related documents

- [RFC-0702](../../docs/rfcs/0702-rulebooks.md): the decision history of this document.
- [`policy.md`](policy.md): the compliance policy, the file this one mirrors.
- [RFC-0003](../../docs/rfcs/0003-us-alignment.md): the US-federal regulatory frame.
- [RFC-0290](../../docs/rfcs/0290-frame-transform-graph.md): the frame graph that places targets in a zone's frame.
- [RFC-0615](../../docs/rfcs/0615-world-model-areas-and-detection.md): the manifest's declared areas, the first place a zone name resolves.
- [`spec/profiles/drone/README.md`](../profiles/drone/README.md): the drone profile, whose altitude cap this document lets a rulebook enforce.
- [`reference/validator/src/urml_validator/rulebooks/us_faa_part107.yaml`](../../reference/validator/src/urml_validator/rulebooks/us_faa_part107.yaml): the bundled FAA rulebook.
- [`examples/rulebooks/`](../../examples/rulebooks/): an organization rulebook, a deployment rulebook and an industrial template.
