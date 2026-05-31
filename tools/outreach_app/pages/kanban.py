"""Kanban funnel: Queued -> Posted -> Acked -> Engaged -> Closed."""

from __future__ import annotations

from nicegui import ui

from .. import data
from ..components.sidebar import render as render_sidebar
from ..components.row_drawer import open_drawer, render as render_drawer
from ..state import get_filters


COLUMN_META = [
    ("Queued", "queue", "grey", "Has not been sent to a maintainer yet."),
    ("Posted", "send", "blue", "Sent, no reply yet."),
    ("Acked", "thumb_up_alt", "blue-grey", "Maintainer acknowledged, nothing substantive."),
    ("Engaged", "forum", "positive", "Substantive reply or active conversation."),
    ("Closed", "block", "red", "Wontfix or declined."),
]


def render() -> None:
    render_drawer()
    render_sidebar()
    f = get_filters()
    columns = data.kanban_columns(filters=f)
    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-6 gap-4"):
        ui.label("Funnel kanban").classes("text-h4 font-medium")
        ui.label("Read-only in v1. Response state stays driven by YAML edits.").classes("text-grey-7")

        with ui.row().classes("w-full gap-3 items-start flex-nowrap overflow-x-auto"):
            for name, icon, color, desc in COLUMN_META:
                rows = columns.get(name, [])
                with ui.card().classes(f"min-w-[18rem] w-72 bg-grey-1"):
                    with ui.row().classes(f"items-center gap-2 p-3 border-b border-grey-3"):
                        ui.icon(icon).classes(f"text-{color}")
                        ui.label(name).classes("text-subtitle1 font-medium")
                        ui.chip(str(len(rows))).props(f"dense color={color} text-color=white")
                    with ui.column().classes("gap-2 p-2 max-h-[calc(100vh-280px)] overflow-y-auto"):
                        if not rows:
                            ui.label(_empty_message(name)).classes("text-grey-6 italic text-sm p-3")
                        for row in rows:
                            _render_card(row)


def _render_card(row: dict) -> None:
    with ui.card().classes("w-full cursor-pointer hover:bg-blue-1") \
            .on("click", lambda w=row["wave"], s=row["slug"]: open_drawer(w, s)):
        with ui.column().classes("gap-1 q-pa-sm"):
            ui.label(row["slug"]).classes("font-medium")
            with ui.row().classes("items-center gap-1"):
                if row.get("sector"):
                    ui.chip(row["sector"]).props("dense outline")
                if row.get("country"):
                    ui.chip(row["country"]).props(f"dense color={'orange' if row['country'] == 'INTL' else 'blue-grey'} text-color=white")
                if row.get("tier"):
                    ui.chip(f"T{row['tier']}").props("dense outline")
            sub_parts = []
            if row.get("rfc"):
                sub_parts.append(f"RFC-{int(row['rfc']):04d}")
            if row.get("last_touch"):
                sub_parts.append(f"touch {row['last_touch']}")
            elif row.get("sent_at"):
                sub_parts.append(f"sent {row['sent_at']}")
            if sub_parts:
                ui.label(" · ".join(sub_parts)).classes("text-xs text-grey-7")
            badges = []
            if row.get("comment_count"):
                badges.append(("comment", row["comment_count"], "grey"))
            if row.get("pending_directive_count"):
                badges.append(("task_alt", row["pending_directive_count"], "purple"))
            if row.get("is_stale"):
                badges.append(("schedule", "stale", "red"))
            if badges:
                with ui.row().classes("items-center gap-1"):
                    for icon, n, color in badges:
                        with ui.row().classes("items-center gap-0"):
                            ui.icon(icon).classes(f"text-xs text-{color}")
                            ui.label(str(n)).classes(f"text-xs text-{color}")


def _empty_message(col: str) -> str:
    return {
        "Queued": "No queued rows.",
        "Posted": "Nothing posted yet.",
        "Acked": "No acks yet.",
        "Engaged": "No engaged threads yet.",
        "Closed": "No blockers yet.",
    }.get(col, "No rows.")
