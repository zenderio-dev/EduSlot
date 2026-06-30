import pytest
from pydantic import ValidationError

from eduslot.models import (
    GroupLoad,
    LessonLoad,
    ScheduleItem,
    TimeSlot,
    WorkloadInput,
)


def test_time_slot_accepts_valid_day_and_slot():
    slot = TimeSlot(day="mon", slot=1)

    assert slot.day == "mon"
    assert slot.slot == 1


def test_time_slot_rejects_invalid_slot_number():
    with pytest.raises(ValidationError):
        TimeSlot(day="mon", slot=99)


def test_lesson_load_requires_positive_lessons_per_week():
    with pytest.raises(ValidationError):
        LessonLoad(
            subject="Python",
            teacher="Иванов",
            lessons_per_week=0,
        )


def test_workload_input_accepts_group_with_lessons():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Группа А",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Иванов",
                        lessons_per_week=2,
                        lesson_type="practice",
                    )
                ],
            )
        ]
    )

    assert workload.groups[0].name == "Группа А"
    assert workload.groups[0].lessons[0].subject == "Python"


def test_schedule_item_contains_required_fields():
    item = ScheduleItem(
        group="Группа А",
        subject="Python",
        teacher="Иванов",
        day="wed",
        slot=3,
        lesson_type="practice",
    )

    assert item.group == "Группа А"
    assert item.day == "wed"
    assert item.slot == 3