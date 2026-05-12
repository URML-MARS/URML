"""Conformance report — pass/fail per case plus diagnostics."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


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


class ConformanceReport(BaseModel):
    """A report covering an entire fixture run."""

    model_config = ConfigDict(extra="forbid")

    results: list[CaseResult] = Field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

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
