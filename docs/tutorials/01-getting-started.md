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

# Tutorial 1 — Getting started

**By the end of this tutorial you will:**

- Have URML installed in a Python virtual environment.
- Have a starter project on disk (a manifest, a sample program, a safety envelope).
- Have the validator accepting your sample program.

You should be able to work through this tutorial in under five minutes.

## Install

URML is shipped as a set of Python packages under `reference/` in the repository. In Phase 0 they are not on PyPI (a deliberate Phase-1 step); `bootstrap.py` installs all five editable into a project-local venv, in dependency order, in one step on any OS:

```bash
git clone https://github.com/URML-MARS/URML.git
cd URML

python bootstrap.py     # creates .venv, installs everything editable
```

If `python` is not found (many systems, including recent Ubuntu, ship only `python3`), use `python3 bootstrap.py` instead. URML needs Python 3.11 or newer.

Re-running is safe (the venv is reused). It's fully reversible — `make clean` or `rm -rf .venv` removes every trace; nothing is published or claimed. Released packages are also on PyPI: `pip install urml-validator urml-ros2-runtime urml-llm-bridge` (see the README quickstart).

Activate the venv, then confirm the CLI:

```bash
. .venv/bin/activate           # Windows: .venv\Scripts\activate
urml --version
```

Expected (your version may be newer):

```
urml-validator 0.2.0
```

> Want a venv with your own name or location? Activate it first, then run `python bootstrap.py` — when a venv is active (`$VIRTUAL_ENV` is set), bootstrap installs into *that* one instead of creating `.venv`.
>
> Prefer to do the whole thing by hand? `python -m venv .venv && . .venv/bin/activate && pip install -e reference/validator -e reference/ros2-runtime -e reference/llm-bridge -e reference/px4-runtime -e conformance` — the five packages `bootstrap.py` installs, in dependency order.

## Scaffold a starter project

URML ships an `urml init` subcommand that lays down everything a first project needs:

```bash
urml init my-first-robot --profile home
```

Expected output (to stderr):

```
Initialized home project at my-first-robot
  wrote envelope.yaml
  wrote Makefile
  wrote manifest.yaml
  wrote program.urml.yaml
  wrote prompt.en.txt
  wrote README.md

Next steps:
  cd my-first-robot
  urml validate program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile home
```

Have a look at what landed:

```bash
cd my-first-robot
ls
```

You should see six files. The interesting ones for this tutorial:

- **`manifest.yaml`** — what the robot says it can do (its capability declaration).
- **`envelope.yaml`** — the safety limits the deployment imposes on top of the manifest.
- **`program.urml.yaml`** — a sample URML program that fetches a red mug.
- **`prompt.en.txt`** — the natural-language request that program corresponds to.

We'll dissect each of those in [Tutorial 2](02-anatomy-of-a-program.md). For now, you just want to see the validator do its job.

## Run the validator

```bash
urml validate program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile home
```

Expected:

```
Validation passed: program.urml.yaml
  (1 warning(s))

  WARN  [policy.attestation_insufficient] <manifest>/provenance/manifest_attestation
    field: manifest_attestation
    Self-declared provenance accepted in v0.1 but flagged. ...
    offending_value: self_declared
    allowed_values: ['third_party_audited', 'cryptographically_signed']
```

The program **passed** — that's the line that matters. The warning is expected and does not block validation. The scaffolded `manifest.yaml` honestly declares `provenance.manifest_attestation: self_declared` (you have not had the robot's hardware audited by a third party, and saying so is the truthful default). The bundled US-federal compliance policy flags self-declared provenance as a **warning**, not an error, so you can see it without being blocked. Three ways to handle it:

- **Leave it.** It is a warning. Validation passed.
- **Turn the policy off** for a quick local run: add `--no-policy`. The output is then a clean `Validation passed:` with no warnings. This is the right choice while you are learning the language; compliance is one flag away.
- **Satisfy it** once you have a real attestation, by setting `manifest_attestation` to `third_party_audited` or `cryptographically_signed` in `manifest.yaml`.

Compliance (the policy mechanism is specified in [RFC-0004](../rfcs/0004-compliance-policy.md)) is a feature you opt into, not a hoop. For the rest of this tutorial, either leave the warning or add `--no-policy`.

That aside, the program is statically verified — every primitive it uses references capabilities the manifest declares; every safety check the envelope imposes holds. **A runtime will refuse to execute any program that fails this validation.** The validator is URML's safety boundary.

## See validation failures, on purpose

To convince yourself the validator earns its keep, break the program. Open `program.urml.yaml` in your editor and change:

```yaml
- move_to:
    location: kitchen
```

to:

```yaml
- move_to:
    location: the_moon
```

Re-run:

```bash
urml validate program.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile home
```

You'll see something like:

```
Validation failed: program.urml.yaml (1 error(s))

  ERROR [capability.missing_location] behavior/steps/0
    field: location
    move_to references undeclared location 'the_moon'.
    suggestion: Add 'the_moon' to manifest.declared_locations, or use `pose` + `frame` instead of a named location.
```

Three things worth noticing:

1. **Stable error code.** `capability.missing_location` is part of URML's public API — the LLM bridge later matches on this exact string to drive its revision flow.
2. **Path to the problem.** `behavior/steps/0` tells you exactly which step is offending.
3. **A concrete suggestion.** The validator doesn't just complain; it tells you what to do.

Put the file back the way it was (`location: kitchen`) and re-run validation to confirm it passes again.

## What you have now

A working URML installation, a starter project on disk, and a fast feedback loop for editing programs. That's enough surface to be productive.

## Next

If you want to understand what's *in* the program you just validated — the layered architecture, the primitive vocabulary, the variable bindings — read [Tutorial 2: Anatomy of a URML program](02-anatomy-of-a-program.md).

If you want to skip ahead to LLM translation, read [Tutorial 3: Natural language to URML](03-natural-language-to-urml.md).

If you want to see the whole loop now — one English sentence turned into a program, validated, then executed step by step, hermetically and with no API key — run `make demo-run` and read [the sentence-to-motion walkthrough](../demos/sentence-to-motion.md).
