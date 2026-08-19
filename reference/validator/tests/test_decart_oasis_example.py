"""Guards for examples/decart-oasis/ (learned-world-model rehearsal spike).

Hermetic: the Oasis SDK is never imported; the injectable FakeA2V records the
exact action stream the live path would send. Pins the honesty-critical
behaviours: validate-then-gate-then-preview ordering, deterministic lowering
with clamped actions and four-tick padded chunks, gate-failure withholding
the preview, and the committed report matching a fresh hermetic run.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = REPO_ROOT / "examples" / "decart-oasis"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rehearse_oasis", EXAMPLE / "rehearse_oasis.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_lowering_is_deterministic_clamped_and_padded() -> None:
    mod = _load()
    program = {
        "behavior": {
            "steps": [
                {"drive": {"distance": 1.0}},
                {"turn": {"angle": -90}},
                {"report": {"to": "run_log", "facts": {}, "status": "success"}},
            ]
        }
    }
    ticks, trace = mod.lower_program(program)
    assert ticks == mod.lower_program(program)[0]  # deterministic
    assert len(ticks) == len(trace)
    assert all(-1.0 <= v <= 1.0 for tick in ticks for v in tick)
    # A negative turn steers left.
    assert any(t[1] < 0 for t in ticks)
    # report contributes no motion ticks: total = drive ticks + turn ticks.
    drive_ticks = mod.math.ceil(1.0 / mod.CRUISE_MPS * mod.TICK_HZ)
    turn_ticks = mod.math.ceil(mod.TURN_SECONDS_PER_90 * mod.TICK_HZ)
    assert len(ticks) == drive_ticks + turn_ticks

    chunks = mod.chunk_actions(ticks)
    assert all(len(c) == mod.ACTIONS_PER_INFER for c in chunks)
    padded = mod.chunk_actions([[0.5, 0.0]])
    assert padded == [[[0.5, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]]


def test_hermetic_run_matches_committed_report(tmp_path: Path) -> None:
    mod = _load()
    out: list[str] = []
    assert mod.run(None, None, out) is True
    fresh = "\n".join(out) + "\n"
    committed = (EXAMPLE / "decart-oasis-report.txt").read_text(encoding="utf-8")
    assert fresh == committed, "report drifted; re-run rehearse_oasis.py and commit"
    assert "GATE: PASSED" in fresh
    assert "OASIS: skipped (hermetic run" in fresh


def test_preview_streams_only_after_gate_and_sends_recorded_schedule() -> None:
    mod = _load()
    fake = mod.FakeA2V()
    out: list[str] = []
    assert mod.run(fake, None, out) is True
    assert fake.prompts == [mod.OASIS_PROMPT]
    program_ticks, _ = mod.lower_program(
        mod.yaml.safe_load(mod.PROGRAM.read_text(encoding="utf-8"))
    )
    sent = [tick for call in fake.calls for tick in call]
    assert sent[: len(program_ticks)] == [[float(a), float(b)] for a, b in program_ticks]
    assert all(len(call) == mod.ACTIONS_PER_INFER for call in fake.calls)


def test_gate_failure_withholds_the_preview(monkeypatch) -> None:
    """An over-cap motion model fails the derived critical property and Oasis
    is never contacted: validate-before-preview is the point of the example."""
    mod = _load()
    monkeypatch.setattr(mod, "CRUISE_MPS", 9.9)  # far above the 0.5 m/s cap
    fake = mod.FakeA2V()
    out: list[str] = []
    assert mod.run(fake, None, out) is False
    assert fake.prompts == []
    assert fake.calls == []
    assert any("GATE: FAILED" in line for line in out)
