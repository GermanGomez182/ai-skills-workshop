#!/usr/bin/env python3
"""Render the weekly report as one self-contained, dark-mode HTML page.

Input: one week of Garmin-shaped JSON (shape documented in
generate_charts.py), optionally with the agent's own prose:

    "narrative": {
      "summary":          ["3 to 5 executive summary sentences"],
      "things_to_watch":  ["hedged, non-medical things to watch"],
      "interpretations":  [{"data": "...", "observation": "...",
                            "interpretation": "..."}]
    }

Numbers, comparisons and notable days are computed here from the
data (weekly_metrics.py). Without a narrative the page falls back to
the one template interpretation this Skill allows.

The page loads nothing from the network: inline CSS, inline SVG
charts, a few lines of JS for tooltips. It works offline on stage.
Standard library only: runs with any python3, no virtualenv.

Usage:

    python3 generate_html.py --input week.json --output weekly-report.html
"""

import argparse
import math
from datetime import date
from html import escape
from pathlib import Path

from weekly_metrics import (
    acute_load_change,
    day_flags,
    fmt,
    fmt_minutes,
    load_vs_recovery_note,
    load_week,
    summarize_week,
    with_coverage,
)

SERIES_DAILY = "var(--series-1)"
SERIES_GARMIN = "var(--series-2)"

CHART_WIDTH = 560
CHART_HEIGHT = 220
PLOT_TOP = 16
PLOT_BOTTOM = 188
PLOT_LEFT = 40
PLOT_RIGHT = 548
BAR_WIDTH = 22
BAR_RADIUS = 4
GRID_TICKS = 4

FLAG_ROWS = ("Resting HR", "HRV", "Sleep score", "Training readiness", "Stress")
FLAG_ROW_FIELDS = {
    "Resting HR": "resting_hr",
    "HRV": "hrv",
    "Sleep score": "sleep_score",
    "Training readiness": "training_readiness",
    "Stress": "stress_avg",
}

TABLE_COLUMNS = (
    (
        "Training",
        lambda d: fmt(
            sum(a.get("duration_min", 0) for a in d.get("activities", [])), " min"
        ),
    ),
    ("Resting HR", lambda d: fmt(d.get("resting_hr"), " bpm")),
    ("Garmin 7d RHR", lambda d: fmt(d.get("resting_hr_7d_avg"), " bpm")),
    ("HRV", lambda d: fmt(d.get("hrv"), " ms")),
    ("Garmin weekly HRV", lambda d: fmt(d.get("hrv_weekly_avg"), " ms")),
    ("Sleep", lambda d: fmt_minutes(d.get("sleep_duration_min"))),
    ("Sleep score", lambda d: fmt(d.get("sleep_score"))),
    ("Readiness", lambda d: fmt(d.get("training_readiness"))),
    ("Stress", lambda d: fmt(d.get("stress_avg"))),
    (
        "Body Battery",
        lambda d: f"{fmt(d.get('body_battery_min'))}-{fmt(d.get('body_battery_max'))}",
    ),
    ("Acute load", lambda d: fmt(d.get("acute_load"))),
)


def e(text) -> str:
    return escape(str(text), quote=True)


def day_label(iso_date: str) -> str:
    return date.fromisoformat(iso_date).strftime("%a %d")


def period_label(start: str, end: str) -> str:
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    return f"{first:%b} {first.day} - {last:%b} {last.day}, {last.year}"


def nice_ceiling(value: float) -> float:
    if value <= 0:
        return 1
    magnitude = 10 ** (len(str(int(value))) - 1)
    for step in (1, 2, 2.5, 5, 10):
        if value <= step * magnitude:
            return step * magnitude
    return 10 * magnitude


def whole_number_range(lo: float, hi: float) -> tuple[int, int]:
    """Axis range padded around the data, with GRID_TICKS whole-number steps."""
    lo, hi = lo - 1, hi + 1
    raw_step = max(1, math.ceil((hi - lo) / GRID_TICKS))
    magnitude = 10 ** (len(str(raw_step)) - 1)
    step = next(m * magnitude for m in (1, 2, 5, 10) if raw_step <= m * magnitude)
    start = math.floor(lo / step) * step
    while start + step * GRID_TICKS < hi:
        start += step
    return start, start + step * GRID_TICKS


def band_centers(count: int) -> list[float]:
    band = (PLOT_RIGHT - PLOT_LEFT) / count
    return [PLOT_LEFT + band * (i + 0.5) for i in range(count)]


