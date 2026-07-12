"""Back-translation: produce a natural-language utterance from a gold program (RFC-0666).

Fixture programs have no paired utterance. `BackTranslator` is the seam:

- `TemplateBackTranslator` renders deterministic English from the program's
  steps. Hermetic, runs in CI, stylistically narrow by design. It exists so
  the pipeline is testable end to end without a network and so the dataset
  floor never depends on an external model.
- `LLMBackTranslator` asks any `LLMProvider` for paraphrases of the intent
  a program encodes. This is where dataset diversity comes from; running it
  at scale is operator-action. The provider protocol keeps it vendor-neutral.

Every candidate utterance goes through the validator oracle downstream
regardless of which translator produced it.
"""

from __future__ import annotations

import json
from typing import Any, Protocol, runtime_checkable

from urml_llm_bridge.providers.base import LLMProvider


@runtime_checkable
class BackTranslator(Protocol):
    """Anything that can phrase a URML program as the instruction that produces it."""

    def to_utterances(
        self,
        program: dict[str, Any],
        manifest: dict[str, Any],
        *,
        language: str = "en",
        n: int = 1,
    ) -> list[str]:
        """Return up to `n` natural-language utterances for `program`."""
        ...


def _fmt_value(value: Any) -> str:
    if isinstance(value, str):
        return value.replace("_", " ")
    return str(value)


def _render_step(step: dict[str, Any]) -> str | None:
    """One clause of imperative English for one primitive step.

    Unknown primitives return None and are skipped by the caller; the
    template path renders what it knows and never invents phrasing for a
    primitive it has no template for.
    """
    if len(step) != 1:
        return None
    name, args = next(iter(step.items()))
    if not isinstance(args, dict):
        return None
    match name:
        case "move_to":
            return f"go to {_fmt_value(args.get('location', 'the target'))}"
        case "detect":
            obj = _fmt_value(args.get("object", "the object"))
            attrs = args.get("attributes")
            if isinstance(attrs, dict) and "color" in attrs:
                return f"find a {_fmt_value(attrs['color'])} {obj}"
            return f"find a {obj}"
        case "grasp":
            return "pick it up"
        case "release":
            if args.get("mode") == "hand_to_user":
                return "hand it to me"
            return f"put it down at {_fmt_value(args['at'])}" if "at" in args else "put it down"
        case "take_off":
            alt = args.get("altitude")
            return f"take off to {alt} meters" if alt is not None else "take off"
        case "land":
            return "land"
        case "return_to_home":
            return "return home"
        case "hover":
            over = args.get("over")
            return f"hover over {_fmt_value(over)}" if over else "hover in place"
        case "capture":
            return f"take a {_fmt_value(args.get('media', 'photo'))}"
        case "scan":
            return "scan the area"
        case "measure":
            return f"measure the {_fmt_value(args.get('what', 'reading'))}"
        case "report":
            return "tell me the result" if args.get("to") == "user" else "report the result"
        case "wait_for":
            condition = args.get("condition")
            if isinstance(condition, dict) and "event" in condition:
                return f"wait for {_fmt_value(condition['event'])}"
            return "wait for the condition"
        case "wait_passively":
            duration = args.get("duration")
            return f"wait {_fmt_value(duration)}" if duration else "wait"
        case "dock":
            return f"dock at {_fmt_value(args.get('at', 'the dock'))}"
        case "call_program":
            return f"run the {_fmt_value(args.get('name', 'named'))} program"
        case "speak":
            return f"say {args.get('text', 'something')!r}"
        case "listen":
            return "listen for my reply"
        case "drive":
            if "radius" in args and "arc" in args:
                return f"orbit {args['arc']} degrees with a {args['radius']} meter radius"
            if "arc" in args:
                return f"curve {args['arc']} degrees over {args.get('distance', 0)} meters"
            return f"drive {args.get('distance', 0)} meters"
        case "turn":
            angle = args.get("angle", 0)
            side = "left" if isinstance(angle, (int, float)) and angle >= 0 else "right"
            return f"turn {side} {abs(angle) if isinstance(angle, (int, float)) else angle} degrees"
        case "pick_from":
            return f"pick a {_fmt_value(args.get('object', 'part'))} from {_fmt_value(args.get('source', 'the bin'))}"
        case "place_at":
            return f"place it at {_fmt_value(args.get('destination', 'the target'))}"
        case "swap_tool":
            return f"swap to the {_fmt_value(args.get('tool', 'next'))} tool"
        case "set_output":
            return f"set output {_fmt_value(args.get('line', ''))}".strip()
        case "follow_trajectory" | "plan_trajectory":
            return "follow the planned route"
        case _:
            return None


def _collect_clauses(node: Any) -> list[str]:
    """Walk a behavior tree and collect renderable clauses in order."""
    clauses: list[str] = []
    if isinstance(node, dict):
        steps = node.get("steps")
        branches = node.get("branches")
        body = node.get("body")
        if isinstance(steps, list):
            for step in steps:
                clauses.extend(_collect_clauses(step))
        elif isinstance(branches, list):
            for branch in branches:
                clauses.extend(_collect_clauses(branch))
        elif isinstance(body, dict):
            clauses.extend(_collect_clauses(body))
        else:
            rendered = _render_step(node)
            if rendered is not None:
                clauses.append(rendered)
    return clauses


class TemplateBackTranslator:
    """Deterministic English rendering of a program's step sequence.

    English only; other languages take the LLM path (RFC-0666 Unresolved
    questions). Returns at most one utterance regardless of `n`, because a
    template has exactly one way to say a thing.
    """

    def to_utterances(
        self,
        program: dict[str, Any],
        manifest: dict[str, Any],
        *,
        language: str = "en",
        n: int = 1,
    ) -> list[str]:
        if language != "en":
            return []
        clauses = _collect_clauses(program.get("behavior", {}))
        if not clauses:
            return []
        if len(clauses) == 1:
            sentence = clauses[0]
        else:
            sentence = ", ".join(clauses[:-1]) + f", then {clauses[-1]}"
        return [sentence[0].upper() + sentence[1:] + "."]


_BACKTRANSLATE_SYSTEM = """\
You reverse-translate robot programs into the instruction a person would have
given to produce them. You will receive a URML program (JSON). Reply with a
JSON array of {n} distinct natural-language instructions in {language}, each a
single sentence a non-programmer might say, each fully implied by the program:
no added goals, no dropped steps. Reply with the JSON array only."""


class LLMBackTranslator:
    """Paraphrase-diverse back-translation through any `LLMProvider`."""

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def to_utterances(
        self,
        program: dict[str, Any],
        manifest: dict[str, Any],
        *,
        language: str = "en",
        n: int = 1,
    ) -> list[str]:
        system = _BACKTRANSLATE_SYSTEM.format(n=n, language=language)
        raw = self._provider.complete(
            system=system,
            user=json.dumps(program, sort_keys=True),
            schema={"type": "array", "items": {"type": "string"}},
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if not isinstance(parsed, list):
            return []
        return [item.strip() for item in parsed if isinstance(item, str) and item.strip()][:n]
