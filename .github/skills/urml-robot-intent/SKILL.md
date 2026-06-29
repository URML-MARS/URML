---
name: urml-robot-intent
description: Turn a natural-language goal for a physical robot into a URML program that is statically validated against the robot's declared capabilities and active safety envelope before any actuator moves. Use this when an agent needs to command a robot, drone, arm, humanoid, or mobile base from a plain-language instruction, or needs to check whether a requested physical action is admissible (within declared capabilities and safety limits) before executing it. Covers the translate then validate then execute loop. Provider-agnostic (any LLM), runs fully offline once a program is validated, and never lets an action reach an actuator until it passes verification.
license: Apache-2.0
---

# URML: validated robot intent for agents

URML is an open language for describing robot intent. This skill gives you one capability: turn a plain-language goal into a robot program that has been checked against a specific robot's real capabilities and safety limits before anything moves.

The core idea: URML does not parse your English. It hands your model a precise target and checks the answer. Verification is a precondition for action, not a test you run afterward.

## When to use this

Use this skill when you need to:
- Command a physical robot (arm, drone, humanoid, mobile base, cobot) from a natural-language instruction.
- Decide whether a requested physical action is admissible before doing it.
- Produce a robot program a human or another system can audit before execution.

Do not use it for pure software tasks. It is about physical actuation.

## The loop

1. **Take** a natural-language goal, for example "bring me the red mug from the kitchen".
2. **Emit** a URML program following URML's published Layer-4 prompt contract.
3. **Validate** the program against the target robot's capability manifest and active safety envelope.
4. **Execute** the accepted program through a substrate adapter (`mock` for a dry run, `ros2` or `px4` for a real runtime).

The safety boundary is step 3. A program that asks for a capability the robot never declared, or that violates the safety envelope, is rejected. It cannot revise its way out of a hardware-provenance failure. Nothing reaches an actuator until the validator accepts it.

## Prove the loop offline first (no API key, no robot)

URML ships a hermetic path: a built-in `echo` provider and a `mock` adapter, runnable against files in the URML repository, with no network.

```bash
pip install -e reference/validator
pip install -e reference/llm-bridge
pip install -e reference/ros2-runtime   # provides the hermetic `mock` adapter (no ROS needed)

# See the exact contract the model is given (no hidden prompt):
urml emit-prompt -m examples/home/red-mug.manifest.yaml --profile home

# Hermetic natural-language to validated program:
urml translate "Bring me the red mug from the kitchen." \
    -m examples/home/red-mug.manifest.yaml --profile home \
    --provider echo --echo-response-file examples/home/red-mug.echo-response.json

# Validate a program on its own:
urml validate examples/home/red-mug.urml.yaml \
    -m examples/home/red-mug.manifest.yaml --profile home

# Execute against the recording mock substrate:
urml execute examples/home/red-mug.urml.yaml \
    -m examples/home/red-mug.manifest.yaml --adapter mock
```

## Use your own model

URML is provider-agnostic. The integration surface is the `LLMProvider` protocol: any object with a `complete(system, user, schema) -> str` method. The bridge orchestrates, your model does the language work, the validator is the safety boundary.

```python
from urml_llm_bridge import Bridge, BridgeRevisionExhausted, BridgePolicyViolation
from urml_llm_bridge.providers.anthropic import AnthropicProvider  # or openai, ollama, local

bridge = Bridge(
    provider=AnthropicProvider(model="claude-sonnet-4-6"),
    manifest=manifest,       # the robot's Layer-1 capability manifest
    envelope=envelope,       # the active safety envelope
    profiles=("home",),
    max_revisions=3,         # bounded validator-feedback loop
)

try:
    result = bridge.translate("Bring me the red mug from the kitchen.")
    runtime.execute(result.program)   # only validated programs reach a runtime
except BridgeRevisionExhausted as exc:
    handle(exc.last_result)           # structured errors after the bounded retries
except BridgePolicyViolation as exc:
    handle(exc.last_result)           # hardware-provenance failure; no retry can fix it
```

`translate()` returns only when the program is accepted, otherwise it raises. The revision loop is automatic: a rejected emission goes back to the model with structured validator errors, up to `max_revisions`. A pure compliance-policy rejection short-circuits, because a program cannot edit its way out of a hardware-provenance problem.

## Rules to follow

- Never skip validation. There is no path that reaches an actuator without the validator. That is a safety and liability boundary.
- Never fabricate capability. If the goal needs something the manifest does not declare, the correct output is a `report(status: failure)` naming what is missing, not an invented action.
- It does not require the cloud. Once a program is validated it runs fully offline.
- It does not persist inputs or outputs. No telemetry.

## References

- Full agent integration guide: `references/urml-for-ai-agents.md` (in this skill) or `docs/integrations/urml-for-ai-agents.md` in the URML repository.
- Normative Layer-4 prompt contract: `spec/layer-4-nl-grammar/v0.1.0.md`.
- Project home: https://urml.dev
- Source and issues: https://github.com/URML-MARS/URML
