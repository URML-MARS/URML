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

# URML registry

The public lookup for robots that run URML programs. Each entry names a robot, its capability manifest, the runtime that drives it, and the evidence behind the listing: recorded runs on hardware or in simulation, validation records that CI replays, and, when the runtime's authors have one, a self-reported conformance result. Each entry also states what that evidence does not show.

The entries are YAML files in [`entries/`](entries/). [`registry.json`](registry.json) is generated from them for the website, and [`entry.schema.json`](entry.schema.json) describes the entry format. Both generated files are checked in CI against fresh output, so they cannot drift from the entries.

## What a listing means

A listing records facts a reader can check: which manifest the robot declares, which runtime drives it, what was run, when, by whom, and where the record of it lives. The checker verifies what a machine can verify: the files exist, their digests match, the validation records still reproduce, and any conformance report says what the entry claims.

A listing is not an endorsement. URML has not tested the robot beyond what the entry's evidence shows, the listing grants no mark, and it says nothing about fitness for production, safety-critical, or regulated use ([TRADEMARK.md](../TRADEMARK.md)). The maintainer reviews a submission for completeness only ([GOVERNANCE.md](../GOVERNANCE.md)) and does not re-run a third party's hardware.

Nothing here is URML-Certified. [TRADEMARK.md](../TRADEMARK.md) reserves that mark for a program that does not exist yet and, if it is created, runs outside this repository ([spec/conformance/v0.1.0.md](../spec/conformance/v0.1.0.md), section 3). The one compatibility tier an entry can carry is the self-reported URML-compatible tier: the runtime's authors ran every fixture of each claimed profile, from the unmodified, current public suite, against the runtime's own adapter, and every one passed. A claim covers a whole profile or nothing. There are no levels, scores, or star ratings.

Entries hold names, never email addresses. The registry collects no contact details and keeps no analytics.

## Entries today

- [`ardupilot-arducopter-pixhawk`](entries/ardupilot-arducopter-pixhawk.yaml): a Pixhawk-class flight controller running ArduCopter, through `urml-ardupilot-runtime`. A bench run on the board (propellers off) and an ArduCopter SITL run, both on 2026-08-29.
- [`gopigo3-example-adapter`](entries/gopigo3-example-adapter.yaml): a GoPiGo3 educational robot, through the example adapter in [`examples/gopigo3/`](../examples/gopigo3/). Hardware runs by an independent user, @slowrunner, in June and July 2026.
- [`px4-sitl-sih-quadrotor`](entries/px4-sitl-sih-quadrotor.yaml): PX4 v1.17.0 in software-in-the-loop simulation (the SIH quadrotor), through `urml-px4-runtime`. A simulated flight on 2026-09-27: armed, took off to 30 m, flew a waypoint, returned and landed.

Neither entry carries a compatibility claim. Each one says why in its limits.

## How PX4 was listed

A listing follows recorded evidence, so PX4 was not in the first cut. The first PX4 SITL run on 2026-09-27 showed why: the gate test passed in seconds because the adapter reported success on command acknowledgements, and PX4's log showed the vehicle never armed. The adapter was changed to confirm each step from telemetry (commit 9ff518c), the test gained a listen-only witness that checks altitude and touchdown, and the next runs flew. The run record is [`reference/px4-runtime/tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih.md`](../reference/px4-runtime/tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih.md). PX4 hardware has not flown a URML program; the entry is simulation evidence only.

## Evidence kinds

`hardware_run` means the robot itself ran URML programs. `simulation_run` means a simulator of the robot or its autopilot ran them. Validation records are the gate's verdicts on the robot's manifest, replayed in CI. A compatibility claim is the conformance suite's result for the runtime's own adapter.

The kinds describe what happened. They are not ranked, and the registry computes nothing from them. Read each entry's limits next to its evidence.

## What the check verifies

`python -m urml_conformance.registry check` reads every file in `entries/` and fails on any of these:

