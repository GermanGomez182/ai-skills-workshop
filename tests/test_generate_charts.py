import json

from conftest import make_day, make_week
from generate_charts import CHART_FILES, generate_all


def test_writes_every_chart_for_the_sample_week(sample_week_path, tmp_path):
    paths = generate_all(sample_week_path, tmp_path)

    assert sorted(p.name for p in paths) == sorted(CHART_FILES)
    assert all(p.stat().st_size > 0 for p in paths)


def test_writes_charts_when_days_are_missing_metrics(tmp_path):
    days = [make_day(f"2026-09-{d:02d}") for d in range(7, 14)]
    days[2].update(
        resting_hr=52, resting_hr_7d_avg=51, hrv=40, hrv_weekly_avg=42, acute_load=300
    )
    input_path = tmp_path / "week.json"
    input_path.write_text(json.dumps(make_week(days)))

    paths = generate_all(input_path, tmp_path / "charts")

    assert len(paths) == len(CHART_FILES)
