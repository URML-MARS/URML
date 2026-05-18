"""Tests for the ``python -m urml_conformance`` BYO-adapter entrypoint."""

from __future__ import annotations

import pytest

from urml_conformance.__main__ import _load_adapter_factory, main


def test_default_run_is_hermetic_and_green() -> None:
    """No --adapter: the MockROSAdapter self-test passes (exit 0)."""
    assert main([]) == 0


def test_filter_selects_a_subset() -> None:
    assert main(["--filter", "quadruped"]) == 0


def test_filter_with_no_match_returns_2() -> None:
    assert main(["--filter", "no-such-fixture-zzz"]) == 2


def test_bad_adapter_spec_is_actionable() -> None:
    with pytest.raises(SystemExit, match="module:attribute"):
        _load_adapter_factory("notacolonspec")


def test_unimportable_adapter_module_is_actionable() -> None:
    with pytest.raises(SystemExit, match="could not import"):
        _load_adapter_factory("urml_conformance._definitely_missing:Thing")


def test_non_callable_attribute_is_rejected() -> None:
    with pytest.raises(SystemExit, match="not callable"):
        _load_adapter_factory("urml_conformance:__doc__")
