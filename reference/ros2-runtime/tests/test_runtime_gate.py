"""The runtime's re-validation uses the caller's policy and manifest directory.

`URMLRuntime.execute` re-validates every program before the first adapter
call. These tests pin that the re-validation runs under the policy the caller
chose (a custom policy, an HBOM-content policy, or no policy) and resolves
HBOM files against the manifest's directory. Before this, the runtime always
re-validated under the bundled default policy with no manifest directory, so
three rejected conformance fixtures still dispatched `send_navigation_goal`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from urml_ros2_runtime import MockROSAdapter, URMLRuntime, ValidationRejectedError

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"
MANIFESTS = VALIDATOR_FIXTURES / "manifests"
POLICIES = VALIDATOR_FIXTURES / "policies"

_PROGRAM: dict[str, Any] = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [{"move_to": {"location": "kitchen"}}],
    },
}


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict)
    return data


def _codes(exc: ValidationRejectedError) -> set[str]:
    result: Any = exc.validation_result
    return {e.code.value for e in result.errors}


def test_hbom_content_policy_is_enforced_by_the_runtime() -> None:
    """A CN part hidden in the HBOM is refused when the runtime gets the policy and dir."""
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    with pytest.raises(ValidationRejectedError) as excinfo:
        runtime.execute(
            _PROGRAM,
            _load(MANIFESTS / "provenance_hbom_cn_chip.yaml"),
            None,
            ("home",),
            policy=_load(POLICIES / "hbom_no_cn_components.yaml"),
            manifest_base_dir=MANIFESTS,
        )
    assert "policy.hbom_component_country_denied" in _codes(excinfo.value)
    assert adapter.call_log == []


def test_vendor_of_vendor_hbom_policy_is_enforced_by_the_runtime() -> None:
    adapter = MockROSAdapter()
    with pytest.raises(ValidationRejectedError) as excinfo:
        URMLRuntime(adapter).execute(
            _PROGRAM,
            _load(MANIFESTS / "provenance_hbom_vendor_of_vendor.yaml"),
            None,
            ("home",),
            policy=_load(POLICIES / "hbom_no_cn_components.yaml"),
            manifest_base_dir=MANIFESTS,
        )
    assert "policy.hbom_component_country_denied" in _codes(excinfo.value)
    assert adapter.call_log == []


def test_evidence_policy_is_enforced_by_the_runtime() -> None:
    adapter = MockROSAdapter()
    with pytest.raises(ValidationRejectedError) as excinfo:
        URMLRuntime(adapter).execute(
            _PROGRAM,
            _load(MANIFESTS / "evidence_mixed.yaml"),
            None,
            ("home",),
            policy=_load(POLICIES / "require_evidence_derived.yaml"),
        )
    assert "policy.evidence_insufficient" in _codes(excinfo.value)
    assert adapter.call_log == []


def test_policy_none_skips_the_compliance_pass() -> None:
    """`policy=None` is the runtime's `--no-policy`: the envelope and manifest still apply."""
    adapter = MockROSAdapter()
    result = URMLRuntime(adapter).execute(
        _PROGRAM,
        _load(MANIFESTS / "turtlebot4_home_cn_critical.yaml"),
        None,
        ("home",),
        policy=None,
    )
    assert result.success is True
    assert [e["method"] for e in adapter.call_log] == ["send_navigation_goal"]


def test_default_policy_applies_when_none_is_given() -> None:
    adapter = MockROSAdapter()
    with pytest.raises(ValidationRejectedError) as excinfo:
        URMLRuntime(adapter).execute(
            _PROGRAM, _load(MANIFESTS / "turtlebot4_home_cn_critical.yaml"), None, ("home",)
        )
    assert "policy.country_denied" in _codes(excinfo.value)
    assert adapter.call_log == []


def test_policy_none_still_enforces_the_manifest() -> None:
    """Skipping the compliance pass never skips validation itself."""
    bad: dict[str, Any] = {
        "profile": "home",
        "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "the_moon"}}]},
    }
    adapter = MockROSAdapter()
    with pytest.raises(ValidationRejectedError):
        URMLRuntime(adapter).execute(
            bad, _load(MANIFESTS / "turtlebot4_home.yaml"), None, ("home",), policy=None
        )
    assert adapter.call_log == []
