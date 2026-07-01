from eduslot.diagnostics import (
    diagnose_group_capacity,
    diagnose_schedule_inputs,
    diagnose_teacher_availability,
)
from eduslot.models import (
    GroupLoad,
    LessonLoad,
    PreferencesInput,
    TeacherPreferenceInput,
    WorkloadInput,
)


def test_diagnose_schedule_inputs_returns_no_conflicts_for_valid_input():
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

    conflicts = diagnose_schedule_inputs(workload, preferences)

    assert conflicts == []


def test_diagnose_teacher_availability_detects_teacher_without_available_slots():
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

    conflicts = diagnose_teacher_availability(workload, preferences)

    assert len(conflicts) == 1
    assert conflicts[0].type == "teacher_has_no_availability"
    assert conflicts[0].affected_teachers == ["Ivanov"]


def test_diagnose_teacher_availability_detects_slot_shortage():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Databases",
                        teacher="Petrov",
                        lessons_per_week=3,
                    )
                ],
            )
        ]
    )
    preferences = PreferencesInput(
        preferences=[
            TeacherPreferenceInput(
                teacher="Petrov",
                text="понедельник с 09:00 до 10:30",
            )
        ]
    )

    conflicts = diagnose_teacher_availability(workload, preferences)

    assert len(conflicts) == 1
    assert conflicts[0].type == "teacher_available_slots_shortage"
    assert conflicts[0].affected_teachers == ["Petrov"]
    assert len(conflicts[0].affected_slots) == 1


def test_diagnose_teacher_availability_uses_full_grid_without_preferences():
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

    conflicts = diagnose_teacher_availability(workload, preferences)

    assert conflicts == []


def test_diagnose_group_capacity_detects_group_overload():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=26,
                    )
                ],
            )
        ]
    )

    conflicts = diagnose_group_capacity(workload)

    assert len(conflicts) == 1
    assert conflicts[0].type == "group_available_slots_shortage"
    assert conflicts[0].affected_groups == ["Group A"]
    assert conflicts[0].affected_teachers == ["Ivanov"]


def test_diagnose_schedule_inputs_returns_multiple_conflicts():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=26,
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

    conflicts = diagnose_schedule_inputs(workload, preferences)
    conflict_types = {conflict.type for conflict in conflicts}

    assert conflict_types == {
        "teacher_available_slots_shortage",
        "group_available_slots_shortage",
    }