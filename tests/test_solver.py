from collections import Counter

from eduslot.models import (
    GroupLoad,
    LessonLoad,
    PreferencesInput,
    ScheduleItem,
    TeacherPreferenceInput,
    WorkloadInput,
)
from eduslot.solver import generate_schedule, generate_schedule_variants


def test_generate_schedule_assigns_every_lesson_once():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=2,
                        lesson_type="practice",
                    ),
                    LessonLoad(
                        subject="Databases",
                        teacher="Petrov",
                        lessons_per_week=1,
                        lesson_type="lecture",
                    ),
                ],
            )
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="понедельник",
            ),
            TeacherPreferenceInput(
                teacher="Petrov",
                text="вторник",
            ),
        ]
    )

    result = generate_schedule(workload, preferences)

    assert result.conflicts == []
    assert len(result.schedule) == 3

    subject_counts = Counter(item.subject for item in result.schedule)

    assert subject_counts["Python"] == 2
    assert subject_counts["Databases"] == 1


def test_generate_schedule_respects_teacher_availability():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    )
                ],
            )
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="среда с 13:50 до 17:00",
            )
        ]
    )

    result = generate_schedule(workload, preferences)

    assert result.conflicts == []
    assert len(result.schedule) == 1
    assert result.schedule[0].day == "wed"
    assert result.schedule[0].slot == 4


def test_generate_schedule_prevents_teacher_overlap():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    )
                ],
            ),
            GroupLoad(
                name="Group B",
                lessons=[
                    LessonLoad(
                        subject="Databases",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    )
                ],
            ),
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="понедельник",
            )
        ]
    )

    result = generate_schedule(workload, preferences)

    assert result.conflicts == []

    teacher_slots = [
        (item.teacher, item.day, item.slot)
        for item in result.schedule
        if item.teacher == "Ivanov"
    ]

    assert len(teacher_slots) == len(set(teacher_slots))


def test_generate_schedule_prevents_group_overlap():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    ),
                    LessonLoad(
                        subject="Databases",
                        teacher="Petrov",
                        lessons_per_week=1,
                    ),
                ],
            )
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="понедельник",
            ),
            TeacherPreferenceInput(
                teacher="Petrov",
                text="понедельник",
            ),
        ]
    )

    result = generate_schedule(workload, preferences)

    assert result.conflicts == []

    group_slots = [
        (item.group, item.day, item.slot)
        for item in result.schedule
        if item.group == "Group A"
    ]

    assert len(group_slots) == len(set(group_slots))


def test_generate_schedule_returns_conflict_when_teacher_has_no_available_slots():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    )
                ],
            )
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="можно после 12:00",
            )
        ]
    )

    result = generate_schedule(workload, preferences)

    assert result.schedule == []
    assert len(result.conflicts) == 1
    assert result.conflicts[0].type == "teacher_availability"


def test_generate_schedule_returns_conflict_for_impossible_group_schedule():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    ),
                    LessonLoad(
                        subject="Databases",
                        teacher="Petrov",
                        lessons_per_week=1,
                    ),
                ],
            )
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="понедельник с 09:00 до 10:30",
            ),
            TeacherPreferenceInput(
                teacher="Petrov",
                text="понедельник с 09:00 до 10:30",
            ),
        ]
    )

    result = generate_schedule(workload, preferences)

    assert result.schedule == []
    assert len(result.conflicts) == 1
    assert result.conflicts[0].type == "no_valid_schedule"


def test_generate_schedule_uses_full_grid_when_teacher_has_no_preference():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    )
                ],
            )
        ]
    )
    preferences = PreferencesInput(preferences=[])

    result = generate_schedule(workload, preferences)

    assert result.conflicts == []
    assert len(result.schedule) == 1
    assert result.warnings == [
        "Пожелания преподавателей не заданы. "
        "Для всех преподавателей используется полная сетка расписания."
    ]


def test_generate_schedule_variants_returns_requested_number_of_variants():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    ),
                    LessonLoad(
                        subject="Databases",
                        teacher="Petrov",
                        lessons_per_week=1,
                    ),
                ],
            )
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="понедельник",
            ),
            TeacherPreferenceInput(
                teacher="Petrov",
                text="понедельник",
            ),
        ]
    )

    variants = generate_schedule_variants(
        workload=workload,
        preferences=preferences,
        max_variants=3,
    )

    assert len(variants) == 3
    assert all(variant.conflicts == [] for variant in variants)
    assert all(len(variant.schedule) == 2 for variant in variants)

    signatures = {
        _build_test_schedule_signature(variant.schedule)
        for variant in variants
    }

    assert len(signatures) == 3


def test_generate_schedule_variants_returns_fewer_when_no_more_variants_exist():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    )
                ],
            )
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="понедельник с 09:00 до 10:30",
            )
        ]
    )

    variants = generate_schedule_variants(
        workload=workload,
        preferences=preferences,
        max_variants=3,
    )

    assert len(variants) == 1
    assert variants[0].conflicts == []
    assert len(variants[0].schedule) == 1


def test_generate_schedule_variants_returns_conflict_when_schedule_is_impossible():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    ),
                    LessonLoad(
                        subject="Databases",
                        teacher="Petrov",
                        lessons_per_week=1,
                    ),
                ],
            )
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="понедельник с 09:00 до 10:30",
            ),
            TeacherPreferenceInput(
                teacher="Petrov",
                text="понедельник с 09:00 до 10:30",
            ),
        ]
    )

    variants = generate_schedule_variants(
        workload=workload,
        preferences=preferences,
        max_variants=3,
    )

    assert len(variants) == 1
    assert variants[0].schedule == []
    assert len(variants[0].conflicts) == 1
    assert variants[0].conflicts[0].type == "no_valid_schedule"


def test_generate_schedule_variants_returns_empty_list_for_zero_variants():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    )
                ],
            )
        ]
    )
    preferences = PreferencesInput(preferences=[])

    variants = generate_schedule_variants(
        workload=workload,
        preferences=preferences,
        max_variants=0,
    )

    assert variants == []


def _build_test_schedule_signature(
    schedule: list[ScheduleItem],
) -> frozenset[tuple[str, str, str, str, int, str]]:
    return frozenset(
        (
            item.group,
            item.subject,
            item.teacher,
            item.day,
            item.slot,
            item.lesson_type,
        )
        for item in schedule
    )