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

Copy-paste-ready Issue / Discussion bodies for the Move #11 outreach. **Wave shape**: 15 net-new VLA / foundation-model targets that Move #2 did not touch (9 Tier A + 6 Tier B), verified 2026-05-28. RFC numbers reserved 0138-0152.

Ledger state: [`outreach-move11.yaml`](outreach-move11.yaml). Full research audit: [`vla-net-new-research-2026-05-28.md`](vla-net-new-research-2026-05-28.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("eleven outreach waves to date") are fine. Naming the specific orgs that responded is not.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #11 post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Schema-extension flags.** Move #11 surfaces multiple v0.1 schema gaps that should be opened as Spec RFCs in parallel (not bundled into the per-target outreach RFCs):

- **Action-head class declaration** (OpenVLA RFC-0138, Octo RFC-0139, Microsoft CogACT RFC-0151).
- **Diffusion-policy-class declaration** (Spherical-DP RFC-0140, MoDE RFC-0141, Stanford DP RFC-0142).
- **SE(3) / group equivariance** declaration (Amazon Spherical-DP RFC-0140).
- **Mixture-of-experts routing declaration** (MoDE RFC-0141).
- **NL-layer-substrate declaration** (smolagents RFC-0143, Gemini Robotics SDK RFC-0145, ROSA RFC-0108).
- **Sim-substrate declaration** (MuJoCo Playground RFC-0144, AI2-THOR RFC-0147).
- **Multimodal-VLA tool-call surface declaration** (Gemini Robotics SDK RFC-0145).
- **OS-layer-substrate declaration + mobile-humanoid mobility class** (OpenMind OM1 RFC-0146).
- **Vision-foundation-model substrate declaration** (RAI Theia RFC-0148).
- **Navigation-substrate + language-conditioned-navigation declaration** (RAI VLFM RFC-0149).
- **Temporal-streams substrate declaration** (Microsoft PSI RFC-0150).
- **Dexterous-control action-space declaration** (Microsoft CogACT RFC-0151).
- **Soft-body actuator class + pneumatic-network actuator class + continuum-manipulator kinematics** (NUS Octopi RFC-0152).

Each is a separate Spec RFC; URML's outreach RFCs ship with the v0.1 `custom` measurement_type / `controller_class: custom` escape-hatch and reference the queued Spec RFC.

---

## Tier A — 9 vendor-direct / research-lab-direct targets

### RFC-0138: OpenVLA

**Post to:** https://github.com/openvla/openvla/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) as the pre-flight typed safety check above OpenVLA action output
```

**Body:**

```markdown
Hi @openvla team,

Proposing a URML v0.1 capability-manifest mapping for OpenVLA over `openvla/openvla`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: a typed primitive vocabulary plus a Layer-1 capability manifest and a validator that gates programs against the manifest before any actuator publishes.

OpenVLA is the foundational open 7B generalist VLA. URML's natural composition shape with OpenVLA is the **pre-flight typed safety check** — URML's validator sits above OpenVLA's emitted action sequence and rejects, before publish, any action that the active capability manifest cannot honor. The same posture URML adopted toward Isaac Lab in a prior outreach.

**This is proposal-only**, part of URML's Move #11 outreach (net-new VLA / foundation-model targets that URML's prior AI/ML wave did not touch — 15 RFCs in this wave).

Full RFC with manifest mapping, three alternatives, and the validator-boundary design discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0138-openvla-outreach.md

Questions worth maintainer input on:

1. **Repository status.** Is `openvla/openvla` actively maintained or has the active development moved to a successor (`openvla-mini`, `openvla-oft`, ...)?
2. **Action-head class manifest fields.** URML's v0.1 has no `vla_model` controller class. Spec RFC queued; what manifest fields would an OpenVLA deployment expect (action head, input modalities, output action space)?
3. **Pre-flight validation boundary.** URML's validator sits above OpenVLA output (validates emitted actions before publish), below the NL input (URML compiles NL to typed primitives that OpenVLA's planner consumes), or in a side-channel that monitors but does not gate?
4. **`extra_inputs` declaration.** OpenVLA's action-head extension mechanism is the natural place URML's manifest could plug in. Contributed `extra_inputs` example, or external bridge?
5. **Bridge home.** URML repo (`reference/vla-bridge/`), `openvla/openvla-urml-bridge`, or external?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0139: Octo

