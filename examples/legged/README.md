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

# Legged Examples

End-to-end legged-robot programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`).

Legged locomotion adds no new profile — the program uses the core twelve under the `home` profile (profiles over forks), exactly as the quadruped conformance fixtures do. The same program validates and executes adapter-agnostically against the legged runtime's `SpotAdapter` / `AnymalAdapter` and hermetically against the mock.

## Scenarios

- **`spot-patrol`** — the minimum-viable legged example. A navigation-only patrol on a `quadruped` manifest ([RFC-0009](../../docs/rfcs/0009-legged-humanoid-mobility.md) `mobility.drive_type: quadruped`): walk to two patrol waypoints, then return to the dock. `dock` is a declared *location* (it has a pose), not a docking action, so the program stays within core navigation.
- **`bittle-sentence`** — the $299 desktop-quadruped hero. RFC-0062 deliverable for [PetoiCamp/OpenCat-Quadruped-Robot#113](https://github.com/PetoiCamp/OpenCat-Quadruped-Robot/issues/113) (Dr. Rongzhong Li, Petoi founder, round-1 + round-2 engagement 2026-05-28 / 2026-05-29). One English sentence — *"Walk forward to the waypoint, then sit on the rest mat."* — translates through URML's NL → primitive → adapter pipeline. On a real Bittle X via the edu-runtime's [`PetoiAdapter`](../../reference/edu-runtime/src/urml_edu_runtime/adapter.py), the three `move_to` calls become maintainer-confirmed OpenCat tokens via the `PetoiRobot` module-level API: `sendSkillStr('kbalance', 0)`, `sendCmdStr('kwkF 5', 0)` (walk forward 5 cycles), `sendSkillStr('ksit', 0)`.

## Validate

```
urml validate spot-patrol.urml.yaml \
  -m spot-patrol.manifest.yaml --profile home
```

The companion manifest is the canonical Spot quadruped fixture. Pass `--no-policy` to skip Pass 5 when exercising programs against manifests without a provenance block. To watch it run on the hermetic mock:

```
urml execute spot-patrol.urml.yaml \
  -m spot-patrol.manifest.yaml --profile home --no-policy
```

## Bittle hero loop (hermetic, no API key, no robot)

The Bittle manifest carries `country_of_origin: CN` (Petoi is Shenzhen), so the bundled US-federal default policy ([RFC-0004](../../docs/rfcs/0004-compliance-policy.md)) would reject it under Pass 5. The hero loop uses `--no-policy` per the universal-language re-anchor (CLAUDE.md 2026-05-16): the language is on stage, compliance is one flag away. Deployment-time acceptance is the operator's policy decision.

```
# 1. Translate the English sentence to URML (echo provider — hermetic, no API key).
urml translate "Walk forward to the waypoint, then sit on the rest mat." \
  --provider echo \
  --echo-response-file bittle-sentence.echo-response.json \
  -m bittle-sentence.manifest.yaml --profile educational --no-policy \
  --out bittle.generated.yaml

# 2. Validate the generated URML against the Bittle X manifest.
urml validate bittle.generated.yaml \
  -m bittle-sentence.manifest.yaml --profile educational --no-policy

# 3. Execute on the hermetic mock — no actuator moves, but the audit trace
# is the same one PetoiAdapter would dispatch to OpenCat on a real Bittle X.
urml execute bittle.generated.yaml --adapter mock \
  -m bittle-sentence.manifest.yaml --profile educational --no-policy
```

The recorded run lives at [`docs/assets/bittle-sentence-to-motion.svg`](../../docs/assets/bittle-sentence-to-motion.svg) — every "out" line in the SVG is asserted byte-for-byte against a live hermetic run by [`reference/validator/tests/test_bittle_demo_svg.py`](../../reference/validator/tests/test_bittle_demo_svg.py). Regenerate the asset with `make demo-record`.

See the examples convention in [`/examples/README.md`](../README.md).
