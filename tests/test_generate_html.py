import json
import re

from conftest import make_day, make_week
from generate_html import build_html, write_html

SECTIONS = (
    "Executive summary",
    "Training",
    "Recovery",
    "Sleep",
    "Notable days",
    "Garmin baselines",
    "Things to watch",
)


def full_week(**overrides) -> dict:
    days = [
        make_day(
            f"2026-09-{d:02d}",
            activities=[{"type": "running", "duration_min": 40}] if d % 2 else [],
            resting_hr=50,
            resting_hr_7d_avg=50,
            hrv=45,
            hrv_weekly_avg=45,
            sleep_duration_min=420,
            sleep_score=80,
            stress_avg=25,
            body_battery_max=85,
            body_battery_min=25,
            training_readiness=75,
            acute_load=400,
        )
        for d in range(7, 14)
    ]
    week = make_week(days)
    week.update(overrides)
    return week


def section_headings(html: str) -> list[str]:
    return re.findall(r'<h2 class="section-title">([^<]+)</h2>', html)


def test_page_shows_report_sections_in_template_order():
    assert section_headings(build_html(full_week())) == list(SECTIONS)


def test_page_is_dark_mode():
    assert "color-scheme: dark" in build_html(full_week())


def test_page_loads_nothing_from_the_network():
    html = build_html(full_week())

    assert not re.search(r'(src|href)="https?:', html)
    assert "@import" not in html
    assert "url(http" not in html


def test_page_lists_each_notable_day_observation():
    week = full_week()
    week["days"][3].update(resting_hr=55, resting_hr_7d_avg=51)

    assert "55 bpm, 4 above Garmin&#x27;s 7-day avg (51)" in build_html(week)


def test_page_says_so_when_no_day_is_notable():
    assert "No day crossed a threshold this week." in build_html(full_week())


def test_page_shows_agent_summary_and_things_to_watch():
    week = full_week(
        narrative={
            "summary": ["Four runs, all before noon."],
            "things_to_watch": ["Resting HR on Saturday could be worth monitoring."],
        }
    )

    html = build_html(week)

    assert "Four runs, all before noon." in html
    assert "Resting HR on Saturday could be worth monitoring." in html


def test_page_shows_interpretation_cards_in_three_layers():
    week = full_week(
        narrative={
            "interpretations": [
                {
                    "data": "Saturday HRV 39 ms",
                    "observation": "11% below Garmin's weekly avg",
                    "interpretation": "Coincided with the longest run",
                }
            ]
        }
    )

    html = build_html(week)

    for text in (
        "Saturday HRV 39 ms",
        "11% below Garmin&#x27;s weekly avg",
        "Coincided with the longest run",
    ):
        assert text in html


def test_page_escapes_text_from_the_week_file():
    week = full_week(narrative={"summary": ["<script>alert(1)</script>"]})

    html = build_html(week)

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_page_falls_back_to_template_note_without_narrative():
    week = full_week()
    for day, load, hrv in zip(
        week["days"], (400, 420, 440, 460, 480, 500, 520), (45, 38, 38, 45, 45, 45, 45)
    ):
        day.update(acute_load=load, hrv=hrv)

    assert "This coincided with a 30% rise in acute training load" in build_html(week)


def test_page_reports_coverage_when_a_metric_is_missing_some_days():
    week = full_week()
    week["days"][1]["hrv"] = None

    assert "6 of 7 days" in build_html(week)


def test_page_never_prints_missing_values_as_none_or_nan():
    week = full_week()
    for field in (
        "hrv",
        "resting_hr",
        "sleep_score",
        "training_readiness",
        "acute_load",
    ):
        week["days"][2][field] = None

    html = build_html(week)

    assert "None" not in html
    assert "NaN" not in html


def test_page_has_a_table_row_for_every_day():
    html = build_html(full_week())

    for day in range(7, 14):
        assert f'<th scope="row">2026-09-{day:02d}</th>' in html


def test_training_chart_draws_a_bar_only_for_days_with_training():
    html = build_html(full_week())
    training = html.split('id="chart-training"')[1].split("</svg>")[0]

    assert training.count('class="bar"') == 4


def test_write_html_creates_the_page_file(tmp_path):
    input_path = tmp_path / "week.json"
    input_path.write_text(json.dumps(full_week()))
    output = tmp_path / "report" / "weekly-report.html"

    write_html(input_path, output)

    assert output.read_text().startswith("<!doctype html>")


def test_line_chart_axis_ticks_are_whole_numbers():
    week = full_week()
    for day, rhr in zip(week["days"], (49, 48, 51, 52, 53, 54, 53)):
        day.update(resting_hr=rhr, resting_hr_7d_avg=50)

    chart = build_html(week).split('id="chart-rhr"')[1].split("</svg>")[0]
    ticks = re.findall(r'text-anchor="end">([^<]+)</text>', chart)

    assert ticks
    assert all(t.isdigit() for t in ticks), ticks


def test_page_shows_every_metric_named_in_the_report_template():
    html = build_html(full_week())

    for label in (
        "Total training time",
        "Rest days",
        "Activity distribution",
        "Avg resting HR",
        "Avg HRV",
        "Body Battery avg high / low",
        "Avg readiness",
        "Avg stress",
        "Avg sleep",
        "Shortest night",
        "Avg sleep score",
    ):
        assert label in html, label
