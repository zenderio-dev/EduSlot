from eduslot.metrics import (
    count_group_windows,
    count_group_windows_by_day,
    count_lessons_per_group,
    count_lessons_per_teacher,
    summarize_schedule_metrics,
)
from eduslot.models import ScheduleItem


def test_count_lessons_per_group():
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="mon",
            slot=1,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group A",
            subject="Databases",
            teacher="Petrov",
            day="mon",
            slot=2,
            lesson_type="lecture",
        ),
        ScheduleItem(
            group="Group B",
            subject="Web Development",
            teacher="Sidorov",
            day="tue",
            slot=1,
            lesson_type="practice",
        ),
    ]

    result = count_lessons_per_group(schedule)

    assert result == {
        "Group A": 2,
        "Group B": 1,
    }


def test_count_lessons_per_teacher():
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="mon",
            slot=1,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group B",
            subject="Python",
            teacher="Ivanov",
            day="tue",
            slot=1,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group A",
            subject="Databases",
            teacher="Petrov",
            day="wed",
            slot=2,
            lesson_type="lecture",
        ),
    ]

    result = count_lessons_per_teacher(schedule)

    assert result == {
        "Ivanov": 2,
        "Petrov": 1,
    }


def test_count_group_windows_returns_zero_for_consecutive_lessons():
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="mon",
            slot=1,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group A",
            subject="Databases",
            teacher="Petrov",
            day="mon",
            slot=2,
            lesson_type="lecture",
        ),
        ScheduleItem(
            group="Group A",
            subject="Math",
            teacher="Sidorov",
            day="mon",
            slot=3,
            lesson_type="practice",
        ),
    ]

    result = count_group_windows(schedule)

    assert result == {
        "Group A": 0,
    }


def test_count_group_windows_detects_single_window():
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="mon",
            slot=1,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group A",
            subject="Databases",
            teacher="Petrov",
            day="mon",
            slot=3,
            lesson_type="lecture",
        ),
    ]

    result = count_group_windows(schedule)

    assert result == {
        "Group A": 1,
    }


def test_count_group_windows_detects_multiple_windows_across_days():
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="mon",
            slot=1,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group A",
            subject="Databases",
            teacher="Petrov",
            day="mon",
            slot=4,
            lesson_type="lecture",
        ),
        ScheduleItem(
            group="Group A",
            subject="Math",
            teacher="Sidorov",
            day="tue",
            slot=2,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group A",
            subject="Physics",
            teacher="Smirnov",
            day="tue",
            slot=5,
            lesson_type="lab",
        ),
    ]

    result = count_group_windows(schedule)

    assert result == {
        "Group A": 4,
    }


def test_count_group_windows_by_day():
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="mon",
            slot=1,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group A",
            subject="Databases",
            teacher="Petrov",
            day="mon",
            slot=3,
            lesson_type="lecture",
        ),
        ScheduleItem(
            group="Group A",
            subject="Math",
            teacher="Sidorov",
            day="tue",
            slot=2,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group A",
            subject="Physics",
            teacher="Smirnov",
            day="tue",
            slot=5,
            lesson_type="lab",
        ),
    ]

    result = count_group_windows_by_day(schedule)

    assert result == {
        "Group A": {
            "mon": 1,
            "tue": 2,
        }
    }


def test_summarize_schedule_metrics():
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="mon",
            slot=1,
            lesson_type="practice",
        ),
        ScheduleItem(
            group="Group A",
            subject="Databases",
            teacher="Petrov",
            day="mon",
            slot=3,
            lesson_type="lecture",
        ),
        ScheduleItem(
            group="Group B",
            subject="Web Development",
            teacher="Ivanov",
            day="tue",
            slot=1,
            lesson_type="practice",
        ),
    ]

    result = summarize_schedule_metrics(schedule)

    assert result.total_lessons == 3
    assert result.lessons_per_group == {
        "Group A": 2,
        "Group B": 1,
    }
    assert result.lessons_per_teacher == {
        "Ivanov": 2,
        "Petrov": 1,
    }
    assert result.group_windows == {
        "Group A": 1,
        "Group B": 0,
    }
    assert result.group_windows_by_day == {
        "Group A": {
            "mon": 1,
        },
        "Group B": {
            "tue": 0,
        },
    }