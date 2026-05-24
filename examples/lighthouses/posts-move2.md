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

# Move #2 post bodies

Copy-paste-ready Issue / Discussion / email bodies for the Move #2 outreach RFCs in [`docs/rfcs/`](../../docs/rfcs/). Each section is one target. Where a target has multiple surfaces (MCP plus Agent Skills, original ALOHA plus Mobile ALOHA, etc.), each surface gets its own post.

Ledger state lives in [`outreach-move2.yaml`](outreach-move2.yaml). After posting, set `sent_at` and `last_touch` to today's date and update `next_action`.

Voice: founder posts under his GitHub identity. The RFC author field already reads `Ido Yahalomi (greenvh@gmail.com)`. Posts sign as the URML maintainer; do not impersonate URML as an organization.

---

## RFC-0040: Hugging Face LeRobot

**Post to:** https://github.com/huggingface/lerobot/issues/new/choose
**Label:** `enhancement`
**Title:** `Proposal: lerobot_policy_urml, a BYOP plugin emitting substrate-neutral URML primitives`

**Body:**

```markdown
Proposing `lerobot_policy_urml`, a plugin that follows LeRobot's published [Bring Your Own Policies](https://huggingface.co/docs/lerobot/bring_your_own_policies) convention. A `URMLPolicy(PreTrainedPolicy)` wrapper composes any inner policy and emits [URML](https://urml.dev) primitives in addition to the raw action tensor. The wrapper preserves LeRobot's training and evaluation contracts (the inner policy stays trainable, eval sees a tensor the way it expects) while making substrate-neutral routing testable in isolation.

URML is an Apache 2.0 specification for substrate-neutral robot intent. Its Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`, plus profile-specific extensions for industrial / drone / mobile / humanoid) sit one layer above ROS 2 / PX4 / Isaac / MuJoCo / AUTOSAR Adaptive / OPC UA Robotics. A policy whose post-processor emits URML can be retargeted across substrates without retraining.

This is proposal-only. No plugin code has been written yet, since the wrapper-vs-pure-post-processor shape and the dataset-annotation shape are both choices the BYOP convention does not pin down.

Full RFC with proposed package layout, primitive-to-policy-output mapping, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0040-hugging-face-lerobot.md

## Feedback we'd value

1. **Wrapper vs. pure post-processor.** Is `URMLPolicy(PreTrainedPolicy)` composing an inner policy the right shape, or should URML stay in a `PolicyProcessorPipeline` only?
2. **Dataset annotation.** Acceptable shapes for a `urml_program` annotation on `LeRobotDataset` v3: sidecar Parquet file in the episode dir, column on the existing Parquet, separate companion dataset by id, or none?
3. **Package home.** PyPI under a URML org, a Hugging Face Hub org under `huggingface.co/urml`, or community PyPI?
4. **Conformance lane.** Open to a downstream URML conformance run published on the Hub model card for policies validated against URML?
5. **Citation form.** Preferred form for downstream URML papers that reference LeRobot.

Happy to answer here, on the HF community Discord, or to open a PR with a stub package once we have signal on the shape.

Thanks for LeRobot and the BYOP convention. Both made this proposal a lot more concrete than it otherwise would have been.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0045: Physical Intelligence (openpi)

**Post to:** https://github.com/Physical-Intelligence/openpi/discussions/new (Show & Tell or Ideas category)
**Cross-reference Issue if Discussion gets low visibility.**
**Title:** `Proposal: urml-openpi-bridge with a URMLOutputs class following openpi's Inputs/Outputs extension pattern`

**Body:**

```markdown
Proposing a `urml-openpi-bridge` package that hooks into openpi's documented Inputs / Outputs extension pattern. A custom `URMLOutputs` class (mirroring the `LiberoOutputs` shape in `src/openpi/policies/libero_policy.py`) translates the policy's `policy.infer(example)["actions"]` output into [URML](https://urml.dev) primitive calls before any motion reaches the substrate adapter. The bridge keeps the raw action tensor on the return dict, so existing openpi evaluation harnesses see the policy as normal. URML emission rides alongside.

URML is an Apache 2.0 specification for substrate-neutral robot intent. Its Layer-2 primitive vocabulary lets π policies retarget across ROS 2 / PX4 / Isaac / MuJoCo / AUTOSAR Adaptive / OPC UA Robotics by switching URML's substrate adapter, without retraining.

This is proposal-only. No bridge code yet, since the Outputs-class-vs-wrapper question and the upstream-vs-standalone packaging question are worth your input first.

Full RFC with proposed package layout, primitive-to-action mapping, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0045-physical-intelligence-openpi.md

## Feedback we'd value

1. **Extension shape.** Is a custom `URMLOutputs` (mirroring `LiberoOutputs`) the right hook, or would Pi prefer a wrapper around `policy_config.create_trained_policy(...)` that intercepts `infer(...)`?
2. **Package home.** Upstream into `Physical-Intelligence/openpi` as a reference `URMLOutputs`, or a standalone third-party PyPI package (`urml-openpi-bridge`)?
3. **Action-chunk semantics.** The proposed `move_to` collapsing rule assumes contiguous joint-target or end-effector-pose tokens. Safe across π₀, π₀-FAST, π₀.₅?
4. **Remote inference.** URMLOutputs on the websocket server side or the robot client side?
5. **Dataset annotation.** openpi consumes LeRobot v3; is a sidecar annotation (matching the LeRobot RFC) the right shape?

Thanks for openpi and for the open-research posture. The Inputs / Outputs pattern made this proposal a lot easier to ground.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0046: Open X-Embodiment

Two surfaces. Email is primary; Issue is a cross-reference for visibility.

### Email body (primary)

**Send to:** open-x-embodiment@googlegroups.com
**Subject:** `Proposal: optional URML primitive annotation on OXE trajectories (substrate-neutral action vocabulary)`

**Body:**

```text
Hi all,

