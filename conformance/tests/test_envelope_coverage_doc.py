"""Keep docs/safety/envelope-coverage.md honest.

The page is the per-primitive matrix of Pass-3 envelope checks: what the
Layer-2 spec requires, what the validator enforces (each code with a pinning
conformance fixture), and what it cannot check statically. These tests fail
when:

- a primitive of the program schema has no row;
- an enforced cell names a fixture that does not exist, is not a rejected
  case, does not list the code, or does not use the primitive;
- the validator, run on that fixture exactly as the conformance runner runs
  it, does not emit the code from a step of that primitive;
- a deferred cell cites neither an RFC nor a spec line;
- a spec citation points at a missing file or past its end, or a row's
  "spec requires" cell does not point at the primitive's check paragraph.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from urml_validator import ErrorCode, validate
from urml_validator.schemas.composition import Step
from urml_validator.schemas.program import URMLProgram
from urml_validator.validator import walk_program

from urml_conformance.fixtures import (
    load_fixture,
    manifest_base_dir,
    resolve_envelope,
    resolve_manifest,
    resolve_policy,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC = REPO_ROOT / "docs" / "safety" / "envelope-coverage.md"
FIXTURES = REPO_ROOT / "conformance" / "fixtures"
RFCS = REPO_ROOT / "docs" / "rfcs"

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_CODE = re.compile(r"`([a-z]+\.[a-z_]+)`")
_SPEC_CITE = re.compile(r"\[(?:spec|[a-z]+ profile) L(\d+)(?:-(\d+))?\]\(([^)]+)\)")
_RFC = re.compile(r"RFC-(\d{4})")


def _rows(heading: str) -> list[list[str]]:
    """The table rows (as stripped cells) under a `## heading` section."""
    text = DOC.read_text(encoding="utf-8")
    marker = f"\n## {heading}\n"
    assert marker in text, f"missing section {heading!r}"
    section = text.split(marker, 1)[1].split("\n## ", 1)[0]
    return [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in section.splitlines()
        if line.startswith("| `")
    ]


def _entries(cell: str) -> list[str]:
    return [] if cell == "none" else [e.strip() for e in cell.split("<br>") if e.strip()]


def _matrix() -> list[list[str]]:
    return _rows("The matrix")


def _pins(rows: list[list[str]], primitive_of: str) -> list[tuple[str, str, str]]:
    """(primitive, code, fixture link) for every enforced entry in a table."""
    pins: list[tuple[str, str, str]] = []
    for row in rows:
        name = row[0].strip("`")
        primitive = name.split(".", 1)[0] if primitive_of == "argument" else name
        enforced = row[2] if primitive_of == "primitive" else f"{row[1]}: {row[2]}"
        for entry in _entries(enforced):
            codes = _CODE.findall(entry)
            links = [target for _, target in _LINK.findall(entry)]
            assert codes and links, f"{name}: enforced entry needs a code and a fixture: {entry!r}"
            pins.extend((primitive, codes[0], link) for link in links)
    return pins


def _all_pins() -> list[tuple[str, str, str]]:
    return _pins(_matrix(), "primitive") + _pins(_rows("Named targets resolve first"), "argument")


def _spec_cites(text: str) -> list[tuple[Path, int, int]]:
    out = []
    for first, last, target in _SPEC_CITE.findall(text):
        start = int(first)
        out.append(((DOC.parent / target).resolve(), start, int(last) if last else start))
    return out


def test_every_primitive_of_the_program_schema_has_one_row() -> None:
    primitives = [row[0].strip("`") for row in _matrix()]
    assert len(primitives) == len(set(primitives)), "a primitive appears twice"
    assert set(primitives) == set(Step.model_fields), (
        f"missing: {sorted(set(Step.model_fields) - set(primitives))}, "
        f"unknown: {sorted(set(primitives) - set(Step.model_fields))}"
    )


def test_every_row_has_four_cells() -> None:
    for row in _matrix():
        assert len(row) == 4, row


def test_every_spec_cell_points_at_the_primitive_check_paragraph() -> None:
    for row in _matrix():
        cites = _spec_cites(row[1])
        assert cites, f"{row[0]}: the spec cell cites no spec line"
        path, first, last = cites[0]
        lines = path.read_text(encoding="utf-8").splitlines()
        span = " ".join(lines[first - 1 : last]).lower()
        assert "safety-envelope checks" in span or "capabilit" in span, (
            f"{row[0]}: {path.name} L{first}-{last} is not the check paragraph"
        )


@pytest.mark.parametrize("pin", _all_pins(), ids=lambda p: f"{p[0]}:{p[1]}:{Path(p[2]).stem}")
def test_enforced_cells_are_pinned_by_a_rejected_fixture(pin: tuple[str, str, str]) -> None:
    primitive, code, link = pin
    ErrorCode(code)  # an existing, stable code
    path = (DOC.parent / link).resolve()
    assert path.is_file(), f"missing fixture {link}"
    assert FIXTURES in path.parents, f"{link} is not a conformance fixture"
    case = load_fixture(path)
    assert not case.expected_validation.accepted, f"{link} is not a rejected case"
    assert code in case.expected_validation.error_codes, f"{link} does not list {code}"
    program = URMLProgram.model_validate(case.program)
    assert primitive in {step.primitive_name for _, step in walk_program(program)}, (
        f"{link} does not use {primitive}"
    )
    assert case.manifest is not None
    result = validate(
        case.program,
        resolve_manifest(case.manifest),
        resolve_envelope(case.envelope) if case.envelope else None,
        profiles=tuple(case.profiles),
        policy=resolve_policy(case.policy),
        manifest_base_dir=manifest_base_dir(case.manifest),
    )
    emitted = {(e.code.value, e.primitive) for e in result.errors}
    assert (code, primitive) in emitted, f"{link}: {code} is not emitted by {primitive}; got {emitted}"


def test_every_deferred_entry_cites_an_rfc_or_a_spec_line() -> None:
    for row in _matrix():
        for entry in _entries(row[3]):
            rfcs = _RFC.findall(entry)
            cites = _spec_cites(entry)
            assert rfcs or cites, f"{row[0]}: deferred entry cites nothing: {entry!r}"
            for number in rfcs:
                assert list(RFCS.glob(f"{number}-*.md")), f"{row[0]}: RFC-{number} does not exist"


def test_every_spec_citation_resolves() -> None:
    text = DOC.read_text(encoding="utf-8")
    cites = _spec_cites(text)
    assert cites
    for path, first, last in cites:
        assert path.is_file(), f"missing spec file {path}"
        assert (REPO_ROOT / "spec") in path.parents, f"{path} is not under spec/"
        count = len(path.read_text(encoding="utf-8").splitlines())
        assert 1 <= first <= last <= count, f"{path.name} L{first}-{last} is out of range"
