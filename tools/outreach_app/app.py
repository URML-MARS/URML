"""NiceGUI page registrations.

Imported for side effects from `__main__.py`. The actual page bodies
live under `pages/`.
"""

from __future__ import annotations

from nicegui import app, ui

from .pages import overview, kanban, targets, directives
from .state import get_filters, clear_filters, toggle_chip
from . import data as _data


SECTOR_COLOR = {
    "robot-platform": "indigo",
    "component-vendor": "deep-purple",
    "substrate-runtime": "blue",
    "protocol-substrate": "light-blue",
    "middleware": "cyan",
    "simulator": "teal",
    "perception": "green",
    "ai-language": "orange",
    "framework-skill": "amber",
    "governance-body": "brown",
    "conceptual-peer": "blue-grey",
    "education-toolchain": "lime",
    "medical": "red",
    "agriculture": "green",
    "delivery": "pink",
}

RESPONSE_COLOR = {
    "none": "grey",
    "acked": "blue-grey",
    "engaged": "green",
    "wontfix": "red",
    "declined": "deep-orange",
}


def header() -> None:
    """Top bar with title + nav + filter summary."""
    with ui.header().classes("items-center justify-between bg-primary text-white shadow"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("hub").classes("text-2xl")
            ui.label("URML outreach").classes("text-lg font-medium")
        with ui.row().classes("items-center gap-1"):
            for label, path, icon in [
                ("Overview", "/", "dashboard"),
                ("Kanban", "/kanban", "view_column"),
                ("Targets", "/targets", "list_alt"),
                ("Directives", "/directives", "task_alt"),
            ]:
                ui.button(
                    label,
                    icon=icon,
                    on_click=lambda p=path: ui.navigate.to(p),
                ).props("flat color=white dense")
        with ui.row().classes("items-center gap-2"):
            f = get_filters()
            active = sum(
                len(getattr(f, k))
                for k in ("sectors", "tiers", "countries", "responses", "waves")
            ) + (1 if f.search else 0)
            badge_text = f"{active} filter{'s' if active != 1 else ''}" if active else "no filters"
            ui.chip(badge_text, icon="filter_alt").props("dense color=white text-color=primary")
            if active:
                ui.button(icon="filter_alt_off", on_click=lambda: (clear_filters(), ui.navigate.reload())) \
                    .props("flat color=white dense").tooltip("Clear all filters")


@ui.page("/")
def page_overview():
    header()
    overview.render()


@ui.page("/kanban")
def page_kanban():
    header()
    kanban.render()


@ui.page("/targets")
def page_targets():
    header()
    targets.render()


@ui.page("/directives")
def page_directives():
    header()
    directives.render()