def y_scale(lo: float, hi: float):
    span = (hi - lo) or 1
    return lambda v: PLOT_BOTTOM - (v - lo) / span * (PLOT_BOTTOM - PLOT_TOP)


def grid(lo: float, hi: float, unit: str) -> str:
    y = y_scale(lo, hi)
    lines = []
    for i in range(GRID_TICKS + 1):
        value = lo + (hi - lo) * i / GRID_TICKS
        cls = "baseline" if i == 0 else "gridline"
        lines.append(
            f'<line class="{cls}" x1="{PLOT_LEFT}" x2="{PLOT_RIGHT}" y1="{y(value):.1f}" y2="{y(value):.1f}"/>'
            f'<text class="tick" x="{PLOT_LEFT - 8}" y="{y(value) + 4:.1f}" text-anchor="end">{value:g}{e(unit)}</text>'
        )
    return "".join(lines)


def x_labels(labels: list[str]) -> str:
    return "".join(
        f'<text class="tick" x="{x:.1f}" y="{PLOT_BOTTOM + 20}" text-anchor="middle">{e(label)}</text>'
        for x, label in zip(band_centers(len(labels)), labels)
    )


def hit_areas(labels: list[str], tips: list[str]) -> str:
    band = (PLOT_RIGHT - PLOT_LEFT) / len(labels)
    return "".join(
        f'<rect class="hit" x="{x - band / 2:.1f}" y="{PLOT_TOP}" width="{band:.1f}" '
        f'height="{PLOT_BOTTOM - PLOT_TOP}" tabindex="0" data-tip="{e(tip)}"/>'
        for x, tip in zip(band_centers(len(labels)), tips)
    )


def rounded_top_bar(x: float, top: float, bottom: float) -> str:
    left, right = x - BAR_WIDTH / 2, x + BAR_WIDTH / 2
    r = min(BAR_RADIUS, (bottom - top) / 2)
    return (
        f'<path class="bar" d="M{left:.1f},{bottom:.1f} V{top + r:.1f} Q{left:.1f},{top:.1f} {left + r:.1f},{top:.1f} '
        f'H{right - r:.1f} Q{right:.1f},{top:.1f} {right:.1f},{top + r:.1f} V{bottom:.1f} Z"/>'
    )


def svg(chart_id: str, title: str, body: str) -> str:
    return (
        f'<svg id="{chart_id}" class="chart" viewBox="0 0 {CHART_WIDTH} {CHART_HEIGHT}" role="img" '
        f'aria-label="{e(title)}">{body}</svg>'
    )


def column_chart(
    chart_id: str, title: str, labels: list[str], values: list, unit: str, fmt_value
) -> str:
    present = [v for v in values if v]
    hi = nice_ceiling(max(present) if present else 0)
    y = y_scale(0, hi)
    bars, peak = [], max(present) if present else None
    for x, v in zip(band_centers(len(labels)), values):
        if not v:
            continue
        bars.append(rounded_top_bar(x, y(v), PLOT_BOTTOM))
        if v == peak:
            bars.append(
                f'<text class="value-label" x="{x:.1f}" y="{y(v) - 8:.1f}" text-anchor="middle">{e(fmt_value(v))}</text>'
            )
    tips = [
        f"{label}\n{fmt_value(v) if v else 'no data'}"
        for label, v in zip(labels, values)
    ]
    body = (
        grid(0, hi, unit) + "".join(bars) + x_labels(labels) + hit_areas(labels, tips)
    )
    return chart_card(title, svg(chart_id, title, body))


def line_path(xs: list[float], values: list, y) -> str:
    segments, current = [], []
    for x, v in zip(xs, values):
        if v is None:
            if current:
                segments.append(current)
            current = []
            continue
        current.append(f"{x:.1f},{y(v):.1f}")
    if current:
        segments.append(current)
    return "".join(f"M{' L'.join(seg)}" for seg in segments)


def line_series(xs: list[float], values: list, y, color: str) -> str:
    dots = "".join(
        f'<circle class="dot" cx="{x:.1f}" cy="{y(v):.1f}" r="4" fill="{color}"/>'
        for x, v in zip(xs, values)
        if v is not None
    )
    return f'<path class="line" d="{line_path(xs, values, y)}" stroke="{color}"/>{dots}'


