from pydantic import BaseModel, Field

from eduslot.models import LessonType, WorkloadInput


class LessonUnit(BaseModel):
    """One lesson occurrence prepared for scheduling."""
    id: str = Field(min_length=1)
    group: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    teacher: str = Field(min_length=1)
    lesson_type: LessonType
    occurrence_index: int = Field(ge=1)

    consecutive_required: bool = False
    order_group: str | None = None
    order_index: int | None = None


def build_lesson_units(workload: WorkloadInput) -> list[LessonUnit]:
    """Convert workload records into individual lesson units."""
    lesson_units: list[LessonUnit] = []

    for group in workload.groups:
        for lesson in group.lessons:
            for occurrence_index in range(1, lesson.lessons_per_week + 1):
                lesson_units.append(
                    LessonUnit(
                        id=_build_lesson_unit_id(
                            group=group.name,
                            subject=lesson.subject,
                            teacher=lesson.teacher,
                            occurrence_index=occurrence_index,
                        ),
                        group=group.name,
                        subject=lesson.subject,
                        teacher=lesson.teacher,
                        lesson_type=lesson.lesson_type,
                        occurrence_index=occurrence_index,
                        consecutive_required=lesson.consecutive_required,
                        order_group=lesson.order_group,
                        order_index=lesson.order_index,
                    )
                )

    return lesson_units


def count_total_lessons(workload: WorkloadInput) -> int:
    """Count total weekly lessons in workload input."""
    return sum(
        lesson.lessons_per_week
        for group in workload.groups
        for lesson in group.lessons
    )


def _build_lesson_unit_id(
    group: str,
    subject: str,
    teacher: str,
    occurrence_index: int,
) -> str:
    raw_id = f"{group}-{subject}-{teacher}-{occurrence_index}"
    return (
        raw_id.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("—", "-")
        .replace("–", "-")
    )