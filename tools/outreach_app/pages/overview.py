"""Overview page: KPI cards + funnel charts + spotlight feeds."""

from __future__ import annotations

import re

from nicegui import ui

from .. import data
from ..components.row_drawer import render as render_drawer, open_drawer
from ..state import get_filters


# Sector → (label, icon, accent color). Used in the engagement feed and
# in the needs-attention list so each sector reads at a glance.
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


def _kpi(label: str, value: int, icon: str, color: str, sub: str = "") -> None:
    with ui.card().tight().classes(f"shadow-2 border-l-4 border-{color}"):
        with ui.card_section().classes("q-pa-md"):
            with ui.row().classes("items-center gap-2"):
                ui.icon(icon).classes(f"text-2xl text-{color}")
                ui.label(label).classes("text-grey-8 text-sm uppercase tracking-wide")
            ui.label(str(value)).classes("text-h3 font-medium")
            if sub:
                ui.label(sub).classes("text-grey-7 text-xs")


def _first_sentence(text: str, max_chars: int = 180) -> str:
    """Pick the first sentence or first ~180 chars from a notes blob."""
    text = (text or "").strip()
    if not text:
        return ""
    # Split on '. ' but keep the first chunk meaningful.
    parts = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)
    head = parts[0]
    if len(head) > max_chars:
        head = head[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return head


def render() -> None:
    render_drawer()
    kpi = data.top_line_numbers()
    funnel = data.funnel_stage_counts()
    sectors = data.sector_distribution()
    waves = data.funnel_by_wave()

    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-6 gap-6"):
        ui.label("URML outreach dashboard").classes("text-h4 font-medium")
        ui.label(
            "Source of truth: examples/lighthouses/outreach*.yaml. "
            "SQLite mirror regenerated on launch."
        ).classes("text-grey-7")

        # KPI row
        with ui.row().classes("w-full gap-4 flex-wrap"):
            _kpi("Targets", kpi["total"], "track_changes", "indigo", "ledger rows total")
            _kpi("Posted", kpi["posted"], "send", "blue", "sent to a maintainer")
            _kpi("Engaged", kpi["engaged"], "forum", "positive", "substantive reply")
            _kpi("Blockers", kpi["blockers"], "block", "amber", "wontfix + declined")
            _kpi("Stale", kpi["stale"], "schedule", "red", ">= 28 days, no response")
            _kpi("Pending for Claude", kpi["pending_directives"], "task_alt", "purple", "to-do list left for me")

        # Conversion funnel (full-width card directly under the KPI row)
        with ui.card().classes("w-full"):
            ui.label("Conversion funnel").classes("text-h6 mb-1")
            ui.label(
                "Where rows are in the pipeline. Each step shows the count, "
                "share of total, and conversion rate from the prior step."
            ).classes("text-grey-7 text-sm mb-3")
            if not funnel or funnel["total"] == 0:
                ui.label("No targets yet.").classes("text-grey-7 italic")
            else:
                _render_conversion_funnel(funnel)

        ui.separator()

        # Two charts side by side
        with ui.row().classes("w-full gap-4 items-stretch flex-wrap"):
            with ui.card().classes("flex-grow min-w-[360px] max-w-[460px]"):
                ui.label("Sectors").classes("text-h6 mb-1")
                ui.label("Total rows per sector with engagement rate.") \
                    .classes("text-grey-7 text-sm mb-2")
                if not sectors:
                    ui.label("No sectors yet (run the schema-v2 migration).") \
                        .classes("text-grey-7 italic")
                else:
                    _render_sector_list(sectors)

            with ui.card().classes("flex-grow min-w-[420px]"):
                ui.label("Funnel by sector").classes("text-h6 mb-1")
                ui.label(
                    "Each row stacks queued/posted (blue) + engaged (green) + "
                    "wontfix/declined (red)."
                ).classes("text-grey-7 text-sm mb-2")
                if not sectors:
                    ui.label("No sectors yet.").classes("text-grey-7 italic")
                else:
                    _render_sector_bar(sectors)

        # Response state by wave on its own row (full width)
        with ui.card().classes("w-full"):
            ui.label("Response state by wave").classes("text-h6 mb-1")
            ui.label(
                "Each row is a Move (1-18). Stacks: queued / posted-no-reply / "
                "engaged / wontfix / declined."
            ).classes("text-grey-7 text-sm mb-2")
            if not waves:
                ui.label("No waves yet.").classes("text-grey-7 italic")
            else:
                _render_wave_stack(waves)

        ui.separator()

        # Spotlight feeds
        with ui.row().classes("w-full gap-4 items-start flex-wrap"):
            with ui.card().classes("flex-grow min-w-[420px]"):
                ui.label("Most recent engagement").classes("text-h6 mb-2")
                ui.label("Maintainer wrote back. Newest first.") \
                    .classes("text-grey-7 text-sm mb-2")
                f = get_filters()
                f.responses = ["engaged"]
                rows = data.list_targets(filters=f, limit=5)
                if not rows:
                    ui.label("No engaged threads yet.").classes("text-grey-7 italic")
                else:
                    _render_engagement_feed(rows)

            with ui.card().classes("flex-grow min-w-[420px]"):
                ui.label("Needs attention").classes("text-h6 mb-2")
                ui.label(
                    "Stale threads (≥ 28 days, no response) + pending Claude directives."
                ).classes("text-grey-7 text-sm mb-2")
                stale_rows = [
                    r for r in data.list_targets(limit=2000)
                    if r.get("is_stale")
                ][:5]
                pending = data.pending_directives_all()
                if not stale_rows and not pending:
                    ui.label("Nothing needs attention right now.") \
                        .classes("text-grey-7 italic")
                else:
                    if pending:
                        ui.label(f"Pending directives ({len(pending)})") \
                            .classes("text-subtitle2 mt-1")
                        for d in pending[:5]:
                            _directive_row(d)
                    if stale_rows:
                        ui.label(
                            f"Stale threads "
                            f"({sum(1 for r in data.list_targets(limit=2000) if r['is_stale'])})"
                        ).classes("text-subtitle2 mt-3")
                        _render_engagement_feed(stale_rows)


# -----------------------------------------------------------------------------
# Spotlight feed (story-style)
# -----------------------------------------------------------------------------


def _render_engagement_feed(rows: list[dict]) -> None:
    """Feed of story-style cards for the Overview spotlights."""
    with ui.column().classes("w-full gap-3"):
        for r in rows:
            _engagement_card(r)


def _engagement_card(r: dict) -> None:
    sector = r.get("sector") or ""
    label, icon, color = SECTOR_META.get(sector, (sector or "—", "circle", "grey-6"))
    snippet = _first_sentence(r.get("next_action") or r.get("notes") or "")
    rfc_str = f"RFC-{int(r['rfc']):04d}" if r.get("rfc") else ""
    date_str = r.get("last_touch") or r.get("sent_at") or ""

    with ui.card().classes("w-full cursor-pointer hover:bg-blue-1") \
            .on("click", lambda w=r["wave"], s=r["slug"]: open_drawer(w, s)):
        with ui.row().classes("items-start gap-3 w-full no-wrap q-pa-md"):
            # Sector avatar
            with ui.element("div").classes(
                f"flex items-center justify-center rounded-full bg-{color} text-white "
                f"shrink-0"
            ).style("width: 40px; height: 40px"):
                ui.icon(icon).classes("text-lg")

            # Body
            with ui.column().classes("gap-1 flex-grow min-w-0"):
                # Title row
                with ui.row().classes("items-center gap-2 w-full no-wrap"):
                    ui.label(r["slug"]).classes("text-subtitle1 font-medium")
                    if rfc_str:
                        ui.label(rfc_str).classes("text-xs text-grey-7")
                    ui.space()
                    ui.label(date_str).classes("text-xs text-grey-6 whitespace-nowrap")

                # Meta row
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.chip(label).props(f"dense outline text-color={color}")
                    if r.get("country"):
                        ui.chip(r["country"]).props(
                            f"dense color={'orange' if r['country'] == 'INTL' else 'blue-grey'} "
                            f"text-color=white"
                        )
                    if r.get("tier"):
                        ui.chip(f"Tier {r['tier']}").props("dense outline")
                    resp = r.get("response") or "none"
                    if resp != "none":
                        ui.chip(resp).props(
                            f"dense color={_response_color(resp)} text-color=white"
                        )

                # Story snippet
                if snippet:
                    ui.label(snippet).classes("text-sm text-grey-8")

                # Optional outbound link
                if r.get("posted_url"):
                    ui.link("Open thread ↗", r["posted_url"], new_tab=True) \
                        .classes("text-xs text-blue-7")


def _directive_row(d: dict) -> None:
    with ui.row().classes("items-center gap-2 cursor-pointer w-full hover:bg-amber-1 q-pa-xs") \
            .on("click", lambda w=d["wave"], s=d["slug"]: open_drawer(w, s)):
        ui.icon("task_alt").classes("text-purple")
        ui.label(d["slug"]).classes("font-medium")
        ui.label(d["text"]).classes("text-grey-8 text-sm flex-grow") \
            .style("white-space: nowrap; overflow: hidden; text-overflow: ellipsis")
        ui.label(d["date"]).classes("text-grey-6 text-xs whitespace-nowrap")


def _response_color(response: str) -> str:
    return {
        "none": "grey",
        "acked": "blue-grey",
        "engaged": "positive",
        "wontfix": "red",
        "declined": "deep-orange",
    }.get(response, "grey")


# -----------------------------------------------------------------------------
# Charts
# -----------------------------------------------------------------------------


# Conversion funnel stages — fixed order. The "key" matches funnel_stage_counts().
_FUNNEL_STAGES = [
    {"key": "queued",  "label": "Queued",  "icon": "schedule",   "color": "grey-6",      "hint": "not yet sent"},
    {"key": "posted",  "label": "Posted",  "icon": "send",       "color": "blue-7",      "hint": "sent, no reply yet"},
    {"key": "acked",   "label": "Acked",   "icon": "done",       "color": "light-blue-7", "hint": "noticed, no substantive reply"},
    {"key": "engaged", "label": "Engaged", "icon": "forum",      "color": "positive",    "hint": "substantive reply"},
    {"key": "closed",  "label": "Closed",  "icon": "block",      "color": "red-6",       "hint": "wontfix + declined"},
]


def _pct(num: int, denom: int) -> str:
    return f"{(100.0 * num / denom):.1f} %" if denom else "—"


def _render_conversion_funnel(funnel: dict) -> None:
    """Five stage cards in a row. Each card shows count + % of total +
    conversion from the prior non-zero stage. No mock data: zero stages
    render their zero count truthfully.
    """
    total = funnel["total"]
    prev_count: int | None = None
    with ui.row().classes("w-full gap-3 items-stretch flex-wrap"):
        for i, stage in enumerate(_FUNNEL_STAGES):
            count = funnel.get(stage["key"], 0)
            share = _pct(count, total)
            from_prior = (
                "first stage" if i == 0 else
                _pct(count, prev_count) + " of prior" if prev_count else "—"
            )
            with ui.card().tight().classes(
                f"flex-grow basis-[180px] shadow-1 border-l-4 border-{stage['color']}"
            ):
                with ui.card_section().classes("q-pa-md"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon(stage["icon"]).classes(f"text-{stage['color']}")
                        ui.label(stage["label"]).classes(
                            "text-grey-8 text-sm uppercase tracking-wide"
                        )
                    ui.label(str(count)).classes("text-h4 font-medium")
                    ui.label(f"{share} of total").classes("text-grey-7 text-xs")
                    ui.label(from_prior).classes("text-grey-6 text-xs")
                    ui.label(stage["hint"]).classes("text-grey-5 text-xs mt-1 italic")
                # Share-of-total progress bar at the bottom of the card
                bar_pct = (100.0 * count / total) if total else 0.0
                ui.linear_progress(
                    value=min(1.0, count / total) if total else 0.0,
                    show_value=False,
                ).props(f"color={stage['color']}").classes("q-mt-none") \
                    .tooltip(f"{count} of {total} = {bar_pct:.1f} % of total")
            prev_count = count


def _render_sector_list(sectors: list[dict]) -> None:
    """Compact list of sectors with totals + engagement rate. Click to filter."""
    sectors_sorted = sorted(sectors, key=lambda s: s["total"], reverse=True)
    with ui.column().classes("w-full gap-1"):
        for s in sectors_sorted:
            sector = s["sector"]
            label, icon, color = SECTOR_META.get(sector, (sector, "circle", "grey-6"))
            total = s.get("total", 0)
            engaged = s.get("engaged", 0)
            blockers = s.get("blockers", 0)
            posted = s.get("posted", 0) or 0
            rate = (engaged / posted * 100.0) if posted else 0.0
            with ui.row().classes(
                "items-center gap-2 w-full no-wrap cursor-pointer hover:bg-grey-2 q-pa-xs rounded"
            ).on("click", lambda v=sector: _filter_by_sector(v)):
                ui.icon(icon).classes(f"text-{color}")
                ui.label(label).classes("text-sm font-medium flex-grow truncate")
                ui.label(str(total)).classes("text-sm font-medium w-10 text-right")
                if engaged:
                    ui.chip(f"{engaged} engaged").props("dense color=positive text-color=white")
                if blockers:
                    ui.chip(f"{blockers} blocker{'s' if blockers != 1 else ''}") \
                        .props("dense color=red text-color=white")
                ui.label(f"{rate:.0f}%" if posted else "—") \
                    .classes("text-xs text-grey-6 w-10 text-right") \
                    .tooltip("Engagement rate among posted rows.")


def _filter_by_sector(sector: str) -> None:
    """Set the sector filter then navigate to /targets."""
    from ..state import set_filters
    from ..data import Filters
    set_filters(Filters(sectors=[sector]))
    ui.navigate.to("/targets")


def _render_sector_bar(sectors: list[dict]) -> None:
    """Horizontal bar (one per sector). Sorted desc by total."""
    sectors_sorted = sorted(sectors, key=lambda s: s["total"], reverse=True)
    names = [s["sector"] for s in sectors_sorted]
    totals = [s["total"] for s in sectors_sorted]
    engaged = [s.get("engaged", 0) for s in sectors_sorted]
    blockers = [s.get("blockers", 0) for s in sectors_sorted]
    rest = [t - e - b for t, e, b in zip(totals, engaged, blockers)]
    rest = [max(0, r) for r in rest]

    height_px = max(280, 28 * len(sectors_sorted) + 80)

    ui.echart(
        {
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
            },
            "legend": {"data": ["posted / queued", "engaged", "wontfix + declined"], "top": 0},
            "grid": {"left": 160, "right": 50, "top": 40, "bottom": 20, "containLabel": False},
            "xAxis": {"type": "value", "splitLine": {"show": True, "lineStyle": {"color": "#eee"}}},
            "yAxis": {
                "type": "category",
                "data": names,
                "inverse": True,
                "axisLabel": {"fontSize": 12},
            },
            "series": [
                {
                    "name": "posted / queued",
                    "type": "bar",
                    "stack": "sector",
                    "data": rest,
                    "itemStyle": {"color": "#90caf9"},
                },
                {
                    "name": "engaged",
                    "type": "bar",
                    "stack": "sector",
                    "data": engaged,
                    "itemStyle": {"color": "#66bb6a"},
                },
                {
                    "name": "wontfix + declined",
                    "type": "bar",
                    "stack": "sector",
                    "data": blockers,
                    "itemStyle": {"color": "#ef5350"},
                },
            ],
        }
    ).style(f"height: {height_px}px")


def _render_wave_stack(waves: list[dict]) -> None:
    labels = [f"Move {w['move_num']}" for w in waves]
    queued = [max(0, (w["total"] or 0) - (w["posted"] or 0)) for w in waves]
    posted = [
        max(0, (w["posted"] or 0) - (w["engaged"] or 0) - (w["wontfix"] or 0) - (w["declined"] or 0))
        for w in waves
    ]
    engaged = [w["engaged"] or 0 for w in waves]
    wontfix = [w["wontfix"] or 0 for w in waves]
    declined = [w["declined"] or 0 for w in waves]
    totals = [w["total"] or 0 for w in waves]

    height_px = max(360, 26 * len(waves) + 80)

    ui.echart(
        {
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "formatter": None,
            },
            "legend": {
                "data": ["queued", "posted (no reply)", "engaged", "wontfix", "declined"],
                "top": 0,
            },
            "grid": {"left": 80, "right": 60, "top": 40, "bottom": 20, "containLabel": False},
            "xAxis": {
                "type": "value",
                "splitLine": {"show": True, "lineStyle": {"color": "#eee"}},
            },
            "yAxis": {
                "type": "category",
                "data": labels,
                "inverse": True,
                "axisLabel": {"fontSize": 12},
            },
            "series": [
                {
                    "name": "queued",
                    "type": "bar",
                    "stack": "wave",
                    "data": queued,
                    "itemStyle": {"color": "#bdbdbd"},
                },
                {
                    "name": "posted (no reply)",
                    "type": "bar",
                    "stack": "wave",
                    "data": posted,
                    "itemStyle": {"color": "#42a5f5"},
                },
                {
                    "name": "engaged",
                    "type": "bar",
                    "stack": "wave",
                    "data": engaged,
                    "itemStyle": {"color": "#66bb6a"},
                },
                {
                    "name": "wontfix",
                    "type": "bar",
                    "stack": "wave",
                    "data": wontfix,
                    "itemStyle": {"color": "#ef5350"},
                },
                {
                    "name": "declined",
                    "type": "bar",
                    "stack": "wave",
                    "data": declined,
                    "itemStyle": {"color": "#ffa726"},
                },
            ],
        }
    ).style(f"height: {height_px}px")