def legend(entries: list[tuple[str, str]]) -> str:
    items = "".join(
        f'<span class="legend-item"><span class="line-key" style="background:{color}"></span>{e(name)}</span>'
        for name, color in entries
    )
    return f'<div class="legend">{items}</div>'


def vs_garmin_chart(
    chart_id: str, title: str, week: dict, field: str, avg_field: str, unit: str
) -> str:
    days = week["days"]
    labels = [day_label(d["date"]) for d in days]
    daily = [d.get(field) for d in days]
    garmin = [d.get(avg_field) for d in days]
    present = [v for v in daily + garmin if v is not None]
    if not present:
        return chart_card(title, '<p class="empty">No data this week.</p>')
    lo, hi = whole_number_range(min(present), max(present))
    y = y_scale(lo, hi)
    xs = band_centers(len(days))
    tips = [
        f"{label}\n{fmt(v, unit)} daily\n{fmt(g, unit)} Garmin avg"
        for label, v, g in zip(labels, daily, garmin)
    ]
    body = (
        grid(lo, hi, "")
        + line_series(xs, garmin, y, SERIES_GARMIN)
        + line_series(xs, daily, y, SERIES_DAILY)
        + x_labels(labels)
        + hit_areas(labels, tips)
    )
    return chart_card(
        title,
        legend([("Daily", SERIES_DAILY), ("Garmin average", SERIES_GARMIN)])
        + svg(chart_id, title, body),
    )


def range_chart(chart_id: str, title: str, week: dict) -> str:
    days = week["days"]
    labels = [day_label(d["date"]) for d in days]
    y = y_scale(0, 100)
    bars = []
    for x, d in zip(band_centers(len(days)), days):
        lo, hi = d.get("body_battery_min"), d.get("body_battery_max")
        if lo is None or hi is None:
            continue
        bars.append(
            f'<rect class="bar" x="{x - BAR_WIDTH / 2:.1f}" y="{y(hi):.1f}" width="{BAR_WIDTH}" '
            f'height="{y(lo) - y(hi):.1f}" rx="{BAR_RADIUS}"/>'
        )
    tips = [
        f"{label}\nhigh {fmt(d.get('body_battery_max'))}\nlow {fmt(d.get('body_battery_min'))}"
        for label, d in zip(labels, days)
    ]
    body = grid(0, 100, "") + "".join(bars) + x_labels(labels) + hit_areas(labels, tips)
    return chart_card(title, svg(chart_id, title, body))


def chart_card(title: str, content: str) -> str:
    return f'<figure class="card chart-card"><figcaption>{e(title)}</figcaption>{content}</figure>'


def stat_tile(label: str, value: str, note: str = "") -> str:
    note_html = f'<div class="tile-note">{e(note)}</div>' if note else ""
    return f'<div class="card tile"><div class="tile-label">{e(label)}</div><div class="tile-value">{e(value)}</div>{note_html}</div>'


def section(section_id: str, title: str, content: str) -> str:
    return f'<section id="{section_id}"><h2 class="section-title">{e(title)}</h2>{content}</section>'


def bullet_list(items: list[str]) -> str:
    return (
        '<ul class="bullets">'
        + "".join(f"<li>{e(item)}</li>" for item in items)
        + "</ul>"
    )


def fallback_summary(week: dict, summary: dict) -> list[str]:
    flagged_days = sum(1 for d in week["days"] if day_flags(d))
    items = [
        f"{summary['activity_count']} activities, {fmt_minutes(summary['total_duration_min'])} total.",
        f"{flagged_days} of {summary['day_count']} days crossed a threshold.",
    ]
    note = load_vs_recovery_note(week)
    return items + [note] if note else items


def hero(week: dict, summary: dict) -> str:
    return f"""
<header class="hero">
  <div class="eyebrow">Garmin Connect &middot; weekly performance report</div>
  <h1>{e(period_label(summary["period"][0], summary["period"][1]))}</h1>
  <div class="hero-figure">{e(fmt_minutes(summary["total_duration_min"]))}</div>
  <div class="hero-caption">Total training time</div>
</header>"""


def kpi_row(summary: dict) -> str:
    return tile_row(
        stat_tile(
            "Avg sleep",
            fmt_minutes(summary["sleep_duration_min"]),
            coverage_note(summary, "sleep_duration_min"),
        ),
        stat_tile("Avg HRV", fmt(summary["hrv"], " ms"), coverage_note(summary, "hrv")),
        stat_tile(
            "Avg resting HR",
            fmt(summary["resting_hr"], " bpm"),
            coverage_note(summary, "resting_hr"),
        ),
        stat_tile(
            "Avg readiness",
            fmt(summary["training_readiness"]),
            coverage_note(summary, "training_readiness"),
        ),
    )


