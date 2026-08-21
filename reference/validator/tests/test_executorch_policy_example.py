"""Guards for examples/executorch-policy/ (envelope-with-the-model, two checks).

Hermetic: no torch, no ExecuTorch. Pins the promises made on
pytorch/executorch#20268: the envelope round-trips by key through the
bundle, the static check refuses the over-scoped deployment with the exact
error code, the runtime shield vetoes the single out-of-range output before
it reaches the adapter, and the committed report matches a fresh run.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = REPO_ROOT / "examples" / "executorch-policy"


def _load():
    spec = importlib.util.spec_from_file_location(
        "run_executorch_policy", EXAMPLE / "run_executorch_policy.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_report_is_deterministic_and_matches_committed() -> None:
    mod = _load()
    fresh = mod.render_report()
    assert fresh == mod.render_report()
    committed = (EXAMPLE / "executorch-policy-report.txt").read_text(encoding="utf-8")
    assert fresh == committed, "report drifted; re-run run_executorch_policy.py and commit"


def test_envelope_round_trips_by_key_through_the_bundle() -> None:
    mod = _load()
    bundle = mod.FakeBundle()
    block = yaml.safe_load(mod.MANIFEST.read_text(encoding="utf-8"))["learned_policy"]
    raw = yaml.safe_dump(block, sort_keys=True).encode("utf-8")
    bundle.export(raw)
    _policy, named = bundle.load()
    assert named.get(mod.ENVELOPE_KEY) == raw
    assert named.get("something/else") is None
    assert yaml.safe_load(raw)["command_ranges"][0]["max"] == 1.0


def test_static_check_refuses_hot_and_accepts_deploy() -> None:
    mod = _load()
    manifest = yaml.safe_load(mod.MANIFEST.read_text(encoding="utf-8"))
    ok, codes = mod.static_check(manifest, {"max_velocity": 0.8})
    assert ok and codes == []
    ok, codes = mod.static_check(manifest, {"max_velocity": 1.5})
    assert not ok
    assert "capability.learned_policy_exceeds_training" in codes


def test_runtime_shield_vetoes_only_the_out_of_range_output() -> None:
    mod = _load()
    policy, _named = mod.FakeBundle().load()
    adapter = mod.FakeRoverAdapter()
    lines = mod.runtime_check(policy, {"max_velocity": 0.8}, adapter)
    vetoes = [ln for ln in lines if "VETO" in ln]
    assert len(vetoes) == 1 and "speed=1.20" in vetoes[0]
    # The vetoed proposal never reached the adapter; the other four did.
    assert len(adapter.dispatched) == len(mod.OBSERVATIONS) - 1
    assert all(speed <= 0.8 for speed, _yaw in adapter.dispatched)
