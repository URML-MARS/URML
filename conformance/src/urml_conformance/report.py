"""Conformance report: pass/fail per case, and what was run against which adapter.

A report serializes as ``urml.conformance-report/1``. Alongside the per-case
``results`` it names the adapter the suite ran against, the urml-conformance
and urml-validator versions, the fixture set (a count and a sha256 over the
fixture files) and the ``--filter``, if one was given. ``all_passed``,
``passed`` and ``failed`` are computed from ``results`` and written out with
them; a report read back must agree with its own results.

Every field added for the report format is optional, so a report written
before it (``{"results": [...]}``) still parses.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    computed_field,
    model_serializer,
    model_validator,
)

#: The format tag a report carries.
REPORT_FORMAT: Literal["urml.conformance-report/1"] = "urml.conformance-report/1"

#: The adapter a report names when the suite ran against the default hermetic
#: mock (no ``--adapter``). Passing it to ``--adapter`` reproduces the run.
DEFAULT_ADAPTER = "urml_ros2_runtime:MockROSAdapter"

# Computed from `results` on output; checked against `results` on input.
_COMPUTED_FIELDS = ("all_passed", "passed", "failed")


class CaseResult(BaseModel):
    """The result of running one fixture."""

    model_config = ConfigDict(extra="forbid")

    name: str
    passed: bool
    diagnostics: list[str] = Field(
        default_factory=list,
        description="Human-readable mismatch details when `passed` is False.",
    )

    def render(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        if not self.diagnostics:
            return f"[{status}] {self.name}"
        lines = [f"[{status}] {self.name}"]
        for diag in self.diagnostics:
            lines.append(f"  - {diag}")
        return "\n".join(lines)


def _outcome(result: Any) -> Any:
    if isinstance(result, dict):
        return result.get("passed")
    return getattr(result, "passed", None)


class ConformanceReport(BaseModel):
    """A report covering an entire fixture run."""

    model_config = ConfigDict(extra="forbid")

    format: Literal["urml.conformance-report/1"] = REPORT_FORMAT
    adapter: str | None = Field(
        None,
        description=(
            "The adapter factory the suite ran against, as a `module:attribute` "
            f"spec. `{DEFAULT_ADAPTER}` is the default hermetic mock."
        ),
    )
    urml_conformance_version: str | None = None
    urml_validator_version: str | None = None
    fixture_count: int | None = Field(None, description="How many fixtures ran.")
    fixtures_sha256: str | None = Field(
        None,
        description=(
            "sha256 over the fixture files that ran: one `<sha256 of the file>  "
            "<path relative to the fixtures directory>` line per file, sorted by "
            "path. Null when the runner was handed parsed cases instead of files."
        ),
    )
    filter: str | None = Field(None, description="The --filter substring, if one was given.")
    profiles: list[str] | None = Field(
        None,
        description=(
            "The --profile selection, if one was given: every fixture that lists any "
            "of these profiles ran."
        ),
    )
    results: list[CaseResult] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _computed_fields_agree(cls, data: Any) -> Any:
        """Read a serialized report: its computed fields must match its results."""
        if not isinstance(data, dict) or not any(key in data for key in _COMPUTED_FIELDS):
            return data
        stated = {key: data[key] for key in _COMPUTED_FIELDS if key in data}
        outcomes = [_outcome(result) for result in data.get("results") or []]
        actual = {
            "all_passed": all(outcome is True for outcome in outcomes),
            "passed": sum(1 for outcome in outcomes if outcome is True),
            "failed": sum(1 for outcome in outcomes if outcome is not True),
        }
        for key, value in stated.items():
            if value != actual[key]:
                raise ValueError(f"{key} is {value!r}, but the results give {actual[key]!r}")
        return {key: value for key, value in data.items() if key not in _COMPUTED_FIELDS}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_passed(self) -> bool:
        """True when every result passed (and when there are no results)."""
        return all(r.passed for r in self.results)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def passed(self) -> int:
        """How many results passed."""
        return sum(1 for r in self.results if r.passed)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def failed(self) -> int:
        """How many results failed."""
        return sum(1 for r in self.results if not r.passed)

    @model_serializer(mode="wrap")
    def _results_last(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        # The summary reads first; the long per-case list goes at the end.
        data: dict[str, Any] = handler(self)
        if "results" in data:
            data["results"] = data.pop("results")
        return data

    @property
    def passed_count(self) -> int:
        return self.passed

    @property
    def failed_count(self) -> int:
        return self.failed

    def failed_cases(self) -> list[CaseResult]:
        return [r for r in self.results if not r.passed]

    def render(self) -> str:
        """Pretty multi-line rendering of the entire report."""
        if not self.results:
            return "Conformance: no fixtures run."
        body = "\n".join(case.render() for case in self.results)
        header = (
            f"Conformance: {self.passed_count}/{len(self.results)} passed"
            + (f", {self.failed_count} failed" if self.failed_count else "")
        )
        return f"{header}\n{body}"
