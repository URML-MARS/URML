# URML Tutorials

A hands-on path from *"I've never heard of URML"* to *"I can validate my own URML programs and translate natural language to robot intent."* You should be able to work through all four tutorials in about an hour.

If you only have five minutes, read [Tutorial 1](01-getting-started.md) — it's the elevator pitch with commands you can copy-paste.

## The sequence

| # | Tutorial | What you'll have when you're done |
|---|---|---|
| 1 | [Getting started](01-getting-started.md) | URML installed, a starter project on disk, a program that validates. |
| 2 | [Anatomy of a URML program](02-anatomy-of-a-program.md) | A working mental model of Layer 1 (manifest), Layer 2 (primitives), Layer 3 (composition). |
| 3 | [Natural language to URML](03-natural-language-to-urml.md) | An LLM translating English requests into validated URML programs, with the revision loop in action. |
| 4 | [Writing your own manifest](04-writing-your-own-manifest.md) | A manifest tailored to *your* robot, not a copied template. |

## What URML is, in one paragraph

URML — Universal Robot Language — is a small, opinionated, human-readable language for describing robot **intent**. It sits *above* existing robot operating systems (ROS 2, PX4, OPC UA Robotics, vendor SDKs) and lets humans, language models, and robots share one vocabulary for *what should happen* — independent of which motors, joints, or frames carry it out. Every URML program is statically verified against a robot's declared capabilities and active safety envelope before a single actuator moves.

If that sounds like it solves a problem you have, keep reading. If it sounds like more abstraction than you need, that's a fair read — URML is a bet that natural-language robot control is the obvious next interface, and that someone needs to write down a shared vocabulary before each vendor invents their own. The bet may be wrong; the tutorials at least let you try it for yourself in an hour.

The full vision lives in [`MANIFESTO.md`](../../MANIFESTO.md). The architectural details live in [`docs/architecture.md`](../architecture.md). The normative specification (in progress) lives in [`spec/`](../../spec/). This document is the on-ramp.

## Prerequisites

- **Python 3.11+** on your machine.
- A terminal. Tutorials use bash; Windows users can run them in PowerShell or WSL with minor adaptations.
- **No ROS 2 installation needed** for any of these tutorials. URML's reference runtime ships a hermetic mock substrate so you can exercise the full pipeline — bridge → validator → runtime — without a robot.
- For Tutorial 3, an **Anthropic or OpenAI API key** if you want to see a real LLM translation. (Optional — Tutorial 3 also shows how to use the included offline `EchoProvider`.)

## How tutorials are structured

Each tutorial:

- Opens with **"By the end of this tutorial you will…"** so you know whether to invest the time.
- Lists copy-pasteable shell commands.
- Shows expected output for key steps so you can spot when something diverges.
- Closes with **"Next"** pointing at what comes after.

If you want to skip ahead, follow your nose. The tutorials reference each other but each is reasonably self-contained.

## A note on the project's state

URML is in **Phase 0**: pre-public draft, solo author working in public. The tutorials describe what works today (the v0.1 surface — validator, LLM bridge, hermetic runtime, conformance suite, CLI), not what is planned for v1.0. When tutorials hand-wave over a future feature (the real ROS 2 adapter, profile-specific primitives, multilingual prompts), they say so explicitly. Nothing is described as if it works when it doesn't.

If you find a step that doesn't work, that's a bug — please open an issue.

## Further reading

- [`MANIFESTO.md`](../../MANIFESTO.md) — why URML, what it is and isn't, who it's for.
- [`docs/architecture.md`](../architecture.md) — the five-layer stack expanded.
- [`docs/glossary.md`](../glossary.md) — every URML term defined.
- [`docs/rfcs/`](../rfcs/) — the design history. Five RFCs are filed: the process (0001), the initial primitive vocabulary (0002), the strategic US-alignment decision (0003), the compliance-policy mechanism (0004), and a forward-looking HBOM-parsing design (0005).
- [`docs/demos/compliance-walkthrough.md`](../demos/compliance-walkthrough.md) — see the compliance pass reject a covered-foreign-country manifest, then watch the `--no-policy` override accept it. Five minutes, three commands.
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — how to engage during Phase 0.

Ready? Start with [Tutorial 1: Getting started](01-getting-started.md).
