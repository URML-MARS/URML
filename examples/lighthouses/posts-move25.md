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

# Move #25 post bodies: SLAM / state estimation (round 2)

Copy-paste-ready bodies for the 10 Tier-A targets. Deferred headliners
(FAST-LIO/Point-LIO, LIO-SAM/LVI-SAM, VINS-Fusion) and folded siblings
(hdl_graph_slam under GLIM) plus Kalibr / maplab are recorded in
[`outreach-move25.yaml`](outreach-move25.yaml), not posted (stale / single-author,
low-yield and AI-content-close-prone).

Shared framing, in every body: URML does NOT do SLAM. URML declares `frames`
and `declared_locations`; the target produces the pose / map estimate those are
expressed against; URML consumes the estimate and validates intent before
dispatch. That honesty (we sit above you, we do not reimplement you) is
deliberate and should keep these from reading as a land-grab.

Bodies follow the [AGENTS.md](../../AGENTS.md) outreach-post-structure rules:
concrete hook, "nothing for you to maintain" up front, one or two real
questions, RFC linked as optional depth, under a two-minute read, zero
em-dashes. VIBE disclosure line last.

All 10 repos have Issues enabled (verified 2026-06-02), so each is a single Issue.

**Posting status:** all 10 POSTED live under `idoco2003` on 2026-06-02, after
RFCs 0332-0341 landed on `main` via PR #278. Ledger `outreach-move25.yaml`
carries the live URLs; `response` stays `none` until a maintainer replies.

**Routing summary**

| RFC | Target | Channel | Status | Live URL |
|---|---|---|---|---|
| 0332 | robot_localization | Issue on `cra-ros-pkg/robot_localization` | **Posted 2026-06-02** | https://github.com/cra-ros-pkg/robot_localization/issues/972 |
| 0333 | GTSAM | Issue on `borglab/gtsam` | **Posted 2026-06-02** | https://github.com/borglab/gtsam/issues/2557 |
| 0334 | OpenVINS | Issue on `rpng/open_vins` | **Posted 2026-06-02** | https://github.com/rpng/open_vins/issues/545 |
| 0335 | KISS-ICP | Issue on `PRBonn/kiss-icp` | **Posted 2026-06-02** | https://github.com/PRBonn/kiss-icp/issues/504 |
| 0336 | GLIM | Issue on `koide3/glim` | **Posted 2026-06-02** | https://github.com/koide3/glim/issues/304 |
| 0337 | OctoMap | Issue on `OctoMap/octomap` | **Posted 2026-06-02** | https://github.com/OctoMap/octomap/issues/447 |
| 0338 | Ceres Solver | Issue on `ceres-solver/ceres-solver` | **Posted 2026-06-02** | https://github.com/ceres-solver/ceres-solver/issues/1201 |
| 0339 | fuse | Issue on `locusrobotics/fuse` | **Posted 2026-06-02** | https://github.com/locusrobotics/fuse/issues/427 |
| 0340 | DLIO | Issue on `vectr-ucla/direct_lidar_inertial_odometry` | **Posted 2026-06-02** | https://github.com/vectr-ucla/direct_lidar_inertial_odometry/issues/107 |
| 0341 | Kimera | Issue on `MIT-SPARK/Kimera-VIO` | **Posted 2026-06-02** | https://github.com/MIT-SPARK/Kimera-VIO/issues/260 |

---

## RFC-0332: robot_localization

**Post to:** https://github.com/cra-ros-pkg/robot_localization/issues/new
**Title:** URML (open robot intent language): consuming a robot_localization estimate to ground declared frames, request for comment

```
Hi robot_localization maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. A person writes an English sentence, URML translates it to a typed primitive, statically validates it against the robot's declared capabilities and a safety envelope, then dispatches. To do that, URML declares frames (REP-105: map, odom, base_link) and named locations expressed in those frames. It does not estimate state itself. robot_localization is exactly the substrate that produces the fused pose and the map->odom->base_link transforms those declarations are expressed against.

Nothing here asks robot_localization to change or maintain anything. This is a request for comment on the boundary, and you are the right people to sanity-check it.

Two real questions. First, for a URML manifest to declare its localization source cleanly, what is the right way to reference a robot_localization output: the fused odometry topic and its frame_id, or something more structured? Second, the filter publishes a covariance; would it be reasonable for URML to treat estimate covariance as an input to a safety envelope (for example, refuse a tight maneuver when the pose covariance is above a threshold), or is that a misuse of the number?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0332-robot-localization-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is robot_localization BSD-licensed?

Thanks for the package that quietly grounds so many ROS stacks.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0333: GTSAM

**Post to:** https://github.com/borglab/gtsam/issues/new
**Title:** URML (open robot intent language): a factor-graph estimate as a pose source, boundary check / request for comment

```
Hi GTSAM maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares frames and named locations; it consumes a pose estimate to ground them, it does not estimate anything itself.

