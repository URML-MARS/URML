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

# Compliance walkthrough — five minutes, three commands

A demo that shows what URML's compliance enforcement actually does. The same red-mug program from the manifesto, validated against three variants of the same robot's manifest: one fully US-compliant, one with a covered-foreign-country critical component, one with a vendor on the FCC Covered List. Then the `--no-policy` override.

Useful for: video demos, slide decks, technical conversations with regulated-procurement audiences, blog posts. The whole walkthrough fits on one screen at presentation zoom.

## Prerequisites

- URML installed (`pip install urml-validator`, or work from a checkout per [Tutorial 1](../tutorials/01-getting-started.md)).
- A terminal, `cd` into the URML repository root.

## The program — unchanged across the demo

```bash
cat examples/home/red-mug.urml.yaml
```

A six-line URML program: navigate to the kitchen, find a red mug, pick it up, hand it to the user. The same program from `MANIFESTO.md` §A Concrete Example. This program does not change across the rest of the walkthrough — what changes is the manifest the program is validated against.

## Scene 1 — the compliant deployment

```bash
urml validate examples/home/red-mug.urml.yaml \
    -m examples/home/red-mug.manifest.yaml \
    --profile home
```

Expected:

```
Validation passed: examples\home\red-mug.urml.yaml
```

The `red-mug.manifest.yaml` declares three critical components — drive controller (US), depth camera (US), claw servo (JP/US). The bundled URML default policy (which mirrors NDAA Section 889 / FY26, the FCC Covered List, etc.) accepts all of them. The validator has run five passes — argument typing, capability checks, safety envelope, variable bindings, and compliance policy — and the program is cleared for execution.

No `--policy` flag was passed; the bundled US-federal default policy was loaded automatically. That is the design: by default, URML enforces US federal procurement rules. Deployers outside the US opt out via `--policy <their_file.yaml>` or `--no-policy`.

## Scene 2 — a covered foreign component

Now swap to a manifest where the drive controller is declared as CN-origin. Same robot in every other respect; the program is unchanged.

```bash
urml validate examples/home/red-mug.urml.yaml \
    -m examples/home/red-mug.cn-critical.manifest.yaml \
    --profile home
```

Expected:

```
Validation failed: examples\home\red-mug.urml.yaml (2 error(s))

  ERROR [policy.country_denied] <manifest>/provenance/components/drive_controller
    field: country_of_origin
    Critical component from covered foreign country (NDAA Section 889 / FY26 NDAA).
    rule_id: critical_country_denylist
    policy_id: urml_us_federal_default
    component_id: drive_controller
    component_role: critical
    offending_field: country_of_origin
    offending_value: CN
    attestation_level: third_party_audited
    remediation_hint: swap_component
    denied_values: ['CN', 'RU', 'IR', 'KP']

  ERROR [policy.country_denied] <manifest>/provenance/components/drive_controller
    field: country_of_final_assembly
    [...]
```

The validator rejects the program with `policy.country_denied`. Two rules fire — one against `country_of_origin`, one against `country_of_final_assembly`, because the demo manifest declares both fields as CN. Each error carries a structured `detail` payload: the rule that fired, the policy that owns the rule, the offending component and field, the denied set, and a `remediation_hint` (`swap_component` — programs cannot fix hardware).

This is the load-bearing point: **the rejection happens before any actuator moves**. There is no runtime check that the deployer might forget to wire up; the validator is the gate, and a program that targets a non-compliant robot is rejected at validation time.

Note also: the `attestation_level: third_party_audited` line. The manifest claims its provenance is third-party-audited. The validator records this; it does not certify it. If the audit is fraudulent, that's a downstream legal problem, not URML's check.

## Scene 3 — a covered vendor

Swap to a manifest where the depth camera's vendor is `dji` — a string used here as a regulatory marker matching the FCC Covered List, not as a claim about specific hardware.

```bash
urml validate examples/home/red-mug.urml.yaml \
    -m examples/home/red-mug.dji-camera.manifest.yaml \
    --profile home
```

Expected:

```
Validation failed: examples\home\red-mug.urml.yaml (1 error(s))

  ERROR [policy.vendor_denied] <manifest>/provenance/components/depth_camera
    field: vendor
    Vendor named in the FCC Covered List, the DoD Chinese Military Companies list, or the American Security Robotics Act.
    rule_id: covered_vendor_denylist
    policy_id: urml_us_federal_default
    component_id: depth_camera
    component_role: critical
    offending_field: vendor
    offending_value: dji
    attestation_level: third_party_audited
    remediation_hint: swap_component
    denied_values: ['dji', 'autel', 'hesai', 'unitree']
```

