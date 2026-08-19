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

# Rehearsing a validated program in a learned world model (Decart Oasis 3)

One validated URML patrol, rolled through [Decart's Oasis 3](https://decart.ai/publications/introducing-oasis-3-first-interactive-world-model-for-physical-ai), an action-conditioned generative world model with an API. The order of operations is the whole point, and it is the same order as RFC-0668's rehearsal gate:

1. `patrol.urml.yaml` validates against `scout.manifest.yaml` and `envelope.yaml`. Nothing is lowered before this.
2. The validated steps lower to a deterministic `[throttle, steering]` schedule under a **declared motion model** (constants at the top of `rehearse_oasis.py`, printed in every report).
3. The **machine gate**: RFC-0667 monitors evaluate the kinematic trace of that schedule against the envelope. A critical violation withholds the preview.
4. Only then does the same action stream go to Oasis 3 (four ticks per `infer()` call), which returns photorealistic frames.

## What the Oasis output is, and is not

The frames are a **human-reviewable visual preview** of what the validated program does. They are not physical evidence: Oasis 3 is a generative model, not a calibrated simulator, and no gate in this example consumes anything extracted from its frames. The machine gate runs entirely on the declared kinematic model, exactly as the hermetic RFC-0668 backend does. If URML ever grows a first-class `--rehearse` backend for learned world models, its evidence class ("learned world model, human-reviewable") stays distinct from the kinematic and physics-sim classes; that distinction is what keeps the rehearsal story honest.

## Run it

Hermetic (no network, no SDK, deterministic; the committed `decart-oasis-report.txt` is byte-asserted in CI):

```bash
python rehearse_oasis.py
```

Live (requires `pip install decart-oasis` and a `DECART_API_KEY` from [platform.decart.ai](https://platform.decart.ai); the API is a paid preview):

```bash
python rehearse_oasis.py --live --frames-dir frames/
```

Frames land as PPM files (stdlib writer, no image dependencies); `frames/` is gitignored. First verified live run: 2026-08-19, 14 `infer()` calls, 56 front-camera frames at 768x512.

## Files

- `scout.manifest.yaml` — a differential-drive sidewalk scout (RFC-0630 `drive`/`turn` relative motion, educational profile).
- `envelope.yaml` — a `max_velocity` cap; RFC-0667 derives it into an implicit critical `always` property, which is what the gate evaluates.
- `patrol.urml.yaml` — the validated program.
- `rehearse_oasis.py` — validate, lower, gate, preview. The Oasis client is injectable; the hermetic fake records the exact action stream the live path would send.
