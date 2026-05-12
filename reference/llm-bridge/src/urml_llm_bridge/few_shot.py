"""Few-shot examples shown to the LLM in the system prompt.

A `FewShot` pairs a natural-language request with the URML program an
ideal model would emit. The bridge inlines these into the system prompt
so the model sees the structural target before being asked to produce
one.

## Public API

- `FewShot` — the per-example pydantic model.
- `home_few_shots()` — examples for the home profile.
- `industrial_few_shots()` — examples for the industrial profile.
- `few_shots_for(profiles)` — pick the right examples for an active
  profile set. Falls back to the home set if no profiles are declared.
- `default_few_shots()` — backwards-compatible alias for the home set,
  used by `Bridge` when no `few_shots=` is supplied.

Every example below validates against the matching manifest fixture in
`reference/validator/tests/fixtures/manifests/`, using only the v0.1
core primitive vocabulary from RFC-0002. Profile-specific primitives
(`take_off`/`land` for drone, `pick_from`/`place_at` for industrial)
land alongside the corresponding profile RFCs and become additional
few-shot examples then.
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


# ===========================================================================
# Home profile examples
# ===========================================================================


_HOME_RED_MUG: dict[str, Any] = {
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


_HOME_RETURN_TO_DOCK: dict[str, Any] = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"dock": {"at": "charging_dock", "service": "charge", "until": "full"}},
            {
                "report": {
                    "to": "user",
                    "facts": {"message": "Returned to dock; charging complete."},
                    "status": "success",
                }
            },
        ],
    },
}


_HOME_CHECK_KITCHEN: dict[str, Any] = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"move_to": {"location": "kitchen"}},
            {
                "detect": {
                    "object": "person",
                    "store_as": "kitchen_person",
                }
            },
            {
                "report": {
                    "to": "user",
                    "facts": {
                        "location": "kitchen",
                        "person_present": True,
                        "subject": "$kitchen_person",
                    },
                    "status": "success",
                }
            },
        ],
    },
}


_HOME_WAIT_THEN_GREET: dict[str, Any] = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {
                "wait_for": {
                    "condition": {"event": "user_present"},
                    "timeout": "300s",
                    "on_timeout": "error",
                }
            },
            {
                "report": {
                    "to": "user",
                    "facts": {"message": "Welcome back."},
                    "status": "success",
                }
            },
        ],
    },
}


def home_few_shots() -> list[FewShot]:
    """Return the home-profile few-shot example set."""
    return [
        FewShot(
            user="Bring me the red mug from the kitchen.",
            program=_HOME_RED_MUG,
            note="Canonical home-profile fetch-and-carry.",
        ),
        FewShot(
            user="Go back to your dock and recharge.",
            program=_HOME_RETURN_TO_DOCK,
            note="Charging + structured report. Uses `dock(service: charge, until: full)`.",
        ),
        FewShot(
            user="Check if anyone is in the kitchen.",
            program=_HOME_CHECK_KITCHEN,
            note="Move + perception + structured report. The `report.facts` "
            "embed the detected object reference for downstream consumers.",
        ),
        FewShot(
            user="Wait until I come back, then say hello.",
            program=_HOME_WAIT_THEN_GREET,
            note="Event-driven wait with a timeout, then report.",
        ),
    ]


# ===========================================================================
# Industrial profile examples (use only the v0.1 core vocabulary)
# ===========================================================================


_INDUSTRIAL_PICK_RED: dict[str, Any] = {
    "profile": "industrial",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"move_to": {"location": "pick_bin"}},
            {
                "detect": {
                    "object": "widget_red",
                    "where": {"near": "pick_bin"},
                    "store_as": "red_widget",
                }
            },
            {"grasp": {"target": "$red_widget", "force": "firm"}},
            {"move_to": {"location": "kitting_tray_red", "carrying": "$red_widget"}},
            {"release": {"mode": "place", "at": "kitting_tray_red"}},
            {"move_to": {"location": "home_pose"}},
            {
                "report": {
                    "to": "line_controller",
                    "facts": {"cycle": "pick_red_to_tray", "result": "ok"},
                    "status": "success",
                }
            },
        ],
    },
}


_INDUSTRIAL_RECONFIGURE_BLUE: dict[str, Any] = {
    "profile": "industrial",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"wait_for": {"condition": {"event": "line_ready"}, "timeout": "30s"}},
            {"move_to": {"location": "pick_bin"}},
            {
                "detect": {
                    "object": "widget_blue",
                    "where": {"near": "pick_bin"},
                    "store_as": "blue_widget",
                }
            },
            {"grasp": {"target": "$blue_widget", "force": "firm"}},
            {"move_to": {"location": "kitting_tray_blue", "carrying": "$blue_widget"}},
            {"release": {"mode": "place", "at": "kitting_tray_blue"}},
            {
                "report": {
                    "to": "line_controller",
                    "facts": {"cycle": "pick_blue_to_tray", "result": "ok"},
                    "status": "success",
                }
            },
        ],
    },
}


def industrial_few_shots() -> list[FewShot]:
    """Return the industrial-profile few-shot example set."""
    return [
        FewShot(
            user="Pick a red widget from the bin and place it in the red kitting tray.",
            program=_INDUSTRIAL_PICK_RED,
            note="Pick-and-place cycle with structured report to the line controller.",
        ),
        FewShot(
            user="Wait for the line to be ready, then move a blue widget to the blue tray.",
            program=_INDUSTRIAL_RECONFIGURE_BLUE,
            note="Event-gated cycle. The Manifesto's change-color/change-tray "
            "reconfiguration is a parameter swap on this template.",
        ),
    ]


# ===========================================================================
# Profile selector
# ===========================================================================


# Drone / healthcare / agricultural / etc. land here as their profile RFCs accept.
# Until then, requesting an unknown profile falls through to the home set,
# which exercises the core vocabulary regardless of domain.
_PROFILE_FACTORIES: dict[str, object] = {
    "home": home_few_shots,
    "industrial": industrial_few_shots,
}


def few_shots_for(profiles: tuple[str, ...]) -> list[FewShot]:
    """Pick the right examples for the active profile set.

    - Empty `profiles` -> returns the home set as a sensible default.
    - One known profile -> that profile's examples.
    - Multiple profiles -> concatenated, profile order preserved.
    - Unknown profiles -> silently skipped; if every requested profile is
      unknown, falls back to the home set so the bridge still has an
      anchor.
    """
    if not profiles:
        return home_few_shots()
    out: list[FewShot] = []
    for name in profiles:
        factory = _PROFILE_FACTORIES.get(name)
        if factory is not None:
            out.extend(factory())  # type: ignore[operator]
    if not out:
        return home_few_shots()
    return out


def default_few_shots() -> list[FewShot]:
    """Backwards-compatible alias used by `Bridge` when no `few_shots=` is given.

    Returns the home-profile example set. Equivalent to `home_few_shots()`.
    """
    return home_few_shots()
