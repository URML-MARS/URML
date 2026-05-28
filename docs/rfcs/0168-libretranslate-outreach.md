---
rfc: 0168
title: LibreTranslate (AGPL-3.0 self-hosted translation server) integration, request for comment from LibreTranslate maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0168: LibreTranslate (AGPL-3.0 self-hosted translation server) integration, request for comment from LibreTranslate maintainers

## Summary

URML does not yet ship a LibreTranslate manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for LibreTranslate — the self-hosted translation server — over [`LibreTranslate/LibreTranslate`](https://github.com/LibreTranslate/LibreTranslate) (**AGPL-3.0**), and **requests review and feedback from the LibreTranslate maintainers**. No spec change.

**This is a Move-12 Tier B RFC with an explicit license-friction note**: LibreTranslate is AGPL-3.0, which carries network-copyleft obligations. URML's reference runtimes are Apache-2.0; statically linking or embedding LibreTranslate into URML would contaminate URML's permissive license posture. The integration shape is therefore **REST-boundary-only**: URML acts as a client of a separately-deployed LibreTranslate server, never as an embedder of LibreTranslate's source.

## Motivation

`LibreTranslate/LibreTranslate` is the most-adopted open self-hosted translation server (AGPL-3.0, 14.4k stars, Issues enabled, last commit `2026-05-26` — daily activity, **not archived**). The project wraps OPUS-MT-derived (and increasingly NLLB-derived) models behind a clean REST API; operators self-host the server inside their own network and call it from any client.

LibreTranslate is interesting to URML for three reasons:

1. **Enterprise-friendly deployment with explicit network boundary.** Many URML deployments — industrial, federal, healthcare — must keep translation traffic inside a private network. LibreTranslate's self-host posture matches that. URML's manifest can declare the LibreTranslate endpoint URL as the translation substrate.
2. **The REST-boundary shape preserves URML's Apache-2.0 license cleanly.** AGPL-3.0 has network-copyleft (the "AGPL trigger" — distributing the software-as-a-service triggers source-disclosure obligations). The URML reference adapter is an HTTP *client* of LibreTranslate, not a derivative work; the boundary stays clean as long as URML never bundles or embeds LibreTranslate's code.
3. **Operator-deployed substrate model.** LibreTranslate already targets the "operator deploys the server, URML deploys the robot" architectural shape URML wants for cloud-optional infrastructure.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `libretranslate_cell.yaml` fixture, network-bounded)

Manifest does not currently declare a translation-engine substrate or a network-endpoint-based substrate. Proposed mapping uses the `custom` escape-hatch (parallel to RFC-0157 / RFC-0158 / RFC-0159 / RFC-0167):

| URML field | Maps to LibreTranslate attribute |
|---|---|
| `nl_layer.translation_engine: custom` (`libretranslate`) | Declares LibreTranslate is the translation substrate |
| `nl_layer.translation_runtime: rest_api` | Declares the runtime is a network endpoint (distinct from in-process runtimes in RFC-0158 / RFC-0159) |
| `nl_layer.translation_endpoint_url: https://translate.local.example/v1` | Declares the LibreTranslate server URL the URML client calls |
| `nl_layer.translation_endpoint_api_key: <secret-ref>` | Declares the optional API key (LibreTranslate supports both keyed and unkeyed modes) |
| `nl_layer.translation_pairs: [en-he, en-es, en-ja, en-zh, ...]` | Declares the language pairs the LibreTranslate server is configured to serve |
| `nl_layer.translation_endpoint_license_constraint: agpl_network_boundary` | **Declares the AGPL-3.0 boundary constraint** — the server is AGPL, the URML client is Apache; validator-enforceable that the URML client never embeds the LibreTranslate code |

### What URML v0.1 does not yet express for LibreTranslate

1. **Translation-engine-class declaration.** Shared with RFC-0157 / RFC-0158 / RFC-0159 / RFC-0167. URML's v0.1 manifest has no translation-engine field.
2. **Network-endpoint runtime declaration.** URML's v0.1 manifest assumes in-process inference. A `translation_runtime: rest_api` declaration with an endpoint URL is a structurally new substrate class.
3. **License-boundary declaration.** Distinct from RFC-0167's `translation_model_license` field, this is `translation_endpoint_license_constraint` — a manifest field that records "the substrate beyond this network boundary is under a license that would otherwise contaminate URML; the boundary is therefore load-bearing". The validator can enforce that the URML build does not embed the constrained-license substrate.
4. **Secret reference for the API key.** URML's manifest has no field for declaring secret-store references (vault paths, env-var names). The API key declaration is the first concrete case.

### Compatibility notes

