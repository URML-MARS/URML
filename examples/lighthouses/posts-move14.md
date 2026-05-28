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

# Move #14 post bodies — mobile manipulators + commercial humanoids (Theme B)

Copy-paste-ready Issue / Discussion bodies for the Move #14 outreach. **Wave shape**: 7 verified Theme B targets (4 Tier A + 3 Tier B), verified 2026-05-28. RFC numbers 0184-0190.

Ledger state: [`outreach-move14.yaml`](outreach-move14.yaml). Full research audit: [`move14-research-2026-05-28.md`](move14-research-2026-05-28.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("fourteen outreach waves to date") are fine. Naming the specific orgs that responded is not.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #14 post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Schema-extension flags.** Move #14 surfaces multiple v0.1 schema gaps that should be opened as Spec RFCs in parallel:

- **Mobile-manipulator topology declaration** (Hello Robot RFC-0184: mobile-base + arm + pan-tilt-head composition; Fetch RFC-0188 similar).
- **Humanoid platform declaration refinement** (1X EVE RFC-0187 refines URML's existing `neo_biped` fixture upstream).
- **Cobot-arm precision-class declaration** (Franka RFC-0185; sibling to Move-1 cobot vendors).
- **Acquisition-era governance declaration** (Fetch / Zebra RFC-0188: maintaining the manifest pin across OEM acquisitions).

Each is a separate Spec RFC; URML's outreach RFCs ship with the v0.1 `custom` measurement_type / mobility-class escape-hatch and reference the queued Spec RFC.

**Four rows carry license-clarification asks** in their per-target question lists:

- RFC-0184 Hello Robot (no SPDX visible).
- RFC-0188 Fetch Robotics (no SPDX visible, post-Zebra-acquisition).
- RFC-0189 PAL Robotics TIAGo (no SPDX visible).
- (Kinova RFC-0186 is BSD-3-Clause + TRI HSR RFC-0190 is BSD-3-Clause-Clear; no ask.)

---

## Tier A — 4 vendor-direct targets

### Mobile manipulators (3)

### RFC-0184: Hello Robot (Stretch)
**Post to**: https://github.com/hello-robot/stretch_ros2/issues/new (Issues enabled). Body TBD when RFC drafts. **License-clarification ask.**

### RFC-0185: Franka Robotics (Panda / FR3)
**Post to**: https://github.com/frankaemika/franka_ros2/issues/new (Issues enabled). Body TBD. Deferred from Move-13 Theme C — correct layer here.

### RFC-0186: Kinova Robotics (Jaco / Movo)
**Post to**: https://github.com/Kinovarobotics/kinova-ros/issues/new (Issues enabled, stale >1.5yr). Body TBD. Engagement is reactivating-nudge + ROS 2 successor question.

### Commercial humanoid (1)

### RFC-0187: 1X Technologies (EVE / NEO)
**Post to**: https://github.com/1x-technologies/eve-ros2-examples/issues/new (Issues enabled). Body TBD. **The only commercial humanoid OEM with vendor-direct active public robot code in Move-14 research.**

---

## Tier B — 3 research-collab / cross-citation targets

### RFC-0188: Fetch Robotics (Fetch + Freight)
**Post to**: https://github.com/fetchrobotics/fetch_ros/issues/new (Issues enabled, stale >1.5yr post-Zebra-acquisition). Body TBD. **License-clarification ask + post-acquisition-governance question.**

### RFC-0189: PAL Robotics (TIAGo / TALOS / ARI)
**Post to**: https://github.com/pal-robotics/tiago_tutorials/issues/new (Issues enabled, stale >2yr). Body TBD. **License-clarification ask + canonical-engagement-surface ask** (PAL has multiple repos; tutorials may not be the right one).

### RFC-0190: Toyota Research HSR
**Post to**: https://github.com/ToyotaResearchInstitute/hsr_description/issues/new (Issues enabled, stale >2yr). Body TBD. **Canonical-engagement-surface ask** (research-org vs Toyota-Japan-OEM split). Cross-citation framing.

---

## Tier C (6) — recorded in research file, NOT engaged

See [`move14-research-2026-05-28.md`](move14-research-2026-05-28.md) for the full Tier-C list with exclusion causes:

- **0 public repos × 2:** Apptronik (Apollo humanoid closed), Sanctuary AI (Phoenix humanoid closed).
- **No humanoid robot code × 2:** Figure AI (55 build-tools repos, no humanoid stack), Tesla Optimus (legacy Maven repos, no Optimus code).
- **Archived primary surface × 1:** Agility Robotics (cassie-doc archived; no active humanoid code).
- **Already engaged × 1:** Boston Dynamics Atlas (no separate repo; Spot engaged via Move-2 RFC-0043).

URML's existing humanoid manifest fixtures (apollo_biped, digit_biped, figure_biped, neo_biped, optimus_biped) exist as URML-side declarations because the upstream engagement surfaces don't exist; private-channel engagement is outside URML's outreach pattern. The Tier C list is URML's honest record of this market-shape reality.