**Post to:** https://github.com/octo-models/octo/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Octo diffusion-transformer policy
```

**Body:**

```markdown
Hi @octo-models team,

Proposing a URML v0.1 capability-manifest mapping for Octo over `octo-models/octo`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

Octo is the UC Berkeley diffusion-transformer generalist policy trained on Open X-Embodiment. URML's manifest declares the learned-controller class; URML's primitive vocabulary is the typed substrate Octo's action chunks dispatch onto. The action-head class declaration is a shared gap URML's outreach is queueing.

Acknowledging `octo-models/octo` has been quiet on GitHub for `>22 months`. Engaging anyway — the architecture remains the canonical diffusion-policy generalist; if active development has moved to a successor project, a redirect would help.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC with the manifest mapping and three alternatives: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0139-octo-outreach.md

Questions worth maintainer input on:

1. **Repository status.** Active, dormant-but-supported, or has development moved to a successor?
2. **Action-head + action-chunk-horizon manifest fields.** Manifest expectations for action-horizon, action-space, pretraining-data provenance?
3. **Bridge shape.** URML's bridge sits above Octo's output, below the NL input, or in a side-channel?
4. **Bridge home.** URML repo (`reference/vla-bridge/`), `octo-models/octo-urml-bridge`, or external?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0140: Amazon Science Spherical Diffusion Policy

**Post to:** https://github.com/amazon-science/Spherical_Diffusion_Policy/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Spherical Diffusion Policy + SE(3) equivariance schema-extension
```

**Body:**

```markdown
Hi @amazon-science team,

Proposing a URML v0.1 capability-manifest mapping for Spherical Diffusion Policy over `amazon-science/Spherical_Diffusion_Policy`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

Spherical-DP's SE(3)-equivariance contribution is the distinct schema-extension question URML's outreach is queueing. URML's v0.1 manifest does not today declare which symmetry classes a learned controller respects; a Spec RFC adding `equivariance_class` (none / SE(3) / SO(3) / equivariant_custom) is queued, and Amazon Science's input would shape its manifest-field design.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0140-amazon-spherical-diffusion-policy-outreach.md

Questions worth maintainer input on:

1. **Equivariance-class manifest fields.** Group-class, basis representation, equivariance-loss-vs-architecture distinction?
2. **Coordinate-frame alignment between manifest and policy.** Manifest-side declaration or always envelope-side?
3. **Diffusion-policy class declaration.** Shared gap with sibling Move-11 RFCs; manifest field expectations?
4. **Bridge home.** URML repo (`reference/vla-bridge/`), Amazon-maintained, or external?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0141: Intuitive Robots MoDE Diffusion Policy

**Post to:** https://github.com/intuitive-robots/MoDE_Diffusion_Policy/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for MoDE + MoE routing schema-extension
```

**Body:**

```markdown
Hi @intuitive-robots team,

Proposing a URML v0.1 capability-manifest mapping for MoDE Diffusion Policy over `intuitive-robots/MoDE_Diffusion_Policy`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

MoDE's mixture-of-experts routing contribution is the distinct schema-extension question URML's outreach is queueing. URML's v0.1 manifest does not today declare which experts a learned controller uses or how routing happens; a Spec RFC adding `routing_class` + `expert_count` is queued, and your input on the KIT-MIT collaboration's manifest expectations would shape it.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0141-intuitive-robots-mode-diffusion-policy-outreach.md

Questions worth maintainer input on:

