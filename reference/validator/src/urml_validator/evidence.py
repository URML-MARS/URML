"""Validation records: an opt-in, local evidence log of what the gate decided.

A validation record captures one verdict of the URML validator, `accepted` or
`refused`, together with a content digest of every input it judged: the
program, the manifest, the envelope, the compliance policy and the rulebooks.
Records are appended, one JSON object per line, to a file the operator names.

Why keep them. A refused program is the evidence that the gate held: what a
model or a person asked the robot to do, which declared limit it broke, and
which validator version said no. An accepted program is the other half of the
same ledger. The URML registry (`registry/`) re-validates committed records to
show that a listed robot's recorded verdicts still reproduce.

Privacy. Nothing is recorded unless the operator turns the log on (the CLI's
`--evidence-log PATH`, `URMLRuntime(evidence_log=...)`, the MCP server's
`URML_MCP_EVIDENCE_LOG`, or the ROS action server's `evidence_log` parameter).
The log is a local file. It holds the program and, for `urml run` and
`urml translate`, the natural-language request, because those are the command
being judged. It holds no user, host or network identifier, and nothing is
sent anywhere. See `docs/evidence/validation-records.md`.

Digests are `sha256:` over canonical JSON (sorted keys, no whitespace), so the
same content hashes the same whether it came from a YAML file, a JSON file or
memory, and whatever the file's formatting.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from urml_validator._version import __version__
from urml_validator.errors import ValidationResult

__all__ = [
    "RECORD_FORMAT",
    "Reverification",
    "ValidationRecord",
    "append_record",
    "build_record",
    "canonical_json",
    "content_digest",
    "read_records",
    "reverify",
]

#: The format tag every record carries. A reader rejects any other value.
RECORD_FORMAT: Literal["urml.validation-record/1"] = "urml.validation-record/1"

Surface = Literal[
    "api", "validate", "execute", "run", "translate", "runtime", "mcp", "action_server"
]
Stage = Literal["validation", "revalidation", "bridge"]
Verdict = Literal["accepted", "refused"]


def canonical_json(value: Any) -> str:
    """Sorted keys, no whitespace, UTF-8 characters kept: the form every digest uses."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _plain(value: Any) -> Any:
    """A JSON-ready form of a dict or a pydantic model, as the caller supplied it."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", exclude_unset=True, by_alias=True)
    return json.loads(json.dumps(value, default=str))


def content_digest(value: Any) -> str:
    """`sha256:<hex>` of the canonical JSON of a dict, list or pydantic model."""
    data = canonical_json(_plain(value)).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


class RulebookRef(BaseModel):
    """One caller-supplied rulebook, by id and content digest."""

    model_config = ConfigDict(extra="forbid")

    rulebook_id: str | None = None
    digest: str


class ToolInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Literal["urml-validator"] = "urml-validator"
    version: str


class ValidationRecord(BaseModel):
    """One verdict of the validator, with digests of everything it judged."""

    model_config = ConfigDict(extra="forbid")

    format: Literal["urml.validation-record/1"] = RECORD_FORMAT
    record_id: str = Field(
        ...,
        description=(
            "sha256 over the record's identity: verdict, input digests, profiles, "
            "codes and tool version. Two runs that judged the same inputs the same "
            "way share an id; recorded_at is not part of it."
        ),
    )
    recorded_at: str = Field(..., description="UTC time the verdict was recorded, to the second.")
    tool: ToolInfo
    surface: Surface = Field(..., description="Which entry point produced the verdict.")
    stage: Stage = Field(
        ...,
        description=(
            "`validation`: the first check. `revalidation`: the runtime's own check "
            "before its first adapter call. `bridge`: the LLM bridge's final verdict."
        ),
    )
    verdict: Verdict
    robot_id: str | None = None
    program: dict[str, Any] | None = Field(
        None,
        description="The program as judged. None when the bridge produced no program.",
    )
    program_digest: str | None = None
    manifest_digest: str
    envelope_digest: str | None = None
    policy: str = Field(
        ..., description="`none`, `default` (the bundled policy), or the content digest of a custom policy."
    )
    rulebooks: list[RulebookRef] = Field(default_factory=list)
    default_rulebooks: bool = True
    as_of: str | None = Field(None, description="The date rulebook effective dates were judged against.")
    profiles: list[str] = Field(default_factory=list)
    codes: list[str] = Field(default_factory=list, description="Error codes, in emission order.")
    warning_codes: list[str] = Field(default_factory=list)
    result: dict[str, Any] = Field(..., description="The ValidationResult, as `urml validate --json` prints it.")
    request: str | None = Field(None, description="The natural-language request, for `run` and `translate`.")
    attempts: int | None = Field(None, description="Bridge attempts, for `run` and `translate`.")
    attempt_codes: list[list[str]] | None = Field(
        None, description="Error codes of each bridge attempt, in order."
    )


def _policy_label(policy: Any) -> str:
    if policy is None:
        return "none"
    if isinstance(policy, str) and policy == "DEFAULT":
        return "default"
    return content_digest(policy)


def _rulebook_refs(rulebooks: Sequence[Any]) -> list[RulebookRef]:
    refs: list[RulebookRef] = []
    for rulebook in rulebooks:
        plain = _plain(rulebook)
        rulebook_id = plain.get("rulebook_id") if isinstance(plain, Mapping) else None
        refs.append(RulebookRef(rulebook_id=rulebook_id, digest=content_digest(plain)))
    return refs


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_record(
    *,
    surface: Surface,
    stage: Stage,
    result: ValidationResult,
    program: Mapping[str, Any] | BaseModel | None,
    manifest: Mapping[str, Any] | BaseModel,
    envelope: Mapping[str, Any] | BaseModel | None = None,
    policy: Any = "DEFAULT",
    rulebooks: Sequence[Any] = (),
    default_rulebooks: bool = True,
    as_of: date | None = None,
    profiles: Sequence[str] = (),
    request: str | None = None,
    attempts: int | None = None,
    attempt_codes: Sequence[Sequence[str]] | None = None,
    recorded_at: str | None = None,
) -> ValidationRecord:
    """Build the record for one verdict. Pure: it reads nothing and writes nothing."""
    program_plain: dict[str, Any] | None = _plain(program) if program is not None else None
    manifest_plain = _plain(manifest)
    robot_id = manifest_plain.get("robot_id") if isinstance(manifest_plain, Mapping) else None
    codes = [str(e.code) for e in result.errors]
    verdict: Verdict = "accepted" if result.accepted else "refused"
    program_digest = content_digest(program_plain) if program_plain is not None else None
    manifest_digest = content_digest(manifest_plain)
    envelope_digest = content_digest(envelope) if envelope is not None else None
    policy_label = _policy_label(policy)
    rulebook_refs = _rulebook_refs(rulebooks)
    as_of_text = as_of.isoformat() if as_of is not None else None
    identity = {
        "format": RECORD_FORMAT,
        "verdict": verdict,
        "program_digest": program_digest,
        "manifest_digest": manifest_digest,
        "envelope_digest": envelope_digest,
        "policy": policy_label,
        "rulebooks": [ref.model_dump() for ref in rulebook_refs],
        "default_rulebooks": default_rulebooks,
        "as_of": as_of_text,
        "profiles": list(profiles),
        "codes": codes,
        "tool_version": __version__,
    }
    return ValidationRecord(
        record_id=content_digest(identity),
        recorded_at=recorded_at or _now(),
        tool=ToolInfo(version=__version__),
        surface=surface,
        stage=stage,
        verdict=verdict,
        robot_id=robot_id if isinstance(robot_id, str) else None,
        program=program_plain,
        program_digest=program_digest,
        manifest_digest=manifest_digest,
        envelope_digest=envelope_digest,
        policy=policy_label,
        rulebooks=rulebook_refs,
        default_rulebooks=default_rulebooks,
        as_of=as_of_text,
        profiles=list(profiles),
        codes=codes,
        warning_codes=[str(w.code) for w in result.warnings],
        result=result.model_dump(mode="json"),
        request=request,
        attempts=attempts,
        attempt_codes=[list(c) for c in attempt_codes] if attempt_codes is not None else None,
    )


def append_record(path: Path | str, record: ValidationRecord) -> None:
    """Append one record as one line of canonical JSON. Creates the file and its folder."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    line = canonical_json(record.model_dump(mode="json")) + "\n"
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)


