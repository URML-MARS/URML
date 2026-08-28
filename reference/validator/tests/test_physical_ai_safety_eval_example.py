"""Guards for examples/physical-ai-safety-eval/ (the MHS-gate harness).

Hermetic. Pins: determinism and the committed report; every corpus row
behaves as its `expect` says with the documented codes; accepted programs
pass the envelope monitors; refused intents never reach the transport.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = REPO_ROOT / "examples" / "physical-ai-safety-eval"


def _load():
    if str(EXAMPLE) not in sys.path:
        sys.path.insert(0, str(EXAMPLE))  # the script imports its sibling mhs_adapter
    spec = importlib.util.spec_from_file_location("run_safety_eval", EXAMPLE / "run_safety_eval.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_report_is_deterministic_and_matches_committed() -> None:
    mod = _load()
    fresh = mod.render_report()
    assert fresh == mod.render_report()
    committed = (EXAMPLE / "safety-eval-report.txt").read_text(encoding="utf-8")
    assert fresh == committed, "report drifted; re-run run_safety_eval.py and commit"


def test_corpus_outcomes_and_codes() -> None:
    from urml_validator import validate

    mod = _load()
    manifest = yaml.safe_load(mod.MANIFEST.read_text(encoding="utf-8"))
    envelope = yaml.safe_load(mod.ENVELOPE.read_text(encoding="utf-8"))
    intents = yaml.safe_load(mod.INTENTS.read_text(encoding="utf-8"))
    assert len(intents) == 7
    for intent in intents:
        result = validate(intent["program"], manifest, envelope, profiles=("industrial",), policy=None)
        assert result.accepted == (intent["expect"] == "accept"), intent["id"]
        codes = {e.code for e in result.errors}
        assert set(intent.get("codes", [])) <= codes, (intent["id"], codes)


def test_refusals_never_reach_the_transport() -> None:
    mod = _load()
    text = mod.render_report()
    # Device calls only come from the two accepted programs; the summary says so.
    assert "2 accepted, 5 refused" in text
    assert "all from accepted programs" in text
    # Every accepted program passed the second check.
    assert "VIOLATED" not in text
    # A refusal names its evidence class.
    assert "capability.missing_gripper  relied on manipulation.grippers[plate_gripper]; evidence declared" in text