I want to be upfront that GTSAM is the lowest-direct-fit target in this round, and I am posting partly to get the boundary right rather than to claim a mapping. GTSAM is the factor-graph backend that a lot of SLAM and state-estimation systems optimize on; URML sits far above that. The honest relationship is indirect: the estimate a GTSAM-backed system produces is what ultimately grounds URML's frames.

So one real question, genuinely a question: is there any sensible point of contact between a thin intent/spec layer like URML and a factor-graph optimization backend, or is the right answer that URML should only ever talk to the system built on top of GTSAM (an estimator), never to GTSAM itself? A clear "stay one layer up" is a useful answer.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0333-gtsam-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is GTSAM BSD-licensed?

Thanks for GTSAM; it is foundational to a remarkable amount of robotics.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0334: OpenVINS

**Post to:** https://github.com/rpng/open_vins/issues/new
**Title:** URML (open robot intent language): consuming an OpenVINS estimate to ground declared frames, request for comment

```
Hi OpenVINS maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares frames (REP-105) and named locations; it consumes a pose estimate to ground them and does not estimate state itself. OpenVINS is exactly the kind of visual-inertial estimator that produces that pose.

To be clear up front on licensing: OpenVINS is GPL-3.0 and URML is Apache-2.0, so the relationship I am proposing is runtime consumption and cross-citation, not vendoring any code in either direction. Nothing here asks you to change or maintain anything.

Two real questions. First, for a URML manifest to declare a VIO localization source, what should it reference: the published pose/odometry and its frame, with the camera-IMU calibration treated as your configuration (Layer 0 from URML's view)? Second, would the filter covariance be a reasonable input to a URML safety envelope, or too easy to misread?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0334-openvins-outreach.md

Could you also confirm the license is GPL-3.0? The GitHub API did not surface an SPDX id at our verification time.

Thanks for OpenVINS and for how well-documented it is.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0335: KISS-ICP

**Post to:** https://github.com/PRBonn/kiss-icp/issues/new
**Title:** URML (open robot intent language): declaring a LiDAR-odometry localization source, request for comment

```
Hi KISS-ICP maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares frames and named locations; it consumes a pose estimate to ground them, it does not do odometry itself. KISS-ICP is a clean, minimal source of exactly that LiDAR odometry.

Nothing here asks KISS-ICP to change or maintain anything. This is a request for comment, and an honest modeling question.

KISS-ICP is deliberately odometry-only: no IMU, no loop closure, so the estimate drifts and there is no globally consistent map. That is a feature, but it matters for how URML should declare the source. So two questions. First, how should a URML manifest distinguish a drift-prone odometry-only localization source from a full SLAM source with a consistent map, so a validator can reason about it honestly? Second, is the published odometry topic plus its frame the right thing for URML to reference?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0335-kiss-icp-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is KISS-ICP MIT-licensed?

Thanks for showing how far a deliberately simple pipeline goes.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0336: GLIM

**Post to:** https://github.com/koide3/glim/issues/new
**Title:** URML (open robot intent language): consuming a GLIM SLAM estimate to ground declared frames, request for comment

```
Hi GLIM maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares frames and named locations; it consumes a pose and map estimate to ground them, it does not do SLAM itself. GLIM produces exactly that: a globally consistent LiDAR-inertial map and pose.

Nothing here asks GLIM to change or maintain anything. A note on scope: this thread is also where I am tracking hdl_graph_slam, since you maintain both; if one is the better integration surface for URML, please point me.

Two real questions. First, for a URML manifest to declare its localization source, should it reference GLIM's pose output plus its frame, and can the globally-consistent map sensibly back URML's occupancy and named-location checks? Second, contrasted with odometry-only pipelines, GLIM gives global consistency; is there a clean signal a consumer like URML should read to know the map has converged enough to trust for validation?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0336-glim-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is GLIM MIT-licensed?

Thanks for GLIM, and for keeping hdl_graph_slam around too.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0337: OctoMap

**Post to:** https://github.com/OctoMap/octomap/issues/new
**Title:** URML (open robot intent language): validating motion against an OctoMap occupancy map, request for comment

```
Hi OctoMap maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. Part of that validation is occupancy: before a robot moves, URML can check the motion stays in free space. OctoMap is the canonical 3D occupancy map that check would read.

