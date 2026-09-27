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

# Safety-rejection walkthrough — the LLM proposed it, URML refused it

The one-line story behind URML: *a language model can propose an unsafe action, and the system statically refuses it before a single actuator moves — handing back a structured error precise enough to drive an automated correction.*

This walkthrough makes that concrete. A drone is asked to fly an inspection waypoint that sits directly over a declared spectator area. URML rejects the program at validation time and emits a machine-readable error. The re-routed program clears the envelope, and the bundled FAA Part 107 rulebook (RFC-0702, on by default for drone programs) still refuses it, because its return-to-home point sits inside the spectator area. No simulator, no API key, fully deterministic: every command below was run to produce the output shown.

Useful for: video demos, slide decks, the "why not just let the LLM drive the robot" conversation, blog posts. Fits on one screen at presentation zoom.

## Prerequisites

- URML installed from a checkout per [Tutorial 1](../tutorials/01-getting-started.md) (`python bootstrap.py`).
- A terminal, `cd` into the URML repository root.

The deployment is described by two files already in the repo — the canonical civilian-drone manifest and a safety envelope that declares a people-occupancy zone:

- `reference/validator/tests/fixtures/manifests/drone_civilian.yaml` — a multirotor with US-compliant hardware provenance.
- `reference/validator/tests/fixtures/envelopes/drone_with_occupancy_zone.yaml` — declares `spectator_area`, a polygon from (-3,-3) to (3,3) in the `agl` frame, `allow_override: false`.

## Scene 1 — the unsafe intent

The model emits this program: take off, fly to a waypoint, photograph it, return, land. The waypoint `(0, 0)` happens to be dead center over the spectator area.

```bash
cat > unsafe-flight.urml.yaml <<'EOF'
profile: drone
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - take_off: { altitude: 30.0 }
    - move_to:
        pose: { x: 0.0, y: 0.0, z: 30.0 }
        frame: agl
    - capture: { media: photo, store_as: shot }
    - return_to_home: {}
    - land: {}
EOF

urml validate unsafe-flight.urml.yaml \
    -m reference/validator/tests/fixtures/manifests/drone_civilian.yaml \
    -e reference/validator/tests/fixtures/envelopes/drone_with_occupancy_zone.yaml \
    --profile drone
```

Expected (exit code 1), the errors first:

```
Validation failed: unsafe-flight.urml.yaml (3 error(s), 2 warning(s))

  ERROR [envelope.occupancy_zone_intrusion] behavior/steps/1
    field: pose
    move_to.pose (0.0, 0.0) in frame 'agl' enters the declared people-occupancy zone 'spectator_area'. Programs that route the robot through people-occupancy zones are rejected by default.
    suggestion: Re-route the target around the occupancy zone, OR mark the zone with `allow_override: true` in the envelope if the deployment has explicitly accepted the risk.

  ERROR [rule.over_people] behavior/steps/1
    field: pose
    14 CFR 107.39: no flight over human beings unless the operation meets a Subpart D category. move_to.pose (0, 0) in frame 'agl' is over the people-occupancy zone 'spectator_area'.
    suggestion: Choose a target outside the people-occupancy zone 'spectator_area'.
    rule: us_faa_part107/over_human_beings (Federal Aviation Administration, US)
    source: https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107/subpart-B/section-107.39

  ERROR [rule.over_people] behavior/steps/3
    field: home
    14 CFR 107.39: no flight over human beings unless the operation meets a Subpart D category. return_to_home 'home' is over the people-occupancy zone 'spectator_area'.
    suggestion: Choose a target outside the people-occupancy zone 'spectator_area'.
    rule: us_faa_part107/over_human_beings (Federal Aviation Administration, US)
    source: https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107/subpart-B/section-107.39
```

Two warnings follow: no deployment rulebook declares how the drone meets Remote ID (14 CFR Part 89), and the manifest's provenance is self-declared. Then the rulebook report lists the Part 107 obligations URML cannot check, such as visual line of sight and weather minima.

