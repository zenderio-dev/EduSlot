from collections import Counter, defaultdict
from collections.abc import Iterable

from eduslot.models import (
    Conflict,
    Day,
    PreferencesInput,
    ScheduleItem,
    TimeSlot,
    WorkloadInput,
)
from eduslot.parser import parse_preference_input


SlotKey = tuple[Day, int]
LessonKey = tuple[str, str, str, str]


def validate_schedule(
    schedule: list[ScheduleItem],
    workload: WorkloadInput,
    preferences: PreferencesInput,
) -> list[Conflict]:
    conflicts: list[Conflict] = []

    conflicts.extend(validate_teacher_overlaps(schedule))
    conflicts.extend(validate_group_overlaps(schedule))
    conflicts.extend(validate_required_load(schedule, workload))
    conflicts.extend(validate_teacher_availability(schedule, preferences))

    return conflicts


def validate_teacher_overlaps(schedule: list[ScheduleItem]) -> list[Conflict]:
    grouped_items: dict[tuple[str, SlotKey], list[ScheduleItem]] = defaultdict(list)

    for item in schedule:
        grouped_items[(item.teacher, (item.day, item.slot))].append(item)

    conflicts: list[Conflict] = []

    for (teacher, slot_key), items in grouped_items.items():
        if len(items) <= 1:
            continue

        day, slot = slot_key
        groups = _unique(item.group for item in items)

        conflicts.append(
            Conflict(
                type="teacher_overlap",
                message=(
                    f"Преподаватель {teacher} назначен на несколько занятий "
                    f"одновременно: {day}, {slot} пара."
                ),
                affected_groups=groups,
                affected_teachers=[teacher],
                affected_slots=[TimeSlot(day=day, slot=slot)],
            )
        )

    return conflicts


def validate_group_overlaps(schedule: list[ScheduleItem]) -> list[Conflict]:
    grouped_items: dict[tuple[str, SlotKey], list[ScheduleItem]] = defaultdict(list)

    for item in schedule:
        grouped_items[(item.group, (item.day, item.slot))].append(item)

    conflicts: list[Conflict] = []

    for (group, slot_key), items in grouped_items.items():
        if len(items) <= 1:
            continue

        day, slot = slot_key
        teachers = _unique(item.teacher for item in items)

        conflicts.append(
            Conflict(
                type="group_overlap",
                message=(
                    f"Группа {group} назначена на несколько занятий одновременно: "
                    f"{day}, {slot} пара."
                ),
                affected_groups=[group],
                affected_teachers=teachers,
                affected_slots=[TimeSlot(day=day, slot=slot)],
            )
        )

    return conflicts


def validate_required_load(
    schedule: list[ScheduleItem],
    workload: WorkloadInput,
) -> list[Conflict]:
    expected_counts = _build_expected_lesson_counts(workload)
    actual_counts = _build_actual_lesson_counts(schedule)

    conflicts: list[Conflict] = []

    all_lesson_keys = set(expected_counts) | set(actual_counts)

    for lesson_key in sorted(all_lesson_keys):
        expected = expected_counts.get(lesson_key, 0)
        actual = actual_counts.get(lesson_key, 0)

        if expected == actual:
            continue

        group, subject, teacher, lesson_type = lesson_key

        if expected == 0:
            conflict_type = "unexpected_lesson"
            message = (
                f"В расписании найдено лишнее занятие: {subject} "
                f"для группы {group} у преподавателя {teacher}."
            )
        else:
            conflict_type = "required_load_mismatch"
            message = (
                f"Количество занятий не соответствует нагрузке: {subject} "
                f"для группы {group} у преподавателя {teacher}. "
                f"Ожидалось: {expected}, найдено: {actual}."
            )

        conflicts.append(
            Conflict(
                type=conflict_type,
                message=message,
                affected_groups=[group],
                affected_teachers=[teacher],
            )
        )

    return conflicts


def validate_teacher_availability(
    schedule: list[ScheduleItem],
    preferences: PreferencesInput,
) -> list[Conflict]:
    availability_by_teacher = _build_availability_by_teacher(preferences)
    conflicts: list[Conflict] = []

    for item in schedule:
        if item.teacher not in availability_by_teacher:
            continue

        available_slots = availability_by_teacher[item.teacher]
        slot_key = (item.day, item.slot)

        if slot_key in available_slots:
            continue

        conflicts.append(
            Conflict(
                type="teacher_availability",
                message=(
                    f"Занятие {item.subject} у группы {item.group} поставлено "
                    f"в слот, недоступный для преподавателя {item.teacher}: "
                    f"{item.day}, {item.slot} пара."
                ),
                affected_groups=[item.group],
                affected_teachers=[item.teacher],
                affected_slots=[TimeSlot(day=item.day, slot=item.slot)],
            )
        )

    return conflicts


def _build_expected_lesson_counts(workload: WorkloadInput) -> Counter[LessonKey]:
    expected_counts: Counter[LessonKey] = Counter()

    for group in workload.groups:
        for lesson in group.lessons:
            key = (
                group.name,
                lesson.subject,
                lesson.teacher,
                lesson.lesson_type,
            )
            expected_counts[key] += lesson.lessons_per_week

    return expected_counts


def _build_actual_lesson_counts(schedule: list[ScheduleItem]) -> Counter[LessonKey]:
    actual_counts: Counter[LessonKey] = Counter()

    for item in schedule:
        key = (
            item.group,
            item.subject,
            item.teacher,
            item.lesson_type,
        )
        actual_counts[key] += 1

    return actual_counts


def _build_availability_by_teacher(
    preferences: PreferencesInput,
) -> dict[str, set[SlotKey]]:
    availability_by_teacher: dict[str, set[SlotKey]] = {}

    for preference in preferences.preferences:
        availability = parse_preference_input(preference)

        availability_by_teacher.setdefault(availability.teacher, set())
        availability_by_teacher[availability.teacher].update(
            (slot.day, slot.slot) for slot in availability.available_slots
        )

    return availability_by_teacher


def _unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))