def tile_row(*tiles: str) -> str:
    return '<div class="tiles">' + "".join(tiles) + "</div>"


def coverage_note(summary: dict, metric: str) -> str:
    return with_coverage("", summary, metric).strip().strip("()") or "all 7 days"


def training_section(week: dict, summary: dict) -> str:
    days = week["days"]
    labels = [day_label(d["date"]) for d in days]
    minutes = [
        sum(a.get("duration_min", 0) for a in d.get("activities", [])) for d in days
    ]
    loads = [d.get("acute_load") for d in days]
    distribution = "".join(
        f'<li><span class="dist-name">{e(kind.replace("_", " "))}</span>'
        f'<span class="dist-track"><span class="dist-fill" style="width:{count / summary["activity_count"] * 100:.0f}%"></span></span>'
        f'<span class="dist-count">{count}</span></li>'
        for kind, count in sorted(
            summary["distribution"].items(), key=lambda kv: -kv[1]
        )
    )
    load = summary["acute_load_change"]
    return section(
        "training",
        "Training",
        tile_row(
            stat_tile("Activities", str(summary["activity_count"])),
            stat_tile("Rest days", str(summary["rest_days"])),
            stat_tile(
                "Acute load, week",
                f"{load:+.0f}%" if load is not None else "n/a",
                "first day -> last day",
            ),
        )
        + '<div class="grid-2">'
        + column_chart(
            "chart-training",
            "Training time by day",
            labels,
            minutes,
            "",
            lambda v: f"{v:.0f} min",
        )
        + column_chart(
            "chart-load",
            "Garmin acute load by day",
            labels,
            loads,
            "",
            lambda v: f"{v:.0f}",
        )
        + "</div>"
        + f'<div class="card"><div class="card-title">Activity distribution</div><ul class="distribution">{distribution or "<li>No activities logged.</li>"}</ul></div>',
    )


def recovery_section(week: dict, summary: dict) -> str:
    labels = [day_label(d["date"]) for d in week["days"]]
    readiness = [d.get("training_readiness") for d in week["days"]]
    battery = f"{fmt(summary['body_battery_max'])} / {fmt(summary['body_battery_min'])}"
    return section(
        "recovery",
        "Recovery",
        tile_row(
            stat_tile(
                "Body Battery avg high / low",
                battery,
                coverage_note(summary, "body_battery_max"),
            ),
            stat_tile(
                "Avg stress",
                fmt(summary["stress_avg"]),
                coverage_note(summary, "stress_avg"),
            ),
        )
        + '<div class="grid-2">'
        + vs_garmin_chart(
            "chart-rhr",
            "Resting HR vs Garmin 7-day average (bpm)",
            week,
            "resting_hr",
            "resting_hr_7d_avg",
            " bpm",
        )
        + vs_garmin_chart(
            "chart-hrv",
            "Overnight HRV vs Garmin weekly average (ms)",
            week,
            "hrv",
            "hrv_weekly_avg",
            " ms",
        )
        + column_chart(
            "chart-readiness",
            "Training readiness by day",
            labels,
            readiness,
            "",
            lambda v: f"{v:.0f}",
        )
        + range_chart("chart-battery", "Body Battery range by day (low to high)", week)
        + "</div>",
    )


def sleep_section(week: dict, summary: dict) -> str:
    labels = [day_label(d["date"]) for d in week["days"]]
    hours = [
        (d["sleep_duration_min"] / 60) if d.get("sleep_duration_min") else None
        for d in week["days"]
    ]
    scores = [d.get("sleep_score") for d in week["days"]]
    return section(
        "sleep",
        "Sleep",
        tile_row(
            stat_tile("Shortest night", fmt_minutes(summary["shortest_sleep_min"])),
            stat_tile(
                "Avg sleep score",
                fmt(summary["sleep_score"]),
                coverage_note(summary, "sleep_score"),
            ),
        )
        + '<div class="grid-2">'
        + column_chart(
            "chart-sleep",
            "Sleep duration by night (hours)",
            labels,
            hours,
            "h",
            lambda v: fmt_minutes(v * 60),
        )
        + column_chart(
            "chart-sleep-score",
            "Sleep score by night",
            labels,
            scores,
            "",
            lambda v: f"{v:.0f}",
        )
        + "</div>",
    )


