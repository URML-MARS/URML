#!/usr/bin/env python3
"""A learned policy's URML envelope travels with the model; two checks gate it.

The flow the ExecuTorch maintainers described on pytorch/executorch#20268,
in their own four steps:

1. Export the policy and its URML envelope together (the envelope is a
   named blob next to the ``.pte``, retrievable by key through
   ``NamedDataMap``; ExecuTorch stores and returns bytes, it attaches no
   robot meaning to them).
2. Load and run the policy with ExecuTorch.
3. Interpret the model outputs in the robotics application.
4. Apply URML's checks before an approved command reaches the controller.

Step 4 is two separate checks, and keeping them separate is the point
(RFC-0383 amended 2026-08-20):

- **Check 1, static (RFC-0383, Pass 3).** The trained envelope read back
  from the bundle is merged into the manifest and checked against the
  deployment's admissible ceiling before any program is accepted. It
  compares declarations to declarations and never sees a policy output.
  ``hot.envelope.yaml`` is refused here; ``deploy.envelope.yaml`` passes.
- **Check 2, runtime (RFC-0667 shield).** Each action the policy proposes
  is checked against the envelope monitors before dispatch and the
  telemetry stream is observed after it. Under the coherent deployment
  envelope one observation drives the policy past the cap; that single
  output is vetoed and never reaches the adapter.

Hermetic by default: a fake bundle stands in for ExecuTorch (same keys,
same bytes, same order of operations), the policy is a fixed linear map,
and the committed ``executorch-policy-report.txt`` is byte-asserted in CI.
``--live`` exports a real ``torch.nn`` policy with ``executorch`` and
appends a labeled live section without touching the committed report.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Protocol

import yaml

from urml_ros2_runtime.shield import Shield, ShieldedAdapter, ShieldViolationError
from urml_validator import validate
from urml_validator.monitor import Sample, evaluate_trace

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "mobile-policy.manifest.yaml"
DEPLOY_ENVELOPE = _HERE / "deploy.envelope.yaml"
HOT_ENVELOPE = _HERE / "hot.envelope.yaml"
PROGRAM = _HERE / "patrol.urml.yaml"
REPORT = _HERE / "executorch-policy-report.txt"

# The named-data key the envelope ships under. A namespace prefix keeps it
# clear of anything a backend might reserve; the thread asks ExecuTorch
# whether `urml/` collides with anything.
ENVELOPE_KEY = "urml/learned_policy.yaml"

# Synthetic observations: distance-to-goal in metres. The fixed policy maps
# 0.5 * distance to linear velocity, so 2.4 m asks for 1.2 m/s, above both
# the deployment cap (0.8) and the trained bound (1.0). That one output is
# what Check 2 exists to catch. No observation lands exactly on the cap: a
# real float32 model returns 0.5 * 1.6 as 0.8000000119, which the shield
# correctly treats as over 0.8, and the hermetic Python-float path would
# not, so the two paths would disagree on a value that is not the point.
OBSERVATIONS: tuple[float, ...] = (0.4, 1.0, 1.5, 2.4, 0.2)
POLICY_GAIN = 0.5
POLICY_YAW_GAIN = 0.1
DT = 0.25


# ---------------------------------------------------------------------------
# Bundle seam: export together, load together. The fake mirrors the real
# named-data contract (bytes in, bytes out, by key) with no ExecuTorch import.
# ---------------------------------------------------------------------------


class PolicyRunner(Protocol):
    def __call__(self, observation: float) -> tuple[float, float]: ...


class NamedData(Protocol):
    def get(self, key: str) -> bytes | None: ...


class PolicyBundle(Protocol):
    def export(self, envelope_bytes: bytes) -> None: ...
    def load(self) -> tuple[PolicyRunner, NamedData]: ...


class FakeBundle:
    """In-memory stand-in for a .pte + .ptd pair."""

    def __init__(self) -> None:
        self._blobs: dict[str, bytes] = {}

    def export(self, envelope_bytes: bytes) -> None:
        self._blobs[ENVELOPE_KEY] = envelope_bytes

    def load(self) -> tuple[PolicyRunner, NamedData]:
        blobs = dict(self._blobs)

        class _Map:
            def get(self, key: str) -> bytes | None:
                return blobs.get(key)

        def policy(observation: float) -> tuple[float, float]:
            return (POLICY_GAIN * observation, POLICY_YAW_GAIN * observation)

        return policy, _Map()


# ---------------------------------------------------------------------------
# The substrate side of Check 2: a telemetry-capable fake adapter. It records
# only the dispatches that reach it; a vetoed action never does.
# ---------------------------------------------------------------------------


class FakeRoverAdapter:
    def __init__(self) -> None:
        self.dispatched: list[tuple[float, float]] = []
        self._speed = 0.0
        self._t = 0.0

    def drive_by(self, *, speed: float, yaw_rate: float) -> None:
        self.dispatched.append((speed, yaw_rate))
        self._speed = speed

    def sample_signals(self) -> Sample:
        self._t += DT
        return Sample(t=self._t, signals={"speed": self._speed})


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def static_check(manifest: dict[str, Any], envelope: dict[str, Any]) -> tuple[bool, list[str]]:
    """Check 1: declarations against declarations, before any program runs."""
    program = _load_yaml(PROGRAM)
    result = validate(program, manifest, envelope, profiles=("home",), policy=None)
    return result.accepted, [e.code for e in result.errors]


def runtime_check(
    policy: PolicyRunner, envelope: dict[str, Any], adapter: FakeRoverAdapter
) -> list[str]:
    """Check 2: each proposed action against the monitors, then dispatch
    through the RFC-0667 shield, which also observes telemetry afterwards."""
    shield = Shield(envelope)
    shielded = ShieldedAdapter(adapter, shield)
    critical = [p for p in shield.properties if p.severity == "critical"]
    lines: list[str] = []
    for i, obs in enumerate(OBSERVATIONS):
        speed, yaw = policy(obs)
        proposed = Sample(t=(i + 1) * DT, signals={"speed": speed})
        admissible = all(evaluate_trace(p.node, [proposed]) for p in critical)
        if not admissible:
            lines.append(
                f"  obs={obs:.1f} m -> policy proposes speed={speed:.2f} m/s: "
                "VETO (would violate envelope.max_velocity); not dispatched"
            )
            continue
        try:
            shielded.drive_by(speed=speed, yaw_rate=yaw)
        except ShieldViolationError as exc:
            lines.append(f"  obs={obs:.1f} m -> HALT after dispatch: {exc}")
            break
        lines.append(f"  obs={obs:.1f} m -> policy proposes speed={speed:.2f} m/s: ALLOW, dispatched")
    return lines


def render_report(bundle: PolicyBundle | None = None) -> str:
    bundle = bundle or FakeBundle()
    manifest = _load_yaml(MANIFEST)

    # 1. Export the envelope with the model (the learned_policy block is
    #    the envelope; it leaves the manifest and rides in the bundle).
    envelope_block = manifest.pop("learned_policy")
    bundle.export(yaml.safe_dump(envelope_block, sort_keys=True).encode("utf-8"))

    # 2. Load, and read the envelope back by key. ExecuTorch only stores and
    #    returns these bytes; parsing and meaning are URML's.
    policy, named = bundle.load()
    raw = named.get(ENVELOPE_KEY)
    assert raw is not None, f"bundle has no {ENVELOPE_KEY!r}"
    manifest["learned_policy"] = yaml.safe_load(raw.decode("utf-8"))

    out = [
        "EXPORT: learned_policy envelope packaged with the policy under "
        f"named-data key {ENVELOPE_KEY!r} ({len(raw)} bytes)",
        "LOAD: envelope read back by key and merged into the manifest",
        "",
    ]

    # 3./4. Check 1 on both deployments.
    for label, path in (("deploy", DEPLOY_ENVELOPE), ("hot", HOT_ENVELOPE)):
        env = _load_yaml(path)
        accepted, codes = static_check(manifest, env)
        verdict = "accepted" if accepted else f"REFUSED ({', '.join(codes)})"
        out.append(
            f"CHECK 1 (static, RFC-0383) {label}.envelope max_velocity={env['max_velocity']}: {verdict}"
        )
    out.append("")

    # Check 2 under the coherent deployment only; the hot one never got this far.
    adapter = FakeRoverAdapter()
    out.append("CHECK 2 (runtime, RFC-0667 shield) under deploy.envelope:")
    out.extend(runtime_check(policy, _load_yaml(DEPLOY_ENVELOPE), adapter))
    out.append(f"  dispatched to adapter: {len(adapter.dispatched)} of {len(OBSERVATIONS)} proposals")
    out.append("")
    out.append(
        "TWO CHECKS: the static check refused the over-scoped deployment without "
        "running anything; the runtime shield vetoed one out-of-range output under "
        "a deployment every declaration called coherent. Neither subsumes the other."
    )
    text = "\n".join(out) + "\n"
    # The example asserts its own claims so drift fails CI, not a reader.
    assert "hot.envelope max_velocity=1.5: REFUSED (capability.learned_policy_exceeds_training)" in text
    assert text.count("VETO") == 1 and len(adapter.dispatched) == len(OBSERVATIONS) - 1
    return text


def _live_bundle() -> PolicyBundle:
    """Real ExecuTorch: export a tiny torch policy with the envelope as named
    data, reload it, read the blob back. Imported lazily; heavy deps."""
    import torch  # type: ignore[import-not-found]
    from executorch.exir import to_edge_transform_and_lower  # type: ignore[import-not-found]
    from executorch.exir._serialize._named_data_store import (  # type: ignore[import-not-found]
        NamedDataStore,
    )
    from executorch.runtime import Runtime  # type: ignore[import-not-found]

    class _Policy(torch.nn.Module):
        def forward(self, obs: torch.Tensor) -> torch.Tensor:
            return torch.stack((POLICY_GAIN * obs, POLICY_YAW_GAIN * obs), dim=-1)

    class _Live:
        def __init__(self) -> None:
            self._out = _HERE / "live"
            self._out.mkdir(exist_ok=True)
            self._blob: bytes | None = None

        def export(self, envelope_bytes: bytes) -> None:
            self._blob = envelope_bytes
            store = NamedDataStore()
            store.add_named_data(ENVELOPE_KEY, envelope_bytes, alignment=1)
            exported = torch.export.export(_Policy(), (torch.zeros(1),))
            prog = to_edge_transform_and_lower(exported).to_executorch()
            (self._out / "policy.pte").write_bytes(prog.buffer)
            # The named data rides as an external .ptd next to the .pte.
            (self._out / "policy.ptd").write_bytes(envelope_bytes)

        def load(self) -> tuple[PolicyRunner, NamedData]:
            runtime = Runtime.get()
            program = runtime.load_program(str(self._out / "policy.pte"))
            method = program.load_method("forward")
            blob = (self._out / "policy.ptd").read_bytes()

            class _Map:
                def get(self, key: str) -> bytes | None:
                    return blob if key == ENVELOPE_KEY else None

            def policy(observation: float) -> tuple[float, float]:
                y = method.execute([torch.tensor([observation])])[0]
                return float(y[0, 0]), float(y[0, 1])

            return policy, _Map()

    return _Live()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--live", action="store_true", help="use real torch + executorch")
    args = parser.parse_args(argv)

    text = render_report()
    print(text, end="")
    REPORT.write_text(text, encoding="utf-8", newline="\n")
    print(f"(wrote {REPORT.name})")

    if args.live:
        try:
            live = render_report(_live_bundle())
        except ImportError as exc:
            print(f"--live requires torch + executorch: {exc}", file=sys.stderr)
            return 2
        print("\n=== LIVE (real ExecuTorch export/load) ===")
        print(live, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
