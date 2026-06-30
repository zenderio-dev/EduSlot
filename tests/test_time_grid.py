from eduslot.models import TimeSlot
from eduslot.time_grid import (
    DAYS,
    LESSON_TIMES,
    format_slot,
    get_all_slots,
    get_slots_between,
    get_slots_for_day,
)


def test_days_contains_five_weekdays():
    assert len(DAYS) == 5
    assert DAYS["mon"] == "Понедельник"
    assert DAYS["fri"] == "Пятница"


def test_lesson_times_contains_five_lessons():
    assert len(LESSON_TIMES) == 5
    assert LESSON_TIMES[1].start == "09:00"
    assert LESSON_TIMES[5].end == "17:30"


def test_get_all_slots_returns_full_week_grid():
    slots = get_all_slots()

    assert len(slots) == 25
    assert TimeSlot(day="mon", slot=1) in slots
    assert TimeSlot(day="fri", slot=5) in slots


def test_get_slots_for_day_returns_only_selected_day():
    slots = get_slots_for_day("wed")

    assert len(slots) == 5
    assert all(slot.day == "wed" for slot in slots)


def test_get_slots_between_returns_lessons_inside_time_range():
    slots = get_slots_between("wed", "13:50", "17:00")

    assert slots == [
        TimeSlot(day="wed", slot=4),
    ]


def test_format_slot_returns_human_readable_value():
    result = format_slot(TimeSlot(day="thu", slot=2))

    assert result == "Четверг, 2 пара (10:40–12:10)"