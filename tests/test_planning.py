from eduslot.models import GroupLoad, LessonLoad, WorkloadInput
from eduslot.planning import build_lesson_units, count_total_lessons


def test_build_lesson_units_expands_lessons_per_week():
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

    lesson_units = build_lesson_units(workload)

    assert len(lesson_units) == 2
    assert lesson_units[0].subject == "Python"
    assert lesson_units[0].occurrence_index == 1
    assert lesson_units[1].occurrence_index == 2


def test_build_lesson_units_preserves_group_and_teacher():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Databases",
                        teacher="Petrov",
                        lessons_per_week=1,
                        lesson_type="lecture",
                    )
                ],
            )
        ]
    )

    lesson_unit = build_lesson_units(workload)[0]

    assert lesson_unit.group == "Group A"
    assert lesson_unit.teacher == "Petrov"
    assert lesson_unit.lesson_type == "lecture"


def test_build_lesson_units_preserves_special_constraints():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Algorithms",
                        teacher="Sidorov",
                        lessons_per_week=1,
                        lesson_type="lecture",
                        consecutive_required=True,
                        order_group="algorithms-flow",
                        order_index=1,
                    )
                ],
            )
        ]
    )

    lesson_unit = build_lesson_units(workload)[0]

    assert lesson_unit.consecutive_required is True
    assert lesson_unit.order_group == "algorithms-flow"
    assert lesson_unit.order_index == 1


def test_count_total_lessons_returns_sum_of_weekly_load():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python",
                        teacher="Ivanov",
                        lessons_per_week=2,
                    ),
                    LessonLoad(
                        subject="Databases",
                        teacher="Petrov",
                        lessons_per_week=3,
                    ),
                ],
            ),
            GroupLoad(
                name="Group B",
                lessons=[
                    LessonLoad(
                        subject="Web",
                        teacher="Sidorov",
                        lessons_per_week=2,
                    )
                ],
            ),
        ]
    )

    assert count_total_lessons(workload) == 7


def test_lesson_unit_id_is_stable():
    workload = WorkloadInput(
        groups=[
            GroupLoad(
                name="Group A",
                lessons=[
                    LessonLoad(
                        subject="Python Basics",
                        teacher="Ivanov",
                        lessons_per_week=1,
                    )
                ],
            )
        ]
    )

    lesson_unit = build_lesson_units(workload)[0]

    assert lesson_unit.id == "group-a-python-basics-ivanov-1"