1. **MoE routing declaration manifest fields.** routing_class, expert_count, gating semantics?
2. **Diffusion-policy class declaration.** Shared gap with sibling Move-11 RFCs.
3. **Multi-collaborator-origin declaration.** Should URML's manifest declare multi-origin research artifacts (origin: `DE+US`)?
4. **Bridge home.** URML repo, KIT-maintained, or external?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0142: Stanford Diffusion Policy

**Post to:** https://github.com/real-stanford/diffusion_policy/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for foundational Diffusion Policy + diffusion-policy class Spec RFC umbrella
```

**Body:**

```markdown
Hi @real-stanford / Cheng Chi et al,

Proposing a URML v0.1 capability-manifest mapping for the foundational Diffusion Policy over `real-stanford/diffusion_policy`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

Diffusion Policy is the architectural reference every 2025-era DP variant extends. URML's outreach engages the lineage at the canonical root: a Spec RFC adding the `diffusion_policy` controller-class declaration is queued, with the foundational paper's manifest-field expectations informing the design.

Acknowledging `real-stanford/diffusion_policy` has been quiet for `>17 months`. The architecture is foundational rather than actively-iterating; engagement is light-touch.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0142-stanford-diffusion-policy-outreach.md

Questions worth maintainer input on:

1. **Repository status.** Active, dormant-but-supported, or has the architecture moved to a successor?
2. **Diffusion-policy class manifest fields.** Diffusion-step count, action-horizon, backbone class, input-modality declaration?
3. **Action-chunk-horizon semantics.** Manifest declaration shape?
4. **Bridge home.** URML repo (`reference/vla-bridge/`), Stanford-maintained, or external?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0143: HuggingFace smolagents

**Post to:** https://github.com/huggingface/smolagents/discussions/new (Discussions enabled, preferred surface for design-discussion)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) as a smolagents tool — typed primitives the agent can compose
```

**Body:**

```markdown
Hi @huggingface smolagents team,

Proposing a URML v0.1 integration shape for smolagents — a `urml_tool` that the agent can register alongside its other tools, emitting validated URML programs. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: a typed primitive vocabulary plus a Layer-1 capability manifest and a validator that rejects, before any actuator publishes, any program a manifest cannot honor.

smolagents's distinguishing feature is that agents emit **executable Python code** rather than JSON tool-call objects, which means a `urml_tool` the agent invokes can compose other URML primitives in the same generated code block. This composition shape — agent emits code → code calls `urml_tool(...)` → URML validates against manifest → URML dispatches — is the natural integration for URML's NL story.

This is **proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0143-huggingface-smolagents-outreach.md

Questions worth maintainer input on:

1. **Tool-registration shape.** Contributed example in `smolagents/examples/`, external `urml-smolagents-bridge` package, or cross-citation only?
2. **NL-layer substrate declaration.** Useful manifest-side observability or unnecessary friction?
3. **Code-generation execution-model declaration.** Should URML's manifest distinguish code-generating agents (smolagents) from JSON-tool-calling agents?
4. **Bridge home.** URML repo (`reference/llm-bridge/`), HuggingFace-contributed example, or external?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0144: DeepMind MuJoCo Playground

**Post to:** https://github.com/google-deepmind/mujoco_playground/discussions/new (Discussions enabled, preferred surface for design-discussion)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) as the typed vocabulary above MuJoCo Playground envs — sim conformance lane
```

**Body:**

```markdown
Hi @google-deepmind mujoco_playground team,

Proposing a URML v0.1 capability-manifest mapping for MuJoCo Playground over `google-deepmind/mujoco_playground`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: a typed primitive vocabulary plus a capability manifest and a validator.

MuJoCo Playground is the GPU-accelerated env layer above the MuJoCo physics core. URML's manifests can target Playground as the **simulation conformance lane**: a manifest declares its expected env; URML's adapter dispatches the same primitives onto both the sim and real-robot substrate; conformance tests run in Playground via JAX's CPU fallback when GPU clusters are unavailable. This is structurally complementary to the MuJoCo simulator-core engagement URML's prior outreach surfaced — env layer (here) vs simulator core (separate thread).

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0144-deepmind-mujoco-playground-outreach.md

