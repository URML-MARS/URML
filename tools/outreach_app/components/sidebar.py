"""Persistent left sidebar with filter chips."""

from __future__ import annotations

from nicegui import ui

from .. import data
from ..state import get_filters, toggle_chip, clear_filters, set_filters
from ..data import Filters


def render() -> None:
    distinct = data.distinct_values()
    f = get_filters()
    with ui.left_drawer(value=True, bottom_corner=True).props("bordered width=280").classes("bg-grey-1 p-3"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label("Filters").classes("text-h6 font-medium")
            ui.button(icon="filter_alt_off", on_click=lambda: (clear_filters(), ui.navigate.reload())) \
                .props("flat dense").tooltip("Clear all")

        search = ui.input("Search slug / contact / notes", value=f.search) \
            .props("outlined dense clearable").classes("w-full mt-2")

        def submit_search() -> None:
            f2 = get_filters()
            f2.search = (search.value or "").strip()
            set_filters(f2)
            ui.navigate.reload()

        search.on("keydown.enter", submit_search)
        search.on("clear", submit_search)
        ui.button("Apply search", on_click=submit_search).props("dense flat color=primary").classes("self-end")

        ui.separator().classes("my-3")

        _chip_section("Sector", "sectors", distinct["sectors"], f.sectors)
        _chip_section("Tier", "tiers", distinct["tiers"], f.tiers)
        _chip_section("Response", "responses", distinct["responses"], f.responses)
        _chip_section("Country", "countries", distinct["countries"], f.countries)
        _chip_section("Wave", "waves", _short_wave_labels(distinct["waves"]), f.waves, raw=distinct["waves"])


def _short_wave_labels(waves: list[str]) -> list[str]:
    out = []
    for w in waves:
        if w == "outreach.yaml":
            out.append("Move 1")
        elif w.startswith("outreach-move") and w.endswith(".yaml"):
            try:
                out.append(f"Move {int(w[len('outreach-move'):-len('.yaml')])}")
            except ValueError:
                out.append(w)
        else:
            out.append(w)
    return out


def _chip_section(title: str, field: str, labels: list[str], active: list[str], raw: list[str] | None = None) -> None:
    if not labels:
        return
    with ui.expansion(title, value=bool(active)).classes("w-full"):
        with ui.row().classes("gap-1 flex-wrap"):
            real_values = raw if raw is not None else labels
            for label, value in zip(labels, real_values):
                is_on = value in active
                color = "primary" if is_on else "grey-4"
                text_color = "white" if is_on else "grey-9"
                btn = ui.chip(label).props(f"dense clickable color={color} text-color={text_color}")
                btn.on(
                    "click",
                    lambda v=value, fld=field: (toggle_chip(fld, v), ui.navigate.reload()),
                )