Three errors, and they are the right ones. The safety-envelope pass (Pass 3) refuses the waypoint over the spectator area. The rulebook pass refuses the same waypoint under 14 CFR 107.39, and also the return to the home point at (0, 0), which sits inside the area. Each rulebook error cites the regulation it enforces. **The rejection happens before takeoff.** There is no runtime geofence the operator might forget to arm; the validator is the gate.

## Scene 2 — the structured error the model gets back

The same validation, as JSON — this is exactly what the LLM bridge feeds back to the model on a rejected emission:

```bash
urml validate unsafe-flight.urml.yaml \
    -m reference/validator/tests/fixtures/manifests/drone_civilian.yaml \
    -e reference/validator/tests/fixtures/envelopes/drone_with_occupancy_zone.yaml \
    --profile drone --json
```

The relevant slice:

```json
{
  "accepted": false,
  "errors": [
    {
      "code": "envelope.occupancy_zone_intrusion",
      "path": ["behavior", "steps", "1"],
      "field": "pose",
      "message": "move_to.pose (0.0, 0.0) in frame 'agl' enters the declared people-occupancy zone 'spectator_area'. Programs that route the robot through people-occupancy zones are rejected by default.",
      "suggestion": "Re-route the target around the occupancy zone, OR mark the zone with `allow_override: true` in the envelope if the deployment has explicitly accepted the risk."
    },
    {
      "code": "rule.over_people",
      "path": ["behavior", "steps", "1"],
      "field": "pose",
      "message": "14 CFR 107.39: no flight over human beings unless the operation meets a Subpart D category. move_to.pose (0, 0) in frame 'agl' is over the people-occupancy zone 'spectator_area'.",
      "suggestion": "Choose a target outside the people-occupancy zone 'spectator_area'."
    },
    {
      "code": "rule.over_people",
      "path": ["behavior", "steps", "3"],
      "field": "home",
      "message": "14 CFR 107.39: no flight over human beings unless the operation meets a Subpart D category. return_to_home 'home' is over the people-occupancy zone 'spectator_area'.",
      "suggestion": "Choose a target outside the people-occupancy zone 'spectator_area'."
    }
  ]
}
```

The JSON also carries the warnings and a `rulebooks` report: each rulebook applied, with its obligations.

The codes (`envelope.occupancy_zone_intrusion`, `rule.over_people`) are **stable strings, part of the validator's public API**. The `path` points at the exact offending step. The `suggestion` states the fix in words. This is enough for a model to revise without a human in the loop: the LLM bridge's revision loop consumes precisely this payload, re-prompts the model with it, and re-validates the new emission, automatically, up to a bounded number of attempts (see [RFC-0004](../rfcs/0004-compliance-policy.md) and the bridge tests under `reference/llm-bridge/tests/`).

## Scene 3 — the corrected program

The model (or a person) reads the error and re-routes the waypoint clear of the zone — `(10, 5)` instead of `(0, 0)`. Nothing else changes.

```bash
cat > safe-flight.urml.yaml <<'EOF'
profile: drone
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - take_off: { altitude: 30.0 }
    - move_to:
        pose: { x: 10.0, y: 5.0, z: 30.0 }
        frame: agl
    - capture: { media: photo, store_as: shot }
    - return_to_home: {}
    - land: {}
EOF

urml validate safe-flight.urml.yaml \
    -m reference/validator/tests/fixtures/manifests/drone_civilian.yaml \
    -e reference/validator/tests/fixtures/envelopes/drone_with_occupancy_zone.yaml \
    --profile drone
```

Expected (exit code 1), the error first:

```
Validation failed: safe-flight.urml.yaml (1 error(s), 2 warning(s))

  ERROR [rule.over_people] behavior/steps/3
    field: home
    14 CFR 107.39: no flight over human beings unless the operation meets a Subpart D category. return_to_home 'home' is over the people-occupancy zone 'spectator_area'.
    suggestion: Choose a target outside the people-occupancy zone 'spectator_area'.
    rule: us_faa_part107/over_human_beings (Federal Aviation Administration, US)
    source: https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107/subpart-B/section-107.39
```

