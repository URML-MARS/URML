---
rfc: 0050
title: NVIDIA Isaac integration (Isaac Lab + Isaac-GR00T), request for comment from isaac-sim and NVIDIA Isaac-GR00T maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-23
updated: 2026-05-23
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

# RFC-0050: NVIDIA Isaac integration (Isaac Lab + Isaac-GR00T), request for comment from isaac-sim and NVIDIA Isaac-GR00T maintainers

## Summary

URML proposes a `urml-isaac-bridge` package with two complementary integration vectors against NVIDIA's open Isaac stack:

1. **Isaac Lab task vector.** A task plugin in `isaac-sim/IsaacLab` that consumes validated URML programs and runs them inside the Lab's training and evaluation harnesses.
2. **Isaac-GR00T policy-client vector.** A wrapper around `NVIDIA/Isaac-GR00T`'s server-client `PolicyClient` API that lets a GR00T VLA policy emit URML primitives as its action vocabulary, rather than substrate-specific tensors.

URML already ships a real `IsaacAdapter` in [`reference/isaac-runtime/`](../../reference/isaac-runtime/) against Isaac Sim. This RFC sits one layer above that adapter: Isaac Lab is the learning framework over Sim, and Isaac-GR00T is the open VLA model family NVIDIA distributes for humanoid and manipulation work. No URML spec change. Bridge code is not in this PR; the RFC requests review from both maintainer groups before it ships.

**Strategic posture, stated explicitly.** URML sits ABOVE Isaac Lab and GR00T as substrate-neutral vocabulary, not as a competitor. NVIDIA's stated direction is for Isaac to be "the Android of generalist robotics"; URML's role is the human-readable intent vocabulary that compiles down to GR00T VLA actions and Isaac Lab task steps, and translates upward to natural-language commands.

## Motivation

`isaac-sim/IsaacLab` (7,238 stars, 655 open issues, BSD-3-Clause, both Issues and Discussions enabled with a Show & Tell category, `enhancement` and `question` labels present, last commit 2026-05-23, uses the Gymnasium env-registration API) is NVIDIA's open RL and robot-learning framework on top of Isaac Sim. `NVIDIA/Isaac-GR00T` (7,102 stars, 289 open issues, Apache-2.0 code with NVIDIA Open Model License for weights, Issues enabled, Discussions disabled, codebase closed to PRs during N1.7 Early Access, last commit 2026-05-23) is the open VLA model family for humanoid and manipulation policies. The `isaac-sim` org has 22 public repositories and 1,532 followers.

Both surfaces are genuinely open (license, Issues, downloadable model weights with documented constraints), distinct from the closed GR00T partner-program waitlist that gates early access to in-development model variants. This RFC targets the open public surface, not the partner program.

The combination is the right URML target for the NVIDIA developer community. URML programs validated against URML's capability manifest and safety envelope can drive Isaac Lab training jobs (the URML program is the task spec) and consume GR00T policies as the action source (the policy emits URML primitives, the substrate adapter executes them). Cosmos is out of scope for this RFC.

## Detailed design

URML's existing artifacts that feed in:

- [`reference/isaac-runtime/`](../../reference/isaac-runtime/): shipping `IsaacAdapter` against Isaac Sim, with hermetic unit tests and a live integration test.
- [`reference/mujoco-runtime/`](../../reference/mujoco-runtime/): the sim sibling that proves substrate-neutrality across physics backends.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference. The GR00T policy-client wrapper is the VLA-side sibling.
- [`docs/rfcs/0040-hugging-face-lerobot.md`](0040-hugging-face-lerobot.md): the LeRobot RFC, structurally identical to the proposed GR00T policy-client wrapper. Both wrap a policy's action output and translate into URML primitives.

### Proposed `urml-isaac-bridge` package shape

One package, two vectors. Layout:

```
urml-isaac-bridge/
├── pyproject.toml                  # extras: ["isaaclab"], ["groot"]
└── src/
    └── urml_isaac_bridge/
        ├── __init__.py
        ├── isaaclab/
        │   ├── task.py             # URMLIsaacLabTask wrapping IsaacAdapter
        │   ├── env.py              # ManagerBasedEnv-compatible URML env
        │   └── config.py           # URMLTaskCfg, asset bindings, reward terms
        └── groot/
            ├── policy_wrapper.py   # URMLGrootPolicyClient wrapping PolicyClient
            ├── primitive_decoder.py # tensor -> URML primitive sequence
            └── config.py
```

Both vectors share the URML manifest validation and the Layer-2 primitive vocabulary. They diverge on what they wrap: the Isaac Lab vector wraps the task / env surface; the GR00T vector wraps the policy server-client.

### Vector 1: Isaac Lab task

`URMLIsaacLabTask` loads a URML program plus its capability manifest and safety envelope, validates them statically, then drives Isaac Lab's env step loop by calling IsaacAdapter's step-and-observe surface. Registered through Isaac Lab's Gymnasium-style `gym.register("URML/...")` entry points, so it slots into `IsaacLab/scripts/environments/list_envs.py` and runs under the existing trainers and evaluators without modifying Lab internals.

