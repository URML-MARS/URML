---
rfc: 0285
title: substrate.rmw_options.action_qos / service_qos — per-action / per-service QoS declarations
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-30
updated: 2026-05-30
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

# RFC-0285: `substrate.rmw_options.action_qos` and `service_qos` — per-action and per-service QoS

## Summary

RFC-0272 declared per-node QoS overrides and noted that ROS 2 actions and services have their own QoS surfaces beyond topic QoS. URML's manifest currently has no place to declare per-action or per-service QoS overrides. This RFC closes that deferral: adds `action_qos` and `service_qos` to `rmw_options` with patterns, override profiles, and precedence rules. Optional. Backward compatible. With this RFC, URML's QoS declaration surface covers all four ROS 2 QoS planes (topic, per-topic-pattern, per-node, action / service).

The surface that demanded this RFC is RFC-0272 deferred-question on per-action and per-service QoS declarations.

## Motivation

ROS 2 actions and services each have multiple QoS profiles:

- **Actions:** four sub-QoS (goal, result, cancel, feedback), each independently configurable.
- **Services:** two sub-QoS (request, response).

URML's manifest has covered topic QoS (RFC-0251 deployment-wide, RFC-0265 per-topic, RFC-0272 per-node). The action and service QoS surfaces have been undeclarable. Three concrete consequences:

1. **Action feedback QoS commonly needs override.** Long-running navigation actions emit feedback at high rate (10+ Hz pose updates); the default reliable feedback QoS can drop messages.
2. **Service request / response QoS sometimes need reliability tuning.** Trigger services for envelope-validation need reliable; query services for status need different timing.
3. **Goal / result reliability differs from feedback reliability.** Goal acceptance is one-shot reliable; result is one-shot reliable; feedback is per-step best-effort. URML's manifest needs to declare each independently.

## Detailed design

### Field shape

```yaml
substrate:
  class: ros2
  rmw_implementation: rmw_fastrtps_cpp
  rmw_options:
    qos_profile: ...                          # from RFC-0251 — deployment-wide topic QoS
    qos_profile_overrides: ...                # from RFC-0265 — per-topic
    per_node_qos: ...                         # from RFC-0272 — per-node
    action_qos:                               # NEW — this RFC
      - action_pattern: "/navigate_to_pose"
        goal_qos:
          reliability: reliable
          history: keep_last
          history_depth: 1
        result_qos:
          reliability: reliable
        cancel_qos:
          reliability: reliable
        feedback_qos:
          reliability: best_effort
          history: keep_last
          history_depth: 10
      - action_pattern: "/follow_path"
        feedback_qos:
          reliability: best_effort
          history_depth: 5
    service_qos:                              # NEW — this RFC
      - service_pattern: "/get_state"
        request_qos:
          reliability: reliable
          history_depth: 1
        response_qos:
          reliability: reliable
          history_depth: 1
      - service_pattern: "/trigger_safety_stop"
        request_qos:
          reliability: reliable
          history_depth: 1
          deadline_ms: 100                     # safety-critical; declared deadline
        response_qos:
          reliability: reliable
```

### Pattern syntax

Action and service patterns mirror the topic-pattern syntax in RFC-0265: glob-style with `/exact`, `/prefix/*`, `/prefix/**` semantics.

### Precedence with other QoS overrides

When a topic / action / service needs a QoS resolution, the validator and runtime follow:

1. **Per-action / per-service pattern match** (this RFC) — first-match wins among the action_qos / service_qos arrays.
2. **Per-node match** (RFC-0272).
3. **Per-topic match** (RFC-0265) — this only applies to topic publication / subscription, not to action / service traffic.
4. **Deployment-wide default** (RFC-0251).

Per-action and per-service patterns take precedence over per-node and per-topic for their specific traffic. The rationale: action / service patterns are more specific than node-level defaults; per-topic patterns don't naturally apply to action / service traffic.

### Sub-QoS field shapes

Action sub-QoS:

| Field | Description |
|---|---|
| `goal_qos` | QoS for goal acceptance (typically reliable; keep_last 1) |
| `result_qos` | QoS for result delivery (typically reliable) |
| `cancel_qos` | QoS for cancellation request (typically reliable) |
| `feedback_qos` | QoS for feedback messages (varies by action; commonly best_effort with keep_last N) |

Service sub-QoS:

| Field | Description |
|---|---|
| `request_qos` | QoS for service request |
| `response_qos` | QoS for service response |

Each sub-QoS uses the `QosProfile` schema from RFC-0251.

### Schema fragment (extending RFC-0251's rmw_options)

