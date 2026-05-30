"""Directives page: pending list on top, history collapsible below."""

from __future__ import annotations

from nicegui import ui

from .. import data, yaml_write
from ..components.row_drawer import open_drawer, render as render_drawer


def render() -> None:
    render_drawer()
    pending = data.pending_directives_all()
    history = data.history_directives_all()
    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-6 gap-3"):
        ui.label("Claude directives").classes("text-h4 font-medium")
        ui.label(
            "What you have asked Claude to do on a specific row. Claude reads "
            "pending directives on touching a row and marks status: done in "
            "the same commit that satisfies them."
        ).classes("text-grey-7")

        with ui.card().classes("w-full"):
            ui.label(f"Pending ({len(pending)})").classes("text-h6 mb-2")
            if not pending:
                ui.label("No pending directives.").classes("text-grey-7 italic")
            for d in pending:
                with ui.card().classes("w-full bg-amber-1 q-pa-sm"):
                    with ui.row().classes("items-center justify-between w-full"):
                        with ui.row().classes("items-center gap-2 cursor-pointer") \
                                .on("click", lambda w=d["wave"], s=d["slug"]: open_drawer(w, s)):
                            ui.chip(d["sector"] or "-").props("dense outline")
                            ui.label(d["slug"]).classes("font-medium")
                            rfc_str = f"RFC-{int(d['rfc']):04d}" if d.get("rfc") else ""
                            ui.label(rfc_str).classes("text-xs text-grey-7")
                        with ui.row().classes("items-center gap-1"):
                            ui.label(d["date"]).classes("text-xs text-grey-7")
                            ui.button(
                                "Mark done",
                                icon="check",
                                on_click=lambda d=d: _set_status(d, "done"),
                            ).props("dense color=positive flat")
                            ui.button(
                                "Skip",
                                icon="block",
                                on_click=lambda d=d: _set_status(d, "skip"),
                            ).props("dense color=grey flat")
                    ui.label(d["text"]).classes("text-sm whitespace-pre-wrap")

        with ui.card().classes("w-full"):
            ui.label(f"History ({len(history)})").classes("text-h6 mb-2")
            if not history:
                ui.label("No history yet.").classes("text-grey-7 italic")
            else:
                for d in history[:50]:
                    color = "positive" if d["status"] == "done" else "grey"
                    with ui.card().classes("w-full q-pa-sm"):
                        with ui.row().classes("items-center gap-2 w-full") \
                                .on("click", lambda w=d["wave"], s=d["slug"]: open_drawer(w, s)) \
                                .classes("cursor-pointer"):
                            ui.chip(d["status"]).props(f"dense color={color} text-color=white")
                            ui.label(d["slug"]).classes("font-medium")
                            ui.label(d["text"]).classes("text-grey-8 text-sm truncate flex-grow")
                            ui.label(d["date"]).classes("text-xs text-grey-7 whitespace-nowrap")
                if len(history) > 50:
                    ui.label(f"... showing first 50 of {len(history)}.").classes("text-grey-6 text-xs")


def _set_status(directive: dict, new_status: str) -> None:
    try:
        yaml_write.update_directive_status(
            directive["wave"], directive["slug"], directive["seq"], new_status,
        )
    except Exception as exc:
        ui.notify(f"Write failed: {exc}", color="negative")
        return
    ui.notify(f"Marked {new_status}", color="positive")
    # Trigger SQLite refresh + reload
    import subprocess
    import sys
    from pathlib import Path
    script = Path(__file__).resolve().parents[2] / "scripts" / "refresh_outreach_db.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)], check=False, capture_output=True)
    ui.navigate.reload()
