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

# LLM Bridge

**Status:** `0.3.0`. Shipped: the provider-agnostic `Bridge` + bounded validator-feedback revision loop, five providers (Anthropic, OpenAI, Ollama, llama.cpp, all lazy-imported, plus the hermetic `EchoProvider`), schema-derived GBNF grammar for llama.cpp (RFC-0021), the `urml translate` / `urml emit-prompt` CLI, and profile-scoped few-shot libraries (home / industrial / drone / educational / fleet). The normative contract is [`spec/layer-4-nl-grammar/`](../../spec/layer-4-nl-grammar/); a hermetic end-to-end walkthrough is [`docs/demos/bridge-roundtrip.md`](../../docs/demos/bridge-roundtrip.md).

## What this is

The **provider-agnostic glue** between natural-language input and a validated URML program. The LLM bridge:

1. Takes a natural-language request from a user (or another system).
2. Prompts a configured LLM with the [Layer-4 prompt contract](../../spec/layer-4-nl-grammar/), the connected robot's [Layer-1 capability manifest](../../spec/layer-1-hal/), and the active safety envelope.
3. Receives the LLM's emission (a URML program).
4. Calls the [validator](../validator/) to statically verify the emission.
5. On rejection, surfaces the structured error back to the LLM and requests a revision. Repeats up to a configured bound.
6. On acceptance, hands the validated program to the runtime for execution.
7. When the request needs a capability the manifest does not declare, the model emits a `report(status: failure)` naming what is missing rather than fabricating capability. (An *interactive* clarifying-question protocol is **not** in v0.1 — see [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/) §5.)

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

## Architecture

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
               ollama.py,
               llama_cpp.py,
               echo.py)
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

## Quickstart (current pre-alpha — hermetic, no provider needed)

```bash
cd reference/llm-bridge
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ../validator           # bridge depends on validator
pip install -e ".[dev]"
pytest
```

Use it in code with the bundled `EchoProvider` (for tests / hermetic CI):

```python
import json
from urml_llm_bridge import Bridge, EchoProvider

red_mug_program = {  # the URML the LLM is expected to emit
    "profile": "home",
    "behavior": {"type": "sequence", "steps": [...]},
}

provider = EchoProvider(scripted=[json.dumps(red_mug_program)])
bridge = Bridge(provider=provider, manifest=manifest, envelope=envelope, profiles=("home",))
result = bridge.translate("Bring me the red mug from the kitchen.")

if result.accepted:
    runtime.execute(result.program)
```

The revision loop runs automatically when the validator rejects the LLM's emission: the bridge feeds the structured errors back to the LLM and asks for a corrected version, up to `max_revisions` times (default 3).

### Using a real provider

Install the extra for the provider you want — the bridge package itself has no SDK dependencies:

```bash
pip install urml-llm-bridge[anthropic]    # adds the `anthropic` SDK
pip install urml-llm-bridge[openai]       # adds the `openai` SDK
pip install urml-llm-bridge[ollama]       # adds httpx; talks to a local `ollama serve`
pip install urml-llm-bridge[llama_cpp]    # adds httpx; talks to a local `llama-server`
```

Then:

```python
from urml_llm_bridge import Bridge
from urml_llm_bridge.providers.anthropic import AnthropicProvider

provider = AnthropicProvider(model="claude-sonnet-4-6")  # reads ANTHROPIC_API_KEY env var
bridge = Bridge(provider=provider, manifest=manifest, envelope=envelope, profiles=("home",))
result = bridge.translate("Bring me the red mug from the kitchen.")
```

Or OpenAI:

```python
from urml_llm_bridge.providers.openai import OpenAIProvider

provider = OpenAIProvider(model="gpt-4o")  # reads OPENAI_API_KEY env var
```

Or a local model, fully offline (RFC-0021):

```python
from urml_llm_bridge.providers.ollama import OllamaProvider
from urml_llm_bridge.providers.llama_cpp import LlamaCppProvider

provider = OllamaProvider(model="llama3.2:1b")   # talks to ollama serve at 127.0.0.1:11434
provider = LlamaCppProvider()                    # talks to llama-server at 127.0.0.1:8080
```

Every adapter surfaces its native structured-output mechanism: Anthropic via tool use (with the URML schema as the `emit_urml` tool's `input_schema`), OpenAI via `response_format={"type": "json_object"}` with the schema conveyed in the system prompt, Ollama via the schema as the `format` constraint, and llama.cpp via a GBNF grammar derived from the schema (structurally invalid output is unrepresentable at the decoder). In all cases, conformance to the schema is validated downstream by `urml_validator.validate()` as part of the bridge's revision loop.

From the CLI, the same providers are one flag away: `urml translate ... --provider ollama --model llama3.2:1b`, `--provider llama_cpp`, or `--provider openai --base-url http://host:port/v1` for any OpenAI-compatible server (LM Studio, vLLM).

## What's not here yet (lands next)

- **Multilingual few-shot variants** (Hebrew, Spanish, Japanese, Mandarin).
- **Conversation memory** for follow-up requests within a session.
- **OpenAI strict JSON-schema mode** — needs schema preprocessing to satisfy the strict-mode constraints (every property required, no `oneOf`, etc.). The current adapter uses `json_object` mode plus the schema in the system prompt for portability.

## Related documents

- [`/spec/layer-4-nl-grammar/`](../../spec/layer-4-nl-grammar/) — the prompt contract this bridge implements.
- [`/reference/validator/`](../validator/) — the safety boundary this bridge feeds.
- [`/examples/`](../../examples/) — the paired natural-language / URML scenarios used as fixtures.
- [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do — the provider-neutrality requirement, in writing.
