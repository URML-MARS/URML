---
rfc: 0090
title: University of Tokyo JSK Robotics Lab integration, research-collab proposal to Masayuki Inaba + Kei Okada
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

# RFC-0090: University of Tokyo JSK Robotics Lab integration, research-collab proposal to Masayuki Inaba + Kei Okada

## Summary

URML proposes alignment with the University of Tokyo JSK Robotics Laboratory via the [`jsk-ros-pkg` GitHub org](https://github.com/jsk-ros-pkg) (34 public repos; led by Prof. Masayuki Inaba and Prof. Kei Okada). The ask is **research-collab** anchored on the most mature academic-ROS surface in Asia: JSK has been publishing ROS packages for over 20 years and continues active development. No spec change on URML's side. Eleventh Move #6 RFC.

## Motivation

JSK Lab is **the** longest-running academic ROS contributor in Asia. The `jsk_recognition`, `jsk_visualization`, `jsk_aerial_robot`, and `jsk_robot` packages are foundational dependencies for hundreds of Asian academic and industrial robotics deployments. URML's outreach to JSK is, more than any other Move #6 target, an outreach to **20+ years of accumulated ROS-academic practice**.

Verified surface (2026-05-25):
- 34 public repos in `jsk-ros-pkg`.
- Top-starred: `jsk_visualization` (357 stars, "jsk visualization ros packages", C++), `jsk_recognition` (289 stars, "JSK perception ROS packages", C++, Issues enabled with 70 open, last commit 2026-02-20), `jsk_robot` (80 stars, Common Lisp), `coral_usb_ros` (57 stars, "ROS package for Coral Edge TPU USB Accelerator", Python), `jsk_aerial_robot` (54 stars, C, multi-rotor / hydrus / dragon platforms).
- License pattern: BSD-3-Clause (where explicit).
- Active development on `jsk_recognition` as of 2026-02-20.
- Amazon Picking Challenge participation history (industrial collaboration precedent).

URML's specific value for JSK:
- **20+ years of ROS practice as a teaching artifact.** URML primitive vocabulary as a complementary teaching surface above the ROS-package-level work JSK has accumulated. UTokyo's robotics curriculum is a candidate audience.
- **`jsk_recognition` cross-link.** URML's `measure` primitive consuming JSK perception outputs is composition, not competition.
- **EusLisp + URML composition.** JSK Lab famously uses Common Lisp (EusLisp / roseus) for high-level robot intent expression. URML's primitive vocabulary at the intent layer can compose with EusLisp's symbolic reasoning at the planning layer. A documented note is paper-worthy.
- **Aerial-robotics cross-link.** `jsk_aerial_robot` is the most cited academic-aerial-multi-rotor research codebase from Asia. URML's [RFC-0041 (ArduPilot)](0041-ardupilot-integration.md) outreach is the institutional substrate bridge.

## Detailed design (light, research-collab)

URML proposes:

1. **`jsk_recognition` cross-link.** Documented note that URML's `measure` primitive consumes `jsk_recognition` perception outputs. The cross-link is composition.
2. **EusLisp + URML composition.** A documented mapping or example showing URML primitives at the intent layer composed with EusLisp / roseus at the planning layer. Paper-worthy if pursued.
3. **UTokyo robotics curriculum integration.** URML primitive vocabulary as a teaching artifact in JSK Lab's practicum courses.
4. **`jsk_aerial_robot` cross-link.** Documented note that URML's aerial-substrate adapter (planned upstream of [RFC-0041 (ArduPilot)](0041-ardupilot-integration.md)) can target `jsk_aerial_robot`-class platforms.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **20+ years of accumulated ROS practice is a high bar.** URML's primitive vocabulary is young (v0.1.0); JSK has decades of ROS pedagogy. URML's value is the substrate-neutral layer above, not a replacement.
- **EusLisp is a niche language.** Composition with EusLisp / roseus is technically interesting but the audience is narrow (mostly Tokyo + JSK alumni labs).
- **Japan academic-calendar cadence.** Japanese academic year runs April-March; engagement window may not align with URML's standard 14-day wait pattern.
- **Language fluency.** JSK's primary working language is Japanese; URML's RFC is in English. URML's RFC body is English-only; the outreach respects that the maintainers may prefer Japanese for substantive technical discussion (URML founder will accept either).

## Alternatives considered

1. **Ship a `JskRosAdapter` consuming `jsk_recognition`.** Rejected. The composition shape is a research-collab question first.
2. **Target a single JSK repo (e.g., `jsk_aerial_robot` only) instead of the lab.** Rejected. The lab is the institutional surface; focusing on one repo misses the cross-link breadth.

## Prior art

- `jsk-ros-pkg` GitHub org (34 public repos).
- `jsk-ros-pkg/jsk_visualization` (357 stars), `jsk_recognition` (289 stars), `jsk_robot` (80 stars), `coral_usb_ros` (57 stars), `jsk_aerial_robot` (54 stars).
- JSK Lab website: `jsk.t.u-tokyo.ac.jp`.
- EusLisp / roseus: the lab's high-level robot intent language.
- Amazon Picking Challenge research outputs.
- [RFC-0041](0041-ardupilot-integration.md): URML's ArduPilot Move #2 outreach; aerial substrate institutional bridge.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles.

## Unresolved questions

For Prof. Inaba + Prof. Okada + JSK Lab team:

1. **`jsk_recognition` + URML composition.** Is documenting URML's `measure` primitive consuming `jsk_recognition` outputs a useful direction?
2. **EusLisp + URML composition.** Is there interest in a documented example showing URML primitives at intent layer composed with EusLisp / roseus at planning layer?
3. **`jsk_aerial_robot` cross-link.** Is the aerial codebase a candidate URML substrate target via the ArduPilot bridge ([RFC-0041](0041-ardupilot-integration.md))?
4. **Coursework integration.** Is JSK Lab's practicum a candidate course for URML primitive vocabulary?
5. **Language fluency.** Substantive technical discussion in Japanese or English. Maintainer preference?
6. **Conformance lane.** Open to a URML conformance line on `jsk_recognition` README or `jsk.t.u-tokyo.ac.jp`?
7. **Anything else.**

## Implementation note

RFC-0090 ships as a single RFC document PR. No code in this PR. Research-collab framing. Eleventh Move #6 RFC; the most mature Asian academic ROS surface. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`jsk-ros-pkg/jsk_recognition` has Issues enabled with 70 open at time of writing (last commit 2026-02-20; verified 2026-05-25). URML's planned channel: open a single Issue on `jsk-ros-pkg/jsk_recognition` or `jsk_visualization` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Inaba + Prof. Okada via `jsk.t.u-tokyo.ac.jp`.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] 20+ years of ROS practice context surfaced.
- [x] EusLisp composition flagged honestly as niche.
- [x] Language-fluency question raised; maintainer preference respected.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, high bar, EusLisp niche, academic cadence, language fluency).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: JP`; default policy passes (US treaty ally).
- [x] CLAUDE.md compliance check passed.