- **Vendor org.** [`LibreTranslate`](https://github.com/LibreTranslate) — vendor-direct (community-led; primary maintainer @pierotofy is US-domiciled).
- **Flagship repo.** [`LibreTranslate/LibreTranslate`](https://github.com/LibreTranslate/LibreTranslate) — **AGPL-3.0**, 14.4k stars, Issues enabled, last commit `2026-05-26` (daily activity), **not archived**.
- **Origin.** Community / US-led. Passes US-federal default policy.
- **License fit.** AGPL-3.0 has network-copyleft. **REST-boundary-only integration**; URML never embeds. The Apache-2.0 stance is preserved.
- **Maintainer signal.** Very active surface (14.4k stars, daily commits). Engagement velocity should be high.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC. Multiple Spec RFCs queued: translation-engine-class declaration (shared with RFC-0157 / RFC-0158 / RFC-0159 / RFC-0167); network-endpoint runtime declaration (novel; introduces the REST-substrate concept to the manifest); license-boundary declaration (novel; complements RFC-0167's model-license declaration); secret-reference declaration (novel; deserves its own Spec RFC as it generalizes well beyond translation).
- Reference runtime: future `reference/translation-bridge/LibreTranslateClient` (a thin REST client that calls a configured endpoint URL) is the natural integration. **URML's build pipeline must verify** the client never bundles LibreTranslate source.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **AGPL-3.0 friction.** URML must enforce the REST-boundary at the build level. A future contributor who naively vendors LibreTranslate code into the URML repo breaks the license posture.
- **Operator-deployed dependency.** The translation runtime is no longer "URML installs it"; the operator must run a LibreTranslate server separately. URML's documentation must make this explicit.
- **Multiple Spec RFCs prerequisite.** Translation-engine-class (shared), network-endpoint runtime (novel), license-boundary (novel), secret-reference (novel). Four Spec RFCs to fully ship the manifest fields.
- **Network-runtime risks the no-cloud invariant.** URML's CLAUDE.md is explicit: "URML programs must execute fully offline once validated". A LibreTranslate endpoint inside the operator's own network is *technically* on-prem and not the public cloud, but the manifest must make the distinction visible to validators.

## Alternatives considered

1. **Engage only Argos Translate (RFC-0158) as the offline default; skip LibreTranslate.** Rejected. Argos covers single-robot deployments; LibreTranslate covers shared-fleet operator-deployed deployments. They serve different deployment shapes.
2. **Treat LibreTranslate as out-of-scope (URML never integrates AGPL).** Rejected. AGPL-via-REST-boundary is a legitimate integration pattern; declaring it out-of-scope leaves a real deployment use case unanswered.
3. **Bundle this RFC with RFC-0158 Argos.** Rejected. Argos is MIT-clean in-process; LibreTranslate is AGPL-over-network. Different friction, different manifest shape.
4. **Cross-citation only.** Considered. The license-boundary declaration is novel enough that an explicit RFC is the right shape.

## Prior art

- [`LibreTranslate/LibreTranslate`](https://github.com/LibreTranslate/LibreTranslate) — the upstream server.
- [`LibreTranslate/argos-translate-files`](https://github.com/LibreTranslate/argos-translate-files) — companion model-format mirror.
- [RFC-0157 (Helsinki-NLP OPUS-MT)](0157-opus-mt-train-outreach.md) — sibling Move-12 RFC, model-family upstream LibreTranslate consumes.
- [RFC-0158 (Argos Translate)](0158-argos-translate-outreach.md) — sibling Move-12 RFC, in-process MIT alternative.
- [RFC-0167 (Meta fairseq / NLLB-200)](0167-fairseq-outreach.md) — sibling Tier B Move-12 RFC, parallel-friction shape (non-commercial model weights vs. AGPL server).
- [CLAUDE.md "URML programs must execute fully offline"](../../CLAUDE.md) — the architectural invariant LibreTranslate's operator-deployed shape preserves.

## Unresolved questions

For the LibreTranslate maintainers:

1. **REST-boundary framing.** Is "URML is an HTTP client of a self-hosted LibreTranslate server, never embedding the source" the framing the LibreTranslate maintainers would endorse, or is there language the project would prefer for downstream integrations?
2. **API key declaration.** Is `translation_endpoint_api_key` with a secret-store reference the right shape, or does LibreTranslate have a preferred convention?
3. **License-boundary declaration.** Is `translation_endpoint_license_constraint: agpl_network_boundary` the right way to declare "this substrate is AGPL but I'm calling it across a network boundary"? Useful as a downstream signal, or unnecessary friction?
4. **Pair availability discovery.** LibreTranslate's `/languages` endpoint enumerates supported pairs at runtime. Should URML's manifest declare the static list, or discover-on-startup?
5. **Self-host vs. public.libretranslate.com.** Is the public hosted instance a supported runtime for URML to declare, or strictly an example?
6. **Adapter home.** URML-side REST-client adapter in URML's `reference/translation-bridge/`, contributed example in `LibreTranslate/examples/`, or external bridge repo?
7. **Conformance listing.** Would the LibreTranslate maintainers consider a README link to URML's compatible-runtimes registry once a working REST-client adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0168 ships as a single RFC document PR (Move-12 batch 2 — translation cluster, **completes the translation bucket**). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`LibreTranslate/LibreTranslate` has Issues enabled (Discussions disabled). URML's planned channel: open a single Issue on `LibreTranslate/LibreTranslate` framed as "URML manifest declaration + REST-boundary integration shape, design RFC", pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (AGPL-3.0, 14.4k stars, Issues enabled, last commit 2026-05-26 daily, isArchived: false).
- [x] AGPL-3.0 friction called out up front (REST-boundary-only integration shape).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (AGPL boundary discipline, operator dependency, four Spec-RFCs prerequisite, no-cloud invariant tension).
- [x] Sibling RFC cross-links explicit (RFC-0157 OPUS-MT, RFC-0158 Argos, RFC-0159 Marian, RFC-0167 NLLB).
- [x] CLAUDE.md no-cloud invariant cited with on-prem-vs-cloud nuance.
- [x] Multiple novel manifest declarations flagged for Spec RFC follow-up (network-endpoint runtime, license-boundary, secret-reference).
- [x] No spec change proposed in this RFC.
