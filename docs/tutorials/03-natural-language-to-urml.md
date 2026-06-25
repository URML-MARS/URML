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

# Tutorial 3 — Natural language to URML

**By the end of this tutorial you will:**

- Have used `urml emit-prompt` to inspect exactly what the LLM bridge sends a language model.
- Have used `urml translate` to convert a natural-language request into a validated URML program — either with a real LLM or with the included offline `EchoProvider`.
- Understand the validator-feedback revision loop and why it exists.

This tutorial assumes you completed [Tutorial 1](01-getting-started.md). [Tutorial 2](02-anatomy-of-a-program.md) is helpful but not required.

## What the bridge does

The LLM bridge is the surface where natural language meets URML. Given a user request, the bridge:

1. Builds a system prompt containing the URML JSON Schema, a summary of the robot's manifest and envelope, and a few-shot example library.
2. Sends the prompt + user request to an LLM (Anthropic, OpenAI, or any provider implementing the `LLMProvider` protocol).
3. Parses the LLM's structured-JSON output.
4. Runs the validator on it.
5. **On rejection**, sends the structured errors *back to the LLM* and asks for a corrected version. Loops up to `max_revisions` times.
6. On acceptance, returns the validated program.

That step 5 — the revision loop — is the load-bearing claim of the bridge. The LLM doesn't have to emit perfect URML; it has to emit URML the validator can give *machine-readable feedback on*. The validator's `capability.*`, `envelope.*`, `binding.*` error codes are designed precisely for an LLM to consume.

## Step 1: See what the bridge would send

You don't need an API key to inspect the bridge's prompt. `urml emit-prompt` writes the exact text the bridge would send to an LLM, given your manifest, envelope, and active profile:

```bash
cd my-first-robot

urml emit-prompt --manifest manifest.yaml \
    --envelope envelope.yaml \
    --profile home
```

The output is long — it includes the full URML JSON Schema. Scroll up to see the structure:

1. **Instruction header**: *"You are a robot-intent translator…"*. Stable text; cache-friendly.
2. **Active profile(s)**: `Active profile(s): home`.
3. **Robot capability manifest**: a compact summary — declared frames, locations, mobility, manipulation, perception, docking stations.
4. **Active safety envelope**: numeric caps + any declared zones/geofences.
5. **Examples**: 1–4 few-shot pairs (NL request + URML program) selected for the active profile.
6. **URML program JSON Schema**: the structured-output contract.

The instruction header and the profile line are plain text; the other four parts each begin with a `=== ... ===` marker, so a `===` count returns four. (A fifth `=== Revision required ===` marker appears only during the translate-retry loop, never in `emit-prompt` output.)

If you have `jq` installed, you can pipe to a file and grep through it:

```bash
urml emit-prompt --manifest manifest.yaml --envelope envelope.yaml --profile home --out prompt.txt
wc -l prompt.txt
grep -c "===" prompt.txt    # four "===" section headers (manifest, envelope, examples, schema)
```

This is *everything* the LLM sees. If a translation goes wrong later, this is the first thing to inspect.

## Step 2: Translate, offline (no API key)

The bridge ships an `EchoProvider` — a hermetic, deterministic test provider that returns canned responses instead of calling a real LLM. Useful for testing, CI, and tutorials.

To use `urml translate` with `EchoProvider`, you need to give it the response you'd want the LLM to produce. Put this in a file `canned-response.yaml`:

```bash
cat > canned-response.yaml <<'EOF'
profile: home
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - move_to: { location: kitchen }
    - detect:
        object: mug
        attributes: { color: red }
        store_as: target_mug
    - grasp: { target: $target_mug, force: gentle }
    - move_to: { location: user, carrying: $target_mug }
    - release: { mode: hand_to_user }
EOF
```

Now translate:

```bash
urml translate "Bring me the red mug from the kitchen." \
    --manifest manifest.yaml \
    --envelope envelope.yaml \
    --profile home \
    --provider echo \
    --echo-response-file canned-response.yaml
```

Expected output:

```yaml
profile: home
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
  - move_to:
      location: kitchen
  - detect:
      object: mug
      attributes:
        color: red
      store_as: target_mug
  ...
```

…followed on stderr by:

```
Translation accepted after 0 revision(s); profile(s)=home
```

That last line is the important one. `0 revision(s)` means the EchoProvider's response validated on the first try. If you'd given an invalid response, you'd see `1 revision(s)` or `2 revision(s)` — except `EchoProvider` only has one canned response, so a revision would just exhaust and the command would exit 1.

## Step 3: Translate, with a real LLM

If you have an Anthropic API key, install the optional `anthropic` extra and set the env var:

```bash
pip install "urml-llm-bridge[anthropic]"
export ANTHROPIC_API_KEY=sk-ant-...
```

(For OpenAI: `pip install "urml-llm-bridge[openai]"` and `export OPENAI_API_KEY=...`. Replace `--provider anthropic` with `--provider openai` below.)