| URML primitive | Isaac Lab env realisation |
|---|---|
| `move_to(pose)` | IsaacAdapter writes the configured control target; env `step()` advances simulation for `steps_per_command` frames |
| `hover` | zero-velocity station-keeping via IsaacAdapter `wait`; env advances time |
| `wait_for(condition)` | env loop steps until observation matches the predicate (or timeout) |
| `measure(what)` | observation read at the current env tick |
| `report(facts, ...)` | structured task log, surfaced through Isaac Lab's existing logging hooks |
| `grasp` / `release` | task-specific actuator command if the env declares a gripper; not-supported otherwise |

### Vector 2: Isaac-GR00T policy-client wrapper

`URMLGrootPolicyClient` wraps the published GR00T `PolicyClient` server-client API (the same surface a normal GR00T deployment uses). The wrapper takes the policy's action-tensor output, decodes it into a URML primitive sequence using a per-policy configuration (which observation channels map to which primitives), validates the resulting sequence against the URML program's safety envelope, then routes the primitives to whichever URML substrate adapter the deployment is using.

```python
# pseudocode for the policy-client wrapper shape
client = URMLGrootPolicyClient(
    inner=PolicyClient(host=..., port=...),    # standard GR00T API
    primitive_decoder=URMLPrimitiveDecoder(...),
    manifest=load_manifest("..."),
    envelope=load_envelope("..."),
)
for observation in stream:
    primitive_sequence = client.infer(observation)  # raw action -> URML primitives
    runtime.execute(primitive_sequence)             # URML substrate adapter
```

The wrapper preserves GR00T's evaluation contract: a downstream user training or evaluating a GR00T model sees the same `PolicyClient` interface; the URML translation happens at the action-decoding boundary, transparent to GR00T's trainers.

### Compatibility notes

- **Licenses.** Isaac Lab is BSD-3-Clause with an Apache-2.0 mimic extension. Isaac-GR00T code is Apache-2.0; GR00T weights are under the NVIDIA Open Model License (a published, documented license, distinct from the closed partner-program access). Isaac Sim's `isaacsim` wheel is governed by NVIDIA's published EULA. URML is Apache 2.0. The bridge package imports each surface lazily through extras.
- **N1.5, N1.6, N1.7.** N1.7 is in Early Access with the codebase closed to PRs during EA. N1.5 and N1.6 are openly available and the right initial integration targets. The wrapper's API does not depend on which model variant is loaded.
- **Python and CUDA.** Isaac Lab and GR00T target specific Python and CUDA matrices; the bridge's extras pin to those bands.
- **Origin.** NVIDIA Corporation is incorporated in Delaware, US. Passes URML's bundled US-federal default policy at the manifest level without flagging.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No URML artifact changes. Both vectors register through public extension points on their respective sides.

## Drawbacks

- **Proposal-only.** Same posture as RFC-0040 (LeRobot) and RFC-0044 (AWS Robotics): the package shape is concrete, the code is not yet shipped, maintainer feedback informs the implementation before the bridge lands.
- **Two-vector scope is wider than typical.** Combining Isaac Lab and GR00T in one RFC creates a thicker review surface than a single-vector RFC would. Mitigation: the two vectors share a package and a manifest model, so the maintainer review naturally decomposes by vector.
- **N1.7 EA closed to PRs.** The bridge cannot contribute upstream to GR00T during Early Access. URML's vector lives in `urml-isaac-bridge`, not as a GR00T fork.
- **GR00T trains against specific embodiments.** A GR00T policy trained for one humanoid does not transfer to another without retraining; URML's primitive vocabulary is substrate-neutral but the policy is not. The wrapper documents this clearly.

## Alternatives considered

1. **Two separate RFCs.** Rejected. The Isaac Lab and GR00T surfaces share NVIDIA's developer community and the same `urml-isaac-bridge` package; splitting the RFC would force two parallel review threads on overlapping audiences.
2. **Skip GR00T entirely.** Rejected. The earlier mental model of "GR00T is partner-program gated" was incorrect at the open-surface level: the model code is Apache-2.0, weights are published under a documented license, Issues are open. Skipping the open surface would forfeit the reach to the NVIDIA VLA community.
3. **Approach only via the partner program for the strategic conversation.** Considered as a parallel founder-direct track, not in scope for this RFC. The partner program covers in-development model variants and commercial integrations; this RFC reaches the open developer community.
4. **Ship the bridge first, ask later.** Rejected. The Isaac Lab task-registration convention and the GR00T PolicyClient API both have observable choices URML should validate with maintainers before code lands.

## Prior art

