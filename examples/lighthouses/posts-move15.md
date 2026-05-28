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

# Move #15 post bodies — niche verticals (surgical, construction, delivery, warehouse) (Theme D)

Copy-paste-ready Issue bodies for the Move #15 outreach. **Wave shape**: 5 verified Theme D targets (3 Tier A + 2 Tier B), verified 2026-05-28. RFC numbers 0191-0195. **The smallest URML wave so far** — reflects the closed-vertical market reality (18 Tier C exclusions documented).

Ledger state: [`outreach-move15.yaml`](outreach-move15.yaml). Full research audit: [`move15-research-2026-05-28.md`](move15-research-2026-05-28.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("fifteen outreach waves to date") are fine.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #15 post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Schema-extension flags.** Move #15 surfaces multiple v0.1 schema gaps:

- **Surgical-class platform + telesurgery-control declarations** (JHU dVRK RFC-0191; URML's first surgical RFC).
- **Assistive / rehabilitation / prosthetic-application-class declaration** (IIT iCub RFC-0192; shared with Move-14 RFC-0186 Kinova).
- **Sidewalk-delivery / urban-delivery platform-class declaration** (Starship RFC-0193; URML's first delivery RFC).
- **Alternate-substrate middleware declaration** (YARP RFC-0194; sibling to URML's existing ros2-runtime).

Each is a separate Spec RFC; URML's outreach RFCs ship with the v0.1 `custom` escape-hatch and reference the queued Spec RFC.

**One license-clarification ask** (RFC-0191 JHU dVRK): CISST custom license is permissive but non-SPDX.

---

## Tier A — 3 research-lab-direct / vendor-direct targets

### RFC-0191: JHU dVRK (Da Vinci Research Kit)
**Post to:** https://github.com/jhu-dvrk/sawIntuitiveResearchKit/issues/new. Body TBD when RFC drafts. **License-clarification ask** (CISST custom permissive → OSI declaration). URML's first surgical / medical RFC.

### RFC-0192: IIT iCub
**Post to:** https://github.com/robotology/icub-main/issues/new. Body TBD. Medical-relevant humanoid (assistive / prosthetic / rehabilitation research angle). The first IIT engagement; sibling RFC-0194 (YARP) at the middleware layer.

### RFC-0193: Starship Technologies (bag_rdr)
**Post to:** https://github.com/starship-technologies/bag_rdr/issues/new. Body TBD. URML's first delivery-robot RFC. Engagement at the ROS-bag infrastructure layer (full robot stack closed).

---

## Tier B — 2 research-collab / cross-citation targets

### RFC-0194: IIT YARP middleware
**Post to:** https://github.com/robotology/yarp/issues/new. Body TBD. Alternate-substrate middleware sibling to URML's existing ros2-runtime. Cross-citation framing pending substrate-declaration Spec RFC.

### RFC-0195: Serve Robotics (Model-Optimizer)
**Post to:** https://github.com/serve-robotics/Model-Optimizer/issues/new. Body TBD. Vendor-affiliated but fork-heavy public surface. Light-touch engagement; sibling to RFC-0193 Starship.

---

## Tier C (18) — recorded in research file, NOT engaged

See [`move15-research-2026-05-28.md`](move15-research-2026-05-28.md) for the full Tier-C list documenting the closed-vertical market reality:

- **Surgical OEMs × 4:** Intuitive Surgical, Auris Health / J&J, CMR Surgical, Stryker Mako — all closed.
- **Construction OEMs × 5:** Built Robotics, Dusty Robotics, Canvas Construction, Civ Robotics, Hilti — **ZERO engageable construction candidates.**
- **Delivery OEMs × 3:** Nuro, Kiwibot, Cartken — no public GitHub.
- **Warehouse AMR × 6:** Fetch Robotics (already engaged Move-14 RFC-0188), Clearpath Robotics (already engaged Move-5 RFC-0072), Open-RMF (already engaged Move-2 RFC-0053), MiR / Locus / Vecna / Symbotic / OTTO Motors / 6 River Systems (all closed), Greyorange (Erlang ops only, no robotics-class surface), Geek+ (PRC-excluded).

The Tier C audit is URML's honest record that the niche-vertical market is predominantly commercial-closed; URML's wave engages where the surface exists.
