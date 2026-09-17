import json

from conftest import make_day, make_week
from generate_pdf import build_pdf
from weekly_metrics import (
    acute_load_change,
    load_vs_recovery_note,
    load_week,
    notable_days,
    summarize_week,
)


def test_load_week_reads_a_single_week_object(tmp_path):
    week = make_week([make_day("2026-09-07"), make_day("2026-09-13")])
    path = tmp_path / "week.json"
    path.write_text(json.dumps(week))

    assert load_week(path)["week_start"] == "2026-09-07"


def test_summary_totals_training_time_and_activity_count():
    week = make_week(
        [
            make_day(
                "2026-09-07", activities=[{"type": "running", "duration_min": 40}]
            ),
            make_day(
                "2026-09-08",
                activities=[
                    {"type": "running", "duration_min": 30},
                    {"type": "strength_training", "duration_min": 20},
                ],
            ),
        ]
    )

    summary = summarize_week(week)

    assert summary["total_duration_min"] == 90
    assert summary["activity_count"] == 3
    assert summary["distribution"] == {"running": 2, "strength_training": 1}


def test_summary_averages_ignore_days_without_data():
    week = make_week(
        [
            make_day("2026-09-07", hrv=40),
            make_day("2026-09-08", hrv=None),
            make_day("2026-09-09", hrv=50),
        ]
    )

    assert summarize_week(week)["hrv"] == 45


def test_summary_counts_days_with_data_per_metric():
    week = make_week(
        [
            make_day("2026-09-07", hrv=40, sleep_score=70),
            make_day("2026-09-08", sleep_score=72),
        ]
    )

    coverage = summarize_week(week)["coverage"]

    assert coverage["hrv"] == 1
    assert coverage["sleep_score"] == 2


def test_rest_days_are_days_without_activities():
    week = make_week(
        [
            make_day(
                "2026-09-07", activities=[{"type": "running", "duration_min": 40}]
            ),
            make_day("2026-09-08"),
            make_day("2026-09-09"),
        ]
    )

    assert summarize_week(week)["rest_days"] == 2


def test_flags_resting_hr_3_bpm_above_garmin_7_day_average():
    week = make_week([make_day("2026-09-07", resting_hr=55, resting_hr_7d_avg=52)])

    assert notable_days(week) == [
        ("2026-09-07", "Resting HR", "55 bpm, 3 above Garmin's 7-day avg (52)")
    ]


def test_does_not_flag_resting_hr_below_threshold():
    week = make_week([make_day("2026-09-07", resting_hr=54, resting_hr_7d_avg=52)])

    assert notable_days(week) == []


def test_flags_hrv_10_percent_below_garmin_weekly_average():
    week = make_week([make_day("2026-09-07", hrv=36, hrv_weekly_avg=40)])

    assert notable_days(week) == [
        ("2026-09-07", "HRV", "36 ms, 10% below Garmin's weekly avg (40)")
    ]


def test_does_not_flag_hrv_just_under_threshold():
    week = make_week([make_day("2026-09-07", hrv=37, hrv_weekly_avg=40)])

    assert notable_days(week) == []


def test_flags_sleep_score_in_garmin_poor_range():
    week = make_week([make_day("2026-09-07", sleep_score=59)])

    assert notable_days(week) == [
        ("2026-09-07", "Sleep score", "59, Garmin 'poor' range (<60)")
    ]


def test_flags_training_readiness_in_garmin_low_range():
    week = make_week([make_day("2026-09-07", training_readiness=49)])

    assert notable_days(week) == [
        ("2026-09-07", "Training readiness", "49, Garmin 'low' range (<50)")
    ]


def test_flags_average_stress_in_garmin_medium_range():
    week = make_week([make_day("2026-09-07", stress_avg=51)])

    assert notable_days(week) == [
        ("2026-09-07", "Stress", "avg 51, Garmin 'medium' or higher (51+)")
    ]


def test_day_without_any_data_is_never_flagged():
    week = make_week([make_day("2026-09-07")])

    assert notable_days(week) == []


def test_acute_load_change_compares_first_and_last_day_with_data():
    week = make_week(
        [
            make_day("2026-09-07", acute_load=None),
            make_day("2026-09-08", acute_load=400),
            make_day("2026-09-13", acute_load=500),
        ]
    )

    assert acute_load_change(week) == 25


def test_acute_load_change_needs_two_days_of_data():
    week = make_week([make_day("2026-09-07", acute_load=400), make_day("2026-09-08")])

    assert acute_load_change(week) is None


def test_note_when_acute_load_rises_and_hrv_dips_on_two_nights():
    week = make_week(
        [
            make_day("2026-09-07", acute_load=400, hrv=35, hrv_weekly_avg=40),
            make_day("2026-09-08", hrv=34, hrv_weekly_avg=40),
            make_day("2026-09-13", acute_load=480),
        ]
    )

    assert load_vs_recovery_note(week) == (
        "HRV was 10%+ below Garmin's weekly average on 2 nights. This coincided "
        "with a 20% rise in acute training load. Could be worth monitoring next week."
    )


def test_no_note_when_hrv_dips_stay_under_threshold():
    week = make_week(
        [
            make_day("2026-09-07", acute_load=400, hrv=38, hrv_weekly_avg=40),
            make_day("2026-09-08", hrv=37, hrv_weekly_avg=40),
            make_day("2026-09-13", acute_load=480),
        ]
    )

    assert load_vs_recovery_note(week) is None


def test_no_note_when_acute_load_is_flat():
    week = make_week(
        [
            make_day("2026-09-07", acute_load=400, hrv=35, hrv_weekly_avg=40),
            make_day("2026-09-08", hrv=34, hrv_weekly_avg=40),
            make_day("2026-09-13", acute_load=410),
        ]
    )

    assert load_vs_recovery_note(week) is None


def test_builds_pdf_from_sample_week(sample_week_path, tmp_path):
    output = tmp_path / "report.pdf"

    build_pdf(sample_week_path, tmp_path / "no-charts", output)

    assert output.read_bytes().startswith(b"%PDF")


def test_builds_pdf_when_a_metric_is_missing_all_week(tmp_path):
    week = make_week(
        [make_day(f"2026-09-{d:02d}", sleep_score=70) for d in range(7, 14)]
    )
    input_path = tmp_path / "week.json"
    input_path.write_text(json.dumps(week))
    output = tmp_path / "report.pdf"

    build_pdf(input_path, tmp_path / "no-charts", output)

    assert output.read_bytes().startswith(b"%PDF")


def test_summary_reports_shortest_night_with_data():
    week = make_week(
        [
            make_day("2026-09-07", sleep_duration_min=420),
            make_day("2026-09-08", sleep_duration_min=None),
            make_day("2026-09-09", sleep_duration_min=355),
        ]
    )

    assert summarize_week(week)["shortest_sleep_min"] == 355