| Field | What it holds | What the check verifies |
|---|---|---|
| `registry_version` | `"1"` | The value. No field outside the schema is allowed anywhere in the entry. |
| `id` | Lowercase words joined by hyphens | It equals the file name. |
| `title`, `submitted_by` | Text; a person or project name | No email address; no wording that suggests URML vouches for the robot. |
| `status` | `listed` or `withdrawn` | A withdrawn entry is checked for shape, paths, digests and wording, and not replayed. |
| `listed`, `last_verified` | Quoted ISO dates | `last_verified` is not earlier than `listed`. |
| `robot` | `name`, `class`, optional `maker`, `manifest` | The manifest exists and parses as a URML capability manifest. |
| `runtime` | `package`, `version`, optional `adapter` (`module:attribute`), `substrate` | A `package` that is a repository path exists. |
| `profiles` | The URML profiles the robot is listed for | At least one, none twice. |
| `compatibility` | Optional: `tier: self_reported`, `profiles`, `report` (`path`, `sha256`) | The report's sha256 matches. It parses as a `urml.conformance-report/1` report whose results agree with its summary, and every fixture passed. It names the entry's `runtime.adapter`, not the mock, and came from this repository's urml-conformance version. It ran every fixture that lists each claimed profile, wherever the fixture lives in the suite (a drone fixture can sit under `fleet/` or `rulebook/`). |
| `field_evidence` | `kind`, `date`, `by`, `summary`, `sources` | Repository paths exist. URLs are `https`. |
| `validation_records` | Optional: `path`, `sha256`, `summary`, `inputs` | The file's sha256 matches. `inputs.manifest` is the robot's manifest. Every record replays (below). |
| `limits` | What the listing does not show | At least one. |

A listed entry carries at least one piece of evidence: a compatibility claim, a field run, or validation records. The wording check covers every field a reader sees as prose, with the list in `BANNED_WORDS` in [`registry.py`](../conformance/src/urml_conformance/registry.py).

## Validation records

A validation record (`urml.validation-record/1`, [`urml_validator/evidence.py`](../reference/validator/src/urml_validator/evidence.py)) is one verdict of the validator: the program it judged, sha256 content digests of the program, manifest, envelope, policy and rulebooks, the verdict, the error and warning codes, and the validator version. The check replays each one with `reverify()`: the inputs named in the entry must hash to the digests the record carries, and the validator, run again on the recorded program, must reach the same verdict with the same error codes. When a URML release changes a verdict, the check fails, and the entry's records are produced again for that release.

Records for a listing are made by validating each program against the listed manifest, with the same inputs the entry declares. From the command line, `--evidence-log` appends one record per verdict:

```bash
urml validate examples/drone/bench-hop.urml.yaml -m examples/drone/pixhawk-ardupilot.manifest.yaml \
    --profile drone --no-policy --evidence-log registry/evidence/<id>/validation-records.jsonl
```

The two entries here were made with the Python API instead (`surface: api`), with `as_of` pinned to the day the records were made:

```python
from datetime import date
from pathlib import Path

import yaml
from urml_validator import validate
from urml_validator.evidence import append_record, build_record

manifest_path = Path("examples/drone/pixhawk-ardupilot.manifest.yaml")
manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
program = yaml.safe_load(Path("examples/drone/bench-hop.urml.yaml").read_text(encoding="utf-8"))
today = date.today()

result = validate(program, manifest, None, profiles=("drone",), policy=None,
                  manifest_base_dir=manifest_path.parent, as_of=today)
record = build_record(surface="api", stage="validation", result=result, program=program,
                      manifest=manifest, policy=None, as_of=today, profiles=("drone",))
append_record("registry/evidence/<id>/validation-records.jsonl", record)
```

`policy=None` (or `--no-policy`) matches `policy: none` in the entry's inputs; `policy="DEFAULT"` (no flag) matches `policy: default`. With `as_of` set, a replay judges rulebook dates against the day the record was made; without it, against the day of the replay. The record format and the other entry points that write records are in [docs/evidence/validation-records.md](../docs/evidence/validation-records.md).

## Run it yourself

```bash
pip install -e reference/validator -e reference/ros2-runtime -e conformance
python -m urml_conformance.registry check
python -m urml_conformance.registry export    # rewrites registry/registry.json
python -m urml_conformance.registry schema    # rewrites registry/entry.schema.json
python -m pytest conformance/tests/test_registry.py
```

[`.github/workflows/registry-check.yml`](../.github/workflows/registry-check.yml) runs the same check and tests on every pull request that touches the registry, the checker, the validator, the fixtures, or the examples an entry points at.

## Add or update an entry

[docs/registry/SUBMISSION.md](../docs/registry/SUBMISSION.md) walks through it: one YAML file, one evidence folder, the check, and a pull request.

## Withdraw an entry

Open a pull request that sets `status: withdrawn` and says why in the description. The submitter can withdraw at any time, and the maintainer withdraws an entry whose evidence no longer holds. A withdrawn entry stays in `registry.json` with that status, so a link to it keeps resolving, and git keeps the history. Its records and report are no longer replayed.
