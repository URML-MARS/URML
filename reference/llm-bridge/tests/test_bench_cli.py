"""`urml bench` CLI tests: hermetic, echo provider only.

These live in the llm-bridge package because `urml bench` needs both
urml-validator (the CLI) and urml-llm-bridge (the engine) installed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from urml_validator.cli import main

from .test_bench import RED_MUG_PROGRAM, REFUSAL_PROGRAM

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures" / "manifests" / "turtlebot4_home.yaml"
HOME_CORPUS = REPO_ROOT / "bench" / "corpora" / "home-en.yaml"


@pytest.fixture
def mini_corpus(tmp_path: Path) -> Path:
    p = tmp_path / "mini.yaml"
    p.write_text(
        yaml.safe_dump(
            {
                "corpus_id": "mini",
                "profile": "home",
                "language": "en",
                "utterances": [
                    {"id": "mug", "text": "Bring me the red mug.", "expected": "accept"},
                    {"id": "sandwich", "text": "Make me a sandwich.", "expected": "refuse"},
                ],
            }
        ),
        encoding="utf-8",
    )
    return p


@pytest.fixture
def echo_script(tmp_path: Path) -> Path:
    p = tmp_path / "script.yaml"
    p.write_text(
        yaml.safe_dump(
            {
                "mug": json.dumps(RED_MUG_PROGRAM),
                "sandwich": REFUSAL_PROGRAM,  # non-string values are JSON-dumped by the CLI
            }
        ),
        encoding="utf-8",
    )
    return p


def _run_bench(
    mini_corpus: Path, echo_script: Path, out: Path, *extra: str
) -> int:
    return main(
        [
            "bench",
            "--corpus",
            str(mini_corpus),
            "--manifest",
            str(MANIFEST),
            "--provider",
            "echo",
            "--echo-script",
            str(echo_script),
            "--no-policy",
            "--out",
            str(out),
            *extra,
        ]
    )


def test_bench_end_to_end(
    mini_corpus: Path, echo_script: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "row.yaml"
    rc = _run_bench(mini_corpus, echo_script, out)
    assert rc == 0
    captured = capsys.readouterr()
    assert "honest_refusal" in captured.out
    assert "| echo | mini | 2 |" in captured.out
    assert out.is_file()
    row = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert row["counts"]["accepted"] == 1
    assert row["counts"]["honest_refusal"] == 1
    assert row["expected_match_rate"] == 1.0


def test_bench_fail_under_match_gate(
    mini_corpus: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A script that refuses everything: the mug row misses its expectation.
    script = tmp_path / "refuse-all.yaml"
    script.write_text(
        yaml.safe_dump({"m": json.dumps(REFUSAL_PROGRAM)}), encoding="utf-8"
    )  # "m" substring-matches both utterances
    out = tmp_path / "row.yaml"
    rc = _run_bench(mini_corpus, script, out, "--fail-under-match", "0.9")
    assert rc == 1
    assert "bench gate failed" in capsys.readouterr().err


def test_bench_render_aggregates(
    mini_corpus: Path, echo_script: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out_dir = tmp_path / "rows"
    rc = _run_bench(mini_corpus, echo_script, out_dir / "row.yaml")
    assert rc == 0
    capsys.readouterr()
    rc = main(["bench", "--render", str(out_dir)])
    assert rc == 0
    table = capsys.readouterr().out
    assert table.startswith("| Model |")
    assert "| mini | 2 |" in table


def test_bench_usage_errors(echo_script: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # No corpus.
    rc = main(["bench", "--manifest", str(MANIFEST), "--provider", "echo", "--echo-script", str(echo_script)])
    assert rc == 2
    assert "--corpus" in capsys.readouterr().err
    # No manifest.
    rc = main(["bench", "--corpus", str(HOME_CORPUS), "--provider", "echo", "--echo-script", str(echo_script)])
    assert rc == 2
    assert "--manifest" in capsys.readouterr().err
    # --echo-script with a non-echo provider.
    rc = main(
        [
            "bench",
            "--corpus",
            str(HOME_CORPUS),
            "--manifest",
            str(MANIFEST),
            "--provider",
            "ollama",
            "--model",
            "x",
            "--echo-script",
            str(echo_script),
        ]
    )
    assert rc == 2
    assert "--echo-script" in capsys.readouterr().err


def test_bench_render_missing_dir(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["bench", "--render", str(tmp_path / "nope")])
    assert rc == 1
    assert "results directory not found" in capsys.readouterr().err