def flag_cell(day: dict, row: str, flags: dict) -> str:
    label = day_label(day["date"])
    if row in flags:
        return f'<div class="cell flagged" tabindex="0" data-tip="{e(label)}&#10;{e(flags[row])}"><span aria-hidden="true">!</span></div>'
    if day.get(FLAG_ROW_FIELDS[row]) is None:
        return f'<div class="cell missing" tabindex="0" data-tip="{e(label)}&#10;{e(row)}: no data">&ndash;</div>'
    return f'<div class="cell ok" tabindex="0" data-tip="{e(label)}&#10;{e(row)}: within range"></div>'


def notable_section(week: dict, narrative: dict) -> str:
    days = week["days"]
    header = '<div class="cell head"></div>' + "".join(
        f'<div class="cell head">{e(day_label(d["date"]))}</div>' for d in days
    )
    per_day = [dict(day_flags(d)) for d in days]
    rows = "".join(
        f'<div class="cell row-head">{e(row)}</div>'
        + "".join(flag_cell(d, row, f) for d, f in zip(days, per_day))
        for row in FLAG_ROWS
    )
    observations = [
        f"{day_label(d['date'])} - {label}: {text}"
        for d, flags in zip(days, per_day)
        for label, text in flags.items()
    ]
    listing = (
        bullet_list(observations)
        if observations
        else '<p class="empty">No day crossed a threshold this week.</p>'
    )
    legend_html = (
        '<div class="legend"><span class="legend-item"><span class="swatch flagged">!</span>crossed a threshold</span>'
        '<span class="legend-item"><span class="swatch ok"></span>within range</span>'
        '<span class="legend-item"><span class="swatch missing">&ndash;</span>no data</span></div>'
    )
    return section(
        "notable",
        "Notable days",
        f'<div class="card">{legend_html}<div class="heat" style="--days:{len(days)}">{header}{rows}</div>{listing}</div>'
        + interpretation_cards(narrative.get("interpretations", [])),
    )


def interpretation_cards(items: list[dict]) -> str:
    if not items:
        return ""
    cards = "".join(
        '<div class="card layers">'
        f'<div class="layer"><span class="layer-tag">Data</span>{e(item.get("data", ""))}</div>'
        f'<div class="layer"><span class="layer-tag">Observation</span>{e(item.get("observation", ""))}</div>'
        f'<div class="layer"><span class="layer-tag">Interpretation</span>{e(item.get("interpretation", ""))}</div>'
        "</div>"
        for item in items
    )
    return f'<div class="grid-2 layers-grid">{cards}</div>'


def baselines_section(week: dict) -> str:
    last = week["days"][-1]
    return section(
        "baselines",
        "Garmin baselines",
        '<div class="tiles">'
        + stat_tile(
            "7-day avg resting HR",
            fmt(last.get("resting_hr_7d_avg"), " bpm"),
            "as of " + day_label(last["date"]),
        )
        + stat_tile(
            "Weekly avg HRV",
            fmt(last.get("hrv_weekly_avg"), " ms"),
            "as of " + day_label(last["date"]),
        )
        + stat_tile(
            "Acute load",
            fmt(last.get("acute_load")),
            "as of " + day_label(last["date"]),
        )
        + "</div>",
    )


def watch_section(week: dict, narrative: dict) -> str:
    items = narrative.get("things_to_watch")
    if not items:
        note = load_vs_recovery_note(week)
        items = [note] if note else ["Nothing flagged by the template rule this week."]
    return section(
        "watch", "Things to watch", f'<div class="card">{bullet_list(items)}</div>'
    )


def data_table(week: dict) -> str:
    head = "".join(f'<th scope="col">{e(name)}</th>' for name, _ in TABLE_COLUMNS)
    rows = "".join(
        f'<tr><th scope="row">{e(d["date"])}</th>'
        + "".join(f"<td>{e(cell(d))}</td>" for _, cell in TABLE_COLUMNS)
        + "</tr>"
        for d in week["days"]
    )
    return (
        '<details class="card table-view"><summary>Daily data table</summary>'
        f'<div class="table-scroll"><table><thead><tr><th scope="col">Date</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
        "</details>"
    )


