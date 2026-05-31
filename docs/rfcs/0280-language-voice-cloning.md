---
rfc: 0280
title: language.tts.voice_cloning — declaring voice-cloning intent in the Layer-1 manifest
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

# RFC-0280: `language.tts.voice_cloning` — voice-cloning declaration

## Summary

RFC-0260 declared `language.tts_engine_class` with `openvoice` (MyShell OpenVoice) as one allowed value. OpenVoice supports zero-shot voice cloning: given a few seconds of reference audio, the engine synthesizes new speech in that voice. URML's manifest currently has no place to declare voice-cloning intent or to attach consent / attribution metadata. Voice cloning has both operational and ethical implications (impersonation risk, consent requirements, jurisdiction-specific regulation). This RFC adds `language.tts.voice_cloning` sub-block with cloning-enabled flag, consent attestation, and source-voice reference declarations. Optional. Backward compatible.

The surface that demanded this RFC is RFC-0260 deferred-question on voice-cloning declaration.

## Motivation

Voice cloning is operationally common in robotics (consistent robot voice across fleet of robots), entertainment (game-character voicing), accessibility (preserving a user's voice when they lose speech), and customer experience (branded TTS voices). URML's manifest cannot today declare:

1. **Whether voice cloning is enabled.** A deployment using OpenVoice with cloning vs OpenVoice with stock voices runs very different operational risk.
2. **Consent attestation.** Cloning a voice without consent is unlawful in some jurisdictions (US BIPA, EU GDPR, California voice-print provisions). URML's manifest should declare consent posture.
3. **Source-voice provenance.** When cloning a specific voice (e.g., a CEO's voice for an enterprise robot), the source-audio identity should be documented.

Three concrete consequences of the gap:

1. **Federal-procurement audit is incomplete.** Federal-procurement deployments may need to attest that voice-cloning is disabled (DoD personnel-voice-impersonation concerns); URML's manifest currently can't declare.
2. **Ethical-deployment audit is impossible.** A manifest declaring `tts_engine_class: openvoice` doesn't say whether cloning is enabled; downstream audit can't tell.
3. **Jurisdiction-specific gating.** Some jurisdictions require explicit operator-side consent declaration; URML's manifest could surface the requirement at validate time.

## Detailed design

### Field shape

```yaml
language:                                    # block defined in RFC-0260
  tts_engine_class: openvoice
  engine_options:
    tts:
      voice_id: "hf://myshell-ai/OpenVoice@v2"   # from RFC-0277 hf:// scheme
      voice_cloning:                              # NEW — this RFC
        enabled: true
        consent:
          consent_obtained: true
          consent_attestation_url: https://example.org/voice-consent.signed
          consent_date: "2026-04-15"
          consent_jurisdiction: ["us_federal", "us_california", "eu_gdpr"]
        source_voice:
          source_audio_reference: hf://example_org/ceo_voice_samples@v1
          source_voice_identity: "Example Org CEO"
          source_audio_duration_sec: 90
        runtime_safeguards:
          watermarking_enabled: true
          synthetic_audio_disclosure: true
```

### Allowed values for `consent.consent_jurisdiction` (multi-select)

| Value | Description |
|---|---|
| `us_federal` | US federal law (BIPA-adjacent, voice-print regulations) |
| `us_california` | California-specific (CCPA, voice-print provisions) |
| `us_illinois` | Illinois BIPA (Biometric Information Privacy Act) |
| `us_texas` | Texas-specific provisions |
| `eu_gdpr` | EU GDPR Article 4 (biometric data classification) |
| `uk_ico` | UK ICO biometric guidance |
| `none_required` | Deployment is in a jurisdiction without specific voice-cloning consent requirements |
| `custom` | Other jurisdiction; document in note |

### Schema fragment (extending RFC-0260's engine_options.tts)

```jsonc
{
  "language": {
    "properties": {
      "engine_options": {
        "properties": {
          "tts": {
            "properties": {
              "voice_cloning": {
                "type": "object",
                "properties": {
                  "enabled": { "type": "boolean", "default": false },
                  "consent": {
                    "type": "object",
                    "properties": {
                      "consent_obtained": { "type": "boolean" },
                      "consent_attestation_url": { "type": "string" },
                      "consent_date": { "type": "string", "format": "date" },
                      "consent_jurisdiction": {
                        "type": "array",
                        "items": {
                          "enum": ["us_federal", "us_california", "us_illinois", "us_texas", "eu_gdpr", "uk_ico", "none_required", "custom"]
                        }
                      }
                    }
                  },
                  "source_voice": {
                    "type": "object",
                    "properties": {
                      "source_audio_reference": { "type": "string" },
                      "source_voice_identity": { "type": "string" },
                      "source_audio_duration_sec": { "type": "number" }
                    }
                  },
                  "runtime_safeguards": {
                    "type": "object",
                    "properties": {
                      "watermarking_enabled": { "type": "boolean" },
                      "synthetic_audio_disclosure": { "type": "boolean" }
                    }
                  }
                }
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

1. **Optional block.** Missing `voice_cloning` block defaults to `enabled: false`.
2. **`enabled: true` requires `consent` block.** When cloning is enabled, `consent.consent_obtained` and `consent.consent_jurisdiction` (at least one value) must be declared. Missing fails.
3. **`enabled: true` requires `source_voice.source_audio_reference`.** Cloning without source-voice declaration is incomplete.
4. **`consent_jurisdiction: us_illinois`** triggers a soft suggestion to declare `runtime_safeguards.watermarking_enabled: true` (Illinois BIPA recommends technical safeguards).
5. **`consent_jurisdiction: eu_gdpr`** triggers a soft suggestion to declare `runtime_safeguards.synthetic_audio_disclosure: true` (GDPR Article 22 + AI Act transparency obligations).
6. **`consent_attestation_url` opacity.** The validator does not fetch the URL. Documentation only.
7. **`--policy` enforcement.** When the default-policy file (RFC-0003) sets `forbid_voice_cloning: true`, manifests with `voice_cloning.enabled: true` fail validation. The field is unset for v0.1.
8. **Forward-compat.** Closed enums.

### Default-policy file additions (RFC-0003)

Optional `forbid_voice_cloning: true | false` field. Unset for v0.1. Federally-procured deployments may set the field via custom policy. When set:

- Any manifest with `language.engine_options.tts.voice_cloning.enabled: true` fails under `--policy`.

### Reference-runtime behavior

Reference runtimes read the voice_cloning block for startup-log diagnostics. When `runtime_safeguards.watermarking_enabled: true`, the runtime applies the TTS engine's watermarking output. When `runtime_safeguards.synthetic_audio_disclosure: true`, the runtime emits a synthetic-audio metadata flag on the output topic for downstream consumers to surface to end users.

### Conformance test additions

`conformance/tests/test_manifest_voice_cloning.py`:

1. Manifest without `voice_cloning` passes (defaults to disabled).
2. Manifest with `voice_cloning.enabled: true + consent (full) + source_voice` passes.
3. Manifest with `voice_cloning.enabled: true` and no consent block fails.
4. Manifest with `voice_cloning.enabled: true + consent_jurisdiction: [us_illinois]` and no `watermarking_enabled` passes with soft suggestion.
5. Manifest with `voice_cloning.enabled: true` and `--policy` against a policy with `forbid_voice_cloning: true` fails.

## Backward compatibility

Pre-v1.0. Additive. Existing manifests unchanged.

## Drawbacks

- **Consent attestation is operator-honesty-based.** URML cannot verify that the attestation_url points to a real signed document. The validator accepts the declaration; downstream audit is operator responsibility.
- **Jurisdiction enum is opinionated.** Six named jurisdictions cover the dominant cases; the long tail uses `custom`.
- **`runtime_safeguards` are TTS-engine-specific.** OpenVoice supports watermarking; other engines may not. The declaration is intent; the runtime applies only what the engine supports.
- **Voice-cloning ethics extend beyond consent.** Deepfake prevention, impersonation detection, abuse reporting are operational concerns the manifest doesn't address.

## Alternatives considered

1. **Skip the field; rely on TTS-engine-side configuration.** Rejected. Voice cloning is operationally important and ethically risky; URML's manifest should declare it.
2. **Use a single `voice_cloning_enabled: bool` field without consent / source_voice sub-fields.** Rejected. The sub-fields are operationally critical; without them the gate is just informational.
3. **Treat voice cloning as a separate `tts_engine_class: openvoice_cloned` value.** Rejected. The cloning is a configuration choice, not a separate engine class.
4. **Require `consent_attestation_url` to fetch and verify at validate time.** Rejected. URML's no-cloud invariant honors offline validation; future `urml verify` mode could fetch.

## Prior art

- [Move-12 RFC-0156 (MyShell OpenVoice outreach)](0156-openvoice-outreach.md) — outreach RFC that surfaced voice-cloning capability.
- [RFC-0260 (language engine classes)](0260-language-engine-classes.md) — parent Spec RFC; this RFC closes the voice-cloning deferral.
- [RFC-0277 (hf:// URI scheme)](0277-language-huggingface-uri-scheme.md) — sibling Spec RFC; voice_id uses the hf:// scheme.
- [RFC-0268 (deployment.commercial_use)](0268-deployment-commercial-use-flag.md) — sibling deployment-metadata RFC; voice cloning may have commercial-context-specific consent requirements.
- US BIPA (Illinois), EU GDPR Article 4, EU AI Act transparency obligations (cross-cite, not reproduce).

## Unresolved questions

1. **Multi-source voice cloning.** Some deployments blend multiple source voices; URML's manifest is single-source today.
2. **Consent withdrawal.** GDPR Article 7 right-to-withdraw consent is real; URML's manifest could declare consent-revocation handling. Future RFC.
3. **Voice-cloning detection metadata.** A future RFC could declare automatic-detection flags so downstream consumers can identify synthetic audio.

## Implementation plan

1. JSON Schema fragment extending RFC-0260's engine_options.tts.
2. Validator with seven checks (enabled-requires-consent, jurisdiction-specific safeguards, policy enforcement, etc.).
3. Conformance tests (five).
4. Default-policy file documentation update.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (operator-honesty, opinion jurisdiction enum, engine-specific safeguards, ethics beyond consent).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0260 (parent), RFC-0156 (outreach), RFC-0277 (hf:// URI), RFC-0268 (commercial flag).
- [x] CLAUDE.md compliance: federal-procurement narrative extends to voice-cloning gate; no-cloud invariant honored (URL not fetched); URML's neutrality across jurisdictions preserved (no opinion on which jurisdiction's law is correct; the manifest declares which jurisdictions apply).