```jsonc
{
  "substrate": {
    "properties": {
      "rmw_options": {
        "properties": {
          "action_qos": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["action_pattern"],
              "properties": {
                "action_pattern": { "type": "string" },
                "goal_qos": { "$ref": "#/$defs/QosProfile" },
                "result_qos": { "$ref": "#/$defs/QosProfile" },
                "cancel_qos": { "$ref": "#/$defs/QosProfile" },
                "feedback_qos": { "$ref": "#/$defs/QosProfile" }
              }
            }
          },
          "service_qos": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["service_pattern"],
              "properties": {
                "service_pattern": { "type": "string" },
                "request_qos": { "$ref": "#/$defs/QosProfile" },
                "response_qos": { "$ref": "#/$defs/QosProfile" }
              }
            }
          }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional fields.** Missing `action_qos` and `service_qos` means actions / services use the deployment-wide topic QoS by default.
2. **First-match wins per array.** Multiple action patterns matching the same action emit a warning surfacing the resolution.
3. **`history: keep_last` requires `history_depth`.** RFC-0251 rule applies to each sub-QoS.
4. **Goal / result / cancel reliability soft-suggestion.** Setting `goal_qos.reliability: best_effort` is unusual (the goal should be reliable); the validator emits a soft suggestion when this happens.
5. **`feedback_qos` history_depth recommended.** When `feedback_qos: keep_last`, `history_depth` is recommended; without it, defaults apply but may cause silent feedback drops at high rates.
6. **Forward-compat.** Schemas extend `QosProfile` from RFC-0251.

### Reference-runtime behavior

Reference runtimes, on action / service creation, apply the matching pattern's sub-QoS profiles. The runtime's action / service client constructs the underlying topics with the declared sub-QoS values.

### Conformance test additions

`conformance/tests/test_manifest_action_service_qos.py`:

1. Manifest without `action_qos` and `service_qos` passes (uses deployment-wide topic QoS).
2. Manifest with `action_qos: [{action_pattern: /navigate_to_pose, feedback_qos.reliability: best_effort + history_depth: 10}]` passes.
3. Manifest with `action_qos: [{action_pattern: /goal, goal_qos.reliability: best_effort}]` passes with soft suggestion.
4. Manifest with `feedback_qos: keep_last` and no `history_depth` passes with soft suggestion.
5. Manifest with overlapping action_patterns emits warning.

## Backward compatibility

Pre-v1.0. Additive. Existing manifests continue to use deployment-wide topic QoS for action / service traffic; this RFC adds opt-in per-action and per-service overrides.

## Drawbacks

- **Four-layer QoS declaration system is operational complexity.** Topic, per-topic-pattern, per-node, per-action / per-service. Documentation must be clear; the precedence rules are not intuitive.
- **Pattern syntax slightly overlaps across the four declaration types.** Patterns target different name spaces (topic / node / action / service); operators must track which kind of pattern is which.
- **Per-sub-QoS schema is verbose.** Each action has four sub-QoS profiles; declaring all four can be 16+ lines of YAML. The validator does not require all four; missing sub-QoS inherits from the next-layer-up.
- **Runtime QoS-resolution overhead grows.** Each action / service creation now does pattern matching across multiple lists. The cost is small but accumulates.

## Alternatives considered

1. **Skip per-action / per-service QoS; rely on deployment-wide.** Rejected. Action feedback QoS commonly needs per-action override; ignoring this leaves URML's manifest incomplete.
2. **Combine action_qos and service_qos into one list with a `target_type: action | service` field.** Rejected. The two have different sub-QoS shapes (4 vs 2); separate lists read cleaner.
3. **Single `endpoint_qos` field covering topics + actions + services.** Rejected. Too generic; the specific sub-QoS semantics for actions and services are operationally distinct from topic QoS.
4. **Per-action sub-QoS as a flat `feedback_reliability: best_effort` style instead of nested `feedback_qos: {reliability: best_effort, ...}`.** Rejected. The nested form composes with `QosProfile` reuse from RFC-0251.

## Prior art

- [RFC-0251 (substrate.rmw_implementation)](0251-substrate-rmw-implementation.md) — parent Spec RFC; deployment-wide QoS.
- [RFC-0265 (qos_profile_overrides)](0265-substrate-rmw-qos-overrides.md), [RFC-0272 (per_node_qos)](0272-substrate-rmw-per-node-qos.md) — sibling Spec RFCs; this RFC closes the deferred per-action / per-service QoS question from RFC-0272.
- ROS 2 action and service documentation (cross-cite).

## Unresolved questions

1. **Cross-publisher / cross-subscriber QoS compatibility for actions / services.** Same as RFC-0272's cross-node concern; URML's manifest doesn't validate cross-side compatibility.
2. **Action discovery delay.** Some actions have discovery-overhead that operators want to limit; URML's manifest could declare an action-discovery-timeout. Future RFC.
3. **Service timeout declarations.** Service calls can timeout; URML's manifest could declare a default timeout per service pattern. Future RFC.

## Implementation plan

1. JSON Schema fragment extending RFC-0251's `rmw_options`.
2. Validator with five checks.
3. Conformance tests (five).
4. Reference-runtime per-action / per-service QoS-resolution layer.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (four-layer complexity, pattern-syntax overlap, verbose sub-QoS, runtime overhead).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0251 (parent), RFC-0265 + RFC-0272 (siblings).
- [x] CLAUDE.md compliance: substrate-neutrality preserved across action / service QoS planes.
