"""Every adapter in the repository keeps up with the runtime that calls it.

Read from source, so no adapter package, SDK or optional extra is imported:

- An adapter method named after a Protocol method accepts every keyword the
  runtime passes at its call sites. RFC-0586 added ``grasp_type`` to the
  Protocol on 2026-06-14 and no adapter outside ros2-runtime took it, so every
  grasp through them raised TypeError until 2026-09-27.
- A method that forwards to the same method on another adapter passes on every
  keyword it accepts. ``CompositeAdapter`` dropped ``arm`` and ``camera``.
- Only the conformance mock reports a scan as done. A scan is waypoints plus a
  capture at each one, and no adapter here implements that; eleven reported
  success anyway until 2026-09-27.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME = REPO_ROOT / "reference" / "ros2-runtime" / "src" / "urml_ros2_runtime"
SEARCHED = (REPO_ROOT / "reference", REPO_ROOT / "examples", REPO_ROOT / "conformance" / "src")
SKIPPED_DIRS = {"tests", "node_modules", ".venv", "build", "dist"}
# The conformance mock simulates a scan so every hermetic suite can run the scan fixtures.
SCAN_SUCCESS_ALLOWED = {"MockROSAdapter"}


def _protocol_methods() -> set[str]:
    tree = ast.parse((RUNTIME / "substrate" / "base.py").read_text(encoding="utf-8"))
    (protocol,) = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "ROSAdapter"]
    return {f.name for f in protocol.body if isinstance(f, ast.FunctionDef) and not f.name.startswith("_")}


def _runtime_keywords(methods: set[str]) -> dict[str, set[str]]:
    """The keywords the runtime passes to each Protocol method, over every call site outside substrate/."""
    passed: dict[str, set[str]] = defaultdict(set)
    for path in RUNTIME.rglob("*.py"):
        if "substrate" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in methods:
                passed[node.func.attr] |= {k.arg for k in node.keywords if k.arg}
    return passed


def _adapter_methods(methods: set[str]) -> list[tuple[str, str, ast.FunctionDef]]:
    """(file:line, class, method) for every class method named after a Protocol method."""
    found = []
    for base in SEARCHED:
        for path in sorted(base.rglob("*.py")):
            if SKIPPED_DIRS & set(path.relative_to(base).parts):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name != "ROSAdapter"]:
                for f in cls.body:
                    if isinstance(f, ast.FunctionDef) and f.name in methods:
                        found.append((f"{path.relative_to(REPO_ROOT).as_posix()}:{f.lineno}", cls.name, f))
    return found


METHODS = _protocol_methods()
PASSED = _runtime_keywords(METHODS)
ADAPTER_METHODS = _adapter_methods(METHODS)


def test_the_guard_reads_the_adapters_and_the_call_sites() -> None:
    """A guard that finds nothing passes; this pins that it reads what it checks."""
    classes = {cls for _, cls, _ in ADAPTER_METHODS}
    expected = {"PX4Adapter", "CompositeAdapter", "UrRtdeAdapter", "SpotAdapter", "RclpyAdapter", "GoPiGo3Adapter"}
    assert expected <= classes
    assert {"arm", "grasp_type", "target_motion"} <= PASSED["send_manipulation_goal"]
    assert "camera" in PASSED["capture_media"]


def test_every_adapter_accepts_every_keyword_the_runtime_passes() -> None:
    problems = []
    for where, cls, f in ADAPTER_METHODS:
        if f.args.kwarg is not None or f.name not in PASSED:
            continue
        accepted = {a.arg for a in f.args.args + f.args.kwonlyargs}
        missing = sorted(PASSED[f.name] - accepted)
        if missing:
            problems.append(f"{where} {cls}.{f.name} cannot take {missing}")
    assert not problems, (
        "the runtime passes keywords these adapters do not accept, so the call raises TypeError:\n"
        + "\n".join(problems)
    )


def test_forwarding_adapters_pass_every_keyword_on() -> None:
    problems = []
    for where, cls, f in ADAPTER_METHODS:
        accepted = [a.arg for a in f.args.kwonlyargs]
        for node in ast.walk(f):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == f.name):
                continue
            if any(k.arg is None for k in node.keywords):
                continue  # forwards **kwargs whole
            passed = {k.arg for k in node.keywords}
            dropped = [name for name in accepted if name not in passed]
            if dropped:
                problems.append(f"{where} {cls}.{f.name} drops {dropped}")
    assert not problems, "these methods accept keywords they do not pass on:\n" + "\n".join(problems)


def test_only_the_conformance_mock_reports_a_scan_as_done() -> None:
    problems = []
    for where, cls, f in ADAPTER_METHODS:
        if f.name != "run_scan" or cls in SCAN_SUCCESS_ALLOWED:
            continue
        for node in ast.walk(f):
            if (
                isinstance(node, ast.keyword)
                and node.arg == "success"
                and isinstance(node.value, ast.Constant)
                and node.value.value is True
            ):
                problems.append(f"{where} {cls}.run_scan reports success")
    assert not problems, (
        "a scan is waypoints plus a capture at each one; an adapter that does not do both "
        "returns a documented refusal, not success:\n" + "\n".join(problems)
    )
