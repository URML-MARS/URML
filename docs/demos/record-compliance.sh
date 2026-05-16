#!/usr/bin/env bash
# Recording script for the compliance walkthrough.
#
#   asciinema rec compliance.cast -c "bash docs/demos/record-compliance.sh"
#
# Run from the repo root, after `python bootstrap.py` and activating the
# venv (so `urml` is on PATH). Every command and its expected output is
# documented verbatim in docs/demos/compliance-walkthrough.md — this
# script is exactly those commands, paced for a screen recording.
set -euo pipefail

say() { printf '\n\033[1;36m# %s\033[0m\n' "$*"; sleep 1.2; }
run() { printf '\033[1;32m$ %s\033[0m\n' "$*"; sleep 0.6; eval "$*"; sleep 1.8; }

say "URML compliance: same program, three manifests, one flag."
run "cat examples/home/red-mug.urml.yaml"

say "Scene 1 — the US-compliant deployment. Expect: Validation passed."
run "urml validate examples/home/red-mug.urml.yaml \
  -m examples/home/red-mug.manifest.yaml --profile home"

say "Scene 2 — swap to a CN-origin critical component. Same program."
run "urml validate examples/home/red-mug.urml.yaml \
  -m examples/home/red-mug.cn-critical.manifest.yaml --profile home || true"
say "Rejected with policy.country_denied — before any actuator moves."

say "Scene 3 — a covered vendor (FCC Covered List marker)."
run "urml validate examples/home/red-mug.urml.yaml \
  -m examples/home/red-mug.dji-camera.manifest.yaml --profile home || true"
say "Different rule, same shape: policy.vendor_denied."

say "Scene 4 — the override. Non-US deployers skip Pass 5."
run "urml validate examples/home/red-mug.urml.yaml \
  -m examples/home/red-mug.cn-critical.manifest.yaml --profile home --no-policy"
say "Same non-compliant manifest, accepted. The mechanism is generic;"
say "only the bundled default is US-aligned. Full story: MANIFESTO.md."