- `isaac-sim/IsaacLab`: the upstream framework (7,238 stars, 655 open issues, BSD-3-Clause, last commit 2026-05-23, Gymnasium API).
- `NVIDIA/Isaac-GR00T`: the open VLA model family (7,102 stars, 289 open issues, Apache-2.0 + NVIDIA Open Model License, last commit 2026-05-23, PolicyClient API).
- `isaac-sim/IsaacSim`: the simulator NVIDIA Isaac Lab runs on (BSD-3-Clause).
- [`reference/isaac-runtime/`](../../reference/isaac-runtime/): URML's existing IsaacAdapter against Isaac Sim.
- [`reference/mujoco-runtime/`](../../reference/mujoco-runtime/): the sim sibling.
- [RFC-0040](0040-hugging-face-lerobot.md): the LeRobot RFC. The GR00T policy-client wrapper is structurally identical (a wrapped policy emits a substrate-neutral primitive sequence).
- [RFC-0044](0044-aws-robotics-sim-worlds.md): the simulator-conformance precedent (URML programs as sim workload).
- [RFC-0045](0045-physical-intelligence-openpi.md): the openpi RFC. Parallel structure for a different VLA family.

## Unresolved questions

Provisional pending Isaac Lab and Isaac-GR00T maintainer feedback:

### Isaac Lab vector

1. **Plugin shape.** Is `urml-isaac-bridge/isaaclab/` as a separate package the right integration point, or would maintainers prefer URML tasks to live as `ManagerBasedEnv` subclasses inside Isaac Lab's task registry?
2. **Reward and termination semantics.** URML programs declare intent; Isaac Lab tasks declare reward. Should the task expose a default reward shape (intent-satisfaction signal) and let users override, or stay reward-agnostic?
3. **Observation specification.** URML's `measure` reads a named observation. Should the plugin auto-derive an Isaac Lab observation space from the URML manifest's declared sensors, or require explicit declaration?
4. **GPU vectorization.** Isaac Lab's key strength is parallel-env training. Does running a URML program inside a vectorized env make sense, or should the plugin force `num_envs=1` at first?

### Isaac-GR00T vector

5. **PolicyClient wrapper boundary.** Should the wrapper sit purely on the client side (intercept actions after they arrive from the server), or also propose a server-side optional emission of URML primitive labels alongside tensors?
6. **Strategic positioning.** Does NVIDIA see URML's substrate-neutral intent vocabulary as complementary (a vocabulary above GR00T policies) or as parallel work the GR00T team is already addressing?

### Shared

7. **Downstream link.** Would Isaac Lab or Isaac-GR00T be open to downstream links from their docs to URML's bridge once it publishes?
8. **Anything else.**

## Implementation note

RFC-0050 ships as a single RFC document PR. No bridge code in this PR. Ledger entry under [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml) (Move #2 RFC).

## Requested feedback

For Isaac Lab maintainers:
1. Plugin shape: separate package vs in-tree env (Q1).
2. Reward and termination semantics (Q2).
3. Observation-space auto-derivation (Q3).
4. Vectorization posture (Q4).

For Isaac-GR00T maintainers:
5. PolicyClient wrapper boundary (Q5).
6. Strategic positioning (Q6).

Shared:
7. Downstream link interest (Q7).
8. Anything else.

## How to respond

`isaac-sim/IsaacLab` has both Issues and Discussions enabled with a Show & Tell category, which is the right surface for the Isaac Lab vector's design conversation. `NVIDIA/Isaac-GR00T` has Issues enabled (Discussions disabled), which is the right surface for the GR00T vector. URML's planned channel: a Discussion on `isaac-sim/IsaacLab` (Show & Tell or Ideas) pointing to this RFC for the Isaac Lab vector, and a scoped Issue on `NVIDIA/Isaac-GR00T` narrowed to Q5 and Q6 for the GR00T vector. Optional cross-post on the NVIDIA Developer Forum Isaac Sim subforum (`forums.developer.nvidia.com/c/omniverse/simulation/69`).

URML public Discussions for the broader conversation: https://github.com/URML-MARS/URML/discussions.

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary explains proposal-only posture, distinguishes Isaac Sim (shipping adapter) from Isaac Lab (proposed task plugin) from Isaac-GR00T (proposed policy-client wrapper).
- [x] Strategic posture stated explicitly (URML above Isaac Lab and GR00T as substrate-neutral vocabulary, not against them).
- [x] Motivation grounded in verified data (Isaac Lab 7,238 / 655 BSD-3-Clause; GR00T 7,102 / 289 Apache-2.0; both last commit 2026-05-23).
- [x] Detailed design references existing URML artifacts (`isaac-runtime`, `mujoco-runtime`, `llm-bridge`, RFC-0040, RFC-0045).
- [x] Alternatives considered (four).
- [x] Drawbacks honest (proposal-only, two-vector scope, N1.7 EA closed to PRs, GR00T embodiment specificity).
- [x] Backward compatibility: additive.
- [x] No spec change. No Layer-2 primitive added.
- [x] Surface verified live: both repos' state confirmed via gh API on 2026-05-23.
- [x] Earlier mental model corrected: GR00T's open surface is Apache-2.0 with documented license for weights, distinct from the partner program. Surface posture in this RFC reflects the verified state.
- [x] No em-dashes in body. Voice consistent with the wave.
- [x] Re-read CLAUDE.md §What Claude Should Never Do; compliant. No closed-track conflation. No cloud dependency. No telemetry.