Questions worth maintainer input on:

1. **Simulation-env manifest fields.** env-name, version, observation-space, action-space, JAX backend declaration?
2. **Adapter shape.** Contributed example in `mujoco_playground/examples/`, external `urml-mujoco-playground-bridge`, or `reference/sim-runtime/` under URML repo?
3. **Engagement-level boundary with mujoco-core.** Coordinated or independent threads?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0145: DeepMind Gemini Robotics SDK

**Post to:** https://github.com/google-deepmind/gemini-robotics-sdk/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Gemini Robotics SDK — multimodal-VLA typed substrate
```

**Body:**

```markdown
Hi @google-deepmind gemini-robotics-sdk team,

Proposing a URML v0.1 capability-manifest mapping for Gemini Robotics SDK over `google-deepmind/gemini-robotics-sdk`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: a typed primitive vocabulary plus a Layer-1 capability manifest and a validator that rejects, before any actuator publishes, any program a manifest cannot honor.

Gemini Robotics is a multimodal VLA that emits tool-calls; URML's primitive vocabulary is the natural typed substrate those calls dispatch to. URML's natural-language layer + `query_detection` primitive compose with Gemini's multimodal tool-call surface in a way structurally similar to the agentic-skills pattern URML engaged in a prior outreach. The high-leverage integration is straightforward: Gemini emits multimodal tool-calls → calls map to typed URML primitives → URML validates against the active manifest → URML dispatches to substrate.

This is **proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave). The integration is the **highest-leverage URML-side touchpoint** in this wave.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0145-deepmind-gemini-robotics-sdk-outreach.md

Questions worth maintainer input on:

1. **NL-layer substrate declaration manifest fields.** Tool-registration convention, multimodal-context declaration, model-access binding?
2. **Multimodal-input cross-sensor binding.** Should URML's manifest declare that a multimodal VLA consumes specific sensors simultaneously?
3. **Bridge home.** URML repo (`reference/llm-bridge/GeminiRoboticsBridge`), `google-deepmind/gemini-robotics-urml` contributed example, or external?
4. **Coordination with the DeepMind broader engagement.** Single-entry-point preferred or separate per-repo?
5. **Conformance listing.** README link to URML's compatible-runtimes registry once a working bridge ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0146: OpenMind OM1

**Post to:** https://github.com/OpenMind/OM1/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) sitting one layer above OM1 — typed intent vocabulary for the OS layer
```

**Body:**

```markdown
Hi @OpenMind OM1 team,

Proposing a URML v0.1 capability-manifest mapping for OM1 over `OpenMind/OM1`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: a typed primitive vocabulary plus a Layer-1 capability manifest and a validator.

The structural fit is clean: OpenMind ships the mobile-humanoid **runtime** (OS layer); URML ships the substrate-neutral **intent language** (one layer above). An OM1 deployment with URML's adapter consumes validated typed primitives and dispatches them onto the humanoid; the manifest declares the OM1 binding. Same posture URML adopted toward ROS 2 / PX4 / Isaac Lab — URML sits above as the vocabulary; the substrate dispatches below.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0146-openmind-om1-outreach.md

Questions worth maintainer input on:

1. **OS-layer substrate manifest declaration.** OS version, supported hardware, capability flags?
2. **OS-vs-policy boundary declaration.** OM1 ships both OS-level and policy-level functionality; should URML's manifest declare which is active at which boundary?
3. **Mobile-humanoid mobility class.** URML's mobility schema has `biped` and `quadruped` but not `mobile_humanoid` (mobile-base + biped torso); manifest-field expectations?
4. **Adapter home.** URML repo (`reference/humanoid-runtime/OpenMindOM1Adapter`), OpenMind-maintained `OpenMind/OM1-urml-bridge`, or both?
5. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier B — 6 research-collab / cross-citation targets

### RFC-0147: Allen AI AI2-THOR

