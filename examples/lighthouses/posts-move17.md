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

# Move #17 post bodies — Sub-wave A (GitHub-Issue-postable)

Copy-paste-ready Issue bodies for the **Move #17 Sub-wave A** — the 5 targets that fit URML's existing `gh issue create` pipeline. **Wave shape**: 5 verified GitHub-engageable targets (Eclipse SDV / ELISA / OPC Foundation / OpenSSF SLSA / OpenSSF Scorecard). RFCs 0212-0216.

Sub-wave B (13 founder-action targets — OSRA, JDF, IEEE 1872-2, NIST EL, ASTM F45.04, IIA, euRobotics, ADRA, JTC 21, DIN/DKE, AFNOR, BSI, OECD) has its own artifact file: [`founder-actions-move17.md`](founder-actions-move17.md).

Sub-wave C (4 docket-watch + 4 US-partner-gated Tier B) has no immediate posting; tracked in [`outreach-move17.yaml`](outreach-move17.yaml).

Ledger state: [`outreach-move17.yaml`](outreach-move17.yaml). Full research audit: [`move17-research-2026-05-29.md`](move17-research-2026-05-29.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("seventeen outreach waves to date") are fine.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #17 Sub-wave A post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Wave-17 framing notes:**

- Move #17 engages **governance bodies**, not substrate / vendor / academic maintainers (the audience of Moves 1-16). The point of engagement is foundation-home reconnaissance per [`CLAUDE.md`](../../CLAUDE.md)'s structural-separation clause.
- Sub-wave A targets are GitHub-engageable cross-citation candidates (Eclipse SDV, ELISA, OPC Foundation, OpenSSF SLSA / Scorecard). Each is **not** a direct foundation-home candidate but a strategic cross-citation that strengthens URML's safe-by-construction / supply-chain-alignment narrative.
- The direct foundation-home conversations (OSRA, JDF) are in Sub-wave B (founder-action) per the engagement mechanic.

---

## Sub-wave A targets (5)

### RFC-0212: Eclipse SDV Blueprints
**Post to:** https://github.com/eclipse-sdv-blueprints/blueprints-website/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting cross-citation feedback from Eclipse SDV Blueprints

**Body:**

Hi Eclipse SDV team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's drone-runtime and industrial-arm-runtime tracks face structurally similar problems to the ones Eclipse SDV blueprint patterns are formalizing across automotive, commercial-vehicle, and (newly in 2026) aerospace: substrate-neutrality, safe composition, declarative intent, and validator-gated execution.

This is a **proposal-only** RFC, posted as part of URML's Move #17 outreach (government-rep wave: standards bodies + open-source foundations + US federal agencies + allied governments, 22 engageable Tier-A targets). URML's Sub-wave A targets cross-citation engagements with foundations that strengthen URML's safe-by-construction narrative without being direct foundation-home candidates. SDV is one such — URML proposes cross-citation rather than embedding.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0212-eclipse-sdv-blueprints-outreach.md

This is URML's fourth Eclipse Foundation engagement after Move-16 (Cyclone DDS / Zenoh / iceoryx); URML is open to a Foundation-level conversation if maintainers prefer that to per-project Issue threads.

Asks for the Eclipse SDV maintainers:

1. **Cross-citation framing preference.** Should URML's reference-runtime READMEs cite Eclipse SDV blueprints by name, by repo URL, or by Foundation-level reference?
2. **Aerospace-blueprint extension scope.** When does the 2026 aerospace extension reach the URML-drone-profile audience? Is there a WG surface where URML's drone profile (RFC-0008) is reviewable as related-art?
3. **Cross-WG citation conventions.** Are there Eclipse Foundation conventions for cross-WG citation URML should follow?
4. **Foundation-level conversation.** With four Eclipse engagements now active, would Eclipse Foundation prefer to convene a single project-collaboration conversation?
5. **EPL-2.0 → Apache-2.0 cross-citation discipline.** URML composes at the API boundary, not by source embedding. Preferred attribution shape from the SDV side?
6. **Conformance listing.** Would Eclipse SDV consider a blueprints-website link to URML's compatible-runtimes registry (RFC-0014) once cross-citation stabilizes?
7. **Anything else.**

Thanks for the safe-vehicle-software composition patterns the SDV WG has been building.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0213: ELISA wg-automotive
**Post to:** https://github.com/elisa-tech/wg-automotive/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting safe-Linux cross-citation feedback from ELISA wg-automotive

**Body:**

Hi ELISA team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's `safety_envelope` manifest field and validator-gated execution model align with ELISA's safe-construction-from-Linux thesis. URML's reference runtimes execute on Linux substrates that face the exact safety-construction problem ELISA was chartered to solve.

This is a **proposal-only** RFC, posted as part of URML's Move #17 outreach (government-rep wave). Sub-wave A engages cross-citation candidates that strengthen URML's safe-by-construction narrative.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0213-elisa-wg-automotive-outreach.md

URML's manifest-validated dispatch + validator static-verification stage is one concrete pattern for declaring the safe-construction boundary explicitly; ELISA's body of work is the broader framework URML composes within.

Asks for the ELISA maintainers:

1. **Cross-citation framing preference.** Should URML's safety-docs cite ELISA by Project name, by specific WG (wg-automotive / wg-aerospace / Safety_Architecture_WG), or both?
2. **Working-group cross-attendance.** Are ELISA WG calls open to non-member attendees? URML maintainer would benefit from monitoring safety-Linux work relevant to URML reference runtimes.
3. **Aerospace + automotive scope mapping.** URML's drone profile (RFC-0008) and industrial profile (RFC-0013) align with wg-aerospace and wg-automotive respectively; is per-WG cross-citation mapping appropriate?
4. **Safety-claim discipline.** URML does not claim safety certification; cross-citation is for safe-construction-framework alignment. Are there ELISA guidelines for how non-certified open-source projects should cross-cite without misrepresenting certification status?
5. **Linux Foundation member-track question.** URML is single-maintainer Phase-1; what's the LF/ELISA path for a future-foundation candidate? (Orientation only; not a Phase-1 ask.)
6. **Conformance listing.** Would ELISA consider a wg-automotive / wg-aerospace README link to URML's compatible-runtimes registry (RFC-0014) once cross-citation stabilizes?
7. **Anything else.**

Thanks for the safety-Linux framework that makes safe-by-construction tractable for open-source.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0214: OPC Foundation UA-Nodeset
**Post to:** https://github.com/OPCFoundation/UA-Nodeset/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting OPC UA Robotics cross-citation + license clarification

**Body:**

Hi OPC Foundation team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's industrial-runtime track targets manipulation primitives (`pick_from`, `place_at`, `swap_tool`) that, on OPC-UA-Robotics deployments, dispatch through the OPC UA Robotics Companion Specification.

This is a **proposal-only** RFC, posted as part of URML's Move #17 outreach (government-rep wave). The OPC UA Robotics Companion Spec is the standards-side recognized industrial-robotics surface URML's industrial profile (RFC-0013) composes against.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0214-opc-foundation-ua-nodeset-outreach.md

URML's Layer-1 HAL capability manifest declares what the robot can do; the OPC UA Robotics NodeSet declares what the OPC UA server exposes. These are structurally close. Cross-citation may surface mapping opportunities (URML manifest field ↔ OPC UA NodeSet attribute).

Asks for the OPC Foundation maintainers:

1. **License clarification.** The UA-Nodeset repo's license is not OSI-declared on the repo surface today. Can the README or LICENSE file declare an explicit OSI license to unlock URML adapter-grade reuse?
2. **Manifest-NodeSet mapping interest.** Is there OPC Foundation interest in scoping a URML-manifest ↔ OPC UA Robotics NodeSet semantic mapping? If yes, what's the channel — UA Robotics Working Group, joint working group, or per-Issue thread?
3. **2026 AI / Agentic AI Companion Spec input.** Does the OPC Foundation accept community input on emerging Companion Specs? URML's NL-translation + validator-gated-execution pattern is offered as a related-art reference.
4. **Industrial-arm scope.** URML's cross-citation is scoped to industrial-arm deployments; is OPC UA Robotics scope likewise industrial-arm, or does it extend to mobile-base / outdoor robotics?
5. **Cross-citation discipline.** URML proposes cross-citation in industrial-profile docs; preferred attribution shape from the OPC Foundation side?
6. **Conformance listing.** Would the OPC Foundation consider a UA-Robotics README link to URML's compatible-runtimes registry (RFC-0014) once URML's industrial-runtime adapter ships?
7. **Anything else.**

Thanks for the OPC UA Robotics Companion Spec that gives industrial robotics a standards-side interoperability surface.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0215: OpenSSF SLSA
**Post to:** https://github.com/slsa-framework/slsa/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting SLSA cross-citation for default-policy federal-procurement framing

**Body:**

Hi SLSA team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML ships a default-policy file (RFC-0003) embedding US-federal alignment (NDAA Section 889, EO 14307, FCC Covered List) for robotics-substrate procurement gating at `urml validate --policy` time. EO 14028 (Improving the Nation's Cybersecurity) and successor frameworks add the supply-chain-provenance layer; SLSA is the operationalization URML's federal-procurement narrative needs.

This is a **proposal-only** RFC, posted as part of URML's Move #17 outreach (government-rep wave). Sibling RFC-0216 covers OpenSSF Scorecard; together they form URML's OpenSSF tooling adoption layer.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0215-openssf-slsa-outreach.md

URML's manifest could declare a future `provenance.slsa_level` field for the substrate; the validator can enforce manifest-vs-attestation at validate time. The field design benefits from SLSA-maintainer review before URML commits to the manifest shape.

Asks for the SLSA maintainers:

1. **`provenance.slsa_level` manifest field design.** What's the SLSA maintainers' preferred shape for a downstream consumer declaring "this substrate is SLSA-L3-attested" in a manifest? Single-level enum, attestation URL, or both?
2. **Multi-component substrate attestation.** Robotics substrates compose multiple OSS projects (ROS 2 = rclcpp + rclpy + rmw + plugins); how should URML declare provenance for a composite substrate?
3. **Validator-side attestation verification.** URML's planned validator integration would fetch and verify the substrate's SLSA attestation at validate time. Preferred verification path (`slsa-verifier`, in-toto verifier, custom)?
4. **EO 14028 cross-citation.** URML's default policy already cites NDAA 889 / EO 14307 / FCC Covered List; adding SLSA L3 + EO 14028 — preferred citation language?
5. **Robotics-substrate SLSA adoption today.** What's the SLSA-side view of robotics-substrate adoption (ROS 2 / PX4 / MoveIt 2)? URML's manifest field would surface real-world gaps.
6. **Conformance listing.** Would SLSA / OpenSSF consider a README cross-link to URML's compatible-runtimes registry (RFC-0014) once URML's manifest field integrates SLSA-level declaration?
7. **Anything else.**

Thanks for the supply-chain-provenance framework that makes federal-procurement-grade open-source possible.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0216: OpenSSF Scorecard
**Post to:** https://github.com/ossf/scorecard/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC on adopting OpenSSF Scorecard for URML reference-runtime repos

**Body:**

Hi OpenSSF Scorecard team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's reference runtimes (`reference/ros2-runtime/`, planned drone-runtime, industrial-runtime, etc.) ship from URML's repo and future companion-package repos; each repo's security posture is currently undocumented externally. Scorecard adoption publishes that posture in a federally-cited format.

This is a **proposal-only** RFC, posted as part of URML's Move #17 outreach (government-rep wave). Sibling RFC-0215 covers SLSA; together they cover URML's OpenSSF tooling adoption layer + federal-procurement narrative.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0216-openssf-scorecard-outreach.md

URML's plan is to (a) adopt the Scorecard GitHub Action on the URML main repo + reference-runtime companion repos and publish the badge in README, (b) propose a future `provenance.scorecard_min_score` manifest field for substrate-quality-gating.

Asks for the OpenSSF Scorecard maintainers:

1. **Robotics-specific signal extensions.** Are there robotics-substrate-specific security signals that would benefit Scorecard, or are the existing ~18 signals sufficient?
2. **`provenance.scorecard_min_score` manifest field design.** Preferred shape for a downstream consumer declaring "this substrate must score >= N"? Single-threshold-number, per-signal-threshold, or other?
3. **Multi-component substrate scoring.** Robotics substrates often compose multiple OSS projects; how should URML's manifest declare an aggregate Scorecard threshold for a composite substrate?
4. **Adoption recommendation for multi-runtime-repo projects.** Are there Scorecard-recommended adoption patterns (single Scorecard run vs per-runtime-repo)?
5. **Reciprocal cross-citation.** Would Scorecard reference URML as one example of an open-spec project consuming Scorecard at the substrate boundary?
6. **OpenSSF / LF engagement convergence.** With SLSA (RFC-0215) + Scorecard (RFC-0216) active concurrently, should URML pursue an OpenSSF / LF Foundation-level conversation rather than per-project Issue threads?
7. **Conformance listing.** Would Scorecard / OpenSSF consider a README link to URML's compatible-runtimes registry (RFC-0014)?
8. **Anything else.**

Thanks for the health-scoring tool that makes open-source security posture publicly verifiable.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

## Tier C — recorded in research file, NOT engaged

See [`move17-research-2026-05-29.md`](move17-research-2026-05-29.md) for the full Tier-C audit. Excerpted high-level categories:

- **Already engaged via prior Moves** (5): OSRF / Open-RMF (Move-2), ROS 2 core (Move-16 RFC-0200), Eclipse Cyclone DDS / Zenoh / iceoryx (Move-16 RFCs 0204 / 0209 / 0210), Linux Foundation Dronecode constituents (Move-16 RFCs 0196-0199 + 0208).
- **No public engagement surface for Phase 1** (6): ANSI/RIA R15.08 (paid trade-association channel), IEC TC 65, ASME, INCITS (no robotics TC exists), Apache Software Foundation (zero robotics-relevant repos), CNCF Robotics SIG (doesn't exist — new-SIG-proposal, not outreach).
- **Defense-export-controlled architectural conflicts** (7): SIBAT, Hoshen, UK DSTL, AU DSTG, CA DRDC, AUKUS, NATO STO. Engaging in URML-tied capacity would conflict with URML's Apache-2.0 + offline + no-cloud commitments. **Cost of access is the open posture.**
- **Wrong-shape regulatory / out-of-scope** (4): OSHA, FDA medical-robotics (out of URML civilian-scope per CLAUDE.md), FCC OET (consumer-of-policy not shaper), NTIA / CISA (no active 2026 robotics docket).
- **Closed / dead** (2): Callaghan Innovation NZ (closing June 2026), NSF NRI (restructured to FRR; already in Tier B), NSF POSE legacy (replaced by PESOSE; already in Tier B).
- **Excluded by default policy** (2): PRC-domiciled candidates (NDAA 889), sanctioned-state candidates.

Total Tier C: ~34 candidates documented for the audit trail.
