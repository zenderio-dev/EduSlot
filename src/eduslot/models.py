from typing import Literal

from pydantic import BaseModel, Field


Day = Literal["mon", "tue", "wed", "thu", "fri"]
LessonType = Literal["lecture", "practice", "lab", "seminar"]


class TimeSlot(BaseModel):
    day: Day
    slot: int = Field(ge=1, le=8)


class LessonLoad(BaseModel):
    subject: str = Field(min_length=1)
    teacher: str = Field(min_length=1)
    lessons_per_week: int = Field(ge=1)
    lesson_type: LessonType = "practice"

    # Специальные ограничения
    consecutive_required: bool = False
    order_group: str | None = None
    order_index: int | None = None


class GroupLoad(BaseModel):
    name: str = Field(min_length=1)
    lessons: list[LessonLoad] = Field(min_length=1)


class WorkloadInput(BaseModel):
    groups: list[GroupLoad] = Field(min_length=1)


class TeacherPreferenceInput(BaseModel):
    teacher: str = Field(min_length=1)
    text: str = Field(min_length=1)


class PreferencesInput(BaseModel):
    preferences: list[TeacherPreferenceInput] = Field(default_factory=list)


class TeacherAvailability(BaseModel):
    teacher: str = Field(min_length=1)
    available_slots: list[TimeSlot]
    warnings: list[str] = Field(default_factory=list)


class ScheduleItem(BaseModel):
    group: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    teacher: str = Field(min_length=1)
    day: Day
    slot: int = Field(ge=1, le=8)
    lesson_type: LessonType


class Conflict(BaseModel):
    type: str = Field(min_length=1)
    message: str = Field(min_length=1)
    affected_groups: list[str] = Field(default_factory=list)
    affected_teachers: list[str] = Field(default_factory=list)
    affected_slots: list[TimeSlot] = Field(default_factory=list)


class ScheduleResult(BaseModel):
    schedule: list[ScheduleItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)