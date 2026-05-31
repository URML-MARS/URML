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

# Layer 1 — Hardware Abstraction

**Status:** Drafted. The normative specification is [`v0.1.0.md`](v0.1.0.md) — the capability-manifest schema (frames, locations, events, mobility, manipulation, perception, docking, outputs) plus the `provenance:` (RFC-0004) and `connectivity:` (RFC-0006) blocks. The Pass-5 compliance policy is specified in [`policy.md`](policy.md). This README is the orientation; `v0.1.0.md` is what a runtime must implement.

## Purpose

Layer 1 defines how a robot **declares what it can do**. A URML-compatible robot ships a *capability manifest* — a small, machine-readable document describing its mobility, manipulation, perception, declared coordinate frames, declared physical limits, and the safety envelope it operates within. The validator uses this manifest to decide whether a given URML program can be executed by this robot before any actuator moves.

Layer 1 is intentionally a thin layer **on top of existing standards**. URDF and SDF already describe kinematic and geometric structure; URML reuses them rather than reinventing. The Layer-1 contribution is the *capability layer above URDF* — the abstraction that lets a URML program ask "can this robot grasp?" without parsing kinematics.

## Boundaries

Layer 1 must **not** assume:

- A specific underlying robot operating system. The manifest is substrate-agnostic; a robot running ROS 2, PX4, AUTOSAR, OPC UA Robotics, or a vendor SDK can all declare the same capabilities the same way.
- That a robot's capabilities are static at runtime. The manifest declares *baseline* capabilities; runtime extensions (e.g., a gripper picks up a tool that extends its reach) are a separate concern, addressed at most by a small runtime-state extension.
- Sensor data, runtime state, or world-model contents. Those flow through the substrate, not the manifest.

Layer 1 must also **not** absorb concerns from adjacent layers:

- **From Layer 2:** what a primitive *does*. Layer 1 says the robot has a gripper; Layer 2 defines `grasp(...)`.
- **From Layer 3:** composition. Manifests describe atomic capability, not behavior.

## What the normative document specifies

[`v0.1.0.md`](v0.1.0.md) carries the manifest schema in full; the items below were the original drafting checklist (see `v0.1.0.md` §5 for the two — URDF cross-reference, envelope-schema folding — that the shipped schema deliberately does *not* implement):

- The capability manifest schema (YAML canonical; JSON-LD for tooling). Sections: mobility, manipulation, perception, frames, limits, safety envelope.
- The safety-envelope schema: declared maximums (velocity, payload, force), declared forbidden zones, declared required preconditions.
- **Hardware provenance** (see *Provenance and Compliance* below).
- The relationship to URDF/SDF: how a Layer-1 manifest references the URDF that describes the robot's structure.
- A worked example: the capability manifest for the v0.1 demo robot (likely a TurtleBot 4; see `docs/open-questions.md` Question 5).

## Provenance and Compliance

Added by [RFC-0004](../../docs/rfcs/0004-compliance-policy.md). The capability manifest carries an optional `provenance:` block declaring per-component hardware origin facts. The validator's Pass 5 evaluates a pluggable compliance policy against this block before any program is accepted for execution. The policy file format is specified in [`policy.md`](policy.md).

### When provenance is required

Provenance is *optional* on the manifest. A manifest without a `provenance:` block triggers no Pass 5 errors — policy enforcement is opt-in. URML's posture per [RFC-0003](../../docs/rfcs/0003-us-alignment.md): the default validator ships with US federal procurement rules active, but a manifest that does not opt into provenance is silently exempt. Deployments that need to *prove* compliance must declare provenance; deployments that don't have a regulatory frame may omit it.

### The `provenance:` block

```yaml
provenance:
  manifest_attestation: self_declared    # self_declared | third_party_audited | cryptographically_signed
  attestation_uri: null                  # optional URI to a signed attestation document
  components:
    - id: drive_controller               # ISO-style snake_case identifier
      role: critical                     # critical | non_critical | informational
      vendor: example_drive_vendor       # free-form machine-readable identifier
      country_of_origin: US              # ISO 3166-1 alpha-2; "unknown" allowed and meaningful
      country_of_final_assembly: US      # often differs from manufacture
      hbom_ref:                          # optional
        format: cyclonedx-1.7            # recommended; free string
        uri: ./hbom/drive_controller.cdx.json
        sha256: "<64-hex-char-integrity-hash>"
```

Field-by-field:

