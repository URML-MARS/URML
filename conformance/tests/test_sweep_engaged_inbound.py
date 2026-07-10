"""Offline unit tests for the engaged-inbound sweep's URL parser.

`tools/scripts/sweep_engaged_inbound.py` is a read-only triage that, for
every engaged ledger row carrying a `posted_url`, fetches the newest
comment and flags an unhandled maintainer reply. The network side needs
`gh`; the URL parsing does not, and it is the part most likely to drift.

These tests pin `_URL_RE` behaviour, in particular the reason ledger rows
must record a GitHub *repo-form* discussion URL
(`.../owner/repo/discussions/N`) rather than the org-form URL GitHub
renders in the address bar (`.../orgs/org/discussions/N`): the org form
still matches, but it misparses (the literal "orgs" is captured as the
owner), so the GraphQL query finds nothing and the row is silently
skipped. Only the repo form yields the `owner/repo` pair the query needs.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SWEEP_PY = REPO_ROOT / "tools" / "scripts" / "sweep_engaged_inbound.py"


def _load_sweep():
    spec = importlib.util.spec_from_file_location("sweep_engaged_inbound", SWEEP_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_url_re_parses_repo_issue_url() -> None:
    m = _load_sweep()._URL_RE.search("https://github.com/owner/repo/issues/12")
    assert m is not None
    assert m.groups() == ("owner", "repo", "issues", "12")


def test_url_re_parses_repo_discussion_url() -> None:
    m = _load_sweep()._URL_RE.search(
        "https://github.com/Mitsubishi-Electric-Asia/melfa_ros2_driver/discussions/25"
    )
    assert m is not None
    assert m.groups() == (
        "Mitsubishi-Electric-Asia",
        "melfa_ros2_driver",
        "discussions",
        "25",
    )


def test_url_re_misparses_bare_org_discussion_url() -> None:
    # The org-form URL GitHub renders (`/orgs/org/discussions/N`) has no repo
    # segment. It still matches, but the optional `orgs/` backtracks and the
    # literal "orgs" is captured as the owner, so the owner/repo pair is wrong
    # ("orgs"/"<org>"). The downstream `repository(owner,name)` GraphQL query
    # then finds nothing and the row is silently skipped. Ledger rows must
    # record the repo-form URL so the check actually runs.
    m = _load_sweep()._URL_RE.search(
        "https://github.com/orgs/Mitsubishi-Electric-Asia/discussions/25"
    )
    assert m is not None
    assert m.groups() == ("orgs", "Mitsubishi-Electric-Asia", "discussions", "25")
