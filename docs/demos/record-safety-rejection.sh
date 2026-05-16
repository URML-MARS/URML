#!/usr/bin/env bash
# Recording script for the safety-rejection walkthrough.
#
#   asciinema rec safety-rejection.cast -c "bash docs/demos/record-safety-rejection.sh"
#
# Run from the repo root, after `python bootstrap.py` and activating the
# venv. Mirrors docs/demos/safety-rejection.md exactly. Fully offline and
# deterministic — no simulator, no API key. Uses repo fixtures
# (drone_civilian manifest + drone_with_occupancy_zone envelope) and a
# scratch program created/removed by this script.
set -euo pipefail

MANIFEST=reference/validator/tests/fixtures/manifests/drone_civilian.yaml
ENVELOPE=reference/validator/tests/fixtures/envelopes/drone_with_occupancy_zone.yaml

say() { printf '\n\033[1;36m# %s\033[0m\n' "$*"; sleep 1.2; }
run() { printf '\033[1;32m$ %s\033[0m\n' "$*"; sleep 0.6; eval "$*"; sleep 1.8; }
cleanup() { rm -f unsafe-flight.urml.yaml safe-flight.urml.yaml; }
trap cleanup EXIT

say "An LLM emits a drone program. One waypoint sits over a spectator area."
cat > unsafe-flight.urml.yaml <<'EOF'
profile: drone
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - take_off: { altitude: 30.0 }
    - move_to: { pose: { x: 0.0, y: 0.0, z: 30.0 }, frame: agl }
    - capture: { media: photo, store_as: shot }
    - return_to_home: {}
    - land: {}
EOF
run "cat unsafe-flight.urml.yaml"

say "Scene 1 — URML refuses it, before takeoff."
run "urml validate unsafe-flight.urml.yaml -m $MANIFEST -e $ENVELOPE --profile drone || true"
say "envelope.occupancy_zone_intrusion — caught by static analysis."

say "Scene 2 — the exact structured error the LLM bridge feeds back:"
run "urml validate unsafe-flight.urml.yaml -m $MANIFEST -e $ENVELOPE --profile drone --json | python -m json.tool || true"

say "Scene 3 — the model re-routes 10m north. Nothing else changes."
cat > safe-flight.urml.yaml <<'EOF'
profile: drone
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - take_off: { altitude: 30.0 }
    - move_to: { pose: { x: 10.0, y: 5.0, z: 30.0 }, frame: agl }
    - capture: { media: photo, store_as: shot }
    - return_to_home: {}
    - land: {}
EOF
run "urml validate safe-flight.urml.yaml -m $MANIFEST -e $ENVELOPE --profile drone"
say "Validation passed. The boundary is exactly the declared safety envelope."
