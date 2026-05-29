---
rfc: 0230
title: OpenBCI / BrainFlow (brain-computer-interface intent input) integration, request for comment from BrainFlow and OpenBCI maintainers
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

# RFC-0230: OpenBCI / BrainFlow (brain-computer-interface intent input) integration

## Summary

URML does not yet model a non-language intent input. This RFC documents how a brain-computer-interface (BCI) intent signal, delivered through [`brainflow-dev/brainflow`](https://github.com/brainflow-dev/brainflow) (MIT) from OpenBCI hardware, could feed URML's behavior layer as an **alternative intent input** beside the Layer-4 natural-language path, and **requests review and feedback from the BrainFlow and OpenBCI maintainers**. No spec change.

**This is a Move-18 frame-break RFC, and the most exploratory of the batch.** The reframe: URML's job is to turn an intent into verified, safe robot motion. Natural language is one source of intent. A BCI-classified intent is another, and it matters most for the assistive-robotics users who cannot use the language path. This RFC is honest that the mapping is an input-bridge, not a runtime adapter.

## Motivation

BrainFlow is a permissively-licensed, cross-platform SDK that delivers a uniform data stream from many biosignal boards, including OpenBCI's. A downstream classifier turns that stream into discrete intent events (for example: "select," "confirm," "left," "stop"). Repo at [`brainflow-dev/brainflow`](https://github.com/brainflow-dev/brainflow) (MIT, 1.7k stars, Issues enabled, last commit 2026-05-22, **not archived**). OpenBCI is the US open-hardware company whose boards BrainFlow supports.

URML benefits from documenting this bridge because:

1. **Intent has more than one source.** URML's Layer 4 assumes natural language. The accessibility case (a user who drives a robot through a BCI rather than speech or text) needs intent to enter at the behavior layer from a non-language source. Documenting that pathway widens the language without changing it.
2. **URML's verification boundary is exactly what a BCI pipeline lacks.** A classified intent firing an unverified robot action is a safety problem. URML validates intent against the capability manifest and safety envelope before execution. URML is the safe action layer a BCI front-end can sit on top of.
3. **It extends the accessibility line URML already opened.** RFC-0079 (Open Bionics) put assistive robotics in scope. A BCI intent input is the upstream half of the same story.

## Detailed design

### The input-bridge, stated plainly

URML does **not** decode EEG and does not classify neural signals. That stays in the BrainFlow-based pipeline. The bridge is narrow:

```
OpenBCI board --> BrainFlow stream --> (user's classifier) --> discrete intent label --> URML behavior trigger --> validate --> execute
```

URML consumes a discrete intent label and maps it to a URML behavior (a named Layer-3 composition) or a Layer-4 intent, then runs its normal validate-then-execute path. This mirrors how speech-to-text (RFC-0153 Whisper and the Move-12 inputs) feeds Layer 4: the recognizer produces a token, URML does the rest. The BCI is the non-verbal analog of the microphone.

### Mapping shape (planned `bci_intent_input.yaml` example)

| URML concept | Maps to BCI / BrainFlow concept |
|---|---|
| Layer-4 intent source | A discrete intent label emitted by the BrainFlow-fed classifier |
| Layer-3 behavior trigger | The named behavior a given intent label invokes |
| Perception `Sensor` (optional) | A BCI device declared with `measurement_type: custom` (no `bci` / `neural` type in v0.1) |
| Verification boundary | Unchanged: URML validates the triggered behavior against the manifest and safety envelope |

### What URML v0.1 does not yet express

1. **A non-language intent-input source at Layer 4.** Layer 4 is specified as natural language. There is no declared notion of a discrete-label intent source. Spec RFC queued.
2. **A neural / BCI sensor `measurement_type`.** URML's `Sensor.measurement_type` enum has `speech` but no `bci` / `neural` entry. A BCI device maps to `custom` today.
3. **Confidence-gated intent.** A BCI classifier emits a confidence; URML has no field to require a confidence threshold before a behavior fires. This is a real safety-relevant gap for this input class.

### Compatibility notes

- **Engagement repo.** [`brainflow-dev/brainflow`](https://github.com/brainflow-dev/brainflow) — MIT, 1.7k stars, Issues enabled, last commit 2026-05-22, **not archived**. The vendor-neutral SDK that OpenBCI hardware (and many other boards) use.
- **Hardware org.** [`OpenBCI`](https://github.com/OpenBCI) — US open-hardware company; `OpenBCI_GUI` is MIT and active. (`pyOpenBCI` is archived under `openbci-archive`; BrainFlow is its living successor and the correct engagement surface.)
- **Origin.** BrainFlow is community open-source; OpenBCI is US-domiciled. Passes US-federal default policy (MIT OSS, no covered-list vendor).
- **License fit.** MIT composes cleanly with URML's Apache-2.0 stance. No GPL boundary in this bridge.
- **Maintainer signal.** BrainFlow is actively maintained with a broad board-support matrix and a community Slack.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; a non-language intent-input source + a `bci` / `neural` sensor `measurement_type` + confidence-gated intent are queued Spec RFCs.
- Reference runtime: a future intent-input bridge (BrainFlow classifier output to a URML behavior trigger) is a candidate. No code in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Weakest adapter story of the batch, by design.** This is an input-bridge, not a substrate adapter. URML does not run on a BCI and does not classify signals. The RFC should not be read as claiming a runtime.
- **Multiple Spec-RFC prerequisites** (non-language intent source, BCI sensor type, confidence gating).
- **Safety surface is real.** A misclassified intent firing a robot action is exactly the failure URML's validator exists to bound, but confidence-gated intent is not yet expressible, so the safety story is incomplete until that Spec RFC lands.
- **Two-party engagement.** The SDK (BrainFlow) and the hardware org (OpenBCI) are different maintainers; the conversation may split.

## Alternatives considered

1. **Engage OpenBCI hardware repos directly instead of BrainFlow.** Rejected as the primary surface. BrainFlow is the living, MIT-licensed, vendor-neutral SDK and the natural integration boundary; `pyOpenBCI` is archived. OpenBCI is cross-referenced, not ignored.
2. **Fold BCI into the Move-12 speech / input work.** Rejected. Speech feeds the natural-language grammar; a BCI emits discrete non-verbal labels. They are sibling intent sources but not the same input class, and conflating them would misstate both.
3. **Wait until URML specifies non-language intent inputs before engaging.** Rejected. The bridge is worth surfacing to the maintainers now precisely so the queued Spec RFC is shaped by their feedback rather than guessed.

## Prior art

- [`brainflow-dev/brainflow`](https://github.com/brainflow-dev/brainflow) — the upstream SDK.
- [RFC-0079 (Open Bionics)](0079-open-bionics-outreach.md) — the accessibility / assistive-robotics line this RFC extends upstream.
- [RFC-0153 (Whisper)](0153-whisper-outreach.md) — the speech-to-Layer-4 input precedent; a BCI is the non-verbal analog.
- [RFC-0227 (Klipper)](0227-klipper-outreach.md), [RFC-0228 (WPILib)](0228-wpilib-outreach.md), [RFC-0229 (Crazyflie)](0229-crazyflie-outreach.md) — sibling Move-18 frame-break RFCs.

## Unresolved questions

For the BrainFlow and OpenBCI maintainers:

1. **Bridge boundary.** Is "BrainFlow stream plus the user's classifier emits a discrete intent label, URML consumes the label" the right boundary, or would you expect URML to engage a different layer of the pipeline?
2. **Intent-label contract.** Is there a conventional shape for classified-intent events in BrainFlow-based projects that URML should map to, rather than inventing one?
3. **Confidence gating.** A classifier emits a confidence. Should URML require a per-intent confidence threshold before a behavior fires? This is the safety-relevant question.
4. **Sensor declaration.** Should a BCI device be declared in URML's manifest at all (as a `bci` / `neural` sensor type), or is it purely an input front-end that never appears in the robot's capability manifest?
5. **Accessibility framing.** Does the assistive-robotics framing match how your users actually drive robots, or is the real usage pattern different?
6. **Two-party scope.** Should URML engage BrainFlow (the SDK) and OpenBCI (the hardware) separately, or is one the right entry point?
7. **Bridge home and conformance.** URML repo (an intent-input bridge), a BrainFlow / OpenBCI example, or neither? Would either project consider a link to URML once a working bridge ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported, no obligation.)
8. **Anything else.**

## Implementation note

RFC-0230 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## How to respond

`brainflow-dev/brainflow` has Issues enabled and an active community Slack; OpenBCI has a community forum. URML's planned channel: a single GitHub Issue on `brainflow-dev/brainflow` (labelled `question`) pointing to this RFC, with OpenBCI cross-referenced. If a maintainer prefers Slack, the forum, or human-only correspondence, that preference is welcome and URML will route to it.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (BrainFlow MIT, 1.7k stars [1692], Issues enabled, last commit 2026-05-22, isArchived: false; pyOpenBCI confirmed archived and dropped).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (input-bridge not a runtime, Spec-RFC prerequisites, incomplete safety story until confidence gating, two-party engagement).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: BrainFlow community OSS (MIT), OpenBCI US-domiciled; default policy passes.
- [x] CLAUDE.md compliance check passed.