def read_records(path: Path | str) -> list[ValidationRecord]:
    """Every record in a log, in order. A malformed line raises ValueError naming it."""
    records: list[ValidationRecord] = []
    text = Path(path).read_text(encoding="utf-8")
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(ValidationRecord.model_validate(json.loads(line)))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"{path}:{number}: not a {RECORD_FORMAT} record: {exc}") from exc
    return records


class Reverification(BaseModel):
    """The outcome of re-running the validator on a recorded program."""

    model_config = ConfigDict(extra="forbid")

    record_id: str
    reproduced: bool
    problems: list[str] = Field(default_factory=list)


def reverify(
    record: ValidationRecord,
    *,
    manifest: Mapping[str, Any] | BaseModel,
    envelope: Mapping[str, Any] | BaseModel | None = None,
    policy: Any = "DEFAULT",
    rulebooks: Sequence[Any] = (),
    manifest_base_dir: Path | None = None,
) -> Reverification:
    """Re-validate a recorded program and compare the verdict and error codes.

    The caller supplies the inputs; each must hash to the digest the record
    carries, so a record can only be re-verified against what it judged.
    A record with no program (the bridge produced none) cannot be replayed.
    """
    from urml_validator.validator import validate

    problems: list[str] = []
    if record.program is None:
        return Reverification(
            record_id=record.record_id,
            reproduced=False,
            problems=["the record has no program to replay"],
        )
    if content_digest(record.program) != record.program_digest:
        problems.append("the program does not match its recorded digest")
    if content_digest(manifest) != record.manifest_digest:
        problems.append("the manifest supplied does not match the recorded manifest digest")
    envelope_digest = content_digest(envelope) if envelope is not None else None
    if envelope_digest != record.envelope_digest:
        problems.append("the envelope supplied does not match the recorded envelope digest")
    if _policy_label(policy) != record.policy:
        problems.append("the policy supplied does not match the recorded policy")
    if [ref.digest for ref in _rulebook_refs(rulebooks)] != [ref.digest for ref in record.rulebooks]:
        problems.append("the rulebooks supplied do not match the recorded rulebooks")
    if problems:
        return Reverification(record_id=record.record_id, reproduced=False, problems=problems)

    result = validate(
        record.program,
        _plain(manifest),
        _plain(envelope) if envelope is not None else None,
        profiles=tuple(record.profiles),
        policy=policy,
        manifest_base_dir=manifest_base_dir,
        rulebooks=[_plain(r) for r in rulebooks],
        default_rulebooks=record.default_rulebooks,
        as_of=date.fromisoformat(record.as_of) if record.as_of else None,
    )
    verdict = "accepted" if result.accepted else "refused"
    if verdict != record.verdict:
        problems.append(f"verdict: recorded {record.verdict}, now {verdict}")
    codes = [str(e.code) for e in result.errors]
    if codes != record.codes:
        problems.append(f"codes: recorded {record.codes}, now {codes}")
    return Reverification(record_id=record.record_id, reproduced=not problems, problems=problems)
