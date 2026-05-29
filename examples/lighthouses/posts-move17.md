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

Bodies follow the [AGENTS.md](../../AGENTS.md) outreach-post-structure rules added after the
Nav2 close (2026-05-29, SteveMacenski closed [navigation2#6184](https://github.com/ros-navigation/navigation2/issues/6184)
as too dense to read): concrete hook first, one or two real questions, light ask stated up
front, full RFC linked as optional depth, under a two-minute read, zero em-dashes.

**Posting priority and honest fit.** These targets are not equal. Two have a genuine,
answerable technical question and are worth posting. Three are cross-citation / README-link
asks, which is the low-value shape a maintainer reads as link-building. Recommendation:

- **Post:** RFC-0214 (OPC UA, real license + mapping question) and RFC-0215 (SLSA, real
  composite-substrate design question). Lead the wave with 0214.
- **Hold pending founder call:** RFC-0213 (ELISA), RFC-0216 (Scorecard), RFC-0212 (SDV).
  Each carries a real risk of a Nav2-shape "this is noise" close. RFC-0216 is better served
  by just adopting the Scorecard Action on our repos (no maintainer ask needed); RFC-0212 is
  the weakest and is the one I would not post cold. Drafts are below if the founder wants
  them anyway.

### RFC-0214: OPC Foundation UA-Nodeset (lead with this one)
**Post to:** https://github.com/OPCFoundation/UA-Nodeset/issues/new (Issues enabled).
**Title:** URML (open robot-intent language): declaring OPC UA Robotics capabilities, plus a license question

```
Hi OPC Foundation maintainers,

URML (urml.dev) is a small open language for describing robot intent. On an industrial arm a
user writes `pick_from(bin_a)`; URML checks it against the robot's declared capabilities, then
dispatches through the target's command interface. On an OPC-UA-Robotics deployment, that
target is the OPC UA Robotics NodeSet. Apache-2.0, no change to your spec proposed, nothing
for you to maintain.

Two small things:

1. The UA-Nodeset repo doesn't seem to declare an OSI license on its surface. Is that
   intentional, or is there a license you'd point to? It decides whether a downstream project
   can ship an adapter that references the NodeSet.
2. If we wanted to write "this robot's capabilities map to these OPC UA Robotics nodes" into
   our manifest, is there a convention you'd want us to follow, or is that new ground?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0214-opc-foundation-ua-nodeset-outreach.md

Thanks for keeping the UA Robotics companion spec a real, usable standard.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

### RFC-0215: OpenSSF SLSA
**Post to:** https://github.com/slsa-framework/slsa/issues/new (Issues enabled).
**Title:** URML: how should a manifest record a composite substrate's SLSA level?

```
Hi SLSA maintainers,

URML (urml.dev) is a small open language for describing robot intent. It validates a program
against the target robot's declared capabilities before anything runs. We want that manifest
to record provenance for the software substrate underneath (ROS 2, PX4, and so on), and SLSA
is the framework we'd point at. Apache-2.0, no change to SLSA proposed.

One real question. A robotics substrate is usually many packages at once (ROS 2 alone is
rclcpp + rclpy + rmw + plugins). If a manifest wants to say "this substrate is SLSA L3," what
shape would you recommend for a composite like that: a single level, a per-component map, or
an attestation URL we resolve at validate time? And for verification, would you point us at
slsa-verifier, the in-toto verifier, or something else?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0215-openssf-slsa-outreach.md

Thanks for SLSA.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

### RFC-0213: ELISA wg-automotive (hold; draft if founder wants)
**Post to:** https://github.com/elisa-tech/wg-automotive/issues/new (Issues enabled).
**Title:** URML: are the wg-automotive / Safety_Architecture_WG calls open to non-member attendees?

```
Hi ELISA wg-automotive maintainers,

URML (urml.dev) is a small open language for describing robot intent. It only lets a program
run after a static check against the robot's declared safety envelope. That "execute only
after verification" boundary is the part of our design that overlaps with ELISA's
safe-construction-from-Linux work, which is why I'm asking rather than reinventing it.
Apache-2.0, nothing requested beyond a pointer.

One question: are the wg-automotive (or Safety_Architecture_WG) calls open to non-member
attendees? I'd like to follow the safety-Linux work that touches our reference runtimes,
without ever implying URML is certified, which it isn't.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0213-elisa-wg-automotive-outreach.md

Thanks for the safety-Linux work.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

### RFC-0216: OpenSSF Scorecard (hold; prefer just adopting the Action)
**Post to:** https://github.com/ossf/scorecard/issues/new (Issues enabled).
**Title:** URML: single Scorecard run vs per-repo for a multi-runtime project?

```
Hi Scorecard maintainers,

URML (urml.dev) is a small open language for describing robot intent. We're adopting the
Scorecard GitHub Action on our repos to publish security posture in a format downstream users
can check. No change requested from you.

One question, only if it's quick: for a project that will eventually span several runtime
repos (one per robot substrate), do you recommend a single Scorecard run at the top level or
one per repo? Anything else we'll take from the docs.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0216-openssf-scorecard-outreach.md

Thanks for Scorecard.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

### RFC-0212: Eclipse SDV Blueprints (weakest; recommend not posting cold)
**Post to:** https://github.com/eclipse-sdv-blueprints/blueprints-website/issues/new (Issues enabled).
**Title:** URML: is a substrate-neutral robot-intent layer in scope as related art for the aerospace blueprint extension?

```
Hi Eclipse SDV maintainers,

URML (urml.dev) is a small open language for describing robot intent, Apache-2.0. Our drone
and industrial-arm runtime tracks hit the same safe-composition problems your blueprints
formalize for vehicles, and we'd rather reference your patterns than reinvent them. Nothing
requested beyond whether that's welcome.

One question: is there a working-group surface where a substrate-neutral robotics-intent layer
(our drone profile) is in scope as related art for the aerospace blueprint extension, or is
that outside SDV's automotive core?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0212-eclipse-sdv-blueprints-outreach.md

Thanks for the SDV blueprints.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

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
