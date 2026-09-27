"""The URML registry: a public lookup of robots, with the evidence behind each listing.

Each entry is one YAML file, ``registry/entries/<id>.yaml``, with its evidence
under ``registry/evidence/<id>/``. This module holds the entry model and the
checker that keeps entries honest::

    python -m urml_conformance.registry check     # every rule below, every entry
    python -m urml_conformance.registry export    # writes registry/registry.json
    python -m urml_conformance.registry schema    # writes registry/entry.schema.json

``check`` verifies, for each entry:

- the file parses, names no unknown field, and its ``id`` is its file name;
- every repository path it names exists, and every sha256 it pins matches the
  bytes of the file;
- the robot's manifest parses as a URML capability manifest;
- a compatibility claim (the self-reported tier of
  ``spec/conformance/v0.1.0.md`` section 3) points at a
  ``urml.conformance-report/1`` report in which every fixture passed, run with
  the entry's own adapter (not the mock) and this repository's
  urml-conformance version, running every fixture of each claimed profile;
- every validation record replays: the validator, run again on the recorded
  program against the declared inputs, reaches the same verdict with the same
  error codes (``urml_validator.evidence.reverify``);
- the wording: no email address anywhere, and none of the words in
  ``BANNED_WORDS`` in any text a reader sees.

Withdrawn entries stay in the export. They are checked for shape, paths,
digests and wording; their records and reports are not replayed.

A listing records facts and evidence. It grants no mark and says nothing about
fitness for any purpose (``TRADEMARK.md``).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Literal

import yaml
from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, model_validator
from pydantic import ValidationError as PydanticValidationError
from urml_validator import __version__ as _validator_version
from urml_validator.evidence import ValidationRecord, read_records, reverify
from urml_validator.schemas.manifest import CapabilityManifest

from urml_conformance._version import __version__ as _conformance_version
from urml_conformance.fixtures import fixture_paths, fixtures_root, load_fixture
from urml_conformance.report import ConformanceReport

__all__ = [
    "BANNED_WORDS",
    "EXPORT_FORMAT",
    "REGISTRY_VERSION",
    "CheckResult",
    "CheckedEntry",
    "Entry",
    "RecordSummary",
    "check_registry",
    "main",
    "render_export",
    "render_schema",
]

REGISTRY_VERSION: Literal["1"] = "1"
EXPORT_FORMAT = "urml.registry/1"
REPO_URL = "https://github.com/URML-MARS/URML"

ENTRIES_DIR = "registry/entries"
EXPORT_PATH = "registry/registry.json"
SCHEMA_PATH = "registry/entry.schema.json"

# conformance/src/urml_conformance/registry.py: parents[3] is the repository root.
_REPO_ROOT = Path(__file__).resolve().parents[3]

#: Words a listing never uses. TRADEMARK.md reserves "URML-Certified" for a
#: program run outside this repository, and a listing implies no review of
#: the robot by URML. Matched in any case, with their inflections.
BANNED_WORDS = re.compile(r"\b(certif\w*|approv\w*|endors\w*|audit\w*|guarant\w*)\b", re.IGNORECASE)

#: No contact capture (GOVERNANCE.md): an entry names people and projects,
#: never an email address.
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")

_ID = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
_SHA256 = r"^[0-9a-f]{64}$"
_ADAPTER_SPEC = r"^[A-Za-z_][A-Za-z0-9_.]*:[A-Za-z_][A-Za-z0-9_.]*$"
_PROFILE = r"^[a-z][a-z0-9_]*$"
_DISTRIBUTION = r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$"


# ---------------------------------------------------------------------------
# Field types
# ---------------------------------------------------------------------------


def _iso_date(value: Any) -> Any:
    if isinstance(value, dt.date):
        raise ValueError(
            f'write the date as a quoted string, "{value.isoformat()}"; '
            "YAML reads an unquoted date as a date object"
        )
    if not isinstance(value, str):
        raise ValueError('expected an ISO date string such as "2026-09-27"')
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{value!r} is not a date in YYYY-MM-DD form") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{value!r} is not a date in YYYY-MM-DD form")
    return value


def _repo_path(value: str) -> str:
    if (
        not value
        or value != value.strip()
        or "\\" in value
        or value.startswith("/")
        or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value)
        or any(part in ("", ".", "..") for part in value.split("/"))
    ):
        raise ValueError(
            f"{value!r} is not a repository path: use a relative path with forward "
            "slashes, no '..', no trailing slash"
        )
    return value


def _source(value: str) -> str:
    if value.startswith("https://"):
        if not value[len("https://") :] or any(c.isspace() for c in value):
            raise ValueError(f"{value!r} is not a usable https URL")
        return value
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        raise ValueError(f"{value!r}: a source is a repository path or an https:// URL")
    return _repo_path(value)


def _policy_ref(value: str) -> str:
    if value in ("none", "default"):
        return value
    return _repo_path(value)


def _text(value: str) -> str:
    if value != value.strip():
        raise ValueError("remove the leading or trailing whitespace")
    return value


IsoDate = Annotated[
    str,
    BeforeValidator(_iso_date),
    Field(pattern=r"^\d{4}-\d{2}-\d{2}$", description="A quoted ISO date, YYYY-MM-DD."),
]
RepoPath = Annotated[str, AfterValidator(_repo_path)]
Source = Annotated[str, AfterValidator(_source)]
Text = Annotated[str, Field(min_length=1), AfterValidator(_text)]
Sha256 = Annotated[str, Field(pattern=_SHA256, description="Lowercase hex sha256 of the file's bytes.")]
Profile = Annotated[str, Field(pattern=_PROFILE)]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# The entry model
# ---------------------------------------------------------------------------


class Robot(_Model):
    """The robot the entry is about."""

    name: Text
    robot_class: Text = Field(
        alias="class",
        description="What kind of robot, in a few words (for example: multirotor aircraft).",
    )
    maker: Text | None = Field(None, description="Who makes the robot, when there is one maker to name.")
    manifest: RepoPath = Field(..., description="The robot's URML capability manifest, a repository path.")


class Runtime(_Model):
    """The software that runs URML programs on the robot."""

    package: Text = Field(
        ...,
        description="A distribution name (for example urml-ardupilot-runtime), or a repository path for an example.",
    )
    version: Text
    adapter: Annotated[str, Field(pattern=_ADAPTER_SPEC)] | None = Field(
        None,
        description="The runtime's adapter factory as module:attribute, as `--adapter` takes it.",
    )
    substrate: Text = Field(..., description="What the runtime drives: an autopilot, an SDK, a middleware.")


class FileRef(_Model):
    """A repository file pinned by its sha256."""

    path: RepoPath
    sha256: Sha256


class Compatibility(_Model):
    """The self-reported URML-compatible tier (spec/conformance/v0.1.0.md section 3)."""

    tier: Literal["self_reported"]
    profiles: list[Profile] = Field(
        ..., min_length=1, description="The profiles whose fixtures pass with the runtime's own adapter."
    )
    report: FileRef = Field(..., description="The urml.conformance-report/1 JSON report.")


class FieldEvidence(_Model):
    """A recorded run of the robot. Kinds describe what happened; they are not ranked."""

    kind: Literal["hardware_run", "simulation_run"]
    date: IsoDate
    by: Text = Field(..., description="Who ran it: a person or a project, never an email address.")
    summary: Text = Field(..., description="What was run and what happened, as the sources report it.")
    sources: list[Source] = Field(..., min_length=1, description="Repository paths or https URLs a reader can open.")


class RecordInputs(_Model):
    """The inputs every validation record was judged against."""

    manifest: RepoPath
    envelope: RepoPath | None = None
    policy: Annotated[str, AfterValidator(_policy_ref)] = Field(
        "none", description="`none`, `default` (the bundled policy), or a repository path to a policy file."
    )
    rulebooks: list[RepoPath] = Field(default_factory=list)
    default_rulebooks: bool = True


class ValidationRecords(_Model):
    """A file of urml.validation-record/1 lines, pinned and replayable."""

    path: RepoPath
    sha256: Sha256
    summary: Text = Field(..., description="How and when the records were produced, and what they show.")
    inputs: RecordInputs


class Entry(_Model):
    """One registry entry: registry/entries/<id>.yaml."""

    registry_version: Literal["1"]
    id: Annotated[str, Field(pattern=_ID, description="Lowercase words joined by hyphens; the file name.")]
    title: Text
    status: Literal["listed", "withdrawn"]
    listed: IsoDate
    last_verified: IsoDate
    submitted_by: Text = Field(..., description="A person or project name, never an email address.")
    robot: Robot
    runtime: Runtime
    profiles: list[Profile] = Field(..., min_length=1)
    compatibility: Compatibility | None = None
    field_evidence: list[FieldEvidence] = Field(default_factory=list)
    validation_records: ValidationRecords | None = None
    limits: list[Text] = Field(
        ..., min_length=1, description="What the listing does not show. Every entry states at least one limit."
    )

    @model_validator(mode="after")
    def _coherent(self) -> Entry:
        if self.last_verified < self.listed:
            raise ValueError("last_verified is earlier than listed")
        if len(set(self.profiles)) != len(self.profiles):
            raise ValueError("profiles lists a profile twice")
        if self.compatibility is not None:
            unlisted = [p for p in self.compatibility.profiles if p not in self.profiles]
            if unlisted:
                raise ValueError(f"compatibility.profiles {unlisted} are not in the entry's profiles")
            if self.runtime.adapter is None:
                raise ValueError(
                    "a compatibility claim needs runtime.adapter: the report must come from "
                    "the runtime's own adapter"
                )
        if self.validation_records is not None and self.validation_records.inputs.manifest != self.robot.manifest:
            raise ValueError("validation_records.inputs.manifest must be the robot's manifest")
        if self.status == "listed" and not (
            self.compatibility or self.field_evidence or self.validation_records
        ):
            raise ValueError(
                "a listed entry carries evidence: compatibility, field_evidence or validation_records"
            )
        return self


# ---------------------------------------------------------------------------
# Checking
# ---------------------------------------------------------------------------


@dataclass
class RecordSummary:
    """What an entry's validation records hold."""

    count: int
    accepted: int
    refused: int
    codes: dict[str, int]
    warning_codes: dict[str, int]
    replayed: bool


