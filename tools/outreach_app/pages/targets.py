"""Targets page: full list with persistent sidebar filter chips.

Each row is a two-line card:
  Line 1 (title): slug · RFC-#### · sector chip · country · tier · response
  Line 2 (body):  contact + first sentence of next_action / notes
                  (right-aligned: last_touch / sent_at)
"""

from __future__ import annotations

import re

from nicegui import ui

from .. import data
from ..components.sidebar import render as render_sidebar
from ..components.row_drawer import open_drawer, render as render_drawer
from ..state import get_filters


SECTOR_META = {
    "robot-platform": ("Robot platform", "smart_toy", "indigo-6"),
    "component-vendor": ("Component vendor", "memory", "deep-purple-6"),
    "substrate-runtime": ("Substrate runtime", "settings_input_component", "blue-6"),
    "protocol-substrate": ("Protocol", "router", "light-blue-7"),
    "middleware": ("Middleware", "hub", "cyan-7"),
    "simulator": ("Simulator", "view_in_ar", "teal-6"),
    "perception": ("Perception", "visibility", "green-7"),
    "ai-language": ("AI / language", "psychology", "orange-7"),
    "framework-skill": ("Framework / skill", "extension", "amber-7"),
    "governance-body": ("Governance", "account_balance", "brown-6"),
    "conceptual-peer": ("Conceptual peer", "compare_arrows", "blue-grey-6"),
    "education-toolchain": ("Education", "school", "lime-7"),
    "medical": ("Medical", "medical_services", "red-6"),
    "agriculture": ("Agriculture", "yard", "light-green-7"),
    "delivery": ("Delivery", "local_shipping", "pink-6"),
}


def _first_sentence(text: str, max_chars: int = 200) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)
    head = parts[0]
    if len(head) > max_chars:
        head = head[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return head


def render() -> None:
    render_drawer()
    render_sidebar()
    f = get_filters()
    rows = data.list_targets(filters=f)

    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-6 gap-3"):
        with ui.row().classes("items-baseline gap-3"):
            ui.label("Targets").classes("text-h4 font-medium")
            ui.label(f"{len(rows)} rows").classes("text-grey-7")

        if not rows:
            ui.label(
                "No rows match the active filters. Clear filters from the left sidebar."
            ).classes("text-grey-7 italic")
            return

        with ui.column().classes("w-full gap-2"):
            for r in rows:
                _row_card(r)


def _row_card(r: dict) -> None:
    sector = r.get("sector") or ""
    label, icon, color = SECTOR_META.get(sector, (sector or "—", "circle", "grey-6"))
    rfc_str = f"RFC-{int(r['rfc']):04d}" if r.get("rfc") else ""
    snippet = _first_sentence(r.get("next_action") or r.get("contact") or "")
    date_str = r.get("last_touch") or r.get("sent_at") or ""
    response = r.get("response") or "none"

    with ui.card().classes("w-full cursor-pointer hover:bg-blue-1 q-pa-none") \
            .on("click", lambda w=r["wave"], s=r["slug"]: open_drawer(w, s)):
        with ui.row().classes("items-stretch w-full no-wrap"):
            # Sector accent strip on the left
            ui.element("div").classes(f"bg-{color}").style("width: 6px")

            with ui.column().classes("gap-1 flex-grow min-w-0 q-pa-md"):
                # Line 1: title + RFC + meta chips + date
                with ui.row().classes("items-center gap-2 w-full no-wrap"):
                    with ui.row().classes("items-center gap-2 min-w-0 flex-grow"):
                        ui.icon(icon).classes(f"text-{color}")
                        ui.label(r["slug"]).classes("text-subtitle1 font-medium truncate")
                        if rfc_str:
                            ui.label(rfc_str).classes("text-xs text-grey-7")
                    # Right-side chips + date
                    with ui.row().classes("items-center gap-2 whitespace-nowrap"):
                        ui.chip(label).props(f"dense outline text-color={color}")
                        if r.get("country"):
                            ui.chip(r["country"]).props(
                                f"dense color={'orange' if r['country'] == 'INTL' else 'blue-grey'} "
                                f"text-color=white"
                            )
                        if r.get("tier"):
                            ui.chip(f"Tier {r['tier']}").props("dense outline")
                        if response != "none":
                            ui.chip(response).props(
                                f"dense color={_response_color(response)} text-color=white"
                            )
                        if r.get("is_stale"):
                            ui.chip("stale", icon="schedule").props("dense color=red text-color=white")
                        if r.get("comment_count"):
                            ui.chip(str(r["comment_count"]), icon="comment").props("dense outline")
                        if r.get("pending_directive_count"):
                            ui.chip(str(r["pending_directive_count"]), icon="task_alt") \
                                .props("dense color=purple text-color=white")
                        ui.label(date_str).classes("text-xs text-grey-6")

                # Line 2: snippet
                if snippet:
                    ui.label(snippet).classes("text-sm text-grey-8") \
                        .style(
                            "display: -webkit-box; "
                            "-webkit-line-clamp: 2; "
                            "-webkit-box-orient: vertical; "
                            "overflow: hidden;"
                        )


def _response_color(response: str) -> str:
    return {
        "none": "grey",
        "acked": "blue-grey",
        "engaged": "positive",
        "wontfix": "red",
        "declined": "deep-orange",
    }.get(response, "grey")
