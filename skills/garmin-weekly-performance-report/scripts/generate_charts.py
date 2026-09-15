#!/usr/bin/env python3
"""Generate the report's chart set from Garmin-shaped weekly JSON data.

Input shape (same as sample-data/sample-garmin-week.json):

    {
      "weeks": [
        {
          "week_start": "YYYY-MM-DD",
          "week_end": "YYYY-MM-DD",
          "days": [
            {
              "date": "YYYY-MM-DD",
              "activities": [{"type": "run", "duration_min": 45,
                               "training_load": 120}, ...],
              "resting_hr": 52,
              "hrv": 65,
              "sleep_duration_min": 410,
              "training_readiness": 72,
              ...
            },
            ...
          ]
        },
        ...
      ]
    }

Weeks are assumed to be in chronological order (oldest first). The
last week in the list is treated as "current."

Usage:

    python3 generate_charts.py --input week.json --output-dir charts/

Produces, in --output-dir:

    training_duration_by_day.png
    sleep_duration_by_day.png
    resting_hr_trend.png
    hrv_trend.png
    training_load_vs_recovery.png

Style is intentionally grayscale and unadorned: this is a training
report, not a wellness app.
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.style.use("grayscale")
plt.rcParams.update({
    "font.family": "monospace",
    "axes.edgecolor": "black",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def load_weeks(input_path: Path) -> list[dict]:
    with open(input_path) as f:
        data = json.load(f)
    return data["weeks"]


def day_total_duration(day: dict) -> float:
    return sum(a.get("duration_min", 0) for a in day.get("activities", []))


def day_total_load(day: dict) -> float:
    return sum(a.get("training_load", 0) for a in day.get("activities", []))


def chart_training_duration_by_day(current_week: dict, output_dir: Path) -> Path:
    durations = [day_total_duration(d) for d in current_week["days"]]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.bar(DAY_LABELS, durations, color="0.3")
    ax.set_title("Training duration by day (min)")
    ax.set_ylabel("minutes")
    fig.tight_layout()
    path = output_dir / "training_duration_by_day.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_sleep_duration_by_day(current_week: dict, output_dir: Path) -> Path:
    minutes = [d.get("sleep_duration_min") for d in current_week["days"]]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.bar(DAY_LABELS, [m if m is not None else 0 for m in minutes], color="0.3")
    ax.set_title("Sleep duration by day (min)")
    ax.set_ylabel("minutes")
    fig.tight_layout()
    path = output_dir / "sleep_duration_by_day.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_metric_trend(weeks: list[dict], field: str, title: str, filename: str,
                        output_dir: Path) -> Path:
    dates, values = [], []
    for week in weeks:
        for day in week["days"]:
            val = day.get(field)
            if val is None:
                continue
            dates.append(day["date"][5:])  # MM-DD
            values.append(val)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(dates, values, marker="o", color="0.2", linewidth=1.5, markersize=3)
    ax.set_title(title)
    ax.set_xticks(dates[::3])
    ax.set_xticklabels(dates[::3], rotation=45, ha="right", fontsize=7)
    fig.tight_layout()
    path = output_dir / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_load_vs_recovery(current_week: dict, output_dir: Path) -> Path:
    loads = [day_total_load(d) for d in current_week["days"]]
    readiness = [d.get("training_readiness") for d in current_week["days"]]
    fig, ax1 = plt.subplots(figsize=(7, 3.4))
    ax1.bar(DAY_LABELS, loads, color="0.6", label="Training load")
    ax1.set_ylabel("Training load")
    ax2 = ax1.twinx()
    ax2.plot(DAY_LABELS, readiness, color="0.0", marker="o", linewidth=2,
              label="Training readiness")
    ax2.set_ylabel("Training readiness")
    ax2.set_ylim(0, 100)
    fig.suptitle("Training load vs. recovery")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=7)
    fig.tight_layout()
    path = output_dir / "training_load_vs_recovery.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def generate_all(input_path: Path, output_dir: Path) -> list[Path]:
    weeks = load_weeks(input_path)
    current_week = weeks[-1]
    output_dir.mkdir(parents=True, exist_ok=True)

    return [
        chart_training_duration_by_day(current_week, output_dir),
        chart_sleep_duration_by_day(current_week, output_dir),
        chart_metric_trend(weeks, "resting_hr", "Resting HR trend", "resting_hr_trend.png", output_dir),
        chart_metric_trend(weeks, "hrv", "HRV trend", "hrv_trend.png", output_dir),
        chart_load_vs_recovery(current_week, output_dir),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    paths = generate_all(args.input, args.output_dir)
    for p in paths:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
