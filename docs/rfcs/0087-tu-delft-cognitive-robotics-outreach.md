---
rfc: 0087
title: TU Delft Cognitive Robotics integration, research-collab proposal to Martijn Wisse
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-25
updated: 2026-05-25
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

# RFC-0087: TU Delft Cognitive Robotics integration, research-collab proposal to Martijn Wisse

## Summary

URML proposes alignment with the TU Delft Cognitive Robotics group via the [`tud-cor` GitHub org](https://github.com/tud-cor) (40 public repos; led by Prof. Martijn Wisse, biorobotics). The ask is **research-collab** focused on Delft's bio-inspired locomotion + dexterous manipulation work plus the established Mobile Robotics teaching pipeline. No spec change on URML's side. Eighth Move #6 RFC.

## Motivation

TU Delft Cognitive Robotics anchors **bio-inspired locomotion + energy-efficient design + dexterous manipulation** at URML's Move #6 wave. The lab teaches Mobile Robotics (Kalman filtering, navigation) and Robotics fundamentals (Python, Arduino) in a long-running EU master's-level curriculum.

Verified surface (2026-05-25):
- `tud-cor`: 40 public repos.
- Top-starred: `FS19_modROS` (51 stars, partial ROS1 integration for FarmSim19, Lua), `ur5_coppeliasim_roscontrol` (8 stars), `coppeliasim_ros_control` (6 stars), `jackal_active_inference_versus_kalman_filter` (4 stars), `acado` (3 stars).
- License pattern: Apache-2.0 predominant; MIT also represented.
- Last commit on `FS19_modROS`: 2024-01-28 (somewhat stale).
- Mobile Robotics + Robotics fundamentals are the lab-affiliated courses.

URML's specific value for TU Delft CoR:
- **Coursework integration.** TU Delft's Mobile Robotics + Robotics fundamentals are exactly the audience URML's primitive vocabulary serves. A documented module on substrate-neutral programming integrates cleanly into existing curricula.
- **Bio-inspired locomotion cross-link.** Wisse's energy-efficient bipedal work complements URML's [RFC-0009 (legged-humanoid mobility)](0009-legged-humanoid-mobility.md) capability schema.
- **CoppeliaSim cross-link.** URML's substrate-Protocol abstraction could compose with CoppeliaSim via `coppeliasim_ros_control`. CoppeliaSim is not currently a URML substrate (URML has Isaac via [RFC-0050](0050-nvidia-isaac-lab-integration.md), MuJoCo via [RFC-0060](0060-mujoco-integration.md), Gazebo via [RFC-0037](0037-osrf-gazebo-integration.md)); adding CoppeliaSim is a possible Spec RFC.

## Detailed design (light, research-collab)

URML proposes:

1. **Coursework integration.** URML primitive vocabulary as a teaching artifact in TU Delft Mobile Robotics or Robotics fundamentals courses.
2. **Bio-inspired locomotion cross-link.** A documented mapping from Wisse's bipedal-walker controllers to URML manifest entries for [RFC-0009](0009-legged-humanoid-mobility.md).
3. **CoppeliaSim Spec RFC question.** TU Delft maintains the most-cited public ROS / CoppeliaSim integration in the academic literature. Is CoppeliaSim a future URML substrate worth a Spec RFC?

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **`tud-cor` repo cadence is uneven.** Top-starred repo's last commit is 2024-01-28; some repos may be in maintenance mode. URML's RFC needs maintainer input on which repos are first-class.
- **CoppeliaSim is closed-source proprietary.** Adding CoppeliaSim as a URML substrate would conflict with URML's open-core posture for the runtime; the cross-link works only at the simulation-target level, not at the URML-shipping-adapter level.
- **EU academic-calendar cadence.** Summer break across May-August at TU Delft; engagement window may extend.

## Alternatives considered

1. **Ship a `TuDelftAdapter` against `coppeliasim_ros_control`.** Rejected. CoppeliaSim's proprietary nature plus the composition-not-substrate framing make adapter-shipping the wrong shape.
2. **Skip CoppeliaSim conversation entirely.** Rejected. The TU Delft CoppeliaSim work is the most-cited academic ROS/CoppeliaSim integration; the conversation is worth having.

## Prior art

- `tud-cor` GitHub org (40 public repos, Apache-2.0 predominant).
- `tud-cor/FS19_modROS` (51 stars), `ur5_coppeliasim_roscontrol` (8 stars), `coppeliasim_ros_control` (6 stars).
- TU Delft Cognitive Robotics website: `tudelft.nl/en/me/about/departments/cognitive-robotics-cor`.
- Mobile Robotics + Robotics fundamentals course pages.
- [RFC-0009](0009-legged-humanoid-mobility.md), [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md).
- [RFC-0037](0037-osrf-gazebo-integration.md), [RFC-0050](0050-nvidia-isaac-lab-integration.md), [RFC-0060](0060-mujoco-integration.md): existing URML simulation-target outreach.

## Unresolved questions

For Prof. Wisse + TU Delft CoR team:

1. **Canonical repos.** Which `tud-cor` repos are the first-class URML integration candidates today, given some repos may be in maintenance mode?
2. **Coursework integration.** Is Mobile Robotics or Robotics fundamentals a candidate course for URML primitive vocabulary?
3. **Bio-inspired locomotion cross-link.** Is there interest in a documented mapping from Wisse's bipedal controllers to URML manifest entries?
4. **CoppeliaSim Spec RFC.** Is CoppeliaSim worth a future URML Spec RFC as a simulation target? If so, what's the right composition shape?
5. **Conformance lane.** Open to a URML conformance line on `tud-cor` repo READMEs?
6. **Anything else.**

## Implementation note

RFC-0087 ships as a single RFC document PR. No code in this PR. Research-collab framing. Eighth Move #6 RFC. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–6 from "Unresolved questions" above.

## How to respond

`tud-cor/FS19_modROS` has Issues enabled (15 total issues, 8 need help; verified 2026-05-25). URML's planned channel: open a single Issue on `tud-cor/FS19_modROS` or another `tud-cor` repo the maintainers identify as canonical, labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Wisse via `M.Wisse@tudelft.nl` or the lab website.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] Motivation grounded in verified `tud-cor` surface.
- [x] CoppeliaSim Spec RFC question surfaced; open-core posture preserved.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, uneven repo cadence, CoppeliaSim closed-source, EU academic cadence).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: NL`; default policy passes.
- [x] CLAUDE.md compliance check passed.
