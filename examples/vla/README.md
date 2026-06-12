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

# URML as the validated-intent gate for a vision-language model

A worked example answering the question @TangmereCottage asked on
[OpenMind/OM1#2587](https://github.com/OpenMind/OM1/issues/2587): **how does URML
coexist with world models / vision-language models?**

It does not compete with them. The model is the front end; URML is the gate.

```
  multimodal input            interpreted intent           validated intent          substrate
  (voice + gesture)  ──VLM──▶  (a URML program)  ──URML──▶  (only if it passes)  ──▶  robot / learned policy
                              the model proposes            URML validates against
                                                            the manifest + safety envelope
```

The model (VLM / VLA / world model) turns voice and gesture into an *intent*.
URML is the typed layer that **validates that intent against the capability
manifest and the safety envelope before it reaches an actuator**. Safe intents
dispatch; unsafe ones are rejected at the gate, with a reason, and never actuate.
URML adds typing and a safety boundary to the model's output; it does not slow
the model down or replace it.

## What it shows

[`validate_intents.py`](validate_intents.py) runs five model-interpreted intents
([`interpreted-intents.yaml`](interpreted-intents.yaml)) through the gate against
a home-service [manifest](home-service.manifest.yaml) + [safety envelope](safety-envelope.yaml):

| Interpreted intent | Gate decision |
| ------------------ | ------------- |
| "head to the kitchen" → `move_to(kitchen)` | **DISPATCH** |
| "bring me the mug" → `move_to → detect → grasp(gentle)` | **DISPATCH** |
| "grab it as hard as you can" → `grasp(force=50 N)` | **REJECTED** — `envelope.force_exceeded` (gripper rated 5 N) |
| "go wait in the group of people" → `move_to(crowd_spot)` | **REJECTED** — `envelope.occupancy_zone_intrusion` |
| "go wait in the garage" → `move_to(garage)` | **REJECTED** — `capability.missing_location` (the robot's world model has no garage) |

The last one is the point for a VLM: when the model **hallucinates** a target the
robot does not actually have, URML catches it statically, before the robot moves.

## Where the fast "Stop" reflex lives

A reflex like voice-"Stop" + flat-hand → halt should be *fast*, not routed through
slow validation. In URML that is a **monitorable property** on the safety envelope
([RFC-0382](../../docs/rfcs/0382-monitorable-temporal-logic-envelope.md)): a
declared, pre-validated rule a runtime monitor enforces directly. The gate
validates the *interpreted intent* before dispatch; it does not sit in the reflex
loop, so it adds no latency to the reflex.

## Where the learned policy lives

The VLA / learned policy can be the **substrate** URML drives, not a competitor to
it. URML declares and bounds what intent is admissible for that policy via the
`learned_policy` block ([RFC-0383](../../docs/rfcs/0383-learned-policy-training-envelope.md)),
so a command outside what the policy was trained for is refused before dispatch.

## Run it

```bash
python examples/vla/validate_intents.py   # regenerates gate-report.txt
```

Hermetic (the validator only, no model, no robot) and deterministic: the committed
[`gate-report.txt`](gate-report.txt) is byte-asserted in CI
(`reference/validator/tests/test_vla_gate.py`), the same discipline the esmini /
ros2_kortex / crazyswarm2 examples use. The natural language front door itself is
URML's Layer 4 (the [LLM bridge](../../reference/llm-bridge/)); this example starts
from the model's interpreted intent and shows the gate.
