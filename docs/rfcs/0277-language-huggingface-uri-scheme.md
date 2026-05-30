---
rfc: 0277
title: hf:// URI scheme — Hugging Face model identity convention for the Layer-1 manifest
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

# RFC-0277: `hf://` URI scheme — Hugging Face model identity convention

## Summary

URML's manifest references models in several places: `language.engine_options.stt.model_size` (RFC-0260), `language.engine_options.tts.voice_id` (RFC-0260), `orchestration.framework_options.model_id` (RFC-0261), `engine_options.translation.target_languages` indirectly via model selection. Many of these models live on Hugging Face Hub. URML's manifest currently has no convention for naming Hugging Face-hosted models: some manifests use bare model names (`whisper-base`), others use full Hub paths (`openai/whisper-base`), others repository URLs. This RFC defines the canonical `hf://` URI scheme, with revision pinning, license attestation, and license-class declaration, and updates four prior Spec RFCs (0260, 0261, 0262, 0276) to use it. Optional. Backward compatible.

The surface that demanded this RFC is Move-12 RFC-0157 (Helsinki-NLP OPUS-MT-train outreach), which surfaced the Hugging Face URI convention as a manifest-level concern.

## Motivation

Hugging Face Hub is the dominant distribution surface for open-source ML models that URML's language engines (RFC-0260), orchestration frameworks (RFC-0261), and licensing block (RFC-0262) reference. URML's manifest needs a canonical way to declare:

1. **Model identity.** Org + model name + revision (commit SHA or tag).
2. **License attestation.** The model's license at the declared revision (model licenses change over time; pinning matters).
3. **Provenance link.** A pointer back to the Hugging Face Hub model card for audit.

Three concrete consequences of the gap:

1. **Manifest references drift.** A manifest declaring `model_id: whisper-base` is ambiguous (which org? which revision? which license?).
2. **Federal-procurement narrative is incomplete.** RFC-0262 declares license at the component level; URML's manifest needs a way to attach license attestation to specific model identities.
3. **Reproducibility is undermined.** Without revision pinning, a manifest can't reproduce a deployment three months later if the model upstream changes.

## Detailed design

### URI scheme

```
hf://<org>/<model>[@<revision>][?<query>]
```

- **`<org>`**: Hugging Face organization or username (e.g., `openai`, `Helsinki-NLP`, `meta-llama`).
- **`<model>`**: Model name (e.g., `whisper-base`, `opus-mt-en-de`).
- **`<revision>`** (optional): Git revision (commit SHA, tag, or branch name). Defaults to `main` (the default branch) if omitted; URML's validator emits a warning when the revision is omitted (un-pinned manifests are non-reproducible).
- **`<query>`** (optional): Query-string-style metadata. Reserved keys: `license=<spdx>`, `attestation=<url>`, `mirror=<url>`. URML's validator parses known keys and passes unknown keys through.

### Examples

```yaml
language:
  engine_options:
    stt:
      model_id: "hf://openai/whisper-base@v2.0?license=mit"
    translation:
      model_id: "hf://Helsinki-NLP/opus-mt-en-de@9a4f8b2?license=cc_by_4_0"
    tts:
      voice_id: "hf://myshell-ai/OpenVoice@e5d3c1a?license=mit"

orchestration:
  framework_options:
    model_id: "hf://meta-llama/Llama-3.1-70B-Instruct@v1.0?license=llama_3_1_community"
```

### Schema fragment (extending Layer-1 model-reference fields)

URML's existing model-reference fields (`model_id`, `voice_id`, etc.) become `string` typed with format hints. The validator parses the string against the `hf://` scheme when it matches, and treats it as opaque otherwise.

```jsonc
{
  "$defs": {
    "ModelReference": {
      "type": "string",
      "pattern": "^(hf:\\/\\/[a-zA-Z0-9._-]+\\/[a-zA-Z0-9._-]+(@[a-zA-Z0-9._-]+)?(\\?[a-zA-Z0-9=&_:.,\\/-]+)?|[a-zA-Z0-9._-]+|\\/.+)$"
    }
  }
}
```

The pattern accepts:
- `hf://` scheme URIs (validated against the scheme).
- Bare model names (legacy / backward-compat).
- Filesystem paths (for local model deployments).

### Allowed values for `license` query parameter

The license value uses URML's RFC-0262 license enum (SPDX-style identifiers: `apache_2_0`, `mit`, `cc_by_4_0`, `cc_by_nc_4_0`, `gpl_3_0`, `agpl_3_0`, `lgpl_3_0`, `bsd_3_clause`, `epl_2_0`, `mpl_2_0`, `unknown`, plus model-specific license identifiers like `llama_3_1_community`, `gemma_terms`, `qwen_research_license`).

### Validator behavior

