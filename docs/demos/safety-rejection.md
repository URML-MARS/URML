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

This walkthrough makes that concrete. A drone is asked to fly an inspection waypoint that sits directly over a declared spectator area. URML rejects the program at validation time, emits a machine-readable error, and the re-routed program validates clean. No simulator, no API key, fully deterministic — every command below was run to produce the output shown.

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

Expected (exit code 1):

```
Validation failed: unsafe-flight.urml.yaml (1 error(s))

  ERROR [envelope.occupancy_zone_intrusion] behavior/steps/1
    field: pose
    move_to.pose (0.0, 0.0) in frame 'agl' enters the declared people-occupancy zone 'spectator_area'. Programs that route the robot through people-occupancy zones are rejected by default.
    suggestion: Re-route the target around the occupancy zone, OR mark the zone with `allow_override: true` in the envelope if the deployment has explicitly accepted the risk.
```

One error, and it is the right one. The drone's provenance is US-compliant, so the compliance pass stays silent — the *only* thing wrong with this program is that it would fly over people, and the validator's safety-envelope pass (Pass 3) catches it. **The rejection happens before takeoff.** There is no runtime geofence the operator might forget to arm; the validator is the gate.

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
    }
  ]
}
```

The `code` (`envelope.occupancy_zone_intrusion`) is a **stable string — part of the validator's public API**. The `path` points at the exact offending step. The `suggestion` states the fix in words. This is enough for a model to revise without a human in the loop: the LLM bridge's revision loop consumes precisely this payload, re-prompts the model with it, and re-validates the new emission — automatically, up to a bounded number of attempts (see [RFC-0004](../rfcs/0004-compliance-policy.md) and the 77 bridge tests under `reference/llm-bridge/tests/`).

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

Expected (exit code 0):

```
Validation passed: safe-flight.urml.yaml
```

Same drone, same deployment, same five-step shape — one coordinate moved out of the spectator area, and the program is cleared. The boundary between "rejected" and "cleared" is exactly the declared safety envelope, checked statically.

To see this same loop run *with a live model* instead of a hand-edited fix, point `urml translate` at a provider (`--provider anthropic`, requires a key): the bridge runs validate → structured error → re-prompt → re-validate for you. The walkthrough above shows the deterministic core that makes that loop trustworthy.

Cleanup:

```bash
rm unsafe-flight.urml.yaml safe-flight.urml.yaml
```

## What just happened

In four commands you saw:

- A model's program rejected for an *intent-level safety violation* (flying over people), not a syntax error — caught by static analysis before any motor turned.
- The rejection delivered as a stable, structured payload designed for a machine to act on, not just a human to read.
- The corrected program accepted, with the safety envelope as the precise, declared boundary.

This is the load-bearing claim of the whole project: an LLM in the loop does not mean an unsafe robot, because the proposal and the verification are separated, and the verifier is not optional. The strategic case is in [`MANIFESTO.md`](../../MANIFESTO.md); the envelope mechanism is the validator's Pass 3.

## What this is NOT

The walkthrough is illustrative. The occupancy-zone polygon, the drone manifest, and the provenance block are fixtures with fictional vendor identifiers; no claim about any real product or site is made. A program passing the validator is a static guarantee about *declared* capabilities and the *declared* envelope — it is not a substitute for real flight authorization, real airspace deconfliction, or counsel review. URML refuses programs that violate the declared envelope; it cannot verify that the declared envelope matches the real world. That boundary is the deployer's.

## Files used in this walkthrough

- `reference/validator/tests/fixtures/manifests/drone_civilian.yaml` — the civilian-drone manifest (US-compliant provenance, so Pass 5 stays silent and the envelope rejection is the only error).
- [`reference/validator/tests/fixtures/envelopes/drone_with_occupancy_zone.yaml`](../../reference/validator/tests/fixtures/envelopes/drone_with_occupancy_zone.yaml) — the safety envelope declaring `spectator_area`.
- `unsafe-flight.urml.yaml` / `safe-flight.urml.yaml` — created inline by the commands above; deleted at the end. No new committed files.

## Related reading

- [Compliance walkthrough](compliance-walkthrough.md) — the same "rejected before any actuator moves" property, for the hardware-provenance pass instead of the safety envelope.
- [Tutorial 3 — Natural language to URML](../tutorials/03-natural-language-to-urml.md) — the LLM bridge and its revision loop.
- [RFC-0004](../rfcs/0004-compliance-policy.md) — the bridge's structured-error revision mechanism, including the policy-error short-circuit.
- The conformance fixture `conformance/fixtures/drone/09_occupancy_zone_intrusion_rejected.yaml` — the same rejection, asserted as a permanent contract any URML-compatible runtime must reproduce.