I'm Ido Yahalomi, the maintainer of URML (Universal Robot Language), an Apache 2.0 specification for substrate-neutral robot intent at urml.dev. I'd like to propose an optional URML primitive annotation layer on OXE trajectories: alongside the existing per-embodiment action tensors, an optional urml_program sidecar field per episode that gives a model trained on URML-annotated OXE the ability to emit URML primitives directly, instead of substrate-specific actions.

URML's Layer-2 vocabulary (move_to, grasp, release, measure, wait_for, report, plus profile-specific extensions for industrial / drone / mobile / humanoid) is what the per-embodiment action tensors agree on at the intent level. An episode that carries a URML primitive sequence alongside its raw actions becomes substrate-neutral training data: cross-embodiment policy transfer becomes embodiment-aware AND substrate-aware.

The proposal is additive: episodes without the urml_program field continue to work unchanged. Annotation can land in three forms (programmatic from action structure, programmatic from natural-language captions, human-in-the-loop on a subset), and I'd value governance input on which is acceptable for upstream merge.

Full RFC with the proposed schema, annotation paths, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0046-open-x-embodiment.md

Feedback I'd value most:

1. Schema acceptability (sidecar field vs. companion dataset that joins by id)
2. Annotation quality bar for upstream acceptance
3. Per-dataset opt-in vs. blanket annotation across all 60 datasets
4. Cross-listing interest with URML conformance for downstream models
5. Routing to DeepMind's Gemini Robotics partner network

A cross-reference Issue is open on google-deepmind/open_x_embodiment for repo visibility.

Thanks for OXE. The dataset shape is what makes this proposal possible.

— Ido Yahalomi (URML maintainer, greenvh@gmail.com, urml.dev)
```

### Issue body (cross-reference)

**Post to:** https://github.com/google-deepmind/open_x_embodiment/issues/new
**Label:** `question` (or feature-shaped equivalent)
**Title:** `Proposal: optional urml_program sidecar annotation on OXE trajectories (cross-reference to googlegroups email)`

**Body:**

```markdown
Cross-reference to the email sent to `open-x-embodiment@googlegroups.com` on $TODAY for repo visibility. The proposal: an optional `urml_program` sidecar field per OXE trajectory that carries a substrate-neutral primitive sequence alongside the existing per-embodiment action tensor. Additive, opt-in, indexed by `start_step` / `end_step` so it aligns with the action timeline.

