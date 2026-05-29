---
rfc: 0265
title: substrate.rmw_options.qos_profile_overrides — per-topic QoS profile overrides in the Layer-1 manifest
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

# RFC-0265: `substrate.rmw_options.qos_profile_overrides` — per-topic QoS overrides

## Summary

RFC-0251 declared deployment-wide QoS via `substrate.rmw_options.qos_profile`. The unresolved-questions section of RFC-0251 flagged per-topic QoS overrides as future work: ROS 2 supports per-topic QoS profiles, and production deployments routinely use them (sensor topics best-effort, command topics reliable). This RFC closes that deferred question by adding `qos_profile_overrides` to `rmw_options` as a list of per-topic-pattern entries. Optional. Backward compatible.

## Motivation

ROS 2's QoS model is per-topic by design. A camera-image topic uses best-effort + keep-last (large messages, drop OK); a velocity-command topic uses reliable + keep-last 1 (small messages, no drops); a transient-local topic uses transient-local durability (late subscribers see the last state).

RFC-0251 covers the deployment-wide default; per-topic overrides are the missing piece. Three concrete consequences of the gap:

1. **Deployment-wide QoS is wrong for any non-trivial deployment.** Production deployments need per-topic overrides; a manifest declaring only the deployment-wide default misrepresents real configuration.
2. **Validator can't reason about per-topic QoS.** URML programs that depend on transient-local durability for state recovery have no manifest declaration to validate against.
3. **Override-pattern syntax matters.** ROS 2 supports topic-name globbing (`/sensors/*` for all sensor topics); URML's manifest should adopt the same pattern.

## Detailed design

### Field shape

```yaml
substrate:
  class: ros2
  rmw_implementation: rmw_fastrtps_cpp
  rmw_options:
    qos_profile:                              # from RFC-0251 — deployment-wide default
      reliability: reliable
      durability: volatile
      history: keep_last
      history_depth: 10
    qos_profile_overrides:                    # NEW — this RFC
      - topic_pattern: "/sensors/**"
        qos_profile:
          reliability: best_effort
          history_depth: 5
      - topic_pattern: "/cmd_vel"
        qos_profile:
          reliability: reliable
          history_depth: 1
      - topic_pattern: "/robot_description"
        qos_profile:
          durability: transient_local
          history: keep_last
          history_depth: 1
```

### Topic-pattern syntax

URML adopts the standard ROS 2 topic-glob syntax:

- `/exact/topic` matches one specific topic.
- `/prefix/*` matches one segment under the prefix.
- `/prefix/**` matches any depth under the prefix.
- Patterns are matched in declaration order; first match wins.

### Schema fragment (extending RFC-0251's rmw_options)

```jsonc
{
  "substrate": {
    "properties": {
      "rmw_options": {
        "properties": {
          "qos_profile_overrides": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["topic_pattern", "qos_profile"],
              "properties": {
                "topic_pattern": { "type": "string" },
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

The `QosProfile` schema is reused from RFC-0251 with all fields optional in the override case (an override may partially-override the deployment-wide default by setting only the fields that differ).

### Validator behavior

1. **Optional field.** Missing `qos_profile_overrides` means the deployment uses only the deployment-wide `qos_profile`.
2. **Topic-pattern syntax validation.** Patterns are validated as valid ROS 2 topic-glob strings: leading `/`, segment characters `[a-zA-Z0-9_-]+`, optional `*` or `**` wildcards.
3. **Partial-override merge semantics.** When a topic matches an override pattern, the override fields merge into the deployment-wide default. Fields not declared in the override inherit from the default.
4. **First-match wins.** When multiple patterns could match a topic, the validator emits a warning at validate time noting the pattern collision and confirms the first-match resolution.
5. **`history: keep_last` requires `history_depth`** (RFC-0251 rule). The rule applies to each override individually.
6. **Forward-compat.** Closed `QosProfile` schema from RFC-0251.

### Reference-runtime behavior

Reference runtimes read `qos_profile_overrides` and, on topic creation, match the topic name against the override patterns. The first matching pattern's merged QoS profile is applied. URML's runtime does not re-evaluate at runtime; the match is at topic-creation time only.

### Conformance test additions

`conformance/tests/test_manifest_qos_overrides.py`:

1. Manifest without `qos_profile_overrides` passes (optional).
2. Manifest with override for `/cmd_vel` topic passes; merge semantics verified.
3. Manifest with overlapping patterns (`/sensors/*` + `/sensors/lidar`) passes with first-match warning.
4. Manifest with invalid topic pattern (`/sensors/(.*)/` — non-glob characters) fails.
5. Manifest with override declaring `history: keep_last` without `history_depth` fails.

## Backward compatibility

Pre-v1.0. Additive: existing manifests with only deployment-wide QoS unchanged. New field extends `rmw_options`.

## Drawbacks

- **First-match-wins ordering is declaration-dependent.** Two manifests with the same overrides in different orders may behave differently. URML's discipline is that ordering matters; the warning surfaces collisions.
- **Glob syntax is partial.** ROS 2 supports more elaborate matching (named topic remap, parameter substitution) that URML's manifest doesn't capture. The simple glob shape is sufficient for v0.1.
- **Per-topic QoS validation is partial.** URML validates the override profile is well-formed; the validator does not check that the actual topic exists in the deployment. Topic-existence check is a runtime concern.
- **Override-merge semantics adds validator complexity.** Each topic-creation in the runtime requires matching + merging logic.

## Alternatives considered

1. **Skip per-topic overrides; rely on substrate-side configuration files.** Rejected. URML's discipline is that the manifest is the contract; substrate-side configs hide the structure.
2. **Use a flat list `qos_profiles` rather than `default + overrides`.** Rejected. Inheritance from the default keeps the manifest compact; deployments typically override 3-5 topics, not enumerate every topic.
3. **Last-match-wins instead of first-match.** Rejected. First-match is more common in routing-style configs (firewall rules, ROS 2 topic remap precedent).
4. **Per-topic regex instead of glob.** Rejected. Regex is more powerful but harder for operators to read; glob is the ROS 2-side convention.

## Prior art

- [RFC-0251 (substrate.rmw_implementation)](0251-substrate-rmw-implementation.md) — parent Spec RFC; this RFC closes the deferred per-topic-QoS question.
- [Move-16 RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — surfaced QoS as a manifest concern.
- ROS 2 QoS documentation (cross-cite, not reproduce).

## Unresolved questions

1. **Per-node QoS overrides.** Some deployments need per-node QoS (one node uses reliable for everything; another uses best-effort). URML's manifest is per-topic today; per-node is a future RFC.
2. **DDS QoS policies beyond the basic set.** RFC-0251 covers reliability / durability / history / deadline / lifespan. Less-common policies (liveliness, resource_limits) are not yet in the schema. Future RFC.
3. **Cross-RMW QoS portability.** Fast DDS and Cyclone DDS interpret some corner-case QoS combinations differently. URML's manifest declares; the cross-RMW compatibility is a substrate-side concern.

## Implementation plan

1. JSON Schema fragment extending RFC-0251's `rmw_options`.
2. Validator with topic-pattern syntax + first-match warning + merge semantics.
3. Conformance tests (five).
4. Reference-runtime topic-creation override matching.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (declaration-order dependency, partial glob, partial validation, complexity).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0251 (parent), Move-16 RFC-0200.
- [x] CLAUDE.md compliance: substrate-neutrality preserved (per-topic-QoS pattern is RMW-independent).