| Field | Type | Notes |
|---|---|---|
| `manifest_attestation` | enum | Who asserts the provenance is true. Policies may require a minimum level; the default US-federal policy warns on `self_declared` in v0.1 and is scheduled to error in v0.2. |
| `attestation_uri` | string \| null | Optional pointer to a signed attestation document. URML does not fetch this; it records the URI. |
| `components` | list | One entry per declared component. Empty list is allowed and means "nothing critical to attest." |
| `components[].id` | identifier | Snake_case identifier scoped to this manifest. |
| `components[].role` | enum | `critical` / `non_critical` / `informational`. The load-bearing selector for policies. |
| `components[].vendor` | string | Free string in v0.1. Future RFCs may add a registered-identifier dimension (DUNS, ROR). |
| `components[].country_of_origin` | string | ISO 3166-1 alpha-2 country code. The literal `unknown` is accepted and policies may treat it as failing or warn. |
| `components[].country_of_final_assembly` | string | Same shape; often differs from `country_of_origin`. NDAA-style rules check both. |
| `components[].hbom_ref` | object \| null | Reference to a Hardware Bill of Materials document. Opaque in v0.1 — URML records the URI and a SHA-256 integrity hash but does not parse SBOM content. |

### What URML does NOT do

- URML does **not** fetch the HBOM document. The validator records what the manifest declares.
- URML does **not** verify the integrity hash. A future RFC may add this; v0.1 treats the hash as a deployer-controlled commitment, not a check.
- URML does **not** certify the provenance. The `manifest_attestation` field surfaces the strength of the claim; the *correctness* of the claim is the declarer's responsibility, not URML's.
- The default policy file shipped with the validator is **not legal advice**. See [`policy.md`](policy.md) and [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) for the certified-policy commercial surface.

### Status

The `provenance:` block is part of the v0.1 schema (`manifest_version: "0.1"`) and is fully implemented in the reference validator. The accompanying policy enforcement specification is in [`policy.md`](policy.md); the strategic and technical decision history is in [RFC-0003](../../docs/rfcs/0003-us-alignment.md) and [RFC-0004](../../docs/rfcs/0004-compliance-policy.md).

## Connectivity (RFC-0006)

Added by [RFC-0006](../../docs/rfcs/0006-connectivity-and-link-loss.md). The capability manifest carries an optional `connectivity:` block declaring the abstract *link roles* the robot supports. Like `provenance:`, it is opt-in: a manifest without a `connectivity:` block, paired with an envelope that declares no link-loss rule, triggers no connectivity errors.

A link *role* is an abstraction — `command_link` (operator/supervisor → robot control), `telemetry_link` (robot → operator status), `peer_link` (robot ↔ robot; declared now, no behavioural semantics until a future multi-robot RFC), `payload_link` (bulk mission/sensor data). **The transport medium that carries a role — WiFi, 5G, LTE, RF, fibre — is Layer 0 and is deliberately not modelled by URML.** This is a hard boundary, not an omission: a manifest that named a radio would fail the substrate-neutrality acid test.

Each declared link carries abstract properties only: `required_for_operation`, `autonomous_when_lost`, an optional declared `max_outage_seconds` tolerance, and an ordered `assurance_class` (`best_effort` < `monitored` < `assured` < `safety_critical`). `assurance_class` is the reconciliation of "express the communications requirement as intent" without coupling to a medium: intent may depend on a link's *assurance*, never on its radio. The ordering is deliberate so a future regulatory rule (e.g. a beyond-visual-line-of-sight command-and-control assurance floor) can require `>= assured` additively; RFC-0006 itself ships no such rule.

The deployment-time counterpart — what the robot must *do* when a declared link is lost — lives in the safety envelope's `link_loss_policy`, not here. The validator (Pass 2 and Pass 3) statically rejects a policy whose action the manifest cannot satisfy; see [RFC-0006](../../docs/rfcs/0006-connectivity-and-link-loss.md) §Detailed design.

## Fleet roster (RFC-0286)

[RFC-0286](../../docs/rfcs/0286-multi-robot-fleet-addressing.md) adds the multi-robot analogue of the capability manifest: a `roster`. A roster gives each robot in a fleet a short, English-callable handle and points at that robot's **existing, unchanged** per-robot manifest:

```yaml
roster_version: "0.1"
members:
  - { name: courier, manifest: husky_amr }
  - { name: arm,     manifest: kawasaki_rs }
```

The roster does not nest or alter a manifest — it binds N already-valid manifests by name. The handle declared here (`courier`, `arm`) is what a Layer-3 `on:` scope and a `barrier:` node address. The roster is optional infrastructure: a single-robot program needs none. A fleet mission file is two YAML documents — the roster, then the program — and the multi-robot validator (`validate_fleet`) checks each member's program subtree against that member's manifest, plus the cross-robot rules (collision-free concurrency, `peer_link` for barriers). The roster activates the `peer_link` role this layer reserved under Connectivity above.

## Conformance points

The conformance suite (`/conformance/fixtures/`) tests:

- Every required field is present.
- Declared limits are internally consistent (e.g., declared `max_velocity` is non-negative and finite).
- The manifest's frame declarations are consistent with the referenced URDF.
- The validator correctly rejects programs that exceed declared capability or violate the safety envelope.

## Related documents

- [`/docs/architecture.md`](../../docs/architecture.md) §Layer 1.
- [`/docs/glossary.md`](../../docs/glossary.md) — capability manifest, frame, safety envelope.
- [`/spec/profiles/`](../profiles/) — each profile may declare additional manifest fields it requires.