URML is an Apache 2.0 spec at [urml.dev](https://urml.dev). Move #2 is URML's outreach program to AI / ML-layer projects.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0046-open-x-embodiment.md

Posting here for visibility to anyone watching `google-deepmind/open_x_embodiment`. The substantive discussion is happening on the Google Group.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0047: Allen Institute MolmoAct

Two surfaces. Issue is primary; courtesy email reaches the authors named in the repo.

### Issue body (primary)

**Post to:** https://github.com/allenai/molmoact/issues/new/choose
**Label:** `enhancement`
**Title:** `Proposal: urml-molmoact-bridge with preview-and-correct loop semantics via URML wait_for + report primitives`

**Body:**

```markdown
Proposing a `urml-molmoact-bridge` package that wraps MolmoAct's action output and translates it into [URML](https://urml.dev) primitive calls. The bimanual coordination story and MolmoAct's preview-before-acting capability both map naturally onto URML primitives: `wait_for(human_signal)` plus `report(preview)` is the URML surface for the preview-and-correct loop, and a `move_to` paired with a `wait_for(other_arm_ready)` on a sibling gripper id expresses the bimanual coordination MolmoAct already supports.

URML is an Apache 2.0 specification for substrate-neutral robot intent at urml.dev. Its Layer-2 primitives let a MolmoAct policy retarget across ROS 2 / PX4 / Isaac / MuJoCo / AUTOSAR Adaptive / OPC UA Robotics by switching URML's substrate adapter, without retraining.

This is proposal-only. No bridge code yet, since the wrapper shape and especially the bimanual-coordination primitive question are worth Ai2 input first.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0047-allen-institute-molmoact.md

## Feedback we'd value

1. **Wrapper home.** Contributed example in `allenai/molmoact` (Ai2-side) or standalone third-party PyPI package (URML-side)?
2. **Preview-and-correct semantics.** Is `wait_for(human_signal)` plus `report(preview)` the right URML expression, or does Ai2 see a cleaner mapping?
3. **Bimanual coordination.** Does URML need a Layer-2 bimanual-coordination primitive (e.g., `coordinate(arm0, arm1, ...)`) or is Layer-3 composition sufficient?
4. **Dataset annotation.** Is the `urml_program` sidecar field acceptable for the new two-armed tabletop dataset?
5. **Conformance lane.** Open to a URML-conformance run on each MolmoAct release's model card?

Sending a parallel courtesy email to the authors named in the repo. Thanks for MolmoAct 2 and the open-science posture.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

### Courtesy email body

**Send to:** haoquanf@allenai.org, jasonl@allenai.org, jiafeid@allenai.org
**Cc (optional):** Dieter Fox via Ai2's published Embodied AI page
**Subject:** `URML / MolmoAct integration proposal (urml-molmoact-bridge with preview-and-correct semantics)`

**Body:**

```text
Hi Haoquan, Jason, Jiafei,

I'm Ido Yahalomi, the maintainer of URML (Universal Robot Language), an Apache 2.0 specification for substrate-neutral robot intent at urml.dev. I've drafted a proposal for a urml-molmoact-bridge that wraps MolmoAct's action output and translates it into URML primitive calls, with particular attention to MolmoAct's preview-and-correct loop (which maps nicely onto URML's wait_for and report primitives) and the bimanual coordination question (which is a known open question in URML's Layer-2 vocabulary).

The full RFC is on URML's repo:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0047-allen-institute-molmoact.md

A cross-reference Issue is open on allenai/molmoact for repo visibility. The questions most relevant to the MolmoAct team are about the bridge home (Ai2-side contributed example vs. standalone PyPI), the preview-and-correct semantics, and the bimanual-coordination primitive question.

Cc'ing Dieter (if reachable through Ai2's Embodied AI initiative page) since the institutional alignment with the broader robotics direction is also relevant.

Happy to answer here or on the GitHub Issue.

Thanks for the open-science posture and for MolmoAct 2.

