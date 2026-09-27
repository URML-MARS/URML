"""Committed bench rows must reproduce.

A number published from `bench/results/` is only as good as the row behind
it. This guard re-runs every committed scripted row in-process (echo
provider, no model) against the inputs its `setup` block names, and asserts
that the fresh run matches the committed row: counts, the gate block, and
each result's outcome, codes and attempts. It also re-hashes every input the
row pins, so an edited manifest, envelope or striker fails here until the
row is re-recorded. A stale number cannot stay published.

Two kinds of row are not re-run:

- Rows tagged `pre-fix` (row id ending in `-pre-fix`). They record the gate
  before a fix landed (the committed ones: c2d251d, before the envelope
  coverage fixes in 949ce9b), and do not reproduce on later code by design.
- Live-model rows. Re-running one needs a provider, and a model's output is
  not deterministic. They are skipped with that reason.
"""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
import yaml
from urml_validator.cli import main

from urml_llm_bridge.bench import load_corpus

REPO_ROOT = Path(__file__).resolve().parents[3]
BENCH = REPO_ROOT / "bench"
RESULTS = BENCH / "results"

#: The `--tag` of a before-the-fix row: history, not a claim about today's gate.
PRE_FIX_TAG = "pre-fix"

#: Setup entries that pin an input file by sha256.
PINNED_INPUTS = ("manifest", "envelope", "echo_script")

#: Row-level fields a re-run must reproduce.
ROW_FIELDS = (
    "schema_version",
    "corpus_id",
    "profile",
    "n",
    "counts",
    "expected_match_rate",
    "revision_attempts_mean",
    "gate",
)

#: Per-result fields a re-run must reproduce. `detail` is left out: it is
#: free text derived from `attempts`.
RESULT_FIELDS = (
    "utterance_id",
    "outcome",
    "expected",
    "expected_match",
    "revision_count",
    "attempts",
    "codes",
    "attempt_codes",
    "attack",
    "hazard",
)

RERECORD = "re-record it as bench/README.md (Published rows) describes"


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path} is not a bench row"
    return data


ROWS: dict[str, dict[str, Any]] = (
    {p.relative_to(RESULTS).as_posix(): _load(p) for p in sorted(RESULTS.rglob("*.yaml"))}
    if RESULTS.is_dir()
    else {}
)


def is_pre_fix(row: dict[str, Any]) -> bool:
    return str(row.get("row_id", "")).endswith(f"-{PRE_FIX_TAG}")


def is_scripted(row: dict[str, Any]) -> bool:
    """A row the echo provider produced from a striker script: re-runnable."""
    setup = row.get("setup") or {}
    return setup.get("provider") == "echo"


GUARDED = sorted(name for name, row in ROWS.items() if not is_pre_fix(row))


def input_drift(row: dict[str, Any], root: Path = REPO_ROOT) -> list[str]:
    """Pinned inputs that are missing or no longer hash to the recorded sha256."""
    drift: list[str] = []
    setup = row.get("setup") or {}
    for name in PINNED_INPUTS:
        ref = setup.get(name)
        if ref is None:
            continue
        path = root / ref["path"]
        if not path.is_file():
            drift.append(f"{name} {ref['path']} is missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            drift.append(f"{name} {ref['path']} changed since the row was recorded")
    return drift


def reproduction_drift(committed: dict[str, Any], fresh: dict[str, Any]) -> list[str]:
    """What a fresh run changed relative to the committed row, one line per field."""
    drift: list[str] = []
    committed_ids = [r["utterance_id"] for r in committed["results"]]
    fresh_ids = [r["utterance_id"] for r in fresh["results"]]
    if committed_ids != fresh_ids:
        return [f"utterances: committed {committed_ids}, now {fresh_ids}"]
    for was, now in zip(committed["results"], fresh["results"], strict=True):
        for field in RESULT_FIELDS:
            if was.get(field) != now.get(field):
                drift.append(
                    f"{was['utterance_id']}.{field}: committed {was.get(field)!r}, "
                    f"now {now.get(field)!r}"
                )
    for field in ROW_FIELDS:
        if committed.get(field) != fresh.get(field):
            drift.append(f"{field}: committed {committed.get(field)!r}, now {fresh.get(field)!r}")
    return drift


def _corpus_path(corpus_id: str) -> Path:
    by_id = {load_corpus(p).corpus_id: p for p in sorted((BENCH / "corpora").glob("*.yaml"))}
    assert corpus_id in by_id, f"no corpus under bench/corpora/ has corpus_id {corpus_id!r}"
    return by_id[corpus_id]


def rerun(row: dict[str, Any], out: Path) -> dict[str, Any]:
    """Run the same hermetic bench the row records, in-process, and load the fresh row."""
    setup = row["setup"]
    assert setup["echo_script"] is not None, "a scripted row must pin its --echo-script"
    args = [
        "bench",
        "--corpus", str(_corpus_path(row["corpus_id"])),
        "--manifest", str(REPO_ROOT / setup["manifest"]["path"]),
        "--provider", "echo",
        "--echo-script", str(REPO_ROOT / setup["echo_script"]["path"]),
        "--max-revisions", str(setup["max_revisions"]),
        "--out", str(out),
    ]
    if setup["envelope"] is not None:
        args += ["--envelope", str(REPO_ROOT / setup["envelope"]["path"])]
    for profile in setup["profiles"]:
        args += ["--profile", profile]
    if setup["policy"] == "none":
        args.append("--no-policy")
    elif setup["policy"] != "default":
        args += ["--policy", str(REPO_ROOT / setup["policy"])]
    assert main(args) == 0
    return _load(out)


# ---------------------------------------------------------------------------
# Every committed row, the pre-fix ones included
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(ROWS))
def test_row_is_well_formed(name: str) -> None:
    """Schema version 2, named after its row id, with repo-relative input paths."""
    row = ROWS[name]
    assert row.get("schema_version") == 2, name
    assert PurePosixPath(name).stem == row["row_id"], name
    setup = row.get("setup")
    assert isinstance(setup, dict), f"{name} has no setup block; record it with `urml bench`"
    for field in PINNED_INPUTS:
        ref = setup.get(field)
        if ref is None:
            continue
        path = PurePosixPath(ref["path"])
        # Recorded from the repository root: no drive letter, no backslash, no escape.
        assert not path.is_absolute() and ":" not in ref["path"], (name, ref["path"])
        assert "\\" not in ref["path"] and ".." not in path.parts, (name, ref["path"])


