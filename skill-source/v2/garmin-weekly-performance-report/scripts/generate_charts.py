#!/usr/bin/env python3
"""Generate the report's chart set from one week of Garmin-shaped JSON.

Input shape (same as sample-data/sample-garmin-week.json):

    {
      "week_start": "YYYY-MM-DD",
      "week_end": "YYYY-MM-DD",
      "days": [
        {
          "date": "YYYY-MM-DD",
          "activities": [{"type": "running", "duration_min": 45}, ...],
          "resting_hr": 52,            "resting_hr_7d_avg": 51,
          "hrv": 44,                   "hrv_weekly_avg": 45,
          "sleep_duration_min": 410,   "sleep_score": 78,
          "stress_avg": 30,
          "body_battery_max": 80,      "body_battery_min": 20,
          "training_readiness": 72,    "acute_load": 450
        },
        ... one entry per day, 7 in total, null for missing values
      ]
    }

Usage:

    python3 generate_charts.py --input week.json --output-dir charts/

Style is intentionally grayscale and unadorned: this is a training
report, not a wellness app.
"""

import argparse
import json
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.style.use("grayscale")
plt.rcParams.update(
    {
        "font.family": "monospace",
        "axes.edgecolor": "black",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)

CHART_FILES = (
    "training_duration_by_day.png",
    "sleep_duration_by_day.png",
    "resting_hr_vs_garmin_avg.png",
    "hrv_vs_garmin_avg.png",
    "acute_load_vs_readiness.png",
)


def load_week(input_path: Path) -> dict:
    with open(input_path) as f:
        return json.load(f)


def day_labels(week: dict) -> list[str]:
    return [date.fromisoformat(d["date"]).strftime("%a %d") for d in week["days"]]


def day_total_duration(day: dict) -> float:
    return sum(a.get("duration_min", 0) for a in day.get("activities", []))


def save(fig, output_dir: Path, filename: str) -> Path:
    fig.tight_layout()
    path = output_dir / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_bars(
    week: dict, values: list, title: str, filename: str, output_dir: Path
) -> Path:
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.bar(day_labels(week), [v or 0 for v in values], color="0.3")
    ax.set_title(title)
    ax.set_ylabel("minutes")
    return save(fig, output_dir, filename)


def chart_vs_garmin_avg(
    week: dict, field: str, avg_field: str, title: str, filename: str, output_dir: Path
) -> Path:
    labels = day_labels(week)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(
        labels,
        [d.get(field) for d in week["days"]],
        marker="o",
        color="0.1",
        label="daily",
    )
    ax.plot(
        labels,
        [d.get(avg_field) for d in week["days"]],
        linestyle="--",
        color="0.5",
        label="Garmin avg",
    )
    ax.set_title(title)
    ax.legend(loc="upper left", fontsize=7)
    return save(fig, output_dir, filename)


def chart_load_vs_readiness(week: dict, output_dir: Path) -> Path:
    labels = day_labels(week)
    fig, ax1 = plt.subplots(figsize=(7, 3.4))
    ax1.bar(
        labels,
        [d.get("acute_load") or 0 for d in week["days"]],
        color="0.6",
        label="Acute load",
    )
    ax1.set_ylabel("Acute load")
    ax2 = ax1.twinx()
    readiness = [d.get("training_readiness") for d in week["days"]]
    ax2.plot(
        labels,
        readiness,
        color="0.0",
        marker="o",
        linewidth=2,
        label="Training readiness",
    )
    ax2.set_ylabel("Training readiness")
    ax2.set_ylim(0, 100)
    fig.suptitle("Acute load vs. training readiness")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=7)
    return save(fig, output_dir, "acute_load_vs_readiness.png")


def generate_all(input_path: Path, output_dir: Path) -> list[Path]:
    week = load_week(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    days = week["days"]

    return [
        chart_bars(
            week,
            [day_total_duration(d) for d in days],
            "Training duration by day (min)",
            "training_duration_by_day.png",
            output_dir,
        ),
        chart_bars(
            week,
            [d.get("sleep_duration_min") for d in days],
            "Sleep duration by day (min)",
            "sleep_duration_by_day.png",
            output_dir,
        ),
        chart_vs_garmin_avg(
            week,
            "resting_hr",
            "resting_hr_7d_avg",
            "Resting HR vs Garmin 7-day avg (bpm)",
            "resting_hr_vs_garmin_avg.png",
            output_dir,
        ),
        chart_vs_garmin_avg(
            week,
            "hrv",
            "hrv_weekly_avg",
            "HRV vs Garmin weekly avg (ms)",
            "hrv_vs_garmin_avg.png",
            output_dir,
        ),
        chart_load_vs_readiness(week, output_dir),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    for p in generate_all(args.input, args.output_dir):
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
