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

# Tutorial 5 — Teaching URML in a classroom

**By the end of this tutorial you will:**

- Have a 30-minute lesson plan that runs on a laptop with no robot, no API key, and no internet after install.
- Know the three moments that make URML land for a beginner: a program that runs, a program the validator catches, and a robot that stops safely when it is unsure.
- Know what URML collects from your students (nothing) and what it promises you (nothing it has not measured).

This tutorial is for the teacher, the club mentor, or the workshop leader. It assumes the four earlier tutorials only as background; the lesson below is self-contained. The robot is optional throughout. Everything runs against URML's hermetic mock substrate, so a class with no hardware budget and a class with a shelf of buggies follow the same script.

## Why URML fits a classroom

A beginner who writes `move_to: the_moon` does not get a crashed robot or a stack trace. They get one sentence telling them what is wrong and one telling them how to fix it, before anything moves. That is the whole pedagogical case: failure is visible, safe, and explained. The [educational profile](../../spec/profiles/educational/README.md) (RFC-0011) leans into this with the most conservative defaults of any profile: a gentle grip ceiling, a slow speed cap, and an "abort and report" error policy so a student's program halts loudly instead of improvising.

The starter files for this lesson live in [`examples/educational/`](../../examples/educational/): three programs (`hello-square`, `classroom-patrol`, `fetch-the-block`) and one shared manifest (`classroom.manifest.yaml`) describing a micro:bit-class buggy with a claw.

## Before class: install once

Follow [Tutorial 1](01-getting-started.md) on the teaching machine. The short version:

```bash
git clone https://github.com/URML-MARS/URML.git
cd URML
python bootstrap.py
. .venv/bin/activate           # Windows: .venv\Scripts\activate
urml --version
```

Nothing after this step needs the internet. There is no account, no sign-in, and no telemetry: URML does not phone home, and it records nothing about who runs it. You can run the whole lesson on an air-gapped laptop.

## Moment 1 — a program that runs (10 minutes)

Open `examples/educational/hello-square.urml.yaml` with the class. It is five lines of intent: drive to four named corners and come home. Read it out loud; a beginner can follow it without a key.

Validate it:

```bash
cd examples/educational
urml validate hello-square.urml.yaml -m classroom.manifest.yaml --profile educational --no-policy
```

Expected:

```
Validation passed: hello-square.urml.yaml
```

Now watch it run on the hermetic mock — no robot required:

```bash
urml execute hello-square.urml.yaml -m classroom.manifest.yaml --profile educational --no-policy
```

You will see a five-step trace, one `send_navigation_goal` per corner, ending in `RESULT: SUCCESS`. Tell the students plainly what the mock is: no actuator moved, but the language, the safety check, and the execution pipeline all ran for real. If you do have a buggy, the same program drives it through the educational runtime (see [`reference/edu-runtime/`](../../reference/edu-runtime/), which covers VEX, LEGO SPIKE, Thymio, Marty, Petoi, and CircuitPython).

**Student exercise.** Have them edit the corner order, or send the buggy to `waypoint_a` and back. Re-validate, re-run. The edit-validate-run loop takes seconds.

## Moment 2 — a program the validator catches (10 minutes)

This is the moment that earns trust. In `hello-square.urml.yaml`, change one corner to a place that does not exist:

```yaml
    - move_to:
        location: the_moon
```

Re-validate:

```bash
urml validate hello-square.urml.yaml -m classroom.manifest.yaml --profile educational --no-policy
```

You get a refusal, not a crash:

```
Validation failed: hello-square.urml.yaml (1 error(s))

  ERROR [capability.missing_location] behavior/steps/0
    field: location
    move_to references undeclared location 'the_moon'.
    suggestion: Add 'the_moon' to manifest.declared_locations, or use `pose` + `frame` instead of a named location.
```

Three things to point out to the class: the error names the exact step, it tells them what to change, and **the robot never moved** — a program that fails validation is never executed. Put `the_moon` back to a real corner and watch it pass again.

## Moment 3 — a robot that stops safely when unsure (10 minutes)

Open `fetch-the-block.urml.yaml`. It finds a block, picks it up gently, and places it on the table. Two educational-profile rules are doing quiet work here. The grasp is `force: gentle`, capped by the gripper. And `detect` will only look for object classes the manifest declares.

Ask the class: what happens if we tell the buggy to find something it has never heard of? Change the detect target:

```yaml
    - detect:
        object: dragon
        store_as: target_block
```

Re-validate:

```bash
urml validate fetch-the-block.urml.yaml -m classroom.manifest.yaml --profile educational --no-policy
```

```
Validation failed: fetch-the-block.urml.yaml (1 error(s))

  ERROR [capability.missing_object_class] behavior/steps/1
    field: object
    detect references object class 'dragon' which is not in the manifest's perception.object_vocabulary.
    suggestion: Add 'dragon' to manifest.perception.object_vocabulary, or pick a declared class.
```

The buggy does not wander off hunting for a dragon and grab the nearest thing it sees. It fails closed: it stops and says why. This is the educational profile's core safety idea, and it is the right instinct to teach early. Change `dragon` back to `block` to pass.

## Optional — let an LLM write the program (if you have a key)

The earlier moments need no API key. If you want to show the headline trick, one English sentence becoming a program, and you have an Anthropic or OpenAI key, follow [Tutorial 3](03-natural-language-to-urml.md):

```bash
urml translate "Drive around the four corners of the room and come back home." \
    --manifest classroom.manifest.yaml --profile educational --provider anthropic
```

No key on the classroom machines? You can still show students exactly what URML would send a language model, with no key and no network, using `urml emit-prompt` (also in Tutorial 3). It is a good way to make the "the model only fills in a strict template" point concrete.

## What to tell students about trust

Two honest notes worth saying out loud, because they are part of why URML is safe to put in front of a class:

- **It collects nothing.** No accounts, no analytics, no identifiers. The lesson runs offline.
- **It promises nothing it has not measured.** URML is an early open-source project. There is no support guarantee here, and this tutorial deliberately makes none. If a step does not work, that is a bug worth reporting, not a service you are owed.

## Next

You now have a lesson. If you want to point URML at a robot that is not in the starter set, [Tutorial 4](04-writing-your-own-manifest.md) shows how to write a manifest for your own hardware. If your school runs a robotics program, competition, or curriculum and you would like to talk about URML fitting into it, the project tracks that interest in the open; open an issue on the [repository](https://github.com/URML-MARS/URML).
