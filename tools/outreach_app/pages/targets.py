"""Targets page: full list with the persistent sidebar filter chips."""

from __future__ import annotations

from nicegui import ui

from .. import data
from ..components.sidebar import render as render_sidebar
from ..components.row_drawer import open_drawer, render as render_drawer
from ..state import get_filters


def render() -> None:
    render_drawer()
    render_sidebar()
    f = get_filters()
    rows = data.list_targets(filters=f)
    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-6 gap-3"):
        with ui.row().classes("items-center justify-between"):
            ui.label("Targets").classes("text-h4 font-medium")
            ui.label(f"{len(rows)} rows").classes("text-grey-7")

        if not rows:
            ui.label(
                "No rows match the active filters. Clear filters from the left sidebar."
            ).classes("text-grey-7 italic")
            return

        with ui.column().classes("w-full gap-2"):
            for r in rows:
                with ui.card().classes("w-full cursor-pointer hover:bg-blue-1") \
                        .on("click", lambda w=r["wave"], s=r["slug"]: open_drawer(w, s)):
                    with ui.row().classes("items-center gap-3 w-full q-pa-sm flex-nowrap"):
                        ui.label(r["slug"]).classes("font-medium w-48 truncate")
                        if r.get("sector"):
                            ui.chip(r["sector"]).props("dense outline")
                        if r.get("country"):
                            ui.chip(r["country"]).props(
                                f"dense color={'orange' if r['country'] == 'INTL' else 'blue-grey'} text-color=white"
                            )
                        if r.get("tier"):
                            ui.chip(f"T{r['tier']}").props("dense outline")
                        if r.get("response"):
                            color = _response_color(r["response"])
                            ui.chip(r["response"]).props(f"dense color={color} text-color=white")
                        ui.label(r.get("contact") or "").classes(
                            "text-grey-8 text-sm truncate flex-grow"
                        )
                        ui.label(r.get("last_touch") or r.get("sent_at") or "") \
                            .classes("text-grey-6 text-xs whitespace-nowrap")


def _response_color(response: str) -> str:
    return {
        "none": "grey",
        "acked": "blue-grey",
        "engaged": "positive",
        "wontfix": "red",
        "declined": "deep-orange",
    }.get(response, "grey")