Nothing here asks OctoMap to change or maintain anything. This is a request for comment on the consumer side.

Two real questions. First, at what grain is it sensible for a validator like URML to query an octree for a free-space / occupancy check on a planned motion or a named location, and are there pitfalls (unknown space, resolution) you would warn a consumer about? Second, what frame and resolution conventions should URML expect a published OctoMap to follow so a static check is meaningful?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0337-octomap-outreach.md

One small thing: I believe the core octomap library is BSD and octovis is GPL; could you confirm? The GitHub API did not surface an SPDX id at our verification time.

Thanks for OctoMap; it is still the default answer for 3D occupancy.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0338: Ceres Solver

**Post to:** https://github.com/ceres-solver/ceres-solver/issues/new
**Title:** URML (open robot intent language): boundary check, is there any contact point with a general optimization backend?

```
Hi Ceres Solver maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares frames and named locations and consumes a pose estimate to ground them.

I will be honest: Ceres is the deepest layer in a round of outreach I am doing on SLAM and state estimation, and very likely below the layer URML should ever talk to. Ceres is general-purpose nonlinear optimization that underlies a lot of SLAM, calibration, and bundle adjustment; URML only benefits indirectly, because the estimates Ceres helps produce eventually ground URML's frames. So this is mostly a boundary check and an acknowledgement of an important piece of the stack.

One real question: is there any meaningful point of contact between a high-level intent/spec layer and Ceres, or is the correct answer simply that URML should talk to the estimator built on Ceres and never to Ceres itself? I expect the latter, and a confirmation is genuinely useful.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0338-ceres-solver-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is Ceres BSD-3-Clause?

Thanks for Ceres; it is load-bearing for the whole field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0339: fuse

**Post to:** https://github.com/locusrobotics/fuse/issues/new
**Title:** URML (open robot intent language): declaring a fuse state-estimation source, request for comment

```
Hi fuse maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares frames and named locations and consumes a fused state estimate to ground them, it does not estimate state itself. fuse is exactly that: a graph-based, plugin-extensible state estimator.

A scope note: I separately reached Locus Robotics on the warehouse side a while back (a different conversation). This is specifically about the open-source fuse framework, not a re-pitch of that.

Two real questions. First, for a URML manifest to declare its localization source, how would you want fuse referenced relative to robot_localization, since fuse is in many ways its successor, just the published state and frame, or something that captures the graph structure? Second, would a fuse estimate's covariance be a reasonable input to a URML safety envelope?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0339-fuse-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is fuse BSD-3-Clause?

Thanks for fuse, and for keeping a modern fusion framework open.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0340: DLIO

**Post to:** https://github.com/vectr-ucla/direct_lidar_inertial_odometry/issues/new
**Title:** URML (open robot intent language): declaring a LiDAR-inertial odometry source, request for comment

```
Hi DLIO maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares frames and named locations and consumes a pose estimate to ground them, it does not do odometry itself. DLIO produces exactly that: lightweight, accurate LiDAR-inertial odometry.

Nothing here asks DLIO to change or maintain anything. This is a request for comment and a modeling question.

DLIO is LiDAR-inertial odometry, so it sits between LiDAR-only odometry (drift, simplest) and full SLAM (globally consistent). That distinction matters for how URML declares the source honestly. So: how should a URML manifest describe a LiDAR-inertial odometry source so a validator knows it has good local accuracy but no global loop-closure guarantee, and is the published odometry plus frame the right reference, with IMU-LiDAR extrinsics treated as your configuration (Layer 0)?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0340-dlio-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is DLIO MIT-licensed?

Thanks for DLIO; the accuracy-to-footprint ratio is impressive.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0341: Kimera

**Post to:** https://github.com/MIT-SPARK/Kimera-VIO/issues/new
**Title:** URML (open robot intent language): pose and semantics from Kimera as URML inputs, request for comment

```
Hi Kimera / MIT SPARK maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares frames, named locations, and a perception object vocabulary; it consumes estimates to ground them, it does not do SLAM itself. Kimera is interesting to URML on two fronts, not one.

Nothing here asks Kimera to change or maintain anything. This is a request for comment.

The two fronts. First, the standard one: Kimera's visual-inertial pose grounds URML's frames, same as the rest of this round. Second, the more speculative one I would value your read on: Kimera produces a metric-semantic mesh with per-element labels, and URML has a perception object vocabulary and named locations. Could a semantic label or a semantic region sensibly become, or validate, a URML named location, and at what grain would that be meaningful rather than noise?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0341-kimera-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is Kimera-VIO BSD-licensed?

Thanks for Kimera and the metric-semantic line of work.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
