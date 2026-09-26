"""Guards for examples/goalkeeper/ (the goalkeeper demo).

Hermetic. Pins: the transcript is deterministic, and both the in-process
render and the script's own stdout equal the committed
goalkeeper-transcript.txt byte for byte; every attack is refused by the
validator and by the runtime with its expected code while the recording
adapter sees zero calls; the safe and beyond-envelope requests pass and reach
the adapter; each request carries the hazard label the bench corpus gives
it; the transcript stays short, ASCII and free of absolute paths; the
README quotes only real transcript lines; and a runtime that skips its check
shows up in the transcript as commands sent.
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml

pytest.importorskip("urml_ros2_runtime")
pytest.importorskip("urml_conformance")

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = REPO_ROOT / "examples" / "goalkeeper"
SCRIPT = EXAMPLE / "run_goalkeeper.py"
TRANSCRIPT = EXAMPLE / "goalkeeper-transcript.txt"
REGENERATE = "run `python examples/goalkeeper/run_goalkeeper.py --write` and commit the transcript"


def _load() -> ModuleType:
    name = "run_goalkeeper"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # Registered before exec: dataclasses resolve string annotations through sys.modules.
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _codes(errors: list[Any]) -> set[str]:
    return {str(getattr(e.code, "value", e.code)) for e in errors}


def test_transcript_is_deterministic_and_matches_committed() -> None:
    mod = _load()
    fresh = mod.render()
    assert fresh == mod.render()
    assert fresh.encode("utf-8") == TRANSCRIPT.read_bytes(), f"transcript drifted; {REGENERATE}"


def test_script_prints_the_committed_transcript_byte_for_byte() -> None:
    """Run the script the way a reader does. Its stdout is the committed file."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(p for p in sys.path if p)  # import what this process imports
    run = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, cwd=REPO_ROOT, env=env, timeout=600, check=False
    )
    assert run.returncode == 0, run.stderr.decode("utf-8", errors="replace")
    assert run.stdout == TRANSCRIPT.read_bytes(), f"script output drifted; {REGENERATE}"


def test_every_attack_is_refused_and_urml_sends_nothing() -> None:
    mod = _load()
    outcomes = mod.play()
    attacks = [o for o in outcomes if o.request.kind == "attack"]
    assert 6 <= len(attacks) <= 8
    assert {o.request.robot.name for o in attacks} == {"cobot arm", "home robot", "drone"}
    for o in attacks:
        assert not o.verdict.accepted, o.label
        assert o.request.expect in _codes(o.verdict.errors), (o.label, _codes(o.verdict.errors))
        assert o.runtime_refused, f"the runtime did not refuse: {o.label}"
        assert o.request.expect in o.runtime_codes, (o.label, o.runtime_codes)
        assert o.commands == (), (o.label, o.commands)
    assert mod.attacks_stopped(outcomes)


def test_the_safe_and_beyond_envelope_requests_pass_and_reach_the_adapter() -> None:
    mod = _load()
    passes = {o.request.kind: o for o in mod.play() if o.request.kind != "attack"}
    assert set(passes) == {"safe", "beyond"}
    for o in passes.values():
        assert o.verdict.accepted and not o.runtime_refused, o.label
        assert o.commands, o.label
    # The beyond-envelope program does what its label says: the latch command reaches the adapter.
    assert "set_output_line" in passes["beyond"].commands


def test_each_request_carries_the_bench_hazard_label_it_claims() -> None:
    """Attacks are envelope rows, the safe request a control, the last one a beyond_envelope row."""
    mod = _load()
    hazard_for = {"attack": "envelope", "safe": "none", "beyond": "beyond_envelope"}
    for request in mod.REQUESTS:
        robot = request.robot
        assert robot.striker.parent == REPO_ROOT / "bench" / "strikers"
        assert robot.envelope.parent == REPO_ROOT / "bench" / "envelopes"
        # A striker shares its file name with the corpus it answers (bench/README.md).
        corpus = yaml.safe_load((REPO_ROOT / "bench" / "corpora" / robot.striker.name).read_text(encoding="utf-8"))
        assert corpus["profile"] == robot.profile
        rows = [row for row in corpus["utterances"] if request.key in row["text"]]
        assert len(rows) == 1, (request.key, [row["id"] for row in rows])
        assert rows[0]["hazard"] == hazard_for[request.kind], (request.key, rows[0]["hazard"])


def test_transcript_is_short_ascii_and_portable() -> None:
    mod = _load()
    text = TRANSCRIPT.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) <= 35
    assert text.isascii(), "plain ASCII only: no em-dashes or typographic quotes"
    assert not re.search(r"\b[A-Za-z]:[\\/]", text), "no absolute Windows paths"
    assert str(REPO_ROOT) not in text and REPO_ROOT.as_posix() not in text
    assert not re.search(r"\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}:\d{2}", text), "no dates or timestamps"
    n = len(mod.ATTACKS)
    assert text.count("URML sent 0 commands.") == n
    assert lines[-1].startswith(f"Tally: {n} of {n} attacks refused, 0 commands sent for them.")


def test_readme_quotes_only_real_transcript_lines() -> None:
    readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
    quoted = [line for block in re.findall(r"```text\n(.*?)```", readme, flags=re.S) for line in block.splitlines()]
    assert quoted, "the README quotes the transcript in ```text blocks"
    transcript = set(TRANSCRIPT.read_text(encoding="utf-8").splitlines())
    for line in quoted:
        assert line in transcript, f"README quotes a line the transcript does not have: {line!r}"


def test_a_runtime_that_skips_its_check_shows_up_in_the_transcript() -> None:
    """The transcript counts commands; it never assumes a refusal."""
    from urml_ros2_runtime import URMLRuntime

    mod = _load()
    outcomes = mod.play(runtime_factory=lambda adapter: URMLRuntime(adapter, revalidate=False))
    text = mod.render(outcomes)
    n = len(mod.ATTACKS)
    sent = sum(len(o.commands) for o in outcomes if o.request.kind == "attack")
    assert not mod.attacks_stopped(outcomes)
    assert sent > 0
    assert "URML sent 0 commands." not in text
    assert text.count("The runtime ran it anyway.") == n
    assert text.splitlines()[-1].startswith(f"Tally: 0 of {n} attacks refused, {sent} commands sent for them.")
