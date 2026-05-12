"""Few-shot examples shown to the LLM in the system prompt.

A `FewShot` pairs a natural-language request with the URML program an
ideal model would emit. The bridge inlines these into the system prompt
so the model sees the structural target before being asked to produce
one.

`default_few_shots()` returns the built-in example set — currently the
canonical `red-mug` scenario from the manifesto. Profiles will eventually
ship their own example libraries; that lookup table is intentionally not
in this module yet.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class FewShot(BaseModel):
    """A single (user_request, target_program) example for the system prompt."""

    model_config = ConfigDict(extra="forbid")

    user: str
    program: dict[str, Any]
    note: str | None = None


_RED_MUG_PROGRAM: dict[str, Any] = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"move_to": {"location": "kitchen"}},
            {
                "detect": {
                    "object": "mug",
                    "attributes": {"color": "red"},
                    "store_as": "target_mug",
                }
            },
            {"grasp": {"target": "$target_mug", "force": "gentle"}},
            {"move_to": {"location": "user", "carrying": "$target_mug"}},
            {"release": {"mode": "hand_to_user"}},
        ],
    },
}


def default_few_shots() -> list[FewShot]:
    """Return the built-in few-shot example set.

    Currently a single example: the red-mug scenario from
    `MANIFESTO.md` §A Concrete Example. Profile-specific example
    libraries land in a follow-up.
    """
    return [
        FewShot(
            user="Bring me the red mug from the kitchen.",
            program=_RED_MUG_PROGRAM,
            note="Canonical home-profile fetch-and-carry.",
        ),
    ]
