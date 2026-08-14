"""The Epically Powerful actuator-envelope worked example must be deterministic and true.

Mirrors the rtic-timing / cram guards: the generator is deterministic, the committed
``epically-powerful-report.txt`` matches it, a command inside the declared actuator
envelope validates, and a command beyond it (torque or velocity) is rejected with the
RFC-0017 range code. For gatech-epic-power/epically-powerful#32.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "epically-powerful"
GEN_PATH = EX / "run_epically_powerful.py"
COMMITTED = EX / "epically-powerful-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_epically_powerful", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic() -> None:
    gen = _load_gen()
    assert gen.render_report() == gen.render_report()


def test_committed_report_matches_generator() -> None:
    gen = _load_gen()
    assert COMMITTED.exists(), f"missing {COMMITTED}"
    assert COMMITTED.read_text(encoding="utf-8") == gen.render_report(), (
        "examples/epically-powerful/epically-powerful-report.txt is stale; "
        "run `python examples/epically-powerful/run_epically_powerful.py` and commit."
    )


def test_in_envelope_validates_out_of_envelope_rejected() -> None:
    """The RFC-0017 range check: a command must lie within the declared line range."""
    gen = _load_gen()

    manifest = gen._load(gen.MANIFEST)

    ok, _, _ = gen._run(manifest, gen._TORQUE_LINE, 20.0)
    assert ok, "20 Nm is within the +/-35 Nm torque envelope"

    bad_t, bad_t_codes, _ = gen._run(manifest, gen._TORQUE_LINE, 50.0)
    assert not bad_t, "50 Nm exceeds the +/-35 Nm torque envelope"
    assert "capability.output_value_out_of_range" in bad_t_codes

    bad_v, bad_v_codes, _ = gen._run(manifest, gen._VELOCITY_LINE, 30.0)
    assert not bad_v, "30 rad/s exceeds the +/-20 rad/s velocity envelope"
    assert "capability.output_value_out_of_range" in bad_v_codes


def test_report_shows_layers_and_altitude() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "[VALID] set_output joint_torque_nm = 20.0 Nm" in report
    assert "[REJECTED] set_output joint_torque_nm = 50.0 Nm" in report
    assert "[REJECTED] set_output joint_velocity_rad_s = 30.0 rad/s" in report
    # The complementary-layers framing is present and honest about altitude.
    assert "URML's static envelope check is the first line, off-hardware" in report
    assert "no dependency on their package" in report
