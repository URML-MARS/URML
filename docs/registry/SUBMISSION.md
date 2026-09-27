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

# Submitting to the URML registry

This page is for anyone who wants a robot listed in the [URML registry](../../registry/README.md): a robot maker, a runtime author, or a user with a recorded run. URML is in Phase 1 and takes outside contributions ([CONTRIBUTING.md](../../CONTRIBUTING.md)). A submission is one pull request that adds one entry file and one evidence folder.

Read [TRADEMARK.md](../../TRADEMARK.md) first. A listing grants no mark. You may call a runtime "URML-compatible" only if it passes the unmodified, current public conformance suite, and you may never call anything "URML-Certified": that mark is reserved for a future program run outside this repository.

## What an entry needs

A capability manifest for the robot, committed in this repository. If it is not already under `examples/`, put it in the entry's evidence folder.

At least one piece of evidence: a recorded run with public sources (`hardware_run` or `simulation_run`), validation records, or a conformance report produced with your runtime's own adapter. The [registry README](../../registry/README.md) explains each kind and what the checker verifies.

Limits: at least one sentence on what your evidence does not show. Every entry has them. A reader trusts an entry that says where it stops.

## Step by step

### 1. Fork and branch

Fork `URML-MARS/URML` and create a branch. Pick an id: lowercase words joined by hyphens, naming the robot and the runtime (`acme-rover-ros2`). The id is the entry's file name.

### 2. Add the evidence folder

Create `registry/evidence/<id>/` with what your entry points at: the manifest (unless it is already in the repository), any envelope, policy or rulebook your validation records use, `validation-records.jsonl`, and `conformance-report.json` if you claim the self-reported tier.

### 3. Run the conformance suite against your own adapter (optional)

Skip this step unless you claim the self-reported URML-compatible tier. The report must come from your runtime's own adapter; a report from the built-in mock describes the mock, and the checker refuses it.

```bash
pip install -e reference/validator -e reference/ros2-runtime -e conformance
urml conformance run --adapter your_pkg.substrate:YourAdapter --profile <profile> \
    --output registry/evidence/<id>/conformance-report.json
```

`python -m urml_conformance --adapter your_pkg.substrate:YourAdapter --profile <profile> --report <path>` writes the same report. A claim covers a whole profile: `--profile` (repeatable) runs every fixture that lists that profile, wherever it lives in the suite, and the checker refuses a claim whose report skips any of them. A runtime that serves only part of a profile (a flight controller with no camera, for example) does not claim that profile; it lists recorded runs as field evidence instead, as the PX4 entry does. The report records the profiles, the number of fixtures, and a sha256 over the fixture files. Do not edit the report or the fixtures. The checker requires `all_passed: true`, your `runtime.adapter` as the report's adapter, and the urml-conformance version of this repository.

### 4. Produce validation records (optional)

Validate the programs you ran on the robot, plus a few refusal cases a reader grasps at once (an altitude above the manifest ceiling, a speed above the declared maximum, a primitive the robot does not declare), against the listed manifest:

```bash
urml validate program.urml.yaml -m registry/evidence/<id>/robot.manifest.yaml \
    --profile <profile> --no-policy --evidence-log registry/evidence/<id>/validation-records.jsonl
```

Use the same manifest, envelope, policy and rulebooks the entry's `validation_records.inputs` declare; the [registry README](../../registry/README.md#validation-records) shows the Python calls as well. The checker replays every record, so a record is evidence only while it still reproduces.

### 5. Write the entry

Create `registry/entries/<id>.yaml`. Quote every date, or YAML reads it as a date object and the checker refuses it.

```yaml
registry_version: "1"
id: acme-rover-ros2
title: Acme Rover through the Acme URML runtime
status: listed
listed: "2026-10-01"
last_verified: "2026-10-01"
submitted_by: Acme Robotics
robot:
  name: Acme Rover
  class: four-wheel ground robot
  maker: Acme Robotics
  manifest: registry/evidence/acme-rover-ros2/acme-rover.manifest.yaml
runtime:
  package: acme-urml-runtime
  version: "1.2.0"
  adapter: acme_urml.substrate:AcmeAdapter
  substrate: ROS 2 Jazzy with Nav2
profiles: [home]
compatibility:
  tier: self_reported
  profiles: [home]
  report:
    path: registry/evidence/acme-rover-ros2/conformance-report.json
    sha256: <sha256 of the report file>
field_evidence:
  - kind: hardware_run
    date: "2026-09-30"
    by: Acme Robotics
    summary: What ran, on which robot, and what happened, in the words of the sources.
    sources:
      - https://github.com/acme/rover/blob/v1.2.0/docs/urml-run.md
validation_records:
  path: registry/evidence/acme-rover-ros2/validation-records.jsonl
  sha256: <sha256 of the records file>
  summary: How and when the records were produced, and what they show.
  inputs:
    manifest: registry/evidence/acme-rover-ros2/acme-rover.manifest.yaml
    policy: none
limits:
  - What the evidence does not show.
```

`sha256` is the hex digest of the file's bytes: `sha256sum <file>` on Linux, `shasum -a 256 <file>` on macOS, `Get-FileHash <file>` in PowerShell (lowercase the result). Write names, never email addresses. Sources are repository paths or `https://` links a reader can open without an account; link a commit or a tagged release rather than a moving branch where you can. The schema is [`registry/entry.schema.json`](../../registry/entry.schema.json).

### 6. Check and export

```bash
python -m urml_conformance.registry check
python -m urml_conformance.registry export
```

`check` must print no problems. `export` rewrites `registry/registry.json`; commit it with your entry, because CI compares it with fresh output.

### 7. Open the pull request

Sign off every commit (`git commit -s`, the DCO), push, and open a pull request with the registry template: add `?template=registry-submission.md` to the new pull request URL. The template's acknowledgements are part of the review.

## What happens next

The `registry-check` workflow runs the checker and the registry tests on the pull request. The maintainer then reviews for completeness only: the check passes, the sources open and say what the summary says, the limits are stated, and the acknowledgements are ticked. The maintainer does not re-run your hardware, run your runtime, or judge your robot.

## Keeping an entry current

Re-verify when URML releases a new version. A release can change a validator verdict, which makes a record stop reproducing, and it moves the urml-conformance version, which a compatibility report must match. Either one fails the check. Produce the records or the report again, update the pinned sha256 values and `last_verified`, run `export`, and open a pull request. If you cannot, withdraw the entry.

## Withdrawing an entry

Open a pull request that sets `status: withdrawn` and says why. No questions asked. A withdrawn entry stays in `registry.json` with that status, so links to it keep resolving and git keeps the history.

## If something goes wrong

Open an issue or start a thread in [GitHub Discussions](https://github.com/URML-MARS/URML/discussions). The conformance suite and the checker are Apache 2.0, so anyone can re-run them and settle a disagreement about what passes.
