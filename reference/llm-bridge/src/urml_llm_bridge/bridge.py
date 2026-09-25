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
                     | parse
                     v
              clarify object? (RFC-0700 clarify mode only, budget left,
                     |          no rejection yet)
                     | yes --> relay question, fold answer into request, loop
                     |         (or raise BridgeClarificationNeeded)
                     no
                     |
                     | validate (urml_validator)
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
import re
from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from urml_validator import (
    ValidationError as URMLValidationError,
)
from urml_validator import (
    ValidationResult,
    export_schema,
    validate,
    validate_fleet,
)

from urml_llm_bridge.errors import (
    BridgeClarificationNeeded,
    BridgePolicyViolation,
    BridgeRevisionExhausted,
    ProviderError,
)
from urml_llm_bridge.few_shot import FewShot, few_shots_for, fleet_few_shots
from urml_llm_bridge.prompt import (
    build_fleet_system_prompt,
    build_system_prompt,
    render_revision_context,
)
from urml_llm_bridge.providers.base import CLARIFY_SCHEMA, LLMProvider

#: RFC-0700: the callback that relays a clarifying question to the operator.
#: Receives (question, options) and returns the operator's answer.
OnClarify = Callable[[str, list[str]], str]


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
    #: RFC-0700 clarify mode: how many clarifying questions were asked and
    #: answered on the way to this result (0 with clarify mode off).
    clarification_count: int = Field(default=0, ge=0)
    #: The (question, answer) pairs, in order.
    clarifications: list[tuple[str, str]] = Field(default_factory=list)


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
        policy: dict[str, Any] | None | Literal["DEFAULT"] = "DEFAULT",
        clarify: bool = False,
        max_clarifications: int = 1,
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
            policy:        Compliance policy (RFC-0004) passed to the validator
                           on every revision attempt. ``"DEFAULT"`` (the default)
                           uses the bundled US-federal policy; ``None`` skips
                           Pass 5; a dict supplies a specific policy file's
                           parsed content.
            clarify:       RFC-0700 clarify mode (default off). When on, the
                           model's FIRST emission may be a
                           ``{"clarify": {...}}`` question instead of a
                           program; see ``translate(on_clarify=...)``. Off,
                           the contract is exactly Layer 4 v0.2.0.
            max_clarifications: Clarification budget (clarify mode only).
                           Questions never consume revision attempts.
        """
        self._provider = provider
        self._manifest = manifest
        self._envelope = envelope
        self._profiles = tuple(profiles)
        self._few_shots = few_shots if few_shots is not None else few_shots_for(self._profiles)
        self._max_revisions = max_revisions
        self._policy = policy
        self._clarify = clarify
        self._max_clarifications = max_clarifications
        self._schema = export_schema("program")

    def translate(
        self,
        user_request: str,
        *,
        on_clarify: OnClarify | None = None,
    ) -> TranslateResult:
        """Translate a natural-language request into a validated URML program.

        Args:
            user_request: The natural-language request.
            on_clarify:   Clarify mode only (RFC-0700). Called with
                (question, options) when the model asks a clarifying
                question; returns the operator's answer, which is folded
                into the request before the loop continues. When clarify
                mode is on and this is None, a question raises
                `BridgeClarificationNeeded` instead — the bridge never
                invents an answer.

        Raises:
            BridgeRevisionExhausted: The validator never accepted the
                program within `max_revisions` retries. The exception carries
                the last `ValidationResult` and the attempt count.
            BridgeClarificationNeeded: Clarify mode, the model asked, and
                no `on_clarify` callback was supplied.
            ProviderError: The LLM provider misbehaved (non-JSON output,
                or an unhandled exception bubbled out of `complete()`).
        """
        revision_context: str | None = None
        raw_completions: list[str] = []
        last_result: ValidationResult | None = None
        clarifications: list[tuple[str, str]] = []
        effective_request = user_request
        had_rejection = False

        attempts_total = self._max_revisions + 1  # initial + revisions
        attempt_idx = 0
        while attempt_idx < attempts_total:
            # RFC-0700: a question is allowed only before the first rejection
            # and while the budget lasts. Outside that window the clarify
            # branch is withheld from the provider (a constrained decoder
            # then cannot emit one) and the prompt says to commit.
            clarify_open = (
                self._clarify
                and not had_rejection
                and len(clarifications) < self._max_clarifications
            )
            system_prompt = build_system_prompt(
                schema=self._schema,
                manifest=self._manifest,
                envelope=self._envelope,
                profiles=self._profiles,
                few_shots=self._few_shots,
                revision_context=revision_context,
                clarify=self._clarify,
                clarify_budget_spent=self._clarify and not clarify_open,
            )
            try:
                if self._clarify:
                    raw = self._provider.complete(
                        system=system_prompt,
                        user=effective_request,
                        schema=self._schema,
                        clarify_schema=CLARIFY_SCHEMA if clarify_open else None,
                    )
                else:
                    # Off: call exactly as v0.2.0 did, so providers that
                    # predate the clarify keyword keep working.
                    raw = self._provider.complete(
                        system=system_prompt,
                        user=effective_request,
                        schema=self._schema,
                    )
            except Exception as exc:
                raise ProviderError(f"provider raised: {type(exc).__name__}: {exc}") from exc

            raw_completions.append(raw)

            program = _parse_emission(raw)

            if clarify_open and set(program.keys()) == {"clarify"}:
                question, options = _parse_clarify(program)
                if on_clarify is None:
                    raise BridgeClarificationNeeded(
                        "the model asked a clarifying question and no on_clarify "
                        "callback was supplied",
                        question=question,
                        options=options,
                        raw_completions=raw_completions,
                    )
                answer = on_clarify(question, options)
                clarifications.append((question, answer))
                effective_request = user_request + "\n\nClarification:\n" + "\n".join(
                    f"Q: {q}\nA: {a}" for q, a in clarifications
                )
                # A question consumes clarification budget, never a revision.
                continue

            result = validate(
                program,
                self._manifest,
                self._envelope,
                profiles=self._profiles,
                policy=self._policy,
            )
            last_result = result

            if result.accepted:
                return TranslateResult(
                    accepted=True,
                    program=program,
                    revision_count=attempt_idx,
                    last_validation=result,
                    raw_completions=raw_completions,
                    clarification_count=len(clarifications),
                    clarifications=clarifications,
                )

            # RFC-0004: short-circuit revision when ONLY policy.* errors remain.
            # Programs cannot fix hardware; another revision will not help.
            non_policy_errors = [e for e in result.errors if not _is_policy_error(e)]
            if not non_policy_errors:
                raise BridgePolicyViolation(
                    "validation rejected for compliance-policy reasons only; "
                    "revision cannot fix hardware provenance",
                    last_result=result,
                    attempts=attempt_idx + 1,
                    raw_completions=raw_completions,
                )

            # Not accepted: prepare for next attempt if any budget remains.
            # RFC-0700: after any rejection the clarify window is closed for
            # the rest of this translation (revision attempts commit).
            had_rejection = True
            attempt_idx += 1
            if attempt_idx >= attempts_total:
                break
            revision_context = render_revision_context(
                prior_emission=raw,
                # Only feed the LLM the errors it can act on. Policy errors are
                # surfaced terminally below if revision exhausts.
                error_payload=[_error_to_dict(e) for e in non_policy_errors],
            )

        assert last_result is not None  # the loop runs at least once
        raise BridgeRevisionExhausted(
            f"validator rejected the LLM's emission in all {attempts_total} attempt(s)",
            last_result=last_result,
            attempts=attempts_total,
            raw_completions=raw_completions,
        )


class FleetBridge:
    """Provider-agnostic translator from natural language to a validated
    multi-robot URML program (RFC-0286).

    The inter-robot analogue of `Bridge`: it summarizes a whole roster (one
    capability block per member) in the prompt and validates each emission with
    `validate_fleet` instead of `validate`. The revision loop, provider protocol,
    and `TranslateResult` shape are identical.
    """

    def __init__(
        self,
        *,
        provider: LLMProvider,
        roster: dict[str, Any],
        member_manifests: dict[str, dict[str, Any]],
        member_envelopes: dict[str, dict[str, Any]] | None = None,
        profiles: tuple[str, ...] = (),
        few_shots: list[FewShot] | None = None,
        max_revisions: int = 3,
        policy: dict[str, Any] | None | Literal["DEFAULT"] = "DEFAULT",
    ) -> None:
        self._provider = provider
        self._roster = roster
        self._member_manifests = member_manifests
        self._member_envelopes = member_envelopes
        self._profiles = tuple(profiles)
        self._few_shots = few_shots if few_shots is not None else fleet_few_shots()
        self._max_revisions = max_revisions
        self._policy = policy
        self._schema = export_schema("program")

    def translate(self, user_request: str) -> TranslateResult:
        """Translate a natural-language request into a validated fleet program.

        Same contract as `Bridge.translate` — raises `BridgeRevisionExhausted`,
        `BridgePolicyViolation`, or `ProviderError`.
        """
        revision_context: str | None = None
        raw_completions: list[str] = []
        last_result: ValidationResult | None = None

        attempts_total = self._max_revisions + 1
        for attempt_idx in range(attempts_total):
            system_prompt = build_fleet_system_prompt(
                schema=self._schema,
                roster=self._roster,
                member_manifests=self._member_manifests,
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
            result = validate_fleet(
                self._roster,
                self._member_manifests,
                program,
                self._member_envelopes,
                profiles=self._profiles,
                policy=self._policy,
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

            non_policy_errors = [e for e in result.errors if not _is_policy_error(e)]
            if not non_policy_errors:
                raise BridgePolicyViolation(
                    "validation rejected for compliance-policy reasons only; "
                    "revision cannot fix hardware provenance",
                    last_result=result,
                    attempts=attempt_idx + 1,
                    raw_completions=raw_completions,
                )

            if attempt_idx + 1 >= attempts_total:
                break
            revision_context = render_revision_context(
                prior_emission=raw,
                error_payload=[_error_to_dict(e) for e in non_policy_errors],
            )

        assert last_result is not None
        raise BridgeRevisionExhausted(
            f"validator rejected the LLM's emission in all {attempts_total} attempt(s)",
            last_result=last_result,
            attempts=attempts_total,
            raw_completions=raw_completions,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_TRAILING_COMMA_RE = re.compile(r",(\s*[}\]])")


def _repair_json_text(text: str) -> str:
    """Conservatively repair the common ways a small model malforms its JSON.

    Three safe, structure-preserving fixes, in order:

    1. Strip a Markdown code fence (```json ... ``` or ``` ... ```).
    2. Extract the outermost ``{ ... }`` object from any surrounding prose
       ("Here is the program: { ... }. Hope that helps!").
    3. Remove trailing commas before ``}`` or ``]``.

    None of these change the program's structure or values; they only remove
    wrapping and noise. The result is re-validated downstream, so a
    repaired-but-wrong program is still rejected by the validator. Repair can
    only recover an otherwise-lost valid emission, never admit a bad one. It
    deliberately does NOT guess at genuinely broken JSON (missing commas,
    truncation), which would risk fabricating a different program.
    """
    s = text.strip()
    # 1. Drop a leading fence line (``` or ```json) and a trailing fence.
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else ""
        s = s.rstrip()
        if s.endswith("```"):
            s = s[:-3]
    # 2. Extract the outermost JSON object from surrounding prose.
    first, last = s.find("{"), s.rfind("}")
    if first != -1 and last > first:
        s = s[first : last + 1]
    # 3. Remove trailing commas before a closing brace/bracket.
    s = _TRAILING_COMMA_RE.sub(r"\1", s)
    return s.strip()


def _parse_emission(raw: str) -> dict[str, Any]:
    """Parse the provider's response as a single JSON object.

    Tolerates leading/trailing whitespace. A frontier model emits clean JSON;
    small / local models often wrap it in Markdown fences or prose, or leave a
    trailing comma, so a strict parse failure falls back to a conservative
    repair (`_repair_json_text`) before giving up. The repaired text is parsed
    and then validated downstream like any other emission, so repair never
    weakens the validation gate.
    """
    text = raw.strip()
    if not text:
        raise ProviderError("provider returned an empty string")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        repaired = _repair_json_text(text)
        try:
            parsed = json.loads(repaired) if repaired and repaired != text else None
        except json.JSONDecodeError:
            parsed = None
        if parsed is None:
            raise ProviderError(f"provider returned non-JSON output: {exc.msg}") from exc
    if not isinstance(parsed, dict):
        raise ProviderError(
            f"provider returned a JSON value of type {type(parsed).__name__}; expected an object"
        )
    return parsed


def _parse_clarify(program: dict[str, Any]) -> tuple[str, list[str]]:
    """Validate a `{"clarify": {...}}` emission and return (question, options).

    A malformed clarify object is a provider defect, not a validation
    failure: the wire shape is fixed by RFC-0700, and constrained decoders
    cannot even produce a malformed one.
    """
    inner = program.get("clarify")
    if not isinstance(inner, dict):
        raise ProviderError("clarify emission is not an object")
    question = inner.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ProviderError("clarify emission has no non-empty `question` string")
    raw_options = inner.get("options", [])
    if not isinstance(raw_options, list) or not all(isinstance(o, str) for o in raw_options):
        raise ProviderError("clarify `options` must be a list of strings")
    extra = set(inner.keys()) - {"question", "options"}
    if extra:
        raise ProviderError(f"clarify emission has unknown key(s): {sorted(extra)}")
    return question.strip(), list(raw_options)


def _error_to_dict(err: URMLValidationError) -> dict[str, Any]:
    """Compact, JSON-safe rendering of a ValidationError for the revision prompt."""
    return {
        "code": str(err.code),
        "primitive": err.primitive,
        "path": err.path,
        "field": err.field,
        "message": err.message,
        "suggestion": err.suggestion,
    }


def _is_policy_error(err: URMLValidationError) -> bool:
    """Return True iff the error is in the `policy.*` namespace."""
    return str(err.code).startswith("policy.")
