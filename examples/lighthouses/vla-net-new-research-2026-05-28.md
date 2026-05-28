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

# Move-11 research — net-new VLA / robot foundation-model targets

**Research date**: 2026-05-28.
**Audience**: founder review before Move-11 RFCs draft.
**Method**: two Explore agents in parallel covered 11 category-groups, cross-checked each candidate against [`outreach-move2.yaml`](outreach-move2.yaml), verified via `gh repo view` for `isArchived: false`, license, recency, Issues, origin.
**Outcome**: 15 verified candidates (9 Tier A + 6 Tier B); 7 excluded with cause.

## Why this wave

Move #2 (2026-05-23) posted RFCs to 21 AI/ML / VLA targets, response rate `none` across the board except Spot (engaged via rai-opensource COLLABORATOR). The Move-2 wave is *not-yet-responded-to*, not *missing*. Move #11 is the **net-new** layer — VLAs / robot foundation models that emerged since Move-2 or that Move-2 didn't reach.

## Tier A (9) — vendor-direct / research-lab-direct, adapter-eligible

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `openvla` | [openvla/openvla](https://github.com/openvla/openvla) | MIT | 6.3k | 2025-03-23 | US | Stanford/TRI/DeepMind 7B generalist VLA. Issues enabled. Last-push 14 mo flagged but foundational; baseline VLA reference. |
| `octo` | [octo-models/octo](https://github.com/octo-models/octo) | MIT | 1.7k | 2024-07-31 | US | UC Berkeley (Sergey Levine lab) 800k-trajectory diffusion VLA. Issues enabled. Older push but architectural reference. |
| `amazon-spherical-diffusion-policy` | [amazon-science/Spherical_Diffusion_Policy](https://github.com/amazon-science/Spherical_Diffusion_Policy) | MIT | 42 | 2025-07-08 | US | Amazon Science ICML 2025; SE(3)-equivariant diffusion policy. Issues enabled. |
| `intuitive-robots-mode` | [intuitive-robots/MoDE_Diffusion_Policy](https://github.com/intuitive-robots/MoDE_Diffusion_Policy) | MIT | 122 | 2025-05-16 | DE/US | ICLR 2025; Karlsruhe Institute of Technology + MIT; mixture-of-experts diffusion transformers. Active. |
| `stanford-diffusion-policy` | [real-stanford/diffusion_policy](https://github.com/real-stanford/diffusion_policy) | MIT | 4.2k | 2024-12-24 | US | Stanford/Columbia/TRI Cheng Chi et al; foundational diffusion-policy paper. Referenced in Move-2 RFC-0054 notes but never directly engaged. |
| `huggingface-smolagents` | [huggingface/smolagents](https://github.com/huggingface/smolagents) | Apache-2.0 | 27.5k | 2026-05-26 | FR/multi | HuggingFace agent framework; code-generation agent backbone. Highly active. Issues + Discussions both enabled. |
| `deepmind-mujoco-playground` | [google-deepmind/mujoco_playground](https://github.com/google-deepmind/mujoco_playground) | Apache-2.0 | 2.0k | 2026-05-27 | US/UK | DeepMind GPU-accelerated robot-learning env. Distinct from Move-2 `google-deepmind/mujoco` simulator core. Issues + Discussions. |
| `deepmind-gemini-robotics-sdk` | [google-deepmind/gemini-robotics-sdk](https://github.com/google-deepmind/gemini-robotics-sdk) | Apache-2.0 | 582 | 2026-05-23 | US/UK | DeepMind Gemini Robotics SDK; **highest-value Move-11 target** — multimodal VLA developer surface. Issues enabled. |
| `openmind-om1` | [OpenMind/OM1](https://github.com/OpenMind/OM1) | MIT | 2.8k | 2026-05-27 | US | OpenMind humanoid AI runtime flagship; openmind.com. 28 public repos in org. Very active. |

## Tier B (6) — research-collab / cross-citation framing

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `allenai-ai2thor` | [allenai/ai2thor](https://github.com/allenai/ai2thor) | Apache-2.0 | 1.7k | 2025-11-04 | US | Allen AI visual interactive simulation; URML conformance lane for household-manipulation. Distinct from Move-2 MolmoAct. |
| `rai-theia` | [rai-opensource/Theia](https://github.com/rai-opensource/Theia) | Other (verify) | 276 | 2025-11-06 | US | RAI Institute (Boston Dynamics AI Institute) vision foundation model. License clarification ask. |
| `rai-vlfm` | [rai-opensource/vlfm](https://github.com/rai-opensource/vlfm) | MIT | 749 | 2025-11-12 | US | RAI Institute VLM-based navigation (ICRA 2024). Companion to RAI Theia. |
| `microsoft-psi` | [microsoft/psi](https://github.com/microsoft/psi) | Other (verify) | 570 | 2026-05-15 | US | Microsoft Platform for Situated Intelligence; temporal streams + offline replay. Issues + Discussions. License clarification ask. |
| `microsoft-cogact` | [microsoft/CogACT](https://github.com/microsoft/CogACT) | MIT | 427 | 2025-10-30 | US | Microsoft CVPR 2025 VLA for dexterous control. |
| `nus-octopi` | [clear-nus/octopi](https://github.com/clear-nus/octopi) | TBD | 76 | 2026-05-24 | SG | National University of Singapore (NUS) octopus-inspired research. License clarification ask. SG passes US-federal default policy (NATO+ allied). |

## Tier C — excluded with cause (recorded so the negative space is auditable)

| Slug | Repo | Cause |
|---|---|---|
| `psi-robot-dexgraspvla` | Psi-Robot/DexGraspVLA | **PRC origin** — org description `灵初智能科技有限公司` (PsiBot 灵初智能, PRC-domiciled). NDAA Section 889. |
| `internrobotics-internnav` | InternRobotics/InternNav | **PRC origin** — Shanghai AI Lab (`shlab.org.cn`). NDAA Section 889. |
| `horizonrobotics-holomotion` | HorizonRobotics/HoloMotion | **PRC origin** — Horizon Robotics, Beijing, China. NDAA Section 889. |
| `sagecao-mamba-policy` | SageCao1125/Mamba-Policy | **HK origin gray area** — HKUST. Operator-decision flag would be needed; defer pending policy clarification. |
| `nvidia-groot-iteration` | NVIDIA/Isaac-GR00T | Already engaged in Move-2 RFC-0050 (posted to NVIDIA/Isaac-GR00T issues/682). |
| `isaac-lab-eureka` | isaac-sim/IsaacLabEureka | Same isaac-sim org as Move-2 RFC-0050 engaged isaac-sim/IsaacLab (discussions/5759). Avoid noise. |
| `openmind-ota-early` | OpenMind/OM1-OTA | 0 stars, too early to engage; superseded by OpenMind/OM1 (Tier A). |

## Distribution across categories

| Move-11 category | Tier A | Tier B | Excluded |
|---|---|---|---|
| Generalist VLAs (OpenVLA / Octo / OM1) | 3 | 0 | 0 |
| Diffusion-policy lineage | 3 | 0 | 0 |
| Dexterous-manipulation VLAs | 0 | 0 | 2 (Psi-Robot + Mamba) |
| NVIDIA newer lines | 0 | 0 | 2 (already engaged) |
| HuggingFace robotics broader | 1 | 0 | 0 |
| Allen AI broader | 0 | 1 | 0 |
| Boston Dynamics AI Institute (RAI) | 0 | 2 | 0 |
| Google DeepMind robotics | 2 | 0 | 0 |
| Toyota Research broader | 0 | 0 | 0 (TRI broader did not surface a new target beyond Move-2 vla_foundry) |
| Microsoft / Apple corporate | 0 | 2 | 0 |
| Singapore / allied research | 0 | 1 | 1 (HK gray) |
| OpenMind OS / 2026-Q2 releases | 0 | 0 | 3 (PRC) |
| **Total** | **9** | **6** | **7** |

## Reserved RFC range

RFCs 0138-0152 reserved for Move #11 in `docs/rfcs/README.md` (Move-10 ended at RFC-0137 AMS-OSRAM; Move #11 picks up at 0138).

## Open license-clarification asks (carry into per-RFC unresolved questions)

- `rai-opensource/Theia`: license listed as "Other" — request explicit OSI declaration.
- `microsoft/psi`: license listed as "Other" — request explicit OSI declaration.
- `clear-nus/octopi`: no SPDX visible — request explicit declaration.

## Next steps

1. Founder review of this research file.
2. Setup PR ships: `outreach-move11.yaml` + `posts-move11.md` skeleton + README index update.
3. Subsequent sessions: draft RFCs 0138-0152 one per session (Move-10 batch shape: 5-6 RFCs per PR).
4. Posting follows Move-10 pattern: founder review of bodies, then assistant posts via `gh` with explicit "go" authorization.
