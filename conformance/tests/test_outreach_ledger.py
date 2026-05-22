"""The Move #1 outreach ledger must not drift from the demo runner.

`examples/lighthouses/outreach.yaml` is the per-vendor record of what was
sent to whom and what came back. `examples/lighthouses/demo.py` enumerates
the same 16 vendors as the parameterized demo runner. If those two ever
disagree (a vendor added to demo.py without a row, or vice versa), the
"listen" side of the project goes blind.

This test asserts:

  * Ledger slug set == LIGHTHOUSES slug set (no missing rows, no orphans).
  * Each ledger row's `rfc` integer matches demo.py's RFC for the same slug.
  * `response` is one of the documented enum values.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "examples" / "lighthouses" / "outreach.yaml"
DEMO_PY = REPO_ROOT / "examples" / "lighthouses" / "demo.py"

_VALID_RESPONSE = {"none", "acked", "engaged", "declined", "wontfix"}


def _load_demo_lighthouses() -> dict:
    spec = importlib.util.spec_from_file_location("lighthouses_demo", DEMO_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.LIGHTHOUSES


def _load_ledger() -> list[dict]:
    with LEDGER.open(encoding="utf-8") as fh:
        rows = yaml.safe_load(fh)
    assert isinstance(rows, list), "outreach.yaml must be a YAML list"
    return rows


def test_ledger_and_demo_lighthouses_have_identical_slug_sets() -> None:
    rows = _load_ledger()
    ledger_slugs = {row["slug"] for row in rows}
    demo_slugs = set(_load_demo_lighthouses().keys())
    extra_in_ledger = ledger_slugs - demo_slugs
    missing_from_ledger = demo_slugs - ledger_slugs
    assert not extra_in_ledger, (
        f"outreach.yaml has slugs not in demo.py LIGHTHOUSES: "
        f"{sorted(extra_in_ledger)!r}"
    )
    assert not missing_from_ledger, (
        f"demo.py LIGHTHOUSES has slugs missing from outreach.yaml: "
        f"{sorted(missing_from_ledger)!r}"
    )


def test_ledger_rfc_numbers_match_demo_runner() -> None:
    rows = _load_ledger()
    demo = _load_demo_lighthouses()
    for row in rows:
        slug = row["slug"]
        demo_rfc = demo[slug][0]
        assert row["rfc"] == demo_rfc, (
            f"{slug}: ledger rfc={row['rfc']} but demo.py rfc={demo_rfc}"
        )


def test_ledger_response_values_are_in_the_enum() -> None:
    rows = _load_ledger()
    for row in rows:
        assert row["response"] in _VALID_RESPONSE, (
            f"{row['slug']}: response={row['response']!r} is not one of "
            f"{sorted(_VALID_RESPONSE)!r}"
        )


def test_ledger_required_fields_present() -> None:
    required = {"slug", "rfc", "sent_at", "channel", "contact",
                "last_touch", "response", "next_action", "notes"}
    for row in _load_ledger():
        missing = required - row.keys()
        assert not missing, f"{row.get('slug','?')}: missing fields {missing!r}"
