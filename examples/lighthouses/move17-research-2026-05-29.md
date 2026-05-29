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

# Move-17 research — government reps for foundation-home alignment

**Research date**: 2026-05-29.
**Audience**: founder review before Move-17 outreach.
**Method**: three parallel research agents covered (1) standards bodies + open-source foundations, (2) US federal agencies via formal channels, (3) allied / international governments + tech ministries. Each verified via `gh api orgs/...` / `gh repo view` where applicable, plus web search for committee URLs, RFI dockets, membership channels.
**Outcome**: **21 verified Tier A targets** (8 Class 1 + 5 Class 2 + 8 Class 3) split across three engagement-mechanic sub-waves. **~15 Tier B** deferred-with-cause. **~30 Tier C** excluded.

## Why this wave is qualitatively different from Moves 1-16

Prior moves engaged substrate / vendor / academic / OEM maintainers — all roughly the same shape (GitHub repo with Issues enabled, vendor email at known address, founder-action posting via `gh issue create`). Move-17 engages **governance bodies** — the plausible long-term hosts for URML's structural separation per [`CLAUDE.md`](../../CLAUDE.md) ("Structural separation is coming. A venture-scale outcome typically ends with two entities: a non-profit foundation owning the standard ... A US-domiciled 501(c)(6) industry association, an SDO with strong US ties (IEEE-SA, INCITS), or a sponsored project under an existing US-domiciled foundation").

**The point of engagement in Move-17 is not an adapter PR.** It is to find a long-term home for URML's standard surface (the spec, the conformance suite, the validator, the LLM bridge), while keeping the commercial surround out of the foundation entirely. Two-track posture per [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) is unchanged.

This means the engagement-mechanic mix is fundamentally different. URML's existing `gh issue create` pipeline fits only a fraction of Move-17 targets; the rest need founder-action artifacts (membership applications, email-to-program-officer, formal consultation submissions, ISO national-mirror-body participation).

## Mechanic-split sub-waves

### Sub-wave A — GitHub-Issue-postable (5 targets)

Same pipeline as Moves 10-16. Assistant-postable via `gh issue create` once RFC + body lands.