# ---------------------------------------------------------------------------
# The guard: every row except the pre-fix ones
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", GUARDED)
def test_row_inputs_are_unchanged(name: str) -> None:
    row = ROWS[name]
    if not is_scripted(row):
        pytest.skip("live-model row: not re-run, so its inputs are not guarded")
    drift = input_drift(row)
    assert not drift, f"{name}: {'; '.join(drift)}; {RERECORD}"


@pytest.mark.parametrize("name", GUARDED)
def test_row_reproduces(name: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    row = ROWS[name]
    if not is_scripted(row):
        pytest.skip("live-model row: re-running it needs a provider")
    fresh = rerun(row, tmp_path / "fresh.yaml")
    capsys.readouterr()
    drift = reproduction_drift(row, fresh)
    assert not drift, f"{name} no longer reproduces; {RERECORD}:\n" + "\n".join(drift)


@pytest.mark.parametrize(
    "stem", sorted(p.stem for p in (BENCH / "strikers").glob("*.yaml"))
)
def test_each_striker_has_a_guarded_row(stem: str) -> None:
    """The published after-numbers stay backed: every striker has a current row."""
    script = f"bench/strikers/{stem}.yaml"
    rows = [
        name
        for name in GUARDED
        if is_scripted(ROWS[name]) and (ROWS[name]["setup"]["echo_script"] or {}).get("path") == script
    ]
    assert rows, f"no committed row outside `{PRE_FIX_TAG}` was measured with {script}"


def test_pre_fix_rows_are_labeled() -> None:
    """The before rows exist, and their notes say the guard skips them."""
    excluded = sorted(name for name, row in ROWS.items() if is_pre_fix(row))
    assert excluded, "the before rows (tag pre-fix) are missing from bench/results/"
    for name in excluded:
        assert "excluded from the results guard" in ROWS[name]["notes"], name


# ---------------------------------------------------------------------------
# The guard catches drift
# ---------------------------------------------------------------------------


def test_row_kinds() -> None:
    """Only the pre-fix tag excludes a row; only echo rows are re-run."""
    assert is_pre_fix({"row_id": "2026-09-26-echo-echo-adversarial-home-en-pre-fix"})
    assert not is_pre_fix({"row_id": "2026-09-26-echo-echo-adversarial-home-en-post-fix"})
    assert not is_pre_fix({"row_id": "2026-09-26-echo-echo-pre-fix-drills"})
    assert is_scripted({"setup": {"provider": "echo"}})
    assert not is_scripted({"setup": {"provider": "ollama"}})
    assert not is_scripted({"setup": None})


def _a_scripted_row() -> dict[str, Any]:
    """A copy of a committed scripted row with a gate block and at least one stop."""
    for name in GUARDED:
        row = ROWS[name]
        stops = [r for r in row["results"] if r["outcome"] != "accepted"]
        if is_scripted(row) and row.get("gate") and stops:
            return copy.deepcopy(row)
    pytest.fail("no committed scripted row with a gate block and a stop to test the guard with")


def test_guard_flags_a_changed_outcome() -> None:
    committed = _a_scripted_row()
    fresh = copy.deepcopy(committed)
    stopped = next(r for r in fresh["results"] if r["outcome"] != "accepted")
    stopped["outcome"] = "accepted"
    stopped["codes"] = []
    fresh["counts"]["accepted"] += 1
    drift = reproduction_drift(committed, fresh)
    assert any(line.startswith(f"{stopped['utterance_id']}.outcome:") for line in drift)
    assert any(line.startswith(f"{stopped['utterance_id']}.codes:") for line in drift)
    assert any(line.startswith("counts:") for line in drift)


def test_guard_flags_a_changed_gate_and_a_dropped_utterance() -> None:
    committed = _a_scripted_row()
    fresh = copy.deepcopy(committed)
    hazard = next(iter(fresh["gate"]))
    fresh["gate"][hazard]["passed"] += 1
    assert any(line.startswith("gate:") for line in reproduction_drift(committed, fresh))
    fresh = copy.deepcopy(committed)
    fresh["results"].pop()
    assert reproduction_drift(committed, fresh)[0].startswith("utterances:")


def test_guard_flags_an_edited_input(tmp_path: Path) -> None:
    script = tmp_path / "bench" / "strikers" / "edited.yaml"
    script.parent.mkdir(parents=True)
    script.write_text("take_off: {}\n", encoding="utf-8")
    recorded = hashlib.sha256(script.read_bytes()).hexdigest()
    row = {
        "setup": {
            "manifest": None,
            "envelope": None,
            "echo_script": {"path": "bench/strikers/edited.yaml", "sha256": recorded},
        }
    }
    assert input_drift(row, root=tmp_path) == []
    script.write_text("take_off: {altitude: 500}\n", encoding="utf-8")
    assert input_drift(row, root=tmp_path) == [
        "echo_script bench/strikers/edited.yaml changed since the row was recorded"
    ]
    script.unlink()
    assert input_drift(row, root=tmp_path) == [
        "echo_script bench/strikers/edited.yaml is missing"
    ]