**Post to:** https://github.com/allenai/ai2thor/discussions/new (Discussions enabled)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for AI2-THOR — household-task simulation conformance
```

**Body:**

```markdown
Hi @allenai ai2thor team,

Proposing a URML v0.1 capability-manifest **cross-citation** for AI2-THOR over `allenai/ai2thor`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

AI2-THOR is the natural simulation harness for URML's home-runtime profile (the manifests that target household-manipulation tasks). Cross-citation framing because AI2-THOR is research-platform, not vendor-OEM, and URML's adapter at the sim-substrate layer is one of several env candidates URML is engaging in parallel.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0147-allenai-ai2thor-outreach.md

Questions worth maintainer input on:

1. **Repository status.** Active, dormant-but-supported, or has development moved to ProcTHOR / Holodeck / a successor?
2. **Sim-substrate manifest fields.** Manifest expectations from AI2-THOR's perspective?
3. **Discrete-action mobility class.** URML's mobility schema is continuous; AI2-THOR's API is discrete. Manifest field expectations?
4. **Bridge home.** Cross-citation only (recommended), URML repo (`reference/sim-runtime/`), or AllenAI-maintained?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0148: RAI Institute Theia

**Post to:** https://github.com/rai-opensource/Theia/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for Theia — and a license-clarification ask
```

**Body:**

```markdown
Hi @rai-opensource Theia team,

Proposing a URML v0.1 capability-manifest **cross-citation** for Theia over `rai-opensource/Theia`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

Theia is a vision foundation model for robotics; URML's manifest declares which vision-foundation-model class is active so adapters can consume Theia's feature representations without re-implementing the model surface.

**License-clarification ask** is the gating fact: the repo's license is listed as "Other" by the GitHub API. An explicit OSI declaration (Apache-2.0 / MIT / BSD-3-Clause) would unlock Apache-2.0 downstream reuse; until clarified, URML's framing stays at cross-citation depth.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0148-rai-theia-outreach.md

Questions worth maintainer input on:

1. **License clarification.** Can `rai-opensource/Theia` get an explicit OSI license declaration?
2. **Vision-foundation-model substrate manifest fields.** Manifest expectations for input modality, output representation class, downstream consumer interface?
3. **Bridge home.** Cross-citation only (recommended pending license), URML repo (`reference/vla-bridge/`), or RAI-maintained?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working cross-citation ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0149: RAI Institute VLFM

**Post to:** https://github.com/rai-opensource/vlfm/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for VLFM — language-conditioned navigation substrate
```

**Body:**

```markdown
Hi @rai-opensource vlfm team,

Proposing a URML v0.1 capability-manifest mapping for VLFM (Vision-Language Frontier Maps) over `rai-opensource/vlfm`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

URML's mobility primitives (`move_to`, `dock`, `scan`) compose with VLM-based frontier-map navigation cleanly: URML declares the navigation-substrate class in the manifest; VLFM dispatches the actual exploration; URML's validator gates the manifest-aware constraints (operating zones, safety envelopes). VLFM's distinct contribution — **language-conditioned navigation** — is the schema-extension question URML's outreach is queueing.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0149-rai-vlfm-outreach.md

Questions worth maintainer input on:

1. **Navigation-substrate manifest fields.** Manifest expectations from a VLFM deployment?
2. **Language-conditioned navigation primitive declaration.** Which language-grounded navigation primitives should URML's manifest declare VLFM supports?
3. **Frontier-map state declaration.** Stateful substrate dependency manifest fields?
4. **Bridge home.** URML repo (`reference/navigation-runtime/VlfmAdapter`), RAI-maintained, or external?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0150: Microsoft PSI

**Post to:** https://github.com/microsoft/psi/discussions/new (Discussions enabled, preferred surface for design-discussion)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for PSI — temporal-streams substrate and a license-clarification ask
```

**Body:**

```markdown
Hi @microsoft psi team,

Proposing a URML v0.1 capability-manifest **cross-citation** for PSI over `microsoft/psi`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

