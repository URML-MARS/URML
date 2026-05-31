"""Filter state.

Held in a module-level dict for simplicity; this is a localhost
solo-maintainer app, so there is no multi-user concurrency story. If
two browser tabs are open the filter state is shared between them by
design (matches the "single source of truth in the YAML" discipline).
"""

from __future__ import annotations

from .data import Filters


_state: dict = {"filters": Filters()}


def get_filters() -> Filters:
    return _state["filters"]


def set_filters(filters: Filters) -> None:
    _state["filters"] = filters


def toggle_chip(field: str, value: str) -> None:
    f = get_filters()
    current: list[str] = list(getattr(f, field))
    if value in current:
        current.remove(value)
    else:
        current.append(value)
    setattr(f, field, current)
    set_filters(f)


def clear_filters() -> None:
    set_filters(Filters())
