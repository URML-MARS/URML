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

# Move-15 research — niche verticals (surgical, construction, delivery, warehouse) (Theme D)

**Research date**: 2026-05-28.
**Audience**: founder review before Move-15 RFCs draft.
**Method**: two Explore agents in parallel covered surgical/medical + construction (Agent 1) and delivery + warehouse AMR (Agent 2), cross-checked each candidate against all prior ledgers (Moves 1-14), verified via `gh repo view` + `gh api orgs/...` for `isArchived: false`, license, recency, Issues, origin.
**Outcome**: **5 verified engageable candidates** (3 Tier A + 2 Tier B); **~15 Tier C excluded with cause** across four sub-categories — most of the niche-vertical market is commercial-closed.

## Why this is URML's smallest wave

Move-15 makes the closed-vertical market visible. Across four sub-categories that look substantial in industry coverage:

- **Surgical / medical robotics**: vendor OEMs (Intuitive Surgical, Auris Health/J&J, CMR Surgical, Stryker Mako) are uniformly closed. Only the **research surface** — Johns Hopkins dVRK + IIT iCub — has public engagement.
- **Construction robotics**: every commercial vendor (Built Robotics, Dusty Robotics, Canvas Construction, Civ Robotics, Hilti construction tools) is closed. **Zero engageable construction candidates.**
- **Delivery robots**: Starship has ROS-adjacent infrastructure repos; Serve Robotics has a fork-heavy public surface; Nuro / Kiwibot / Cartken have no verified public GitHub.
- **Warehouse AMR**: MiR / Locus / Vecna / Symbotic / OTTO Motors / 6 River Systems all closed; Greyorange has Erlang ops infrastructure only (Tier C). Already-engaged duplicates: Fetch Robotics (Move-14 RFC-0188), Clearpath Robotics (Move-5 RFC-0072), Open-RMF (Move-2 RFC-0053).

URML's wave is honest about this. The Tier C list is the audit trail.

## Tier A (3) — research-lab-direct or vendor-direct

