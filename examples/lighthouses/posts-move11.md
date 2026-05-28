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

# Move #11 post bodies — net-new VLA / robot foundation models

Copy-paste-ready Issue / Discussion bodies for the Move #11 outreach. **Wave shape**: 15 net-new VLA / foundation-model targets that Move #2 did not touch (9 Tier A + 6 Tier B), verified 2026-05-28. RFC numbers reserved 0138-0152; each per-target body lands in a future session as the RFC drafts.

Ledger state: [`outreach-move11.yaml`](outreach-move11.yaml). Full research audit: [`vla-net-new-research-2026-05-28.md`](vla-net-new-research-2026-05-28.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("eleven outreach waves to date") are fine. Naming the specific orgs that responded is not.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #11 post ends with the one-paragraph authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*Authoring disclosure: URML is the invention of Ido Yahalomi. The outreach prose is AI-assisted (Claude, under the maintainer's review). See [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md). The maintainer reads and approves every post before it ships. Reviewers who prefer human-only correspondence are welcome to say so.*
```

**Schema-extension flags.** Move #11 surfaces multiple v0.1 schema gaps that should be opened as Spec RFCs in parallel (not bundled into the per-target outreach RFCs):

- **Action-head class declaration** (OpenVLA RFC-0138, Octo RFC-0139, Microsoft CogACT RFC-0151).
- **Diffusion-policy-class declaration** (Spherical-DP RFC-0140, MoDE RFC-0141, Stanford DP RFC-0142).
- **SE(3) / group equivariance** declaration (Amazon Spherical-DP RFC-0140).
- **Mixture-of-experts routing declaration** (MoDE RFC-0141).
- **Soft-body actuator class** (NUS Octopi RFC-0152).
- **Multimodal-VLA tool-call surface declaration** (Gemini Robotics SDK RFC-0145; structurally similar to RFC-0123 Cubert cuvis-ai-agentic-skills).

Each is a separate Spec RFC; URML's outreach RFCs ship with the v0.1 `custom` measurement_type / mobility-class escape-hatch and reference the queued Spec RFC.

---

## Tier A — 9 vendor-direct / research-lab-direct targets

### RFC-0138: OpenVLA
**Post to:** https://github.com/openvla/openvla/issues/new. Body TBD when RFC drafts.

### RFC-0139: Octo
**Post to:** https://github.com/octo-models/octo/issues/new. Body TBD.

### RFC-0140: Amazon Science Spherical Diffusion Policy
**Post to:** https://github.com/amazon-science/Spherical_Diffusion_Policy/issues/new. Body TBD. **Schema-extension flag**: SE(3) equivariance + diffusion-policy-class Spec RFC.

### RFC-0141: Intuitive Robots MoDE Diffusion Policy
**Post to:** https://github.com/intuitive-robots/MoDE_Diffusion_Policy/issues/new. Body TBD. **Schema-extension flag**: MoE routing + diffusion-policy-class Spec RFC.

### RFC-0142: Stanford Diffusion Policy
**Post to:** https://github.com/real-stanford/diffusion_policy/issues/new. Body TBD. **Schema-extension flag**: diffusion-policy-class Spec RFC (shared with RFC-0140 + RFC-0141).

### RFC-0143: HuggingFace smolagents
**Post to:** https://github.com/huggingface/smolagents/discussions/new (Discussions enabled — preferred for design discussion). Body TBD.

### RFC-0144: DeepMind MuJoCo Playground
**Post to:** https://github.com/google-deepmind/mujoco_playground/discussions/new (Discussions enabled). Body TBD.

### RFC-0145: DeepMind Gemini Robotics SDK
**Post to:** https://github.com/google-deepmind/gemini-robotics-sdk/issues/new. Body TBD. **Highest-value Move-11 target.** **Schema-extension flag**: multimodal-VLA tool-call surface declaration (cross-link to RFC-0123 Cubert pattern).

### RFC-0146: OpenMind OM1
**Post to:** https://github.com/OpenMind/OM1/issues/new. Body TBD.

---

## Tier B — 6 research-collab / cross-citation targets

### RFC-0147: Allen AI AI2-THOR
**Post to:** https://github.com/allenai/ai2thor/discussions/new (Discussions enabled). Body TBD.

### RFC-0148: RAI Institute Theia
**Post to:** https://github.com/rai-opensource/Theia/issues/new. Body TBD. **License-clarification ask** (license listed as Other; explicit OSI declaration requested).

### RFC-0149: RAI Institute VLFM
**Post to:** https://github.com/rai-opensource/vlfm/issues/new. Body TBD.

### RFC-0150: Microsoft PSI
**Post to:** https://github.com/microsoft/psi/discussions/new (Discussions enabled). Body TBD. **License-clarification ask** (license listed as Other).

### RFC-0151: Microsoft CogACT
**Post to:** https://github.com/microsoft/CogACT/issues/new. Body TBD.

### RFC-0152: NUS Clear Lab Octopi
**Post to:** https://github.com/clear-nus/octopi/issues/new. Body TBD. **License-clarification ask** (no SPDX visible). **Schema-extension flag**: soft-body actuator class.

---

## Tier C (7) — recorded in research file, NOT engaged

See [`vla-net-new-research-2026-05-28.md`](vla-net-new-research-2026-05-28.md) for the full Tier-C list with exclusion causes (PRC origin × 3 — Psi-Robot/DexGraspVLA, InternRobotics/InternNav, HorizonRobotics/HoloMotion; HK gray × 1 — SageCao1125/Mamba-Policy; already engaged in Move-2 × 2 — NVIDIA/Isaac-GR00T, isaac-sim/IsaacLab; superseded × 1 — OpenMind/OM1-OTA). No posts.
