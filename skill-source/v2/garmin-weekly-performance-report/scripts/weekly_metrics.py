"""Weekly metrics shared by every report renderer (PDF, HTML).

Computes the DATA and OBSERVATION layers from one week of
Garmin-shaped JSON (shape documented in generate_charts.py):
aggregates, coverage, and days that cross the thresholds in
../metrics.md. No rendering, no I/O beyond loading the week.
"""

import json
from pathlib import Path

# Thresholds mirrored from ../metrics.md -- keep the two in sync.
RESTING_HR_ABOVE_AVG_BPM = 3
HRV_BELOW_AVG_PCT = 10
SLEEP_SCORE_POOR_BELOW = 60
READINESS_LOW_BELOW = 50
STRESS_MEDIUM_FROM = 51
ACUTE_LOAD_CHANGE_PCT = 20
HRV_DIP_NIGHTS_FOR_NOTE = 2

AVERAGED_METRICS = (
    "resting_hr",
    "hrv",
    "sleep_duration_min",
    "sleep_score",
    "stress_avg",
    "body_battery_max",
    "body_battery_min",
    "training_readiness",
)


def load_week(input_path: Path) -> dict:
    with open(input_path) as f:
        return json.load(f)


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def pct_change(current, previous):
    if current is None or previous in (None, 0):
        return None
    return (current - previous) / previous * 100


def day_total_duration(day):
    return sum(a.get("duration_min", 0) for a in day.get("activities", []))


def activity_distribution(week):
    counts = {}
    for day in week["days"]:
        for a in day.get("activities", []):
            counts[a["type"]] = counts.get(a["type"], 0) + 1
    return counts


def summarize_week(week: dict) -> dict:
    days = week["days"]
    summary = {
        "period": (week["week_start"], week["week_end"]),
        "day_count": len(days),
        "total_duration_min": sum(day_total_duration(d) for d in days),
        "activity_count": sum(len(d.get("activities", [])) for d in days),
        "rest_days": sum(1 for d in days if not d.get("activities")),
        "distribution": activity_distribution(week),
        "coverage": {
            m: sum(1 for d in days if d.get(m) is not None) for m in AVERAGED_METRICS
        },
    }
    for metric in AVERAGED_METRICS:
        summary[metric] = mean([d.get(metric) for d in days])
    nights = [d["sleep_duration_min"] for d in days if _has(d, "sleep_duration_min")]
    summary["shortest_sleep_min"] = min(nights) if nights else None
    return summary


def _has(day, *fields):
    return all(day.get(f) is not None for f in fields)


def hrv_below_avg_pct(day):
    if not _has(day, "hrv", "hrv_weekly_avg"):
        return None
    change = pct_change(day["hrv"], day["hrv_weekly_avg"])
    return None if change is None else -change


def hrv_dip_crosses_threshold(day) -> bool:
    below = hrv_below_avg_pct(day)
    return below is not None and below >= HRV_BELOW_AVG_PCT


def day_flags(day: dict) -> list[tuple[str, str]]:
    flags = []
    if _has(day, "resting_hr", "resting_hr_7d_avg"):
        above = day["resting_hr"] - day["resting_hr_7d_avg"]
        if above >= RESTING_HR_ABOVE_AVG_BPM:
            flags.append(
                (
                    "Resting HR",
                    f"{day['resting_hr']:.0f} bpm, {above:.0f} above Garmin's 7-day avg ({day['resting_hr_7d_avg']:.0f})",
                )
            )
    if hrv_dip_crosses_threshold(day):
        below = hrv_below_avg_pct(day)
        flags.append(
            (
                "HRV",
                f"{day['hrv']:.0f} ms, {below:.0f}% below Garmin's weekly avg ({day['hrv_weekly_avg']:.0f})",
            )
        )
    if _has(day, "sleep_score") and day["sleep_score"] < SLEEP_SCORE_POOR_BELOW:
        flags.append(
            (
                "Sleep score",
                f"{day['sleep_score']:.0f}, Garmin 'poor' range (<{SLEEP_SCORE_POOR_BELOW})",
            )
        )
    if (
        _has(day, "training_readiness")
        and day["training_readiness"] < READINESS_LOW_BELOW
    ):
        flags.append(
            (
                "Training readiness",
                f"{day['training_readiness']:.0f}, Garmin 'low' range (<{READINESS_LOW_BELOW})",
            )
        )
    if _has(day, "stress_avg") and day["stress_avg"] >= STRESS_MEDIUM_FROM:
        flags.append(
            (
                "Stress",
                f"avg {day['stress_avg']:.0f}, Garmin 'medium' or higher ({STRESS_MEDIUM_FROM}+)",
            )
        )
    return flags


def notable_days(week: dict) -> list[tuple[str, str, str]]:
    """Returns (date, label, observation) for every metric that crossed a metrics.md threshold."""
    return [
        (day["date"], label, text)
        for day in week["days"]
        for label, text in day_flags(day)
    ]


def acute_load_change(week: dict):
    loads = [d["acute_load"] for d in week["days"] if d.get("acute_load") is not None]
    if len(loads) < 2:
        return None
    return pct_change(loads[-1], loads[0])


def hrv_dip_nights(week: dict) -> int:
    return sum(1 for d in week["days"] if hrv_dip_crosses_threshold(d))


def load_vs_recovery_note(week: dict):
    """The one template interpretation this script is allowed to make."""
    load_change = acute_load_change(week)
    nights = hrv_dip_nights(week)
    if (
        load_change is None
        or load_change < ACUTE_LOAD_CHANGE_PCT
        or nights < HRV_DIP_NIGHTS_FOR_NOTE
    ):
        return None
    return (
        f"HRV was {HRV_BELOW_AVG_PCT}%+ below Garmin's weekly average on {nights} nights. This coincided "
        f"with a {load_change:.0f}% rise in acute training load. Could be worth monitoring next week."
    )


def fmt_minutes(m):
    if m is None:
        return "n/a"
    h, mm = divmod(round(m), 60)
    return f"{h}h {mm:02d}m"


def fmt(v, unit=""):
    if v is None:
        return "n/a"
    return f"{v:.0f}{unit}"


def with_coverage(text: str, summary: dict, metric: str) -> str:
    covered, total = summary["coverage"][metric], summary["day_count"]
    return text if covered == total else f"{text}  ({covered} of {total} days)"
