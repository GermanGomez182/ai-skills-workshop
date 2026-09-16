#!/usr/bin/env python3
"""Assemble the weekly report PDF from Garmin-shaped JSON data and charts.

This script computes the DATA and OBSERVATION layers (numbers and
comparisons) on its own, deterministically. It does NOT attempt the
INTERPRETATION layer the way the agent does when running the Skill
live -- it only adds the one hedged, template interpretation this
Skill explicitly allows (training load up + sleep/recovery down in
the same week). Everything else stays observational on purpose: the
judgment calls belong to interpretation-guidelines.md and a model
that has read them, not to a standalone script.

Usage:

    python3 generate_charts.py --input week.json --output-dir charts/
    python3 generate_pdf.py --input week.json --charts-dir charts/ \\
        --output report.pdf
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Thresholds mirrored from ../metrics.md -- keep the two in sync.
THRESHOLDS = {
    "training_duration_pct": 15,
    "training_load_pct": 20,
    "resting_hr_abs": 3,
    "hrv_pct": 10,
    "sleep_duration_pct": 10,
    "sleep_score_abs": 8,
    "readiness_abs": 10,
    "stress_pct": 15,
}


def load_weeks(input_path: Path) -> list[dict]:
    with open(input_path) as f:
        return json.load(f)["weeks"]


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def pct_change(current, previous):
    if current is None or previous in (None, 0):
        return None
    return (current - previous) / previous * 100


def day_total_duration(day):
    return sum(a.get("duration_min", 0) for a in day.get("activities", []))


def day_total_load(day):
    return sum(a.get("training_load", 0) for a in day.get("activities", []))


def activity_distribution(week):
    counts = {}
    for day in week["days"]:
        for a in day.get("activities", []):
            counts[a["type"]] = counts.get(a["type"], 0) + 1
    return counts


def summarize_week(week: dict) -> dict:
    days = week["days"]
    return {
        "period": (week["week_start"], week["week_end"]),
        "total_duration_min": sum(day_total_duration(d) for d in days),
        "activity_count": sum(len(d.get("activities", [])) for d in days),
        "distribution": activity_distribution(week),
        "training_load": sum(day_total_load(d) for d in days),
        "resting_hr": mean([d.get("resting_hr") for d in days]),
        "avg_hr": mean([d.get("avg_hr") for d in days]),
        "hrv": mean([d.get("hrv") for d in days]),
        "sleep_duration_min": mean([d.get("sleep_duration_min") for d in days]),
        "sleep_score": mean([d.get("sleep_score") for d in days]),
        "stress_avg": mean([d.get("stress_avg") for d in days]),
        "body_battery_max": mean([d.get("body_battery_max") for d in days]),
        "body_battery_min": mean([d.get("body_battery_min") for d in days]),
        "training_readiness": mean([d.get("training_readiness") for d in days]),
    }


def fmt_minutes(m):
    if m is None:
        return "n/a"
    h, mm = divmod(round(m), 60)
    return f"{h}h {mm:02d}m"


def fmt(v, unit=""):
    if v is None:
        return "n/a"
    return f"{v:.0f}{unit}"


def notable_changes(current, previous):
    """Returns list of (label, observation_text) that cross metrics.md thresholds."""
    notes = []
    d = pct_change(current["total_duration_min"], previous["total_duration_min"])
    if d is not None and abs(d) >= THRESHOLDS["training_duration_pct"]:
        notes.append(("Training duration", f"{'up' if d > 0 else 'down'} {abs(d):.0f}% vs previous week"))

    d = pct_change(current["training_load"], previous["training_load"])
    if d is not None and abs(d) >= THRESHOLDS["training_load_pct"]:
        notes.append(("Training load", f"{'up' if d > 0 else 'down'} {abs(d):.0f}% vs previous week"))

    if current["resting_hr"] is not None and previous["resting_hr"] is not None:
        delta = current["resting_hr"] - previous["resting_hr"]
        if abs(delta) >= THRESHOLDS["resting_hr_abs"]:
            notes.append(("Resting HR", f"{'up' if delta > 0 else 'down'} {abs(delta):.0f} bpm vs previous week"))

    d = pct_change(current["hrv"], previous["hrv"])
    if d is not None and abs(d) >= THRESHOLDS["hrv_pct"]:
        notes.append(("HRV", f"{'up' if d > 0 else 'down'} {abs(d):.0f}% vs previous week"))

    d = pct_change(current["sleep_duration_min"], previous["sleep_duration_min"])
    if d is not None and abs(d) >= THRESHOLDS["sleep_duration_pct"]:
        notes.append(("Sleep duration", f"{'up' if d > 0 else 'down'} {abs(d):.0f}% vs previous week"))

    if current["sleep_score"] is not None and previous["sleep_score"] is not None:
        delta = current["sleep_score"] - previous["sleep_score"]
        if abs(delta) >= THRESHOLDS["sleep_score_abs"]:
            notes.append(("Sleep score", f"{'up' if delta > 0 else 'down'} {abs(delta):.0f} pts vs previous week"))

    if current["training_readiness"] is not None and previous["training_readiness"] is not None:
        delta = current["training_readiness"] - previous["training_readiness"]
        if abs(delta) >= THRESHOLDS["readiness_abs"]:
            notes.append(("Training readiness", f"{'up' if delta > 0 else 'down'} {abs(delta):.0f} pts vs previous week"))

    return notes


def load_vs_recovery_note(current, previous):
    """The one template interpretation this script is allowed to make."""
    load_delta = pct_change(current["training_load"], previous["training_load"])
    sleep_delta = pct_change(current["sleep_duration_min"], previous["sleep_duration_min"])
    readiness_delta = None
    if current["training_readiness"] is not None and previous["training_readiness"] is not None:
        readiness_delta = current["training_readiness"] - previous["training_readiness"]

    if load_delta and load_delta > 15 and (
        (sleep_delta and sleep_delta < -8) or (readiness_delta and readiness_delta < -8)
    ):
        return ("This coincided with an increase in training load. "
                "Could be worth monitoring next week.")
    return None


class ReportPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self.set_font("Courier", "", 7)
        self.set_text_color(90, 90, 90)
        half = (self.w - self.l_margin - self.r_margin) / 2
        self.cell(half, 8, f"Generated {datetime.now().isoformat(timespec='seconds')}", align="L")
        self.cell(half, 8, f"Page {self.page_no()}", align="R")


def section_heading(pdf: ReportPDF, text: str):
    pdf.ln(4)
    pdf.set_font("Courier", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(0, 0, 0)
    y = pdf.get_y()
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(3)
    pdf.set_font("Courier", "", 10)


def line(pdf: ReportPDF, label: str, value: str):
    pdf.set_font("Courier", "B", 10)
    pdf.cell(55, 6, label)
    pdf.set_font("Courier", "", 10)
    pdf.cell(0, 6, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def bullet(pdf: ReportPDF, text: str):
    pdf.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf(input_path: Path, charts_dir: Path, output_path: Path):
    weeks = load_weeks(input_path)
    current_raw = weeks[-1]
    previous_raw = weeks[-2] if len(weeks) >= 2 else None
    baseline_weeks = weeks[-4:] if len(weeks) >= 4 else weeks

    current = summarize_week(current_raw)
    previous = summarize_week(previous_raw) if previous_raw else None
    baseline_summaries = [summarize_week(w) for w in baseline_weeks]

    baseline = {
        key: mean([s[key] for s in baseline_summaries])
        for key in ("training_load", "sleep_duration_min", "resting_hr", "hrv", "training_readiness")
    }

    changes = notable_changes(current, previous) if previous else []
    load_note = load_vs_recovery_note(current, previous) if previous else None

    pdf = ReportPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.set_margins(16, 16, 16)

    pdf.set_font("Courier", "B", 20)
    pdf.cell(0, 12, "WEEKLY PERFORMANCE REPORT", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Courier", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, f"Period: {current['period'][0]} -> {current['period'][1]}",
              new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)

    section_heading(pdf, "EXECUTIVE SUMMARY")
    if changes:
        for label, text in changes[:5]:
            bullet(pdf, f"- {label}: {text}")
    else:
        bullet(pdf, "- No changes crossed a notable threshold this week.")
    if load_note:
        bullet(pdf, f"- {load_note}")

    section_heading(pdf, "TRAINING")
    line(pdf, "Total training time", fmt_minutes(current["total_duration_min"]))
    line(pdf, "Number of activities", fmt(current["activity_count"]))
    dist = ", ".join(f"{k}: {v}" for k, v in current["distribution"].items()) or "n/a"
    line(pdf, "Activity distribution", dist)
    line(pdf, "Training load", fmt(current["training_load"]))
    if previous:
        d = pct_change(current["training_load"], previous["training_load"])
        line(pdf, "vs previous week", f"{d:+.0f}%" if d is not None else "n/a")

    section_heading(pdf, "RECOVERY")
    line(pdf, "Resting HR", fmt(current["resting_hr"], " bpm"))
    line(pdf, "HRV", fmt(current["hrv"], " ms"))
    line(pdf, "Body Battery (max/min)", f"{fmt(current['body_battery_max'])}/{fmt(current['body_battery_min'])}")
    line(pdf, "Training readiness", fmt(current["training_readiness"]))

    section_heading(pdf, "SLEEP")
    line(pdf, "Average duration", fmt_minutes(current["sleep_duration_min"]))
    line(pdf, "Average sleep score", fmt(current["sleep_score"]))
    if previous:
        d = pct_change(current["sleep_duration_min"], previous["sleep_duration_min"])
        line(pdf, "vs previous week", f"{d:+.0f}%" if d is not None else "n/a")

    section_heading(pdf, "NOTABLE CHANGES")
    if changes:
        for label, text in changes:
            bullet(pdf, f"- {label}: {text}")
    else:
        bullet(pdf, "Nothing crossed a notable threshold this week.")

    section_heading(pdf, "4-WEEK CONTEXT")
    line(pdf, "Training load (4wk avg)", fmt(baseline["training_load"]))
    line(pdf, "Sleep duration (4wk avg)", fmt_minutes(baseline["sleep_duration_min"]))
    line(pdf, "Resting HR (4wk avg)", fmt(baseline["resting_hr"], " bpm"))
    line(pdf, "HRV (4wk avg)", fmt(baseline["hrv"], " ms"))

    section_heading(pdf, "THINGS TO WATCH")
    if load_note:
        bullet(pdf, f"- {load_note}")
    else:
        bullet(pdf, "- Nothing flagged this week. Keep an eye on training load if it keeps climbing.")

    chart_files = [
        "training_duration_by_day.png",
        "sleep_duration_by_day.png",
        "resting_hr_trend.png",
        "hrv_trend.png",
        "training_load_vs_recovery.png",
    ]
    existing_charts = [charts_dir / c for c in chart_files if (charts_dir / c).exists()]
    if existing_charts:
        pdf.add_page()
        section_heading(pdf, "CHARTS")
        for chart_path in existing_charts:
            pdf.image(str(chart_path), w=pdf.w - pdf.l_margin - pdf.r_margin)
            pdf.ln(2)

    pdf.output(str(output_path))
    return output_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--charts-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    path = build_pdf(args.input, args.charts_dir, args.output)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