> Install the package by name (as above) so it works from any directory, including the `my-first-robot/` project you are standing in. The `pip install -e "reference/llm-bridge[...]"` form only resolves from the **repo root** of a source checkout (Tutorial 1's `bootstrap.py` path already installs every extra there).

> **Using a local model (Ollama, LM Studio, ...).** Any OpenAI-compatible server works through the `openai` provider. Point the bridge at it and name the model:
>
> ```bash
> export OPENAI_BASE_URL="http://127.0.0.1:11434"   # your Ollama server
> export OPENAI_API_KEY="ollama"                     # any non-empty string
> urml translate "Bring me the red mug from the kitchen." \
>     --manifest manifest.yaml --envelope envelope.yaml --profile home \
>     --provider openai --model "qwen3.5:9b"
> ```
>
> `--model` matters: the `openai` provider defaults to a hosted model name, so pass the local model you pulled. Translation is the demanding step, and a small model (under roughly 7B) often emits structurally invalid URML that the validator then rejects; a capable local model works offline (a community user reported qwen3.5:9b at a 128k context translating cleanly). The validator gates either way, so a weak model can be wrong but the robot still only runs a validated program. There is a community Ollama HOWTO on [Discussion #497](https://github.com/URML-MARS/URML/discussions/497).
>
> If the first translate times out (`APITimeoutError`) and a retry then succeeds, that is a cold start: the server is loading a multi-GB model into memory on the first call. Give it more headroom with `export URML_OPENAI_TIMEOUT=600` (seconds), keep the model warm (Ollama's `OLLAMA_KEEP_ALIVE`), or simply re-run.

Then:

```bash
urml translate "Bring me the red mug from the kitchen." \
    --manifest manifest.yaml \
    --envelope envelope.yaml \
    --profile home \
    --provider anthropic
```

The LLM sees the manifest, the envelope, the schema, and the few-shot examples (including the red-mug example, since it's the canonical home-profile fixture). It emits a JSON URML program. The bridge validates it. If accepted, the program is printed to stdout; if rejected, the bridge feeds the structured errors back and asks the LLM to revise, up to three times.

For the exact red-mug request, the LLM usually nails it on the first attempt. To see the revision loop work harder, try a request that *almost* fits the manifest but pushes against an edge:

```bash
urml translate "Drive at full speed to the kitchen and grab a blue cup." \
    --manifest manifest.yaml \
    --envelope envelope.yaml \
    --profile home \
    --provider anthropic
```

Possible outcomes:

- The LLM emits `move_to(speed: 0.5)` — exceeds the manifest's `max_velocity: 0.46`. Validator rejects with `envelope.velocity_exceeded`; LLM revises to `speed: 0.4` or omits speed entirely.
- The LLM emits `detect(object: cup, attributes: {color: blue})` — `cup` is in the manifest's vocabulary, so accepted. Or it tries `detect(object: blue_cup)` — `blue_cup` isn't in the vocabulary; validator rejects with `capability.missing_object_class`; LLM revises.

Watch stderr for the revision count: `Translation accepted after N revision(s)`. The non-zero numbers are where the validator-feedback loop earned its keep.

## Step 4: Inspect a translated program (sanity check)

Whatever the LLM produced, you can re-validate it explicitly:

```bash
urml translate "..." [args] > my-program.urml.yaml
urml validate my-program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile home
```

This is a useful defense-in-depth habit: never trust the bridge's `accepted` flag alone — always re-validate before any runtime execution. Per [`CLAUDE.md`](../../CLAUDE.md), bypassing the validator at runtime is in the *Never Do* list. The runtime itself re-validates internally, but a habit of explicit re-validation between pipeline steps catches bugs in *any* of those steps.

## The mental model

```
                          urml translate
                                │
                                ▼
            ┌───────────────────┴──────────────────────┐
            │             Bridge.translate             │
            │                                          │
            │   build prompt (manifest, envelope,      │
            │   schema, few-shots, prior emission?)    │
            │                  │                       │
            │                  ▼                       │
            │           LLM provider                   │  ← Anthropic / OpenAI / Echo
            │                  │                       │
            │            JSON response                 │
            │                  │                       │
            │                  ▼                       │
            │              validator                   │  ← static checks
            │              accepted?                   │
            │           ┌──yes──┐  ┌──no──┐            │
            │           │       │  │      ▼            │
            │           │       │  │  add structured   │
            │           ▼       │  │  errors to prompt │
            │     return result │  │  loop ↑           │
            │                   │  │                   │
            │                   │  └─→ revisions > N?  │
            │                   │      → raise         │
            └───────────────────┴──────────────────────┘
```

The bridge's "intelligence" is small. The LLM does the language work; the validator does the safety work; the bridge orchestrates and surfaces errors so the loop is short and structured.

## What you have now

A working LLM bridge — either real (Anthropic/OpenAI) or offline (Echo). Familiarity with the prompt the bridge builds, the revision loop, and the validator as the safety floor.

## Next

You've now seen URML programs *and* generated them from natural language. The remaining tutorial covers what happens when the scaffolded manifest doesn't match your robot — [Tutorial 4: Writing your own manifest](04-writing-your-own-manifest.md).
