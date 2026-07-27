---
rfc: 0669
title: MCU firmware descriptor in the manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-07-20
updated: 2026-07-23
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

# RFC-0669: MCU firmware descriptor in the manifest

## Summary

RFC-0018 gave a non-mobile sensor/actuator node an honest capability shape
(`minimal_node`: what it senses, what it actuates). It does not say *what firmware
the node runs*. Two boards with the same LED and light sensor can run different
firmware series, different cores, different middleware, and different versions, and
that difference decides which command surface a runtime actually has. This RFC
proposes an optional Layer-1 `firmware` descriptor: a small, vendor-neutral
declaration of the firmware identity a node runs (series, core, version, software
components), so a manifest can distinguish those two boards and a runtime can bind
to the right surface.

The field set comes directly from a request-for-comment exchange with
STMicroelectronics engineers on
[STM32CubeF4#203](https://github.com/STMicroelectronics/STM32CubeF4/issues/203),
who spelled out what an STM32 firmware description should carry and argued it should
be **per-series**, not a single umbrella. This RFC generalizes their four fields to
any MCU vendor (STM32 is the motivating instance, not the only one) and files them
as a **Draft for maintainer decision**. It adds no primitive.

## Motivation

`minimal_node` (RFC-0018) answers "what does this board sense and actuate." It does
not answer "what is this board." For a classroom LED node that gap is tolerable. For
the professional and industrial MCU class it is not: which middleware stack is
present (a USB Core library vs an Eclipse USBX stack), which version of it, which
core the firmware was built for, and which firmware release the node runs all change
what a runtime can honestly dispatch. Today a manifest either omits that entirely or
smuggles it into free-text `description`, which the conformance suite cannot check.

The concrete driver is a real vendor's read of the problem. On
[STM32CubeF4#203](https://github.com/STMicroelectronics/STM32CubeF4/issues/203),
STMicroelectronics engineers, asked what a URML capability declaration should carry
for an STM32 firmware, answered with a specific list and a scope decision:

> A feature-based description of an STM32 firmware should indicate: the STM32 series
> (e.g. STM32F4, STM32WL); the core supported (e.g. CM0, CM0+, CM4, CM33); the
> firmware version; and the list of software components the firmware is made of
> (CMSIS, HAL-LL drivers, middleware). Engagement should be **per-series**: each
> firmware should have its own structured description, because the middleware a series
> offers (USB Core vs Eclipse USBX) and the version it pins drift per series and per
> release.

That is a clean, external specification for a manifest field URML did not have, from
the people who ship the firmware. Declining to model it would leave the largest
professional-MCU population describing its firmware identity in prose.

## Detailed design

An optional Layer-1 manifest block, vendor-neutral, additive:

```
firmware:
  series: <FirmwareToken>         # the MCU series, e.g. "STM32F4", "esp32s3", "nrf52"
  core: <FirmwareToken>           # the CPU core the firmware targets, e.g. "cortex-m4", "xtensa-lx7"
  version: <string>              # the firmware release, e.g. "1.28.0" (semver-ish, free string in v0.1)
  components:                    # the software components the firmware is built from
    - name: <FirmwareToken>      # e.g. "cmsis", "stm32f4xx-hal", "usbx"
      version: <string>          # optional; the component version if pinned
```

`extra: forbid`, as everywhere in Layer 1. The block is **declarative only**; it
introduces no primitive and gates nothing on its own in v0.1. It is a positive,
conformance-checkable statement of firmware identity.

`series`, `core`, and each component `name` are **firmware tokens** a runtime can
match on. They are NOT URML `Identifier`s (strict snake_case): these are third-party
vendor tokens URML does not own, so the charset admits the punctuation real MCU names
use, hyphens, dots, and plus (`^[A-Za-z0-9][A-Za-z0-9._+-]*$`), for example
`cortex-m0+`, `stm32f4xx-hal`, `esp32s3`. Mixed case is allowed so a vendor's own
spelling round-trips. `version` fields are free strings in v0.1 (a normative version
grammar is deferred, see Unresolved questions). The four fields map one-to-one onto
the ST engineers' list: series, core, firmware version, component list.

**Per-series is the manifest, not a field.** The ST recommendation that engagement be
per-series matches how URML already works: one manifest per target, not one umbrella
for a whole family. A `firmware` block therefore describes exactly one series-and-
release, and a family with several series is several manifests, not one manifest with
a list of series. This RFC records that as the intended usage, and the validator does
not try to represent a multi-series umbrella in a single block.

**Relationship to `minimal_node`.** `firmware` is orthogonal and composes with it: a
`minimal_node` says what the board senses and actuates, a `firmware` block says what
firmware identity it runs. `firmware` is not mutually exclusive with anything; a
mobile robot's compute board also runs firmware, though the motivating case is the
non-mobile node. A manifest may carry `firmware` with or without `minimal_node`.

### Substrate-neutrality (acid test)

The block must be declarable for a board with zero STM32 or ST content. It is: an
ESP32-S3 node declares `series: esp32s3`, `core: xtensa-lx7`, a version, and
`components: [{name: esp-idf, version: ...}]`; an nRF52 node declares `series: nrf52`,
`core: cortex-m4`, and its SDK components. No field names a vendor, an SDK, or a
toolchain. STM32 is the instance that surfaced the need, not a coupling.

### Spec changes

- **Layer 1**: add the optional `firmware` model + a spec section
  (`spec/layer-1-hal`, the section after RFC-0018's §2.17 `minimal_node`), with a
  normative note that a `firmware` block describes exactly one series-and-release and
  that a multi-series family is modeled as multiple manifests.
- No Layer 2/3/4 change. No primitive.

### Validator changes

Schema parse only, in v0.1. `series` and `core` are required non-empty firmware
tokens when `firmware` is present, and component entries have a non-empty `name`;
all of that is enforced by the model (required fields plus the firmware-token
constraint), so a violation surfaces as a Pass-1 schema error and no dedicated
validator pass is needed. Unlike `minimal_node`, `firmware` has no cross-block rule,
so there is no `_check_firmware`. A future Pass-2 rule (a runtime or policy that
requires a minimum firmware version, or that a named component be present) is
explicitly deferred, in the RFC-0011 / RFC-0018 declare-now/enforce-later staging.

### Reference runtime changes

None required. An MCU-facing runtime may optionally read `firmware` to choose its
command set (as `EmbeddedAdapter` already reads capabilities), but is not obligated
to in v0.1.

### Conformance suite changes

A `conformance/fixtures/educational/` (or a new `mcu/`) manifest-acceptance fixture
for a board carrying a `firmware` block plus a `minimal_node`, validator-only (no
`expected_execution`, the no-SDK pattern RFC-0018 reused), demonstrating both an
STM32-instance manifest and one non-STM32 manifest so the neutrality claim is a
tested fixture, not a promise.

## Backward compatibility

Fully compatible. Additive optional block; every existing manifest stays valid;
`manifest_version` stays `0.1`. The only constraint is on manifests that opt into
`firmware`. Pre-v1.0.

## Drawbacks

It adds manifest surface, and URML's bias is fewer fields, not more. A fair objection
is "put firmware identity in `provenance.components` and stop": those component
entries already carry an id and a vendor. But `provenance` is about supply-chain
attestation and country-of-origin for procurement policy, not about the runtime
firmware surface a command binds to; overloading it would conflate two separately
decidable concerns. A second drawback is version semantics: leaving `version` a free
string in v0.1 means the validator cannot compare versions, so a "require >= X" rule
has nothing to stand on until a version grammar is decided (deferred below). Third,
this block is most useful paired with a hardware descriptor keyed on the part number
(peripherals, packaging, pin/GPIO), which the ST engineers also asked for; scoping
that out (see Alternatives) means `firmware` alone is only half of what they
described.

## Alternatives considered

1. **Do nothing; keep firmware identity in `description` (status quo).** Rejected:
   free text is not conformance-checkable and cannot be matched by a runtime. It is
   the legitimate "do nothing in v0.1" option the maintainer may still pick.
2. **Reuse `provenance.components`.** Rejected: `provenance` models supply-chain
   attestation (role, vendor, country of origin/assembly, HBOM) for procurement
   policy, not the runtime firmware surface. Different purpose, different consumers.
3. **Model the whole ST proposal now, firmware plus a part-number hardware
   descriptor.** Deferred, not rejected. The hardware descriptor (peripherals and
   instance counts, package, pin and GPIO mapping) is a larger surface that overlaps
   with capabilities a manifest already implies, and adding it in the same RFC would
   bundle two separately decidable one-way-door decisions. This RFC proposes the
   firmware descriptor and leaves the hardware descriptor to a companion RFC, so each
   is decided on its own merits.
4. **A per-vendor firmware block (an `stm32` block).** Rejected: it would couple the
   manifest to one vendor and fail the substrate-neutrality acid test. The
   vendor-neutral `series`/`core`/`components` shape covers STM32, ESP32, nRF, RP2040,
   and future MCUs without a fork per vendor.

## Prior art

Board and firmware identification in constrained-device ecosystems: PlatformIO board
manifests (`platform`, `framework`, MCU + core fields), Zephyr devicetree and
board-level Kconfig, the Arduino boards.txt core/variant model, and CMSIS-Pack
device/component descriptions. URML-internal: RFC-0018 (`minimal_node`, the
capability half this identity half composes with), RFC-0017 (`set_output`, the verb
those nodes use), RFC-0006 (declare-an-abstract-capability precedent), RFC-0308
(micro-ROS, the MCU-transport tier this pairs with). External source: the
request-for-comment exchange with STMicroelectronics engineers on
[STM32CubeF4#203](https://github.com/STMicroelectronics/STM32CubeF4/issues/203).

## Unresolved questions

- Whether `version` and component `version` should stay free strings or adopt a
  normative grammar (semver, or a looser "comparable" rule) so a policy can require a
  minimum. Free string in v0.1; a grammar is the natural follow-on before any
  version-comparison rule.
- Whether `core` should be a free identifier or a controlled vocabulary of known
  cores; a controlled list is more checkable but needs maintenance as cores appear.
- Whether `components[].name` should reference a controlled component registry
  (checkable, but a maintenance burden and a neutrality risk) or stay free
  identifiers.
- The companion hardware descriptor keyed on the full part number (Alternative 3):
  whether it is worth its manifest surface, and if so whether it is one RFC with this
  one or a separate follow-on.

## Implementation note

### Shipped (Draft -> Implemented, 2026-07-23)

Landed as a Layer-1-only change, fully additive (every existing manifest stays
valid; `manifest_version` stays `0.1`):

- **Schema**: `Firmware` (`series`, `core` required; `version`, `components`
  optional) + `FirmwareComponent` (`name` required, `version` optional) +
  `CapabilityManifest.firmware`. A new `FirmwareToken` type in
  `schemas/common.py` (`^[A-Za-z0-9][A-Za-z0-9._+-]*$`, 1..64) carries the
  vendor-token charset, distinct from the strict snake_case `Identifier`. Spec:
  `spec/layer-1-hal/v0.2.0.md` §2.22.
- **Validator**: none. The block is self-contained (no cross-block rule), so
  required-field and token-charset violations surface as Pass-1 schema errors;
  there is no `_check_firmware`.
- **Conformance**: two manifest fixtures (`stm32_firmware_node`,
  `esp32_firmware_node`) registered in the conformance manifest map, plus two
  `conformance/fixtures/educational/` acceptance cases (STM32 instance +
  non-STM32 neutrality), validator-only (the RFC-0018 no-SDK pattern).
- **Tests**: `reference/validator/tests/test_firmware_descriptor.py` (18 cases:
  STM32 + ESP32 acceptance, required series/core, non-empty component name, the
  token charset admitting `cortex-m0+` / `stm32f4xx-hal` and rejecting whitespace,
  `extra: forbid`, optional version/components, full-manifest validation, and no
  false mutual-exclusion with `mobility`).

The companion part-number hardware descriptor (Alternative 3) stays a separate
follow-on; it is not part of this change.

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case (an external vendor's stated field list), not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks (nothing; additive).
- [x] If this RFC adds a Layer-2 primitive, both ROS-2 and non-ROS implementation sketches are present (substrate-neutrality acid test). Not applicable: this RFC adds no primitive; it is an optional Layer-1 manifest declaration. The neutrality acid test is applied to the *declaration* instead (STM32, ESP32, nRF all declarable).
- [x] The implementation note explains how this lands, not just what. Not applicable until Accepted; the Detailed design carries the spec/validator/conformance landing plan.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it (no vendor coupling, no substrate coupling, no primitive, additive and pre-v1.0).
