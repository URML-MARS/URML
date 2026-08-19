#!/usr/bin/env python3
"""Rehearse a validated URML program in Decart's Oasis 3 world model.

The seam this example proves: a URML program is validated against the
manifest and envelope, its steps lower to a deterministic action schedule
under a declared motion model, the RFC-0667 kinematic gate evaluates that
schedule against the envelope, and only then does the same action stream
roll through Oasis 3 (an action-conditioned learned world model) to produce
a watchable, photorealistic preview of what the validated program does.

Honesty first, because a learned world model invites overclaiming:

- The MACHINE gate here is the kinematic one, exactly as in RFC-0668. The
  velocity trace it evaluates comes from the declared motion model below,
  not from Oasis.
- The Oasis output is a VISUAL PREVIEW for a human reviewer. It is evidence
  of nothing physical: Oasis 3 is a generative model, not a calibrated
  simulator, and no signal extracted from its frames feeds any gate. The
  evidence class is "learned world model, human-reviewable", distinct from
  the kinematic and MuJoCo rehearsal classes.
- Bare invocation is hermetic (a fake client, no network, deterministic
  report). ``--live`` requires the ``decart-oasis`` SDK and a
  ``DECART_API_KEY``; the API is a paid preview, so nothing contacts it
  unless asked.

Usage:

    python rehearse_oasis.py                       # hermetic dry run + report
    python rehearse_oasis.py --live                # also stream through Oasis 3
    python rehearse_oasis.py --live --frames-dir frames/   # save PPM frames
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path
from typing import Any, Protocol

import yaml

from urml_validator import validate
from urml_validator.monitor import Sample, compile_envelope_monitors, evaluate_trace

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "scout.manifest.yaml"
ENVELOPE = _HERE / "envelope.yaml"
PROGRAM = _HERE / "patrol.urml.yaml"
REPORT = _HERE / "decart-oasis-report.txt"

# ---------------------------------------------------------------------------
# The declared motion model. These constants ARE the model: the kinematic gate
# judges the schedule under them, and the report prints them, so the evidence
# is always labeled with the assumptions it was produced under (the RFC-0668
# posture: a passed rehearsal is evidence under a named motion model).
# ---------------------------------------------------------------------------

CRUISE_MPS = 0.4          # assumed speed while a `drive` step runs
TURN_MPS = 0.1            # assumed speed while a `turn` step runs
TICK_HZ = 4.0             # schedule resolution; Oasis takes 4 ticks per infer()
THROTTLE_PER_MPS = 1.25   # maps model m/s onto Oasis throttle in [-1, 1]
TURN_STEER = 0.4          # steering magnitude while turning
TURN_SECONDS_PER_90 = 2.0 # assumed duration of a 90-degree turn

ACTIONS_PER_INFER = 4     # Oasis 3 contract: four [throttle, steering] per call
OASIS_PROMPT = "a small delivery robot driving along a quiet urban sidewalk, daylight"


def _clamp(x: float) -> float:
    return max(-1.0, min(1.0, x))


def lower_program(program: dict[str, Any]) -> tuple[list[list[float]], list[Sample]]:
    """Lower validated steps to (action ticks, kinematic trace).

    Each tick is one ``[throttle, steering]`` pair at ``TICK_HZ``; the trace
    carries the model velocity for the same tick, which is what the gate
    evaluates. Deterministic and pure: same program, same schedule.
    """
    ticks: list[list[float]] = []
    trace: list[Sample] = []

    def _emit(n: int, throttle: float, steering: float, velocity: float) -> None:
        for _ in range(n):
            ticks.append([_clamp(throttle), _clamp(steering)])
            # `speed` is the ego signal name RFC-0667's derived caps bind to.
            trace.append(Sample(t=len(ticks) / TICK_HZ, signals={"speed": velocity}))

    for step in program["behavior"]["steps"]:
        (verb, args), = step.items()
        if verb == "drive":
            seconds = float(args["distance"]) / CRUISE_MPS
            _emit(
                max(1, math.ceil(seconds * TICK_HZ)),
                CRUISE_MPS * THROTTLE_PER_MPS,
                0.0,
                CRUISE_MPS,
            )
        elif verb == "turn":
            angle = float(args["angle"])
            seconds = abs(angle) / 90.0 * TURN_SECONDS_PER_90
            _emit(
                max(1, math.ceil(seconds * TICK_HZ)),
                TURN_MPS * THROTTLE_PER_MPS,
                TURN_STEER if angle > 0 else -TURN_STEER,
                TURN_MPS,
            )
        # report/speak and other non-motion verbs contribute no motion ticks.
    return ticks, trace


def chunk_actions(ticks: list[list[float]]) -> list[list[list[float]]]:
    """Group ticks into Oasis infer() calls of exactly four, zero-padded."""
    chunks = []
    for i in range(0, len(ticks), ACTIONS_PER_INFER):
        chunk = [list(t) for t in ticks[i : i + ACTIONS_PER_INFER]]
        while len(chunk) < ACTIONS_PER_INFER:
            chunk.append([0.0, 0.0])
        chunks.append(chunk)
    return chunks


# ---------------------------------------------------------------------------
# Oasis client seam. The real SDK (decart-oasis) is imported only under
# --live; the fake keeps the example hermetic and the schedule inspectable.
# ---------------------------------------------------------------------------


class OasisClient(Protocol):
    def prompt(self, text: str) -> None: ...
    def infer(self, actions: list[list[float]]) -> Any: ...


class FakeA2V:
    """Records the action stream; returns no frames (hermetic)."""

    def __init__(self) -> None:
        self.prompts: list[str] = []
        self.calls: list[list[list[float]]] = []

    def prompt(self, text: str) -> None:
        self.prompts.append(text)

    def infer(self, actions: list[list[float]]) -> Any:
        self.calls.append(actions)
        return type("R", (), {"frames": {}})()


def _write_ppm(path: Path, frame: Any) -> None:
    """Save one RGB uint8 frame as binary PPM, stdlib only."""
    height, width = frame.shape[0], frame.shape[1]
    with path.open("wb") as fh:
        fh.write(f"P6\n{width} {height}\n255\n".encode("ascii"))
        fh.write(frame.tobytes())


def run(client: OasisClient | None, frames_dir: Path | None, out: list[str]) -> bool:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    envelope = yaml.safe_load(ENVELOPE.read_text(encoding="utf-8"))
    program = yaml.safe_load(PROGRAM.read_text(encoding="utf-8"))

    # 1. Validate: nothing is lowered, previewed, or streamed before this.
    result = validate(program, manifest, envelope, profiles=("educational",))
    if not result.accepted:
        out.append("VALIDATION: REJECTED")
        for issue in result.errors:
            out.append(f"  {issue.code}: {issue.message}")
        return False
    out.append("VALIDATION: accepted (educational profile, scout manifest)")

    # 2. Lower under the declared motion model.
    ticks, trace = lower_program(program)
    chunks = chunk_actions(ticks)
    out.append(
        "MOTION MODEL: "
        f"cruise={CRUISE_MPS} m/s, turn={TURN_MPS} m/s at {TICK_HZ:.0f} Hz, "
        f"throttle_per_mps={THROTTLE_PER_MPS}, turn_steer={TURN_STEER}"
    )
    out.append(f"SCHEDULE: {len(ticks)} ticks -> {len(chunks)} Oasis infer() calls")

    # 3. The machine gate: RFC-0667 monitors over the kinematic trace.
    gate_ok = True
    for prop in compile_envelope_monitors(envelope):
        verdict = evaluate_trace(prop.node, trace)
        out.append(
            f"GATE [{prop.severity}] {prop.name} ({prop.source}): "
            f"{'satisfied' if verdict else 'VIOLATED'}"
        )
        if not verdict and prop.severity == "critical":
            gate_ok = False
    if not gate_ok:
        out.append("GATE: FAILED under the declared motion model; Oasis preview withheld.")
        return False
    out.append("GATE: PASSED under the declared motion model.")

    # 4. The visual preview (only after the gate, mirroring RFC-0668's order).
    if client is None:
        out.append("OASIS: skipped (hermetic run; pass --live to stream the preview)")
        return True
    client.prompt(OASIS_PROMPT)
    frame_count = 0
    for i, chunk in enumerate(chunks):
        result = client.infer(chunk)
        front = getattr(result, "frames", {}).get("front", [])
        if frames_dir is not None:
            frames_dir.mkdir(parents=True, exist_ok=True)
            for j, frame in enumerate(front):
                _write_ppm(frames_dir / f"front-{i:04d}-{j}.ppm", frame)
        frame_count += len(front)
    out.append(
        f"OASIS: streamed {len(chunks)} infer() calls, received {frame_count} front frames. "
        "EVIDENCE CLASS: learned world model, human-reviewable preview only; "
        "no gate consumes these frames."
    )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--live", action="store_true", help="stream through the real Oasis 3 API")
    parser.add_argument("--frames-dir", type=Path, default=None, metavar="DIR")
    args = parser.parse_args(argv)

    client: OasisClient | None = None
    if args.live:
        try:
            from decart_oasis import A2VClient
        except ImportError:
            print("--live requires the SDK: pip install decart-oasis", file=sys.stderr)
            return 2
        if not os.environ.get("DECART_API_KEY"):
            print("--live requires DECART_API_KEY (see docs.platform.decart.ai)", file=sys.stderr)
            return 2
        client = A2VClient()

    out: list[str] = []
    try:
        if args.live and client is not None:
            with client:  # type: ignore[union-attr]
                ok = run(client, args.frames_dir, out)
        else:
            ok = run(None, None, out)
    except ConnectionError as exc:
        print(f"oasis: connection failed: {exc}", file=sys.stderr)
        return 1

    text = "\n".join(out) + "\n"
    print(text, end="")
    if not args.live:
        REPORT.write_text(text, encoding="utf-8", newline="\n")
        print(f"(wrote {REPORT.name})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
