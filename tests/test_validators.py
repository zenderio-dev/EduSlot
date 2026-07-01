from eduslot.models import (
    GroupLoad,
    LessonLoad,
    PreferencesInput,
    ScheduleItem,
    TeacherPreferenceInput,
    WorkloadInput,
)
from eduslot.validators import (
    validate_group_overlaps,
    validate_required_load,
    validate_schedule,
    validate_teacher_availability,
    validate_teacher_overlaps,
)


def test_validate_schedule_returns_no_conflicts_for_valid_schedule():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
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
            day="tue",
            slot=1,
            lesson_type="lecture",
        ),
    ]

    conflicts = validate_schedule(schedule, workload, preferences)

    assert conflicts == []


def test_validate_teacher_overlaps_detects_teacher_conflict():
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
            subject="Databases",
            teacher="Ivanov",
            day="mon",
            slot=1,
            lesson_type="lecture",
        ),
    ]

    conflicts = validate_teacher_overlaps(schedule)

    assert len(conflicts) == 1
    assert conflicts[0].type == "teacher_overlap"
    assert conflicts[0].affected_teachers == ["Ivanov"]


def test_validate_group_overlaps_detects_group_conflict():
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
            slot=1,
            lesson_type="lecture",
        ),
    ]

    conflicts = validate_group_overlaps(schedule)

    assert len(conflicts) == 1
    assert conflicts[0].type == "group_overlap"
    assert conflicts[0].affected_groups == ["Group A"]


def test_validate_required_load_detects_missing_lessons():
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
                    )
                ],
            )
        ]
    )
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="mon",
            slot=1,
            lesson_type="practice",
        )
    ]

    conflicts = validate_required_load(schedule, workload)

    assert len(conflicts) == 1
    assert conflicts[0].type == "required_load_mismatch"
    assert conflicts[0].affected_groups == ["Group A"]
    assert conflicts[0].affected_teachers == ["Ivanov"]


def test_validate_required_load_detects_unexpected_lessons():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=1,
                        lesson_type="practice",
                    )
                ],
            )
        ]
    )
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
    ]

    conflicts = validate_required_load(schedule, workload)

    assert len(conflicts) == 1
    assert conflicts[0].type == "unexpected_lesson"
    assert conflicts[0].affected_groups == ["Group A"]
    assert conflicts[0].affected_teachers == ["Petrov"]


def test_validate_teacher_availability_detects_unavailable_slot():
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Ivanov",
                text="понедельник",
            )
        ]
    )
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="tue",
            slot=1,
            lesson_type="practice",
        )
    ]

    conflicts = validate_teacher_availability(schedule, preferences)

    assert len(conflicts) == 1
    assert conflicts[0].type == "teacher_availability"
    assert conflicts[0].affected_teachers == ["Ivanov"]


def test_validate_teacher_availability_ignores_teacher_without_preferences():
    preferences = PreferencesInput(preferences=[])
    schedule = [
        ScheduleItem(
            group="Group A",
            subject="Python",
            teacher="Ivanov",
            day="tue",
            slot=1,
            lesson_type="practice",
        )
    ]

    conflicts = validate_teacher_availability(schedule, preferences)

    assert conflicts == []