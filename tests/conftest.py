import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = (
    REPO_ROOT / "skill-source" / "v2" / "garmin-weekly-performance-report" / "scripts"
)
SAMPLE_WEEK = REPO_ROOT / "sample-data" / "sample-garmin-week.json"

sys.path.insert(0, str(SCRIPTS_DIR))


def make_day(date: str, **metrics) -> dict:
    day = {
        "date": date,
        "activities": [],
        "resting_hr": None,
        "resting_hr_7d_avg": None,
        "hrv": None,
        "hrv_weekly_avg": None,
        "sleep_duration_min": None,
        "sleep_score": None,
        "stress_avg": None,
        "body_battery_max": None,
        "body_battery_min": None,
        "training_readiness": None,
        "acute_load": None,
    }
    day.update(metrics)
    return day


def make_week(days: list[dict]) -> dict:
    return {"week_start": days[0]["date"], "week_end": days[-1]["date"], "days": days}


@pytest.fixture
def sample_week_path() -> Path:
    return SAMPLE_WEEK
