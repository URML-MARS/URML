# LLM Bridge

**Status:** Pre-implementation. Phase 1 target.

## What this is

The **provider-agnostic glue** between natural-language input and a validated URML program. The LLM bridge:

1. Takes a natural-language request from a user (or another system).
2. Prompts a configured LLM with the [Layer-4 prompt contract](../../spec/layer-4-nl-grammar/), the connected robot's [Layer-1 capability manifest](../../spec/layer-1-hal/), and the active safety envelope.
3. Receives the LLM's emission (a URML program).
4. Calls the [validator](../validator/) to statically verify the emission.
5. On rejection, surfaces the structured error back to the LLM and requests a revision. Repeats up to a configured bound.
6. On acceptance, hands the validated program to the runtime for execution.
7. When the natural-language request is ambiguous, the LLM is expected to ask the user a small number of structured questions before emitting URML.

## Provider neutrality is non-negotiable

URML's value as a standard depends on Layer 4 being **provider-neutral**. The LLM bridge must support, as first-class citizens:

- **Anthropic** (Claude family).
- **OpenAI** (GPT family).
- **Open-weights models** (Llama, Mistral, Qwen, and their successors), via local serving (vLLM, llama.cpp, Ollama) or hosted inference providers.
- **On-device models** for offline-capable deployments.

Adding a new provider must be a small adapter in `providers/`, not a structural change to the bridge. If a provider's particular feature would let URML produce better URML, the bridge surfaces the feature behind a profile-neutral abstraction — never by privileging that provider.

Vendor lock-in here is explicitly prohibited by [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do.

## What the bridge does NOT do

- It does **not** include or embed any specific LLM provider's API client as a hard dependency. Provider clients are optional and pluggable.
- It does **not** require cloud connectivity. A deployment using a local open-weights model runs offline end to end.
- It does **not** persist user inputs, model outputs, or any other data without explicit, opt-in, documented purpose. Trust is the most valuable asset of this project; the bridge will not be the place it leaks.
- It does **not** execute URML. That is the runtime's job.
- It does **not** make safety decisions. The validator is the safety boundary; the bridge only relays.

## Architecture (planned)

```
                ┌────────────────────────┐
   user / NL    │   LLM Bridge           │   validated URML
   ─────────────▶  • build prompt        ├──────────────────▶  runtime
                │  • call provider       │
                │  • validate emission   │
                │  • revise loop         │
                └──┬──────────────────▲──┘
                   │                  │
                   ▼                  │
              providers/           validator
              (anthropic.py,       (separate
               openai.py,           process)
               local_vllm.py,
               on_device.py)
```

The bridge is small. The intelligence lives in the LLM (which is configured, not built here) and in the validator (which is a separate process). The bridge orchestrates.

## Language

- **Python**. `mypy --strict`. Public API fully type-annotated.

## API (sketch)

```python
from urml.llm_bridge import Bridge

bridge = Bridge(
    provider="anthropic",          # or "openai", "vllm", "ollama", ...
    spec_versions={...},
    manifest=manifest,
    envelope=envelope,
    profiles=("home",),
    max_revisions=3,
)

result = bridge.translate("Bring me the red mug from the kitchen.")

if result.accepted:
    runtime.execute(result.program)
else:
    # After max_revisions, structured errors surface to the caller.
    show_user(result.user_message, result.errors)
```

## Conformance contract

The bridge has its own conformance bar: for the published few-shot example library, the bridge produces accepted URML at or above a stated success rate (per-provider, declared in the bridge's release notes). The conformance suite includes these end-to-end fixtures.

## Core Commitment

The LLM bridge — the *bridge logic and the prompt contract*, not any specific provider's API — is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0 and provider-agnostic.

## Related documents

- [`/spec/layer-4-nl-grammar/`](../../spec/layer-4-nl-grammar/) — the prompt contract this bridge implements.
- [`/reference/validator/`](../validator/) — the safety boundary this bridge feeds.
- [`/examples/`](../../examples/) — the paired natural-language / URML scenarios used as fixtures.
- [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do — the provider-neutrality requirement, in writing.
