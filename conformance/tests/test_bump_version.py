"""Offline unit tests for the lockstep version-bump script.

`tools/scripts/bump_version.py` rewrites every version surface of the
twenty-package family (pyproject `version =`, `_version.py`
`__version__ =`, intra-repo `urml-*>=X` pins, the validator docstring
`Stability:` line). These tests exercise apply and check against a
synthetic two-package tree, pinning the behaviours most likely to drift:
non-URML pins are never touched, and check flags any straggler.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUMP_PY = REPO_ROOT / "tools" / "scripts" / "bump_version.py"


def _load_bump():
    spec = importlib.util.spec_from_file_location("bump_version", BUMP_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def mini_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A two-package family shaped like the real tree."""
    mod = _load_bump()
    monkeypatch.setattr(mod, "PACKAGE_DIRS", ("reference/validator", "conformance"))

    validator = tmp_path / "reference" / "validator"
    (validator / "src" / "urml_validator").mkdir(parents=True)
    (validator / "pyproject.toml").write_text(
        '[project]\nname = "urml-validator"\nversion = "0.3.0"\n'
        'dependencies = [\n  "pyyaml>=6.0",\n]\n',
        encoding="utf-8",
    )
    # The annotated spelling used by the validator/bridge/conformance files.
    (validator / "src" / "urml_validator" / "_version.py").write_text(
        '__version__: str = "0.3.0"\n', encoding="utf-8"
    )
    (validator / "src" / "urml_validator" / "__init__.py").write_text(
        '"""Stability: 0.3.0. The schemas track the vocabulary."""\n',
        encoding="utf-8",
    )

    conformance = tmp_path / "conformance"
    (conformance / "src" / "urml_conformance").mkdir(parents=True)
    (conformance / "pyproject.toml").write_text(
        '[project]\nname = "urml-conformance"\nversion = "0.3.0"\n'
        "dependencies = [\n"
        '  "urml-validator>=0.3.0",\n'
        '  "martypy>=3.2",\n'
        "]\n"
        "[project.optional-dependencies]\n"
        'llm = ["urml-llm-bridge>=0.3.0"]\n',
        encoding="utf-8",
    )
    (conformance / "src" / "urml_conformance" / "_version.py").write_text(
        '__version__ = "0.3.0"\n', encoding="utf-8"
    )
    return tmp_path


def test_apply_rewrites_every_surface(mini_tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_bump()
    monkeypatch.setattr(mod, "PACKAGE_DIRS", ("reference/validator", "conformance"))
    rc = mod.apply(mini_tree, "0.3.0", "0.4.0")
    assert rc == 0

    validator_pyproject = (mini_tree / "reference/validator/pyproject.toml").read_text("utf-8")
    assert 'version = "0.4.0"' in validator_pyproject

    conformance_pyproject = (mini_tree / "conformance/pyproject.toml").read_text("utf-8")
    assert 'version = "0.4.0"' in conformance_pyproject
    assert "urml-validator>=0.4.0" in conformance_pyproject
    assert "urml-llm-bridge>=0.4.0" in conformance_pyproject  # the optional-extra pin
    assert "martypy>=3.2" in conformance_pyproject  # non-URML pins never touched

    version_py = (mini_tree / "reference/validator/src/urml_validator/_version.py").read_text("utf-8")
    assert version_py == '__version__: str = "0.4.0"\n'


def test_apply_updates_validator_stability_docstring(
    mini_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load_bump()
    monkeypatch.setattr(mod, "PACKAGE_DIRS", ("reference/validator", "conformance"))
    mod.apply(mini_tree, "0.3.0", "0.4.0")
    init = (mini_tree / "reference/validator/src/urml_validator/__init__.py").read_text("utf-8")
    assert "Stability: 0.4.0." in init


def test_check_passes_after_apply_and_flags_drift(
    mini_tree: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = _load_bump()
    monkeypatch.setattr(mod, "PACKAGE_DIRS", ("reference/validator", "conformance"))
    assert mod.check(mini_tree, "0.3.0") == 0
    mod.apply(mini_tree, "0.3.0", "0.4.0")
    assert mod.check(mini_tree, "0.4.0") == 0

    # Introduce a straggler pin and confirm check catches it.
    pyproject = mini_tree / "conformance" / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text("utf-8").replace("urml-llm-bridge>=0.4.0", "urml-llm-bridge>=0.3.0"),
        encoding="utf-8",
    )
    assert mod.check(mini_tree, "0.4.0") == 1
    assert "DRIFT" in capsys.readouterr().out


def test_apply_is_a_noop_second_time(mini_tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_bump()
    monkeypatch.setattr(mod, "PACKAGE_DIRS", ("reference/validator", "conformance"))
    assert mod.apply(mini_tree, "0.3.0", "0.4.0") == 0
    assert mod.apply(mini_tree, "0.3.0", "0.4.0") == 1  # nothing left at 0.3.0
