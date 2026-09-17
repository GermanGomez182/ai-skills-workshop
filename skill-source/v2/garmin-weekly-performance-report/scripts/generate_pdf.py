#!/usr/bin/env python3
"""Assemble the weekly report PDF from one week of Garmin-shaped JSON and charts.

Input shape (same as sample-data/sample-garmin-week.json, and the file
the agent writes to output/week.json): see generate_charts.py.

This script computes the DATA and OBSERVATION layers (numbers and
comparisons against Garmin's own rolling baselines) on its own,
deterministically. It does NOT attempt the INTERPRETATION layer the
way the agent does when running the Skill live -- it only adds the
one hedged, template interpretation this Skill explicitly allows
(acute load up + HRV below baseline in the same week). The judgment
calls belong to interpretation-guidelines.md and a model that has
read them, not to a standalone script.

Usage:

    python3 generate_charts.py --input week.json --output-dir charts/
    python3 generate_pdf.py --input week.json --charts-dir charts/ \\
        --output report.pdf
"""

import argparse
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from generate_charts import CHART_FILES
from weekly_metrics import (
    acute_load_change,
    fmt,
    fmt_minutes,
    load_vs_recovery_note,
    load_week,
    notable_days,
    summarize_week,
    with_coverage,
)


class ReportPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self.set_font("Courier", "", 7)
        self.set_text_color(90, 90, 90)
        half = (self.w - self.l_margin - self.r_margin) / 2
        self.cell(
            half,
            8,
            f"Generated {datetime.now().astimezone().isoformat(timespec='seconds')}",
            align="L",
        )
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
    pdf.cell(60, 6, label)
    pdf.set_font("Courier", "", 10)
    pdf.cell(0, 6, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def bullet(pdf: ReportPDF, text: str):
    pdf.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf(input_path: Path, charts_dir: Path, output_path: Path):
    week = load_week(input_path)
    summary = summarize_week(week)
    flagged = notable_days(week)
    load_change = acute_load_change(week)
    load_note = load_vs_recovery_note(week)
    last_day = week["days"][-1]

    pdf = ReportPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.set_margins(16, 16, 16)

    pdf.set_font("Courier", "B", 20)
    pdf.cell(0, 12, "WEEKLY PERFORMANCE REPORT", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Courier", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(
        0,
        6,
        f"Period: {summary['period'][0]} -> {summary['period'][1]}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)

    section_heading(pdf, "EXECUTIVE SUMMARY")
    bullet(
        pdf,
        f"- {summary['activity_count']} activities, {fmt_minutes(summary['total_duration_min'])} total.",
    )
    bullet(
        pdf,
        f"- {len({date for date, _, _ in flagged})} of {summary['day_count']} days crossed a threshold.",
    )
    if load_note:
        bullet(pdf, f"- {load_note}")

    section_heading(pdf, "TRAINING")
    line(pdf, "Total training time", fmt_minutes(summary["total_duration_min"]))
    line(pdf, "Number of activities", fmt(summary["activity_count"]))
    line(pdf, "Rest days", fmt(summary["rest_days"]))
    dist = ", ".join(f"{k}: {v}" for k, v in summary["distribution"].items()) or "n/a"
    line(pdf, "Activity distribution", dist)
    line(
        pdf,
        "Acute load, start -> end",
        f"{load_change:+.0f}%" if load_change is not None else "n/a",
    )

    section_heading(pdf, "RECOVERY")
    line(
        pdf,
        "Resting HR (avg)",
        with_coverage(fmt(summary["resting_hr"], " bpm"), summary, "resting_hr"),
    )
    line(pdf, "HRV (avg)", with_coverage(fmt(summary["hrv"], " ms"), summary, "hrv"))
    bb = f"{fmt(summary['body_battery_max'])}/{fmt(summary['body_battery_min'])}"
    line(pdf, "Body Battery (high/low)", with_coverage(bb, summary, "body_battery_max"))
    line(
        pdf,
        "Training readiness (avg)",
        with_coverage(
            fmt(summary["training_readiness"]), summary, "training_readiness"
        ),
    )
    line(
        pdf,
        "Stress (avg)",
        with_coverage(fmt(summary["stress_avg"]), summary, "stress_avg"),
    )

    section_heading(pdf, "SLEEP")
    line(
        pdf,
        "Average duration",
        with_coverage(
            fmt_minutes(summary["sleep_duration_min"]), summary, "sleep_duration_min"
        ),
    )
    line(pdf, "Shortest night", fmt_minutes(summary["shortest_sleep_min"]))
    line(
        pdf,
        "Average sleep score",
        with_coverage(fmt(summary["sleep_score"]), summary, "sleep_score"),
    )

    section_heading(pdf, "NOTABLE DAYS")
    if flagged:
        for date, label, text in flagged:
            bullet(pdf, f"- {date}  {label}: {text}")
    else:
        bullet(pdf, "No day crossed a threshold this week.")

    section_heading(pdf, "GARMIN BASELINES")
    line(pdf, "7-day avg resting HR", fmt(last_day.get("resting_hr_7d_avg"), " bpm"))
    line(pdf, "Weekly avg HRV", fmt(last_day.get("hrv_weekly_avg"), " ms"))
    line(pdf, "Acute load (last day)", fmt(last_day.get("acute_load")))

    section_heading(pdf, "THINGS TO WATCH")
    bullet(
        pdf,
        f"- {load_note}"
        if load_note
        else "- Nothing flagged by the template rule this week.",
    )

    existing_charts = [charts_dir / c for c in CHART_FILES if (charts_dir / c).exists()]
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