— Ido Yahalomi (URML maintainer, greenvh@gmail.com, urml.dev)
```

---

## RFC-0048: Anthropic (MCP + Agent Skills)

Two surfaces, two posts. MCP is the Discussion; Agent Skills is the Issue.

### MCP Discussion body

**Post to:** https://github.com/modelcontextprotocol/specification/discussions/new (Show & Tell or Ideas category)
**Title:** `Proposal: URML as an MCP server (urml_translate / urml_validate / urml_execute tools for substrate-neutral robot intent)`

**Body:**

```markdown
Proposing an MCP server that exposes [URML](https://urml.dev)'s translate / validate / execute pipeline as MCP tools. Any MCP client (Claude Desktop, Claude Code, Cursor, future MCP-aware tools) becomes a URML driver: a robotics workflow goes from "ask the model" to "the model drives the robot" without leaving the conversation, with URML's static validation as the safety boundary.

URML is an Apache 2.0 specification for substrate-neutral robot intent. Its Layer-2 primitive vocabulary sits above ROS 2 / PX4 / Isaac / MuJoCo / AUTOSAR Adaptive / OPC UA Robotics. The MCP server exposes three tools:

- `urml_translate`: English to URML
- `urml_validate`: URML program plus manifest plus profile to pass / fail with envelope
- `urml_execute`: validated URML program plus substrate brand to hermetic execution trace

Plus an optional MCP `Resource` exposing the primitive vocabulary as a fetchable document. The server is offline by default. The validator is non-bypassable from the MCP surface.

This is proposal-only. No server code yet, since the tool surface (granularity, additions, removals) and the resource-vs-prompt question for the primitive vocabulary are worth MCP-maintainer input first.

Full RFC with proposed tool surface, resource surface, alternatives, and the parallel Agent Skills integration vector:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0048-anthropic-mcp-and-agent-skills.md

## Feedback we'd value

1. **Tool surface.** Are the three tools the right granularity, or should they be merged, split, or augmented with `urml_lint` / `urml_explain`?
2. **Resource vs. Prompt.** Should the primitive vocabulary be exposed as an MCP Resource, an MCP Prompt, or both?
3. **Server distribution.** Should URML publish the server to the MCP registry, or rely on PyPI distribution only at first?
4. **SEP route.** If the URML server surfaces a spec-extension need, is `/seps` the right channel?

A parallel Issue is open on `anthropics/skills` for the Agent Skills vector of this proposal.

Thanks for MCP and the open-standard posture.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

### Agent Skills Issue body

**Post to:** https://github.com/anthropics/skills/issues/new/choose
**Label:** `enhancement` or feature-proposal equivalent
**Title:** `Proposal: a urml Skill teaching Claude the URML grammar for substrate-neutral robot intent`

**Body:**

```markdown
Proposing a `urml` Agent Skill that teaches Claude to author [URML](https://urml.dev) programs natively. Pairs with the MCP server vector (parallel Discussion open on `modelcontextprotocol/specification`) so a Claude session with the skill loaded can author URML programs, validate them, and execute them via MCP without leaving the conversation.

URML is an Apache 2.0 specification for substrate-neutral robot intent. The Skill folder follows the `anthropics/skills` published convention:

```
skills/urml/
├── SKILL.md                  # yaml frontmatter + grammar overview
├── grammar/
│   ├── layer-2-primitives-summary.md
│   ├── manifest-format.md
│   └── validation-rules.md
└── examples/
    ├── home-red-mug.urml.yaml
    ├── industrial-pick-and-place.urml.yaml
    └── drone-survey.urml.yaml
```

The `SKILL.md` frontmatter:

```yaml
---
name: urml
description: Author URML (Universal Robot Language) programs from English requests. Use this skill when the user wants to describe robot intent, generate a URML program, validate it against a capability manifest, or execute it on a substrate.
---
```

This is proposal-only. No Skill folder yet, since the skill-scope (inline grammar vs. defer to MCP Resource) and the distribution-channel question are worth Anthropic input first.

Full RFC with the MCP-server companion vector:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0048-anthropic-mcp-and-agent-skills.md

## Feedback we'd value

1. **Skill scope.** How much of the URML grammar should the Skill inline vs. defer to the spec via the MCP Resource?
2. **Distribution.** PR to `anthropics/skills` (canonical channel), mirror in URML's repo, both?
3. **Vetting.** Per Anthropic's measured rollout, what is the path for community Skills like this one?
4. **Composition with MCP.** When the URML MCP server is available, should the Skill defer to it, or duplicate enough to stay self-sufficient?

Thanks for the Agent Skills open standard and for Skill Creator (which made authoring this proposal a lot easier).

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0052: Meta FAIR V-JEPA 2

**Post to:** https://github.com/facebookresearch/vjepa2/issues/new/choose
**Label:** `question` or research-collab framing (not feature request)
**Title:** `Research-collab proposal: URML primitives as V-JEPA 2-AC action conditioning + V-JEPA 2 predictions as URML predictive-safety lane`

**Body:**

```markdown
Hi V-JEPA 2 team,

Posting this as a research-collaboration proposal rather than a feature request. I'm Ido Yahalomi, the maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. Two integration vectors with V-JEPA 2 that look interesting from URML's side:

**Vector A: URML primitives as V-JEPA 2-AC action conditioning input.** Each URML primitive maps to one or more action-conditioning tokens; V-JEPA 2-AC's prediction proceeds normally over those tokens. The downstream effect: a robot trained under URML-annotated Droid (RFC-0046 proposes the OXE annotation pass) becomes substrate-aware as well as embodiment-aware.

**Vector B: V-JEPA 2 predictions as URML's predictive-safety lane.** Before URML's validator accepts a program, the world model predicts the end-state video embedding; URML's safety envelope checks the prediction. Pre-execution simulation of a candidate program against a learned model of the world. No other URML target offers this shape; V-JEPA 2 is the only world-model in URML's Move #2 outreach landscape.

Proposal-only. No bridge code yet, since the action-conditioning encoding (Q1) and the predictive-safety framing (Q2) are worth FAIR input first.

Full RFC with proposed schema, action-conditioning mapping, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0052-meta-fair-vjepa2.md

## Feedback we'd value

1. **Action-conditioning encoding.** What is the right token-level encoding for URML primitives in V-JEPA 2-AC's action conditioning?
2. **Predictive-safety framing.** Use as a pre-execution gate, or evaluation-only?
3. **Droid annotation.** Is the URML annotation on Droid trajectories (matching RFC-0046) acceptable to the Droid maintainers via FAIR?
4. **Bridge home.** Standalone `urml-vjepa2-bridge` on PyPI, contributed example in `facebookresearch/vjepa2`, or both?
5. **Research-collab shape.** Is there a workshop, benchmark, or paper where a URML conformance lane would be a useful contribution?

Thanks for V-JEPA 2 and for the open-research posture. The world-model angle is the most distinctive integration I've found across this outreach program.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0054: TRI Large Behavior Models

**Post to:** https://github.com/TRI-ML/vla_foundry/issues/new/choose
**Label:** `enhancement`
**Title:** `Proposal: urml-tri-lbm-bridge plugging into vla_foundry's @register_model_params and DataParams extension pattern`

**Body:**

```markdown
Proposing a `urml-tri-lbm-bridge` package that follows `vla_foundry`'s documented `@register_model_params()` decorator and `DataParams` subclass-registration pattern. Two integration vectors:

**Vector A: LBM inference emitting URML primitives.** A post-inference adapter wraps the `vla_foundry/inference/scripts/` deployment path so the LBM's action chunk is translated into [URML](https://urml.dev) primitive calls before any motor command reaches the substrate.

**Vector B: URML-annotated training via DataParams.** A `URMLAnnotatedDataParams` subclass that accepts trajectories carrying the `urml_program` sidecar (matching RFCs 0046 OXE and 0047 Ai2 MolmoAct). LBMs trained under this DataParams emit URML primitives natively.

URML is an Apache 2.0 specification for substrate-neutral robot intent. The bridge is structurally identical to the LeRobot, openpi, and MolmoAct bridges proposed in adjacent Move #2 RFCs; vla_foundry's extension pattern is unusually clean among them, which is why this RFC follows the published convention verbatim rather than proposing changes to it.

Proposal-only. No bridge code yet, since the DataParams contract (Q1) and the inference-wrapper home (Q2) are worth TRI-ML input first.

The TRI plus Boston Dynamics partnership (October 2024) targets Atlas with LBMs. URML already ships `SpotAdapter` (RFC-0043 on BD's quadruped) and a future humanoid-runtime extension would close the loop on Atlas-via-LBM deployment.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0054-tri-large-behavior-models.md

## Feedback we'd value

1. **DataParams contract.** Is the `urml_annotated` subclass under draccus the right mechanism, or would TRI prefer a different opt-in pattern?
2. **Inference wrapper home.** Standalone `urml-tri-lbm-bridge` on PyPI (URML-side) or upstream as a contributed example in `TRI-ML/vla_foundry/inference/`?
3. **LBM version coupling.** Tight coupling to current LBM action-chunk format, or version-tolerant via draccus config?
4. **Atlas deployment-path scoping.** Is a URML-emitting LBM on Atlas a meaningful planning target for the bridge today, or should the RFC stay scoped to training and inference only?
5. **chiral integration.** Should the inference wrapper expose primitive emission through TRI's `chiral` WebSocket evaluation interface?
6. **Annotation provenance under DGP.** How should the annotation pass document its provenance under DGP's conventions?

Thanks for vla_foundry, for the LBM program, and for Drake (separate RFC-0059 follow-up). The open-research posture across the TRI stack is the largest part of why URML's Move #2 outreach has a coherent shape.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0055: NVIDIA Cosmos-Reason1

**Post to:** https://github.com/nvidia-cosmos/cosmos-reason1/issues/new/choose
**Title:** `Proposal: urml-cosmos-bridge as a constrained-decoding wrapper over Cosmos-Reason1 (reasoner emits URML primitive programs)`

**Body:**

```markdown
Proposing a `urml-cosmos-bridge` package that wraps Cosmos-Reason1's documented inference path (`scripts/inference.py` via `transformers>=4.51.3`) with constrained decoding against [URML](https://urml.dev)'s grammar. The reasoner stops emitting free-form text plans and starts emitting validated URML primitive programs that URML's substrate adapter can execute.

URML is an Apache 2.0 specification for substrate-neutral robot intent. Among URML's Move #2 outreach targets, Cosmos-Reason1 is the only reasoner (every other target is either a policy that emits actions or a world model that predicts state). The integration is constraining the reasoner's output space to URML's primitive vocabulary, not wrapping an action stream.

URMLConstrainedCosmosReasoner loads a Cosmos-Reason1 checkpoint and runs inference with the URML profile-scoped GBNF grammar (URML already ships GBNF export per RFC-0021). The output is guaranteed parseable as URML and is validated against the manifest before return.

Proposal-only. No bridge code yet, since the constrained-decoding integration path (Q1) and the prompt-template direction (Q2) are worth Cosmos input first.

Full RFC with proposed prompt templates, mapping table, drawbacks, and alternatives:

https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0055-nvidia-cosmos-reason.md

## Feedback we'd value

1. **Constrained-decoding integration.** Grammar-constrained decoding via standard `transformers` API, or a Cosmos-specific decoder hook through `cosmos-cookbook`?
2. **Prompt-template direction.** What prompt shapes elicit Cosmos-Reason1's best reasoning when constrained to URML's primitive vocabulary?
3. **Reason 2 timeline.** When Reason 2 ships, migration path for the bridge?
4. **Bridge home.** Standalone `urml-cosmos-bridge` on PyPI, contributed example in `nvidia-cosmos/cosmos-cookbook`, or both?
5. **Cosmos-Predict integration.** A parallel RFC (RFC-0057) wires `cosmos-predict2.5` into URML's predictive-safety lane. Composing Reason1 with Predict2.5 closes a loop URML cares about.
6. **Evaluation alignment.** Would a URML-conformance evaluation lane be a useful addition?

Thanks for the open-source Cosmos posture across Reason and Predict.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0056: Stanford ALOHA and Mobile ALOHA

Two surfaces. Mobile ALOHA is primary; original ALOHA is cross-reference.

### Mobile ALOHA Issue body (primary)

**Post to:** https://github.com/MarkFzp/mobile-aloha/issues/new/choose
**Label:** `enhancement` or feature-shaped equivalent
**Title:** `Research-collab proposal: urml-aloha-bridge for in-the-loop URML primitive labelling + post-hoc annotation`

**Body:**

```markdown
Hi MarkFzp,

Posting this as a research-collaboration proposal. I'm Ido Yahalomi, the maintainer of [URML](https://urml.dev), an Apache 2.0 specification for substrate-neutral robot intent. The integration with ALOHA is at the data layer (teleoperation and recording), not the runtime layer. Two vectors:

**Vector A: URML-aware extension to `aloha_scripts/record_episodes.py`.** During recording, the operator selects the current URML primitive via a keyboard shortcut (or voice via URML's NL layer). The recorder writes the primitive label alongside the existing observation and action streams. Every frame becomes tagged with the URML primitive the operator was executing.

**Vector B: Post-hoc URML annotation pass.** For already-recorded ALOHA datasets, a pass infers URML primitive boundaries from observation and action streams plus any natural-language task captions, using URML's existing LLM bridge.

The result of either path feeds downstream training (LeRobot, openpi, MolmoAct, GR00T, TRI LBM) with URML-annotated data via the standard LeRobotDataset v3 + `urml_program` sidecar shape (RFCs 0040 / 0046).

Proposal-only. No bridge code yet, since the labelling UX (Q1) and the bimanual-coordination primitive question (Q2) are worth ALOHA-maintainer input first.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0056-stanford-aloha.md

## Feedback we'd value

1. **Labelling UX.** Keyboard shortcut, voice via URML's NL layer, pedal trigger, or something else?
2. **Bimanual coordination.** Does URML need a Layer-2 bimanual-coordination primitive (`coordinate(arm0, arm1, ...)`), or is Layer-3 composition over single-arm primitives sufficient? Same open question as RFC-0047 (Ai2 MolmoAct).
3. **Annotation provenance.** How should the URML annotation track which path produced it (operator-labelled vs. post-hoc inferred)?
4. **Bridge home.** Standalone `urml-aloha-bridge` on PyPI (URML-side), contributed example in `MarkFzp/mobile-aloha` (ALOHA-side), or separate Stanford-affiliated repo?
5. **Existing-dataset coverage.** Is there a high-leverage subset of existing ALOHA recordings worth annotating first?
6. **Hardware-tutorial alignment.** Should the Stanford Robotics Center tutorial include a URML setup step?

A parallel reference Issue is open on `tonyzhaozh/aloha` to reach the original ALOHA maintainer line.

Thanks for Mobile ALOHA and for the open-hardware recipe. The reproducibility is what makes this proposal possible at all.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

### Original ALOHA Issue body (cross-reference)

**Post to:** https://github.com/tonyzhaozh/aloha/issues/new
**Title:** `Cross-reference: URML / ALOHA integration proposal (primary thread on MarkFzp/mobile-aloha)`

**Body:**

```markdown
Cross-reference to the URML / ALOHA integration proposal filed on MarkFzp/mobile-aloha on $TODAY. The proposal extends `aloha_scripts/record_episodes.py` with optional URML primitive labelling and proposes a post-hoc annotation pass over already-recorded ALOHA datasets.

URML is an Apache 2.0 spec at [urml.dev](https://urml.dev). The data shape converges on LeRobotDataset v3 plus the `urml_program` sidecar (RFCs 0040 / 0046).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0056-stanford-aloha.md

Primary thread: https://github.com/MarkFzp/mobile-aloha/issues/$N (link after that thread is opened)

Posting here for visibility to anyone watching `tonyzhaozh/aloha`. The substantive discussion is on the Mobile ALOHA thread.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0057: NVIDIA Cosmos-Predict2.5

**Post to:** https://github.com/nvidia-cosmos/cosmos-predict2.5/issues/new/choose
**Title:** `Proposal: urml-cosmos-predict-bridge wiring Cosmos-Predict2.5 into URML's predictive-safety lane (composes with Reason1)`

**Body:**

```markdown
Proposing a `urml-cosmos-predict-bridge` package that wires `cosmos-predict2.5` into [URML](https://urml.dev)'s predictive-safety lane: before any motion executes, the world model predicts the post-execution video state, and URML's safety envelope checks the prediction. NVIDIA-side parallel of the V-JEPA 2 Vector B proposal in RFC-0052.

Composes with the Cosmos-Reason1 proposal (RFC-0055, parallel Issue on `nvidia-cosmos/cosmos-reason1`). Reason1 emits URML programs from images and questions; Predict2.5 takes those URML programs as text input and renders predicted future video; URML's envelope validates the prediction. Closed loop: reason about what to do, predict what happens if it happens, validate, execute or reject.

URML is an Apache 2.0 specification for substrate-neutral robot intent.

Proposal-only. No bridge code yet, since the URML-to-prompt encoding (Q1) and the closed-loop infrastructure question (Q5) are worth NVIDIA input first.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0057-nvidia-cosmos-predict.md

## Feedback we'd value

1. **URML-to-prompt encoding.** Natural-language paraphrase, raw YAML, structured grammar Predict2.5 was trained to expect, or something else?
2. **Robot inference variant.** Is the robot variant the right entry point for URML's predictive-safety lane?
3. **Cost-aware deployment.** Recommendations for when to invoke the predictive-safety lane vs. when to skip it?
4. **V-JEPA 2 coexistence.** URML's future predictive-safety spec is intended to support both Cosmos and V-JEPA 2 as backends; alignment opportunities?
5. **Reason1 + Predict2.5 closed loop.** Is there NVIDIA infrastructure (Omniverse, NIM, hosted endpoints) where the loop is already a supported deployment pattern?
6. **Distillation default.** Full-precision or distilled checkpoints by default?

Thanks for Cosmos-Predict2.5 and for the open-source posture across the Cosmos stack.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0058: OpenAI (cold knock)

**Post to:** https://github.com/openai/openai-cookbook/issues/new/choose
**Label:** `question`
**Title:** `URML robotics-integration proposal (cold knock pending OpenAI's eventual public robotics surface)`

**Body:**

```markdown
Hi OpenAI,

Filing this as an honest cold knock. URML's Move #2 outreach program has filed RFCs against every major US AI lab with substantive robotics work (Anthropic, Google DeepMind via OXE, Meta FAIR, NVIDIA, Ai2, TRI, Physical Intelligence, Hugging Face LeRobot, Stanford ALOHA). OpenAI's robotics team restarted in February 2025 but the work is intentionally non-public to date. This RFC closes the asymmetry honestly: URML's primitive vocabulary plus validator are documented, and we'd like OpenAI to remember URML's name when the robotics work goes public.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`, plus profile extensions) sit above ROS 2 / PX4 / Isaac / MuJoCo / AUTOSAR Adaptive / OPC UA Robotics.

The integration patterns URML has documented for other targets:

- Wrapper around a policy's action method (RFC-0040 LeRobot, RFC-0045 openpi, RFC-0047 MolmoAct, RFC-0054 TRI LBM)
- Constrained-decoding over a reasoning model (RFC-0055 Cosmos-Reason1)
- Predictive-safety lane against a world model (RFC-0052 V-JEPA 2, RFC-0057 Cosmos-Predict)

When OpenAI publishes a robotics SDK, model, or API, URML's integration follows whichever shape fits. URML's `reference/llm-bridge/` already supports OpenAI's general-purpose LLM API; the robotics-specific extension is the forward-declared piece this RFC names.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0058-openai-robotics.md

## Asks (low expectation of immediate answer)

1. Is there a current or planned public surface where URML's proposal could be reviewed by the robotics team directly?
2. Expected shape of the first public robotics artifact (SDK, model release, hosted API)?
3. Openness to URML being a documented integration target when the team is ready to publish?
4. Right outreach channel for cold-knock proposals like this one?

No expectation of a substantive reply on this thread. Filing for the record.

Thanks for the LLM ecosystem URML's bridge already relies on.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0059: Drake

**Post to:** https://github.com/RobotLocomotion/drake/discussions/new (Ideas or Show & Tell category)
**Title:** `Proposal: urml-drake-bridge with DrakeAdapter substrate + Drake-backed analytical safety lane`

**Body:**

```markdown
Proposing a `urml-drake-bridge` package with two integration vectors against Drake:

**Vector A: `DrakeAdapter` as URML substrate.** Wraps a `drake::systems::Simulator` plus `Diagram`, implements URML's substrate Protocol (the same one used by `MockROSAdapter`, the planned `IsaacAdapter` and `MuJoCoAdapter`), translates URML primitive calls into Drake control inputs.

**Vector B: Drake-backed analytical safety lane.** Drake's `InverseKinematics`, `CollisionChecker`, and `DirectCollocation` solvers feed URML's safety envelope. Programs validate against Drake's model-based verification before any execution. The analytical counterpart to the learned-world-model safety lanes proposed for V-JEPA 2 (RFC-0052) and Cosmos-Predict2.5 (RFC-0057).

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). Drake fills the model-based-verification niche the learning-first Move #2 targets do not.

Proposal-only. No bridge code yet, since the substrate-adapter shape (Q1) and the verification surface scope (Q2) are worth Drake-maintainer input first.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0059-drake-model-based-robotics.md

## Feedback we'd value

1. **Substrate-adapter shape.** Is wrapping `Simulator` plus `Diagram` the right entry point for URML's Protocol, or does Drake recommend a `LeafSystem` subclass instead?
2. **Verification surface scope.** Which solvers are the most appropriate first targets for the analytical safety lane?
3. **Python binding coverage.** Are the bindings for the proposed verification calls complete, or would URML need to contribute upstream wrappers?
4. **Bridge home.** Standalone `urml-drake-bridge` on PyPI, contributed example in `RobotLocomotion/drake/examples/`, or both?
5. **Analytical-plus-predictive contract.** URML's future predictive-safety spec will need a contract that supports both analytical (Drake) and predictive (V-JEPA 2, Cosmos-Predict) backends. Is there a Drake-side perspective on what that contract should look like?
6. **TRI alignment.** TRI co-maintains Drake and ships LBMs (separate RFC-0054). Threaded together institutionally, or kept separate?

Thanks for Drake. The model-based-robotics open-source surface is the largest part of why this RFC is substantive and not aspirational.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## RFC-0060: MuJoCo

**Post to:** https://github.com/google-deepmind/mujoco/discussions/new (help or questions category, since this is a substantive integration proposal)
**Title:** `Proposal: formalizing URML's mujoco-runtime stub into a full MuJoCoAdapter + optional urml_envelope_plugin`

**Body:**

```markdown
Posting this as a substantive integration proposal. URML already ships a `reference/mujoco-runtime/` stub and a gated `mujoco-integration.yml` CI workflow, but the adapter is not feature-complete. This RFC formalizes the in-progress integration and surfaces two vectors:

**Vector A: `MuJoCoAdapter` as URML substrate.** A full adapter wrapping `mujoco.MjModel`, `mujoco.MjData`, and `mujoco.mj_step` per the documented Python bindings (>=3.10). Implements URML's substrate Protocol; runs URML programs against MuJoCo's physics.

**Vector B: Optional `urml_envelope_plugin`.** Uses MuJoCo's documented `/plugin/` architecture to expose URML primitive semantics inside the simulation loop. At simulation step, the plugin checks the next URML primitive's preconditions against MuJoCo's state and enforces URML's safety envelope without leaving the physics loop.

URML is an Apache 2.0 specification for substrate-neutral robot intent at [urml.dev](https://urml.dev). The RFC is honest about the stub-to-full gap: "URML supports MuJoCo" (currently claimed) is closer to "URML's MuJoCo adapter is feature-complete" (not yet true).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0060-mujoco-integration.md

## Feedback we'd value

1. **Adapter shape.** Is wrapping `MjModel` plus `MjData` plus `mj_step` directly the right entry point for URML's Protocol, or does DeepMind recommend a different composition?
2. **MJCF vs URDF.** URML manifests reference URDF more commonly; is MuJoCo's URDF importer sufficient, or should the adapter expect MJCF first-class?
3. **Plugin viability.** Is the `urml_envelope_plugin` (Vector B) a use case the MuJoCo plugin architecture supports cleanly?
4. **DeepMind alignment.** Should URML coordinate the MuJoCo integration with the OXE annotation work (RFC-0046)? Technically independent but institutionally adjacent.
5. **CI integration.** Would DeepMind be open to MuJoCo's CI exercising a URML-validated scenario as one of its integration tests?

Thanks for MuJoCo and for the open-source posture. URML's substrate-neutrality story leans on this engine more than on any other single piece of upstream open-source.

— Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev))
```

---

## Workflow for posting

For each target (in any order, but recommended to start with the open-source-friendly ones for fastest feedback):

1. Open the target's new-Issue or new-Discussion URL (above each section).
2. Paste the title.
3. Paste the body (the contents inside the ```markdown or ```text fence, NOT the fence markers themselves).
4. Apply the recommended label if the form requires one.
5. Submit.
6. Copy the resulting Issue / Discussion URL.
7. Update [`outreach-move2.yaml`](outreach-move2.yaml) for that slug:
   - Set `sent_at` to today.
   - Set `last_touch` to today.
   - Append the URL to `notes`.
   - Update `next_action` to the chosen wait window (Move #1 used "wait 14 d").
8. Continue.

Move #1 sent 16 posts in one day. Move #2 has 13 (mine) and the founder may extend with the 8 in-progress parallel drafts (RFC-0041 ArduPilot, RFC-0042 Waymo, RFC-0043 Spot, RFC-0044 AWS Robotics, RFC-0049 ANYmal, RFC-0050 NVIDIA Isaac, RFC-0051 CARLA, RFC-0053 Open-RMF). The post-body drafts for the founder's parallel work are not in this file; the founder can write them in the same shape, or ask URML to.

After all posts are sent, the ledger reflects the truth and `make audit` re-measures cleanly.
