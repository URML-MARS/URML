"""Slide-in row detail drawer.

Renders the full notes, every comment + directive, and the two composers
(Add comment, Add directive). Writes go through `yaml_write` atomically.
"""

from __future__ import annotations

from nicegui import ui

from .. import data, yaml_write


_drawer_state = {"open": False, "wave": "", "slug": ""}


def open_drawer(wave: str, slug: str) -> None:
    _drawer_state["open"] = True
    _drawer_state["wave"] = wave
    _drawer_state["slug"] = slug
    _render_drawer.refresh()


def close_drawer() -> None:
    _drawer_state["open"] = False
    _render_drawer.refresh()


@ui.refreshable
def _render_drawer() -> None:
    if not _drawer_state["open"]:
        return
    wave = _drawer_state["wave"]
    slug = _drawer_state["slug"]
    target = data.get_target(wave, slug)
    if target is None:
        with ui.dialog().props("position=right maximized=false").classes("w-[40rem]") as dlg:
            with ui.card().classes("w-full h-full"):
                ui.label(f"Row not found: {slug} in {wave}").classes("text-h6 text-negative")
                ui.button("Close", on_click=lambda: (dlg.close(), close_drawer()))
        dlg.open()
        return

    comments = data.list_comments(wave, slug)
    directives = data.list_directives(wave, slug)

    with ui.dialog().props("position=right maximized=false persistent=false") as dlg:
        with ui.card().classes("w-[42rem] max-w-screen-md p-0 q-pa-none"):
            # Header
            with ui.row().classes(
                "items-center justify-between w-full p-4 bg-primary text-white sticky top-0 z-10"
            ):
                with ui.column().classes("gap-0"):
                    ui.label(target["slug"]).classes("text-h6 font-medium")
                    rfc_str = f"RFC-{int(target['rfc']):04d}" if target.get("rfc") else ""
                    sub = " · ".join(s for s in [rfc_str, target.get("sector") or "", target.get("country") or "", wave] if s)
                    ui.label(sub).classes("text-sm opacity-90")
                ui.button(icon="close", on_click=lambda: (dlg.close(), close_drawer())) \
                    .props("flat round color=white dense")

            with ui.column().classes("w-full p-4 gap-4"):
                # State chips
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    if target.get("response"):
                        ui.chip(target["response"], icon="forum").props("dense color=primary text-color=white")
                    if target.get("tier"):
                        ui.chip(f"Tier {target['tier']}").props("dense outline")
                    if target.get("posted_url"):
                        ui.link("Open posted thread ↗", target["posted_url"], new_tab=True) \
                            .classes("text-sm")

                # Contact + dates
                with ui.row().classes("items-center gap-4 text-sm text-grey-8 flex-wrap"):
                    if target.get("contact"):
                        ui.label(f"contact: {target['contact']}").classes("truncate max-w-md")
                    if target.get("sent_at"):
                        ui.label(f"sent: {target['sent_at']}")
                    if target.get("last_touch"):
                        ui.label(f"last touch: {target['last_touch']}")

                # Notes
                if target.get("notes"):
                    with ui.expansion("Notes", icon="notes", value=False).classes("w-full"):
                        ui.label(target["notes"]).classes("text-sm whitespace-pre-wrap")

                if target.get("next_action"):
                    with ui.expansion("Next action", icon="play_arrow", value=True).classes("w-full"):
                        ui.label(target["next_action"]).classes("text-sm whitespace-pre-wrap")

                ui.separator()

                # Comments
                ui.label(f"Comments ({len(comments)})").classes("text-subtitle1 font-medium")
                if not comments:
                    ui.label("No comments yet.").classes("text-grey-7 italic text-sm")
                else:
                    for c in comments:
                        with ui.card().classes("w-full bg-grey-2 q-pa-sm"):
                            ui.label(c["date"]).classes("text-xs text-grey-7")
                            ui.label(c["text"]).classes("text-sm whitespace-pre-wrap")

                # Add comment
                with ui.column().classes("w-full gap-2"):
                    comment_input = ui.textarea(
                        label="Add a comment",
                        placeholder="What were you thinking when you scanned this row?",
                    ).props("outlined autogrow").classes("w-full")

                    def submit_comment() -> None:
                        text = (comment_input.value or "").strip()
                        if not text:
                            ui.notify("Comment is empty", color="warning")
                            return
                        try:
                            yaml_write.append_comment(wave, slug, text)
                        except Exception as exc:
                            ui.notify(f"Write failed: {exc}", color="negative")
                            return
                        comment_input.value = ""
                        ui.notify("Comment saved", color="positive")
                        _refresh_db()
                        _render_drawer.refresh()

                    ui.button("Save comment", icon="add_comment", on_click=submit_comment) \
                        .props("color=primary")

                ui.separator()

                # Directives
                pending = [d for d in directives if d["status"] == "pending"]
                history = [d for d in directives if d["status"] != "pending"]
                ui.label(f"Claude directives ({len(pending)} pending)") \
                    .classes("text-subtitle1 font-medium")

                if not pending and not history:
                    ui.label("No directives yet.").classes("text-grey-7 italic text-sm")

                for d in pending:
                    with ui.card().classes("w-full bg-amber-1 q-pa-sm"):
                        with ui.row().classes("items-center justify-between w-full"):
                            ui.label(f"{d['date']} · pending").classes("text-xs text-grey-8")
                            with ui.row().classes("gap-1"):
                                ui.button(
                                    "Mark done",
                                    icon="check",
                                    on_click=lambda seq=d["seq"]: _set_status(wave, slug, seq, "done"),
                                ).props("dense color=positive flat")
                                ui.button(
                                    "Skip",
                                    icon="block",
                                    on_click=lambda seq=d["seq"]: _set_status(wave, slug, seq, "skip"),
                                ).props("dense color=grey flat")
                        ui.label(d["text"]).classes("text-sm whitespace-pre-wrap")

                if history:
                    with ui.expansion(f"History ({len(history)})", icon="history").classes("w-full"):
                        for d in history:
                            color = "positive" if d["status"] == "done" else "grey"
                            with ui.card().classes("w-full q-pa-sm"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.chip(d["status"], icon="check_circle" if d["status"] == "done" else "block") \
                                        .props(f"dense color={color} text-color=white")
                                    ui.label(d["date"]).classes("text-xs text-grey-7")
                                ui.label(d["text"]).classes("text-sm whitespace-pre-wrap")

                # Add directive
                with ui.column().classes("w-full gap-2"):
                    directive_input = ui.textarea(
                        label="Leave a directive for Claude",
                        placeholder="e.g. Draft a round-2 reply when this maintainer responds.",
                    ).props("outlined autogrow").classes("w-full")
                    status_select = ui.select(
                        options=["pending", "done", "skip"],
                        value="pending",
                        label="Status",
                    ).props("outlined dense").classes("max-w-xs")

                    def submit_directive() -> None:
                        text = (directive_input.value or "").strip()
                        if not text:
                            ui.notify("Directive is empty", color="warning")
                            return
                        try:
                            yaml_write.append_directive(wave, slug, text, status_select.value)
                        except Exception as exc:
                            ui.notify(f"Write failed: {exc}", color="negative")
                            return
                        directive_input.value = ""
                        ui.notify("Directive saved", color="positive")
                        _refresh_db()
                        _render_drawer.refresh()

                    ui.button("Save directive", icon="task", on_click=submit_directive) \
                        .props("color=primary")
    dlg.open()


def _set_status(wave: str, slug: str, seq: int, status: str) -> None:
    try:
        yaml_write.update_directive_status(wave, slug, seq, status)
    except Exception as exc:
        ui.notify(f"Write failed: {exc}", color="negative")
        return
    ui.notify(f"Marked {status}", color="positive")
    _refresh_db()
    _render_drawer.refresh()


def _refresh_db() -> None:
    """Refresh the SQLite mirror so the next read sees the new YAML state."""
    import subprocess
    import sys
    from pathlib import Path

    script = Path(__file__).resolve().parents[2] / "scripts" / "refresh_outreach_db.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)], check=False, capture_output=True)


def render() -> None:
    """Mount the drawer on a page. Call this once per page."""
    _render_drawer()
