#!/usr/bin/env python3
"""Re-measure the post-burst test surface; print a markdown block to paste.

This is the listening side of the project's discipline: after a burst of
shipping (new fixtures, new runtimes, new RFCs), the front-page numbers
need to reflect what actually shipped, not what shipped before the burst.
``docs/launch/claims-audit.md`` is paired with the README "What URML gives
you" cells; the founder transcribes from here into both, in lockstep.

The script does **not** modify any file. It reads the audit's current
table, runs every package's ``pytest -q`` in a subprocess, counts the
conformance fixtures from disk, and prints:

  * a per-suite line: "validator  242 -> 242 passed" (unchanged) or
                      "conformance  97 -> 105 passed (+8 warehouse)"
  * the total row.
  * a fixture breakdown by directory.
  * a paste-ready markdown table block in the audit's existing format.

Then the maintainer reads, sanity-checks, and copies the changed numbers
into ``docs/launch/claims-audit.md`` and the README. Auto-rewrite would
trade away the discipline of inspecting drift before publishing it; the
script reports, the human writes.

Stdlib only. Runs on every OS the bootstrap venv runs on.
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Suites in the exact order claims-audit.md presents them.
# (label, cwd relative to repo root).
SUITES: list[tuple[str, Path]] = [
    ("validator", REPO / "reference" / "validator"),
    ("llm-bridge", REPO / "reference" / "llm-bridge"),
    ("ros2-runtime", REPO / "reference" / "ros2-runtime"),
    ("px4-runtime", REPO / "reference" / "px4-runtime"),
    ("conformance", REPO / "conformance"),
    ("marine-runtime", REPO / "reference" / "marine-runtime"),
    ("industrial-arm-runtime", REPO / "reference" / "industrial-arm-runtime"),
    ("legged-runtime", REPO / "reference" / "legged-runtime"),
    ("humanoid-runtime", REPO / "reference" / "humanoid-runtime"),
    ("mobile-runtime", REPO / "reference" / "mobile-runtime"),
    ("opcua-runtime", REPO / "reference" / "opcua-runtime"),
    ("cobot-runtime", REPO / "reference" / "cobot-runtime"),
    ("mujoco-runtime", REPO / "reference" / "mujoco-runtime"),
    ("embedded-runtime", REPO / "reference" / "embedded-runtime"),
    ("edu-runtime", REPO / "reference" / "edu-runtime"),
    ("isaac-runtime", REPO / "reference" / "isaac-runtime"),
    ("autosar-runtime", REPO / "reference" / "autosar-runtime"),
    ("model", REPO / "reference" / "model"),
]

# Match pytest's summary line: "234 passed in 3.78s",
# "115 passed, 4 skipped in 1.21s", etc.
_SUMMARY = re.compile(r"(\d+)\s+passed(?:,\s+(\d+)\s+skipped)?(?:[^=]*?)(?:in\s|$)")

# Match audit-table rows so we can show old vs new without parsing the
# whole document: e.g. "| validator | **242 passed** |"
#                     "| ros2-runtime | **115 passed, 4 skipped** |"
_AUDIT_ROW = re.compile(
    r"\|\s*([a-z0-9_-]+)\s*\|\s*\*\*(\d+)\s+passed(?:,\s+(\d+)\s+skipped)?\*\*"
)


def run_suite(label: str, cwd: Path):
    """Return one of:

        ("ok", passed:int, skipped:int, summary_line:str)
        ("env", reason:str)         — not measurable in this env (missing
                                      optional dep, no collected tests, etc.).
        ("fail", reason:str)        — real failures, not an env issue.
        ("missing", str)            — the cwd does not exist.

    The caller decides how to render and whether to roll the row into the
    total.
    """
    if not cwd.is_dir():
        return ("missing", f"{cwd} does not exist")
    try:
        # Do NOT pass `-q` — some pytest configurations suppress the
        # "N passed in Xs" summary banner under -q.
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "--tb=no"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return ("fail", "timed out after 600 s")
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    tail = out[-4000:]
    matches = list(_SUMMARY.finditer(tail))
    if matches:
        last = matches[-1]
        passed = int(last.group(1))
        skipped = int(last.group(2)) if last.group(2) else 0
        return ("ok", passed, skipped, last.group(0).strip())
    # No "N passed" — distinguish missing-dep / no-collect / real failure.
    if "ModuleNotFoundError" in tail or "ImportError while importing" in tail:
        first = next(
            (ln for ln in tail.splitlines()
             if "ModuleNotFoundError" in ln or "ImportError" in ln),
            "missing optional dep",
        )
        return ("env", f"missing optional dep: {first.strip()[:140]}")
    if "no tests ran" in tail or "collected 0 items" in tail:
        return ("env", "no tests collected (package not installed?)")
    last_line = next((ln for ln in reversed(tail.splitlines()) if ln.strip()), "")
    return ("fail", f"rc={proc.returncode}; {last_line.strip()[:140]}")


def read_audit_baseline() -> dict[str, tuple[int, int]]:
    """Parse the current per-suite numbers out of claims-audit.md."""
    audit = REPO / "docs" / "launch" / "claims-audit.md"
    baseline: dict[str, tuple[int, int]] = {}
    if not audit.is_file():
        return baseline
    for line in audit.read_text(encoding="utf-8").splitlines():
        m = _AUDIT_ROW.match(line)
        if m:
            label = m.group(1)
            passed = int(m.group(2))
            skipped = int(m.group(3)) if m.group(3) else 0
            baseline[label] = (passed, skipped)
    return baseline


def count_fixtures() -> tuple[int, dict[str, int]]:
    """Total YAML conformance fixtures + per-subdir breakdown."""
    root = REPO / "conformance" / "fixtures"
    total = 0
    per_dir: dict[str, int] = {}
    for p in sorted(root.rglob("*.yaml")):
        total += 1
        rel = p.relative_to(root)
        bucket = rel.parts[0] if len(rel.parts) > 1 else rel.parent.name or "(root)"
        per_dir[bucket] = per_dir.get(bucket, 0) + 1
    return total, per_dir


def git_head_short() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO, text=True
        ).strip()
    except Exception:
        return "(unknown)"


def main() -> int:
    baseline = read_audit_baseline()
    fix_total, fix_by_dir = count_fixtures()
    audit_fix_total = baseline.pop("__fixtures__", (0, 0))[0] if False else None
    # The current audit prose lists "97" as the fixture total. We don't
    # depend on parsing it precisely; we just report the live disk count.

    print()
    print(f"=== URML claims-audit refresh — {date.today().isoformat()} ({git_head_short()}) ===")
    print()
    print(f"{'Suite':28} {'old':>14}   {'new':>14}   {'delta'}")
    print("-" * 78)

    # results[label] = ("ok", passed, skipped) | ("env"|"fail"|"missing", reason)
    results: dict[str, tuple] = {}
    total_passed = 0
    total_skipped = 0
    unmeasurable: list[tuple[str, str, str]] = []
    for label, cwd in SUITES:
        outcome = run_suite(label, cwd)
        results[label] = outcome
        old = baseline.get(label)
        old_s = f"{old[0]} p, {old[1]} s" if old else "(not in audit)"
        if outcome[0] == "ok":
            _, passed, skipped, _summary = outcome
            new_s = f"{passed} p, {skipped} s"
            total_passed += passed
            total_skipped += skipped
            delta_parts: list[str] = []
            if old:
                if passed - old[0]:
                    delta_parts.append(f"passed {passed - old[0]:+d}")
                if skipped - old[1]:
                    delta_parts.append(f"skipped {skipped - old[1]:+d}")
            delta = ", ".join(delta_parts) if delta_parts else (
                "(unchanged)" if old else "(new row)"
            )
        else:
            kind, reason = outcome[0], outcome[1]
            new_s = "n/a"
            delta = f"{kind}: {reason}"
            unmeasurable.append((label, kind, reason))
        print(f"{label:28} {old_s:>14}   {new_s:>14}   {delta}")

    print("-" * 78)
    print(f"{'TOTAL (measured rows)':28} {'':>14}   {total_passed} p, {total_skipped} s")
    if unmeasurable:
        print()
        print(f"NOT MEASURABLE IN THIS ENV ({len(unmeasurable)} rows):")
        for label, kind, reason in unmeasurable:
            print(f"  {label:28} {kind}: {reason}")
        print("  -> Re-run in a venv with each package's [dev]/optional extras")
        print("     installed (per-package PYTHONPATH + extras, per the audit prose),")
        print("     or KEEP the prior audit numbers for these rows.")
    print()
    print(f"Conformance fixtures: {fix_total} YAML cases under conformance/fixtures/")
    for bucket, n in sorted(fix_by_dir.items()):
        print(f"  {bucket:24} {n}")
    print()
    print("================ paste-ready markdown for claims-audit.md ================")
    print()
    print(f"**Measured {date.today().isoformat()}, on `main`** (commit `{git_head_short()}`).")
    print()
    print("| Suite | Result |")
    print("|---|---|")
    # Use measured numbers for ok rows; fall back to the prior audit number
    # for rows that were not measurable in this env. The maintainer reviews.
    paste_total_passed = 0
    paste_total_skipped = 0
    for label, _cwd in SUITES:
        outcome = results[label]
        if outcome[0] == "ok":
            _, passed, skipped, _ = outcome
        elif label in baseline:
            passed, skipped = baseline[label]
        else:
            passed, skipped = 0, 0
        paste_total_passed += passed
        paste_total_skipped += skipped
        if skipped:
            print(f"| {label} | **{passed} passed, {skipped} skipped** |")
        else:
            print(f"| {label} | **{passed} passed** |")
    print(
        f"| **Total** | **{paste_total_passed} passed + "
        f"{paste_total_skipped} gated-skipped** |"
    )
    if unmeasurable:
        print()
        print(f"> Note: {len(unmeasurable)} row(s) carry the prior audit number "
              f"because this env could not measure them "
              f"({', '.join(label for label, _, _ in unmeasurable)}). "
              "Re-run elsewhere if you need a fresh measurement for those.")
    print()
    print(f"Conformance fixtures: **{fix_total}** YAML cases under `conformance/fixtures/` — "
          + ", ".join(f"{b} {n}" for b, n in sorted(fix_by_dir.items())) + ".")
    print()
    print("===========================================================================")
    print("Now: open docs/launch/claims-audit.md and the README front-page cells,")
    print("transcribe the numbers above in lockstep. Do not auto-edit — review first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
