# Sentence to motion: one English sentence, executed step by step

This is the demo the whole project exists for. You type one English sentence.
URML turns it into a validated program and then runs that program, printing
the exact sequence of robot actions it executed. Three commands, about two
minutes, no API key, no robot, no cloud. It reproduces identically on Linux,
macOS, and Windows.

Useful for: the first thing to show someone who asks "what is URML." It is the
language doing something, reproducibly, by anyone, not a description of what it
would do.

## Prerequisites

- URML installed from a checkout per [Tutorial 1](../tutorials/01-getting-started.md),
  which gives you a bootstrap virtual environment with every reference package.
- A terminal, `cd` into the URML repository root.
- No `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`. This demo is hermetic on purpose.

## The sentence

```
Bring me the red mug from the kitchen.
```

That is the entire input. It lives in
[`examples/home/red-mug.en.txt`](../../examples/home/red-mug.en.txt). The rest
of this walkthrough is URML acting on it.

## Scene 1: the sentence becomes a URML program

The bridge sends every model the same published Layer-4 contract and validates
whatever comes back. To keep this demo offline and deterministic, the `echo`
provider returns a committed canned completion instead of calling a model. The
canned response is the raw string a real LLM would emit, checked into the repo
at [`examples/home/red-mug.echo-response.json`](../../examples/home/red-mug.echo-response.json).

```bash
urml translate "Bring me the red mug from the kitchen." \
    -m examples/home/red-mug.manifest.yaml --profile home \
    --provider echo --echo-response-file examples/home/red-mug.echo-response.json \
    --out /tmp/redmug.generated.yaml
```

Expected (on stderr):

```
Translation accepted after 0 revision(s); profile(s)=home
wrote /tmp/redmug.generated.yaml
```

The generated `/tmp/redmug.generated.yaml`:

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
  - grasp:
      target: $target_mug
      force: gentle
  - move_to:
      location: user
      carrying: $target_mug
  - release:
      mode: hand_to_user
```

The English became a structured five-step program. Swap
`--provider echo --echo-response-file ...` for `--provider anthropic` (or
`openai`) and a real key, and nothing else changes. That is the
provider-neutrality guarantee. The full system prompt the model is given is
visible with `urml emit-prompt`;
[Tutorial 3](../tutorials/03-natural-language-to-urml.md) walks through that
contract and the validator-feedback revision loop in detail.

## Scene 2: the validator clears it for execution

```bash
urml validate /tmp/redmug.generated.yaml \
    -m examples/home/red-mug.manifest.yaml \
    --profile home \
    --no-policy
```

Expected:

```
Validation passed: /tmp/redmug.generated.yaml
```

Four passes ran: argument typing, capability checks against the robot's
manifest, safety envelope, and variable bindings. The program asks for `grasp`
and `detect`; the validator confirmed this robot declares those capabilities
before letting the program proceed.

`--no-policy` skips the fifth pass, compliance. That pass is on by default and
enforces US federal procurement rules; it is one flag away, not the story
here. The story is the language. The compliance pass has its own walkthrough:
[compliance-walkthrough.md](compliance-walkthrough.md).

## Scene 3: the program executes

```bash
urml execute /tmp/redmug.generated.yaml \
    -m examples/home/red-mug.manifest.yaml \
    --profile home \
    --no-policy
```

Expected:

```
URML execute: /tmp/redmug.generated.yaml
  adapter:   mock
  substrate: HERMETIC MOCK. No physical or simulated robot, no actuator moved. This proves the URML language, validation, and execution pipeline end to end. For a real simulated autopilot, run --adapter px4 against PX4 SITL (see docs/demos/sentence-to-flight.md).
  re-validation: passed (executed only after the validator accepted it)

  trace (5 step(s) executed, 5 adapter call(s)):
   1. send_navigation_goal  location=kitchen
   2. query_detection  object_class=mug attributes={'color': 'red'}
   3. send_manipulation_goal  action=grasp target={'class': 'mug', ...} force_n=1.5 approach=auto
   4. send_navigation_goal  location=user carrying={'class': 'mug', ...}
   5. send_manipulation_goal  action=release approach=auto release_mode=hand_to_user

  bindings:
    target_mug = {'class': 'mug', 'pose': {'x': 1.0, 'y': 1.0, 'z': 0.0}, ...}

  RESULT: SUCCESS (5 step(s) executed)
```

This is the part the rest of the repository was building toward. The five-step
program ran. Each line of the trace is one primitive dispatched to a substrate
adapter: navigate, detect, grasp, navigate while carrying, release. The
`$target_mug` reference set by `detect` flowed into `grasp` and the second
`move_to`; you can see the resolved binding at the bottom. `urml execute`
re-validated the program before running it, because URML executes only
validated programs (this is a safety boundary, stated in `CLAUDE.md`).

One sentence in. A robot's worth of coordinated actions out, each one checked
against the robot's real capabilities first.

## The whole loop in one command

```bash
make demo-run
```

This runs Scene 1 through Scene 3 as a single hermetic chain. `make demo`
(validate only) still exists and is unchanged.

## What this is NOT

The `mock` adapter is a mock. It is labeled `HERMETIC MOCK` in its own output
for exactly this reason: calling this "a robot moved" would be a lie. Nothing
physical or simulated moved. What this demo proves is the full language
pipeline, English to validated program to executed step sequence, reproducible
by anyone with a checkout and no credentials.

The next milestone is a simulated autopilot actually flying from the same kind
of sentence: [sentence-to-flight.md](sentence-to-flight.md), which ends in
`urml execute --adapter px4` against PX4 SITL. A physical robot needs hardware
and an operator and is out of Phase-0 scope. No claim of physical-hardware
verification is made anywhere in this repository.

This walkthrough is illustrative. A real deployment uses a real robot's
manifest, a real safety envelope, and (unless explicitly exempt) the
compliance pass left on.

## Files used in this walkthrough

- [`examples/home/red-mug.en.txt`](../../examples/home/red-mug.en.txt): the
  one-sentence input.
- [`examples/home/red-mug.echo-response.json`](../../examples/home/red-mug.echo-response.json):
  the committed canned LLM completion that makes Scene 1 hermetic. A real
  provider replaces this; the rest of the pipeline does not change.
- [`examples/home/red-mug.manifest.yaml`](../../examples/home/red-mug.manifest.yaml):
  the target robot's capability manifest.
- `/tmp/redmug.generated.yaml`: the program URML generates from the sentence
  in Scene 1, validated in Scene 2, executed in Scene 3.

## Related reading

- [Tutorial 3: Natural language to URML](../tutorials/03-natural-language-to-urml.md):
  the Layer-4 prompt contract the model is given, and the validator-feedback
  revision loop, in detail.
- [compliance-walkthrough.md](compliance-walkthrough.md): the fifth validator
  pass this demo skips with `--no-policy`, shown on its own.
- [Tutorial 1: Getting started](../tutorials/01-getting-started.md): install
  and first run.
- [`MANIFESTO.md`](../../MANIFESTO.md) §A Concrete Example: the red-mug program
  as the canonical illustration of what URML is for.