Different rule, same shape. The covered-vendor list ships in the bundled default policy file; each entry traces to an enacted statute or final agency list (FCC's covered-equipment action effective 2025-12-23 added DJI and Autel; the FY26 NDAA §164 named Hesai; the American Security Robotics Act targets Unitree).

The mechanism is the same as the country-denylist rule: declared facts on the manifest are matched against a denylist; matches emit structured errors before execution.

## Scene 4 — the override

A deployer outside the US, or one with a specific exception (counterterrorism use; per ASRA §carve-outs), can disable Pass 5 entirely:

```bash
urml validate examples/home/red-mug.urml.yaml \
    -m examples/home/red-mug.cn-critical.manifest.yaml \
    --profile home \
    --no-policy
```

Expected:

```
Validation passed: examples\home\red-mug.urml.yaml
```

Same non-compliant manifest, accepted. `--no-policy` skips Pass 5 entirely. The four prior passes still run — argument typing, capability, envelope, bindings — so the program is still well-formed; only the compliance check is bypassed.

For non-US deployers who need their own jurisdiction's rules, the equivalent is `--policy <their_file.yaml>`:

```bash
urml validate examples/home/red-mug.urml.yaml \
    -m examples/home/red-mug.manifest.yaml \
    --profile home \
    --policy /path/to/eu-ai-act.yaml
```

URML supplies the mechanism. The rule set is a YAML file the deployer (or a third-party auditor) writes. The default ships pre-loaded with US federal rules; everything else is one flag away.

## What just happened

In 90 seconds and three commands you saw:

- The validator's fifth pass enforce a real regulatory regime on a real example.
- Structured errors carry enough detail for an LLM (or a human) to understand exactly what failed and why.
- The mechanism is generic; only the bundled defaults are US-specific.
- Override is a single flag.

The strategic posture behind this is in [RFC-0003](../rfcs/0003-us-alignment.md); the technical mechanism is in [RFC-0004](../rfcs/0004-compliance-policy.md); the normative policy file format is at [`spec/layer-1-hal/policy.md`](../../spec/layer-1-hal/policy.md).

## What this is NOT

A policy file passing the URML validator is not a legal compliance determination. The bundled default ships under Apache 2.0 forever per [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) item 7; audited and certified policy files carrying third-party legal attestation are a separate commercial surface (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) §What This Commitment Does Not Cover).

The walkthrough above is illustrative. Real deployments need real provenance attestations and counsel review.

## Files used in this walkthrough

- [`examples/home/red-mug.urml.yaml`](../../examples/home/red-mug.urml.yaml) — the URML program, unchanged across all scenes.
- [`examples/home/red-mug.manifest.yaml`](../../examples/home/red-mug.manifest.yaml) — the fully US-compliant manifest.
- [`examples/home/red-mug.cn-critical.manifest.yaml`](../../examples/home/red-mug.cn-critical.manifest.yaml) — the same manifest with `drive_controller` declared as CN-origin. Trips `policy.country_denied`.
- [`examples/home/red-mug.dji-camera.manifest.yaml`](../../examples/home/red-mug.dji-camera.manifest.yaml) — the same manifest with the camera vendor set to `dji`. Trips `policy.vendor_denied`.

All manifests use fictional vendor identifiers (`example_*`) for non-tripwire fields and real regulatory markers (ISO country codes, the literal vendor strings on the FCC Covered List) only where the rejection is the point being demonstrated. No claim about any real product is being made.

## Related reading

- [Tutorial 4 — Writing your own manifest](../tutorials/04-writing-your-own-manifest.md) §Exercise 6: declares hardware provenance for compliance checks.
- [`spec/layer-1-hal/policy.md`](../../spec/layer-1-hal/policy.md) — normative policy file format.
- [RFC-0003](../rfcs/0003-us-alignment.md) — why URML aligns with US federal regulation; the trade-offs accepted.
- [RFC-0004](../rfcs/0004-compliance-policy.md) — the technical mechanism, including the LLM-bridge revision short-circuit (`BridgePolicyViolation`).
