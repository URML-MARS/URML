"""Bridge — the orchestrator from natural language to validated URML.

```
                                +---- system prompt -------+
                                |  • instructions          |
                                |  • manifest summary      |
   user request -----+          |  • envelope summary      |
                     |          |  • few-shot examples     |
                     |          |  • URML JSON Schema      |
                     v          +--------------------------+
                  Bridge.translate()
                     |
              calls  v
                  LLMProvider.complete()  --> JSON string
                     |
                     | parse + validate (urml_validator)
                     v
              accepted? --yes--> return TranslateResult
                     |
                     no, revisions left? --yes--> add revision_context, loop
                     |
                     no --> raise BridgeRevisionExhausted
```

The bridge does NOT execute URML. It only produces validated programs;
handing them to a runtime is the caller's job.

Provider-neutrality is structural: nothing in this module imports a
specific LLM SDK. Use `EchoProvider` for tests; install
`urml-llm-bridge[anthropic]` / `[openai]` for real providers.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from urml_validator import (
    ValidationError as URMLValidationError,
)
from urml_validator import (
    ValidationResult,
    export_schema,
    validate,
)

from urml_llm_bridge.errors import BridgeRevisionExhausted, ProviderError
from urml_llm_bridge.few_shot import FewShot, few_shots_for
from urml_llm_bridge.prompt import build_system_prompt, render_revision_context
from urml_llm_bridge.providers.base import LLMProvider


class TranslateResult(BaseModel):
    """The output of `Bridge.translate()`.

    On success, `accepted=True` and `program` is the validated URML program
    as a parsed dict. On failure that does NOT raise (e.g., a single
    rejection that is still inside the revision budget), the loop continues;
    `Bridge.translate()` only returns when either the program is accepted
    or the revision budget is exhausted (which raises).
    """

    model_config = ConfigDict(extra="forbid")

    accepted: bool
    program: dict[str, Any] | None = None
    revision_count: int = Field(0, ge=0)
    last_validation: ValidationResult
    raw_completions: list[str] = Field(default_factory=list)


class Bridge:
    """Provider-agnostic translator from natural language to validated URML."""

    def __init__(
        self,
        *,
        provider: LLMProvider,
        manifest: dict[str, Any],
        envelope: dict[str, Any] | None = None,
        profiles: tuple[str, ...] = (),
        few_shots: list[FewShot] | None = None,
        max_revisions: int = 3,
    ) -> None:
        """Configure a Bridge instance.

        Args:
            provider:      Any LLMProvider — typically EchoProvider in tests,
                           a real adapter in production.
            manifest:      Active robot's capability manifest (raw dict from YAML).
            envelope:      Optional active safety envelope.
            profiles:      Profile name(s) this Bridge handles.
            few_shots:     Examples to inline into the prompt. If omitted, the
                           bridge auto-selects examples that match the active
                           `profiles` via `few_shots_for(profiles)`.
            max_revisions: How many revision attempts to allow after the first
                           emission. `max_revisions=0` means one attempt and out.
        """
        self._provider = provider
        self._manifest = manifest
        self._envelope = envelope
        self._profiles = tuple(profiles)
        self._few_shots = few_shots if few_shots is not None else few_shots_for(self._profiles)
        self._max_revisions = max_revisions
        self._schema = export_schema("program")

    def translate(self, user_request: str) -> TranslateResult:
        """Translate a natural-language request into a validated URML program.

        Raises:
            BridgeRevisionExhausted: The validator never accepted the
                program within `max_revisions` retries. The exception carries
                the last `ValidationResult` and the attempt count.
            ProviderError: The LLM provider misbehaved (non-JSON output,
                or an unhandled exception bubbled out of `complete()`).
        """
        revision_context: str | None = None
        raw_completions: list[str] = []
        last_result: ValidationResult | None = None

        attempts_total = self._max_revisions + 1  # initial + revisions
        for attempt_idx in range(attempts_total):
            system_prompt = build_system_prompt(
                schema=self._schema,
                manifest=self._manifest,
                envelope=self._envelope,
                profiles=self._profiles,
                few_shots=self._few_shots,
                revision_context=revision_context,
            )
            try:
                raw = self._provider.complete(
                    system=system_prompt,
                    user=user_request,
                    schema=self._schema,
                )
            except Exception as exc:
                raise ProviderError(f"provider raised: {type(exc).__name__}: {exc}") from exc

            raw_completions.append(raw)

            program = _parse_emission(raw)
            result = validate(
                program,
                self._manifest,
                self._envelope,
                profiles=self._profiles,
            )
            last_result = result

            if result.accepted:
                return TranslateResult(
                    accepted=True,
                    program=program,
                    revision_count=attempt_idx,
                    last_validation=result,
                    raw_completions=raw_completions,
                )

            # Not accepted: prepare for next attempt if any budget remains.
            if attempt_idx + 1 >= attempts_total:
                break
            revision_context = render_revision_context(
                prior_emission=raw,
                error_payload=[_error_to_dict(e) for e in result.errors],
            )

        assert last_result is not None  # the loop runs at least once
        raise BridgeRevisionExhausted(
            f"validator rejected the LLM's emission in all {attempts_total} attempt(s)",
            last_result=last_result,
            attempts=attempts_total,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_emission(raw: str) -> dict[str, Any]:
    """Parse the provider's response as a single JSON object.

    Tolerates leading/trailing whitespace. Rejects (with ProviderError)
    anything that isn't a JSON object at the top level — providers MUST
    NOT wrap their output in Markdown fences.
    """
    text = raw.strip()
    if not text:
        raise ProviderError("provider returned an empty string")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"provider returned non-JSON output: {exc.msg}") from exc
    if not isinstance(parsed, dict):
        raise ProviderError(
            f"provider returned a JSON value of type {type(parsed).__name__}; expected an object"
        )
    return parsed


def _error_to_dict(err: URMLValidationError) -> dict[str, Any]:
    """Compact, JSON-safe rendering of a ValidationError for the revision prompt."""
    return {
        "code": err.code.value,
        "primitive": err.primitive,
        "path": err.path,
        "field": err.field,
        "message": err.message,
        "suggestion": err.suggestion,
    }