The URML-fit framing is **temporal-streams substrate declaration**. URML's manifest declares sensors individually; PSI provides the cross-sensor temporal-alignment + offline-replay infrastructure that downstream URML adapters can compose with. The manifest would declare `temporal_streams_substrate: microsoft_psi` to make the PSI binding observable.

**License-clarification ask** is the gating fact: the repo's license is listed as "Other" by the GitHub API. An explicit OSI declaration would unlock Apache-2.0 downstream reuse.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0150-microsoft-psi-outreach.md

Questions worth maintainer input on:

1. **License clarification.** Can `microsoft/psi` get an explicit OSI license declaration?
2. **Temporal-streams substrate manifest fields.** Clock class, replay-mode declaration, cross-sensor sync semantics?
3. **Bridge home.** Cross-citation only (recommended pending license), URML repo, or Microsoft-maintained?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working cross-citation ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0151: Microsoft CogACT

**Post to:** https://github.com/microsoft/CogACT/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for CogACT — cognition-action joint-architecture VLA
```

**Body:**

```markdown
Hi @microsoft CogACT team,

Proposing a URML v0.1 capability-manifest mapping for CogACT over `microsoft/CogACT`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

CogACT's cognition-action joint-architecture is the distinct contribution URML's manifest would declare. URML's primitive vocabulary is the typed substrate consuming the policy's action output; URML's validator gates the action sequences CogACT emits against the active capability manifest before publish. Same pre-flight-check pattern URML's outreach has used in sibling VLA engagements.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0151-microsoft-cogact-outreach.md

Questions worth maintainer input on:

1. **Repository status.** Active, or paper-publication-only?
2. **Action-head + dexterous-control manifest fields.** Manifest expectations from CogACT perspective?
3. **Cognition-action joint-architecture declaration.** Should URML's manifest declare joint-trained controllers as a distinct class?
4. **Bridge home.** URML repo (`reference/vla-bridge/CogACTBridge`), Microsoft-maintained, or external?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0152: NUS Clear Lab Octopi

**Post to:** https://github.com/clear-nus/octopi/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for Octopi — first soft-robotics RFC + license-clarification + soft-body schema-extension
```

**Body:**

```markdown
Hi @clear-nus Octopi team,

Proposing a URML v0.1 capability-manifest **cross-citation** for Octopi over `clear-nus/octopi`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

This is URML's **first soft-robotics outreach RFC**. Soft-body is a structural URML schema gap — URML's `mobility.drive_type` and `actuators` vocabulary are rigid-body-centric in v0.1 (no `soft_body_continuum`, no `pneumatic_network`). Three Spec RFCs are queued for soft-robotics support; Octopi is the natural research input.

**License-clarification ask**: no SPDX is visible on the repo. An explicit OSI declaration would unlock adapter-grade reuse; cross-citation framing is the recommended posture until license + soft-body Spec RFCs land.

**This is proposal-only**, part of URML's Move #11 outreach (15 net-new VLA / foundation-model RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0152-nus-octopi-outreach.md

Questions worth maintainer input on:

1. **License clarification.** Can `clear-nus/octopi` get an explicit OSI license declaration?
2. **Soft-body mobility class manifest fields.** DOF, continuum-segment count, control-input class?
3. **Pneumatic-network actuator declaration.** Manifest field expectations?
4. **Continuum-manipulator kinematics.** Manifest declaration class and granularity?
5. **Bridge home.** Cross-citation only (recommended), URML repo, or NUS-maintained?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier C (7) — recorded in research file, NOT engaged

See [`vla-net-new-research-2026-05-28.md`](vla-net-new-research-2026-05-28.md) for the full Tier-C list with exclusion causes (PRC origin × 3 — Psi-Robot/DexGraspVLA, InternRobotics/InternNav, HorizonRobotics/HoloMotion; HK gray × 1 — SageCao1125/Mamba-Policy; already engaged in Move-2 × 2 — NVIDIA/Isaac-GR00T, isaac-sim/IsaacLab; superseded × 1 — OpenMind/OM1-OTA). No posts.