@dataclass
class CheckedEntry:
    """One entry file and what the check found."""

    path: Path
    entry: Entry | None
    problems: list[str] = field(default_factory=list)
    records: RecordSummary | None = None
    report: ConformanceReport | None = None


@dataclass
class CheckResult:
    """Every entry the check read."""

    root: Path
    entries: list[CheckedEntry]
    problems_outside_entries: list[str] = field(default_factory=list)

    @property
    def problems(self) -> list[str]:
        found = list(self.problems_outside_entries)
        for checked in self.entries:
            found.extend(checked.problems)
        return found

    @property
    def ok(self) -> bool:
        return not self.problems


def default_root() -> Path:
    """This checkout's root when the module runs from one, else the working directory."""
    if (_REPO_ROOT / "registry").is_dir():
        return _REPO_ROOT
    return Path.cwd()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(value: Any, location: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield location or "<entry>", value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _strings(item, f"{location}.{key}" if location else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _strings(item, f"{location}[{index}]")


def _reader_text(entry: Entry) -> Iterator[tuple[str, str]]:
    """Every field a reader of the listing sees as prose."""
    yield "title", entry.title
    yield "submitted_by", entry.submitted_by
    yield "robot.name", entry.robot.name
    yield "robot.class", entry.robot.robot_class
    if entry.robot.maker is not None:
        yield "robot.maker", entry.robot.maker
    yield "runtime.substrate", entry.runtime.substrate
    for index, evidence in enumerate(entry.field_evidence):
        yield f"field_evidence[{index}].by", evidence.by
        yield f"field_evidence[{index}].summary", evidence.summary
    if entry.validation_records is not None:
        yield "validation_records.summary", entry.validation_records.summary
    for index, limit in enumerate(entry.limits):
        yield f"limits[{index}]", limit


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _is_mock(spec: str) -> bool:
    module, _, attr = spec.partition(":")
    return attr == "MockROSAdapter" and module.split(".")[0] == "urml_ros2_runtime"


def _pydantic_problems(exc: PydanticValidationError) -> Iterator[str]:
    for error in exc.errors():
        where = ".".join(str(part) for part in error["loc"]) or "<entry>"
        yield f"{where}: {error['msg']}"


class _EntryCheck:
    """The checks for one entry file."""

    def __init__(self, path: Path, root: Path) -> None:
        self.path = path
        self.root = root
        self.rel = path.relative_to(root).as_posix()
        self.result = CheckedEntry(path=path, entry=None)

    def fail(self, message: str) -> None:
        self.result.problems.append(f"{self.rel}: {message}")

    def repo_file(self, rel: str, what: str, *, file_only: bool = False) -> Path | None:
        """The path inside the repository, or None (with a problem) when it is missing."""
        target = self.root / rel
        try:
            target.resolve().relative_to(self.root.resolve())
        except ValueError:
            self.fail(f"{what} {rel!r} points outside the repository")
            return None
        if not target.exists():
            self.fail(f"{what} {rel!r} does not exist")
            return None
        if file_only and not target.is_file():
            self.fail(f"{what} {rel!r} is not a file")
            return None
        return target

    def load_input(self, rel: str, what: str) -> tuple[bool, Any]:
        """Parse a repository YAML file; (False, None) with a problem when it cannot be read."""
        target = self.repo_file(rel, what, file_only=True)
        if target is None:
            return False, None
        try:
            return True, _load_yaml(target)
        except (yaml.YAMLError, OSError, UnicodeDecodeError) as exc:
            self.fail(f"{what} {rel!r} is not readable YAML: {exc}")
            return False, None

    def pinned_file(self, ref_path: str, sha256: str, what: str) -> Path | None:
        target = self.repo_file(ref_path, what, file_only=True)
        if target is None:
            return None
        actual = _file_sha256(target)
        if actual != sha256:
            self.fail(f"{what} {ref_path!r}: sha256 is {actual}, the entry pins {sha256}")
            return None
        return target

    def run(self) -> CheckedEntry:
        try:
            raw = _load_yaml(self.path)
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            self.fail(f"not valid UTF-8 YAML: {exc}")
            return self.result
        if not isinstance(raw, dict):
            self.fail("an entry is a YAML mapping")
            return self.result
        for location, text in _strings(raw):
            if EMAIL.search(text):
                self.fail(f"{location}: no email addresses in an entry (GOVERNANCE.md: no contact capture)")
        try:
            entry = Entry.model_validate(raw)
        except PydanticValidationError as exc:
            for problem in _pydantic_problems(exc):
                self.fail(problem)
            return self.result
        self.result.entry = entry
        if entry.id != self.path.stem:
            self.fail(f"id {entry.id!r} does not match the file name {self.path.name!r}")
        for location, text in _reader_text(entry):
            match = BANNED_WORDS.search(text)
            if match:
                self.fail(
                    f"{location}: {match.group(0)!r} is not used in a listing "
                    "(TRADEMARK.md; see registry/README.md, wording)"
                )
        self.check_manifest(entry)
        for index, evidence in enumerate(entry.field_evidence):
            for source in evidence.sources:
                if not source.startswith("https://"):
                    self.repo_file(source, f"field_evidence[{index}] source")
        self.check_package(entry.runtime.package)
        if entry.compatibility is not None:
            self.check_compatibility(entry)
        if entry.validation_records is not None:
            self.check_records(entry)
        return self.result

    def check_package(self, package: str) -> None:
        """A distribution name, or the repository path of an example adapter."""
        if "/" not in package:
            if not re.match(_DISTRIBUTION, package):
                self.fail(f"runtime.package {package!r} is neither a distribution name nor a repository path")
            return
        try:
            self.repo_file(_repo_path(package), "runtime.package")
        except ValueError as exc:
            self.fail(f"runtime.package: {exc}")

    def check_manifest(self, entry: Entry) -> None:
        loaded, manifest = self.load_input(entry.robot.manifest, "robot.manifest")
        if not loaded:
            return
        try:
            CapabilityManifest.model_validate(manifest)
        except PydanticValidationError as exc:
            first = str(exc).splitlines()[:3]
            self.fail(f"robot.manifest does not parse as a URML capability manifest: {' '.join(first)}")

    def check_compatibility(self, entry: Entry) -> None:
        assert entry.compatibility is not None
        claim = entry.compatibility
        target = self.pinned_file(claim.report.path, claim.report.sha256, "compatibility.report")
        if target is None:
            return
        try:
            report = ConformanceReport.model_validate_json(target.read_bytes())
        except PydanticValidationError as exc:
            self.fail(f"compatibility.report is not a urml.conformance-report/1 report: {exc.errors()[0]['msg']}")
            return
        self.result.report = report
        if entry.status != "listed":
            return
        if not report.results:
            self.fail("compatibility.report holds no results")
            return
        if not report.all_passed:
            self.fail(
                f"compatibility.report: all_passed is false ({report.failed} of "
                f"{len(report.results)} fixtures failed)"
            )
        if report.adapter is None:
            self.fail(
                "compatibility.report does not name the adapter it ran against; produce it "
                "with `urml conformance run --adapter ... --output`"
            )
        elif _is_mock(report.adapter):
            self.fail(
                "compatibility.report was run against the mock adapter; a self-report "
                "runs the suite with the runtime's own adapter (--adapter)"
            )
        elif report.adapter != entry.runtime.adapter:
            self.fail(
                f"compatibility.report was run with {report.adapter!r}, not the entry's "
                f"runtime.adapter {entry.runtime.adapter!r}"
            )
        if report.urml_conformance_version != _conformance_version:
            self.fail(
                f"compatibility.report comes from urml-conformance "
                f"{report.urml_conformance_version}; re-run it with {_conformance_version}"
            )
        if report.fixtures_sha256 is None or not re.match(_SHA256, report.fixtures_sha256):
            self.fail("compatibility.report does not record the sha256 of its fixture set")
        if report.fixture_count != len(report.results):
            self.fail("compatibility.report: fixture_count does not match its results")
        suite = profile_fixtures(self.root)
        ran = {result.name for result in report.results}
        for profile in claim.profiles:
            expected = suite.get(profile, set())
            if not expected:
                self.fail(f"the conformance suite has no {profile!r} fixture, so a claim for it cannot be checked")
                continue
            missing = sorted(expected - ran)
            if missing:
                shown = ", ".join(missing[:5]) + (", ..." if len(missing) > 5 else "")
                self.fail(
                    f"compatibility.report does not run every {profile!r} fixture: "
                    f"{len(missing)} of {len(expected)} are missing ({shown}). A claim covers "
                    f"the whole profile: run `urml conformance run --adapter ... --profile "
                    f"{profile} --output ...`"
                )

    def check_records(self, entry: Entry) -> None:
        assert entry.validation_records is not None
        block = entry.validation_records
        target = self.pinned_file(block.path, block.sha256, "validation_records")
        inputs = block.inputs
        what = "validation_records.inputs"
        readable = True
        loaded, manifest = self.load_input(inputs.manifest, f"{what}.manifest")
        readable &= loaded
        envelope: Any = None
        if inputs.envelope is not None:
            loaded, envelope = self.load_input(inputs.envelope, f"{what}.envelope")
            readable &= loaded
        policy: Any = None if inputs.policy == "none" else "DEFAULT"
        if inputs.policy not in ("none", "default"):
            loaded, policy = self.load_input(inputs.policy, f"{what}.policy")
            readable &= loaded
        rulebooks: list[Any] = []
        for rel in inputs.rulebooks:
            loaded, rulebook = self.load_input(rel, f"{what}.rulebooks")
            readable &= loaded
            rulebooks.append(rulebook)
        if target is None:
            return
        try:
            records = read_records(target)
        except ValueError as exc:
            self.fail(f"validation_records: {exc}")
            return
        if not records:
            self.fail("validation_records holds no records")
            return
        self.result.records = _summarize(records, replayed=False)
        if entry.status != "listed" or not readable:
            return
        base_dir = (self.root / inputs.manifest).parent
        replayed = True
        for number, record in enumerate(records, start=1):
            label = f"validation_records record {number}"
            if record.default_rulebooks != inputs.default_rulebooks:
                self.fail(
                    f"{label}: default_rulebooks is {record.default_rulebooks}, "
                    f"the inputs say {inputs.default_rulebooks}"
                )
                replayed = False
                continue
            stray = [p for p in record.profiles if p not in entry.profiles]
            if stray:
                self.fail(f"{label}: judged with profiles {stray} that the entry does not list")
            try:
                check = reverify(
                    record,
                    manifest=manifest,
                    envelope=envelope,
                    policy=policy,
                    rulebooks=rulebooks,
                    manifest_base_dir=base_dir,
                )
            except Exception as exc:  # a malformed input must not stop the other entries
                replayed = False
                self.fail(f"{label} could not be replayed: {type(exc).__name__}: {exc}")
                continue
            if not check.reproduced:
                replayed = False
                self.fail(f"{label} does not reproduce: {'; '.join(check.problems)}")
        self.result.records = _summarize(records, replayed=replayed)


def _summarize(records: list[ValidationRecord], *, replayed: bool) -> RecordSummary:
    codes: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    for record in records:
        codes.update(set(record.codes))
        warnings.update(set(record.warning_codes))
    return RecordSummary(
        count=len(records),
        accepted=sum(1 for r in records if r.verdict == "accepted"),
        refused=sum(1 for r in records if r.verdict == "refused"),
        codes=dict(sorted(codes.items())),
        warning_codes=dict(sorted(warnings.items())),
        replayed=replayed,
    )


def profile_fixtures(root: Path) -> dict[str, set[str]]:
    """Every fixture name in the suite, by each profile the fixture lists.

    A compatibility claim for a profile covers all of them, wherever they live
    in the suite (a drone fixture can sit under `fleet/` or `rulebook/`).
    """
    base = root / "conformance" / "fixtures"
    if not base.is_dir():
        base = fixtures_root()
    by_profile: dict[str, set[str]] = {}
    for path in fixture_paths(base):
        case = load_fixture(path)
        for profile in case.profiles:
            by_profile.setdefault(profile, set()).add(case.name)
    return by_profile


def check_registry(root: Path | None = None) -> CheckResult:
    """Check every entry under ``registry/entries/``."""
    base = (root or default_root()).resolve()
    entries_dir = base / ENTRIES_DIR
    result = CheckResult(root=base, entries=[])
    if not entries_dir.is_dir():
        result.problems_outside_entries.append(f"{ENTRIES_DIR}: no such directory under {base}")
        return result
    for path in sorted(entries_dir.iterdir(), key=lambda p: p.name):
        if path.is_dir():
            result.problems_outside_entries.append(f"{ENTRIES_DIR}/{path.name}: entries are files, not folders")
            continue
        if path.suffix != ".yaml":
            result.problems_outside_entries.append(
                f"{ENTRIES_DIR}/{path.name}: an entry is a .yaml file named after its id"
            )
            continue
        result.entries.append(_EntryCheck(path, base).run())
    return result


# ---------------------------------------------------------------------------
# Export and schema
# ---------------------------------------------------------------------------


class RegistryCheckError(Exception):
    """The registry has problems, so it cannot be exported."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = problems


def _url(root: Path, rel: str) -> str:
    kind = "tree" if (root / rel).is_dir() else "blob"
    return f"{REPO_URL}/{kind}/main/{rel}"


def _source_url(root: Path, source: str) -> str:
    return source if source.startswith("https://") else _url(root, source)


def _export_entry(root: Path, checked: CheckedEntry) -> dict[str, Any]:
    entry = checked.entry
    assert entry is not None
    compatibility: dict[str, Any] | None = None
    if entry.compatibility is not None:
        report = checked.report
        compatibility = {
            "tier": entry.compatibility.tier,
            "profiles": list(entry.compatibility.profiles),
            # How much of the suite the claim rests on, as the report records it.
            "fixtures_run": report.fixture_count if report is not None else None,
            "filter": report.filter if report is not None else None,
            "report_url": _url(root, entry.compatibility.report.path),
        }
    records: dict[str, Any] | None = None
    if entry.validation_records is not None and checked.records is not None:
        summary = checked.records
        records = {
            "count": summary.count,
            "accepted": summary.accepted,
            "refused": summary.refused,
            "codes": summary.codes,
            "warning_codes": summary.warning_codes,
            "summary": entry.validation_records.summary,
            "url": _url(root, entry.validation_records.path),
            "reverified_with": f"urml-validator {_validator_version}" if summary.replayed else None,
        }
    return {
        "id": entry.id,
        "title": entry.title,
        "status": entry.status,
        "listed": entry.listed,
        "last_verified": entry.last_verified,
        "submitted_by": entry.submitted_by,
        "robot": {
            "name": entry.robot.name,
            "class": entry.robot.robot_class,
            "maker": entry.robot.maker,
            "manifest_url": _url(root, entry.robot.manifest),
        },
        "runtime": {
            "package": entry.runtime.package,
            "version": entry.runtime.version,
            "adapter": entry.runtime.adapter,
            "substrate": entry.runtime.substrate,
        },
        "profiles": list(entry.profiles),
        "compatibility": compatibility,
        "field_evidence": [
            {
                "kind": evidence.kind,
                "date": evidence.date,
                "by": evidence.by,
                "summary": evidence.summary,
                "sources": [_source_url(root, source) for source in evidence.sources],
            }
            for evidence in entry.field_evidence
        ],
        "validation_records": records,
        "limits": list(entry.limits),
        "entry_url": _url(root, f"{ENTRIES_DIR}/{entry.id}.yaml"),
    }


def render_export(root: Path | None = None) -> str:
    """``registry/registry.json`` as it should read: deterministic, sorted by id, no timestamps.

    Runs the full check first; raises ``RegistryCheckError`` when it finds problems.
    """
    result = check_registry(root)
    if not result.ok:
        raise RegistryCheckError(result.problems)
    checked = sorted(
        (c for c in result.entries if c.entry is not None),
        key=lambda c: c.entry.id if c.entry is not None else "",
    )
    document = {
        "format": EXPORT_FORMAT,
        "entries": [_export_entry(result.root, c) for c in checked],
    }
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def render_schema() -> str:
    """``registry/entry.schema.json``: the JSON Schema of an entry file."""
    schema = Entry.model_json_schema(by_alias=True)
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$comment"] = (
        "Generated from urml_conformance.registry.Entry by "
        "`python -m urml_conformance.registry schema`. Do not edit by hand."
    )
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # LF on every platform, like every text file in the repository.
    path.write_text(text, encoding="utf-8", newline="\n")


def _print_problems(problems: list[str]) -> None:
    for problem in problems:
        print(f"  {problem}", file=sys.stderr)
    print(f"{len(problems)} problem(s) found", file=sys.stderr)


def _cmd_check(root: Path) -> int:
    result = check_registry(root)
    for checked in result.entries:
        if checked.entry is None:
            continue
        line = f"  {checked.entry.id}: {checked.entry.status}"
        if checked.records is not None:
            verb = "replayed" if checked.records.replayed else "read, not replayed"
            line += (
                f", {checked.records.count} validation records {verb} "
                f"({checked.records.accepted} accepted, {checked.records.refused} refused)"
            )
        print(line)
    if not result.ok:
        _print_problems(result.problems)
        return 1
    count = len(result.entries)
    noun = "entry" if count == 1 else "entries"
    print(f"registry check: {count} {noun}, no problems (urml-validator {_validator_version})")
    return 0


def _cmd_export(root: Path, output: Path | None) -> int:
    try:
        text = render_export(root)
    except RegistryCheckError as exc:
        _print_problems(exc.problems)
        print("not exported: fix the problems above first", file=sys.stderr)
        return 1
    target = output or root / EXPORT_PATH
    _write(target, text)
    print(f"wrote {target}")
    return 0


def _cmd_schema(root: Path, output: Path | None) -> int:
    target = output or root / SCHEMA_PATH
    _write(target, render_schema())
    print(f"wrote {target}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m urml_conformance.registry",
        description="Check, export, and describe the URML registry (registry/README.md).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="The repository root that holds registry/ (default: this checkout).",
    )
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    commands.add_parser("check", help="Check every entry: paths, digests, reports, record replays, wording.")
    p_export = commands.add_parser("export", help="Check, then write registry/registry.json.")
    p_export.add_argument("--output", type=Path, default=None, help="Write here instead.")
    p_schema = commands.add_parser("schema", help="Write registry/entry.schema.json from the entry model.")
    p_schema.add_argument("--output", type=Path, default=None, help="Write here instead.")
    args = parser.parse_args(argv)
    root = (args.root or default_root()).resolve()
    if args.command == "check":
        return _cmd_check(root)
    if args.command == "export":
        return _cmd_export(root, args.output)
    return _cmd_schema(root, args.output)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