1. **`hf://` scheme parsing.** When `model_id` (or sibling field) starts with `hf://`, validator parses the URI and validates org / model / revision / query parameters.
2. **Revision-pinning warning.** When a `hf://` URI omits the `@<revision>` part, the validator emits a warning (un-pinned manifests are non-reproducible).
3. **License-query cross-check with RFC-0262.** When `?license=` is set and the deployment also has a `licensing.components[]` entry for the model, the validator cross-checks consistency. Mismatch emits a warning.
4. **`mirror` query parameter.** When `?mirror=<url>` is set, the URL is documentation; URML's validator does not fetch the mirror. Future RFC could add offline-fetch verification.
5. **Bare model name backward-compat.** Bare model names (no `hf://`) continue to validate but emit a soft suggestion recommending the `hf://` scheme for explicit identity.
6. **Forward-compat.** The pattern accepts future scheme additions (e.g., `local://`, `s3://`) by not failing on unknown schemes; the validator just doesn't parse them.

### Reference-runtime behavior

Reference runtimes parse the `hf://` URI to resolve the model identity. The runtime composes against the Hugging Face Hub client (`huggingface_hub` Python library) to download the model at the declared revision. The download uses URML's existing offline-cache discipline; the runtime does not fetch at runtime if the model is already in the local cache.

### Conformance test additions

`conformance/tests/test_manifest_hf_uri.py`:

1. Manifest with `model_id: "hf://openai/whisper-base@v2.0"` passes.
2. Manifest with `model_id: "hf://openai/whisper-base"` (no revision) passes with warning.
3. Manifest with `model_id: "whisper-base"` (bare name) passes with soft suggestion.
4. Manifest with `model_id: "hf://openai/whisper-base?license=mit"` and `licensing.components[{name: whisper-base, license: gpl_3_0}]` passes with cross-check warning.
5. Manifest with `model_id: "hf://invalid/path with spaces"` fails (invalid URI characters).

## Backward compatibility

Pre-v1.0. Additive: bare model names continue to validate. `hf://` is recommended but not required.

## Drawbacks

- **`hf://` is Hugging Face-specific.** URML's manifest gains an opinion on Hugging Face as the canonical hosting surface. Other model hubs (Replicate, Modal, ONNX Model Zoo, vendor-specific) would need sibling URI schemes; this RFC scopes only the dominant case.
- **Revision-pinning warning is soft.** A maintainer who omits the revision gets a warning; the manifest still validates. The discipline is documentation, not enforcement.
- **Query-parameter convention is novel for URML.** URI query strings carry license + mirror + attestation metadata; the syntax is established (URL query strings) but URML's prior Spec RFCs used YAML sub-fields. The asymmetry is intentional: model identity is a single string with embedded metadata; YAML sub-fields would inflate the schema.
- **No verification of upstream model license against query parameter.** URML's validator parses the declared license but doesn't fetch Hugging Face Hub to verify it matches the actual model license. Future offline-verification mode could close this gap.

## Alternatives considered

1. **Use YAML sub-fields per model reference instead of URI scheme.** Rejected. Inline strings work better for model IDs (one-line manifest entries); YAML sub-fields would require expanding every model reference into a nested object.
2. **Adopt OCI artifact-registry scheme (`oci://`) instead.** Rejected for now. Hugging Face Hub is the dominant case; OCI adoption for models is emerging but not yet standard. Future RFC if OCI model artifacts become dominant.
3. **Standardize across multiple hubs (Replicate, Modal) in one RFC.** Rejected. Hugging Face is the dominant case; sibling hubs are future RFCs as their adoption surfaces in URML outreach.
4. **Make `hf://` required (no bare-name backward-compat).** Rejected. Existing manifests must continue to validate; soft suggestion is the right strength.

## Prior art

- [Move-12 RFC-0157 (Helsinki-NLP OPUS-MT-train outreach)](0157-opus-mt-train-outreach.md) — the outreach RFC that surfaced this convention.
- [RFC-0260 (language engine classes)](0260-language-engine-classes.md), [RFC-0261 (orchestration.framework)](0261-orchestration-framework.md), [RFC-0276 (wake-word substrate)](0276-language-wake-word-substrate.md) — sibling Spec RFCs whose model-reference fields adopt this convention.
- [RFC-0262 (licensing.boundary)](0262-licensing-boundary.md) — sibling Spec RFC; license_query parameter cross-references the licensing.components[] entries.
- Hugging Face Hub URL conventions (cross-cite, not reproduce).

## Unresolved questions

1. **Local-filesystem URI scheme.** A `file:///etc/urml/models/whisper-base` URI for air-gapped deployments. Future RFC.
2. **Model-card attestation declaration.** When the `?attestation=` query parameter is set, what format is the attestation (signed manifest, in-toto attestation, raw URL)? Future RFC.
3. **Multi-file model references.** Some models ship across multiple files (e.g., split safetensors); URML's manifest treats them as one identity. Future RFC.

## Implementation plan

1. JSON Schema fragment for the URI pattern.
2. Validator URI-parsing layer.
3. Conformance tests (five).
4. Update example manifests to use `hf://` where applicable.
5. Update RFCs 0260 / 0261 / 0276 to reference this RFC.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (HF-specific opinion, soft warning, novel query syntax, no upstream verification).
- [x] Backward compatibility additive (bare names continue to validate).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0260, 0261, 0276 (consumer RFCs), 0262 (license), Move-12 RFC-0157 (origin).
- [x] CLAUDE.md compliance: no-cloud invariant honored (validator does not fetch URIs); substrate-neutrality preserved at the manifest layer.