def build_html(week: dict) -> str:
    summary = summarize_week(week)
    summary["acute_load_change"] = acute_load_change(week)
    narrative = week.get("narrative") or {}
    body = (
        hero(week, summary)
        + kpi_row(summary)
        + section(
            "summary",
            "Executive summary",
            f'<div class="card">{bullet_list(narrative.get("summary") or fallback_summary(week, summary))}</div>',
        )
        + training_section(week, summary)
        + recovery_section(week, summary)
        + sleep_section(week, summary)
        + notable_section(week, narrative)
        + baselines_section(week)
        + watch_section(week, narrative)
        + data_table(week)
    )
    title = f"Weekly performance report - {period_label(summary['period'][0], summary['period'][1])}"
    return PAGE.format(title=e(title), css=CSS, body=body, js=JS)


def write_html(input_path: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(load_week(input_path)))
    return output_path


CSS = """
:root {
  color-scheme: dark;
  --page: #0d0d0d;
  --surface-1: #1a1a19;
  --text-primary: #ffffff;
  --text-secondary: #c3c2b7;
  --text-muted: #898781;
  --gridline: #2c2c2a;
  --baseline: #383835;
  --border: rgba(255, 255, 255, 0.10);
  --series-1: #3987e5;
  --series-2: #d95926;
  --status-warning: #fab219;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--page); color: var(--text-primary);
  font: 15px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif;
}
main { max-width: 1120px; margin: 0 auto; padding: 0 16px 64px; }
.hero {
  position: relative; margin: 0 -16px 24px; padding: 56px 16px 40px; overflow: hidden;
  border-bottom: 1px solid var(--border);
  background:
    radial-gradient(60% 120% at 0% 0%, rgba(57, 135, 229, 0.22), transparent 60%),
    radial-gradient(50% 120% at 100% 0%, rgba(217, 89, 38, 0.16), transparent 60%);
}
.eyebrow { color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.14em; font-size: 12px; }
h1 { margin: 6px 0 20px; font-size: clamp(26px, 4vw, 38px); font-weight: 600; letter-spacing: -0.01em; }
.hero-figure { font-size: clamp(56px, 9vw, 88px); font-weight: 650; line-height: 1; letter-spacing: -0.03em; }
.hero-caption { color: var(--text-secondary); margin-top: 10px; }
section { margin-top: 40px; }
.section-title {
  font-size: 13px; text-transform: uppercase; letter-spacing: 0.14em; color: var(--text-secondary);
  margin: 0 0 14px; font-weight: 600;
}
.card {
  background: var(--surface-1); border: 1px solid var(--border); border-radius: 14px; padding: 18px 20px;
  margin-bottom: 16px;
}
.card-title, figcaption { color: var(--text-secondary); font-size: 13px; margin-bottom: 10px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 16px; }
.tile { margin: 0; }
.tile-label { color: var(--text-secondary); font-size: 13px; }
.tile-value { font-size: 30px; font-weight: 600; margin-top: 4px; letter-spacing: -0.01em; }
.tile-note { color: var(--text-muted); font-size: 12px; }
.grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 460px), 1fr)); gap: 16px; margin-bottom: 16px; }
.chart-card { margin: 0; }
.chart { width: 100%; height: auto; display: block; overflow: visible; }
.gridline { stroke: var(--gridline); stroke-width: 1; }
.baseline { stroke: var(--baseline); stroke-width: 1; }
.tick { fill: var(--text-muted); font-size: 11px; font-variant-numeric: tabular-nums; }
.value-label { fill: var(--text-secondary); font-size: 11px; font-weight: 600; }
.bar { fill: var(--series-1); transform-box: fill-box; transform-origin: bottom; animation: grow 700ms cubic-bezier(.2,.8,.2,1) both; }
.line { fill: none; stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.dot { stroke: var(--surface-1); stroke-width: 2; }
.hit { fill: transparent; cursor: crosshair; outline: none; }
.hit:hover, .hit:focus-visible { fill: rgba(255, 255, 255, 0.04); }
@keyframes grow { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@media (prefers-reduced-motion: reduce) { .bar { animation: none; } }
@media (max-width: 600px) {
  .tick, .value-label { font-size: 20px; }
  .card { padding: 14px; }
  .distribution li { grid-template-columns: 110px 1fr 24px; }
}
.legend { display: flex; flex-wrap: wrap; gap: 16px; color: var(--text-secondary); font-size: 12px; margin-bottom: 8px; }
.legend-item { display: inline-flex; align-items: center; gap: 6px; }
.line-key { width: 16px; height: 2px; border-radius: 1px; display: inline-block; }
.distribution { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.distribution li { display: grid; grid-template-columns: 140px 1fr 32px; align-items: center; gap: 12px; }
.dist-name { color: var(--text-secondary); text-transform: capitalize; }
.dist-track { height: 8px; background: var(--gridline); border-radius: 4px; overflow: hidden; }
.dist-fill { display: block; height: 100%; background: var(--series-1); border-radius: 4px; }
.dist-count { text-align: right; font-variant-numeric: tabular-nums; }
.heat { display: grid; grid-template-columns: minmax(120px, 1.4fr) repeat(var(--days), minmax(34px, 1fr)); gap: 4px; margin: 8px 0 16px; overflow-x: auto; }
.cell { min-height: 34px; border-radius: 6px; display: grid; place-items: center; font-size: 12px; }
.cell.head { color: var(--text-muted); min-height: auto; }
.cell.row-head { justify-content: start; color: var(--text-secondary); }
.cell.ok, .swatch.ok { background: rgba(57, 135, 229, 0.10); }
.cell.missing, .swatch.missing { color: var(--text-muted); background: transparent; border: 1px dashed var(--baseline); }
.cell.flagged, .swatch.flagged { background: var(--status-warning); color: #0d0d0d; font-weight: 700; }
.cell[tabindex] { cursor: crosshair; }
.swatch { width: 16px; height: 16px; border-radius: 4px; display: inline-grid; place-items: center; font-size: 11px; }
.bullets { margin: 0; padding-left: 20px; display: grid; gap: 6px; }
.bullets li::marker { color: var(--series-1); }
.empty { color: var(--text-muted); margin: 0; }
.layers { display: grid; gap: 10px; margin: 0; }
.layers-grid { margin-top: 16px; }
.layer { display: grid; grid-template-columns: 116px 1fr; gap: 12px; align-items: baseline; }
.layer-tag { font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text-muted); }
.layer:last-child { color: var(--text-primary); }
.table-view { margin-top: 40px; }
.table-view summary { cursor: pointer; color: var(--text-secondary); }
.table-scroll { overflow-x: auto; margin-top: 12px; }
table { border-collapse: collapse; width: 100%; font-size: 13px; font-variant-numeric: tabular-nums; }
th, td { padding: 8px 10px; text-align: right; border-bottom: 1px solid var(--gridline); white-space: nowrap; }
th[scope="row"], thead th:first-child { text-align: left; }
thead th { color: var(--text-muted); font-weight: 500; }
footer { color: var(--text-muted); font-size: 12px; margin-top: 32px; }
#tip {
  position: fixed; pointer-events: none; z-index: 10; background: #262625; border: 1px solid var(--border);
  border-radius: 8px; padding: 8px 10px; font-size: 12px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
}
#tip .tip-head { color: var(--text-muted); margin-bottom: 2px; }
#tip .tip-row { color: var(--text-primary); font-weight: 600; }
"""

