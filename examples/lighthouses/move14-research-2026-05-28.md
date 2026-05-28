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

# Move-14 research — mobile manipulators + commercial humanoids (Theme B)

**Research date**: 2026-05-28.
**Audience**: founder review before Move-14 RFCs draft.
**Method**: two Explore agents in parallel covered mobile-manipulator and commercial-humanoid categories, cross-checked each candidate against all prior ledgers (Moves 1-13), verified via `gh repo view` + `gh api orgs/...` for `isArchived: false`, license, recency, Issues, origin.
**Outcome**: **7 verified engageable candidates** (4 Tier A + 3 Tier B); **6 Tier C excluded with cause**.

## Why this wave is smaller than prior moves

Theme B exposes a honest fact about the commercial humanoid market: **most humanoid OEMs are closed-source**. Apptronik, Sanctuary AI, Figure AI, Tesla Optimus — all have GitHub presence (or org placeholders) without any humanoid robot code published. Agility Robotics' primary GitHub surface is archived. Boston Dynamics Atlas has no separate GitHub repo (Spot was engaged via RFC-0043 in Move #2).

The mobile-manipulator side is healthier but the active surfaces are narrower than perception (Move #10) or actuators/embedded (Move #13). Hello Robot (Stretch), Franka, Kinova, 1X Technologies, plus three stale-but-engageable rows are the realistic Move-14 set.

URML's outreach engages where the engageable surface exists. The Tier C exclusion list is the audit trail showing this is a market-shape reality, not URML missing targets.

## Tier A (4) — vendor-direct, adapter-eligible

### Mobile manipulators (3)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `hello-robot-stretch` | [hello-robot/stretch_ros2](https://github.com/hello-robot/stretch_ros2) | None visible (clarification ask) | 120 | 2026-05-26 | US | Vendor-direct ROS 2 interface for Stretch mobile manipulator. MIT-spinoff, active (2 days from cutoff). License-clarification ask. |
| `frankaemika-franka-ros2` | [frankaemika/franka_ros2](https://github.com/frankaemika/franka_ros2) | Apache-2.0 | 337 | 2026-05-19 | DE Munich | Vendor-direct ROS 2 driver for Panda / FR3 cobot arm. Active (9 days). **Deferred from Move-13 Theme C — wrong layer there; correct layer here.** |
| `kinovarobotics-kinova-ros` | [Kinovarobotics/kinova-ros](https://github.com/Kinovarobotics/kinova-ros) | BSD-3-Clause | 410 | 2024-08-12 | CA Montreal | Vendor-direct ROS driver for Jaco / Movo cobot arms. Stale 654 days but large star count signals deployed-fleet adoption. Engagement may be reactivating nudge. |

### Commercial humanoids (1)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `1x-technologies-eve-ros2-examples` | [1x-technologies/eve-ros2-examples](https://github.com/1x-technologies/eve-ros2-examples) | Apache-2.0 | 6 | 2026-01-12 | NO Oslo | Vendor-direct ROS 2 examples for 1X EVE humanoid. Norway NATO+. The only commercial humanoid OEM with vendor-direct active public robot code found. |

## Tier B (3) — research-collab / cross-citation framing

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `fetchrobotics-fetch-ros` | [fetchrobotics/fetch_ros](https://github.com/fetchrobotics/fetch_ros) | None visible (clarification ask) | 202 | 2024-08-20 | US (now Zebra) | Stale 646 days; Fetch acquired by Zebra Technologies 2023. License-clarification ask. Engagement to check post-acquisition governance + URML-fit. |
| `pal-robotics-tiago-tutorials` | [pal-robotics/tiago_tutorials](https://github.com/pal-robotics/tiago_tutorials) | None visible (clarification ask) | 87 | 2024-02-29 | ES Barcelona | Stale 818 days on tutorials repo. PAL Robotics has multiple repos — engagement asks for the canonical TIAGo / TALOS / ARI engagement surface. License-clarification ask. |
| `toyota-research-hsr-description` | [ToyotaResearchInstitute/hsr_description](https://github.com/ToyotaResearchInstitute/hsr_description) | BSD-3-Clause-Clear | 37 | 2024-05-05 | US (TRI) | URDF/mesh asset repo; stale 753 days. TRI is research-direct, not Toyota Japan OEM. Engagement asks for the primary HSR engagement channel. |

## Tier C — excluded with cause (the closed-humanoid honest record)

| Slug | Org / Repo | Cause |
|---|---|---|
| `apptronik-public` | Apptronik-Public org | **0 public repos.** Apollo humanoid is closed; "Building Robots for Humans" tagline unfulfilled on GitHub. URML's manifest already includes an `apollo_biped` fixture per RFC-0009 — engagement requires private channels (not URML's pattern). |
| `sanctuary-ai` | Sanctuary-AI org | **0 public repos.** Phoenix humanoid closed. Canada BC; would pass policy if engageable. |
| `figure-ai` | figurerobotics user account, 55 repos | **No humanoid robot code.** All 55 public repos are build-tools (Bazel, DDS, vision libraries, CASADi, COLMAP). Robot stack remains private. URML's manifest already includes a `figure_biped` fixture per RFC-0009 — engagement requires private channels. |
| `tesla-optimus` | tesla org, 20 repos | **No Optimus code.** Public org contains legacy Maven / IDE tooling. URML's manifest already includes an `optimus_biped` fixture per RFC-0009 — engagement requires private channels. |
| `agility-robotics-cassie-doc` | agilityrobotics/cassie-doc | **Primary engageable surface archived.** Cassie-doc archived; no active robot code repos at agilityrobotics org. URML's manifest already includes a `digit_biped` fixture per RFC-0009. (Founder's partnership-target list noted Agility specifically; private channels are the path.) |
| `boston-dynamics-atlas` | boston-dynamics org | **No Atlas-specific repo.** spot-sdk is the only public engageable surface, and that was engaged via Move #2 RFC-0043 (Spot). Atlas remains closed. |

## Distribution

| Class | Tier A | Tier B | Excluded |
|---|---|---|---|
| Mobile manipulators | 3 (Hello Robot, Franka, Kinova) | 3 (Fetch, PAL TIAGo, Toyota HSR) | 0 |
| Commercial humanoids | 1 (1X Technologies) | 0 | 6 (Apptronik, Sanctuary, Figure, Tesla, Agility, BD Atlas) |
| **Total** | **4** | **3** | **6** |

## Reserved RFC range

RFCs 0184-0190 reserved for Move #14 in `docs/rfcs/README.md`. Move-13 ends at RFC-0183.

## Open license-clarification asks

Four rows carry license-clarification asks in their unresolved-questions list:

- `hello-robot/stretch_ros2`: no SPDX visible — request explicit declaration.
- `fetchrobotics/fetch_ros`: no SPDX visible (acquisition-era staleness) — request declaration; verify post-Zebra governance.
- `pal-robotics/tiago_tutorials`: no SPDX visible — request declaration + canonical engagement-surface guidance.
- (`Kinovarobotics/kinova-ros` is BSD-3-Clause; no ask there.)

## Honest framing notes for the per-RFC bodies

- **Commercial-humanoid closed-source reality.** RFCs 0184 (1X Technologies) and the Tier C audit honestly acknowledge that URML's existing humanoid manifest fixtures (apollo_biped, digit_biped, figure_biped, neo_biped, optimus_biped) exist as URML-side declarations without corresponding upstream engagement, because the upstream surfaces aren't engageable. URML doesn't pretend otherwise.
- **Mobile-manipulator staleness clusters.** Fetch, PAL, TRI HSR are all stale by URML's 6-month rule. URML's engagement is partly a reactivating nudge, partly a pulse-check on whether the canonical engagement surface has moved.
- **Franka double-engagement framing.** RFC-0182 STMicroelectronics in Move-13 stayed at chip-class engagement; Franka was deferred from Move-13 Theme C because cobot OEM ≠ actuator vendor. RFC-0185 (Franka) is the correct-layer engagement.

## Next steps

1. Founder review of this research file.
2. Setup PR ships: `outreach-move14.yaml` + `posts-move14.md` skeleton.
3. Subsequent sessions: draft RFCs 0184-0190 (likely 1-2 batches given the smaller wave).
4. Posting follows Move-10/11/13 pattern: founder review of bodies, then assistant posts via `gh` with explicit "go" authorization.
