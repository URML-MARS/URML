# LLM-bridge round-trip — natural language to validated URML, no network

A demo that shows what URML's Layer-4 prompt contract actually does: the exact
system prompt an LLM is given, then a full natural-language → validated-URML
round-trip — run **hermetically**, with no API key and no network, using the
built-in `echo` provider. The point is to see Layer 4 work end to end without
trusting (or paying) a model.

Useful for: video demos, slide decks, explaining "URML doesn't parse English —
it gives the model a precise target and checks the answer." Fits on one screen
at presentation zoom.

## Prerequisites

- URML installed (work from a checkout per [Tutorial 1](../tutorials/01-getting-started.md)).
- A terminal, `cd` into the URML repository root.

## Scene 1 — the contract the model is given

```bash
urml emit-prompt -m examples/home/red-mug.manifest.yaml --profile home
```

This prints the full system prompt the bridge would build: the stable
instruction header, a compact summary of the robot's capability manifest, the
few-shot examples, and the URML program JSON Schema. This is the entire
Layer-4 contract — there is no hidden prompt. Nothing here names a vendor; any
provider gets the same contract.

## Scene 2 — a hermetic round-trip

The `echo` provider returns a canned completion instead of calling a model, so
the round-trip is deterministic and offline. Write the canned emission:

```bash
cat > /tmp/echo_redmug.json <<'EOF'
{"profile":"home","behavior":{"type":"sequence","on_error":"abort_and_report",
 "steps":[{"move_to":{"location":"kitchen"}},
 {"detect":{"object":"mug","attributes":{"color":"red"},"store_as":"target_mug"}},
 {"grasp":{"target":"$target_mug","force":"gentle"}},
 {"move_to":{"location":"user","carrying":"$target_mug"}},
 {"release":{"mode":"hand_to_user"}}]}}
EOF
```

Run the bridge:

```bash
urml translate "Bring me the red mug from the kitchen." \
    -m examples/home/red-mug.manifest.yaml --profile home \
    --provider echo --echo-response-file /tmp/echo_redmug.json
```

Expected (first line, then the program):

```
Translation accepted after 0 revision(s); profile(s)=home
profile: home
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
  - move_to:
      location: kitchen
  ...
```

The emission was JSON-parsed and run through the **full five-pass validator**
(including the bundled US-federal compliance policy) before being accepted.
Swap `--provider echo --echo-response-file ...` for `--provider anthropic`
(or `openai`) and a real key, and nothing else changes — that is the
provider-neutrality guarantee.

## Scene 3 — the validator-feedback loop

The bridge does not trust the model: a rejected emission is returned to the
model with the validator's *structured* errors
(`{code, primitive, path, field, message, suggestion}`), bounded by
`--max-revisions` (default 3). A rejection that is **only** a compliance-policy
failure short-circuits immediately — a program cannot revise its way out of a
hardware-provenance problem (RFC-0004).

The multi-attempt loop is exercised end to end in
`reference/llm-bridge/tests/test_bridge.py` (a scripted `EchoProvider` whose
first response is deliberately invalid and whose second is correct), and the
loop is specified normatively in
[`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md)
§3.

## What this shows

URML's Layer-4 answer is not "trust the model." It is: give every model the
same precise, published contract; validate what comes back against the robot's
real capabilities and safety envelope; and feed structured errors back until
the program is provably valid or the budget runs out. The model does the
language work; URML guarantees the result is checkable before any actuator
moves.
