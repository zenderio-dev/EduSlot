from collections import Counter, defaultdict

from pydantic import BaseModel, Field

from eduslot.models import Day, ScheduleItem
from eduslot.time_grid import LESSON_TIMES


class ScheduleMetrics(BaseModel):
    """Summary metrics for a generated schedule."""
    total_lessons: int = Field(ge=0)
    lessons_per_group: dict[str, int] = Field(default_factory=dict)
    lessons_per_teacher: dict[str, int] = Field(default_factory=dict)
    group_windows: dict[str, int] = Field(default_factory=dict)
    group_windows_by_day: dict[str, dict[Day, int]] = Field(default_factory=dict)


def summarize_schedule_metrics(schedule: list[ScheduleItem]) -> ScheduleMetrics:
    """Calculate all supported schedule metrics."""
    return ScheduleMetrics(
        total_lessons=len(schedule),
        lessons_per_group=count_lessons_per_group(schedule),
        lessons_per_teacher=count_lessons_per_teacher(schedule),
        group_windows=count_group_windows(schedule),
        group_windows_by_day=count_group_windows_by_day(schedule),
    )


def count_lessons_per_group(schedule: list[ScheduleItem]) -> dict[str, int]:
    """Count lessons for each group."""
    counter: Counter[str] = Counter()

    for item in schedule:
        counter[item.group] += 1

    return dict(sorted(counter.items()))


def count_lessons_per_teacher(schedule: list[ScheduleItem]) -> dict[str, int]:
    """Count lessons for each teacher."""
    counter: Counter[str] = Counter()

    for item in schedule:
        counter[item.teacher] += 1

    return dict(sorted(counter.items()))


def count_group_windows(schedule: list[ScheduleItem]) -> dict[str, int]:
    """Count total timetable windows for each group."""
    windows_by_day = count_group_windows_by_day(schedule)

    result: dict[str, int] = {}

    for group, day_windows in sorted(windows_by_day.items()):
        result[group] = sum(day_windows.values())

    return result


def count_group_windows_by_day(
    schedule: list[ScheduleItem],
) -> dict[str, dict[Day, int]]:
    """Count timetable windows for each group by day."""
    occupied_slots = _build_group_day_slots(schedule)

    result: dict[str, dict[Day, int]] = {}

    for group, slots_by_day in sorted(occupied_slots.items()):
        result[group] = {}

        for day, slots in sorted(slots_by_day.items(), key=lambda item: item[0]):
            window_count = _count_windows_for_slots(slots)
            result[group][day] = window_count

    return result


def _build_group_day_slots(
    schedule: list[ScheduleItem],
) -> dict[str, dict[Day, set[int]]]:
    occupied_slots: dict[str, dict[Day, set[int]]] = defaultdict(
        lambda: defaultdict(set)
    )

    for item in schedule:
        occupied_slots[item.group][item.day].add(item.slot)

    return occupied_slots


def _count_windows_for_slots(occupied_slots: set[int]) -> int:
    if len(occupied_slots) <= 1:
        return 0

    first_slot = min(occupied_slots)
    last_slot = max(occupied_slots)

    valid_slots = set(LESSON_TIMES)

    return sum(
        1
        for slot in range(first_slot + 1, last_slot)
        if slot in valid_slots and slot not in occupied_slots
    )