The same two warnings and the rulebook report follow, as in Scene 1.

The envelope is satisfied now: the waypoint is clear of the zone, and Pass 3 has nothing left to say. The program is still refused, this time by the law. `return_to_home` flies back to the home point at (0, 0), inside the spectator area, and 14 CFR 107.39 forbids flight over people unless the operation meets a Subpart D category. The fix is a deployment decision the model cannot make on its own: move the home point out of the zone, or declare an operations-over-people category in the operator's deployment rulebook. This walkthrough keeps the refusal. The envelope held the site's limit, the rulebook held the law, and both acted before takeoff.

To see this same loop run *with a live model* instead of a hand-edited fix, point `urml translate` at a provider (`--provider anthropic`, requires a key): the bridge runs validate → structured error → re-prompt → re-validate for you. The walkthrough above shows the deterministic core that makes that loop trustworthy.

Cleanup:

```bash
rm unsafe-flight.urml.yaml safe-flight.urml.yaml
```

## What just happened

In four commands you saw:

- A model's program rejected for an *intent-level safety violation* (flying over people), not a syntax error — caught by static analysis before any motor turned.
- The rejection delivered as a stable, structured payload designed for a machine to act on, not just a human to read.
- The corrected program cleared the envelope and was still refused by the FAA rulebook for returning over the spectator area: two declared boundaries, the site's and the law's, checked before takeoff.

This is the load-bearing claim of the whole project: an LLM in the loop does not mean an unsafe robot, because the proposal and the verification are separated, and the verifier is not optional. The strategic case is in [`MANIFESTO.md`](../../MANIFESTO.md); the envelope mechanism is the validator's Pass 3, and the rulebook pass is specified in [RFC-0702](../rfcs/0702-rulebooks.md) and [`spec/layer-1-hal/rulebook.md`](../../spec/layer-1-hal/rulebook.md).

## What this is NOT

The walkthrough is illustrative. The occupancy-zone polygon, the drone manifest, and the provenance block are fixtures with fictional vendor identifiers; no claim about any real product or site is made. A program passing the validator is a static guarantee about *declared* capabilities and the *declared* envelope — it is not a substitute for real flight authorization, real airspace deconfliction, or counsel review. URML refuses programs that violate the declared envelope; it cannot verify that the declared envelope matches the real world. That boundary is the deployer's.

## Files used in this walkthrough

- `reference/validator/tests/fixtures/manifests/drone_civilian.yaml`: the civilian-drone manifest (US-compliant provenance, so Pass 5 raises no error; it flags the self-declared attestation as a warning).
- [`reference/validator/src/urml_validator/rulebooks/us_faa_part107.yaml`](../../reference/validator/src/urml_validator/rulebooks/us_faa_part107.yaml): the bundled FAA Part 107 rulebook, loaded by default for drone programs.
- [`reference/validator/tests/fixtures/envelopes/drone_with_occupancy_zone.yaml`](../../reference/validator/tests/fixtures/envelopes/drone_with_occupancy_zone.yaml) — the safety envelope declaring `spectator_area`.
- `unsafe-flight.urml.yaml` / `safe-flight.urml.yaml` — created inline by the commands above; deleted at the end. No new committed files.

## Related reading

- [Compliance walkthrough](compliance-walkthrough.md) — the same "rejected before any actuator moves" property, for the hardware-provenance pass instead of the safety envelope.
- [Tutorial 3 — Natural language to URML](../tutorials/03-natural-language-to-urml.md) — the LLM bridge and its revision loop.
- [RFC-0004](../rfcs/0004-compliance-policy.md) — the bridge's structured-error revision mechanism, including the policy-error short-circuit.
- The conformance fixture `conformance/fixtures/drone/09_occupancy_zone_intrusion_rejected.yaml` — the same rejection, asserted as a permanent contract any URML-compatible runtime must reproduce.
