from collections import Counter
from collections.abc import Iterable

from eduslot.models import Conflict, Day, PreferencesInput, TimeSlot, WorkloadInput
from eduslot.parser import parse_preference_input
from eduslot.time_grid import get_all_slots


SlotKey = tuple[Day, int]

DAY_ORDER: list[Day] = ["mon", "tue", "wed", "thu", "fri"]


def diagnose_schedule_inputs(
    workload: WorkloadInput,
    preferences: PreferencesInput,
) -> list[Conflict]:
    """Diagnose input data before running the scheduler."""
    conflicts: list[Conflict] = []

    conflicts.extend(diagnose_teacher_availability(workload, preferences))
    conflicts.extend(diagnose_group_capacity(workload))

    return conflicts


def diagnose_teacher_availability(
    workload: WorkloadInput,
    preferences: PreferencesInput,
) -> list[Conflict]:
    """Check whether teachers have enough available slots."""
    teacher_lesson_counts = _build_teacher_lesson_counts(workload)
    availability_by_teacher = _build_availability_by_teacher(preferences)
    default_slots = _to_slot_keys(get_all_slots())

    conflicts: list[Conflict] = []

    for teacher, required_lessons in sorted(teacher_lesson_counts.items()):
        available_slots = availability_by_teacher.get(teacher, default_slots)

        if not available_slots:
            conflicts.append(
                Conflict(
                    type="teacher_has_no_availability",
                    message=(
                        f"Для преподавателя {teacher} не найдено доступных слотов. "
                        f"По нагрузке требуется занятий: {required_lessons}."
                    ),
                    affected_teachers=[teacher],
                )
            )
            continue

        if required_lessons > len(available_slots):
            conflicts.append(
                Conflict(
                    type="teacher_available_slots_shortage",
                    message=(
                        f"Для преподавателя {teacher} требуется занятий: "
                        f"{required_lessons}, но доступных слотов только: "
                        f"{len(available_slots)}."
                    ),
                    affected_teachers=[teacher],
                    affected_slots=_to_time_slots(available_slots),
                )
            )

    return conflicts


def diagnose_group_capacity(workload: WorkloadInput) -> list[Conflict]:
    """Check whether group workload fits into the weekly time grid."""
    available_slot_count = len(get_all_slots())
    group_lesson_counts = _build_group_lesson_counts(workload)
    teachers_by_group = _build_teachers_by_group(workload)

    conflicts: list[Conflict] = []

    for group, required_lessons in sorted(group_lesson_counts.items()):
        if required_lessons <= available_slot_count:
            continue

        conflicts.append(
            Conflict(
                type="group_available_slots_shortage",
                message=(
                    f"Для группы {group} требуется занятий: {required_lessons}, "
                    f"но в сетке расписания доступно только слотов: "
                    f"{available_slot_count}."
                ),
                affected_groups=[group],
                affected_teachers=_unique(teachers_by_group[group]),
                affected_slots=get_all_slots(),
            )
        )

    return conflicts


def _build_teacher_lesson_counts(workload: WorkloadInput) -> Counter[str]:
    lesson_counts: Counter[str] = Counter()

    for group in workload.groups:
        for lesson in group.lessons:
            lesson_counts[lesson.teacher] += lesson.lessons_per_week

    return lesson_counts


def _build_group_lesson_counts(workload: WorkloadInput) -> Counter[str]:
    lesson_counts: Counter[str] = Counter()

    for group in workload.groups:
        for lesson in group.lessons:
            lesson_counts[group.name] += lesson.lessons_per_week

    return lesson_counts


def _build_teachers_by_group(workload: WorkloadInput) -> dict[str, list[str]]:
    teachers_by_group: dict[str, list[str]] = {}

    for group in workload.groups:
        teachers_by_group.setdefault(group.name, [])

        for lesson in group.lessons:
            teachers_by_group[group.name].append(lesson.teacher)

    return teachers_by_group


def _build_availability_by_teacher(
    preferences: PreferencesInput,
) -> dict[str, set[SlotKey]]:
    availability_by_teacher: dict[str, set[SlotKey]] = {}

    for preference in preferences.preferences:
        availability = parse_preference_input(preference)

        availability_by_teacher.setdefault(availability.teacher, set())
        availability_by_teacher[availability.teacher].update(
            _to_slot_keys(availability.available_slots)
        )

    return availability_by_teacher


def _to_slot_keys(slots: Iterable[TimeSlot]) -> set[SlotKey]:
    return {(slot.day, slot.slot) for slot in slots}


def _to_time_slots(slot_keys: Iterable[SlotKey]) -> list[TimeSlot]:
    return [
        TimeSlot(day=day, slot=slot)
        for day, slot in sorted(slot_keys, key=_slot_sort_key)
    ]


def _slot_sort_key(slot_key: SlotKey) -> tuple[int, int]:
    day, slot = slot_key
    return DAY_ORDER.index(day), slot


def _unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))