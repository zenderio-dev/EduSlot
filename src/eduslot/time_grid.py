from dataclasses import dataclass

from eduslot.models import Day, TimeSlot


@dataclass(frozen=True)
class LessonTime:
    slot: int
    start: str
    end: str


DAYS: dict[Day, str] = {
    "mon": "Понедельник",
    "tue": "Вторник",
    "wed": "Среда",
    "thu": "Четверг",
    "fri": "Пятница",
}


LESSON_TIMES: dict[int, LessonTime] = {
    1: LessonTime(slot=1, start="09:00", end="10:30"),
    2: LessonTime(slot=2, start="10:40", end="12:10"),
    3: LessonTime(slot=3, start="12:40", end="14:10"),
    4: LessonTime(slot=4, start="14:20", end="15:50"),
    5: LessonTime(slot=5, start="16:00", end="17:30"),
}


def get_all_slots() -> list[TimeSlot]:
    result: list[TimeSlot] = []

    for day in DAYS:
        for slot in LESSON_TIMES:
            result.append(TimeSlot(day=day, slot=slot))

    return result


def get_slots_for_day(day: Day) -> list[TimeSlot]:
    return [TimeSlot(day=day, slot=slot) for slot in LESSON_TIMES]


def get_slots_between(day: Day, start_time: str, end_time: str) -> list[TimeSlot]:
    result: list[TimeSlot] = []

    for slot, lesson_time in LESSON_TIMES.items():
        lesson_starts_inside_range = lesson_time.start >= start_time
        lesson_ends_inside_range = lesson_time.end <= end_time

        if lesson_starts_inside_range and lesson_ends_inside_range:
            result.append(TimeSlot(day=day, slot=slot))

    return result


def format_slot(time_slot: TimeSlot) -> str:
    lesson_time = LESSON_TIMES[time_slot.slot]
    day_name = DAYS[time_slot.day]

    return f"{day_name}, {time_slot.slot} пара ({lesson_time.start}–{lesson_time.end})"