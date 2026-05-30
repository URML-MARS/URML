"""Overview page: KPI cards + funnel charts + spotlight lists."""

from __future__ import annotations

from nicegui import ui

from .. import data
from ..components.row_drawer import render as render_drawer, open_drawer
from ..state import get_filters


def _kpi(label: str, value: int, icon: str, color: str, sub: str = "") -> None:
    with ui.card().tight().classes(f"shadow-2 border-l-4 border-{color}"):
        with ui.card_section().classes("q-pa-md"):
            with ui.row().classes("items-center gap-2"):
                ui.icon(icon).classes(f"text-2xl text-{color}")
                ui.label(label).classes("text-grey-8 text-sm uppercase tracking-wide")
            ui.label(str(value)).classes("text-h3 font-medium")
            if sub:
                ui.label(sub).classes("text-grey-7 text-xs")


def render() -> None:
    render_drawer()
    kpi = data.top_line_numbers()
    sectors = data.sector_distribution()
    waves = data.funnel_by_wave()

    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-6 gap-6"):
        ui.label("URML outreach dashboard").classes("text-h4 font-medium")
        ui.label(
            "Source of truth: examples/lighthouses/outreach*.yaml. "
            "Refresh on every app launch; manual via `make outreach-refresh`."
        ).classes("text-grey-7")

        # KPI row
        with ui.row().classes("w-full gap-4 flex-wrap"):
            _kpi("Targets", kpi["total"], "track_changes", "indigo", "ledger rows total")
            _kpi("Posted", kpi["posted"], "send", "blue", "sent to a maintainer")
            _kpi("Engaged", kpi["engaged"], "forum", "positive", "substantive reply")
            _kpi("Blockers", kpi["blockers"], "block", "amber", "wontfix + declined")
            _kpi("Stale", kpi["stale"], "schedule", "red", ">= 28 days, no response")
            _kpi("Pending for Claude", kpi["pending_directives"], "task_alt", "purple", "to-do list left for me")

        ui.separator()

        # Two charts side by side
        with ui.row().classes("w-full gap-4 items-stretch"):
            with ui.card().classes("flex-grow"):
                ui.label("Funnel by sector").classes("text-h6 mb-2")
                if not sectors:
                    ui.label("No sectors yet.").classes("text-grey-7 italic")
                else:
                    _render_sector_donut(sectors)

            with ui.card().classes("flex-grow"):
                ui.label("Response state by wave").classes("text-h6 mb-2")
                if not waves:
                    ui.label("No waves yet.").classes("text-grey-7 italic")
                else:
                    _render_wave_stack(waves)

        ui.separator()

        # Spotlight lists
        with ui.row().classes("w-full gap-4 items-start"):
            with ui.card().classes("flex-grow"):
                ui.label("Most recent engagement").classes("text-h6 mb-2")
                f = get_filters()
                f.responses = ["engaged"]
                rows = data.list_targets(filters=f, limit=5)
                if not rows:
                    ui.label("No engaged threads yet.").classes("text-grey-7 italic")
                else:
                    _render_spotlight_rows(rows)

            with ui.card().classes("flex-grow"):
                ui.label("Needs attention").classes("text-h6 mb-2")
                ui.label(
                    "Stale threads (≥ 28 d, no response) + pending Claude directives."
                ).classes("text-grey-7 text-sm mb-1")
                stale_rows = [
                    r for r in data.list_targets(limit=200)
                    if r.get("is_stale")
                ][:5]
                pending = data.pending_directives_all()[:5]
                if not stale_rows and not pending:
                    ui.label("Nothing needs attention right now.").classes("text-grey-7 italic")
                else:
                    if pending:
                        ui.label(f"Pending directives ({len(data.pending_directives_all())})").classes("text-subtitle2")
                        for d in pending:
                            with ui.row().classes("items-center gap-2 cursor-pointer w-full") \
                                    .on("click", lambda w=d["wave"], s=d["slug"]: open_drawer(w, s)):
                                ui.icon("task_alt").classes("text-purple")
                                ui.label(d["slug"]).classes("font-medium")
                                ui.label(d["text"]).classes("text-grey-8 text-sm truncate flex-grow")
                                ui.label(d["date"]).classes("text-grey-6 text-xs")
                    if stale_rows:
                        ui.label(f"Stale threads ({len([r for r in data.list_targets(limit=2000) if r['is_stale']])})") \
                            .classes("text-subtitle2 mt-3")
                        _render_spotlight_rows(stale_rows)


def _render_spotlight_rows(rows: list[dict]) -> None:
    for r in rows:
        with ui.row().classes("items-center gap-2 cursor-pointer w-full") \
                .on("click", lambda w=r["wave"], s=r["slug"]: open_drawer(w, s)):
            ui.chip(r["sector"] or "-").props("dense outline")
            ui.label(r["slug"]).classes("font-medium")
            ui.label(r.get("contact") or "").classes("text-grey-8 text-sm truncate flex-grow")
            ui.label(r.get("last_touch") or r.get("sent_at") or "").classes("text-grey-6 text-xs")


def _render_sector_donut(sectors: list[dict]) -> None:
    data_pairs = [{"value": s["total"], "name": s["sector"]} for s in sectors]
    ui.echart(
        {
            "tooltip": {"trigger": "item"},
            "legend": {"orient": "vertical", "left": "left", "type": "scroll"},
            "series": [
                {
                    "name": "Sector",
                    "type": "pie",
                    "radius": ["45%", "70%"],
                    "avoidLabelOverlap": True,
                    "itemStyle": {"borderRadius": 6, "borderColor": "#fff", "borderWidth": 2},
                    "label": {"show": False, "position": "center"},
                    "emphasis": {"label": {"show": True, "fontSize": 16, "fontWeight": "bold"}},
                    "labelLine": {"show": False},
                    "data": data_pairs,
                }
            ],
        }
    ).classes("h-64")


def _render_wave_stack(waves: list[dict]) -> None:
    labels = [f"Move {w['move_num']}" for w in waves]
    posted = [(w["posted"] or 0) - (w["engaged"] or 0) - (w["wontfix"] or 0) - (w["declined"] or 0) for w in waves]
    posted = [max(0, p) for p in posted]
    engaged = [w["engaged"] or 0 for w in waves]
    wontfix = [w["wontfix"] or 0 for w in waves]
    declined = [w["declined"] or 0 for w in waves]
    queued = [(w["total"] or 0) - (w["posted"] or 0) for w in waves]
    queued = [max(0, q) for q in queued]
    ui.echart(
        {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "legend": {"data": ["queued", "posted (no reply)", "engaged", "wontfix", "declined"]},
            "grid": {"left": 70, "right": 20, "top": 30, "bottom": 30},
            "xAxis": {"type": "value"},
            "yAxis": {"type": "category", "data": labels, "inverse": True},
            "series": [
                {"name": "queued", "type": "bar", "stack": "wave", "data": queued, "itemStyle": {"color": "#9e9e9e"}},
                {"name": "posted (no reply)", "type": "bar", "stack": "wave", "data": posted, "itemStyle": {"color": "#42a5f5"}},
                {"name": "engaged", "type": "bar", "stack": "wave", "data": engaged, "itemStyle": {"color": "#66bb6a"}},
                {"name": "wontfix", "type": "bar", "stack": "wave", "data": wontfix, "itemStyle": {"color": "#ef5350"}},
                {"name": "declined", "type": "bar", "stack": "wave", "data": declined, "itemStyle": {"color": "#ffa726"}},
            ],
        }
    ).classes("h-96")