### Surgical / medical (2)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `jhu-dvrk-saw-intuitive-research-kit` | [jhu-dvrk/sawIntuitiveResearchKit](https://github.com/jhu-dvrk/sawIntuitiveResearchKit) | CISST (custom permissive) | 157 | 2026-04-18 | US (JHU Maryland) | Research-lab-direct (Johns Hopkins ERC CISST). The da Vinci Research Kit — surgical-robotics flagship for open research. License is non-SPDX but permissive distribution. |
| `robotology-icub-main` | [robotology/icub-main](https://github.com/robotology/icub-main) | BSD-3-Clause | 118 | 2026-04-27 | IT (IIT Genoa) | Research-lab-direct (Italian Institute of Technology). iCub is humanoid + assistive/prosthetic / rehabilitation research; the medical-relevant humanoid surface URML's prior humanoid coverage didn't reach. |

### Delivery (1)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `starship-bag-rdr` | [starship-technologies/bag_rdr](https://github.com/starship-technologies/bag_rdr) | MIT | 29 | 2026-02-22 | EE / UK | Vendor-direct (Starship Technologies, Estonian-UK sidewalk delivery). ROS-bag reader infrastructure repo is the most-engageable surface; the actual delivery robot is closed. Engagement enters via the ROS-adjacent infrastructure layer. |

## Tier B (2) — research-collab / cross-citation framing

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `robotology-yarp` | [robotology/yarp](https://github.com/robotology/yarp) | LGPL (Other) | 592 | 2026-05-18 | IT (IIT) | Research-lab-direct middleware — Yet Another Robot Platform. Used by iCub + medical-research projects. Sibling to RFC-0193 iCub but at the substrate-middleware layer (URML's existing `reference/ros2-runtime/` is the analog). Cross-citation framing because middleware is structurally different from per-target adapter pattern. |
| `serve-robotics-model-optimizer` | [serve-robotics/Model-Optimizer](https://github.com/serve-robotics/Model-Optimizer) | Apache-2.0 | (fork-heavy public surface) | 2026-05-22 | US (Uber spinoff) | Vendor-affiliated. Most public surface is forks (24 repos, predominantly community-fork copies). Model-Optimizer is the most-recently-active. Engagement is light-touch given the minimal vendor-original public surface. |

## Tier C — excluded with cause (the closed-vertical market reality)

### Surgical / medical OEMs (4)

| Slug | Cause |
|---|---|
| `intuitive-surgical` | **Closed.** Da Vinci surgical robot OEM; no public GitHub presence; dVRK research kit (RFC-0191) is JHU's separately-licensed research surface, not Intuitive Surgical's commercial product. |
| `auris-health` | **Closed.** Acquired by Johnson & Johnson 2019; no public GitHub robotics presence. |
| `cmr-surgical` | **Closed.** Versius surgical robot, UK; no public GitHub. |
| `stryker-mako` | **Closed.** Mako orthopedic surgical robot; no public GitHub. |

### Construction OEMs (5)

| Slug | Cause |
|---|---|
| `built-robotics` | **No public GitHub presence.** Autonomous excavator OEM, US. |
| `dusty-robotics` | **No public GitHub presence.** Construction-layout robot, US. |
| `canvas-construction` | **No public GitHub presence.** Drywall robot, US. |
| `civ-robotics` | **No public GitHub presence.** Autonomous surveying, US. |
| `hilti-construction-tools` | **No public robotics GitHub.** Digital construction surface exists but no engageable robotics repo. |

### Delivery OEMs (3)

| Slug | Cause |
|---|---|
| `nuro` | **No public GitHub presence.** Autonomous delivery, US. |
| `kiwibot` | **No public GitHub presence.** Sidewalk delivery, US/Colombia. |
| `cartken` | **No public GitHub presence.** Sidewalk delivery, US (acquired Coco). |

### Warehouse AMR (6, of which 3 are already-engaged duplicates)

| Slug | Cause |
|---|---|
| `fetchrobotics` | **Already engaged Move-14 RFC-0188.** Fetch + Freight mobile manipulator (post-Zebra-acquisition). |
| `clearpathrobotics` | **Already engaged Move-5 RFC-0072.** Clearpath warehouse AMR + mobile robotics platform. |
| `open-rmf` | **Already engaged Move-2 RFC-0053.** Multi-robot coordination + fleet management. |
| `mir-locus-vecna-symbotic-otto-6river` | **All closed.** No verified public GitHub presence for any of MiR, Locus, Vecna, Symbotic, OTTO Motors (Rockwell-acquired), or 6 River Systems (Shopify). |
| `greyorange-erldash` | **Erlang ops infrastructure only.** 35 public repos, but no robotics-class engagement surface; `erldash` last commit 2020-07-29 (>5 years stale). |
| `geek-plus` | **PRC origin.** NDAA Section 889 exclusion. |

## Distribution

| Sub-category | Tier A | Tier B | Excluded |
|---|---|---|---|
| Surgical / medical | 2 (dVRK, iCub) | 1 (YARP middleware) | 4 (Intuitive Surgical, Auris/J&J, CMR Surgical, Stryker Mako) |
| Construction | 0 | 0 | 5 (Built, Dusty, Canvas, Civ, Hilti) |
| Delivery | 1 (Starship bag_rdr) | 1 (Serve Robotics Model-Optimizer) | 3 (Nuro, Kiwibot, Cartken) |
| Warehouse AMR | 0 | 0 | 6 (3 already-engaged duplicates + 3 closed-or-stale) |
| **Total** | **3** | **2** | **18** |

## Reserved RFC range

RFCs 0191-0195 reserved for Move #15 in `docs/rfcs/README.md`. Move-14 ends at RFC-0190.

## Honest framing notes for the per-RFC bodies

- **URML's first surgical / medical RFCs.** RFC-0191 (dVRK) and RFC-0193 (iCub) open the surgical/medical-research class for URML's manifest. The OEM-vendor layer (Intuitive Surgical, Auris/J&J, CMR Surgical, Stryker Mako) is closed; URML's engagement is at the research-lab layer where the surface exists.
- **No construction-vertical engagement at all.** This wave's research found zero engageable construction-robotics GitHub surfaces. The Tier C list documents the closed-sector reality.
- **Delivery is mostly closed too.** RFC-0192 Starship engages at the ROS-bag-infrastructure layer because the actual delivery-robot stack is closed.
- **YARP middleware Spec-RFC question.** RFC-0194 YARP is research-lab middleware — sibling layer to URML's existing `reference/ros2-runtime/`. The engagement asks whether URML manifest should declare YARP as an alternate substrate to ROS 2.
- **Move-15 size doesn't mean Move-15 is unimportant.** Surgical and assistive robotics are high-impact verticals; the wave is small because the engageable surfaces are research-direct only.

## Open license-clarification asks

- `jhu-dvrk/sawIntuitiveResearchKit`: CISST custom license — not SPDX. RFC asks for OSI clarification or canonical permissive declaration.

## Next steps

1. Founder review of this research file.
2. Setup PR ships: `outreach-move15.yaml` + `posts-move15.md` skeleton.
3. Subsequent sessions: draft RFCs 0191-0195 (single batch given the smaller wave).
4. Posting follows Move-10/11/13/14 pattern.
