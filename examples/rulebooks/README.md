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

# Rulebooks: government and company rules the validator checks

A rulebook states what law or a company allows a robot to do. The validator checks every program against the rulebooks that apply to it, after the safety envelope, and cites the rule when it refuses. The format is in [`spec/layer-1-hal/rulebook.md`](../../spec/layer-1-hal/rulebook.md) and the decision record is [RFC-0702](../../docs/rfcs/0702-rulebooks.md).

These files are a Draft, like RFC-0702. The reference validator reads them: `--rulebook PATH` loads an organization or deployment rulebook, and the bundled FAA rulebook applies by default to aircraft.

## Four files, four owners

| File | Says | Owner |
|---|---|---|
| Manifest | what the robot can do | the robot's maker or integrator |
| Safety envelope | what this site allows physically | the site operator |
| Rulebook | what law and company policy allow | a regulator or an organization; the operator, for declarations and exceptions |
| Compliance policy | what the robot may be made of | procurement |

A rulebook names places and never draws them. A zone name in a rule resolves against the manifest's `declared_areas`, then the envelope's `people_occupancy_zones` and `geofences`.

## The files here

| File | Kind | What it shows |
|---|---|---|
| [`example-warehouse.yaml`](example-warehouse.yaml) | organization | Example Logistics, a fictional company: no photos or video in the restrooms or the HR office, no entry to the server room or the hazmat cage, an allowlist of controller programs, and a 1.5 m/s speed cap |
| [`example-deployment.yaml`](example-deployment.yaml) | deployment | A fictional drone operator: one declaration (a Remote ID broadcast module) and one exception (a fictional certificate of waiver that raises the altitude limit to 500 feet, 152.4 m) |
| [`industrial-template.yaml`](industrial-template.yaml) | organization, template | How an integrator maps ISO 10218-1:2025, ISO 10218-2:2025 and ISO/TS 15066:2016 onto rules and obligations. It carries no values: the ISO text is copyrighted, and every value comes from the integrator's risk assessment and licensed copy. An unfilled template fails to load |

The bundled government rulebook lives with the validator: [`us_faa_part107.yaml`](../../reference/validator/src/urml_validator/rulebooks/us_faa_part107.yaml), the statically checkable subset of 14 CFR Part 107 and Part 89. It applies by default to drone programs and to any robot whose manifest declares an aircraft drive type, and `--no-policy` does not switch it off. `--no-default-rulebooks` does, with a warning.

Everything named Example Logistics, Example Aerial Survey or 107W-EXAMPLE-0001 is fictional.

## How the pieces fit

The FAA rulebook caps altitude at 121.92 m (400 feet) above ground level. A program that takes off to 137.16 m (450 feet) is refused, even with `--no-policy` (an excerpt of the output):

```text
  ERROR [rule.cap_exceeded] behavior/steps/0
    field: altitude
    14 CFR 107.51(b): maximum altitude 400 feet (121.92 m) above ground level. take_off.altitude is 137.16 m; the limit is 121.92 m.
    suggestion: Use a value at or below 121.92 m.
    rule: us_faa_part107/altitude_400ft_agl (Federal Aviation Administration, US)
    source: https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107/subpart-B/section-107.51#p-107.51(b)
```

The operator's deployment rulebook records a waiver as an exception. The exception names its basis and a new limit, and the same program is accepted with a warning that names the waiver. The model cannot write that file: a waiver the user claims in a sentence changes nothing.

The rules a program cannot show, such as visual line of sight, night lighting and weather minimums, appear as obligations in every report. URML lists them and does not check them.

The commands:

```bash
urml validate program.urml.yaml -m manifest.yaml -e envelope.yaml \
  --rulebook examples/rulebooks/example-warehouse.yaml
urml validate flight.urml.yaml -m drone.manifest.yaml \
  --rulebook examples/rulebooks/example-deployment.yaml
```

The conformance fixtures under [`conformance/fixtures/rulebook/`](../../conformance/fixtures/rulebook/) run both files, and each rejected fixture also proves URML sent zero commands.

## Not legal advice

A program passing a rulebook is not a legal compliance determination. A rulebook checks the statically checkable subset of the rules it encodes, and the operator remains responsible for all of them. Verify the bundled rulebook against the current eCFR before relying on it; its `reviewed` date says when it was last checked.