JS = """
const tip = document.getElementById("tip");
function place(x, y) {
  const pad = 14, w = tip.offsetWidth, h = tip.offsetHeight;
  tip.style.left = Math.min(x + pad, innerWidth - w - 8) + "px";
  tip.style.top = Math.max(8, y - h - pad) + "px";
}
function show(el, x, y) {
  tip.replaceChildren();
  el.dataset.tip.split("\\n").forEach((text, i) => {
    const row = document.createElement("div");
    row.className = i === 0 ? "tip-head" : "tip-row";
    row.textContent = text;
    tip.append(row);
  });
  tip.hidden = false;
  place(x, y);
}
document.querySelectorAll("[data-tip]").forEach((el) => {
  el.addEventListener("pointermove", (ev) => show(el, ev.clientX, ev.clientY));
  el.addEventListener("pointerleave", () => { tip.hidden = true; });
  el.addEventListener("focus", () => { const r = el.getBoundingClientRect(); show(el, r.right, r.top); });
  el.addEventListener("blur", () => { tip.hidden = true; });
});
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<main>
{body}
<footer>Data from Garmin Connect. Observations, not medical advice.</footer>
</main>
<div id="tip" role="tooltip" hidden></div>
<script>{js}</script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    print(f"wrote {write_html(args.input, args.output)}")


if __name__ == "__main__":
    main()
