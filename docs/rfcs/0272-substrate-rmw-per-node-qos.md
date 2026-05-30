---
rfc: 0272
title: substrate.rmw_options.per_node_qos — per-node QoS profile declarations
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0272: `substrate.rmw_options.per_node_qos` — per-node QoS declarations

## Summary

RFC-0251 declared deployment-wide QoS; RFC-0265 added per-topic QoS overrides. Both note that some deployments need per-node QoS: one node uses reliable for all its topics, another uses best-effort for all its topics, regardless of topic name. This RFC closes that loop: adds `per_node_qos` to `rmw_options` as a list of per-node-pattern entries, defines validator behavior, and clarifies the interaction with topic-pattern overrides (RFC-0265). Optional. Backward compatible.

## Motivation

Real production deployments have nodes with characteristic QoS profiles:

- Sensor-driver nodes typically publish best-effort for high-rate data (camera, lidar, IMU).
- Command nodes typically subscribe reliable for safety-critical inputs (e/stop, watchdog).
- Visualization nodes typically subscribe best-effort (rviz, plotting).

Declaring QoS per-node is more natural and compact than declaring per-topic patterns for each topic the node publishes / subscribes. Three concrete consequences of the gap:

1. **Per-topic patterns are verbose for node-uniform deployments.** A camera-driver node publishing 12 topics needs 12 topic patterns; one per-node declaration handles all 12.
2. **Node-uniform QoS is operationally common.** Most node implementations are QoS-uniform within the node; declaring at node-level matches the implementation reality.
3. **Interaction with topic-pattern overrides needs clarity.** When a node has a per-node QoS profile AND a topic-pattern override matches one of its topics, which wins? This RFC defines the precedence rules.

## Detailed design

### Field shape

```yaml
substrate:
  class: ros2
  rmw_implementation: rmw_fastrtps_cpp
  rmw_options:
    qos_profile:                              # from RFC-0251 — deployment-wide
      reliability: reliable
      durability: volatile
      history: keep_last
      history_depth: 10
    qos_profile_overrides:                    # from RFC-0265 — per-topic
      - topic_pattern: "/sensors/**"
        qos_profile:
          reliability: best_effort
    per_node_qos:                             # NEW — this RFC
      - node_pattern: "camera_driver"
        qos_profile:
          reliability: best_effort
          history_depth: 5
      - node_pattern: "safety_watchdog"
        qos_profile:
          reliability: reliable
          history_depth: 1
      - node_pattern: "rviz*"                  # matches rviz2, rviz3 etc.
        qos_profile:
          reliability: best_effort
```

### Node-pattern syntax

URML adopts a glob-like syntax for node names (similar to topic patterns in RFC-0265 but without the `/` prefix and `**` semantics that are topic-specific):

- `camera_driver` — exact node-name match.
- `rviz*` — glob match (any node name starting with `rviz`).
- `/namespace1/*` — namespaced node names (single-segment under namespace).
- `/namespace2/**` — deep namespace match.

### Precedence between per-topic and per-node overrides

When a topic's QoS resolution needs to happen, the validator and runtime follow this precedence:

1. **Per-topic override matches** (RFC-0265 `qos_profile_overrides`). First-match wins among the list.
2. **Per-node override matches** (this RFC's `per_node_qos`). First-match wins among the list.
3. **Deployment-wide default** (`qos_profile` from RFC-0251).

If both per-topic and per-node would match, **per-topic wins**. The rationale: topic-pattern overrides target specific topics with specific requirements; per-node defaults express node-uniform behavior. The more-specific declaration wins.

### Schema fragment (extending RFC-0251's rmw_options)

```jsonc
{
  "substrate": {
    "properties": {
      "rmw_options": {
        "properties": {
          "per_node_qos": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["node_pattern", "qos_profile"],
              "properties": {
                "node_pattern": { "type": "string" },
                "qos_profile": { "$ref": "#/$defs/QosProfile" }
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

1. **Optional field.** Missing `per_node_qos` means the deployment uses deployment-wide + per-topic overrides only.
2. **Node-pattern syntax validation.** Patterns must be valid: `[a-zA-Z0-9_-]+` plus optional `*` wildcard, optional `/` namespace prefix.
3. **Per-node + per-topic precedence warning.** When a per-node pattern and a per-topic pattern could both apply to the same topic, the validator emits an informational note at validate time documenting the per-topic-wins precedence.
4. **Collision warning.** When multiple per-node patterns could match the same node name, the validator emits a warning surfacing the first-match resolution.
5. **`history: keep_last` requires `history_depth`** (RFC-0251 rule). Applies to each per-node entry.
6. **Forward-compat.** `QosProfile` schema from RFC-0251.

### Reference-runtime behavior

Reference runtimes, on topic creation, resolve QoS in the documented precedence order: per-topic override → per-node override → deployment-wide default. The match happens at topic-creation time; URML's runtime does not re-resolve at runtime.

### Conformance test additions

`conformance/tests/test_manifest_per_node_qos.py`:

1. Manifest without `per_node_qos` passes (optional).
2. Manifest with `per_node_qos: [{node_pattern: camera_driver, qos_profile.reliability: best_effort}]` passes.
3. Manifest with both per-topic and per-node patterns matching the same topic: per-topic wins; validator emits informational note.
4. Manifest with overlapping per-node patterns (`rviz*` + `rviz2`) passes with first-match warning.
5. Manifest with invalid node pattern (contains `:` or other illegal chars) fails.

## Backward compatibility

Pre-v1.0. Additive: existing manifests unchanged. New field extends `rmw_options`.

## Drawbacks

- **Three layers of QoS declaration (deployment-wide, per-topic, per-node) is operational complexity.** Operators reading a manifest must track precedence rules to predict the effective QoS for a topic. URML's discipline: the rules are documented; the validator surfaces collisions.
- **Node-pattern syntax is partially overlapping with topic-pattern (RFC-0265).** Two slightly-different glob syntaxes; the difference reflects the structural difference between topic names and node names but adds learning cost.
- **Per-topic-wins precedence is opinion.** Some operators may prefer per-node-wins (the node-uniform-default-with-topic-exceptions framing). URML picks per-topic-wins because more-specific-wins is the standard pattern in routing-style configs.
- **Runtime QoS-resolution overhead.** Each topic creation now does three pattern matches. The cost is small but real; production deployments with many topics should profile.

## Alternatives considered

1. **Skip per-node QoS; rely on per-topic overrides.** Rejected. Node-uniform QoS is operationally common and the per-topic-only model is verbose.
2. **Per-node-wins precedence.** Rejected. More-specific-wins (per-topic) is the standard pattern; per-node-wins would be surprising for operators familiar with firewall-style routing configs.
3. **Combine per-topic and per-node into a single override list with a `target_type` field.** Rejected. The two are structurally different concerns and benefit from separate lists for readability.
4. **Treat per-node QoS as a node-launch-config concern outside URML's manifest.** Rejected. URML's discipline: the manifest is the contract; deferring to launch config hides the structure.

## Prior art

- [RFC-0251 (substrate.rmw_implementation)](0251-substrate-rmw-implementation.md) — parent Spec RFC; deployment-wide QoS.
- [RFC-0265 (qos_profile_overrides)](0265-substrate-rmw-qos-overrides.md) — sibling Spec RFC; per-topic QoS overrides. This RFC closes the deferred per-node-QoS question from RFC-0265.
- ROS 2 QoS documentation (cross-cite).

## Unresolved questions

1. **Per-action / per-service QoS declarations.** ROS 2 services and actions have their own QoS surfaces; URML's manifest currently covers only topics. Future RFC.
2. **Cross-node QoS validation.** If publisher node has `reliability: best_effort` and subscriber node has `reliability: reliable`, the QoS is incompatible. URML's manifest can declare both but doesn't validate the compatibility; future RFC.
3. **Namespace-wide QoS.** Some deployments want all topics under `/sensors/` to use best_effort regardless of node. URML's per-topic patterns (RFC-0265) cover this case; declaring under per-node would be a different shape.

## Implementation plan

1. JSON Schema fragment.
2. Validator with node-pattern syntax + precedence rules + collision warnings.
3. Conformance tests (five).
4. Reference-runtime QoS-resolution layer.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (three-layer complexity, partially-overlapping syntaxes, opinion-based precedence, runtime overhead).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0251 (parent) + RFC-0265 (sibling).
- [x] CLAUDE.md compliance: substrate-neutrality preserved (per-node QoS pattern is RMW-independent); enum closure preserved.
