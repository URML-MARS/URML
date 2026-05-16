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

Re-running is safe (the venv is reused). It's fully reversible — `make clean` or `rm -rf .venv` removes every trace; nothing is published or claimed. When PyPI packages land (Phase 1+), this collapses to `pip install urml-validator urml-llm-bridge`.

Activate the venv, then confirm the CLI:

```bash
. .venv/bin/activate           # Windows: .venv\Scripts\activate
urml --version
```

Expected:

```
urml-validator 0.1.0a1
```

> Prefer to do it by hand, or only want a subset? The old path still works:
> `python -m venv .venv && . .venv/bin/activate && pip install -e reference/validator -e reference/llm-bridge`.
> `bootstrap.py` just automates exactly that for all five packages.

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
```

That's it. The program is statically verified — every primitive it uses references capabilities the manifest declares; every safety check the envelope imposes holds. **A runtime will refuse to execute any program that fails this validation.** The validator is URML's safety boundary.

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