| RFC | Slug | Repo | License | Class | Notes |
|---|---|---|---|---|---|
| 0212 | `eclipse-sdv-blueprints` | [eclipse-sdv-blueprints/blueprints-website](https://github.com/eclipse-sdv-blueprints/blueprints-website) | EPL-2.0 | C1 | Eclipse Foundation SDV Working Group; automotive + aerospace + commercial-vehicle blueprints |
| 0213 | `elisa-tech-wg-automotive` | [elisa-tech/wg-automotive](https://github.com/elisa-tech/wg-automotive) | Multi-OSI | C1 | Linux Foundation ELISA; safety-Linux for medical / automotive / robotics |
| 0214 | `opc-foundation-ua-nodeset` | [OPCFoundation/UA-Nodeset](https://github.com/OPCFoundation/UA-Nodeset) | TBD verify | C1 | OPC UA Robotics companion specification |
| 0215 | `openssf-slsa` | [slsa-framework/slsa](https://github.com/slsa-framework/slsa) | Other | C1 | Supply-chain provenance; cited by EO 14028; complements URML's NDAA-889 default |
| 0216 | `openssf-scorecard` | [ossf/scorecard](https://github.com/ossf/scorecard) | Apache-2.0 | C1 | Security health scoring; federally-cited tooling |

### Sub-wave B — Founder-action (13 targets, 10 with RFCs + 3 membership-only)

Each needs the founder's identity. Assistant prepares verbatim drafts; founder reviews and sends through the proper channel. URML RFC on `main` provides public cross-citation.

**With RFCs (10):**

| RFC | Slug | Surface | Channel | Class | Notes |
|---|---|---|---|---|---|
| 0217 | `osra-membership-inquiry` | [osralliance.org](https://osralliance.org/) | Alliance contact form / direct email | C1 | OSRF-governed alliance over ROS / Gazebo / Open-RMF; closest robotics-native foundation-home fit |
| 0218 | `jdf-formation-inquiry` | [jointdevelopment.org](https://jointdevelopment.org/) | Membership-formation channel | C1 | Linux Foundation JDF; ISO/IEC JTC 1 PAS submitter; neutral standards path |
| 0219 | `ieee-1872-2-wg-signup` | [sagroups.ieee.org/1872-2](https://sagroups.ieee.org/1872-2/) | IEEE-SA WG application | C1 | Autonomous Robotics Ontology; closest IEEE cross-citation |
| 0220 | `nist-el-isd-feedback` | [nist.gov/el/intelligent-systems-division-73500/robotics-community-feedback](https://www.nist.gov/el/intelligent-systems-division-73500/robotics-community-feedback) | Email to Craig Schlenoff (program manager) | C2 | Closest US-federal fit; 1-2 page memo |
| 0221 | `astm-f45-04-position-paper` | [astm.org/membership-participation/technical-committees/committee-f45](https://www.astm.org/membership-participation/technical-committees/committee-f45) | Paid ASTM individual membership + F45.04 subcommittee paper | C2 | Highest-leverage US SDO; NIST staff co-chair |
| 0222 | `cen-cenelec-jtc-21-enquiry` | [jtc21.eu](https://jtc21.eu/) | Public-enquiry comment (next prEN window) | C3 | EU AI standards; routes via national member body (for IL: SII) |
| 0223 | `din-dke-ai-roadmap` | [din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap](https://www.din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap) | Roadmap-participation contribution | C3 | DE national position into CEN-CENELEC JTC 21 |
| 0224 | `afnor-grand-defi-ai` | [afnor.org/en/news/shaping-european-ai-leadership/](https://www.afnor.org/en/news/shaping-european-ai-leadership/) | Consultation-platform submission | C3 | FR national position into JTC 21 |
| 0225 | `bsi-ai-standards-hub` | [aistandardshub.org](https://aistandardshub.org/) | AI Standards Hub engagement; international remit explicit | C3 | UK national surface; BSI + Alan Turing Institute + NPL |
| 0226 | `oecd-ai-policy-observatory` | [oecd.ai](https://oecd.ai/en/) | Policy submission to AI Policy Observatory catalogue | C3 | International norms surface (OECD AI Principles + Hiroshima Process); IL is OECD member |

**Membership-only (3, no RFC, just application):**

| Slug | Surface | Channel | Class | Notes |
|---|---|---|---|---|
| `israel-innovation-authority` | [innovationisrael.org.il](https://innovationisrael.org.il/en/) | Direct Hebrew application; AI/robotics deep-tech basket | C3 | Founder-domiciled; lowest-friction |
| `eu-robotics-aisbl` | [eu-robotics.net/membership](https://eu-robotics.net/membership/) | Associate Membership application form | C3 | EU robotics association; ~250 members; Horizon Europe associated-country access |
| `adra-association` | [adr-association.eu](https://adr-association.eu/) | Membership application | C3 | Horizon Europe AI-Data-Robotics PPP successor to SPARC; 180+ members |

### Sub-wave C — Deferred (4 targets, ledger row only)

Federal-docket watch: no immediate action; track for next window.

| Slug | Watch | Class | Last cycle | Next |
|---|---|---|---|---|
| `nist-caisi-rfi-watch` | [csrc.nist.gov drafts](https://csrc.nist.gov/publications/drafts-open-for-comment) | C2 | RFI closed 9 Mar 2026 (NIST-2025-0035) | Next CAISI AI-agent docket |
| `faa-bvls-utm-watch` | [Federal Register](https://www.federalregister.gov) filter "FAA UAS" | C2 | BVLOS NPRM Aug 2025; FAA reopened | Next BVLOS / UTM reopened docket |
| `nhtsa-av-step-watch` | [transportation.gov/av/publicnotices](https://www.transportation.gov/av/publicnotices) | C2 | Mar 2026 public meeting; comments closed 10 Apr 2026 | Next AV-policy docket |
| `enisa-cra-standardisation-watch` | [enisa.europa.eu/publications/cyber-resilience-act-requirements-standards-mapping](https://www.enisa.europa.eu/publications/cyber-resilience-act-requirements-standards-mapping) | C3 | CRA draft-guidelines consultation closed 31 Mar 2026 | Next CRA / cyber-resilience consultation |

## Tier B — relevant but deferred-with-cause

These are real engagement candidates that this wave does **not** pursue because they're (a) US-domicile-gated and URML lacks a US partner, (b) require institutional cover URML doesn't have at Phase 1, or (c) are dead / archived / closed.

### Class 1 Tier B (5)

| Slug | Surface | Defer reason |
|---|---|---|
| `ros-industrial-industrial-ci` | [ros-industrial/industrial_ci](https://github.com/ros-industrial/industrial_ci) | SwRI-stewarded; ROS-aligned, but URML is substrate-neutral — engagement here is mostly already covered by Move-16 RFC-0200 (ROS 2 core). Reconsider when a Move-17 ROS-Industrial-specific angle emerges. |
| `ros-industrial-consortium-scan-n-plan` | [ros-industrial-consortium/scan_n_plan_workshop](https://github.com/ros-industrial-consortium/scan_n_plan_workshop) | Same as above. |
| `lf-edge-eve` | [lf-edge/eve](https://github.com/lf-edge/eve) | Edge-virtualization engine; "Physical AI" framing 2026. Cross-citation candidate but not foundation-home material. |
| `cncf-toc` | [cncf/toc](https://github.com/cncf/toc) | No robotics SIG exists; URML pitch would be a new-SIG proposal, not a fit to existing surface. Defer to Phase 2. |
| `iso-tc-299` | [ISO/TC 299 Robotics](https://www.iso.org/committee/5915511.html) | Canonical international robotics SDO; engagement is via national member bodies (SII for Israel; ANSI for US) and is gated on JDF (Sub-wave B RFC-0218) being a viable PAS route. Phase 2. |

### Class 2 Tier B (4)

| Slug | Surface | Defer reason |
|---|---|---|
| `arm-institute` | [arminstitute.org/membership](https://arminstitute.org/membership/) | DoD Manufacturing Innovation Institute; 450+ members; engagement requires US-domiciled co-member (academic lab or industrial sponsor). Pursue when US partner exists. |
| `nsf-pesose` | [NSF 26-506](https://www.nsf.gov/funding/opportunities/pesose-pathways-enable-secure-open-source-ecosystems/nsf26-506/solicitation) | Pathways to Enable Secure Open-Source Ecosystems; **NSF PI must be at US-domiciled institution**. Pursue with US academic partner. |
| `nsf-frr` | [NSF FRR](https://www.nsf.gov/funding/opportunities/frr-foundational-research-robotics) | Foundational Research in Robotics; same NSF PI gate. Pursue with US academic partner. Outreach should target FRR-funded labs (researcher-to-researcher), not NSF directly. |
| `darpa-tto-rfi-watch` | [darpa.mil/work-with-us/opportunities](https://www.darpa.mil/work-with-us/opportunities) | RFI-only responses (no funding) are technically open to non-US persons; funded work requires US-domiciled prime. Monitor for next robotics-relevant RFI. |

### Class 3 Tier B (6)

| Slug | Surface | Defer reason |
|---|---|---|
| `jisc-japan` | [JISC](https://www.jisc.go.jp/eng/) | Major TC 299 contributor; engagement is through committee work, not public-comment surface. Needs Japanese partner or DIN/AFNOR cross-listing. |
| `nedo-japan` | [Eureka Globalstars Japan](https://www.eurekanetwork.org/programmes-and-calls/globalstars/globalstars-call-with-japan/) | 2025-26 call closed Jan 2026; routes via IIA-NEDO bilateral (which is reached via the IIA Sub-wave B membership application). Track for next window. |
| `meti-japan` | [METI Robot Industry](https://www.meti.go.jp/english/policy/mono_info_service/robot_industry/index.html) | Ministry not a contribution surface; co-issues AI Guidelines with MIC; route input via OECD policy submission (RFC-0226). |
| `kist-keit-korea` | [KIST](https://kist.re.kr/eng/) / [KEIT](https://www.keit.re.kr/) | AI Humanoid Core Tech Project 2026-2030 is consortium-shaped; no IL-direct channel. Needs KR-domiciled academic partner. |
| `uk-robotics-growth-partnership` | [Smart Machines 2035 Strategy](https://assets.publishing.service.gov.uk/media/67aa2e965dea3871ea1ceb12/smart-machines-strategy-2035.pdf) | Robotics Adoption Hubs funding (up to £38M) is UK-registered-orgs only. Strategy consultation events joinable but funding gated. Public comments only. |
| `sii-israel` | [SII / Standards Institution of Israel](https://www.sii.org.il/) | Israeli national mirror to ISO/IEC and CEN/CENELEC; the actual channel for JTC 21 (RFC-0222) and ISO TC 299. Add as Tier-A IL-domestic if Hebrew correspondence preferred over routing through Ministry of Innovation; currently treated as the underlying mechanic for Sub-wave B JTC 21 / DIN / AFNOR / future ISO TC 299 work. |

## Tier C — excluded with cause

### Class 1 (11)

| Slug | Cause |
|---|---|
| `osrf` | Already engaged Move-2 RFC-0037 (Gazebo) + RFC-0053 (Open-RMF). OSRA is the new governance body over the same projects; engagement at the OSRA level (Sub-wave B RFC-0217) supersedes. |
| `ros2-core` | Already engaged Move-16 RFC-0200. |
| `eclipse-cyclonedds` / `eclipse-zenoh` / `eclipse-iceoryx` | Already engaged Move-16 RFCs 0204 / 0209 / 0210. Eclipse Foundation already reached via Move-16; Sub-wave A RFC-0212 (SDV Blueprints) is the cross-WG extension. |
| `linux-foundation-dronecode` | Already engaged Move-16 RFCs 0196 / 0197 / 0198 / 0199 / 0208 (PX4 / MAVLink / MAVSDK / DroneCAN / QGroundControl). Dronecode covered at constituent-project level. |
| `ansi-ria-r15.08` | Managed by A3 (Automate.org); paid trade-association channel; no public engagement surface for Phase 1 URML. Defer to Phase 2 when measured response-time data supports formal SDO submission per [feedback_public_commitments](https://github.com/URML-MARS/URML). |
| `iec-tc-65` | National-body delegation channel only; no public participation surface. Phase 2. |
| `asme-robotics` | No public robotics-software surface. Phase 2. |
| `incits` | INCITS technical-committee directory lists AI / Biometrics / Cybersecurity / Networks / C-lang — **no robotics TC exists**. Confirmed via [incits.org/participation/technical-committees](https://www.incits.org/participation/technical-committees). |
| `apache-software-foundation` | Substring scan of 3,131 Apache repos returned zero robotics-relevant matches. Apache scope is AI / big data / web. |
| `cncf-robotics-sig` | **No robotics SIG exists.** A new-SIG proposal is structurally different from outreach engagement; defer to Phase 2. |

### Class 2 (11)

| Slug | Cause |
|---|---|
| `nsf-nri` | Restructured. NRI wound down; FRR is successor (Tier B). Do not double-count. |
| `nsf-pose-legacy` | Archived. Replaced by PESOSE (Tier B). Do not double-count. |
| `darpa-i2o-mto-sto` | Same eligibility frame as DARPA TTO (Tier B). No office-level engagement surface; programs are BAA-driven. Subsumed under DARPA TTO Tier B. |
| `dod-cdao` | US-domiciled commercial vendors only; no Phase 1 fit. |
| `afrl` | US-domiciled performer required for open BAAs. Wait for US partner. |
| `arl-devcom` | US-domiciled performer required for CRADAs. Wait for US partner. |
| `osha-robotics` | No OSHA-specific robotics standard; relies on Alliance with NIOSH + A3. Industrial profile is right artifact when there's something to standardize; not Phase 1 federal-outreach material. |
| `fda-medical-robotics` | URML has no medical profile; Core Commitment scope-bars medical autonomy per CLAUDE.md ("civilian, consumer, educational, industrial, research"). Out of URML scope. |
| `fcc-oet-covered-list` | URML's default policy file **consumes** the FCC Covered List per RFC-0003. FCC OET does not solicit input on which robots/runtimes should comply. Wrong-shape target; note as input source. |
| `ntia-open-source-policy` | No active robotics-relevant docket 2026. Track for future RFIs; do not initiate. |
| `cisa-supply-chain` | Active robotics-supply-chain interest exists but no CISA-issued robotics-specific RFI 2026. Monitor; do not initiate. |

### Class 3 (12)

Defense-export-controlled (architectural conflict with URML's Apache-2.0 + offline + no-cloud posture):

| Slug | Cause |
|---|---|
| `sibat-israel-mod` | Israeli MoD International Defense Cooperation Directorate; administers Wassenaar dual-use controls. Engaging in URML-tied capacity would risk dual-use export-control classification. **Cost of access is the open posture itself.** |
| `israel-hoshen-ddrd` | IDF defense initiative under MoD DDRD; same export-control + open-posture conflict as SIBAT. |
| `uk-dstl` | UK MoD R&D; NATO research competitions are member-only; no IL-DSTL bilateral. Defense gate + UK-domicile gate. |
| `australia-dstg` | TTCP (US/UK/CA/AU/NZ) Five-Eyes-locked. Israel not in scope. |
| `canada-drdc` | Same Five-Eyes / TTCP gating as DSTG; Canadian defense agency. |

Locked / wrong-shape:

| Slug | Cause |
|---|---|
| `aukus-pillar-2` | US/UK/AU trilateral; explicitly "not yet in a position to consider additional partners" (verified 2026). Israel not in scope. AURAS / TORVICE work is security-cleared; conflicts with open-source posture even if access existed. |
| `nato-sto` | Member-nominated only. Israel is NATO partner (Mediterranean Dialogue / Individually Tailored Partnership Programme), not member. Founder cannot self-nominate; URML has no NATO-member sponsor. Phase 3+ future-foundation candidate. |
| `callaghan-innovation-nz` | **Winding down — closure June 2026.** Products / services transferring to MBIE + new Public Research Organisations. Engagement target gone before reply window would close. Re-evaluate after PRO successor list stabilizes. |
| `mic-japan` | Ministry not a contribution surface; co-issues AI Guidelines with METI; same routing as METI Tier B (via OECD policy submission RFC-0226). |
| `weizmann-technion-standards-bodies` | **Unverified.** Web verification did not surface Weizmann- or Technion-branded standards bodies as discrete targets. Actual route is SII (Tier B). |

Excluded by default policy:

| Slug | Cause |
|---|---|
| `prc-domiciled-candidates` | NDAA Section 889. MIIT (China), CCID, CESI excluded. Not in candidate list; noted for completeness. |
| `sanctioned-state-candidates` | US-federal default policy exclusion. RU, IR, KP, CU, SY, VE. Not in candidate list; noted. |

## Distribution

| Class | Tier A | Tier B | Excluded |
|---|---|---|---|
| C1 standards bodies + open-source foundations | 8 | 5 | 11 |
| C2 US federal agencies | 5 (2 actionable + 3 docket-watch) | 4 (US-partner-gated) | 11 |
| C3 allied / international governments | 8 | 6 | 12 |
| **Total** | **21** | **15** | **34** |

## Sub-wave breakdown (mechanics)

| Sub-wave | Mechanic | Count | RFCs reserved | Posting authority |
|---|---|---|---|---|
| **A** GitHub-Issue-postable | `gh issue create` (existing pipeline) | 5 | 0212-0216 | Assistant on founder authorization |
| **B-with-RFC** Founder-action | Email / membership / formal submission, URML RFC backs | 10 | 0217-0226 | Founder personally |
| **B-membership-only** Founder-action | Membership application form, no public RFC | 3 (IIA, euRobotics, ADRA) | — | Founder personally |
| **C** Docket-watch / partner-gated | Ledger row only; no immediate action | 7 (3 docket + 4 US-partner) | — | None this wave |

**Reserved RFC range**: Move-17 reserves **RFCs 0212-0226** (15 RFCs). Move-16 ends at RFC-0211.

## Honest framing notes

- **No single foundation is a slam-dunk home.** OSRA (RFC-0217) is the closest robotics-native fit, but ROS-aligned, which risks the substrate-neutral identity Move-16 just engaged. JDF (RFC-0218) is the cleanest neutral path (used by OpenUSD, OpenChain) and the closest structural fit for "URML as JDF project under LF". These two are the headline Sub-wave B targets.
- **Israeli founder access is asymmetric.** IL-domestic (IIA, SII) is single-email easy. Five Eyes (UK Robotics Growth Partnership, AUKUS, NATO STO, DSTL, DSTG, DRDC) is locked or partial. EU (euRobotics, ADRA, JTC 21, DIN/DKE, AFNOR) is open per Horizon Europe associated-country status. NATO STO requires member-nomination Israel is not eligible for as partner.
- **Defense-export-controlled bodies are net-negative for URML's open posture.** SIBAT + Hoshen + AUKUS + NATO STO + Five-Eyes-defense-research-agencies all carry architectural conflict with URML's Apache-2.0 + offline-execution + no-cloud commitments. Do not romanticize the access; the cost is the open posture.
- **The US federal slice is much smaller than it looks.** Of 22 federal candidates investigated, only 2 (NIST EL email, ASTM F45.04 paper) are actionable now in URML's current form. 3 more (CAISI, FAA, NHTSA) are docket-watch with no currently-open window. The other 17 are wrong-shape (regulatory, not standards-shaping), US-domicile-gated, or premature. Sub-wave B for US-federal is intentionally small.
- **Standards-body classical channels (ANSI, IEC, ASME, INCITS, ISO TC 299) are wrong for Phase 1.** They require membership dues, national-body sponsorship, and committee-email outreach. URML doesn't have the operational machinery yet. Defer to Phase 2 when measured response-time data supports formal SDO submission per the public-commitments discipline.
- **No prior-Move overlap** with any Tier-A or Tier-B Move-17 target except Class 1 prior-engaged duplicates (OSRF, ROS 2 core, Eclipse projects already engaged in Move-16, Dronecode covered via constituent engagement) — all explicitly noted in Tier C.

## Next steps

1. **This setup PR** ships: `outreach-move17.yaml` (22 Tier A + Tier B rows), this research file, `posts-move17.md` skeleton (5 Sub-wave A entries with Body TBD), `founder-actions-move17.md` skeleton (13 Sub-wave B entries with Draft TBD).
2. **Subsequent sessions**: draft RFCs 0212-0226 (15 RFCs likely 3 batches: Sub-wave A 5 RFCs; Sub-wave B-with-RFC 10 RFCs split across 2 batches).
3. **Sub-wave A posting**: bulk `gh issue create` after RFCs + bodies land. Same pattern as Moves 10-16.
4. **Sub-wave B sending**: assistant prepares verbatim drafts in `founder-actions-move17.md`. Founder reviews, refines, and sends each through its proper channel under his maintainer identity (email account, ASTM membership account, IIA application portal, OECD submission form, etc.).
5. **Sub-wave C tracking**: ledger rows updated on docket-window-open events as RFI cycles surface.
